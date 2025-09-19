import os
import json

def load_templates():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(current_dir, '../../components/expression_constructors.json')
    with open(templates_path, 'r', encoding='utf-8') as f:
        templates_list = json.load(f)
    return templates_list
        
def build_templates_list():
    templates_list = load_templates()
    """构建格式化的模板列表字符串"""
    templates = []
    templates_str = "template_id, description, parameters_description, python_codes\n"
    for template in templates_list:
        templates.append(f"{template['id']}, {template['description']}, {template['parameters_description']}, `python`{template['python_template']}")
    templates_str += "\n\n".join(templates)
    return templates_str 

def build_template_name_list():
    templates_list = load_templates()
    template_name_list = []
    for template in templates_list:
        template_name_list.append(f"{template['description']}")
    return template_name_list
    
def analyze_items(items):
    """分析实际的items数据，提取关键信息"""
    if not items:
        return "无课程数据"
    
    # 提取所有唯一的教师
    teachers = set()
    course_names = set()
    departments = set()
    credits = set()
    time_slots = set()
    drop_rates = set()
    cleaned_items = []
    for item in items:
        cleaned_item = dict(item)  # 浅拷贝
        for key in ['batch', 'chosen_when_confirmed', 'num', 'priority', 'priority_type']:
            if key in cleaned_item:
                del cleaned_item[key]
        cleaned_items.append(cleaned_item)
    items = cleaned_items
    # 将items内容倒序
    items = items[::-1]
    for item in items:
        if '主讲教师' in item:
            teachers.add(item['主讲教师'])
        if '课程名' in item:
            course_names.add(item['课程名'])
        if '开课院系' in item:
            departments.add(item['开课院系'])
        if '学分' in item:
            credits.add(item['学分'])
        if '掉课率' in item:
            drop_rates.add(item['掉课率'])
        if '上课时间' in item:
            # 解析多个时间段
            times = item['上课时间'].split(';')
            for time in times:
                time_slots.add(time.strip())
    
    analysis = []
    analysis.append(f"一共有 {len(items)} 门课程, 其中")
    # 构建课程到教师/院系/时间的映射
    course_to_teachers = {}
    course_to_departments = {}
    course_to_times = {}
    course_to_drop_rates = {}
    for it in items:
        name = it.get('课程名')
        if not name:
            continue
        if '主讲教师' in it:
            course_to_teachers.setdefault(name, set()).add(it['主讲教师'])
        if '开课院系' in it:
            course_to_departments.setdefault(name, set()).add(it['开课院系'])
        if '上课时间' in it:
            for t in it['上课时间'].split(';'):
                course_to_times.setdefault(name, set()).add(t.strip())
        if '掉课率' in it:
            course_to_drop_rates.setdefault(name, set()).add(it['掉课率'])
    # 逐课程展示对应关系
    teacher_lines = [f"{cn} -> {('/').join(sorted(list(ts)))}" for cn, ts in course_to_teachers.items()]
    dept_lines = [f"{cn} -> {('/').join(sorted(list(ds)))}" for cn, ds in course_to_departments.items()]
    time_lines = [f"{cn} -> {('/').join(sorted(list(ts)))}" for cn, ts in course_to_times.items()]
    drop_rate_lines = [f"{cn} -> {('/').join(sorted(list(dr)))}" for cn, dr in course_to_drop_rates.items()]
    analysis.append("课程-主讲教师: " + ("; ".join(teacher_lines) if teacher_lines else "无"))
    analysis.append("课程-开课院系: " + ("; ".join(dept_lines) if dept_lines else "无"))
    # analysis.append("课程-上课时间: " + ("; ".join(time_lines) if time_lines else "无"))
    # analysis.append("课程-掉课率: " + ("; ".join(drop_rate_lines) if drop_rate_lines else "无"))
    
    # 添加几个具体的课程示例
    analysis.append("\n示例课程(共3门):")
    for i, item in enumerate(items[:3]):
        analysis.append(f"  {i+1}. {item}")
    
    return "\n".join(analysis)

def analyze_items_names(items):
    """分析实际的items数据，提取关键信息"""
    if not items:
        return "无课程数据"
    
    # 提取所有唯一的教师
    teachers = set()
    course_names = set()
    departments = set()
    credits = set()
    time_slots = set()
    cleaned_items = []
    for item in items:
        cleaned_item = dict(item)  # 浅拷贝
        for key in ['batch', 'chosen_when_confirmed', 'num', 'priority_type']:
            if key in cleaned_item:
                del cleaned_item[key]
        cleaned_items.append(cleaned_item)
    items = cleaned_items
    # 将items内容倒序
    items = items[::-1]
    for item in items:
        if '主讲教师' in item:
            teachers.add(item['主讲教师'])
        if '课程名' in item:
            course_names.add(item['课程名'])
        if '开课院系' in item:
            departments.add(item['开课院系'])
        if '上课时间' in item:
            # 解析多个时间段
            times = item['上课时间'].split(';')
            for time in times:
                time_slots.add(time.strip())
    
    analysis = []
    analysis.append(f"一共有 {len(items)} 门课程, 其中")
    # 构建课程到教师/院系/时间的映射
    course_to_teachers = {}
    course_to_departments = {}
    course_to_times = {}
    for it in items:
        name = it.get('课程名')
        if not name:
            continue
        if '主讲教师' in it:
            course_to_teachers.setdefault(name, set()).add(it['主讲教师'])
        if '开课院系' in it:
            course_to_departments.setdefault(name, set()).add(it['开课院系'])
        if '上课时间' in it:
            for t in it['上课时间'].split(';'):
                course_to_times.setdefault(name, set()).add(t.strip())
    # 逐课程展示对应关系
    teacher_lines = [f"{cn} -> {('/').join(sorted(list(ts)))}" for cn, ts in course_to_teachers.items()]
    dept_lines = [f"{cn} -> {('/').join(sorted(list(ds)))}" for cn, ds in course_to_departments.items()]
    time_lines = [f"{cn} -> {('/').join(sorted(list(ts)))}" for cn, ts in course_to_times.items()]
    analysis.append("课程-主讲教师: " + ("; ".join(teacher_lines) if teacher_lines else "无"))
    analysis.append("课程-开课院系: " + ("; ".join(dept_lines) if dept_lines else "无"))
    analysis.append("课程-上课时间: " + ("; ".join(time_lines) if time_lines else "无"))
    
    # 添加几个具体的课程示例
    analysis.append("\n示例课程(共3门):")
    for i, item in enumerate(items[:3]):
        analysis.append(f"  {i+1}. {item}")
    
    return "\n".join(analysis)