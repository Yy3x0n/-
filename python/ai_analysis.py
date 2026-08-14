"""
短视频业务分析 - 大模型自动分析
=============================
读取聚合数据 → 计算关键指标 → 调用 DeepSeek API → 生成分析报告
"""
import pandas as pd
import json
import os
from urllib.request import Request, urlopen
from urllib.error import URLError

# ============================================
# 配置
# ============================================
# DeepSeek API 配置 (OpenAI 兼容接口)
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your-api-key-here")
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

DATA_DIR = "powerbi"
OUTPUT_DIR = "reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def read_data():
    """读取所有聚合数据，计算关键业务指标"""
    metrics = {}

    # ---- 用户增长 ----
    df_growth = pd.read_csv(f"{DATA_DIR}/ads_user_growth.csv")
    total_dau = df_growth["dau"].mean()
    total_new = df_growth["new_user_cnt"].sum()
    metrics["用户增长"] = {
        "数据天数": len(df_growth),
        "日均活跃用户(DAU)": f"{total_dau:.0f}",
        "总新增用户数": f"{total_new:.0f}",
        "日均新增用户": f"{df_growth['new_user_cnt'].mean():.0f}",
        "平均次日留存率": f"{df_growth['day1_retention'].mean():.2%}",
        "平均3日留存率": f"{df_growth['day3_retention'].mean():.2%}",
        "平均7日留存率": f"{df_growth['day7_retention'].mean():.2%}",
        "DAU趋势": df_growth[["exposed_date", "dau"]].to_dict("records"),
        "留存率趋势": df_growth[["exposed_date", "day1_retention", "day3_retention", "day7_retention"]].to_dict("records"),
    }

    # ---- 用户画像 ----
    df_portrait = pd.read_csv(f"{DATA_DIR}/ads_user_portrait.csv")
    # 性别分布
    gender_dist = df_portrait.groupby("gender")["user_cnt"].sum().to_dict()
    metrics["用户画像"] = {
        "性别分布": {"男(M)": int(gender_dist.get("M", 0)), "女(F)": int(gender_dist.get("F", 0))},
        "年龄段分布": df_portrait.groupby("age_group")["user_cnt"].sum().to_dict(),
        "城市等级分布": df_portrait.groupby("fre_city_level")["user_cnt"].sum().to_dict(),
    }
    # 各年龄段行为差异
    age_behavior = df_portrait.groupby("age_group").agg(
        like_rate=("like_rate", "mean"),
        click_rate=("click_rate", "mean"),
        avg_watch_time=("avg_watch_time", "mean"),
    ).round(4).to_dict()
    metrics["用户画像"]["年龄段行为差异"] = age_behavior

    # ---- 内容分析 ----
    df_category = pd.read_csv(f"{DATA_DIR}/ads_category_rank.csv")
    # TOP10 类目
    top_cat = df_category.groupby("category_name_cn")["expose_cnt"].sum().nlargest(10).to_dict()
    metrics["内容分析"] = {
        "TOP10类目(按曝光量)": top_cat,
        "类目总数": df_category["category_id"].nunique(),
    }
    # 整体互动率
    total_expose = df_category["expose_cnt"].sum()
    total_like = df_category["like_cnt"].sum()
    total_comment = df_category["comment_cnt"].sum()
    total_follow = df_category["follow_cnt"].sum()
    metrics["内容分析"]["整体互动指标"] = {
        "总曝光量": f"{total_expose:,}",
        "点赞率": f"{total_like / total_expose:.2%}",
        "评论率": f"{total_comment / total_expose:.2%}",
        "关注率": f"{total_follow / total_expose:.2%}",
        "平均完播率": f"{df_category['watch_rate_avg'].mean():.2%}",
    }

    # ---- 时段分析 ----
    df_hourly = pd.read_csv(f"{DATA_DIR}/ads_hourly_pattern.csv")
    peak_hour = df_hourly.groupby("exposed_hour")["expose_cnt"].mean().idxmax()
    peak_val = df_hourly.groupby("exposed_hour")["expose_cnt"].mean().max()
    metrics["时段分析"] = {
        "活跃高峰小时": f"{int(peak_hour)}:00",
        "高峰时段平均曝光量": f"{peak_val:.0f}",
        "24小时分布": df_hourly.groupby("exposed_hour")["expose_cnt"].mean().round(0).to_dict(),
    }

    return metrics


def build_prompt(metrics):
    """构建分析提示词"""
    return f"""你是一名资深短视频数据分析师。请根据以下数据，写一份专业的业务分析报告。

## 数据概况
- 数据时间范围：2022年9月15日-22日（共8天）
- 数据来源：快手短视频平台用户行为数据
- 数据量：约69万条交互记录（去重后），覆盖6654名用户

## 关键业务指标

### 一、用户增长
- 日均活跃用户(DAU)：{metrics['用户增长']['日均活跃用户(DAU)']}
- 总新增用户数：{metrics['用户增长']['总新增用户数']}
- 日均新增用户：{metrics['用户增长']['日均新增用户']}
- 平均次日留存率：{metrics['用户增长']['平均次日留存率']}
- 平均3日留存率：{metrics['用户增长']['平均3日留存率']}
- 平均7日留存率：{metrics['用户增长']['平均7日留存率']}

### 二、用户画像
- 性别分布：M(男) {metrics['用户画像']['性别分布']['男(M)']:,} 人，F(女) {metrics['用户画像']['性别分布']['女(F)']:,} 人
- 年龄段分布：{json.dumps(metrics['用户画像']['年龄段分布'], ensure_ascii=False)}
- 城市等级分布：{json.dumps(metrics['用户画像']['城市等级分布'], ensure_ascii=False)}

### 三、内容表现
- TOP10类目（按曝光量）：{json.dumps(metrics['内容分析']['TOP10类目(按曝光量)'], ensure_ascii=False)}
- 整体点赞率：{metrics['内容分析']['整体互动指标']['点赞率']}
- 整体评论率：{metrics['内容分析']['整体互动指标']['评论率']}
- 整体关注率：{metrics['内容分析']['整体互动指标']['关注率']}
- 平均完播率：{metrics['内容分析']['整体互动指标']['平均完播率']}

### 四、时段活跃
- 活跃高峰：{metrics['时段分析']['活跃高峰小时']}
- 24小时分布：{json.dumps(metrics['时段分析']['24小时分布'], ensure_ascii=False)}

## 要求
请输出一份结构化的分析报告，包含以下部分：
1. **核心结论**（3-5句话总结最重要的发现）
2. **用户增长分析**（DAU趋势、留存表现评价、增长建议）
3. **用户画像洞察**（用户群体特征、行为差异）
4. **内容分析**（热门内容类型、互动率表现、内容策略建议）
5. **运营建议**（基于数据的具体可执行建议）

请用中文输出，语言专业但易懂，适合放入实习项目报告。"""


def call_deepseek(prompt):
    """调用 DeepSeek API"""
    if API_KEY == "your-api-key-here":
        return None, "[!] 请先设置 DEEPSEEK_API_KEY 环境变量\n   PowerShell: $env:DEEPSEEK_API_KEY='sk-xxx'\n   CMD: set DEEPSEEK_API_KEY=sk-xxx"

    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是一名资深短视频数据分析师，擅长从数据中提炼业务洞察，输出专业、结构化的分析报告。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 3000,
    }).encode("utf-8")

    req = Request(API_URL, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    })

    try:
        with urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"], None
    except URLError as e:
        return None, f"API 调用失败: {e}"
    except Exception as e:
        return None, f"未知错误: {e}"


def main():
    print("=" * 60)
    print("短视频业务分析 - 大模型自动分析")
    print("=" * 60)

    # 1. 读取数据并计算指标
    print("\n[1/3] 读取聚合数据，计算关键指标...")
    metrics = read_data()
    print("  指标计算完成")

    # 2. 构建提示词
    print("\n[2/3] 构建分析提示词...")
    prompt = build_prompt(metrics)
    print(f"  提示词长度: {len(prompt)} 字符")

    # 3. 调用 API
    print("\n[3/3] 调用 DeepSeek API 生成分析报告...")
    report, error = call_deepseek(prompt)

    if error:
        print(f"\n{error}")
        print("\n提示词已保存到 reports/prompt.txt，你也可以手动复制给大模型分析")
        with open(f"{OUTPUT_DIR}/prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt)
        return

    # 4. 保存报告
    report_path = f"{OUTPUT_DIR}/ai_analysis_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 短视频业务分析报告\n\n")
        f.write("> 由 DeepSeek 大模型自动生成\n\n")
        f.write(report)

    print("\n" + "=" * 60)
    print("分析报告已生成!")
    print(f"文件路径: {report_path}")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    main()