<template>
    <div v-if="show" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Add Courses</h3>
          <div class="search-box">
              <input 
                v-model="searchCourseQuery" 
                type="text" 
                placeholder="Enter the course name to search"
              />
            </div>
            <div class="search-box">
              <input 
                v-model="taskIdQuery" 
                type="number" 
                placeholder="Enter the task id"
              />
            </div>
            <div class="search-box" v-if="false">
              <input 
                type="text" 
                placeholder="Enter the lecturer to search"
              />
            </div>
            <div class="search-box" v-if="false">
              <input 
                v-model="searchDepartmentQuery" 
                type="text" 
                placeholder="Enter the department to search"
              />
            </div>
          <button @click="onClose" class="close-button">×</button>
        </div>
        
        <div class="modal-body">
          <div class="favorites">
            <div class="favorites-tables">
              <div class="table-container all-projects">
                <h3>Database</h3>
                <div class="grouped-table">
                  <div class="select-all-header">
                    <input 
                      type="checkbox" 
                      :checked="isAllDatabaseSelected" 
                      :indeterminate.prop="isDatabasePartiallySelected"
                      @change="toggleSelectAllDatabase"
                    />
                    <span>全选 【{{ totalDatabaseItems }}】</span>
                  </div>
                  <div v-for="(group, courseName) in groupedDatabaseCourses" :key="courseName" class="course-group" >
                    <div class="course-group-header" >
                      <input 
                        type="checkbox" 
                        :checked="isDatabaseGroupSelected(courseName)" 
                        :indeterminate.prop="isDatabaseGroupPartiallySelected(courseName)"
                        @click.stop
                        @change="toggleDatabaseGroupSelection(courseName)"
                      />
                      <span class="course-name">{{ courseName }} 【{{ group.length }}】</span>
                      <span class="expand-icon" @click="toggleDatabaseGroup(courseName)">{{ expandedDatabaseGroups[courseName] ? '▼' : '▶' }}</span>
                    </div>
                    <div v-if="expandedDatabaseGroups[courseName]" class="course-group-content">
                      <table>
                        <thead>
                          <tr>
                            <th>选择</th>
                            <th v-for="(header, index) in headers" :key="index">{{ header }}</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(item, index) in group" :key="index">
                            <td>
                              <input type="checkbox" v-model="item.selected" />
                            </td>
                            <td v-for="(header, idx) in headers" :key="idx">
                              {{ item[header] }}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>

              <div class="table-container selected-projects">
                <h3>Candidate Courses</h3>
                <div class="grouped-table">
                  <div v-for="(group, courseName) in groupedCandidateCourses" :key="courseName" class="course-group">
                    <div class="course-group-header" >
                      <input 
                        type="checkbox" 
                        :checked="isCandidateGroupSelected(courseName)" 
                        :indeterminate.prop="isCandidateGroupPartiallySelected(courseName)"
                        @click.stop
                        @change="toggleCandidateGroupSelection(courseName)"
                      />
                      <span class="course-name">{{ courseName }} 【{{ group.length }}】</span>
                      <span class="expand-icon" @click="toggleCandidateGroup(courseName)">{{ expandedCandidateGroups[courseName] ? '▼' : '▶' }}</span>
                    </div>
                    <div v-if="expandedCandidateGroups[courseName]" class="course-group-content">
                      <table>
                        <thead>
                          <tr>
                            <th>选择</th>
                            <th v-for="(header, index) in headers" :key="index">{{ header }}</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(item, index) in group" :key="index">
                            <td>
                              <input type="checkbox" v-model="item.selected" />
                            </td>
                            <td v-for="(header, idx) in headers" :key="idx">
                              {{ item[header] }}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="action-button-group">
              <button @click="addToCandidates" :disabled="!canAddToCandidates" class="move-right-btn">
                add
              </button>
              <button @click="removeFromCandidates" :disabled="!canRemoveFromCandidates" class="move-back-btn">
                delete
              </button>
            </div>
          </div>
        </div>
  
        <div class="modal-footer">
          <button @click="onClose" class="cancel-btn">取消</button>
          <button @click="onConfirm" class="confirm-btn">确认</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { headers, searchCourseQuery, searchDepartmentQuery, filteredDatabase } from '../logic/fileService.js';
  import { allSelected, someSelected, toggleSelectAll, allCandidateSelected, someCandidateSelected, tempCandidateItems, items } from '../logic/coursesService.js';
  import { currentPreference } from '../logic/preferenceService.js';

  // 定义props
  const props = defineProps({
    show: {
      type: Boolean,
      required: true
    },
    currentCandidateItems: {
      type: Array,
      default: () => []
    }
  });
  
  // 定义emit
  const emit = defineEmits(['close', 'confirm']);
  
  // 展开状态管理
  const expandedDatabaseGroups = ref({});
  const expandedCandidateGroups = ref({});

  // Task ID 查询
  const taskIdQuery = ref('');

  // Task ID 到课程列表的映射
  const taskIdCourseMapping = {
    0: [
      '微积分A(2)', '面向对象程序设计基础', '大学化学A', '大学化学B'
    ],
    1: [
      '微积分A(2)', '多元微积分', '商务数据分析', '概率论与数理统计', 
      '概率论与数理统计(社科类)', '区块链技术金融应用', '计量经济学(1)', 
      '财务报表分析', '深度学习及金融数据分析', '英语阅读写作(A)',
      '毛泽东思想和中国特色社会主义理论体系概论', '一年级男生体育(2)', 
      '中国文明', '中国古代文明', '中国哲学(2)', '经典与想象：中国古代传说新读', 
      '《孟子》研读'
    ],
    2: [
      '微积分B(2)', '大学物理B(1)', '面向对象程序设计基础', '计算机程序设计基础', 
      '计算机程序设计基础(2)', '数字逻辑电路', '数字逻辑设计', '英语阅读写作(B)', 
      '中国近现代史纲要', '一年级女生体育(2)', '人机交互', '心智'
    ],
    3: [
      '物理化学(2)', '反应工程基础', '生物化学基础实验', '大学化学A', '大学化学B', 
      '概率论与数理统计', '概率论与随机过程', '概率论与随机过程(1)', 
      '英语听说交流(B)', '中国马克思主义与当代', '二年级男生篮球', '人工智能基础'
    ],
    4: [
      '微积分B(2)', '大学物理B(1)', '面向对象程序设计基础', '计算机程序设计基础', 
      '计算机程序设计基础(2)', '数字逻辑电路', '数字逻辑设计', '英语阅读写作(B)', 
      '中国近现代史纲要', '一年级女生体育(2)', '人机交互', '心智',
      '学术探知', '中国传统雕塑彩塑', '自然辩证法概论', 
      '区块链技术金融应用', '计量经济学(1)', 
      '财务报表分析', '深度学习及金融数据分析',
    ]
  };

  // 根据task id筛选课程的计算属性
  const filteredDatabaseByTaskId = computed(() => {
    if (!taskIdCourseMapping[parseInt(taskIdQuery.value)]) {
      return filteredDatabase.value;
    }
    
    const allowedCourses = taskIdCourseMapping[parseInt(taskIdQuery.value)];
    // 先筛选出包含在allowedCourses中的课程
    const filtered = filteredDatabase.value.filter(course => {
      const courseName = course['课程名'] || course.courseName || '';
      // 只要课程名中包含任一关键词即可
      return allowedCourses.some(keyword => courseName.includes(keyword));
    });
    // 按照allowedCourses中的顺序排序
    return filtered.sort((a, b) => {
      const nameA = a['课程名'] || a.courseName || '';
      const nameB = b['课程名'] || b.courseName || '';
      // 找到allowedCourses中第一个匹配的索引
      const idxA = allowedCourses.findIndex(keyword => nameA.includes(keyword));
      const idxB = allowedCourses.findIndex(keyword => nameB.includes(keyword));
      return idxA - idxB;
    });
  });

  // 按课程名分组的计算属性
  const groupedDatabaseCourses = computed(() => {
    const groups = {};
    filteredDatabaseByTaskId.value.forEach(course => {
      const courseName = course['课程名'] || course.courseName || 'Unknown';
      if (!groups[courseName]) {
        groups[courseName] = [];
      }
      course.selected = false;
      groups[courseName].push(course);
    });
    return groups;
  });

  const groupedCandidateCourses = computed(() => {
    const groups = {};
    tempCandidateItems.value.forEach(course => {
      const courseName = course['课程名'] || course.courseName || 'Unknown';
      if (!groups[courseName]) {
        groups[courseName] = [];
      }
      groups[courseName].push(course);
    });
    return groups;
  });

  // 展开/收起分组
  const toggleDatabaseGroup = (courseName) => {
    expandedDatabaseGroups.value[courseName] = !expandedDatabaseGroups.value[courseName];
  };

  const toggleCandidateGroup = (courseName) => {
    expandedCandidateGroups.value[courseName] = !expandedCandidateGroups.value[courseName];
  };

  // 分组选择逻辑
  const isDatabaseGroupSelected = (courseName) => {
    const group = groupedDatabaseCourses.value[courseName];
    return group && group.length > 0 && group.every(item => item.selected);
  };

  const isDatabaseGroupPartiallySelected = (courseName) => {
    const group = groupedDatabaseCourses.value[courseName];
    if (!group || group.length === 0) return false;
    const selectedCount = group.filter(item => item.selected).length;
    return selectedCount > 0 && selectedCount < group.length;
  };

  const toggleDatabaseGroupSelection = (courseName) => {
    const group = groupedDatabaseCourses.value[courseName];
    if (!group) return;
    
    const allSelected = group.every(item => item.selected);
    group.forEach(item => {
      item.selected = !allSelected;
    });
  };

  const isCandidateGroupSelected = (courseName) => {
    const group = groupedCandidateCourses.value[courseName];
    return group && group.length > 0 && group.every(item => item.selected);
  };

  const isCandidateGroupPartiallySelected = (courseName) => {
    const group = groupedCandidateCourses.value[courseName];
    if (!group || group.length === 0) return false;
    const selectedCount = group.filter(item => item.selected).length;
    return selectedCount > 0 && selectedCount < group.length;
  };

  const toggleCandidateGroupSelection = (courseName) => {
    const group = groupedCandidateCourses.value[courseName];
    if (!group) return;
    
    const allSelected = group.every(item => item.selected);
    group.forEach(item => {
      item.selected = !allSelected;
    });
  };

  // 根据batch计算priority的函数
  const calculatePriorityFromBatch = (batch) => {
    // return Math.max(1, 4 - batch);
    return 3;
  };
  
  // 初始化临时候选课程和展开状态
  onMounted(() => {
    tempCandidateItems.value = props.currentCandidateItems.map(item => ({
      ...item,
      // 确保每个item都有priority相关字段
      priority: item.priority || calculatePriorityFromBatch(item.batch || 1),
      priority_type: item.priority_type || 'default'
    }));
    
    // 重置所有原始数据源items中课程的selected状态为false（根本解决方案）
    items.value.forEach(item => {
      item.selected = false;
    });
    
    // 重置所有filteredDatabase中课程的selected状态为false（双重保险）
    filteredDatabase.value.forEach(item => {
      item.selected = false;
    });
    
    // 默认折叠所有分组
    Object.keys(groupedDatabaseCourses.value).forEach(courseName => {
      expandedDatabaseGroups.value[courseName] = false;
    });
    Object.keys(groupedCandidateCourses.value).forEach(courseName => {
      expandedCandidateGroups.value[courseName] = false;
    });
  });
  
  // 关闭弹窗
  const onClose = () => {
    emit('close');
  };
  
  // 确认选择
  const onConfirm = () => {
    // 创建一个副本发送给接收方
    currentPreference.value.candidatesBatch += 1;
    const candidateItemsCopy = [...tempCandidateItems.value];
    // 发出确认事件
    emit('confirm', candidateItemsCopy);
    // 清空搜索查询
    searchDepartmentQuery.value = '';
    searchCourseQuery.value = '';
    taskIdQuery.value = '';
    // 清空临时选择的项目
    tempCandidateItems.value = [];
    // 添加延迟确保数据处理完成后再关闭弹窗
    setTimeout(() => {
      emit('close');
    }, 10);
  };
  
  // 添加到候选课程
  const addToCandidates = () => {
    const itemsToAdd = filteredDatabaseByTaskId.value
      .filter(item => item.selected)
      .map(item => ({
        ...item,
        selected: true,  
        chosen: false,
        added: false,
        userSelected: false,
        chosen_when_confirmed: false,
        batch: currentPreference.value.candidatesBatch,
        priority: calculatePriorityFromBatch(currentPreference.value.candidatesBatch),
        priority_type: 'default',
      }));
    
    // 添加到临时候选课程，避免重复
    itemsToAdd.forEach(item => {
      const exists = tempCandidateItems.value.some(
        existing => existing['课程名'] === item['课程名'] && 
                   existing['主讲教师'] === item['主讲教师'] &&
                   existing['上课时间'] === item['上课时间']
      );
      if (!exists) {
        tempCandidateItems.value.push(item);
      }
    });
    
    // 重置选中状态
    filteredDatabaseByTaskId.value.forEach(item => {
      item.selected = false;
    });
  };
  
  // 从候选课程中移除
  const removeFromCandidates = () => {
    tempCandidateItems.value = tempCandidateItems.value.filter(item => !item.selected);
  };
  
  // 计算是否可以添加到候选课程
  const canAddToCandidates = computed(() => {
    return filteredDatabaseByTaskId.value.some(item => item.selected);
  });
  
  // 计算是否可以从候选课程中移除
  const canRemoveFromCandidates = computed(() => {
    return tempCandidateItems.value.some(item => item.selected);
  });

  // 全选相关的计算属性
  const totalDatabaseItems = computed(() => {
    return filteredDatabaseByTaskId.value.length;
  });

  const isAllDatabaseSelected = computed(() => {
    return totalDatabaseItems.value > 0 && filteredDatabaseByTaskId.value.every(item => item.selected);
  });

  const isDatabasePartiallySelected = computed(() => {
    const selectedCount = filteredDatabaseByTaskId.value.filter(item => item.selected).length;
    return selectedCount > 0 && selectedCount < totalDatabaseItems.value;
  });

  // 全选切换方法
  const toggleSelectAllDatabase = () => {
    const newValue = !isAllDatabaseSelected.value;
    filteredDatabaseByTaskId.value.forEach(item => {
      item.selected = newValue;
    });
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 1200px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
  }
  
  .modal-header {
    padding: 15px 10px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }
  
  .modal-footer {
    padding: 15px 20px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
  
  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
  }
  
  .cancel-btn, .confirm-btn {
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .cancel-btn {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
  }
  
  .confirm-btn {
    background-color: #1976D2;
    color: white;
    border: none;
  }
  
  .search-box {
    margin-bottom: 10px;
  }
  
  .search-box input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .favorites-tables {
    display: flex;
    gap: 20px;
    margin-top: 20px;
  }
  
  .table-container {
    flex: 1;
    overflow: auto;
    max-height: 400px;
  }
  
  .grouped-table {
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .course-group {
    border-bottom: 1px solid #eee;
  }
  
  .course-group:last-child {
    border-bottom: none;
  }
  
  .select-all-header {
    background-color: #e3f2fd;
    padding: 12px 16px;
    border-bottom: 1px solid #dee2e6;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #1976D2;
  }
  
  .course-group-header {
    background-color: #f8f9fa;
    padding: 12px 16px;
    border-bottom: 1px solid #dee2e6;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  
  .course-group-header:hover {
    background-color: #e9ecef;
  }
  
  .expand-icon {
    color: #666;
    font-size: 12px;
    width: 12px;
  }
  
  .course-name {
    color: #333;
  }
  
  .course-group-content {
    background-color: white;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }
  
  th {
    background-color: #f5f5f5;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  .action-button-group {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
  }
  
  .move-right-btn, .move-back-btn {
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .move-right-btn {
    background-color: #4CAF50;
    color: white;
    border: none;
  }
  
  .move-right-btn:disabled {
    background-color: #a5d6a7;
    cursor: not-allowed;
  }
  
  .move-back-btn {
    background-color: #f44336;
    color: white;
    border: none;
  }
  
  .move-back-btn:disabled {
    background-color: #ef9a9a;
    cursor: not-allowed;
  }
  </style>