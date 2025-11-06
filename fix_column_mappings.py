#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
فحص سريع للأعمدة وإضافة mappings جديدة
"""

import pandas as pd
from pathlib import Path

# تحديث column_mapping في camel_awards_analyzer.py
new_mappings = {
    # من الملفات القديمة (مع مسافات)
    'entry date': 'EntryDate',
    'owner name': 'OwnerName',
    'award amount': 'AwardAmount',
    'entry number': 'EntryNumber',
    'owner number': 'OwnerNumber',
    'trainer name': 'TrainerName',
    'payment method': 'PaymentMethod',
    'paymentrefrence': 'BankReference',
    'payment refrence': 'BankReference',
    
    # من الملفات الجديدة (بدون مسافات)
    'entrydate': 'EntryDate',
    'ownername': 'OwnerName',
    'awardamount': 'AwardAmount',
    'entrynumber': 'EntryNumber',
    'ownernumber': 'OwnerNumber',
    'trainername': 'TrainerName',
    'paymenttype': 'PaymentMethod',
    'paymentreference': 'BankReference',
}

print("🔧 إضافة Mappings الجديدة:")
print("="*60)
for old, new in sorted(new_mappings.items()):
    print(f"   '{old}' → '{new}'")

print("\n💡 يجب إضافة هذه الأعمدة إلى normalize_column_names() في camel_awards_analyzer.py")
print("\nالكود المقترح:")
print("-"*60)
print("""
column_mapping = {
    # أسماء المالك
    'owner_name': 'OwnerName',
    'owner name': 'OwnerName',  # جديد (مع مسافة)
    'ownername': 'OwnerName',   # جديد (بدون مسافة)
    'اسم المالك': 'OwnerName',
    'المالك': 'OwnerName',
    'الاسم': 'OwnerName',
    'name': 'OwnerName',
    
    # الموسم
    'season': 'Season',
    'الموسم': 'Season',
    'موسم': 'Season',
    
    # السباق
    'race': 'Race',
    'السباق': 'Race',
    'سباق': 'Race',
    'race_name': 'Race',
    'اسم السباق': 'Race',
    
    # المبلغ
    'award_amount': 'AwardAmount',
    'award amount': 'AwardAmount',  # جديد (مع مسافة)
    'awardamount': 'AwardAmount',   # جديد (بدون مسافة)
    'amount': 'AwardAmount',
    'المبلغ': 'AwardAmount',
    'مبلغ': 'AwardAmount',
    'القيمة': 'AwardAmount',
    'قيمة': 'AwardAmount',
    'الجائزة': 'AwardAmount',
    
    # تاريخ الإدخال
    'entry_date': 'EntryDate',
    'entry date': 'EntryDate',  # جديد (مع مسافة)
    'entrydate': 'EntryDate',   # جديد (بدون مسافة)
    'date': 'EntryDate',
    'التاريخ': 'EntryDate',
    'تاريخ': 'EntryDate',
    'تاريخ الإدخال': 'EntryDate',
    'تاريخ السباق': 'EntryDate',
    
    # بيانات البنك
    'bank_name': 'BankName',
    'bank name': 'BankName',
    'اسم المستفيد': 'BankName',
    'المستفيد': 'BankName',
    'beneficiary': 'BankName',
    
    'bank_date': 'BankDate',
    'bank date': 'BankDate',
    'تاريخ التحويل': 'BankDate',
    'تاريخ الدفع': 'BankDate',
    'payment_date': 'BankDate',
    'payment date': 'BankDate',
    
    'bank_amount': 'BankAmount',
    'bank amount': 'BankAmount',
    'مبلغ التحويل': 'BankAmount',
    'payment_amount': 'BankAmount',
    'payment amount': 'BankAmount',
    
    'bank_reference': 'BankReference',
    'bank reference': 'BankReference',
    'paymentrefrence': 'BankReference',  # جديد (خطأ إملائي شائع)
    'payment refrence': 'BankReference',  # جديد
    'paymentreference': 'BankReference',  # جديد
    'payment reference': 'BankReference',
    'reference': 'BankReference',
    'المرجع': 'BankReference',
    'رقم المرجع': 'BankReference',
    'رقم العملية': 'BankReference',
}
""")
