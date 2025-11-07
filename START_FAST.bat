@echo off
echo ================================================
echo    تشغيل تطبيق تحليل جوائز سباقات الهجن
echo    Camel Awards Analysis - Fast Version 
echo ================================================
echo.
echo جاري بدء التطبيق...
echo.

REM إيقاف أي عملية Streamlit قديمة
taskkill /F /IM streamlit.exe 2>nul

REM الانتظار قليلاً
timeout /t 2 /nobreak >nul

REM تشغيل التطبيق
echo تشغيل التطبيق على المنفذ 8512...
python -m streamlit run main_app.py --server.headless true --server.port 8512

echo.
echo ================================================
echo التطبيق متوقف
echo ================================================
pause
