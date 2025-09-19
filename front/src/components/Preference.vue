<template>
    <div class="preference-panel">

        <!-- 必修课设置 -->
        <div class="section"  v-if="currentPreference.requiredCourses.length > 0 || getPrioriModifiedCourses().length > 0 || currentPreference.objectives.length > 0 || filteredRegularConstraints.length > 0 || currentPreference.filteredConstraints.length > 0">
            <div class="section-title" v-if="false">
                <i class="section-icon">📚</i>Course Setting
            </div>
            <div class="section-content" v-if="currentPreference && currentPreference.requiredCourses.length>0">
                <span  @click="toggleKey('requiredCourses')" class="clickable">
                    {{ currentPreference.requiredCourses.length }} required courses
                    <span class="toggle-icon">{{ isKeyExpanded('requiredCourses', 'list') ? '▲' : '▼' }}</span>
                </span>
                <div v-if="isKeyExpanded('requiredCourses')">
                    <div v-for="(course, index) in currentPreference.requiredCourses" :key="course" class="course-item">
                        <span class="course-content">{{ index + 1 }}. {{ course }}</span>
                        <button @click="removeRequiredCourse(course)" class="delete-course-btn" title="删除必修课">
                            ×
                        </button>
                    </div>
                </div>
            </div>
            <div class="section-content" v-if="currentPreference && getPrioriModifiedCourses().length > 0">
                <span  @click="toggleKey('coursePriority')" class="clickable">
                    {{ getPrioriModifiedCourses().length }} course priorities
                    <span class="toggle-icon">{{ isKeyExpanded('coursePriority', 'list') ? '▲' : '▼' }}</span>
                </span>
                <div v-if="isKeyExpanded('coursePriority')">
                    <div v-for="(course, index) in getPrioriModifiedCourses()" :key="course" class="course-item">
                        <span class="course-content">{{ index + 1 }}. {{ course['课程名'] }}-({{ course['主讲教师'] }})-({{ course['上课时间'] }}): {{ course.priority }}⭐️</span>
                        <button @click="removeCoursePriority(course)" class="delete-course-btn" title="删除课程优先级">
                            ×
                        </button>
                    </div>
                </div>
            </div>
        
            <div class="section-content">
                <span v-if="currentPreference && (currentPreference.objectives.length > 0 || currentPreference.constraints.length > 0)" @click="toggleKey('constraints', 'section')" class="clickable">
                    {{ currentPreference.constraints.length + currentPreference.objectives.length }} conditions
                    <span class="toggle-icon">{{ isKeyExpanded('constraints', 'section') ? '▲' : '▼' }}</span>
                </span>
                <!-- 目标设置子部分 -->
                <div class="subsection">
                    <div v-if="isKeyExpanded('constraints', 'section') && currentPreference && currentPreference.objectives && currentPreference.objectives.length > 0">
                        <div
                            v-for="objective in currentPreference.objectives"
                            :key="objective.name"
                            class="key-value-pair"
                        >
                            <div class="key filter-key">
                                <span class="key-text">{{ getPrefObjectiveKey(objective) }}</span>
                                
                                <span class="toggle-controls">
                                    
                                    <button @click="setWeight(objective)" class="weight-button" title="设置权重">
                                        ⚖️
                                    </button>
                                    <span class="toggle-icon" @click="toggleKey('objectives', objective.name); logToggleAction(objective.name)">
                                        {{ isKeyExpanded('objectives', objective.name) ? '▲' : '▼' }}
                                    </span>
                                    <button @click="handleObjectiveChange(objective)" class="delete-objective-btn" title="删除目标">
                                        ×
                                    </button>
                                </span>
                            </div>
                            <div class="value" v-if="isKeyExpanded('objectives', objective.name)">
                                <div v-html="getMathExpression(objective)"/>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- 约束设置子部分 -->
                <div class="subsection">
                    <div v-if="isKeyExpanded('constraints', 'section') && ((currentPreference && filteredRegularConstraints && filteredRegularConstraints.length > 0) || currentPreference.filteredConstraints.length > 0)">
                        <div
                            v-for="constraint in filteredRegularConstraints"
                            :key="constraint.name"
                            class="key-value-pair"
                        >
                            <div class="key filter-key">
                                
                                <!-- 对于不包含"选择课程"的约束，显示可编辑字段 -->
                                <div v-if="!constraint.name.includes('选择课程')" class="constraint-display-container">
                                    <!-- 默认显示的约束描述 -->
                                    <span class="constraint-description">{{ constraint.name }} {{ getDisplayConstraintType(constraint) }} {{ getDisplayRhs(constraint) }}</span>
                                    
                                    <!-- hover时显示的可编辑字段 -->
                                    <div class="constraint-edit-fields">
                                        <span class="constraint-name">{{ constraint.name.length > 30 ? constraint.name.slice(0, 30) + '…' : constraint.name }}</span>
                                        <div class="constraint-controls">
                                            <select 
                                                :value="getDisplayConstraintType(constraint)" 
                                                @change="handleConstraintValueChange(constraint, 'constraint_type', $event.target.value)"
                                                class="constraint-type-select"
                                                @click.stop
                                            >
                                                <option value="<=">≤</option>
                                                <option value=">=">≥</option>
                                                <option value="=">=</option>
                                            </select>
                                            <input 
                                                type="number" 
                                                :value="getDisplayRhs(constraint)" 
                                                @input="handleConstraintValueChange(constraint, 'rhs', $event.target.value)"
                                                @click.stop 
                                                class="constraint-rhs-input"
                                            />
                                        </div>
                                    </div>
                                </div>
                                <!-- 对于包含"选择课程"的约束，显示原有的key-text -->
                                <span v-else class="key-text">{{ getPrefConstraintKey(constraint) }}</span>
                                <span class="toggle-controls">
                                    <span class="toggle-icon" @click="toggleKey('constraints', constraint.name); logToggleAction(constraint.name)">
                                    {{ isKeyExpanded('constraints', constraint.name) ? '▲' : '▼' }}
                                    </span>
                                    <button @click="handleConstraintChange(constraint)" class="delete-constraint-btn" title="删除约束">×</button>
                                </span>
                            </div>
                            <div class="value" v-if="isKeyExpanded('constraints', constraint.name)">
                                <div v-html="getMathExpression(constraint)"/>
                            </div>
                        </div>
                        <div
                            v-for="constraint in currentPreference.filteredConstraints"
                            :key="constraint.name"
                            class="key-value-pair"
                        >
                            <div class="key filter-key">
                                <!-- 对于filteredConstraints，显示统一的hover编辑界面 -->
                                <div class="constraint-display-container">
                                    <!-- 默认显示的约束描述 -->
                                    <span class="constraint-description">{{ getFilteredConstraintKey(constraint) }}</span>
                                    
                                    <!-- hover时显示的可编辑字段（如果applicable） -->
                                    <div v-if="constraint.filter_type === 'feature'" class="constraint-edit-fields">
                                        <span class="constraint-name">{{ constraint.name }}</span>
                                        <div class="constraint-controls">
                                            <select 
                                                v-model="constraint.constraint_type" 
                                                @change="handleFilteredConstraintValueChange(constraint, 'constraint_type')"
                                                class="constraint-type-select"
                                                @click.stop
                                            >
                                                <option value="<=">≤</option>
                                                <option value=">=">≥</option>
                                                <option value="=">=</option>
                                            </select>
                                            <input 
                                                type="number" 
                                                v-model="constraint.rhs" 
                                                @input="handleFilteredConstraintValueChange(constraint, 'rhs')"
                                                @click.stop 
                                                class="constraint-rhs-input"
                                            />
                                        </div>
                                    </div>
                                    <!-- 对于选择课程类型的filteredConstraints，只显示描述 -->
                                    <div v-else class="constraint-edit-fields">
                                        <span class="constraint-name">{{ getFilteredConstraintKey(constraint) }}</span>
                                    </div>
                                </div>
                                
                                <span class="toggle-controls">
                                    <span class="toggle-icon" @click="toggleKey('filteredConstraints', constraint.name); logToggleAction(constraint.name)">
                                    {{ isKeyExpanded('filteredConstraints', constraint.name) ? '▲' : '▼' }}
                                    </span>
                                    <button @click="toggleConstraint(constraint)" class="delete-constraint-btn" title="删除约束">×</button>
                                </span>
                            </div>
                            <div class="value" v-if="isKeyExpanded('filteredConstraints', constraint.name)">
                                <div v-html="getMathExpression(constraint)"/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 求解结果 -->
        <div class="section result-section" v-if="false">
            <div class="section-title clickable" @click="toggleKey('results', 'section')">
                <i class="section-icon">📊</i>Results
                <span class="toggle-icon">{{ isKeyExpanded('results', 'section') ? '▲' : '▼' }}</span>
            </div>
            <div v-if="isKeyExpanded('results', 'section')" class="solution-count">
                <span v-html="formattedDescription(currentPreference)"></span>
            </div>
        </div>

        <!-- 操作按钮 -->
        <div class="button-container">
            <button @click="solving" class="action-button solve-button">
                <!-- <img src="../assets/solve.svg" alt="solve" class="button-icon" /> -->
                <span>🔍  Find Solutions</span>
            </button>
        </div>
    </div>
</template>

<script setup>
import { isKeyExpanded, toggleKey, getConstraintKey, getConstraintValue, getObjectiveKey, getObjectiveValue, getFilteredConstraintKey, getMathExpression, getPrefObjectiveKey, getPrefConstraintKey, expandedKeys } from '../logic/keyService';
import { currentPreference, getPrioriModifiedCourses } from '../logic/preferenceService';
import { formattedDescription, getFeatureDisplay, solving } from '../logic/modelNodeService';
import { confirmSolution, applyFilter, filters } from '../logic/solutionService';
import { toggleConstraint, handleObjectiveChange, handleConstraintChange } from '../logic/modifiedPanelService';
import { logUserAction, ACTION_TYPES } from '../logic/userActionLogService';
import { computed, onMounted } from 'vue';
import { addUserMessage } from '../logic/messageService';

// 设置默认展开状态
onMounted(() => {
  // 默认展开objectives、constraints和results这三个section
  expandedKeys.value.add('objectives-section');
  expandedKeys.value.add('constraints-section');
  expandedKeys.value.add('results-section');
});

const logToggleAction = (name) => {
  logUserAction(ACTION_TYPES.TOGGLE_CONDITION, {
    conditionName: name,
    new_state: isKeyExpanded('objectives', name) || isKeyExpanded('constraints', name) || isKeyExpanded('filteredConstraints', name) ? 'expand' : 'collapse',
  });
};

// 计算属性：过滤掉已存在于filteredConstraints中的约束
const filteredRegularConstraints = computed(() => {
  if (!currentPreference.value || !currentPreference.value.constraints) {
    return [];
  }
  
  // 获取filteredConstraints中所有的name
  const filteredConstraintNames = currentPreference.value.filteredConstraints.map(fc => fc.name);
  
  // 过滤掉已存在于filteredConstraints中的约束
  return currentPreference.value.constraints.filter(constraint => 
    !filteredConstraintNames.includes(constraint.name)
  );
});

// 删除课程优先级的方法
const removeCoursePriority = (course) => {
    course.priority = 3;
    course.priority_type = 'default';
    updatePreferenceCoursesChange(course, 'rating', { rating: 3 });
    logUserAction(ACTION_TYPES.REMOVE_COURSE_PRIORITY, {
      course: course,
    });
  };

// 删除必修课程的方法
const removeRequiredCourse = (course) => {
  // 显示确认对话框
  if (confirm(`确定要删除必修课程"${course}"吗？删除后该课程将不再作为必修课要求。`)) {
    // 从 currentPreference.requiredCourses 中移除指定课程
    const index = currentPreference.value.requiredCourses.indexOf(course);
    if (index > -1) {
      currentPreference.value.requiredCourses.splice(index, 1);
      
      // 记录用户删除必修课程的操作
      logUserAction(ACTION_TYPES.REMOVE_REQUIRED_COURSE, {
        course: course,
      });
      addUserMessage(`Delete required course: ${course}`);
      console.log(`已删除必修课程: ${course}，剩余必修课程数量: ${currentPreference.value.requiredCourses.length}`);
    }
  }
};

// 设置权重的方法
const setWeight = (objective) => {
  const currentWeight = objective.weight || 1;
  const newWeight = prompt(`请输入 "${getPrefObjectiveKey(objective)}" 的权重（当前权重：${currentWeight}）:`, currentWeight);
  
  if (newWeight !== null && !isNaN(newWeight) && newWeight > 0) {
    objective.weight = parseFloat(newWeight);
    
    // 记录用户设置权重的操作
    logUserAction(ACTION_TYPES.SET_OBJECTIVE_WEIGHT, {
      objective: objective.name,
      weight: objective.weight
    });
    addUserMessage(`Update objective ${objective.name} weight to: ${objective.weight}`);
    console.log(`已设置目标 ${objective.name} 的权重为: ${objective.weight}`);

  } else if (newWeight !== null) {
    alert('请输入有效的正数权重！');
  }
};

// 处理约束值变更的方法
const handleConstraintValueChange = (constraint, fieldType, newValue) => {
  // 记录约束变更操作
  logUserAction(ACTION_TYPES.MODIFY_CONSTRAINT, {
    constraint_name: constraint.name,
    fieldType: fieldType,
    newValue: newValue
  });
  
  // 触发重新求解或更新相关逻辑
  console.log(`约束 ${constraint.name} 的 ${fieldType} 已更新为: ${newValue}`);
  addUserMessage(`Update ${fieldType} of constraint ${constraint.name} to: ${newValue}`);
  
  // 将约束映射到筛选条件（不修改原constraint）
  const constraintTypeToOperation = {
    '<=': 'lessThanOrEqual',
    '>=': 'greaterThanOrEqual', 
    '=': 'equal'
  };
  
  // 获取特征名（约束的name字段）
  const featureName = constraint.name;
  
  // 获取当前的约束类型和值（优先从filters中获取，否则从原constraint获取）
  const currentConstraintType = getDisplayConstraintType(constraint);
  const currentRhs = getDisplayRhs(constraint);
  
  // 创建或更新对应的筛选条件 
  if (!filters.value[featureName]) {
    // 创建新的筛选条件
    filters.value[featureName] = {
      operation: fieldType === 'constraint_type' ? 
        constraintTypeToOperation[newValue] : 
        constraintTypeToOperation[currentConstraintType] || 'equal',
      value: fieldType === 'rhs' ? newValue : currentRhs
    };
  } else {
    // 更新现有的筛选条件
    if (fieldType === 'constraint_type') {
      filters.value[featureName].operation = constraintTypeToOperation[newValue] || 'equal';
    } else if (fieldType === 'rhs') {
      filters.value[featureName].value = newValue;
    }
  }
  
  console.log(`已将约束映射到筛选条件: ${featureName} ${filters.value[featureName].operation} ${filters.value[featureName].value}`);
  // 立即应用筛选条件
  applyFilter();
};

// 处理filteredConstraints的值变更方法
const handleFilteredConstraintValueChange = (constraint, fieldType) => {
  // 记录约束变更操作
  logUserAction(ACTION_TYPES.MODIFY_CONSTRAINT, {
    constraint_name: constraint.name,
    fieldType: fieldType,
    newValue: fieldType === 'constraint_type' ? constraint.constraint_type : constraint.rhs
  });

  // 触发重新求解或更新相关逻辑
  console.log(`筛选约束 ${constraint.name} 的 ${fieldType} 已更新为: ${fieldType === 'constraint_type' ? constraint.constraint_type : constraint.rhs}`);

  // 将约束映射到筛选条件
  const constraintTypeToOperation = {
    '<=': 'lessThanOrEqual',
    '>=': 'greaterThanOrEqual', 
    '=': 'equal'
  };

  // 获取特征名（约束的name字段）
  const featureName = constraint.name;

  // 直接更新筛选条件（filteredConstraint本身就是基于filters生成的）
  if (!filters.value[featureName]) {
    filters.value[featureName] = {
      operation: constraintTypeToOperation[constraint.constraint_type] || 'equal',
      value: constraint.rhs
    };
  } else {
    // 更新现有的筛选条件
    if (fieldType === 'constraint_type') {
      filters.value[featureName].operation = constraintTypeToOperation[constraint.constraint_type] || 'equal';
    } else if (fieldType === 'rhs') {
      filters.value[featureName].value = constraint.rhs;
    }
  }

  console.log(`已将筛选约束映射到筛选条件: ${featureName} ${filters.value[featureName].operation} ${filters.value[featureName].value}`);

  // 立即应用筛选条件
  applyFilter();
};

// 获取约束应该显示的constraint_type（优先显示filteredConstraint中的值）
const getDisplayConstraintType = (constraint) => {
  const featureName = constraint.name;
  if (filters.value[featureName]) {
    // 从operation反推constraint_type
    const operationToConstraintType = {
      'lessThanOrEqual': '<=',
      'greaterThanOrEqual': '>=',
      'equal': '='
    };
    return operationToConstraintType[filters.value[featureName].operation] || constraint.constraint_type;
  }
  const map = {
    '==': '=',
  }
  return map[constraint.constraint_type] || constraint.constraint_type;
};

// 获取约束应该显示的rhs值（优先显示filteredConstraint中的值）
const getDisplayRhs = (constraint) => {
  const featureName = constraint.name;
  if (filters.value[featureName]) {
    return filters.value[featureName].value;
  }
  return constraint.rhs;
};
</script>

<style scoped>
.preference-panel {
    padding: 5px;
    border: 1px solid #eee;
    background-color: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    /* margin-bottom: 20px; */
}

.panel-header {
    margin-bottom: 20px;
    text-align: center;
}

.panel-header h2 {
    color: #4a6fa5;
    margin-bottom: 8px;
    font-size: 1.5rem;
}

.panel-description {
    color: #666;
    font-size: 0.9rem;
}

.section {
    margin-bottom: 6px;
    border-radius: 6px;
    overflow: hidden;
    background-color: #f9f9f9;
    border: 1px solid #eee;
}

.section-title {
    font-weight: bold;
    color: #4a6fa5;
    padding: 5px 15px;
    background-color: #f0f7ff;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    align-items: center;
}

.section-icon {
    margin-right: 8px;
    font-style: normal;
}

.modified-title {
    background-color: #f0f7ff;
    color: #1a73e8;
}

.section-content {
    padding: 6px;
}

.subsection {
    margin-bottom: 0px;
}

.subsection:last-child {
    margin-bottom: 0;
}

.subsection-title {
    font-weight: 600;
    color: #4a6fa5;
    font-size: 0.8rem;
    background-color: #f8f9fa;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    transition: all 0.2s ease;
}

.subsection-title.clickable {
    cursor: pointer;
}

.subsection-title.clickable:hover {
    background-color: #e6f0ff;
    color: #1a73e8;
}

.subsection-title .toggle-icon {
    font-size: 12px;
    transition: transform 0.2s ease;
}

.empty-message {
    color: #999;
    font-style: italic;
    padding: 10px 0;
    text-align: center;
}

.clickable {
    cursor: pointer;
    color: #4a6fa5;
    font-weight: bold;
    display: block;
    margin: 5px 0;
    transition: color 0.2s;
}

.clickable:hover {
    color: #1a73e8;
}

.toggle-icon {
    margin-left: 5px;
    font-size: 0.8em;
}

.key-value-pair {
    margin: 1px 0;
    padding-bottom: 0px;
}

.key-value-pair:last-child {
    border-bottom: none;
}

.key {
    display: flex;
    align-items: center;
    font-weight: 500;
    padding: 5px 0;
}

.filter-key {
    cursor: default;
    padding: 8px 12px;
    border-radius: 4px;
    background-color: #f0f7ff;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px; /* 固定高度，包含padding */
    box-sizing: border-box; /* 确保padding包含在高度内 */
}

.filter-key:hover {
    background-color: #e0f0ff;
}

.filter-checkbox {
    margin-right: 10px;
}

.filter-text {
    flex: 1;
    color: #1a73e8;
}

.key-text {
    color: #1a73e8;
    text-align: left;
    flex: 1;
    font-weight: 500;
}

.weight-button {
    background-color: #f0f7ff;
    border: none;
    color: #1a73e8;
    border-radius: 4px;
    padding: 0px 0px;
    margin: 0 0px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s ease;
    height: 28px;
    min-width: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.weight-button:hover {
    background-color: #e0f0ff;
    border-color: #0d62d0;
    color: #0d62d0;
}

.toggle-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
}

/* 统一hover效果：hover到整个key-value-pair时同时显示编辑字段和toggle-controls */
.key-value-pair:hover .toggle-controls {
    opacity: 1;
    visibility: visible;
    /* 保持margin-left: auto，让按钮保持在右侧 */
}

.key-value-pair:hover .constraint-edit-fields {
    margin-left: 0px;
    opacity: 1;
    visibility: visible;
}

.key-value-pair:hover .constraint-description {
    opacity: 0;
    visibility: hidden;
}

.toggle-icon {
    cursor: pointer;
    font-size: 14px;
    color: #666;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.2s ease;
}

.toggle-icon:hover {
    background-color: #f0f0f0;
    color: #1a73e8;
}

.delete-objective-btn, .delete-constraint-btn {
    background-color: #ff4d4f;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    opacity: 0.8;
}

.delete-objective-btn:hover {
    background-color: #ff7875;
    opacity: 1;
    box-shadow: 0 2px 4px rgba(255, 77, 79, 0.3);
}

.delete-objective-btn:active {
    /* 移除active状态的缩小效果 */
}

.value {
    margin-top: 4px;
    margin-left: 28px;
    color: #666;
    font-size: 0.9em;
    background-color: #f5f5f5;
    padding: 8px;
    border-radius: 4px;
}

.course-item {
    padding: 8px 10px;
    margin: 5px 0;
    background-color: #f5f5f5;
    border-radius: 4px;
    border-left: 3px solid #4a6fa5;
    display: flex; /* Added for delete button alignment */
    align-items: center; /* Added for delete button alignment */
    transition: all 0.2s ease; /* Add smooth transition */
}

.course-item:hover {
    background-color: #eef4ff; /* Light blue background on hover */
    border-left-color: #1a73e8; /* Change border color on hover */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Add subtle shadow */
}

.course-item:hover .delete-course-btn {
    opacity: 1; /* Show delete button more prominently on course item hover */
}

.course-content {
    flex: 1; /* Allow content to take available space */
    margin-right: 10px; /* Space between content and button */
}

.delete-course-btn {
    background-color: #ff4d4f; /* Red color for delete button */
    color: white;
    border: none;
    border-radius: 50%; /* Make it a circle */
    width: 24px;
    height: 24px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    flex-shrink: 0; /* Prevent shrinking */
    opacity: 0.8; /* Slightly transparent by default */
}

.delete-course-btn:hover {
    background-color: #ff7875; /* Darker red on hover */
    opacity: 1; /* Full opacity on hover */
    box-shadow: 0 2px 4px rgba(255, 77, 79, 0.3); /* Add shadow on hover */
}

.result-section {
    background-color: #f0f7ff;
}

.solution-count {
    padding: 15px;
    background-color: #fff;
    border-radius: 5px;
    border-left: 4px solid #4a6fa5;
    margin: 10px;
    font-size: 0.9rem;
}

.button-container {
    display: flex;
    justify-content: center;
    margin-top: 5px;
}


.save-button {
    background-color: #4a6fa5;
}

.solve-button {
    background-color: #1a73e8;
    max-width: 200px;
}

.solve-button:hover {
    background-color: #0d62d0;
}

.action-button {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: flex-start; /* 改为左对齐 */
    padding: 12px 15px;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    transition: all 0.2s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    position: relative; /* 添加相对定位 */
    height: 27px;
}

.button-icon {
    width: 20px;
    height: 20px;
    margin-right: 10px; 
    margin-left: 50px; /* 移除左边距 */
}

.action-button span {
    position: absolute; /* 绝对定位 */
    left: 0;
    right: 0;
    text-align: center; /* 文本居中 */
    margin-left: 0px;   
}

.action-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.constraint-display-container {
    display: flex;
    align-items: center;
    /* 移除justify-content设置，让它自然填充空间 */
    gap: 10px;
    /* 移除 margin-left，让内容从最左边开始 */
    position: relative;
    height: 38px; /* 与filter-key的56px配合 */
    overflow: hidden; /* 防止内容溢出 */
    flex: 1; /* 占据可用空间 */
}

.constraint-description {
    /* 占据可用空间并左对齐 */
    font-weight: 500;
    color: #1a73e8;
    transition: opacity 0.2s ease;
    text-align: left; /* 确保文本左对齐 */
    width: 100%; /* 确保占据整个容器宽度 */
}

/* 默认隐藏编辑字段 */
.constraint-edit-fields {
    display: flex;
    align-items: center;
    justify-content: flex-start; /* 编辑字段内部向左对齐 */
    gap: 10px;
    opacity: 0;
    visibility: hidden;
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    transition: opacity 0.2s ease, visibility 0.2s ease;
}

/* hover时显示编辑字段，隐藏描述 */
.constraint-display-container:hover .constraint-description {
    opacity: 0;
    visibility: hidden;
}

.constraint-display-container:hover .constraint-edit-fields {
    opacity: 1;
    visibility: visible;
}

.constraint-name {
    /* 移除flex: 1，让它只占据需要的空间 */
    font-weight: 500;
    color: #1a73e8;
    text-align: left; /* 确保约束名称左对齐 */
    white-space: nowrap; /* 防止约束名称换行 */
}

.constraint-controls {
    display: flex;
    align-items: center;
    justify-content: flex-start; /* 确保控件向左对齐 */
    gap: 8px;
    /* 不设置margin-left: auto，让它紧跟在constraint-name后面 */
}

.constraint-type-select,
.constraint-rhs-input {
    padding: 6px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.9em;
    color: #333;
    background-color: #fff;
    min-width: 60px;
    text-align: left; /* 改为左对齐 */
}

.constraint-type-select:focus,
.constraint-rhs-input:focus {
    outline: none;
    border-color: #1a73e8;
}

.constraint-type-select {
    cursor: pointer;
}

.constraint-rhs-input {
    width: 60px;
    cursor: text;
}

</style>