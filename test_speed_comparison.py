# -*- coding: utf-8 -*-
"""
اختبار مقارنة سرعة التحميل
Speed Comparison Test
"""

import time
import pandas as pd
from pathlib import Path
from core.multi_file_loader import load_multiple_files
from core.fast_file_loader import load_files_parallel


def create_test_files(num_files=5, rows_per_file=10000):
    """إنشاء ملفات اختبار"""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    files = []
    for i in range(num_files):
        df = pd.DataFrame({
            'ID': range(i * rows_per_file, (i + 1) * rows_per_file),
            'Name': [f'Person_{j}' for j in range(rows_per_file)],
            'Amount': [100 + j * 0.5 for j in range(rows_per_file)],
            'Date': pd.date_range('2024-01-01', periods=rows_per_file, freq='1H')
        })
        
        file_path = test_dir / f"test_file_{i}.csv"
        df.to_csv(file_path, index=False)
        files.append(file_path)
    
    return files


def test_standard_loader(files):
    """اختبار المحمل العادي"""
    print("🔄 اختبار المحمل العادي (load_multiple_files)...")
    
    # محاكاة ملفات Streamlit
    class FakeUploadedFile:
        def __init__(self, path):
            self.path = path
            self.name = path.name
            self._content = None
            
        def seek(self, pos):
            pass
            
        def read(self):
            if self._content is None:
                with open(self.path, 'rb') as f:
                    self._content = f.read()
            return self._content
    
    fake_files = [FakeUploadedFile(f) for f in files]
    
    start = time.time()
    df, stats, removed = load_multiple_files(fake_files, use_duckdb=True)
    duration = time.time() - start
    
    print(f"   ✅ اكتمل في {duration:.2f} ثانية")
    print(f"   📊 السجلات: {len(df):,}")
    print(f"   🗑️ المحذوفات: {removed:,}")
    
    return duration, len(df)


def test_parallel_loader(files):
    """اختبار المحمل المتوازي"""
    print("\n🚀 اختبار المحمل المتوازي (load_files_parallel)...")
    
    class FakeUploadedFile:
        def __init__(self, path):
            self.path = path
            self.name = path.name
            self._content = None
            
        def seek(self, pos):
            pass
            
        def read(self):
            if self._content is None:
                with open(self.path, 'rb') as f:
                    self._content = f.read()
            return self._content
    
    fake_files = [FakeUploadedFile(f) for f in files]
    
    start = time.time()
    df, stats, removed = load_files_parallel(
        fake_files, 
        use_duckdb=True,
        max_workers=4
    )
    duration = time.time() - start
    
    print(f"   ✅ اكتمل في {duration:.2f} ثانية")
    print(f"   📊 السجلات: {len(df):,}")
    print(f"   🗑️ المحذوفات: {removed:,}")
    
    return duration, len(df)


def main():
    print("=" * 60)
    print("🧪 اختبار مقارنة سرعة التحميل")
    print("=" * 60)
    
    # إنشاء ملفات اختبار
    print("\n📝 إنشاء ملفات اختبار...")
    num_files = 7
    rows_per_file = 10000
    files = create_test_files(num_files, rows_per_file)
    print(f"   ✅ تم إنشاء {num_files} ملفات، كل ملف يحتوي على {rows_per_file:,} سجل")
    
    # اختبار المحمل العادي
    time_standard, rows_standard = test_standard_loader(files)
    
    # اختبار المحمل المتوازي
    time_parallel, rows_parallel = test_parallel_loader(files)
    
    # المقارنة
    print("\n" + "=" * 60)
    print("📊 نتائج المقارنة:")
    print("=" * 60)
    print(f"⏱️  المحمل العادي:   {time_standard:.2f} ثانية")
    print(f"⚡ المحمل المتوازي: {time_parallel:.2f} ثانية")
    
    if time_standard > time_parallel:
        speedup = time_standard / time_parallel
        improvement = ((time_standard - time_parallel) / time_standard) * 100
        print(f"\n🎉 التحسين: {speedup:.2f}x أسرع ({improvement:.1f}% تحسين)")
        print(f"⏰ توفير الوقت: {time_standard - time_parallel:.2f} ثانية")
    else:
        print("\n⚠️  المحمل العادي أسرع في هذا الاختبار")
    
    # تنظيف
    print("\n🗑️  تنظيف ملفات الاختبار...")
    for f in files:
        f.unlink()
    Path("test_data").rmdir()
    print("   ✅ تم التنظيف")
    
    print("\n✨ انتهى الاختبار!")


if __name__ == "__main__":
    main()
