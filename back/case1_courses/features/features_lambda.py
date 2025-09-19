
features_lambda = {
    "总课程数量": "lambda vars, items: sum(vars['x_' + item['课程名'] + '_' + item['主讲教师'] + '_' + item['上课时间']] for item in items)",
    "总学分": "lambda vars, items: sum(vars['x_' + item['课程名'] + '_' + item['主讲教师'] + '_' + item['上课时间']] * int(item['学分']) for item in items)",
    "早8课程数量": "lambda vars, items: sum(    vars['x_' + item['课程名'] + '_' + item['主讲教师'] + '_' + item['上课时间']]    for item in items    for time in item['上课时间'].split(';')    if time and '-' in time and any(end_time == '1' for time_part in [time.split('(')[0]]           for start_time, end_time in [time_part.split('-')]))",
    "晚上课程数量": "lambda vars, items: sum(1 for item in items if any(vars['x_' + item['课程名'] + '_' + item['主讲教师'] + '_' + item['上课时间']] and (time == '(全周)' and 0 or (time.find('-') != -1 and int(time.split('-')[1].split('(')[0]) in [6])) for time in item['上课时间'].split(';')))"
}