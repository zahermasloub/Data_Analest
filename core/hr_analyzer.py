"""
محلل بيانات الموارد البشرية
يوفر فحوصات متخصصة لبيانات الموظفين والرواتب والحضور
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class HRAnalyzer:
    """محلل بيانات الموارد البشرية مع فحوصات متنوعة"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.results = {}
    
    def analyze_salaries(self, salary_column: str) -> Dict[str, Any]:
        """
        تحليل الرواتب
        - الراتب المتوسط والوسيط
        - نطاق الرواتب (أعلى/أقل)
        - معامل التباين
        - توزيع الرواتب
        """
        if salary_column not in self.data.columns:
            return {"error": f"العمود {salary_column} غير موجود"}
        
        salaries = pd.to_numeric(self.data[salary_column], errors='coerce').dropna()
        
        if len(salaries) == 0:
            return {"error": "لا توجد بيانات رواتب صالحة"}
        
        results = {
            "المتوسط": float(salaries.mean()),
            "الوسيط": float(salaries.median()),
            "أعلى راتب": float(salaries.max()),
            "أقل راتب": float(salaries.min()),
            "الانحراف المعياري": float(salaries.std()),
            "معامل التباين": float((salaries.std() / salaries.mean()) * 100),
            "الربع الأول": float(salaries.quantile(0.25)),
            "الربع الثالث": float(salaries.quantile(0.75)),
            "عدد الموظفين": len(salaries)
        }
        
        # تحديد الرواتب الشاذة
        Q1 = salaries.quantile(0.25)
        Q3 = salaries.quantile(0.75)
        IQR = Q3 - Q1
        outliers = salaries[(salaries < Q1 - 1.5 * IQR) | (salaries > Q3 + 1.5 * IQR)]
        results["عدد الرواتب الشاذة"] = len(outliers)
        
        return results
    
    def analyze_attendance(self, attendance_column: str, threshold: int = 20) -> Dict[str, Any]:
        """
        تحليل الحضور
        - متوسط أيام الحضور
        - الموظفين بحضور ضعيف
        - معدل الحضور العام
        """
        if attendance_column not in self.data.columns:
            return {"error": f"العمود {attendance_column} غير موجود"}
        
        attendance = pd.to_numeric(self.data[attendance_column], errors='coerce').dropna()
        
        if len(attendance) == 0:
            return {"error": "لا توجد بيانات حضور صالحة"}
        
        results = {
            "متوسط الحضور": float(attendance.mean()),
            "أعلى حضور": float(attendance.max()),
            "أقل حضور": float(attendance.min()),
            "الانحراف المعياري": float(attendance.std()),
            "عدد الموظفين": len(attendance)
        }
        
        # الموظفين بحضور ضعيف
        poor_attendance = attendance[attendance < threshold]
        results["موظفين بحضور ضعيف"] = len(poor_attendance)
        results["نسبة الحضور الضعيف"] = float((len(poor_attendance) / len(attendance)) * 100)
        
        return results
    
    def analyze_departments(self, dept_column: str) -> Dict[str, Any]:
        """
        تحليل الأقسام
        - عدد الموظفين في كل قسم
        - توزيع الأقسام
        - أكبر وأصغر قسم
        """
        if dept_column not in self.data.columns:
            return {"error": f"العمود {dept_column} غير موجود"}
        
        dept_counts = self.data[dept_column].value_counts()
        
        results = {
            "عدد الأقسام": len(dept_counts),
            "توزيع الأقسام": dept_counts.to_dict(),
            "أكبر قسم": dept_counts.index[0],
            "عدد موظفي أكبر قسم": int(dept_counts.iloc[0]),
            "أصغر قسم": dept_counts.index[-1],
            "عدد موظفي أصغر قسم": int(dept_counts.iloc[-1]),
            "متوسط الموظفين بالقسم": float(dept_counts.mean())
        }
        
        return results
    
    def analyze_performance(self, performance_column: str) -> Dict[str, Any]:
        """
        تحليل الأداء
        - متوسط التقييمات
        - توزيع مستويات الأداء
        - الموظفين المتميزين
        """
        if performance_column not in self.data.columns:
            return {"error": f"العمود {performance_column} غير موجود"}
        
        performance = pd.to_numeric(self.data[performance_column], errors='coerce').dropna()
        
        if len(performance) == 0:
            return {"error": "لا توجد بيانات أداء صالحة"}
        
        results = {
            "متوسط الأداء": float(performance.mean()),
            "أعلى تقييم": float(performance.max()),
            "أقل تقييم": float(performance.min()),
            "الانحراف المعياري": float(performance.std()),
            "عدد الموظفين": len(performance)
        }
        
        # تصنيف مستويات الأداء
        excellent = performance[performance >= 90]
        good = performance[(performance >= 70) & (performance < 90)]
        average = performance[(performance >= 50) & (performance < 70)]
        poor = performance[performance < 50]
        
        results["ممتاز (90+)"] = len(excellent)
        results["جيد (70-89)"] = len(good)
        results["متوسط (50-69)"] = len(average)
        results["ضعيف (<50)"] = len(poor)
        
        return results
    
    def analyze_gender_distribution(self, gender_column: str) -> Dict[str, Any]:
        """
        تحليل التوزيع حسب الجنس
        """
        if gender_column not in self.data.columns:
            return {"error": f"العمود {gender_column} غير موجود"}
        
        gender_counts = self.data[gender_column].value_counts()
        total = len(self.data)
        
        results = {
            "التوزيع": gender_counts.to_dict(),
            "النسب المئوية": {k: float((v/total)*100) for k, v in gender_counts.items()},
            "الإجمالي": total
        }
        
        return results
    
    def analyze_experience(self, experience_column: str) -> Dict[str, Any]:
        """
        تحليل سنوات الخبرة
        """
        if experience_column not in self.data.columns:
            return {"error": f"العمود {experience_column} غير موجود"}
        
        experience = pd.to_numeric(self.data[experience_column], errors='coerce').dropna()
        
        if len(experience) == 0:
            return {"error": "لا توجد بيانات خبرة صالحة"}
        
        results = {
            "متوسط سنوات الخبرة": float(experience.mean()),
            "أعلى خبرة": float(experience.max()),
            "أقل خبرة": float(experience.min()),
            "الانحراف المعياري": float(experience.std())
        }
        
        # تصنيف الخبرات
        junior = experience[experience < 3]
        mid = experience[(experience >= 3) & (experience < 7)]
        senior = experience[(experience >= 7) & (experience < 10)]
        expert = experience[experience >= 10]
        
        results["مبتدئ (<3 سنوات)"] = len(junior)
        results["متوسط (3-6 سنوات)"] = len(mid)
        results["خبير (7-9 سنوات)"] = len(senior)
        results["محترف (10+ سنوات)"] = len(expert)
        
        return results
    
    def find_salary_gaps(self, salary_column: str, dept_column: str) -> pd.DataFrame:
        """
        اكتشاف الفجوات في الرواتب بين الأقسام
        """
        if salary_column not in self.data.columns or dept_column not in self.data.columns:
            return pd.DataFrame({"error": ["الأعمدة المطلوبة غير موجودة"]})
        
        dept_salaries = self.data.groupby(dept_column)[salary_column].agg(['mean', 'median', 'std', 'count'])
        dept_salaries.columns = ['متوسط الراتب', 'الوسيط', 'الانحراف المعياري', 'عدد الموظفين']
        dept_salaries = dept_salaries.sort_values('متوسط الراتب', ascending=False)
        
        # حساب الفجوة مع القسم الأعلى
        max_salary = dept_salaries['متوسط الراتب'].max()
        dept_salaries['الفجوة'] = max_salary - dept_salaries['متوسط الراتب']
        dept_salaries['نسبة الفجوة %'] = (dept_salaries['الفجوة'] / max_salary * 100).round(2)
        
        return dept_salaries.reset_index()
    
    def find_high_performers(self, performance_column: str, threshold: float = 85) -> pd.DataFrame:
        """
        تحديد الموظفين المتميزين
        """
        if performance_column not in self.data.columns:
            return pd.DataFrame({"error": ["العمود المطلوب غير موجود"]})
        
        high_performers = self.data[pd.to_numeric(self.data[performance_column], errors='coerce') >= threshold].copy()
        
        if len(high_performers) == 0:
            return pd.DataFrame({"message": ["لا يوجد موظفين متميزين بالحد المطلوب"]})
        
        return high_performers.sort_values(performance_column, ascending=False)
    
    def calculate_turnover_risk(self, satisfaction_column: str, performance_column: str) -> pd.DataFrame:
        """
        تقييم مخاطر ترك العمل
        بناءً على مستوى الرضا والأداء
        """
        if satisfaction_column not in self.data.columns or performance_column not in self.data.columns:
            return pd.DataFrame({"error": ["الأعمدة المطلوبة غير موجودة"]})
        
        df = self.data.copy()
        df['satisfaction_num'] = pd.to_numeric(df[satisfaction_column], errors='coerce')
        df['performance_num'] = pd.to_numeric(df[performance_column], errors='coerce')
        
        # حساب مستوى المخاطرة
        def calculate_risk(row):
            if pd.isna(row['satisfaction_num']) or pd.isna(row['performance_num']):
                return 'غير معروف'
            
            if row['satisfaction_num'] < 50 and row['performance_num'] < 60:
                return 'مخاطرة عالية جداً'
            elif row['satisfaction_num'] < 50:
                return 'مخاطرة عالية'
            elif row['satisfaction_num'] < 70 and row['performance_num'] > 80:
                return 'مخاطرة متوسطة'
            else:
                return 'مخاطرة منخفضة'
        
        df['مستوى المخاطرة'] = df.apply(calculate_risk, axis=1)
        
        # إحصائيات المخاطر
        risk_counts = df['مستوى المخاطرة'].value_counts()
        
        return df[['مستوى المخاطرة']].join(df[[satisfaction_column, performance_column]])
