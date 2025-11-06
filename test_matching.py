# -*- coding: utf-8 -*-
"""
اختبار المطابقة المحسنة
"""
import io
import sys

# ضبط encoding للعربية
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from core.camel_awards_analyzer import CamelAwardsAnalyzer
from pathlib import Path

def main():
    base = Path('d:/Data_Analest/الملفات')
    awards_files = [
        base / 'AwardsForSeason2022-2023.xlsx',
        base / 'AwardsForSeason2023-2024.xlsx',
    ]
    bank_file = base / 'ملف البنك.xlsx'
    
    analyzer = CamelAwardsAnalyzer(use_advanced_features=False)
    
    print('=' * 80)
    print('🚀 تشغيل محلل الجوائز المحسّن')
    print('=' * 80)
    
    print('\n📥 تحميل ملفات الجوائز...')
    awards_df = analyzer.load_awards_files(awards_files)
    print(f'   ✅ تم تحميل {len(awards_df):,} جائزة')
    
    print('\n🏦 تحميل كشف البنك...')
    bank_df = analyzer.load_bank_statement(bank_file)
    print(f'   ✅ تم تحميل {len(bank_df):,} معاملة بنكية')
    
    print('\n🔗 بدء المطابقة...')
    results = analyzer.match_with_bank(time_window_days=7)
    
    print('\n' + '=' * 80)
    print('📊 النتائج النهائية')
    print('=' * 80)
    
    status_dist = results['StatusFlag'].value_counts()
    print('\nتوزيع الحالات:')
    for status, count in status_dist.items():
        print(f'   {status} {count:,} سجل ({count/len(results)*100:.1f}%)')
    
    matched = results[results['StatusFlag'] == '✅']
    print(f'\n✅ إجمالي المطابقات: {len(matched):,}')
    
    if len(matched) > 0:
        exact_matches = len(matched[matched['MatchType'] == 'Exact'])
        fuzzy_matches = len(matched[matched['MatchType'] == 'Fuzzy'])
        print(f'   - مطابقات تامة: {exact_matches:,}')
        print(f'   - مطابقات ضبابية: {fuzzy_matches:,}')
        
        print('\nأمثلة من المطابقات:')
        sample = matched[['OwnerName', 'AwardAmount', 'BankName', 'BankAmount', 'MatchType', 'MatchScore']].head(10)
        print(sample.to_string(index=False))
    
    unmatched = results[results['StatusFlag'] == '⚠️']
    print(f'\n⚠️ غير مطابق: {len(unmatched):,}')
    
    if len(unmatched) > 0:
        print('\nأمثلة من الجوائز غير المطابقة:')
        sample_unmatched = unmatched[['OwnerName', 'AwardAmount', 'EntryDate', 'ReasonText']].head(5)
        print(sample_unmatched.to_string(index=False))
    
    # حفظ النتائج
    output_file = 'outputs/matching_results.xlsx'
    Path('outputs').mkdir(exist_ok=True)
    results.to_excel(output_file, index=False)
    print(f'\n💾 تم حفظ النتائج في: {output_file}')
    
    print('\n' + '=' * 80)
    print('✅ اكتمل التحليل بنجاح!')
    print('=' * 80)

if __name__ == '__main__':
    main()
