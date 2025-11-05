# -*- coding: utf-8 -*-
"""
محلل الدفعات المكررة - كشف متقدم للتكرارات
يدعم: تطابق تام، تطابق ضبابي، تطابق جزئي
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class DuplicateAnalyzer:
    """محلل متقدم للدفعات المكررة"""
    
    def __init__(self, df: pd.DataFrame):
        """
        تهيئة المحلل
        
        Args:
            df: DataFrame للتحليل
        """
        self.df = df.copy()
        self.duplicates: Optional[pd.DataFrame] = None
        self.duplicate_groups: Dict = {}
        self.stats: Dict = {}
    
    def find_exact_duplicates(self, 
                            subset: Optional[List[str]] = None,
                            keep: str = 'first') -> pd.DataFrame:
        """
        البحث عن التكرارات التامة
        
        Args:
            subset: الأعمدة المستخدمة للمقارنة (None = جميع الأعمدة)
            keep: أي نسخة نحتفظ بها ('first', 'last', False)
            
        Returns:
            DataFrame بالتكرارات
        """
        # تحديد الصفوف المكررة
        mask = self.df.duplicated(subset=subset, keep=False)
        duplicates = self.df[mask].copy()
        
        if len(duplicates) > 0:
            # إضافة معرف المجموعة
            if subset:
                duplicates['duplicate_group'] = duplicates.groupby(subset).ngroup()
            else:
                duplicates['duplicate_group'] = duplicates.groupby(list(self.df.columns)).ngroup()
            
            logger.info(f"تم العثور على {len(duplicates)} سجل مكرر")
        
        return duplicates
    
    def find_payment_duplicates(self,
                               entity_col: str,
                               amount_col: str,
                               date_col: Optional[str] = None,
                               event_col: Optional[str] = None,
                               time_window_days: Optional[int] = None) -> pd.DataFrame:
        """
        البحث عن دفعات مكررة (نفس الجهة + نفس المبلغ + نفس الحدث)
        
        Args:
            entity_col: عمود اسم الجهة/الشخص
            amount_col: عمود المبلغ
            date_col: عمود التاريخ (اختياري)
            event_col: عمود الحدث/السباق (اختياري)
            time_window_days: نافذة زمنية للتكرار (None = بدون تقييد)
            
        Returns:
            DataFrame بالدفعات المكررة
        """
        logger.info("البحث عن دفعات مكررة...")
        
        # التحقق من وجود الأعمدة
        required_cols = [entity_col, amount_col]
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"الأعمدة المطلوبة غير موجودة: {missing}")
        
        # بناء قائمة الأعمدة للمقارنة
        comparison_cols = [entity_col, amount_col]
        if event_col and event_col in self.df.columns:
            comparison_cols.append(event_col)
        
        # البحث عن التكرارات
        df_work = self.df.copy()
        
        # إذا كان هناك نافذة زمنية
        if date_col and date_col in df_work.columns and time_window_days:
            df_work[date_col] = pd.to_datetime(df_work[date_col], errors='coerce')
            df_work = df_work.dropna(subset=[date_col])
            df_work = df_work.sort_values(date_col)
            
            # البحث عن التكرارات ضمن النافذة الزمنية
            duplicates = self._find_duplicates_with_time_window(
                df_work, comparison_cols, date_col, time_window_days
            )
        else:
            # البحث عن التكرارات بدون تقييد زمني
            mask = df_work.duplicated(subset=comparison_cols, keep=False)
            duplicates = df_work[mask].copy()
            
            if len(duplicates) > 0:
                duplicates['duplicate_group'] = duplicates.groupby(comparison_cols).ngroup()
        
        # إضافة عدد التكرارات لكل مجموعة
        if len(duplicates) > 0 and 'duplicate_group' in duplicates.columns:
            duplicates['duplicate_count'] = duplicates.groupby('duplicate_group')['duplicate_group'].transform('count')
            duplicates = duplicates.sort_values(['duplicate_group', entity_col])
            
            # حساب الإحصائيات
            self._calculate_duplicate_stats(duplicates, comparison_cols)
        
        self.duplicates = duplicates
        logger.info(f"تم العثور على {len(duplicates)} دفعة مكررة في {duplicates['duplicate_group'].nunique() if len(duplicates) > 0 else 0} مجموعة")
        
        return duplicates
    
    def find_fuzzy_duplicates(self,
                             name_col: str,
                             threshold: float = 0.90,
                             additional_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        البحث عن تكرارات ضبابية (أسماء متشابهة وليست متطابقة تماماً)
        
        Args:
            name_col: عمود الأسماء
            threshold: عتبة التشابه (0-1)، القيمة الافتراضية 0.90 (90%)
            additional_cols: أعمدة إضافية للتحقق منها
            
        Returns:
            DataFrame بالتكرارات الضبابية
        """
        logger.info(f"البحث عن تكرارات ضبابية (عتبة: {threshold*100}%)...")
        
        if name_col not in self.df.columns:
            raise ValueError(f"العمود {name_col} غير موجود")
        
        fuzzy_matches = []
        df_work = self.df.copy()
        df_work[name_col] = df_work[name_col].fillna('').astype(str).str.strip()
        
        # تنظيف وتطبيع الأسماء
        df_work['_normalized_name'] = df_work[name_col].str.lower().str.replace(r'\s+', ' ', regex=True)
        
        unique_names = df_work['_normalized_name'].unique()
        
        for i, name1 in enumerate(unique_names):
            if not name1:
                continue
            for name2 in unique_names[i+1:]:
                if not name2:
                    continue
                
                # حساب نسبة التشابه
                similarity = SequenceMatcher(None, name1, name2).ratio()
                
                if similarity >= threshold:
                    # جلب جميع السجلات المطابقة
                    rows1 = df_work[df_work['_normalized_name'] == name1]
                    rows2 = df_work[df_work['_normalized_name'] == name2]
                    
                    # التحقق من الأعمدة الإضافية إن وجدت
                    match = True
                    if additional_cols:
                        for col in additional_cols:
                            if col in df_work.columns:
                                if rows1[col].iloc[0] != rows2[col].iloc[0]:
                                    match = False
                                    break
                    
                    if match:
                        fuzzy_matches.append({
                            'name1': name1,
                            'name2': name2,
                            'similarity': similarity,
                            'count1': len(rows1),
                            'count2': len(rows2),
                            'original_name1': rows1[name_col].iloc[0],
                            'original_name2': rows2[name_col].iloc[0]
                        })
        
        if fuzzy_matches:
            fuzzy_df = pd.DataFrame(fuzzy_matches)
            logger.info(f"تم العثور على {len(fuzzy_df)} تطابق ضبابي")
            return fuzzy_df
        else:
            logger.info("لم يتم العثور على تطابقات ضبابية")
            return pd.DataFrame()
    
    def find_partial_duplicates(self,
                               columns: List[str],
                               min_matching_cols: int = 2) -> pd.DataFrame:
        """
        البحث عن تكرارات جزئية (تطابق في بعض الأعمدة وليس كلها)
        
        Args:
            columns: الأعمدة للمقارنة
            min_matching_cols: الحد الأدنى من الأعمدة المتطابقة
            
        Returns:
            DataFrame بالتكرارات الجزئية
        """
        logger.info(f"البحث عن تكرارات جزئية (حد أدنى: {min_matching_cols} عمود)...")
        
        partial_duplicates = []
        
        # إنشاء جميع التوليفات الممكنة
        from itertools import combinations
        
        for r in range(min_matching_cols, len(columns) + 1):
            for col_combination in combinations(columns, r):
                mask = self.df.duplicated(subset=list(col_combination), keep=False)
                if mask.any():
                    dups = self.df[mask].copy()
                    dups['matching_columns'] = ', '.join(col_combination)
                    dups['match_count'] = len(col_combination)
                    partial_duplicates.append(dups)
        
        if partial_duplicates:
            result = pd.concat(partial_duplicates, ignore_index=True)
            result = result.drop_duplicates()
            logger.info(f"تم العثور على {len(result)} تكرار جزئي")
            return result
        else:
            return pd.DataFrame()
    
    def _find_duplicates_with_time_window(self,
                                         df: pd.DataFrame,
                                         comparison_cols: List[str],
                                         date_col: str,
                                         window_days: int) -> pd.DataFrame:
        """البحث عن التكرارات ضمن نافذة زمنية محددة"""
        duplicates = []
        
        # تجميع حسب الأعمدة المقارنة
        grouped = df.groupby(comparison_cols)
        
        for name, group in grouped:
            if len(group) < 2:
                continue
            
            # فرز حسب التاريخ
            group = group.sort_values(date_col)
            dates = group[date_col].values
            
            # التحقق من وجود تكرارات ضمن النافذة الزمنية
            for i in range(len(dates)):
                for j in range(i + 1, len(dates)):
                    time_diff = (dates[j] - dates[i]) / np.timedelta64(1, 'D')
                    
                    if time_diff <= window_days:
                        duplicates.extend([group.iloc[i], group.iloc[j]])
        
        if duplicates:
            result = pd.DataFrame(duplicates)
            result['duplicate_group'] = result.groupby(comparison_cols).ngroup()
            return result
        else:
            return pd.DataFrame()
    
    def _calculate_duplicate_stats(self, duplicates: pd.DataFrame, comparison_cols: List[str]) -> None:
        """حساب إحصائيات التكرارات"""
        self.stats = {
            'total_duplicates': len(duplicates),
            'duplicate_groups': duplicates['duplicate_group'].nunique(),
            'duplicate_rate': len(duplicates) / len(self.df) * 100,
            'avg_duplicates_per_group': len(duplicates) / duplicates['duplicate_group'].nunique(),
        }
        
        # إحصائيات حسب الأعمدة
        for col in comparison_cols:
            if col in duplicates.columns:
                self.stats[f'unique_{col}'] = duplicates[col].nunique()
    
    def get_duplicate_summary(self) -> Dict:
        """
        الحصول على ملخص التكرارات
        
        Returns:
            قاموس بإحصائيات التكرارات
        """
        if self.duplicates is None or len(self.duplicates) == 0:
            return {'message': 'لم يتم العثور على تكرارات'}
        
        summary = {
            'statistics': self.stats,
            'top_duplicate_groups': self._get_top_duplicate_groups(10),
            'duplicate_details': self.duplicates.to_dict('records')[:100]  # أول 100 سجل
        }
        
        return summary
    
    def _get_top_duplicate_groups(self, n: int = 10) -> List[Dict]:
        """الحصول على أكثر المجموعات تكراراً"""
        if self.duplicates is None or len(self.duplicates) == 0:
            return []
        
        top_groups = (
            self.duplicates.groupby('duplicate_group')
            .size()
            .sort_values(ascending=False)
            .head(n)
        )
        
        result = []
        for group_id, count in top_groups.items():
            group_data = self.duplicates[self.duplicates['duplicate_group'] == group_id].iloc[0]
            result.append({
                'group_id': int(group_id),
                'count': int(count),
                'sample': group_data.to_dict()
            })
        
        return result
    
    def export_duplicates(self, output_path: str) -> None:
        """
        تصدير التكرارات إلى ملف Excel
        
        Args:
            output_path: مسار الملف للحفظ
        """
        if self.duplicates is None or len(self.duplicates) == 0:
            logger.warning("لا توجد تكرارات للتصدير")
            return
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            self.duplicates.to_excel(writer, sheet_name='Duplicates', index=False)
            
            # إضافة ملخص
            summary_df = pd.DataFrame([self.stats])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        logger.info(f"تم تصدير التكرارات إلى: {output_path}")


def analyze_duplicates(df: pd.DataFrame,
                       entity_col: str,
                       amount_col: str,
                       event_col: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    دالة مساعدة سريعة لتحليل الدفعات المكررة
    
    Args:
        df: DataFrame للتحليل
        entity_col: عمود الجهة
        amount_col: عمود المبلغ
        event_col: عمود الحدث (اختياري)
        
    Returns:
        (DataFrame بالتكرارات، إحصائيات)
    """
    analyzer = DuplicateAnalyzer(df)
    duplicates = analyzer.find_payment_duplicates(entity_col, amount_col, event_col=event_col)
    stats = analyzer.get_duplicate_summary()
    
    return duplicates, stats
