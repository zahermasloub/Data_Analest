# -*- coding: utf-8 -*-
"""
مكونات UI قابلة لإعادة الاستخدام
مجموعة شاملة من المكونات الجاهزة للاستخدام
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
import pandas as pd


class UIComponents:
    """مجموعة مكونات UI احترافية"""
    
    @staticmethod
    def hero_section(
        title: str,
        subtitle: str,
        description: str = "",
        icon: str = "📊"
    ):
        """قسم البطل (Hero Section) في أعلى الصفحة"""
        st.markdown(f"""
        <div class="glass-card fade-in" style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h1 class="gradient-text" style="margin: 0; font-size: 3rem; font-weight: 900;">
                {title}
            </h1>
            <h2 style="margin: 1rem 0; font-size: 1.5rem; font-weight: 600; opacity: 0.9;">
                {subtitle}
            </h2>
            {f'<p style="font-size: 1.1rem; opacity: 0.8; max-width: 800px; margin: 1rem auto;">{description}</p>' if description else ''}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def metric_card(
        label: str,
        value: str,
        delta: str = "",
        icon: str = "📊",
        color: str = "primary"
    ):
        """بطاقة مقياس محسّنة"""
        delta_html = f'<div style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.8;">{delta}</div>' if delta else ''
        
        st.markdown(f"""
        <div class="glass-card fade-in" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.7; margin-bottom: 0.5rem;">
                {label}
            </div>
            <div style="font-size: 2rem; font-weight: 700;">
                {value}
            </div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def info_box(
        title: str,
        content: str,
        box_type: str = "info",
        icon: str = ""
    ):
        """صندوق معلومات ملون"""
        type_configs = {
            "info": {"icon": "ℹ️", "class": "stInfo"},
            "success": {"icon": "✅", "class": "stSuccess"},
            "warning": {"icon": "⚠️", "class": "stWarning"},
            "error": {"icon": "❌", "class": "stError"}
        }
        
        config = type_configs.get(box_type, type_configs["info"])
        display_icon = icon if icon else config["icon"]
        
        st.markdown(f"""
        <div class="{config['class']}" style="padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 0.75rem 0; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;">{display_icon}</span>
                <span>{title}</span>
            </h4>
            <div style="opacity: 0.95; line-height: 1.6;">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def feature_card(
        icon: str,
        title: str,
        description: str,
        features: List[str]
    ):
        """بطاقة ميزة مع قائمة"""
        features_html = "\n".join([f"<li style='margin-bottom: 0.5rem;'>{f}</li>" for f in features])
        
        st.markdown(f"""
        <div class="glass-card fade-in" style="height: 100%;">
            <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">{icon}</div>
            <h3 style="text-align: center; margin-bottom: 1rem;">{title}</h3>
            <p style="text-align: center; opacity: 0.8; margin-bottom: 1.5rem;">{description}</p>
            <ul style="list-style: none; padding: 0;">
                {features_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def stats_card(
        stats: Dict[str, Any],
        title: str = "إحصائيات سريعة"
    ):
        """بطاقة إحصائيات"""
        stats_html = ""
        for label, value in stats.items():
            stats_html += f"""
            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--border-primary);">
                <span style="font-weight: 600;">{label}</span>
                <span style="font-weight: 700; color: var(--primary);">{value}</span>
            </div>
            """
        
        st.markdown(f"""
        <div class="glass-card fade-in">
            <h3 style="margin-bottom: 1.5rem;">{title}</h3>
            {stats_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def progress_card(
        title: str,
        current: int,
        total: int,
        color: str = "primary"
    ):
        """بطاقة تقدم"""
        percentage = (current / total * 100) if total > 0 else 0
        
        st.markdown(f"""
        <div class="glass-card fade-in">
            <h4 style="margin-bottom: 1rem;">{title}</h4>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>{current} / {total}</span>
                <span style="font-weight: 700;">{percentage:.1f}%</span>
            </div>
            <div style="width: 100%; height: 8px; background: var(--border-primary); border-radius: 4px; overflow: hidden;">
                <div style="width: {percentage}%; height: 100%; background: var(--{color}); transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def timeline_card(
        title: str = "سير العمل",
        items: Optional[List[Dict[str, str]]] = None
    ):
        """بطاقة خط زمني باستخدام مكونات Streamlit الأصلية"""
        if items is None:
            items = []
        
        # عنوان البطاقة
        st.markdown(f"### {title}")
        st.markdown("---")
        
        # عرض كل عنصر في timeline
        for i, item in enumerate(items):
            col1, col2 = st.columns([1, 10])
            
            with col1:
                # الرقم الدائري
                st.markdown(f"""
                <div style="
                    width: 50px; 
                    height: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 50%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: white; 
                    font-weight: bold; 
                    font-size: 1.2rem;
                    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.4);
                ">
                    {i+1}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # العنوان والوصف
                st.markdown(f"**{item.get('title', '')}**")
                st.markdown(f"<p style='color: #888; margin-top: -10px;'>{item.get('description', '')}</p>", unsafe_allow_html=True)
            
            # خط فاصل (إلا في آخر عنصر)
            if i < len(items) - 1:
                st.markdown("<br>", unsafe_allow_html=True)
    
    @staticmethod
    def gradient_header(
        text: str,
        subtitle: str = "",
        icon: str = ""
    ):
        """عنوان بتدرج لوني"""
        icon_html = f'<span style="font-size: 1.5em; margin-left: 0.5rem;">{icon}</span>' if icon else ''
        subtitle_html = f'<p style="font-size: 1.2rem; opacity: 0.8; margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ''
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
            <h1 class="gradient-text" style="display: inline-flex; align-items: center;">
                {icon_html}
                {text}
            </h1>
            {subtitle_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def data_table_enhanced(
        df: pd.DataFrame,
        title: str = "",
        show_search: bool = True,
        max_height: int = 400
    ):
        """جدول بيانات محسّن"""
        if title:
            st.markdown(f"### {title}")
        
        if show_search:
            search = st.text_input("🔍 بحث في البيانات:", key=f"search_{id(df)}")
            if search:
                # بحث في جميع الأعمدة
                mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
                df = df[mask]
        
        st.dataframe(df, use_container_width=True, height=max_height)
        
        # إحصائيات سريعة
        col1, col2, col3 = st.columns(3)
        col1.metric("عدد الصفوف", f"{len(df):,}")
        col2.metric("عدد الأعمدة", len(df.columns))
        col3.metric("حجم البيانات", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    @staticmethod
    def chart_card(
        fig,
        title: str = "",
        description: str = ""
    ):
        """بطاقة رسم بياني"""
        st.markdown(f"""
        <div class="glass-card fade-in">
            {f'<h3 style="margin-bottom: 0.5rem;">{title}</h3>' if title else ''}
            {f'<p style="opacity: 0.8; margin-bottom: 1rem;">{description}</p>' if description else ''}
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def comparison_cards(
        items: List[Dict[str, Any]],
        title: str = "مقارنة"
    ):
        """بطاقات مقارنة"""
        st.markdown(f"### {title}")
        
        cols = st.columns(len(items))
        for col, item in zip(cols, items):
            with col:
                st.markdown(f"""
                <div class="glass-card fade-in" style="text-align: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">{item.get('icon', '📊')}</div>
                    <h4 style="margin-bottom: 0.5rem;">{item.get('label', '')}</h4>
                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">
                        {item.get('value', '')}
                    </div>
                    <p style="opacity: 0.7; font-size: 0.9rem;">{item.get('description', '')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def sidebar_section(
        title: str,
        icon: str = "⚙️"
    ):
        """قسم في الشريط الجانبي مع تنسيق"""
        st.sidebar.markdown(f"""
        <div style="background: var(--gradient-primary); padding: 1rem; border-radius: 12px; text-align: center; margin-bottom: 1.5rem; box-shadow: var(--shadow-md);">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <h3 style="color: white; margin: 0; font-weight: 700;">{title}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def footer(
        app_name: str = "Data Analest",
        version: str = "1.0.0",
        developer: str = "GitHub Copilot",
        year: int = 2025
    ):
        """تذييل احترافي"""
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem 1rem; background: var(--gradient-primary); border-radius: 16px; margin-top: 3rem; color: white; box-shadow: var(--shadow-xl);">
            <h2 style="margin: 0; font-weight: 800; font-size: 2.5rem; color: white;">💼 {app_name}</h2>
            <p style="margin: 1rem 0; font-size: 1.3rem; font-weight: 600; opacity: 0.95;">نظام تحليل البيانات المالية الاحترافي</p>
            <p style="margin: 1rem 0; font-size: 1rem; opacity: 0.9;">
                ✨ تم التطوير بواسطة {developer} | 📅 {year}
            </p>
            <p style="margin: 1rem 0; font-size: 0.95rem; opacity: 0.85;">
                📧 zahermasloub@github.com | 🌐 github.com/zahermasloub/Data_Analest
            </p>
            <p style="margin-top: 1.5rem; font-size: 0.875rem; opacity: 0.8; padding-top: 1rem; border-top: 2px solid rgba(255,255,255,0.2);">
                الإصدار {version} | © {year} جميع الحقوق محفوظة | الترخيص: MIT
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def loading_spinner(text: str = "جاري التحميل..."):
        """سبينر تحميل مخصص"""
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div class="pulse" style="display: inline-block; font-size: 3rem; margin-bottom: 1rem;">⏳</div>
            <p style="font-size: 1.2rem; font-weight: 600; opacity: 0.8;">{text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def badge(text: str, color: str = "primary"):
        """شارة صغيرة"""
        return f'<span style="background: var(--{color}); color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600; display: inline-block;">{text}</span>'
    
    @staticmethod
    def icon_button(icon: str, text: str, key: str):
        """زر مع أيقونة"""
        return st.button(f"{icon} {text}", key=key, use_container_width=True)
    
    @staticmethod
    def empty_state(
        icon: str = "📭",
        title: str = "لا توجد بيانات",
        description: str = "لم يتم العثور على أي بيانات لعرضها",
        action_text: str = "",
        action_key: str = ""
    ):
        """حالة فارغة"""
        action_html = ""
        if action_text and action_key:
            if st.button(action_text, key=action_key):
                return True
        
        st.markdown(f"""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 5rem; margin-bottom: 1rem; opacity: 0.5;">{icon}</div>
            <h3 style="margin-bottom: 0.5rem; opacity: 0.8;">{title}</h3>
            <p style="opacity: 0.6;">{description}</p>
            {action_html}
        </div>
        """, unsafe_allow_html=True)
        return False
    
    @staticmethod
    def tabs_enhanced(
        tabs: List[str],
        icons: List[str] = None
    ):
        """تبويبات محسّنة مع أيقونات"""
        if icons and len(icons) == len(tabs):
            tab_labels = [f"{icon} {tab}" for icon, tab in zip(icons, tabs)]
        else:
            tab_labels = tabs
        
        return st.tabs(tab_labels)
