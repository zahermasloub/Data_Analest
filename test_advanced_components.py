# -*- coding: utf-8 -*-
"""
🧪 اختبار المكونات المتقدمة
Test Advanced Features
========================
اختبار سريع للوحدات الجديدة: Advanced Matcher, Audit Logger, Performance Optimizer
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# إضافة المسار للوصول للوحدات
sys.path.insert(0, str(Path(__file__).parent))

def test_advanced_matcher():
    """اختبار محرك المطابقة المتقدم"""
    print("\n" + "="*60)
    print("🔍 اختبار Advanced Matcher")
    print("="*60)
    
    try:
        from core.advanced_matcher import AdvancedMatcher
        
        # إنشاء بيانات تجريبية
        awards_df = pd.DataFrame({
            'OwnerName': ['محمد أحمد علي', 'علي حسن محمود', 'فاطمة خالد', 'سارة عبدالله'],
            'OwnerName_norm': ['محمد احمد علي', 'علي حسن محمود', 'فاطمه خالد', 'ساره عبدالله'],
            'AwardAmount': [5000.0, 3000.0, 7500.0, 2000.0],
            'EntryDate': [
                datetime(2024, 1, 1),
                datetime(2024, 1, 5),
                datetime(2024, 1, 10),
                datetime(2024, 1, 15)
            ],
            'Season': ['2024', '2024', '2024', '2024'],
            'Race': ['سباق الإمارات', 'سباق دبي', 'سباق أبوظبي', 'سباق الشارقة']
        })
        
        bank_df = pd.DataFrame({
            'BankName': ['محمد احمد علي', 'علي حسان محمود', 'فاطمة خالد احمد'],
            'BankName_norm': ['محمد احمد علي', 'علي حسان محمود', 'فاطمه خالد احمد'],
            'TransferAmount': [5000.0, 3000.0, 7500.0],
            'TransferDate': [
                datetime(2024, 1, 2),  # +1 يوم
                datetime(2024, 1, 6),  # +1 يوم
                datetime(2024, 1, 12)  # +2 يوم
            ],
            'BankReference': ['REF001', 'REF002', 'REF003']
        })
        
        # إنشاء المطابق
        matcher = AdvancedMatcher(fuzzy_threshold=85)
        
        # اختبار المطابقة الحتمية
        print("\n1️⃣ اختبار Exact Match...")
        exact = matcher.exact_match(awards_df, bank_df, time_window_days=7)
        print(f"   ✅ عدد المطابقات الحتمية: {len(exact)}")
        
        # اختبار المطابقة الضبابية
        print("\n2️⃣ اختبار Fuzzy Match...")
        unmatched = awards_df[~awards_df.index.isin(exact.index)]
        fuzzy = matcher.fuzzy_match(unmatched, bank_df, time_window_days=7)
        print(f"   ✅ عدد المطابقات الضبابية: {len(fuzzy)}")
        
        # اختبار جميع الطبقات
        print("\n3️⃣ اختبار All Layers...")
        all_matches, still_unmatched = matcher.match_all_layers(
            awards_df=awards_df,
            bank_df=bank_df,
            time_window_days=7,
            use_record_linkage=False  # تعطيل RL للسرعة
        )
        
        print(f"   ✅ إجمالي المطابقات: {len(all_matches)}")
        print(f"   ✅ غير المطابقة: {len(still_unmatched)}")
        
        # عرض النتائج
        if len(all_matches) > 0:
            print("\n📊 تفاصيل المطابقات:")
            for idx, row in all_matches.iterrows():
                print(f"   - {row['OwnerName']}: {row['MatchType']} (Score: {row['MatchScore']})")
        
        print("\n✅ Advanced Matcher يعمل بنجاح!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في Advanced Matcher: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_audit_logger():
    """اختبار نظام التسجيل"""
    print("\n" + "="*60)
    print("📝 اختبار Audit Logger")
    print("="*60)
    
    try:
        from core.audit_logger import AuditLogger
        
        # إنشاء المسجِّل
        logger = AuditLogger(log_dir="outputs/audit_logs_test")
        
        # تسجيل تحليل تجريبي
        print("\n1️⃣ تسجيل تحليل تجريبي...")
        run_id = logger.log_analysis_run(
            awards_files=["test_awards_1.xlsx", "test_awards_2.xlsx"],
            bank_file="test_bank_statement.xlsx",
            statistics={
                'total_awards': 100,
                'total_bank_records': 80,
                'exact_matches': 50,
                'fuzzy_matches': 20,
                'rl_matches': 5,
                'unmatched_awards': 25,
                'suspected_duplicates': 3,
                'confirmed_duplicates': 1
            },
            time_window_days=7,
            fuzzy_threshold=90,
            use_record_linkage=True,
            execution_time=5.5,
            user_name="Test User",
            status="Success"
        )
        print(f"   ✅ RunID: {run_id}")
        
        # تسجيل مطابقات تجريبية
        print("\n2️⃣ تسجيل مطابقات تجريبية...")
        test_matches = pd.DataFrame({
            'OwnerName': ['محمد أحمد', 'علي حسن'],
            'AwardAmount': [5000, 3000],
            'EntryDate': [datetime(2024, 1, 1), datetime(2024, 1, 2)],
            'BankReference': ['REF001', 'REF002'],
            'BeneficiaryName': ['محمد احمد', 'علي حسن'],
            'TransferAmount': [5000, 3000],
            'TransferDate': [datetime(2024, 1, 2), datetime(2024, 1, 3)],
            'MatchType': ['Exact', 'Fuzzy'],
            'MatchScore': [100, 95],
            'DateDiff': [1, 1]
        })
        
        logger.log_matches(run_id, test_matches)
        print(f"   ✅ تم تسجيل {len(test_matches)} مطابقة")
        
        # تسجيل خطأ تجريبي
        print("\n3️⃣ تسجيل خطأ تجريبي...")
        logger.log_error(
            error_type="TestError",
            error_message="هذا خطأ تجريبي للاختبار",
            context={'test': True, 'timestamp': str(datetime.now())}
        )
        print("   ✅ تم تسجيل الخطأ")
        
        # استرجاع آخر التحليلات
        print("\n4️⃣ استرجاع آخر التحليلات...")
        recent = logger.get_recent_runs(limit=5)
        print(f"   ✅ عدد السجلات: {len(recent)}")
        
        # توليد تقرير
        print("\n5️⃣ توليد تقرير نصي...")
        report = logger.generate_report(run_id)
        print(report)
        
        print("\n✅ Audit Logger يعمل بنجاح!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في Audit Logger: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_performance_optimizer():
    """اختبار محسِّن الأداء"""
    print("\n" + "="*60)
    print("⚡ اختبار Performance Optimizer")
    print("="*60)
    
    try:
        from core.performance_optimizer import PerformanceOptimizer, recommend_optimizer_settings
        
        # اختبار التوصيات
        print("\n1️⃣ اختبار التوصيات...")
        for size in [5, 50, 150]:
            rec = recommend_optimizer_settings(size)
            print(f"   📁 {size} MB: {rec['reason']}")
        
        # إنشاء المحسِّن
        print("\n2️⃣ إنشاء المحسِّن...")
        optimizer = PerformanceOptimizer(use_duckdb=True, use_dask=False)
        stats = optimizer.get_statistics()
        print(f"   ✅ DuckDB: {'✓' if stats['duckdb_enabled'] else '✗'}")
        print(f"   ✅ Dask: {'✓' if stats['dask_enabled'] else '✗'}")
        
        # اختبار فلترة البيانات
        print("\n3️⃣ اختبار الفلترة...")
        test_df = pd.DataFrame({
            'AwardAmount': [1000, 2500, 5000, 7500, 10000],
            'OwnerName': ['محمد', 'علي', 'فاطمة', 'سارة', 'أحمد']
        })
        
        filtered = optimizer.filter_by_amount_duckdb(
            df=test_df,
            min_amount=2000,
            max_amount=8000,
            amount_column='AwardAmount'
        )
        
        print(f"   ✅ قبل الفلترة: {len(test_df)} صف")
        print(f"   ✅ بعد الفلترة: {len(filtered)} صف")
        
        # اختبار التجميع
        print("\n4️⃣ اختبار التجميع...")
        test_df['Season'] = ['2024', '2024', '2024', '2023', '2023']
        
        aggregated = optimizer.aggregate_by_group_duckdb(
            df=test_df,
            group_by=['Season'],
            agg_columns={'AwardAmount': 'SUM'}
        )
        
        print(f"   ✅ عدد المجموعات: {len(aggregated)}")
        if len(aggregated) > 0:
            for _, row in aggregated.iterrows():
                print(f"      - Season {row['Season']}: {row['AwardAmount_SUM']:,.0f}")
        
        # إغلاق
        optimizer.close()
        
        print("\n✅ Performance Optimizer يعمل بنجاح!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في Performance Optimizer: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """تشغيل جميع الاختبارات"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🧪 اختبار المكونات المتقدمة" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        'Advanced Matcher': test_advanced_matcher(),
        'Audit Logger': test_audit_logger(),
        'Performance Optimizer': test_performance_optimizer()
    }
    
    # ملخص النتائج
    print("\n" + "="*60)
    print("📊 ملخص النتائج")
    print("="*60)
    
    for component, passed in results.items():
        status = "✅ نجح" if passed else "❌ فشل"
        print(f"   {component}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n   إجمالي: {passed}/{total} اختبار ناجح")
    
    if passed == total:
        print("\n🎉 جميع الاختبارات نجحت!")
    else:
        print(f"\n⚠️ {total - passed} اختبار فشل")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
