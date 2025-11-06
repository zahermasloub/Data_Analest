#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Loader v2.0 - Pandas Only (مستقر)
=======================================

نسخة مستقرة تستخدم pandas فقط (بدون polars) 
تحل جميع مشاكل أسماء الأعمدة والهيدر

الاستخدام:
    from core.data_loader_pandas import read_awards_excel, read_bank_excel
    
    awards_df = read_awards_excel("awards.xlsx")
    bank_df = read_bank_excel("bank.xlsx")
"""

import re
import pandas as pd
from typing import List, Optional

# ============================================
# 1) خرائط الأعمدة - ملفات الجوائز
# ============================================

AWARDS_COLMAP = {
    # تاريخ
    "entry date": "EntryDate",
    "entrydate": "EntryDate",

    # موسم
    "season": "Season",

    # سباق
    "race": "Race",

    # المالك
    "owner number": "OwnerNumber",
    "ownernumber": "OwnerNumber",
    "owner name": "OwnerName",
    "ownername": "OwnerName",
    "owner qatariid": "OwnerQatariId",
    "ownerqatariid": "OwnerQatariId",

    # المدرب
    "trainer number": "TrainerNumber",
    "trainernumber": "TrainerNumber",
    "trainername": "TrainerName",
    "trainer name": "TrainerName",
    "trainer qatari id": "TrainerQatariId",
    "trainer qatariid": "TrainerQatariId",
    "trainerqatariid": "TrainerQatariId",

    # الإدخال/النوع
    "entry number": "EntryTypeNumber",
    "entrytypenumber": "EntryTypeNumber",

    # المبلغ/الدفع
    "award amount": "AwardAmount",
    "awardamount": "AwardAmount",
    "payment method": "PaymentType",
    "paymenttype": "PaymentType",

    # مستفيد/عملة/حساب
    "beneficiarynameen": "BeneficiaryEnglishName",
    "beneficiary english name": "BeneficiaryEnglishName",
    "beneficiarycurrencycode": "CurrencyCode",
    "currencycode": "CurrencyCode",
    "ibannumber": "IBAN",
    "iban": "IBAN",
    "swiftcode": "SwiftCode",
    "beneficiaryaddressen1": "Address1",
    "address1": "Address1",
    "beneficiaryaddressen2": "Address2",
    "address2": "Address2",
    "transfer rate": "TransferRate",
    "transferrate": "TransferRate",
    "rate": "TransferRate",

    # مراجع الدفع (الأصلية + المندوبين)
    "paymentrefrence": "PaymentReference",       # شائعة بالتهجئة الخطأ Refrence
    "paymentreference": "PaymentReference",
    "payment refrence": "PaymentReference",
    "payment reference": "PaymentReference",

    "paymentrefrence_d1": "DelegatePaymentReference",
    "delegatepaymentreference": "DelegatePaymentReference",

    "paymentrefrence_d2": "SecondDelegatePaymentReference",
    "seconddelegatepaymentreference": "SecondDelegatePaymentReference",

    "paymentrefrence_d3": "ThirdDelegatePaymentReference",
    "thirddelegatepaymentreference": "ThirdDelegatePaymentReference",

    # أسماء/أرقام المندوبين
    "customername_d1": "DelegateName",
    "delegatename": "DelegateName",
    "customerid_d1": "DelegateQatariId",
    "delegateqatariid": "DelegateQatariId",
    "customernamed1": "DelegateName",
    "customeridd1": "DelegateQatariId",

    "customername_d2": "SecondDelegateName",
    "seconddelegatename": "SecondDelegateName",
    "customerid_d2": "SecondDelegateQatariId",
    "seconddelegateqatariid": "SecondDelegateQatariId",

    "customername_d3": "ThirdDelegateName",
    "thirddelegatename": "ThirdDelegateName",
    "customerid_d3": "ThirdDelegateQatariId",
    "thirddelegateqatariid": "ThirdDelegateQatariId",

    # أخرى
    "print status": "PrintStatus",
    "printstatus": "PrintStatus",
}

# ============================================
# 2) خرائط الأعمدة - كشف البنك
# ============================================

BANK_HEADER_CANDIDATES = [
    "BankReference","BeneficiaryName","BeneficiaryNameEn","Beneficiary English Name",
    "IBAN","IbanNumber","TransferAmount","Transfer Amount","TransferDate","Transfer Date",
    "Currency","CurrencyCode","PaymentReference","Payment Refrence",
]

BANK_COLMAP = {
    "bankreference": "BankReference",
    "paymentreference": "BankReference",
    "payment refrence": "BankReference",
    "paymentrefrence": "BankReference",
    "beneficiaryname": "BeneficiaryName",
    "beneficiarynameen": "BeneficiaryName",
    "beneficiary english name": "BeneficiaryName",
    "iban": "IBAN",
    "ibannumber": "IBAN",
    "transferamount": "TransferAmount",
    "transfer amount": "TransferAmount",
    "amount": "TransferAmount",
    "transferdate": "TransferDate",
    "transfer date": "TransferDate",
    "date": "TransferDate",
    "currency": "CurrencyCode",
    "currencycode": "CurrencyCode",
}

# ============================================
# 3) وظائف مساعدة
# ============================================

AMOUNT_STRIP_REGEX = r"[^0-9\.\-]"  # تنظيف المبلغ من أي رموز

def normalize_colnames(cols: List[str], colmap: dict) -> List[str]:
    """تطبيع أسماء الأعمدة"""
    out = []
    for c in cols:
        c0 = str(c).strip()
        if not c0 or c0.lower().startswith("unnamed"):
            out.append(None)  # سيتم إسقاطها
            continue
        key = c0.lower().replace("_", " ").replace("-", " ").strip()
        key = re.sub(r"\s+", " ", key)
        key2 = key.replace(" ", "")
        std = colmap.get(key2) or colmap.get(key) or None
        out.append(std or c0.replace(" ", ""))  # لو غير معروفة: ألغِ الفراغات فقط
    return out

def clean_amount_column(series: pd.Series) -> pd.Series:
    """تنظيف عمود المبالغ"""
    return (
        series.astype(str)
        .str.replace(AMOUNT_STRIP_REGEX, "", regex=True)
        .replace("", pd.NA)
        .astype(float, errors='ignore')
        .round(2)
    )

# ============================================
# 4) قراءة ملفات الجوائز
# ============================================

def read_awards_excel(path: str) -> pd.DataFrame:
    """
    قراءة ملف جوائز Excel مع توحيد الأعمدة تلقائياً
    
    Args:
        path: مسار ملف Excel
        
    Returns:
        Pandas DataFrame بأعمدة موحدة
    """
    # قراءة الملف
    df = pd.read_excel(path)
    
    # إعادة تسمية الأعمدة
    new_cols = normalize_colnames(df.columns.tolist(), AWARDS_COLMAP)
    
    # بناء خريطة إعادة التسمية وإسقاط الـ None (Unnamed)
    rename_map = {old: new for old, new in zip(df.columns, new_cols) if new}
    df = df.rename(columns=rename_map)
    
    # إسقاط الأعمدة Unnamed (التي صارت None)
    drop_cols = [old for old, new in zip(df.columns, new_cols) if new is None]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # تنظيف المبلغ
    if "AwardAmount" in df.columns:
        df["AwardAmount"] = clean_amount_column(df["AwardAmount"])

    # توحيد التاريخ
    if "EntryDate" in df.columns:
        df["EntryDate"] = pd.to_datetime(df["EntryDate"], errors='coerce')

    return df

# ============================================
# 5) قراءة كشف البنك (اكتشاف الهيدر)
# ============================================

def detect_header_row(df_raw: pd.DataFrame, max_scan: int = 20) -> Optional[int]:
    """
    اكتشاف صف الهيدر في ملف Excel
    """
    best_row, best_hits = None, -1
    for i in range(min(max_scan, len(df_raw))):
        row_vals = [str(x or "").strip() for x in df_raw.iloc[i]]
        hits = 0
        for val in row_vals:
            low = val.lower().strip()
            if low in ("", "unnamed: 0", "unnamed", "nan"): 
                continue
            # تطابق دقيق أو قريب مع المرشحين
            for cand in BANK_HEADER_CANDIDATES:
                c = cand.lower()
                if low == c or c.replace(" ", "") == low.replace(" ", ""):
                    hits += 1
                    break
        if hits > best_hits:
            best_hits = hits
            best_row = i
    
    return best_row if best_hits > 0 else None

def read_bank_excel(path: str) -> pd.DataFrame:
    """
    قراءة كشف البنك مع اكتشاف صف الهيدر تلقائياً
    
    Args:
        path: مسار ملف Excel
        
    Returns:
        Pandas DataFrame بأعمدة موحدة
    """
    # نقرأ أولاً بدون افتراض هيدر
    df0 = pd.read_excel(path, header=None)
    
    # اكتشف صفّ الترويسات
    hdr = detect_header_row(df0)
    if hdr is None:
        # fallback: استخدم الصف الأول كعناوين
        hdr = 0
    
    # إعادة قراءة مع الهيدر الصحيح
    df = pd.read_excel(path, header=hdr)

    # طبّق الأسماء
    std_cols = normalize_colnames(df.columns.tolist(), BANK_COLMAP)
    rename_map = {old: new for old, new in zip(df.columns, std_cols) if new}
    df = df.rename(columns=rename_map)
    
    drop_cols = [old for old, new in zip(df.columns, std_cols) if new is None]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # تنظيف وتحويل
    if "TransferAmount" in df.columns:
        df["TransferAmount"] = clean_amount_column(df["TransferAmount"])
    if "TransferDate" in df.columns:
        df["TransferDate"] = pd.to_datetime(df["TransferDate"], errors='coerce')

    return df
