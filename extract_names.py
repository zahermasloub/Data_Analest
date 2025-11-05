import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load the data
df = pd.read_csv('العجوري 11-4.csv', encoding='utf-8-sig')

# Create unique column names
original_columns = df.columns.tolist()
new_columns = []
seen = {}

for col in original_columns:
    if col in seen:
        seen[col] += 1
        new_columns.append(f"{col}_{seen[col]}")
    else:
        seen[col] = 1
        new_columns.append(col)

df.columns = new_columns

# Remove duplicate columns
cols_to_keep = []
cols_seen = set()
for col in df.columns:
    base_col = col.split('_')[0] if '_' in col else col
    if base_col not in cols_seen:
        cols_to_keep.append(col)
        cols_seen.add(base_col)

df_clean = df[cols_to_keep]

# Clean data
df_clean['AwardAmount'] = df_clean['AwardAmount'].astype(str).str.replace(',', '').str.replace('"', '')
df_clean['AwardAmount'] = pd.to_numeric(df_clean['AwardAmount'], errors='coerce')
df_clean['EntryDate'] = pd.to_datetime(df_clean['EntryDate'])
df_clean = df_clean.dropna(subset=['OwnerName', 'Race', 'AwardAmount'])

# Create participant_id
def create_participant_id(row):
    identifiers = []
    if pd.notna(row['OwnerQatariId']) and row['OwnerQatariId'] != '':
        identifiers.append(f"QID_{row['OwnerQatariId']}")
    if pd.notna(row['OwnerNumber']) and row['OwnerNumber'] != '':
        identifiers.append(f"NUM_{row['OwnerNumber']}")
    if pd.notna(row['OwnerName']) and row['OwnerName'] != '':
        name = str(row['OwnerName']).strip().lower()
        identifiers.append(f"NAME_{name}")
    return hash(tuple(identifiers)) if identifiers else None

df_clean['participant_id'] = df_clean.apply(create_participant_id, axis=1)
df_clean['race_id'] = df_clean['Race'].str.strip().str.lower().apply(hash)

# Find duplicates
duplicate_criteria = ['participant_id', 'race_id', 'AwardAmount']
potential_duplicates = df_clean[df_clean.duplicated(subset=duplicate_criteria, keep=False)]

dup_summary = potential_duplicates.groupby(duplicate_criteria).agg({
    'EntryDate': ['count', 'min', 'max'],
    'PaymentReference': 'first',
    'OwnerName': 'first',
    'Race': 'first'
}).reset_index()

dup_summary.columns = ['participant_id', 'race_id', 'amount', 'occurrences', 'first_date', 'last_date', 'payment_ref', 'owner_name', 'race_name']
actual_duplicates = dup_summary[dup_summary['occurrences'] > 1]

print('='*100)
print(f'عدد الحالات المكررة: {len(actual_duplicates)}')
print('='*100)
print()

if len(actual_duplicates) > 0:
    print('أسماء الأشخاص الذين لديهم دفعات متكررة:')
    print('='*100)
    print()
    
    for i, row in actual_duplicates.iterrows():
        print(f"{i+1}. الاسم: {row['owner_name']}")
        print(f"   السباق: {row['race_name']}")
        print(f"   المبلغ: {row['amount']:,.0f} ريال قطري")
        print(f"   عدد التكرارات: {row['occurrences']}")
        print('-'*100)
    
    print()
    print('='*100)
    print('ملخص حسب الشخص (مرتب حسب عدد التكرارات):')
    print('='*100)
    print()
    
    person_summary = actual_duplicates.groupby('owner_name').agg({
        'occurrences': 'sum',
        'race_name': 'count',
        'amount': 'sum'
    }).sort_values('occurrences', ascending=False)
    person_summary.columns = ['إجمالي التكرارات', 'عدد السباقات المكررة', 'إجمالي المبالغ']
    
    print(f"{'الاسم':<50} {'إجمالي التكرارات':>20} {'عدد السباقات':>20} {'إجمالي المبالغ (ريال)':>30}")
    print('-'*120)
    
    for name, stats in person_summary.iterrows():
        print(f"{name:<50} {int(stats['إجمالي التكرارات']):>20} {int(stats['عدد السباقات المكررة']):>20} {stats['إجمالي المبالغ']:>30,.0f}")
    
    print()
    print('='*100)
    print(f'إجمالي عدد الأشخاص المتأثرين: {len(person_summary)}')
    print('='*100)
else:
    print('لا توجد دفعات متكررة')
