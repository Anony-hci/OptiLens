from llm.prompts.parser import analyze_items, build_template_name_list
class EntityExtractionPrompt():
    def __init__(self, instruction, items, items_description):
        self.instruction = instruction
        self.items = items
        self.items_analysis = analyze_items(items)
        self.items_description = items_description
        self.template_name_list = build_template_name_list()
        self.SystemPrompt = f"""
Your task is to 对 user instruction 进行解析，将其用领域相关的属性表达。

— Course Data Attributes —
{self.items_description}

— Course Data Description and Examples — 
{self.items_analysis}

- Reference Entities —
{self.template_name_list}
        
— Examples —
1.
Instruction: 总学分不超过26
Reasoning: Strip condition “不超过” and parameter “26”.
Output: {{“entities”: [“总学分”]}}

2.
Instruction: 周三下午的课不超过2节
Reasoning: Remove condition “不超过” and parameter “2节”, map “下午” to periods [3,4,5] on Wednesday.
Output: {{“entities”: [“星期三并且上课节次为[3,4,5]的课程数量”]}}

3.
Instruction: 大物要张留碗老师
Reasoning: Focus on stating the entity using course name and instructor.
Output: {{“entities”: [“课程名是’大学物理A’且主讲教师是’张留碗’的课程数量”]}}

4.
Instruction: 周四不要有课, 多选课
Reasoning: Remove condition “不要” and “多”, identifying entities “周四的课程数量” and “总课程数量”.
Output: {{“entities”: [“星期四的课程数量”, “总课程数量”]}}

5. 
Instruction: 早上第一节课尽可能少
Reasoning: Remove condition “尽可能少”, map “早上” to periods [1,2], and combine with “第一节课” to get period [1].
Output: {{“entities”: [“上课节次为[1]的课程数量”]}}

6. Instruction: 概率论与数理统计 、概率论与数理统计(社科类) 这两门中选一门
Output: {{"entities": ["课程名中包含[概率论与数理统计, 概率论与数理统计(社科类)]中的任意一个关键词的课程数量"]}}

7. Instruction: 微积分这门课要选1-2这个时间
Output: {{"entities": ["课程名是’微积分B(2)’, 时间在星期一的第2节课 的课程数量"]}}

— Output Requirements —
Provide extracted entities in JSON format: {{“entities”: [“”, “”]}}
"""
        self.UserPrompt = f"""
— User Instruction —
{self.instruction}

"""