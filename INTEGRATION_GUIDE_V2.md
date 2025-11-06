# دليل الدمج - المحمّل الجديد v2.0

## 📋 الملفات المضافة

### 1. `core/data_loader_v2.py`
المحمّل الجديد للبيانات مع جميع الإصلاحات:
- ✅ توحيد أسماء الأعمدة (Entry Date ↔ EntryDate)
- ✅ إزالة أعمدة Unnamed تلقائياً
- ✅ اكتشاف صف الهيدر في ملفات البنك
- ✅ تنظيف المبالغ والتواريخ
- ✅ دعم Polars و Pandas

### 2. `test_new_loader.py`
ملف اختبار شامل للمحمّل الجديد

### 3. `diagnose_data.py` (محدّث)
تم إصلاح مشكلة `use_container_width` → `width='stretch'`

---

## 🚀 طريقة الاستخدام

### الطريقة 1: استخدام مباشر (موصى به)

```python
from core.data_loader_v2 import read_awards_excel_pandas, read_bank_excel_pandas

# قراءة ملفات الجوائز
awards_df = read_awards_excel_pandas("awards.xlsx")
print(f"✅ {len(awards_df)} سجل جوائز")
print(f"✅ الأعمدة: {', '.join(awards_df.columns[:5])}")

# قراءة كشف البنك
bank_df = read_bank_excel_pandas("bank.xlsx")
print(f"✅ {len(bank_df)} سجل بنكي")
```

### الطريقة 2: دمج مع الكود الحالي

#### تحديث `core/camel_awards_analyzer.py`:

```python
# في بداية الملف (بعد الـ imports):
try:
    from core.data_loader_v2 import read_awards_excel_pandas, read_bank_excel_pandas
    USE_NEW_LOADER = True
except ImportError:
    USE_NEW_LOADER = False
    print("⚠️ المحمّل الجديد غير متوفر، استخدام الطريقة القديمة")

# في دالة load_awards_files:
def load_awards_files(self, files):
    if USE_NEW_LOADER:
        # استخدام المحمّل الجديد
        dfs = []
        for file in files:
            try:
                df = read_awards_excel_pandas(file)
                dfs.append(df)
                print(f"✅ تم تحميل {len(df)} سجل من {Path(file).name}")
            except Exception as e:
                print(f"❌ خطأ في {file}: {e}")
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    else:
        # الطريقة القديمة (الكود الحالي)
        ...

# في دالة load_bank_statement:
def load_bank_statement(self, file):
    if USE_NEW_LOADER:
        try:
            df = read_bank_excel_pandas(file)
            print(f"✅ تم تحميل {len(df)} سجل بنكي")
            return df
        except Exception as e:
            print(f"❌ خطأ في تحميل كشف البنك: {e}")
            return pd.DataFrame()
    else:
        # الطريقة القديمة (الكود الحالي)
        ...
```

---

## 🔧 التثبيت

### المتطلبات الإضافية:

```bash
pip install polars openpyxl
```

### أو أضف للـ `requirements.txt`:

```
polars>=0.20.0
openpyxl>=3.1.0
```

---

## ✅ الاختبار

### 1. اختبار المحمّل فقط:

```bash
python test_new_loader.py
```

### 2. اختبار مع التطبيق الكامل:

```bash
streamlit run main_app.py
```

---

## 🔍 المشاكل المحلولة

### قبل:
- ❌ أعمدة Unnamed: 0, Unnamed: 1, ...
- ❌ "Entry Date" ≠ "EntryDate" (عدم تطابق)
- ❌ صف الهيدر في البنك غير صحيح
- ❌ المبالغ بها رموز (QAR, $, etc.)
- ❌ 0 مطابقات من 66,709 سجل

### بعد:
- ✅ إزالة Unnamed تلقائياً
- ✅ توحيد جميع الصيغ: "Entry Date", "entry date", "EntryDate" → `EntryDate`
- ✅ اكتشاف صف الهيدر تلقائياً (يبحث في أول 20 صف)
- ✅ تنظيف المبالغ: "QAR 1,500.00" → `1500.00`
- ✅ متوقع: آلاف المطابقات ✨

---

## 📊 خرائط الأعمدة المدعومة

### ملفات الجوائز (40+ تنويعة):

| الصيغ القديمة | الصيغة الموحدة |
|---------------|-----------------|
| Entry Date, entry date, entrydate | `EntryDate` |
| Owner Name, owner name, ownername | `OwnerName` |
| Award Amount, award amount, awardamount | `AwardAmount` |
| Payment Refrence, Payment Reference, paymentreference | `PaymentReference` |
| Trainer Name, trainer name, trainername | `TrainerName` |
| Owner Qatari ID, owner qatariid, ownerqatariid | `OwnerQatariId` |
| ... و 30+ تنويعة أخرى |  |

### كشف البنك:

| الصيغ المحتملة | الصيغة الموحدة |
|----------------|-----------------|
| Payment Reference, BankReference, paymentrefrence | `BankReference` |
| Beneficiary Name, BeneficiaryNameEn | `BeneficiaryName` |
| Transfer Amount, TransferAmount, Amount | `TransferAmount` |
| Transfer Date, TransferDate, Date | `TransferDate` |
| IBAN, IbanNumber, iban | `IBAN` |
| Currency, CurrencyCode | `CurrencyCode` |

---

## 🎯 التكامل مع UI

### تحديث Streamlit (تم ✅):

```python
# القديم (deprecated):
st.dataframe(df, use_container_width=True)

# الجديد:
st.dataframe(df, width='stretch')
```

تم التطبيق في:
- ✅ `diagnose_data.py` (5 مواضع)

---

## 📝 ملاحظات مهمة

### 1. التوافق العكسي:
- المحمّل الجديد يعمل جنباً إلى جنب مع القديم
- إذا فشل التثبيت، يعود للطريقة القديمة تلقائياً

### 2. الأداء:
- Polars أسرع 5-10× من Pandas للملفات الكبيرة
- يتم التحويل لـ Pandas في النهاية للتوافق

### 3. اللغة العربية:
- جميع الرسائل بالعربية
- دعم كامل للأعمدة العربية (اسم المالك، المبلغ، etc.)

---

## 🐛 استكشاف الأخطاء

### المشكلة: `ModuleNotFoundError: No module named 'polars'`

**الحل:**
```bash
pip install polars openpyxl
```

### المشكلة: لا يزال هناك 0 مطابقات

**التشخيص:**
```bash
python test_new_loader.py
```

سيعرض:
- ✅ عدد السجلات المقروءة
- ✅ الأعمدة الموجودة
- ✅ عينات من المراجع
- ✅ المطابقات المتوقعة

### المشكلة: `width parameter is deprecated`

**الحل:**
استبدل جميع:
- `use_container_width=True` → `width='stretch'`
- `use_container_width=False` → `width='content'`

تم التطبيق في `diagnose_data.py` ✅

---

## 📞 الدعم

إذا واجهت أي مشاكل:

1. شغّل `test_new_loader.py` للتشخيص
2. تحقق من أن Polars مثبت
3. تأكد من أن الملفات في مجلد `uploads/`
4. افحص سجلات الأخطاء (Console)

---

## ✨ الخطوات التالية

1. [ ] شغّل `test_new_loader.py`
2. [ ] تحقق من النتائج
3. [ ] دمج مع `camel_awards_analyzer.py`
4. [ ] اختبار مع البيانات الحقيقية
5. [ ] توثيق النتائج

---

**تاريخ الإصدار:** نوفمبر 6، 2025  
**الإصدار:** 2.0  
**الحالة:** جاهز للاستخدام ✅
