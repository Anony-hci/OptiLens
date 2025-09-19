import json
from llm.prompts.parser import analyze_items, build_template_name_list
class instructionAnalysisPrompt:
    def __init__(self, previous_model, instruction, items):
        self.previous_model = self._build_previous_model(previous_model)
        self.items = analyze_items(items)
        self.template_name_list = build_template_name_list()
        self.SystemPrompt = f'''
You are an assistant for instruction analysis. Your task is to break down a given user instruction into structured modifications to the problem model, referencing both the previous model state and the available items.

- Procedure -
1. **Instruction Decomposition**
   - Based on `previous_model` and `items`, split the user `instruction` into a list of modification units, called `modified_list`.

2. **Modification Analysis**
   For each `modified_item` in `modified_list`:
   
   **Step 2.1 — Identify type**
   - Determine the `type` of the modification. Valid values are:
     1. `"set_course_priority"`
     2. `"set_condition"`
     如果是尽量选一门，则是set_condition，constraint_type为<=1，constraint_lhs为课程列表
     如果是x门选一门，则是set_condition，constraint_type为==1

   **Step 2.2 — Handle `set_course_priority`**
   - Extract the courses mentioned, with details:
     - `course_name`: str or null
     - `teacher_name`: str or null
     - `weekday`: int 1–7 or null
     - `period`: int 1–6 or null
   - Return as `related_courses` (list of course detail objects).
   - Include the original `instruction` field for context.

   **Step 2.3 — Handle `set_condition`**
   1. Determine `modify_type`: `"add"` or `"delete"`, by comparing with `previous_model`.
      - If `"delete"`, include `condition_type` and `old_name`.
      - If `"add"`, include `condition_type`, (`constraint_lhs`, `constraint_type`, `rhs`) or (`objective_type`, `objective_expression`).
   2. Identify `condition_type`: `"constraint"` or `"objective"`.
   3. If `"constraint"`:
      - Extract:
        - `constraint_lhs`: str
        - `constraint_type`: one of `"=="`, `"!="`, `">="`, `"<="`
        - `rhs`: int
   4. If `"objective"`:
      - Extract:
        - `objective_type`: `"maximize"` or `"minimize"`
        - `objective_expression`: str

其中，`constraint_lhs`和`objective_expression`是参考`template_name_list`中的表达式，需要根据`items`中的信息进行解析。如果是语义的描述，例如与金融有关的课，硬课等，分析items中的课程有哪些与金融有关，提取其课程名组成列表。

- Template Name List -
{self.template_name_list}

'''
        self.UserPrompt = f'''
instruction:
{instruction}

previous_model:
{self.previous_model}

items:
{self.items}

Return the analysis result **in JSON format**.

Example output:
{{
    "modified_list": [
        {{
            "type": "set_required_courses",
            "course_list": ["微积分A(2)"]
        }},
        {{
            "type": "set_course_priority",
            "related_courses": [
                {{
                    "course_name": "微积分A(2)",
                    "teacher_name": "晏平",
                    "weekday": null,
                    "period": null
                }},
                {{
                    "course_name": "微积分A(2)",
                    "teacher_name": "王晓峰",
                    "weekday": null,
                    "period": null
                }}
            ],
            "instruction": "微积分A(2)这门课不同老师之间存在偏好，优先晏平，然后是王晓峰"
        }},
        {{
            "type": "set_condition",
            "modify_type": "add",
            "condition_type": "constraint",
            "constraint_lhs": "早8的课程数量",
            "constraint_type": "==",
            "rhs": 2
        }},
        {{
            "type": "set_condition",
            "modify_type": "add",
            "condition_type": "objective",
            "objective_type": "maximize",
            "objective_expression": "选择的课程数量"
        }},
        {{
            "type": "set_condition",
            "modify_type": "delete",
            "condition_type": "objective",
            "old_name": "早8的课程数量"
        }}
    ]
}}
'''
    def _build_previous_model(self, previous_model):
        problem_model = {"objectives": [], "constraints": []}
        for objective in previous_model["objectives"]:
            problem_model["objectives"].append({
                "name": objective["name"],
                "objective_type": objective["objective_type"],
                "objective_expression": objective["name"]
            })
        for constraint in previous_model["constraints"]:
            problem_model["constraints"].append({
                "name": constraint["name"],
                "constraint_lhs": constraint["name"],
                "constraint_type": constraint["constraint_type"],
                "rhs": constraint["rhs"]
            })
        return json.dumps(problem_model, indent=4)
