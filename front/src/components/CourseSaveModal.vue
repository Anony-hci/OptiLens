<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>选择要保存的课程</h3>
        <button @click="onClose" class="close-button">×</button>
      </div>
      
      <div class="modal-body">
        <div class="course-selection-container">
          <div class="selection-header">
            <input 
              type="checkbox" 
              :checked="isAllSelected" 
              :indeterminate="isPartiallySelected"
              @change="toggleSelectAll"
            />
            <span>全选当前方案中的课程</span>
          </div>
          
          <div class="courses-list">
            <div 
              v-for="course in localCourses" 
              :key="`${course['课程名']}_${course['主讲教师']}_${course['上课时间']}`"
              class="course-item"
            >
              <input 
                type="checkbox" 
                v-model="course.selected" 
                @change="updateSelection"
              />
              <div class="course-info">
                <span class="course-name">{{ course['课程名'] }}</span>
                <span class="course-teacher">{{ course['主讲教师'] }}</span>
                <span class="course-time">{{ course['上课时间'] }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="onClose" class="cancel-btn">取消</button>
        <button @click="onConfirm" class="confirm-btn" :disabled="!hasSelectedCourses">确认保存</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

// 定义props
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  availableCourses: {
    type: Array,
    required: true
  }
});

// 定义emit
const emit = defineEmits(['close', 'confirm']);

// 本地课程数据，包含选择状态（独立于传入的availableCourses）
const localCourses = ref([]);

// 初始化本地课程数据
watch(() => props.availableCourses, (newCourses) => {
  if (newCourses && newCourses.length > 0) {
    // 创建新的对象，避免直接修改传入的数据
    localCourses.value = newCourses.map(course => ({
      ...course,
      selected: true // 默认全选
    }));
  } else {
    localCourses.value = [];
  }
}, { immediate: true });

// 计算属性：是否全选
const isAllSelected = computed(() => {
  return localCourses.value.length > 0 && localCourses.value.every(course => course.selected);
});

// 计算属性：是否部分选中
const isPartiallySelected = computed(() => {
  const selectedCount = localCourses.value.filter(course => course.selected).length;
  return selectedCount > 0 && selectedCount < localCourses.value.length;
});

// 计算属性：是否有选中的课程
const hasSelectedCourses = computed(() => {
  return localCourses.value.some(course => course.selected);
});

// 全选/取消全选
const toggleSelectAll = () => {
  const newValue = !isAllSelected.value;
  localCourses.value.forEach(course => {
    course.selected = newValue;
  });
};

// 更新选择状态
const updateSelection = () => {
  // 这里可以添加额外的逻辑，比如验证选择的有效性
};

// 关闭弹窗
const onClose = () => {
  emit('close');
};

// 确认选择
const onConfirm = () => {
  // 只返回选中的课程，不包含selected状态
  const selectedCourses = localCourses.value
    .filter(course => course.selected)
    .map(course => {
      // 移除selected属性，返回原始课程数据
      const { selected, ...courseData } = course;
      return courseData;
    });
  
  emit('confirm', selectedCourses);
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
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.modal-footer {
  padding: 20px;
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
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #333;
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  border: none;
  transition: all 0.2s ease;
}

.cancel-btn {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  color: #333;
}

.cancel-btn:hover {
  background-color: #e8e8e8;
}

.confirm-btn {
  background-color: #4a6fa5;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #3a5a8a;
}

.confirm-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.course-selection-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.selection-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.selection-header input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.selection-header span {
  font-weight: 600;
  color: #495057;
}

.courses-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.course-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  background-color: #fff;
  transition: all 0.2s ease;
}

.course-item:hover {
  border-color: #4a6fa5;
  box-shadow: 0 2px 8px rgba(74, 111, 165, 0.1);
}

.course-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  flex-shrink: 0;
}

.course-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}

.course-name {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.course-teacher {
  color: #666;
  font-size: 14px;
}

.course-time {
  color: #888;
  font-size: 12px;
  font-style: italic;
}

/* 滚动条样式 */
.courses-list::-webkit-scrollbar {
  width: 6px;
}

.courses-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.courses-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.courses-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 