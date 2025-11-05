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

# Find exact duplicates: Same Name + Same Race + Same Amount + Different Dates
duplicate_criteria = ['OwnerName', 'Race', 'AwardAmount']
potential_duplicates = df_clean[df_clean.duplicated(subset=duplicate_criteria, keep=False)].copy()

# Group by Name, Race, and Amount
grouped = potential_duplicates.groupby(duplicate_criteria)

print('='*120)
print('الدفعات المكررة: نفس الاسم + نفس السباق + نفس المبلغ + تواريخ مختلفة')
print('='*120)
print()

duplicate_cases = []

for (name, race, amount), group in grouped:
    if len(group) > 1:
        # Check if dates are different
        unique_dates = group['EntryDate'].nunique()
        
        if unique_dates > 1 or len(group) > 1:  # Multiple entries
            dates_list = group['EntryDate'].dt.strftime('%Y-%m-%d').tolist()
            payment_refs = group['PaymentReference'].tolist()
            
            duplicate_cases.append({
                'الاسم': name,
                'السباق': race,
                'المبلغ': amount,
                'عدد التكرارات': len(group),
                'عدد التواريخ المختلفة': unique_dates,
                'التواريخ': dates_list,
                'أرقام الدفع': payment_refs
            })

print(f'إجمالي عدد الحالات المكررة: {len(duplicate_cases)}')
print('='*120)
print()

# Display each case
for i, case in enumerate(duplicate_cases, 1):
    print(f"{i}. الاسم: {case['الاسم']}")
    print(f"   السباق: {case['السباق']}")
    print(f"   المبلغ: {case['المبلغ']:,.0f} ريال قطري")
    print(f"   عدد التكرارات: {case['عدد التكرارات']}")
    print(f"   عدد التواريخ المختلفة: {case['عدد التواريخ المختلفة']}")
    print(f"   التواريخ:")
    for j, date in enumerate(case['التواريخ'], 1):
        ref = case['أرقام الدفع'][j-1]
        print(f"      - التاريخ {j}: {date} (رقم الدفع: {ref})")
    print('-'*120)
    print()

# Export detailed report
print('='*120)
print('إنشاء تقرير مفصل...')
print('='*120)

detailed_records = []
for (name, race, amount), group in grouped:
    if len(group) > 1:
        unique_dates = group['EntryDate'].nunique()
        if unique_dates > 1 or len(group) > 1:
            for idx, row in group.iterrows():
                detailed_records.append({
                    'اسم المالك': row['OwnerName'],
                    'السباق': row['Race'],
                    'المبلغ': row['AwardAmount'],
                    'تاريخ الدفع': row['EntryDate'].strftime('%Y-%m-%d'),
                    'الموسم': row['Season'],
                    'رقم الدفع': row['PaymentReference'],
                    'المستفيد': row['BeneficiaryEnglishName'],
                    'IBAN': row['IBAN'],
                    'نوع الدفع': row['PaymentType']
                })

detailed_df = pd.DataFrame(detailed_records)

# Sort by name, race, amount, and date
detailed_df = detailed_df.sort_values(['اسم المالك', 'السباق', 'المبلغ', 'تاريخ الدفع'])

# Save to Excel
detailed_df.to_excel('تقرير_الدفعات_المكررة_مفصل.xlsx', index=False, engine='openpyxl')
print(f'✓ تم حفظ التقرير المفصل: تقرير_الدفعات_المكررة_مفصل.xlsx ({len(detailed_records)} سجل)')

# Summary statistics
print()
print('='*120)
print('إحصائيات ملخصة:')
print('='*120)

# Group by person to see who has most duplicates
person_summary = {}
for case in duplicate_cases:
    name = case['الاسم']
    if name not in person_summary:
        person_summary[name] = {
            'عدد_السباقات': 0,
            'إجمالي_التكرارات': 0,
            'إجمالي_المبالغ': 0
        }
    person_summary[name]['عدد_السباقات'] += 1
    person_summary[name]['إجمالي_التكرارات'] += case['عدد التكرارات']
    person_summary[name]['إجمالي_المبالغ'] += case['المبلغ'] * case['عدد التكرارات']

# Sort by total duplicates
sorted_persons = sorted(person_summary.items(), 
                       key=lambda x: x[1]['إجمالي_التكرارات'], 
                       reverse=True)

print()
print('الأشخاص الأكثر تكراراً:')
print('-'*120)
print(f"{'الاسم':<50} {'عدد السباقات':>15} {'إجمالي التكرارات':>20} {'إجمالي المبالغ (ريال)':>30}")
print('-'*120)

for name, stats in sorted_persons[:20]:  # Top 20
    print(f"{name:<50} {stats['عدد_السباقات']:>15} {stats['إجمالي_التكرارات']:>20} {stats['إجمالي_المبالغ']:>30,.0f}")

print()
print('='*120)
print(f'إجمالي عدد الأشخاص المتأثرين: {len(person_summary)}')
print(f'إجمالي عدد الحالات المكررة: {len(duplicate_cases)}')
print(f'إجمالي عدد السجلات المكررة: {len(detailed_records)}')
print('='*120)
