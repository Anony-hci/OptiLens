<template>
  <div>
    <!-- 普通文本消息 -->
    <div v-if="msg.type === 'text'">
      <p>
        <!-- <strong>{{ msg.sender }}: </strong> -->
        <span v-html="msg.text"></span>
      </p>
    </div>

    <!-- 添加课程选择消息 -->
    <div v-if="msg.type === 'addCourses'">
      <p>You have added {{ msg.content.addedCount }} / {{ msg.content.totalCount }} courses. Which of them are required courses?</p>
      <div class="course-selection-container">
        <!-- 添加全选功能 -->
        <div class="select-all-container">
          <input 
            type="checkbox" 
            id="select-all" 
            :checked="areAllCoursesSelected(msg.content.courses)"
            :indeterminate.prop="areSomeCoursesSelected(msg.content.courses) && !areAllCoursesSelected(msg.content.courses)"
            @change="toggleSelectAllCourses(msg.content.courses)"
          />
          <label for="select-all" class="select-all-label">Select all</label>
        </div>
        <div class="courses-list">
          <div v-for="(course, index) in msg.content.courses" :key="index" class="course-item">
            <input 
              type="checkbox" 
              :id="`course-${index}`" 
              v-model="course.isRequired" 
            />
            <label :for="`course-${index}`">{{ course.name }}</label>
          </div>
        </div>
      </div>
      <div class="course-confirm-button" v-if="!msg.confirmed">
        <button 
          @click="confirmRequiredCourses(msg)" 
          class="confirm-button"
          :style="!msg.content.courses.some(course => course.isRequired) ? 'background-color: #4d6584' : ''"
        >
          {{ !msg.content.courses.some(course => course.isRequired) ? 'None of the above are required courses' : 'Add as required courses'  }}
        </button>
      </div>
      <p v-else class="confirmed-message">
        {{ msg.content.courses.some(course => course.isRequired) ?'Required courses set' : 'No required courses' }}
      </p>
    </div>

    <div v-if="msg.type === 'find'">
      <p>{{ msg.content || 'The candidate courses or preferences you set have changed,'}} Please click 
        <button 
          @click="startSolving(msg.content, msg.id)" 
          class="solve-button"
        >
          Find
        </button> {{ msg.content ? 'to find more solutions' : 'to find solutions.' }}</p>
    </div>
    <!-- 问题模型消息 -->
    <div v-if="msg.type === 'problemModel'">
      <p>{{ "Preferences modified as instructed:" }}</p>
      <div
        v-for="objective in msg.content.updated_objectives"
        :key="objective.name"
        class="key-value-pair"
      >
        <div
          class="key-container"
        >
          <div
            class="key"
            @click="toggleKey('problemModel', objective.name, msg.id); logToggleAction(objective.name, msg.id)"
            :class="{ clickable: true }"
          >
            <input 
              type="checkbox" 
              v-model="objective.selected" 
              @click.stop
              :checked="objective.selected !== false"
              :disabled="msg.updated"
            />
            {{ getObjectiveKey(objective) }}
            <span class="toggle-icon">
              {{ isKeyExpanded('problemModel', objective.name, msg.id) ? '▲' : '▼' }}
            </span>
          </div> 
          
          <div class="expression-description">
            <div v-if="hasCourses(objective.expression)" class="courses-panel">
              <div v-for="course in extractCourseVars(objective.expression)" :key="course.fullName" class="course-item">
                <input type="checkbox" v-model="course.selected">
                <span>{{ formatCourseName(course.fullName) }}</span>
              </div>
            </div>
            <div v-else>
              {{ objective.description }}
            </div>
          </div>
        </div>
        <div
          class="value"
          v-if="isKeyExpanded('problemModel', objective.name, msg.id)"
        >
          
          <span v-html="getMathExpression(objective)"></span>
          
        </div>
      </div>

      <div
        v-for="constraint in msg.content.updated_constraints"
        :key="constraint.description"
        class="key-value-pair"
      >
        <div
          class="key-container"
        >
          <div
            class="key"
            @click="toggleKey('problemModel', constraint.description, msg.id); logToggleAction(constraint.name, msg.id)"
            :class="{ clickable: true }"
          >
            <input 
              type="checkbox" 
              v-model="constraint.selected" 
              @click.stop
              :checked="constraint.selected !== false"
            />
            {{ getConstraintKey(constraint) }}
            <span class="toggle-icon">
              {{ isKeyExpanded('problemModel', constraint.description, msg.id) ? '▲' : '▼' }}
            </span>
          </div>
          <div class="expression-description">
            <div v-if="hasCourses(constraint.lhs)" class="courses-panel">
              <div v-for="course in extractCourseVars(constraint.lhs)" :key="course.fullName" class="course-item">
                <input type="checkbox" v-model="course.selected">
                <span>{{ formatCourseName(course.fullName) }}</span>
              </div>
            </div>
            <div v-else>
              {{ constraint.description }}
            </div>
          </div>
          
        </div>
        <div
          class="value"
          v-if="isKeyExpanded('problemModel', constraint.description, msg.id)"
        >
        
          <span v-html="getMathExpression(constraint)"></span>
        </div>
      </div>
      <div>
        <button
          v-if="!msg.updated"
          @click="updateProblemModel(msg.content, msg.id)"
          class="constraint-button"
        >
          update
        </button>
        <p v-else class="confirmed-message">
          Updated to preferences
        </p>
      </div>
    </div>
    <!-- 特征选择消息 -->
    <div v-if="msg.type === 'features'">
      <p>{{ msg.text }}<br>我们针对所有的方案提供了特征：<br></p>
      <div class="features-container">
        <button
          v-for="feature in features" 
          :key="feature.name"
          class="feature-button"
          :style="{ backgroundColor: feature.selected ? '#1a73e8' : '#FFFFFF' }"
          @click="() => {
            feature.selected = !feature.selected;
            $forceUpdate();
          }"
        >
          {{ feature.name }}
        </button>
        <p>如果想要查看其他特征，则添加"fff"前缀在对话框中输入。</p>
      </div>
    </div>

    <!-- 添加特征表达式消息 -->
    <div v-if="msg.type === 'addedFeatureExprs'">
      <p>
        <!-- <strong>{{ msg.sender }}:</strong> -->
        {{ msg.text }}</p>
      <div
        v-for="(value, key) in msg.content"
        :key="key"
        class="key-value-pair"
      >
        <div
        class="key"
        @click="toggleKey('addedFeatureExprs', key, msg.id)"
        :class="{ clickable: true }"
        >
        {{ key }}
        <span class="toggle-icon">
            {{ isKeyExpanded('addedFeatureExprs', key, msg.id) ? '▲' : '▼' }}
        </span>
        </div>
        <div
        class="value"
        v-if="isKeyExpanded('addedFeatureExprs', key, msg.id)"
        v-html="value.replace(/\n/g, '<br>')"
        style="white-space: pre-wrap;"
        >
        
        </div>
      </div>

      <div class="feature-update-button" v-if="false">
        <button
        v-if="!msg.updated"
        @click="saveFeatureExprs(msg.content, true)"
        class="feature-button-true"
        >
        正确
        </button>
        <button
        v-if="!msg.updated"
        @click="saveFeatureExprs(msg.content, false)"
        class="feature-button-false"
        >
        不正确
        </button>
        <p v-else>
        {{ msg.buttonMessage }}
        </p>
      </div>
    </div>

    <!-- 偏好设置更新确认消息 -->
    <div v-if="msg.type === 'preferenceUpdated'">
      <p>{{ "偏好设置已更新，当前包含：" }}</p>
      <!-- <p class="update-timestamp">更新时间：{{ new Date(msg.content.updateTimestamp).toLocaleString('zh-CN') }}</p> -->
      
      <!-- 候选课程 -->
      <div class="key-value-pair">
        <div class="key-container">
          <div class="key">
            📚 {{ getUniqueCourseNames(msg.content.candidateItems).length }}/{{ msg.content.candidateItems.length }}门候选课程
            <span class="toggle-icon" @click="toggleKey('preferenceUpdated', 'candidateCourses', msg.id)">
              {{ isKeyExpanded('preferenceUpdated', 'candidateCourses', msg.id) ? '▲' : '▼' }}
            </span>
          </div>
        </div>
        <div
          class="value"
          v-if="isKeyExpanded('preferenceUpdated', 'candidateCourses', msg.id)"
        >
          <div class="courses-panel">
            <div v-for="course in getUniqueCourseNames(msg.content.candidateItems)" :key="course['课程名'] + course['主讲教师'] + course['上课时间']" class="course-item">
              <span>{{ course }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 必修课程 -->
      <div class="key-value-pair">
        <div class="key-container">
          <div class="key">
            🎯 {{ msg.content.requiredCourses.length }}门必修课程
            <span class="toggle-icon" @click="toggleKey('preferenceUpdated', 'requiredCourses', msg.id)">
              {{ isKeyExpanded('preferenceUpdated', 'requiredCourses', msg.id) ? '▲' : '▼' }}
            </span>
          </div>
        </div>
        <div
          class="value"
          v-if="isKeyExpanded('preferenceUpdated', 'requiredCourses', msg.id)"
        >
          <div class="courses-panel">
            <div v-for="course in msg.content.requiredCourses" :key="course" class="course-item">
              <span>{{ course }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 条件（约束和目标） -->
      <div class="key-value-pair">
        <div class="key-container">
          <div class="key">
            🔒 {{ (msg.content.objectives?.length || 0) + (msg.content.constraints?.length || 0) }}个条件
            <span class="toggle-icon" @click="toggleKey('preferenceUpdated', 'conditions', msg.id)">
              {{ isKeyExpanded('preferenceUpdated', 'conditions', msg.id) ? '▲' : '▼' }}
            </span>
          </div>
        </div>
        <div
          class="value"
          v-if="isKeyExpanded('preferenceUpdated', 'conditions', msg.id)"
        >
          <!-- 目标函数 -->
          <div v-if="msg.content.objectives && msg.content.objectives.length > 0">
            <ul class="conditions-list">
              <li v-for="objective in msg.content.objectives" :key="objective.description">
                {{ objective.description }}
              </li>
            </ul>
          </div>
          
          <!-- 约束条件 -->
          <div v-if="msg.content.constraints && msg.content.constraints.length > 0">
            <ul class="conditions-list">
              <li v-for="constraint in msg.content.constraints" :key="constraint.description">
                {{ constraint.description }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="preference-actions">
        <p class="action-question" v-if="!msg.updated">是否需要根据更新后的设置重新寻找方案？
          <button 
          
          @click="startSolving(msg.content, msg.id)" 
          class="solve-button"
        >
          Find
        </button>
        </p>
        <p v-else class="confirmed-message">
          已重新寻找方案
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { toggleKey, isKeyExpanded, getObjectiveKey, getObjectiveValue, getConstraintKey, getConstraintValue, getMathExpression } from '../logic/keyService';
import { features, solving } from '../logic/modelNodeService';
import { saveFeatureExprs, messages, generateMessageId, addFindMessage } from '../logic/messageService';
import { getConstraints, getObjectives, updateModifiedModel, updatePreferenceRequiredCourses } from '../logic/preferenceService';
import { logUserAction, ACTION_TYPES } from '../logic/userActionLogService';
import { extractCourseVars, formatCourseName, generateCourseDescription, hasCourses } from '../logic/parseService';
import { sendRequiredCoursesToBackend } from '../logic/apiService';
import { currentPreference, updatePreferenceProblemModel } from '../logic/preferenceService';
import { getUniqueCourseNames } from '../logic/coursesService';
import { watch } from 'vue';

defineProps({
  msg: {
    type: Object,
    required: true
  }
});

// 确保所有消息都有id
watch(() => messages.value, (newMessages) => {
  newMessages.forEach((msg, index) => {
    if (!msg.id) {
      msg.id = `msg_${index}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
  });
}, { immediate: true, deep: true });

// 添加确认必修课程的函数
const confirmRequiredCourses = async (msg) => {
  // 获取所有被标记为必修的课程名称
  const requiredCourses = msg.content.courses
    .filter(course => course.isRequired)
    .map(course => course.name);
  
  // 记录操作
  logUserAction(ACTION_TYPES.SET_REQUIRED_COURSES, {
    requiredCoursesCount: requiredCourses.length,
    requiredCourses: requiredCourses
  });
  
  const requestData = {
    candidateItems: currentPreference.value.candidateItems,
    requiredCourses: requiredCourses,
  }

  updatePreferenceRequiredCourses(requiredCourses);
  
  // const response = await sendRequiredCoursesToBackend(requestData);
  
  // 标记消息为已确认
  msg.confirmed = true;
  addFindMessage();
  
};

// 添加全选功能相关方法
const areAllCoursesSelected = (courses) => {
  return courses.length > 0 && courses.every(course => course.isRequired);
};

const areSomeCoursesSelected = (courses) => {
  return courses.some(course => course.isRequired);
};

const toggleSelectAllCourses = (courses) => {
  const allSelected = areAllCoursesSelected(courses);
  courses.forEach(course => {
    course.isRequired = !allSelected;
  });
};

// 添加新的更新函数
const updateProblemModel = (content, id) => {
  //
  // 过滤出选中的目标和约束
  const selectedContent = {
    updated_objectives: content.updated_objectives?.filter(obj => obj.selected !== false),
    updated_constraints: content.updated_constraints?.filter(cons => cons.selected !== false)
  };
  
  // 记录操作
  logUserAction(ACTION_TYPES.UPDATE_PROBLEM_MODEL, {
    objectivesCount: selectedContent.updated_objectives?.length || 0,
    constraintsCount: selectedContent.updated_constraints?.length || 0,
    objectives: selectedContent.updated_objectives?.map(obj => obj.description) || [],
    constraints: selectedContent.updated_constraints?.map(cons => cons.description) || []
  });
  
  // 调用原有的更新函数
  updateModifiedModel(selectedContent);
  updatePreferenceProblemModel(selectedContent);

  const msgIndex = messages.value.findIndex(msg => msg.id === id);
  if (msgIndex !== -1) {
    messages.value[msgIndex].updated = true;
  }
  console.log("messages", messages)
  
  // 添加偏好设置更新确认消息
  addPreferenceUpdatedMessage(selectedContent);
};

// 添加偏好设置更新确认消息
const addPreferenceUpdatedMessage = (selectedContent) => {
  // 记录更新时的固定状态，而不是动态变化的当前状态
  const updateTimeState = {
    objectives: getObjectives() || [],
    constraints: getConstraints() || [],
    candidateItems: [...(currentPreference.value.candidateItems || [])], // 深拷贝当前状态
    requiredCourses: [...(currentPreference.value.requiredCourses || [])], // 深拷贝当前状态
    updateTimestamp: new Date().toISOString() // 记录更新时间
  };
  const newMessage = {
    id: generateMessageId('preferenceUpdated'), // 添加唯一id
    sender: 'Bot',
    type: 'preferenceUpdated',
    text: '偏好设置已更新',
    content: updateTimeState,
    confirmed: false
  };
  addFindMessage();
  // messages.value.push(newMessage);
};

// 开始求解
const startSolving = async (content, id) => {
  // 根据传入的id，找到对应的message并将其updated设为true
  const msgIndex = messages.value.findIndex(msg => msg.id === id);
  if (msgIndex !== -1) {
    messages.value[msgIndex].updated = true;
  }
  console.log('开始基于当前偏好设置进行求解');
  messages.value.push({
    id: generateMessageId('text'),
    sender: 'You',
    type: 'text',
    text: 'Please help me find solutions that meets the current preferences~'
  })
  
  
  try {
    // 调用求解函数
    await solving();
    console.log('求解已启动');
  } catch (error) {
    console.error('求解过程中出现错误:', error);
  }
};

// 添加toggle操作记录函数
const logToggleAction = (name, msgId) => {
  const actionType = ACTION_TYPES.TOGGLE_CONDITION;
  const isExpanded = isKeyExpanded('problemModel', name, msgId);
  
  logUserAction(actionType, {
    conditionName: name,
    new_state: isExpanded ? 'expand' : 'collapse',
  });
};


</script>

<style scoped>
.key-value-pair {
  margin: 10px 0;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 8px;
}

.key-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.key {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.expression-description {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9em;
  color: #666;
  padding-left: 24px; /* 与 checkbox 对齐 */
  border-bottom: 1px solid #eee;
  padding-bottom: 4px;
}

.value {
  padding: 8px;
  margin-top: 4px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.toggle-icon {
  font-size: 12px;
  color: #666;
  cursor: pointer;
}

.clickable {
  cursor: pointer;
}

.constraint-update-button,
.feature-update-button {
  margin-top: 10px;
  text-align: right;
  
}

.constraint-button,
.feature-button-true,
.feature-button-false {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  background-color: #1a73e8;
}

.feature-button-true {
  background-color: #1a73e8;
  color: white;
}

.feature-button-false {
  background-color: #f44336;
  color: white;
}

.course-item {
  margin-left: 30px;
}

.conditions-list {
  margin: 8px 0;
  padding-left: 20px;
  list-style-type: disc;
}

.conditions-list li {
  margin: 4px 0;
  padding: 4px 8px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  font-size: 13px;
  color: #495057;
}

.conditions-list h6 {
  margin: 8px 0 4px 0;
  color: #1a73e8;
  font-size: 13px;
  font-weight: 600;
}

.update-timestamp {
  font-size: 12px;
  color: #6c757d;
  font-style: italic;
  margin: 4px 0 12px 0;
  text-align: center;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 8px;
}

input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

.course-selection-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 10px 0;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.select-all-container {
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
  margin-bottom: 8px;
}

.select-all-label {
  font-weight: bold;
  color: #333;
  margin-left: 8px;
  cursor: pointer;
}

.courses-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-confirm-button {
  margin-top: 10px;
  text-align: right;
}
.solve-button,
.confirm-button {
  padding: 5px 10px;
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.confirmed-message {
  margin-top: 10px;
  color: #1a73e8;
  font-style: italic;
  margin-left: 10px;
}

/* 偏好设置更新消息样式 */
.preference-update-message {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  margin: 10px 0;
}

.preference-update-message h4 {
  margin: 0 0 12px 0;
  color: #28a745;
  font-size: 16px;
  font-weight: 600;
}

.preference-update-message p {
  margin: 8px 0;
  color: #495057;
  font-size: 14px;
}

.preference-section {
  margin: 12px 0;
  padding: 8px 0;
}

.preference-section h5 {
  margin: 0 0 8px 0;
  color: #1a73e8;
  font-size: 14px;
  font-weight: 600;
}

.preference-list {
  margin: 0;
  padding-left: 20px;
  list-style-type: none;
}

.preference-list li {
  margin: 4px 0;
  padding: 4px 8px;
  background-color: #fff;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  font-size: 13px;
  color: #495057;
}

.preference-actions {
  margin-top: 1px;
  padding-top: 1px;
}

.action-question {
  margin: 0 0 12px 0;
  color: #495057;
  font-weight: 500;
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}



.skip-button {
  background-color: #6c757d;
  color: white;
}

.skip-button:hover {
  background-color: #5a6268;
  transform: translateY(-1px);
}
</style>