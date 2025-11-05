# -*- coding: utf-8 -*-
"""
محلل الانحرافات والشذوذات - كشف القيم الشاذة إحصائياً
يدعم: IQR, Z-Score, Isolation Forest, DBSCAN
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """كاشف الانحرافات والشذوذات المتقدم"""
    
    def __init__(self, df: pd.DataFrame):
        """
        تهيئة الكاشف
        
        Args:
            df: DataFrame للتحليل
        """
        self.df = df.copy()
        self.anomalies: Optional[pd.DataFrame] = None
        self.stats: Dict = {}
    
    def detect_iqr_anomalies(self,
                            column: str,
                            multiplier: float = 1.5) -> pd.DataFrame:
        """
        كشف الشذوذات باستخدام IQR (Interquartile Range)
        
        Args:
            column: العمود للتحليل
            multiplier: معامل IQR (1.5 = قياسي، 3.0 = متحفظ)
            
        Returns:
            DataFrame بالشذوذات
        """
        logger.info(f"كشف الشذوذات في {column} باستخدام IQR...")
        
        if column not in self.df.columns:
            raise ValueError(f"العمود {column} غير موجود")
        
        # حساب IQR
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # حساب الحدود
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        # تحديد الشذوذات
        mask = (self.df[column] < lower_bound) | (self.df[column] > upper_bound)
        anomalies = self.df[mask].copy()
        
        if len(anomalies) > 0:
            anomalies['anomaly_type'] = 'IQR'
            anomalies['anomaly_score'] = anomalies[column].apply(
                lambda x: abs(x - Q3) / IQR if x > upper_bound else abs(Q1 - x) / IQR
            )
            anomalies['lower_bound'] = lower_bound
            anomalies['upper_bound'] = upper_bound
        
        logger.info(f"تم العثور على {len(anomalies)} شذوذ ({len(anomalies)/len(self.df)*100:.2f}%)")
        
        return anomalies
    
    def detect_zscore_anomalies(self,
                               column: str,
                               threshold: float = 3.0) -> pd.DataFrame:
        """
        كشف الشذوذات باستخدام Z-Score
        
        Args:
            column: العمود للتحليل
            threshold: عتبة Z-Score (القيمة الافتراضية: 3.0)
            
        Returns:
            DataFrame بالشذوذات
        """
        logger.info(f"كشف الشذوذات في {column} باستخدام Z-Score...")
        
        try:
            if column not in self.df.columns:
                raise ValueError(f"العمود {column} غير موجود")
            
            # الحصول على البيانات غير الفارغة
            valid_data = self.df[column].dropna()
            valid_indices = self.df[column].notna()
            
            # حساب Z-Score
            z_scores = np.abs(stats.zscore(valid_data))
            
            # تحديد الشذوذات
            anomaly_mask = z_scores > threshold
            
            # الحصول على الصفوف الكاملة للشذوذات
            anomalies = self.df[valid_indices].iloc[anomaly_mask].copy()
            
            if len(anomalies) > 0:
                anomalies['anomaly_type'] = 'Z-Score'
                anomalies['z_score'] = z_scores[anomaly_mask].values
                anomalies['anomaly_score'] = (z_scores[anomaly_mask] / threshold).values
            
            logger.info(f"تم العثور على {len(anomalies)} شذوذ ({len(anomalies)/len(self.df)*100:.2f}%)")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"خطأ في Z-Score: {e}")
            return pd.DataFrame()
    
    def detect_isolation_forest_anomalies(self,
                                         columns: List[str],
                                         contamination: float = 0.1) -> pd.DataFrame:
        """
        كشف الشذوذات باستخدام Isolation Forest (Machine Learning)
        
        Args:
            columns: الأعمدة للتحليل
            contamination: نسبة الشذوذات المتوقعة (0.1 = 10%)
            
        Returns:
            DataFrame بالشذوذات
        """
        logger.info(f"كشف الشذوذات في {columns} باستخدام Isolation Forest...")
        
        # التحقق من الأعمدة
        missing = [col for col in columns if col not in self.df.columns]
        if missing:
            raise ValueError(f"الأعمدة غير موجودة: {missing}")
        
        # إعداد البيانات
        data = self.df[columns].dropna()
        
        if len(data) < 10:
            logger.warning("عدد السجلات قليل جداً لتطبيق Isolation Forest")
            return pd.DataFrame()
        
        # تدريب النموذج
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        predictions = iso_forest.fit_predict(data)
        scores = iso_forest.score_samples(data)
        
        # تحديد الشذوذات (-1 = شذوذ، 1 = عادي)
        anomaly_mask = predictions == -1
        anomalies = data[anomaly_mask].copy()
        
        if len(anomalies) > 0:
            anomalies['anomaly_type'] = 'Isolation_Forest'
            anomalies['anomaly_score'] = np.abs(scores[anomaly_mask])
        
        logger.info(f"تم العثور على {len(anomalies)} شذوذ ({len(anomalies)/len(self.df)*100:.2f}%)")
        
        return anomalies
    
    def detect_dbscan_anomalies(self,
                               columns: List[str],
                               eps: float = 0.5,
                               min_samples: int = 5) -> pd.DataFrame:
        """
        كشف الشذوذات باستخدام DBSCAN (Clustering)
        
        Args:
            columns: الأعمدة للتحليل
            eps: مسافة الجوار
            min_samples: الحد الأدنى من العينات للتجمع
            
        Returns:
            DataFrame بالشذوذات
        """
        logger.info(f"كشف الشذوذات في {columns} باستخدام DBSCAN...")
        
        # التحقق من الأعمدة
        missing = [col for col in columns if col not in self.df.columns]
        if missing:
            raise ValueError(f"الأعمدة غير موجودة: {missing}")
        
        # إعداد البيانات
        data = self.df[columns].dropna()
        
        if len(data) < min_samples:
            logger.warning(f"عدد السجلات ({len(data)}) أقل من min_samples ({min_samples})")
            return pd.DataFrame()
        
        # تطبيع البيانات
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        
        # تطبيق DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = dbscan.fit_predict(data_scaled)
        
        # -1 تعني نقاط شاذة (noise)
        anomaly_mask = clusters == -1
        anomalies = data[anomaly_mask].copy()
        
        if len(anomalies) > 0:
            anomalies['anomaly_type'] = 'DBSCAN'
            anomalies['cluster'] = -1
        
        logger.info(f"تم العثور على {len(anomalies)} شذوذ ({len(anomalies)/len(self.df)*100:.2f}%)")
        
        return anomalies
    
    def detect_all_anomalies(self,
                           column: str,
                           iqr_multiplier: float = 1.5,
                           zscore_threshold: float = 3.0) -> Dict[str, pd.DataFrame]:
        """
        كشف الشذوذات باستخدام جميع الطرق المتاحة
        
        Args:
            column: العمود للتحليل
            iqr_multiplier: معامل IQR
            zscore_threshold: عتبة Z-Score
            
        Returns:
            قاموس بنتائج كل طريقة
        """
        logger.info(f"تطبيق جميع طرق كشف الشذوذات على {column}...")
        
        results = {}
        
        try:
            results['iqr'] = self.detect_iqr_anomalies(column, iqr_multiplier)
        except Exception as e:
            logger.error(f"خطأ في IQR: {e}")
            results['iqr'] = pd.DataFrame()
        
        try:
            results['zscore'] = self.detect_zscore_anomalies(column, zscore_threshold)
        except Exception as e:
            logger.error(f"خطأ في Z-Score: {e}")
            results['zscore'] = pd.DataFrame()
        
        try:
            results['isolation_forest'] = self.detect_isolation_forest_anomalies([column])
        except Exception as e:
            logger.error(f"خطأ في Isolation Forest: {e}")
            results['isolation_forest'] = pd.DataFrame()
        
        # دمج النتائج
        all_anomalies = []
        for method, df in results.items():
            if len(df) > 0:
                all_anomalies.append(df)
        
        if all_anomalies:
            self.anomalies = pd.concat(all_anomalies, ignore_index=True)
            self.anomalies = self.anomalies.drop_duplicates()
        
        return results
    
    def get_statistical_summary(self, column: str) -> Dict:
        """
        الحصول على ملخص إحصائي شامل
        
        Args:
            column: العمود للتحليل
            
        Returns:
            قاموس بالإحصائيات
        """
        if column not in self.df.columns:
            raise ValueError(f"العمود {column} غير موجود")
        
        data = self.df[column].dropna()
        
        summary = {
            'count': len(data),
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'range': data.max() - data.min(),
            'q1': data.quantile(0.25),
            'q3': data.quantile(0.75),
            'iqr': data.quantile(0.75) - data.quantile(0.25),
            'skewness': data.skew(),
            'kurtosis': data.kurtosis(),
            'cv': (data.std() / data.mean() * 100) if data.mean() != 0 else 0,  # Coefficient of Variation
        }
        
        return summary
    
    def compare_groups(self,
                      value_column: str,
                      group_column: str) -> pd.DataFrame:
        """
        مقارنة الإحصائيات بين المجموعات
        
        Args:
            value_column: عمود القيم
            group_column: عمود التصنيف
            
        Returns:
            DataFrame بالمقارنة
        """
        logger.info(f"مقارنة {value_column} حسب {group_column}...")
        
        comparison = self.df.groupby(group_column)[value_column].agg([
            'count',
            'mean',
            'median',
            'std',
            'min',
            'max',
            ('q25', lambda x: x.quantile(0.25)),
            ('q75', lambda x: x.quantile(0.75))
        ]).round(2)
        
        comparison['cv'] = (comparison['std'] / comparison['mean'] * 100).round(2)
        comparison = comparison.sort_values('mean', ascending=False)
        
        return comparison
    
    def export_anomalies(self, output_path: str) -> None:
        """
        تصدير الشذوذات إلى ملف Excel
        
        Args:
            output_path: مسار الملف للحفظ
        """
        if self.anomalies is None or len(self.anomalies) == 0:
            logger.warning("لا توجد شذوذات للتصدير")
            return
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            self.anomalies.to_excel(writer, sheet_name='Anomalies', index=False)
            
            # إحصائيات
            stats_df = pd.DataFrame([self.stats])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        logger.info(f"تم تصدير الشذوذات إلى: {output_path}")


def detect_anomalies(df: pd.DataFrame,
                    column: str,
                    method: str = 'iqr') -> Tuple[pd.DataFrame, Dict]:
    """
    دالة مساعدة سريعة لكشف الشذوذات
    
    Args:
        df: DataFrame للتحليل
        column: العمود للتحليل
        method: الطريقة ('iqr', 'zscore', 'all')
        
    Returns:
        (DataFrame بالشذوذات، إحصائيات)
    """
    detector = AnomalyDetector(df)
    
    if method == 'iqr':
        anomalies = detector.detect_iqr_anomalies(column)
    elif method == 'zscore':
        anomalies = detector.detect_zscore_anomalies(column)
    elif method == 'all':
        results = detector.detect_all_anomalies(column)
        anomalies = detector.anomalies
    else:
        raise ValueError(f"طريقة غير معروفة: {method}")
    
    stats = detector.get_statistical_summary(column)
    
    return anomalies, stats
