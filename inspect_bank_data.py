# -*- coding: utf-8 -*-
"""
فحص بيانات البنك بالتفصيل
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from core.camel_awards_analyzer import CamelAwardsAnalyzer
from pathlib import Path
import pandas as pd

def main():
    base = Path('d:/Data_Analest/الملفات')
    awards_files = [
        base / 'AwardsForSeason2022-2023.xlsx',
        base / 'AwardsForSeason2023-2024.xlsx',
    ]
    bank_file = base / 'ملف البنك.xlsx'
    
    analyzer = CamelAwardsAnalyzer(use_advanced_features=False)
    
    print('=' * 80)
    print('🔍 فحص تفصيلي للبيانات')
    print('=' * 80)
    
    # تحميل الجوائز
    print('\n📥 تحليل بيانات الجوائز...')
    awards_df = analyzer.load_awards_files(awards_files)
    print(f'   إجمالي السجلات: {len(awards_df):,}')
    print(f'   الأعمدة: {awards_df.columns.tolist()}')
    print('\n   نطاق التواريخ:')
    print(f'   من: {awards_df["EntryDate"].min()}')
    print(f'   إلى: {awards_df["EntryDate"].max()}')
    print('\n   نطاق المبالغ:')
    print(f'   أصغر: {awards_df["AwardAmount"].min():,.0f}')
    print(f'   أكبر: {awards_df["AwardAmount"].max():,.0f}')
    print(f'   متوسط: {awards_df["AwardAmount"].mean():,.0f}')
    
    print('\n   أمثلة من الجوائز:')
    sample_awards = awards_df[['OwnerName', 'AwardAmount', 'EntryDate']].head(10)
    for idx, row in sample_awards.iterrows():
        print(f'      {row["OwnerName"][:30]:30s} | {row["AwardAmount"]:>10,.0f} | {row["EntryDate"]}')
    
    # تحميل البنك
    print('\n🏦 تحليل بيانات البنك...')
    bank_df = analyzer.load_bank_statement(bank_file)
    print(f'   إجمالي السجلات: {len(bank_df):,}')
    print(f'   الأعمدة: {bank_df.columns.tolist()}')
    
    # فحص BankName
    print('\n   فحص عمود BankName:')
    bank_name_count = bank_df['BankName'].notna().sum()
    print(f'   سجلات غير فارغة: {bank_name_count:,} ({bank_name_count/len(bank_df)*100:.1f}%)')
    
    if bank_name_count > 0:
        print('\n   أمثلة من الأسماء:')
        sample_names = bank_df[bank_df['BankName'].notna()]['BankName'].head(10)
        for name in sample_names:
            print(f'      {str(name)[:50]}')
    else:
        print('   ⚠️ لا توجد أسماء في عمود BankName!')
        
        # فحص أعمدة أخرى قد تحتوي على الأسماء
        print('\n   البحث عن أسماء في أعمدة أخرى...')
        for col in bank_df.columns:
            if 'name' in str(col).lower() or 'اسم' in str(col).lower():
                non_null = bank_df[col].notna().sum()
                if non_null > 0:
                    print(f'   عمود "{col}": {non_null:,} سجل غير فارغ')
                    print(f'      أمثلة: {bank_df[col].dropna().head(3).tolist()}')
    
    # فحص المبالغ
    print('\n   فحص المبالغ:')
    bank_amount_count = bank_df['BankAmount'].notna().sum()
    print(f'   سجلات غير فارغة: {bank_amount_count:,} ({bank_amount_count/len(bank_df)*100:.1f}%)')
    
    if bank_amount_count > 0:
        print(f'   نطاق المبالغ:')
        print(f'   أصغر: {bank_df["BankAmount"].min():,.0f}')
        print(f'   أكبر: {bank_df["BankAmount"].max():,.0f}')
        print(f'   متوسط: {bank_df["BankAmount"].mean():,.0f}')
        
        print('\n   توزيع المبالغ (عينة):')
        sample_amounts = bank_df[bank_df['BankAmount'].notna()]['BankAmount'].head(20)
        for amt in sample_amounts:
            print(f'      {amt:>15,.2f}')
    
    # فحص التواريخ
    print('\n   فحص التواريخ:')
    bank_date_count = bank_df['BankDate'].notna().sum()
    print(f'   سجلات غير فارغة: {bank_date_count:,} ({bank_date_count/len(bank_df)*100:.1f}%)')
    
    if bank_date_count > 0:
        print(f'   نطاق التواريخ:')
        print(f'   من: {bank_df["BankDate"].min()}')
        print(f'   إلى: {bank_df["BankDate"].max()}')
    
    # محاولة إيجاد مطابقات محتملة
    print('\n' + '=' * 80)
    print('🔗 البحث عن مطابقات محتملة')
    print('=' * 80)
    
    # البحث عن مبالغ مشتركة
    award_amounts = set(awards_df['AwardAmount'].dropna().unique())
    bank_amounts = set(bank_df['BankAmount'].dropna().unique())
    common_amounts = award_amounts.intersection(bank_amounts)
    
    print(f'\nمبالغ الجوائز الفريدة: {len(award_amounts):,}')
    print(f'مبالغ البنك الفريدة: {len(bank_amounts):,}')
    print(f'مبالغ مشتركة: {len(common_amounts):,}')
    
    if len(common_amounts) > 0:
        print('\nأمثلة من المبالغ المشتركة:')
        for amt in list(common_amounts)[:10]:
            award_count = len(awards_df[awards_df['AwardAmount'] == amt])
            bank_count = len(bank_df[bank_df['BankAmount'] == amt])
            print(f'   {amt:>12,.0f} - جوائز: {award_count:>3} | بنك: {bank_count:>3}')
    
    print('\n' + '=' * 80)

if __name__ == '__main__':
    main()
