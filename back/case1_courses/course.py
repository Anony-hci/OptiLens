import csv
import json
from case1_courses.features.features_py import features_py
import inspect
import os
from components.templates import search_related_items, count_target_items, count_credits

items_description = """
The course includes five columns: 课程名，学分，主讲教师，上课时间，掉课率。
上课时间包括三个部分，格式为x-y(z)。
1. x for weekday (e.g., 4 means Thursday).
2. y for period (e.g., 1 means the first period). 早上包括periods[1,2], period-1(8:00~9:35), period-2(9:50~12:15); 下午包括periods[3,4,5], period-3(13:30~15:05), period-4(15:20~16:55), period-5(17:05~18:40); 晚上包括periods[6], period-6(19:20~21:45).
3. z for week (e.g., 1-8 means the first eight weeks).

Class Time Examples：
（1）2-3(全周): the class of third period on Tuesday.
（2）3-1(全周);5-2(全周): the class of first period on Wednesday and second period on Friday.
（3）(全周): no specific weekday-period.
"""
item_key = "x_课程名_主讲教师_上课时间"


class FeatureCalculator:
    """参数化特征计算器"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """加载 expression_constructors.json 中的模板"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_path = os.path.join(current_dir, '../components/expression_constructors.json')
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates_list = json.load(f)
            return {t['id']: t for t in templates_list}
        except Exception as e:
            print(f"Warning: Could not load templates: {e}")
            return {}
    
    def calculate_feature(self, feature_def, items, solution_vars, additional_vars=None):
        """
        计算特征值
        feature_def: 特征定义，可以是字符串（旧格式）或字典（参数化格式）
        items: 课程数据
        solution_vars: 解的变量值字典 (变量名 -> 0/1)
        additional_vars: 额外的变量信息，用于更精确的特征计算
        """
        if isinstance(feature_def, dict) and 'template_id' in feature_def:
            result = self._calculate_parameterized_feature(feature_def, items, solution_vars)
        elif isinstance(feature_def, dict) and 'expression_type' in feature_def:
            result = self._calculate_expression_type_feature(feature_def, items, solution_vars, additional_vars)
        else:
            result = self._calculate_legacy_feature(feature_def, items, solution_vars)
        
        # 确保返回的结果是可序列化的
        if isinstance(result, (int, float, str, bool)) or result is None:
            return result
        else:
            # 如果结果不是基本类型，转换为字符串
            return str(result)
    
    def _calculate_parameterized_feature(self, feature_def, items, solution_vars):
        """计算参数化特征"""
        template_id = feature_def.get('template_id')
        parameters = feature_def.get('parameters', {})
        
        # 确保 template_id 是整数类型
        if isinstance(template_id, str):
            try:
                template_id = int(template_id)
            except ValueError:
                print(f"Warning: Invalid template_id: {template_id}")
                return 0
        
        if template_id not in self.templates:
            print(f"Warning: Template {template_id} not found")
            print(f"Available templates: {list(self.templates.keys())}")
            return 0
            
        template = self.templates[template_id]
        
        # 构建完整的 Python 代码
        python_code = template['python_template'] + '\n'
        
        # 构建函数调用，替换参数
        call_code = template['call_template']
        for param_name, param_value in parameters.items():
            placeholder = f'{{{param_name}}}'
            # 直接用参数值替换占位符，不添加引号
            # 模板中已经包含了正确的引号格式
            call_code = call_code.replace(placeholder, str(param_value))
        
        python_code += call_code
        
        # 执行并返回结果
        local_scope = {"items": items, "vars": solution_vars}
        try:
            exec(python_code, globals(), local_scope)
            result = local_scope.get('results', 0)
            # 确保结果是可序列化的
            if isinstance(result, (int, float, str, bool)) or result is None:
                return result
            else:
                return str(result)
        except Exception as e:
            print(f"Error calculating parameterized feature: {e}")
            print(f"Code: {python_code}")
            return 0
    
    def _calculate_expression_type_feature(self, feature_def, items, solution_vars, additional_vars=None):
        """计算 expression_type 格式的特征"""
        expression_type = feature_def.get('expression_type', '')
        target_items = feature_def.get('target_items', {})
        
        # 根据 target_items 筛选相关课程
        target_courses = search_related_items(items, **target_items)
        
        try:
            if expression_type == "count_courses":
                # 计算选中的课程数量
                result = 0
                for item in target_courses:
                    var_name = f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"
                    if var_name in solution_vars:
                        result += solution_vars[var_name]
                return result
                
            elif expression_type == "count_credits":
                # 计算选中课程的总学分
                result = 0
                for item in target_courses:
                    var_name = f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"
                    if var_name in solution_vars and solution_vars[var_name] > 0:
                        result += float(item['学分'])
                return result
                
            elif expression_type == "count_days":
                # 使用 additional_vars 中的 day_vars 计算上课天数
                if additional_vars and "day_vars" in additional_vars:
                    day_vars = additional_vars["day_vars"]
                    days_count = 0
                    for day, day_var in day_vars.items():
                        # day_var 是 Gurobi 变量对象，直接获取值
                        if hasattr(day_var, 'X') and day_var.X > 0.5:
                            days_count += 1
                    return days_count
                else:
                    # 回退到基于课程时间的计算
                    days_with_courses = set()
                    for item in target_courses:
                        var_name = f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"
                        if var_name in solution_vars and solution_vars[var_name] > 0:
                            # 解析上课时间，提取天数
                            time_list = item['上课时间'].split(';')
                            for time in time_list:
                                time = time.strip()
                                if '-' in time and '(' in time:
                                    time_point = time.split('(')[0]  # 提取时间点(如3-6)
                                    if '-' in time_point:
                                        day = int(time_point.split('-')[0])
                                        days_with_courses.add(day)
                    return len(days_with_courses)
                
            elif expression_type == "count_consecutive_courses":
                # 使用 additional_vars 中的 consecutive_vars 计算连续课程数量
                if additional_vars and "consecutive_vars" in additional_vars:
                    consecutive_vars = additional_vars["consecutive_vars"]
                    consecutive_count = 0
                    
                    # 遍历所有连续变量
                    for key, consecutive_var in consecutive_vars.items():
                        if hasattr(consecutive_var, 'X') and consecutive_var.X > 0.5:
                            consecutive_count += 1
                    
                    return consecutive_count
                    
                else:
                    return 0
                    # 回退到基于课程时间的计算
                    consecutive_count = 0
                    
                    # 检查是否指定了特定的课程名
                    if 'course_name' in target_items and isinstance(target_items['course_name'], list):
                        # 处理指定课程名的情况
                        course_names = target_items['course_name']
                        if len(course_names) >= 2:
                            # 计算所有可能的两两组合
                            for i in range(len(course_names)):
                                for j in range(i + 1, len(course_names)):
                                    course1_name = course_names[i]
                                    course2_name = course_names[j]
                                    
                                    # 获取这两个课程的所有实例
                                    course1_instances = search_related_items(items, course_name=[course1_name])
                                    course2_instances = search_related_items(items, course_name=[course2_name])
                                    
                                    # 分析两个课程的时间段，找出是否有连续的情况
                                    for course1 in course1_instances:
                                        for course2 in course2_instances:
                                            var1_name = f"x_{course1['课程名']}_{course1['主讲教师']}_{course1['上课时间']}"
                                            var2_name = f"x_{course2['课程名']}_{course2['主讲教师']}_{course2['上课时间']}"
                                            
                                            # 只有当两个课程都被选中时才考虑连续性
                                            if (var1_name in solution_vars and solution_vars[var1_name] > 0 and
                                                var2_name in solution_vars and solution_vars[var2_name] > 0):
                                                
                                                # 解析两个课程的时间
                                                time1_list = course1['上课时间'].split(';')
                                                time2_list = course2['上课时间'].split(';')
                                                
                                                for time1 in time1_list:
                                                    for time2 in time2_list:
                                                        # 解析时间格式：如 "3-2(全周)" -> day=3, period=2
                                                        if '(' in time1 and '(' in time2:
                                                            time1_clean = time1.split('(')[0]  # "3-2"
                                                            time2_clean = time2.split('(')[0]  # "3-2"
                                                            
                                                            if '-' in time1_clean and '-' in time2_clean:
                                                                day1, period1 = map(int, time1_clean.split('-'))
                                                                day2, period2 = map(int, time2_clean.split('-'))
                                                                
                                                                # 判断是否同一天且时间段相邻
                                                                if day1 == day2 and abs(period1 - period2) == 1:
                                                                    consecutive_count += 1
                    
                    elif 'period' in target_items and isinstance(target_items['period'], list):
                        # 处理指定连续时间段的情况
                        periods = target_items['period']
                        # 检查是否连续
                        if len(periods) >= 2 and all(periods[i+1] - periods[i] == 1 for i in range(len(periods)-1)):
                            # 为每一天计算连续时间段
                            for day in range(1, 6):  # 周一到周五
                                # 获取这个连续时间段的所有课程
                                period_courses = []
                                for period in periods:
                                    period_courses.extend(search_related_items(items, time=f"{day}-{period}"))
                                
                                # 检查是否有课程被选中
                                selected_courses = []
                                for course in period_courses:
                                    var_name = f"x_{course['课程名']}_{course['主讲教师']}_{course['上课时间']}"
                                    if var_name in solution_vars and solution_vars[var_name] > 0:
                                        selected_courses.append(course)
                                
                                # 如果这个连续时间段有课程被选中，则计数
                                if len(selected_courses) > 0:
                                    consecutive_count += 1
                    
                    else:
                        # 默认情况：计算所有连续时间段
                        # 按天分组课程
                        day_courses = {}
                        for item in target_courses:
                            var_name = f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"
                            if var_name in solution_vars and solution_vars[var_name] > 0:
                                time_list = item['上课时间'].split(';')
                                for time in time_list:
                                    time = time.strip()
                                    if '-' in time and '(' in time:
                                        time_point = time.split('(')[0]
                                        if '-' in time_point:
                                            day, period = map(int, time_point.split('-'))
                                            if day not in day_courses:
                                                day_courses[day] = []
                                            day_courses[day].append(period)
                        
                        # 计算连续时间段
                        for day, periods in day_courses.items():
                            periods = sorted(periods)
                            for i in range(len(periods) - 1):
                                if periods[i+1] - periods[i] == 1:
                                    consecutive_count += 1
                    
                    return consecutive_count
                
            else:
                print(f"未知的表达式类型: {expression_type}")
                return 0
                
        except Exception as e:
            print(f"Error calculating expression_type feature: {e}")
            return 0
    
    def _calculate_legacy_feature(self, feature_def, items, solution_vars):
        """计算传统格式的特征"""
        if isinstance(feature_def, str) and feature_def.strip().startswith('lambda'):
            # Lambda 表达式
            try:
                lambda_func = eval(feature_def)
                params = inspect.signature(lambda_func).parameters
                if len(params) == 2:
                    result = lambda_func(solution_vars, items)
                elif len(params) == 1:
                    result = lambda_func(solution_vars)
                else:
                    print(f"Unexpected lambda parameters: {len(params)}")
                    return 0
                
                # 确保结果是可序列化的
                if isinstance(result, (int, float, str, bool)) or result is None:
                    return result
                else:
                    return str(result)
            except Exception as e:
                print(f"Error evaluating lambda feature: {e}")
                return 0
        else:
            # Python 代码字符串
            local_scope = {"items": items, "vars": solution_vars}
            try:
                exec(feature_def, globals(), local_scope)
                result = local_scope.get('results', 0)
                # 确保结果是可序列化的
                if isinstance(result, (int, float, str, bool)) or result is None:
                    return result
                else:
                    return str(result)
            except Exception as e:
                print(f"Error executing feature code: {e}")
                return 0


# 创建全局特征计算器实例
feature_calculator = FeatureCalculator()


def get_current_features():
    """
    获取当前的特征表达式，优先从文件读取，如果文件不存在则使用默认值
    """
    try:
        with open('features/feature_exprs.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

    
def update_features(added_feature_exprs):
    feature_exprs_lambda = {**features_py, **added_feature_exprs}
    import os
    from datetime import datetime
    
    # 确保目录存在
    log_dir = 'features/features_logs/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime('%m%d_%H%M%S')
    log_filename = f'feature_exprs_{timestamp}.json'
    log_filepath = os.path.join(log_dir, log_filename)
    
    # 保存到带时间戳的日志文件
    with open(log_filepath, 'w', encoding='utf-8') as file:
        json.dump(feature_exprs_lambda, file, ensure_ascii=False, indent=4)

def add_features_to_results(results, items, feature_exprs, problem_model, optimization_model=None):
    # 收集所有特征的键和值
    all_feature_values = {}
    
    # 获取 additional_vars（如果可用）
    additional_vars = optimization_model.additional_vars if optimization_model and hasattr(optimization_model, 'additional_vars') else None
    
    # 首先为每个solution计算features
    for solution in results['solutions']:
        features = get_features(solution['Variables'], items, feature_exprs, problem_model, additional_vars)
        # features = get_features_lambda(solution['Variables'], items, feature_exprs, problem_model)
        solution['features'] = features
        
        # 收集每个特征的所有值
        for feature_key, feature_value in features.items():
            if feature_key not in all_feature_values:
                all_feature_values[feature_key] = {}
            
            # 确保feature_value是可序列化的
            if isinstance(feature_value, (int, float, str, bool)) or feature_value is None:
                value_key = str(feature_value)
            else:
                # 如果值不可序列化，转换为字符串
                value_key = str(feature_value)
                print(f"警告：特征 '{feature_key}' 的值类型为 {type(feature_value)}，已转换为字符串")
            
            all_feature_values[feature_key][value_key] = all_feature_values[feature_key].get(value_key, 0) + 1
    
    # 将统计信息添加到结果中
    results['features_statistics'] = all_feature_values
    
    return results

def get_features(variables, items, feature_exprs, problem_model, additional_vars=None):
    features = {}
    
    # 调试：检查variables参数
    for var_name, var_value in variables.items():
        if not isinstance(var_value, (int, float, str, bool)) and var_value is not None:
            print(f"警告：变量 '{var_name}' 的值类型为 {type(var_value)}，可能不可序列化")
            # 将不可序列化的值转换为数值
            try:
                variables[var_name] = float(var_value)
            except (ValueError, TypeError):
                variables[var_name] = 0
    
    # 1. 计算自定义特征
    for feature_name, feature_expr in feature_exprs.items():
        if feature_name.startswith("con") or feature_name.startswith("obj"): 
            continue
        
        # 使用特征计算器计算特征值
        result = feature_calculator.calculate_feature(feature_expr, items, variables, additional_vars)
        # 确保结果是可序列化的
        if isinstance(result, (int, float, str, bool)) or result is None:
            features[feature_name] = round(result, 2) if isinstance(result, (float)) else result
        else:
            # 如果结果不是基本类型，转换为字符串
            features[feature_name] = str(result)
    
    # 2. 计算目标函数的值
    for objective in problem_model.objectives:
        feature_name = objective['name']
        feature_expr = objective['expression']
        
        # 检查是否是简单的变量名（字符串类型且在variables中）
        if isinstance(feature_expr, str) and feature_expr in variables:
            continue
        
        if 'expression' in feature_expr:
            feature_expr = feature_expr['expression']
            
        # 使用特征计算器计算目标函数值
        result = feature_calculator.calculate_feature(feature_expr, items, variables, additional_vars)
        # 确保结果是可序列化的
        if isinstance(result, (int, float, str, bool)) or result is None:
            features[feature_name] = round(result, 2) if isinstance(result, (float)) else result
        else:
            # 如果结果不是基本类型，转换为字符串
            features[feature_name] = str(result)
    
    # 3. 计算约束条件的值
    for constraint in problem_model.constraints:
        # 跳过没有描述的约束
        feature_name = constraint['name']
        lhs_expr = constraint['lhs']
        
        # 检查是否是简单的变量名（字符串类型且在variables中）
        if isinstance(lhs_expr, str) and lhs_expr in variables:
            continue
        
        if 'expression' in lhs_expr:
            lhs_expr = lhs_expr['expression']
            
        # 使用特征计算器计算约束左侧表达式的值
        result = feature_calculator.calculate_feature(lhs_expr, items, variables, additional_vars)
        # 确保结果是可序列化的
        if isinstance(result, (int, float, str, bool)) or result is None:
            features[feature_name] = round(result, 2) if isinstance(result, (float)) else result
        else:
            # 如果结果不是基本类型，转换为字符串
            features[feature_name] = str(result)
        
    return features

def get_features_lambda(variables, items, feature_exprs_lambda, problem_model):
    features = {}
    # Iterate over the expressions and compute each feature
    for feature_name, feature_expr in feature_exprs_lambda.items():
        # Use eval to evaluate the feature expression
        try:
            # Prepare the context for eval
            context = {'vars': variables, 'courses': items}
            feature_lambda = eval(feature_expr, context)
            features[feature_name] = feature_lambda(variables, items)
        except Exception as e:
            print(f"Error evaluating feature '{feature_name}': {e}")
            features[feature_name] = None  # If evaluation fails, assign None or a default value
    
    for objective in problem_model.objectives:
        context = {'vars': variables, 'items': items}
        feature_name = "obj:" + objective['description']
        feature_expr = objective['expression']
        feature_lambda = eval(feature_expr, context)
        features[feature_name] = feature_lambda(variables, items)

    return features


def generate_time_conflict_constraints(courses):
    
    def parse_week_range(time_str):
        if '(全周)' in time_str:
            return list(range(1, 17))
        elif '(前八周)' in time_str:
            return list(range(1, 9))
        elif '(后八周)' in time_str:
            return list(range(9, 17))
        elif '(单周)' in time_str:
            return list(range(1, 17, 2))
        elif '(双周)' in time_str:
            return list(range(2, 17, 2))
        elif '周)' in time_str:
            week_str = time_str[time_str.find('(')+1:time_str.find('周')]
            weeks = []
            if ',' in week_str:
                # 处理 (1,3,6周) 或 (1, 3-12周) 格式
                for part in week_str.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        weeks.extend(list(range(start, end+1)))
                    else:
                        weeks.append(int(part))
            elif '-' in week_str:
                # 处理 5周 格式 (表示1-5周)
                start, end = map(int, week_str.split('-'))
                weeks = list(range(start, end+1))
            else:
                # 处理 (1周) 格式
                weeks = [int(week_str)]
            return weeks
        return None

    def has_time_overlap(time1, time2):
        week_range1 = parse_week_range(time1)
        week_range2 = parse_week_range(time2)
        if not week_range1 or not week_range2:
            return False
            
        # 检查两个列表是否有重叠的元素
        for week in week_range1:
            if week in week_range2:
                return True
                
        return False
    
    constraints = []
    # 收集所有时间段及其对应的课程
    time_slots = {}  # 格式: {时间点: [(课程名, 教师, 上课时间), ...]}
    # 首先收集每个时间点的所有课程
    for course in courses:
        for time in course['上课时间'].split(';'):
            time = time.strip()
            if ('-' not in time):
                continue
            time_point = time[:time.find('(')]  # 提取时间点(如3-6)
            
            if time_point not in time_slots:
                time_slots[time_point] = []
            time_slots[time_point].append((course['课程名'], course['主讲教师'], course['上课时间']))

    # 对每个时间点生成约束
    for time_point, courses_at_time in time_slots.items():
        if len(courses_at_time) > 1:  # 只有当同一时间点有多个课程时才需要约束
            # 收集在这个时间点有重叠的课程
            overlapping_courses = []
            for i, (course1_name, teacher1, time1) in enumerate(courses_at_time):
                for course2_name, teacher2, time2 in courses_at_time[i+1:]:
                    if has_time_overlap(time1, time2):
                        overlapping_courses.append((course1_name, teacher1, time1))
                        overlapping_courses.append((course2_name, teacher2, time2))
            
            if overlapping_courses:
                # 去重
                overlapping_courses = list(set(overlapping_courses))
                # 生成约束：所有重叠课程的选择变量之和不能超过1
                lhs = " + ".join([f"vars['x_{course_name}_{teacher}_{time}']" 
                                for course_name, teacher, time in overlapping_courses])
                
                constraints.append({
                    "lhs": f"lambda vars: {lhs}",
                    "constraint_type": "<=",
                    "rhs": 1,
                    "description": f"时间点 {time_point} 的课程冲突",
                    "type": "上课时间不能重叠",
                })

    return constraints

def generate_same_course_constraints(courses, vars_name='x'):
    """
    生成同一门课程只能选一节的约束。
    根据课程名对课程进行分组,对于每个有多节课的课程,生成约束确保只能选择其中一节。
    """
    constraints = []
    
    # 按课程名分组收集课程
    course_groups = {}
    for course in courses:
        course_name = course['课程名']
        if course_name not in course_groups:
            course_groups[course_name] = []
        course_groups[course_name].append(course)
    
    # 对每个有多节课的课程生成约束
    for course_name, course_list in course_groups.items():
        if len(course_list) > 1:  # 只有当同一课程有多节课时才需要约束
            # 生成约束：同一课程的所有课程选择变量之和不能超过1
            lhs = " + ".join([f"vars['x_{course['课程名']}_{course['主讲教师']}_{course['上课时间']}']" 
                            for course in course_list])
            
            constraints.append({
                "lhs": f"lambda vars: {lhs}",
                "constraint_type": "<=",
                "rhs": 1,
                "description": f"课程 {course_name} 只能选择一节课",
                "type": "同一门课程只能选一节",
            })

    return constraints


def generate_required_course_constraints(required_course_names, courses, vars_name='x'):
    """
    生成必修课程的选择约束，确保每门必修课程必须选择一节。
    
    参数:
    required_course_names -- 必修课程名称列表
    courses -- 所有课程的列表
    vars_name -- 决策变量的前缀，默认为'x'
    
    返回:
    constraints -- 必修课约束列表
    """
    constraints = []
    
    # 对每门必修课生成约束
    for course_name in required_course_names:
        # 找出该课程名下的所有课程
        course_sections = [course for course in courses if course['课程名'] == course_name]
        
        if not course_sections:
            print(f"警告: 未找到课程 '{course_name}' 的任何课节")
            continue
        
        # 生成约束：该课程的所有课节选择变量之和必须等于1
        lhs = " + ".join([
            f"vars['x_{course_name}_{course['主讲教师']}_{course['上课时间']}']" 
            for course in course_sections
        ])
        
        # 如果没有找到任何课节，跳过
        if not lhs:
            continue
        
        constraints.append({
            "lhs": f"lambda vars: {lhs}",
            "constraint_type": "==",
            "rhs": 1,
            "description": f"必修课 {course_name} 必须选择一节",
            "type": "必修课必须选择",
        })
    
    return constraints

def get_default_problem_model():
    problem_model = {
        "updated_objectives": [{
            "type": "add",
            "objective_type": "maximize",
            "expression": "results = vars['x_数值分析_喻文健_5-2(全周)'] + vars['x_数值分析_喻文健_5-3(全周)']",
            "description": "最大化选择的课程数量", 
            },
            {
            "type": "add",
            "objective_type": "minimize",
            "expression": "lambda vars, items: sum(1 for item in items if any(vars.get('x_' + item['课程名'] + '_' + item['主讲教师'] + '_' + item['上课时间'], 0) and (time == '(全周)' and 0 or (time.find('-') != -1 and int(time.split('-')[1].split('(')[0]) in [1])) for time in item['上课时间'].split(',')))",
            "description": "最小化早8课程数量", 
            },   
            {
            "type": "add",
            "objective_type": "minimize",
            "expression": "lambda vars, items: sum(1 for item in items if any(vars.get('x_' + item['课程名'] + '_' + item['主讲教师'] + '_' + item['上课时间'], 0) and (time == '(全周)' and 0 or (time.find('-') != -1 and int(time.split('-')[1].split('(')[0]) in [6])) for time in item['上课时间'].split(',')))",
            "description": "最小化晚上课程数量", 
            },       
        ],
        "updated_constraints": [{
        "type": "update",
        "lhs": """"def total_credits(items, vars):\\n    total_credits = 0\\n    for item in items:\\n        key = f\\"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}\\"\\n        if key in vars:\\n            total_credits += int(item['学分']) * vars[key]\\n    return total_credits\\nresults = total_credits(items, vars)""",
        "constraint_type": "<=",
        "rhs": 32,
        "lhs_description": "所有选中的课程乘上对应的学分后相加",
        "description": "总学分小于等于32",
        "old_description": "最大化总学分"
    },
    {
        "type": "add",
        "lhs": "results = vars['x_数值分析_喻文健_5-2(全周)'] + vars['x_数值分析_喻文健_5-3(全周)']",
        "constraint_type": "==",
        "rhs": 1,
        "lhs_description": "喻文健的数值分析课",
        "description": "选择喻文健的数值分析课",
    },]
        
    }
    return problem_model

def get_global_constraints(items, required_courses):
    time_conflict_constraints = generate_time_conflict_constraints(items)
    courses_constraints = generate_same_course_constraints(items)
    required_courses_constraints = generate_required_course_constraints(required_courses, items)
    
    # 生成必修课程约束
    # required_course_constraints = generate_required_course_constraints(items)
    # global_constraints = time_conflict_constraints + required_course_constraints
    # print(f"时间冲突约束: {time_conflict_constraints}")
    # print(f"必修课程约束: {required_course_constraints}")
    return time_conflict_constraints + courses_constraints + required_courses_constraints

def calculate_total_credits(items_key, variables):
    total_credits = 0
    total_courses = 0
    selected_vars = {var_name for var_name, value in variables.items() if value == 1.0}
    for item in items_key:
        if item['var_name'] in selected_vars:
            total_credits += float(item['学分'])
            total_courses += 1
            # print(f"Selected course: {item['课程名']}, Teacher: {item['主讲教师']}, Credits: {item['学分']}")
    # print(f"Total credits: {total_credits}")
    # print(f"Total courses: {total_courses}")
    return total_credits, total_courses


def count_classes(items_key, variables):
    selected_vars = {var_name for var_name, value in variables.items() if value == 1.0}
    for item in items_key:
        if item['var_name'] in selected_vars:
            class_times = item['上课时间'].split(',')
            print(f"class_times: {class_times}")
            for class_time in class_times:
                # Start of Selection
                if '-' in class_time:
                    day, period_with_suffix = class_time.split('-')
                else:
                    continue
                period = period_with_suffix.split('(')[0]
                print(f"class_time: {class_time}, day: {day}, period: {period}")
                if period == '1' or period == 1:
                    early_morning_count += 1
                if period == '6'or period == 6:
                    late_evening_count +=1
    print(f"Total early morning classes: {early_morning_count}")
    print(f"Total late evening classes: {late_evening_count}")
    return early_morning_count, late_evening_count



def search_course(csv_file, course_list=None, type=None, label=None):
    course_info = []

    # 打开并读取CSV文件
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # 遍历 CSV 文件的每一行
        for row in reader:
            course_name = row.get('课程名')  # 假设 CSV 中有"课程名"这一列
            
            teacher = row.get('主讲教师')  # 假设 CSV 中有"主讲教师"这一列
            class_time = row.get('上课时间')  # 假设 CSV 中有"上课时间"这一列
            credit = row.get('学分')
            depart = row.get('开课院系')
            drop_rate = row.get('掉课率')
            # 为每个符合条件的课程创建一个字典，并添加到列表中
            if (course_name in course_list):
                course_info.append({
                    '课程名': course_name,
                    '主讲教师': teacher,
                    '学分': credit,
                    '上课时间': class_time,
                    '开课院系': depart,
                    '掉课率': drop_rate,
                })
    
    return course_info

def merge_course_info(*course_info):
    # 初始化一个空的列表用于存放合并后的课程信息
    merged_info = []
    
    # 遍历所有传入的课程信息列表
    for course_list in course_info:
        # 将每个列表的内容添加到 merged_info 中
        merged_info.extend(course_list)
    
    return merged_info
    


