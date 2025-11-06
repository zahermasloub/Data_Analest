from core.camel_awards_analyzer import CamelAwardsAnalyzer

# تحميل الإعدادات الافتراضية مع بدائل في حال غياب الملف
try:
    from server.camel_awards import analyzer_settings as CFG
except Exception:
    class CFG:
        FUZZY_THRESHOLD = 85
        DATE_WINDOW_DAYS = 7
        INCLUDE_AUDIT_SHEET = True
        NORMALIZE_WITH_UNIDECODE = True

awards = ["data/awards_2023.xlsx", "data/awards_2024.xlsx"]
bank   = "data/bank_2024.xlsx"

# 1) الإنشاء بدون وسطاء إضافية (لتفادي TypeError)
an = CamelAwardsAnalyzer(use_advanced_features=True)

# 2) محاولة ضبط الخيارات على الكائن إن توفرّت
if hasattr(an, "set_options") and callable(getattr(an, "set_options")):
    try:
        an.set_options(
            fuzzy_threshold=CFG.FUZZY_THRESHOLD,
            date_window_days=CFG.DATE_WINDOW_DAYS,
            normalize_with_unidecode=CFG.NORMALIZE_WITH_UNIDECODE,
        )
    except TypeError:
        pass  # بعض الإصدارات قد تقبل مجموعة فرعية فقط
else:
    # تعيين خواص مباشرة إن وُجدت
    if hasattr(an, "fuzzy_threshold"): an.fuzzy_threshold = CFG.FUZZY_THRESHOLD
    if hasattr(an, "date_window_days"): an.date_window_days = CFG.DATE_WINDOW_DAYS
    if hasattr(an, "normalize_with_unidecode"): an.normalize_with_unidecode = CFG.NORMALIZE_WITH_UNIDECODE

# 3) تحميل الملفات
an.load_awards_files(awards)
an.load_bank_statement(bank)

# 4) تشغيل المطابقة مع تمرير المعاملات إن كان مدعومًا
try:
    res = an.match_with_bank(
        time_window_days=CFG.DATE_WINDOW_DAYS,
        use_record_linkage=True,
        fuzzy_threshold=CFG.FUZZY_THRESHOLD,
        normalize_with_unidecode=CFG.NORMALIZE_WITH_UNIDECODE,
        files_info={"awards_files": awards, "bank_file": bank},
    )
except TypeError:
    # توقيع أقدم/مختلف
    res = an.match_with_bank(
        time_window_days=CFG.DATE_WINDOW_DAYS,
        use_record_linkage=True,
        files_info={"awards_files": awards, "bank_file": bank},
    )

# 5) التصدير: إضافة ورقة Audit Log إن كان مدعومًا
out_path = "var/reports/camel_awards/output_smoke.xlsx"
try:
    out = an.export_report(out_path, include_audit_sheet=CFG.INCLUDE_AUDIT_SHEET)
except TypeError:
    out = an.export_report(out_path)

print("RunID:", getattr(an, "current_run_id", "N/A"))
print("Rows:", len(res))
