# -*- coding: utf-8 -*-
"""
سكريبت اختبار النظام على البيانات الموجودة
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

from core.data_loader import DataLoader
from core.duplicate_analyzer import DuplicateAnalyzer
from core.anomaly_detector import AnomalyDetector

def test_system():
    """اختبار النظام"""
    print("=" * 80)
    print("اختبار محلل البيانات المالية")
    print("=" * 80)
    print()
    
    # 1. تحميل البيانات
    print("1️⃣ تحميل البيانات...")
    data_file = Path(__file__).parent / "العجوري 11-4.csv"
    
    if not data_file.exists():
        print(f"❌ الملف غير موجود: {data_file}")
        return
    
    try:
        loader = DataLoader(data_file)
        loader.load()
        loader.auto_clean()
        df = loader.get_data()
        
        print(f"✅ تم تحميل {len(df):,} صف و {len(df.columns)} عمود")
        print(f"   الأعمدة: {', '.join(df.columns[:5])}...")
        print()
    except Exception as e:
        print(f"❌ خطأ في التحميل: {e}")
        return
    
    # 2. كشف أنواع الأعمدة
    print("2️⃣ كشف أنواع الأعمدة...")
    column_types = loader.detect_column_types()
    print(f"   أعمدة رقمية: {len(column_types['numeric'])}")
    print(f"   أعمدة نصية: {len(column_types['text'])}")
    print(f"   أعمدة مبالغ: {column_types['amount']}")
    print()
    
    # 3. البحث عن عمود المبلغ
    amount_cols = column_types['amount']
    if not amount_cols:
        # البحث في الأعمدة الرقمية
        numeric_cols = column_types['numeric']
        if numeric_cols:
            amount_col = numeric_cols[0]
            print(f"⚠️ لم يتم العثور على عمود مبلغ محدد، سيتم استخدام: {amount_col}")
        else:
            print("❌ لا توجد أعمدة رقمية للتحليل")
            return
    else:
        amount_col = amount_cols[0]
        print(f"✅ عمود المبلغ: {amount_col}")
    print()
    
    # 4. كشف الانحرافات
    print("3️⃣ كشف الانحرافات (IQR)...")
    try:
        detector = AnomalyDetector(df)
        anomalies_iqr = detector.detect_iqr_anomalies(amount_col, multiplier=1.5)
        
        print(f"   تم العثور على {len(anomalies_iqr):,} شذوذ ({len(anomalies_iqr)/len(df)*100:.2f}%)")
        
        if len(anomalies_iqr) > 0:
            print(f"   أعلى 3 قيم شاذة:")
            top_3 = anomalies_iqr.nlargest(3, amount_col)[[amount_col]]
            for idx, row in top_3.iterrows():
                print(f"      - {row[amount_col]:,.0f}")
        print()
    except Exception as e:
        print(f"❌ خطأ في كشف الانحرافات: {e}")
        print()
    
    # 5. الإحصائيات
    print("4️⃣ الإحصائيات الوصفية...")
    try:
        stats = detector.get_statistical_summary(amount_col)
        print(f"   العدد: {stats['count']:,}")
        print(f"   المتوسط: {stats['mean']:,.0f}")
        print(f"   الوسيط: {stats['median']:,.0f}")
        print(f"   الانحراف المعياري: {stats['std']:,.0f}")
        print(f"   الحد الأدنى: {stats['min']:,.0f}")
        print(f"   الحد الأقصى: {stats['max']:,.0f}")
        print(f"   معامل الاختلاف: {stats['cv']:.2f}%")
        print()
    except Exception as e:
        print(f"❌ خطأ في الإحصائيات: {e}")
        print()
    
    # 6. كشف التكرارات (إن وجدت أعمدة مناسبة)
    print("5️⃣ كشف التكرارات...")
    text_cols = column_types['text']
    if len(text_cols) > 0 and amount_col:
        try:
            entity_col = text_cols[0]  # أول عمود نصي
            print(f"   استخدام عمود الجهة: {entity_col}")
            
            analyzer = DuplicateAnalyzer(df)
            duplicates = analyzer.find_payment_duplicates(
                entity_col=entity_col,
                amount_col=amount_col
            )
            
            print(f"   تم العثور على {len(duplicates):,} دفعة مكررة")
            if len(duplicates) > 0:
                print(f"   عدد المجموعات المكررة: {duplicates['duplicate_group'].nunique()}")
        except Exception as e:
            print(f"❌ خطأ في كشف التكرارات: {e}")
    else:
        print("   ⚠️ لا توجد أعمدة مناسبة لكشف التكرارات")
    
    print()
    print("=" * 80)
    print("✅ اكتمل الاختبار بنجاح!")
    print("=" * 80)
    print()
    print("للاستخدام التفاعلي، قم بتشغيل:")
    print("   streamlit run app.py")
    print()


if __name__ == "__main__":
    test_system()
