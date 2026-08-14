-- ADS 视频热度排行表
-- 来源: dws_video_daily (按天排行) + 全量累计
-- 说明: 每日热门视频 TOP 排行 + 全周期累计排行
DROP TABLE IF EXISTS ads_video_rank;
CREATE TABLE ads_video_rank (
    p_date          STRING   COMMENT '日期',
    pid             BIGINT   COMMENT '视频ID',
    title           STRING   COMMENT '视频标题',
    author_id       BIGINT   COMMENT '作者ID',
    category_id     INT      COMMENT '类目ID',
    tag_name        STRING   COMMENT '标签',
    expose_cnt      BIGINT   COMMENT '曝光量',
    like_cnt        BIGINT   COMMENT '点赞数',
    comment_cnt     BIGINT   COMMENT '评论数',
    forward_cnt     BIGINT   COMMENT '转发数',
    collect_cnt     BIGINT   COMMENT '收藏数',
    interact_cnt    BIGINT   COMMENT '互动总量(点赞+评论+转发+收藏)',
    watch_rate_avg  DOUBLE   COMMENT '平均完播率',
    engage_rate     DOUBLE   COMMENT '互动率(互动量/曝光量)'
)
STORED AS PARQUET;

INSERT OVERWRITE TABLE ads_video_rank
SELECT
    v.p_date,
    v.pid,
    i.title,
    v.author_id,
    v.category_id,
    i.tag_name,
    v.expose_cnt,
    v.like_cnt,
    v.comment_cnt,
    v.forward_cnt,
    v.collect_cnt,
    v.like_cnt + v.comment_cnt + v.forward_cnt + v.collect_cnt AS interact_cnt,
    v.watch_rate_avg,
    ROUND(
        (v.like_cnt + v.comment_cnt + v.forward_cnt + v.collect_cnt) * 1.0
        / NULLIF(v.expose_cnt, 0), 4
    ) AS engage_rate
FROM dws_video_daily v
LEFT JOIN (
    -- 每个视频取一条标题和标签 (去重)
    SELECT pid, MAX(title) AS title, MAX(tag_name) AS tag_name
    FROM dwd_interaction
    GROUP BY pid
) i ON v.pid = i.pid
ORDER BY v.p_date, v.expose_cnt DESC;