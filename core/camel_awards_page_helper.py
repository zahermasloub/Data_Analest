# -*- coding: utf-8 -*-
"""
مساعد صفحة تحليل جوائز سباقات الهجن
Camel Awards Page Helper for Streamlit Integration
===================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

from core.enhanced_audit_system import (
    DataNormalizer,
    EnhancedBankMatcher,
    GroundTruthValidator,
    ComprehensiveReportGenerator
)


def detect_duplicates_enhanced(
    df: pd.DataFrame,
    normalizer: DataNormalizer
) -> pd.DataFrame:
    """
    كشف التكرارات باستخدام المفتاح المركب
    
    Composite Key:
        Season + Race + OwnerNumber + OwnerName + OwnerQatariID + AwardAmount
    """
    # الحقول المطلوبة
    required_fields = ['Season', 'Race', 'OwnerNumber', 'OwnerName', 'OwnerQatariID', 'AwardAmount']
    
    # التحقق من وجود الحقول
    missing_fields = [f for f in required_fields if f not in df.columns]
    if missing_fields:
        print(f"⚠️ حقول مفقودة: {missing_fields}")
        # استخدام الحقول المتاحة فقط
        available_fields = [f for f in required_fields if f in df.columns]
        if not available_fields:
            return pd.DataFrame()
    else:
        available_fields = required_fields
    
    # إنشاء المفتاح المركب (استخدام list comprehension بدلاً من += لتجنب مشاكل NotImplementedType)
    df_composite = df.copy()
    
    # بناء المفتاح المركب بطريقة آمنة
    key_parts = []
    for field in available_fields:
        try:
            # تحويل آمن لـ string مع معالجة جميع أنواع البيانات
            field_values = df_composite[field].fillna('').apply(lambda x: str(x) if pd.notna(x) else '')
            key_parts.append(field_values)
        except Exception as e:
            print(f"   ⚠️ تخطي حقل {field} في المفتاح المركب: {str(e)}")
            continue
    
    # دمج جميع الأجزاء بـ '|'
    if key_parts:
        df_composite['CompositeKey'] = key_parts[0].astype(str)
        for part in key_parts[1:]:
            df_composite['CompositeKey'] = df_composite['CompositeKey'] + '|' + part.astype(str)
    else:
        # في حالة عدم وجود حقول صالحة، استخدم index
        df_composite['CompositeKey'] = df_composite.index.astype(str)
    
    df_composite['CompositeKey'] = df_composite['CompositeKey'].str.strip('|')
    
    # حساب عدد التكرارات
    key_counts = df_composite['CompositeKey'].value_counts()
    duplicates = key_counts[key_counts > 1]
    
    if len(duplicates) == 0:
        return pd.DataFrame()
    
    # تصفية السجلات المكررة
    duplicates_df = df_composite[df_composite['CompositeKey'].isin(duplicates.index)].copy()
    
    # إضافة معلومات التكرار
    duplicates_df['DuplicateCount'] = duplicates_df['CompositeKey'].map(key_counts)
    duplicates_df['DuplicateGroup'] = duplicates_df.groupby('CompositeKey').ngroup() + 1
    
    # ترتيب حسب المجموعة
    duplicates_df = duplicates_df.sort_values(['DuplicateGroup', 'CompositeKey'])
    
    return duplicates_df


def run_comprehensive_audit(
    awards_data: pd.DataFrame,
    bank_data: Optional[pd.DataFrame] = None,
    ground_truth_data: Optional[pd.DataFrame] = None,
    use_composite_key: bool = True,
    enable_bank_matching: bool = True,
    enable_ground_truth: bool = True
) -> Dict:
    """
    تنفيذ التدقيق الشامل
    
    Args:
        awards_data: بيانات الجوائز
        bank_data: كشف البنك (اختياري)
        ground_truth_data: بيانات الحقيقة الأرضية (اختياري)
        use_composite_key: استخدام المفتاح المركب
        enable_bank_matching: تفعيل مطابقة البنك
        enable_ground_truth: تفعيل التحقق من الحقيقة الأرضية
        
    Returns:
        Dict يحتوي على جميع النتائج
    """
    results = {}
    
    # 1. تطبيع البيانات
    print("📊 تطبيع بيانات الجوائز...")
    normalizer = DataNormalizer()
    normalized_awards = normalizer.normalize_dataframe(
        awards_data.copy(),
        df_name="Awards"
    )
    results['normalized_awards'] = normalized_awards
    results['normalization_mapping'] = normalizer.get_mapping_documentation()
    
    # 2. كشف التكرارات
    print("🔍 كشف التكرارات...")
    if use_composite_key:
        duplicates = detect_duplicates_enhanced(normalized_awards, normalizer)
    else:
        # استخدام طريقة بسيطة
        duplicates = normalized_awards[normalized_awards.duplicated(keep=False)]
    
    # تنظيف الأعمدة المكررة في نتائج التكرارات (PyArrow لا يدعمها)
    if not duplicates.empty and duplicates.columns.duplicated().any():
        print(f"   ⚠️ إزالة {duplicates.columns.duplicated().sum()} عمود مكرر من نتائج التكرارات")
        duplicates = duplicates.loc[:, ~duplicates.columns.duplicated(keep='first')]
    
    results['duplicates'] = duplicates
    results['duplicate_stats'] = {
        'total_records': len(normalized_awards),
        'duplicate_records': len(duplicates),
        'duplicate_percentage': (len(duplicates) / len(normalized_awards) * 100) if len(normalized_awards) > 0 else 0,
        'unique_duplicate_groups': duplicates['DuplicateGroup'].nunique() if 'DuplicateGroup' in duplicates.columns else 0
    }
    
    # 3. مطابقة البنك
    bank_matches = None
    bank_match_stats = None
    
    if enable_bank_matching and bank_data is not None and len(bank_data) > 0:
        print("🏦 مطابقة كشف البنك...")
        try:
            matcher = EnhancedBankMatcher()
            bank_matches = matcher.match_awards_to_bank(
                normalized_awards,
                bank_data.copy()
            )
            
            # حساب إحصائيات المطابقة
            if bank_matches is not None and len(bank_matches) > 0:
                bank_match_stats = {
                    'total_matched': len(bank_matches[bank_matches['MatchStatus'].str.contains('Matched', case=False, na=False)]),
                    'exact_matches': len(bank_matches[bank_matches['MatchStatus'] == 'Matched']),
                    'fuzzy_matches': len(bank_matches[bank_matches['MatchStatus'] == 'Partial Match']),
                    'not_matched': len(bank_matches[bank_matches['MatchStatus'] == 'Not Matched'])
                }
        except Exception as e:
            print(f"❌ خطأ في مطابقة البنك: {e}")
            bank_matches = None
            bank_match_stats = None
    
    results['bank_matches'] = bank_matches
    results['bank_match_stats'] = bank_match_stats
    
    # 4. التحقق من الحقيقة الأرضية
    validation_results = None
    validation_metrics = None
    
    if enable_ground_truth and ground_truth_data is not None and len(ground_truth_data) > 0:
        print("✅ التحقق من الحقيقة الأرضية...")
        try:
            validator = GroundTruthValidator()
            validation_results = validator.validate_detection(duplicates)
            
            if validation_results:
                # استخراج المقاييس
                validation_metrics = {
                    'accuracy': validation_results.get('accuracy', 0),
                    'recall': validation_results.get('recall', 0),
                    'precision': validation_results.get('precision', 0),
                    'f1_score': validation_results.get('f1_score', 0),
                    'true_positive': validation_results.get('true_positive', 0),
                    'false_positive': validation_results.get('false_positive', 0),
                    'true_negative': validation_results.get('true_negative', 0),
                    'false_negative': validation_results.get('false_negative', 0),
                    'confusion_matrix': {
                        'true_positive': validation_results.get('true_positive', 0),
                        'false_positive': validation_results.get('false_positive', 0),
                        'true_negative': validation_results.get('true_negative', 0),
                        'false_negative': validation_results.get('false_negative', 0)
                    }
                }
        except Exception as e:
            print(f"❌ خطأ في التحقق: {e}")
            validation_results = None
            validation_metrics = None
    
    results['validation'] = validation_results
    results['validation_metrics'] = validation_metrics
    
    return results


def generate_reports(
    results: Dict,
    output_dir: Path,
    timestamp: str
) -> Dict[str, str]:
    """
    إنشاء التقارير الشاملة
    
    Args:
        results: نتائج التدقيق
        output_dir: مجلد الحفظ
        timestamp: الطابع الزمني
        
    Returns:
        Dict يحتوي على مسارات التقارير
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # إعادة إنشاء الكائنات اللازمة من results
    # (لأن ComprehensiveReportGenerator يحتاج الكائنات وليس البيانات مباشرة)
    
    # إنشاء normalizer جديد
    normalizer = DataNormalizer()
    
    # إنشاء bank_matcher
    bank_matcher = EnhancedBankMatcher()
    
    # إنشاء ground_truth_validator
    ground_truth_validator = GroundTruthValidator()
    
    # إنشاء مولد التقارير بالتوقيع الصحيح
    report_generator = ComprehensiveReportGenerator(
        duplicates=results['duplicates'],
        normalizer=normalizer,
        bank_matcher=bank_matcher,
        ground_truth_validator=ground_truth_validator,
        output_dir=str(output_dir)
    )
    
    report_paths = report_generator.generate_all_reports()
    
    return report_paths
