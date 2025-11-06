#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار المحمّل الجديد v2.0
===========================

يختبر قراءة الملفات مع الحل الجديد
"""

import sys
from pathlib import Path

# إضافة المسار
sys.path.insert(0, str(Path(__file__).parent))

# استخدام النسخة المستقرة (pandas only)
try:
    from core.data_loader_pandas import read_awards_excel, read_bank_excel
    print("✅ تم استيراد data_loader_pandas بنجاح")
except ImportError as e:
    print(f"❌ فشل استيراد data_loader_pandas: {e}")
    sys.exit(1)

def test_awards_files():
    """اختبار قراءة ملفات الجوائز"""
    print("\n" + "="*60)
    print("📊 اختبار ملفات الجوائز")
    print("="*60)
    
    awards_paths = [
        "uploads/Awards_Delegations_2018-2019.xlsx",
        "uploads/Awards_Delegations_2019-2020.xlsx",
        "uploads/Awards_Delegations_2020-2021.xlsx",
        "uploads/Awards_Delegations_2021-2022.xlsx",
        "uploads/AwardsForSeason2022-2023.xlsx",
        "uploads/AwardsForSeason2023-2024.xlsx",
        "uploads/AwardsForSeason2024-2025.xlsx",
    ]
    
    all_dfs = []
    for p in awards_paths:
        path = Path(p)
        if not path.exists():
            print(f"⏭️  تخطي {p} (غير موجود)")
            continue
        
        try:
            print(f"\n📁 قراءة: {path.name}")
            df = read_awards_excel(str(path))
            
            print(f"   ✅ السجلات: {len(df):,}")
            print(f"   ✅ الأعمدة: {len(df.columns)}")
            print(f"   ✅ الأعمدة الموجودة:")
            
            # عرض أول 10 أعمدة
            for col in df.columns[:10]:
                print(f"      - {col}")
            
            if len(df.columns) > 10:
                print(f"      ... و {len(df.columns) - 10} عمود آخر")
            
            # فحص الأعمدة المهمة
            if 'OwnerName' in df.columns:
                print(f"   ✅ OwnerName موجود: {df['OwnerName'].notna().sum():,} قيمة")
            if 'AwardAmount' in df.columns:
                print(f"   ✅ AwardAmount موجود: {df['AwardAmount'].notna().sum():,} قيمة")
                print(f"      المدى: {df['AwardAmount'].min():.2f} - {df['AwardAmount'].max():.2f}")
            if 'PaymentReference' in df.columns:
                print(f"   ✅ PaymentReference موجود: {df['PaymentReference'].notna().sum():,} قيمة")
            
            all_dfs.append(df)
            
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    if all_dfs:
        print(f"\n{'='*60}")
        print(f"✅ تم قراءة {len(all_dfs)} ملف بنجاح")
        print(f"✅ إجمالي السجلات: {sum(len(df) for df in all_dfs):,}")
        print(f"{'='*60}")
        
        return all_dfs
    else:
        print("\n❌ لم يتم قراءة أي ملف")
        return []

def test_bank_file():
    """اختبار قراءة كشف البنك"""
    print("\n" + "="*60)
    print("🏦 اختبار كشف البنك")
    print("="*60)
    
    # ابحث عن ملف البنك
    possible_paths = [
        "uploads/bank.xlsx",
        "uploads/بنك.xlsx",
        "uploads/Bank_Statement.xlsx",
    ]
    
    # ابحث أيضاً في مجلد uploads
    uploads = Path("uploads")
    if uploads.exists():
        for f in uploads.glob("*.xlsx"):
            if f.name not in [p.split("/")[-1] for p in possible_paths]:
                possible_paths.append(str(f))
    
    bank_df = None
    for p in possible_paths:
        path = Path(p)
        if path.exists():
            try:
                print(f"\n📁 قراءة: {path.name}")
                df = read_bank_excel(str(path))
                
                print(f"   ✅ السجلات: {len(df):,}")
                print(f"   ✅ الأعمدة: {len(df.columns)}")
                print(f"   ✅ الأعمدة الموجودة:")
                
                for col in df.columns:
                    print(f"      - {col}")
                
                # فحص الأعمدة المهمة
                if 'BankReference' in df.columns:
                    print(f"   ✅ BankReference موجود: {df['BankReference'].notna().sum():,} قيمة")
                if 'TransferAmount' in df.columns:
                    print(f"   ✅ TransferAmount موجود: {df['TransferAmount'].notna().sum():,} قيمة")
                    print(f"      المدى: {df['TransferAmount'].min():.2f} - {df['TransferAmount'].max():.2f}")
                if 'BeneficiaryName' in df.columns:
                    print(f"   ✅ BeneficiaryName موجود: {df['BeneficiaryName'].notna().sum():,} قيمة")
                
                bank_df = df
                break
                
            except Exception as e:
                print(f"   ❌ خطأ: {e}")
    
    if bank_df is not None:
        print(f"\n{'='*60}")
        print(f"✅ تم قراءة كشف البنك بنجاح")
        print(f"✅ إجمالي السجلات: {len(bank_df):,}")
        print(f"{'='*60}")
        return bank_df
    else:
        print("\n❌ لم يتم العثور على كشف البنك")
        return None

if __name__ == "__main__":
    print("="*60)
    print("🔬 اختبار المحمّل الجديد للبيانات")
    print("="*60)
    
    awards_dfs = test_awards_files()
    bank_df = test_bank_file()
    
    # اختبار التطابق
    if awards_dfs and bank_df is not None:
        print("\n" + "="*60)
        print("🔍 اختبار التطابق السريع")
        print("="*60)
        
        import pandas as pd
        all_awards = pd.concat(awards_dfs, ignore_index=True)
        
        if 'PaymentReference' in all_awards.columns and 'BankReference' in bank_df.columns:
            award_refs = set(all_awards['PaymentReference'].dropna().astype(str))
            bank_refs = set(bank_df['BankReference'].dropna().astype(str))
            
            matches = award_refs & bank_refs
            print(f"\n✅ عدد المراجع في الجوائز: {len(award_refs):,}")
            print(f"✅ عدد المراجع في البنك: {len(bank_refs):,}")
            print(f"{'='*60}")
            
            if matches:
                print(f"🎉 المتطابقات: {len(matches):,} مرجع")
                print(f"\nأمثلة:")
                for ref in list(matches)[:5]:
                    print(f"   - {ref}")
            else:
                print("⚠️  لا توجد مراجع متطابقة")
                print("\nأمثلة من الجوائز:")
                for ref in list(award_refs)[:5]:
                    print(f"   - {ref}")
                print("\nأمثلة من البنك:")
                for ref in list(bank_refs)[:5]:
                    print(f"   - {ref}")
        
        # اختبار المبالغ
        if 'AwardAmount' in all_awards.columns and 'TransferAmount' in bank_df.columns:
            award_amounts = set(all_awards['AwardAmount'].dropna().round(2))
            bank_amounts = set(bank_df['TransferAmount'].dropna().round(2))
            
            amount_matches = award_amounts & bank_amounts
            print(f"\n💰 المبالغ المتطابقة: {len(amount_matches):,}")
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار")
    print("="*60)
