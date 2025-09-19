import sys
import os
# 将项目根目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import re
import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from llm.chat import openai_client, construct_user
from llm.prompts.entityExtractionPrompt import EntityExtractionPrompt
from llm.prompts.templateRetrievalPrompt import TemplateRetrievalPrompt
from llm.prompts.templateGenerationPrompt import TemplateGenerationPrompt
from llm.prompts.parameterFillingPrompt import ParameterFillingPrompt
from llm.prompts.modelUpdatePrompt import ModelUpdatePrompt
from llm.prompts.classifyInputTypePrompt import classifyInputTypePrompt
from llm.prompts.setCoursePriorityPrompt import setCoursePriorityPrompt
from llm.prompts.diagnosisPrompt import diagnosisPrompt
from llm.prompts.instructionAnalysisPrompt import instructionAnalysisPrompt
from components.OptimizationModel import OptimizationModel
from components.ProblemModel import ProblemModel
from case1_courses.course import search_course, merge_course_info, get_global_constraints,  add_features_to_results, items_description, item_key, generate_required_course_constraints
from case1_courses.features.features_py import features_py
from components.code2gurobi import lhs_to_expr


def generate_features(query, items, results, feature_exprs_lambda):    
    is_valid, generated_expressions, details, exact_match = generate_expression(None, query, items, items_description)
    if not is_valid:
        return None, None
    added_feature_exprs = {}
    for expression in generated_expressions:
        feature_name = expression['name']
        if 'parameters' in expression and expression['parameters']:
            filled_feature_name = feature_name
            for param_key, param_value in expression['parameters'].items():
                placeholder = f"<{param_key}>"
                filled_feature_name = filled_feature_name.replace(placeholder, str(param_value))
            feature_name = filled_feature_name
        if 'expression' in expression:
            feature_expr = expression['expression']
        elif 'template_id' in expression:
            feature_expr = {'template_id': expression['template_id'], 'parameters': expression['parameters']}
        added_feature_exprs[feature_name] = feature_expr
        combined_feature_exprs = {**feature_exprs_lambda, **added_feature_exprs}
    print(f"updated feature_exprs_lambda: {combined_feature_exprs}")
    return added_feature_exprs, combined_feature_exprs


def problem_solving(selected_items, problem_model, required_courses, is_incremental = False, base_solution = None, added_variables = None, is_set = True):
    pbModel = ProblemModel()
    global_constraints = get_global_constraints(selected_items, required_courses)
    pbModel.set_global_constraints(global_constraints) 
    # pbModel.set_default_model()
    if is_set:
        pbModel.set_problem_model(problem_model)
    else:
        pbModel.update_problem_model(problem_model)
    optiModel = OptimizationModel()
    if (is_incremental):
        optiModel.set_incremental_optimization_model(base_solution, added_variables, selected_items, pbModel)
    else:
        optiModel.set_optimization_model(selected_items, pbModel)
    results = optiModel.optimize()
    return pbModel, optiModel, results

def get_featureExprs(features_py, problem_model):
    # 创建一个新字典，复制 features_py 中的所有特征
    featuresAll = features_py.copy()
    # 添加 problem_model 中的目标函数作为特征
    for objective in problem_model.objectives:
        key = objective['name']
        featuresAll[key] = objective['expression']
    # 添加 problem_model 中的目标函数作为特征
    for constraint in problem_model.constraints:
        key = constraint['name'] 
        featuresAll[key] = constraint['lhs']
    
    return featuresAll

def get_items():
    csv_file = "../front/src/data/courses5.csv"
    course_list = ['微积分A(2)', '大学物理B(1)', '面向对象程序设计基础', '计算机程序设计基础', '计算机程序设计基础(2)', '数字逻辑电路', '数字逻辑设计', '英语阅读写作(B)', 
      '中国近现代史纲要', '一年级女生体育(2)', '人机交互', '心智',
      '学术探知', '中国传统雕塑彩塑', '自然辩证法概论', 
      '区块链技术金融应用', '计量经济学(1)', 
      '财务报表分析', '深度学习及金融数据分析']
    items = search_course(csv_file, course_list)
    return items

def case1_course():
    # input_text = "下午的课要1节"
    input_text = "硬课少一点"
    csv_file = "../front/src/data/courses5.csv"
    course_list = ["微积分A(2)","大学物理B(1)","离散数学(2)","高等线性代数选讲","面向对象程序设计基础","中国近现代史纲要","英语(2)","一年级女生体育(2)","写作与沟通", "大学化学A", "大学化学B"]
    required_courses = ["微积分A(2)","大学物理B(1)","离散数学(2)"]
    items = search_course(csv_file, course_list)
    return input_text, items, required_courses

def load_templates(mode=False):
    # 获取 expression_constructors.json 的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    constructors_path = os.path.join(current_dir, './expression_constructors.json')

    # 读取原有的 expression_constructors
    if os.path.exists(constructors_path):
        with open(constructors_path, 'r', encoding='utf-8') as f:
            expression_constructors = json.load(f)
            if mode:
                return {t['id']: t for t in expression_constructors}
    else:
        expression_constructors = []
    return expression_constructors

# 新增函数：用于将生成的模板保存到 expression_constructors.json
def save_generated_templates_to_constructors(generated_templates):
    expression_constructors = load_templates()
    # 检查已存在的 id，避免重复
    existing_ids = set()
    for t in expression_constructors:
        if 'id' in t:
            existing_ids.add(int(t['id']))

    # 只添加 id 不重复的模板
    new_templates = []
    for template in generated_templates:
        if 'id' in template:
            try:
                template['id'] = int(template['id'])
            except Exception:
                continue  # 跳过无法转为int的模板
        if int(template.get('id', '')) not in existing_ids:
            expression_constructors.append(template)
            new_templates.append(template)
            existing_ids.add(int(template.get('id', '')))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    constructors_path = os.path.join(current_dir, './expression_constructors.json')
    # 保存回 expression_constructors.json
    with open(constructors_path, 'w', encoding='utf-8') as f:
        json.dump(expression_constructors, f, ensure_ascii=False, indent=2)

    print(f"已保存 {len(new_templates)} 个新模板到 expression_constructors.json")

def template_retrieval(instruction, items_description, items, print_prompt = False):
    extraction_prompt = TemplateRetrievalPrompt(instruction, items_description, items)
    extraction_result = openai_client.sync_call_gpt(
        extraction_prompt.SystemPrompt, 
        [construct_user(extraction_prompt.UserPrompt)], 
        "gpt-4o", 
        return_json=True
    )
    if print_prompt:
        print(f"=== template_retrieval prompt===\n system: {extraction_prompt.SystemPrompt}, \n\n user: {extraction_prompt.UserPrompt}")
    return extraction_result

def template_generation(instruction, items, items_description, print_prompt = False):
    template_generation_prompt = TemplateGenerationPrompt(instruction, items, items_description)
    template_generation_result = openai_client.sync_call_gpt(
        template_generation_prompt.SystemPrompt,
        [construct_user(template_generation_prompt.UserPrompt)],   
        "gpt-4o",
        return_json=True
    )
    if print_prompt:
        print(f"=== template_generation prompt===\n system: {template_generation_prompt.SystemPrompt}, \n\n user: {template_generation_prompt.UserPrompt}")
    return template_generation_result

def test_generated_expressions(expression, items, vars):
    templates = load_templates(mode=True)
    print("==test_generated_expressions==\n")
    if 'expression' in expression:
        linExpr = lhs_to_expr(expression['expression'], items, vars, templates)
    else:
        linExpr = lhs_to_expr(expression, items, vars, templates)
    if not isinstance(linExpr, gp.LinExpr) and not isinstance(linExpr, gp.QuadExpr):
        print(f"not linExpr or quadExpr: {linExpr}")
        return False, linExpr
    return True, None

def parameter_filling(instruction, relevant_template_ids, items_description, item_key, items, print_prompt = False):
    param_fill_prompt = ParameterFillingPrompt(
        instruction, 
        relevant_template_ids, 
        items_description, 
        item_key,
        items 
    )   
    param_fill_result = openai_client.sync_call_gpt(
        param_fill_prompt.SystemPrompt,
        [construct_user(param_fill_prompt.UserPrompt)],
        "gpt-4o",
        return_json=True
    )   
    if print_prompt:
        print(f"=== parameter_filling prompt===\n system: {param_fill_prompt.SystemPrompt}, \n\n user: {param_fill_prompt.UserPrompt}")
    return param_fill_result

def model_update(instruction, generated_templates, previous_model, items_description, item_key, print_prompt = False):
    update_prompt = ModelUpdatePrompt(instruction, generated_templates, previous_model, items_description, item_key)
    update_result = openai_client.sync_call_gpt(
        update_prompt.SystemPrompt,
        [construct_user(update_prompt.UserPrompt)],
        "gpt-4o",
        return_json=True
    )
    if print_prompt:
        print(f"=== model_update prompt===\n system: {update_prompt.SystemPrompt}, \n\n user: {update_prompt.UserPrompt}")
    return update_result

def generate_expression(instruction, items, items_description, print_prompt = False):
    try_times = 0
    is_valid = False
    details = {}
    vars = {}
    model = gp.Model()
    for item in items:
        var_name = f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"
        var = model.addVar(name=var_name, lb=0, ub=1, vtype=GRB.BINARY)
        vars[var_name] = var
        model.update()
    while(try_times < 3 and not is_valid):
        try_times += 1
        print(f"==== 第{try_times}次尝试 ====")
        # 步骤1: 抽取相关的preference template
        print("步骤1: 抽取相关的preference template...")
        extraction_result = template_retrieval(instruction, items_description, items, print_prompt)
        exact_match = extraction_result.get('exact_match', False)
        relevant_template_ids = extraction_result.get('template_ids', [])
        if exact_match: 
            # 步骤2: 给template填充参数
            print("步骤2: 给template填充参数...")
            param_fill_result = parameter_filling(instruction, relevant_template_ids, items_description, item_key, items, print_prompt)
            generated_templates = param_fill_result.get('generated_templates', {})
            is_valid, linExpr = test_generated_expressions(generated_templates, items, vars)
        else:
            print("步骤3:没有相关模板，生成新的模板...")
            template_generation_result = template_generation(instruction, items, items_description, print_prompt)
            generated_templates = template_generation_result.get('generated_expressions', {})
            is_valid, linExpr = test_generated_expressions(generated_templates, items, vars)
        details[try_times] = {
            'exact_match': exact_match,
            'relevant_template_ids': relevant_template_ids,
            'generated_expressions': generated_templates,
            'is_valid': is_valid,
            'linExpr': linExpr,
        }
    return is_valid, generated_templates, details, exact_match

def extract_entities(instruction, items, items_description, print_prompt = False):
    prompt = EntityExtractionPrompt(instruction, items, items_description)
    response = openai_client.sync_call_gpt(prompt.SystemPrompt, [construct_user(prompt.UserPrompt)], "gpt-4o", return_json=True)
    entities = response.get('entities', [])
    if print_prompt:
        print(f"=== extract_entities prompt===\n system: {prompt.SystemPrompt} \n\n user: {prompt.UserPrompt}")
    return entities

def search_related_items(items, course_name=None, teacher_name=None, period=None, day=None, time=None, drop_rate=None, drop_rate_type=None):
    related_items = []
    for item in items:
        time_list = item['上课时间'].split(';')
        day_list = []
        period_list = []
        parsed_time_list = []
        #3-2(全周);5-1(全周)
        for parsed_time in time_list:
            parsed_time = parsed_time.split('(')[0]
            parsed_time_list.append(parsed_time)
            parsed_day, parsed_period = parsed_time.split('-')
            day_list.append(int(parsed_day))
            period_list.append(int(parsed_period))
        
        time_match = True
        if time is not None:
            if isinstance(time, list):
                time_match = any(t in parsed_time_list for t in time)
            else:
                time_match = time in parsed_time_list
        
        # 检查课程名匹配
        course_match = True
        if course_name is not None:
            if isinstance(course_name, list):
                course_match = item['课程名'] in course_name
            else:
                course_match = item['课程名'] == course_name
        
        # 检查教师名匹配
        teacher_match = True
        if teacher_name is not None:
            if isinstance(teacher_name, list):
                teacher_match = item['主讲教师'] in teacher_name
            else:
                teacher_match = item['主讲教师'] == teacher_name
        
        # 检查天数匹配
        day_match = True
        if day is not None:
            if isinstance(day, list):
                day_match = any(d in day_list for d in day)
            else:
                day_match = int(day) in day_list
        
        # 检查时间段匹配
        period_match = True
        if period is not None:
            if isinstance(period, list):
                period_match = any(p in period_list for p in period)
            else:
                period_match = int(period) in period_list
        
        # 检查drop_rate匹配
        drop_rate_match = True
        if drop_rate is not None:
            if drop_rate_type == '>=':
                drop_rate_match = float(item['掉课率']) >= float(drop_rate)
            elif drop_rate_type == '>':
                drop_rate_match = float(item['掉课率']) > float(drop_rate)
            elif drop_rate_type == '<=':
                drop_rate_match = float(item['掉课率']) <= float(drop_rate)
            elif drop_rate_type == '<':
                drop_rate_match = float(item['掉课率']) < float(drop_rate)
            elif drop_rate_type == '==':
                drop_rate_match = float(item['掉课率']) == float(drop_rate)
            elif drop_rate_type == '!=':
                drop_rate_match = float(item['掉课率']) != float(drop_rate)
        
        if course_match and teacher_match and day_match and period_match and time_match and drop_rate_match:
            related_items.append(item)
    return related_items

def modify_problem_model(previous_model, instruction, items):
    instruction_analysis_prompt = instructionAnalysisPrompt(previous_model, instruction, items)
    results = openai_client.sync_call_gpt(instruction_analysis_prompt.SystemPrompt, [construct_user(instruction_analysis_prompt.UserPrompt)], "gpt-4o", return_json=True)
    modified_list = results.get('modified_list', [])
    return modified_list

def set_condition(expression, modified_item, updated_problemModel):
    if modified_item['condition_type'] == 'constraint':
        updated_problemModel['updated_constraints'].append({
            "type": modified_item['modify_type'],
            "name": modified_item['constraint_lhs'],
            "lhs": expression,
            "constraint_type": modified_item['constraint_type'],
            "rhs": modified_item['rhs'],
            "description": modified_item.get('description', ''),
            "old_name": modified_item.get('old_name', ''),
        })
    elif modified_item['condition_type'] == 'objective':
        updated_problemModel['updated_objectives'].append({
            "type": modified_item['modify_type'],
            "name": modified_item['objective_expression'],
            "expression": expression,
            "objective_type": modified_item['objective_type'],
            "description": modified_item.get('description', ''),
            "old_name": modified_item.get('old_name', ''),
        })
    return updated_problemModel

def parse_instruction(previous_model, instruction, items):
    from llm.prompts.nlpPrompt import nlpPrompt
    prompt = nlpPrompt(instruction, items_description, items, previous_model)
    results = openai_client.sync_call_gpt(prompt.SystemPrompt, [construct_user(prompt.UserPrompt)], "gpt-4o", return_json=True)
    results = results.get("modifications", [])
    updated_problemModel, modified_items = generate_modifications(results, items)
    return updated_problemModel, modified_items

def generate_modifications(results, items):
    modified_items = []
    updated_problemModel = {"updated_constraints": [], "updated_objectives": []}
    for i, result in enumerate(results):
        action_type = result.get("action_type", "")
        condition_type = result.get("condition_type", "")
        condition_value = result.get("condition_value", {})
        description = result.get("description", "")
        if condition_type == "item_priority":
            print(f"condition_type: {condition_type}, condition_value: {condition_value}")
            for priority_item in condition_value:
                target_priority_items = priority_item["target_items"]
                priority = priority_item["priority"]
                target_items = search_related_items(items, **target_priority_items)
                print(f"target_items: {target_items}")
                print(f"{len(items)}")
                for item in target_items:
                    var_name = f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"
                    item["priority"] = priority
                modified_items.extend(target_items)
        elif condition_type == "objective":
            expression = condition_value.get("expression", {})
            type = condition_value.get("type", "")
            weight = condition_value.get("weight", 1.0)
            old_name = condition_value.get("old_name", "")
            updated_problemModel["updated_objectives"].append({
                "type": action_type,
                "name": generate_name(expression),
                "expression": expression,
                "objective_type": type,
                "weight": weight,
                "description": description,
                "old_name": old_name,
            })
        elif condition_type == "constraint":
            expression = condition_value.get("expression", {})
            type = condition_value.get("type", "")
            value = condition_value.get("value", 1.0)
            old_name = condition_value.get("old_name", "")
            updated_problemModel["updated_constraints"].append({
                "type": action_type,
                "name": generate_name(expression),
                "lhs": expression,
                "constraint_type": type,
                "rhs": value,
                "description": description,
                "old_name": old_name,
            })
        elif condition_type == "objective_weight":
            weight = condition_value.get("weight", 1.0)
            objective_name = condition_value.get("objective_name", "")
            updated_problemModel["updated_objectives"].append({
                "type": action_type,
                "name": objective_name,
                "weight": weight,
                "description": description,
            })
    return updated_problemModel, modified_items

def generate_name(expression):
    expression_type = expression.get("expression_type", "")
    target_items = expression.get("target_items", {})
    course_name = target_items.get("course_name", "")
    instructor = target_items.get("instructor", "")
    day = target_items.get("day", "")
    period = target_items.get("period", "")
    drop_rate = target_items.get("drop_rate", "")
    drop_rate_type = target_items.get("drop_rate_type", "")
    course_name_description = f"in {course_name}" if course_name else ""
    instructor_description = f"taught by {instructor}" if instructor else ""
    day_description = f"on day{day}" if day else ""
    period_description = f"in period{period}" if period else ""
    drop_rate_description = f"with drop rate {drop_rate_type}  {drop_rate}" if drop_rate and drop_rate_type else ""
    print(f"expression_type: {expression_type}, target_items: {target_items}")
    if expression_type == "count_courses":
        if target_items.get("all_items", False) == True:
            return "Number of selected courses"
        else:
            return f"Number of courses {course_name_description} {instructor_description} {day_description} {period_description}"
    elif expression_type == "count_credits":
        if target_items.get("all_items", False) == True:
            return "Total credits"
        else:
            return f"Total credits of courses {course_name_description} {instructor_description} {day_description} {period_description}"
    elif expression_type == "count_days":
        if target_items.get("all_items", False) == True:
            return "Number of days with courses"
        else:
            return f"Number of days with courses {course_name_description} {instructor_description} {day_description} {period_description}"
    elif expression_type == "count_consecutive_courses":
        if target_items.get("all_items", False) == True:
            return "Number of consecutive courses"
        else:
            return f"Number of consecutive courses {course_name_description} {instructor_description} {day_description} {period_description}"
    else:
        return None
    
def parse_user_input(previous_model, instruction, items):
    modified_result = modify_problem_model(previous_model, instruction, items)
    print(f"modified_result: {modified_result}")
    updated_problemModel = {"updated_constraints": [], "updated_objectives": []}
    modified_items = []
    response_message = ""
    for modified_item in modified_result:
        if modified_item['type'] == 'set_required_courses':
            updated_problemModel = set_required_courses(modified_item['course_list'], items, updated_problemModel)
        elif modified_item['type'] == 'set_course_priority':
            related_courses = modified_item['related_courses']
            related_items = []
            for related_course in related_courses:
                searched_items = search_related_items(items, related_course.get('course_name', None), related_course.get('teacher_name', None), related_course.get('period', None), related_course.get('day', None), related_course.get('time', None))
                related_items.extend(searched_items)
            modified_items_result, response_message_result = set_course_priority(related_items, items, modified_item['instruction'])
            modified_items.extend(modified_items_result)
            response_message += response_message_result
            
        elif modified_item['type'] == 'set_condition':
            condition_description = modified_item['constraint_lhs'] if modified_item['condition_type'] == 'constraint' else modified_item['objective_expression']
            is_valid, generated_expressions, details, extract_match = generate_expression(condition_description, items, items_description)
            if is_valid:
                updated_problemModel = set_condition(generated_expressions, modified_item, updated_problemModel)
    
    return updated_problemModel, modified_items, response_message

def fill_name_parameters(name, parameters):
    """
    根据参数填充name中的占位符
    
    Args:
        name (str): 包含占位符的名称字符串
        parameters (dict): 参数字典，键为参数名，值为参数值
    
    Returns:
        str: 填充后的名称字符串
    """
    if not parameters:
        return name
    
    filled_name = name
    for param_name, param_value in parameters.items():
        # 替换占位符 <param_name> 为实际值
        placeholder = f"<{param_name}>"
        # 如果参数值是列表，转换为合适的字符串表示
        if isinstance(param_value, list):
            # 对于列表，使用更简洁的表示方式
            if len(param_value) == 1:
                value_str = str(param_value[0])
            else:
                value_str = f"{param_value[0]}等{len(param_value)}个"
        else:
            value_str = str(param_value)
        filled_name = filled_name.replace(placeholder, str(param_value))
    
    return filled_name

def fill_math_expression_parameters(math_expression, parameters):
    """
    根据参数填充math_expression中的占位符
    
    Args:
        math_expression (str): 包含占位符的数学表达式
        parameters (dict): 参数字典，键为参数名，值为参数值
    
    Returns:
        str: 填充后的数学表达式
    """
    if not parameters:
        return math_expression
    
    filled_expression = math_expression
    for param_name, param_value in parameters.items():
        # 替换占位符 {{{param_name}}} 为实际值（注意是三个大括号）
        placeholder = f"{{{{{param_name}}}}}"
        # 如果参数值是列表，需要特殊格式化
        if isinstance(param_value, list):
            # 对于列表，格式化为 [item1, item2, ...]
            value_str = str(param_value)
        else:
            value_str = str(param_value)
        filled_expression = filled_expression.replace(placeholder, value_str)
    
    return filled_expression

def add_math_expression(problem_model):
    templates = load_templates()
    print(f"problem_model: {problem_model}")
    for objective in problem_model.get('updated_objectives', []):
        for template in templates:
            if 'template_id' in objective['expression'] and template['id'] == int(objective['expression']['template_id']):
                # 获取模板的math_expression
                math_expression = template['math_expression']
                name = template['name']
                # 获取objective的参数 - 从expression中获取
                parameters = objective['expression'].get('parameters', {})
                # 填充参数
                filled_expression = fill_math_expression_parameters(math_expression, parameters)
                objective['math_expression'] = filled_expression
                filled_name = fill_name_parameters(name, parameters)
                objective['name'] = filled_name
                break
    for constraint in problem_model.get('updated_constraints', []):
        for template in templates:
            if 'template_id' in constraint['lhs'] and template['id'] == int(constraint['lhs'].get('template_id', '')):
                # 获取模板的math_expression
                math_expression = template['math_expression']
                # 获取constraint的参数 - 从lhs中获取
                parameters = constraint['lhs'].get('parameters', {})
                # 填充参数
                filled_expression = fill_math_expression_parameters(math_expression, parameters)
                constraint['math_expression'] = filled_expression
                name = template['name']
                filled_name = fill_name_parameters(name, parameters)
                constraint['name'] = filled_name
                break
    return problem_model

def analyse_solution(results):
    # 创建一个字典来存储每个课程的出现次数
    course_counts = {}
    
    # 遍历所有解决方案
    for solution in results.get('solutions', []):
        variables = solution.get('Variables', {})
        
        # 遍历所有变量
        for var_name, value in variables.items():
            # 只处理取值为1的变量（被选中的课程）
            if value == 1.0:
                # 如果课程不存在于统计字典中，初始化计数为1
                if var_name not in course_counts:
                    course_counts[var_name] = 1
                else:
                    # 如果课程已存在，增加计数
                    course_counts[var_name] += 1
    
    return course_counts

def classify_user_input(user_input, items):
    classify_input_type_prompt = classifyInputTypePrompt(user_input, items)
    response = openai_client.sync_call_gpt(classify_input_type_prompt.SystemPrompt, [construct_user(classify_input_type_prompt.UserPrompt)], "gpt-4o", return_json=True)
    input_type = response.get('input_type', '')
    course_list = response.get('course_list', [])
    priority_list = response.get('priority_list', [])
    return input_type, course_list, priority_list
    
def set_required_courses(course_list, items, updated_problem_model):
    required_course_constraints = generate_required_course_constraints(course_list, items)
    for constraint in required_course_constraints:
        updated_problem_model['updated_constraints'].append({
            "type": "add",
            "name": constraint['description'],
            "lhs": constraint['lhs'],
            "constraint_type": "==",
            "rhs": 1,
            "description": constraint['description'],
        })
    return updated_problem_model

def set_course_priority_prompt(target_items, user_input):
    prompt = setCoursePriorityPrompt(target_items, user_input, items_description)
    response = openai_client.sync_call_gpt(prompt.SystemPrompt, [construct_user(prompt.UserPrompt)], "gpt-4o", return_json=True)
    return response.get('updated_items', [])

def set_course_priority(target_items, candidate_items, user_input):
    updated_description = ""
    new_target_items = set_course_priority_prompt(target_items, user_input)
    print(f"new_target_items: {new_target_items}")
    for item in new_target_items:
        for item2 in candidate_items:
            if item['课程名'] == item2['课程名'] and item['主讲教师'] == item2['主讲教师']:
                item2['priority'] = item['priority']
    for item in new_target_items:
        updated_description += f"{item['课程名']} - {item['主讲教师']} 的优先级设置为{item.get('priority', '-1')}\n"
    # updated_description += "\n未修改优先级的课程：\n"
    # for item in target_items:
    #     label = False
    #     for item2 in new_target_items:
    #         if item['课程名'] == item2['课程名'] and item['主讲教师'] == item2['主讲教师']:
    #             label = True
    #             break
    #     if not label:
    #         updated_description += f"{item['课程名']} - {item['主讲教师']} 的优先级为{item.get('priority', '-1')}\n"
    return new_target_items, updated_description

def get_diagnosis_message(results):
    message = ""
    iis = results.get('IIS', [])
    if (len(iis) == 1):
        message = f"请检查一下这条约束的描述是否正确：{iis[0]}。尝试删除这条需求后重新描述。"
    else:
        prompt = diagnosisPrompt(iis)
        message = openai_client.sync_call_gpt(prompt.SystemPrompt, [construct_user(prompt.UserPrompt)], "gpt-4o", return_json=False)
    return message


def main():
    user_input, items, course_list = case1_course()
    pbModel = ProblemModel()
    global_constraints = get_global_constraints(items, course_list)
    pbModel.set_global_constraints(global_constraints)
    
    # 获取当前的问题模型状态
    previous_model = {
        "objectives": pbModel.objectives,
        "constraints": pbModel.constraints
    }
    
    # 使用新的分步骤parse_user_input函数
    updated_problem_model, modified_items, response_message = parse_user_input(previous_model, user_input, items)
    print(f"updated_problem_model: {updated_problem_model}, modified_items: {modified_items}, response_message: {response_message}")
    if updated_problem_model is None and modified_items is None:
        return
    pbModel.update_problem_model(updated_problem_model)
    print("----\npbModel objectives:", pbModel.objectives, "pbModel constraints:", pbModel.constraints)
    optiModel = OptimizationModel()
    optiModel.set_optimization_model(items, pbModel)
    results = optiModel.optimize()
    course_counts = analyse_solution(results)
    results = add_features_to_results(results, items, features_py, pbModel)
    print(results['solutions'][0]['features']) 
    
def test_features():
    user_input, candidate_items, required_courses = case1_course()
    problem_model = {"objectives": [], "constraints": []}
    pbModel, optiModel, results = problem_solving(candidate_items, problem_model, required_courses)
    added_feature_exprs, combined_feature_exprs = generate_features(user_input, candidate_items, results, get_featureExprs(features_py, pbModel))
    results = add_features_to_results(results, candidate_items, combined_feature_exprs, pbModel)
    print(f"results features: {results['solutions'][0]['features']}")
    print(f"added_feature_exprs: {added_feature_exprs}")

def test_generate_modifications():
    results = {
        "modifications": [ 
            { 
            "action_type": "add", 
            "description": "For the course Calculus, prioritize teacher Zhang Jimin first, then Li Wenjun and Lu Ziqun; other preferences remain the same", 
            "condition_type": "item_priority", 
            "condition_value": [ 
                { 
                "target_items": { 
                    "course_name": "微积分A(2)", 
                    "teacher_name": ["章纪民"] 
                }, 
                "priority": 5 
                }, 
                { 
                "target_items": { 
                    "course_name": "微积分A(2)", 
                    "teacher_name": ["李文军", "鲁自群"] 
                }, 
                "priority": 4 
                } 
            ] 
            }, 
            { 
            "action_type": "add", 
            "description": "Maximize the number of courses selected", 
            "condition_type": "objective", 
            "condition_value": { 
                "expression": { 
                "expression_type": "count_courses", 
                "target_items": { 
                    "all_items": True 
                } 
                }, 
                "type": "maximize", 
                "weight": 1 
            } 
            }, 
            { 
            "action_type": "add", 
            "description": "No more than 1 course among University Physics and Calculus in period 3", 
            "condition_type": "constraint", 
            "condition_value": { 
                "expression": { 
                "expression_type": "count_courses", 
                "target_items": { 
                    "course_name": ["大学物理B(1)", "微积分A(2)"], 
                    "period": [3] 
                } 
                }, 
                "type": "<=", 
                "value": 1 
            } 
            }, 
            { 
            "action_type": "add", 
            "description": "The number of days with classes does not exceed 4 days", 
            "condition_type": "constraint", 
            "condition_value": { 
                "expression": { 
                "expression_type": "count_days", 
                "target_items": { 
                    "all_items": True
                } 
                }, 
                "type": "<=", 
                "value": 4 
            } 
            }, 
            { 
            "action_type": "add", 
            "description": "Number of consecutive courses in periods 2 and 3 no more than 2", 
            "condition_type": "constraint", 
            "condition_value": { 
                "expression": { 
                "expression_type": "count_consecutive_courses", 
                "target_items": { 
                    "period": [2, 3]
                } 
                }, 
                "type": "<=", 
                "value": 2 
            } 
            }, 
            { 
            "action_type": "add", 
            "description": "Total selected credits must not exceed 18", 
            "condition_type": "constraint", 
            "condition_value": { 
                "expression": { 
                "expression_type": "count_credits", 
                "target_items": { 
                    "all_items": True 
                } 
                }, 
                "type": "<=", 
                "value": 18 
            } 
            }, 
            { 
            "action_type": "add", 
            "description": "Set the importance of selecting as many finance-related courses as possible to the highest", 
            "condition_type": "modify_weight", 
            "condition_value": { 
                "target_objective_id": 2, 
                "weight": 5 
            } 
            }, 
            { 
            "action_type": "delete", 
            "description": "Delete the constraint for avoiding early 8 AM classes", 
            "condition_id": 1 
            } 
        ] 
        }
    results = results.get("modifications", [])
    items = get_items()
    updated_problemModel, modified_items = generate_modifications(results, items)
    print(f"updated_problemModel: {updated_problemModel}, modified_items: {modified_items}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv('.env')
    # test_features()
    # main()
    test_generate_modifications()


# todo: gurobi修改，支持得到多个解，以及获得求解过程
# 软约束还没处理; 结果的解释（由pilot解释）

# 挑战：1. 如果数据库里的内容很多，如何将数据导入 （还是不考虑，将其作为limitation）
# 后续：常识性约束可以在wizard总结有哪几类缺失后进行补充
