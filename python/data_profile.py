# -*- coding: utf-8 -*-
"""
数据探查脚本
读取 data/raw/ 下的 interaction_sampled.csv 和 categories_cn_en.csv，
输出基本信息、缺失值、重复值、字段取值分布等探查结果。
"""

import os
import pandas as pd

# ============================================================
# 配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

INT_FILE = os.path.join(DATA_DIR, "interaction_sampled.csv")
CAT_FILE = os.path.join(DATA_DIR, "categories_cn_en.csv")

# ============================================================
# 1. 读取数据
# ============================================================
print("=" * 60)
print("1. 读取数据")
print("=" * 60)

df_int = pd.read_csv(INT_FILE, low_memory=False)
df_cat = pd.read_csv(CAT_FILE)

print(f"  interaction_sampled.csv → {df_int.shape[0]:,} 行 × {df_int.shape[1]} 列")
print(f"  categories_cn_en.csv   → {df_cat.shape[0]:,} 行 × {df_cat.shape[1]} 列")

# 文件大小
size_int = os.path.getsize(INT_FILE)
size_cat = os.path.getsize(CAT_FILE)
print(f"\n  文件大小:")
print(f"    interaction_sampled.csv → {size_int:,} 字节 ({size_int / 1024 / 1024:.2f} MB)")
print(f"    categories_cn_en.csv   → {size_cat:,} 字节 ({size_cat / 1024 / 1024:.2f} MB)")


# ============================================================
# 2. 字段名与数据类型
# ============================================================
print("\n" + "=" * 60)
print("2. 字段名与数据类型")
print("=" * 60)

print("\n  [interaction_sampled.csv]")
for i, col in enumerate(df_int.columns, 1):
    print(f"    {i:2d}. {col:<25s} dtype={df_int[col].dtype}")

print("\n  [categories_cn_en.csv]")
for i, col in enumerate(df_cat.columns, 1):
    print(f"    {i:2d}. {col:<25s} dtype={df_cat[col].dtype}")


# ============================================================
# 3. 缺失值分析
# ============================================================
print("\n" + "=" * 60)
print("3. 缺失值分析")
print("=" * 60)

def missing_report(df, name):
    print(f"\n  [{name}]")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) == 0:
        print("    ✓ 无缺失值")
    else:
        for col, cnt in missing.items():
            pct = cnt / len(df) * 100
            print(f"    {col:<25s} 缺失 {cnt:,} 行 ({pct:.2f}%)")

missing_report(df_int, "interaction_sampled.csv")
missing_report(df_cat, "categories_cn_en.csv")


# ============================================================
# 4. 重复值分析
# ============================================================
print("\n" + "=" * 60)
print("4. 重复值分析")
print("=" * 60)

dup_int = df_int.duplicated().sum()
dup_cat = df_cat.duplicated().sum()
print(f"\n  interaction_sampled.csv → 完全重复行: {dup_int:,} ({dup_int / len(df_int) * 100:.2f}%)")
print(f"  categories_cn_en.csv   → 完全重复行: {dup_cat:,} ({dup_cat / len(df_cat) * 100:.2f}%)")


# ============================================================
# 5. 各字段取值分布
# ============================================================
print("\n" + "=" * 60)
print("5. 各字段取值分布")
print("=" * 60)

def value_summary(df, name):
    print(f"\n  [{name}]")
    for col in df.columns:
        s = df[col]
        n_unique = s.nunique()
        non_null = s.notna().sum()

        print(f"\n  --- {col} ---")
        print(f"    非空值: {non_null:,}  |  唯一值: {n_unique:,}")

        if s.dtype == "bool":
            vc = s.value_counts()
            for val, cnt in vc.items():
                print(f"      {val}: {cnt:,} ({cnt / len(df) * 100:.1f}%)")
        elif s.dtype in ("int64", "float64") and n_unique <= 10:
            vc = s.value_counts().sort_index()
            for val, cnt in vc.items():
                print(f"      {val}: {cnt:,} ({cnt / len(df) * 100:.1f}%)")
        elif s.dtype in ("int64", "float64"):
            print(f"      min={s.min():.2f}  |  max={s.max():.2f}  |  mean={s.mean():.2f}  |  median={s.median():.2f}")
        elif s.dtype == "object":
            top = s.value_counts().head(5)
            print(f"      Top5 取值:")
            for val, cnt in top.items():
                val_str = str(val)[:40]
                print(f"        [{val_str}] → {cnt:,}")

value_summary(df_int, "interaction_sampled.csv")
value_summary(df_cat, "categories_cn_en.csv")


# ============================================================
# 6. 两表关联分析
# ============================================================
print("\n" + "=" * 60)
print("6. 两表关联分析")
print("=" * 60)

int_ids = set(df_int["category_id"].dropna().unique())
cat_ids = set(df_cat["category_id"].dropna().unique())
matched = int_ids & cat_ids
unmatched = int_ids - cat_ids

print(f"\n  interaction 中 category_id 唯一值: {len(int_ids):,}")
print(f"  categories   中 category_id 唯一值: {len(cat_ids):,}")
print(f"  可匹配数量: {len(matched):,}")
print(f"  无法匹配数量: {len(unmatched):,}")
print(f"  匹配率: {len(matched) / len(int_ids) * 100:.1f}%")
print(f"\n  关联字段: category_id (主键), parent_id, root_id, category_level")
print(f"  结论: 两表可通过 category_id 进行 LEFT JOIN 关联。")


# ============================================================
# 7. 字段业务分类
# ============================================================
print("\n" + "=" * 60)
print("7. 字段业务分类 (interaction_sampled.csv)")
print("=" * 60)

categories = {
    "用户画像": ["user_id", "gender", "age", "mod_price", "fre_city", "fre_community_type", "fre_city_level"],
    "视频属性": ["pid", "author_id", "author_fans_count", "duration", "title"],
    "用户行为": ["watch_time", "cvm_like", "click", "comment", "follow", "collect", "forward", "hate"],
    "时间": ["exposed_time", "p_hour", "p_date"],
    "内容分类": ["category_id", "category_level", "parent_id", "root_id", "tag_name"],
}

# 验证不虚构字段
all_fields = set(df_int.columns)
known_fields = set()
for fields in categories.values():
    known_fields.update(fields)
unknown = all_fields - known_fields

for cat_name, fields in categories.items():
    actual = [f for f in fields if f in df_int.columns]
    print(f"\n  ■ {cat_name} ({len(actual)} 个)")
    for f in actual:
        print(f"      {f}")

if unknown:
    print(f"\n  ■ 未分类字段 ({len(unknown)} 个)")
    for f in unknown:
        print(f"      {f}")

print(f"\n  categories_cn_en.csv 为类目维度字典表，共 {len(df_cat.columns)} 个字段:")
for col in df_cat.columns:
    print(f"      {col}")


print("\n" + "=" * 60)
print("数据探查完成。")
print("=" * 60)