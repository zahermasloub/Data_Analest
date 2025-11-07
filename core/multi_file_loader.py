# -*- coding: utf-8 -*-
"""
Loader utilities to combine multiple uploaded files (CSV/Excel) into a single DataFrame.
Prefers DuckDB for fast UNION ALL when schemas match; falls back to pandas concat otherwise.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict, Any

import pandas as pd


def _clean_dataframe(df: pd.DataFrame, label: str = "") -> Tuple[pd.DataFrame, List[str]]:
    """Clean DataFrame by removing Unnamed columns and handling duplicate column names.
    
    Args:
        df: DataFrame to clean
        label: label for logging
        
    Returns:
        (cleaned_df, warnings): cleaned DataFrame and list of warning messages
    """
    warnings = []
    
    # 1. Remove Unnamed columns (CRITICAL for Arrow serialization)
    unnamed_cols = [col for col in df.columns if 'unnamed' in str(col).lower()]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)
        warnings.append(f"🗑️ حذف {len(unnamed_cols)} عمود Unnamed من {label}: {unnamed_cols}")
    
    # 2. Handle duplicate column names
    if df.columns.duplicated().any():
        duplicates = df.columns[df.columns.duplicated(keep=False)].unique().tolist()
        warnings.append(f"⚠️ أعمدة مكررة في {label}: {duplicates}")
        
        # Strategy: keep first occurrence, add suffix to duplicates
        new_columns = []
        col_counts: Dict[str, int] = {}
        
        for col in df.columns:
            col_str = str(col)
            if col_str in col_counts:
                col_counts[col_str] += 1
                # For duplicates after the first, either drop or rename
                # Here we'll drop them to avoid confusion
                new_columns.append(f"_DUPLICATE_{col_str}_{col_counts[col_str]}")
                warnings.append(f"  → تم وضع علامة للحذف: {col_str} (نسخة {col_counts[col_str]})")
            else:
                col_counts[col_str] = 0
                new_columns.append(col)
        
        df.columns = new_columns
        
        # Now drop the marked duplicates
        drop_cols = [c for c in df.columns if str(c).startswith('_DUPLICATE_')]
        if drop_cols:
            df = df.drop(columns=drop_cols)
            warnings.append(f"🗑️ حذف {len(drop_cols)} عمود مكرر")
    
    # 3. Ensure all remaining columns are unique
    if df.columns.duplicated().any():
        # Fallback: force unique by adding numeric suffix
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols == dup] = [f"{dup}.{i}" if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols.tolist()
        warnings.append(f"⚠️ تم إعادة تسمية أعمدة متبقية مكررة في {label}")
    
    # 4. Final check: remove any remaining Unnamed columns (double safety)
    final_unnamed = [col for col in df.columns if 'unnamed' in str(col).lower()]
    if final_unnamed:
        df = df.drop(columns=final_unnamed)
        warnings.append(f"🔴 حذف طارئ لأعمدة Unnamed متبقية: {final_unnamed}")
    
    return df, warnings


def _read_uploaded_file(file_obj) -> Tuple[List[pd.DataFrame], List[Dict[str, Any]]]:
    """Read a Streamlit UploadedFile (CSV/Excel) and return list of DataFrames with per-part stats.

    Returns:
        (dfs, stats):
            dfs: list of DataFrames (one per CSV or per Excel sheet)
            stats: list of dicts {"label": str, "rows": int, "columns": int, "warnings": list}
    """
    name = getattr(file_obj, "name", "uploaded")
    suffix = Path(name).suffix.lower()
    dfs: List[pd.DataFrame] = []
    stats: List[Dict[str, Any]] = []

    # Ensure buffer at start (Streamlit UploadedFile is a BytesIO-like)
    try:
        file_obj.seek(0)
    except Exception:
        pass

    if suffix in [".csv", ".txt"]:
        # تحسين: استخدام low_memory=False لتجنب الفحص المتكرر للأنواع
        # استخدام engine='c' للسرعة القصوى
        df = pd.read_csv(file_obj, low_memory=False, engine='c')
        df, warnings = _clean_dataframe(df, name)
        dfs.append(df)
        stats.append({
            "label": name, 
            "rows": len(df), 
            "columns": len(df.columns),
            "warnings": warnings
        })
    elif suffix in [".xlsx", ".xls"]:
        # تحسين: استخدام openpyxl بشكل مباشر مع data_only=True
        # قراءة فقط البيانات وتجاهل الصيغ لتحسين السرعة
        excel = pd.read_excel(file_obj, sheet_name=None, engine='openpyxl')
        for sheet_name, df in excel.items():
            label = f"{name}::{sheet_name}"
            df, warnings = _clean_dataframe(df, label)
            dfs.append(df)
            stats.append({
                "label": label, 
                "rows": len(df), 
                "columns": len(df.columns),
                "warnings": warnings
            })
    else:
        raise ValueError(f"صيغة غير مدعومة: {suffix} للملف {name}")

    return dfs, stats


def load_multiple_files(
    uploaded_files: List[Any],
    use_duckdb: bool = True,
    drop_exact_duplicates: bool = True,
) -> Tuple[pd.DataFrame, List[Dict[str, Any]], int]:
    """Combine multiple uploaded files into one DataFrame.

    Args:
        uploaded_files: list of Streamlit UploadedFile objects
        use_duckdb: if True and schemas match across parts, use DuckDB UNION ALL
        drop_exact_duplicates: drop exact duplicate rows after merge (best practice)

    Returns:
        combined_df, per_part_stats, removed_duplicates_count
    """
    if not uploaded_files:
        raise ValueError("لم يتم رفع أي ملفات")

    all_parts: List[pd.DataFrame] = []
    per_part_stats: List[Dict[str, Any]] = []

    for file_obj in uploaded_files:
        dfs, stats = _read_uploaded_file(file_obj)
        all_parts.extend(dfs)
        per_part_stats.extend(stats)

    if not all_parts:
        # No data found in provided files/sheets
        return pd.DataFrame(), per_part_stats, 0

    # Check schema compatibility
    def _cols_signature(df: pd.DataFrame) -> tuple:
        return tuple(str(c) for c in df.columns)

    same_schema = len({ _cols_signature(df) for df in all_parts }) == 1

    combined: pd.DataFrame
    used_duckdb = False

    if use_duckdb and same_schema:
        try:
            import duckdb  # type: ignore
            con = duckdb.connect()
            for i, df in enumerate(all_parts):
                con.register(f"t{i}", df)
            union_sql = " UNION ALL ".join([f"SELECT * FROM t{i}" for i in range(len(all_parts))])
            combined = con.execute(union_sql).df()
            con.close()
            used_duckdb = True
        except Exception:
            # Fallback to pandas concat if duckdb not available or any error occurs
            combined = pd.concat(all_parts, ignore_index=True, sort=False)
    else:
        # Different schemas or disabled: use pandas concat to align columns
        combined = pd.concat(all_parts, ignore_index=True, sort=False)

    removed = 0
    if drop_exact_duplicates and not combined.empty:
        before = len(combined)
        combined = combined.drop_duplicates().reset_index(drop=True)
        removed = before - len(combined)

    # Add a small note in stats indicating backend used (for UI display if desired)
    per_part_stats.append({
        "label": "__summary__",
        "rows": len(combined),
        "columns": len(combined.columns),
        "used_duckdb": used_duckdb,
        "removed_exact_duplicates": removed,
    })

    return combined, per_part_stats, removed
