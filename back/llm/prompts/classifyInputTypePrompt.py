from .parser import analyze_items_names
class classifyInputTypePrompt:
    def __init__(self, user_input, items):
        self.items_description = analyze_items_names(items)
        self.SystemPrompt = '''
你是一个自然语言处理专家，擅长分析用户输入的意图，并根据用户输入的意图返回相应的类型。
用户输入的意图包括三类：
1. 设置必修课：例如
input: “微积分、大学物理B(1)、面向对象程序设计基础是必修课”
output: {"input_type": "set_required_courses", "course_list": ["微积分B(2)", "大学物理B(1)", "面向对象程序设计基础"]} 
2. 设置课程优先级：例如
input: “对于微积分课，我最想上马连荣，其次是杨晶，其他的都无所谓。”
output: {"input_type": "set_course_priority", "course_list": ["微积分B(2)"], "priority_list": ["马连荣", "杨晶"]} 
3. 其他关于课程表的偏好：例如
input: “以下两门中任选一门：计算机程序设计基础、计算机程序设计基础(2) ”,“早上第一节课尽量不要有课”
output: {"input_type" : "other_constraints"}
input: "微积分课程要杨一龙老师"
output: {"input_type" : "other_constraints"}

注意，我们这个分类主要就是筛选出必修课和设置课程优先级两种类型。其他的课程约束，直接输出input_type, 后续会进行另外的处理。
'''
        self.UserPrompt = f'''
用户输入：{user_input}
课程数据说明：
{self.items_description}

对用户输入进行分析，返回相应的类型。

以json格式返回结果, 要求course_list和priority_list中包含的课程名和老师名称，在课程数据说明中存在。
'''
    