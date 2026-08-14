-- ODS 类目字典表
DROP TABLE IF EXISTS ods_category;
CREATE EXTERNAL TABLE ods_category (
    category_level    INT     COMMENT '类目层级',
    category_id       INT     COMMENT '类目ID',
    category_name_cn  STRING  COMMENT '类目中文名',
    parent_id         INT     COMMENT '父类目ID',
    root_id           INT     COMMENT '根类目ID',
    category_name_en  STRING  COMMENT '类目英文名'
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/raw/category'
TBLPROPERTIES ('skip.header.line.count'='1');