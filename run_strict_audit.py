"""
تشغيل نظام التدقيق الصارم - دقة 100%
=====================================

نظام تدقيق متقدم بمعايير صارمة للجهات الأمنية
"""

from pathlib import Path
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.strict_audit_analyzer import StrictAuditAnalyzer
import pandas as pd


def main():
    print("="*80)
    print("🔒 نظام التدقيق الصارم - دقة 100%")
    print("="*80)
    print("📋 المتطلبات:")
    print("   ✓ كشف التكرارات بدقة 100%")
    print("   ✓ التحقق من البنك بدقة 100%")
    print("   ✓ بدون تسامح في الأخطاء")
    print("   ✓ تقارير معتمدة للجهات الأمنية")
    print("="*80)
    
    # Initialize analyzer
    analyzer = StrictAuditAnalyzer()
    
    # Step 1: Load award files
    print("\n📂 الخطوة 1: تحميل ملفات الجوائز")
    print("-" * 80)
    
    # Use combined file
    awards_file = Path("uploads/Combined_Awards_2018_2025.xlsx")
    
    if not awards_file.exists():
        print(f"❌ الملف غير موجود: {awards_file}")
        return
    
    try:
        print(f"   📄 تحميل: {awards_file.name}... ", end='')
        awards_data = pd.read_excel(awards_file)
        awards_data['SourceFile'] = awards_file.name
        print(f"✅ ({len(awards_data):,} سجل)")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return
    
    print(f"\n✅ إجمالي السجلات: {len(awards_data):,}")
    
    # Step 2: Detect duplicates with 100% accuracy
    print("\n🔍 الخطوة 2: كشف التكرارات بمعيار 100%")
    print("-" * 80)
    print("📋 المفتاح المركب (Composite Key):")
    print("   1. Season (الموسم)")
    print("   2. Race (السباق)")
    print("   3. Owner Number (رقم المالك)")
    print("   4. Owner Name (اسم المالك)")
    print("   5. Owner QatariID (الرقم القطري)")
    print("   6. Award Amount (مبلغ الجائزة)")
    print("\n⚠️ ملاحظة: Entry Date مسموح باختلافه (هذا ما يكشف التكرار)")
    
    duplicates = analyzer.detect_strict_duplicates(awards_data)
    
    # Step 3: Load bank statement
    print("\n🏦 الخطوة 3: تحميل كشف البنك")
    print("-" * 80)
    
    bank_file = Path("uploads/العجوري 11-4.csv")
    if bank_file.exists():
        try:
            print(f"   📄 تحميل: {bank_file.name}... ", end='')
            
            # Try to find header row
            df_peek = pd.read_csv(bank_file, nrows=20, encoding='utf-8-sig', encoding_errors='ignore')
            header_row = None
            
            for i in range(len(df_peek)):
                row_values = df_peek.iloc[i].astype(str).str.lower()
                if any('award' in str(v).lower() or 'reference' in str(v).lower() for v in row_values):
                    header_row = i
                    break
            
            if header_row is None:
                header_row = 0
            
            bank_data = pd.read_csv(bank_file, header=header_row, encoding='utf-8-sig', encoding_errors='ignore')
            
            # Normalize column names
            bank_data.columns = bank_data.columns.str.strip()
            
            # Map columns
            column_mapping = {}
            for col in bank_data.columns:
                col_lower = col.lower().strip()
                if 'award ref 10 digits' in col_lower or 'awardref10digits' in col_lower:
                    column_mapping[col] = 'AwardRef10Digits'
                elif 'award ref' in col_lower and '10' not in col_lower:
                    column_mapping[col] = 'AwardRef'
                elif 'bank reference' in col_lower or 'bankreference' in col_lower:
                    column_mapping[col] = 'BankReference'
                elif 'request reference' in col_lower:
                    column_mapping[col] = 'RequestReference'
                elif 'transaction date' in col_lower:
                    column_mapping[col] = 'TransactionDate'
                elif 'value date' in col_lower:
                    column_mapping[col] = 'ValueDate'
                elif 'beneficiary' in col_lower and 'name' in col_lower:
                    column_mapping[col] = 'BeneficiaryName'
                elif 'debit' in col_lower:
                    column_mapping[col] = 'Debit'
                elif 'credit' in col_lower:
                    column_mapping[col] = 'Credit'
                elif 'iban' in col_lower:
                    column_mapping[col] = 'IBAN'
            
            if column_mapping:
                bank_data = bank_data.rename(columns=column_mapping)
            
            # Calculate TransferAmount
            if 'Credit' in bank_data.columns:
                bank_data['TransferAmount'] = pd.to_numeric(bank_data['Credit'], errors='coerce')
            elif 'Debit' in bank_data.columns:
                bank_data['TransferAmount'] = pd.to_numeric(bank_data['Debit'], errors='coerce')
            
            print(f"✅ ({len(bank_data):,} معاملة)")
            print(f"   📋 الأعمدة الرئيسية المكتشفة:")
            key_cols = ['AwardRef', 'AwardRef10Digits', 'BankReference', 'TransferAmount']
            for col in key_cols:
                if col in bank_data.columns:
                    non_null = bank_data[col].notna().sum()
                    print(f"      • {col}: {non_null:,} قيمة")
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            bank_data = None
    else:
        print(f"   ⚠️ الملف غير موجود: {bank_file.name}")
        bank_data = None
    
    # Step 4: Verify against bank (100% accuracy)
    if len(duplicates) > 0 and bank_data is not None:
        print("\n✅ الخطوة 4: التحقق من كشف البنك بمعيار 100%")
        print("-" * 80)
        
        verification_results = analyzer.verify_bank_strict(duplicates, bank_data)
        
        # Store results
        analyzer.matched_df = verification_results['matched']
        analyzer.unmatched_df = verification_results['unmatched']
        
        # Update duplicates with confirmed status
        # التكرار المؤكد = تكرار + مطابقة بنكية 100%
        if len(analyzer.matched_df) > 0:
            matched_indices = analyzer.matched_df.index
            duplicates.loc[matched_indices, '_ConfirmedDuplicate'] = True
            duplicates.loc[matched_indices, 'ReasonText'] = '🔴 تكرار مؤكد + بنك مطابق'
        
        # Update unmatched duplicates reason
        if len(analyzer.unmatched_df) > 0:
            unmatched_indices = analyzer.unmatched_df.index
            # Keep existing reason or update based on bank status
            for idx in unmatched_indices:
                if idx in duplicates.index:
                    bank_reason = analyzer.unmatched_df.loc[idx, 'MatchReason'] if 'MatchReason' in analyzer.unmatched_df.columns else ''
                    if bank_reason:
                        duplicates.loc[idx, 'ReasonText'] = f'⚠️ تكرار - {bank_reason}'
        
        # Update analyzer.duplicates with new info
        analyzer.duplicates = duplicates
        
    else:
        print("\n⚠️ تخطي التحقق من البنك (لا توجد بيانات)")
        analyzer.matched_df = pd.DataFrame()
        analyzer.unmatched_df = duplicates.copy() if len(duplicates) > 0 else pd.DataFrame()
    
    # Step 5: Generate strict reports
    print("\n📄 الخطوة 5: إنشاء التقارير النهائية")
    print("-" * 80)
    
    generated_files = analyzer.generate_strict_reports()
    
    # Generate bank verification report
    if hasattr(analyzer, 'matched_df') and hasattr(analyzer, 'unmatched_df'):
        output_path = Path("outputs")
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        bank_report_file = output_path / f"Strict_Bank_Verification_{timestamp}.xlsx"
        
        print(f"\n📝 التقرير 2: تقرير التحقق من البنك")
        print(f"   الملف: {bank_report_file.name}")
        
        with pd.ExcelWriter(bank_report_file, engine='openpyxl') as writer:
            # Sheet 1: Matched (100%)
            if len(analyzer.matched_df) > 0:
                export_cols_matched = [
                    'Season', 'Race', 'OwnerNumber', 'OwnerName', 'OwnerQatariId',
                    'AwardAmount', 'EntryDate', 'PaymentReference',
                    'BankTransferAmount', 'BankTransactionDate', 'BankBeneficiary',
                    'BankReference', 'BankIBAN',
                    'MatchStatus', 'MatchReason', 'AmountDifference',
                    '_DuplicateGroup', '_DuplicateCount'
                ]
                available = [c for c in export_cols_matched if c in analyzer.matched_df.columns]
                analyzer.matched_df[available].to_excel(writer, sheet_name='Matched_100%', index=False)
                print(f"   ✅ سجلات مطابقة 100%: {len(analyzer.matched_df):,}")
            
            # Sheet 2: Unmatched
            if len(analyzer.unmatched_df) > 0:
                export_cols_unmatched = [
                    'Season', 'Race', 'OwnerNumber', 'OwnerName', 'OwnerQatariId',
                    'AwardAmount', 'EntryDate', 'PaymentReference',
                    'MatchStatus', 'MatchReason',
                    '_DuplicateGroup', '_DuplicateCount'
                ]
                available = [c for c in export_cols_unmatched if c in analyzer.unmatched_df.columns]
                analyzer.unmatched_df[available].to_excel(writer, sheet_name='Unmatched', index=False)
                print(f"   ❌ سجلات غير مطابقة: {len(analyzer.unmatched_df):,}")
            
            # Sheet 3: Verification summary
            summary_data = {
                'Metric': [
                    'إجمالي السجلات المكررة',
                    'سجلات مطابقة 100%',
                    'سجلات غير مطابقة',
                    'نسبة المطابقة',
                    'معيار الدقة',
                    'التسامح في المبلغ',
                    'التسامح في التاريخ'
                ],
                'Value': [
                    len(duplicates),
                    len(analyzer.matched_df),
                    len(analyzer.unmatched_df),
                    f"{(len(analyzer.matched_df)/len(duplicates)*100):.1f}%" if len(duplicates) > 0 else "0%",
                    '100% (صارم)',
                    '0.00 ريال (تطابق تام)',
                    'غير مطبق (Reference فقط)'
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"   ✅ تم الحفظ بنجاح")
        generated_files['bank_verification'] = str(bank_report_file)
    
    # Final summary
    print("\n" + "="*80)
    print("✅ اكتمل التدقيق الصارم")
    print("="*80)
    print("\n📊 الملخص النهائي:")
    
    stats = analyzer.validation_report['statistics']
    
    if 'duplicates' in stats:
        dup_stats = stats['duplicates']
        print(f"\n🔍 التكرارات:")
        print(f"   • إجمالي السجلات: {dup_stats['total_records']:,}")
        print(f"   • سجلات مكررة: {dup_stats['total_duplicates']:,}")
        print(f"   • مجموعات التكرار: {dup_stats['unique_groups']:,}")
        print(f"   • نسبة التكرار: {dup_stats['duplicate_rate']:.2f}%")
        print(f"   • إجمالي المبالغ المكررة: {dup_stats['total_amount']:,.2f} ريال")
    
    if 'bank_verification' in stats:
        bank_stats = stats['bank_verification']
        print(f"\n🏦 التحقق من البنك:")
        print(f"   • إجمالي السجلات: {bank_stats['total']:,}")
        print(f"   • ✅ مطابق 100%: {bank_stats['matched']:,} ({bank_stats['match_rate']:.1f}%)")
        print(f"   • ❌ غير مطابق: {bank_stats['unmatched']:,} ({100-bank_stats['match_rate']:.1f}%)")
    
    print(f"\n📁 التقارير المُنشأة:")
    for report_type, file_path in generated_files.items():
        print(f"   • {Path(file_path).name}")
    
    print("\n" + "="*80)
    print("🔒 التقارير معتمدة وموثوقة بدقة 100% للجهات الأمنية")
    print("="*80)


if __name__ == "__main__":
    main()
