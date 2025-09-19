// src/logic/scheduleService.js
import { ref, computed, watch } from 'vue';
import { filters, applyFilter, updateCandidateItems } from './solutionService';
import { allCourses } from './coursesService.js';
import { logUserAction, ACTION_TYPES } from './userActionLogService.js';
import { solutionsNum } from './solutionService';
import { currentPreference, updatePreferenceCoursesChange, updatePreferenceDescription } from './preferenceService.js';
import { addUserMessage } from './messageService.js';



export const periods = ref(['Period 1', 'Period 2', 'Period 3', 'Period 4', 'Period 5', 'Period 6']);

// 为每个课程创建显示控制对象
export const courseDisplayControl = ref({});
// 为每个课程创建折叠控制对象
export const courseFoldState = ref({});

// 添加分组显示控制
export const groupDisplayControl = ref({});
// 添加分组折叠控制
export const groupFoldState = ref({});


// 定义显示模式常量
export const DISPLAY_MODES = {
  NONE: 0,
  CHOSEN: 1,     // 只显示已选课程
  IMPORTANT: 2,  // 显示固定和未决定课程
  ALL: 3         // 显示所有课程
};

export const DISPLAY_NAMES = ['none', 'chosen', 'important', 'all'];

export const currentMode = ref(DISPLAY_MODES.ALL);

// 添加一个计算属性来安全访问 courseDisplayControl
export const getCourseDisplayStatus = (courseName) => {
  if (!courseDisplayControl.value[courseName]) {
    courseDisplayControl.value[courseName] = {
      displayMode: DISPLAY_MODES.ALL // 默认显示所有
    };
  }
  return courseDisplayControl.value[courseName].displayMode;
};

// 切换是否只显示选中课程的状态
export const toggleshowAllCourses = (auto = true) => {
  if (auto) {
    // 循环切换显示模式：CHOSEN -> IMPORTANT -> ALL -> NONE -> CHOSEN
    if (currentMode.value === DISPLAY_MODES.CHOSEN) {
      currentMode.value = DISPLAY_MODES.IMPORTANT;
      setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.IMPORTANT);
    } else if (currentMode.value === DISPLAY_MODES.IMPORTANT) {
      currentMode.value = DISPLAY_MODES.ALL;
      setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.ALL);
    } else if (currentMode.value === DISPLAY_MODES.ALL){
      currentMode.value = DISPLAY_MODES.NONE;
      setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.NONE);
    } else if (currentMode.value === DISPLAY_MODES.NONE){
      currentMode.value = DISPLAY_MODES.CHOSEN;
      setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.CHOSEN);
    } else {
      currentMode.value = DISPLAY_MODES.ALL;
      setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.ALL);
    }
  } else {
    // 如果auto为false，直接设置为CHOSEN模式
    currentMode.value = DISPLAY_MODES.CHOSEN;
  }
  try {
    setGlobalDisplayMode(currentMode.value);
    setGlobalVisibility(currentMode.value);
    console.log("toggleshowAllCourses", courseDisplayByKey.value, currentPreference.value.candidateItems);
  } catch (e) {
    console.warn('设置显示模式为 CHOSEN 时出现问题:', e);
  }
  // 打印更新后的状态
  console.log("更新后的显示模式:", currentMode.value);
  console.log("更新后的课程显示控制:", courseDisplayByKey.value);
};

// 直接设置全局显示模式（同时同步所有课程与分组的显示模式，并可选同步所有 slot）
export const setGlobalDisplayMode = (mode) => {
  if (![DISPLAY_MODES.NONE, DISPLAY_MODES.CHOSEN, DISPLAY_MODES.IMPORTANT, DISPLAY_MODES.ALL].includes(mode)) return;
  currentMode.value = mode;
  if (allCourses.value && allCourses.value.size > 0) {
    Array.from(allCourses.value).forEach(courseName => {
      if (!courseDisplayControl.value[courseName]) {
        courseDisplayControl.value[courseName] = {};
      }
      courseDisplayControl.value[courseName].displayMode = mode;
    });
  }
  const groups = getCourseGroups();
  groups.forEach(group => {
    if (!groupDisplayControl.value[group.id]) {
      groupDisplayControl.value[group.id] = {};
    }
    groupDisplayControl.value[group.id].displayMode = mode;
  });
  // 同步所有 slot 的显示模式（与课程/分组一致）
  const slotMap = {
    [DISPLAY_MODES.ALL]: SLOT_DISPLAY_MODES.ALL,
    [DISPLAY_MODES.CHOSEN]: SLOT_DISPLAY_MODES.CHOSEN,
    [DISPLAY_MODES.IMPORTANT]: SLOT_DISPLAY_MODES.IMPORTANT,
    [DISPLAY_MODES.NONE]: SLOT_DISPLAY_MODES.NONE
  };
  setAllSlotDisplayStatus(slotMap[mode]);

  logUserAction(ACTION_TYPES.CHANGE_VIEW_MODE, {
    object: 'global',
    new_state: DISPLAY_NAMES[mode]
  });
};

// 修改切换函数支持三种模式
export const toggleCourseDisplay = (courseName) => {
  // 初始化课程显示控制对象（如果不存在）
  if (!courseDisplayControl.value[courseName]) {
    courseDisplayControl.value[courseName] = {
      displayMode: DISPLAY_MODES.ALL
    };
  }
  
  // 循环切换显示模式： CHOSEN -> IMPORTANT -> ALL -> CHOSEN
  const courseMode = courseDisplayControl.value[courseName].displayMode;
  let nextMode;

if (courseMode === DISPLAY_MODES.CHOSEN) {
    nextMode = DISPLAY_MODES.IMPORTANT;
    setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.IMPORTANT);
  } else if (courseMode === DISPLAY_MODES.IMPORTANT) {
    nextMode = DISPLAY_MODES.ALL;
    setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.ALL);
  } else if (courseMode === DISPLAY_MODES.ALL){
    nextMode = DISPLAY_MODES.NONE;
    setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.NONE);
  } else if (courseMode === DISPLAY_MODES.NONE){
    nextMode = DISPLAY_MODES.CHOSEN;
    setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.CHOSEN);
  } else {
    nextMode = DISPLAY_MODES.ALL;
    setAllSlotDisplayStatus(SLOT_DISPLAY_MODES.ALL);
  }
  
  courseDisplayControl.value[courseName].displayMode = nextMode;

  // 同步可见性映射（按课程名）
  setCourseNameVisibility(courseName, nextMode);
  
  // 记录切换课程显示模式操作 - 使用新的ACTION_TYPE
  logUserAction(ACTION_TYPES.CHANGE_VIEW_MODE, {
    object: courseName,
    new_state: DISPLAY_NAMES[nextMode]
  });
};

// 直接设置某课程的显示模式
export const setCourseDisplayStatus = (courseName, mode) => {
  if (!courseDisplayControl.value[courseName]) {
    courseDisplayControl.value[courseName] = { displayMode: DISPLAY_MODES.ALL };
  }
  courseDisplayControl.value[courseName].displayMode = mode;
  logUserAction(ACTION_TYPES.CHANGE_VIEW_MODE, {
    object: courseName,
    new_state: DISPLAY_NAMES[mode]
  });
};

// 检查是否所有课程都被折叠
export const isAllCoursesFolded = computed(() => {
  return Array.from(allCourses.value).every(courseName => isCourseFolded(courseName));
});



// 检查课程是否被折叠
export const isCourseFolded = (courseName) => {
  if (courseFoldState.value[courseName] === undefined) {
    courseFoldState.value[courseName] = true; // 默认折叠
  }
  return courseFoldState.value[courseName];
};

// 切换课程折叠状态
export const toggleCourseFold = (courseName) => {
  if (courseFoldState.value[courseName] === undefined) {
    courseFoldState.value[courseName] = true;
  }
  courseFoldState.value[courseName] = !courseFoldState.value[courseName];
  
  // 记录切换课程折叠状态操作 - 使用新的ACTION_TYPE
  logUserAction(ACTION_TYPES.EXPAND_COLLAPSE, {
    object: courseName,
    new_state: isCourseFolded(courseName) ? 'collapsed' : 'expanded'
  });
};

// 添加一个函数来切换所有课程的折叠状态
export const toggleAllCoursesFold = () => {
  // 确定当前的整体状态：如果所有课程都已折叠，则展开所有；否则折叠所有
  const shouldExpand = isAllCoursesFolded.value;
  
  // 遍历所有课程并设置折叠状态
  Array.from(allCourses.value).forEach(courseName => {
    courseFoldState.value[courseName] = !shouldExpand;
  });
  
  // 记录切换所有课程折叠状态操作 - 使用新的ACTION_TYPE
  logUserAction(ACTION_TYPES.EXPAND_COLLAPSE, {
    object: 'all',
    new_state: !shouldExpand ? 'collapsed' : 'expanded'
  });
};

// 添加课程分组相关功能
export const getCourseGroups = () => {
  const groups = [];
  const { objectives, constraints } = currentPreference.value;
  
  // 从 objectives 中提取 template_id 为 6 的分组
  if (objectives) {
    objectives.forEach(objective => {
      if (objective.expression && 
          typeof objective.expression === 'object' && 
          (objective.expression.template_id === 6 || objective.expression.template_id === 5)) {
        const parameters = objective.expression.parameters;
        if (parameters && (parameters.keyword_list || parameters.course_list || parameters.keyword)) {
          const keywordList = parameters.keyword_list || parameters.course_list || parameters.keyword;
          groups.push({
            id: `objective_${objective.name}`,
            name: objective.name,
            type: 'objective',
            keywords: keywordList,
            source: 'objective'
          });
        }
      }

    });
  }
  
  // 从 constraints 中提取 template_id 为 6 的分组
  if (constraints) {
    constraints.forEach(constraint => {
      if (constraint.lhs && 
          typeof constraint.lhs === 'object' && 
          (constraint.lhs.template_id === 6 || constraint.lhs.template_id === 5)) {
        const parameters = constraint.lhs.parameters;
        if (parameters && (parameters.keyword_list || parameters.course_name_list || parameters.keyword)) {
          const keywordList = parameters.keyword_list || parameters.course_name_list || parameters.keyword;
          groups.push({
            id: `constraint_${constraint.name}`,
            name: constraint.name,
            type: 'constraint',
            keywords: keywordList,
            source: 'constraint'
          });
        }
      }
    });
  }


  
  return groups;
};

// 检查课程是否属于某个分组
export const getCourseGroup = (courseName) => {
  const groups = getCourseGroups();
  for (const group of groups) {
    for (const keyword of group.keywords) {
      if (courseName.includes(keyword)) {
        return group;
      }
    }
  }
  return null;
};

// 获取分组的课程列表
export const getGroupCourses = (group) => {
  if (!currentPreference.value.candidateItems) return [];
  
  return currentPreference.value.candidateItems.filter(item => {
    const courseName = item['课程名'];
    return group.keywords.some(keyword => courseName.includes(keyword));
  });
};

// 获取分组的显示模式
export const getGroupDisplayStatus = (groupId) => {
  if (!groupDisplayControl.value[groupId]) {
    groupDisplayControl.value[groupId] = {
      displayMode: DISPLAY_MODES.ALL
    };
  }
  return groupDisplayControl.value[groupId].displayMode;
};

// 切换分组显示模式
export const toggleGroupDisplay = (groupId) => {
  if (!groupDisplayControl.value[groupId]) {
    groupDisplayControl.value[groupId] = {
      displayMode: DISPLAY_MODES.ALL
    };
  }
  
  const currentMode = groupDisplayControl.value[groupId].displayMode;
  let nextMode;
  
  if (currentMode === DISPLAY_MODES.CHOSEN) {
    nextMode = DISPLAY_MODES.IMPORTANT;
  } else if (currentMode === DISPLAY_MODES.IMPORTANT) {
    nextMode = DISPLAY_MODES.ALL;
  } else if (currentMode === DISPLAY_MODES.ALL) {
    nextMode = DISPLAY_MODES.CHOSEN;
  } else {
    nextMode = DISPLAY_MODES.ALL;
  }
  
  groupDisplayControl.value[groupId].displayMode = nextMode;
  
  // 找到对应的分组
  const groups = getCourseGroups();
  const group = groups.find(g => g.id === groupId);
  
  if (group) {
    // 获取该分组下的所有课程名称
    const groupCourseNames = [];
    if (allCourses.value && allCourses.value.size > 0) {
      Array.from(allCourses.value).forEach(courseName => {
        if (group.keywords.some(keyword => courseName.includes(keyword))) {
          groupCourseNames.push(courseName);
        }
      });
    }
    
    // 更新该分组下所有课程的显示模式为分组的显示模式
    groupCourseNames.forEach(courseName => {
      if (!courseDisplayControl.value[courseName]) {
        courseDisplayControl.value[courseName] = {};
      }
      courseDisplayControl.value[courseName].displayMode = nextMode;
    });
    
    console.log(`更新分组 ${groupId} 显示模式为: ${nextMode}`);
    console.log(`受影响的课程: ${groupCourseNames.join(', ')}`);
  }
  
  // 同步可见性映射（分组）
  setGroupVisibility(groupId, nextMode);

  logUserAction(ACTION_TYPES.TOGGLE_GROUP_DISPLAY, {
    groupId: groupId,
    displayMode: nextMode
  });
};

// 直接设置分组显示模式（并将分组内课程同步到该模式）
export const setGroupDisplayStatus = (groupId, mode) => {
  if (!groupDisplayControl.value[groupId]) {
    groupDisplayControl.value[groupId] = { displayMode: DISPLAY_MODES.ALL };
  }
  groupDisplayControl.value[groupId].displayMode = mode;

  const groups = getCourseGroups();
  const group = groups.find(g => g.id === groupId);
  if (group) {
    const groupCourseNames = [];
    if (allCourses.value && allCourses.value.size > 0) {
      Array.from(allCourses.value).forEach(courseName => {
        if (group.keywords.some(keyword => courseName.includes(keyword))) {
          groupCourseNames.push(courseName);
        }
      });
    }
    groupCourseNames.forEach(courseName => {
      if (!courseDisplayControl.value[courseName]) {
        courseDisplayControl.value[courseName] = {};
      }
      courseDisplayControl.value[courseName].displayMode = mode;
    });
  }

  logUserAction(ACTION_TYPES.TOGGLE_GROUP_DISPLAY, {
    groupId: groupId,
    displayMode: mode
  });
};

// 检查分组是否被折叠
export const isGroupFolded = (groupId) => {
  if (!groupFoldState.value[groupId]) {
    groupFoldState.value[groupId] = false; // 默认展开
  }
  return groupFoldState.value[groupId];
};

// 切换分组折叠状态
export const toggleGroupFold = (groupId) => {
  if (!groupFoldState.value[groupId]) {
    groupFoldState.value[groupId] = false;
  }
  groupFoldState.value[groupId] = !groupFoldState.value[groupId];
  
  // 记录用户操作
  logUserAction(ACTION_TYPES.TOGGLE_GROUP_FOLD, {
    groupId: groupId,
    isFolded: groupFoldState.value[groupId]
  });
};

// 检查课程是否应该根据分组显示模式显示
export const shouldDisplayCourseInGroup = (course, group) => {
  const groupDisplayMode = getGroupDisplayStatus(group.id);
  
  if (groupDisplayMode === DISPLAY_MODES.ALL) {
    return true;
  } else if (groupDisplayMode === DISPLAY_MODES.CHOSEN) {
    const isDeleted = (currentPreference.value.isIncremental === true) && 
           course.chosen_when_confirmed && 
           !course.chosen;
    return course.chosen || course.userSelected || isDeleted;
  } else if (groupDisplayMode === DISPLAY_MODES.IMPORTANT) {
    const isDeleted = (currentPreference.value.isIncremental === true) && 
           course.chosen_when_confirmed && 
           !course.chosen;
    const courseNum = course.num !== undefined ? course.num : 0;
    const isFixed = (courseNum === solutionsNum.value) && solutionsNum.value > 0;
    const isUndecided = courseNum > 0 && courseNum < solutionsNum.value && solutionsNum.value > 0;
    
    return isFixed || isUndecided || isDeleted;
  }
  return false;
};

// 获取排序后的课程列表（分组课程在前）
export const getSortedCourses = () => {
  if (!allCourses.value) return [];
  
  const groups = getCourseGroups();
  const groupedCourses = new Set();
  const result = [];
  
  // 添加分组课程
  groups.forEach(group => {
    const groupCourses = [];
    // 按照candidateItems的顺序获取分组课程
    if (currentPreference.value.candidateItems) {
      currentPreference.value.candidateItems.forEach(item => {
        const courseName = item['课程名'];
        if (group.keywords.some(keyword => courseName.includes(keyword)) && 
            allCourses.value.has(courseName)) {
          if (!groupCourses.includes(courseName)) {
            groupCourses.push(courseName);
            groupedCourses.add(courseName);
          }
        }
      });
    }
    
    if (groupCourses.length > 0) {
      result.push({
        type: 'group',
        group: group,
        courses: groupCourses
      });
    }
  });
  
  // 添加未分组课程 - 按candidateItems的原始顺序
  if (currentPreference.value.candidateItems) {
    const addedCourses = new Set();
    currentPreference.value.candidateItems.forEach(item => {
      const courseName = item['课程名'];
      if (!groupedCourses.has(courseName) && 
          allCourses.value.has(courseName) && 
          !addedCourses.has(courseName)) {
        result.push({
          type: 'course',
          courseName: courseName
        });
        addedCourses.add(courseName);
      }
    });
  }
  
  return result;
};

// 定义星期映射
const dayMap = {
  '1': 'monday',
  '2': 'tuesday',
  '3': 'wednesday',
  '4': 'thursday',
  '5': 'friday'
};

  // 定义节次映射
const periodMap = {
  '1': 'Period 1',
  '2': 'Period 2',
  '3': 'Period 3',
  '4': 'Period 4',
  '5': 'Period 5',
  '6': 'Period 6'
  };

export const periodTimeMap = {
  'Period 1': '(8:00-9:35)',
  'Period 2': '(9:50-12:15)',
  'Period 3': '(13:30-15:05)',
  'Period 4': '(15:20-16:55)',
  'Period 5': '(17:05-18:40)',
  'Period 6': '(19:20-21:45)'
}
  
// 创建一个 computed 属性来动态生成课程表
export const schedule = computed(() => {
  // 初始化课程表
  const scheduleData = {
    'Period 1': { monday: [], tuesday: [], wednesday: [], thursday: [], friday: [] },
    'Period 2': { monday: [], tuesday: [], wednesday: [], thursday: [], friday: [] },
    'Period 3': { monday: [], tuesday: [], wednesday: [], thursday: [], friday: [] },
    'Period 4': { monday: [], tuesday: [], wednesday: [], thursday: [], friday: [] },
    'Period 5': { monday: [], tuesday: [], wednesday: [], thursday: [], friday: [] },
    'Period 6': { monday: [], tuesday: [], wednesday: [], thursday: [], friday: [] },
  };


  // 遍历 candidateItems，将每个课程安排添加到课程表中
  currentPreference.value.candidateItems.forEach(item => {
    if(item.selected){
      const timeStr = item['上课时间'];
      const timeEntries = timeStr.split(';');

      timeEntries.forEach(timeEntry => {
        const match = timeEntry.match(/(\d+)-(\d+)\((.*?)\)/);
        if (match) {
          const dayNumber = match[1];
          const periodNumber = match[2];

          const dayName = dayMap[dayNumber];
          const periodName = periodMap[periodNumber];

          if (dayName && periodName) {
            // 将课程安排放入对应的时间段和星期
            scheduleData[periodName][dayName].push(item);
          }
        }
      });
    }
  });
  return scheduleData;
  
});

// ========== 基于课程唯一键的 timetable 可见性控制 ==========
// 课程唯一键：课程名-主讲教师-上课时间
export const getCourseKey = (item) => `${item['课程名']}-${item['主讲教师']}-${item['上课时间']}`;

// 映射：key -> boolean（是否在timetable显示）。默认 true
export const courseDisplayByKey = ref({});

export const isCourseVisibleInTimetable = computed(() => {
  // 返回一个函数，接收 item，判断其是否在课表中可见
  return (item) => {
    const key = getCourseKey(item);
    // 优先显示用户手动选中的课程，否则根据 courseDisplayByKey 控制
    return item.userSelected || courseDisplayByKey.value[key];
  };
});


const computeImportantFlags = (item) => {
  const courseNum = item.num !== undefined ? item.num : 0;
  const isFixed = (courseNum === solutionsNum.value) && solutionsNum.value > 0;
  const isUndecided = courseNum > 0 && courseNum < solutionsNum.value && solutionsNum.value > 0;
  return { isFixed, isUndecided };
};

const setVisibilityForItems = (items, mode) => {
  items.forEach(item => {
    const key = getCourseKey(item);
    if (mode === DISPLAY_MODES.ALL) {
      courseDisplayByKey.value[key] = true;
    } else if (mode === DISPLAY_MODES.NONE) {
      courseDisplayByKey.value[key] = false;
    } else if (mode === DISPLAY_MODES.CHOSEN) {
      courseDisplayByKey.value[key] = item.chosen;
    } else if (mode === DISPLAY_MODES.IMPORTANT) {
      const { isFixed, isUndecided } = computeImportantFlags(item);
      courseDisplayByKey.value[key] = isFixed || isUndecided;
    }
  });
};

// 设置全局可见性（所有候选课程）
export const setGlobalVisibility = (mode) => {
  const items = currentPreference.value.candidateItems || [];
  setVisibilityForItems(items, mode);
};

// 设置某课程名下所有条目的可见性
export const setCourseNameVisibility = (courseName, mode) => {
  const items = (currentPreference.value.candidateItems || []).filter(i => i['课程名'] === courseName);
  setVisibilityForItems(items, mode);
};

// 设置分组内所有条目的可见性
export const setGroupVisibility = (groupId, mode) => {
  const groups = getCourseGroups();
  const group = groups.find(g => g.id === groupId);
  if (!group) return;
  const items = (currentPreference.value.candidateItems || []).filter(i => group.keywords.some(k => i['课程名'].includes(k)));
  setVisibilityForItems(items, mode);
};

// 设置某个 slot（period, day）内所有条目的可见性
export const setSlotVisibility = (period, day, mode) => {
  const items = schedule.value?.[period]?.[day] || [];
  // 将 SLOT 映射为 DISPLAY 模式，避免 ALL 与 NONE 数值顺序不一致导致的反转
  const slotToDisplay = (m) => {
    if (m === SLOT_DISPLAY_MODES.ALL) return DISPLAY_MODES.ALL;
    if (m === SLOT_DISPLAY_MODES.CHOSEN) return DISPLAY_MODES.CHOSEN;
    if (m === SLOT_DISPLAY_MODES.IMPORTANT) return DISPLAY_MODES.IMPORTANT;
    return DISPLAY_MODES.NONE;
  };
  setVisibilityForItems(items, slotToDisplay(mode));
};

// ========== Slot 级别显示控制（Period + Day） ==========
// slot 显示模式（与课程显示模式不同，这里只需要 ALL/CHOSEN/UNDECIDED）
export const SLOT_DISPLAY_MODES = {
  ALL: 0,
  CHOSEN: 1,
  IMPORTANT: 2,
  NONE: 3
};

// 存储每个 slot 的显示状态：key 形如 'Period 1#monday'
export const slotDisplayControl = ref({});

const getSlotKey = (period, day) => `${period}#${day}`;

export const getSlotDisplayStatus = (period, day) => {
  const key = getSlotKey(period, day);
  if (!slotDisplayControl.value[key]) {
    slotDisplayControl.value[key] = { displayMode: SLOT_DISPLAY_MODES.CHOSEN };
  }
  return slotDisplayControl.value[key].displayMode;
};

export const setAllSlotDisplayStatus = (mode) => {
  for (let period of periods.value) {
    for (let day of ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']) {
      setSlotDisplayStatus(period, day, mode);
    }
  }
}
export const setSlotDisplayStatus = (period, day, mode) => {
  const key = getSlotKey(period, day);
  if (!slotDisplayControl.value[key]) {
    slotDisplayControl.value[key] = { displayMode: SLOT_DISPLAY_MODES.ALL };
  }
  slotDisplayControl.value[key].displayMode = mode;
  
};

// 结合课程显示策略与 slot 显示策略
export const shouldDisplayCourseForCell = (course, period, day) => {
  // 改为并集逻辑：候选列表规则 OR 单元格规则
  const courseOk = shouldDisplayCourse(course);

  const mode = getSlotDisplayStatus(period, day);
  let slotOk = true;
  if (mode === SLOT_DISPLAY_MODES.NONE) {
    slotOk = false;
  } else if (mode === SLOT_DISPLAY_MODES.ALL) {
    slotOk = true;
  } else {
    const courseNum = course.num !== undefined ? course.num : 0;
    const isUndecided = courseNum > 0 && courseNum < solutionsNum.value && solutionsNum.value > 0;
    const isFixed = (courseNum === solutionsNum.value) && solutionsNum.value > 0;

    if (mode === SLOT_DISPLAY_MODES.CHOSEN) {
      slotOk = !!course.chosen;
    } else if (mode === SLOT_DISPLAY_MODES.IMPORTANT) {
      slotOk = isUndecided || isFixed;
    }
  }

  return courseOk || slotOk;
};

export const selectCourse = (item) => {
  updatePreferenceDescription('');

  // 在 candidateItems 中找到对应的课程并更新 userSelected 状态
  const course = currentPreference.value.candidateItems.find(
    (selectedItem) =>
      selectedItem['课程名'] === item['课程名'] &&
      selectedItem['主讲教师'] === item['主讲教师'] &&
      selectedItem['上课时间'] === item['上课时间']
  );
  
  if (course) {
    // 切换当前课程的 userSelected 状态
    course.userSelected = !course.userSelected;
    
    // 如果当前课程被选中，则删除同名但不同教师或时间的课程
    if (course.userSelected) {
      // 找出所有同名但不同教师或时间的课程
      const sameCourseNames = currentPreference.value.candidateItems.filter(
        (selectedItem) =>
          selectedItem['课程名'] === item['课程名'] &&
          (selectedItem['主讲教师'] !== item['主讲教师'] ||
           selectedItem['上课时间'] !== item['上课时间'])
      );
      
      sameCourseNames.forEach(sameNameItem => {
        sameNameItem.userSelected = false;
        const filterKey = "x_" + sameNameItem['课程名'] + "_" + sameNameItem['主讲教师'] + "_" + sameNameItem['上课时间'];
        delete filters.value[filterKey];
      });
    }
  }

  const filterKey = "x_" + item['课程名'] + "_" + item['主讲教师'] + "_" + item['上课时间'];
  if (course && course.userSelected) {
    // 如果课程被选中，添加筛选条件
    filters.value[filterKey] = { operation: 'item', value: 1.0};
  } else {
    // 如果课程被取消选中，删除筛选条件
    delete filters.value[filterKey];
  }
  
  applyFilter();
  
  // 记录点击课程表中课程操作 - 使用新的ACTION_TYPE
  logUserAction(ACTION_TYPES.COURSE_SELECT, {
    course_name: item['课程名'],
    instructor: item['主讲教师'],
    time: item['上课时间'],
    new_state: course && course.userSelected ? 'selected' : 'unselected'
  });
};

export const removeNotSelectedCourse = (item) => {
  const course = currentPreference.value.candidateItems.find(
    (selectedItem) =>
      selectedItem['课程名'] === item['课程名'] &&
      selectedItem['主讲教师'] === item['主讲教师'] &&
      selectedItem['上课时间'] === item['上课时间']
  );
  if (course) {
    course.selected = true;
  }
  removeNotItemFilter(item)
}

export const removeItemFilter = (filterKey) => {
  delete filters.value[filterKey];
  applyFilter();  // 重新应用筛选
}


// 计算是否有选中的课程
export const hascandidateItems = computed(() => {
  return currentPreference.value.candidateItems.some(item => item.userSelected); // 检查是否有 userSelected 为 true 的项
});

export const toggleCourse = (item) => {
  if (item.selected) {
    addCourse(item);
    updatePreferenceCoursesChange(item, 'add');
  } else {
    removeCourse(item);
    updatePreferenceCoursesChange(item, 'remove');
  }
  
  // 记录课程卡片勾选操作 - 使用新的ACTION_TYPE
  logUserAction(ACTION_TYPES.COURSE_CARD_CHECK, {
    course_name: item['课程名'],
    instructor: item['主讲教师'],
    time: item['上课时间'],
    new_state: item.selected ? 'checked' : 'unchecked'
  });
};

export const addCourse = (item) => {
  removeNotItemFilter(item)
  addUserMessage(`Add course: ${item['课程名']} - ${item['主讲教师']} - ${item['上课时间']}`);
}

export const removeCourse = (course) => {
  // 将 candidateItems 中对应课程的 selected 设置为 false
  const item = currentPreference.value.candidateItems.find(item => item['课程名'] === course['课程名'] && item['主讲教师'] === course['主讲教师'] && item['上课时间'] === course['上课时间']);
  if (item) {
    item.selected = false;
    item.userSelected = false;
    item.chosen = false;
  }
  // addNotItemFilter(item)
  applyFilter();
  
  addUserMessage(`Remove course: ${item['课程名']} - ${item['主讲教师']} - ${item['上课时间']}`);
};

export const logRemoveCourse = (item)=>{
    // 记录移除课程操作 - 使用新的ACTION_TYPE
    logUserAction(ACTION_TYPES.REMOVE_COURSE, {
      course_name: item['课程名'],
      instructor: item['主讲教师'],
      time: item['上课时间']
    });
}

// 将选中状态为 true 的课程项内容填充到输入框中
export const addToInputBox = () => {
  // 获取所有 userSelected 为 true 的课程
  const selectedCourses = currentPreference.value.candidateItems
    .filter(item => item.userSelected)
    .map(item => `${item['课程名']} (${item['主讲教师']}) - ${item['上课时间']}`);

  // 将选中的课程填充到输入框
  userMessage.value = "选择课程: " + selectedCourses.join(',');
};


export const addNotItemFilter = (item) => {
  const filterKey = "x_" + item['课程名'] + "_" + item['主讲教师'] + "_" + item['上课时间']
  delete filters.value[filterKey];
  filters.value[filterKey] = { operation: 'item', value: 0.0}
  applyFilter()
}

export const removeNotItemFilter = (item) => {
  const filterKey = "x_" + item['课程名'] + "_" + item['主讲教师'] + "_" + item['上课时间']
  delete filters.value[filterKey];
  applyFilter()
}

// 添加辅助函数来确定是否应该显示课程
export const shouldDisplayCourse = (course) => {
  const displayMode = getCourseDisplayStatus(course['课程名']);
  
  if (displayMode === DISPLAY_MODES.ALL) {
    return true;
  } else if (displayMode === DISPLAY_MODES.CHOSEN) {
    const isDeleted = (currentPreference.value.isIncremental === true ) && 
           course.chosen_when_confirmed && 
           !course.chosen;
    return course.chosen || course.userSelected || isDeleted;
  } else if (displayMode === DISPLAY_MODES.IMPORTANT) {
    const idDeleted = (currentPreference.value.isIncremental === true ) && 
           course.chosen_when_confirmed && 
           !course.chosen;
    // 检查 course.num 是否有效
    const courseNum = course.num !== undefined ? course.num : 0;
    
    // 显示固定和未决定的课程
    const isFixed = (courseNum === solutionsNum.value ) && solutionsNum.value > 0;
    const isUndecided = courseNum > 0 && courseNum < solutionsNum.value && solutionsNum.value > 0;
    
    return isFixed || isUndecided || idDeleted;
  }
  return false;
};
