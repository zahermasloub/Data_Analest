import pandas as pd
from core.camel_awards_analyzer import CamelAwardsAnalyzer

analyzer = CamelAwardsAnalyzer()
analyzer.load_bank_statement('الملفات/ملف البنك.xlsx')

print("Bank columns:", list(analyzer.bank_data.columns))
print("\nBank data shape:", analyzer.bank_data.shape)
print("\nFirst few columns:")
for col in list(analyzer.bank_data.columns)[:15]:
    print(f"  - {col}")
