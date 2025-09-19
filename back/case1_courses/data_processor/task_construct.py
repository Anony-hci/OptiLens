# 读取courses5.csv
# 我构建了以下三个任务：分别为不同专业的同学进行课程选择
# 任务1：金融专业的同学进行课程选择
# 任务2：计算机科学与技术专业的同学进行课程选择
# 任务3：化学专业的同学进行课程选择
#对于每个任务，我都列出了其中必修课，以及可选的课程，帮我整理所有的课程名，然后从courses5.csv中抽取出相应的课程，并分别保存为csv文件。此外，每个任务需要有一个分析，包括总的候选课程数量，并且需要分点给出，例如两门选一门的，即需要给出两门课程的候选课程数量。

import pandas as pd
import os

def load_courses_data():
    """加载课程数据"""
    csv_path = "../../front/src/data/courses5.csv"
    if not os.path.exists(csv_path):
        csv_path = "front/src/data/courses5.csv"
    return pd.read_csv(csv_path)

def find_exact_course_entries(df, course_name):
    """精确查找某个课程名称的所有条目"""
    matches = df[df['课程名'] == course_name]
    return matches

def find_courses_containing_keywords(df, keywords):
    """查找课程名中包含特定关键词的所有条目"""
    all_matches = []
    for keyword in keywords:
        matches = df[df['课程名'].str.contains(keyword, na=False, regex=False)]
        if not matches.empty:
            all_matches.append(matches)
    
    if all_matches:
        # 合并并去重
        combined = pd.concat(all_matches, ignore_index=True)
        combined = combined.drop_duplicates(subset=['课程名', '主讲教师', '上课时间'])
        return combined
    else:
        return pd.DataFrame()

def process_task1_finance():
    """处理任务1：金融专业课程选择"""
    print("=" * 50)
    print("任务1：金融专业课程选择")
    print("=" * 50)
    
    # 必修课程
    required_courses = [
        "微积分A(2)",
        "多元微积分", 
        "商务数据分析",
        "英语阅读写作(B)",
        "毛泽东思想和中国特色社会主义理论体系概论",
        "一年级男生体育(2)"
    ]
    
    # 选择课程组
    choice_groups = {
        "概率论选择组(两门选一门)": ["概率论与数理统计", "概率论与数理统计(社科类)"],
        "专业选修组(五门选一门)": ["区块链技术金融应用", "计量经济学(1)", "营销分析", "财务报表分析", "深度学习及金融数据分析"],
        "认知文明组(尽量选一门)": ["中国文明", "中国古代文明", "中国哲学(2)", "经典与想象:中国古代传说新读", "《孟子》研读"]
    }
    
    return process_task(required_courses, choice_groups, "task1_finance_courses.csv", "金融专业")

def process_task2_cs():
    """处理任务2：计算机科学与技术专业课程选择"""
    print("=" * 50)
    print("任务2：计算机科学与技术专业课程选择")
    print("=" * 50)
    
    # 必修课程
    required_courses = [
        "微积分A(2)",
        "大学物理B(1)",
        "面向对象程序设计基础",
        "英语阅读写作(A)",
        "中国近现代史纲要",
        "一年级女生体育(2)"
    ]
    
    # 选择课程组 - 使用关键词搜索
    choice_groups = {
        "程序设计基础组(两门选一门)": ["计算机程序设计基础", "计算机程序设计基础(2)"],
        "数字逻辑组(两门选一门)": ["数字逻辑电路", "数字逻辑设计"],
        "人机交互心智组(尽量选一门)": {"keywords": ["人机交互", "认知"]}  # 使用关键词搜索
    }
    
    return process_task(required_courses, choice_groups, "task2_cs_courses.csv", "计算机科学与技术专业")

def process_task3_chemistry():
    """处理任务3：化学专业课程选择"""
    print("=" * 50)
    print("任务3：化学专业课程选择")
    print("=" * 50)
    
    # 必修课程
    required_courses = [
        "物理化学(2)",
        "反应工程基础",
        "生物化学基础实验",
        "英语听说交流(B)",
        "中国马克思主义与当代",
        "二年级男生篮球"
    ]
    
    # 选择课程组 - 使用关键词搜索
    choice_groups = {
        "大学化学组(两门选一门)": ["大学化学A", "大学化学B"],
        "概率论组(四门选一门)": ["概率论与数理统计", "概率论与随机过程", "概率论与随机过程(1)", "概率论与随机过程(2)"],
        "人工智能组(尽量选一门)": {"keywords": ["人工智能"]}  # 使用关键词搜索
    }
    
    return process_task(required_courses, choice_groups, "task3_chemistry_courses.csv", "化学专业")

def process_task(required_courses, choice_groups, output_filename, major_name):
    """处理单个任务"""
    df = load_courses_data()
    
    # 收集所有相关课程
    all_course_names = required_courses.copy()
    
    # 处理选择课程组
    for group_name, courses in choice_groups.items():
        if isinstance(courses, dict) and "keywords" in courses:
            # 跳过关键词组，稍后单独处理
            continue
        else:
            all_course_names.extend(courses)
    
    # 查找所有相关课程条目
    all_found_courses = []
    
    # 处理精确匹配的课程
    for course_name in all_course_names:
        course_entries = find_exact_course_entries(df, course_name)
        if not course_entries.empty:
            all_found_courses.append(course_entries)
    
    # 处理关键词匹配的课程
    for group_name, courses in choice_groups.items():
        if isinstance(courses, dict) and "keywords" in courses:
            keyword_courses = find_courses_containing_keywords(df, courses["keywords"])
            if not keyword_courses.empty:
                all_found_courses.append(keyword_courses)
    
    # 合并所有找到的课程
    if all_found_courses:
        combined_courses = pd.concat(all_found_courses, ignore_index=True)
        # 去重（基于课程名、主讲教师、上课时间）
        combined_courses = combined_courses.drop_duplicates(subset=['课程名', '主讲教师', '上课时间'])
        # 保存到CSV文件
        combined_courses.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"已保存 {len(combined_courses)} 条课程记录到 {output_filename}")
    else:
        combined_courses = pd.DataFrame()
        print(f"未找到任何相关课程")
    
    # 生成详细分析报告
    print(f"\n{major_name}课程条目分析：")
    print(f"总候选课程条目数量：{len(combined_courses)}")
    
    print("\n必修课程分析：")
    required_total = 0
    for course_name in required_courses:
        course_entries = find_exact_course_entries(df, course_name)
        entry_count = len(course_entries)
        required_total += entry_count
        status = f"找到 {entry_count} 条记录" if entry_count > 0 else "未找到"
        print(f"  {course_name}：{status}")
    print(f"  必修课程总条目数：{required_total}")
    
    print("\n选修课程组分析：")
    choice_total = 0
    for group_name, courses in choice_groups.items():
        print(f"  {group_name}：")
        group_total = 0
        
        if isinstance(courses, dict) and "keywords" in courses:
            # 处理关键词搜索
            keyword_courses = find_courses_containing_keywords(df, courses["keywords"])
            group_total = len(keyword_courses)
            print(f"    关键词搜索：{courses['keywords']}")
            print(f"    找到课程数：{group_total} 条记录")
            if not keyword_courses.empty:
                unique_course_names = keyword_courses['课程名'].unique()
                print(f"    课程类型数：{len(unique_course_names)} 种不同课程")
                for course in unique_course_names[:5]:  # 只显示前5个课程名
                    course_count = len(keyword_courses[keyword_courses['课程名'] == course])
                    print(f"      {course}：{course_count} 条记录")
                if len(unique_course_names) > 5:
                    print(f"      ...还有 {len(unique_course_names) - 5} 种其他课程")
        else:
            # 处理精确匹配
            for course_name in courses:
                course_entries = find_exact_course_entries(df, course_name)
                entry_count = len(course_entries)
                group_total += entry_count
                status = f"找到 {entry_count} 条记录" if entry_count > 0 else "未找到"
                print(f"    {course_name}：{status}")
        
        print(f"    该组总条目数：{group_total}")
        choice_total += group_total
    
    print(f"\n选修课程总条目数：{choice_total}")
    print(f"全部课程总条目数：{required_total + choice_total}")
    
    return combined_courses

def main():
    """主函数"""
    print("开始处理课程数据...")
    
    # 处理三个任务
    task1_result = process_task1_finance()
    print("\n")
    
    task2_result = process_task2_cs()
    print("\n")
    
    task3_result = process_task3_chemistry()
    
    print("\n" + "=" * 50)
    print("所有任务处理完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()

#任务一：
# 微积分A(2) 
# 多元微积分 
# 商务数据分析 
# 两门选一门：概率论与数理统计 、概率论与数理统计(社科类) 
# 以下选择一门：区块链技术金融应用、计量经济学(1)、营销分析、财务报表分析、深度学习及金融数据分析 
# 英语阅读写作(B)
# 毛泽东思想和中国特色社会主义理论体系概论
# 一年级男生体育(2)

# 对认知文明的课程感兴趣，尽量选一门：中国文明、中国古代文明、中国哲学(2) 、经典与想象:中国古代传说新读、《孟子》研读

#任务二：
# 微积分A(2)
# 大学物理B(1)
# 任选一门：计算机程序设计基础、计算机程序设计基础(2) 
# 任选一门：数字逻辑电路 、数字逻辑设计 
# 面向对象程序设计基础
# 英语阅读写作(A)
# 中国近现代史纲要
# 一年级女生体育(2)

# 对人机交互、心智相关的课程感兴趣，尽量选一门

# 任务3：
# 两门中任选一门：大学化学A、大学化学B
# 任选一门：概率论与数理统计、概率论与随机过程、概率论与随机过程(1) 、概率论与随机过程(2) 
# 物理化学(2) 
# 反应工程基础 
# 生物化学基础实验
# 英语听说交流(B)
# 中国马克思主义与当代
# 二年级男生篮球

# 对人工智能相关的课程感兴趣，尽量选择一门