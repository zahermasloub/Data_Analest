import pandas as pd

# Load data
df = pd.read_excel('uploads/Combined_Awards_2018_2025.xlsx')

# Search for Ibrahim records
result = df[(df['OwnerName'].str.contains('ابراهيم', na=False)) & 
            (df['OwnerName'].str.contains('النعيمي', na=False))]

print(f'عدد السجلات: {len(result)}')
print('\nالتفاصيل الكاملة:')

for idx, row in result.iterrows():
    print(f"\n{'='*80}")
    print(f"الموسم: {row['Season']}")
    print(f"السباق: {row['Race']}")
    print(f"رقم المالك: {row['OwnerNumber']}")
    print(f"اسم المالك: {row['OwnerName']}")
    print(f"البطاقة: {row['OwnerQatariId']}")
    print(f"المبلغ: {row['AwardAmount']}")
    print(f"تاريخ الإدخال: {row['EntryDate']}")
    print(f"Reference: {row.get('Reference', 'N/A')}")
