import pandas as pd

# قراءة ملف البنك مباشرة بدون normalization
df = pd.read_excel('الملفات/ملف البنك.xlsx', header=5)

print("Original columns from row 5:")
for i, col in enumerate(df.columns):
    print(f"  {i}: '{col}'")
    
print(f"\nTotal columns: {len(df.columns)}")
print(f"Total rows: {len(df)}")
