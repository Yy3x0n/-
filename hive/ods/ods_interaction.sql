-- ODS 用户交互行为表
DROP TABLE IF EXISTS ods_interaction;
CREATE EXTERNAL TABLE ods_interaction (
    user_id            BIGINT    COMMENT '用户ID',
    pid                BIGINT    COMMENT '视频ID',
    author_id          BIGINT    COMMENT '作者ID',
    category_id        INT       COMMENT '类目ID',
    category_level     INT       COMMENT '类目层级',
    parent_id          INT       COMMENT '父类目ID',
    root_id            INT       COMMENT '根类目ID',
    exposed_time       BIGINT    COMMENT '曝光时间戳',
    author_fans_count  BIGINT    COMMENT '作者粉丝数',
    watch_time         INT       COMMENT '观看时长(秒)',
    duration           DOUBLE    COMMENT '视频时长(秒)',
    cvm_like           BOOLEAN   COMMENT '是否点赞',
    click              BOOLEAN   COMMENT '是否点击',
    comment            BOOLEAN   COMMENT '是否评论',
    follow             BOOLEAN   COMMENT '是否关注',
    collect            BOOLEAN   COMMENT '是否收藏',
    forward            BOOLEAN   COMMENT '是否转发',
    hate               BOOLEAN   COMMENT '是否点踩',
    tag_name           STRING    COMMENT '标签名',
    title              STRING    COMMENT '视频标题',
    p_hour             INT       COMMENT '曝光小时',
    p_date             STRING    COMMENT '曝光日期',
    gender             STRING    COMMENT '性别',
    age                STRING    COMMENT '年龄',
    mod_price          INT       COMMENT '设备价格',
    fre_city           STRING    COMMENT '常驻城市',
    fre_community_type STRING    COMMENT '社区类型',
    fre_city_level     STRING    COMMENT '城市等级'
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/raw/interaction'
TBLPROPERTIES ('skip.header.line.count'='1');