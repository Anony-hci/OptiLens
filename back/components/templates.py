import gurobipy as gp
from gurobipy import GRB

def search_related_items(items, course_name=None, teacher_name=None, period=None, day=None, time=None, drop_rate=None, drop_rate_type=None, all_items=False):
    related_items = []
    if all_items:
        return items
    for item in items:
        time_list = item['上课时间'].split(';')
        day_list = []
        period_list = []
        parsed_time_list = []
        #3-2(全周);5-1(全周)
        for parsed_time in time_list:
            parsed_time = parsed_time.split('(')[0]
            parsed_time_list.append(parsed_time)
            parsed_day, parsed_period = parsed_time.split('-')
            day_list.append(int(parsed_day))
            period_list.append(int(parsed_period))
        
        time_match = True
        if time is not None:
            if isinstance(time, list):
                time_match = any(t in parsed_time_list for t in time)
            else:
                time_match = time in parsed_time_list
        
        # 检查课程名匹配
        course_match = True
        if course_name is not None:
            if isinstance(course_name, list):
                course_match = item['课程名'] in course_name
            else:
                course_match = item['课程名'] == course_name
        
        # 检查教师名匹配
        teacher_match = True
        if teacher_name is not None:
            if isinstance(teacher_name, list):
                teacher_match = item['主讲教师'] in teacher_name
            else:
                teacher_match = item['主讲教师'] == teacher_name
        
        # 检查天数匹配
        day_match = True
        if day is not None:
            if isinstance(day, list):
                day_match = any(d in day_list for d in day)
            else:
                day_match = int(day) in day_list
        
        # 检查时间段匹配
        period_match = True
        if period is not None:
            if isinstance(period, list):
                period_match = any(p in period_list for p in period)
            else:
                period_match = int(period) in period_list
        
        # 检查drop_rate匹配
        drop_rate_match = True
        if drop_rate is not None:
            if drop_rate_type == '>=':
                drop_rate_match = float(item['掉课率']) >= float(drop_rate)
            elif drop_rate_type == '>':
                drop_rate_match = float(item['掉课率']) > float(drop_rate)
            elif drop_rate_type == '<=':
                drop_rate_match = float(item['掉课率']) <= float(drop_rate)
            elif drop_rate_type == '<':
                drop_rate_match = float(item['掉课率']) < float(drop_rate)
            elif drop_rate_type == '==':
                drop_rate_match = float(item['掉课率']) == float(drop_rate)
            elif drop_rate_type == '!=':
                drop_rate_match = float(item['掉课率']) != float(drop_rate)
        
        if course_match and teacher_match and day_match and period_match and time_match and drop_rate_match:
            related_items.append(item)
    return related_items

def count_credits(items, vars):
    return gp.quicksum(item['学分'] * vars[f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"] for item in items)

def count_target_items(target_items, vars):
    return gp.quicksum(vars[f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"] for item in target_items) 

def count_days(items, vars, model):
    """
    计算上课天数，需要创建额外的天数变量
    """
    # 为每一天创建二进制变量
    day_vars = {}
    
    # 按天分组课程
    day_courses = {}
    for day in range(1, 6):
        day_courses[day] = search_related_items(items, day=day)
    
    # 建立天数变量与课程变量的关联约束
    for day in range(1, 6):
        courses_in_day = day_courses[day]
        
        if courses_in_day:
            day_var = model.model.addVar(name=f"day_{day}", lb=0, ub=1, vtype=GRB.BINARY)
            day_vars[day] = day_var
            # 如果该天有课程被选中，那么该天必须标记为"有课"
            # day_var >= max(course_vars for courses in that day)
            for course_idx, course in enumerate(courses_in_day):
                var_name = f"x_{course['课程名']}_{course['主讲教师']}_{course['上课时间']}"
                if var_name in vars:
                    course_var = vars[var_name]
                    constraint = model.model.addConstr(day_var >= course_var, name=f"day_{day}_course_link_{course_idx}")
            
            # 如果该天没有课程被选中，那么该天标记为"无课"
            # day_var <= sum(course_vars for courses in that day)
            course_vars_list = [vars[f"x_{course['课程名']}_{course['主讲教师']}_{course['上课时间']}"] 
                               for course in courses_in_day]
            model.model.addConstr(day_var <= gp.quicksum(course_vars_list), name=f"day_{day}_no_course")
    
    # 返回天数变量和总天数表达式
    return day_vars, gp.quicksum(day_vars.values())


def count_consecutive_courses(items, vars, model, specified_items = None):
    """
    计算连续上课的课程数量
    Args:
        items: 课程列表
        specified_items: {"course_name": ["微积分A(2)", "大学物理B(1)", "面向对象程序设计基础"]}
        specified_items: {"period": [2, 3]}
    Returns:
        consecutive_vars: 连续时间段的变量字典
        total_consecutive: 总连续上课数量的表达式
    """
    # 创建连续时间段的变量
    consecutive_vars = {}
    
    if specified_items and "course_name" in specified_items:
        # 指定课程名称连续的情况
        course_names = specified_items["course_name"]
        if len(course_names) >= 2:
            # 计算所有可能的两两组合
            for i in range(len(course_names)):
                for j in range(i + 1, len(course_names)):
                    course1_name = course_names[i]
                    course2_name = course_names[j]
                    
                    # 获取这两个课程的所有实例
                    course1_instances = search_related_items(items, course_name=[course1_name])
                    course2_instances = search_related_items(items, course_name=[course2_name])
                    
                    # 分析两个课程的时间段，找出是否有连续的情况
                    consecutive_time_slots = []
                    
                    for course1 in course1_instances:
                        for course2 in course2_instances:
                            # 解析两个课程的时间
                            time1_list = course1['上课时间'].split(';')
                            time2_list = course2['上课时间'].split(';')
                            
                            for time1 in time1_list:
                                for time2 in time2_list:
                                    # 解析时间格式：如 "3-2(全周)" -> day=3, period=2
                                    if '(' in time1 and '(' in time2:
                                        time1_clean = time1.split('(')[0]  # "3-2"
                                        time2_clean = time2.split('(')[0]  # "3-2"
                                        
                                        if '-' in time1_clean and '-' in time2_clean:
                                            day1, period1 = map(int, time1_clean.split('-'))
                                            day2, period2 = map(int, time2_clean.split('-'))
                                            
                                            # 判断是否同一天且时间段相邻
                                            if day1 == day2 and abs(period1 - period2) == 1:
                                                consecutive_time_slots.append({
                                                    'day': day1,
                                    'period1': min(period1, period2),
                                    'period2': max(period1, period2),
                                    'course1': course1,
                                    'course2': course2
                                })
                    
                    # 为每个连续时间段创建变量
                    for slot_idx, slot in enumerate(consecutive_time_slots):
                        key = f"consecutive_courses_{course1_name.replace('(', '_').replace(')', '_')}_{course2_name.replace('(', '_').replace(')', '_')}_{slot['day']}-{slot['period1']}_{slot['day']}-{slot['period2']}_{slot_idx}"
                        consecutive_var = model.model.addVar(name=key, lb=0, ub=1, vtype=GRB.BINARY)
                        consecutive_vars[key] = consecutive_var
                        
                        # 建立关联约束：只有当两个课程都被选中时，连续变量才为1
                        course1_var = vars[f"x_{slot['course1']['课程名']}_{slot['course1']['主讲教师']}_{slot['course1']['上课时间']}"]
                        course2_var = vars[f"x_{slot['course2']['课程名']}_{slot['course2']['主讲教师']}_{slot['course2']['上课时间']}"]
                        
                        # 如果连续变量为1，那么两个课程都必须被选中
                        model.model.addConstr(consecutive_var <= course1_var, name=f"{key}_course1_required_{slot_idx}")
                        model.model.addConstr(consecutive_var <= course2_var, name=f"{key}_course2_required_{slot_idx}")
                        
                        # 如果两个课程都被选中，连续变量可以为1
                        model.model.addConstr(consecutive_var >= course1_var + course2_var - 1, name=f"{key}_both_courses_selected_{slot_idx}")
    
    elif specified_items and "period" in specified_items:
        # 指定连续时间段的情况
        periods = specified_items["period"]
        # 检查是否连续
        if len(periods) >= 2 and all(periods[i+1] - periods[i] == 1 for i in range(len(periods)-1)):
            # 为每一天创建连续时间段变量
            for day in range(1, 6):  # 周一到周五
                # 创建这个连续时间段的变量
                key = f"consecutive_{day}-{periods[0]}_{day}-{periods[-1]}"
                consecutive_var = model.model.addVar(name=key, lb=0, ub=1, vtype=GRB.BINARY)
                consecutive_vars[key] = consecutive_var
                
                # 获取这个时间段的所有课程
                period_courses = []
                for period in periods:
                    period_courses.extend(search_related_items(items, time=f"{day}-{period}"))
                
                # 建立关联约束
                if period_courses:
                    # 只有当连续时间段内都有课程被选中时，连续变量才为1
                    # 使用辅助变量来表示每个时间段是否有课
                    period1_has_course = model.model.addVar(name=f"{key}_period1_has_course", lb=0, ub=1, vtype=GRB.BINARY)
                    period2_has_course = model.model.addVar(name=f"{key}_period2_has_course", lb=0, ub=1, vtype=GRB.BINARY)
                    
                    # 获取两个时间段的课程
                    period1_courses = search_related_items(items, time=f"{day}-{periods[0]}")
                    period2_courses = search_related_items(items, time=f"{day}-{periods[1]}")
                    
                    # 如果第一个时间段有课被选中，period1_has_course为1
                    if period1_courses:
                        period1_vars = [vars[f"x_{course['课程名']}_{course['主讲教师']}_{course['上课时间']}"] 
                                      for course in period1_courses]
                        model.model.addConstr(period1_has_course <= gp.quicksum(period1_vars), name=f"{key}_period1_has_course_upper")
                        model.model.addConstr(gp.quicksum(period1_vars) <= len(period1_vars) * period1_has_course, name=f"{key}_period1_has_course_lower")
                    
                    # 如果第二个时间段有课被选中，period2_has_course为1
                    if period2_courses:
                        period2_vars = [vars[f"x_{course['课程名']}_{course['主讲教师']}_{course['上课时间']}"] 
                                      for course in period2_courses]
                        model.model.addConstr(period2_has_course <= gp.quicksum(period2_vars), name=f"{key}_period2_has_course_upper")
                        model.model.addConstr(gp.quicksum(period2_vars) <= len(period2_vars) * period2_has_course, name=f"{key}_period2_has_course_lower")
                    
                    # 只有当两个时间段都有课时，连续变量才为1
                    model.model.addConstr(consecutive_var <= period1_has_course, name=f"{key}_period1_required")
                    model.model.addConstr(consecutive_var <= period2_has_course, name=f"{key}_period2_required")
                    
                    # 如果两个时间段都有课，连续变量可以为1
                    model.model.addConstr(consecutive_var >= period1_has_course + period2_has_course - 1, name=f"{key}_both_periods_selected")
        else:
            print(f"指定的时间段 {periods} 不是连续的")
            return {}, None
    else:
        # 默认情况：计算所有连续时间段
        for day in range(1, 6):
            for start_period in range(1, 6):
                end_period = start_period + 1
                
                # 获取这个连续时间段的所有课程
                period1_courses = search_related_items(items, time=f"{day}-{start_period}")
                period2_courses = search_related_items(items, time=f"{day}-{end_period}")
                
                # 建立关联约束
                if period1_courses and period2_courses:
                    key = f"consecutive_{day}-{start_period}_{day}-{end_period}"
                    consecutive_var = model.model.addVar(name=key, lb=0, ub=1, vtype=GRB.BINARY)
                    consecutive_vars[key] = consecutive_var
                    # 只有当两个时间段都有课程时，才可能产生连续上课
                    # 获取两个时间段的课程变量
                    period1_vars = [vars[f"x_{course['课程名']}_{course['主讲教师']}_{course['上课时间']}"] 
                                for course in period1_courses]
                    period2_vars = [vars[f"x_{course['课程名']}_{course['主讲教师']}_{course['上课时间']}"] 
                                for course in period2_courses]
                    
                    # 只有当两个时间段都有课被选中时，连续变量才为1
                    # 使用辅助变量来表示两个时间段是否都有课
                    period1_has_course = model.model.addVar(name=f"{key}_period1_has_course", lb=0, ub=1, vtype=GRB.BINARY)
                    period2_has_course = model.model.addVar(name=f"{key}_period2_has_course", lb=0, ub=1, vtype=GRB.BINARY)
                    
                    # 如果第一个时间段有课被选中，period1_has_course为1
                    model.model.addConstr(period1_has_course <= gp.quicksum(period1_vars), name=f"{key}_period1_has_course_upper")
                    model.model.addConstr(gp.quicksum(period1_vars) <= len(period1_vars) * period1_has_course, name=f"{key}_period1_has_course_lower")
                    
                    # 如果第二个时间段有课被选中，period2_has_course为1
                    model.model.addConstr(period2_has_course <= gp.quicksum(period2_vars), name=f"{key}_period2_has_course_upper")
                    model.model.addConstr(gp.quicksum(period2_vars) <= len(period2_vars) * period2_has_course, name=f"{key}_period2_has_course_lower")
                    
                    # 只有当两个时间段都有课时，连续变量才为1
                    model.model.addConstr(consecutive_var <= period1_has_course, name=f"{key}_period1_required")
                    model.model.addConstr(consecutive_var <= period2_has_course, name=f"{key}_period2_required")
                    
                    # 如果两个时间段都有课，连续变量可以为1
                    model.model.addConstr(consecutive_var >= period1_has_course + period2_has_course - 1, name=f"{key}_both_periods_selected")
    
    # 返回连续变量和总连续数量表达式
    if consecutive_vars:
        total_consecutive = gp.quicksum(consecutive_vars.values())
        return consecutive_vars, total_consecutive
    else:
        return {}, None