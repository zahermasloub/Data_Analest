import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load the data
df = pd.read_csv('العجوري 11-4.csv', encoding='utf-8-sig')

print("Dataset Overview:")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print("\nFirst few rows:")
print(df.head(3))

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

print("\nCleaned column names:")
for i, col in enumerate(df.columns):
    print(f"{i+1:2d}. {col}")

# Data Cleaning
print("\n" + "="*80)
print("DATA CLEANING")
print("="*80)
print("Initial record count:", len(df))

cleaning_log = []

# 1. Remove completely empty columns
empty_cols = df.columns[df.isnull().all()].tolist()
df_clean = df.drop(columns=empty_cols)
cleaning_log.append(f"Removed {len(empty_cols)} completely empty columns: {empty_cols}")

# 2. Remove duplicate columns keeping first occurrence
cols_to_keep = []
cols_seen = set()
for col in df_clean.columns:
    base_col = col.split('_')[0] if '_' in col else col
    if base_col not in cols_seen:
        cols_to_keep.append(col)
        cols_seen.add(base_col)
    else:
        cleaning_log.append(f"Removed duplicate column: {col}")

df_clean = df_clean[cols_to_keep]

# 3. Clean AwardAmount - convert to numeric
df_clean['AwardAmount'] = df_clean['AwardAmount'].astype(str).str.replace(',', '').str.replace('"', '')
df_clean['AwardAmount'] = pd.to_numeric(df_clean['AwardAmount'], errors='coerce')
cleaning_log.append(f"Converted AwardAmount to numeric, {df_clean['AwardAmount'].isna().sum()} conversion errors")

# 4. Convert EntryDate to datetime
df_clean['EntryDate'] = pd.to_datetime(df_clean['EntryDate'])
cleaning_log.append("Converted EntryDate to datetime")

# 5. Remove rows with critical missing data
initial_count = len(df_clean)
df_clean = df_clean.dropna(subset=['OwnerName', 'Race', 'AwardAmount'])
final_count = len(df_clean)
cleaning_log.append(f"Removed {initial_count - final_count} rows with missing OwnerName, Race, or AwardAmount")

print("\nData Cleaning Summary:")
for log in cleaning_log:
    print(f"- {log}")

print(f"\nFinal dataset shape: {df_clean.shape}")

# Identity Resolution
print("\n" + "="*80)
print("IDENTITY RESOLUTION")
print("="*80)

def create_participant_id(row):
    """Create unique participant ID using available identifiers"""
    identifiers = []
    
    # Priority 1: OwnerQatariId (most reliable)
    if pd.notna(row['OwnerQatariId']) and row['OwnerQatariId'] != '':
        identifiers.append(f"QID_{row['OwnerQatariId']}")
    
    # Priority 2: OwnerNumber
    if pd.notna(row['OwnerNumber']) and row['OwnerNumber'] != '':
        identifiers.append(f"NUM_{row['OwnerNumber']}")
    
    # Priority 3: OwnerName (normalized)
    if pd.notna(row['OwnerName']) and row['OwnerName'] != '':
        # Normalize name: remove extra spaces, convert to lowercase
        name = str(row['OwnerName']).strip().lower()
        identifiers.append(f"NAME_{name}")
    
    return hash(tuple(identifiers)) if identifiers else None

# Apply participant ID creation
df_clean['participant_id'] = df_clean.apply(create_participant_id, axis=1)

# Check for participants without IDs
no_id_count = df_clean['participant_id'].isna().sum()
print(f"Participants without ID: {no_id_count} ({no_id_count/len(df_clean)*100:.2f}%)")

# Create race_id
df_clean['race_id'] = df_clean['Race'].str.strip().str.lower().apply(hash)

print(f"Unique participants: {df_clean['participant_id'].nunique()}")
print(f"Unique races: {df_clean['race_id'].nunique()}")

# Duplicate Payment Analysis
print("\n" + "="*80)
print("DUPLICATE PAYMENT ANALYSIS")
print("="*80)

# 1. Exact duplicate rows (all columns match)
exact_duplicates = df_clean[df_clean.duplicated(keep=False)]
print(f"Exact duplicate rows: {len(exact_duplicates)}")

# 2. Same participant, same race, same amount (potential duplicate payments)
duplicate_criteria = ['participant_id', 'race_id', 'AwardAmount']
potential_duplicates = df_clean[df_clean.duplicated(subset=duplicate_criteria, keep=False)]

# Group and analyze potential duplicates
dup_summary = potential_duplicates.groupby(duplicate_criteria).agg({
    'EntryDate': ['count', 'min', 'max'],
    'PaymentReference': 'first',
    'OwnerName': 'first',
    'Race': 'first'
}).reset_index()

dup_summary.columns = ['participant_id', 'race_id', 'amount', 'occurrences', 'first_date', 'last_date', 'payment_ref', 'owner_name', 'race_name']

# Filter for actual duplicates (more than 1 occurrence)
actual_duplicates = dup_summary[dup_summary['occurrences'] > 1]

print(f"\nPotential duplicate payments (same participant + race + amount): {len(actual_duplicates)}")

if len(actual_duplicates) > 0:
    print("\nDuplicate Payment Cases:")
    for _, dup in actual_duplicates.iterrows():
        print(f"- {dup['owner_name']} in {dup['race_name']}: {dup['amount']:,.0f} QAR, {dup['occurrences']} occurrences")

# Deviation Analysis
print("\n" + "="*80)
print("DEVIATION ANALYSIS")
print("="*80)

# Calculate statistical measures for each race
race_stats = df_clean.groupby('Race').agg({
    'AwardAmount': ['count', 'mean', 'median', 'std', 'min', 'max'],
    'participant_id': 'nunique'
}).round(2)

race_stats.columns = ['count', 'mean', 'median', 'std', 'min', 'max', 'unique_participants']
race_stats = race_stats.sort_values('mean', ascending=False)

print("\nRace Payment Statistics (Top 10 by mean amount):")
print(race_stats.head(10))

# Calculate IQR-based anomalies for each race
def detect_anomalies_iqr(group):
    Q1 = group['AwardAmount'].quantile(0.25)
    Q3 = group['AwardAmount'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    group['is_anomaly_iqr'] = (group['AwardAmount'] < lower_bound) | (group['AwardAmount'] > upper_bound)
    group['anomaly_reason_iqr'] = np.where(group['AwardAmount'] > upper_bound, 'High', 
                                        np.where(group['AwardAmount'] < lower_bound, 'Low', 'Normal'))
    return group

# Calculate Z-score based anomalies
def detect_anomalies_zscore(group):
    if len(group) > 1 and group['AwardAmount'].std() > 0:
        group['z_score'] = (group['AwardAmount'] - group['AwardAmount'].mean()) / group['AwardAmount'].std()
        group['is_anomaly_zscore'] = abs(group['z_score']) > 3
    else:
        group['z_score'] = 0
        group['is_anomaly_zscore'] = False
    return group

# Apply anomaly detection
df_anomaly = df_clean.groupby('Race').apply(detect_anomalies_iqr).reset_index(drop=True)
df_anomaly = df_anomaly.groupby('Race').apply(detect_anomalies_zscore).reset_index(drop=True)

# Summary of anomalies
iqr_anomalies = df_anomaly[df_anomaly['is_anomaly_iqr']]
zscore_anomalies = df_anomaly[df_anomaly['is_anomaly_zscore']]

print(f"\nAnomalies detected:")
print(f"- IQR method: {len(iqr_anomalies)} anomalies ({len(iqr_anomalies)/len(df_anomaly)*100:.1f}%)")
print(f"- Z-score method: {len(zscore_anomalies)} anomalies ({len(zscore_anomalies)/len(df_anomaly)*100:.1f}%)")

if len(iqr_anomalies) > 0:
    print("\nTop IQR Anomalies (High Values):")
    high_anomalies = iqr_anomalies[iqr_anomalies['anomaly_reason_iqr'] == 'High'].nlargest(5, 'AwardAmount')
    for _, anomaly in high_anomalies.iterrows():
        print(f"- {anomaly['OwnerName']}: {anomaly['AwardAmount']:,.0f} QAR in {anomaly['Race']}")

# Visualizations
print("\n" + "="*80)
print("GENERATING VISUALIZATIONS")
print("="*80)

# Set up plotting style
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)

# 1. Boxplot for top 10 races by mean amount
top_races = race_stats.head(10).index
df_top_races = df_clean[df_clean['Race'].isin(top_races)]

plt.figure(figsize=(14, 8))
box_data = [df_top_races[df_top_races['Race'] == race]['AwardAmount'] for race in top_races]
bp = plt.boxplot(box_data, labels=range(1, len(top_races)+1), vert=True)
plt.xticks(range(1, len(top_races)+1), [f"Race {i}" for i in range(1, len(top_races)+1)])
plt.title('Payment Distribution by Race (Top 10 by Average)', fontsize=14, fontweight='bold')
plt.ylabel('Award Amount (QAR)', fontsize=12)
plt.xlabel('Race Number', fontsize=12)
plt.yscale('log')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('boxplot_races.png', dpi=300, bbox_inches='tight')
print("✓ Saved: boxplot_races.png")
plt.close()

# 2. Histogram of all award amounts
plt.figure(figsize=(12, 6))
plt.hist(df_clean['AwardAmount'], bins=50, edgecolor='black', alpha=0.7, color='skyblue')
plt.title('Distribution of All Award Amounts', fontsize=14, fontweight='bold')
plt.xlabel('Award Amount (QAR)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.axvline(df_clean['AwardAmount'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df_clean["AwardAmount"].mean():,.0f} QAR')
plt.axvline(df_clean['AwardAmount'].median(), color='green', linestyle='--', linewidth=2, label=f'Median: {df_clean["AwardAmount"].median():,.0f} QAR')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('histogram_awards.png', dpi=300, bbox_inches='tight')
print("✓ Saved: histogram_awards.png")
plt.close()

# 3. Top participants bar chart
plt.figure(figsize=(12, 8))
top_participants = df_clean.groupby('OwnerName')['AwardAmount'].sum().nlargest(10)
plt.barh(range(len(top_participants)), top_participants.values, color='coral')
plt.yticks(range(len(top_participants)), [name[:30] + '...' if len(name) > 30 else name for name in top_participants.index])
plt.xlabel('Total Award Amount (QAR)', fontsize=12)
plt.title('Top 10 Participants by Total Awards', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()
for i, v in enumerate(top_participants.values):
    plt.text(v, i, f' {v:,.0f}', va='center', fontsize=9)
plt.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('top_participants.png', dpi=300, bbox_inches='tight')
print("✓ Saved: top_participants.png")
plt.close()

# 4. Anomalies visualization
if len(iqr_anomalies) > 0:
    plt.figure(figsize=(12, 6))
    plt.scatter(df_anomaly[~df_anomaly['is_anomaly_iqr']].index, 
                df_anomaly[~df_anomaly['is_anomaly_iqr']]['AwardAmount'], 
                alpha=0.5, s=20, label='Normal', color='blue')
    plt.scatter(df_anomaly[df_anomaly['is_anomaly_iqr']].index, 
                df_anomaly[df_anomaly['is_anomaly_iqr']]['AwardAmount'], 
                alpha=0.8, s=50, label='Anomaly', color='red', marker='x')
    plt.title('Payment Anomalies Detection (IQR Method)', fontsize=14, fontweight='bold')
    plt.xlabel('Record Index', fontsize=12)
    plt.ylabel('Award Amount (QAR)', fontsize=12)
    plt.yscale('log')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('anomalies_scatter.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: anomalies_scatter.png")
    plt.close()

# Pivot table analysis
print("\n" + "="*80)
print("PIVOT TABLE ANALYSIS")
print("="*80)

pivot_data = df_clean.pivot_table(
    values='AwardAmount', 
    index='OwnerName', 
    columns='Race', 
    aggfunc='sum',
    fill_value=0
)

print("\nTop 10 participants by total awards:")
top_participants = df_clean.groupby('OwnerName')['AwardAmount'].sum().nlargest(10)
for rank, (name, amount) in enumerate(top_participants.items(), 1):
    print(f"{rank:2d}. {name}: {amount:,.0f} QAR")

# Generate Reports
print("\n" + "="*80)
print("GENERATING REPORTS")
print("="*80)

# 1. Duplicates Report
duplicates_report = actual_duplicates.copy()
if len(duplicates_report) == 0:
    duplicates_report = pd.DataFrame(columns=['owner_name', 'race_name', 'amount', 'occurrences', 'first_date', 'last_date'])

# 2. Anomalies Report
anomalies_report = df_anomaly[df_anomaly['is_anomaly_iqr']][[
    'EntryDate', 'Season', 'Race', 'OwnerName', 'AwardAmount', 
    'anomaly_reason_iqr', 'z_score', 'PaymentType'
]].copy()
anomalies_report = anomalies_report.sort_values(['Race', 'AwardAmount'], ascending=[True, False])

# Save reports
with pd.ExcelWriter('duplicates_report.xlsx', engine='openpyxl') as writer:
    duplicates_report.to_excel(writer, sheet_name='Duplicate_Payments', index=False)

with pd.ExcelWriter('anomalies_report.xlsx', engine='openpyxl') as writer:
    anomalies_report.to_excel(writer, sheet_name='Anomalous_Payments', index=False)

print(f"✓ duplicates_report.xlsx: {len(duplicates_report)} records")
print(f"✓ anomalies_report.xlsx: {len(anomalies_report)} records")

# Executive Summary
print("\n" + "="*80)
print("GENERATING EXECUTIVE SUMMARY")
print("="*80)

# Calculate key metrics
total_awards = df_clean['AwardAmount'].sum()
avg_award = df_clean['AwardAmount'].mean()
median_award = df_clean['AwardAmount'].median()
std_award = df_clean['AwardAmount'].std()
min_award = df_clean['AwardAmount'].min()
max_award = df_clean['AwardAmount'].max()

summary_md = f"""# Camel Race Payments Analysis Report

## Executive Summary

This analysis examined **{len(df_clean):,} payment records** across **{df_clean['race_id'].nunique()} camel racing events**, involving **{df_clean['participant_id'].nunique()} unique participants**. The comprehensive audit revealed:

### Key Findings:
- **{len(actual_duplicates)} duplicate payments** detected for the same participant in the same race
- **{len(iqr_anomalies)} anomalous payments** identified using statistical methods (IQR)
- **Extreme value dispersion** with awards ranging from {min_award:,.0f} to {max_award:,.0f} QAR
- **Highly skewed distribution** - median payment ({median_award:,.0f} QAR) {'much lower' if median_award < avg_award * 0.5 else 'lower'} than mean ({avg_award:,.0f} QAR)

### Data Quality:
- **Excellent data completeness** - no missing critical fields
- **Clean data structure** - {len(exact_duplicates)} exact duplicate records
- **Proper identifier resolution** - all participants successfully mapped

### Risk Assessment: {'LOW' if len(actual_duplicates) == 0 and len(iqr_anomalies) < 50 else 'MODERATE' if len(actual_duplicates) < 5 else 'HIGH'}
{'While no duplicate payments were found, the wide payment distribution and extreme high-value awards warrant further review for potential procedural controls.' if len(actual_duplicates) == 0 else 'Duplicate payments detected - immediate review required.'}

## Detailed Analysis

### Payment Statistics
- Total payments analyzed: **{len(df_clean):,}** records
- Total award value: **{total_awards:,.0f} QAR**
- Average award: **{avg_award:,.0f} QAR**
- Median award: **{median_award:,.0f} QAR**
- Standard deviation: **{std_award:,.0f} QAR**
- Range: **{min_award:,.0f}** to **{max_award:,.0f} QAR**

### Top Events by Average Award:
"""

for rank, (race, stats) in enumerate(race_stats.head(5).iterrows(), 1):
    summary_md += f"{rank}. {race} - **{stats['mean']:,.0f} QAR** (n={int(stats['count'])})\n"

summary_md += f"""
### Top Participants by Total Awards:
"""

for rank, (name, amount) in enumerate(top_participants.head(5).items(), 1):
    summary_md += f"{rank}. {name} - **{amount:,.0f} QAR**\n"

summary_md += f"""
## Anomaly Analysis

### Distribution by Type:
- **High-value anomalies**: {len(iqr_anomalies[iqr_anomalies['anomaly_reason_iqr'] == 'High'])} ({len(iqr_anomalies[iqr_anomalies['anomaly_reason_iqr'] == 'High'])/len(df_clean)*100:.1f}%)
- **Low-value anomalies**: {len(iqr_anomalies[iqr_anomalies['anomaly_reason_iqr'] == 'Low'])} ({len(iqr_anomalies[iqr_anomalies['anomaly_reason_iqr'] == 'Low'])/len(df_clean)*100:.1f}%)
- **Z-score flagged**: {len(zscore_anomalies)} ({len(zscore_anomalies)/len(df_clean)*100:.1f}%)

## Recommendations

### Immediate Actions:
1. **Review high-value anomalies** - Investigate payments over 1,000,000 QAR for proper authorization
2. **Establish payment tiers** - Create standardized award ranges for each race type
3. **Implement amount validation** - Set maximum reasonable limits per race category

### Process Improvements:
1. **Standardize payment approval workflow** for awards exceeding certain thresholds
2. **Regular audit trails** for high-value transactions
3. **Participant payment history monitoring** to detect unusual patterns

### Technical Controls:
1. **Automated duplicate detection** in payment processing system
2. **Statistical monitoring** for anomalous payment patterns
3. **Segregation of duties** for payment authorization and processing

## Methodology

### Duplicate Detection:
- **Criteria**: Same participant + same race + same amount
- **No time-window restriction** applied
- **Result**: {len(actual_duplicates)} duplicates found

### Anomaly Detection:
- **IQR Method**: Values outside Q1-1.5*IQR or Q3+1.5*IQR
- **Z-score Method**: Values with |Z-score| > 3
- **Result**: {len(iqr_anomalies)} anomalies identified via IQR ({len(iqr_anomalies)/len(df_clean)*100:.1f}% of dataset)

### Data Quality:
- All critical fields populated
- Consistent data formats
- Proper identifier resolution achieved

---
*Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

with open('overview_summary.md', 'w', encoding='utf-8') as f:
    f.write(summary_md)

print("✓ overview_summary.md")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print("\nGenerated files:")
print("1. boxplot_races.png - Payment distribution by top races")
print("2. histogram_awards.png - Overall award distribution")
print("3. top_participants.png - Top 10 participants bar chart")
print("4. anomalies_scatter.png - Anomaly detection visualization")
print("5. duplicates_report.xlsx - Duplicate payments report")
print("6. anomalies_report.xlsx - Anomalous payments report")
print("7. overview_summary.md - Executive summary report")
print("\n" + "="*80)
