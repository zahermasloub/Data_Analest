import pandas as pd
import glob

# Find latest report
files = glob.glob('outputs/Strict_Duplicates_*.xlsx')
latest = max(files)
print(f'قراءة: {latest}')

# Read unmatched duplicates
df = pd.read_excel(latest, sheet_name='Unmatched')
print(f'\nعدد السجلات المكررة: {len(df)}')

# Find Ibrahim records
result = df[df['OwnerName'].str.contains('ابراهيم', na=False)]
print(f'\nسجلات تحتوي على "ابراهيم": {len(result)}')

print('\n' + '='*100)
for idx, row in result.iterrows():
    print(f"\nالموسم: {row['Season']}")
    print(f"السباق: {row['Race']}")
    print(f"اسم المالك: {row['OwnerName']}")
    print(f"رقم المالك: {row['OwnerNumber']}")
    print(f"البطاقة: {row['OwnerQatariId']}")
    print(f"المبلغ: {row['AwardAmount']}")
    print(f"تاريخ الإدخال: {row['EntryDate']}")
    print(f"مجموعة التكرار: {row.get('_DuplicateGroup', 'N/A')}")
