# -*- coding: utf-8 -*-
"""
📦 مدير المكتبات التلقائي
Package Manager - Auto Installation
=====================================
التحقق من المكتبات المطلوبة وتثبيتها تلقائياً

Library Used: subprocess (built-in), importlib
Install if missing: N/A (Built-in modules)
"""

import subprocess
import sys
import importlib
from typing import List, Dict, Tuple
import warnings

class PackageManager:
    """مدير المكتبات التلقائي"""
    
    # قائمة المكتبات المطلوبة مع أسماء الاستيراد
    REQUIRED_PACKAGES = {
        # Core Data Processing
        'polars': 'polars>=0.19.0',
        'pyarrow': 'pyarrow>=14.0.0',
        'openpyxl': 'openpyxl>=3.1.0',
        'xlsxwriter': 'xlsxwriter>=3.1.0',
        'pandas': 'pandas>=2.1.0',
        
        # Text Processing & Matching
        'rapidfuzz': 'rapidfuzz>=3.5.0',
        'recordlinkage': 'recordlinkage>=0.16.0',
        'janitor': 'pyjanitor>=0.26.0',  # Note: import name is 'janitor'
        'dateparser': 'dateparser>=1.2.0',
        'pandera': 'pandera>=0.17.0',
        'unidecode': 'Unidecode>=1.3.0',
        
        # Performance (Optional)
        'duckdb': 'duckdb>=0.9.0',
        'dask': 'dask[complete]>=2023.12.0',
    }
    
    @staticmethod
    def ensure_package(package_name: str, pip_name: str = None) -> bool:
        """
        التحقق من وجود المكتبة وتثبيتها إن لزم
        
        Library Used: subprocess, importlib
        
        Args:
            package_name: اسم المكتبة للاستيراد (مثل: polars)
            pip_name: اسم المكتبة في pip (مثل: polars>=0.19.0)
            
        Returns:
            True إذا كانت المكتبة متوفرة أو تم تثبيتها بنجاح
        """
        if pip_name is None:
            pip_name = package_name
        
        try:
            # محاولة استيراد المكتبة
            importlib.import_module(package_name)
            return True
        except ImportError:
            print(f"⚠️  المكتبة {package_name} غير مثبتة. جاري التثبيت...")
            
            try:
                # محاولة التثبيت
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"✅ تم تثبيت {package_name} بنجاح")
                return True
            except subprocess.CalledProcessError:
                print(f"❌ فشل تثبيت {package_name}")
                return False
    
    @classmethod
    def ensure_all_packages(cls, optional: bool = False) -> Dict[str, bool]:
        """
        التحقق من جميع المكتبات المطلوبة
        
        Args:
            optional: تضمين المكتبات الاختيارية (duckdb, dask)
            
        Returns:
            قاموس بحالة كل مكتبة
        """
        results = {}
        
        for import_name, pip_name in cls.REQUIRED_PACKAGES.items():
            # تخطي المكتبات الاختيارية إذا لم تُطلب
            if not optional and import_name in ['duckdb', 'dask']:
                continue
            
            results[import_name] = cls.ensure_package(import_name, pip_name)
        
        return results
    
    @classmethod
    def get_missing_packages(cls) -> List[str]:
        """
        الحصول على قائمة المكتبات المفقودة
        
        Returns:
            قائمة بأسماء المكتبات غير المثبتة
        """
        missing = []
        
        for import_name in cls.REQUIRED_PACKAGES.keys():
            # تخطي المكتبات الاختيارية
            if import_name in ['duckdb', 'dask']:
                continue
            
            try:
                importlib.import_module(import_name)
            except ImportError:
                missing.append(import_name)
        
        return missing
    
    @classmethod
    def install_missing_packages(cls) -> Tuple[int, int]:
        """
        تثبيت جميع المكتبات المفقودة
        
        Returns:
            (عدد المثبتة بنجاح, عدد الفاشلة)
        """
        missing = cls.get_missing_packages()
        
        if not missing:
            print("✅ جميع المكتبات المطلوبة مثبتة بالفعل")
            return (0, 0)
        
        print(f"📦 جاري تثبيت {len(missing)} مكتبة...")
        
        success_count = 0
        fail_count = 0
        
        for package_name in missing:
            pip_name = cls.REQUIRED_PACKAGES[package_name]
            
            if cls.ensure_package(package_name, pip_name):
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n📊 النتيجة: {success_count} نجحت, {fail_count} فشلت")
        return (success_count, fail_count)
    
    @staticmethod
    def check_version(package_name: str) -> str:
        """
        الحصول على إصدار المكتبة
        
        Args:
            package_name: اسم المكتبة
            
        Returns:
            رقم الإصدار أو "غير متوفر"
        """
        try:
            module = importlib.import_module(package_name)
            return getattr(module, '__version__', 'غير معروف')
        except ImportError:
            return "غير مثبت"
    
    @classmethod
    def print_status_report(cls):
        """طباعة تقرير حالة جميع المكتبات"""
        print("\n" + "="*60)
        print("📦 تقرير حالة المكتبات - Packages Status Report")
        print("="*60)
        
        for import_name, pip_name in cls.REQUIRED_PACKAGES.items():
            version = cls.check_version(import_name)
            status = "✅" if version != "غير مثبت" else "❌"
            optional = " (اختياري)" if import_name in ['duckdb', 'dask'] else ""
            
            print(f"{status} {import_name:<15} : {version:<15} {optional}")
        
        print("="*60 + "\n")


# دالة مساعدة للاستخدام السريع
def ensure_camel_awards_dependencies():
    """
    التأكد من تثبيت جميع المكتبات المطلوبة لمحلل الجوائز
    
    Library Used: PackageManager (custom)
    """
    print("🏆 جاري التحقق من مكتبات محلل جوائز سباقات الهجن...")
    
    manager = PackageManager()
    results = manager.ensure_all_packages(optional=False)
    
    # عرض النتائج
    all_installed = all(results.values())
    
    if all_installed:
        print("✅ جميع المكتبات المطلوبة جاهزة!")
        return True
    else:
        failed = [name for name, status in results.items() if not status]
        print(f"⚠️  فشل تثبيت: {', '.join(failed)}")
        print("💡 حاول التثبيت يدوياً: pip install -r requirements.txt")
        return False


if __name__ == "__main__":
    # عند التشغيل المباشر
    PackageManager.print_status_report()
    
    missing = PackageManager.get_missing_packages()
    if missing:
        print(f"\n⚠️  مكتبات مفقودة: {', '.join(missing)}")
        
        response = input("\n❓ هل تريد تثبيتها الآن؟ (y/n): ")
        if response.lower() in ['y', 'yes', 'نعم']:
            PackageManager.install_missing_packages()
            PackageManager.print_status_report()
    else:
        print("\n✅ جميع المكتبات المطلوبة مثبتة!")
