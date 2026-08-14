-- DWS 类目每日行为汇总表
-- 来源: dwd_interaction
-- 粒度: category_id + p_date
-- 说明: 不跨天、不 JOIN，仅在 dwd_interaction 上按类目+日期聚合
DROP TABLE IF EXISTS dws_category_daily;
CREATE TABLE dws_category_daily (
    category_id     INT      COMMENT '类目ID',
    p_date          STRING   COMMENT '曝光日期',
    expose_cnt      BIGINT   COMMENT '曝光次数',
    video_cnt       BIGINT   COMMENT '视频数(去重)',
    user_cnt        BIGINT   COMMENT '用户数(去重)',
    watch_time_sum  BIGINT   COMMENT '观看总时长(秒)',
    watch_rate_avg  DOUBLE   COMMENT '平均完播率',
    like_cnt        BIGINT   COMMENT '点赞次数',
    click_cnt       BIGINT   COMMENT '点击次数',
    comment_cnt     BIGINT   COMMENT '评论次数',
    follow_cnt      BIGINT   COMMENT '关注次数',
    collect_cnt     BIGINT   COMMENT '收藏次数',
    forward_cnt     BIGINT   COMMENT '转发次数',
    hate_cnt        BIGINT   COMMENT '点踩次数',
    like_rate       DOUBLE   COMMENT '点赞率',
    click_rate      DOUBLE   COMMENT '点击率',
    comment_rate    DOUBLE   COMMENT '评论率',
    follow_rate     DOUBLE   COMMENT '关注率',
    collect_rate    DOUBLE   COMMENT '收藏率',
    forward_rate    DOUBLE   COMMENT '转发率',
    hate_rate       DOUBLE   COMMENT '点踩率'
)
STORED AS PARQUET;