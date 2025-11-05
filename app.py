# -*- coding: utf-8 -*-
"""
تطبيق تحليل البيانات المالية - واجهة Streamlit
نظام متكامل لمراجعة وتدقيق الدفعات المالية
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

from core.data_loader import DataLoader
from core.duplicate_analyzer import DuplicateAnalyzer
from core.anomaly_detector import AnomalyDetector
from config import MESSAGES, ALLOWED_EXTENSIONS

# إعدادات الصفحة
st.set_page_config(
    page_title="محلل البيانات المالية",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #1f77b4;
        font-family: 'Arial', sans-serif;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'loader' not in st.session_state:
    st.session_state.loader = None
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False


def main():
    """الواجهة الرئيسية"""
    
    # العنوان الرئيسي
    st.title("📊 محلل البيانات المالية المتقدم")
    st.markdown("---")
    
    # الشريط الجانبي
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        
        # رفع الملف
        st.subheader("1️⃣ رفع الملف")
        uploaded_file = st.file_uploader(
            "اختر ملف Excel أو CSV",
            type=['xlsx', 'xls', 'csv'],
            help="الحد الأقصى: 500 ميجابايت"
        )
        
        if uploaded_file:
            process_uploaded_file(uploaded_file)
        
        st.markdown("---")
        
        # الإجراءات
        if st.session_state.df is not None:
            st.subheader("2️⃣ نوع التحليل")
            analysis_type = st.selectbox(
                "اختر نوع التحليل",
                ["نظرة عامة", "كشف التكرارات", "كشف الانحرافات", "تحليل متقدم", "تقرير شامل"]
            )
            
            if st.button("🚀 تنفيذ التحليل", type="primary"):
                execute_analysis(analysis_type)
    
    # المحتوى الرئيسي
    if st.session_state.df is None:
        show_welcome_page()
    else:
        show_data_overview()


def process_uploaded_file(uploaded_file):
    """معالجة الملف المرفوع"""
    try:
        with st.spinner("جاري تحميل الملف..."):
            # حفظ الملف مؤقتاً
            temp_path = Path("uploads") / uploaded_file.name
            temp_path.parent.mkdir(exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # تحميل البيانات
            loader = DataLoader(temp_path)
            loader.load()
            loader.auto_clean()
            
            st.session_state.df = loader.get_data()
            st.session_state.loader = loader
            
            st.sidebar.success(f"✅ تم تحميل {len(st.session_state.df)} صف بنجاح!")
            
    except Exception as e:
        st.sidebar.error(f"❌ خطأ في التحميل: {str(e)}")


def show_welcome_page():
    """صفحة الترحيب"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## 🎯 مرحباً بك في محلل البيانات المالية
        
        ### ✨ الميزات الرئيسية:
        
        - 📥 **رفع سهل**: دعم Excel و CSV
        - 🔍 **كشف التكرارات**: تطابق تام وضبابي
        - 📊 **كشف الانحرافات**: IQR, Z-Score, ML
        - 📈 **تحليلات متقدمة**: إحصائيات شاملة
        - 📄 **تقارير احترافية**: تصدير بصيغ متعددة
        
        ### 🚀 البداية:
        1. ارفع ملفك من الشريط الجانبي
        2. اختر نوع التحليل المطلوب
        3. احصل على النتائج فوراً
        
        ---
        *تم التطوير باستخدام أحدث التقنيات في علم البيانات*
        """)


def show_data_overview():
    """عرض نظرة عامة على البيانات"""
    st.header("📋 نظرة عامة على البيانات")
    
    df = st.session_state.df
    
    # معلومات أساسية
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("عدد الصفوف", f"{len(df):,}")
    with col2:
        st.metric("عدد الأعمدة", len(df.columns))
    with col3:
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        st.metric("الحجم", f"{memory_mb:.2f} MB")
    with col4:
        null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        st.metric("نسبة القيم الفارغة", f"{null_pct:.1f}%")
    
    st.markdown("---")
    
    # عرض البيانات
    with st.expander("📊 عرض البيانات", expanded=False):
        st.dataframe(df.head(100), use_container_width=True, height=400)
    
    # معلومات الأعمدة
    with st.expander("📑 معلومات الأعمدة"):
        col_info = pd.DataFrame({
            'نوع البيانات': df.dtypes,
            'القيم الفارغة': df.isnull().sum(),
            'نسبة الفراغ %': (df.isnull().sum() / len(df) * 100).round(2),
            'القيم الفريدة': df.nunique()
        })
        st.dataframe(col_info, use_container_width=True)


def execute_analysis(analysis_type):
    """تنفيذ التحليل المحدد"""
    df = st.session_state.df
    
    if analysis_type == "نظرة عامة":
        show_overview_analysis(df)
    elif analysis_type == "كشف التكرارات":
        show_duplicate_analysis(df)
    elif analysis_type == "كشف الانحرافات":
        show_anomaly_analysis(df)
    elif analysis_type == "تحليل متقدم":
        show_advanced_analysis(df)
    elif analysis_type == "تقرير شامل":
        show_comprehensive_report(df)


def show_overview_analysis(df):
    """تحليل نظرة عامة"""
    st.header("📈 التحليل الإحصائي الشامل")
    
    # اختيار الأعمدة الرقمية
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("⚠️ لا توجد أعمدة رقمية للتحليل")
        return
    
    selected_col = st.selectbox("اختر العمود للتحليل", numeric_cols)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 الإحصائيات الوصفية")
        stats = df[selected_col].describe()
        st.dataframe(stats, use_container_width=True)
    
    with col2:
        st.subheader("📉 التوزيع")
        fig = px.histogram(df, x=selected_col, nbins=50, 
                          title=f"توزيع {selected_col}")
        st.plotly_chart(fig, use_container_width=True)
    
    # Box Plot
    st.subheader("📦 مخطط الصندوق")
    fig = px.box(df, y=selected_col, title=f"مخطط الصندوق - {selected_col}")
    st.plotly_chart(fig, use_container_width=True)


def show_duplicate_analysis(df):
    """تحليل التكرارات"""
    st.header("🔍 كشف الدفعات المكررة")
    
    # اختيار الأعمدة
    all_cols = df.columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        entity_col = st.selectbox("عمود الجهة/الاسم", all_cols)
    with col2:
        amount_col = st.selectbox("عمود المبلغ", all_cols)
    with col3:
        event_col = st.selectbox("عمود الحدث (اختياري)", ["لا يوجد"] + all_cols)
    
    event_col = None if event_col == "لا يوجد" else event_col
    
    if st.button("🔎 البحث عن التكرارات"):
        with st.spinner("جاري البحث..."):
            analyzer = DuplicateAnalyzer(df)
            duplicates = analyzer.find_payment_duplicates(
                entity_col=entity_col,
                amount_col=amount_col,
                event_col=event_col
            )
            
            if len(duplicates) > 0:
                st.success(f"✅ تم العثور على {len(duplicates)} دفعة مكررة")
                
                # عرض النتائج
                st.subheader("📋 الدفعات المكررة")
                st.dataframe(duplicates, use_container_width=True, height=400)
                
                # إحصائيات
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("عدد المجموعات المكررة", 
                             duplicates['duplicate_group'].nunique())
                with col2:
                    st.metric("نسبة التكرار", 
                             f"{len(duplicates)/len(df)*100:.2f}%")
                
                # تصدير
                if st.button("💾 تصدير النتائج"):
                    output_path = Path("outputs") / f"duplicates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    analyzer.export_duplicates(str(output_path))
                    st.success(f"✅ تم التصدير إلى: {output_path}")
            else:
                st.info("ℹ️ لم يتم العثور على دفعات مكررة")


def show_anomaly_analysis(df):
    """تحليل الانحرافات"""
    st.header("📊 كشف الانحرافات والشذوذات")
    
    # اختيار العمود
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("⚠️ لا توجد أعمدة رقمية للتحليل")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_col = st.selectbox("اختر العمود", numeric_cols)
    with col2:
        method = st.selectbox("الطريقة", ["IQR", "Z-Score", "جميع الطرق"])
    with col3:
        if method == "IQR":
            param = st.slider("معامل IQR", 1.0, 3.0, 1.5, 0.5)
        elif method == "Z-Score":
            param = st.slider("عتبة Z-Score", 2.0, 4.0, 3.0, 0.5)
        else:
            param = None
    
    if st.button("🔍 كشف الشذوذات"):
        with st.spinner("جاري التحليل..."):
            detector = AnomalyDetector(df)
            
            if method == "IQR":
                anomalies = detector.detect_iqr_anomalies(selected_col, param)
            elif method == "Z-Score":
                anomalies = detector.detect_zscore_anomalies(selected_col, param)
            else:
                results = detector.detect_all_anomalies(selected_col)
                anomalies = detector.anomalies
            
            if len(anomalies) > 0:
                st.success(f"✅ تم العثور على {len(anomalies)} شذوذ")
                
                # عرض النتائج
                st.subheader("📋 القيم الشاذة")
                st.dataframe(anomalies, use_container_width=True, height=400)
                
                # رسم بياني
                fig = px.scatter(df, y=selected_col, 
                               title=f"القيم الشاذة في {selected_col}",
                               color=df.index.isin(anomalies.index),
                               labels={'color': 'شاذ'})
                st.plotly_chart(fig, use_container_width=True)
                
                # تصدير
                if st.button("💾 تصدير النتائج"):
                    output_path = Path("outputs") / f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    detector.export_anomalies(str(output_path))
                    st.success(f"✅ تم التصدير إلى: {output_path}")
            else:
                st.info("ℹ️ لم يتم العثور على شذوذات")


def show_advanced_analysis(df):
    """تحليل متقدم"""
    st.header("🎯 التحليل المتقدم")
    
    st.info("⚠️ هذه الميزة قيد التطوير - ستتضمن تحليلات إضافية متقدمة")


def show_comprehensive_report(df):
    """تقرير شامل"""
    st.header("📄 التقرير الشامل")
    
    st.info("⚠️ هذه الميزة قيد التطوير - ستقوم بتوليد تقرير PDF شامل")


if __name__ == "__main__":
    main()
