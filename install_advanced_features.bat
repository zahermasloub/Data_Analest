@echo off
chcp 65001 > nul
title تثبيت المكونات المتقدمة - Installing Advanced Components
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     تثبيت المكونات المتقدمة لمحلل جوائز الهجن             ║
echo ║   Installing Advanced Components for Camel Awards         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/6] 📦 تثبيت مكتبات المطابقة - Matching Libraries...
pip install rapidfuzz>=3.5.0
if errorlevel 1 (
    echo ❌ فشل تثبيت rapidfuzz
    goto error
)
echo ✅ تم تثبيت rapidfuzz

pip install recordlinkage>=0.16.0
if errorlevel 1 (
    echo ❌ فشل تثبيت recordlinkage
    goto error
)
echo ✅ تم تثبيت recordlinkage
echo.

echo [2/6] 🧹 تثبيت مكتبات التنظيف - Cleaning Libraries...
pip install pyjanitor>=0.26.0
if errorlevel 1 (
    echo ⚠️ تحذير: فشل تثبيت pyjanitor (اختياري)
)
echo ✅ تم تثبيت pyjanitor

pip install dateparser>=1.2.0
if errorlevel 1 (
    echo ⚠️ تحذير: فشل تثبيت dateparser (اختياري)
)
echo ✅ تم تثبيت dateparser

pip install pandera>=0.17.0
if errorlevel 1 (
    echo ⚠️ تحذير: فشل تثبيت pandera (اختياري)
)
echo ✅ تم تثبيت pandera

pip install Unidecode>=1.3.0
if errorlevel 1 (
    echo ⚠️ تحذير: فشل تثبيت Unidecode (اختياري)
)
echo ✅ تم تثبيت Unidecode
echo.

echo [3/6] ⚡ تثبيت مكتبات الأداء - Performance Libraries...
pip install duckdb>=0.9.0
if errorlevel 1 (
    echo ⚠️ تحذير: فشل تثبيت duckdb (اختياري - سيعمل النظام بدونه)
) else (
    echo ✅ تم تثبيت duckdb
)

pip install "dask[complete]>=2023.12.0"
if errorlevel 1 (
    echo ⚠️ تحذير: فشل تثبيت dask (اختياري - للملفات الكبيرة جداً)
) else (
    echo ✅ تم تثبيت dask
)
echo.

echo [4/6] 📊 تثبيت مكتبات البيانات - Data Libraries...
pip install polars>=0.20.0
if errorlevel 1 (
    echo ⚠️ تحذير: فشل تثبيت polars (اختياري)
)
echo ✅ تم تثبيت polars

pip install pyarrow>=14.0.0
if errorlevel 1 (
    echo ⚠️ تحذير: فشل تثبيت pyarrow (اختياري)
)
echo ✅ تم تثبيت pyarrow
echo.

echo [5/6] 🔍 التحقق من التثبيت - Verifying Installation...
python -c "import rapidfuzz; print('✅ rapidfuzz:', rapidfuzz.__version__)"
python -c "import recordlinkage; print('✅ recordlinkage:', recordlinkage.__version__)"
python -c "try: import duckdb; print('✅ duckdb:', duckdb.__version__); except: print('⚠️ duckdb not available (optional)')"
python -c "try: import dask; print('✅ dask:', dask.__version__); except: print('⚠️ dask not available (optional)')"
echo.

echo [6/6] 🧪 تشغيل الاختبارات - Running Tests...
echo هل تريد تشغيل اختبارات المكونات؟ (Y/N)
set /p choice="Your choice: "
if /i "%choice%"=="Y" (
    echo.
    echo 🧪 تشغيل الاختبارات...
    python test_advanced_components.py
    if errorlevel 1 (
        echo.
        echo ⚠️ بعض الاختبارات فشلت - راجع الرسائل أعلاه
    ) else (
        echo.
        echo ✅ جميع الاختبارات نجحت!
    )
)
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║                   ✅ التثبيت مكتمل!                       ║
echo ║              Installation Complete!                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📚 الخطوة التالية - Next Step:
echo    - راجع CAMEL_AWARDS_INTEGRATION_GUIDE.md للدمج
echo    - Review CAMEL_AWARDS_INTEGRATION_GUIDE.md for integration
echo.
echo    - أو شغّل: python test_advanced_components.py
echo    - Or run: python test_advanced_components.py
echo.
pause
exit /b 0

:error
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║               ❌ حدث خطأ في التثبيت                      ║
echo ║            Installation Error Occurred                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo الرجاء التحقق من:
echo - اتصال الإنترنت متاح
echo - Python و pip مثبتان بشكل صحيح
echo - تشغيل Command Prompt كـ Administrator
echo.
echo أو جرب التثبيت اليدوي:
echo    pip install -r requirements.txt
echo.
pause
exit /b 1
