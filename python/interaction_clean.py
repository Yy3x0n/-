import pandas as pd

# 读取数据
df = pd.read_csv("data/raw/interaction_sampled.csv")

# 查看数据基本情况
print(df.info())
print(df.describe())

# 检查缺失值
print(df.isnull().sum())

# 查看重复值
print(df.duplicated().sum())

# 时间戳转换
df["exposed_datetime"] = pd.to_datetime(
    df["exposed_time"],
    unit="s"
)

# 日期
df["exposed_date"] = df["exposed_datetime"].dt.date

# 小时
df["exposed_hour"] = df["exposed_datetime"].dt.hour


# p_date 转换为日期
df["p_date"] = pd.to_datetime(
    df["p_date"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)
print(df["p_date"].head(5))

# 检查分类字段
print(df["category_level"].value_counts())
print(df["category_id"].nunique())
print(df["parent_id"].nunique())
print(df["root_id"].nunique())

print(df["tag_name"].head(10))
print(df["title"].head(10))


print(df["watch_time"].describe())
print(df["watch_time"].min())
print(df["watch_time"].max())

print(df["duration"].describe())
print(df["duration"].min())
print(df["duration"].max())

behavior_cols = [
    "cvm_like", "click", "comment",
    "follow", "collect", "forward", "hate"
]

for col in behavior_cols:
    print(f"\n{col}")
    print(df[col].value_counts())

print("\n用户数：", df["user_id"].nunique())
print("视频数：", df["pid"].nunique())
print("作者数：", df["author_id"].nunique())

print("\n重复行：", df.duplicated().sum())
print("\n缺失值：")
print(df.isnull().sum())
print(df.columns)

#导出数据
df.to_csv("data/clean/interaction_clean.csv", index=False)