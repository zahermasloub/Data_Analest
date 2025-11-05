# -*- coding: utf-8 -*-
"""
فحص نهائي شامل للبرنامج
"""

print("=" * 80)
print(" " * 28 + "🔍 فحص نهائي شامل")
print("=" * 80)
print()

# 1. فحص المكتبات
print("1️⃣ فحص المكتبات الأساسية...")
try:
    from core.data_loader import DataLoader
    from core.duplicate_analyzer import DuplicateAnalyzer
    from core.anomaly_detector import AnomalyDetector
    import config
    print("   ✅ جميع المكتبات تعمل\n")
except Exception as e:
    print(f"   ❌ خطأ: {e}\n")
    exit(1)

# 2. فحص تحميل البيانات
print("2️⃣ فحص تحميل البيانات...")
try:
    loader = DataLoader('العجوري 11-4.csv')
    df = loader.load().auto_clean().get_data()
    print(f"   ✅ تم التحميل: {len(df):,} صف، {len(df.columns)} عمود\n")
except Exception as e:
    print(f"   ❌ خطأ: {e}\n")
    exit(1)

# 3. فحص كشف التكرارات
print("3️⃣ فحص كشف التكرارات...")
try:
    analyzer = DuplicateAnalyzer(df)
    dups = analyzer.find_payment_duplicates('Season', 'EntryTypeNumber')
    print(f"   ✅ تم الكشف: {len(dups)} تكرار\n")
except Exception as e:
    print(f"   ❌ خطأ: {e}\n")
    exit(1)

# 4. فحص كشف الانحرافات
print("4️⃣ فحص كشف الانحرافات...")
try:
    detector = AnomalyDetector(df)
    anoms = detector.detect_all_anomalies('EntryTypeNumber')
    print(f"   ✅ تم الكشف: {len(anoms)} شذوذ\n")
except Exception as e:
    print(f"   ❌ خطأ: {e}\n")
    exit(1)

# 5. فحص الإحصائيات
print("5️⃣ فحص الإحصائيات...")
try:
    mean_val = df['EntryTypeNumber'].mean()
    std_val = df['EntryTypeNumber'].std()
    print(f"   ✅ المتوسط: {mean_val:,.0f}")
    print(f"   ✅ الانحراف المعياري: {std_val:,.0f}\n")
except Exception as e:
    print(f"   ❌ خطأ: {e}\n")
    exit(1)

# 6. فحص التصدير
print("6️⃣ فحص التصدير...")
try:
    output_file = 'outputs/final_test.xlsx'
    if len(dups) > 0:
        analyzer.export_duplicates(output_file)
        print(f"   ✅ تم التصدير: {output_file}\n")
    else:
        print("   ℹ️  لا توجد تكرارات للتصدير\n")
except Exception as e:
    print(f"   ❌ خطأ: {e}\n")
    exit(1)

# النتيجة النهائية
print("=" * 80)
print(" " * 25 + "✅ جميع الفحوصات نجحت!")
print("=" * 80)
print()
print("📊 الملخص:")
print(f"   • البيانات: {len(df):,} صف")
print(f"   • التكرارات: {len(dups)} مكرر")
print(f"   • الانحرافات: {len(anoms)} شذوذ")
print(f"   • المتوسط: {mean_val:,.0f}")
print()
print("✅ البرنامج سليم وجاهز للاستخدام!")
