"""
Enhanced Audit System - نظام التدقيق المحسّن
===========================================

نظام تدقيق شامل ومحسّن بناءً على متطلبات البرمبت الاحترافي

المميزات الرئيسية:
1. توحيد البيانات الشامل (DataNormalizer)
2. مطابقة بنكية متقدمة (EnhancedBankMatcher)
3. التحقق من الحالات المعروفة (GroundTruthValidator)
4. تقارير احترافية شاملة (ComprehensiveReportGenerator)

المؤلف: محلل البيانات الاحترافي
التاريخ: نوفمبر 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any, Optional
import re
import warnings

warnings.filterwarnings('ignore')


# ============================================================================
# القسم 1: DataNormalizer - محوّل البيانات الموحد
# ============================================================================

class DataNormalizer:
    """
    محوّل البيانات الموحد - Data Normalization Engine
    
    الغرض: توحيد أسماء الأعمدة وحماية الأرقام التعريفية
    
    Features:
    - خريطة توحيد شاملة للأعمدة
    - حماية الأرقام التعريفية من التحويل العلمي
    - إزالة أعمدة Unnamed
    - توثيق التوحيد المطبق
    """
    
    # خريطة توحيد الأعمدة الشاملة
    COLUMN_MAPPING = {
        # Entry Date
        'Entry Date': 'EntryDate',
        'EntryDate': 'EntryDate',
        'entry date': 'EntryDate',
        
        # Owner Information
        'Owner Number': 'OwnerNumber',
        'OwnerNumber': 'OwnerNumber',
        'owner number': 'OwnerNumber',
        
        'Owner Name': 'OwnerName',
        'OwnerName': 'OwnerName',
        'owner name': 'OwnerName',
        
        'Owner QatariId': 'OwnerQatariID',
        'OwnerQatariId': 'OwnerQatariID',
        'Owner Qatari Id': 'OwnerQatariID',
        'OwnerQatariID': 'OwnerQatariID',
        'owner qatariid': 'OwnerQatariID',
        
        # Award Information
        'Award Amount': 'AwardAmount',
        'AwardAmount': 'AwardAmount',
        'award amount': 'AwardAmount',
        
        # Payment Information
        'Payment Method': 'PaymentMethod',
        'PaymentType': 'PaymentMethod',
        'payment method': 'PaymentMethod',
        
        # Payment References (مع تصحيح الخطأ الإملائي)
        'PaymentRefrence': 'PaymentReference',
        'PaymentReference': 'PaymentReference',
        'payment reference': 'PaymentReference',
        
        'PaymentRefrence_D1': 'PaymentReference_D1',
        'PaymentReference_D1': 'PaymentReference_D1',
        'DelegatePaymentReference': 'PaymentReference_D1',
        
        'PaymentRefrence_D2': 'PaymentReference_D2',
        'PaymentReference_D2': 'PaymentReference_D2',
        'SecondDelegatePaymentReference': 'PaymentReference_D2',
        
        'PaymentRefrence_D3': 'PaymentReference_D3',
        'PaymentReference_D3': 'PaymentReference_D3',
        'ThirdDelegatePaymentReference': 'PaymentReference_D3',
        
        # Beneficiary Information
        'Beneficiary English Name': 'BeneficiaryNameEn',
        'BeneficiaryEnglishName': 'BeneficiaryNameEn',
        'BeneficiaryNameEn': 'BeneficiaryNameEn',
        
        # IBAN
        'IBAN': 'IbanNumber',
        'Iban': 'IbanNumber',
        'IbanNumber': 'IbanNumber',
        
        # Transfer Information
        'Transfer Rate': 'TransferRate',
        'TransferRate': 'TransferRate',
        
        'Print Status': 'PrintStatus',
        'PrintStatus': 'PrintStatus',
        
        # Bank Statement Fields
        'Award Ref': 'AwardRef',
        'AwardRef': 'AwardRef',
        'Award Ref 10 Digits': 'AwardRef10Digits',
        'AwardRef10Digits': 'AwardRef10Digits',
        'Bank Reference': 'BankReference',
        'BankReference': 'BankReference',
        'Transfer Amount': 'TransferAmount',
        'TransferAmount': 'TransferAmount',
        'Transfer Date': 'TransferDate',
        'TransferDate': 'TransferDate',
        'Transaction Date': 'TransactionDate',
        'TransactionDate': 'TransactionDate',
        'Value Date': 'ValueDate',
        'ValueDate': 'ValueDate',
        'Beneficiary Name': 'BeneficiaryName',
        'BeneficiaryName': 'BeneficiaryName',
        'Currency Code': 'CurrencyCode',
        'CurrencyCode': 'CurrencyCode',
        'Debit': 'Debit',
        'Credit': 'Credit',
    }
    
    # حقول الأرقام التعريفية التي يجب حمايتها
    ID_FIELDS = [
        'OwnerQatariID',
        'TrainerQatariId',
        'OwnerNumber',
        'JockeyQatariId',
    ]
    
    def __init__(self):
        self.applied_mappings = []
        self.removed_columns = []
        self.protected_fields = []
    
    def normalize_dataframe(self, df: pd.DataFrame, df_name: str = "DataFrame") -> pd.DataFrame:
        """
        توحيد DataFrame بشكل كامل
        
        Args:
            df: DataFrame للتوحيد
            df_name: اسم للتوثيق
            
        Returns:
            DataFrame موحد
        """
        df = df.copy()
        original_columns = df.columns.tolist()
        
        print(f"\n🔧 توحيد البيانات: {df_name}")
        print(f"   الأعمدة الأصلية: {len(original_columns)}")
        
        # 0. **حماية مسبقة شاملة**: إزالة أي أعمدة Unnamed (case-insensitive check)
        unnamed_cols_strict = [col for col in df.columns if 'unnamed' in str(col).lower()]
        if unnamed_cols_strict:
            df = df.drop(columns=unnamed_cols_strict)
            self.removed_columns.extend(unnamed_cols_strict)
            print(f"   🔴 حماية طارئة: حذف {len(unnamed_cols_strict)} عمود Unnamed: {unnamed_cols_strict}")
        
        # 1. إزالة أعمدة Unnamed (legacy check with .startswith)
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed')]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
            self.removed_columns.extend(unnamed_cols)
            print(f"   ✅ إزالة {len(unnamed_cols)} عمود Unnamed")
        
        # 2. تنظيف أسماء الأعمدة
        df.columns = df.columns.str.strip()
        
        # 2.5. **معالجة الأعمدة المكررة قبل التوحيد**
        if df.columns.duplicated().any():
            duplicated_cols = df.columns[df.columns.duplicated(keep=False)].unique().tolist()
            print(f"   ⚠️ أعمدة مكررة مكتشفة: {duplicated_cols}")
            
            # إنشاء أسماء أعمدة فريدة بإضافة رقم تسلسلي
            new_cols = []
            col_counts = {}
            for col in df.columns:
                if col in col_counts:
                    col_counts[col] += 1
                    new_cols.append(f"{col}_dup{col_counts[col]}")
                else:
                    col_counts[col] = 0
                    new_cols.append(col)
            
            df.columns = new_cols
            print(f"   🔧 إعادة تسمية الأعمدة المكررة بإضافة _dup suffix")
        
        # 3. تطبيق خريطة التوحيد
        mappings_applied = {}
        for col in df.columns:
            if col in self.COLUMN_MAPPING:
                new_name = self.COLUMN_MAPPING[col]
                if col != new_name:
                    mappings_applied[col] = new_name
                    self.applied_mappings.append({
                        'DataFrame': df_name,
                        'Original': col,
                        'Unified': new_name
                    })
        
        if mappings_applied:
            df = df.rename(columns=mappings_applied)
            print(f"   ✅ توحيد {len(mappings_applied)} عمود")
        
        # 4. حماية الحقول الرقمية التعريفية
        for field in self.ID_FIELDS:
            if field in df.columns:
                try:
                    # التأكد من أن field هو string وليس list/tuple
                    if not isinstance(field, str):
                        print(f"   ⚠️ تخطي حقل غير صالح: {field} (نوعه: {type(field)})")
                        continue
                    
                    # التأكد من أن df[field] يرجع Series وليس DataFrame
                    col_data = df[field]
                    if isinstance(col_data, pd.DataFrame):
                        print(f"   ⚠️ تخطي {field}: يرجع DataFrame بدلاً من Series")
                        continue
                    
                    # تحويل لنص وإزالة .0 إن وجدت
                    df[field] = col_data.astype(str).str.replace('.0', '', regex=False).str.strip()
                    # استبدال nan/None بقيمة فارغة
                    df[field] = df[field].replace(['nan', 'None', 'NaN'], '')
                    self.protected_fields.append(field)
                except Exception as e:
                    print(f"   ⚠️ خطأ في حماية الحقل {field}: {str(e)}")
                    continue
        
        if self.protected_fields:
            print(f"   🔒 حماية {len(set(self.protected_fields))} حقل رقمي")
        
        # 5. تنظيف قيم نصية عامة
        text_fields = ['Season', 'Race', 'OwnerName']
        for field in text_fields:
            if field in df.columns:
                try:
                    col_data = df[field]
                    if isinstance(col_data, pd.DataFrame):
                        print(f"   ⚠️ تخطي {field}: يرجع DataFrame بدلاً من Series")
                        continue
                    df[field] = col_data.astype(str).str.strip()
                    df[field] = df[field].apply(lambda x: ' '.join(str(x).split()))  # دمج مسافات متعددة
                except Exception as e:
                    print(f"   ⚠️ خطأ في تنظيف النص {field}: {str(e)}")
                    continue
        
        # 6. تنظيف وتحويل المبالغ
        amount_fields = ['AwardAmount', 'TransferAmount', 'Debit', 'Credit']
        for field in amount_fields:
            if field in df.columns:
                try:
                    col_data = df[field]
                    if isinstance(col_data, pd.DataFrame):
                        print(f"   ⚠️ تخطي {field}: يرجع DataFrame بدلاً من Series")
                        continue
                    # إزالة رموز العملة والفواصل
                    df[field] = col_data.astype(str).str.replace(r'[^\d.-]', '', regex=True)
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                    df[field] = df[field].round(2)
                except Exception as e:
                    print(f"   ⚠️ خطأ في تحويل المبلغ {field}: {str(e)}")
                    continue
        
        # 7. تحويل التواريخ
        date_fields = ['EntryDate', 'TransferDate', 'TransactionDate', 'ValueDate']
        for field in date_fields:
            if field in df.columns:
                try:
                    col_data = df[field]
                    if isinstance(col_data, pd.DataFrame):
                        print(f"   ⚠️ تخطي {field}: يرجع DataFrame بدلاً من Series")
                        continue
                    df[field] = pd.to_datetime(col_data, errors='coerce')
                except Exception as e:
                    print(f"   ⚠️ خطأ في تحويل التاريخ {field}: {str(e)}")
                    continue
        
        print(f"   ✅ الأعمدة بعد التوحيد: {len(df.columns)}")
        
        return df
    
    def get_mapping_documentation(self) -> pd.DataFrame:
        """
        توثيق جميع التوحيدات المطبقة
        
        Returns:
            DataFrame يحتوي على خريطة التوحيد
        """
        if not self.applied_mappings:
            return pd.DataFrame({
                'DataFrame': ['لا توجد توحيدات'],
                'Original': [''],
                'Unified': ['']
            })
        
        return pd.DataFrame(self.applied_mappings)
    
    def get_full_mapping_table(self) -> pd.DataFrame:
        """
        جدول التوحيد الكامل (جميع الخرائط المتاحة)
        
        Returns:
            DataFrame يحتوي على جميع الخرائط المعرّفة
        """
        mappings = []
        for original, unified in self.COLUMN_MAPPING.items():
            if original != unified:  # فقط الخرائط التي تُغيّر الاسم
                mappings.append({
                    'Original_Name': original,
                    'Unified_Name': unified,
                    'Category': self._categorize_field(unified)
                })
        
        return pd.DataFrame(mappings)
    
    def _categorize_field(self, field_name: str) -> str:
        """تصنيف الحقل حسب نوعه"""
        if 'Owner' in field_name:
            return 'Owner Information'
        elif 'Award' in field_name or 'Amount' in field_name:
            return 'Award Information'
        elif 'Payment' in field_name or 'Reference' in field_name:
            return 'Payment Information'
        elif 'Bank' in field_name or 'Transfer' in field_name:
            return 'Bank Information'
        elif 'Date' in field_name:
            return 'Date Fields'
        else:
            return 'Other'


# ============================================================================
# القسم 2: EnhancedBankMatcher - مطابق البنك المتقدم
# ============================================================================

class EnhancedBankMatcher:
    """
    مطابق البنك المتقدم - Enhanced Bank Matcher
    
    الغرض: مطابقة دقيقة بين سجلات الجوائز وكشف البنك
    
    Features:
    - دعم جميع مراجع الدفع (PaymentReference, D1, D2, D3)
    - مطابقة مرنة (آخر N أرقام)
    - فحص المبلغ والتاريخ
    - تصنيف ثلاثي: Matched / Partial / Unmatched
    """
    
    def __init__(
        self,
        ref_last_digits: int = 10,
        amount_tolerance: float = 0.00,
        date_window_days: int = 14
    ):
        """
        Args:
            ref_last_digits: عدد الأرقام الأخيرة للمطابقة المرنة
            amount_tolerance: التسامح في المبلغ (0.00 = تطابق تام)
            date_window_days: نافذة التاريخ المسموحة (±days)
        """
        self.ref_last_digits = ref_last_digits
        self.amount_tolerance = amount_tolerance
        self.date_window_days = date_window_days
        
        self.matched_records = []
        self.partial_records = []
        self.unmatched_records = []
    
    def match_awards_to_bank(
        self,
        awards_df: pd.DataFrame,
        bank_df: pd.DataFrame
    ) -> Dict[str, pd.DataFrame]:
        """
        مطابقة جميع سجلات الجوائز مع كشف البنك
        
        Args:
            awards_df: DataFrame الجوائز
            bank_df: DataFrame البنك
            
        Returns:
            قاموس يحتوي على: matched, partial, unmatched
        """
        print("\n" + "="*80)
        print("🏦 مطابقة البنك المتقدمة")
        print("="*80)
        print(f"   📋 إعدادات المطابقة:")
        print(f"      • آخر {self.ref_last_digits} أرقام للمطابقة المرنة")
        print(f"      • التسامح في المبلغ: {self.amount_tolerance:.2f} ريال")
        print(f"      • نافذة التاريخ: ±{self.date_window_days} يوم")
        
        # تحضير بيانات البنك
        bank_df = self._prepare_bank_data(bank_df)
        
        total = len(awards_df)
        print(f"\n🔄 معالجة {total:,} سجل...")
        
        # معالجة كل سجل
        for idx, row in awards_df.iterrows():
            match_result = self._match_single_award(row, bank_df)
            
            # تصنيف النتيجة
            if match_result['status'] == 'MATCHED_100':
                self.matched_records.append(match_result['data'])
            elif match_result['status'] == 'PARTIAL':
                self.partial_records.append(match_result['data'])
            else:
                self.unmatched_records.append(match_result['data'])
        
        # تحويل إلى DataFrames
        matched_df = pd.DataFrame(self.matched_records) if self.matched_records else pd.DataFrame()
        partial_df = pd.DataFrame(self.partial_records) if self.partial_records else pd.DataFrame()
        unmatched_df = pd.DataFrame(self.unmatched_records) if self.unmatched_records else pd.DataFrame()
        
        # إحصائيات
        self._print_statistics(matched_df, partial_df, unmatched_df, total)
        
        return {
            'matched': matched_df,
            'partial': partial_df,
            'unmatched': unmatched_df
        }
    
    def _prepare_bank_data(self, bank_df: pd.DataFrame) -> pd.DataFrame:
        """تحضير وتنظيف بيانات البنك"""
        bank_df = bank_df.copy()
        
        # تنظيف حقول المراجع
        ref_fields = ['AwardRef', 'AwardRef10Digits', 'BankReference']
        for field in ref_fields:
            if field in bank_df.columns:
                bank_df[field] = bank_df[field].astype(str).str.strip()
                bank_df[field] = bank_df[field].str.replace(r'[^\w]', '', regex=True)
                bank_df[field] = bank_df[field].str.lower()
        
        # التأكد من أن المبلغ رقمي
        if 'TransferAmount' in bank_df.columns:
            bank_df['TransferAmount'] = pd.to_numeric(bank_df['TransferAmount'], errors='coerce')
        
        return bank_df
    
    def _extract_all_references(self, row: pd.Series) -> List[str]:
        """استخراج جميع المراجع من سجل جائزة"""
        refs = []
        ref_fields = ['PaymentReference', 'PaymentReference_D1', 'PaymentReference_D2', 'PaymentReference_D3']
        
        for field in ref_fields:
            try:
                if field in row.index:
                    value = row[field]
                    # التحقق من أن القيمة ليست Series
                    if isinstance(value, pd.Series):
                        continue
                    if pd.notna(value) and value is not None:
                        ref = str(value).strip()
                        if ref and ref.lower() not in ['nan', 'none', '']:
                            refs.append(ref)
            except:
                continue
        
        return refs
    
    def _clean_reference(self, ref: str) -> str:
        """تنظيف رقم مرجعي"""
        ref = str(ref).strip()
        ref = re.sub(r'[^\w]', '', ref)  # إزالة كل ما عدا حروف وأرقام
        ref = ref.lower()
        return ref
    
    def _match_single_award(self, award_row: pd.Series, bank_df: pd.DataFrame) -> Dict:
        """مطابقة سجل جائزة واحد مع البنك"""
        
        # استخراج بيانات الجائزة
        award_data = award_row.to_dict()
        award_refs = self._extract_all_references(award_row)
        award_amount = award_row.get('AwardAmount', 0)
        award_date = award_row.get('EntryDate')
        
        # إذا لم يكن هناك مراجع
        if not award_refs:
            award_data['MatchStatus'] = 'NO_REFERENCE'
            award_data['MatchReason'] = '❌ لا يوجد رقم مرجعي'
            return {'status': 'UNMATCHED', 'data': award_data}
        
        # محاولة المطابقة مع كل مرجع
        for ref in award_refs:
            ref_clean = self._clean_reference(ref)
            
            if len(ref_clean) < self.ref_last_digits:
                continue
            
            # البحث في البنك
            bank_matches = self._find_bank_matches(ref_clean, bank_df)
            
            if len(bank_matches) > 0:
                # فحص المبلغ
                amount_match = self._verify_amount(award_amount, bank_matches)
                
                if amount_match is not None:
                    # مطابقة كاملة 100%
                    award_data['MatchStatus'] = 'MATCHED_100'
                    award_data['MatchReason'] = '✅ مطابقة بنكية كاملة'
                    award_data['MatchedReference'] = ref
                    award_data['BankTransferAmount'] = amount_match.get('TransferAmount')
                    award_data['BankTransactionDate'] = amount_match.get('TransactionDate')
                    award_data['BankValueDate'] = amount_match.get('ValueDate')
                    award_data['BankBeneficiary'] = amount_match.get('BeneficiaryName')
                    award_data['BankReference'] = amount_match.get('BankReference')
                    award_data['BankIBAN'] = amount_match.get('IBAN')
                    award_data['AmountDifference'] = 0.00
                    
                    # فحص التاريخ (اختياري)
                    if award_date and pd.notna(award_date):
                        date_check = self._verify_date(award_date, amount_match)
                        award_data['DateCheck'] = date_check
                    
                    return {'status': 'MATCHED_100', 'data': award_data}
                else:
                    # مرجع مطابق لكن مبلغ مختلف = PARTIAL
                    best_match = bank_matches.iloc[0]
                    bank_amount = best_match.get('TransferAmount', 0)
                    diff = abs(award_amount - bank_amount) if bank_amount else 0
                    
                    award_data['MatchStatus'] = 'PARTIAL'
                    award_data['MatchReason'] = f'⚠️ Ref مطابق - مبلغ مختلف (فرق: {diff:.2f})'
                    award_data['MatchedReference'] = ref
                    award_data['BankTransferAmount'] = bank_amount
                    award_data['AmountDifference'] = diff
                    award_data['BankReference'] = best_match.get('BankReference')
                    
                    return {'status': 'PARTIAL', 'data': award_data}
        
        # لم يتم العثور على أي مطابقة
        award_data['MatchStatus'] = 'UNMATCHED'
        award_data['MatchReason'] = '❌ Ref غير موجود بالبنك'
        award_data['AttemptedRefs'] = ' | '.join(award_refs)
        
        return {'status': 'UNMATCHED', 'data': award_data}
    
    def _find_bank_matches(self, ref_clean: str, bank_df: pd.DataFrame) -> pd.DataFrame:
        """البحث عن مطابقات في البنك"""
        ref_last = ref_clean[-self.ref_last_digits:]
        
        # البحث في جميع الأعمدة الممكنة
        matches = pd.DataFrame()
        
        # قائمة الأعمدة المحتملة للمراجع
        possible_ref_columns = ['AwardRef', 'AwardRef10Digits', 'BankReference', 'PaymentReference']
        
        for col in possible_ref_columns:
            if col in bank_df.columns:
                col_matches = bank_df[
                    bank_df[col].astype(str).str.contains(ref_last, na=False, case=False)
                ]
                if len(col_matches) > 0:
                    matches = pd.concat([matches, col_matches], ignore_index=True)
        
        # إزالة التكرارات
        if len(matches) > 0:
            matches = matches.drop_duplicates()
        
        return matches
    
    def _verify_amount(self, award_amount: float, bank_matches: pd.DataFrame) -> Optional[Dict]:
        """التحقق من المبلغ"""
        for idx, bank_row in bank_matches.iterrows():
            bank_amount = bank_row.get('TransferAmount')
            
            if pd.isna(bank_amount):
                continue
            
            diff = abs(award_amount - bank_amount)
            
            if diff <= self.amount_tolerance:
                return bank_row.to_dict()
        
        return None
    
    def _verify_date(self, award_date: pd.Timestamp, bank_row: Dict) -> str:
        """التحقق من التاريخ"""
        bank_date = bank_row.get('TransactionDate') or bank_row.get('ValueDate')
        
        if pd.isna(bank_date):
            return 'تاريخ البنك غير متاح'
        
        diff_days = abs((award_date - bank_date).days)
        
        if diff_days <= self.date_window_days:
            return f'✅ ضمن النافذة ({diff_days} يوم)'
        else:
            return f'⚠️ خارج النافذة ({diff_days} يوم)'
    
    def _print_statistics(self, matched, partial, unmatched, total):
        """طباعة الإحصائيات"""
        matched_count = len(matched)
        partial_count = len(partial)
        unmatched_count = len(unmatched)
        
        match_rate = (matched_count / total * 100) if total > 0 else 0
        partial_rate = (partial_count / total * 100) if total > 0 else 0
        
        print(f"\n📊 نتائج المطابقة:")
        print(f"   إجمالي السجلات: {total:,}")
        print(f"   ✅ مطابق 100%: {matched_count:,} ({match_rate:.1f}%)")
        print(f"   ⚠️ جزئي/مشتبه: {partial_count:,} ({partial_rate:.1f}%)")
        print(f"   ❌ غير مطابق: {unmatched_count:,} ({100-match_rate-partial_rate:.1f}%)")
        
        # تفصيل أسباب عدم المطابقة
        if unmatched_count > 0 and len(unmatched) > 0:
            print(f"\n⚠️ أسباب عدم المطابقة:")
            if 'MatchReason' in unmatched.columns:
                reasons = unmatched['MatchReason'].value_counts()
                for reason, count in reasons.items():
                    print(f"   • {reason}: {count:,} سجل")


# ============================================================================
# القسم 3: GroundTruthValidator - مدقق الحالات المعروفة
# ============================================================================

class GroundTruthValidator:
    """
    مدقق الحالات المعروفة - Ground Truth Validator
    
    الغرض: التحقق من اكتشاف جميع حالات التكرار المعروفة مسبقاً
    
    Features:
    - 28 حالة مُحددة مسبقاً
    - تقرير مفصل بالحالات المكتشفة/المفقودة
    - نسبة الاكتشاف
    """
    
    # الحالات المعروفة من البرمبت (Ground Truth)
    KNOWN_DUPLICATE_PAIRS = [
        ('821B291050', '821B291373'),
        ('821B731113', '822B731638'),
        ('821B731181', '822B731655'),
        ('821B780256', '821B780936'),
        ('821B780108', '822B780961'),
        ('822B860645', '822B861016', '822B861020'),  # ثلاثي
        ('822B870766', '822B871164'),
        ('822C161124', '824C161706'),
        ('822C160320', '824C161708'),
        ('822C160718', '824C161711'),
        ('822C160760', '822C161657'),
        ('822C220292', '823C220693'),
        ('822C340338', '823C341078'),
        ('823C360755', '823C361534'),
        ('823C360159', '823C361544'),
        ('823C360796', '823C361529'),
        ('822C340243', '823C341104', '823C341106'),  # ثلاثي
        ('824D101013', '824D101473'),
        ('823C360031', '824C361546', '823C361516'),  # ثلاثي
        ('820B150249', '823B150327'),
    ]
    
    def __init__(self):
        self.validation_results = None
    
    def validate_detection(self, duplicates_df: pd.DataFrame) -> Dict:
        """
        التحقق من اكتشاف جميع الحالات المعروفة
        
        Args:
            duplicates_df: DataFrame التكرارات المكتشفة
            
        Returns:
            قاموس يحتوي على نتائج التحقق
        """
        print("\n" + "="*80)
        print("🔍 التحقق من الحالات المعروفة (Ground Truth)")
        print("="*80)
        print(f"   📋 إجمالي الحالات المعروفة: {len(self.KNOWN_DUPLICATE_PAIRS)}")
        
        results = {
            'total_cases': len(self.KNOWN_DUPLICATE_PAIRS),
            'detected': [],
            'missing': [],
            'detection_rate': 0.0
        }
        
        for case_num, case_refs in enumerate(self.KNOWN_DUPLICATE_PAIRS, 1):
            detected, details = self._check_case_detected(case_refs, duplicates_df)
            
            case_info = {
                'case_number': case_num,
                'references': ' & '.join(case_refs),
                'ref_count': len(case_refs),
                'detected': detected,
                'details': details
            }
            
            if detected:
                results['detected'].append(case_info)
            else:
                results['missing'].append(case_info)
        
        detected_count = len(results['detected'])
        results['detection_rate'] = (detected_count / results['total_cases'] * 100) if results['total_cases'] > 0 else 0
        
        # طباعة النتائج
        print(f"\n📊 نتائج التحقق:")
        print(f"   ✅ حالات مكتشفة: {detected_count} / {results['total_cases']}")
        print(f"   ❌ حالات مفقودة: {len(results['missing'])} / {results['total_cases']}")
        print(f"   📈 نسبة الاكتشاف: {results['detection_rate']:.1f}%")
        
        if results['missing']:
            print(f"\n⚠️ الحالات المفقودة:")
            for case in results['missing'][:5]:  # أول 5 فقط
                print(f"   • {case['references']}")
            if len(results['missing']) > 5:
                print(f"   ... و {len(results['missing']) - 5} حالة أخرى")
        
        self.validation_results = results
        return results
    
    def _check_case_detected(self, case_refs: tuple, duplicates_df: pd.DataFrame) -> Tuple[bool, str]:
        """
        التحقق من اكتشاف حالة محددة
        
        Args:
            case_refs: tuple من المراجع المتوقعة
            duplicates_df: DataFrame التكرارات
            
        Returns:
            (detected: bool, details: str)
        """
        ref_columns = ['PaymentReference', 'PaymentReference_D1', 'PaymentReference_D2', 'PaymentReference_D3']
        
        found_refs = set()
        
        for ref in case_refs:
            for col in ref_columns:
                if col in duplicates_df.columns:
                    try:
                        # بحث عن الرقم المرجعي
                        mask = duplicates_df[col].astype(str).str.contains(ref, na=False, case=False)
                        matches = duplicates_df[mask]
                        
                        if len(matches) > 0:
                            found_refs.add(ref)
                            break
                    except:
                        continue
        
        # يجب إيجاد جميع المراجع في الحالة
        detected = len(found_refs) == len(case_refs)
        
        if detected:
            details = f'✅ جميع المراجع ({len(found_refs)}/{len(case_refs)}) مكتشفة'
        else:
            details = f'❌ مراجع ناقصة ({len(found_refs)}/{len(case_refs)}) - مفقود: {set(case_refs) - found_refs}'
        
        return detected, details
    
    def generate_validation_report(self) -> pd.DataFrame:
        """
        إنشاء تقرير تفصيلي للتحقق
        
        Returns:
            DataFrame يحتوي على كل حالة وحالة اكتشافها
        """
        if not self.validation_results:
            return pd.DataFrame()
        
        all_cases = self.validation_results['detected'] + self.validation_results['missing']
        all_cases = sorted(all_cases, key=lambda x: x['case_number'])
        
        report_data = []
        for case in all_cases:
            report_data.append({
                'Case_Number': case['case_number'],
                'References': case['references'],
                'Reference_Count': case['ref_count'],
                'Status': '✅ مكتشف' if case['detected'] else '❌ مفقود',
                'Details': case['details']
            })
        
        return pd.DataFrame(report_data)


# ============================================================================
# القسم 4: ComprehensiveReportGenerator - مولد التقارير الشامل
# ============================================================================

class ComprehensiveReportGenerator:
    """
    مولد التقارير الشامل - Comprehensive Report Generator
    
    الغرض: إنشاء جميع التقارير المطلوبة حسب البرمبت
    
    Reports:
    1. Awards_Duplicates_[timestamp].xlsx
    2. Bank_Match_Verification_[timestamp].xlsx
    3. Ground_Truth_Validation_[timestamp].xlsx
    """
    
    def __init__(
        self,
        duplicates: pd.DataFrame,
        normalizer: DataNormalizer,
        bank_matcher: EnhancedBankMatcher,
        ground_truth_validator: GroundTruthValidator,
        output_dir: str = "outputs"
    ):
        self.duplicates = duplicates
        self.normalizer = normalizer
        self.bank_matcher = bank_matcher
        self.ground_truth_validator = ground_truth_validator
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # التوقيت حسب الدوحة
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_all_reports(self) -> Dict[str, str]:
        """
        إنشاء جميع التقارير
        
        Returns:
            قاموس بمسارات الملفات المُنشأة
        """
        print("\n" + "="*80)
        print("📄 إنشاء التقارير الشاملة")
        print("="*80)
        
        generated_files = {}
        
        # Report 1: Duplicates
        dup_file = self.generate_duplicates_report()
        if dup_file:
            generated_files['duplicates'] = str(dup_file)
        
        # Report 2: Bank Verification
        bank_file = self.generate_bank_verification_report()
        if bank_file:
            generated_files['bank_verification'] = str(bank_file)
        
        # Report 3: Ground Truth
        gt_file = self.generate_ground_truth_report()
        if gt_file:
            generated_files['ground_truth'] = str(gt_file)
        
        return generated_files
    
    def generate_duplicates_report(self) -> Optional[Path]:
        """
        تقرير التكرارات الشامل
        
        Sheets:
        1. Duplicates_AllRows
        2. Duplicates_Summary
        3. Data_Dictionary
        """
        if self.duplicates is None or len(self.duplicates) == 0:
            print("   ⚠️ لا توجد تكرارات للتصدير")
            return None
        
        file_path = self.output_dir / f"Awards_Duplicates_{self.timestamp}.xlsx"
        
        print(f"\n📝 التقرير 1: تقرير التكرارات")
        print(f"   الملف: {file_path.name}")
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Sheet 1: Duplicates_AllRows
            export_cols = [
                'Season', 'Race', 'OwnerNumber', 'OwnerName', 'OwnerQatariID',
                'AwardAmount', 'EntryDate',
                'PaymentReference', 'PaymentReference_D1', 'PaymentReference_D2', 'PaymentReference_D3',
                '_DuplicateGroup', '_DuplicateCount', '_DuplicateSeverity',
                'ReasonText', 'SourceFile'
            ]
            available = [c for c in export_cols if c in self.duplicates.columns]
            self.duplicates[available].to_excel(writer, sheet_name='Duplicates_AllRows', index=False)
            print(f"   ✅ Sheet 1: Duplicates_AllRows ({len(self.duplicates):,} سجل)")
            
            # Sheet 2: Duplicates_Summary
            if '_DuplicateGroup' in self.duplicates.columns:
                summary = self.duplicates.groupby('_DuplicateGroup').agg({
                    'AwardAmount': ['first', 'sum', 'count'],
                    'EntryDate': ['min', 'max'] if 'EntryDate' in self.duplicates.columns else ['count'],
                    'OwnerName': 'first',
                    'OwnerNumber': 'first',
                    'Race': 'first',
                    'Season': 'first'
                }).reset_index()
                
                summary.columns = ['GroupID', 'Amount', 'TotalAmount', 'Count', 
                                 'FirstDate', 'LastDate', 'Owner', 'OwnerNumber', 'Race', 'Season']
                summary = summary.sort_values('Count', ascending=False)
                
                summary.to_excel(writer, sheet_name='Duplicates_Summary', index=False)
                print(f"   ✅ Sheet 2: Duplicates_Summary ({len(summary):,} مجموعة)")
            
            # Sheet 3: Data_Dictionary
            dictionary = self.normalizer.get_mapping_documentation()
            dictionary.to_excel(writer, sheet_name='Data_Dictionary', index=False)
            print(f"   ✅ Sheet 3: Data_Dictionary ({len(dictionary):,} توحيد)")
        
        print(f"   ✅ تم الحفظ: {file_path.name}")
        return file_path
    
    def generate_bank_verification_report(self) -> Optional[Path]:
        """
        تقرير التحقق البنكي الشامل
        
        Sheets:
        1. Bank_Matches
        2. Bank_PartialOrSuspected
        3. Bank_Unmatched
        4. Notes
        """
        matched = pd.DataFrame(self.bank_matcher.matched_records)
        partial = pd.DataFrame(self.bank_matcher.partial_records)
        unmatched = pd.DataFrame(self.bank_matcher.unmatched_records)
        
        if len(matched) == 0 and len(partial) == 0 and len(unmatched) == 0:
            print("   ⚠️ لا توجد بيانات تحقق بنكي")
            return None
        
        file_path = self.output_dir / f"Bank_Match_Verification_{self.timestamp}.xlsx"
        
        print(f"\n📝 التقرير 2: تقرير التحقق البنكي")
        print(f"   الملف: {file_path.name}")
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Sheet 1: Bank_Matches
            if len(matched) > 0:
                matched.to_excel(writer, sheet_name='Bank_Matches', index=False)
                print(f"   ✅ Sheet 1: Bank_Matches ({len(matched):,} سجل)")
            
            # Sheet 2: Bank_PartialOrSuspected
            if len(partial) > 0:
                partial.to_excel(writer, sheet_name='Bank_PartialOrSuspected', index=False)
                print(f"   ⚠️ Sheet 2: Bank_PartialOrSuspected ({len(partial):,} سجل)")
            
            # Sheet 3: Bank_Unmatched
            if len(unmatched) > 0:
                unmatched.to_excel(writer, sheet_name='Bank_Unmatched', index=False)
                print(f"   ❌ Sheet 3: Bank_Unmatched ({len(unmatched):,} سجل)")
            
            # Sheet 4: Notes
            notes = self._generate_notes()
            notes.to_excel(writer, sheet_name='Notes', index=False)
            print(f"   ✅ Sheet 4: Notes ({len(notes):,} ملاحظة)")
        
        print(f"   ✅ تم الحفظ: {file_path.name}")
        return file_path
    
    def generate_ground_truth_report(self) -> Optional[Path]:
        """
        تقرير التحقق من الحالات المعروفة
        
        Sheets:
        1. Validation_Results
        2. Summary
        """
        if not self.ground_truth_validator.validation_results:
            print("   ⚠️ لا توجد نتائج تحقق من الحالات المعروفة")
            return None
        
        file_path = self.output_dir / f"Ground_Truth_Validation_{self.timestamp}.xlsx"
        
        print(f"\n📝 التقرير 3: تقرير الحالات المعروفة")
        print(f"   الملف: {file_path.name}")
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Sheet 1: Validation_Results
            report = self.ground_truth_validator.generate_validation_report()
            report.to_excel(writer, sheet_name='Validation_Results', index=False)
            print(f"   ✅ Sheet 1: Validation_Results ({len(report):,} حالة)")
            
            # Sheet 2: Summary
            results = self.ground_truth_validator.validation_results
            summary = pd.DataFrame({
                'Metric': [
                    'إجمالي الحالات المعروفة',
                    'حالات مكتشفة',
                    'حالات مفقودة',
                    'نسبة الاكتشاف'
                ],
                'Value': [
                    results['total_cases'],
                    len(results['detected']),
                    len(results['missing']),
                    f"{results['detection_rate']:.1f}%"
                ]
            })
            summary.to_excel(writer, sheet_name='Summary', index=False)
            print(f"   ✅ Sheet 2: Summary")
        
        print(f"   ✅ تم الحفظ: {file_path.name}")
        return file_path
    
    def _generate_notes(self) -> pd.DataFrame:
        """إنشاء ملاحظات التقرير"""
        notes_data = []
        
        # Settings
        notes_data.append({
            'Category': 'Settings',
            'Item': 'REF_LAST_DIGITS',
            'Value': str(self.bank_matcher.ref_last_digits),
            'Description': 'عدد الأرقام الأخيرة للمطابقة المرنة'
        })
        notes_data.append({
            'Category': 'Settings',
            'Item': 'AMOUNT_TOLERANCE',
            'Value': f"{self.bank_matcher.amount_tolerance:.2f}",
            'Description': 'التسامح في فرق المبلغ (0.00 = تطابق تام)'
        })
        notes_data.append({
            'Category': 'Settings',
            'Item': 'DATE_WINDOW_DAYS',
            'Value': str(self.bank_matcher.date_window_days),
            'Description': 'نافذة التاريخ المسموحة (±أيام)'
        })
        
        # Statistics
        notes_data.append({
            'Category': 'Statistics',
            'Item': 'Total Matched',
            'Value': str(len(self.bank_matcher.matched_records)),
            'Description': 'عدد السجلات المطابقة 100%'
        })
        notes_data.append({
            'Category': 'Statistics',
            'Item': 'Total Partial',
            'Value': str(len(self.bank_matcher.partial_records)),
            'Description': 'عدد السجلات الجزئية/المشتبهة'
        })
        notes_data.append({
            'Category': 'Statistics',
            'Item': 'Total Unmatched',
            'Value': str(len(self.bank_matcher.unmatched_records)),
            'Description': 'عدد السجلات غير المطابقة'
        })
        
        # Assumptions
        notes_data.append({
            'Category': 'Assumptions',
            'Item': 'Reference Matching',
            'Value': 'Last 10 digits',
            'Description': 'المطابقة بآخر 10 أرقام من المرجع'
        })
        notes_data.append({
            'Category': 'Assumptions',
            'Item': 'Amount Matching',
            'Value': 'Exact match (0.00)',
            'Description': 'المبلغ يجب أن يتطابق بالكامل'
        })
        notes_data.append({
            'Category': 'Assumptions',
            'Item': 'Multiple References',
            'Value': 'PaymentReference + D1/D2/D3',
            'Description': 'يتم فحص جميع المراجع الأربعة'
        })
        
        return pd.DataFrame(notes_data)


# ============================================================================
# نهاية الكود - Enhanced Audit System
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("نظام التدقيق المحسّن - Enhanced Audit System")
    print("="*80)
    print("\nهذا ملف مكتبة (Library) - استخدمه من خلال:")
    print("  from core.enhanced_audit_system import DataNormalizer, EnhancedBankMatcher, ...")
    print("="*80)
