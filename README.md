# 基于 Hive 数仓的短视频用户增长与内容分析平台

> 数据分析实习求职项目

## 技术栈

Python · Pandas · Hive · HDFS · SQL · Power BI · DeepSeek API

## 项目结构

```
├── data/raw/                  # 原始数据
├── python/                    # Python 脚本
│   ├── data_profile.py        #   数据探查
│   ├── powerbi_export.py      #   数仓聚合 → 导出CSV
│   └── ai_analysis.py         #   大模型自动分析
├── hive/                      # Hive SQL
│   ├── ods/                   #   ODS 层（贴源层）
│   ├── dwd/                   #   DWD 层（明细层）
│   ├── dws/                   #   DWS 层（汇总层）
│   └── ads/                   #   ADS 层（应用层）
├── powerbi/                   # Power BI 看板 + 导出数据
├── reports/                   # 报告输出
└── hive/run_all.sql           # 全链路执行脚本
```

## 数据仓库架构

```
ODS (贴源层) → DWD (明细层) → DWS (汇总层) → ADS (应用层)
   ↑                 ↑              ↑              ↑
 EXTERNAL         去重+清洗     按实体+日聚合   跨天+JOIN分析
 TEXTFILE         PARQUET       PARQUET        PARQUET
```

| 层级 | 表名 | 说明 |
|------|------|------|
| ODS | ods_interaction | 原始交互数据 |
| ODS | ods_category | 类目字典 |
| DWD | dwd_interaction | 清洗后明细数据 |
| DWD | dwd_category | 清洗后类目表 |
| DWS | dws_user_daily | 用户每日行为汇总 |
| DWS | dws_video_daily | 视频每日行为汇总 |
| DWS | dws_category_daily | 类目每日行为汇总 |
| ADS | ads_user_growth | 用户增长与留存 |
| ADS | ads_category_rank | 类目表现排行 |
| ADS | ads_user_portrait | 用户画像分析 |
| ADS | ads_video_rank | 视频热度排行 |
| ADS | ads_hourly_pattern | 时段活跃分布 |

## 快速开始

### 1. 数据探查

```bash
python python/data_profile.py
```

### 2. 导出 Power BI 数据

```bash
python python/powerbi_export.py
```

### 3. Power BI 看板

打开 `powerbi/ShortVideo_Data_Analysis_Dashboard.pbix`

### 4. 大模型自动分析

```bash
# 设置 API Key
$env:DEEPSEEK_API_KEY='sk-xxx'

# 运行分析
python python/ai_analysis.py
```

## 数据说明

- 数据来源：快手短视频平台用户行为数据
- 时间范围：2022年9月15日-22日（8天）
- 数据量：约79万条原始记录，去重后约69万条
- 覆盖用户：6,654 名
- 覆盖视频：31,496 个