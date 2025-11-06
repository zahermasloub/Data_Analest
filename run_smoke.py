from core.camel_awards_analyzer import CamelAwardsAnalyzer

# عدّل المسارات حسب ملفاتك الفعلية
awards = ["data/awards_2023.xlsx", "data/awards_2024.xlsx"]
bank   = "data/bank_2024.xlsx"

an = CamelAwardsAnalyzer(use_advanced_features=True)

an.load_awards_files(awards)
an.load_bank_statement(bank)

res = an.match_with_bank(
    time_window_days=7,
    use_record_linkage=True,
    files_info={"awards_files": awards, "bank_file": bank}
)

out = an.export_report("var/reports/camel_awards/output_smoke.xlsx")
print("RunID:", an.current_run_id)
print("Rows:", len(res))
