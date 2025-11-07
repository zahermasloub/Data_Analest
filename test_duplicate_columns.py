"""Create test Excel files with duplicate columns and Unnamed columns to verify fixes."""
import pandas as pd
import numpy as np

# Test Case 1: File with duplicate column names
data1 = {
    'Season': ['2023', '2023', '2023'],
    'Race': ['Race1', 'Race2', 'Race3'],
    'OwnerQatariID': ['11111', '22222', '33333'],
    'OwnerQatariID.1': ['11111', '22222', '33333'],  # Duplicate!
    'OwnerName': ['Owner A', 'Owner B', 'Owner C'],
    'OwnerName.1': ['Owner A', 'Owner B', 'Owner C'],  # Duplicate!
    'AwardAmount': [1000, 2000, 3000],
    'AwardAmount.1': [1000, 2000, 3000],  # Duplicate!
}
df1 = pd.DataFrame(data1)

# Manually set duplicate column names (pandas will add .1, .2 etc)
# We need to directly create a dataframe with actual duplicate names
# This is tricky - Excel will save it properly
df1_with_duplicates = pd.DataFrame({
    ('Unnamed: 0', ''): [0, 1, 2],
    ('Season', ''): ['2023', '2023', '2023'],
    ('Race', ''): ['Race1', 'Race2', 'Race3'],
    ('OwnerQatariID', ''): ['11111', '22222', '33333'],
    ('OwnerQatariID', ' '): ['11111-dup', '22222-dup', '33333-dup'],  # Duplicate with space
    ('OwnerName', ''): ['Owner A', 'Owner B', 'Owner C'],
    ('OwnerName', ' '): ['Owner A-dup', 'Owner B-dup', 'Owner C-dup'],
    ('AwardAmount', ''): [1000, 2000, 3000],
    ('AwardAmount', ' '): [1000.5, 2000.5, 3000.5],
})

# Remove the MultiIndex by flattening to just first level
df1_with_duplicates.columns = [col[0] for col in df1_with_duplicates.columns]

print("Creating test file with duplicate columns...")
print(f"Columns: {df1_with_duplicates.columns.tolist()}")
print(f"Duplicate check: {df1_with_duplicates.columns.duplicated().any()}")

# Save to Excel
output_file = 'd:/Data_Analest/test_file_with_duplicates.xlsx'
df1_with_duplicates.to_excel(output_file, index=False)
print(f"✅ Created: {output_file}")
print(f"   - Has Unnamed: 0 column")
print(f"   - Has duplicate 'OwnerQatariID' columns")
print(f"   - Has duplicate 'OwnerName' columns")
print(f"   - Has duplicate 'AwardAmount' columns")

# Test Case 2: Normal file without issues (for comparison)
data2 = {
    'Season': ['2024', '2024', '2024'],
    'Race': ['RaceA', 'RaceB', 'RaceC'],
    'OwnerQatariID': ['44444', '55555', '66666'],
    'OwnerName': ['Owner D', 'Owner E', 'Owner F'],
    'AwardAmount': [4000, 5000, 6000],
}
df2 = pd.DataFrame(data2)
output_file2 = 'd:/Data_Analest/test_file_clean.xlsx'
df2.to_excel(output_file2, index=False)
print(f"\n✅ Created: {output_file2}")
print(f"   - No duplicate columns")
print(f"   - No Unnamed columns")

print("\n🔧 Test Instructions:")
print("1. Open Streamlit app at http://localhost:8505")
print("2. Navigate to 'تحليل جوائز سباقات الهجن' page")
print("3. Upload both test files:")
print(f"   - {output_file}")
print(f"   - {output_file2}")
print("4. Check for warnings about duplicate columns")
print("5. Verify that no PyArrow errors occur")
print("6. Confirm that 'OwnerQatariID', 'OwnerName', 'AwardAmount' are all protected (4/4 fields)")
