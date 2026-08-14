-- ADS 用户画像行为分析表
-- 来源: dwd_interaction (需要用户属性字段，DWS 已丢失)
-- 说明: 按性别、年龄段、城市等级分析用户行为差异
DROP TABLE IF EXISTS ads_user_portrait;
CREATE TABLE ads_user_portrait (
    gender           STRING   COMMENT '性别',
    age_group        STRING   COMMENT '年龄段',
    city_level       STRING   COMMENT '城市等级',
    user_cnt         BIGINT   COMMENT '用户数',
    expose_cnt       BIGINT   COMMENT '总曝光量',
    avg_watch_time   DOUBLE   COMMENT '人均观看时长(秒)',
    watch_rate_avg   DOUBLE   COMMENT '平均完播率',
    like_rate        DOUBLE   COMMENT '点赞率',
    click_rate       DOUBLE   COMMENT '点击率',
    comment_rate     DOUBLE   COMMENT '评论率',
    follow_rate      DOUBLE   COMMENT '关注率',
    collect_rate     DOUBLE   COMMENT '收藏率',
    forward_rate     DOUBLE   COMMENT '转发率'
)
STORED AS PARQUET;

INSERT OVERWRITE TABLE ads_user_portrait
SELECT
    gender,
    CASE
        WHEN age < 25 THEN '18-24'
        WHEN age < 35 THEN '25-34'
        WHEN age < 45 THEN '35-44'
        WHEN age < 55 THEN '45-54'
        ELSE '55+'
    END                                                     AS age_group,
    city_level,
    COUNT(DISTINCT user_id)                                 AS user_cnt,
    COUNT(*)                                                AS expose_cnt,
    ROUND(AVG(watch_time), 2)                               AS avg_watch_time,
    AVG(CASE WHEN watch_time > 0 THEN watch_rate END)       AS watch_rate_avg,
    ROUND(SUM(is_like)    / NULLIF(COUNT(*), 0), 4)         AS like_rate,
    ROUND(SUM(is_click)   / NULLIF(COUNT(*), 0), 4)         AS click_rate,
    ROUND(SUM(is_comment) / NULLIF(COUNT(*), 0), 4)         AS comment_rate,
    ROUND(SUM(is_follow)  / NULLIF(COUNT(*), 0), 4)         AS follow_rate,
    ROUND(SUM(is_collect) / NULLIF(COUNT(*), 0), 4)         AS collect_rate,
    ROUND(SUM(is_forward) / NULLIF(COUNT(*), 0), 4)         AS forward_rate
FROM dwd_interaction
GROUP BY gender,
    CASE
        WHEN age < 25 THEN '18-24'
        WHEN age < 35 THEN '25-34'
        WHEN age < 45 THEN '35-44'
        WHEN age < 55 THEN '45-54'
        ELSE '55+'
    END,
    city_level;