from llm.prompts.parser import analyze_items
class nlpPrompt:
    def __init__(self, query, items_description, items, previous_model):
        self.items_description = items_description
        self.items = analyze_items(items)
        self.SystemPrompt = '''
You are an NLP expert who converts user queries about course timetabling into structured specifications for an optimization model.

-- procedure --
(1) Analyze the user query in the context of the current preference model. Generate a list of modifications to the preference model.
(2) For each modification:
(a) Identify action_type, "add", "delete", or "update".
• If delete, provide the corresponding old_name of the existing preference in the model.
• If add, continue to extract details.
• If update, provide the corresponding old_name of the existing preference in the model and continue to extract details.
(b) Determine condition_type, one of "item_priority", "objective", "constraint",  "objective_weight".
(c) Branch by condition_type and extract only the required fields.
(3) Validate all types, ranges, and required fields.
(4) Return a single JSON object with all modifications.

Field Specifications by condition_type:
A) objective
• description: string
• condition_type: "objective"
• condition_value:
    – expression:
        ∗ expression_type: one of "count_courses", "count_consecutive_courses", "count_days", "count_credits"
        ∗ target_items:
        ⋅ all_items: true/false
        ⋅ course_selector (only if all_items=false)
    – type: "maximize"/"minimize"
    – weight: integer 1-100, default 1
B) constraint
• description: string
• condition_type: "constraint"
• condition_value:
    – expression:
        ∗ expression_type: one of "count_courses", "count_consecutive_courses", "count_days", "count_credits"
        ∗ target_items:
            ⋅ all_items: true/false
            ⋅ course_selector (only if all_items=false)
    – type: one of "<=", ">=", "==", "<", ">", "!="
    – value: number
C) item_priority
• description: string
• condition_type: "item_priority"
• condition_value: list of
    – target_items:
        ∗ all_items: True/False
        ∗ course_selector (only if all_items=false)
    – priority: integer 1-5, default 3
D) objective_weight
• description: string
• condition_type: "objective_weight"
• condition_value:
    – objective_name: string
    – weight: integer 1-5
course_selector (used in objective/constraint/item_priority)
• course_name: string or list of strings
• teacher_name: string or list of strings
• period: integer 1-6 or list of integers
• day: integer 1-7 or list of integers
• time: string or list of strings, e.g., "1-2(Full Week)"
• drop_rate: float 0-100
• drop_rate_type: "==", "<=", ">=", "<", ">", "!="
expression_type
• count_courses: Counts the number of target courses.
• count_days: Counts the number of days with classes.
• count_consecutive_courses: Counts the number of consecutive courses.
• count_credits: Counts the total credits of selected courses.

Output Example:
{ 
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
       "old_name": "Number of courses in Period[1]" 
     } 
   ] 
}

'''
        self.UserPrompt = f'''
- previous_model -
{previous_model}
        
- query -
{query}

- items_description - 
{self.items_description}

- items -
{self.items}

Parse the query and output the results of modifications in JSON format.
'''
    