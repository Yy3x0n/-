-- ADS 用户增长分析表
-- 来源: dws_user_daily
-- 说明: 日活、新增用户、留存率（DWS 不跨天，ADS 层做跨天计算）
DROP TABLE IF EXISTS ads_user_growth;
CREATE TABLE ads_user_growth (
    p_date          STRING   COMMENT '日期',
    dau             BIGINT   COMMENT '日活用户数',
    new_user_cnt    BIGINT   COMMENT '当日新增用户数',
    day1_retention  DOUBLE   COMMENT '次日留存率',
    day3_retention  DOUBLE   COMMENT '3日留存率',
    day7_retention  DOUBLE   COMMENT '7日留存率'
)
STORED AS PARQUET;

-- 计算用户首次活跃日期
DROP TABLE IF EXISTS tmp_user_first_date;
CREATE TEMPORARY TABLE tmp_user_first_date AS
SELECT user_id, MIN(p_date) AS first_date
FROM dws_user_daily
GROUP BY user_id;

-- 插入数据
INSERT OVERWRITE TABLE ads_user_growth
SELECT
    t.p_date,
    t.dau,
    t.new_user_cnt,
    -- 次日留存：次日仍活跃的用户数 / 新增用户数
    ROUND(
        COALESCE(
            SUM(CASE WHEN r1.user_id IS NOT NULL THEN 1 ELSE 0 END) * 1.0
            / NULLIF(t.new_user_cnt, 0), 0
        ), 4
    ) AS day1_retention,
    -- 3日留存
    ROUND(
        COALESCE(
            SUM(CASE WHEN r3.user_id IS NOT NULL THEN 1 ELSE 0 END) * 1.0
            / NULLIF(t.new_user_cnt, 0), 0
        ), 4
    ) AS day3_retention,
    -- 7日留存
    ROUND(
        COALESCE(
            SUM(CASE WHEN r7.user_id IS NOT NULL THEN 1 ELSE 0 END) * 1.0
            / NULLIF(t.new_user_cnt, 0), 0
        ), 4
    ) AS day7_retention
FROM (
    -- 每日活跃用户数与新增用户数
    SELECT
        a.p_date,
        COUNT(DISTINCT a.user_id) AS dau,
        SUM(CASE WHEN f.first_date = a.p_date THEN 1 ELSE 0 END) AS new_user_cnt
    FROM dws_user_daily a
    LEFT JOIN tmp_user_first_date f ON a.user_id = f.user_id
    GROUP BY a.p_date
) t
-- 次日留存：first_date 的用户在 first_date+1 是否活跃
LEFT JOIN tmp_user_first_date f1 ON 1 = 1
LEFT JOIN dws_user_daily r1
    ON f1.user_id = r1.user_id
    AND r1.p_date = f1.first_date
    AND f1.first_date = t.p_date
    AND r1.p_date = CAST(CAST(f1.first_date AS INT) + 1 AS STRING)
-- 3日留存
LEFT JOIN tmp_user_first_date f3 ON 1 = 1
LEFT JOIN dws_user_daily r3
    ON f3.user_id = r3.user_id
    AND r3.p_date = CAST(CAST(f3.first_date AS INT) + 3 AS STRING)
    AND f3.first_date = t.p_date
-- 7日留存
LEFT JOIN tmp_user_first_date f7 ON 1 = 1
LEFT JOIN dws_user_daily r7
    ON f7.user_id = r7.user_id
    AND r7.p_date = CAST(CAST(f7.first_date AS INT) + 7 AS STRING)
    AND f7.first_date = t.p_date
GROUP BY t.p_date, t.dau, t.new_user_cnt
ORDER BY t.p_date;