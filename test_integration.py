#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار التكامل الكامل - Camel Awards Analyzer v2.0
=====================================================

هذا الملف يختبر التكامل الكامل بين:
1. CamelAwardsAnalyzer (المحلل الرئيسي)
2. AdvancedMatcher (مطابقة 3 طبقات)
3. AuditLogger (تسجيل شامل)
4. PerformanceOptimizer (تحسين الأداء)

الاستخدام:
    python test_integration.py
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# إضافة core إلى مسار البحث
sys.path.insert(0, str(Path(__file__).parent))

from core.camel_awards_analyzer import CamelAwardsAnalyzer

def create_sample_awards_data(num_records: int = 50) -> pd.DataFrame:
    """
    إنشاء بيانات جوائز تجريبية
    """
    import numpy as np
    
    owners = [
        'محمد بن سالم الكعبي',
        'عبدالله بن خالد السويدي',
        'فاطمة بنت راشد الهاجري',
        'سعيد بن محمد النعيمي',
        'منصور بن علي القبيسي'
    ]
    
    races = ['هجن الشيوخ', 'هجن الأشواط الرئيسية', 'هجن المفتوحة', 'هجن الملاك']
    seasons = ['2023-2024', '2024-2025']
    
    data = []
    for i in range(num_records):
        data.append({
            'OwnerName': np.random.choice(owners),
            'Race': np.random.choice(races),
            'Season': np.random.choice(seasons),
            'AwardAmount': np.random.choice([5000, 10000, 15000, 20000, 25000]),
            'EntryDate': datetime.now() - timedelta(days=np.random.randint(1, 30))
        })
    
    return pd.DataFrame(data)

def create_sample_bank_data(awards_df: pd.DataFrame, match_rate: float = 0.7) -> pd.DataFrame:
    """
    إنشاء كشف بنك تجريبي (70% مطابق، 30% مختلف)
    """
    import numpy as np
    
    bank_data = []
    num_matches = int(len(awards_df) * match_rate)
    
    # إضافة السجلات المطابقة
    for idx, row in awards_df.head(num_matches).iterrows():
        # مطابقة تامة
        if np.random.random() < 0.5:
            bank_name = row['OwnerName']
        else:
            # مطابقة ضبابية (تعديل بسيط في الاسم)
            bank_name = row['OwnerName'].replace('بن', 'ابن').replace('محمد', 'محمّد')
        
        bank_data.append({
            'BankName': bank_name,
            'BankAmount': row['AwardAmount'],
            'BankDate': row['EntryDate'] + timedelta(days=np.random.randint(-3, 5)),
            'BankReference': f'REF-{idx:05d}'
        })
    
    # إضافة سجلات غير مطابقة
    for i in range(len(awards_df) - num_matches):
        bank_data.append({
            'BankName': 'شخص غير موجود',
            'BankAmount': 999.99,
            'BankDate': datetime.now(),
            'BankReference': f'REF-UNMATCH-{i:05d}'
        })
    
    return pd.DataFrame(bank_data)

def test_basic_integration():
    """
    اختبار التكامل الأساسي (بدون المكونات المتقدمة)
    """
    print("="*70)
    print("🧪 اختبار 1: التكامل الأساسي (Exact + Fuzzy فقط)")
    print("="*70)
    
    try:
        # إنشاء البيانات التجريبية
        awards_df = create_sample_awards_data(50)
        bank_df = create_sample_bank_data(awards_df, match_rate=0.7)
        
        # حفظ الملفات مؤقتاً
        Path('outputs/test').mkdir(parents=True, exist_ok=True)
        awards_df.to_excel('outputs/test/sample_awards.xlsx', index=False)
        bank_df.to_excel('outputs/test/sample_bank.xlsx', index=False)
        
        # إنشاء المحلل (بدون المكونات المتقدمة)
        analyzer = CamelAwardsAnalyzer(use_advanced_features=False)
        
        # تحميل البيانات
        print("\n📊 تحميل البيانات...")
        analyzer.awards_data = awards_df
        analyzer.awards_data['OwnerName_norm'] = analyzer.awards_data['OwnerName'].apply(
            analyzer.normalize_text
        )
        
        analyzer.bank_data = bank_df
        analyzer.bank_data['BankName_norm'] = analyzer.bank_data['BankName'].apply(
            analyzer.normalize_text
        )
        
        # المطابقة
        print("\n🔍 بدء المطابقة الأساسية...")
        results = analyzer.match_with_bank(time_window_days=7)
        
        # عرض النتائج
        print("\n📈 النتائج:")
        print(f"   إجمالي السجلات: {len(results)}")
        print(f"   مطابقات ناجحة: {len(results[results['StatusFlag'] == '✅'])}")
        print(f"   غير مطابق: {len(results[results['StatusFlag'] == '⚠️'])}")
        
        # التصدير
        output_path = analyzer.export_report('outputs/test/basic_report.xlsx')
        print(f"\n✅ تم حفظ التقرير: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ فشل الاختبار: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_integration():
    """
    اختبار التكامل المتقدم (مع جميع المكونات)
    """
    print("\n" + "="*70)
    print("🚀 اختبار 2: التكامل المتقدم (3 طبقات + Audit + Optimizer)")
    print("="*70)
    
    try:
        # إنشاء البيانات التجريبية
        awards_df = create_sample_awards_data(100)
        bank_df = create_sample_bank_data(awards_df, match_rate=0.8)
        
        # حفظ الملفات مؤقتاً
        awards_df.to_excel('outputs/test/sample_awards_advanced.xlsx', index=False)
        bank_df.to_excel('outputs/test/sample_bank_advanced.xlsx', index=False)
        
        # إنشاء المحلل (مع المكونات المتقدمة)
        analyzer = CamelAwardsAnalyzer(use_advanced_features=True)
        
        # تحميل البيانات
        print("\n📊 تحميل البيانات...")
        analyzer.awards_data = awards_df
        analyzer.awards_data['OwnerName_norm'] = analyzer.awards_data['OwnerName'].apply(
            analyzer.normalize_text
        )
        
        analyzer.bank_data = bank_df
        analyzer.bank_data['BankName_norm'] = analyzer.bank_data['BankName'].apply(
            analyzer.normalize_text
        )
        
        # المطابقة (مع Record Linkage)
        print("\n🔍 بدء المطابقة المتقدمة...")
        results = analyzer.match_with_bank(
            time_window_days=7,
            use_record_linkage=True,
            files_info={
                'awards_files': ['sample_awards_advanced.xlsx'],
                'bank_file': 'sample_bank_advanced.xlsx'
            }
        )
        
        # عرض النتائج
        print("\n📈 النتائج:")
        if analyzer.statistics:
            stats = analyzer.statistics
            print(f"   إجمالي الجوائز: {stats.get('total_awards', 0)}")
            print(f"   إجمالي البنك: {stats.get('total_bank_records', 0)}")
            print(f"   مطابقات Exact: {stats.get('exact_matches', 0)}")
            print(f"   مطابقات Fuzzy: {stats.get('fuzzy_matches', 0)}")
            print(f"   مطابقات RL: {stats.get('rl_matches', 0)}")
            print(f"   غير مطابق: {stats.get('unmatched_awards', 0)}")
            print(f"   وقت التنفيذ: {stats.get('execution_time', 0):.2f} ثانية")
        
        # التصدير
        output_path = analyzer.export_report('outputs/test/advanced_report.xlsx')
        print(f"\n✅ تم حفظ التقرير: {output_path}")
        
        # عرض RunID
        if analyzer.current_run_id:
            print(f"\n📝 RunID: {analyzer.current_run_id}")
            print(f"   يمكنك الاطلاع على السجل في: outputs/audit_logs/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ فشل الاختبار: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    تشغيل جميع الاختبارات
    """
    print("\n" + "🎯"*35)
    print("   Camel Awards Analyzer v2.0 - اختبار التكامل الكامل")
    print("🎯"*35 + "\n")
    
    results = []
    
    # اختبار 1: التكامل الأساسي
    results.append(("التكامل الأساسي", test_basic_integration()))
    
    # اختبار 2: التكامل المتقدم
    results.append(("التكامل المتقدم", test_advanced_integration()))
    
    # عرض النتيجة النهائية
    print("\n" + "="*70)
    print("📊 ملخص الاختبارات")
    print("="*70)
    
    for name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"   {name}: {status}")
    
    total_passed = sum(1 for _, r in results if r)
    print(f"\nالنتيجة النهائية: {total_passed}/{len(results)} اجتازوا الاختبار")
    
    if total_passed == len(results):
        print("\n🎉 رائع! جميع الاختبارات نجحت!")
    else:
        print("\n⚠️ بعض الاختبارات فشلت. يرجى مراجعة السجلات.")

if __name__ == "__main__":
    main()
