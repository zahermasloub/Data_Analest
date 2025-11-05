@echo off
echo ====================================
echo محلل البيانات المالية المتقدم
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python غير مثبت! يرجى تثبيت Python 3.8 أو أحدث
    pause
    exit /b 1
)

echo [INFO] Python مثبت بنجاح
echo.

REM Check if requirements are installed
echo [INFO] التحقق من المكتبات المطلوبة...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [WARN] المكتبات غير مثبتة. جاري التثبيت...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] فشل تثبيت المكتبات!
        pause
        exit /b 1
    )
    echo [SUCCESS] تم تثبيت المكتبات بنجاح
) else (
    echo [SUCCESS] المكتبات مثبتة
)

echo.
echo ====================================
echo تشغيل التطبيق...
echo ====================================
echo.
echo سيتم فتح المتصفح تلقائياً على:
echo http://localhost:8501
echo.
echo للإيقاف: اضغط Ctrl+C
echo ====================================
echo.

REM Run Streamlit
streamlit run app.py

pause
