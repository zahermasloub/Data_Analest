"""
اختبار بسيط للتحقق من تثبيت duckdb
"""

print("=" * 60)
print("🔍 فحص تثبيت DuckDB")
print("=" * 60)

try:
    import duckdb
    print(f"\n✅ duckdb مثبت بنجاح!")
    print(f"   الإصدار: {duckdb.__version__}")
    
    # اختبار بسيط
    conn = duckdb.connect(':memory:')
    result = conn.execute("SELECT 'Hello from DuckDB!' as message").fetchone()
    print(f"\n✅ DuckDB يعمل بشكل صحيح!")
    print(f"   الرسالة: {result[0]}")
    
    # اختبار مع DataFrame
    import pandas as pd
    df = pd.DataFrame({
        'name': ['أحمد', 'محمد', 'علي'],
        'amount': [1000, 2000, 3000]
    })
    
    result = conn.execute("SELECT SUM(amount) as total FROM df").fetchone()
    print(f"\n✅ يمكن الاستعلام على DataFrames!")
    print(f"   المجموع: {result[0]:,.0f}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ جميع الاختبارات نجحت!")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n❌ خطأ: duckdb غير مثبت!")
    print(f"   الرسالة: {e}")
    print("\n💡 لتثبيته:")
    print("   C:/Python314/python.exe -m pip install --only-binary=:all: duckdb")
    
except Exception as e:
    print(f"\n❌ خطأ: {e}")
