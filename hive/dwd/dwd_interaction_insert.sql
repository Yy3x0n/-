-- DWD 用户交互行为明细表 - 数据导入
-- 来源: ods_interaction
-- 处理: 去重 → 类型转换(boolean→int) → 命名规范化 → 派生完播率 → 过滤脏数据
INSERT OVERWRITE TABLE dwd_interaction
SELECT DISTINCT
    user_id,
    pid,
    author_id,
    category_id,
    category_level,
    parent_id,
    root_id,
    exposed_time                                        AS exposed_ts,
    CAST(p_date AS STRING)                              AS exposed_date,
    p_hour                                              AS exposed_hour,
    author_fans_count                                   AS author_fans,
    watch_time,
    duration,
    CAST(cvm_like  AS INT)                              AS is_like,
    CAST(click     AS INT)                              AS is_click,
    CAST(comment   AS INT)                              AS is_comment,
    CAST(follow    AS INT)                              AS is_follow,
    CAST(collect   AS INT)                              AS is_collect,
    CAST(forward   AS INT)                              AS is_forward,
    CAST(hate      AS INT)                              AS is_hate,
    tag_name,
    title,
    gender,
    CAST(age AS INT)                                    AS age,
    mod_price,
    fre_city                                            AS city,
    fre_community_type                                  AS community_type,
    fre_city_level                                      AS city_level,
    CASE WHEN duration > 0 THEN watch_time / duration
         ELSE 0
    END                                                 AS watch_rate
FROM ods_interaction
WHERE CAST(age AS INT) IS NOT NULL
  AND CAST(age AS INT) BETWEEN 10 AND 100
  AND duration > 0;