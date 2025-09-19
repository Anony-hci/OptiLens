import { ref, nextTick } from 'vue';
import { getMessageResponseFromBackend, getFeaturesResponseFromBackend, getSavedFeaturesResponseFromBackend } from './apiService';
import { currentPreference, updatePreferenceSolutions, updatePreferenceDescription, updatePreferenceCandidateItems, getProblemModel } from './preferenceService.js';
import { addNewNode,} from './modelNodeService';
import { maximal_cliques } from './maximalCliquesService';
import { logUserAction, ACTION_TYPES } from './userActionLogService.js';
import { setGlobalDisplayMode, setGlobalVisibility, toggleshowAllCourses } from './scheduleService.js';

// 用户消息和聊天记录
export const userMessage = ref(''); // 用户输入的消息
export const messages = ref([]); // 用来存储消息记录

// 生成唯一消息ID的辅助函数
export const generateMessageId = (type) => {
  return `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const addUserMessage = (text) => {
  messages.value.push({ 
    id: generateMessageId('user'),
    sender: 'You', 
    text: text, 
    type: 'text' 
  });
  // addFindMessage();
}

export const addFindMessage = (text='') => {
  messages.value.push({
    id: generateMessageId('bot'),
    content: text,
    sender: 'Bot',
    type: 'find' 
  })
}

// 初始化欢迎消息
export const initializeMessages = () => {
    messages.value.push({ 
      id: generateMessageId('welcome'),
      sender: 'Bot', 
      text: "Hello, I am your course selection assistant. My default settings are:<br>1) Only one section will be chosen for the same course;<br>2) Only one course will be chosen for the same time slot;<br>3) I will try to select as many of the courses you add as possible.<br><br>Next, please add the courses you are interested in.", 
      type: 'text' 
    });
  };

// 消息发送和处理
export const sendMessage = async () => {
    if (userMessage.value.trim() === "") return;
  
    // 添加用户消息到聊天记录
    messages.value.push({ 
      id: generateMessageId('user'),
      sender: 'You', 
      text: userMessage.value, 
      type: 'text' 
    });

    // 检查用户输入是否为纯整数
    if (!isNaN(parseInt(userMessage.value)) && userMessage.value.trim() === parseInt(userMessage.value).toString()) {
      const inputNumber = parseInt(userMessage.value);
      const currentRequiredCoursesNum = currentPreference.value.requiredCourses.length;
      const totalCourseNum = currentRequiredCoursesNum + inputNumber;
      
      // 生成总课程数量约束，参考template id=10
      const totalCoursesConstraint = {
        type: "add",
        name: "总课程数量",
        lhs: {
          template_id: "10",
          parameters: {}
        },
        constraint_type: "==",
        rhs: totalCourseNum,
        description: "总课程数量",
        math_expression: '\\sum_{i=1}^{n} x_i',
      };
      
      // 构造problemModel
      const problemModel = {
        updated_constraints: [totalCoursesConstraint]
      };
      
      // 添加problemModel类型的消息
      const problemModelMessage = {
        id: generateMessageId('problemModel'),
        sender: 'Bot',
        type: 'problemModel',
        content: problemModel,
        updated: false,
      };
      
      messages.value.push(problemModelMessage);
      
      return;
    }
  
    // 获取当前已选中项目的内容
    const candidateItemsData = currentPreference.value.candidateItems.filter(item => item.selected);
  
    // 创建一个包含消息和选中项目的请求体
    let requestData = {
      message: userMessage.value,
      messages: messages.value,
      candidateItems: candidateItemsData,
      problemModel: getProblemModel(),
      requiredCourses: currentPreference.value.requiredCourses,
    };

    const message = userMessage.value;
    userMessage.value = '';

    let response;
    if (messages.value.length > 1 && messages.value[messages.value.length-2].text && messages.value[messages.value.length-2].text.startsWith('新增的课程没有必修课。')) {
      const added_courses = messages.value[messages.value.length-3].content.courses.map(course => course.name);
      requestData.message = `从新增的课程【${added_courses.join(',')}】中选择${message}门课程`;
      response = await getMessageResponseFromBackend(requestData);
    }
    else if (message.startsWith("fff")) {
      // 如果用户消息以 "特征：" 开头，获取特征响应
      requestData = {...requestData, solutionResults: currentPreference.value.solutionResults};
      response = await getFeaturesResponseFromBackend(requestData);
    } else {
      // 否则获取普通消息响应
      response = await getMessageResponseFromBackend(requestData);
    }

    // 记录发送消息操作 - 使用新的ACTION_TYPE
    logUserAction(ACTION_TYPES.USER_INSTRUCTION, {
      content: message
    });
    processResponseMessage(response)
        // 记录发送消息操作
    if(response.message){
      logUserAction(ACTION_TYPES.USER_INSTRUCTION, {
        content: response.message
      });
    }
  
  };

  export const processResponseMessage = (response) => {
    if (response.problemModel) {
      const problemModelMessage = {
        sender: 'Bot',
        type: 'problemModel',
        text: response.message,
        content: response.problemModel,
        updated: false,
      };
      messages.value.push(problemModelMessage);
    }else if (response.addedFeatureExprs) {
      const addedFeatureExprsMessage = {
        sender: 'Bot',
        type: 'addedFeatureExprs',
        text: response.message,
        content: response.addedFeatureExprs
      }
      updatePreferenceSolutions(response.solutionResults);
      addNewNode(false, true, Object.keys(response.addedFeatureExprs))
      // updatePreferenceCandidateItems();
      messages.value.push(addedFeatureExprsMessage);
      currentPreference.value.featureExprs = { ...currentPreference.value.featureExprs, ...response.addedFeatureExprs };

    }else if (response.solutionResults){
      logUserAction(ACTION_TYPES.GET_SOLUTIONS, {
        status: response.solutionResults.status || 'unknown',
        solution_num: response.solutionResults ? response.solutionResults.solutionNum : 0
      });
      if (typeof response.solutionResults === 'string') {
        response.solutionResults = JSON.parse(response.solutionResults);
      }
      // 更新当前节点的求解结果
      updatePreferenceSolutions(response.solutionResults);
      
      // 使用 nextTick 确保在下一个 DOM 更新周期后执行
      nextTick(() => {
        updatePreferenceCandidateItems();
        toggleshowAllCourses(false);

      });
      let description;
      if (response.solutionResults.status === 'OPTIMAL') {
        const solutionNum = response.solutionResults ? response.solutionResults.solutionNum || 0 : 0;
        if (solutionNum === 500){
            description =  `There are more than 500 solutions, we will show you the first 500~`;
        }else{
            description = `We found ${solutionNum} solutions.`;
        }
        // if(response.always_included_courses && response.always_included_courses.length > 0){
        //   description += `<br><br>所有课表中都包括了${response.always_included_courses.length}门课程(蓝色)：<br>${response.always_included_courses.map((course, index) => `&nbsp;&nbsp;${index + 1}. ${course}`).join(',<br> ')}。<br>背景为黄色的课程是需要您进一步选择的课程。`
        // }
      } else if(response.solutionResults.status === 'INFEASIBLE'){
        if (response.solutionResults.IIS.length === 1){
          description = "存在无法满足的约束：" + response.solutionResults.IIS.map(item => Object.keys(item)[0]).join("<br>");
        } else{
          description = "不存在满足所有条件的课表";
          description += "，冲突的约束为：<br>" + response.solutionResults.IIS.map((item, index) => `${index + 1}. ${Object.keys(item)[0]}`).join('<br>');
        } 
      } else {
        description = `求解状态为${response.solutionResults.status}，得到了${response.solutionResults.solutionNum}个课表方案~`
      }
      // 确保 HTML 标签能被正确解析
      updatePreferenceDescription(description)
      messages.value.push({ sender: 'Bot', text: description, type: 'text' });
    }
    
    if(response.message) {
      console.log("response.message", response.message)
      messages.value.push({ sender: 'Bot', text: response.message.replace(/\n/g, '<br>'), type: 'text' });
    }

    // 处理响应消息
    if (response.modifiedItems) {
      for (const item of response.modifiedItems) {
        const index = currentPreference.value.candidateItems.findIndex(i => i.课程名 === item.课程名 && i.主讲教师 === item.主讲教师 && i.priority !== item.priority);
        if (index !== -1) {
          currentPreference.value.candidateItems[index].priority = item.priority;
          currentPreference.value.candidateItems[index].priority_type = 'user';
        }
      }
    }

    if (response.featureExprs) {
      currentPreference.value.featureExprs = response.featureExprs;
    }
    
    if (response.global_constraints){
      updateGlobalConstraints(response.global_constraints);
      console.log("Initialized first node with global constraints");
    }

    if(response.maximal_cliques){
      maximal_cliques.value = response.maximal_cliques;
    }

    if(response.candidateItems){
      currentPreference.value.candidateItems = response.candidateItems;
      // 抽取不同的课程名
      const uniqueCourseNames = currentPreference.value.candidateItems ? [...new Set(currentPreference.value.candidateItems.map(item => item['课程名']))] : [];
      if (currentPreference.value.candidateItems.length > 0) {
        // 创建课程选择消息
        messages.value.push({ 
          sender: 'Bot', 
          type: 'addCourses',
          content: {
            addedCount: uniqueCourseNames.length,
            totalCount: currentPreference.value.candidateItems.length, // 修改为这次添加的课程总数
            courses: uniqueCourseNames.map(name => ({
              name: name,
              isRequired: true // 如果是第一次添加课程，默认全选
            })),
            isFirstTime: true
          },
          confirmed: false
        });
      }
    }

  }

  
  export const saveFeatureExprs = async (featureExpr, isTrue) => {
    const requestData = {
      addedFeatureExprs: featureExpr,
      isTrue: isTrue,
      candidateItems: currentPreference.value.candidateItems,
      problemModel: getProblemModel(),
    }
    console.log("addedFeatureExprs", featureExpr)
    messages.value[messages.value.length - 1].updated = true;
    if(isTrue) {
      messages.value[messages.value.length - 1].buttonMessage = "已记录该特征"
    }else {
      messages.value[messages.value.length - 1].buttonMessage = "重新生成特征，请稍等..."
    }
    const response = await getSavedFeaturesResponseFromBackend(requestData);
    processResponseMessage(response)
    
  }