"""
مولد الفحوصات الذكي باستخدام AI
يسمح للموظفين بإنشاء فحوصات جديدة بدون خبرة برمجية
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd


class SmartTestGenerator:
    """
    مولد فحوصات ذكي يحول الوصف النصي إلى كود قابل للتنفيذ
    """
    
    def __init__(self, storage_path: str = "custom_tests.json"):
        self.storage_path = storage_path
        self.custom_tests = self._load_custom_tests()
        
        # قوالب الفحوصات الجاهزة
        self.templates = {
            "مقارنة": self._template_comparison,
            "عدد": self._template_count,
            "متوسط": self._template_average,
            "مجموع": self._template_sum,
            "نسبة": self._template_percentage,
            "تصفية": self._template_filter,
            "تجميع": self._template_groupby,
            "أعلى_قيم": self._template_top_values,
            "أقل_قيم": self._template_bottom_values,
            "نطاق": self._template_range,
        }
    
    def _load_custom_tests(self) -> Dict:
        """تحميل الفحوصات المخصصة من ملف JSON"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_custom_tests(self):
        """حفظ الفحوصات المخصصة في ملف JSON"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.custom_tests, f, ensure_ascii=False, indent=2)
    
    def parse_natural_language(self, description: str) -> Dict[str, Any]:
        """
        تحليل الوصف النصي واستخراج المعلومات
        
        أمثلة:
        - "أريد عدد الموظفين في قسم المبيعات"
        - "احسب متوسط الرواتب للموظفين"
        - "اعرض الموظفين الذين رواتبهم أكبر من 5000"
        """
        description_lower = description.lower()
        
        result = {
            "type": None,
            "column": None,
            "condition": None,
            "value": None,
            "operation": None
        }
        
        # تحديد نوع العملية
        if any(word in description_lower for word in ["عدد", "كم"]):
            result["type"] = "عدد"
        elif any(word in description_lower for word in ["متوسط", "معدل"]):
            result["type"] = "متوسط"
        elif any(word in description_lower for word in ["مجموع", "إجمالي"]):
            result["type"] = "مجموع"
        elif any(word in description_lower for word in ["نسبة", "معدل"]):
            result["type"] = "نسبة"
        elif any(word in description_lower for word in ["أعلى", "أكبر", "الأفضل"]):
            result["type"] = "أعلى_قيم"
        elif any(word in description_lower for word in ["أقل", "أصغر", "الأسوأ"]):
            result["type"] = "أقل_قيم"
        elif any(word in description_lower for word in ["بين", "نطاق", "من"]):
            result["type"] = "نطاق"
        elif any(word in description_lower for word in ["اعرض", "أظهر", "اختر"]):
            result["type"] = "تصفية"
        elif any(word in description_lower for word in ["حسب", "لكل", "مجموعة"]):
            result["type"] = "تجميع"
        
        # استخراج الشروط
        if "أكبر من" in description_lower or ">" in description:
            result["condition"] = ">"
        elif "أقل من" in description_lower or "<" in description:
            result["condition"] = "<"
        elif "يساوي" in description_lower or "=" in description:
            result["condition"] = "=="
        elif "يحتوي" in description_lower:
            result["condition"] = "contains"
        
        return result
    
    def create_test_from_template(
        self,
        test_name: str,
        description: str,
        template_type: str,
        column_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        إنشاء فحص جديد من قالب جاهز
        
        المعاملات:
        - test_name: اسم الفحص
        - description: وصف الفحص
        - template_type: نوع القالب (مقارنة، عدد، متوسط، إلخ)
        - column_name: اسم العمود المراد فحصه
        - **kwargs: معاملات إضافية حسب نوع القالب
        """
        if template_type not in self.templates:
            return {"error": f"القالب {template_type} غير موجود"}
        
        test_config = {
            "name": test_name,
            "description": description,
            "template": template_type,
            "column": column_name,
            "parameters": kwargs,
            "created_at": datetime.now().isoformat(),
            "enabled": True
        }
        
        # حفظ الفحص
        test_id = f"custom_test_{len(self.custom_tests) + 1}"
        self.custom_tests[test_id] = test_config
        self._save_custom_tests()
        
        return {"success": True, "test_id": test_id, "config": test_config}
    
    def execute_test(self, test_id: str, data: pd.DataFrame) -> Dict[str, Any]:
        """تنفيذ فحص مخصص على البيانات"""
        if test_id not in self.custom_tests:
            return {"error": "الفحص غير موجود"}
        
        test_config = self.custom_tests[test_id]
        
        if not test_config.get("enabled", True):
            return {"error": "الفحص معطل"}
        
        template_type = test_config["template"]
        column = test_config["column"]
        params = test_config["parameters"]
        
        if template_type not in self.templates:
            return {"error": "القالب غير موجود"}
        
        try:
            # تنفيذ القالب
            template_func = self.templates[template_type]
            result = template_func(data, column, **params)
            
            return {
                "success": True,
                "test_name": test_config["name"],
                "description": test_config["description"],
                "result": result
            }
        except Exception as e:
            return {"error": f"خطأ في التنفيذ: {str(e)}"}
    
    # ==================== قوالب الفحوصات ====================
    
    def _template_comparison(
        self,
        data: pd.DataFrame,
        column: str,
        operator: str,
        value: Any
    ) -> Dict[str, Any]:
        """قالب المقارنة: مقارنة قيم عمود بقيمة محددة"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        col_data = pd.to_numeric(data[column], errors='coerce')
        
        if operator == ">":
            filtered = data[col_data > value]
        elif operator == "<":
            filtered = data[col_data < value]
        elif operator == "==":
            filtered = data[col_data == value]
        elif operator == ">=":
            filtered = data[col_data >= value]
        elif operator == "<=":
            filtered = data[col_data <= value]
        else:
            return {"error": "المعامل غير صحيح"}
        
        return {
            "count": len(filtered),
            "percentage": float((len(filtered) / len(data)) * 100),
            "data": filtered
        }
    
    def _template_count(
        self,
        data: pd.DataFrame,
        column: str,
        value: Optional[Any] = None
    ) -> Dict[str, Any]:
        """قالب العد: عد القيم في عمود"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        if value is None:
            # عد جميع القيم
            result = {
                "total_count": len(data),
                "non_null_count": data[column].notna().sum(),
                "null_count": data[column].isna().sum(),
                "unique_count": data[column].nunique()
            }
        else:
            # عد قيمة محددة
            count = (data[column] == value).sum()
            result = {
                "value": value,
                "count": int(count),
                "percentage": float((count / len(data)) * 100)
            }
        
        return result
    
    def _template_average(
        self,
        data: pd.DataFrame,
        column: str,
        condition_column: Optional[str] = None,
        condition_value: Optional[Any] = None
    ) -> Dict[str, Any]:
        """قالب المتوسط: حساب متوسط عمود رقمي"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        # تطبيق شرط إذا وجد
        if condition_column and condition_value:
            filtered_data = data[data[condition_column] == condition_value]
        else:
            filtered_data = data
        
        col_data = pd.to_numeric(filtered_data[column], errors='coerce')
        
        return {
            "average": float(col_data.mean()),
            "median": float(col_data.median()),
            "std": float(col_data.std()),
            "min": float(col_data.min()),
            "max": float(col_data.max()),
            "count": len(col_data.dropna())
        }
    
    def _template_sum(
        self,
        data: pd.DataFrame,
        column: str,
        condition_column: Optional[str] = None,
        condition_value: Optional[Any] = None
    ) -> Dict[str, Any]:
        """قالب المجموع: حساب مجموع عمود رقمي"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        if condition_column and condition_value:
            filtered_data = data[data[condition_column] == condition_value]
        else:
            filtered_data = data
        
        col_data = pd.to_numeric(filtered_data[column], errors='coerce')
        
        return {
            "sum": float(col_data.sum()),
            "count": len(col_data.dropna()),
            "average": float(col_data.mean())
        }
    
    def _template_percentage(
        self,
        data: pd.DataFrame,
        column: str,
        value: Any
    ) -> Dict[str, Any]:
        """قالب النسبة: حساب نسبة قيمة معينة"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        count = (data[column] == value).sum()
        total = len(data)
        
        return {
            "value": value,
            "count": int(count),
            "total": total,
            "percentage": float((count / total) * 100)
        }
    
    def _template_filter(
        self,
        data: pd.DataFrame,
        column: str,
        condition: str,
        value: Any
    ) -> Dict[str, Any]:
        """قالب التصفية: تصفية البيانات حسب شرط"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        if condition == "contains":
            filtered = data[data[column].astype(str).str.contains(str(value), na=False)]
        elif condition == "==":
            filtered = data[data[column] == value]
        elif condition == "!=":
            filtered = data[data[column] != value]
        else:
            return {"error": "الشرط غير صحيح"}
        
        return {
            "count": len(filtered),
            "percentage": float((len(filtered) / len(data)) * 100),
            "data": filtered
        }
    
    def _template_groupby(
        self,
        data: pd.DataFrame,
        column: str,
        agg_column: str,
        operation: str = "count"
    ) -> Dict[str, Any]:
        """قالب التجميع: تجميع البيانات حسب عمود"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        if operation == "count":
            result = data[column].value_counts().to_dict()
        elif operation == "sum" and agg_column in data.columns:
            result = data.groupby(column)[agg_column].sum().to_dict()
        elif operation == "mean" and agg_column in data.columns:
            result = data.groupby(column)[agg_column].mean().to_dict()
        else:
            return {"error": "العملية غير صحيحة"}
        
        return {
            "groups": result,
            "total_groups": len(result)
        }
    
    def _template_top_values(
        self,
        data: pd.DataFrame,
        column: str,
        n: int = 10
    ) -> Dict[str, Any]:
        """قالب أعلى القيم"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        col_data = pd.to_numeric(data[column], errors='coerce')
        top_indices = col_data.nlargest(n).index
        top_data = data.loc[top_indices]
        
        return {
            "count": len(top_data),
            "data": top_data
        }
    
    def _template_bottom_values(
        self,
        data: pd.DataFrame,
        column: str,
        n: int = 10
    ) -> Dict[str, Any]:
        """قالب أقل القيم"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        col_data = pd.to_numeric(data[column], errors='coerce')
        bottom_indices = col_data.nsmallest(n).index
        bottom_data = data.loc[bottom_indices]
        
        return {
            "count": len(bottom_data),
            "data": bottom_data
        }
    
    def _template_range(
        self,
        data: pd.DataFrame,
        column: str,
        min_value: float,
        max_value: float
    ) -> Dict[str, Any]:
        """قالب النطاق: البحث في نطاق معين"""
        if column not in data.columns:
            return {"error": f"العمود {column} غير موجود"}
        
        col_data = pd.to_numeric(data[column], errors='coerce')
        filtered = data[(col_data >= min_value) & (col_data <= max_value)]
        
        return {
            "count": len(filtered),
            "percentage": float((len(filtered) / len(data)) * 100),
            "min": min_value,
            "max": max_value,
            "data": filtered
        }
    
    # ==================== إدارة الفحوصات ====================
    
    def get_all_tests(self) -> Dict[str, Any]:
        """الحصول على جميع الفحوصات المخصصة"""
        return self.custom_tests
    
    def get_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على فحص محدد"""
        return self.custom_tests.get(test_id)
    
    def delete_test(self, test_id: str) -> bool:
        """حذف فحص مخصص"""
        if test_id in self.custom_tests:
            del self.custom_tests[test_id]
            self._save_custom_tests()
            return True
        return False
    
    def toggle_test(self, test_id: str) -> bool:
        """تفعيل/تعطيل فحص"""
        if test_id in self.custom_tests:
            self.custom_tests[test_id]["enabled"] = not self.custom_tests[test_id].get("enabled", True)
            self._save_custom_tests()
            return True
        return False
    
    def get_available_templates(self) -> List[str]:
        """الحصول على قائمة القوالب المتاحة"""
        return list(self.templates.keys())
