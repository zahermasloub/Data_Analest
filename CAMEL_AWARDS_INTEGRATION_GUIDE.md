# 🎯 دليل دمج المكونات المتقدمة - Camel Awards Analyzer
## Advanced Integration Guide

تم إنشاء **3 مكونات متقدمة** جديدة للمحلل. هذا الدليل يوضح كيفية دمجها مع الكود الحالي.

---

## 📦 المكونات الجديدة

### 1️⃣ **Advanced Matcher** - محرك المطابقة المتقدم
**الملف:** `core/advanced_matcher.py`

**المكتبات المستخدمة:**
- `pandas>=2.1.0` - معالجة البيانات
- `rapidfuzz>=3.5.0` - المطابقة الضبابية
- `recordlinkage>=0.16.0` - المطابقة المتقدمة
- `numpy>=1.24.0` - العمليات الرياضية

**المميزات:**
- ✅ **Exact Matching**: مطابقة حتمية (مبلغ + تاريخ)
- ✅ **Fuzzy Matching**: مطابقة ضبابية بالأسماء (rapidfuzz)
- ✅ **Record Linkage**: مطابقة متقدمة بالخوارزميات الاحتمالية
- ✅ **Multi-layer Processing**: معالجة طبقات متعددة تلقائياً

**الوظائف الرئيسية:**
```python
from core.advanced_matcher import AdvancedMatcher

matcher = AdvancedMatcher(fuzzy_threshold=90)

# الطريقة 1: مطابقة طبقة واحدة
exact_matches = matcher.exact_match(awards_df, bank_df, time_window_days=7)
fuzzy_matches = matcher.fuzzy_match(unmatched_awards, bank_df, time_window_days=7)
rl_matches = matcher.record_linkage_match(unmatched_awards, bank_df, time_window_days=7)

# الطريقة 2: مطابقة جميع الطبقات تلقائياً (موصى به)
all_matches, unmatched = matcher.match_all_layers(
    awards_df=awards_df,
    bank_df=bank_df,
    time_window_days=7,
    use_record_linkage=True  # استخدام RL للحالات الصعبة
)
```

**أعمدة الإخراج:**
- `MatchType`: نوع المطابقة (Exact/Fuzzy/RecordLinkage)
- `MatchScore`: درجة التطابق (0-100)
- `DateDiff`: الفرق بين التواريخ (أيام)

---

### 2️⃣ **Audit Logger** - نظام تسجيل العمليات
**الملف:** `core/audit_logger.py`

**المكتبات المستخدمة:**
- `pandas>=2.1.0` - معالجة البيانات
- `duckdb>=0.9.0` - قاعدة بيانات عالية الأداء (اختياري)
- `json` (built-in) - تخزين الأخطاء
- `uuid` (built-in) - معرفات فريدة
- `datetime` (built-in) - التواريخ

**المميزات:**
- ✅ **Analysis Logging**: تسجيل كل تشغيل تحليل (RunID فريد)
- ✅ **Match Details**: حفظ تفاصيل كل مطابقة
- ✅ **Error Tracking**: تسجيل الأخطاء مع السياق الكامل
- ✅ **Dual Storage**: CSV + DuckDB (أداء عالي)
- ✅ **Query & Reports**: استرجاع وتقارير نصية

**الوظائف الرئيسية:**
```python
from core.audit_logger import AuditLogger
import time

logger = AuditLogger(log_dir="outputs/audit_logs")

# تسجيل تشغيل التحليل
start_time = time.time()
# ... تنفيذ التحليل ...
execution_time = time.time() - start_time

run_id = logger.log_analysis_run(
    awards_files=["file1.xlsx", "file2.xlsx"],
    bank_file="bank_statement.xlsx",
    statistics={
        'total_awards': 1500,
        'total_bank_records': 800,
        'exact_matches': 600,
        'fuzzy_matches': 300,
        'rl_matches': 50,
        'unmatched_awards': 550,
        'suspected_duplicates': 20,
        'confirmed_duplicates': 5
    },
    time_window_days=7,
    fuzzy_threshold=90,
    use_record_linkage=True,
    execution_time=execution_time,
    user_name="Admin",
    status="Success"
)

# تسجيل المطابقات
logger.log_matches(run_id, matched_df)

# تسجيل خطأ
logger.log_error(
    error_type="FileNotFound",
    error_message="ملف الجوائز غير موجود",
    context={"file": "awards.xlsx", "path": "/uploads/"}
)

# استرجاع آخر التحليلات
recent_runs = logger.get_recent_runs(limit=10)

# استرجاع تفاصيل تشغيل محدد
details = logger.get_run_details(run_id)
# details = {'run_info': {...}, 'matches': DataFrame}

# توليد تقرير نصي
report = logger.generate_report(run_id)
print(report)
```

**ملفات الإخراج:**
- `outputs/audit_logs/analysis_runs.csv` - سجل التحليلات
- `outputs/audit_logs/match_details.csv` - تفاصيل المطابقات
- `outputs/audit_logs/errors.json` - سجل الأخطاء
- `outputs/audit_logs/audit.duckdb` - قاعدة بيانات (اختياري)

---

### 3️⃣ **Performance Optimizer** - محسِّن الأداء
**الملف:** `core/performance_optimizer.py`

**المكتبات المستخدمة:**
- `duckdb>=0.9.0` - استعلامات SQL سريعة
- `dask[complete]>=2023.12.0` - معالجة موزعة
- `pandas>=2.1.0` - معالجة البيانات
- `pyarrow>=14.0.0` - تسريع I/O

**المميزات:**
- ✅ **Smart Loading**: تحميل ذكي حسب حجم الملف
- ✅ **DuckDB Queries**: استعلامات SQL أسرع من pandas
- ✅ **Dask Processing**: معالجة موزعة للملفات الكبيرة جداً
- ✅ **Auto Recommendations**: توصيات تلقائية للإعدادات

**الوظائف الرئيسية:**
```python
from core.performance_optimizer import PerformanceOptimizer, recommend_optimizer_settings

# الحصول على توصيات
file_size_mb = 85
recommendations = recommend_optimizer_settings(file_size_mb)
print(recommendations)
# {'use_duckdb': True, 'use_dask': False, 'reason': '...'}

# تهيئة المحسِّن
optimizer = PerformanceOptimizer(
    use_duckdb=True,  # للاستعلامات السريعة
    use_dask=False    # للملفات الضخمة فقط
)

# تحميل ملف واحد
df = optimizer.load_excel_optimized("awards.xlsx")

# تحميل عدة ملفات
files = ["awards1.xlsx", "awards2.xlsx", "awards3.xlsx"]
combined_df = optimizer.load_multiple_excel_optimized(files)

# فلترة باستخدام DuckDB (أسرع)
filtered = optimizer.filter_by_amount_duckdb(
    df=combined_df,
    min_amount=1000,
    max_amount=50000,
    amount_column='AwardAmount'
)

# تجميع باستخدام DuckDB
aggregated = optimizer.aggregate_by_group_duckdb(
    df=combined_df,
    group_by=['Season', 'Race'],
    agg_columns={'AwardAmount': 'SUM', 'OwnerName': 'COUNT'}
)

# دمج جداول (JOIN) باستخدام DuckDB
merged = optimizer.join_dataframes_duckdb(
    left_df=awards_df,
    right_df=bank_df,
    left_on='OwnerName_norm',
    right_on='BankName_norm',
    how='inner'
)

# إحصائيات
stats = optimizer.get_statistics()
print(stats)

# إغلاق الاتصالات
optimizer.close()
```

**توصيات الحجم:**
- `< 10 MB`: pandas عادي (لا داعي للتحسين)
- `10-100 MB`: استخدام DuckDB فقط
- `> 100 MB`: استخدام DuckDB + Dask

---

## 🔗 دمج المكونات مع CamelAwardsAnalyzer

### خطوة 1: تحديث الـ `__init__`
```python
from core.advanced_matcher import AdvancedMatcher
from core.audit_logger import AuditLogger
from core.performance_optimizer import PerformanceOptimizer
import time

class CamelAwardsAnalyzer:
    def __init__(self):
        # المتغيرات الحالية
        self.awards_data = None
        self.bank_data = None
        self.merged_results = None
        self.statistics = {}
        
        # المكونات الجديدة
        self.matcher = AdvancedMatcher(fuzzy_threshold=90)
        self.logger = AuditLogger()
        self.optimizer = None  # يتم تهيئته عند الحاجة
        self.current_run_id = None
```

### خطوة 2: تحديث `load_awards_files`
```python
def load_awards_files(self, files: List[Any]) -> pd.DataFrame:
    """تحميل ودمج ملفات الجوائز مع التحسين"""
    
    # حساب الحجم الإجمالي (تقريبي)
    total_size_mb = len(files) * 5  # تقدير
    
    # تهيئة المحسِّن
    recommendations = recommend_optimizer_settings(total_size_mb)
    self.optimizer = PerformanceOptimizer(
        use_duckdb=recommendations['use_duckdb'],
        use_dask=recommendations['use_dask']
    )
    
    # تحميل الملفات
    if total_size_mb > 10:
        # استخدام المحسِّن
        file_paths = [f.name if hasattr(f, 'name') else str(f) for f in files]
        self.awards_data = self.optimizer.load_multiple_excel_optimized(file_paths)
    else:
        # الطريقة العادية (الكود الحالي)
        # ... كود التحميل الحالي ...
        pass
    
    # باقي المعالجة (تطبيع، تواريخ، إلخ)
    # ... كما هو ...
    
    return self.awards_data
```

### خطوة 3: تحديث `match_with_bank`
```python
def match_with_bank(self, time_window_days: int = 7, use_record_linkage: bool = False) -> pd.DataFrame:
    """مطابقة مع البنك باستخدام المحرك المتقدم"""
    
    if self.awards_data is None or self.bank_data is None:
        raise ValueError("يجب تحميل البيانات أولاً")
    
    print("🔍 بدء المطابقة المتقدمة...")
    start_time = time.time()
    
    try:
        # استخدام محرك المطابقة المتقدم
        matched_df, unmatched_df = self.matcher.match_all_layers(
            awards_df=self.awards_data,
            bank_df=self.bank_data,
            time_window_days=time_window_days,
            use_record_linkage=use_record_linkage
        )
        
        # إضافة أعمدة الحالة
        matched_df['Status'] = matched_df['MatchType'].apply(
            lambda x: 'مطابق' if x in ['Exact', 'Fuzzy', 'RecordLinkage'] else 'غير مطابق'
        )
        
        # دمج مع غير المطابقة
        unmatched_df['MatchType'] = 'Unmatched'
        unmatched_df['MatchScore'] = 0
        unmatched_df['Status'] = 'غير مطابق'
        
        self.merged_results = pd.concat([matched_df, unmatched_df], ignore_index=True)
        
        # حساب الإحصائيات
        execution_time = time.time() - start_time
        self.statistics = {
            'total_awards': len(self.awards_data),
            'total_bank_records': len(self.bank_data),
            'exact_matches': len(matched_df[matched_df['MatchType'] == 'Exact']),
            'fuzzy_matches': len(matched_df[matched_df['MatchType'] == 'Fuzzy']),
            'rl_matches': len(matched_df[matched_df['MatchType'] == 'RecordLinkage']),
            'unmatched_awards': len(unmatched_df),
            'execution_time': execution_time
        }
        
        # تسجيل التحليل
        self.current_run_id = self.logger.log_analysis_run(
            awards_files=["multiple_files"],  # استبدل بأسماء الملفات الفعلية
            bank_file="bank_statement.xlsx",
            statistics=self.statistics,
            time_window_days=time_window_days,
            fuzzy_threshold=90,
            use_record_linkage=use_record_linkage,
            execution_time=execution_time,
            user_name="System",
            status="Success"
        )
        
        # تسجيل المطابقات
        self.logger.log_matches(self.current_run_id, matched_df)
        
        print(f"✅ تمت المطابقة في {execution_time:.2f} ثانية")
        return self.merged_results
        
    except Exception as e:
        # تسجيل الخطأ
        self.logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={'function': 'match_with_bank', 'time_window': time_window_days}
        )
        raise
```

### خطوة 4: تحديث `detect_internal_duplicates`
```python
def detect_internal_duplicates(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """اكتشاف التكرارات مع التسجيل"""
    
    try:
        # الكود الحالي لاكتشاف التكرارات
        # ... كما هو ...
        
        suspected = self.merged_results[self.merged_results['DuplicateStatus'] == 'مشتبه']
        confirmed = self.merged_results[self.merged_results['DuplicateStatus'] == 'مؤكد']
        
        # تحديث الإحصائيات
        self.statistics['suspected_duplicates'] = len(suspected)
        self.statistics['confirmed_duplicates'] = len(confirmed)
        
        return suspected, confirmed
        
    except Exception as e:
        self.logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={'function': 'detect_internal_duplicates'}
        )
        raise
```

### خطوة 5: تحديث `export_report` (إضافة Pivot Sheet)
```python
def export_report(self, output_path: str) -> str:
    """تصدير التقرير مع Pivot Table"""
    
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Sheet 1: البيانات الكاملة
            self.merged_results.to_excel(writer, sheet_name='النتائج الكاملة', index=False)
            
            # Sheet 2: Pivot Table
            if len(self.merged_results) > 0:
                pivot = self.merged_results.pivot_table(
                    index=['Season', 'Race'],
                    columns='MatchType',
                    values='AwardAmount',
                    aggfunc=['count', 'sum'],
                    fill_value=0
                )
                pivot.to_excel(writer, sheet_name='الملخص Pivot')
            
            # Sheet 3: الإحصائيات
            stats_df = pd.DataFrame([self.statistics])
            stats_df.to_excel(writer, sheet_name='الإحصائيات', index=False)
            
            # Sheet 4: سجل التشغيل (من Audit Logger)
            if self.current_run_id:
                details = self.logger.get_run_details(self.current_run_id)
                run_info = pd.DataFrame([details['run_info']])
                run_info.to_excel(writer, sheet_name='سجل التشغيل', index=False)
            
            # التنسيقات... (كما هو)
        
        return output_path
        
    except Exception as e:
        self.logger.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={'function': 'export_report', 'output_path': output_path}
        )
        raise
```

---

## 🎯 الاستخدام في Streamlit

### تحديث `main_app_redesigned.py` - صفحة جوائز الهجن
```python
import streamlit as st
from core.camel_awards_analyzer import CamelAwardsAnalyzer
from core.performance_optimizer import recommend_optimizer_settings

# ... في الصفحة ...

# خيارات متقدمة
with st.expander("⚙️ إعدادات متقدمة"):
    use_record_linkage = st.checkbox(
        "استخدام Record Linkage (للحالات الصعبة)",
        value=False,
        help="خوارزميات مطابقة متقدمة - أبطأ لكن أدق"
    )
    
    use_performance_optimizer = st.checkbox(
        "تفعيل محسِّن الأداء",
        value=True,
        help="استخدام DuckDB/Dask للملفات الكبيرة"
    )

# زر التحليل
if st.button("🔍 بدء التحليل", type="primary"):
    with st.spinner("جاري التحليل..."):
        analyzer = CamelAwardsAnalyzer()
        
        # عرض توصيات الأداء
        if use_performance_optimizer:
            total_size = sum([f.size for f in awards_files]) / (1024*1024)  # MB
            recommendations = recommend_optimizer_settings(total_size)
            st.info(f"💡 {recommendations['reason']}")
        
        # تحميل البيانات
        awards_df = analyzer.load_awards_files(awards_files)
        bank_df = analyzer.load_bank_statement(bank_file)
        
        # المطابقة
        results = analyzer.match_with_bank(
            time_window_days=time_window,
            use_record_linkage=use_record_linkage
        )
        
        # اكتشاف التكرارات
        suspected, confirmed = analyzer.detect_internal_duplicates()
        
        # عرض النتائج
        st.success(f"✅ تمت المطابقة: {analyzer.statistics['exact_matches'] + analyzer.statistics['fuzzy_matches'] + analyzer.statistics['rl_matches']} سجل")
        
        # عرض الإحصائيات
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("مطابقات حتمية", analyzer.statistics['exact_matches'])
        with col2:
            st.metric("مطابقات ضبابية", analyzer.statistics['fuzzy_matches'])
        with col3:
            st.metric("مطابقات RL", analyzer.statistics['rl_matches'])
        with col4:
            st.metric("غير مطابق", analyzer.statistics['unmatched_awards'])
        
        # عرض البيانات
        st.dataframe(results)
        
        # تصدير
        if st.button("📥 تصدير التقرير"):
            output_file = analyzer.export_report("outputs/camel_awards_report.xlsx")
            
            with open(output_file, 'rb') as f:
                st.download_button(
                    "⬇️ تحميل التقرير",
                    f,
                    file_name="تقرير_جوائز_الهجن.xlsx",
                    mime="application/vnd.ms-excel"
                )
        
        # عرض سجل التشغيل
        if analyzer.current_run_id:
            with st.expander("📝 سجل التشغيل"):
                report = analyzer.logger.generate_report(analyzer.current_run_id)
                st.text(report)
```

---

## 📊 نتائج التحسين المتوقعة

| الحجم | pandas عادي | مع DuckDB | مع DuckDB+Dask |
|------|------------|-----------|----------------|
| 10 MB | 5 ث | 5 ث | - |
| 50 MB | 25 ث | 12 ث | - |
| 100 MB | 60 ث | 25 ث | 18 ث |
| 500 MB | 350 ث | 120 ث | 65 ث |

**ملاحظة:** النتائج تقريبية وتعتمد على الأجهزة.

---

## ✅ قائمة التحقق - Integration Checklist

- [x] تثبيت المكتبات الجديدة في `requirements.txt`
- [x] إنشاء `core/advanced_matcher.py`
- [x] إنشاء `core/audit_logger.py`
- [x] إنشاء `core/performance_optimizer.py`
- [ ] تحديث `core/camel_awards_analyzer.py` (دمج المكونات)
- [ ] تحديث `main_app_redesigned.py` (إضافة خيارات متقدمة)
- [ ] اختبار المطابقة الأساسية
- [ ] اختبار Record Linkage
- [ ] اختبار Audit Trail
- [ ] اختبار Performance Optimizer
- [ ] توليد تقرير شامل بـ 4 أوراق
- [ ] اختبار على ملفات كبيرة (>100 MB)

---

## 🐛 استكشاف الأخطاء

### خطأ: "duckdb not found"
```bash
pip install duckdb>=0.9.0
```

### خطأ: "recordlinkage import error"
```bash
pip install recordlinkage>=0.16.0
```

### خطأ: "dask not installed"
```bash
pip install "dask[complete]>=2023.12.0"
```

### خطأ: "Audit logs folder not found"
سيتم إنشاء المجلد تلقائياً، لكن تأكد من الأذونات:
```python
from pathlib import Path
Path("outputs/audit_logs").mkdir(parents=True, exist_ok=True)
```

---

## 📚 مراجع المكتبات

- **rapidfuzz**: https://github.com/maxbachmann/RapidFuzz
- **recordlinkage**: https://recordlinkage.readthedocs.io/
- **duckdb**: https://duckdb.org/docs/
- **dask**: https://docs.dask.org/

---

## 🎉 الخلاصة

تم إنشاء **3 مكونات قوية** تضيف:
1. **مطابقة متعددة الطبقات** (Exact → Fuzzy → RL)
2. **تسجيل شامل** للعمليات والأخطاء
3. **أداء محسّن** للملفات الكبيرة

كل المكونات **مستقلة** و**قابلة للتفعيل/التعطيل** حسب الحاجة.

**الخطوة التالية:** دمج هذه المكونات في `CamelAwardsAnalyzer` الرئيسي كما موضح أعلاه. 🚀
