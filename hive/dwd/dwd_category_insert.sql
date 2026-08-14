-- DWD 类目维度表 - 数据导入
-- 来源: ods_category
-- 处理: 去重 → 过滤 category_name_cn 为空的行
INSERT OVERWRITE TABLE dwd_category
SELECT DISTINCT
    category_id,
    category_level,
    category_name_cn,
    category_name_en,
    parent_id,
    root_id
FROM ods_category
WHERE category_name_cn IS NOT NULL
  AND category_name_cn != '';