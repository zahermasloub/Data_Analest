#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Loader v2.0 - محمّل البيانات المحسّن
==========================================

يحل جميع مشاكل:
- أسماء الأعمدة المختلفة بين الملفات
- الأعمدة Unnamed
- اكتشاف صف الهيدر تلقائياً في كشف البنك
- تنظيف المبالغ والتواريخ

الاستخدام:
    from core.data_loader_v2 import read_awards_excel, read_bank_excel
    
    awards_df = read_awards_excel("awards.xlsx")
    bank_df = read_bank_excel("bank.xlsx")
"""

from __future__ import annotations
import re
import polars as pl
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

STANDARD_AWARDS_ORDER = [
    "EntryDate","Season","Race",
    "OwnerNumber","OwnerName","OwnerQatariId",
    "TrainerNumber","TrainerName","TrainerQatariId",
    "EntryTypeNumber",
    "AwardAmount","PaymentType",
    "BeneficiaryEnglishName","CurrencyCode","IBAN","SwiftCode",
    "Address1","Address2","TransferRate","PaymentReference","PrintStatus",
    "DelegatePaymentReference","DelegateName","DelegateQatariId",
    "SecondDelegatePaymentReference","SecondDelegateName","SecondDelegateQatariId",
    "ThirdDelegatePaymentReference","ThirdDelegateName","ThirdDelegateQatariId",
]

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

def clean_amount_series(s: pl.Series) -> pl.Series:
    """تنظيف عمود المبالغ"""
    return (
        s.cast(pl.Utf8, strict=False)
         .str.replace_all(AMOUNT_STRIP_REGEX, "")
         .cast(pl.Float64, strict=False)
         .round(2)
    )

# ============================================
# 4) قراءة ملفات الجوائز
# ============================================

def read_awards_excel(path: str) -> pl.DataFrame:
    """
    قراءة ملف جوائز Excel مع توحيد الأعمدة تلقائياً
    
    Args:
        path: مسار ملف Excel
        
    Returns:
        Polars DataFrame بأعمدة موحدة
    """
    # استخدام pandas مباشرة (أكثر استقراراً مع Excel)
    import pandas as pd
    df_pd = pd.read_excel(path)
    df = pl.from_pandas(df_pd)
    
    # إعادة تسمية الأعمدة
    new_cols = normalize_colnames(df.columns, AWARDS_COLMAP)
    
    # بناء خريطة إعادة التسمية وإسقاط الـ None (Unnamed)
    rename_map = {old: new for old, new in zip(df.columns, new_cols) if new}
    df = df.rename(rename_map)
    
    # إسقاط الأعمدة Unnamed (التي صارت None)
    drop_cols = [old for old, new in zip(df.columns, new_cols) if new is None]
    if drop_cols:
        df = df.drop(drop_cols)

    # توحيد أسماء شائعة بين مواسم مختلفة
    if "EntryDate" not in df.columns and "Entry Date" in df.columns:
        df = df.rename({"Entry Date": "EntryDate"})
    if "AwardAmount" not in df.columns and "Award Amount" in df.columns:
        df = df.rename({"Award Amount": "AwardAmount"})
    if "PaymentType" not in df.columns and "Payment Method" in df.columns:
        df = df.rename({"Payment Method": "PaymentType"})

    # تنظيف المبلغ
    if "AwardAmount" in df.columns:
        df = df.with_columns(clean_amount_series(pl.col("AwardAmount")).alias("AwardAmount"))

    # توحيد التاريخ
    if "EntryDate" in df.columns:
        df = df.with_columns(pl.col("EntryDate").str.strptime(pl.Date, strict=False).alias("EntryDate"))

    # تأكد من وجود الأعمدة القياسية (إن لم توجد أنشئها فارغة)
    for col in STANDARD_AWARDS_ORDER:
        if col not in df.columns:
            df = df.with_columns(pl.lit(None).alias(col))

    # إعادة ترتيب (اختياري)
    df = df.select([c for c in STANDARD_AWARDS_ORDER if c in df.columns])
    
    return df

# ============================================
# 5) قراءة كشف البنك (اكتشاف الهيدر)
# ============================================

def detect_header_row(df_raw: pl.DataFrame, max_scan: int = 20) -> Optional[int]:
    """
    اكتشاف صف الهيدر في ملف Excel
    """
    best_row, best_hits = None, -1
    for i in range(min(max_scan, df_raw.height)):
        row_vals = [str(x or "").strip() for x in df_raw.row(i)]
        hits = 0
        for val in row_vals:
            low = val.lower().strip()
            if low in ("", "unnamed: 0", "unnamed"): 
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

def read_bank_excel(path: str) -> pl.DataFrame:
    """
    قراءة كشف البنك مع اكتشاف صف الهيدر تلقائياً
    
    Args:
        path: مسار ملف Excel
        
    Returns:
        Polars DataFrame بأعمدة موحدة
    """
    try:
        # نقرأ أولاً بدون افتراض هيدر
        df0 = pl.read_excel(path, read_options={"header_row": None})
    except Exception as e:
        print(f"⚠️ فشل قراءة {path} بـ Polars، محاولة بـ pandas...")
        import pandas as pd
        df_pd = pd.read_excel(path, header=None)
        df0 = pl.from_pandas(df_pd)
    
    # اكتشف صفّ الترويسات
    hdr = detect_header_row(df0)
    if hdr is None:
        # fallback: استخدم الصف الأول كعناوين
        hdr = 0
    
    # افصل الهيدر والبيانات
    header_vals = [str(x or "").strip() for x in df0.row(hdr)]
    df_data = df0.slice(hdr + 1)

    # طبّق الأسماء
    std_cols = normalize_colnames(header_vals, BANK_COLMAP)
    rename_map = {old: new for old, new in zip(df_data.columns, std_cols) if new}
    df = df_data.rename(rename_map)
    
    drop_cols = [old for old, new in zip(df_data.columns, std_cols) if new is None]
    if drop_cols:
        df = df.drop(drop_cols)

    # تنظيف وتحويل
    if "TransferAmount" in df.columns:
        df = df.with_columns(clean_amount_series(pl.col("TransferAmount")).alias("TransferAmount"))
    if "TransferDate" in df.columns:
        df = df.with_columns(pl.col("TransferDate").str.strptime(pl.Date, strict=False).alias("TransferDate"))

    # توليد أعمدة مفقودة كفارغة حسب الحاجة
    for col in ("BankReference","BeneficiaryName","IBAN","CurrencyCode","TransferAmount","TransferDate"):
        if col not in df.columns:
            df = df.with_columns(pl.lit(None).alias(col))

    # ترتيب بسيط
    bank_order = ["BankReference","BeneficiaryName","IBAN","CurrencyCode","TransferAmount","TransferDate"]
    df = df.select([c for c in bank_order if c in df.columns] + [c for c in df.columns if c not in bank_order])
    
    return df

# ============================================
# 6) تحويل Polars → Pandas (للتوافق)
# ============================================

def to_pandas(df: pl.DataFrame):
    """تحويل Polars DataFrame إلى Pandas"""
    return df.to_pandas()

def read_awards_excel_pandas(path: str):
    """قراءة ملف جوائز وإرجاع Pandas DataFrame"""
    return to_pandas(read_awards_excel(path))

def read_bank_excel_pandas(path: str):
    """قراءة كشف البنك وإرجاع Pandas DataFrame"""
    return to_pandas(read_bank_excel(path))
