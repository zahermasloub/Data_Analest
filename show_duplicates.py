import pandas as pd

# Read the duplicates report
df = pd.read_excel('duplicates_report.xlsx', engine='openpyxl')

print('='*80)
print(f'عدد الحالات المكررة: {len(df)}')
print('='*80)
print()

if len(df) > 0:
    print('أسماء الأشخاص الذين لديهم دفعات متكررة:')
    print('='*80)
    print()
    
    for i, row in df.iterrows():
        print(f"{i+1}. الاسم: {row['owner_name']}")
        print(f"   السباق: {row['race_name']}")
        print(f"   المبلغ: {row['amount']:,.0f} ريال")
        print(f"   عدد التكرارات: {row['occurrences']}")
        print(f"   تاريخ أول دفعة: {row['first_date']}")
        print(f"   تاريخ آخر دفعة: {row['last_date']}")
        print('-'*80)
        print()
    
    # Summary by person
    print('='*80)
    print('ملخص حسب الشخص (إجمالي الحالات المكررة لكل شخص):')
    print('='*80)
    person_summary = df.groupby('owner_name').agg({
        'occurrences': 'sum',
        'race_name': 'count'
    }).sort_values('occurrences', ascending=False)
    person_summary.columns = ['إجمالي التكرارات', 'عدد السباقات']
    
    for name, stats in person_summary.iterrows():
        print(f"{name}: {int(stats['إجمالي التكرارات'])} تكرار في {int(stats['عدد السباقات'])} سباق")
        
else:
    print('لا توجد دفعات متكررة')
