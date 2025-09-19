import { fetchData } from './apiService.js';
import { ref } from 'vue';
import { currentConfig } from "../config/config";

const API_URL = currentConfig.API_URL;

// 操作类型常量
export const ACTION_TYPES = {
  // 新增课程相关
  ADD_COURSES: 'ADD_COURSES',
  
  // 展开/折叠相关
  EXPAND_COLLAPSE: 'EXPAND_COLLAPSE',
  
  // 切换视图模式相关
  CHANGE_VIEW_MODE: 'CHANGE_VIEW_MODE',
  
  // 课程卡片勾选相关
  COURSE_CARD_CHECK: 'COURSE_CARD_CHECK',
  
  // 课程选择相关
  COURSE_SELECT: 'COURSE_SELECT',
  
  // 移除课程相关
  REMOVE_COURSE: 'REMOVE_COURSE',

  DELETE_COURSE: 'DELETE_COURSE',
  
  // 保存课表相关
  SAVE_COURSES: 'SAVE_COURSES',
  
  // 问题求解相关
  GET_SOLUTIONS: 'GET_SOLUTIONS',
  
  // 用户指令相关
  USER_INSTRUCTION: 'USER_INSTRUCTION',
  UPDATE_PROBLEM_MODEL: 'UPDATE_PROBLEM_MODEL',
  SAVE_FEATURE_EXPRS: 'SAVE_FEATURE_EXPRS',
  TOGGLE_CONDITION: 'TOGGLE_CONDITION',
  
  // 移除条件相关
  REMOVE_CONDITION: 'REMOVE_CONDITION',
  
  // 查看历史相关
  VIEW_HISTORY: 'VIEW_HISTORY',
  
  // 切换节点相关
  SWITCH_NODE: 'SWITCH_NODE',

  // 方案导航相关
  NAVIGATE_SOLUTION: 'NAVIGATE_SOLUTION',
  
  
  // 特征表格相关
  APPLY_FEATURE_FILTER: 'APPLY_FEATURE_FILTER',
  REMOVE_FEATURE_FILTER: 'REMOVE_FEATURE_FILTER',
  
  // 偏好面板
  MODIFY_CONSTRAINT: 'MODIFY_CONSTRAINT',
  SET_OBJECTIVE_WEIGHT: 'SET_OBJECTIVE_WEIGHT',
  
  // 必修课程相关
  SET_REQUIRED_COURSES: 'SET_REQUIRED_COURSES',
  REMOVE_REQUIRED_COURSE: 'REMOVE_REQUIRED_COURSE',
  UPDATE_COURSE_PRIORITY: 'UPDATE_COURSE_PRIORITY',
  REMOVE_COURSE_PRIORITY: 'REMOVE_COURSE_PRIORITY',
  
  // 数据管理相关
  SAVE_DATA: 'SAVE_DATA', // 用户主动保存数据
};

// 用户操作日志
export const userActionLog = ref([]);

// 记录用户操作
export const logUserAction = async (actionType, actionData = {}) => {
  console.log('logUserAction 被调用，actionType:', actionType, 'actionData:', actionData);
  
  try {
    const timestamp = new Date().toISOString();
    const sessionId = localStorage.getItem('sessionId');
    
    console.log('timestamp:', timestamp, 'sessionId:', sessionId);
    
    if (!sessionId) {
      console.error('Session ID not found for logging action');
      return;
    }
    
    // 确保每个action都带有时间戳
    const logData = {
      sessionId,
      timestamp,
      actionType,
      actionData: {
        ...actionData,
        timestamp: timestamp // 在actionData中也添加时间戳
      }
    };
    
    console.log('Logging user action:', logData);
    
    // 发送日志到后端
    console.log('准备发送到后端...');
    await fetchData(`${API_URL}/log_user_action`, 'POST', logData);
    console.log('已发送到后端');

    const logEntry = {
      timestamp,
      actionType,
      data: actionData
    };

    userActionLog.value.push(logEntry);
    console.log('已添加到本地日志');
    
    // 开发环境下在控制台输出日志
    if (process.env.NODE_ENV === 'development') {
      console.log('User Action:', logEntry);
    }
  } catch (error) {
    console.error('Error logging user action:', error);
  }
}; 