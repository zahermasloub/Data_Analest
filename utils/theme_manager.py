# -*- coding: utf-8 -*-
"""
نظام إدارة الثيمات - Dark/Light Mode
يوفر تصاميم احترافية متوافقة مع الوضع الليلي والنهاري
"""

import streamlit as st
from typing import Dict, Any


class ThemeManager:
    """مدير الثيمات المتقدم"""
    
    def __init__(self):
        self.current_theme = self._initialize_theme()
    
    def _initialize_theme(self) -> str:
        """تهيئة الثيم المحفوظ أو الافتراضي"""
        if 'theme' not in st.session_state:
            st.session_state.theme = 'dark'  # الوضع الافتراضي
        return st.session_state.theme
    
    def toggle_theme(self):
        """تبديل الثيم"""
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()
    
    def get_current_theme(self) -> str:
        """الحصول على الثيم الحالي"""
        return st.session_state.get('theme', 'dark')
    
    def get_theme_colors(self) -> Dict[str, str]:
        """الحصول على ألوان الثيم الحالي"""
        theme = self.get_current_theme()
        
        if theme == 'dark':
            return self._get_dark_theme()
        else:
            return self._get_light_theme()
    
    def _get_dark_theme(self) -> Dict[str, str]:
        """ألوان الوضع الليلي"""
        return {
            # الألوان الأساسية
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#3b82f6',
            
            # الخلفيات
            'background_primary': '#0f172a',
            'background_secondary': '#1e293b',
            'background_tertiary': '#334155',
            'background_card': '#1e293b',
            'background_sidebar': '#0f172a',
            
            # النصوص
            'text_primary': '#f1f5f9',
            'text_secondary': '#cbd5e1',
            'text_muted': '#94a3b8',
            'text_inverse': '#0f172a',
            
            # الحدود
            'border_primary': '#334155',
            'border_secondary': '#475569',
            'border_accent': '#667eea',
            
            # الظلال
            'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
            'shadow_md': '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
            'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
            'shadow_xl': '0 20px 25px -5px rgba(0, 0, 0, 0.6)',
            
            # التدرجات
            'gradient_primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'gradient_secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'gradient_success': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'gradient_background': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
            
            # حالات التفاعل
            'hover_overlay': 'rgba(255, 255, 255, 0.05)',
            'active_overlay': 'rgba(255, 255, 255, 0.1)',
            'disabled_overlay': 'rgba(0, 0, 0, 0.3)',
            
            # الشفافية
            'overlay_light': 'rgba(255, 255, 255, 0.1)',
            'overlay_medium': 'rgba(255, 255, 255, 0.2)',
            'overlay_heavy': 'rgba(255, 255, 255, 0.3)',
        }
    
    def _get_light_theme(self) -> Dict[str, str]:
        """ألوان الوضع النهاري"""
        return {
            # الألوان الأساسية
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#3b82f6',
            
            # الخلفيات
            'background_primary': '#ffffff',
            'background_secondary': '#f8fafc',
            'background_tertiary': '#f1f5f9',
            'background_card': '#ffffff',
            'background_sidebar': '#f8fafc',
            
            # النصوص
            'text_primary': '#0f172a',
            'text_secondary': '#475569',
            'text_muted': '#64748b',
            'text_inverse': '#ffffff',
            
            # الحدود
            'border_primary': '#e2e8f0',
            'border_secondary': '#cbd5e1',
            'border_accent': '#667eea',
            
            # الظلال
            'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'shadow_md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.15)',
            'shadow_xl': '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
            
            # التدرجات
            'gradient_primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'gradient_secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'gradient_success': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'gradient_background': 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            
            # حالات التفاعل
            'hover_overlay': 'rgba(0, 0, 0, 0.05)',
            'active_overlay': 'rgba(0, 0, 0, 0.1)',
            'disabled_overlay': 'rgba(0, 0, 0, 0.2)',
            
            # الشفافية
            'overlay_light': 'rgba(0, 0, 0, 0.05)',
            'overlay_medium': 'rgba(0, 0, 0, 0.1)',
            'overlay_heavy': 'rgba(0, 0, 0, 0.15)',
        }
    
    def inject_custom_css(self):
        """حقن CSS مخصص حسب الثيم الحالي"""
        colors = self.get_theme_colors()
        theme = self.get_current_theme()
        
        css = f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Cairo:wght@300;400;600;700;900&display=swap');
            
            /* ==================== Variables ==================== */
            :root {{
                --primary: {colors['primary']};
                --secondary: {colors['secondary']};
                --accent: {colors['accent']};
                --success: {colors['success']};
                --warning: {colors['warning']};
                --danger: {colors['danger']};
                --info: {colors['info']};
                
                --bg-primary: {colors['background_primary']};
                --bg-secondary: {colors['background_secondary']};
                --bg-tertiary: {colors['background_tertiary']};
                --bg-card: {colors['background_card']};
                
                --text-primary: {colors['text_primary']};
                --text-secondary: {colors['text_secondary']};
                --text-muted: {colors['text_muted']};
                
                --border-primary: {colors['border_primary']};
                --border-secondary: {colors['border_secondary']};
                
                --shadow-sm: {colors['shadow_sm']};
                --shadow-md: {colors['shadow_md']};
                --shadow-lg: {colors['shadow_lg']};
                --shadow-xl: {colors['shadow_xl']};
            }}
            
            /* ==================== Global Styles ==================== */
            * {{
                font-family: 'Cairo', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
            }}
            
            html, body, [class*="css"] {{
                background: {colors['background_primary']} !important;
                color: {colors['text_primary']} !important;
            }}
            
            /* ==================== Main Content ==================== */
            .main {{
                background: {colors['gradient_background']} !important;
                padding: 2rem 3rem !important;
            }}
            
            .main .block-container {{
                max-width: 1400px !important;
                padding-top: 1rem !important;
                padding-bottom: 3rem !important;
            }}
            
            /* ==================== Sidebar ==================== */
            [data-testid="stSidebar"] {{
                background: {colors['background_sidebar']} !important;
                border-right: 1px solid {colors['border_primary']} !important;
                box-shadow: {colors['shadow_lg']} !important;
            }}
            
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
                color: {colors['text_primary']} !important;
            }}
            
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {{
                color: {colors['text_primary']} !important;
                font-weight: 700 !important;
            }}
            
            [data-testid="stSidebar"] label {{
                color: {colors['text_secondary']} !important;
                font-weight: 600 !important;
            }}
            
            /* ==================== Headers ==================== */
            h1, h2, h3, h4, h5, h6 {{
                color: {colors['text_primary']} !important;
                font-weight: 700 !important;
                margin-bottom: 1rem !important;
            }}
            
            h1 {{
                font-size: 2.5rem !important;
                letter-spacing: -0.02em !important;
                line-height: 1.2 !important;
            }}
            
            h2 {{
                font-size: 2rem !important;
                letter-spacing: -0.01em !important;
                padding-bottom: 0.5rem !important;
                border-bottom: 2px solid {colors['border_primary']} !important;
            }}
            
            h3 {{
                font-size: 1.5rem !important;
            }}
            
            /* ==================== Cards ==================== */
            .element-container {{
                margin-bottom: 1rem !important;
            }}
            
            [data-testid="stExpander"] {{
                background: {colors['background_card']} !important;
                border: 1px solid {colors['border_primary']} !important;
                border-radius: 12px !important;
                box-shadow: {colors['shadow_md']} !important;
                margin-bottom: 1rem !important;
                overflow: hidden !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}
            
            [data-testid="stExpander"]:hover {{
                box-shadow: {colors['shadow_lg']} !important;
                transform: translateY(-2px) !important;
                border-color: {colors['border_accent']} !important;
            }}
            
            .streamlit-expanderHeader {{
                background: {colors['background_secondary']} !important;
                color: {colors['text_primary']} !important;
                font-weight: 600 !important;
                font-size: 1.1rem !important;
                padding: 1rem 1.5rem !important;
                border-radius: 12px 12px 0 0 !important;
            }}
            
            .streamlit-expanderHeader:hover {{
                background: {colors['hover_overlay']} !important;
            }}
            
            .streamlit-expanderContent {{
                padding: 1.5rem !important;
                background: {colors['background_card']} !important;
            }}
            
            /* ==================== Buttons ==================== */
            .stButton button {{
                background: {colors['gradient_primary']} !important;
                color: {colors['text_inverse']} !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 0.75rem 2rem !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                letter-spacing: 0.025em !important;
                box-shadow: {colors['shadow_md']} !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                cursor: pointer !important;
            }}
            
            .stButton button:hover {{
                transform: translateY(-2px) !important;
                box-shadow: {colors['shadow_xl']} !important;
                filter: brightness(1.1) !important;
            }}
            
            .stButton button:active {{
                transform: translateY(0) !important;
                box-shadow: {colors['shadow_sm']} !important;
            }}
            
            /* ==================== Download Button ==================== */
            .stDownloadButton button {{
                background: {colors['gradient_success']} !important;
                color: {colors['text_inverse']} !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 0.75rem 2rem !important;
                font-weight: 600 !important;
                box-shadow: {colors['shadow_md']} !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}
            
            .stDownloadButton button:hover {{
                transform: translateY(-2px) !important;
                box-shadow: {colors['shadow_xl']} !important;
                filter: brightness(1.1) !important;
            }}
            
            /* ==================== Metrics ==================== */
            [data-testid="stMetric"] {{
                background: {colors['background_card']} !important;
                padding: 1.5rem !important;
                border-radius: 12px !important;
                border: 1px solid {colors['border_primary']} !important;
                box-shadow: {colors['shadow_md']} !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}
            
            [data-testid="stMetric"]:hover {{
                transform: translateY(-4px) !important;
                box-shadow: {colors['shadow_lg']} !important;
                border-color: {colors['border_accent']} !important;
            }}
            
            [data-testid="stMetric"] label {{
                color: {colors['text_muted']} !important;
                font-size: 0.875rem !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
            }}
            
            [data-testid="stMetric"] [data-testid="stMetricValue"] {{
                color: {colors['text_primary']} !important;
                font-size: 2rem !important;
                font-weight: 700 !important;
                line-height: 1 !important;
            }}
            
            [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
                font-weight: 600 !important;
            }}
            
            /* ==================== Tabs ==================== */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.5rem !important;
                background: {colors['background_card']} !important;
                border-radius: 12px !important;
                padding: 0.5rem !important;
                border: 1px solid {colors['border_primary']} !important;
                box-shadow: {colors['shadow_sm']} !important;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                height: auto !important;
                border-radius: 8px !important;
                padding: 0.75rem 1.5rem !important;
                font-weight: 600 !important;
                color: {colors['text_secondary']} !important;
                background: transparent !important;
                border: none !important;
                transition: all 0.3s ease !important;
            }}
            
            .stTabs [data-baseweb="tab"]:hover {{
                background: {colors['hover_overlay']} !important;
                color: {colors['text_primary']} !important;
            }}
            
            .stTabs [aria-selected="true"] {{
                background: {colors['gradient_primary']} !important;
                color: {colors['text_inverse']} !important;
                box-shadow: {colors['shadow_sm']} !important;
            }}
            
            /* ==================== Alerts ==================== */
            .stAlert {{
                border-radius: 12px !important;
                border: none !important;
                padding: 1rem 1.5rem !important;
                box-shadow: {colors['shadow_md']} !important;
                margin-bottom: 1rem !important;
            }}
            
            .stSuccess {{
                background: linear-gradient(135deg, {colors['success']} 0%, {colors['success']}dd 100%) !important;
                color: white !important;
            }}
            
            .stInfo {{
                background: linear-gradient(135deg, {colors['info']} 0%, {colors['info']}dd 100%) !important;
                color: white !important;
            }}
            
            .stWarning {{
                background: linear-gradient(135deg, {colors['warning']} 0%, {colors['warning']}dd 100%) !important;
                color: white !important;
            }}
            
            .stError {{
                background: linear-gradient(135deg, {colors['danger']} 0%, {colors['danger']}dd 100%) !important;
                color: white !important;
            }}
            
            /* ==================== Dataframes ==================== */
            [data-testid="stDataFrame"] {{
                border-radius: 12px !important;
                overflow: hidden !important;
                border: 1px solid {colors['border_primary']} !important;
                box-shadow: {colors['shadow_md']} !important;
            }}
            
            [data-testid="stDataFrame"] thead tr th {{
                background: {colors['background_secondary']} !important;
                color: {colors['text_primary']} !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
                font-size: 0.875rem !important;
                letter-spacing: 0.05em !important;
                padding: 1rem !important;
                border-bottom: 2px solid {colors['border_accent']} !important;
            }}
            
            [data-testid="stDataFrame"] tbody tr {{
                background: {colors['background_card']} !important;
                color: {colors['text_primary']} !important;
                transition: background-color 0.2s ease !important;
            }}
            
            [data-testid="stDataFrame"] tbody tr:hover {{
                background: {colors['hover_overlay']} !important;
            }}
            
            [data-testid="stDataFrame"] tbody tr td {{
                padding: 0.875rem 1rem !important;
                border-bottom: 1px solid {colors['border_primary']} !important;
            }}
            
            /* ==================== File Uploader ==================== */
            [data-testid="stFileUploader"] {{
                background: {colors['background_card']} !important;
                border: 2px dashed {colors['border_secondary']} !important;
                border-radius: 12px !important;
                padding: 2rem !important;
                transition: all 0.3s ease !important;
            }}
            
            [data-testid="stFileUploader"]:hover {{
                border-color: {colors['border_accent']} !important;
                background: {colors['hover_overlay']} !important;
            }}
            
            [data-testid="stFileUploader"] label {{
                color: {colors['text_primary']} !important;
                font-weight: 600 !important;
                font-size: 1.1rem !important;
            }}
            
            /* ==================== Select / Multiselect ==================== */
            .stSelectbox, .stMultiSelect {{
                margin-bottom: 1rem !important;
            }}
            
            .stSelectbox label, .stMultiSelect label {{
                color: {colors['text_primary']} !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                margin-bottom: 0.5rem !important;
            }}
            
            .stSelectbox > div > div,
            .stMultiSelect > div > div {{
                background: {colors['background_card']} !important;
                border: 1px solid {colors['border_primary']} !important;
                border-radius: 8px !important;
                color: {colors['text_primary']} !important;
            }}
            
            /* ==================== Radio Buttons ==================== */
            .stRadio label {{
                color: {colors['text_primary']} !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
            }}
            
            .stRadio [role="radiogroup"] label {{
                color: {colors['text_secondary']} !important;
                font-weight: 500 !important;
                padding: 0.5rem 1rem !important;
                border-radius: 8px !important;
                transition: all 0.2s ease !important;
            }}
            
            .stRadio [role="radiogroup"] label:hover {{
                background: {colors['hover_overlay']} !important;
                color: {colors['text_primary']} !important;
            }}
            
            /* ==================== Checkbox ==================== */
            .stCheckbox label {{
                color: {colors['text_secondary']} !important;
                font-weight: 500 !important;
            }}
            
            /* ==================== Slider ==================== */
            .stSlider label {{
                color: {colors['text_primary']} !important;
                font-weight: 600 !important;
            }}
            
            .stSlider [data-baseweb="slider"] {{
                background: {colors['border_primary']} !important;
            }}
            
            /* ==================== Text Input ==================== */
            .stTextInput label, .stTextArea label, .stNumberInput label {{
                color: {colors['text_primary']} !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
            }}
            
            .stTextInput input, .stTextArea textarea, .stNumberInput input {{
                background: {colors['background_card']} !important;
                border: 1px solid {colors['border_primary']} !important;
                border-radius: 8px !important;
                color: {colors['text_primary']} !important;
                padding: 0.75rem 1rem !important;
            }}
            
            .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {{
                border-color: {colors['border_accent']} !important;
                box-shadow: 0 0 0 3px {colors['primary']}22 !important;
            }}
            
            /* ==================== Divider ==================== */
            hr {{
                border: none !important;
                height: 2px !important;
                background: {colors['gradient_primary']} !important;
                opacity: 0.3 !important;
                margin: 2rem 0 !important;
            }}
            
            /* ==================== Spinner ==================== */
            .stSpinner > div {{
                border-top-color: {colors['primary']} !important;
            }}
            
            /* ==================== Progress Bar ==================== */
            .stProgress > div > div {{
                background: {colors['gradient_primary']} !important;
            }}
            
            /* ==================== Scrollbar ==================== */
            ::-webkit-scrollbar {{
                width: 10px !important;
                height: 10px !important;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {colors['background_secondary']} !important;
                border-radius: 5px !important;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {colors['border_secondary']} !important;
                border-radius: 5px !important;
                transition: background 0.3s ease !important;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {colors['primary']} !important;
            }}
            
            /* ==================== Custom Classes ==================== */
            .glass-card {{
                background: {colors['overlay_light']} !important;
                backdrop-filter: blur(10px) !important;
                border: 1px solid {colors['border_primary']} !important;
                border-radius: 16px !important;
                padding: 2rem !important;
                box-shadow: {colors['shadow_xl']} !important;
            }}
            
            .gradient-text {{
                background: {colors['gradient_primary']} !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                background-clip: text !important;
            }}
            
            .pulse {{
                animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite !important;
            }}
            
            @keyframes pulse {{
                0%, 100% {{
                    opacity: 1 !important;
                }}
                50% {{
                    opacity: .5 !important;
                }}
            }}
            
            /* ==================== Animations ==================== */
            @keyframes fadeIn {{
                from {{
                    opacity: 0 !important;
                    transform: translateY(10px) !important;
                }}
                to {{
                    opacity: 1 !important;
                    transform: translateY(0) !important;
                }}
            }}
            
            .fade-in {{
                animation: fadeIn 0.5s ease-out !important;
            }}
            
            /* ==================== Responsive ==================== */
            @media (max-width: 768px) {{
                .main .block-container {{
                    padding: 1rem !important;
                }}
                
                h1 {{
                    font-size: 2rem !important;
                }}
                
                h2 {{
                    font-size: 1.5rem !important;
                }}
                
                [data-testid="stMetric"] {{
                    padding: 1rem !important;
                }}
            }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def render_theme_toggle(self):
        """عرض زر تبديل الثيم"""
        theme = self.get_current_theme()
        colors = self.get_theme_colors()
        
        # أيقونة حسب الوضع الحالي
        icon = "🌙" if theme == "light" else "☀️"
        text = "الوضع الليلي" if theme == "light" else "الوضع النهاري"
        
        button_html = f"""
        <style>
            .theme-toggle {{
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 999999;
                background: {colors['gradient_primary']};
                color: {colors['text_inverse']};
                border: none;
                border-radius: 50px;
                padding: 0.75rem 1.5rem;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                box-shadow: {colors['shadow_lg']};
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .theme-toggle:hover {{
                transform: translateY(-2px);
                box-shadow: {colors['shadow_xl']};
                filter: brightness(1.1);
            }}
            
            .theme-toggle:active {{
                transform: translateY(0);
            }}
        </style>
        """
        
        st.markdown(button_html, unsafe_allow_html=True)
        
        # زر التبديل
        if st.button(f"{icon} {text}", key="theme_toggle_btn", use_container_width=False):
            self.toggle_theme()


# إنشاء instance عام
theme_manager = ThemeManager()
