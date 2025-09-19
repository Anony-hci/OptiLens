import inspect
from components.templates import count_target_items, count_credits, count_days, count_consecutive_courses, search_related_items

def lhs_to_expr(lhs, items, variables, templates, model=None):
    if isinstance(lhs, dict) and 'expression_type' in lhs:
        print(f"lhs_to_expr_expression_type: {lhs}")
        return lhs_to_expr_expression_type(lhs, items, variables, model)
    elif isinstance(lhs, str):
        if lhs.strip().startswith('lambda'):
            return lhs_to_expr_lambda(lhs, items, variables)
        else:
            print(f"lhs_to_expr_py: {lhs}")
            return lhs_to_expr_py(lhs, items, variables)
    elif isinstance(lhs, dict) and 'template_id' in lhs:
        print(f"lhs_to_expr_parameterized: {lhs}")
        return lhs_to_expr_parameterized(lhs, items, variables, templates)
    else:
        print(f"lhs_to_expr_py: {lhs}")
        return lhs_to_expr_py(lhs, items, variables)

def lhs_to_expr_expression_type(lhs, items, vars, model):
    expression_type = lhs.get("expression_type", "")
    target_items = lhs.get("target_items", {})
    additional_vars = {}
    
    target_courses = search_related_items(items, **target_items)
    if expression_type == "count_courses":
        expression = count_target_items(target_courses, vars)
    elif expression_type == "count_credits":
        expression = count_credits(target_courses, vars)
    elif expression_type == "count_days":
        day_vars, expression = count_days(target_courses, vars, model)
        additional_vars["day_vars"] = day_vars
        additional_vars["total_days"] = expression
    elif expression_type == "count_consecutive_courses":
        # 处理连续课程的指定项
        specified_items = None
        if "course_name" in target_items:
            specified_items = {"course_name": target_items["course_name"]}
        elif "period" in target_items:
            specified_items = {"period": target_items["period"]}
        
        consecutive_vars, expression = count_consecutive_courses(target_courses, vars, model, specified_items)
        if consecutive_vars:
            additional_vars["consecutive_vars"] = consecutive_vars
            additional_vars["total_consecutive"] = expression
    else:
        print(f"未知的表达式类型: {expression_type}")
    
    # 将 additional_vars 存储到模型中（如果模型支持）
    if hasattr(model, 'additional_vars') and additional_vars:
        model.additional_vars.update(additional_vars)
    
    return expression

def lhs_to_expr_parameterized(lhs_def, items, variables, templates):
    """
    处理参数化的表达式定义
    lhs_def: {'template_id': int, 'parameters': dict}
    """
    template_id = lhs_def.get('template_id')
    parameters = lhs_def.get('parameters', {})
    
    # 确保 template_id 是整数类型
    if isinstance(template_id, str):
        try:
            template_id = int(template_id)
        except ValueError:
            print(f"Warning: Invalid template_id: {template_id}")
            return None
    
    if template_id not in templates:
        print(f"Warning: Template {template_id} not found")
        print(f"Available templates: {list(templates.keys())}")
        return None
        
    template = templates[template_id]
    print(f"template: {template['description']}")
    
    # 添加调试信息
    print(f"Debug - variables keys: {list(variables.keys())[:5]}")  # 显示前5个键
    print(f"Debug - items count: {len(items)}")
    
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
    # 执行代码
    local_scope = {"items": items, "vars": variables}
    try:
        exec(python_code, globals(), local_scope)
        results = local_scope.get('results', None)
        # print(f"results: {results}")
        return results
    except Exception as e:
        print(f"Error executing parameterized expression: {e}")
        print(f"Code: {python_code}")
        return None
    
def lhs_to_expr_py(lhs, items, variables):
    if isinstance(lhs, str):
        # 如果 lhs 是字符串，先尝试将其作为变量名查找
        if lhs in variables:
            return variables[lhs]  # 返回变量对象
    print(f"lhs: {lhs}")
    if 'expression' in lhs:
        lhs = lhs['expression']
    # 如果不是变量名，则尝试评估表达式为 lambda 函数
    print(f"Debug - variables keys: {list(variables.keys())[:5]}")
    print(f"Debug - items: {len(items)}")
    print(f"Debug - lhs: {lhs}")
    try:
        local_scope = {"items": items, "vars": variables}
        exec(lhs, globals(), local_scope)  # 执行代码，修改局部作用域
        return local_scope.get('results', None)  # 获取执行结果（例如 total_courses）
    except Exception as e:
        print(f"Error evaluating expression: {e}")
        return None

def lhs_to_expr_lambda(lhs, items, variables):
    if isinstance(lhs, str):
        # 如果 lhs 是字符串，先尝试将其作为变量名查找
        if lhs in variables:
            return variables[lhs]  # 返回变量对象
        
        # 如果不是变量名，则尝试评估表达式为 lambda 函数
        try:
            lambda_func = eval(lhs)
        except Exception as e:
            print(f"Error evaluating expression: {e}")
            return None
        # 检查 lambda 函数的参数
        params = inspect.signature(lambda_func).parameters
        if len(params) == 2:  # If it expects both 'vars' and 'courses'
            expression = lambda_func(variables, items)
        elif len(params) == 1:  # If it expects only 'vars'
            expression = lambda_func(variables)
        else:
            raise ValueError(f"Unexpected number of parameters in expression: {len(params)}")
    
    return expression

