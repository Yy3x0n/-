-- DWD 类目维度表
-- 来源: ods_category
-- 处理: 去重 → 过滤 category_name_cn 为空的行
DROP TABLE IF EXISTS dwd_category;
CREATE TABLE dwd_category (
    category_id      INT     COMMENT '类目ID',
    category_level   INT     COMMENT '类目层级',
    category_name_cn STRING  COMMENT '类目中文名',
    category_name_en STRING  COMMENT '类目英文名',
    parent_id        INT     COMMENT '父类目ID',
    root_id          INT     COMMENT '根类目ID'
)
STORED AS PARQUET;