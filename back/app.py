import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from flask_cors import CORS
from components.scheduler import get_global_constraints, parse_user_input, generate_features, problem_solving, analyse_solution, get_featureExprs, add_math_expression, parse_instruction
from components.similarityCal import calculate_similarity_with_base_solution, sort_results
from components.ProblemModel import ProblemModel
from components.OptimizationModel import OptimizationModel
from case1_courses.course import add_features_to_results, update_features, get_current_features, get_default_problem_model, generate_required_course_constraints
from components.scheduler import set_required_courses, set_course_priority, classify_user_input, get_diagnosis_message
# from case1_courses.maximal_cliques import generate_clique_constraints
from case1_courses.features.features_py import features_py
from Session import Session
import uuid
from dotenv import load_dotenv
# from recover import get_recover_data
import json
import threading
import queue
import time
app = Flask(__name__)
# 允许所有来源的跨域请求
CORS(app, resources={r"/*": {"origins": "*"}})
import os
import copy

global feature_query

# 存储当前正在对话的用户信息
sessions = {}

# 创建一个队列用于异步保存任务
save_queue = queue.Queue()

# 配置日志记录
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 设置日志级别为 INFO

# 创建日志格式
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 创建终端（控制台）处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 创建轮转文件处理器
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# 将处理器添加到 logger
# logger.addHandler(console_handler)
logger.addHandler(file_handler)

def save_worker():
    """后台工作线程，处理保存任务"""
    while True:
        try:
            # 从队列中获取保存任务
            task = save_queue.get()
            if task is None:  # None 表示停止工作线程
                break
            
            user_id, data = task
            user_dir = f"../user-study/IterLens/{user_id}"
            data_dir = f"{user_dir}/data"
            
            # 确保data目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 生成时间戳文件名
            timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
            data_file_path = f"{data_dir}/data_{timestamp}.json"
            
            # 添加保存时间戳到数据中
            data['save_timestamp'] = timestamp
            data['save_datetime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            
            # 保存数据
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"用户数据已异步保存到 {data_file_path}")
            
        except Exception as e:
            logger.error(f"异步保存用户数据时出错: {str(e)}")
        finally:
            save_queue.task_done()

# 启动后台保存工作线程
save_thread = threading.Thread(target=save_worker)
save_thread.daemon = True
save_thread.start()

def save_user_action_log(user_id, action_type, action_data):
    """保存用户操作日志"""
    try:
        # 添加时间戳
        data = {
            'timestamp': time.time(),
            'datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'action_type': action_type,
            'action_data': action_data
        }
        
        # 将操作添加到session的action_logs中
        if user_id in sessions:
            sessions[user_id].action_logs.append(data)
            logger.info(f"[ACTION_LOG] 操作已添加到session，当前总操作数: {len(sessions[user_id].action_logs)}")
        else:
            logger.warning(f"[ACTION_LOG] Session {user_id} 不存在，无法保存操作日志")
            return
        
        # 保存完整的操作历史到时间戳文件
        user_dir = f"../user-study/IterLens/{user_id}"
        logs_dir = f"{user_dir}/logs"
        
        # 确保logs目录存在
        os.makedirs(logs_dir, exist_ok=True)
        
        # 生成时间戳文件名
        timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        log_file_path = f"{logs_dir}/log_{timestamp}.json"
        
        # 保存完整的操作历史到新文件
        with open(log_file_path, 'w', encoding='utf-8') as f:
            json.dump(sessions[user_id].action_logs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[ACTION_LOG] 完整操作历史已保存到 {log_file_path}，共 {len(sessions[user_id].action_logs)} 个操作")
        
    except Exception as e:
        logger.error(f"[ACTION_LOG] 保存用户操作日志时出错: {str(e)}")

def get_latest_data_file(user_id):
    """获取用户最新的数据文件路径"""
    try:
        user_dir = f"../user-study/IterLens/{user_id}"
        data_dir = f"{user_dir}/data"
        
        # 检查旧的data.json文件（兼容性）
        old_data_file = f"{user_dir}/data.json"
        if os.path.exists(old_data_file) and not os.path.exists(data_dir):
            logger.info(f"找到旧格式数据文件: {old_data_file}")
            return old_data_file
            
        # 检查新的data目录
        if not os.path.exists(data_dir):
            return None
            
        # 获取所有data文件
        data_files = [f for f in os.listdir(data_dir) if f.startswith('data_') and f.endswith('.json')]
        
        if not data_files:
            return None
            
        # 按文件名排序（时间戳格式确保了字典序就是时间序）
        data_files.sort(reverse=True)
        latest_file = os.path.join(data_dir, data_files[0])
        
        logger.info(f"找到最新数据文件: {latest_file}")
        return latest_file
        
    except Exception as e:
        logger.error(f"获取最新数据文件时出错: {str(e)}")
        return None

def save_user_data_async(user_id):
    """异步保存用户数据到JSON文件"""
    if user_id in sessions:
        # 准备要保存的数据
        user_data = {
            'current_preference': sessions[user_id].current_preference,
            'messages': sessions[user_id].messages,
            'problem_model': sessions[user_id].problem_model,
            'model_nodes': sessions[user_id].model_nodes,
            'features_exprs': sessions[user_id].features_exprs,
            'action_logs': sessions[user_id].action_logs
        }
        
        # 将保存任务放入队列
        try:
            save_queue.put((user_id, user_data), block=False)
        except queue.Full:
            logger.warning(f"保存队列已满，跳过用户 {user_id} 的数据保存")

@app.route('/set_base_solution', methods=['POST'])
def set_base_solution():
    data = request.get_json()
    id = data.get('sessionId', 123)
    base_solution = data.get('currentSolution', {})
    results = data.get('currentSolutionResult', {})
    # sessions[id].base_solution = base_solution
    logger.info(f"base_solution: {base_solution}")
    results = calculate_similarity_with_base_solution(base_solution, results)
    solutions = {
        "message": f"已经根据您选中的方案筛选了相近的方案。",
        "solutionResults": results
    }
    return jsonify(solutions)

@app.route('/saved_features', methods=['POST'])
def saved_features():
    global feature_query
    data = request.get_json()
    id, user_input, candidate_items, problem_model = parse_data(data)
    added_feature_exprs = data.get('addedFeatureExprs', {})
    logger.info(f"addedFeatureExprs: {added_feature_exprs}")
    is_true = data.get('isTrue', None)
    if(is_true):
        for key, value in added_feature_exprs.items():
            features_py[key] = value
        sessions[id].features_exprs = features_py
        return jsonify({"sessionId": id}), 200
    elif(not is_true):
        pbModel, optiModel, results = problem_solving(candidate_items, problem_model)
        added_feature_exprs, combined_feature_exprs = generate_features(feature_query, candidate_items, results, features_py)
        results = add_features_to_results(results, candidate_items, combined_feature_exprs, pbModel)
        print(is_true)
        solutions = {
            "message": f"重新生成特征：",
            "solutionResults": results,
            "addedFeatureExprs": added_feature_exprs,
        }
        return jsonify(solutions)

@app.route('/features', methods=['POST'])
def features():
    global feature_query
    data = request.get_json()
    id, user_input, candidate_items, problem_model = parse_data(data)
    solution_results = data['solutionResults']
    feature_query = user_input
    user_input = user_input[3:]
    pbModel = ProblemModel()
    pbModel.set_problem_model(problem_model)
    added_feature_exprs, combined_feature_exprs = generate_features(user_input, candidate_items, solution_results, get_featureExprs(features_py, pbModel))
    if added_feature_exprs is None:
        message = "我们没有理解你的需求，请更试一次。"
        return jsonify({"message": message}), 200

    results = add_features_to_results(solution_results, candidate_items, combined_feature_exprs, pbModel)
    logger.info(f"features: {results['solutions'][0]['features']}")
    logger.info(f"added_feature_exprs: {added_feature_exprs}")
    
    solutions = {
        "message": f"添加特征：",
        "solutionResults": results,
        "addedFeatureExprs": added_feature_exprs,
    }
    return jsonify(solutions)

@app.route('/message', methods=['POST'])
def message():
    data = request.get_json()
    id, user_input, candidate_items, problem_model = parse_data(data)
    updated_problemModel, modified_items = parse_instruction(problem_model, user_input, candidate_items)
    
    if updated_problemModel is None and modified_items is None:
        message = "我们没有理解你的需求，请更详细描述你的需求。"
        response_message = {
            "message": message
        }
    else:
        # updated_problemModel = add_math_expression(updated_problemModel)
        logger.info(f"updated_model: {updated_problemModel}")
        response_message = {
            "problemModel": updated_problemModel,
            "modifiedItems": modified_items,
        }

    return jsonify({
        "sessionId": id,
        **response_message
    }), 200

@app.route('/incremental_solve', methods=['POST'])
def incremental_solve():
    data = request.get_json()
    id, candidate_items, problem_model, base_solution, added_variables = parse_incremental_data(data)
    required_courses = data['requiredCourses']
    pbModel, optiModel, results = problem_solving(candidate_items, problem_model, required_courses, True, base_solution, added_variables)
    course_counts = analyse_solution(results)
    # 必选课程的信息
    always_included_courses = []
    if(results['status'] == 'OPTIMAL' or results['status'] == 'TIME_LIMIT' ):
        results = add_features_to_results(results, candidate_items, features_py, pbModel)
        solution_num = results['solutionNum']
        results = sort_results(results)
        for var_name, count in course_counts.items():
            if count == solution_num and solution_num > 0:
                # 从变量名中提取课程信息
                parts = var_name.split('_')
                if len(parts) >= 4:
                    course_name = parts[1]
                    teacher = parts[2]
                    always_included_courses.append(f"{course_name}（{teacher}）")
                    
    response = {
        "always_included_courses": always_included_courses,
        "solutionResults": results,
        "featureExprs": get_featureExprs(features_py, pbModel),
        "courseCounts": course_counts,
    }
    logger.info(f"------solve function-----\npbModel objectives:{pbModel.objectives}\npbModel constraints:{ pbModel.constraints}\npbModel ")
    logger.info(f"optiModel: {optiModel.model}")
    logger.info(f"getting solutions: {results}")
    logger.info(f"featureExprs: {get_featureExprs(features_py, pbModel)}")
    
    return jsonify(response)

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    id, user_input, candidate_items, problem_model = parse_data(data)
    print(f"problem_model:\n{problem_model}; candidate_items:\n{len(candidate_items)}")
    required_courses = data['requiredCourses']
    # sessions[id].candidate_items = candidate_items
    pbModel, optiModel, results = problem_solving(candidate_items, problem_model, required_courses)
    course_counts = analyse_solution(results)
    # 必选课程的信息
    always_included_courses = []
    
    if(results['status'] == 'OPTIMAL' or results['status'] == 'TIME_LIMIT'):
        results = add_features_to_results(results, candidate_items, features_py, pbModel, optiModel)
        results = sort_results(results)
        solution_num = results['solutionNum']
        
        for var_name, count in course_counts.items():
            if count == solution_num and solution_num > 0:
                # 从变量名中提取课程信息
                parts = var_name.split('_')
                if len(parts) >= 4:
                    course_name = parts[1]
                    teacher = parts[2]
                    always_included_courses.append(f"{course_name}（{teacher}）")
    
    if (results['status'] == 'INFEASIBLE'):
        print(f"results status: {results['status']}")
        message = get_diagnosis_message(results)
        print(f"message: {message}")
        response = {
            "solutionResults": results,
            "message": message,
        }
        return jsonify(response), 200
    
    
    logger.info(f"------solve function-----\npbModel objectives:{pbModel.objectives}\npbModel constraints:{ pbModel.constraints}\npbModel ")
    
    
    # logger.info(f"optiModel: {optiModel.model}")
    # logger.info(f"获取到的课表:\n状态: {results['status']}\n解的数量: {results.get('solutionNum', 0)}\n")

    response = {
        "always_included_courses": always_included_courses,
        "solutionResults": results,
        "featureExprs": get_featureExprs(features_py, pbModel),
        "courseCounts": course_counts,
    }
    logger.info(f"featureExprs: {get_featureExprs(features_py, pbModel)}")
    return jsonify(response)

def parse_incremental_data(data):
    id = data.get('sessionId', 123)  # 获取会话ID
    problem_model = data.get('problemModel', {})
    candidate_items = data.get('candidateItems', [])
    
    # 解析 base_solution，包含value和priority信息
    base_solution = {} 
    for item in candidate_items:
        key = f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"
        base_solution[key] = {
            'value': 1 if item['chosen'] else 0,
            'priority': item.get('priority', 3.0)  # 使用课程的优先级，默认为3.0
        }

    # 解析 added_variables
    added_variables = []
    for item in candidate_items:
        if item['added']:
            key = f"x_{item['课程名']}_{item['主讲教师']}_{item['上课时间']}"
            added_variables.append(key)
    
    candidate_items = [item for item in candidate_items if item['selected']]
    for item in candidate_items:
        # 使用pop()方法一次性删除不需要的字段
        item.pop('selected', None)  # 如果字段存在，删除；如果不存在，不做任何操作
        item.pop('chosen', None)
        item.pop('userSelected', None)
        item.pop('added', None)
    
    return id, candidate_items, problem_model, base_solution, added_variables
    

def parse_data(data):
    id = data.get('sessionId', 123)  # 获取会话ID
    user_input = data.get('message', '')  # 获取用户消息
    problem_model = data.get('problemModel', {})
    candidate_items = data.get('candidateItems', [])  # 获取选中的项目
    candidate_items = [item for item in candidate_items if item['selected']]
    for item in candidate_items:
        # 使用pop()方法一次性删除不需要的字段
        item.pop('selected', None)  # 如果字段存在，删除；如果不存在，不做任何操作
        item.pop('chosen', None)
        item.pop('userSelected', None)
        item.pop('added', None)
        

    return id, user_input, candidate_items, problem_model



@app.route('/hello', methods=['POST'])
def hello():
    problem_model = get_default_problem_model()
    request_data = {
        "status": "success", 
        # "problemModel": problem_model,
        "featureExprs": features_py,
        "message": "Welcome~ I am your course selection assistant~",
        }
    return jsonify(request_data), 200


@app.route('/create_session', methods=['POST'])
def create_session():
    data = request.get_json()
    id = data.get('sessionId', 123)
    user_dir = f"../user-study/IterLens/{id}"
    
    # 获取最新的数据文件
    latest_data_file = get_latest_data_file(id)
    
    if latest_data_file and os.path.exists(latest_data_file):
        try:
            with open(latest_data_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                current_preference = user_data.get('current_preference', [])
                messages = user_data.get('messages', [])
                problem_model = user_data.get('problem_model', {})
                model_nodes = user_data.get('model_nodes', [])
                features_exprs = user_data.get('features_exprs', {})
                action_logs = user_data.get('action_logs', [])
                sessions[id] = Session(current_preference, messages, problem_model, model_nodes, features_exprs, action_logs)
                
                logger.info(f"已从 {latest_data_file} 加载用户 {id} 的现有数据，包含 {len(action_logs)} 个操作记录")
                request_data = {
                    "status": "success",
                    "currentPreference": current_preference,
                    "messages": messages,
                    "problemModel": problem_model,
                    "modelNodes": model_nodes,
                }
                return jsonify(request_data), 200
        except Exception as e:
            logger.error(f"加载用户数据时出错: {str(e)}")
            # 如果加载失败，创建新session
            sessions[id] = Session([],[],{},[],{},[])
            return jsonify({"message": "Failed to load existing data, created new session."}), 200
    else:
        # 创建新的用户数据文件夹
        os.makedirs(user_dir, exist_ok=True)
        sessions[id] = Session([],[],{},[],{},[])
        logger.info(f"为用户 {id} 创建新session")
        return jsonify({"message": "Session created successfully."}), 200

@app.route('/close_session', methods=['POST'])
def close_session():
    if request.method != 'POST':
        return '', 405  # 或者让它什么都不做也行
    data = request.get_json()
    id = data.get('sessionId', 123)
    print(id)
    if id and id in sessions:
        # 同步保存用户数据到JSON文件
        try:
            user_dir = f"../user-study/IterLens/{id}"
            data_dir = f"{user_dir}/data"
            
            # 确保data目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 生成时间戳文件名
            timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
            data_file_path = f"{data_dir}/data_{timestamp}.json"
            
            # 准备要保存的数据
            user_data = {
                'current_preference': sessions[id].current_preference,
                'messages': sessions[id].messages,
                'model_nodes': sessions[id].model_nodes,
                'action_logs': sessions[id].action_logs,
                'save_timestamp': timestamp,
                'save_datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'session_closed': True
            }
            
            # 写入JSON文件
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"用户数据已保存到 {data_file_path}")
        except Exception as e:
            logger.error(f"保存用户数据时出错: {str(e)}")
        del sessions[id]
        logger.info(f"Session {id} closed and deleted.")
        return jsonify({"message": "Session closed and deleted successfully."}), 200
    else:
        return jsonify({"message": "Session not found."}), 404

@app.route('/required_courses', methods=['POST'])
def required_courses():
    data = request.get_json()
    id = data.get('sessionId', 123)
    required_courses = data.get('requiredCourses', [])
    logger.info(f"Received required courses: {required_courses}")
    
    # 构建响应消息
    if required_courses:
        message = f"已将以下课程设置为必修课：{', '.join(required_courses)}。这意味着在所有方案中，这些课程必须被选择。"
    else:
        message = "新增的课程没有必修课。"
    return jsonify({
        "message": message,
    })
    
    
@app.route('/log_user_action', methods=['POST', 'OPTIONS'])
def log_user_action():
    if request.method == 'OPTIONS':
        return jsonify({"message": "OPTIONS handled successfully."}), 200
    
    try:
        data = request.get_json()
        user_id = data.get('sessionId', 123)
        action_type = data.get('actionType', '')
        action_data = data.get('actionData', {})
        print(f"action_type: {action_type}, action_data: {action_data}")
        # 保存用户操作日志
        save_user_action_log(user_id, action_type, action_data)
        
        return jsonify({"message": "User action logged successfully."}), 200
    except Exception as e:
        logger.error(f"记录用户操作时出错: {str(e)}")
        return jsonify({"message": "Failed to log user action."}), 500

@app.route('/update_messages', methods=['POST'])
def update_messages():
    data = request.get_json()
    id = data.get('sessionId', 123)
    new_messages = data.get('messages', [])
    
    if id in sessions:
        sessions[id].messages = new_messages
        # 异步保存数据
        save_user_data_async(id)
        return jsonify({"message": "Messages updated successfully."}), 200
    else:
        return jsonify({"message": "Session not found."}), 404

@app.route('/update_model_nodes', methods=['POST'])
def update_model_nodes():
    data = request.get_json()
    id = data.get('sessionId', 123)
    new_model_nodes = data.get('modelNodes', [])
    
    if id in sessions:
        sessions[id].model_nodes = new_model_nodes
        # 异步保存数据
        save_user_data_async(id)
        return jsonify({"message": "Model nodes updated successfully."}), 200
    else:
        return jsonify({"message": "Session not found."}), 404

@app.route('/update_preference', methods=['POST'])
def update_preference():
    data = request.get_json()
    id = data.get('sessionId', 123)
    new_preference = data.get('currentPreference', [])
    
    if id in sessions:
        sessions[id].current_preference = new_preference
        # 异步保存数据
        save_user_data_async(id)
        return jsonify({"message": "CurrentPreference updated successfully."}), 200
    else:
        return jsonify({"message": "Session not found."}), 404

@app.route('/save_data', methods=['POST'])
def save_data():
    """保存用户的消息和偏好数据"""
    try:
        data = request.get_json()
        id = data.get('sessionId', 123)
        messages = data.get('messages', [])
        current_preference = data.get('currentPreference', {})
        model_nodes = data.get('modelNodes', [])
        
        logger.info(f"[SAVE_DATA] 开始保存数据，用户ID: {id}")
        logger.info(f"[SAVE_DATA] 接收数据 - messages: {len(messages)}, preference: {bool(current_preference)}, model_nodes: {len(model_nodes)}")
        
        if id not in sessions:
            logger.error(f"[SAVE_DATA] Session {id} 不存在")
            return jsonify({"message": "Session not found."}), 404
        
        # 更新session中的数据
        if messages:
            sessions[id].messages = messages
        if current_preference:
            sessions[id].current_preference = current_preference
        if model_nodes:
            sessions[id].model_nodes = model_nodes
        
        logger.info(f"[SAVE_DATA] Session数据已更新")
        
        # 记录用户操作日志
        action_data = {
            'action': 'manual_save',
            'message_count': len(messages) if messages else 0,
            'candidate_courses_count': len(current_preference.get('candidateItems', [])) if current_preference else 0,
            'model_nodes_count': len(model_nodes) if model_nodes else 0,
            'action_logs_count': len(sessions[id].action_logs)
        }
        logger.info(f"[SAVE_DATA] 开始保存操作日志...")
        save_user_action_log(id, action_data)
        logger.info(f"[SAVE_DATA] 操作日志保存完成")
        
        # 同步保存数据到文件，确保保存成功
        try:
            user_dir = f"../user-study/IterLens/{id}"
            data_dir = f"{user_dir}/data"
            
            logger.info(f"[SAVE_DATA] 数据目录路径: {data_dir}")
            
            # 确保data目录存在
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"[SAVE_DATA] 数据目录创建成功")
            
            # 生成时间戳文件名
            timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
            data_file_path = f"{data_dir}/data_{timestamp}.json"
            logger.info(f"[SAVE_DATA] 数据文件路径: {data_file_path}")
            
            # 准备要保存的数据
            user_data = {
                'current_preference': sessions[id].current_preference,
                'messages': sessions[id].messages,
                'model_nodes': sessions[id].model_nodes,
                'action_logs': sessions[id].action_logs,
                'save_timestamp': timestamp,
                'save_datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            }
            
            # 同步写入JSON文件
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"用户数据已同步保存到 {data_file_path}")
            
        except Exception as save_error:
            logger.error(f"同步保存用户数据时出错: {str(save_error)}")
            return jsonify({"message": f"Failed to save data to file: {str(save_error)}"}), 500
        
        return jsonify({f"message": f"数据已成功保存！保存时间: {time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}。"}), 200
        
    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")
        return jsonify({"message": "Failed to save data."}), 500

if __name__ == '__main__':
    load_dotenv('.env')
    # 获取 API 密钥和端口
    app.run(host='0.0.0.0', port=8010, debug=True)