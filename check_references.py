# -*- coding: utf-8 -*-
"""
فحص Reference Numbers
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
    print('🔍 فحص Reference Numbers')
    print('=' * 80)
    
    # تحميل الجوائز
    awards_df = analyzer.load_awards_files(awards_files)
    print(f'\n📥 الجوائز ({len(awards_df):,} سجل):')
    
    # فحص paymentreference
    if 'paymentreference' in awards_df.columns:
        ref_count = awards_df['paymentreference'].notna().sum()
        print(f'   ✓ paymentreference: {ref_count:,} سجل غير فارغ ({ref_count/len(awards_df)*100:.1f}%)')
        if ref_count > 0:
            print('   أمثلة:')
            for val in awards_df['paymentreference'].dropna().head(10):
                print(f'      {val}')
    
    # تحميل البنك
    bank_df = analyzer.load_bank_statement(bank_file)
    print(f'\n🏦 البنك ({len(bank_df):,} سجل):')
    
    # فحص كل أعمدة Reference
    ref_columns = ['AwardReference', 'AwardReferenceLong', 'BankReference', 'BankRequestReference']
    for col in ref_columns:
        if col in bank_df.columns:
            ref_count = bank_df[col].notna().sum()
            print(f'   ✓ {col}: {ref_count:,} سجل غير فارغ ({ref_count/len(bank_df)*100:.1f}%)')
            if ref_count > 0:
                print('      أمثلة:')
                for val in bank_df[col].dropna().head(5):
                    print(f'         {val}')
    
    # البحث عن تطابقات
    print('\n' + '=' * 80)
    print('🔗 البحث عن تطابقات Reference')
    print('=' * 80)
    
    if 'paymentreference' in awards_df.columns:
        award_refs = set(awards_df['paymentreference'].dropna().astype(str).unique())
        print(f'\nReference في الجوائز: {len(award_refs):,} قيمة فريدة')
        
        for col in ref_columns:
            if col in bank_df.columns and bank_df[col].notna().sum() > 0:
                bank_refs = set(bank_df[col].dropna().astype(str).unique())
                common_refs = award_refs.intersection(bank_refs)
                print(f'\n{col}:')
                print(f'   قيم فريدة في البنك: {len(bank_refs):,}')
                print(f'   تطابقات: {len(common_refs):,}')
                
                if len(common_refs) > 0:
                    print(f'   أمثلة من التطابقات:')
                    for ref in list(common_refs)[:5]:
                        award_count = len(awards_df[awards_df['paymentreference'].astype(str) == ref])
                        bank_count = len(bank_df[bank_df[col].astype(str) == ref])
                        print(f'      {ref} - جوائز: {award_count} | بنك: {bank_count}')
    
    print('\n' + '=' * 80)

if __name__ == '__main__':
    main()
