# -*- coding: utf-8 -*-
"""
مثال عملي: كشف الدفعات المكررة
"""

from typing import Any
import pandas as pd
from core.data_loader import DataLoader
from core.duplicate_analyzer import DuplicateAnalyzer

# 1. تحميل البيانات
print("⏳ جاري تحميل البيانات...")
loader = DataLoader('العجوري 11-4.csv')
df: pd.DataFrame = loader.load().auto_clean().get_data()
print(f"✅ تم تحميل {len(df):,} صف\n")

# 2. عرض أسماء الأعمدة لتحديد الأعمدة المناسبة
print("📋 الأعمدة المتاحة:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i}. {col}")
print()

# 3. كشف التكرارات
# غيّر أسماء الأعمدة حسب بياناتك
print("🔍 البحث عن التكرارات...")
analyzer = DuplicateAnalyzer(df)

# مثال 1: البحث حسب عمودين فقط
duplicates = analyzer.find_payment_duplicates(
    entity_col='OwnerName',      # غيّر هذا حسب عمود الاسم
    amount_col='EntryTypeNumber' # غيّر هذا حسب عمود المبلغ
)

print(f"\n📊 النتائج:")
print(f"   • عدد التكرارات: {len(duplicates):,}")

if len(duplicates) > 0:
    print(f"   • عدد المجموعات: {duplicates['duplicate_group'].nunique()}")
    print(f"   • نسبة التكرار: {len(duplicates)/len(df)*100:.2f}%")
    
    # عرض أول 10 تكرارات
    print(f"\n📋 أول 10 تكرارات:")
    print(duplicates.head(10)[['OwnerName', 'EntryTypeNumber', 'duplicate_count']])
    
    # تصدير إلى Excel
    output_file = 'outputs/duplicates_report.xlsx'
    analyzer.export_duplicates(output_file)
    print(f"\n✅ تم تصدير التقرير إلى: {output_file}")
else:
    print("   • لم يتم العثور على تكرارات")

# 4. كشف التكرارات الضبابية (أسماء متشابهة)
print("\n\n🔍 البحث عن تطابق ضبابي (أسماء متشابهة)...")
fuzzy_matches = analyzer.find_fuzzy_duplicates(
    name_col='OwnerName',
    threshold=0.90  # 90% تطابق أو أكثر
)

if len(fuzzy_matches) > 0:
    print(f"✅ تم العثور على {len(fuzzy_matches)} تطابق ضبابي")
    print("\n📋 الأسماء المتشابهة:")
    for _, row in fuzzy_matches.head(5).iterrows():
        print(f"   • {row['original_name1']} ↔️ {row['original_name2']} ({row['similarity']*100:.1f}% تطابق)")
else:
    print("   • لم يتم العثور على تطابقات ضبابية")

print("\n" + "="*80)
print("✅ اكتمل التحليل!")
print("="*80)
