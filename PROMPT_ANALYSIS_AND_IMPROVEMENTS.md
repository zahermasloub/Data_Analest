# تحليل البرمبت الاحترافي وخطة التحسينات
## Professional Prompt Analysis & Implementation Plan

---

## 📋 القسم الأول: ما فهمته من البرمبت

### 1️⃣ **الهدف الرئيسي (Core Objective)**
نظام تدقيق متقدم ومتكامل يهدف إلى:
- **كشف التكرارات** في صرف جوائز سباقات الهجن عبر مواسم متعددة
- **مطابقة بنكية دقيقة** للتحقق من الصرف الفعلي
- **إنتاج تقارير احترافية** جاهزة للجهات التدقيقية والأمنية

---

### 2️⃣ **المفهوم الجوهري: المفتاح المركب (Composite Key)**

#### ✅ **المفتاح المركب للتكرار (6 حقول):**
```
Key = (Season + Race + Owner Number + Owner Name + Owner QatariId + Award Amount)
```

#### 🔑 **المنطق:**
- **تطابق تام** في الـ 6 حقول = **صرف مكرر**
- **Entry Date لا يدخل في المفتاح** - يُسمح باختلافه
- **هذا هو جوهر كشف التكرار**: نفس الشخص، نفس السباق، نفس الموسم، نفس المبلغ، ولكن صُرف مرتين في تواريخ مختلفة

#### ⚠️ **ملاحظة حاسمة:**
البرمبت يؤكد على:
- **NO fuzzy matching للأسماء** (تطابق تام بعد التطبيع الشكلي فقط)
- **Award Amount رقمي بعد التنظيف** (تقريب خانتين عشريتين)
- **تطبيع النصوص**: إزالة مسافات، توحيد الأحرف، لكن **بدون تغيير جوهري**

---

### 3️⃣ **توحيد البيانات (Data Normalization) - خطوة حاسمة**

#### 📌 **المشكلة:**
ملفات من مواسم مختلفة بأسماء أعمدة مختلفة:
- `Entry Date` vs `EntryDate`
- `Owner QatariId` vs `OwnerQatariID` vs `Owner Qatari Id`
- `PaymentRefrence` vs `PaymentReference` (لاحظ الخطأ الإملائي)

#### ✅ **الحل:**
خريطة توحيد شاملة (Column Mapping Dictionary):
```python
{
    'Entry Date': 'EntryDate',
    'Owner Number': 'OwnerNumber',
    'Owner QatariId': 'OwnerQatariID',
    'Owner Qatari Id': 'OwnerQatariID',
    'PaymentRefrence': 'PaymentReference',  # Fix typo
    ...
}
```

#### ⚠️ **تحذير حاسم:**
- **حفظ الأرقام التعريفية كنص** (Owner QatariId)
- **منع التحويل للصيغة العلمية** (7.84E+14 ❌)
- **الحفاظ على الأصفار البادئة**

---

### 4️⃣ **المطابقة البنكية (Bank Matching)**

#### 🏦 **المفهوم:**
التحقق من أن الجائزة المكررة **تم صرفها فعلياً** من البنك

#### 🔗 **آلية المطابقة:**

**من جهة الجوائز:**
- `PaymentRefrence` (المرجع الرئيسي)
- `PaymentRefrence_D1` / `D2` / `D3` (مراجع الوكلاء)

**من جهة البنك:**
- `Award Ref` (المرجع الكامل)
- `Award Ref 10 Digits` (آخر 10 أرقام)

#### 📊 **قواعد المطابقة:**
1. **تنظيف موحد**: إزالة مسافات، رموز، فواصل
2. **مطابقة مباشرة**: إذا تساوى النص بعد التنظيف
3. **مطابقة مرنة**: آخر 10 أرقام (REF_LAST_DIGITS = 10)

#### 🎯 **التصنيف:**
- ✅ **Matched**: مطابقة مؤكدة 100%
- ⚠️ **Partial/Suspected**: تطابق جزئي أو تعارض
- ❌ **Unmatched**: لا يوجد مرجع مطابق

#### 🔍 **فحوص إضافية (إن توفرت):**
- **المبلغ**: `Award Amount` = `TransferAmount` (±0.00 افتراضياً)
- **التاريخ**: `Entry Date` و `TransferDate` ضمن ±14 يوم
- **العملة**: استخدام `Transfer Rate` إن اختلفت

---

### 5️⃣ **المخرجات المطلوبة (Deliverables)**

#### 📄 **ملف 1: Awards_Duplicates_[timestamp].xlsx**
```
Sheet 1: Duplicates_AllRows
  - كل الصفوف المكررة بالكامل
  - إبراز PaymentRefrence وجميع المراجع الفرعية
  - GroupID + KeyCount

Sheet 2: Duplicates_Summary
  - تجميع حسب المفتاح المركب
  - عدد السجلات + إجمالي المبالغ
  - أول/آخر Entry Date

Sheet 3: Data_Dictionary
  - خريطة توحيد الأسماء (من → إلى)
```

#### 📄 **ملف 2: Bank_Match_Verification_[timestamp].xlsx**
```
Sheet 1: Bank_Matches
  - كل مجموعة مكررة ثبت لها تحويل بنكي
  - تفاصيل المطابقة الكاملة

Sheet 2: Bank_PartialOrSuspected
  - حالات جزئية/مشتبهة مع السبب

Sheet 3: Bank_Unmatched
  - مجموعات مكررة بدون تحويل مطابق

Sheet 4: Notes
  - الافتراضات + الإعدادات + المشكلات
```

---

### 6️⃣ **Ground Truth Cases - 28 حالة إلزامية**

#### ⚠️ **الهدف:**
التحقق من أن النظام يكتشف جميع الحالات المعروفة مسبقاً:

```
821B291050 & 821B291373
821B731113 & 822B731638
821B731181 & 822B731655
...
(28 زوج/مجموعة محددة)
```

#### 📌 **ملاحظة:**
- بعضها عبر سنوات مختلفة
- بتواريخ صرف متباعدة
- **المفتاح المركب هو الفيصل** وليس التاريخ

---

## 🔧 القسم الثاني: تحليل الوضع الحالي

### ✅ **ما هو موجود ومكتمل:**

1. **StrictAuditAnalyzer** في `core/strict_audit_analyzer.py`:
   - ✅ كشف التكرارات بالمفتاح المركب
   - ✅ التحقق من البنك الصارم
   - ✅ توليد التقارير

2. **run_strict_audit.py**:
   - ✅ تحميل ملفات الجوائز
   - ✅ كشف التكرارات
   - ✅ التحقق البنكي
   - ✅ إنشاء تقارير Excel

3. **الإعدادات الصارمة**:
   - ✅ `AMOUNT_TOLERANCE = 0.00` (تطابق تام)
   - ✅ المفتاح المركب: 6 حقول

---

### ⚠️ **الفجوات المحددة في الكود الحالي:**

#### 1. **توحيد الأعمدة غير شامل**
❌ **المشكلة:**
- لا توجد خريطة توحيد شاملة للأسماء
- لا يتعامل مع `PaymentRefrence` vs `PaymentReference`
- لا يتعامل مع `PaymentRefrence_D1/D2/D3`

✅ **الحل المطلوب:**
```python
COLUMN_MAPPING = {
    'Entry Date': 'EntryDate',
    'Owner Number': 'OwnerNumber',
    'Owner QatariId': 'OwnerQatariID',
    'Owner Qatari Id': 'OwnerQatariID',
    'Award Amount': 'AwardAmount',
    'PaymentRefrence': 'PaymentReference',
    'DelegatePaymentReference': 'PaymentReference_D1',
    ...
}
```

#### 2. **منع فساد الأرقام التعريفية غير مطبق**
❌ **المشكلة:**
- عند قراءة Excel، قد تتحول الهويات القطرية لصيغة علمية
- يمكن فقدان الأصفار البادئة

✅ **الحل المطلوب:**
```python
# عند قراءة Excel
dtype_dict = {
    'OwnerQatariId': str,
    'OwnerNumber': str,
    'TrainerQatariId': str
}
df = pd.read_excel(file, dtype=dtype_dict)
```

#### 3. **اكتشاف ترويسة البنك التلقائي غير مكتمل**
⚠️ **المشكلة:**
- الكود الحالي يفحص أول 20 صف
- لكن لا يوثق محاولة الاكتشاف بشكل كامل

✅ **الحل المطلوب:**
- توثيق الصفوف المفحوصة
- اقتراح المعالجة إذا فشل الاكتشاف

#### 4. **مطابقة مراجع الوكلاء غير مكتملة**
❌ **المشكلة:**
- الكود الحالي يطابق `PaymentReference` فقط
- لا يطابق `PaymentReference_D1/D2/D3`

✅ **الحل المطلوب:**
```python
# يجب جمع كل المراجع
award_refs = []
for field in ['PaymentReference', 'PaymentReference_D1', 
              'PaymentReference_D2', 'PaymentReference_D3']:
    if field in row and pd.notna(row[field]):
        award_refs.append(str(row[field]))
```

#### 5. **Ground Truth Validation مفقودة**
❌ **المشكلة:**
- لا يوجد فحص تلقائي للحالات الـ 28 المعروفة
- لا تقرير بأي حالات مفقودة

✅ **الحل المطلوب:**
```python
GROUND_TRUTH_CASES = [
    ('821B291050', '821B291373'),
    ('821B731113', '822B731638'),
    ...
]

def validate_ground_truth(duplicates, ground_truth):
    """التحقق من اكتشاف جميع الحالات المعروفة"""
    missing_cases = []
    for pair in ground_truth:
        # تحقق من وجود كلا المرجعين في التكرارات
        ...
    return missing_cases
```

#### 6. **ملف Data Dictionary مفقود**
❌ **المشكلة:**
- لا يتم إنشاء Sheet `Data_Dictionary` في التقرير
- لا توثيق للتوحيد المطبق

✅ **الحل المطلوب:**
```python
# في generate_strict_reports
mapping_df = pd.DataFrame([
    {'Original': 'Entry Date', 'Unified': 'EntryDate', 'Notes': 'توحيد التاريخ'},
    {'Original': 'Owner Qatari Id', 'Unified': 'OwnerQatariID', 'Notes': 'رقم الهوية'},
    ...
])
mapping_df.to_excel(writer, sheet_name='Data_Dictionary', index=False)
```

#### 7. **ملف Bank_PartialOrSuspected مفقود**
❌ **المشكلة:**
- التصنيف الحالي: Matched أو Unmatched فقط
- لا توجد فئة `Partial/Suspected`

✅ **الحل المطلوب:**
- إضافة منطق للحالات الجزئية:
  - مرجع موجود بالبنك لكن مبلغ مختلف
  - مبلغ مطابق لكن مرجع غير واضح
  - تواريخ متعارضة

#### 8. **Notes Sheet غير مكتمل**
❌ **المشكلة:**
- لا يتم توثيق:
  - الافتراضات المستخدمة
  - مشكلات التنظيف
  - الإعدادات القابلة للتعديل

✅ **الحل المطلوب:**
```python
notes_data = {
    'Category': ['Settings', 'Settings', 'Data Quality', ...],
    'Item': ['DATE_WINDOW_DAYS', 'AMOUNT_TOLERANCE', 'Missing Values', ...],
    'Value': ['14', '0.00', 'X rows removed', ...]
}
```

#### 9. **تحويل العملات غير مطبق**
⚠️ **المشكلة:**
- لا يتعامل مع `Transfer Rate` عند اختلاف العملات
- لا توثيق لهذا القيد

✅ **الحل المطلوب:**
- فحص وجود `CurrencyCode` في البنك
- استخدام `TransferRate` إن وُجد
- توثيق أي اختلاف غير قابل للمعالجة

---

## 🚀 القسم الثالث: خطة التحسينات

### 📦 **التحسين 1: إنشاء DataNormalizer Class**

**الغرض:** توحيد البيانات بشكل احترافي قبل أي معالجة

```python
class DataNormalizer:
    """محوّل البيانات الموحد - Data Normalization Engine"""
    
    COLUMN_MAPPING = {
        'Entry Date': 'EntryDate',
        'Owner Number': 'OwnerNumber',
        'Owner Name': 'OwnerName',
        'Owner QatariId': 'OwnerQatariID',
        'Owner Qatari Id': 'OwnerQatariID',
        'OwnerQatariId': 'OwnerQatariID',
        'Award Amount': 'AwardAmount',
        'AwardAmount': 'AwardAmount',
        'Payment Method': 'PaymentMethod',
        'PaymentType': 'PaymentMethod',
        'PaymentRefrence': 'PaymentReference',  # Fix typo
        'PaymentReference': 'PaymentReference',
        'DelegatePaymentReference': 'PaymentReference_D1',
        'SecondDelegatePaymentReference': 'PaymentReference_D2',
        'ThirdDelegatePaymentReference': 'PaymentReference_D3',
        'PaymentRefrence_D1': 'PaymentReference_D1',
        'PaymentRefrence_D2': 'PaymentReference_D2',
        'PaymentRefrence_D3': 'PaymentReference_D3',
        'Beneficiary English Name': 'BeneficiaryNameEn',
        'BeneficiaryEnglishName': 'BeneficiaryNameEn',
        'IBAN': 'IbanNumber',
        'Iban': 'IbanNumber',
        'Transfer Rate': 'TransferRate',
    }
    
    ID_FIELDS = [
        'OwnerQatariID', 'TrainerQatariId', 'OwnerNumber'
    ]
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """توحيد أسماء الأعمدة وحماية الأرقام التعريفية"""
        df = df.copy()
        
        # 1. حذف أعمدة Unnamed
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # 2. تنظيف أسماء الأعمدة
        df.columns = df.columns.str.strip()
        
        # 3. توحيد الأسماء
        df = df.rename(columns=self.COLUMN_MAPPING)
        
        # 4. حماية الحقول الرقمية
        for field in self.ID_FIELDS:
            if field in df.columns:
                df[field] = df[field].astype(str).str.strip()
        
        return df
    
    def get_mapping_documentation(self) -> pd.DataFrame:
        """توثيق التوحيد المطبق"""
        mappings = []
        for original, unified in self.COLUMN_MAPPING.items():
            mappings.append({
                'Original_Name': original,
                'Unified_Name': unified,
                'Type': 'Column Mapping'
            })
        return pd.DataFrame(mappings)
```

---

### 📦 **التحسين 2: تحسين BankMatcher**

**الغرض:** مطابقة بنكية شاملة مع دعم جميع المراجع

```python
class BankMatcher:
    """مطابق البنك المتقدم - Advanced Bank Matcher"""
    
    def __init__(self, ref_last_digits=10, amount_tolerance=0.00, date_window_days=14):
        self.ref_last_digits = ref_last_digits
        self.amount_tolerance = amount_tolerance
        self.date_window_days = date_window_days
    
    def extract_all_references(self, row: pd.Series) -> List[str]:
        """استخراج جميع المراجع من سجل الجائزة"""
        refs = []
        ref_fields = [
            'PaymentReference',
            'PaymentReference_D1',
            'PaymentReference_D2',
            'PaymentReference_D3'
        ]
        
        for field in ref_fields:
            if field in row and pd.notna(row[field]):
                ref = str(row[field]).strip()
                if ref and ref.lower() not in ['nan', 'none', '']:
                    refs.append(ref)
        
        return refs
    
    def match_award_to_bank(self, award_row, bank_df):
        """مطابقة سجل جائزة مع كشف البنك - شامل"""
        
        # 1. استخراج المراجع
        award_refs = self.extract_all_references(award_row)
        
        if not award_refs:
            return {
                'status': 'NO_REFERENCE',
                'reason': '❌ لا يوجد رقم مرجعي',
                'matched_bank_row': None
            }
        
        # 2. البحث في البنك
        for ref in award_refs:
            ref_clean = self.clean_reference(ref)
            
            # محاولة المطابقة
            bank_matches = self.find_bank_matches(ref_clean, bank_df)
            
            if len(bank_matches) > 0:
                # فحص المبلغ
                amount_match = self.verify_amount(
                    award_row['AwardAmount'],
                    bank_matches
                )
                
                if amount_match is not None:
                    # مطابقة كاملة
                    return {
                        'status': 'MATCHED_100',
                        'reason': '✅ مطابقة بنكية كاملة',
                        'matched_bank_row': amount_match,
                        'matched_reference': ref
                    }
                else:
                    # مرجع موجود لكن مبلغ مختلف
                    return {
                        'status': 'PARTIAL',
                        'reason': '⚠️ Ref مطابق - مبلغ مختلف',
                        'matched_bank_row': bank_matches.iloc[0],
                        'matched_reference': ref
                    }
        
        # 3. لم يتم العثور على مطابقة
        return {
            'status': 'UNMATCHED',
            'reason': '❌ Ref غير موجود بالبنك',
            'matched_bank_row': None,
            'attempted_refs': award_refs
        }
```

---

### 📦 **التحسين 3: GroundTruthValidator**

**الغرض:** التحقق من اكتشاف جميع الحالات المعروفة

```python
class GroundTruthValidator:
    """مدقق الحالات المعروفة - Ground Truth Validator"""
    
    KNOWN_DUPLICATE_PAIRS = [
        ('821B291050', '821B291373'),
        ('821B731113', '822B731638'),
        ('821B731181', '822B731655'),
        ('821B780256', '821B780936'),
        ('821B780108', '822B780961'),
        ('822B860645', '822B861016', '822B861020'),  # Triple
        ('822B870766', '822B871164'),
        ('822C161124', '824C161706'),
        ('822C160320', '824C161708'),
        ('822C160718', '824C161711'),
        ('822C160760', '822C161657'),
        ('822C220292', '823C220693'),
        ('822C340338', '823C341078'),
        ('823C360755', '823C361534'),
        ('823C360159', '823C361544'),
        ('823C360796', '823C361529'),
        ('822C340243', '823C341104', '823C341106'),  # Triple
        ('824D101013', '824D101473'),
        ('823C360031', '824C361546', '823C361516'),  # Triple
        ('820B150249', '823B150327'),
    ]
    
    def validate_detection(self, duplicates_df: pd.DataFrame) -> Dict:
        """التحقق من اكتشاف جميع الحالات"""
        
        results = {
            'total_cases': len(self.KNOWN_DUPLICATE_PAIRS),
            'detected': [],
            'missing': [],
            'detection_rate': 0.0
        }
        
        for case in self.KNOWN_DUPLICATE_PAIRS:
            detected = self.check_case_detected(case, duplicates_df)
            
            if detected:
                results['detected'].append({
                    'refs': case,
                    'status': '✅ مكتشف'
                })
            else:
                results['missing'].append({
                    'refs': case,
                    'status': '❌ مفقود'
                })
        
        results['detection_rate'] = len(results['detected']) / results['total_cases'] * 100
        
        return results
    
    def check_case_detected(self, case_refs: tuple, duplicates_df: pd.DataFrame) -> bool:
        """التحقق من اكتشاف حالة محددة"""
        # البحث في أعمدة المراجع
        ref_columns = ['PaymentReference', 'PaymentReference_D1', 
                      'PaymentReference_D2', 'PaymentReference_D3']
        
        found_refs = []
        for ref in case_refs:
            for col in ref_columns:
                if col in duplicates_df.columns:
                    matches = duplicates_df[
                        duplicates_df[col].astype(str).str.contains(ref, na=False, case=False)
                    ]
                    if len(matches) > 0:
                        found_refs.append(ref)
                        break
        
        # يجب إيجاد جميع المراجع في الحالة
        return len(found_refs) == len(case_refs)
```

---

### 📦 **التحسين 4: تحسين ReportGenerator**

**الغرض:** تقارير شاملة مع جميع الصفحات المطلوبة

```python
def generate_comprehensive_reports(self):
    """إنشاء تقارير شاملة حسب متطلبات البرمبت"""
    
    # Report 1: Awards_Duplicates_[timestamp].xlsx
    duplicates_file = self.generate_duplicates_report()
    
    # Report 2: Bank_Match_Verification_[timestamp].xlsx
    bank_file = self.generate_bank_verification_report()
    
    # Report 3: Ground_Truth_Validation_[timestamp].xlsx
    validation_file = self.generate_ground_truth_report()
    
    return {
        'duplicates': duplicates_file,
        'bank_verification': bank_file,
        'ground_truth': validation_file
    }

def generate_duplicates_report(self):
    """تقرير التكرارات الشامل"""
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Sheet 1: Duplicates_AllRows
        self.duplicates.to_excel(writer, sheet_name='Duplicates_AllRows', index=False)
        
        # Sheet 2: Duplicates_Summary
        summary = self.create_duplicates_summary()
        summary.to_excel(writer, sheet_name='Duplicates_Summary', index=False)
        
        # Sheet 3: Data_Dictionary
        dictionary = self.normalizer.get_mapping_documentation()
        dictionary.to_excel(writer, sheet_name='Data_Dictionary', index=False)

def generate_bank_verification_report(self):
    """تقرير التحقق البنكي الشامل"""
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Sheet 1: Bank_Matches (100%)
        self.matched_df.to_excel(writer, sheet_name='Bank_Matches', index=False)
        
        # Sheet 2: Bank_PartialOrSuspected
        self.partial_df.to_excel(writer, sheet_name='Bank_PartialOrSuspected', index=False)
        
        # Sheet 3: Bank_Unmatched
        self.unmatched_df.to_excel(writer, sheet_name='Bank_Unmatched', index=False)
        
        # Sheet 4: Notes
        notes = self.generate_notes_documentation()
        notes.to_excel(writer, sheet_name='Notes', index=False)
```

---

## 📊 القسم الرابع: التطبيق العملي

### الفوائد المستقبلية:
1. **قابلية إعادة الاستخدام**: يمكن تطبيق نفس المنطق على:
   - ملفات موارد بشرية (HR)
   - بيانات مصرفية أخرى
   - أي بيانات تحتاج كشف تكرار

2. **مرونة التكوين**:
```python
config = {
    'composite_key': ['Field1', 'Field2', 'Field3'],
    'amount_tolerance': 0.00,
    'date_window': 14,
    'ref_last_digits': 10
}
```

3. **توثيق ذاتي**: كل عملية موثقة في:
   - Data Dictionary
   - Notes Sheet
   - Validation Reports

4. **قابلية التدقيق**: تقارير جاهزة للجهات الرقابية

---

## ✅ الخلاصة

### ما يميز البرمبت:
1. ✅ **دقة عالية**: معايير 100% بدون تسامح
2. ✅ **شمولية**: يغطي جميع جوانب التدقيق
3. ✅ **توثيق كامل**: كل عملية موثقة
4. ✅ **قابلية تدقيق**: Ground Truth Validation
5. ✅ **مرونة**: إعدادات قابلة للتعديل

### ما ينقص النظام الحالي:
1. ⚠️ **توحيد البيانات**: غير شامل
2. ⚠️ **حماية الأرقام**: غير مطبقة بشكل كامل
3. ⚠️ **مطابقة المراجع**: D1/D2/D3 غير مدعومة
4. ⚠️ **Ground Truth**: غير مطبقة
5. ⚠️ **التقارير**: ناقصة (Data Dictionary, Partial, Notes)

### الخطوة التالية:
تطبيق التحسينات المقترحة في ملف محدث جديد.

---

**📌 ملاحظة نهائية:**
البرمبت احترافي جداً ويعكس فهماً عميقاً لمتطلبات التدقيق. التحسينات المقترحة ستجعل النظام:
- ✅ متوافق 100% مع البرمبت
- ✅ قابل لإعادة الاستخدام
- ✅ موثوق للجهات الرقابية
- ✅ مرن للتطبيقات المستقبلية
