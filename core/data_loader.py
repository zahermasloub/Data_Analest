# -*- coding: utf-8 -*-
"""
محرك تحميل ومعالجة البيانات من ملفات Excel و CSV
يدعم: قراءة ذكية، تنظيف تلقائي، كشف أنواع الأعمدة
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import warnings
import logging
from datetime import datetime

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """محمل بيانات ذكي مع معالجة متقدمة"""
    
    def __init__(self, file_path: Union[str, Path]):
        """
        تهيئة محمل البيانات
        
        Args:
            file_path: مسار ملف Excel أو CSV
        """
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.original_df: Optional[pd.DataFrame] = None
        self.column_mapping: Dict[str, str] = {}
        self.metadata: Dict = {}
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")
    
    def load(self, sheet_name: Optional[Union[str, int]] = 0, 
             encoding: str = 'utf-8-sig') -> pd.DataFrame:
        """
        تحميل البيانات من الملف
        
        Args:
            sheet_name: اسم أو رقم الورقة (للإكسل)
            encoding: الترميز المستخدم
            
        Returns:
            DataFrame محمل
        """
        logger.info(f"تحميل الملف: {self.file_path.name}")
        
        try:
            if self.file_path.suffix.lower() in ['.xlsx', '.xls']:
                self.df = self._load_excel(sheet_name)
            elif self.file_path.suffix.lower() == '.csv':
                self.df = self._load_csv(encoding)
            else:
                raise ValueError(f"نوع ملف غير مدعوم: {self.file_path.suffix}")
            
            # حفظ نسخة أصلية
            self.original_df = self.df.copy()
            
            # جمع معلومات أساسية
            self._collect_metadata()
            
            logger.info(f"تم التحميل: {len(self.df)} صف، {len(self.df.columns)} عمود")
            return self.df
            
        except Exception as e:
            logger.error(f"خطأ في التحميل: {str(e)}")
            raise
    
    def _load_excel(self, sheet_name: Union[str, int]) -> pd.DataFrame:
        """تحميل ملف Excel"""
        try:
            # محاولة قراءة باستخدام openpyxl
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
        except Exception:
            # محاولة باستخدام xlrd للملفات القديمة
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='xlrd')
        return df
    
    def _load_csv(self, encoding: str) -> pd.DataFrame:
        """تحميل ملف CSV"""
        # محاولة عدة ترميزات
        encodings = [encoding, 'utf-8', 'utf-8-sig', 'cp1256', 'windows-1256']
        
        for enc in encodings:
            try:
                df = pd.read_csv(self.file_path, encoding=enc)
                logger.info(f"نجح التحميل بترميز: {enc}")
                return df
            except UnicodeDecodeError:
                continue
        
        raise ValueError("فشل تحميل الملف بجميع الترميزات المتاحة")
    
    def clean_column_names(self) -> 'DataLoader':
        """تنظيف وتوحيد أسماء الأعمدة"""
        if self.df is None:
            raise ValueError("يجب تحميل البيانات أولاً")
        
        original_columns = self.df.columns.tolist()
        new_columns = []
        seen = {}
        
        for col in original_columns:
            # إزالة المسافات الزائدة
            col_clean = str(col).strip()
            
            # التعامل مع الأعمدة المكررة
            if col_clean in seen:
                seen[col_clean] += 1
                new_col = f"{col_clean}_{seen[col_clean]}"
            else:
                seen[col_clean] = 1
                new_col = col_clean
            
            new_columns.append(new_col)
            self.column_mapping[new_col] = col
        
        self.df.columns = new_columns
        logger.info(f"تم تنظيف {len(new_columns)} اسم عمود")
        
        return self
    
    def remove_empty_rows_and_columns(self, threshold: float = 0.9) -> 'DataLoader':
        """
        إزالة الصفوف والأعمدة الفارغة
        
        Args:
            threshold: نسبة القيم الفارغة المسموحة (0.9 = 90%)
        """
        if self.df is None:
            raise ValueError("يجب تحميل البيانات أولاً")
        
        initial_shape = self.df.shape
        
        # إزالة الأعمدة الفارغة تماماً
        empty_cols = self.df.columns[self.df.isnull().all()].tolist()
        if empty_cols:
            self.df = self.df.drop(columns=empty_cols)
            logger.info(f"تم إزالة {len(empty_cols)} عمود فارغ")
        
        # إزالة الأعمدة التي تتجاوز نسبة الفراغ الحد المسموح
        null_pct = self.df.isnull().mean()
        cols_to_drop = null_pct[null_pct > threshold].index.tolist()
        if cols_to_drop:
            self.df = self.df.drop(columns=cols_to_drop)
            logger.info(f"تم إزالة {len(cols_to_drop)} عمود بنسبة فراغ > {threshold*100}%")
        
        # إزالة الصفوف الفارغة تماماً
        self.df = self.df.dropna(how='all')
        
        final_shape = self.df.shape
        logger.info(f"الشكل: {initial_shape} → {final_shape}")
        
        return self
    
    def detect_column_types(self) -> Dict[str, List[str]]:
        """
        كشف أنواع الأعمدة تلقائياً (أرقام، تواريخ، نصوص، معرفات)
        
        Returns:
            قاموس بأنواع الأعمدة
        """
        if self.df is None:
            raise ValueError("يجب تحميل البيانات أولاً")
        
        column_types = {
            'numeric': [],
            'date': [],
            'text': [],
            'id': [],
            'amount': [],
            'category': []
        }
        
        for col in self.df.columns:
            col_lower = col.lower()
            
            # كشف الأعمدة الرقمية
            if pd.api.types.is_numeric_dtype(self.df[col]):
                column_types['numeric'].append(col)
                
                # كشف أعمدة المبالغ
                if any(keyword in col_lower for keyword in ['amount', 'قيمة', 'مبلغ', 'total', 'payment', 'دفعة']):
                    column_types['amount'].append(col)
            
            # كشف أعمدة التواريخ
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                column_types['date'].append(col)
            else:
                # محاولة تحويل إلى تاريخ
                try:
                    pd.to_datetime(self.df[col].dropna().head(100), errors='raise')
                    column_types['date'].append(col)
                    continue
                except:
                    pass
                
                # كشف أعمدة المعرفات
                if any(keyword in col_lower for keyword in ['id', 'رقم', 'معرف', 'code', 'كود']):
                    column_types['id'].append(col)
                
                # كشف الأعمدة النصية
                else:
                    column_types['text'].append(col)
                    
                    # كشف أعمدة التصنيف (قيم متكررة محدودة)
                    unique_ratio = self.df[col].nunique() / len(self.df)
                    if unique_ratio < 0.05:  # أقل من 5% قيم فريدة
                        column_types['category'].append(col)
        
        self.metadata['column_types'] = column_types
        logger.info(f"تم كشف أنواع الأعمدة: {sum(len(v) for v in column_types.values())} عمود")
        
        return column_types
    
    def remove_duplicate_columns(self) -> 'DataLoader':
        """إزالة الأعمدة المكررة مع الاحتفاظ بالأول"""
        if self.df is None:
            raise ValueError("يجب تحميل البيانات أولاً")
        
        cols_to_keep = []
        cols_seen = set()
        
        for col in self.df.columns:
            # استخراج الاسم الأساسي
            base_col = col.split('_')[0] if '_' in col and col.split('_')[-1].isdigit() else col
            
            if base_col not in cols_seen:
                cols_to_keep.append(col)
                cols_seen.add(base_col)
        
        removed = len(self.df.columns) - len(cols_to_keep)
        if removed > 0:
            self.df = self.df[cols_to_keep]
            logger.info(f"تم إزالة {removed} عمود مكرر")
        
        return self
    
    def auto_clean(self) -> 'DataLoader':
        """تنظيف تلقائي شامل للبيانات"""
        logger.info("بدء التنظيف التلقائي...")
        
        self.clean_column_names()
        self.remove_empty_rows_and_columns()
        self.remove_duplicate_columns()
        self.detect_column_types()
        
        logger.info("اكتمل التنظيف التلقائي")
        return self
    
    def _collect_metadata(self) -> None:
        """جمع معلومات وصفية عن البيانات"""
        if self.df is None:
            return
        
        self.metadata.update({
            'file_name': self.file_path.name,
            'file_size_mb': self.file_path.stat().st_size / (1024 * 1024),
            'load_time': datetime.now().isoformat(),
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / (1024 * 1024),
            'null_counts': self.df.isnull().sum().to_dict(),
            'dtypes': self.df.dtypes.astype(str).to_dict(),
        })
    
    def get_summary(self) -> Dict:
        """
        الحصول على ملخص شامل للبيانات
        
        Returns:
            قاموس بالمعلومات الوصفية
        """
        if self.df is None:
            raise ValueError("يجب تحميل البيانات أولاً")
        
        summary = {
            'metadata': self.metadata,
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'null_percentage': (self.df.isnull().sum() / len(self.df) * 100).to_dict(),
            'sample_data': self.df.head(3).to_dict('records'),
        }
        
        # إحصائيات للأعمدة الرقمية
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary['numeric_stats'] = self.df[numeric_cols].describe().to_dict()
        
        return summary
    
    def get_data(self) -> pd.DataFrame:
        """الحصول على DataFrame المُعالج"""
        if self.df is None:
            raise ValueError("يجب تحميل البيانات أولاً")
        return self.df.copy()
    
    def get_original_data(self) -> pd.DataFrame:
        """الحصول على DataFrame الأصلي قبل المعالجة"""
        if self.original_df is None:
            raise ValueError("يجب تحميل البيانات أولاً")
        return self.original_df.copy()


def load_and_clean(file_path: Union[str, Path], 
                   sheet_name: Optional[Union[str, int]] = 0) -> Tuple[pd.DataFrame, Dict]:
    """
    دالة مساعدة سريعة لتحميل وتنظيف البيانات
    
    Args:
        file_path: مسار الملف
        sheet_name: رقم أو اسم الورقة (للإكسل)
        
    Returns:
        (DataFrame منظف، معلومات وصفية)
    """
    loader = DataLoader(file_path)
    loader.load(sheet_name=sheet_name)
    loader.auto_clean()
    
    return loader.get_data(), loader.metadata
