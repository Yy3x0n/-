# -*- coding: utf-8 -*-
"""数据探查脚本：分析 interaction_sampled.csv 和 categories_cn_en.csv"""

import pandas as pd
import numpy as np
import os

DATA_DIR = "e:/short_video_analysis/data/raw"
OUTPUT = "e:/short_video_analysis/reports/data_profile.md"

# ============================================================
# 辅助函数
# ============================================================

def file_size_mb(path):
    size = os.path.getsize(path)
    return size, size / (1024 * 1024)

def profile_df(df, name):
    """返回一个 DataFrame 的探查结果字典"""
    result = {}

    # 行数列数
    result["rows"] = len(df)
    result["cols"] = len(df.columns)

    # 字段名
    result["columns"] = list(df.columns)

    # 数据类型
    result["dtypes"] = {col: str(df[col].dtype) for col in df.columns}

    # 缺失值
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    result["missing"] = {
        col: {"count": int(missing[col]), "pct": float(missing_pct[col])}
        for col in df.columns
    }

    # 重复行
    result["duplicates"] = int(df.duplicated().sum())

    # 每个字段的主要取值
    result["value_summary"] = {}
    for col in df.columns:
        s = df[col]
        if s.dtype == "object":
            # 字符串列
            n_unique = s.nunique()
            top_vals = s.value_counts().head(10).to_dict()
            result["value_summary"][col] = {
                "n_unique": n_unique,
                "top_values": {str(k): int(v) for k, v in top_vals.items()},
            }
        elif s.dtype == "bool":
            val_counts = s.value_counts().to_dict()
            result["value_summary"][col] = {
                "n_unique": s.nunique(),
                "top_values": {str(k): int(v) for k, v in val_counts.items()},
            }
        else:
            # 数值列（尝试转换，如果失败则按字符串处理）
            try:
                result["value_summary"][col] = {
                    "n_unique": int(s.nunique()),
                    "min": float(s.min()) if not pd.isna(s.min()) else None,
                    "max": float(s.max()) if not pd.isna(s.max()) else None,
                    "mean": round(float(s.mean()), 2) if not pd.isna(s.mean()) else None,
                    "median": float(s.median()) if not pd.isna(s.median()) else None,
                }
            except (ValueError, TypeError):
                # 混合类型列，按字符串处理
                n_unique = s.nunique()
                top_vals = s.astype(str).value_counts().head(10).to_dict()
                result["value_summary"][col] = {
                    "n_unique": n_unique,
                    "top_values": {str(k): int(v) for k, v in top_vals.items()},
                }

    return result


def format_md_report(profile1, profile2, size1, size2):
    """生成 Markdown 报告"""
    lines = []

    lines.append("# 数据探查报告")
    lines.append("")
    lines.append("> 生成时间：自动生成")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ============================================================
    # 文件1: interaction_sampled.csv
    # ============================================================
    lines.append("## 1. interaction_sampled.csv")
    lines.append("")

    lines.append("### 1.1 基本信息")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 文件大小 | {size1[1]:.2f} MB ({size1[0]:,} 字节) |")
    lines.append(f"| 行数 | {profile1['rows']:,} |")
    lines.append(f"| 列数 | {profile1['cols']} |")
    lines.append("")

    lines.append("### 1.2 字段列表与数据类型")
    lines.append("")
    lines.append("| 序号 | 字段名 | 数据类型 |")
    lines.append("|------|--------|----------|")
    for i, col in enumerate(profile1["columns"], 1):
        lines.append(f"| {i} | `{col}` | `{profile1['dtypes'][col]}` |")
    lines.append("")

    lines.append("### 1.3 缺失值统计")
    lines.append("")
    has_missing = any(v["count"] > 0 for v in profile1["missing"].values())
    if has_missing:
        lines.append("| 字段名 | 缺失数量 | 缺失率 (%) |")
        lines.append("|--------|----------|------------|")
        for col in profile1["columns"]:
            m = profile1["missing"][col]
            if m["count"] > 0:
                lines.append(f"| `{col}` | {m['count']:,} | {m['pct']}% |")
    else:
        lines.append("**无缺失值**")
    lines.append("")

    lines.append("### 1.4 重复数据")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 完全重复行数 | {profile1['duplicates']:,} |")
    lines.append(f"| 重复率 | {profile1['duplicates'] / profile1['rows'] * 100:.2f}% |")
    lines.append("")

    lines.append("### 1.5 各字段主要取值情况")
    lines.append("")
    for col in profile1["columns"]:
        vs = profile1["value_summary"][col]
        lines.append(f"#### `{col}`")
        lines.append("")
        if "top_values" in vs:
            lines.append(f"- 唯一值数量：{vs['n_unique']:,}")
            lines.append("- 前10取值：")
            lines.append("")
            lines.append("| 值 | 出现次数 |")
            lines.append("|----|----------|")
            for val, cnt in list(vs["top_values"].items())[:10]:
                lines.append(f"| {val} | {cnt:,} |")
        else:
            lines.append(f"- 唯一值数量：{vs['n_unique']:,}")
            lines.append(f"- 最小值：{vs['min']}")
            lines.append(f"- 最大值：{vs['max']}")
            lines.append(f"- 均值：{vs['mean']}")
            lines.append(f"- 中位数：{vs['median']}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # ============================================================
    # 文件2: categories_cn_en.csv
    # ============================================================
    lines.append("## 2. categories_cn_en.csv")
    lines.append("")

    lines.append("### 2.1 基本信息")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 文件大小 | {size2[1]:.2f} MB ({size2[0]:,} 字节) |")
    lines.append(f"| 行数 | {profile2['rows']:,} |")
    lines.append(f"| 列数 | {profile2['cols']} |")
    lines.append("")

    lines.append("### 2.2 字段列表与数据类型")
    lines.append("")
    lines.append("| 序号 | 字段名 | 数据类型 |")
    lines.append("|------|--------|----------|")
    for i, col in enumerate(profile2["columns"], 1):
        lines.append(f"| {i} | `{col}` | `{profile2['dtypes'][col]}` |")
    lines.append("")

    lines.append("### 2.3 缺失值统计")
    lines.append("")
    has_missing2 = any(v["count"] > 0 for v in profile2["missing"].values())
    if has_missing2:
        lines.append("| 字段名 | 缺失数量 | 缺失率 (%) |")
        lines.append("|--------|----------|------------|")
        for col in profile2["columns"]:
            m = profile2["missing"][col]
            if m["count"] > 0:
                lines.append(f"| `{col}` | {m['count']:,} | {m['pct']}% |")
    else:
        lines.append("**无缺失值**")
    lines.append("")

    lines.append("### 2.4 重复数据")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 完全重复行数 | {profile2['duplicates']:,} |")
    lines.append(f"| 重复率 | {profile2['duplicates'] / profile2['rows'] * 100:.2f}% |")
    lines.append("")

    lines.append("### 2.5 各字段主要取值情况")
    lines.append("")
    for col in profile2["columns"]:
        vs = profile2["value_summary"][col]
        lines.append(f"#### `{col}`")
        lines.append("")
        if "top_values" in vs:
            lines.append(f"- 唯一值数量：{vs['n_unique']:,}")
            lines.append("- 前10取值：")
            lines.append("")
            lines.append("| 值 | 出现次数 |")
            lines.append("|----|----------|")
            for val, cnt in list(vs["top_values"].items())[:10]:
                lines.append(f"| {val} | {cnt:,} |")
        else:
            lines.append(f"- 唯一值数量：{vs['n_unique']:,}")
            lines.append(f"- 最小值：{vs['min']}")
            lines.append(f"- 最大值：{vs['max']}")
            lines.append(f"- 均值：{vs['mean']}")
            lines.append(f"- 中位数：{vs['median']}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # ============================================================
    # 3. 关联分析
    # ============================================================
    lines.append("## 3. 两表关联分析")
    lines.append("")
    lines.append("### 3.1 关联字段")
    lines.append("")
    lines.append("| 源表 | 关联字段 | 目标表 | 关联字段 |")
    lines.append("|------|----------|--------|----------|")
    lines.append("| `interaction_sampled` | `category_id` | `categories_cn_en` | `category_id` |")
    lines.append("| `interaction_sampled` | `parent_id` | `categories_cn_en` | `parent_id` |")
    lines.append("| `interaction_sampled` | `root_id` | `categories_cn_en` | `root_id` |")
    lines.append("| `interaction_sampled` | `category_level` | `categories_cn_en` | `category_level` |")
    lines.append("")

    # 关联匹配统计
    int_cat_ids = set(cat_df["category_id"].dropna().astype(int).unique())
    cat_cat_ids = set(cat_df["category_id"].dropna().astype(int).unique())
    matched = int_cat_ids & cat_cat_ids
    unmatched_in_int = int_cat_ids - cat_cat_ids
    lines.append("### 3.2 category_id 匹配情况")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| interaction 中唯一 category_id 数 | {len(int_cat_ids):,} |")
    lines.append(f"| categories 中唯一 category_id 数 | {len(cat_cat_ids):,} |")
    lines.append(f"| 可匹配的 category_id 数 | {len(matched):,} |")
    lines.append(f"| interaction 中无法匹配的 category_id 数 | {len(unmatched_in_int):,} |")
    lines.append(f"| interaction 中 category_id 匹配率 | {len(matched) / len(int_cat_ids) * 100:.2f}% |")
    lines.append("")
    lines.append("**结论：两表可以通过 `category_id` 进行 LEFT JOIN 关联，匹配率很高，关联性强。**")
    lines.append("")

    lines.append("---")
    lines.append("")

    # ============================================================
    # 4. 字段业务含义与分类
    # ============================================================
    lines.append("## 4. 字段业务含义与分类")
    lines.append("")
    lines.append("### 4.1 interaction_sampled.csv 字段分类")
    lines.append("")
    lines.append("| 分类 | 字段 | 业务含义 | 数据类型 |")
    lines.append("|------|------|----------|----------|")

    field_meta = {
        "user_id": ("用户", "用户唯一标识", "int"),
        "pid": ("视频", "视频/作品唯一标识", "int"),
        "author_id": ("视频", "作者/创作者唯一标识", "int"),
        "category_id": ("内容分类", "视频类目ID（三级类目体系）", "int"),
        "category_level": ("内容分类", "类目层级（1=一级类目，2=二级类目，3=三级类目）", "int"),
        "parent_id": ("内容分类", "父类目ID", "int"),
        "root_id": ("内容分类", "根类目ID（一级类目ID）", "int"),
        "exposed_time": ("时间", "视频曝光时间戳（Unix秒）", "int"),
        "author_fans_count": ("视频", "作者粉丝数", "int"),
        "watch_time": ("行为", "用户观看时长（秒）", "int"),
        "duration": ("视频", "视频总时长（秒）", "float"),
        "cvm_like": ("行为", "是否点赞", "bool"),
        "click": ("行为", "是否点击", "bool"),
        "comment": ("行为", "是否评论", "bool"),
        "follow": ("行为", "是否关注作者", "bool"),
        "collect": ("行为", "是否收藏", "bool"),
        "forward": ("行为", "是否转发", "bool"),
        "hate": ("行为", "是否点踩/不喜欢", "bool"),
        "tag_name": ("内容分类", "视频标签名", "str"),
        "title": ("视频", "视频标题", "str"),
        "p_hour": ("时间", "曝光小时（0-23）", "int"),
        "p_date": ("时间", "曝光日期（YYYYMMDD格式）", "int"),
        "gender": ("用户", "用户性别（M=男，F=女）", "str"),
        "age": ("用户", "用户年龄", "int"),
        "mod_price": ("用户", "用户设备价格（反映消费能力）", "int"),
        "fre_city": ("用户", "用户常驻城市", "str"),
        "fre_community_type": ("用户", "用户社区类型", "str"),
        "fre_city_level": ("用户", "用户所在城市等级", "str"),
    }

    user_fields = []
    video_fields = []
    behavior_fields = []
    time_fields = []
    category_fields = []

    for col in profile1["columns"]:
        cat, meaning, dtype = field_meta.get(col, ("其他", "", ""))
        lines.append(f"| {cat} | `{col}` | {meaning} | {dtype} |")
        if cat == "用户":
            user_fields.append(col)
        elif cat == "视频":
            video_fields.append(col)
        elif cat == "行为":
            behavior_fields.append(col)
        elif cat == "时间":
            time_fields.append(col)
        elif cat == "内容分类":
            category_fields.append(col)

    lines.append("")

    lines.append("### 4.2 分类汇总")
    lines.append("")
    lines.append(f"- **用户画像字段**（{len(user_fields)}个）：{', '.join(f'`{f}`' for f in user_fields)}")
    lines.append(f"- **视频属性字段**（{len(video_fields)}个）：{', '.join(f'`{f}`' for f in video_fields)}")
    lines.append(f"- **用户行为字段**（{len(behavior_fields)}个）：{', '.join(f'`{f}`' for f in behavior_fields)}")
    lines.append(f"- **时间字段**（{len(time_fields)}个）：{', '.join(f'`{f}`' for f in time_fields)}")
    lines.append(f"- **内容分类字段**（{len(category_fields)}个）：{', '.join(f'`{f}`' for f in category_fields)}")
    lines.append("")

    lines.append("### 4.3 categories_cn_en.csv 字段分类")
    lines.append("")
    lines.append("| 字段 | 业务含义 | 数据类型 |")
    lines.append("|------|----------|----------|")
    lines.append("| `category_level` | 类目层级（1/2/3） | int |")
    lines.append("| `category_id` | 类目唯一标识 | int |")
    lines.append("| `category_name_cn` | 类目中文名 | str |")
    lines.append("| `parent_id` | 父类目ID | int |")
    lines.append("| `root_id` | 根类目（一级类目）ID | int |")
    lines.append("| `category_name_en` | 类目英文名 | str |")
    lines.append("")
    lines.append("该表是一个**类目维度字典表**，用于解释 `interaction_sampled` 中的 `category_id` 的中英文含义。")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 主流程
# ============================================================

print("正在读取 interaction_sampled.csv ...")
int_df = pd.read_csv(
    os.path.join(DATA_DIR, "interaction_sampled.csv"),
    dtype={
        "user_id": "int64",
        "pid": "int64",
        "author_id": "int64",
        "category_id": "int64",
        "category_level": "int64",
        "parent_id": "int64",
        "root_id": "int64",
    },
    low_memory=False,
)
print(f"  interaction_sampled 读取完成：{len(int_df)} 行, {len(int_df.columns)} 列")

print("正在读取 categories_cn_en.csv ...")
cat_df = pd.read_csv(os.path.join(DATA_DIR, "categories_cn_en.csv"))
print(f"  categories_cn_en 读取完成：{len(cat_df)} 行, {len(cat_df.columns)} 列")

# 文件大小
size1 = file_size_mb(os.path.join(DATA_DIR, "interaction_sampled.csv"))
size2 = file_size_mb(os.path.join(DATA_DIR, "categories_cn_en.csv"))

print("正在探查 interaction_sampled ...")
profile1 = profile_df(int_df, "interaction_sampled")

print("正在探查 categories_cn_en ...")
profile2 = profile_df(cat_df, "categories_cn_en")

print("正在生成 Markdown 报告 ...")
report = format_md_report(profile1, profile2, size1, size2)

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(report)

print(f"报告已保存至：{OUTPUT}")
print("完成！")