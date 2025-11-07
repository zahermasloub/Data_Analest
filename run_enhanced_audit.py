"""
تشغيل نظام التدقيق المحسّن - Run Enhanced Audit System
========================================================

برنامج تشغيل نظام التدقيق المحسّن بناءً على متطلبات البرمبت الاحترافي

المميزات:
- توحيد البيانات الشامل
- كشف التكرارات بدقة 100%
- مطابقة بنكية متقدمة (Matched / Partial / Unmatched)
- التحقق من الحالات المعروفة (28 حالة)
- تقارير شاملة (3 ملفات Excel)

الاستخدام:
    python run_enhanced_audit.py
"""

from pathlib import Path
import sys
import pandas as pd
from datetime import datetime

# Fix console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from core.enhanced_audit_system import (
    DataNormalizer,
    EnhancedBankMatcher,
    GroundTruthValidator,
    ComprehensiveReportGenerator
)


def load_awards_files(uploads_dir: Path) -> pd.DataFrame:
    """
    تحميل ودمج جميع ملفات الجوائز
    
    Args:
        uploads_dir: مجلد الملفات
        
    Returns:
        DataFrame مدموج
    """
    print("\n" + "="*80)
    print("📂 تحميل ملفات الجوائز")
    print("="*80)
    
    # البحث عن ملف مدموج
    combined_file = uploads_dir / "Combined_Awards_2018_2025.xlsx"
    
    if combined_file.exists():
        print(f"   📄 تحميل الملف المدموج: {combined_file.name}")
        
        # تحديد الأنواع للحماية من التحويل العلمي
        dtype_dict = {
            'OwnerQatariId': str,
            'Owner Qatari Id': str,
            'OwnerQatariID': str,
            'OwnerNumber': str,
            'Owner Number': str,
            'TrainerQatariId': str
        }
        
        try:
            df = pd.read_excel(combined_file, dtype=dtype_dict)
            df['SourceFile'] = combined_file.name
            print(f"   ✅ تم التحميل: {len(df):,} سجل")
            return df
        except Exception as e:
            print(f"   ❌ خطأ في التحميل: {e}")
            return pd.DataFrame()
    
    # إذا لم يوجد ملف مدموج، ابحث عن ملفات فردية
    print("   🔍 البحث عن ملفات فردية...")
    award_files = list(uploads_dir.glob("Awards*.xlsx")) + list(uploads_dir.glob("AwardsForSeason*.xlsx"))
    
    if not award_files:
        print("   ❌ لم يتم العثور على ملفات جوائز")
        return pd.DataFrame()
    
    print(f"   📁 عثر على {len(award_files)} ملف")
    
    all_dataframes = []
    
    for file in award_files:
        print(f"   📄 {file.name}... ", end='')
        try:
            df = pd.read_excel(file, dtype=dtype_dict)
            df['SourceFile'] = file.name
            all_dataframes.append(df)
            print(f"✅ ({len(df):,} سجل)")
        except Exception as e:
            print(f"❌ خطأ: {e}")
    
    if not all_dataframes:
        print("   ❌ فشل تحميل جميع الملفات")
        return pd.DataFrame()
    
    # دمج جميع الملفات
    merged = pd.concat(all_dataframes, ignore_index=True)
    print(f"\n   ✅ إجمالي السجلات بعد الدمج: {len(merged):,}")
    
    return merged


def load_bank_statement(uploads_dir: Path) -> pd.DataFrame:
    """
    تحميل كشف البنك مع اكتشاف ترويسة تلقائي
    
    Args:
        uploads_dir: مجلد الملفات
        
    Returns:
        DataFrame كشف البنك
    """
    print("\n" + "="*80)
    print("🏦 تحميل كشف البنك")
    print("="*80)
    
    # البحث عن ملف البنك
    bank_files = list(uploads_dir.glob("*.csv")) + list(uploads_dir.glob("*البنك*.xlsx")) + list(uploads_dir.glob("*bank*.csv"))
    
    if not bank_files:
        print("   ❌ لم يتم العثور على ملف البنك")
        return pd.DataFrame()
    
    # أخذ أول ملف
    bank_file = bank_files[0]
    print(f"   📄 تحميل: {bank_file.name}")
    
    try:
        # محاولة قراءة CSV
        if bank_file.suffix.lower() == '.csv':
            # فحص أول 20 صف للعثور على الترويسة
            df_peek = pd.read_csv(bank_file, nrows=20, encoding='utf-8-sig', encoding_errors='ignore')
            
            header_row = None
            for i in range(len(df_peek)):
                row_values = df_peek.iloc[i].astype(str).str.lower()
                if any('award' in str(v).lower() or 'reference' in str(v).lower() for v in row_values):
                    header_row = i
                    print(f"   ✅ اكتشاف الترويسة في الصف: {i + 1}")
                    break
            
            if header_row is None:
                header_row = 0
                print(f"   ⚠️ استخدام الصف الأول كترويسة")
            
            # قراءة الملف كاملاً
            bank_df = pd.read_csv(bank_file, header=header_row, encoding='utf-8-sig', encoding_errors='ignore')
        else:
            # قراءة Excel
            bank_df = pd.read_excel(bank_file)
        
        # تنظيف أسماء الأعمدة
        bank_df.columns = bank_df.columns.str.strip()
        
        print(f"   ✅ تم التحميل: {len(bank_df):,} معاملة")
        print(f"   📋 الأعمدة: {', '.join(bank_df.columns[:5].tolist())}...")
        
        return bank_df
        
    except Exception as e:
        print(f"   ❌ خطأ في التحميل: {e}")
        return pd.DataFrame()


def detect_duplicates_enhanced(
    df: pd.DataFrame,
    normalizer: DataNormalizer
) -> pd.DataFrame:
    """
    كشف التكرارات باستخدام المفتاح المركب
    
    Composite Key:
        Season + Race + OwnerNumber + OwnerName + OwnerQatariID + AwardAmount
    
    Args:
        df: DataFrame موحد
        normalizer: محول البيانات
        
    Returns:
        DataFrame التكرارات
    """
    print("\n" + "="*80)
    print("🔍 كشف التكرارات بالمفتاح المركب")
    print("="*80)
    
    # الحقول المطلوبة
    required_fields = ['Season', 'Race', 'OwnerNumber', 'OwnerName', 'OwnerQatariID', 'AwardAmount']
    
    print(f"   📋 المفتاح المركب (6 حقول):")
    for i, field in enumerate(required_fields, 1):
        print(f"      {i}. {field}")
    
    # التحقق من وجود الحقول
    missing = [f for f in required_fields if f not in df.columns]
    if missing:
        print(f"   ❌ حقول مفقودة: {missing}")
        return pd.DataFrame()
    
    # إزالة الصفوف بحقول فارغة
    df_clean = df.copy()
    initial_count = len(df_clean)
    
    for field in required_fields:
        df_clean = df_clean[df_clean[field].notna()].copy()
    
    removed = initial_count - len(df_clean)
    if removed > 0:
        print(f"   ⚠️ إزالة {removed:,} صف بحقول فارغة")
    
    # تنظيف وتطبيع
    for field in ['Season', 'Race', 'OwnerName']:
        if field in df_clean.columns:
            df_clean[field] = df_clean[field].astype(str).str.strip().str.lower()
    
    df_clean['OwnerNumber'] = df_clean['OwnerNumber'].astype(str).str.strip()
    df_clean['OwnerQatariID'] = df_clean['OwnerQatariID'].astype(str).str.strip()
    df_clean['AwardAmount'] = pd.to_numeric(df_clean['AwardAmount'], errors='coerce').round(2)
    
    # إزالة الصفوف بمبالغ غير صحيحة
    df_clean = df_clean[df_clean['AwardAmount'] > 0].copy()
    
    # إنشاء المفتاح المركب
    df_clean['_CompositeKey'] = (
        df_clean['Season'] + '|' +
        df_clean['Race'] + '|' +
        df_clean['OwnerNumber'] + '|' +
        df_clean['OwnerName'] + '|' +
        df_clean['OwnerQatariID'] + '|' +
        df_clean['AwardAmount'].astype(str)
    )
    
    # عد التكرارات
    df_clean['_DuplicateCount'] = df_clean.groupby('_CompositeKey')['_CompositeKey'].transform('count')
    df_clean['_DuplicateGroup'] = df_clean.groupby('_CompositeKey').ngroup()
    
    # تصفية التكرارات فقط (count >= 2)
    duplicates = df_clean[df_clean['_DuplicateCount'] >= 2].copy()
    
    # ترتيب
    if 'EntryDate' in duplicates.columns:
        duplicates['EntryDate'] = pd.to_datetime(duplicates['EntryDate'], errors='coerce')
        duplicates = duplicates.sort_values(['_DuplicateGroup', 'EntryDate'])
    else:
        duplicates = duplicates.sort_values('_DuplicateGroup')
    
    # إضافة معلومات
    duplicates['_DuplicateSeverity'] = 'مشتبه'
    duplicates['ReasonText'] = '✅ تكرار مؤكد - مفتاح مركب متطابق'
    
    # إحصائيات
    total = len(df_clean)
    dup_count = len(duplicates)
    unique_groups = duplicates['_DuplicateGroup'].nunique() if dup_count > 0 else 0
    total_amount = duplicates['AwardAmount'].sum() if dup_count > 0 else 0
    dup_rate = (dup_count / total * 100) if total > 0 else 0
    
    print(f"\n   📊 نتائج الكشف:")
    print(f"      إجمالي السجلات الصحيحة: {total:,}")
    print(f"      سجلات مكررة: {dup_count:,}")
    print(f"      مجموعات التكرار: {unique_groups:,}")
    print(f"      نسبة التكرار: {dup_rate:.2f}%")
    print(f"      إجمالي المبالغ المكررة: {total_amount:,.2f} ريال")
    
    if unique_groups > 0:
        print(f"\n   🔝 أكثر 5 حالات تكراراً:")
        top = duplicates.groupby('_CompositeKey').size().sort_values(ascending=False).head(5)
        for i, (key, count) in enumerate(top.items(), 1):
            example = duplicates[duplicates['_CompositeKey'] == key].iloc[0]
            print(f"      {i}. {example['OwnerName'][:30]} - {example['Race'][:20]} ({count} مرات)")
    
    return duplicates


def main():
    """البرنامج الرئيسي"""
    
    print("="*80)
    print("🚀 نظام التدقيق المحسّن - Enhanced Audit System")
    print("="*80)
    print("📋 المميزات:")
    print("   ✓ توحيد البيانات الشامل")
    print("   ✓ كشف التكرارات بدقة 100%")
    print("   ✓ مطابقة بنكية متقدمة (3 فئات)")
    print("   ✓ التحقق من 28 حالة معروفة")
    print("   ✓ 3 تقارير Excel احترافية")
    print("="*80)
    
    # المجلدات
    uploads_dir = Path("uploads")
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # Step 1: Initialize components
    print("\n🔧 تهيئة المكونات...")
    normalizer = DataNormalizer()
    bank_matcher = EnhancedBankMatcher(
        ref_last_digits=10,
        amount_tolerance=0.00,
        date_window_days=14
    )
    ground_truth_validator = GroundTruthValidator()
    
    # Step 2: Load awards data
    awards_raw = load_awards_files(uploads_dir)
    
    if len(awards_raw) == 0:
        print("\n❌ فشل تحميل بيانات الجوائز")
        return
    
    # Step 3: Normalize awards data
    awards_normalized = normalizer.normalize_dataframe(awards_raw, "Awards")
    
    # Step 4: Detect duplicates
    duplicates = detect_duplicates_enhanced(awards_normalized, normalizer)
    
    if len(duplicates) == 0:
        print("\n✅ لم يتم العثور على تكرارات")
        # يمكن الاستمرار لتوليد تقرير فارغ
    
    # Step 5: Load bank statement
    bank_raw = load_bank_statement(uploads_dir)
    
    if len(bank_raw) > 0:
        # Normalize bank data
        bank_normalized = normalizer.normalize_dataframe(bank_raw, "Bank")
        
        # Step 6: Match with bank
        if len(duplicates) > 0:
            match_results = bank_matcher.match_awards_to_bank(duplicates, bank_normalized)
        else:
            print("\n⚠️ تخطي المطابقة البنكية (لا توجد تكرارات)")
    else:
        print("\n⚠️ تخطي المطابقة البنكية (لا يوجد كشف بنك)")
    
    # Step 7: Validate ground truth
    if len(duplicates) > 0:
        ground_truth_validator.validate_detection(duplicates)
    else:
        print("\n⚠️ تخطي التحقق من الحالات المعروفة (لا توجد تكرارات)")
    
    # Step 8: Generate comprehensive reports
    report_generator = ComprehensiveReportGenerator(
        duplicates=duplicates,
        normalizer=normalizer,
        bank_matcher=bank_matcher,
        ground_truth_validator=ground_truth_validator,
        output_dir=str(outputs_dir)
    )
    
    generated_files = report_generator.generate_all_reports()
    
    # Final summary
    print("\n" + "="*80)
    print("✅ اكتمل التدقيق المحسّن")
    print("="*80)
    
    print("\n📊 الملخص النهائي:")
    
    if len(duplicates) > 0:
        print(f"\n🔍 التكرارات:")
        print(f"   • إجمالي السجلات المكررة: {len(duplicates):,}")
        print(f"   • مجموعات التكرار: {duplicates['_DuplicateGroup'].nunique():,}")
        print(f"   • إجمالي المبالغ: {duplicates['AwardAmount'].sum():,.2f} ريال")
    
    if len(bank_matcher.matched_records) > 0 or len(bank_matcher.partial_records) > 0 or len(bank_matcher.unmatched_records) > 0:
        total_bank = len(bank_matcher.matched_records) + len(bank_matcher.partial_records) + len(bank_matcher.unmatched_records)
        matched_pct = (len(bank_matcher.matched_records) / total_bank * 100) if total_bank > 0 else 0
        partial_pct = (len(bank_matcher.partial_records) / total_bank * 100) if total_bank > 0 else 0
        
        print(f"\n🏦 المطابقة البنكية:")
        print(f"   • ✅ مطابق 100%: {len(bank_matcher.matched_records):,} ({matched_pct:.1f}%)")
        print(f"   • ⚠️ جزئي/مشتبه: {len(bank_matcher.partial_records):,} ({partial_pct:.1f}%)")
        print(f"   • ❌ غير مطابق: {len(bank_matcher.unmatched_records):,} ({100-matched_pct-partial_pct:.1f}%)")
    
    if ground_truth_validator.validation_results:
        results = ground_truth_validator.validation_results
        print(f"\n🎯 الحالات المعروفة:")
        print(f"   • إجمالي الحالات: {results['total_cases']}")
        print(f"   • حالات مكتشفة: {len(results['detected'])}")
        print(f"   • حالات مفقودة: {len(results['missing'])}")
        print(f"   • نسبة الاكتشاف: {results['detection_rate']:.1f}%")
    
    print(f"\n📁 التقارير المُنشأة ({len(generated_files)}):")
    for report_type, file_path in generated_files.items():
        print(f"   • {Path(file_path).name}")
    
    print("\n" + "="*80)
    print("🎉 النظام المحسّن جاهز للاستخدام المستقبلي على ملفات أخرى")
    print("="*80)
    
    print("\n💡 للاستخدام على بيانات أخرى:")
    print("   1. ضع ملفات البيانات في مجلد uploads/")
    print("   2. شغّل: python run_enhanced_audit.py")
    print("   3. راجع التقارير في مجلد outputs/")


if __name__ == "__main__":
    main()
