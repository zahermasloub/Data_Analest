import pandas as pd
import glob

# Find latest report
files = glob.glob('outputs/Strict_Duplicates_*.xlsx')
latest = max(files)
print(f'📂 قراءة التقرير: {latest}\n')

# Read all sheets
xls = pd.ExcelFile(latest)
print(f'📑 الصفحات المتوفرة: {xls.sheet_names}\n')

# Read main duplicates sheet
df = pd.read_excel(latest, sheet_name='All_Duplicates')
print(f'✅ عدد السجلات المكررة: {len(df)}\n')

# Show available columns
print('📋 الأعمدة المتوفرة:')
for i, col in enumerate(df.columns, 1):
    print(f'   {i}. {col}')

# Check for name verification columns
print('\n🔍 حقول التوثيق للأسماء:')
name_cols = [col for col in df.columns if 'OwnerName' in col]
for col in name_cols:
    print(f'   ✅ {col}')

# Show sample data
print('\n📊 عينة من البيانات (أول تكرار):')
print('='*100)

if len(df) > 0:
    # Get first duplicate group
    first_group = df['_DuplicateGroup'].iloc[0]
    group_data = df[df['_DuplicateGroup'] == first_group]
    
    for idx, row in group_data.iterrows():
        print(f"\n السجل {idx + 1}:")
        print(f"   الموسم: {row['Season']}")
        print(f"   السباق: {row['Race']}")
        print(f"   رقم المشارك: {row['OwnerNumber']}")
        print(f"   اسم المالك: {row['OwnerName']}")
        print(f"   رقم البطاقة: {row['OwnerQatariId']}")
        print(f"   المبلغ: {row['AwardAmount']}")
        print(f"   تاريخ الإدخال: {row['EntryDate']}")
        
        # Show name verification fields
        if 'OwnerName_AllVariations' in row:
            print(f"   📝 جميع اختلافات الأسماء: {row['OwnerName_AllVariations']}")
        if 'OwnerName_VariationsCount' in row:
            print(f"   🔢 عدد الاختلافات: {row['OwnerName_VariationsCount']}")
        if 'OwnerName_MatchStatus' in row:
            print(f"   ✔️ حالة المطابقة: {row['OwnerName_MatchStatus']}")
        
        print(f"   مجموعة التكرار: #{row['_DuplicateGroup']}")
