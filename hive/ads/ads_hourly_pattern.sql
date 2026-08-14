-- ADS 时段活跃分布分析
-- 来源: dwd_interaction
-- 说明: 按小时统计平台活跃度，分析用户活跃时段
DROP TABLE IF EXISTS ads_hourly_pattern;
CREATE TABLE ads_hourly_pattern (
    p_date          STRING   COMMENT '日期',
    p_hour          INT      COMMENT '小时(0-23)',
    expose_cnt      BIGINT   COMMENT '曝光量',
    watch_cnt       BIGINT   COMMENT '观看量',
    like_cnt        BIGINT   COMMENT '点赞数',
    comment_cnt     BIGINT   COMMENT '评论数',
    avg_watch_time  DOUBLE   COMMENT '平均观看时长(秒)',
    watch_rate_avg  DOUBLE   COMMENT '平均完播率'
)
STORED AS PARQUET;

INSERT OVERWRITE TABLE ads_hourly_pattern
SELECT
    exposed_date                                    AS p_date,
    exposed_hour                                    AS p_hour,
    COUNT(*)                                        AS expose_cnt,
    SUM(CASE WHEN watch_time > 0 THEN 1 ELSE 0 END) AS watch_cnt,
    SUM(is_like)                                    AS like_cnt,
    SUM(is_comment)                                 AS comment_cnt,
    ROUND(AVG(watch_time), 2)                       AS avg_watch_time,
    AVG(CASE WHEN watch_time > 0 THEN watch_rate END) AS watch_rate_avg
FROM dwd_interaction
GROUP BY exposed_date, exposed_hour
ORDER BY exposed_date, exposed_hour;