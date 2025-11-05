# -*- coding: utf-8 -*-
"""
إعدادات التطبيق المركزية
"""

import os
from pathlib import Path

# المسارات الأساسية
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATE_DIR = BASE_DIR / "templates"

# إنشاء المجلدات إذا لم تكن موجودة
for dir_path in [UPLOAD_DIR, OUTPUT_DIR, TEMPLATE_DIR]:
    dir_path.mkdir(exist_ok=True)

# إعدادات تحميل الملفات
ALLOWED_EXTENSIONS = ['.xlsx', '.xls', '.csv']
MAX_FILE_SIZE_MB = 500

# إعدادات كشف التكرارات
DUPLICATE_DETECTION = {
    'exact_match': True,
    'fuzzy_match': True,
    'fuzzy_threshold': 90,  # نسبة التطابق المطلوبة
    'time_window_days': None,  # None = لا يوجد تقييد زمني
}

# إعدادات كشف الشذوذات والانحرافات
ANOMALY_DETECTION = {
    'methods': ['iqr', 'zscore', 'isolation_forest', 'dbscan'],
    'iqr_multiplier': 1.5,
    'zscore_threshold': 3,
    'isolation_contamination': 0.1,
    'sensitivity': 'medium',  # low, medium, high
}

# إعدادات التحليل الإحصائي
STATISTICAL_ANALYSIS = {
    'confidence_level': 0.95,
    'significance_level': 0.05,
    'min_sample_size': 30,
}

# إعدادات التقارير
REPORT_SETTINGS = {
    'language': 'ar',  # ar, en, both
    'include_visualizations': True,
    'include_statistical_tests': True,
    'export_formats': ['html', 'pdf', 'excel'],
}

# إعدادات الأداء
PERFORMANCE = {
    'chunk_size': 10000,  # عدد الصفوف لكل دفعة
    'use_multiprocessing': True,
    'n_jobs': -1,  # -1 = استخدام جميع النوى المتاحة
}

# رسائل النظام
MESSAGES = {
    'ar': {
        'upload_success': 'تم تحميل الملف بنجاح',
        'processing': 'جاري معالجة البيانات...',
        'analysis_complete': 'اكتمل التحليل بنجاح',
        'error': 'حدث خطأ أثناء المعالجة',
        'no_duplicates': 'لم يتم العثور على دفعات مكررة',
        'no_anomalies': 'لم يتم العثور على انحرافات غير طبيعية',
    },
    'en': {
        'upload_success': 'File uploaded successfully',
        'processing': 'Processing data...',
        'analysis_complete': 'Analysis completed successfully',
        'error': 'An error occurred during processing',
        'no_duplicates': 'No duplicate payments found',
        'no_anomalies': 'No anomalies detected',
    }
}

# أنواع الأعمدة الشائعة (للكشف التلقائي)
COLUMN_TYPES = {
    'id_columns': ['id', 'رقم', 'معرف', 'identifier', 'code', 'كود'],
    'name_columns': ['name', 'اسم', 'participant', 'مشارك', 'entity', 'جهة'],
    'amount_columns': ['amount', 'قيمة', 'مبلغ', 'total', 'إجمالي', 'payment', 'دفعة'],
    'date_columns': ['date', 'تاريخ', 'time', 'وقت', 'datetime', 'timestamp'],
    'category_columns': ['category', 'فئة', 'type', 'نوع', 'class', 'صنف'],
}
