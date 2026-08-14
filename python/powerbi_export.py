"""
Power BI 数据导出脚本
=====================
从原始数据出发，完成清洗 → DWS聚合 → ADS分析，导出CSV供Power BI使用
"""
import pandas as pd
import numpy as np
import os

# ============================================
# 0. 路径设置
# ============================================
RAW_DIR = "data/raw"
OUT_DIR = "data/powerbi"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================
# 1. 读取原始数据
# ============================================
print("[1/8] 读取原始数据...")
df = pd.read_csv(f"{RAW_DIR}/interaction_sampled.csv")
categories = pd.read_csv(f"{RAW_DIR}/categories_cn_en.csv")

print(f"  交互数据: {df.shape}")
print(f"  类目数据: {categories.shape}")

# ============================================
# 2. 数据清洗
# ============================================
print("[2/8] 数据清洗...")

# 去重
before = len(df)
df = df.drop_duplicates()
print(f"  去重: {before} → {len(df)} (删除 {before - len(df)} 行)")

# 年龄过滤
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df = df[(df["age"] >= 10) & (df["age"] <= 100)]

# 布尔列转 int
bool_cols = ["cvm_like", "click", "comment", "follow", "collect", "forward", "hate"]
for col in bool_cols:
    df[col] = df[col].astype(int)

# 衍生字段
df["exposed_datetime"] = pd.to_datetime(df["exposed_time"], unit="s")
df["exposed_date"] = df["exposed_datetime"].dt.strftime("%Y%m%d")
df["exposed_hour"] = df["exposed_datetime"].dt.hour
df["p_date_str"] = df["p_date"].astype(str)
df["watch_rate"] = np.where(df["duration"] > 0, df["watch_time"] / df["duration"], 0)
df["watch_rate"] = df["watch_rate"].clip(0, 1)
df["has_watch"] = (df["watch_time"] > 0).astype(int)

print(f"  清洗后: {len(df)} 行")

# 清洗类目表
categories = categories.drop_duplicates()
categories = categories[categories["category_name_cn"].notna() & (categories["category_name_cn"] != "")]

# ============================================
# 3. DWS 用户每日汇总
# ============================================
print("[3/8] 计算 DWS 用户每日汇总...")

dws_user = df.groupby(["user_id", "exposed_date"]).agg(
    expose_cnt=("user_id", "count"),
    watch_cnt=("has_watch", "sum"),
    watch_time_sum=("watch_time", "sum"),
    watch_rate_avg=("watch_rate", lambda x: x[x > 0].mean() if (x > 0).any() else 0),
    like_cnt=("cvm_like", "sum"),
    click_cnt=("click", "sum"),
    comment_cnt=("comment", "sum"),
    follow_cnt=("follow", "sum"),
    collect_cnt=("collect", "sum"),
    forward_cnt=("forward", "sum"),
    hate_cnt=("hate", "sum"),
).reset_index()

dws_user["like_rate"] = (dws_user["like_cnt"] / dws_user["expose_cnt"]).round(4)
dws_user["click_rate"] = (dws_user["click_cnt"] / dws_user["expose_cnt"]).round(4)
dws_user["comment_rate"] = (dws_user["comment_cnt"] / dws_user["expose_cnt"]).round(4)
dws_user["follow_rate"] = (dws_user["follow_cnt"] / dws_user["expose_cnt"]).round(4)
dws_user["collect_rate"] = (dws_user["collect_cnt"] / dws_user["expose_cnt"]).round(4)
dws_user["forward_rate"] = (dws_user["forward_cnt"] / dws_user["expose_cnt"]).round(4)
dws_user["hate_rate"] = (dws_user["hate_cnt"] / dws_user["expose_cnt"]).round(4)

dws_user.to_csv(f"{OUT_DIR}/dws_user_daily.csv", index=False)
print(f"  用户每日汇总: {len(dws_user)} 行")

# ============================================
# 4. DWS 视频每日汇总
# ============================================
print("[4/8] 计算 DWS 视频每日汇总...")

dws_video = df.groupby(["pid", "exposed_date"]).agg(
    author_id=("author_id", "first"),
    category_id=("category_id", "first"),
    expose_cnt=("pid", "count"),
    watch_cnt=("has_watch", "sum"),
    watch_time_sum=("watch_time", "sum"),
    watch_rate_avg=("watch_rate", lambda x: x[x > 0].mean() if (x > 0).any() else 0),
    like_cnt=("cvm_like", "sum"),
    click_cnt=("click", "sum"),
    comment_cnt=("comment", "sum"),
    follow_cnt=("follow", "sum"),
    collect_cnt=("collect", "sum"),
    forward_cnt=("forward", "sum"),
    hate_cnt=("hate", "sum"),
).reset_index()

dws_video["like_rate"] = (dws_video["like_cnt"] / dws_video["expose_cnt"]).round(4)
dws_video["click_rate"] = (dws_video["click_cnt"] / dws_video["expose_cnt"]).round(4)
dws_video["comment_rate"] = (dws_video["comment_cnt"] / dws_video["expose_cnt"]).round(4)
dws_video["follow_rate"] = (dws_video["follow_cnt"] / dws_video["expose_cnt"]).round(4)
dws_video["collect_rate"] = (dws_video["collect_cnt"] / dws_video["expose_cnt"]).round(4)
dws_video["forward_rate"] = (dws_video["forward_cnt"] / dws_video["expose_cnt"]).round(4)
dws_video["hate_rate"] = (dws_video["hate_cnt"] / dws_video["expose_cnt"]).round(4)

dws_video.to_csv(f"{OUT_DIR}/dws_video_daily.csv", index=False)
print(f"  视频每日汇总: {len(dws_video)} 行")

# ============================================
# 5. DWS 类目每日汇总
# ============================================
print("[5/8] 计算 DWS 类目每日汇总...")

dws_category = df.groupby(["category_id", "exposed_date"]).agg(
    expose_cnt=("category_id", "count"),
    video_cnt=("pid", "nunique"),
    user_cnt=("user_id", "nunique"),
    watch_time_sum=("watch_time", "sum"),
    watch_rate_avg=("watch_rate", lambda x: x[x > 0].mean() if (x > 0).any() else 0),
    like_cnt=("cvm_like", "sum"),
    click_cnt=("click", "sum"),
    comment_cnt=("comment", "sum"),
    follow_cnt=("follow", "sum"),
    collect_cnt=("collect", "sum"),
    forward_cnt=("forward", "sum"),
    hate_cnt=("hate", "sum"),
).reset_index()

dws_category["like_rate"] = (dws_category["like_cnt"] / dws_category["expose_cnt"]).round(4)
dws_category["click_rate"] = (dws_category["click_cnt"] / dws_category["expose_cnt"]).round(4)
dws_category["comment_rate"] = (dws_category["comment_cnt"] / dws_category["expose_cnt"]).round(4)
dws_category["follow_rate"] = (dws_category["follow_cnt"] / dws_category["expose_cnt"]).round(4)
dws_category["collect_rate"] = (dws_category["collect_cnt"] / dws_category["expose_cnt"]).round(4)
dws_category["forward_rate"] = (dws_category["forward_cnt"] / dws_category["expose_cnt"]).round(4)
dws_category["hate_rate"] = (dws_category["hate_cnt"] / dws_category["expose_cnt"]).round(4)

dws_category.to_csv(f"{OUT_DIR}/dws_category_daily.csv", index=False)
print(f"  类目每日汇总: {len(dws_category)} 行")

# ============================================
# 6. ADS 用户增长分析
# ============================================
print("[6/8] 计算 ADS 用户增长分析...")

# 每日活跃用户
user_first = df.groupby("user_id")["exposed_date"].min().reset_index()
user_first.columns = ["user_id", "first_date"]

daily_stats = df.groupby("exposed_date").agg(
    dau=("user_id", "nunique"),
).reset_index()

daily_stats["new_user_cnt"] = daily_stats["exposed_date"].apply(
    lambda d: (user_first["first_date"] == d).sum()
)

# 留存率计算
retention_data = []
dates = sorted(daily_stats["exposed_date"].unique())
for d in dates:
    new_users = user_first[user_first["first_date"] == d]["user_id"].tolist()
    if not new_users:
        retention_data.append({"p_date": d, "day1_retention": 0, "day3_retention": 0, "day7_retention": 0})
        continue

    # 次日留存
    d1 = str(int(d) + 1)
    d1_active = df[(df["user_id"].isin(new_users)) & (df["exposed_date"] == d1)]["user_id"].nunique()
    # 3日留存
    d3 = str(int(d) + 3)
    d3_active = df[(df["user_id"].isin(new_users)) & (df["exposed_date"] == d3)]["user_id"].nunique()
    # 7日留存
    d7 = str(int(d) + 7)
    d7_active = df[(df["user_id"].isin(new_users)) & (df["exposed_date"] == d7)]["user_id"].nunique()

    retention_data.append({
        "p_date": d,
        "day1_retention": round(d1_active / len(new_users), 4),
        "day3_retention": round(d3_active / len(new_users), 4),
        "day7_retention": round(d7_active / len(new_users), 4),
    })

ret_df = pd.DataFrame(retention_data)
ads_growth = daily_stats.merge(ret_df, left_on="exposed_date", right_on="p_date").drop(columns=["p_date"])
ads_growth.to_csv(f"{OUT_DIR}/ads_user_growth.csv", index=False)
print(f"  用户增长: {len(ads_growth)} 行")

# ============================================
# 7. ADS 类目排行
# ============================================
print("[7/8] 计算 ADS 类目排行...")

ads_category = dws_category.merge(
    categories[["category_id", "category_name_cn"]],
    on="category_id",
    how="left"
)

ads_category["interact_rate"] = (
    (ads_category["like_cnt"] + ads_category["comment_cnt"] +
     ads_category["follow_cnt"] + ads_category["collect_cnt"] +
     ads_category["forward_cnt"]) / ads_category["expose_cnt"]
).round(4)

ads_category = ads_category.sort_values(["exposed_date", "expose_cnt"], ascending=[True, False])
ads_category.to_csv(f"{OUT_DIR}/ads_category_rank.csv", index=False)
print(f"  类目排行: {len(ads_category)} 行")

# ============================================
# 8. ADS 用户画像
# ============================================
print("[8/8] 计算 ADS 用户画像...")

df["age_group"] = pd.cut(
    df["age"],
    bins=[0, 24, 34, 44, 54, 100],
    labels=["18-24", "25-34", "35-44", "45-54", "55+"]
)

ads_portrait = df.groupby(["gender", "age_group", "fre_city_level"], observed=False).agg(
    user_cnt=("user_id", "nunique"),
    expose_cnt=("user_id", "count"),
    avg_watch_time=("watch_time", "mean"),
    watch_rate_avg=("watch_rate", lambda x: x[x > 0].mean() if (x > 0).any() else 0),
    like_cnt=("cvm_like", "sum"),
    click_cnt=("click", "sum"),
    comment_cnt=("comment", "sum"),
    follow_cnt=("follow", "sum"),
    collect_cnt=("collect", "sum"),
    forward_cnt=("forward", "sum"),
).reset_index()

ads_portrait["like_rate"] = (ads_portrait["like_cnt"] / ads_portrait["expose_cnt"]).round(4)
ads_portrait["click_rate"] = (ads_portrait["click_cnt"] / ads_portrait["expose_cnt"]).round(4)
ads_portrait["comment_rate"] = (ads_portrait["comment_cnt"] / ads_portrait["expose_cnt"]).round(4)
ads_portrait["follow_rate"] = (ads_portrait["follow_cnt"] / ads_portrait["expose_cnt"]).round(4)
ads_portrait["collect_rate"] = (ads_portrait["collect_cnt"] / ads_portrait["expose_cnt"]).round(4)
ads_portrait["forward_rate"] = (ads_portrait["forward_cnt"] / ads_portrait["expose_cnt"]).round(4)
ads_portrait["avg_watch_time"] = ads_portrait["avg_watch_time"].round(2)
ads_portrait = ads_portrait[ads_portrait["user_cnt"] > 0]

ads_portrait.to_csv(f"{OUT_DIR}/ads_user_portrait.csv", index=False)
print(f"  用户画像: {len(ads_portrait)} 行")

# ============================================
# 9. 视频排行 (额外)
# ============================================
print("[额外] 计算视频排行...")

video_info = df.groupby("pid").agg(
    title=("title", "first"),
    tag_name=("tag_name", "first"),
).reset_index()

ads_video = dws_video.merge(video_info, on="pid", how="left")
ads_video["interact_cnt"] = (
    ads_video["like_cnt"] + ads_video["comment_cnt"] +
    ads_video["forward_cnt"] + ads_video["collect_cnt"]
)
ads_video["engage_rate"] = (ads_video["interact_cnt"] / ads_video["expose_cnt"]).round(4)
ads_video = ads_video.sort_values(["exposed_date", "expose_cnt"], ascending=[True, False])

ads_video.to_csv(f"{OUT_DIR}/ads_video_rank.csv", index=False)
print(f"  视频排行: {len(ads_video)} 行")

# ============================================
# 10. 时段分布 (额外)
# ============================================
print("[额外] 计算时段分布...")

ads_hourly = df.groupby(["exposed_date", "exposed_hour"]).agg(
    expose_cnt=("user_id", "count"),
    watch_cnt=("has_watch", "sum"),
    like_cnt=("cvm_like", "sum"),
    comment_cnt=("comment", "sum"),
    avg_watch_time=("watch_time", "mean"),
    watch_rate_avg=("watch_rate", "mean"),
).reset_index()

ads_hourly["avg_watch_time"] = ads_hourly["avg_watch_time"].round(2)
ads_hourly["watch_rate_avg"] = ads_hourly["watch_rate_avg"].round(4)
ads_hourly.to_csv(f"{OUT_DIR}/ads_hourly_pattern.csv", index=False)
print(f"  时段分布: {len(ads_hourly)} 行")

# ============================================
# 完成
# ============================================
print("\n" + "=" * 50)
print("Power BI 数据导出完成!")
print(f"输出目录: {OUT_DIR}/")
print("=" * 50)
for f in os.listdir(OUT_DIR):
    size = os.path.getsize(f"{OUT_DIR}/{f}") / 1024
    print(f"  {f:30s}  {size:8.1f} KB")