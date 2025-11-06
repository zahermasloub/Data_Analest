# -*- coding: utf-8 -*-
"""
⚡ مُحسِّن الأداء - Performance Optimizer
==========================================
تسريع معالجة الملفات الكبيرة باستخدام DuckDB و Dask

Libraries Used:
- duckdb>=0.9.0 (للاستعلامات SQL السريعة)
- dask[complete]>=2023.12.0 (للمعالجة الموزعة)
- pandas>=2.1.0
- pyarrow>=14.0.0

Install if missing:
pip install duckdb "dask[complete]" pandas pyarrow
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Union
import warnings

# محاولة استيراد duckdb
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    warnings.warn("⚠️ duckdb غير متوفر - سيتم استخدام pandas العادي")

# محاولة استيراد dask
try:
    import dask.dataframe as dd
    from dask.diagnostics import ProgressBar
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False
    warnings.warn("⚠️ dask غير متوفر - سيتم استخدام pandas العادي")


class PerformanceOptimizer:
    """محسِّن الأداء للملفات الكبيرة"""
    
    def __init__(self, use_duckdb: bool = True, use_dask: bool = False):
        """
        تهيئة المحسِّن
        
        Args:
            use_duckdb: استخدام DuckDB للاستعلامات السريعة
            use_dask: استخدام Dask للمعالجة الموزعة
        """
        self.use_duckdb = use_duckdb and DUCKDB_AVAILABLE
        self.use_dask = use_dask and DASK_AVAILABLE
        self.conn = None
        
        if self.use_duckdb:
            self._init_duckdb()
    
    def _init_duckdb(self):
        """تهيئة اتصال DuckDB في الذاكرة"""
        try:
            self.conn = duckdb.connect(':memory:')
            print("✅ تم تهيئة DuckDB في الذاكرة")
        except Exception as e:
            print(f"⚠️ خطأ في تهيئة DuckDB: {str(e)}")
            self.use_duckdb = False
    
    def load_excel_optimized(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        تحميل ملف Excel بأداء محسّن
        
        Library Used: pandas, dask (optional)
        
        Args:
            file_path: مسار الملف
            sheet_name: اسم الورقة (اختياري)
            
        Returns:
            DataFrame
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")
        
        print(f"📂 تحميل: {file_path.name}")
        
        # استخدام pandas العادي (أسرع لملفات Excel)
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name or 0,
                engine='openpyxl'
            )
            print(f"   ✅ تم تحميل {len(df):,} صف")
            return df
        except Exception as e:
            print(f"   ❌ خطأ: {str(e)}")
            return pd.DataFrame()
    
    def load_multiple_excel_optimized(
        self,
        file_paths: List[Union[str, Path]],
        sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        تحميل ودمج عدة ملفات Excel
        
        Library Used: pandas, dask (optional)
        
        Args:
            file_paths: قائمة مسارات الملفات
            sheet_name: اسم الورقة (اختياري)
            
        Returns:
            DataFrame مدمج
        """
        if not file_paths:
            return pd.DataFrame()
        
        print(f"📂 تحميل {len(file_paths)} ملف...")
        
        dataframes = []
        for file_path in file_paths:
            df = self.load_excel_optimized(file_path, sheet_name)
            if not df.empty:
                dataframes.append(df)
        
        if not dataframes:
            return pd.DataFrame()
        
        # الدمج
        print("🔄 دمج الملفات...")
        combined = pd.concat(dataframes, ignore_index=True)
        print(f"   ✅ إجمالي: {len(combined):,} صف")
        
        return combined
    
    def filter_by_amount_duckdb(
        self,
        df: pd.DataFrame,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        amount_column: str = 'AwardAmount'
    ) -> pd.DataFrame:
        """
        فلترة حسب المبلغ باستخدام DuckDB
        
        Library Used: duckdb
        
        Args:
            df: DataFrame
            min_amount: الحد الأدنى
            max_amount: الحد الأقصى
            amount_column: اسم عمود المبلغ
            
        Returns:
            DataFrame مفلتر
        """
        if not self.use_duckdb or df.empty:
            # Fallback إلى pandas
            result = df.copy()
            if min_amount is not None:
                result = result[result[amount_column] >= min_amount]
            if max_amount is not None:
                result = result[result[amount_column] <= max_amount]
            return result
        
        try:
            # استعلام DuckDB
            query = f"SELECT * FROM df WHERE 1=1"
            
            if min_amount is not None:
                query += f" AND {amount_column} >= {min_amount}"
            
            if max_amount is not None:
                query += f" AND {amount_column} <= {max_amount}"
            
            result = self.conn.execute(query).df()
            return result
            
        except Exception as e:
            print(f"⚠️ خطأ DuckDB: {str(e)}")
            # Fallback
            result = df.copy()
            if min_amount is not None:
                result = result[result[amount_column] >= min_amount]
            if max_amount is not None:
                result = result[result[amount_column] <= max_amount]
            return result
    
    def join_dataframes_duckdb(
        self,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        left_on: str,
        right_on: str,
        how: str = 'inner'
    ) -> pd.DataFrame:
        """
        دمج DataFrames باستخدام DuckDB
        
        Library Used: duckdb
        
        Args:
            left_df: الجدول الأيسر
            right_df: الجدول الأيمن
            left_on: عمود المطابقة (أيسر)
            right_on: عمود المطابقة (أيمن)
            how: نوع الدمج (inner/left/right/outer)
            
        Returns:
            DataFrame مدمج
        """
        if not self.use_duckdb:
            # Fallback إلى pandas
            return pd.merge(
                left_df,
                right_df,
                left_on=left_on,
                right_on=right_on,
                how=how
            )
        
        try:
            # استعلام DuckDB
            join_type = how.upper()
            
            query = f"""
                SELECT *
                FROM left_df
                {join_type} JOIN right_df
                ON left_df.{left_on} = right_df.{right_on}
            """
            
            result = self.conn.execute(query).df()
            return result
            
        except Exception as e:
            print(f"⚠️ خطأ DuckDB: {str(e)}")
            # Fallback
            return pd.merge(
                left_df,
                right_df,
                left_on=left_on,
                right_on=right_on,
                how=how
            )
    
    def aggregate_by_group_duckdb(
        self,
        df: pd.DataFrame,
        group_by: List[str],
        agg_columns: Dict[str, str]
    ) -> pd.DataFrame:
        """
        تجميع وتلخيص باستخدام DuckDB
        
        Library Used: duckdb
        
        Args:
            df: DataFrame
            group_by: أعمدة التجميع
            agg_columns: قاموس {عمود: دالة} مثل {'Amount': 'SUM'}
            
        Returns:
            DataFrame مجمَّع
        """
        if not self.use_duckdb or df.empty:
            # Fallback إلى pandas
            agg_dict = {col: func.lower() for col, func in agg_columns.items()}
            return df.groupby(group_by).agg(agg_dict).reset_index()
        
        try:
            # بناء استعلام SQL
            select_parts = [', '.join(group_by)]
            
            for col, func in agg_columns.items():
                select_parts.append(f"{func}({col}) as {col}_{func}")
            
            select_clause = ', '.join(select_parts)
            group_clause = ', '.join(group_by)
            
            query = f"""
                SELECT {select_clause}
                FROM df
                GROUP BY {group_clause}
            """
            
            result = self.conn.execute(query).df()
            return result
            
        except Exception as e:
            print(f"⚠️ خطأ DuckDB: {str(e)}")
            # Fallback
            agg_dict = {col: func.lower() for col, func in agg_columns.items()}
            return df.groupby(group_by).agg(agg_dict).reset_index()
    
    def process_large_file_dask(
        self,
        file_path: Union[str, Path],
        processing_func,
        chunk_size: str = '100MB'
    ) -> pd.DataFrame:
        """
        معالجة ملف كبير باستخدام Dask
        
        Library Used: dask
        
        Args:
            file_path: مسار الملف
            processing_func: دالة المعالجة
            chunk_size: حجم القطعة
            
        Returns:
            DataFrame معالج
        """
        if not self.use_dask:
            # Fallback إلى pandas
            df = pd.read_csv(file_path)
            return processing_func(df)
        
        try:
            # قراءة باستخدام Dask
            ddf = dd.read_csv(file_path, blocksize=chunk_size)
            
            # تطبيق الدالة
            result_ddf = ddf.map_partitions(processing_func)
            
            # تنفيذ مع شريط التقدم
            with ProgressBar():
                result = result_ddf.compute()
            
            return result
            
        except Exception as e:
            print(f"⚠️ خطأ Dask: {str(e)}")
            # Fallback
            df = pd.read_csv(file_path)
            return processing_func(df)
    
    def get_statistics(self) -> Dict[str, any]:
        """
        إحصائيات الأداء
        
        Returns:
            قاموس بالإحصائيات
        """
        return {
            'duckdb_enabled': self.use_duckdb,
            'dask_enabled': self.use_dask,
            'duckdb_available': DUCKDB_AVAILABLE,
            'dask_available': DASK_AVAILABLE
        }
    
    def close(self):
        """إغلاق الاتصالات"""
        if self.conn:
            try:
                self.conn.close()
                print("✅ تم إغلاق اتصال DuckDB")
            except:
                pass
    
    def __del__(self):
        """Destructor"""
        self.close()


# دوال مساعدة
def recommend_optimizer_settings(file_size_mb: float) -> Dict[str, bool]:
    """
    توصية بإعدادات المحسِّن حسب حجم الملف
    
    Args:
        file_size_mb: حجم الملف (MB)
        
    Returns:
        قاموس بالإعدادات الموصى بها
    """
    if file_size_mb < 10:
        # ملفات صغيرة - pandas عادي
        return {
            'use_duckdb': False,
            'use_dask': False,
            'reason': 'ملف صغير - pandas عادي كافٍ'
        }
    
    elif file_size_mb < 100:
        # ملفات متوسطة - DuckDB فقط
        return {
            'use_duckdb': True,
            'use_dask': False,
            'reason': 'ملف متوسط - استخدام DuckDB للتسريع'
        }
    
    else:
        # ملفات كبيرة - DuckDB + Dask
        return {
            'use_duckdb': True,
            'use_dask': True,
            'reason': 'ملف كبير - استخدام DuckDB + Dask'
        }
