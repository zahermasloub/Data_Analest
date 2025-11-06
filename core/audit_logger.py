# -*- coding: utf-8 -*-
"""
📝 نظام تسجيل العمليات - Audit Trail System
==============================================
تسجيل شامل لجميع العمليات التحليلية

Libraries Used:
- pandas>=2.1.0
- duckdb>=0.9.0 (اختياري - للأداء العالي)
- json (built-in)
- datetime (built-in)
- pathlib (built-in)

Install if missing:
pip install pandas duckdb
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

# محاولة استيراد duckdb (اختياري)
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    print("⚠️ duckdb غير متوفر - سيتم استخدام CSV للتسجيل")


class AuditLogger:
    """نظام تسجيل العمليات"""
    
    def __init__(self, log_dir: str = "outputs/audit_logs"):
        """
        تهيئة نظام التسجيل
        
        Args:
            log_dir: مجلد حفظ السجلات
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # ملفات التسجيل
        self.analysis_log_file = self.log_dir / "analysis_runs.csv"
        self.match_log_file = self.log_dir / "match_details.csv"
        self.error_log_file = self.log_dir / "errors.json"
        
        # قاعدة بيانات DuckDB (اختياري)
        self.db_file = self.log_dir / "audit.duckdb"
        self.use_duckdb = DUCKDB_AVAILABLE
        
        # تهيئة الجداول
        self._init_tables()
    
    def _init_tables(self):
        """تهيئة جداول التسجيل"""
        
        # جدول التحليلات
        if not self.analysis_log_file.exists():
            analysis_df = pd.DataFrame(columns=[
                'RunID',
                'Timestamp',
                'AwardsFiles',
                'BankFile',
                'TotalAwards',
                'TotalBankRecords',
                'ExactMatches',
                'FuzzyMatches',
                'RLMatches',
                'UnmatchedAwards',
                'SuspectedDuplicates',
                'ConfirmedDuplicates',
                'TimeWindowDays',
                'FuzzyThreshold',
                'UseRecordLinkage',
                'ExecutionTimeSeconds',
                'UserName',
                'Status'
            ])
            analysis_df.to_csv(self.analysis_log_file, index=False, encoding='utf-8-sig')
        
        # جدول المطابقات
        if not self.match_log_file.exists():
            match_df = pd.DataFrame(columns=[
                'MatchID',
                'RunID',
                'Timestamp',
                'OwnerName',
                'AwardAmount',
                'EntryDate',
                'BankReference',
                'BeneficiaryName',
                'TransferAmount',
                'TransferDate',
                'MatchType',
                'MatchScore',
                'DateDiff'
            ])
            match_df.to_csv(self.match_log_file, index=False, encoding='utf-8-sig')
        
        # قاعدة DuckDB
        if self.use_duckdb:
            self._init_duckdb_tables()
    
    def _init_duckdb_tables(self):
        """تهيئة جداول DuckDB"""
        try:
            conn = duckdb.connect(str(self.db_file))
            
            # جدول التحليلات
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_runs (
                    RunID VARCHAR PRIMARY KEY,
                    Timestamp TIMESTAMP,
                    AwardsFiles VARCHAR,
                    BankFile VARCHAR,
                    TotalAwards INTEGER,
                    TotalBankRecords INTEGER,
                    ExactMatches INTEGER,
                    FuzzyMatches INTEGER,
                    RLMatches INTEGER,
                    UnmatchedAwards INTEGER,
                    SuspectedDuplicates INTEGER,
                    ConfirmedDuplicates INTEGER,
                    TimeWindowDays INTEGER,
                    FuzzyThreshold INTEGER,
                    UseRecordLinkage BOOLEAN,
                    ExecutionTimeSeconds DOUBLE,
                    UserName VARCHAR,
                    Status VARCHAR
                )
            """)
            
            # جدول المطابقات
            conn.execute("""
                CREATE TABLE IF NOT EXISTS match_details (
                    MatchID VARCHAR PRIMARY KEY,
                    RunID VARCHAR,
                    Timestamp TIMESTAMP,
                    OwnerName VARCHAR,
                    AwardAmount DOUBLE,
                    EntryDate DATE,
                    BankReference VARCHAR,
                    BeneficiaryName VARCHAR,
                    TransferAmount DOUBLE,
                    TransferDate DATE,
                    MatchType VARCHAR,
                    MatchScore INTEGER,
                    DateDiff INTEGER,
                    FOREIGN KEY (RunID) REFERENCES analysis_runs(RunID)
                )
            """)
            
            conn.close()
            print("✅ تم تهيئة قاعدة بيانات DuckDB")
            
        except Exception as e:
            print(f"⚠️ خطأ في تهيئة DuckDB: {str(e)}")
            self.use_duckdb = False
    
    def log_analysis_run(
        self,
        awards_files: List[str],
        bank_file: str,
        statistics: Dict[str, Any],
        time_window_days: int,
        fuzzy_threshold: int,
        use_record_linkage: bool,
        execution_time: float,
        user_name: str = "System",
        status: str = "Success"
    ) -> str:
        """
        تسجيل تشغيل تحليل جديد
        
        Library Used: pandas, duckdb (optional)
        
        Args:
            awards_files: ملفات الجوائز
            bank_file: ملف البنك
            statistics: إحصائيات النتائج
            time_window_days: نافذة المطابقة
            fuzzy_threshold: عتبة المطابقة الضبابية
            use_record_linkage: استخدام RL
            execution_time: وقت التنفيذ (ثواني)
            user_name: اسم المستخدم
            status: حالة التشغيل
            
        Returns:
            RunID الفريد
        """
        run_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # بيانات السجل
        log_entry = {
            'RunID': run_id,
            'Timestamp': timestamp,
            'AwardsFiles': ';'.join(awards_files),
            'BankFile': bank_file,
            'TotalAwards': statistics.get('total_awards', 0),
            'TotalBankRecords': statistics.get('total_bank_records', 0),
            'ExactMatches': statistics.get('exact_matches', 0),
            'FuzzyMatches': statistics.get('fuzzy_matches', 0),
            'RLMatches': statistics.get('rl_matches', 0),
            'UnmatchedAwards': statistics.get('unmatched_awards', 0),
            'SuspectedDuplicates': statistics.get('suspected_duplicates', 0),
            'ConfirmedDuplicates': statistics.get('confirmed_duplicates', 0),
            'TimeWindowDays': time_window_days,
            'FuzzyThreshold': fuzzy_threshold,
            'UseRecordLinkage': use_record_linkage,
            'ExecutionTimeSeconds': execution_time,
            'UserName': user_name,
            'Status': status
        }
        
        # حفظ في CSV
        try:
            existing_df = pd.read_csv(self.analysis_log_file, encoding='utf-8-sig')
            new_row = pd.DataFrame([log_entry])
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            updated_df.to_csv(self.analysis_log_file, index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"⚠️ خطأ في حفظ CSV: {str(e)}")
        
        # حفظ في DuckDB
        if self.use_duckdb:
            try:
                conn = duckdb.connect(str(self.db_file))
                df = pd.DataFrame([log_entry])
                conn.execute("INSERT INTO analysis_runs SELECT * FROM df")
                conn.close()
            except Exception as e:
                print(f"⚠️ خطأ في حفظ DuckDB: {str(e)}")
        
        print(f"📝 تم تسجيل التحليل: {run_id}")
        return run_id
    
    def log_matches(
        self,
        run_id: str,
        matches_df: pd.DataFrame
    ):
        """
        تسجيل تفاصيل المطابقات
        
        Args:
            run_id: معرف التشغيل
            matches_df: DataFrame المطابقات
        """
        if len(matches_df) == 0:
            return
        
        timestamp = datetime.now()
        
        # تحضير البيانات
        match_logs = []
        for _, match in matches_df.iterrows():
            match_log = {
                'MatchID': str(uuid.uuid4()),
                'RunID': run_id,
                'Timestamp': timestamp,
                'OwnerName': match.get('OwnerName', ''),
                'AwardAmount': match.get('AwardAmount', 0),
                'EntryDate': match.get('EntryDate'),
                'BankReference': match.get('BankReference', ''),
                'BeneficiaryName': match.get('BeneficiaryName', ''),
                'TransferAmount': match.get('TransferAmount', 0),
                'TransferDate': match.get('TransferDate'),
                'MatchType': match.get('MatchType', ''),
                'MatchScore': match.get('MatchScore', 0),
                'DateDiff': match.get('DateDiff', 0)
            }
            match_logs.append(match_log)
        
        # حفظ في CSV
        try:
            existing_df = pd.read_csv(self.match_log_file, encoding='utf-8-sig')
            new_df = pd.DataFrame(match_logs)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df.to_csv(self.match_log_file, index=False, encoding='utf-8-sig')
        except Exception as e:
            print(f"⚠️ خطأ في حفظ CSV: {str(e)}")
        
        # حفظ في DuckDB
        if self.use_duckdb:
            try:
                conn = duckdb.connect(str(self.db_file))
                df = pd.DataFrame(match_logs)
                conn.execute("INSERT INTO match_details SELECT * FROM df")
                conn.close()
            except Exception as e:
                print(f"⚠️ خطأ في حفظ DuckDB: {str(e)}")
        
        print(f"📝 تم تسجيل {len(match_logs)} مطابقة")
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ):
        """
        تسجيل الأخطاء
        
        Args:
            error_type: نوع الخطأ
            error_message: رسالة الخطأ
            context: سياق الخطأ
        """
        error_entry = {
            'ErrorID': str(uuid.uuid4()),
            'Timestamp': datetime.now().isoformat(),
            'ErrorType': error_type,
            'ErrorMessage': error_message,
            'Context': context
        }
        
        # حفظ في JSON
        try:
            errors = []
            if self.error_log_file.exists():
                with open(self.error_log_file, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
            
            errors.append(error_entry)
            
            with open(self.error_log_file, 'w', encoding='utf-8') as f:
                json.dump(errors, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ خطأ في تسجيل الأخطاء: {str(e)}")
    
    def get_recent_runs(self, limit: int = 10) -> pd.DataFrame:
        """
        استرجاع آخر التحليلات
        
        Library Used: pandas, duckdb (optional)
        
        Args:
            limit: عدد السجلات
            
        Returns:
            DataFrame بآخر التحليلات
        """
        if self.use_duckdb:
            try:
                conn = duckdb.connect(str(self.db_file))
                df = conn.execute(f"""
                    SELECT * FROM analysis_runs 
                    ORDER BY Timestamp DESC 
                    LIMIT {limit}
                """).df()
                conn.close()
                return df
            except Exception as e:
                print(f"⚠️ خطأ في قراءة DuckDB: {str(e)}")
        
        # Fallback إلى CSV
        try:
            df = pd.read_csv(self.analysis_log_file, encoding='utf-8-sig')
            return df.tail(limit)
        except:
            return pd.DataFrame()
    
    def get_run_details(self, run_id: str) -> Dict[str, Any]:
        """
        استرجاع تفاصيل تشغيل محدد
        
        Args:
            run_id: معرف التشغيل
            
        Returns:
            قاموس بالتفاصيل
        """
        if self.use_duckdb:
            try:
                conn = duckdb.connect(str(self.db_file))
                
                # بيانات التشغيل
                run_df = conn.execute(f"""
                    SELECT * FROM analysis_runs 
                    WHERE RunID = '{run_id}'
                """).df()
                
                # المطابقات المرتبطة
                matches_df = conn.execute(f"""
                    SELECT * FROM match_details 
                    WHERE RunID = '{run_id}'
                """).df()
                
                conn.close()
                
                return {
                    'run_info': run_df.to_dict('records')[0] if len(run_df) > 0 else {},
                    'matches': matches_df
                }
            except Exception as e:
                print(f"⚠️ خطأ في قراءة DuckDB: {str(e)}")
        
        return {'run_info': {}, 'matches': pd.DataFrame()}
    
    def generate_report(self, run_id: Optional[str] = None) -> str:
        """
        توليد تقرير نصي
        
        Args:
            run_id: معرف تشغيل محدد (اختياري)
            
        Returns:
            نص التقرير
        """
        if run_id:
            details = self.get_run_details(run_id)
            info = details['run_info']
            
            report = f"""
📊 تقرير التحليل - {info.get('Timestamp', 'N/A')}
{'=' * 60}

🆔 معرف التشغيل: {info.get('RunID', 'N/A')}
👤 المستخدم: {info.get('UserName', 'N/A')}
✅ الحالة: {info.get('Status', 'N/A')}

📁 الملفات:
   - ملفات الجوائز: {info.get('AwardsFiles', 'N/A')}
   - كشف البنك: {info.get('BankFile', 'N/A')}

📈 الإحصائيات:
   - إجمالي الجوائز: {info.get('TotalAwards', 0):,}
   - سجلات البنك: {info.get('TotalBankRecords', 0):,}
   - مطابقات حتمية: {info.get('ExactMatches', 0):,}
   - مطابقات ضبابية: {info.get('FuzzyMatches', 0):,}
   - مطابقات RL: {info.get('RLMatches', 0):,}
   - غير مطابقة: {info.get('UnmatchedAwards', 0):,}
   - تكرارات مشتبهة: {info.get('SuspectedDuplicates', 0):,}
   - تكرارات مؤكدة: {info.get('ConfirmedDuplicates', 0):,}

⚙️ الإعدادات:
   - نافذة المطابقة: {info.get('TimeWindowDays', 0)} يوم
   - عتبة التطابق الضبابي: {info.get('FuzzyThreshold', 0)}%
   - استخدام Record Linkage: {'نعم' if info.get('UseRecordLinkage') else 'لا'}

⏱️ وقت التنفيذ: {info.get('ExecutionTimeSeconds', 0):.2f} ثانية
"""
            return report
        
        else:
            # تقرير عام
            recent = self.get_recent_runs(5)
            
            report = f"""
📊 ملخص آخر التحليلات
{'=' * 60}

إجمالي التحليلات: {len(recent)}

"""
            for _, run in recent.iterrows():
                report += f"""
⏱️ {run.get('Timestamp', 'N/A')}
   المطابقات: {run.get('ExactMatches', 0) + run.get('FuzzyMatches', 0) + run.get('RLMatches', 0):,}
   غير المطابقة: {run.get('UnmatchedAwards', 0):,}
   التكرارات: {run.get('ConfirmedDuplicates', 0):,}
   ───────────────────────────────────────────────
"""
            
            return report
