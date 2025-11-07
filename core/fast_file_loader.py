# -*- coding: utf-8 -*-
"""
Fast File Loader - نسخة محسّنة لتحميل الملفات بسرعة عالية
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict, Any
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import io


def _quick_clean_dataframe(df: pd.DataFrame, label: str = "") -> Tuple[pd.DataFrame, List[str]]:
    """تنظيف سريع للـ DataFrame - نسخة محسّنة للأداء
    
    Args:
        df: DataFrame للتنظيف
        label: تسمية توضيحية
        
    Returns:
        (cleaned_df, warnings): DataFrame نظيف وقائمة التحذيرات
    """
    warnings = []
    
    # 1. إزالة أعمدة Unnamed (بحث أسرع)
    unnamed_mask = df.columns.str.lower().str.contains('unnamed', na=False)
    if unnamed_mask.any():
        unnamed_cols = df.columns[unnamed_mask].tolist()
        df = df.drop(columns=unnamed_cols)
        warnings.append(f"🗑️ حذف {len(unnamed_cols)} عمود Unnamed")
    
    # 2. معالجة الأعمدة المكررة (بدون حلقات)
    if df.columns.duplicated().any():
        # الاحتفاظ بالعمود الأول فقط من كل مجموعة مكررات
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        warnings.append(f"⚠️ إزالة أعمدة مكررة")
    
    return df, warnings


def _read_file_fast(file_obj, name: str) -> Tuple[List[pd.DataFrame], List[Dict[str, Any]]]:
    """قراءة ملف واحد بسرعة عالية
    
    Args:
        file_obj: كائن الملف المرفوع
        name: اسم الملف
        
    Returns:
        (dfs, stats): قائمة DataFrames والإحصائيات
    """
    suffix = Path(name).suffix.lower()
    dfs: List[pd.DataFrame] = []
    stats: List[Dict[str, Any]] = []
    
    try:
        file_obj.seek(0)
    except Exception:
        pass
    
    try:
        if suffix in [".csv", ".txt"]:
            # قراءة CSV مع تحسينات الأداء
            df = pd.read_csv(
                file_obj,
                low_memory=False,  # تجنب تحذيرات النوع
                engine='c',  # محرك C أسرع
                encoding_errors='ignore'  # تجاهل أخطاء الترميز
            )
            df, warnings = _quick_clean_dataframe(df, name)
            dfs.append(df)
            stats.append({
                "label": name,
                "rows": len(df),
                "columns": len(df.columns),
                "warnings": warnings
            })
            
        elif suffix in [".xlsx", ".xls"]:
            # قراءة Excel مع تحسينات
            excel = pd.read_excel(
                file_obj,
                sheet_name=None,
                engine='openpyxl'
            )
            
            for sheet_name, df in excel.items():
                label = f"{name}::{sheet_name}"
                df, warnings = _quick_clean_dataframe(df, label)
                dfs.append(df)
                stats.append({
                    "label": label,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "warnings": warnings
                })
        else:
            raise ValueError(f"صيغة غير مدعومة: {suffix}")
            
    except Exception as e:
        stats.append({
            "label": name,
            "rows": 0,
            "columns": 0,
            "warnings": [f"❌ خطأ في قراءة الملف: {str(e)}"]
        })
    
    return dfs, stats


def load_files_parallel(
    uploaded_files: List[Any],
    use_duckdb: bool = True,
    drop_exact_duplicates: bool = True,
    max_workers: int = 4
) -> Tuple[pd.DataFrame, List[Dict[str, Any]], int]:
    """تحميل متوازي للملفات - أسرع من التحميل المتسلسل
    
    Args:
        uploaded_files: قائمة الملفات المرفوعة
        use_duckdb: استخدام DuckDB للدمج
        drop_exact_duplicates: إزالة التكرارات المتطابقة
        max_workers: عدد الـ threads للمعالجة المتوازية
        
    Returns:
        (combined_df, per_part_stats, removed_duplicates_count)
    """
    if not uploaded_files:
        raise ValueError("لم يتم رفع أي ملفات")
    
    all_parts: List[pd.DataFrame] = []
    per_part_stats: List[Dict[str, Any]] = []
    
    # معالجة متوازية للملفات
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # إنشاء مهام للقراءة
        future_to_file = {
            executor.submit(_read_file_fast, file_obj, getattr(file_obj, "name", f"file_{i}")): i
            for i, file_obj in enumerate(uploaded_files)
        }
        
        # جمع النتائج
        for future in as_completed(future_to_file):
            try:
                dfs, stats = future.result()
                all_parts.extend(dfs)
                per_part_stats.extend(stats)
            except Exception as e:
                per_part_stats.append({
                    "label": f"unknown_file_{future_to_file[future]}",
                    "rows": 0,
                    "columns": 0,
                    "warnings": [f"❌ فشل التحميل: {str(e)}"]
                })
    
    if not all_parts:
        return pd.DataFrame(), per_part_stats, 0
    
    # دمج البيانات
    combined: pd.DataFrame
    used_duckdb = False
    
    # فحص توافق المخطط
    first_cols = set(all_parts[0].columns)
    same_schema = all(set(df.columns) == first_cols for df in all_parts)
    
    if use_duckdb and same_schema and len(all_parts) > 1:
        try:
            import duckdb
            con = duckdb.connect()
            
            # تسجيل الجداول
            for i, df in enumerate(all_parts):
                con.register(f"t{i}", df)
            
            # دمج باستخدام UNION ALL
            union_sql = " UNION ALL ".join([f"SELECT * FROM t{i}" for i in range(len(all_parts))])
            combined = con.execute(union_sql).df()
            con.close()
            used_duckdb = True
            
        except Exception:
            # الرجوع إلى pandas إذا فشل DuckDB
            combined = pd.concat(all_parts, ignore_index=True, sort=False, copy=False)
    else:
        # دمج باستخدام pandas
        combined = pd.concat(all_parts, ignore_index=True, sort=False, copy=False)
    
    # إزالة التكرارات المتطابقة
    removed = 0
    if drop_exact_duplicates and not combined.empty:
        before = len(combined)
        combined = combined.drop_duplicates().reset_index(drop=True)
        removed = before - len(combined)
    
    # إضافة ملخص
    per_part_stats.append({
        "label": "__summary__",
        "rows": len(combined),
        "columns": len(combined.columns),
        "used_duckdb": used_duckdb,
        "removed_exact_duplicates": removed,
    })
    
    return combined, per_part_stats, removed
