#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
أداة تشخيص البيانات - Camel Awards Analyzer
============================================

هذا الملف يفحص البيانات لتحديد سبب عدم المطابقة

الاستخدام:
    streamlit run diagnose_data.py
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# إضافة core إلى المسار
sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="تشخيص البيانات", page_icon="🔍", layout="wide")

st.title("🔍 تشخيص بيانات جوائز الإبل")

# تحميل الملفات
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 ملفات الجوائز")
    awards_files = st.file_uploader(
        "ارفع ملفات الجوائز",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        key='awards'
    )

with col2:
    st.subheader("🏦 كشف البنك")
    bank_file = st.file_uploader(
        "ارفع كشف البنك",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=False,
        key='bank'
    )

if awards_files and bank_file:
    st.markdown("---")
    
    # قراءة ملفات الجوائز
    st.subheader("📊 فحص ملفات الجوائز")
    
    awards_dfs = []
    for i, file in enumerate(awards_files):
        st.markdown(f"### الملف {i+1}: `{file.name}`")
        
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            awards_dfs.append(df)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("عدد السجلات", f"{len(df):,}")
            with col2:
                st.metric("عدد الأعمدة", len(df.columns))
            with col3:
                st.metric("الفارغة", f"{df.isna().sum().sum():,}")
            
            st.markdown("**أسماء الأعمدة:**")
            st.code(", ".join(df.columns.tolist()))
            
            st.markdown("**عينة من البيانات:**")
            st.dataframe(df.head(3), width=None)
            
            # فحص الأعمدة المهمة
            st.markdown("**فحص الأعمدة المهمة:**")
            
            # البحث عن عمود الاسم
            name_cols = [col for col in df.columns if any(x in col.lower() for x in ['name', 'اسم', 'مالك', 'owner'])]
            if name_cols:
                st.success(f"✅ عمود الاسم: `{name_cols[0]}`")
                st.text(f"عينة: {df[name_cols[0]].head(3).tolist()}")
            else:
                st.error("❌ لم يتم العثور على عمود الاسم")
            
            # البحث عن عمود المبلغ
            amount_cols = [col for col in df.columns if any(x in col.lower() for x in ['amount', 'مبلغ', 'قيمة', 'جائزة'])]
            if amount_cols:
                st.success(f"✅ عمود المبلغ: `{amount_cols[0]}`")
                st.text(f"عينة: {df[amount_cols[0]].head(3).tolist()}")
                st.text(f"نوع البيانات: {df[amount_cols[0]].dtype}")
                st.text(f"المدى: {df[amount_cols[0]].min():,.2f} - {df[amount_cols[0]].max():,.2f}")
            else:
                st.error("❌ لم يتم العثور على عمود المبلغ")
            
            # البحث عن عمود التاريخ
            date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'تاريخ'])]
            if date_cols:
                st.success(f"✅ عمود التاريخ: `{date_cols[0]}`")
                st.text(f"عينة: {df[date_cols[0]].head(3).tolist()}")
                st.text(f"نوع البيانات: {df[date_cols[0]].dtype}")
            else:
                st.error("❌ لم يتم العثور على عمود التاريخ")
            
            st.markdown("---")
            
        except Exception as e:
            st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
    
    # قراءة كشف البنك
    st.subheader("🏦 فحص كشف البنك")
    
    try:
        if bank_file.name.endswith('.csv'):
            bank_df = pd.read_csv(bank_file)
        else:
            bank_df = pd.read_excel(bank_file)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد السجلات", f"{len(bank_df):,}")
        with col2:
            st.metric("عدد الأعمدة", len(bank_df.columns))
        with col3:
            st.metric("الفارغة", f"{bank_df.isna().sum().sum():,}")
        
        st.markdown("**أسماء الأعمدة:**")
        st.code(", ".join(bank_df.columns.tolist()))
        
        st.markdown("**عينة من البيانات:**")
        st.dataframe(bank_df.head(3), width=None)
        
        # فحص الأعمدة المهمة
        st.markdown("**فحص الأعمدة المهمة:**")
        
        # البحث عن عمود الاسم
        name_cols = [col for col in bank_df.columns if any(x in col.lower() for x in ['name', 'اسم', 'مستفيد', 'beneficiary'])]
        if name_cols:
            st.success(f"✅ عمود الاسم: `{name_cols[0]}`")
            st.text(f"عينة: {bank_df[name_cols[0]].head(3).tolist()}")
        else:
            st.error("❌ لم يتم العثور على عمود الاسم")
        
        # البحث عن عمود المبلغ
        amount_cols = [col for col in bank_df.columns if any(x in col.lower() for x in ['amount', 'مبلغ', 'قيمة'])]
        if amount_cols:
            st.success(f"✅ عمود المبلغ: `{amount_cols[0]}`")
            st.text(f"عينة: {bank_df[amount_cols[0]].head(3).tolist()}")
            st.text(f"نوع البيانات: {bank_df[amount_cols[0]].dtype}")
            st.text(f"المدى: {bank_df[amount_cols[0]].min():,.2f} - {bank_df[amount_cols[0]].max():,.2f}")
        else:
            st.error("❌ لم يتم العثور على عمود المبلغ")
        
        # البحث عن عمود التاريخ
        date_cols = [col for col in bank_df.columns if any(x in col.lower() for x in ['date', 'تاريخ'])]
        if date_cols:
            st.success(f"✅ عمود التاريخ: `{date_cols[0]}`")
            st.text(f"عينة: {bank_df[date_cols[0]].head(3).tolist()}")
            st.text(f"نوع البيانات: {bank_df[date_cols[0]].dtype}")
        else:
            st.error("❌ لم يتم العثور على عمود التاريخ")
        
    except Exception as e:
        st.error(f"❌ خطأ في قراءة كشف البنك: {str(e)}")
    
    # مقارنة المبالغ
    if awards_dfs and 'bank_df' in locals():
        st.markdown("---")
        st.subheader("🔍 مقارنة المبالغ")
        
        # دمج ملفات الجوائز
        combined_awards = pd.concat(awards_dfs, ignore_index=True)
        
        # محاولة العثور على أعمدة المبلغ
        award_amount_col = None
        for col in combined_awards.columns:
            if any(x in col.lower() for x in ['amount', 'مبلغ', 'قيمة', 'جائزة']):
                award_amount_col = col
                break
        
        bank_amount_col = None
        for col in bank_df.columns:
            if any(x in col.lower() for x in ['amount', 'مبلغ', 'قيمة']):
                bank_amount_col = col
                break
        
        if award_amount_col and bank_amount_col:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 مبالغ الجوائز:**")
                award_amounts = pd.to_numeric(combined_awards[award_amount_col], errors='coerce').dropna()
                st.write(f"العدد: {len(award_amounts):,}")
                st.write(f"المجموع: {award_amounts.sum():,.2f}")
                st.write(f"المتوسط: {award_amounts.mean():,.2f}")
                st.write(f"الأصغر: {award_amounts.min():,.2f}")
                st.write(f"الأكبر: {award_amounts.max():,.2f}")
                
                st.markdown("**أكثر 10 مبالغ تكراراً:**")
                st.dataframe(
                    award_amounts.value_counts().head(10).reset_index(),
                    width=None
                )
            
            with col2:
                st.markdown("**🏦 مبالغ البنك:**")
                bank_amounts = pd.to_numeric(bank_df[bank_amount_col], errors='coerce').dropna()
                st.write(f"العدد: {len(bank_amounts):,}")
                st.write(f"المجموع: {bank_amounts.sum():,.2f}")
                st.write(f"المتوسط: {bank_amounts.mean():,.2f}")
                st.write(f"الأصغر: {bank_amounts.min():,.2f}")
                st.write(f"الأكبر: {bank_amounts.max():,.2f}")
                
                st.markdown("**أكثر 10 مبالغ تكراراً:**")
                st.dataframe(
                    bank_amounts.value_counts().head(10).reset_index(),
                    width=None
                )
            
            # البحث عن مبالغ مشتركة
            common_amounts = set(award_amounts.unique()) & set(bank_amounts.unique())
            st.info(f"💡 المبالغ المشتركة: {len(common_amounts):,}")
            
            if len(common_amounts) > 0:
                st.success(f"✅ هناك {len(common_amounts):,} مبلغ مشترك بين الملفين")
                st.dataframe(
                    pd.DataFrame(sorted(common_amounts, reverse=True)[:20], columns=['المبالغ المشتركة']),
                    width=None
                )
            else:
                st.error("❌ لا توجد مبالغ مشتركة بين الملفين!")
                st.warning("💡 تحقق من:")
                st.write("- هل المبالغ بنفس العملة؟")
                st.write("- هل هناك أخطاء في إدخال البيانات؟")
                st.write("- هل البيانات لنفس الفترة الزمنية؟")

else:
    st.info("📤 يرجى رفع ملفات الجوائز وكشف البنك للبدء في التشخيص")
