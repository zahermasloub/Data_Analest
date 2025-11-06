"""
Professional Audit Test Suite
==============================

Testing the Advanced Audit Analyzer with real-world data
following enterprise-grade requirements.
"""

from core.advanced_audit_analyzer import AdvancedAuditAnalyzer
from pathlib import Path
import time


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def run_professional_audit():
    """Execute complete professional audit workflow."""
    
    print_section("🎯 ADVANCED AUDIT ANALYZER - PROFESSIONAL EDITION")
    print("Following enterprise-grade requirements with:")
    print("  ✓ Multi-season consolidation")
    print("  ✓ Composite key duplicate detection")
    print("  ✓ Bank payment verification")
    print("  ✓ Comprehensive audit trail")
    
    # Initialize
    start_time = time.time()
    analyzer = AdvancedAuditAnalyzer()
    
    # Step 1: Load Award Files
    print_section("📂 STEP 1: Loading Award Files")
    
    award_files = [
        'الملفات/Awards_Delegations_2018-2019.xlsx',
        'الملفات/Awards_Delegations_2019-2020.xlsx',
        'الملفات/Awards_Delegations_2020-2021.xlsx',
        'الملفات/Awards_Delegations_2021-2022.xlsx',
        'الملفات/AwardsForSeason2022-2023.xlsx',
        'الملفات/AwardsForSeason2023-2024.xlsx',
        'الملفات/AwardsForSeason2024-2025.xlsx',
    ]
    
    # Check which files exist
    existing_files = []
    for file in award_files:
        if Path(file).exists():
            existing_files.append(file)
        else:
            print(f"⚠️  File not found: {file}")
    
    if not existing_files:
        print("❌ No award files found!")
        return
    
    print(f"\n📋 Loading {len(existing_files)} award files...")
    
    try:
        awards_df = analyzer.load_awards_files(existing_files)
        
        print(f"\n✅ Successfully loaded and consolidated:")
        print(f"   Total Records: {len(awards_df):,}")
        print(f"   Columns: {len(awards_df.columns)}")
        print(f"   Date Range: {awards_df['EntryDate'].min()} to {awards_df['EntryDate'].max()}" 
              if 'EntryDate' in awards_df.columns else "")
        
        # Show key fields status
        key_fields = ['Season', 'Race', 'OwnerNumber', 'OwnerName', 'OwnerQatariID', 'AwardAmount']
        print(f"\n📊 Key Fields Status:")
        for field in key_fields:
            if field in awards_df.columns:
                non_null = awards_df[field].notna().sum()
                percent = (non_null / len(awards_df)) * 100
                print(f"   {field:20s}: {non_null:6,} / {len(awards_df):6,} ({percent:5.1f}%)")
            else:
                print(f"   {field:20s}: ❌ NOT FOUND")
        
    except Exception as e:
        print(f"❌ Error loading awards: {e}")
        return
    
    # Step 2: Load Bank Statement
    print_section("🏦 STEP 2: Loading Bank Statement")
    
    bank_file = 'الملفات/ملف البنك.xlsx'
    
    if not Path(bank_file).exists():
        print(f"⚠️  Bank file not found: {bank_file}")
        bank_loaded = False
    else:
        try:
            bank_df = analyzer.load_bank_statement(bank_file)
            bank_loaded = True
            
            print(f"\n✅ Successfully loaded bank statement:")
            print(f"   Total Transactions: {len(bank_df):,}")
            print(f"   Columns: {len(bank_df.columns)}")
            
            # Show reference fields
            ref_fields = ['AwardRef', 'AwardRef10Digits', 'BankReference']
            print(f"\n📊 Reference Fields Status:")
            for field in ref_fields:
                if field in bank_df.columns:
                    non_null = bank_df[field].notna().sum()
                    percent = (non_null / len(bank_df)) * 100
                    print(f"   {field:20s}: {non_null:6,} / {len(bank_df):6,} ({percent:5.1f}%)")
                else:
                    print(f"   {field:20s}: ❌ NOT FOUND")
            
        except Exception as e:
            print(f"❌ Error loading bank: {e}")
            bank_loaded = False
    
    # Step 3: Detect Duplicates
    print_section("🔍 STEP 3: Duplicate Detection (Composite Key)")
    
    print("\n🔑 Composite Key Fields:")
    print("   - Season")
    print("   - Race")
    print("   - Owner Number")
    print("   - Owner Name")
    print("   - Owner QatariID")
    print("   - Award Amount")
    print("\n⚠️  Note: Entry Date is ALLOWED to differ")
    
    try:
        duplicates_df = analyzer.detect_duplicates()
        
        if len(duplicates_df) == 0:
            print(f"\n✅ No duplicates found - All records are unique!")
        else:
            print(f"\n⚠️  Duplicates Found:")
            print(f"   Total Duplicate Records: {len(duplicates_df):,}")
            print(f"   Unique Duplicate Groups: {duplicates_df['_DuplicateGroup'].nunique():,}")
            
            if 'AwardAmount' in duplicates_df.columns:
                total_amount = duplicates_df['AwardAmount'].sum()
                print(f"   Total Duplicate Amount: {total_amount:,.2f} QAR")
            
            # Show top duplicate groups
            if '_DuplicateCount' in duplicates_df.columns:
                top_groups = duplicates_df.groupby('_DuplicateGroup').agg({
                    '_DuplicateCount': 'first',
                    'AwardAmount': 'first',
                    'OwnerName': 'first',
                    'Race': 'first'
                }).nlargest(5, '_DuplicateCount')
                
                print(f"\n📋 Top 5 Duplicate Groups:")
                for idx, (_, row) in enumerate(top_groups.iterrows(), 1):
                    print(f"   {idx}. {row['OwnerName'][:40]:40s} | "
                          f"{row['Race'][:30]:30s} | "
                          f"Count: {int(row['_DuplicateCount']):2d} | "
                          f"Amount: {row['AwardAmount']:,.0f}")
        
    except Exception as e:
        print(f"❌ Error detecting duplicates: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Bank Verification
    if bank_loaded and len(duplicates_df) > 0:
        print_section("💰 STEP 4: Bank Payment Verification")
        
        print("\n🔍 Matching Strategy:")
        print("   1. Extract PaymentReference and PaymentReference_D1 from awards")
        print("   2. Match against AwardRef and AwardRef10Digits in bank")
        print("   3. Use last 10 digits for partial matching")
        print("   4. Categorize: Matched / Partial / Unmatched")
        
        try:
            matched, partial, unmatched = analyzer.verify_bank_payments()
            
            print(f"\n📊 Verification Results:")
            print(f"   ✅ Matched (Confirmed):        {len(matched):6,} records")
            print(f"   ⚠️  Partial/Suspected:         {len(partial):6,} records")
            print(f"   ❌ Unmatched (Not in Bank):   {len(unmatched):6,} records")
            print(f"   {'─'*50}")
            print(f"   📊 Total:                      {len(matched) + len(partial) + len(unmatched):6,} records")
            
            # Calculate percentages
            total = len(duplicates_df)
            if total > 0:
                print(f"\n📈 Percentages:")
                print(f"   Matched:   {(len(matched)/total*100):5.1f}%")
                print(f"   Partial:   {(len(partial)/total*100):5.1f}%")
                print(f"   Unmatched: {(len(unmatched)/total*100):5.1f}%")
            
            # Show sample matches
            if len(matched) > 0:
                print(f"\n✅ Sample Matched Records (Top 3):")
                for idx, (_, row) in enumerate(matched.head(3).iterrows(), 1):
                    print(f"   {idx}. {row.get('OwnerName', 'N/A')[:40]:40s} | "
                          f"Award: {row.get('AwardAmount', 0):,.0f} | "
                          f"Bank: {row.get('BankTransferAmount', 0):,.0f}")
            
            if len(unmatched) > 0:
                print(f"\n❌ Sample Unmatched Records (Top 3):")
                for idx, (_, row) in enumerate(unmatched.head(3).iterrows(), 1):
                    print(f"   {idx}. {row.get('OwnerName', 'N/A')[:40]:40s} | "
                          f"Amount: {row.get('AwardAmount', 0):,.0f}")
            
        except Exception as e:
            print(f"❌ Error in bank verification: {e}")
            import traceback
            traceback.print_exc()
    
    # Step 5: Generate Reports
    print_section("📄 STEP 5: Generating Reports")
    
    try:
        reports = analyzer.generate_reports()
        
        print("\n✅ Reports Generated Successfully:")
        for report_type, report_path in reports.items():
            if report_path and Path(report_path).exists():
                file_size = Path(report_path).stat().st_size / 1024  # KB
                print(f"   📊 {report_type:20s}: {report_path.name} ({file_size:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error generating reports: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    elapsed = time.time() - start_time
    
    print_section("✅ AUDIT COMPLETE")
    
    print(f"\n⏱️  Total Processing Time: {elapsed:.2f} seconds")
    print(f"📊 Total Records Processed: {len(awards_df):,}")
    if len(duplicates_df) > 0:
        print(f"⚠️  Duplicates Detected: {len(duplicates_df):,} ({len(duplicates_df)/len(awards_df)*100:.2f}%)")
    print(f"✅ Audit Trail Saved")
    
    print("\n" + "="*80)
    print("🎉 Professional audit analysis completed successfully!")
    print("="*80)


if __name__ == "__main__":
    run_professional_audit()
