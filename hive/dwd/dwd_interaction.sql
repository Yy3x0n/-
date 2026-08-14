-- DWD 用户交互行为明细表
-- 来源: ods_interaction
-- 处理: 去重 → 类型转换 → 命名规范化 → 派生字段
DROP TABLE IF EXISTS dwd_interaction;
CREATE TABLE dwd_interaction (
    user_id       BIGINT   COMMENT '用户ID',
    pid           BIGINT   COMMENT '视频ID',
    author_id     BIGINT   COMMENT '作者ID',
    category_id   INT      COMMENT '类目ID',
    category_level INT     COMMENT '类目层级',
    parent_id     INT      COMMENT '父类目ID',
    root_id       INT      COMMENT '根类目ID',
    exposed_ts    BIGINT   COMMENT '曝光时间戳',
    exposed_date  STRING   COMMENT '曝光日期',
    exposed_hour  INT      COMMENT '曝光小时',
    author_fans   BIGINT   COMMENT '作者粉丝数',
    watch_time    INT      COMMENT '观看时长(秒)',
    duration      DOUBLE   COMMENT '视频时长(秒)',
    is_like       INT      COMMENT '是否点赞',
    is_click      INT      COMMENT '是否点击',
    is_comment    INT      COMMENT '是否评论',
    is_follow     INT      COMMENT '是否关注',
    is_collect    INT      COMMENT '是否收藏',
    is_forward    INT      COMMENT '是否转发',
    is_hate       INT      COMMENT '是否点踩',
    tag_name      STRING   COMMENT '标签名',
    title         STRING   COMMENT '视频标题',
    gender        STRING   COMMENT '性别',
    age           INT      COMMENT '年龄',
    mod_price     INT      COMMENT '设备价格',
    city          STRING   COMMENT '城市',
    community_type STRING  COMMENT '社区类型',
    city_level    STRING   COMMENT '城市等级',
    watch_rate    DOUBLE   COMMENT '完播率'
)
STORED AS PARQUET;