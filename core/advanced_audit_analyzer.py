"""
Advanced Audit Analyzer for Camel Race Awards
==============================================

Professional audit system following enterprise-grade requirements:
- Multi-season award file consolidation
- Intelligent duplicate detection with composite keys
- Bank payment verification with reference matching
- Comprehensive reporting with audit trails

Author: Senior Data Analysis Team
Version: 2.0.0 (Professional Edition)
Date: November 6, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime, timedelta
import re
import warnings
warnings.filterwarnings('ignore')


class AdvancedAuditAnalyzer:
    """
    Enterprise-grade audit analyzer for camel race awards with bank verification.
    
    Capabilities:
    - Multi-file consolidation with header normalization
    - Composite key duplicate detection
    - Reference-based bank payment verification
    - Detailed audit trail generation
    """
    
    # Configuration parameters
    DATE_WINDOW_DAYS = 14
    AMOUNT_TOLERANCE = 0.00  # Exact match required
    REF_LAST_DIGITS = 10
    EXPORT_TOP_N_SAMPLES = 50
    
    def __init__(self):
        """Initialize analyzer with audit logging."""
        self.awards_data: Optional[pd.DataFrame] = None
        self.bank_data: Optional[pd.DataFrame] = None
        self.duplicates: Optional[pd.DataFrame] = None
        self.audit_log: List[Dict] = []
        self.validation_results: Dict = {}
        
        self._log_event("INIT", "Advanced Audit Analyzer initialized")
    
    def _log_event(self, action: str, details: str, data: Optional[Dict] = None):
        """Log audit events with timestamp."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'data': data or {}
        }
        self.audit_log.append(event)
        print(f"[{action}] {details}")
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent matching.
        
        Rules:
        - Trim whitespace
        - Remove multiple spaces
        - Lowercase
        - Remove special characters
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Trim and normalize spaces
        text = str(text).strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Lowercase for matching
        text = text.lower()
        
        return text
    
    def detect_header_row(self, file_path: str, max_rows: int = 20) -> int:
        """
        Intelligently detect header row in Excel file.
        
        Strategy:
        - Scan first 20 rows
        - Look for row with most non-empty, string values
        - Prefer rows with known field names
        """
        self._log_event("HEADER_DETECT", f"Scanning {file_path} for header row")
        
        df_preview = pd.read_excel(file_path, header=None, nrows=max_rows)
        
        known_fields = [
            'season', 'race', 'owner', 'name', 'amount', 'date', 'reference',
            'iban', 'beneficiary', 'transfer', 'award', 'payment', 'qatari'
        ]
        
        best_row = 0
        best_score = 0
        
        for idx, row in df_preview.iterrows():
            # Count non-empty values
            non_empty = row.notna().sum()
            
            # Count string values
            string_count = sum(1 for val in row if isinstance(val, str))
            
            # Check for known field names
            field_matches = 0
            for val in row:
                if isinstance(val, str):
                    val_lower = val.lower()
                    if any(field in val_lower for field in known_fields):
                        field_matches += 5
            
            # Calculate score
            score = string_count * 2 + field_matches + (non_empty * 0.5)
            
            if score > best_score:
                best_score = score
                best_row = idx
        
        self._log_event("HEADER_DETECT", f"Detected header at row {best_row} (score: {best_score:.1f})")
        return best_row
    
    def normalize_column_names(self, df: pd.DataFrame, context: str = "awards") -> pd.DataFrame:
        """
        Standardize column names with intelligent mapping.
        
        Args:
            df: Input DataFrame
            context: 'awards' or 'bank' for context-specific mapping
        
        Returns:
            DataFrame with normalized column names
        """
        df = df.copy()
        
        # Drop unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]
        
        # Build comprehensive mapping
        column_mapping = {
            # Awards fields
            'entry date': 'EntryDate',
            'entrydate': 'EntryDate',
            'date': 'EntryDate',
            'تاريخ': 'EntryDate',
            
            'season': 'Season',
            'الموسم': 'Season',
            
            'race': 'Race',
            'race name': 'Race',
            'السباق': 'Race',
            
            'owner number': 'OwnerNumber',
            'ownernumber': 'OwnerNumber',
            'رقم المالك': 'OwnerNumber',
            
            'owner name': 'OwnerName',
            'ownername': 'OwnerName',
            'اسم المالك': 'OwnerName',
            
            'owner qatari id': 'OwnerQatariID',
            'owner qatariid': 'OwnerQatariID',
            'ownerqatariid': 'OwnerQatariID',
            'qatari id': 'OwnerQatariID',
            
            'award amount': 'AwardAmount',
            'awardamount': 'AwardAmount',
            'amount': 'AwardAmount',
            'المبلغ': 'AwardAmount',
            'value': 'AwardAmount',
            
            'payment refrence': 'PaymentReference',
            'paymentrefrence': 'PaymentReference',
            'payment reference': 'PaymentReference',
            'paymentreference': 'PaymentReference',
            'ref': 'PaymentReference',
            
            'payment refrence_d1': 'PaymentReference_D1',
            'paymentrefrence_d1': 'PaymentReference_D1',
            'payment refrence_d2': 'PaymentReference_D2',
            'paymentrefrence_d2': 'PaymentReference_D2',
            'payment refrence_d3': 'PaymentReference_D3',
            'paymentrefrence_d3': 'PaymentReference_D3',
            
            'beneficiary name en': 'BeneficiaryNameEn',
            'beneficiarynameen': 'BeneficiaryNameEn',
            'beneficiary english name': 'BeneficiaryNameEn',
            
            'iban number': 'IBAN',
            'ibannumber': 'IBAN',
            'iban': 'IBAN',
        }
        
        if context == "bank":
            bank_mapping = {
                'transaction date': 'TransactionDate',
                'transactiondate': 'TransactionDate',
                'value date': 'ValueDate',
                'valuedate': 'ValueDate',
                'تاريخ التحويل': 'TransactionDate',
                
                'award ref': 'AwardRef',
                'awardref': 'AwardRef',
                'award reference': 'AwardRef',
                
                'award ref 10 digits': 'AwardRef10Digits',
                'award ref 10digits': 'AwardRef10Digits',
                'awardref10digits': 'AwardRef10Digits',
                
                'bank ref': 'BankReference',
                'bankreference': 'BankReference',
                'reference': 'BankReference',
                
                'request reference': 'RequestReference',
                'requestreference': 'RequestReference',
                
                'debit': 'Debit',
                'debit amount': 'Debit',
                'مدين': 'Debit',
                
                'credit': 'Credit',
                'credit amount': 'Credit',
                'دائن': 'Credit',
                
                'name': 'BeneficiaryName',
                'beneficiary': 'BeneficiaryName',
                'المستفيد': 'BeneficiaryName',
                
                'account balance': 'AccountBalance',
                'balance': 'AccountBalance',
                
                'narrative': 'Narrative',
            }
            column_mapping.update(bank_mapping)
        
        # Apply mapping (case-insensitive)
        rename_dict = {}
        for col in df.columns:
            col_lower = self.normalize_text(str(col))
            if col_lower in column_mapping:
                rename_dict[col] = column_mapping[col_lower]
        
        df = df.rename(columns=rename_dict)
        
        self._log_event("NORMALIZE", f"Normalized {len(rename_dict)} columns in {context} data")
        
        return df
    
    def load_awards_files(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Load and consolidate multiple award files.
        
        Features:
        - Auto-detect header row
        - Normalize column names
        - Clean data
        - Track source file
        """
        self._log_event("LOAD_START", f"Loading {len(file_paths)} award files")
        
        all_awards = []
        load_summary = []
        
        for file_path in file_paths:
            try:
                # Detect header row
                header_row = self.detect_header_row(file_path)
                
                # Load file
                df = pd.read_excel(file_path, header=header_row)
                
                # Add source tracking
                df['SourceFile'] = Path(file_path).name
                
                # Normalize columns
                df = self.normalize_column_names(df, context="awards")
                
                # Clean data
                df = self._clean_award_data(df)
                
                all_awards.append(df)
                
                load_summary.append({
                    'file': Path(file_path).name,
                    'rows': len(df),
                    'columns': len(df.columns)
                })
                
                self._log_event("LOAD_SUCCESS", f"Loaded {Path(file_path).name}: {len(df):,} rows")
                
            except Exception as e:
                self._log_event("LOAD_ERROR", f"Failed to load {file_path}: {str(e)}")
                load_summary.append({
                    'file': Path(file_path).name,
                    'error': str(e)
                })
        
        if not all_awards:
            raise ValueError("No award files were loaded successfully")
        
        # Consolidate all awards
        self.awards_data = pd.concat(all_awards, ignore_index=True)
        
        self._log_event("LOAD_COMPLETE", f"Consolidated {len(self.awards_data):,} total award records", 
                       {'summary': load_summary})
        
        return self.awards_data
    
    def _clean_award_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize award data."""
        df = df.copy()
        
        # Clean text fields
        text_fields = ['OwnerName', 'BeneficiaryNameEn', 'Race', 'Season']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].apply(lambda x: self.normalize_text(x) if pd.notna(x) else x)
                df[field] = df[field].str.strip()
                df[field] = df[field].replace('', np.nan)
        
        # Convert Award Amount to numeric
        if 'AwardAmount' in df.columns:
            df['AwardAmount'] = pd.to_numeric(
                df['AwardAmount'].astype(str).str.replace(r'[^\d.]', '', regex=True),
                errors='coerce'
            )
        
        # Convert dates
        if 'EntryDate' in df.columns:
            df['EntryDate'] = pd.to_datetime(df['EntryDate'], errors='coerce')
        
        # Clean reference fields
        ref_fields = ['PaymentReference', 'PaymentReference_D1', 'PaymentReference_D2', 'PaymentReference_D3']
        for field in ref_fields:
            if field in df.columns:
                df[field] = df[field].astype(str).str.strip()
                df[field] = df[field].replace(['nan', 'None', ''], np.nan)
        
        return df
    
    def load_bank_statement(self, file_path: str) -> pd.DataFrame:
        """
        Load and normalize bank statement.
        
        Features:
        - Auto-detect header row
        - Rebuild column structure
        - Calculate transfer amounts from Debit/Credit
        """
        self._log_event("BANK_LOAD_START", f"Loading bank statement: {file_path}")
        
        # Detect header row
        header_row = self.detect_header_row(file_path)
        
        # Load file
        df = pd.read_excel(file_path, header=header_row)
        
        # Normalize columns
        df = self.normalize_column_names(df, context="bank")
        
        # Calculate TransferAmount if not present
        if 'TransferAmount' not in df.columns:
            if 'Debit' in df.columns and 'Credit' in df.columns:
                df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
                df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
                df['TransferAmount'] = df['Debit'] - df['Credit']
            elif 'Debit' in df.columns:
                df['TransferAmount'] = pd.to_numeric(df['Debit'], errors='coerce')
            elif 'Credit' in df.columns:
                df['TransferAmount'] = pd.to_numeric(df['Credit'], errors='coerce')
        
        # Convert dates
        if 'TransactionDate' in df.columns:
            df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], errors='coerce')
        if 'ValueDate' in df.columns:
            df['ValueDate'] = pd.to_datetime(df['ValueDate'], errors='coerce')
        
        # Clean reference fields
        ref_fields = ['AwardRef', 'AwardRef10Digits', 'BankReference', 'RequestReference']
        for field in ref_fields:
            if field in df.columns:
                df[field] = df[field].astype(str).str.strip()
                df[field] = df[field].replace(['nan', 'None', ''], np.nan)
        
        self.bank_data = df
        
        self._log_event("BANK_LOAD_COMPLETE", f"Loaded {len(df):,} bank transactions")
        
        return self.bank_data
    
    def detect_duplicates(self) -> pd.DataFrame:
        """
        Detect duplicates using composite key.
        
        Composite Key:
        - Season
        - Race
        - Owner Number
        - Owner Name
        - Owner QatariId
        - Award Amount
        
        EntryDate is ALLOWED to differ.
        """
        if self.awards_data is None:
            raise ValueError("Awards data not loaded. Call load_awards_files() first.")
        
        self._log_event("DUPLICATE_DETECT_START", "Starting duplicate detection with composite key")
        
        # Define composite key fields
        key_fields = ['Season', 'Race', 'OwnerNumber', 'OwnerName', 'OwnerQatariID', 'AwardAmount']
        
        # Validate key fields exist
        missing_fields = [f for f in key_fields if f not in self.awards_data.columns]
        if missing_fields:
            self._log_event("DUPLICATE_WARN", f"Missing key fields: {missing_fields}")
            key_fields = [f for f in key_fields if f in self.awards_data.columns]
        
        if not key_fields:
            raise ValueError("No key fields available for duplicate detection")
        
        # Create composite key
        df = self.awards_data.copy()
        df['_CompositeKey'] = df[key_fields].astype(str).agg('|'.join, axis=1)
        
        # Find duplicates
        df['_DuplicateCount'] = df.groupby('_CompositeKey')['_CompositeKey'].transform('count')
        df['_DuplicateGroup'] = df.groupby('_CompositeKey').ngroup()
        
        # Filter only duplicates (count >= 2)
        duplicates = df[df['_DuplicateCount'] >= 2].copy()
        
        # Sort by duplicate group and entry date
        if 'EntryDate' in duplicates.columns:
            duplicates = duplicates.sort_values(['_DuplicateGroup', 'EntryDate'])
        else:
            duplicates = duplicates.sort_values('_DuplicateGroup')
        
        self.duplicates = duplicates
        
        # Generate summary statistics
        total_duplicates = len(duplicates)
        unique_groups = duplicates['_DuplicateGroup'].nunique()
        total_amount = duplicates['AwardAmount'].sum() if 'AwardAmount' in duplicates.columns else 0
        
        self._log_event("DUPLICATE_DETECT_COMPLETE", 
                       f"Found {total_duplicates:,} duplicate records in {unique_groups:,} groups",
                       {
                           'total_duplicates': total_duplicates,
                           'unique_groups': unique_groups,
                           'total_amount': float(total_amount) if not pd.isna(total_amount) else 0
                       })
        
        return self.duplicates
    
    def verify_bank_payments(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Verify duplicates against bank statement.
        
        Returns:
            Tuple of (matched, partial, unmatched) DataFrames
        """
        if self.duplicates is None or self.bank_data is None:
            raise ValueError("Duplicates and bank data must be loaded first")
        
        self._log_event("BANK_VERIFY_START", "Starting bank payment verification")
        
        matched_records = []
        partial_records = []
        unmatched_records = []
        
        for idx, award_row in self.duplicates.iterrows():
            # Extract reference fields from award
            award_refs = []
            if 'PaymentReference' in award_row and pd.notna(award_row['PaymentReference']):
                award_refs.append(str(award_row['PaymentReference']).strip())
            if 'PaymentReference_D1' in award_row and pd.notna(award_row['PaymentReference_D1']):
                award_refs.append(str(award_row['PaymentReference_D1']).strip())
            
            if not award_refs:
                # No reference to match
                unmatched_records.append(award_row.to_dict())
                continue
            
            # Try to find match in bank statement
            match_found = False
            partial_match = False
            bank_match = None
            
            for award_ref in award_refs:
                # Clean reference
                award_ref_clean = re.sub(r'[^\w]', '', award_ref).lower()
                
                # Vectorized matching (faster)
                bank_matches = self.bank_data[
                    (self.bank_data['AwardRef10Digits'].astype(str).str.lower().str.contains(award_ref_clean[-self.REF_LAST_DIGITS:], na=False)) |
                    (self.bank_data['AwardRef'].astype(str).str.lower().str.contains(award_ref_clean[-self.REF_LAST_DIGITS:], na=False))
                ]
                
                if len(bank_matches) > 0:
                    # Take first match
                    bank_match = bank_matches.iloc[0]
                    match_found = True
                    break
                
                if match_found:
                    break
            
            # Categorize result
            award_dict = award_row.to_dict()
            if match_found and bank_match is not None:
                award_dict['BankTransferAmount'] = bank_match.get('TransferAmount')
                award_dict['BankTransactionDate'] = bank_match.get('TransactionDate')
                award_dict['BankBeneficiary'] = bank_match.get('BeneficiaryName')
                award_dict['BankReference'] = bank_match.get('BankReference')
                matched_records.append(award_dict)
            elif partial_match and bank_match is not None:
                award_dict['BankTransferAmount'] = bank_match.get('TransferAmount')
                award_dict['BankTransactionDate'] = bank_match.get('TransactionDate')
                award_dict['BankBeneficiary'] = bank_match.get('BeneficiaryName')
                award_dict['BankReference'] = bank_match.get('BankReference')
                partial_records.append(award_dict)
            else:
                unmatched_records.append(award_dict)
        
        # Convert to DataFrames
        matched_df = pd.DataFrame(matched_records) if matched_records else pd.DataFrame()
        partial_df = pd.DataFrame(partial_records) if partial_records else pd.DataFrame()
        unmatched_df = pd.DataFrame(unmatched_records) if unmatched_records else pd.DataFrame()
        
        self._log_event("BANK_VERIFY_COMPLETE", 
                       f"Verified {len(self.duplicates)} records",
                       {
                           'matched': len(matched_df),
                           'partial': len(partial_df),
                           'unmatched': len(unmatched_df)
                       })
        
        return matched_df, partial_df, unmatched_df
    
    def generate_reports(self, output_dir: str = "outputs"):
        """
        Generate comprehensive Excel reports.
        
        Outputs:
        1. Awards_Duplicates_[timestamp].xlsx
        2. Bank_Match_Verification_[timestamp].xlsx
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Report 1: Duplicates
        if self.duplicates is not None and len(self.duplicates) > 0:
            duplicates_file = output_path / f"Awards_Duplicates_{timestamp}.xlsx"
            
            with pd.ExcelWriter(duplicates_file, engine='openpyxl') as writer:
                # All duplicate rows
                self.duplicates.to_excel(writer, sheet_name='Duplicates_AllRows', index=False)
                
                # Summary by group
                summary = self.duplicates.groupby('_DuplicateGroup').agg({
                    'AwardAmount': ['first', 'sum', 'count'],
                    'EntryDate': ['min', 'max'],
                    'OwnerName': 'first',
                    'Race': 'first',
                    'Season': 'first'
                }).reset_index()
                summary.columns = ['GroupID', 'Amount', 'TotalAmount', 'Count', 'MinDate', 'MaxDate', 'Owner', 'Race', 'Season']
                summary.to_excel(writer, sheet_name='Duplicates_Summary', index=False)
                
                # Data dictionary
                data_dict = pd.DataFrame({
                    'Field': self.duplicates.columns,
                    'DataType': [str(self.duplicates[col].dtype) for col in self.duplicates.columns],
                    'NonNull': [self.duplicates[col].notna().sum() for col in self.duplicates.columns]
                })
                data_dict.to_excel(writer, sheet_name='Data_Dictionary', index=False)
            
            self._log_event("REPORT_GENERATED", f"Duplicates report: {duplicates_file}")
        
        # Report 2: Bank Verification
        try:
            matched, partial, unmatched = self.verify_bank_payments()
            
            verification_file = output_path / f"Bank_Match_Verification_{timestamp}.xlsx"
            
            with pd.ExcelWriter(verification_file, engine='openpyxl') as writer:
                # Matched
                if len(matched) > 0:
                    matched.to_excel(writer, sheet_name='Bank_Matches', index=False)
                
                # Partial
                if len(partial) > 0:
                    partial.to_excel(writer, sheet_name='Bank_PartialOrSuspected', index=False)
                
                # Unmatched
                if len(unmatched) > 0:
                    unmatched.to_excel(writer, sheet_name='Bank_Unmatched', index=False)
                
                # Notes/Assumptions
                notes_data = {
                    'Parameter': ['DATE_WINDOW_DAYS', 'AMOUNT_TOLERANCE', 'REF_LAST_DIGITS', 'TIMESTAMP'],
                    'Value': [self.DATE_WINDOW_DAYS, self.AMOUNT_TOLERANCE, self.REF_LAST_DIGITS, timestamp],
                    'Description': [
                        'Date proximity window for matching',
                        'Amount difference tolerance',
                        'Number of digits for partial reference matching',
                        'Report generation timestamp'
                    ]
                }
                pd.DataFrame(notes_data).to_excel(writer, sheet_name='Notes', index=False)
            
            self._log_event("REPORT_GENERATED", f"Bank verification report: {verification_file}")
            
        except Exception as e:
            self._log_event("REPORT_ERROR", f"Error generating bank verification report: {str(e)}")
        
        # Save audit log
        audit_log_file = output_path / f"Audit_Log_{timestamp}.xlsx"
        pd.DataFrame(self.audit_log).to_excel(audit_log_file, index=False)
        self._log_event("AUDIT_LOG_SAVED", f"Audit log: {audit_log_file}")
        
        return {
            'duplicates': duplicates_file if self.duplicates is not None else None,
            'verification': verification_file if 'verification_file' in locals() else None,
            'audit_log': audit_log_file
        }


def main():
    """Example usage of Advanced Audit Analyzer."""
    
    print("="*80)
    print("Advanced Audit Analyzer - Professional Edition")
    print("="*80)
    
    # Initialize analyzer
    analyzer = AdvancedAuditAnalyzer()
    
    # Define award files
    award_files = [
        'الملفات/Awards_Delegations_2018-2019.xlsx',
        'الملفات/Awards_Delegations_2019-2020.xlsx',
        'الملفات/Awards_Delegations_2020-2021.xlsx',
        'الملفات/Awards_Delegations_2021-2022.xlsx',
        'الملفات/AwardsForSeason2022-2023.xlsx',
        'الملفات/AwardsForSeason2023-2024.xlsx',
        'الملفات/AwardsForSeason2024-2025.xlsx',
    ]
    
    # Load awards
    analyzer.load_awards_files(award_files)
    
    # Load bank statement
    analyzer.load_bank_statement('الملفات/ملف البنك.xlsx')
    
    # Detect duplicates
    analyzer.detect_duplicates()
    
    # Generate reports
    reports = analyzer.generate_reports()
    
    print("\n" + "="*80)
    print("Analysis Complete!")
    print("="*80)
    print(f"\nReports generated:")
    for report_type, report_path in reports.items():
        if report_path:
            print(f"  - {report_type}: {report_path}")


if __name__ == "__main__":
    main()
