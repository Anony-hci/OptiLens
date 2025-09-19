class setCoursePriorityPrompt:
    def __init__(self, target_items, user_input, items_description):
        self.target_items = target_items_description(target_items)
        self.SystemPrompt = '''
给定用户对于课程的偏好，对课程的优先级进行重新设置。其中，优先级设置为1-5，5为最高优先级，1为最低优先级。对于现有的其他课程的优先级和用户描述的排序不一致的话，也要对应修改。

示例1：
input: “对于微积分课，我最想上马连荣，其次是杨晶，其他的都无所谓。”
courses_description: 
课程名, 主讲教师, priority
微积分B(2), 马连荣, 3
微积分B(2), 杨晶, 3
微积分B(2), 李明, 3
...所有的微积分B(2)课程的优先级都是3
output: 只输出修改的课程，不输出未修改的课程。
{"updated_items": [{"课程名": "微积分B(2)", "主讲教师": "马连荣", "priority": 5}, {"课程名": "微积分B(2)", "主讲教师": "杨晶", "priority": 4}]}

示例2：
input: “英语阅读，马连荣>杨晶、李明>其他”
courses_description: 
课程名, 主讲教师, priority
英语阅读, 马连荣, 4
英语阅读, 杨晶, 3
英语阅读, 李明, 4
英语阅读, 王五, 5
...其他都是3
output: 
{"updated_items": [{"课程名": "英语阅读", "主讲教师": "马连荣", "priority": 5}, {"课程名": "英语阅读", "主讲教师": "杨晶", "priority": 4},{"课程名": "英语阅读", "主讲教师": "王五", "priority": 3}]}

'''
        self.UserPrompt = f'''
用户输入：{user_input}

对应的items为
{self.target_items}

items_description:
{items_description}

根据用户输入，对courses_description中的课程的优先级进行重新设置。

以json格式返回结果，key为updated_items，value为修改的课程列表。要求课程名和主讲教师在courses_description中存在。
'''

def target_items_description(target_items):
    # 对于target_items, 提取课程名和老师名称和优先级，然后组合成字符串
    description = "课程名, 主讲教师, priority\n"
    for item in target_items:
        description += f"{item['课程名']}, {item['主讲教师']}, {item.get('priority', 3)}\n"
    return description