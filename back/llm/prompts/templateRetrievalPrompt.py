import json
import os
from llm.prompts.parser import build_templates_list, analyze_items
class TemplateRetrievalPrompt:
    def __init__(self, instruction, items_description, items):
        self.items_description = items_description
        self.items = analyze_items(items)
        self.templates_list = build_templates_list()
        self.instruction = f"- instruction -\n{instruction}" if instruction else ""
        self.SystemPrompt = f"""
Given user instruction, identify related template from a predefined list.

— Template List —
{self.templates_list}

— Analysis Steps —
1. Determine whether there exists a template that can exactly represent the given entities. If so, set exact_match to True; otherwise, set it to False. 其中，如果存在部分对于课程的模糊语义描述，例如“硬课”，则可以从课程中提取出符合语义的课程名列表，set exact_match to True, 使用template: "课程名为<course_name_list>中的任意一个的课程数量", 并从items中提取出符合语义的课程名列表，作为course_name_list。
2. If exact_match is True, return the corresponding template_id. If False, return a list of related template IDs from template_list to assist in future template generation.


— Output Requirements —
Output the result in JSON format:
{{
    "exact_match": True | False, # bool, whether the instruction can be represented exactly
    "template_ids": [3] |[1, 3, 5], # list of int, list of relevant template IDs
    "explanation": “Brief explanation of why these concepts were chosen”
}}
"""

        self.UserPrompt = f"""
{self.instruction}

- items_description -
{self.items_description}

- items -
{self.items}
"""

    
    
