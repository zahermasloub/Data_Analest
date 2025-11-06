"""
اختبار المطابقة على dataset كبير (66K جائزة)
مع التحسينات لتقليل استهلاك الذاكرة
"""

import pandas as pd
from core.camel_awards_analyzer import CamelAwardsAnalyzer
import time

print("=" * 80)
print("🔬 اختبار المطابقة على Dataset كبير")
print("=" * 80)

# تهيئة المحلل
analyzer = CamelAwardsAnalyzer()

# تحميل البيانات
print("\n📂 تحميل البيانات...")

try:
    # تحميل الجوائز
    awards_files = [
        'الملفات/AwardsForSeason2022-2023.xlsx',
        'الملفات/AwardsForSeason2023-2024.xlsx'
    ]
    
    analyzer.load_awards_files(awards_files)
    
    # تحميل كشف البنك
    analyzer.load_bank_statement('الملفات/ملف البنك.xlsx')
    
    print(f"   ✓ الجوائز: {len(analyzer.awards_data):,} سجل")
    print(f"   ✓ البنك: {len(analyzer.bank_data):,} سجل")
    
    # عرض معلومات عن References
    if 'paymentreference' in analyzer.awards_data.columns:
        awards_with_ref = analyzer.awards_data[
            analyzer.awards_data['paymentreference'].notna() &
            (analyzer.awards_data['paymentreference'] != '')
        ]
        print(f"   📋 جوائز لديها Reference: {len(awards_with_ref):,} ({len(awards_with_ref)/len(analyzer.awards_data)*100:.1f}%)")
    
    # إجراء المطابقة
    print("\n" + "=" * 80)
    start_time = time.time()
    
    results = analyzer.match_with_bank()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print("=" * 80)
    print(f"\n✅ اكتملت المطابقة في {elapsed:.2f} ثانية")
    print("=" * 80)
    
    # عرض الإحصائيات
    print("\n📊 توزيع الحالات:")
    print("-" * 80)
    
    match_types = results['MatchType'].value_counts()
    for match_type, count in match_types.items():
        percentage = count / len(results) * 100
        
        if match_type == 'No Match':
            icon = '⚠️'
        elif match_type in ['Reference-Exact', 'Exact']:
            icon = '✅'
        elif match_type == 'Reference-Diff':
            icon = '⚠️'
        else:
            icon = '🔍'
        
        print(f"   {icon} {match_type:20s}: {count:6,} سجل ({percentage:5.1f}%)")
    
    print("-" * 80)
    print(f"   📊 إجمالي: {len(results):,} سجل")
    
    # تفاصيل المطابقات
    matched_results = results[results['MatchType'] != 'No Match']
    unmatched_results = results[results['MatchType'] == 'No Match']
    
    print(f"\n   ✅ مطابقات ناجحة: {len(matched_results):,} ({len(matched_results)/len(results)*100:.1f}%)")
    print(f"   ⚠️  غير مطابق: {len(unmatched_results):,} ({len(unmatched_results)/len(results)*100:.1f}%)")
    
    # أمثلة على المطابقات الناجحة
    if len(matched_results) > 0:
        print("\n" + "=" * 80)
        print("🎯 أمثلة على المطابقات الناجحة:")
        print("=" * 80)
        
        # Reference-Exact
        ref_exact = results[results['MatchType'] == 'Reference-Exact']
        if len(ref_exact) > 0:
            print(f"\n✅ Reference-Exact ({len(ref_exact):,} مطابقة):")
            sample = ref_exact.head(3)
            for idx, row in sample.iterrows():
                print(f"   • {row['OwnerName'][:40]:40s} | {row['AwardAmount']:10,.0f} ريال")
                print(f"     تاريخ الجائزة: {row['EntryDate'].strftime('%Y-%m-%d') if pd.notna(row['EntryDate']) else 'N/A'}")
                print(f"     تاريخ البنك: {row['BankDate'].strftime('%Y-%m-%d') if pd.notna(row['BankDate']) else 'N/A'}")
                print()
        
        # Reference-Diff
        ref_diff = results[results['MatchType'] == 'Reference-Diff']
        if len(ref_diff) > 0:
            print(f"\n⚠️ Reference-Diff ({len(ref_diff):,} مطابقة):")
            sample = ref_diff.head(2)
            for idx, row in sample.iterrows():
                print(f"   • {row['OwnerName'][:40]:40s}")
                print(f"     الجائزة: {row['AwardAmount']:10,.0f} ريال")
                print(f"     البنك: {row['BankAmount']:10,.0f} ريال")
                print(f"     الفرق: {abs(row['AwardAmount'] - row['BankAmount']):10,.0f} ريال")
                print()
    
    # حفظ النتائج
    output_file = 'outputs/matching_results_large.xlsx'
    print(f"\n💾 حفظ النتائج إلى: {output_file}")
    results.to_excel(output_file, index=False)
    print(f"   ✓ تم الحفظ بنجاح!")
    
    print("\n" + "=" * 80)
    print("✅ اكتمل الاختبار بنجاح!")
    print("=" * 80)

except FileNotFoundError as e:
    print(f"\n❌ خطأ: الملف غير موجود - {e}")
except Exception as e:
    print(f"\n❌ خطأ: {e}")
    import traceback
    traceback.print_exc()
