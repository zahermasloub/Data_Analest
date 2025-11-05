@echo off
REM تشغيل سريع للتطبيق - Data Analest Quick Launch
cd /d "%~dp0\.."
start "Data Analest" C:/Python314/python.exe -m streamlit run main_app_redesigned.py
