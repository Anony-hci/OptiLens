class ModelUpdatePrompt:
    def __init__(self, instruction, generated_templates, previous_model, items_description, item_key):
        self.instruction = instruction
        self.generated_templates = generated_templates
        self.previous_model = previous_model
        self.items_description = items_description
        self.item_key = item_key
        self.templates = self._build_templates()
        self.SystemPrompt = f"""
You are a modeling assistant for 0-1 integer programming problems. Given a user instruction and the relevant templates or expressions, your task is to modify the current optimization model accordingly. 

If the current model is empty, you should add appropriate objectives or constraints based on the instruction.

--- Modification Guidelines ---

1. Objective Modifications:
   - If the instruction contains words like "maximize", "prefer more", "increase" → add a 'maximize' objective.
   - If the instruction contains words like "minimize", "prefer fewer", "decrease" → add a 'minimize' objective.

2. Constraint Modifications:
   - If the instruction includes explicit numeric limits → add a constraint.
   - If the instruction uses phrases like "no more than", "at most" → use a "<=" constraint.
   - If the instruction uses phrases like "at least", "not fewer than" → use a ">=" constraint.
   - If the instruction uses phrases like "must be", "equal to" → use a "==" constraint.

3. Modification Types:
   - `add`: add a new objective or constraint
   - `update`: update an existing objective or constraint
   - `delete`: remove an existing objective or constraint

Please strictly follow the format and guidelines.
"""

        self.UserPrompt = f"""
- Current Model -
{self.previous_model}

- User Instruction -
{self.instruction}

- Relevant Templates or Expressions -
{self.templates}

Based on the user instruction and the related templates or expressions, please modify the current optimization model accordingly.

- Output Format -
Output the modified model in JSON format.
{{
    "updated_objectives": [
        {{
            "type": "add|update|delete",
            "name": "follow the name format in the template",
            "expression": "python code | template_id + parameters",
            "objective_type": "maximize|minimize",
            "description": "follow the description format in the template",
            "old_name: "original objective name (required only for update/delete)"
        }}
    ],
    "updated_constraints": [
        {{
            "type": "add|update|delete",
            "name": "follow the name format in the template",
            "lhs": "python code | template_id + parameters",
            "constraint_type": "<=|>=|==",
            "rhs": "numeric value",
            "description": "follow the description format in the template",
            "old_name": "original constraint name (required only for update/delete)"
        }}
    ]
}}

The expression and lhs can be either a String of Python expression or a json object of `template_id + parameters`. The type is determined by the the Relevant Templates or Expressions provided in above.

1. python code:
"expression": "def expression_name(items, vars):
    # compute symbolic expression
    return results
results = expression_name(items, vars)"

2. template_id + parameters:
"expression": {{
    "template_id": int, "template ID",
    "parameters": {{"param_name": "param_value"}},
}}
"""

    def _build_templates(self):
        """构建生成概念的详细信息"""
        if not self.generated_templates:
            return "无生成的概念"
        print(f"generated_templates: {self.generated_templates}")
        details = []
        for i, template in enumerate(self.generated_templates):
            if 'template_id' in template:
                detail = f"""
    ------
    name: {template['name']}
    description: {template['description']}
    template id: {template['template_id']}
    parameters: {template['parameters']}
"""
                details.append(detail)
            else:
                print(f"template: {template}")
                detail = f"""
    ------
    name: {template['name']}
    description: {template['description']} 
    expression python code: "{template['expression']}"
"""
                details.append(detail)
        return "\n".join(details) 