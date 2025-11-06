# -*- coding: utf-8 -*-
"""
🏆 محلل جوائز سباقات الهجن
Camel Race Awards Analyzer
================================
نظام متقدم لتحليل ومطابقة جوائز سباقات الهجن مع كشوفات البنك
واكتشاف الصرف المكرر والتأكد من سلامة البيانات

الميزات المتقدمة v2.0:
- مطابقة 3 طبقات: Exact → Fuzzy → Record Linkage
- تسجيل شامل مع Audit Trail
- أداء محسّن للملفات الكبيرة
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import re
from rapidfuzz import fuzz
import warnings
import time

warnings.filterwarnings('ignore')

# استيراد المكونات المتقدمة
try:
    from core.advanced_matcher import AdvancedMatcher
    ADVANCED_MATCHER_AVAILABLE = True
except ImportError:
    ADVANCED_MATCHER_AVAILABLE = False
    warnings.warn("⚠️ Advanced Matcher غير متوفر - استخدام المطابقة الأساسية")

try:
    from core.audit_logger import AuditLogger
    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False
    warnings.warn("⚠️ Audit Logger غير متوفر - لن يتم حفظ السجلات")

try:
    from core.performance_optimizer import PerformanceOptimizer, recommend_optimizer_settings
    PERFORMANCE_OPTIMIZER_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZER_AVAILABLE = False
    warnings.warn("⚠️ Performance Optimizer غير متوفر - استخدام pandas العادي")


class CamelAwardsAnalyzer:
    """محلل جوائز سباقات الهجن - الإصدار المتقدم v2.0"""
    
    def __init__(self, use_advanced_features: bool = True):
        """
        تهيئة المحلل
        
        Args:
            use_advanced_features: استخدام المكونات المتقدمة (مطابقة 3 طبقات، تسجيل، أداء محسّن)
        """
        # المتغيرات الأساسية
        self.awards_data = None
        self.bank_data = None
        self.merged_results = None
        self.statistics = {}
        
        # المكونات المتقدمة
        self.use_advanced_features = use_advanced_features
        self.matcher = None
        self.logger = None
        self.optimizer = None
        self.current_run_id = None
        
        # تهيئة المكونات المتقدمة
        if use_advanced_features:
            if ADVANCED_MATCHER_AVAILABLE:
                self.matcher = AdvancedMatcher(fuzzy_threshold=90)
                print("✅ Advanced Matcher مفعّل")
            
            if AUDIT_LOGGER_AVAILABLE:
                self.logger = AuditLogger(log_dir="outputs/audit_logs")
                print("✅ Audit Logger مفعّل")
            
            # Performance Optimizer يتم تهيئته عند الحاجة
            if PERFORMANCE_OPTIMIZER_AVAILABLE:
                print("✅ Performance Optimizer متاح")
        
    def normalize_text(self, text: str) -> str:
        """
        تطبيع وتوحيد النصوص
        
        Args:
            text: النص المراد تطبيعه
            
        Returns:
            النص المطبّع
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""

        # تحويل القيمة إلى نص وإزالة الفواصل السفلية كمسافات
        text = str(text).replace('_', ' ')
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text).strip()

        # توحيد Unicode (تطبيع الحروف العربية)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ى', 'ي')
        
        # تحويل لأحرف صغيرة
        text = text.lower()
        
        return text
    
    def normalize_column_names(self, df: pd.DataFrame, context: str = "generic") -> pd.DataFrame:
        """
        توحيد أسماء الأعمدة
        
        Args:
            df: DataFrame المراد توحيد أعمدته
            context: سياق البيانات (awards / bank / generic)
            
        Returns:
            DataFrame بأعمدة موحدة
        """
        df_copy = df.copy()
        df_copy.columns = [self.normalize_text(col) for col in df_copy.columns]

        def canonical(label: str) -> str:
            return self.normalize_text(label).replace(' ', '')

        # مجموعات الأسماء الشائعة
        base_groups = {
            'Season': ['season', 'الموسم', 'موسم'],
            'Race': ['race', 'السباق', 'سباق', 'race name', 'اسم السباق'],
            'AwardAmount': ['award amount', 'awardamount', 'amount', 'المبلغ', 'مبلغ', 'القيمة', 'الجائزة', 'value'],
            'EntryDate': ['entrydate', 'entry date', 'date', 'التاريخ', 'تاريخ', 'تاريخ الإدخال', 'تاريخ السباق']
        }

        awards_groups = {
            'OwnerName': ['ownername', 'اسم المالك', 'المالك', 'الاسم', 'owner name']
        }

        bank_groups = {
            'BankName': ['bankname', 'اسم المستفيد', 'المستفيد', 'beneficiary', 'beneficiary name', 'name', 'ownername'],
            'BankAmount': ['bankamount', 'مبلغ التحويل', 'payment amount', 'amount', 'debit', 'credit'],
            'BankDate': ['bankdate', 'تاريخ التحويل', 'تاريخ الدفع', 'payment date', 'transaction date'],
            'BankReference': ['bankreference', 'reference', 'المرجع', 'رقم المرجع', 'رقم العملية', 'request reference', 'bank ref', 'award ref', 'award ref 10 digits']
        }

        def build_mapping(groups: Dict[str, List[str]]) -> Dict[str, str]:
            mapping: Dict[str, str] = {}
            for target, aliases in groups.items():
                for alias in aliases:
                    mapping[canonical(alias)] = target
            return mapping

        mapping = build_mapping(base_groups)

        if context == 'awards':
            mapping.update(build_mapping(awards_groups))
        elif context == 'bank':
            mapping.update(build_mapping(bank_groups))
        else:
            mapping.update(build_mapping(awards_groups))
            mapping.update(build_mapping(bank_groups))

        rename_map: Dict[str, str] = {}
        for col in df_copy.columns:
            key = canonical(col)
            if key in mapping:
                rename_map[col] = mapping[key]

        df_copy.rename(columns=rename_map, inplace=True)

        # معالجة خاصة لسياق البنك: التأكد من تسمية الأعمدة الحرجة
        if context == 'bank':
            if 'BankName' not in df_copy.columns and 'OwnerName' in df_copy.columns:
                df_copy.rename(columns={'OwnerName': 'BankName'}, inplace=True)

            if 'BankDate' not in df_copy.columns:
                for fallback in ['transaction date', 'value date']:
                    if fallback in df_copy.columns:
                        df_copy.rename(columns={fallback: 'BankDate'}, inplace=True)
                        break

        return df_copy
    
    def load_awards_files(self, files: List[Any]) -> pd.DataFrame:
        """
        تحميل ودمج ملفات الجوائز
        
        Args:
            files: قائمة بملفات Excel للجوائز
            
        Returns:
            DataFrame موحد للجوائز
        """
        all_data = []
        
        for file in files:
            try:
                # قراءة الملف
                if hasattr(file, 'name'):
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file)
                    else:
                        df = pd.read_excel(file)
                else:
                    df = pd.read_excel(file)
                
                # توحيد الأعمدة
                df = self.normalize_column_names(df, context="awards")
                
                all_data.append(df)
                
            except Exception as e:
                print(f"خطأ في تحميل الملف: {str(e)}")
                continue
        
        if not all_data:
            raise ValueError("لم يتم تحميل أي ملفات بنجاح")
        
        # دمج جميع الملفات
        self.awards_data = pd.concat(all_data, ignore_index=True)
        
        # إنشاء عمود الاسم المطبّع
        if 'OwnerName' in self.awards_data.columns:
            self.awards_data['OwnerName_norm'] = self.awards_data['OwnerName'].apply(self.normalize_text)
        
        # تحويل التواريخ
        if 'EntryDate' in self.awards_data.columns:
            self.awards_data['EntryDate'] = pd.to_datetime(
                self.awards_data['EntryDate'], 
                errors='coerce',
                dayfirst=True
            )
        
        # تحويل المبالغ لأرقام
        if 'AwardAmount' in self.awards_data.columns:
            self.awards_data['AwardAmount'] = pd.to_numeric(
                self.awards_data['AwardAmount'], 
                errors='coerce'
            )
        
        return self.awards_data
    
    def load_bank_statement(self, file: Any) -> pd.DataFrame:
        """
        تحميل كشف البنك
        
        Args:
            file: ملف Excel لكشف البنك
            
        Returns:
            DataFrame لكشف البنك
        """
        try:
            # قراءة الملف
            if hasattr(file, 'name'):
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    # محاولة قراءة من صفوف مختلفة (في حال كانت headers في صف غير الأول)
                    df = pd.read_excel(file, header=None)
                    
                    # البحث عن الصف الذي يحتوي على headers
                    header_row = 0
                    for i in range(min(10, len(df))):
                        row_values = df.iloc[i].astype(str).str.lower()
                        if any('name' in str(v) or 'اسم' in str(v) or 'amount' in str(v) or 'مبلغ' in str(v) for v in row_values):
                            header_row = i
                            break
                    
                    # إعادة قراءة الملف مع الـ header الصحيح
                    if header_row > 0:
                        df = pd.read_excel(file, header=header_row)
                    else:
                        df = pd.read_excel(file)
            else:
                df = pd.read_excel(file)
            
            # توحيد الأعمدة
            df = self.normalize_column_names(df, context="bank")

            # إنشاء عمود المبلغ البنكي إذا لم يتم إيجاده مباشرة
            if 'BankAmount' not in df.columns:
                debit_col = None
                credit_col = None
                for col in df.columns:
                    if col.lower() == 'debit':
                        debit_col = col
                    elif col.lower() == 'credit':
                        credit_col = col
                if debit_col and credit_col:
                    df['BankAmount'] = df[debit_col].fillna(0) - df[credit_col].fillna(0)
                elif debit_col:
                    df['BankAmount'] = df[debit_col]
                elif credit_col:
                    df['BankAmount'] = df[credit_col]

            # تعيين تاريخ البنك من أعمدة بديلة إذا لزم الأمر
            if 'BankDate' not in df.columns:
                for fallback in ['Transaction Date', 'Value Date']:
                    if fallback in df.columns:
                        df.rename(columns={fallback: 'BankDate'}, inplace=True)
                        break
            
            self.bank_data = df
            
            # إنشاء عمود الاسم المطبّع
            if 'BankName' in self.bank_data.columns:
                self.bank_data['BankName_norm'] = self.bank_data['BankName'].apply(self.normalize_text)
            
            # تحويل التواريخ
            if 'BankDate' in self.bank_data.columns:
                self.bank_data['BankDate'] = pd.to_datetime(
                    self.bank_data['BankDate'], 
                    errors='coerce',
                    dayfirst=True
                )
            
            # تحويل المبالغ لأرقام
            if 'BankAmount' in self.bank_data.columns:
                self.bank_data['BankAmount'] = pd.to_numeric(
                    self.bank_data['BankAmount'], 
                    errors='coerce'
                )
            
            return self.bank_data
            
        except Exception as e:
            raise ValueError(f"خطأ في تحميل كشف البنك: {str(e)}")
    
    def match_with_bank(
        self,
        time_window_days: int = 7,
        use_record_linkage: bool = False,
        files_info: Optional[Dict[str, List[str]]] = None
    ) -> pd.DataFrame:
        """
        مطابقة بيانات الجوائز مع كشف البنك (الإصدار المتقدم v2.0)
        
        الميزات الجديدة:
        - مطابقة 3 طبقات: Exact → Fuzzy → Record Linkage
        - تسجيل شامل مع Audit Trail
        - أداء محسّن للملفات الكبيرة
        
        Args:
            time_window_days: نافذة التطابق الزمني بالأيام
            use_record_linkage: استخدام مطابقة Record Linkage (للحالات الصعبة)
            files_info: معلومات الملفات للتسجيل (dict مع مفاتيح 'awards_files', 'bank_file')
            
        Returns:
            DataFrame بنتائج المطابقة المتقدمة
        """
        if self.awards_data is None or self.bank_data is None:
            raise ValueError("يجب تحميل بيانات الجوائز وكشف البنك أولاً")
        
        print(f"\n🔍 بدء المطابقة المتقدمة...")
        print(f"   📊 جوائز: {len(self.awards_data):,} سجل")
        print(f"   🏦 بنك: {len(self.bank_data):,} سجل")
        print(f"   ⏰ نافذة زمنية: ±{time_window_days} يوم")
        
        start_time = time.time()
        
        try:
            # استخدام المطابق المتقدم إذا كان متاحاً
            if self.use_advanced_features and self.matcher and ADVANCED_MATCHER_AVAILABLE:
                print(f"   ✨ استخدام Advanced Matcher (3 طبقات)")
                
                # المطابقة بجميع الطبقات
                matched_df, unmatched_df = self.matcher.match_all_layers(
                    awards_df=self.awards_data,
                    bank_df=self.bank_data,
                    time_window_days=time_window_days,
                    use_record_linkage=use_record_linkage
                )
                
                # إضافة أعمدة إضافية للتوافق
                if len(matched_df) > 0:
                    matched_df['StatusFlag'] = '✅'
                    matched_df['ReasonText'] = matched_df.apply(
                        lambda x: f"مطابقة {x['MatchType']} بنسبة {x['MatchScore']}%",
                        axis=1
                    )
                
                if len(unmatched_df) > 0:
                    unmatched_df['MatchType'] = 'No Match'
                    unmatched_df['MatchScore'] = 0
                    unmatched_df['BankDate'] = None
                    unmatched_df['BankReference'] = None
                    unmatched_df['StatusFlag'] = '⚠️'
                    unmatched_df['ReasonText'] = 'لم يتم العثور على مطابقة'
                
                # دمج النتائج
                self.merged_results = pd.concat([matched_df, unmatched_df], ignore_index=True)
                
            else:
                # استخدام المطابقة الأساسية (الكود القديم)
                print(f"   ⚠️ استخدام المطابقة الأساسية (Exact + Fuzzy فقط)")
                self.merged_results = self._basic_matching(time_window_days)
            
            # حساب الإحصائيات
            execution_time = time.time() - start_time
            
            exact_matches = len(self.merged_results[self.merged_results['MatchType'] == 'Exact'])
            fuzzy_matches = len(self.merged_results[self.merged_results['MatchType'] == 'Fuzzy'])
            rl_matches = len(self.merged_results[self.merged_results['MatchType'] == 'RecordLinkage'])
            unmatched = len(self.merged_results[self.merged_results['MatchType'] == 'No Match'])
            
            self.statistics = {
                'total_awards': len(self.awards_data),
                'total_bank_records': len(self.bank_data),
                'exact_matches': exact_matches,
                'fuzzy_matches': fuzzy_matches,
                'rl_matches': rl_matches,
                'unmatched_awards': unmatched,
                'execution_time': execution_time,
                'time_window_days': time_window_days,
                'use_record_linkage': use_record_linkage
            }
            
            # تسجيل في Audit Logger
            if self.use_advanced_features and self.logger and AUDIT_LOGGER_AVAILABLE:
                try:
                    # تحديد أسماء الملفات
                    if files_info:
                        awards_files = files_info.get('awards_files', ['unknown'])
                        bank_file = files_info.get('bank_file', 'unknown')
                    else:
                        awards_files = ['multiple_files']
                        bank_file = 'bank_statement.xlsx'
                    
                    self.current_run_id = self.logger.log_analysis_run(
                        awards_files=awards_files,
                        bank_file=bank_file,
                        statistics=self.statistics,
                        time_window_days=time_window_days,
                        fuzzy_threshold=90,
                        use_record_linkage=use_record_linkage,
                        execution_time=execution_time,
                        user_name="System",
                        status="Success"
                    )
                    
                    # تسجيل المطابقات
                    if len(self.merged_results[self.merged_results['MatchType'] != 'No Match']) > 0:
                        matches_only = self.merged_results[self.merged_results['MatchType'] != 'No Match']
                        self.logger.log_matches(self.current_run_id, matches_only)
                    
                    print(f"   📝 تم التسجيل: RunID={self.current_run_id[:8]}...")
                    
                except Exception as e:
                    print(f"   ⚠️ تحذير: فشل التسجيل - {str(e)}")
            
            # عرض النتائج
            print(f"\n✅ اكتملت المطابقة في {execution_time:.2f} ثانية")
            print(f"   ✔️ مطابقات حتمية: {exact_matches}")
            print(f"   ✔️ مطابقات ضبابية: {fuzzy_matches}")
            if rl_matches > 0:
                print(f"   ✔️ مطابقات RL: {rl_matches}")
            print(f"   ⚠️ غير مطابق: {unmatched}")
            
            return self.merged_results
            
        except Exception as e:
            # تسجيل الخطأ
            if self.use_advanced_features and self.logger and AUDIT_LOGGER_AVAILABLE:
                try:
                    self.logger.log_error(
                        error_type=type(e).__name__,
                        error_message=str(e),
                        context={
                            'function': 'match_with_bank',
                            'time_window_days': time_window_days,
                            'use_record_linkage': use_record_linkage
                        }
                    )
                except:
                    pass
            
            print(f"❌ خطأ في المطابقة: {str(e)}")
            raise
    
    def _basic_matching(self, time_window_days: int) -> pd.DataFrame:
        """
        المطابقة الأساسية (Exact + Fuzzy فقط)
        النسخة الاحتياطية إذا لم تتوفر المكونات المتقدمة
        """
        results = []
        
        for idx, award_row in self.awards_data.iterrows():
            result = {
                'OwnerName': award_row.get('OwnerName', ''),
                'Race': award_row.get('Race', ''),
                'Season': award_row.get('Season', ''),
                'AwardAmount': award_row.get('AwardAmount', 0),
                'EntryDate': award_row.get('EntryDate', None),
                'BankDate': None,
                'BankReference': None,
                'MatchScore': 0,
                'StatusFlag': '',
                'ReasonText': '',
                'MatchType': 'No Match'
            }
            
            owner_name = award_row.get('OwnerName_norm', '')
            award_amount = award_row.get('AwardAmount', 0)
            entry_date = award_row.get('EntryDate', None)
            
            if pd.isna(award_amount) or pd.isna(entry_date):
                result['StatusFlag'] = '⚠️'
                result['ReasonText'] = 'بيانات ناقصة'
                results.append(result)
                continue
            
            # البحث في كشف البنك
            best_match = None
            best_score = 0
            
            for _, bank_row in self.bank_data.iterrows():
                bank_amount = bank_row.get('BankAmount', 0)
                bank_date = bank_row.get('BankDate', None)
                bank_name = bank_row.get('BankName_norm', '')
                
                if pd.isna(bank_amount) or pd.isna(bank_date):
                    continue
                
                # تحقق من المبلغ
                if abs(award_amount - bank_amount) > 0.01:
                    continue
                
                # تحقق من النافذة الزمنية
                date_diff = abs((entry_date - bank_date).days)
                if date_diff > time_window_days:
                    continue
                
                # الطبقة 1: مطابقة تامة
                if owner_name == bank_name:
                    best_match = bank_row
                    best_score = 100
                    result['MatchType'] = 'Exact'
                    break
                
                # الطبقة 2: مطابقة ضبابية
                fuzzy_score = fuzz.ratio(owner_name, bank_name)
                if fuzzy_score >= 90 and fuzzy_score > best_score:
                    best_match = bank_row
                    best_score = fuzzy_score
                    result['MatchType'] = 'Fuzzy'
            
            if best_match is not None:
                result['BankDate'] = best_match.get('BankDate', None)
                result['BankReference'] = best_match.get('BankReference', '')
                result['MatchScore'] = best_score
                result['StatusFlag'] = '✅'
                result['ReasonText'] = f'مطابقة بنسبة {best_score}%'
            else:
                result['StatusFlag'] = '⚠️'
                result['ReasonText'] = 'لم يتم العثور على مطابقة في كشف البنك'
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def detect_internal_duplicates(self) -> pd.DataFrame:
        """
        كشف الصرف المكرر داخل ملفات الجوائز
        
        Returns:
            DataFrame بالتكرارات المكتشفة
        """
        if self.merged_results is None:
            raise ValueError("يجب إجراء المطابقة مع البنك أولاً")
        
        df = self.merged_results.copy()
        
        # تجميع حسب: الاسم، السباق، المبلغ
        grouped = df.groupby(['OwnerName', 'Race', 'AwardAmount'])
        
        for name, group in grouped:
            if len(group) > 1:
                # تحقق من التواريخ
                dates = group['EntryDate'].dropna().unique()
                
                if len(dates) > 1:
                    # تكرار مشتبه - نفس البيانات بتواريخ مختلفة
                    indices = group.index
                    df.loc[indices, 'StatusFlag'] = '⚠️'
                    df.loc[indices, 'ReasonText'] = df.loc[indices, 'ReasonText'] + ' | صرف مكرر مشتبه'
        
        # تحقق من تكرار المرجع البنكي
        if 'BankReference' in df.columns:
            bank_refs = df['BankReference'].dropna()
            duplicate_refs = bank_refs[bank_refs.duplicated(keep=False)]
            
            if len(duplicate_refs) > 0:
                for ref in duplicate_refs.unique():
                    indices = df[df['BankReference'] == ref].index
                    df.loc[indices, 'StatusFlag'] = '❌'
                    df.loc[indices, 'ReasonText'] = df.loc[indices, 'ReasonText'] + ' | صرف مكرر مؤكد (مرجع بنكي مكرر)'
        
        self.merged_results = df
        return df
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """
        حساب الإحصائيات الشاملة
        
        Returns:
            قاموس بالإحصائيات
        """
        if self.merged_results is None:
            return {}
        
        df = self.merged_results
        
        total_records = len(df)
        matched_ok = len(df[df['StatusFlag'] == '✅'])
        suspected = len(df[df['StatusFlag'] == '⚠️'])
        confirmed_duplicate = len(df[df['StatusFlag'] == '❌'])
        
        # إحصائيات حسب الموسم
        seasons_stats = {}
        if 'Season' in df.columns:
            seasons_stats = df.groupby('Season').size().to_dict()
        
        # إحصائيات حسب السباق
        races_stats = {}
        if 'Race' in df.columns:
            races_stats = df.groupby('Race').size().to_dict()
        
        self.statistics = {
            'total_records': total_records,
            'matched_ok': matched_ok,
            'suspected': suspected,
            'confirmed_duplicate': confirmed_duplicate,
            'match_rate': (matched_ok / total_records * 100) if total_records > 0 else 0,
            'seasons': seasons_stats,
            'races': races_stats,
            'total_amount': df['AwardAmount'].sum() if 'AwardAmount' in df.columns else 0
        }
        
        return self.statistics
    
    def export_report(self, output_path: str = None) -> str:
        """
        تصدير التقرير النهائي إلى Excel (الإصدار المتقدم v2.0)
        
        الميزات الجديدة:
        - Sheet 1: النتائج الكاملة
        - Sheet 2: جدول Pivot تفاعلي
        - Sheet 3: الإحصائيات الشاملة
        - Sheet 4: Audit Log (سجل التشغيل)
        
        Args:
            output_path: مسار الحفظ
            
        Returns:
            مسار الملف المحفوظ
        """
        if self.merged_results is None:
            raise ValueError("لا توجد نتائج للتصدير")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'outputs/camel_awards_report_{timestamp}.xlsx'
        
        # إنشاء المجلد إذا لم يكن موجوداً
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📊 تصدير التقرير المتقدم...")
        
        try:
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # تنسيقات الألوان
                green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
                yellow_format = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
                red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4472C4',
                    'font_color': 'white',
                    'align': 'center'
                })
                
                # Sheet 1: جميع النتائج
                self.merged_results.to_excel(writer, sheet_name='النتائج الكاملة', index=False)
                worksheet = writer.sheets['النتائج الكاملة']
                
                # تطبيق التنسيق الشرطي
                if 'StatusFlag' in self.merged_results.columns:
                    status_col = self.merged_results.columns.get_loc('StatusFlag')
                    for row_num, status in enumerate(self.merged_results['StatusFlag'], start=1):
                        if status == '✅':
                            worksheet.write(row_num, status_col, status, green_format)
                        elif status == '⚠️':
                            worksheet.write(row_num, status_col, status, yellow_format)
                        elif status == '❌':
                            worksheet.write(row_num, status_col, status, red_format)
                
                print(f"   ✅ Sheet 1: النتائج الكاملة ({len(self.merged_results):,} سجل)")
                
                # Sheet 2: ملخص Pivot
                if 'Season' in self.merged_results.columns and 'Race' in self.merged_results.columns:
                    try:
                        pivot = pd.pivot_table(
                            self.merged_results,
                            values='AwardAmount',
                            index=['Season', 'Race'],
                            columns='StatusFlag',
                            aggfunc='count',
                            fill_value=0
                        )
                        pivot.to_excel(writer, sheet_name='ملخص Pivot')
                        print(f"   ✅ Sheet 2: جدول Pivot")
                    except Exception as e:
                        print(f"   ⚠️ تحذير: لم يتم إنشاء Pivot - {str(e)}")
                
                # Sheet 3: الإحصائيات
                if self.statistics:
                    # تحويل الإحصائيات إلى DataFrame أكثر وضوحاً
                    stats_rows = []
                    for key, value in self.statistics.items():
                        if not isinstance(value, dict):
                            stats_rows.append({
                                'المؤشر': key,
                                'القيمة': value
                            })
                    
                    stats_df = pd.DataFrame(stats_rows)
                    stats_df.to_excel(writer, sheet_name='الإحصائيات', index=False)
                    
                    # تنسيق رأس الجدول
                    worksheet_stats = writer.sheets['الإحصائيات']
                    for col_num, value in enumerate(stats_df.columns.values):
                        worksheet_stats.write(0, col_num, value, header_format)
                    
                    print(f"   ✅ Sheet 3: الإحصائيات ({len(stats_rows)} مؤشر)")
                
                # Sheet 4: Audit Log (إذا كان متاحاً)
                if self.use_advanced_features and self.logger and AUDIT_LOGGER_AVAILABLE and self.current_run_id:
                    try:
                        # الحصول على تفاصيل التشغيل
                        run_details = self.logger.get_run_details(self.current_run_id)
                        run_info = run_details.get('run_info', {})
                        
                        if run_info:
                            audit_rows = [
                                {'المعلومة': 'RunID', 'القيمة': self.current_run_id},
                                {'المعلومة': 'تاريخ التشغيل', 'القيمة': run_info.get('Timestamp', 'N/A')},
                                {'المعلومة': 'إجمالي الجوائز', 'القيمة': run_info.get('TotalAwards', 0)},
                                {'المعلومة': 'مطابقات Exact', 'القيمة': run_info.get('ExactMatches', 0)},
                                {'المعلومة': 'مطابقات Fuzzy', 'القيمة': run_info.get('FuzzyMatches', 0)},
                                {'المعلومة': 'مطابقات RL', 'القيمة': run_info.get('RLMatches', 0)},
                                {'المعلومة': 'غير مطابق', 'القيمة': run_info.get('UnmatchedAwards', 0)},
                                {'المعلومة': 'وقت التنفيذ (ث)', 'القيمة': f"{run_info.get('ExecutionTimeSeconds', 0):.2f}"},
                                {'المعلومة': 'المستخدم', 'القيمة': run_info.get('UserName', 'System')},
                                {'المعلومة': 'الحالة', 'القيمة': run_info.get('Status', 'N/A')}
                            ]
                            
                            audit_df = pd.DataFrame(audit_rows)
                            audit_df.to_excel(writer, sheet_name='Audit Log', index=False)
                            
                            # تنسيق رأس الجدول
                            worksheet_audit = writer.sheets['Audit Log']
                            for col_num, value in enumerate(audit_df.columns.values):
                                worksheet_audit.write(0, col_num, value, header_format)
                            
                            print(f"   ✅ Sheet 4: Audit Log (RunID: {self.current_run_id[:8]}...)")
                    
                    except Exception as e:
                        print(f"   ⚠️ تحذير: لم يتم إضافة Audit Log - {str(e)}")
            
            print(f"\n✅ تم حفظ التقرير: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ خطأ في التصدير: {str(e)}")
            raise
    
    def filter_results(
        self, 
        season: Optional[str] = None,
        race: Optional[str] = None,
        status: Optional[str] = None,
        participant: Optional[str] = None
    ) -> pd.DataFrame:
        """
        فلترة النتائج
        
        Args:
            season: الموسم
            race: السباق
            status: الحالة
            participant: المشارك
            
        Returns:
            DataFrame مفلتر
        """
        if self.merged_results is None:
            return pd.DataFrame()
        
        df = self.merged_results.copy()
        
        if season and 'Season' in df.columns:
            df = df[df['Season'] == season]
        
        if race and 'Race' in df.columns:
            df = df[df['Race'] == race]
        
        if status and 'StatusFlag' in df.columns:
            df = df[df['StatusFlag'] == status]
        
        if participant and 'OwnerName' in df.columns:
            df = df[df['OwnerName'].str.contains(participant, case=False, na=False)]
        
        return df
