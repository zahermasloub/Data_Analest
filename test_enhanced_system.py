"""
اختبار سريع للنظام المحسّن - Quick Test
========================================

اختبار جميع المكونات الرئيسية
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from core.enhanced_audit_system import (
    DataNormalizer,
    EnhancedBankMatcher,
    GroundTruthValidator,
    ComprehensiveReportGenerator
)
import pandas as pd


def test_data_normalizer():
    """اختبار محوّل البيانات"""
    print("\n" + "="*80)
    print("🧪 اختبار DataNormalizer")
    print("="*80)
    
    # بيانات اختبار
    test_data = pd.DataFrame({
        'Entry Date': ['2024-01-01', '2024-01-02'],
        'Owner Number': ['123', '456'],
        'Owner Name': ['محمد أحمد', 'علي سعيد'],
        'Owner Qatari Id': ['28512345678', '28598765432'],  # لاحظ الاختلاف في الاسم
        'Award Amount': ['5000.00', '3000.00'],
        'Unnamed: 0': [1, 2],  # سيتم إزالته
    })
    
    normalizer = DataNormalizer()
    normalized = normalizer.normalize_dataframe(test_data, "Test")
    
    print(f"\n✅ النتائج:")
    print(f"   الأعمدة الأصلية: {len(test_data.columns)}")
    print(f"   الأعمدة بعد التوحيد: {len(normalized.columns)}")
    print(f"   الأعمدة الموحدة: {normalized.columns.tolist()}")
    
    # التحقق من التوحيد
    assert 'EntryDate' in normalized.columns, "❌ فشل توحيد EntryDate"
    assert 'OwnerQatariID' in normalized.columns, "❌ فشل توحيد OwnerQatariID"
    assert 'Unnamed: 0' not in normalized.columns, "❌ لم يتم إزالة Unnamed"
    
    print(f"\n✅ جميع الاختبارات نجحت!")
    
    return normalizer


def test_bank_matcher():
    """اختبار مطابق البنك"""
    print("\n" + "="*80)
    print("🧪 اختبار EnhancedBankMatcher")
    print("="*80)
    
    # بيانات جوائز اختبار
    awards = pd.DataFrame({
        'Season': ['2023-2024', '2023-2024', '2023-2024'],
        'Race': ['سباق 1', 'سباق 2', 'سباق 3'],
        'OwnerNumber': ['123', '456', '789'],
        'OwnerName': ['محمد', 'علي', 'أحمد'],
        'OwnerQatariID': ['28512345678', '28598765432', '28511111111'],
        'AwardAmount': [5000.00, 3000.00, 2000.00],
        'PaymentReference': ['821B291050', '821B731113', '999X999999'],
        'PaymentReference_D1': ['', '', ''],
    })
    
    # بيانات بنك اختبار
    bank = pd.DataFrame({
        'AwardRef': ['821B291050', '821B731113'],
        'AwardRef10Digits': ['1B291050', '1B731113'],
        'BankReference': ['BNK001', 'BNK002'],
        'TransferAmount': [5000.00, 2999.00],  # لاحظ الاختلاف في الثاني
        'TransactionDate': ['2024-01-15', '2024-01-16'],
        'BeneficiaryName': ['محمد أحمد', 'علي سعيد'],
    })
    
    matcher = EnhancedBankMatcher(
        ref_last_digits=10,
        amount_tolerance=0.00,
        date_window_days=14
    )
    
    results = matcher.match_awards_to_bank(awards, bank)
    
    print(f"\n✅ النتائج:")
    print(f"   مطابق 100%: {len(results['matched'])}")
    print(f"   جزئي: {len(results['partial'])}")
    print(f"   غير مطابق: {len(results['unmatched'])}")
    
    # التحقق
    assert len(results['matched']) == 1, "❌ يجب أن يكون هناك مطابقة واحدة"
    assert len(results['partial']) == 1, "❌ يجب أن يكون هناك جزئية واحدة"
    assert len(results['unmatched']) == 1, "❌ يجب أن يكون هناك غير مطابق واحد"
    
    print(f"\n✅ جميع الاختبارات نجحت!")
    
    return matcher


def test_ground_truth_validator():
    """اختبار مدقق الحالات المعروفة"""
    print("\n" + "="*80)
    print("🧪 اختبار GroundTruthValidator")
    print("="*80)
    
    # بيانات تكرارات اختبار (تحتوي على بعض الحالات المعروفة)
    duplicates = pd.DataFrame({
        'PaymentReference': [
            '821B291050', '821B291373',  # زوج معروف
            '821B731113', '822B731638',  # زوج معروف
            '999X999999', '888Y888888',  # زوج غير معروف
        ],
        'PaymentReference_D1': [''] * 6,
        'OwnerName': ['محمد'] * 6,
    })
    
    validator = GroundTruthValidator()
    results = validator.validate_detection(duplicates)
    
    print(f"\n✅ النتائج:")
    print(f"   إجمالي الحالات: {results['total_cases']}")
    print(f"   حالات مكتشفة: {len(results['detected'])}")
    print(f"   حالات مفقودة: {len(results['missing'])}")
    print(f"   نسبة الاكتشاف: {results['detection_rate']:.1f}%")
    
    # التحقق
    assert results['total_cases'] == 20, "❌ يجب أن يكون هناك 20 حالة معروفة"
    assert len(results['detected']) >= 2, "❌ يجب اكتشاف حالتين على الأقل"
    
    print(f"\n✅ جميع الاختبارات نجحت!")
    
    return validator


def test_composite_key():
    """اختبار المفتاح المركب"""
    print("\n" + "="*80)
    print("🧪 اختبار المفتاح المركب")
    print("="*80)
    
    # بيانات اختبار
    data = pd.DataFrame({
        'Season': ['2023-2024', '2023-2024', '2023-2024', '2024-2025'],
        'Race': ['سباق 1', 'سباق 1', 'سباق 1', 'سباق 2'],
        'OwnerNumber': ['123', '123', '123', '456'],
        'OwnerName': ['محمد', 'محمد', 'محمد أحمد', 'علي'],  # لاحظ الاختلاف البسيط
        'OwnerQatariID': ['28512345678', '28512345678', '28512345678', '28598765432'],
        'AwardAmount': [5000.00, 5000.00, 5000.00, 3000.00],
        'EntryDate': ['2024-01-01', '2024-02-15', '2024-01-01', '2024-01-01'],  # تواريخ مختلفة
    })
    
    # تطبيع
    for col in ['Season', 'Race', 'OwnerName']:
        data[col] = data[col].astype(str).str.strip().str.lower()
    
    # إنشاء المفتاح
    data['_Key'] = (
        data['Season'] + '|' +
        data['Race'] + '|' +
        data['OwnerNumber'] + '|' +
        data['OwnerName'] + '|' +
        data['OwnerQatariID'] + '|' +
        data['AwardAmount'].astype(str)
    )
    
    # عد التكرارات
    data['_Count'] = data.groupby('_Key')['_Key'].transform('count')
    
    duplicates = data[data['_Count'] >= 2]
    
    print(f"\n✅ النتائج:")
    print(f"   إجمالي السجلات: {len(data)}")
    print(f"   سجلات مكررة: {len(duplicates)}")
    print(f"   مجموعات التكرار: {duplicates['_Key'].nunique()}")
    
    print(f"\n📋 المفاتيح المكررة:")
    for key in duplicates['_Key'].unique():
        count = (data['_Key'] == key).sum()
        print(f"   • {key[:50]}... ({count} مرات)")
    
    # التحقق
    # الصفوف 0 و 1 يجب أن تكون مكررة (نفس كل شيء ما عدا التاريخ)
    # الصف 2 مختلف (اسم مختلف قليلاً)
    assert len(duplicates) >= 2, "❌ يجب اكتشاف تكرارين على الأقل"
    
    print(f"\n✅ جميع الاختبارات نجحت!")
    
    # ملاحظة مهمة
    print(f"\n⚠️ ملاحظة مهمة:")
    print(f"   الصف 2 (محمد أحمد) مختلف عن الصف 0,1 (محمد)")
    print(f"   بعد التطبيع، الفرق لا يزال موجوداً")
    print(f"   لذلك لن يُعتبر تكراراً - وهذا صحيح!")
    print(f"   البرمبت يطلب تطابق تام بعد التطبيع الشكلي فقط")


def main():
    """البرنامج الرئيسي"""
    print("="*80)
    print("🧪 اختبار النظام المحسّن - Enhanced System Test")
    print("="*80)
    
    try:
        # Test 1: DataNormalizer
        normalizer = test_data_normalizer()
        
        # Test 2: BankMatcher
        matcher = test_bank_matcher()
        
        # Test 3: GroundTruthValidator
        validator = test_ground_truth_validator()
        
        # Test 4: Composite Key
        test_composite_key()
        
        # النتيجة النهائية
        print("\n" + "="*80)
        print("✅ جميع الاختبارات نجحت!")
        print("="*80)
        print("\n💡 النظام جاهز للاستخدام:")
        print("   python run_enhanced_audit.py")
        
    except AssertionError as e:
        print(f"\n❌ فشل الاختبار: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
