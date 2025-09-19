import json
import os
from llm.prompts.parser import load_templates, analyze_items
class ParameterFillingPrompt:
    def __init__(self, instruction, relevant_template_ids, items_description, item_key, items):
        self.templates_list = load_templates()
        self.instruction = instruction
        self.relevant_template_ids = relevant_template_ids
        self.items_description = items_description
        self.item_key = item_key
        self.items = items
        
        # 构建相关概念的详细信息
        self.relevant_templates = self._get_relevant_templates()
        
        # 从实际items中解析信息
        self.items_analysis = analyze_items(items)
        
        self.SystemPrompt = f"""
Given user instruction, fill in the parameters of template for the instruction.
"""

        self.UserPrompt = f"""
- User instruction -
{self.instruction}

- Template -
{self.relevant_templates}

- Items Data Description -
{self.items_analysis}

- Output Format -
Generate filled templates in JSON format:
{{
    "generated_templates": 
        {{
            "name": "generated based on the template name",
            "description": "generated based on the template description",
            "template_id": ID,
            "parameters": {{"param_name": "param_value"}},
        }}
}}

--- 要求 ---
1. 严格按照模板中的参数描述来生成参数，例如需要从items中提取课程名称，则参数名称为keyword，参数值为items中包含的课程名称。
2. 参数类型：
   - 字符串参数：直接传入字符串值，如 "张三"、"可视化"
   - 整数参数：传入数字，如 3、1
   - 无参数模板：parameters为空字典 {{}}

其中，如果存在部分对于课程的模糊语义描述，例如“硬课”，则可以从课程中提取出符合语义的课程名列表，使用template: "课程名为<course_name_list>中的任意一个的课程数量", 并从items中提取出符合语义的课程名列表，作为course_name_list。

"""


    def _get_relevant_templates(self):
        """获取相关概念的详细信息"""
        relevant = []
        for template in self.templates_list:
            if template['id'] in self.relevant_template_ids:
                filtered_template = {
                    "id": template.get("id"),
                    "description": template.get("description"),
                    "parameters": template.get("parameters"),
                    "parameters_description": template.get("parameters_description")
                }
                relevant.append(filtered_template)
        return json.dumps(relevant, ensure_ascii=False)