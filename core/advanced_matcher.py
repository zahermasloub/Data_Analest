# -*- coding: utf-8 -*-
"""
🔗 محرك المطابقة المتقدم - Advanced Matching Engine
======================================================
مطابقة متعددة الطبقات: Exact → Fuzzy → Record Linkage

Libraries Used:
- pandas>=2.1.0
- rapidfuzz>=3.5.0
- recordlinkage>=0.16.0
- numpy>=1.24.0

Install if missing:
pip install pandas rapidfuzz recordlinkage numpy
"""

import pandas as pd
import numpy as np
from rapidfuzz import fuzz
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import recordlinkage as rl
from recordlinkage.compare import Compare

class AdvancedMatcher:
    """محرك المطابقة المتقدم"""
    
    def __init__(self, fuzzy_threshold: int = 90):
        """
        تهيئة محرك المطابقة
        
        Args:
            fuzzy_threshold: عتبة التطابق الضبابي (0-100)
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.match_results = None
    
    def exact_match(
        self,
        awards_df: pd.DataFrame,
        bank_df: pd.DataFrame,
        time_window_days: int = 7
    ) -> pd.DataFrame:
        """
        المطابقة الحتمية (Exact Matching)
        
        Library Used: pandas
        
        القواعد:
        - AwardAmount == TransferAmount
        - الفرق بين التواريخ ≤ time_window_days
        - (اختياري) BankReference موجود
        
        Args:
            awards_df: بيانات الجوائز
            bank_df: بيانات البنك
            time_window_days: نافذة التطابق الزمني
            
        Returns:
            DataFrame بالمطابقات الحتمية
        """
        matches = []
        
        for _, award in awards_df.iterrows():
            award_amount = award.get('AwardAmount', 0)
            entry_date = award.get('EntryDate')
            
            if pd.isna(award_amount) or pd.isna(entry_date):
                continue
            
            # البحث في كشف البنك
            for _, bank in bank_df.iterrows():
                bank_amount = bank.get('TransferAmount', bank.get('BankAmount', 0))
                transfer_date = bank.get('TransferDate', bank.get('BankDate'))
                
                if pd.isna(bank_amount) or pd.isna(transfer_date):
                    continue
                
                # شرط المبلغ
                if abs(award_amount - bank_amount) > 0.01:
                    continue
                
                # شرط التاريخ
                try:
                    date_diff = abs((entry_date - transfer_date).days)
                    if date_diff > time_window_days:
                        continue
                except:
                    continue
                
                # مطابقة ناجحة
                match = {
                    **award.to_dict(),
                    'BankReference': bank.get('BankReference', ''),
                    'TransferAmount': bank_amount,
                    'TransferDate': transfer_date,
                    'BeneficiaryName': bank.get('BeneficiaryName', bank.get('BankName', '')),
                    'MatchType': 'Exact',
                    'MatchScore': 100,
                    'DateDiff': date_diff
                }
                matches.append(match)
                break  # أول مطابقة فقط
        
        return pd.DataFrame(matches)
    
    def fuzzy_match(
        self,
        unmatched_awards: pd.DataFrame,
        bank_df: pd.DataFrame,
        time_window_days: int = 7
    ) -> pd.DataFrame:
        """
        المطابقة الضبابية (Fuzzy Matching)
        
        Library Used: rapidfuzz, pandas
        
        القواعد:
        - AwardAmount == TransferAmount
        - similarity(OwnerName, BankName) >= threshold
        - الفرق بين التواريخ ≤ time_window_days
        
        Args:
            unmatched_awards: الجوائز غير المطابقة
            bank_df: بيانات البنك
            time_window_days: نافذة التطابق الزمني
            
        Returns:
            DataFrame بالمطابقات الضبابية
        """
        matches = []
        
        for _, award in unmatched_awards.iterrows():
            award_amount = award.get('AwardAmount', 0)
            entry_date = award.get('EntryDate')
            owner_name = str(award.get('OwnerName_norm', '')).lower()
            
            if pd.isna(award_amount) or pd.isna(entry_date) or not owner_name:
                continue
            
            best_match = None
            best_score = 0
            
            # البحث في كشف البنك
            for _, bank in bank_df.iterrows():
                bank_amount = bank.get('TransferAmount', bank.get('BankAmount', 0))
                transfer_date = bank.get('TransferDate', bank.get('BankDate'))
                bank_name = str(bank.get('BankName_norm', '')).lower()
                
                if pd.isna(bank_amount) or pd.isna(transfer_date) or not bank_name:
                    continue
                
                # شرط المبلغ
                if abs(award_amount - bank_amount) > 0.01:
                    continue
                
                # شرط التاريخ
                try:
                    date_diff = abs((entry_date - transfer_date).days)
                    if date_diff > time_window_days:
                        continue
                except:
                    continue
                
                # حساب التشابه
                similarity = fuzz.ratio(owner_name, bank_name)
                
                if similarity >= self.fuzzy_threshold and similarity > best_score:
                    best_score = similarity
                    best_match = {
                        **award.to_dict(),
                        'BankReference': bank.get('BankReference', ''),
                        'TransferAmount': bank_amount,
                        'TransferDate': transfer_date,
                        'BeneficiaryName': bank.get('BeneficiaryName', bank.get('BankName', '')),
                        'MatchType': 'Fuzzy',
                        'MatchScore': similarity,
                        'DateDiff': date_diff
                    }
            
            if best_match:
                matches.append(best_match)
        
        return pd.DataFrame(matches)
    
    def record_linkage_match(
        self,
        unmatched_awards: pd.DataFrame,
        bank_df: pd.DataFrame,
        time_window_days: int = 7,
        score_threshold: float = 0.75
    ) -> pd.DataFrame:
        """
        مطابقة Record Linkage (للحالات المعقدة)
        
        Library Used: recordlinkage, pandas
        
        استخدام خوارزميات متقدمة للمطابقة المركبة
        
        Args:
            unmatched_awards: الجوائز غير المطابقة
            bank_df: بيانات البنك
            time_window_days: نافذة التطابق الزمني
            score_threshold: عتبة النتيجة (0-1)
            
        Returns:
            DataFrame بالمطابقات المحتملة
        """
        if len(unmatched_awards) == 0 or len(bank_df) == 0:
            return pd.DataFrame()
        
        try:
            # تحضير البيانات
            awards_prep = unmatched_awards.copy()
            bank_prep = bank_df.copy()
            
            # إنشاء مؤشرات
            awards_prep['_idx'] = range(len(awards_prep))
            bank_prep['_idx'] = range(len(bank_prep))
            
            awards_prep.set_index('_idx', inplace=True)
            bank_prep.set_index('_idx', inplace=True)
            
            # إنشاء محرك المطابقة
            indexer = rl.Index()
            
            # استخدام Blocking للتسريع (حسب المبلغ)
            if 'AwardAmount' in awards_prep.columns:
                # تقريب المبالغ لإنشاء كتل
                awards_prep['_amount_block'] = (awards_prep['AwardAmount'] / 1000).astype(int)
                bank_prep['_amount_block'] = (bank_prep.get('TransferAmount', bank_prep.get('BankAmount', 0)) / 1000).astype(int)
                
                indexer.block(left_on='_amount_block', right_on='_amount_block')
            else:
                # Full comparison إذا لم يكن هناك عمود مبلغ
                indexer.full()
            
            candidate_pairs = indexer.index(awards_prep, bank_prep)
            
            # مقارنة الأزواج
            compare = Compare()
            
            # مقارنة الأسماء (String similarity)
            if 'OwnerName_norm' in awards_prep.columns and 'BankName_norm' in bank_prep.columns:
                compare.string(
                    'OwnerName_norm', 
                    'BankName_norm',
                    method='jarowinkler',
                    label='name_sim'
                )
            
            # مقارنة المبالغ (Exact)
            if 'AwardAmount' in awards_prep.columns:
                compare.exact('AwardAmount', '_amount_block', label='amount_match')
            
            # تنفيذ المقارنة
            features = compare.compute(candidate_pairs, awards_prep, bank_prep)
            
            # حساب النتيجة الإجمالية
            if not features.empty:
                # متوسط ميزات المطابقة
                features['total_score'] = features.mean(axis=1)
                
                # فلترة حسب العتبة
                potential_matches = features[features['total_score'] >= score_threshold]
                
                # تحويل للنتائج النهائية
                matches = []
                for (award_idx, bank_idx), row in potential_matches.iterrows():
                    award = awards_prep.loc[award_idx]
                    bank = bank_prep.loc[bank_idx]
                    
                    # التحقق من النافذة الزمنية
                    try:
                        entry_date = award.get('EntryDate')
                        transfer_date = bank.get('TransferDate', bank.get('BankDate'))
                        
                        if pd.notna(entry_date) and pd.notna(transfer_date):
                            date_diff = abs((entry_date - transfer_date).days)
                            if date_diff > time_window_days:
                                continue
                        else:
                            date_diff = None
                    except:
                        date_diff = None
                    
                    match = {
                        **award.to_dict(),
                        'BankReference': bank.get('BankReference', ''),
                        'TransferAmount': bank.get('TransferAmount', bank.get('BankAmount', 0)),
                        'TransferDate': transfer_date,
                        'BeneficiaryName': bank.get('BeneficiaryName', bank.get('BankName', '')),
                        'MatchType': 'RecordLinkage',
                        'MatchScore': int(row['total_score'] * 100),
                        'DateDiff': date_diff
                    }
                    matches.append(match)
                
                return pd.DataFrame(matches)
            
        except Exception as e:
            print(f"⚠️ خطأ في Record Linkage: {str(e)}")
        
        return pd.DataFrame()
    
    def match_all_layers(
        self,
        awards_df: pd.DataFrame,
        bank_df: pd.DataFrame,
        time_window_days: int = 7,
        use_record_linkage: bool = False
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        تطبيق جميع طبقات المطابقة
        
        Library Used: pandas, rapidfuzz, recordlinkage
        
        Args:
            awards_df: بيانات الجوائز
            bank_df: بيانات البنك
            time_window_days: نافذة التطابق الزمني
            use_record_linkage: استخدام Record Linkage
            
        Returns:
            (matched_df, unmatched_df)
        """
        print("🔍 المطابقة الطبقة 1: Exact Matching...")
        exact_matches = self.exact_match(awards_df, bank_df, time_window_days)
        
        # تحديد غير المطابقة
        if len(exact_matches) > 0:
            matched_indices = exact_matches.index
            unmatched = awards_df[~awards_df.index.isin(matched_indices)]
        else:
            unmatched = awards_df.copy()
        
        print(f"   ✅ مطابقات حتمية: {len(exact_matches)}")
        
        # الطبقة 2: Fuzzy
        print("🔍 المطابقة الطبقة 2: Fuzzy Matching...")
        fuzzy_matches = self.fuzzy_match(unmatched, bank_df, time_window_days)
        print(f"   ✅ مطابقات ضبابية: {len(fuzzy_matches)}")
        
        # تحديث غير المطابقة
        if len(fuzzy_matches) > 0:
            unmatched = unmatched[~unmatched.index.isin(fuzzy_matches.index)]
        
        # الطبقة 3: Record Linkage (اختياري)
        rl_matches = pd.DataFrame()
        if use_record_linkage and len(unmatched) > 0:
            print("🔍 المطابقة الطبقة 3: Record Linkage...")
            rl_matches = self.record_linkage_match(unmatched, bank_df, time_window_days)
            print(f"   ✅ مطابقات Record Linkage: {len(rl_matches)}")
            
            if len(rl_matches) > 0:
                unmatched = unmatched[~unmatched.index.isin(rl_matches.index)]
        
        # دمج جميع المطابقات
        all_matches = pd.concat([exact_matches, fuzzy_matches, rl_matches], ignore_index=True)
        
        print(f"\n📊 إجمالي المطابقات: {len(all_matches)}")
        print(f"📊 غير المطابقة: {len(unmatched)}")
        
        return all_matches, unmatched
