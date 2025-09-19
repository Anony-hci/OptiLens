import json
import os
from llm.prompts.parser import load_templates
class TemplateGenerationPrompt:
    def __init__(self, instruction, items, items_description, generated_templates=None, linExpr=None):
        self.expression_constructors = load_templates()
        self.instruction = instruction
        self.items = items
        self.items_description = items_description
        self.items_analysis = self._analyze_items()
        self.templates_list = self._build_templates_list()
        self.generation_history = self._build_generation_history(generated_templates, linExpr)
        
        self.SystemPrompt = f"""
You are an assistant for expression generation. Given a user instruction, your task is to generate a symbolic Python expression that describes this instruction's logic using the provided items and decision variables.
Note: The python expression is used to generate gurobi expressions, so you cannot directly perform calculations on the input decision variables `vars` (such as using 'sum', 'max', 'min', 'len', etc. directly on `vars`). You should only construct symbolic expressions, such as '*, +'.
"""

        self.UserPrompt = f"""
- User Instruction -
{self.instruction}

- Item Data Description -
{self.items_description}
{self.items_analysis}

- Template Lists -
{self.templates_list}

- Output Format -
Output the generated expression in JSON format:
{{
    "generated_expressions": 
        {{
        "name": "Name of the entity in the instruction",
        "expression": "Python function definition and call",
        "description": "Explanation of the logic behind the expression",
        "math_expression": "LaTeX-style mathematical expression, use {{}} to wrap parameters"
        }}
}}

Example of expression content (python code), include both the function definition and the function call.

"def expression_name(items, vars):
    # compute symbolic expression
    return results
results = expression_name(items, vars)"

The function must accept two arguments:
1. items: a list of courses, as described in the item data description
2. vars: a dictionary where the keys are decision variable names in the form "x_{{item['课程名']}}_{{item['主讲教师']}}_{{item['上课时间']}}", and the values are binary Gurobi variables.

### Note:
1. Since vars contains symbolic decision variables, the expression should represent symbolic logic, not numerical results.
2. The logic in the expression must align with the item structure and variable format.
"""

    def _build_templates_list(self):
        """构建格式化的模板列表字符串"""
        templates_str = []
        for template in self.expression_constructors:
            templates_str.append(f"ID {template['id']}: {template['name']} - {template['description']}. Parameters: {template['parameters_description']}. Python code: `python`{template['python_template']}")
        return f"一共有{len(templates_str)}个模板，分别是：\n" + "\n".join(templates_str) 
    
    def _analyze_items(self):
        """分析实际的items数据，提取关键信息"""
        if not self.items:
            return "无课程数据"
        
        # 提取所有唯一的教师
        teachers = set()
        course_names = set()
        departments = set()
        credits = set()
        time_slots = set()
        cleaned_items = []
        for item in self.items:
            cleaned_item = dict(item)  # 浅拷贝
            for key in ['batch', 'chosen_when_confirmed', 'num', 'priority', 'priority_type']:
                if key in cleaned_item:
                    del cleaned_item[key]
            cleaned_items.append(cleaned_item)
        self.items = cleaned_items
        # 将items内容倒序
        self.items = self.items[::-1]
        for item in self.items:
            if '主讲教师' in item:
                teachers.add(item['主讲教师'])
            if '课程名' in item:
                course_names.add(item['课程名'])
            if '开课院系' in item:
                departments.add(item['开课院系'])
            if '学分' in item:
                credits.add(item['学分'])
            if '上课时间' in item:
                # 解析多个时间段
                times = item['上课时间'].split(';')
                for time in times:
                    time_slots.add(time.strip())
        
        analysis = []
        analysis.append(f"共有 {len(self.items)} 门课程")
        analysis.append(f"主讲教师（共{len(teachers)}位）: {', '.join(teachers)}")
        analysis.append(f"课程名称（共{len(course_names)}门）: {', '.join(course_names)}")
        analysis.append(f"开课院系（共{len(departments)}个）: {', '.join(departments)}")
        analysis.append(f"上课时间（共{len(time_slots)}个时段）: {', '.join(time_slots)}")
        
        # 添加几个具体的课程示例
        analysis.append("\n示例课程:")
        for i, item in enumerate(self.items[:5]):
            analysis.append(f"  {i+1}. {item}")
        
        return "\n".join(analysis)
    
    def _build_generation_history(self, generated_templates, linExpr):
        if generated_templates is None:
            return ""
        message = f"--- 生成历史 ---\n之前生成的表达式无法正确计算，其LinExpr为：\n{linExpr}, 其表达式为：\n"
        history = []
        for i, template in enumerate(generated_templates):
            history.append(f"===expression {i+1}===\n{template['expression']}\n")
        message += "\n".join(history) + "\n请根据item的数据格式和之前的template中对于item和vars的使用，生成新的表达式。"
        return message