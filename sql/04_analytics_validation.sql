
-- 04_analytics_validation.sql
-- Check total sample reconciliation
SELECT total_samples, eligible_samples, unavailable_samples FROM vw_wawqi_national_summary;

-- Check category totals against state summaries
SELECT 
    SUM(excellent_count) as c_exc,
    SUM(good_count) as c_good,
    SUM(poor_count) as c_poor,
    SUM(very_poor_count) as c_vp,
    SUM(unsuitable_count) as c_uns
FROM mv_wawqi_state_summary;
