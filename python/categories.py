import pandas as pd

# 读取数据集
df = pd.read_csv("data/raw/categories_cn_en.csv")

print("数据规模：", df.shape)

print("\n缺失值：")
print(df.isnull().sum())

print("\n重复行：", df.duplicated().sum())

print("\ncategory_id重复：", df["category_id"].duplicated().sum())

print("\ncategory_level：")
print(df["category_level"].value_counts())

print("\n分类数量：", df["category_id"].nunique())

# 导出数据集
df.to_csv("data/clean/categories.csv", index=False)