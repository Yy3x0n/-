-- DWS 视频每日行为汇总表 - 数据导入
-- 来源: dwd_interaction
-- 粒度: pid + p_date
INSERT OVERWRITE TABLE dws_video_daily
SELECT
    pid,
    exposed_date                                        AS p_date,
    MAX(author_id)                                      AS author_id,
    MAX(category_id)                                    AS category_id,
    COUNT(*)                                            AS expose_cnt,
    SUM(CASE WHEN watch_time > 0 THEN 1 ELSE 0 END)     AS watch_cnt,
    SUM(watch_time)                                     AS watch_time_sum,
    AVG(CASE WHEN watch_time > 0 THEN watch_rate END)   AS watch_rate_avg,
    SUM(is_like)                                        AS like_cnt,
    SUM(is_click)                                       AS click_cnt,
    SUM(is_comment)                                     AS comment_cnt,
    SUM(is_follow)                                      AS follow_cnt,
    SUM(is_collect)                                     AS collect_cnt,
    SUM(is_forward)                                     AS forward_cnt,
    SUM(is_hate)                                        AS hate_cnt,
    ROUND(SUM(is_like)    / NULLIF(COUNT(*), 0), 4)     AS like_rate,
    ROUND(SUM(is_click)   / NULLIF(COUNT(*), 0), 4)     AS click_rate,
    ROUND(SUM(is_comment) / NULLIF(COUNT(*), 0), 4)     AS comment_rate,
    ROUND(SUM(is_follow)  / NULLIF(COUNT(*), 0), 4)     AS follow_rate,
    ROUND(SUM(is_collect) / NULLIF(COUNT(*), 0), 4)     AS collect_rate,
    ROUND(SUM(is_forward) / NULLIF(COUNT(*), 0), 4)     AS forward_rate,
    ROUND(SUM(is_hate)    / NULLIF(COUNT(*), 0), 4)     AS hate_rate
FROM dwd_interaction
GROUP BY pid, exposed_date;