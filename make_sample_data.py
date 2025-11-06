import pandas as pd
from pathlib import Path
Path("data").mkdir(parents=True, exist_ok=True)

awards_2023 = pd.DataFrame([
    {"OwnerName":"سالم بن راشد","Season":"2023/2024","Race":"R-101","AwardAmount":5000,"EntryDate":"2024-02-10"},
    {"OwnerName":"محمد العذبة","Season":"2023/2024","Race":"R-102","AwardAmount":7000,"EntryDate":"2024-02-11"},
    # حالة تكرار مشتبه: نفس الاسم+السباق+المبلغ بتاريخ مختلف
    {"OwnerName":"سالم بن راشد","Season":"2023/2024","Race":"R-101","AwardAmount":5000,"EntryDate":"2024-02-12"},
])

awards_2024 = pd.DataFrame([
    {"OwnerName":"سعيد المنصوري","Season":"2024/2025","Race":"R-201","AwardAmount":9000,"EntryDate":"2025-01-05"},
    {"OwnerName":"محمد العذبة","Season":"2024/2025","Race":"R-202","AwardAmount":7000,"EntryDate":"2025-01-06"},
])

bank_2024 = pd.DataFrame([
    # مطابقة Exact لـ محمد العذبة (المبلغ 7000 ضمن نافذة 7 أيام)
    {"BankReference":"BR-9001","BeneficiaryName":"محمد العذبه","IBAN":"QA00TEST0001","TransferAmount":7000,"TransferDate":"2025-01-09"},
    # غير مطابق (مبلغ مختلف)
    {"BankReference":"BR-9002","BeneficiaryName":"سعيد المنصوري","IBAN":"QA00TEST0002","TransferAmount":8000,"TransferDate":"2025-01-06"},
    # مطابقة محتملة لـ سالم بن راشد (Fuzzy + نفس المبلغ ونطاق التاريخ)
    {"BankReference":"BR-9003","BeneficiaryName":"سالم بن راشد","IBAN":"QA00TEST0003","TransferAmount":5000,"TransferDate":"2024-02-11"},
])

awards_2023.to_excel("data/awards_2023.xlsx", index=False)
awards_2024.to_excel("data/awards_2024.xlsx", index=False)
bank_2024.to_excel("data/bank_2024.xlsx", index=False)
print("✅ Created sample files in ./data")
