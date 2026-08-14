-- ADS 类目表现排行表
-- 来源: dws_category_daily + dwd_category (JOIN 获取中文名)
-- 说明: 按日统计各类目曝光量、互动率等，用于内容分析
DROP TABLE IF EXISTS ads_category_rank;
CREATE TABLE ads_category_rank (
    p_date            STRING   COMMENT '日期',
    category_id       INT      COMMENT '类目ID',
    category_name_cn  STRING   COMMENT '类目中文名',
    expose_cnt        BIGINT   COMMENT '曝光量',
    video_cnt         BIGINT   COMMENT '视频数',
    user_cnt          BIGINT   COMMENT '用户数',
    watch_rate_avg    DOUBLE   COMMENT '平均完播率',
    like_rate         DOUBLE   COMMENT '点赞率',
    click_rate        DOUBLE   COMMENT '点击率',
    comment_rate      DOUBLE   COMMENT '评论率',
    follow_rate       DOUBLE   COMMENT '关注率',
    collect_rate      DOUBLE   COMMENT '收藏率',
    forward_rate      DOUBLE   COMMENT '转发率',
    interact_rate     DOUBLE   COMMENT '综合互动率(点赞+评论+关注+收藏+转发)/曝光'
)
STORED AS PARQUET;

INSERT OVERWRITE TABLE ads_category_rank
SELECT
    d.p_date,
    d.category_id,
    c.category_name_cn,
    d.expose_cnt,
    d.video_cnt,
    d.user_cnt,
    d.watch_rate_avg,
    d.like_rate,
    d.click_rate,
    d.comment_rate,
    d.follow_rate,
    d.collect_rate,
    d.forward_rate,
    ROUND(
        (d.like_cnt + d.comment_cnt + d.follow_cnt + d.collect_cnt + d.forward_cnt) * 1.0
        / NULLIF(d.expose_cnt, 0), 4
    ) AS interact_rate
FROM dws_category_daily d
LEFT JOIN dwd_category c ON d.category_id = c.category_id
ORDER BY d.p_date, d.expose_cnt DESC;