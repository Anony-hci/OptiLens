<!-- src/components/Step2.vue -->
<template>
    <div class="step step-2">
      <div class="chat-and-panels">
        <!-- 左侧：收藏夹 -->
        <div class="selected-items-panel">
          <h3>Candidate Courses
            <div style="display: inline-flex; align-items: center;">
              <button @click="addItems" class="add-course-btn">Add</button>

              <!-- 添加折叠/展开所有课程的按钮 -->
              <button 
                class="toggle-all-btn"
                @click="toggleAllCoursesFold"
                :title="isAllCoursesFolded ? '展开所有课程' : '折叠所有课程'"
              >
                {{ isAllCoursesFolded ? '▶' : '▼ ' }}
              </button>
              <div class="dropdown-wrapper" @mouseenter="showGlobalMenu = true" @mouseleave="showGlobalMenu = false">
                <button class="filter-button" @click="toggleshowAllCourses()">
                  <img v-if="currentMode === DISPLAY_MODES.ALL" src="../assets/all.svg" width="22" height="22" alt="all" />
                  <img v-else-if="currentMode === DISPLAY_MODES.CHOSEN" src="../assets/chosen.svg" width="15" height="15" alt="chosen" />
                  <img v-else-if="currentMode === DISPLAY_MODES.IMPORTANT" src="../assets/important.svg" width="20" height="20" alt="important" />
                  <img v-else src="../assets/cancle.svg" width="16" height="16" alt="none" />
                </button>
                <div v-if="false" class="display-menu">
                  <div class="display-menu-item" @click="setGlobalDisplay(DISPLAY_MODES.CHOSEN)"><img src="../assets/chosen.svg" width="14" height="14" /> chosen <span class="menu-check" v-if="currentMode === DISPLAY_MODES.CHOSEN">✓</span></div>
                  <div class="display-menu-item" @click="setGlobalDisplay(DISPLAY_MODES.IMPORTANT)"><img src="../assets/important.svg" width="18" height="18" /> available <span class="menu-check" v-if="currentMode === DISPLAY_MODES.IMPORTANT">✓</span></div>
                  <div class="display-menu-item" @click="setGlobalDisplay(DISPLAY_MODES.ALL)"><img src="../assets/all.svg" width="18" height="18" /> all <span class="menu-check" v-if="currentMode === DISPLAY_MODES.ALL">✓</span></div>
                  <div class="display-menu-item" @click="setGlobalDisplay(DISPLAY_MODES.NONE)"><img src="../assets/cancle.svg" width="14" height="14" /> none <span class="menu-check" v-if="currentMode === DISPLAY_MODES.NONE">✓</span></div>
                </div>
              </div>
            </div>

            <span :style="{fontSize: '12px'}">  <br> {{ candidateItems_courses_selected.length }}/{{ candidateItems_selected }} </span>
          </h3>

          <div class="selected-items-table-container">
            <div class="courses-container">
              <template v-for="item in getSortedCourses()" :key="item.type === 'group' ? item.group.id : item.courseName">
                
                <!-- 分组标题 -->
                <template v-if="item.type === 'group'">
                  <div class="course-group-header-card group-header">
                    <div class="course-group-controls">
                      <!-- 分组级别的checkbox -->
                      <div class="group-checkbox-container">
                        <input 
                          type="checkbox" 
                          :checked="isGroupAllSelected(item.group)"
                          :indeterminate="isGroupPartiallySelected(item.group)"
                          @change="toggleGroupSelection(item.group)"
                          @click.stop
                          class="group-checkbox"
                        />
                      </div>

                      <span 
                        class="course-group-btn group-name"
                        :style="{ fontWeight: getGroupCourses(item.group).some(course => course.chosen) ? 'bold' : 'normal' }"          
                      >
                        {{ item.group.name.replace('的课程数量', '') }} 
                      </span>

                      <!-- 分组折叠/展开按钮 -->
                      <button 
                        @click="toggleGroupFold(item.group.id)" 
                        class="toggle-fold-btn group-fold-btn"
                        :title="isGroupFolded(item.group.id) ? '展开分组' : '折叠分组'"
                      >
                        {{ isGroupFolded(item.group.id) ? '▶' : '▼' }}
                      </button>

                      <!-- 分组的显示控制按钮：悬浮展开四态 -->
                      <div class="dropdown-wrapper" @mouseenter="openGroupMenu = item.group.id" @mouseleave="openGroupMenu = null">
                        <button class="toggle-fold-btn group-display-btn">
                          <img v-if="getGroupDisplayStatus(item.group.id) === DISPLAY_MODES.ALL" src="../assets/all.svg" width="22" height="22" alt="all" />
                          <img v-else-if="getGroupDisplayStatus(item.group.id) === DISPLAY_MODES.CHOSEN" src="../assets/chosen.svg" width="15" height="15" alt="chosen" />
                          <img v-else-if="getGroupDisplayStatus(item.group.id) === DISPLAY_MODES.IMPORTANT" src="../assets/important.svg" width="20" height="20" alt="important" />
                          <img v-else src="../assets/cancle.svg" width="16" height="16" alt="none" />
                        </button>
                        <div v-if="openGroupMenu === item.group.id" class="display-menu">
                          <div class="display-menu-item" @click="setGroupDisplay(item.group.id, DISPLAY_MODES.CHOSEN)"><img src="../assets/chosen.svg" width="14" height="14" /> chosen <span class="menu-check" v-if="getGroupDisplayStatus(item.group.id) === DISPLAY_MODES.CHOSEN">✓</span></div>
                          <div class="display-menu-item" @click="setGroupDisplay(item.group.id, DISPLAY_MODES.IMPORTANT)"><img src="../assets/important.svg" width="18" height="18" /> available <span class="menu-check" v-if="getGroupDisplayStatus(item.group.id) === DISPLAY_MODES.IMPORTANT">✓</span></div>
                          <div class="display-menu-item" @click="setGroupDisplay(item.group.id, DISPLAY_MODES.ALL)"><img src="../assets/all.svg" width="18" height="18" /> all <span class="menu-check" v-if="getGroupDisplayStatus(item.group.id) === DISPLAY_MODES.ALL">✓</span></div>
                          <div class="display-menu-item" @click="setGroupDisplay(item.group.id, DISPLAY_MODES.NONE)"><img src="../assets/cancle.svg" width="14" height="14" /> none <span class="menu-check" v-if="getGroupDisplayStatus(item.group.id) === DISPLAY_MODES.NONE">✓</span></div>
                        </div>
                      </div>

                      <!-- 删除整个分组按钮 -->
                      <button 
                        class="delete-course-group-btn"
                        @click.stop="removeGroup(item.group)"
                        :title="`删除所有 ${item.group.name.replace('的课程数量', '课程')} 下的课程`"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                  
                  <!-- 分组下的课程 -->
                  <template v-if="!isGroupFolded(item.group.id)" v-for="courseName in item.courses" :key="courseName">
                    <!-- 课程组标题 -->
                    <div class="course-group-header-card grouped-course-header">
                      <div class="course-group-controls">
                        <!-- 课程组级别的checkbox -->
                        <div class="course-checkbox-container">
                          <input 
                            type="checkbox" 
                            :checked="isCourseGroupAllSelected(courseName)"
                            :indeterminate="isCourseGroupPartiallySelected(courseName)"
                            @change="toggleCourseGroupSelection(courseName)"
                            @click.stop
                            class="course-group-checkbox"
                          />
                        </div>

                        <span 
                          class="course-group-btn"
                          :style="{ fontWeight: currentPreference.candidateItems.filter(item => item['课程名'] === courseName).some(item => item.chosen) ? 'bold' : 'normal' }"          
                        >
                          {{ courseName }} 
                        </span>

                        <!-- 折叠/展开按钮 -->
                        <button 
                          class="toggle-fold-btn"
                          @click="toggleCourseFold(courseName)"
                        >
                          {{ isCourseFolded(courseName) ? '▶' : '▼' }}
                        </button>

                        <!-- 查看/取消查看按钮 -->
                        <button @click="toggleCourseDisplay(courseName)" class="toggle-fold-btn">
                          <img v-if="getCourseDisplayStatus(courseName) === DISPLAY_MODES.ALL" src="../assets/all.svg" width="22" height="22" alt="check" />
                          <img v-else-if="getCourseDisplayStatus(courseName) === DISPLAY_MODES.CHOSEN" src="../assets/chosen.svg" width="15" height="15" alt="check" />
                          <img v-else-if="getCourseDisplayStatus(courseName) === DISPLAY_MODES.IMPORTANT" src="../assets/important.svg" width="20" height="20" alt="check" />
                          <img v-else src="../assets/cancle.svg" width="16" height="16" alt="cancel" />
                        </button>

                        <!-- 删除整个课程组按钮 -->
                        <button 
                          class="delete-course-group-btn"
                          @click.stop="removeCourseGroup(courseName)"
                          :title="`删除所有 ${courseName} 课程`"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                    
                    <!-- 该课程组下的课程卡片 -->
                    <div v-if="!isCourseFolded(courseName)" class="course-cards-container grouped-course-cards">
                      <div v-for="courseItem in currentPreference.candidateItems.filter(item => item['课程名'] === courseName)" 
                          :key="courseItem['课程名'] + courseItem['上课时间']"
                          :class="[
                            'course-card',
                            {
                              'userSelected': courseItem.userSelected,
                              'chosen': courseItem.chosen,
                              'fixed': (courseItem.num === filteredSolutionsNum ) && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                              'undecided': courseItem.num > 0 && courseItem.num < filteredSolutionsNum && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                              'blocked': (courseItem.num === 0 || courseItem.num === null || courseItem.num === none) && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                              'added': isAdded(courseItem),
                              'deleted': isDeleted(courseItem),
                            }
                          ]"
                          
                          @click="selectCourse(courseItem)"
                      >
                        <!-- 课程选择checkbox -->
                        <div class="course-checkbox-container">
                          <input 
                            type="checkbox" 
                            v-model="courseItem.selected"
                            @click.stop
                            @change="toggleCourse(courseItem)"
                            class="course-checkbox"
                          />
                        </div>

                        <!-- 课程卡片主体内容 -->
                        <div class="course-card-main">
                          <!-- 状态标签 -->
                          <span v-if="isAdded(courseItem)" class="status-tag added-tag">Added</span>
                          <span v-if="isDeleted(courseItem)" class="status-tag removed-tag">Removed</span>
                          
                          <!-- 课程卡片头部：优先级和删除按钮 -->
                          <div class="course-card-header">
                            <div class="priority-section">
                              <label class="priority-label">优先级</label>
                              <div class="star-rating" @click.stop>
                                <span 
                                  v-for="star in 5" 
                                  :key="star"
                                  class="star"
                                  :class="{ 
                                    'active': star <= (courseItem.priority || 1),
                                    'user-set': courseItem.priority_type === 'user'
                                  }"
                                  @click="updateCoursePriority(courseItem, star)"
                                >
                                  ★
                                </span>
                              </div>
                            </div>
                            <button 
                              class="delete-course-btn-card"
                              @click.stop="removeCandidateCourse(courseItem)"
                              title="删除此课程"
                            >
                              ×
                            </button>
                          </div>

                          <!-- 课程卡片内容 -->
                          <div class="course-card-content">
                            <div class="course-info-row" v-for="(header, idx) in headers" :key="idx">
                              <span class="info-label">{{ header }}:</span>
                              <span class="info-value">{{ courseItem[header] }}</span>
                            </div>
                          </div>

                          <!-- 条件渲染勾，使用绝对定位将勾放置在右下角 -->
                          <span v-if="courseItem.userSelected" class="checkmark-card">✔</span>
                        </div>
                      </div>
                    </div>
                  </template>
                </template>
                
                <!-- 非分组课程 -->
                <template v-else-if="item.type === 'course'">
                  <!-- 课程组标题 -->
                  <div class="course-group-header-card">
                    <div class="course-group-controls">
                      <!-- 课程组级别的checkbox -->
                      <div class="course-checkbox-container">
                        <input 
                          type="checkbox" 
                          :checked="isCourseGroupAllSelected(item.courseName)"
                          :indeterminate="isCourseGroupPartiallySelected(item.courseName)"
                          @change="toggleCourseGroupSelection(item.courseName)"
                          @click.stop
                          class="course-group-checkbox"
                        />
                      </div>

                      <span 
                        class="course-group-btn"
                        :style="{ fontWeight: currentPreference.candidateItems.filter(courseItem => courseItem['课程名'] === item.courseName).some(courseItem => courseItem.chosen) ? 'bold' : 'normal' }"          
                      >
                        {{ item.courseName }} 
                      </span>

                      <!-- 折叠/展开按钮 -->
                      <button 
                        class="toggle-fold-btn"
                        @click="toggleCourseFold(item.courseName)"
                      >
                        {{ isCourseFolded(item.courseName) ? '▶' : '▼' }}
                      </button>

                      <!-- 课程组显示模式：悬浮展开四态 -->
                      <div class="dropdown-wrapper" @mouseenter="openCourseMenu = item.courseName" @mouseleave="openCourseMenu = null">
                        <button class="toggle-fold-btn" @click="toggleCourseDisplay(item.courseName)">
                          <img v-if="getCourseDisplayStatus(item.courseName) === DISPLAY_MODES.ALL" src="../assets/all.svg" width="22" height="22" alt="all" />
                          <img v-else-if="getCourseDisplayStatus(item.courseName) === DISPLAY_MODES.CHOSEN" src="../assets/chosen.svg" width="15" height="15" alt="chosen" />
                          <img v-else-if="getCourseDisplayStatus(item.courseName) === DISPLAY_MODES.IMPORTANT" src="../assets/important.svg" width="20" height="20" alt="important" />
                          <img v-else src="../assets/cancle.svg" width="16" height="16" alt="none" />
                        </button>
                        <div v-if="openCourseMenu === item.courseName" class="display-menu">
                          <div class="display-menu-item" @click="setCourseDisplay(item.courseName, DISPLAY_MODES.CHOSEN)"><img src="../assets/chosen.svg" width="14" height="14" /> chosen <span class="menu-check" v-if="getCourseDisplayStatus(item.courseName) === DISPLAY_MODES.CHOSEN">✓</span></div>
                          <div class="display-menu-item" @click="setCourseDisplay(item.courseName, DISPLAY_MODES.IMPORTANT)"><img src="../assets/important.svg" width="18" height="18" /> available <span class="menu-check" v-if="getCourseDisplayStatus(item.courseName) === DISPLAY_MODES.IMPORTANT">✓</span></div>
                          <div class="display-menu-item" @click="setCourseDisplay(item.courseName, DISPLAY_MODES.ALL)"><img src="../assets/all.svg" width="18" height="18" /> all <span class="menu-check" v-if="getCourseDisplayStatus(item.courseName) === DISPLAY_MODES.ALL">✓</span></div>
                          <div class="display-menu-item" @click="setCourseDisplay(item.courseName, DISPLAY_MODES.NONE)"><img src="../assets/cancle.svg" width="14" height="14" /> none <span class="menu-check" v-if="getCourseDisplayStatus(item.courseName) === DISPLAY_MODES.NONE">✓</span></div>
                        </div>
                      </div>

                      <!-- 删除整个课程组按钮 -->
                      <button 
                        class="delete-course-group-btn"
                        @click.stop="removeCourseGroup(item.courseName)"
                        :title="`删除所有 ${item.courseName} 课程`"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                  
                  <!-- 该课程组下的课程卡片 -->
                  <div v-if="!isCourseFolded(item.courseName)" class="course-cards-container">
                    <div v-for="courseItem in currentPreference.candidateItems.filter(courseItem => courseItem['课程名'] === item.courseName)" 
                        :key="courseItem['课程名'] + courseItem['上课时间']"
                        :class="[
                          'course-card',
                          {
                            'userSelected': courseItem.userSelected,
                            'chosen': courseItem.chosen,
                            'fixed': (courseItem.num === filteredSolutionsNum ) && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                            'undecided': courseItem.num > 0 && courseItem.num < filteredSolutionsNum && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                            'blocked': (courseItem.num === 0 || courseItem.num === null || courseItem.num === none) && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                            'added': isAdded(courseItem),
                            'deleted': isDeleted(courseItem),
                          }
                        ]"
                        @click="selectCourse(courseItem)"
                    >
                      <!-- 课程选择checkbox -->
                      <div class="course-checkbox-container">
                        <input 
                          type="checkbox" 
                          v-model="courseItem.selected"
                          @click.stop
                          @change="toggleCourse(courseItem)"
                          class="course-checkbox"
                        />
                      </div>

                      <!-- 课程卡片主体内容 -->
                      <div class="course-card-main">
                        <!-- 状态标签 -->
                        <span v-if="isAdded(courseItem)" class="status-tag added-tag">Added</span>
                        <span v-if="isDeleted(courseItem)" class="status-tag removed-tag">Removed</span>
                        
                        <!-- 课程卡片头部：优先级和删除按钮 -->
                        <div class="course-card-header">
                          <div class="priority-section">
                            <label class="priority-label">优先级</label>
                            <div class="star-rating" @click.stop>
                              <span 
                                v-for="star in 5" 
                                :key="star"
                                class="star"
                                :class="{ 
                                  'active': star <= (courseItem.priority || 1),
                                  'user-set': courseItem.priority_type === 'user'
                                }"
                                @click="updateCoursePriority(courseItem, star)"
                              >
                                ★
                              </span>
                            </div>
                          </div>
                          <button 
                            class="delete-course-btn-card"
                            @click.stop="removeCandidateCourse(courseItem)"
                            title="删除此课程"
                          >
                            ×
                          </button>
                        </div>

                        <!-- 课程卡片内容 -->
                        <div class="course-card-content">
                          <div class="course-info-row" v-for="(header, idx) in headers" :key="idx">
                            <span class="info-label">{{ header }}:</span>
                            <span class="info-value">{{ courseItem[header] }}</span>
                          </div>
                        </div>

                        <!-- 条件渲染勾，使用绝对定位将勾放置在右下角 -->
                        <span v-if="courseItem.userSelected" class="checkmark-card">✔</span>
                      </div>
                    </div>
                  </div>
                </template>
              </template>
            </div>
          </div>
        </div>
  
        
  
        <!-- 中间：求解结果 -->
        <div class="solution-results-panel">
          <h3 style="display: flex; align-items: center; justify-content: space-between;">
            <span>Timetable</span>
            <div class="save-button-container" v-if="filteredSolutionsNum>0">
                <button @click="openSaveModal" class="save-button">
                  <span>Save Courses</span>
                </button>
              </div>
            <button @click="saveCurrentData" class="save-data-btn" :disabled="isSaving" v-if="false">
              <span v-if="!isSaving">💾 保存数据</span>
              <span v-else>⏳ 保存中...</span>
            </button>
          </h3>
        
          <div class="solution-content">
            <!-- 课程表部分 -->
            <div class="course-schedule" >
              <table>
                <thead>
                  <tr>
                    <th style="width: 60px; min-width: 60px;">Period</th>
                    <th>MON</th>
                    <th>TUE</th>
                    <th>WED</th>
                    <th>THU</th>
                    <th>FRI</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="period in periods" :key="period">
                    <td style="width: 60px; min-width: 60px;">{{ period }}</td>
                    <!-- 遍历每个时间段的课程 -->
                    <td v-for="day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']" :key="day" class="schedule-cell" @mouseenter="hoverSlot = { period, day }" @mouseleave="hoverSlot = null">
                      <!-- 悬浮 Slot 控制菜单（单按钮循环四态） -->
                      <div v-if="hoverSlot && hoverSlot.period === period && hoverSlot.day === day" class="slot-control">
                        <button class="slot-control-btn" @click.stop="toggleSlotMode(period, day)" :title="slotModeTitle(getSlotDisplayStatus(period, day))">
                          <img v-if="getSlotDisplayStatus(period, day) === SLOT_DISPLAY_MODES.ALL" src="../assets/all.svg" width="18" height="18" alt="all" />
                          <img v-else-if="getSlotDisplayStatus(period, day) === SLOT_DISPLAY_MODES.CHOSEN" src="../assets/chosen.svg" width="14" height="14" alt="chosen" />
                          <img v-else-if="getSlotDisplayStatus(period, day) === SLOT_DISPLAY_MODES.IMPORTANT" src="../assets/important.svg" width="18" height="18" alt="important" />
                          <img v-else src="../assets/cancle.svg" width="14" height="14" alt="none" />
                        </button>
                      </div>
                      <div v-for="course in schedule[period][day]" :key="course['课程名']">
                        <button 
                          :class="[
                            'course-button',
                            {
                              'chosen': course.chosen,
                              'userSelected': course.userSelected,
                              'fixed': (course.num === filteredSolutionsNum ) && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                              'undecided': course.num > 0 && course.num < filteredSolutionsNum && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                              'blocked': (course.num === 0 || course.num === null || course.num === none) && filteredSolutionsNum !== null && filteredSolutionsNum !== 0 ,
                              'added': isAdded(course),
                              'deleted': isDeleted(course),
                              'infeasible': filteredSolutionsNum === 0,
                            }
                          ]"
                          @click="selectCourse(course)"
                          v-if="isCourseVisibleInTimetable(course)"
                        >
                          <!-- Added 标签 -->
                          <span v-if="isAdded(course)" class="status-tag added-tag">Added</span>
                          
                          <!-- Deleted/Removed 标签 -->
                          <span v-if="isDeleted(course)" class="status-tag removed-tag">Removed</span>
                          
                          <span 
                            style="position: absolute; 
                                   top: 50%; 
                                   transform: translateY(-50%);
                                   right: 2px; 
                                   font-size: 8px;"
                            v-if="filteredSolutionsNum === solutionsNum "
                          >
                            <!-- {{ course['num'] }} -->
                          </span>
                          {{ course['课程名'] }}<span v-if="course['priority'] !== 3"> {{ course['priority'] }}⭐️</span><br>({{ course['主讲教师'] }})<br>{{ course['上课时间'] }}

                            <!-- 删除按钮触发区域 -->
                            <div 
                              class="delete-trigger-area"
                              @mouseenter="showDeleteBtn = true"
                              @mouseleave="showDeleteBtn = false"
                            ></div>

                          <!-- 删除按钮 "x"，初始隐藏 -->
                          <span 
                            class="delete-btn"
                            @click.stop="removeCourse(course);logRemoveCourse(course);"
                          >
                            x
                          </span>

                          <!-- 条件渲染勾，使用绝对定位将勾放置在右下角 -->
                          <span v-if="course.userSelected" class="checkmark">✔</span>
                        </button>

                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <!-- 课程状态说明 -->
              <div class="course-status-legend" v-if="filteredSolutionsNum > 0">
                <h4>Course Status：</h4>
                <div class="legend-items-container">
                  <div class="legend-items">
                    <div class="legend-item">
                      <div class="legend-color fixed-color"></div>
                      <span>Fixed - Selected in all solutions</span>
                      <div class="legend-color undecided-color"></div>
                      <span>Undecided - Selected in some solutions</span>
                      <div class="legend-color blocked-color"></div>
                      <span>Blocked - Not selected in any solutions</span>
                      <span style="font-weight: bold;">Bold</span> <span>- Selected in the current solution</span>
                    </div>
                    <div class="legend-items" v-if="false">
                    <div class="legend-item">
                      <span class="legend-status-tag added-tag">Added</span>
                      <span>- 相比保存的课程，增加的课程</span>
                      <span class="legend-status-tag removed-tag">Removed</span>
                      <span>- 之前保存的课程中，被移除的课程</span>
                    </div>
                  </div>
                  </div>
                </div>
              </div>
              <div class="course-operation-legend-container">
                <!-- 课程操作方式说明 -->
                <div class="course-operation-legend" v-if="false">
                  <h4>课程操作方式：</h4>
                  <div class="legend-items">
                    <div class="legend-item">
                      <div class="legend-icon select-icon">✓</div>
                      <span>直接点击课程：显示蓝色√表示选择该课程；再次点击则取消选择</span>
                    </div>
                    <div class="legend-item">
                      <div class="legend-icon remove-icon">×</div>
                      <span>点击右上角的×：移除该课程，不再考虑</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="solution-results" v-if="currentPreference?.solutionResults">
              <!-- 第一行：状态显示 -->
                <!-- <div v-if="currentSolutionResult.status === 'OPTIMAL'" class="solution-summary">
                  得到 {{ currentSolutionResult.solutionNum }} 个可行解
                </div> -->

                <!-- 特征描述 -->
                <div class="constraints-section" >
                <div v-if="filteredSolutionsNum == 0" style="color: #888; padding: 16px;">
                  没有可行的课表方案，请调整约束或课程选择后重试。
                </div>
                <table class="solutions-table" v-if="filteredSolutionsNum > 0 && !isChanged">
                  <thead>
                    <tr>
                      <th></th>
                      <th style="width: 200px;">Distribution</th>
                      <th v-for="(solution, index) in displayedSolutions.solutions" :key="displayedSolutions.startIndex + index">
                         {{ displayedSolutions.startIndex + index + 1 }}
                      </th>
                        <!-- 固定宽度 -->
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="featureName in orderedFeaturesName(selectedFeatures)" :key="featureName" >
                      <td class="feature-name" 
                          @click="openFilterMenu(featureName)" 
                          :style="{ color: '#1a73e8' }"
                      >
                        {{ getFeatureDisplay(featureName) }}
                        <!-- 显示筛选菜单 -->
                        <div v-if="filterMenus[featureName]" class="filter-menu" @click.stop>
                          <label>筛选：</label>
                          <select v-model="filters[featureName].operation" @change="handleFilterChange(featureName, 'operation')"  style="width: 70px">
                            <option value="equal">等于</option>
                            <!-- <option value="notEqual">不等于</option> -->
                            <option value="greaterThanOrEqual">大于等于</option>
                            <option value="lessThanOrEqual">小于等于</option>
                          </select>
                          <input type="number" v-model="filters[featureName].value" @input="handleFilterChange(featureName, 'value')"  @click.stop style="width: 40px"/>
                          <button @click="removeFilter(featureName)" style="width: 20px; color: red">×</button>
                        </div>
                      </td>
                      <td class="histogram-cell">
                        <div class="histogram-container">
                          <template v-if="features_statistics[featureName]">
                            <div 
                              v-for="(count, value) in features_statistics[featureName]" 
                              :key="value"
                              class="histogram-column"
                            >
                              <div class="histogram-bar"
                                :style="{
                                  height: `${(count / filteredSolutionsNum) * 10}px`,
                                  backgroundColor: generateDynamicColor(featureName),
                                  width: '15px',
                                  position: 'relative',
                                  padding: '0px'
                                }"
                                :title="value"
                              >
                                <div class="bar-value">{{ count }}</div>
                              </div>
                              <div class="x-label">{{ value }}</div>
                            </div>
                          </template>
                        </div>
                      </td>
                      <td v-for="(solution, index) in displayedSolutions.solutions" 
                          :key="displayedSolutions.startIndex + index"
                          :class="{ 'current-solution': displayedSolutions.startIndex + index === currentPreference.currentSolutionIndex }">
                        {{ solution.features[featureName] }}
                      </td>
                    </tr>
                    
                    <!-- 添加雷达图行 -->
                    <tr class="radar-chart-row" v-if="false">
                      <td class="feature-name">雷达图</td>
                      <td class="histogram-cell">
                        <!-- 保持为空 -->
                      </td>
                      <td v-for="(solution, index) in displayedSolutions.solutions" 
                          :key="displayedSolutions.startIndex + index"
                          class="radar-chart-cell"
                          @mouseenter="showLargeChart(index, $event)"
                          @mouseleave="hideLargeChart">
                        <canvas :ref="el => { if (el) spiderChartRefs[index] = el }"></canvas>
                      </td>
                      
                    </tr>
                  </tbody>
                </table>
              </div>

                <!-- <div class="constraints-section" v-if="currentSolutionResult.solutions?.[currentPreference.currentSolutionIndex]?.Constraints">
                  <h4>约束满足情况:</h4>
                  <div 
                    v-for="(constraintDetail, constraintName) in currentSolutionResult?.solutions?.[currentPreference.currentSolutionIndex]?.Constraints" 
                    :key="constraintName" 
                    class="constraint-pair"
                  >
                    <template v-if="!constraintDetail.constrName.includes('必修课') && !constraintDetail.constrName.includes('必须上')">
                      <div class="constraint-key">{{ constraintDetail.constrName }}</div>
                      <div class="constraint-value" v-if="constraintDetail.constrName.includes('上课时间') && constraintDetail.constrName.includes('只能选一节课')">
                        {{ constraintDetail.lhs === 0 ? '没有课' : '有一节课' }}
                      </div>
                      <div class="constraint-value" v-else>lhs: {{ constraintDetail.lhs }}, rhs: {{ constraintDetail.rhs }}</div>
                    </template>
                  </div>
                </div> -->
              </div>
            </div>
            <!-- 页码控件 -->
            <div class="solution-navigation" v-if="filteredSolutionsNum > 0">
              <button @click="goToPreviousSolution" :disabled="currentPreference.currentSolutionIndex === 0">previous</button>
              <span> {{ currentPreference.currentSolutionIndex + 1 }}  /  {{ filteredSolutionsNum }} </span>
              <button @click="goToNextSolution" :disabled="currentPreference.currentSolutionIndex >= filteredSolutionsNum - 1">next</button>
              <button @click="setBaseSolution" v-if="false"  >点击查看相近的方案</button>
              <button @click="removeFromSolutionResultsHistory" v-if="is_checked_closest">取消查看相近的方案</button>
            </div>
            <!-- 分页控件 -->
            <div class="pagination" v-if="false">
              <button @click="goToPreviousPage" :disabled="currentPage === 0">上一轮</button>
              <span>第 {{ currentPage + 1 }} 轮 / 共 {{ totalPages }} 轮结果</span>
              <button @click="goToNextPage" :disabled="currentPage >= totalPages - 1">下一轮</button>
            </div>
            

            
          </div>
          
        </div>

        <!-- 右边：对话框 -->
        <div class="chat-box">
          <h3 style="display: flex; align-items: center;">
            <span>Preference Setting</span>
            <button @click="showEnlargedGraph" class="enlarge-button" style="margin-left: 10px;">
              <span class="enlarge-icon" style="display: flex; align-items: center;">🔍 View History</span>   
            </button>
          </h3>

          <!-- <ModelNodeGraph ref="modelNodeGraphRef"/> -->
          <Preference />
           
          <h3>Dialog</h3>
          <div class="messages" ref="messagesContainer">
            <!-- 遍历显示消息 -->
            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['message', msg.sender === 'You' ? 'user-message' : (msg.type === 'problemModel' ? 'problem-model-message' : msg.type === 'addedFeatureExprs' ? 'added-feature-exprs-message' : 'bot-message')]"
            >
              <Message :msg="msg" />
            </div>
          </div>
            <div class="input-box">
            <!-- 用户输入框 -->
            <input
              v-model="userMessage"
              @keydown.enter="sendMessage"
              placeholder="Type a message..."
            />
            <button @click="sendMessage">Send</button>
          </div>
        </div>
      </div>
    </div>
    <span>User ID: {{ sessionId }}</span>
    <!-- 添加弹出层 -->
    <div v-if="hoveredChart.show" 
         class="large-chart-popup"
         :style="{ left: hoveredChart.x + 'px', top: hoveredChart.y + 'px' }">
      <canvas ref="largeChartRef"></canvas>
    </div>

    <!-- 放大查看ModelNodeGraph的弹出层 -->
    <div v-if="enlargedGraphVisible" class="enlarged-graph-overlay" @click="hideEnlargedGraph">
      <div class="enlarged-graph-container" @click.stop>
        <div class="enlarged-graph-header">
          <h3>问题建模视图</h3>
          <button @click="hideEnlargedGraph" class="close-button">×</button>
        </div>
        <div class="enlarged-graph-content">
          <!-- 使用 v-if 确保组件完全重新创建 -->
          <div v-if="enlargedGraphVisible" class="enlarged-graph-wrapper">
            <ModelNodeGraph ref="enlargedModelNodeGraphRef" class="enlarged-model-node-graph" />
          </div>
        </div>
      </div>
    </div>


    <!-- 信息弹窗 - 使用从infoModel.js导入的状态变量 -->
    <InfoModal
      :show="showInfoModal"
      :title="modalTitle"
      @close="closeModal"
      @confirm="handleModalConfirm"
      :showConfirm="modalShowConfirm"
    >
      <div class="modal-info-content">
        {{ modalContent }}
      </div>
    </InfoModal>

    <!-- 使用新的课程选择弹窗组件 -->
    <CourseSelectionModal 
      :show="showAddCoursesModal"
      @close="closeAddCoursesModal"
      @confirm="handleConfirmAddCourses"
    />

    <!-- 课程保存选择弹窗 -->
    <CourseSaveModal
      :show="showSaveModal"
      :availableCourses="availableCoursesForSave"
      @close="closeSaveModal"
      @confirm="handleConfirmSave"
    />


  </template>
  
  <script setup>
  import { messages, userMessage, sendMessage, saveFeatureExprs, processResponseMessage, initializeMessages, generateMessageId, addUserMessage } from '../logic/messageService.js';
  import { currentSolutionIndex, filteredSolutionsNum, goToPreviousSolution, goToNextSolution, displayedSolutions, solutions, applyFilter, openFilterMenu, removeFilter, filters, filterMenus, translateOperation, setBaseSolution, orderedFeaturesName, confirmSolution, confirmSolutionWithSelectedCourses, is_checked_closest, features_statistics, updateCandidateItems, handleFilterChange, solutionsNum, filteredSolutions, previousSolutionCourses, initializePreviousSolutionCourses, initializeSolutionService } from '../logic/solutionService.js';
  import { currentPage, totalPages, goToPreviousPage, goToNextPage, } from '../logic/paginationService.js';
  import { periods, schedule, selectCourse, removeCourse, hascandidateItems, addToInputBox, removeItemFilter, removeNotSelectedCourse, toggleCourse, toggleCourseDisplay, courseDisplayControl, getCourseDisplayStatus, isCourseFolded, toggleCourseFold, toggleshowAllCourses, isAllCoursesFolded, toggleAllCoursesFold, DISPLAY_MODES, currentMode, getCourseGroups, getCourseGroup, getGroupCourses, getGroupDisplayStatus, toggleGroupDisplay, isGroupFolded, toggleGroupFold, shouldDisplayCourseInGroup, getSortedCourses, logRemoveCourse } from '../logic/scheduleService.js';
  import { shouldDisplayCourseForCell, SLOT_DISPLAY_MODES, setSlotDisplayStatus, getSlotDisplayStatus, setGlobalDisplayMode, setCourseDisplayStatus, setGroupDisplayStatus, isCourseVisibleInTimetable, setGlobalVisibility, setCourseNameVisibility, setGroupVisibility, setSlotVisibility } from '../logic/scheduleService.js';
  import { headers, loadDefaultCSV } from '../logic/fileService.js';
  import { allCandidateSelected, someCandidateSelected, toggleSelectAll, hasAddedItems, candidateItems_courses_selected, candidateItems_selected, allCourses} from '../logic/coursesService.js';
  import { removeFromSolutionResultsHistory } from '../logic/historyService.js';
  import {ref, computed, watch, onMounted, onUpdated, nextTick, onBeforeUnmount } from 'vue';
  import Chart from 'chart.js/auto';
  import Message from './Message.vue';
  import { getFeatureDisplay, modelNodes, selectedFeatures, solving } from '../logic/modelNodeService';
  import ModelNodeGraph from './ModelNodeGraph.vue'
  import Preference from './Preference.vue';
  import InfoModal from './InfoModal.vue';
  // 导入弹窗相关函数和状态
  import { showInfoModal, modalTitle, modalContent, modalShowConfirm, modalCallback, showModal, handleModalConfirm, closeModal} from '../logic/infoModel.js';
  // import csvPath from '../data/filtered_courses.csv?url';
  import csvPath from '../data/courses5.csv?url';
  import CourseSelectionModal from './CourseSelection.vue';
  import CourseSaveModal from './CourseSaveModal.vue';
  import { sayHelloToBackend } from '../logic/apiService.js';
  import { logUserAction, ACTION_TYPES } from '../logic/userActionLogService.js';
  import { shouldDisplayCourse } from '../logic/scheduleService.js';
  import { clearCoursesChanges, currentPreference, getConstraintsChanges, getObjectivesChanges, isChanged, updatePreferenceCoursesChange } from '../logic/preferenceService.js';
  import { updateMessagesToBackend, updateCurrentPreferenceToBackend, saveDataToBackend } from '../logic/apiService.js';
  import { addNewNode } from '../logic/modelNodeService.js';

  // 课程保存相关的响应式变量
  const showSaveModal = ref(false);
  const availableCoursesForSave = ref([]);

  // 悬浮的 slot（单元格）控制
  const hoverSlot = ref(null);
  const toggleSlotMode = (period, day) => {
    const mode = getSlotDisplayStatus(period, day);
    let next;
    if (mode === SLOT_DISPLAY_MODES.CHOSEN) {
      next = SLOT_DISPLAY_MODES.IMPORTANT;
    } else if (mode === SLOT_DISPLAY_MODES.IMPORTANT) {
      next = SLOT_DISPLAY_MODES.ALL;
    } else if (mode === SLOT_DISPLAY_MODES.ALL) {
      next = SLOT_DISPLAY_MODES.CHOSEN;
    }
    setSlotDisplayStatus(period, day, next);
    setSlotVisibility(period, day, next);
  };

  // 悬浮菜单显隐状态
  const showGlobalMenu = ref(false);
  const openGroupMenu = ref(null);
  const openCourseMenu = ref(null);

  // 菜单项点击处理
  const setGlobalDisplay = (mode) => {
    setGlobalDisplayMode(mode);
    // 同步可见性映射
    setGlobalVisibility(mode);
    showGlobalMenu.value = false;
  };
  const setGroupDisplay = (groupId, mode) => {
    setGroupDisplayStatus(groupId, mode);
    // 同步可见性映射
    setGroupVisibility(groupId, mode);
    openGroupMenu.value = null;
  };
  const setCourseDisplay = (courseName, mode) => {
    setCourseDisplayStatus(courseName, mode);
    // 同步可见性映射
    setCourseNameVisibility(courseName, mode);
    openCourseMenu.value = null;
  };

  const slotModeTitle = (mode) => {
    if (mode === SLOT_DISPLAY_MODES.ALL) return '显示所有课程';
    if (mode === SLOT_DISPLAY_MODES.CHOSEN) return '只显示已选课程';
    if (mode === SLOT_DISPLAY_MODES.IMPORTANT) return '显示固定和未决定课程';
    return 'none';
  };

  // 课程保存相关的方法
  const openSaveModal = () => {
    // 获取当前方案中chosen为true的课程
    const currentSolution = filteredSolutions.value[currentPreference.value.currentSolutionIndex];
    if (currentSolution && currentSolution.Variables) {
      const chosenCourses = currentPreference.value.candidateItems.filter(item => {
        const key = `x_${item['课程名']}_${item['主讲教师']}_${item['上课时间']}`;
        return currentSolution.Variables[key] === 1.0;
      });
      
      // 创建课程数据的副本，避免修改原始数据
      availableCoursesForSave.value = chosenCourses.map(course => ({ ...course }));
      showSaveModal.value = true;
    }
  };

  const closeSaveModal = () => {
    showSaveModal.value = false;
  };

  const handleConfirmSave = (selectedCourses) => {
    // 调用修改后的confirmSolution函数，传入选中的课程
    confirmSolutionWithSelectedCourses(selectedCourses);
    closeSaveModal();
  };

  // 在组件挂载时也滚动到底部
  onMounted(() => {
    loadDefaultCSV(csvPath);
    initializeSolutionService();    // 其他初始化代码...
    // initializeFirstNode();
    initializeMessages();
    scrollMessagesToBottom();

    // 确保所有candidateItems都有selected属性
    nextTick(() => {
      if (currentPreference.value.candidateItems) {
        currentPreference.value.candidateItems.forEach(item => {
          if (item.selected === undefined) {
            item.selected = false;
          }
        });
      }
    });

  });

  // 预定义一组鲜明的基础颜色
  const baseColors = [
    '#FF0000', // 红色
    '#00FF00', // 绿色
    '#0000FF', // 蓝色
    '#FF00FF', // 洋红
    '#00FFFF', // 青色
    '#FFA500', // 橙色
    '#800080', // 紫色
    '#008000', // 深绿色
    '#000080', // 海军蓝
    '#FF4500', // 橙红色
    '#4B0082', // 靛蓝
    '#8B4513', // 马鞍棕色
    '#006400', // 深绿色
    '#483D8B', // 暗灰蓝
    '#FF1493', // 深粉色
  ];

  // 确保这个函数被导出和定义
  const generateDynamicColor = (str) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return baseColors[Math.abs(hash) % baseColors.length];
  };

  // 存储图表实例的引用
  const charts = ref([]);

  // 规范化特征值到0-1之间
  const normalizeFeatureValue = (value, featureName, allSolutions) => {
    const values = allSolutions.map(s => s.features[featureName]);
    const max = Math.max(...values);
    const min = Math.min(...values);
    return max === min ? 0.5 : (value - min) / (max - min);
  };

  // 添加 ref 数组来存储 canvas 引用
  const spiderChartRefs = ref([]);

  // 修改 updateSpiderCharts 函数
  const updateSpiderCharts = async () => {
    await nextTick();
    
    // 清除旧的图表
    charts.value.forEach(chart => chart?.destroy());
    charts.value = [];

    displayedSolutions.value.solutions.forEach((solution, index) => {
      const canvas = spiderChartRefs.value[index];
      if (!canvas) return;

      const featureNames = orderedFeaturesName(solution.features);
      const normalizedData = featureNames.map(name => 
        normalizeFeatureValue(solution.features[name], name, solutions.value)
      );

      const chart = new Chart(canvas, {
        type: 'radar',
        data: {
          labels: featureNames,
          datasets: [{
            data: normalizedData,
            fill: false,  // 关闭填充
            backgroundColor: 'rgba(200, 200, 200, 0.1)',
            borderColor: '#666',
            pointBackgroundColor: featureNames.map(name => generateDynamicColor(name)),
            pointBorderColor: featureNames.map(name => generateDynamicColor(name)),
            borderWidth: 0.5,
            pointRadius: 2,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            r: {
              beginAtZero: true,
              max: 1,
              ticks: {
                display: false
              },
              pointLabels: {
                display: false
              },
              angleLines: {
                display: true,
                color: '#ddd',
                lineWidth: 0.5
              },
              grid: {
                display: true,
                color: '#ddd',
                lineWidth: 0.5
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          },
          elements: {
            line: {
              borderWidth: 0.5,
              tension: 0
            },
            point: {
              radius: 2,
              hitRadius: 3,
              hoverRadius: 3
            }
          }
        }
      });
      
      charts.value.push(chart);
    });
  };

  // 修改 watch 函数，确保在数据变化时重新创建图表
  watch([displayedSolutions, solutions], () => {
    nextTick(() => {
      updateSpiderCharts();
    });
  }, { deep: true });

  // 添加悬停相关的状态
  const hoveredChart = ref({
    show: false,
    x: 0,
    y: 0,
    index: -1
  });

  const largeChartRef = ref(null);
  let largeChart = null;

  // 修改显示大图的函数
  const showLargeChart = (index, event) => {
    hoveredChart.value = {
      show: true,
      x: event.clientX + 10,
      y: event.clientY - 300,
      index: index
    };

    nextTick(() => {
      if (!largeChartRef.value) return;

      const solution = displayedSolutions.value.solutions[index];
      const featureNames = orderedFeaturesName(solution.features);
      const normalizedData = featureNames.map(name => 
        normalizeFeatureValue(solution.features[name], name, solutions.value)
      );

      if (largeChart) {
        largeChart.destroy();
      }

      largeChart = new Chart(largeChartRef.value, {
        type: 'radar',
        data: {
          labels: featureNames,
          datasets: [{
            data: normalizedData,
            fill: false,
            backgroundColor: 'rgba(200, 200, 200, 0.1)',
            borderColor: '#666',
            pointBackgroundColor: featureNames.map(name => generateDynamicColor(name)),
            pointBorderColor: featureNames.map(name => generateDynamicColor(name)),
            borderWidth: 1,
            pointRadius: 4,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            r: {
              beginAtZero: true,
              max: 1,
              ticks: {
                display: false
              },
              pointLabels: {
                display: true,
                callback: (label, index) => {
                  // 显示特征名称和对应的原始值
                  const originalValue = solution.features[label];
                  return `${label}: ${originalValue}`;
                },
                font: {
                  size: 10
                }
              },
              angleLines: {
                display: true,
                color: '#ddd',
                lineWidth: 0.5
              },
              grid: {
                display: true,
                color: '#ddd',
                lineWidth: 0.5
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              enabled: true,
              callbacks: {
                label: (context) => {
                  const featureName = featureNames[context.dataIndex];
                  const originalValue = solution.features[featureName];
                  return `${featureName}: ${originalValue}`;
                }
              }
            }
          }
        }
      });
    });
  };

  // 隐藏大图
  const hideLargeChart = () => {
    hoveredChart.value.show = false;
    if (largeChart) {
      largeChart.destroy();
      largeChart = null;
    }
  };

  // 添加对话框容器的引用
  const messagesContainer = ref(null);

  // 滚动到对话框底部的函数
  const scrollMessagesToBottom = () => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  };

  // 监听消息变化，自动滚动到底部
  watch(messages, () => {
    nextTick(() => {
      scrollMessagesToBottom();
    });
  }, { deep: true });

  // 获取ModelNodeGraph组件的引用
  const modelNodeGraphRef = ref(null);
  const enlargedModelNodeGraphRef = ref(null);

  // 放大图表相关状态
  const enlargedGraphVisible = ref(false);

  // 修改显示放大的ModelNodeGraph函数
  const showEnlargedGraph = () => {
    console.log('显示放大图表');
    enlargedGraphVisible.value = true;
    document.body.style.overflow = 'hidden';
    
    // 记录查看历史操作
    logUserAction(ACTION_TYPES.VIEW_HISTORY, {});
    
    // 使用 setTimeout 确保在 DOM 更新后再访问引用
    setTimeout(() => {
      console.log('弹出层显示后，enlargedModelNodeGraphRef:', enlargedModelNodeGraphRef.value);
      if (enlargedModelNodeGraphRef.value) {
        try {
          if (typeof enlargedModelNodeGraphRef.value.calculateTreeLayout === 'function' &&
              typeof enlargedModelNodeGraphRef.value.drawConnections === 'function') {
            enlargedModelNodeGraphRef.value.calculateTreeLayout();
            enlargedModelNodeGraphRef.value.drawConnections();
          } else {
            console.error('放大图表组件缺少必要的方法');
          }
        } catch (error) {
          console.error('访问放大图表组件方法时出错:', error);
        }
      } else {
        console.error('放大图表组件引用不存在');
      }
    }, 100); // 短暂延迟确保 DOM 已更新
  };

  // 修改隐藏放大的ModelNodeGraph
  const hideEnlargedGraph = () => {
    // 在隐藏前清除引用，防止访问已卸载的组件
    enlargedModelNodeGraphRef.value = null;
    enlargedGraphVisible.value = false;
    document.body.style.overflow = '';
  };

  // 控制弹窗显示的状态
  const showAddCoursesModal = ref(false);

  // 添加课程按钮的处理函数
  const addItems = () => {
    showAddCoursesModal.value = true;
  };

  // 关闭弹窗
  const closeAddCoursesModal = () => {
    showAddCoursesModal.value = false;
  };
  // 处理确认添加课程
  const handleConfirmAddCourses = (selectedCourses) => {
    
    // 记录添加前的课程数量
    const beforeCount = currentPreference.value.candidateItems.length;
    
    // 获取这次添加的课程的课程名（在添加到candidateItems之前）
    const addedCourseNames = [...new Set(selectedCourses.filter(course => 
      !currentPreference.value.candidateItems.some(item => 
        item['课程名'] === course['课程名'] &&
        item['主讲教师'] === course['主讲教师'] && 
        item['上课时间'] === course['上课时间']
      )).map(item => item['课程名']))];
    
    // 添加课程
    selectedCourses.forEach(course => {
      if (!currentPreference.value.candidateItems.some(item => 
        item['课程名'] === course['课程名'] &&
        item['主讲教师'] === course['主讲教师'] && 
        item['上课时间'] === course['上课时间']
      )) {
        // 确保新添加的课程有selected属性
        const newCourse = { ...course, selected: true };
        currentPreference.value.candidateItems.push(newCourse);
        updatePreferenceCoursesChange(newCourse, 'add');
      }
    });
    
    // 计算新增的课程数量
    const addedCount = currentPreference.value.candidateItems.length - beforeCount;
    

    
    // 如果有新增课程，创建新节点
    if (addedCount > 0) {
      // 新建一个节点
      addNewNode(false, false, [], true);
      clearCoursesChanges()
      // 添加课程选择消息
      messages.value.push({
        id: generateMessageId('text'),
        sender: 'You',
        type: 'text',
        text: `Add ${addedCourseNames.length}/${selectedCourses.length} courses.`
      })
      messages.value.push({ 
        id: generateMessageId('addCourses'),
        sender: 'Bot', 
        type: 'addCourses',
        content: {
          addedCount: addedCourseNames.length,
          totalCount: selectedCourses.length, // 修改为这次添加的课程总数
          courses: addedCourseNames.map(name => ({
            name: name,
            isRequired: false,
            // isRequired: beforeCount === 0 // 如果是第一次添加课程，默认全选
          })),
          isFirstTime: false,
          // isFirstTime: beforeCount === 0
        },
        confirmed: false
      });
      logUserAction(ACTION_TYPES.ADD_COURSES, {
        course_num: addedCount,
        course_name_list: addedCourseNames
      });
    }
    
    // 关闭弹窗
    closeAddCoursesModal();
    Promise.resolve().then(() => {
      setGlobalDisplayMode(DISPLAY_MODES.ALL);
      setVisibilityForItems(selectedCourses, DISPLAY_MODES.ALL);
    });
  };

  // 在组件卸载前清理引用
  onBeforeUnmount(() => {
    // 清理所有组件引用
    modelNodeGraphRef.value = null;
    enlargedModelNodeGraphRef.value = null;
  });

  // 添加判断课程是否为"新增"的函数
  const isAdded = (course) => {
    if (currentPreference.value.id === 0) return false;
    
    return (currentPreference.value.isIncremental === true ) && 
           !course.chosen_when_confirmed && 
           course.chosen;
  };

  // 添加判断课程是否为"删除"的函数
  const isDeleted = (course) => {
    if (currentPreference.value.id === 0) return false;
    
    return (currentPreference.value.isIncremental === true ) && 
           course.chosen_when_confirmed && 
           !course.chosen;
  };

  // 添加删除候选课程的方法
  const removeCandidateCourse = (course) => {
    // 显示确认对话框
    if (confirm(`确定要删除课程"${course['课程名']}"吗？删除后该课程将从候选课程列表中移除。`)) {
      // 从候选课程列表中移除
      const index = currentPreference.value.candidateItems.findIndex(item => 
        item['课程名'] === course['课程名'] &&
        item['主讲教师'] === course['主讲教师'] &&
        item['上课时间'] === course['上课时间']
      );
      
      if (index > -1) {
        currentPreference.value.candidateItems.splice(index, 1);
        
        // 记录课程变更
        updatePreferenceCoursesChange(course, 'remove');
        addUserMessage(`Delete course: ${course['课程名']} - ${course['主讲教师']} - ${course['上课时间']}`);
        
        // 记录用户操作日志 - 使用新的ACTION_TYPE
        logUserAction(ACTION_TYPES.DELETE_COURSE, {
          course_name: course['课程名'],
          instructor: course['主讲教师'],
          time: course['上课时间']
        });
        
        addNewNode(false, false, [], true);
        clearCoursesChanges()
        
        console.log(`已删除候选课程: ${course['课程名']}，剩余候选课程数量: ${currentPreference.value.candidateItems.length}`);
      }
    }
  };

  // 添加删除整个课程组的方法
  const removeCourseGroup = (courseName) => {
    // 找到所有相同课程名的课程
    const coursesToRemove = currentPreference.value.candidateItems.filter(item => 
      item['课程名'] === courseName
    );
    
    if (coursesToRemove.length === 0) {
      console.log(`没有找到课程名为 ${courseName} 的课程`);
      return;
    }
    
    // 显示确认对话框
    if (confirm(`确定要删除所有"${courseName}"课程吗？这将删除该课程名下的 ${coursesToRemove.length} 节课程。`)) {
      // 记录删除前的课程数量
      const beforeCount = currentPreference.value.candidateItems.length;
      
      // 删除所有相同课程名的课程
      coursesToRemove.forEach(course => {
        const index = currentPreference.value.candidateItems.findIndex(item => 
          item['课程名'] === course['课程名'] &&
          item['主讲教师'] === course['主讲教师'] &&
          item['上课时间'] === course['上课时间']
        );
        
        if (index > -1) {
          currentPreference.value.candidateItems.splice(index, 1);
          // 记录课程变更
          updatePreferenceCoursesChange(course, 'remove');
        }
      });
      addUserMessage(`Delete course group: ${courseName}`);
      
      // 计算删除的课程数量
      const deletedCount = beforeCount - currentPreference.value.candidateItems.length;
      
      // 记录用户操作日志 - 使用新的ACTION_TYPE
      logUserAction(ACTION_TYPES.DELETE_COURSE, {
        course_name: courseName,
        instructor: 'multiple',
        time: 'multiple',
        deleted_count: deletedCount
      });
      
      addNewNode(false, false, [], true);
      clearCoursesChanges()
      
      console.log(`已删除课程组 ${courseName}，删除了 ${deletedCount} 节课程，剩余候选课程数量: ${currentPreference.value.candidateItems.length}`);
    }
  };

  // 添加删除整个分组的方法
  const removeGroup = (group) => {
    // 获取该分组下的所有课程
    const groupCourses = getGroupCourses(group);
    
    if (groupCourses.length === 0) {
      console.log(`分组 ${group.name} 下没有课程`);
      return;
    }
    
    // 显示确认对话框
    const groupDisplayName = group.name.replace('的课程数量', '');
    if (confirm(`确定要删除分组"${groupDisplayName}"下的所有课程吗？这将删除 ${groupCourses.length} 节课程。`)) {
      // 记录删除前的课程数量
      const beforeCount = currentPreference.value.candidateItems.length;
      
      // 删除分组下的所有课程
      groupCourses.forEach(course => {
        const index = currentPreference.value.candidateItems.findIndex(item => 
          item['课程名'] === course['课程名'] &&
          item['主讲教师'] === course['主讲教师'] &&
          item['上课时间'] === course['上课时间']
        );
        
        if (index > -1) {
          currentPreference.value.candidateItems.splice(index, 1);
          // 记录课程变更
          updatePreferenceCoursesChange(course, 'remove');
        }
      });
      addUserMessage(`Delete course group: ${groupDisplayName}`);
      
      // 计算删除的课程数量
      const deletedCount = beforeCount - currentPreference.value.candidateItems.length;
      
      // 记录用户操作日志 - 使用新的ACTION_TYPE
      logUserAction(ACTION_TYPES.DELETE_COURSE, {
        course_name: groupDisplayName,
        instructor: 'multiple',
        time: 'multiple',
        deleted_count: deletedCount
      });
      
      addNewNode(false, false, [], true);
      clearCoursesChanges()
      
      console.log(`已删除分组 ${groupDisplayName}，删除了 ${deletedCount} 节课程，剩余候选课程数量: ${currentPreference.value.candidateItems.length}`);
    }
  };


  // 更新课程优先级的方法
  const updateCoursePriority = (course, newPriority) => {
    const priority = parseFloat(newPriority);
    if (isNaN(priority) || priority < 1 || priority > 5) {
      return; // 验证失败，不更新
    }
    
    // 记录更新前的优先级，用于日志记录
    const oldPriority = course.priority;
    
    // 更新优先级
    course.priority = priority;
    // 标记为用户设置
    course.priority_type = 'user';
    
    // 调用updatePreferenceCoursesChange记录课程变更
    updatePreferenceCoursesChange(course, 'rating', { rating: priority });
    
    // 记录用户操作日志
    logUserAction(ACTION_TYPES.UPDATE_COURSE_PRIORITY, {
      course: `${course['课程名']}_${course['主讲教师']}_${course['上课时间']}`,
      old_priority: oldPriority,
      new_priority: priority,
      priority_type: 'user'
    });
    addUserMessage(`Modify course priority: ${course['课程名']} - ${course['主讲教师']} - ${course['上课时间']} (${oldPriority}⭐->${priority}⭐)`);
    
    console.log(`已更新课程 ${course['课程名']} 的优先级为: ${priority}`);
  };

  // 监听当前方案索引的变化
  watch(currentSolutionIndex, (newIndex, oldIndex) => {
    if (oldIndex !== undefined && oldIndex !== newIndex) {
      // 获取当前方案中的课程
      const currentCourses = new Set();
      
      // 遍历课程表中的所有课程
      currentPreference.value.candidateItems.forEach(course => {
        if (course.chosen) {
          currentCourses.add(`${course['课程名']}-${course['主讲教师']}-${course['上课时间']}`);
        }
      });
      
      // 找出添加和删除的课程
      const addedCourses = [...currentCourses].filter(c => !previousSolutionCourses.value.has(c));
      const removedCourses = [...previousSolutionCourses.value].filter(c => !currentCourses.has(c));
      
      // 更新上一个方案的课程集合
      previousSolutionCourses.value = currentCourses;
      
      // 为变化的课程添加高亮类
      nextTick(() => {
        // 找到所有需要高亮的课程按钮
        const courseButtons = document.querySelectorAll('.course-button');
        courseButtons.forEach(button => {
          const courseText = button.textContent;
          // 检查这个按钮是否代表一个变化的课程
          const isChanged = [...addedCourses, ...removedCourses].some(changedCourse => {
            const [name, teacher, time] = changedCourse.split('-');
            return courseText.includes(name) && courseText.includes(teacher);
          });
          
          if (isChanged) {
            // 移除之前的动画类（如果有）
            button.classList.remove('highlight-change');
            // 触发重绘
            void button.offsetWidth;
            // 添加动画类
            button.classList.add('highlight-change');
          }
        });
      });
    }
  });

  // 监听candidateItems变化，确保所有课程都有selected属性
  watch(() => currentPreference.value.candidateItems, (newItems) => {
    if (newItems && Array.isArray(newItems)) {
      newItems.forEach(item => {
        if (item.selected === undefined) {
          item.selected = false;
        }
      });
    }
  }, { deep: true, immediate: true });

  // 当 filteredSolutions 变化时，重置 previousSolutionCourses
  watch(filteredSolutions, () => {
    // 重置当前解索引
    currentPreference.value.currentSolutionIndex = 0;
    // 初始化 previousSolutionCourses
    initializePreviousSolutionCourses(0);
  }, { immediate: true });



  // 获取显示模式的提示文本
  const getDisplayModeTitle = (courseName) => {
    const mode = getCourseDisplayStatus(courseName);
    switch (mode) {
      case DISPLAY_MODES.ALL:
        return '显示所有课程';
      case DISPLAY_MODES.CHOSEN:
        return '只显示已选课程';
      case DISPLAY_MODES.IMPORTANT:
        return '显示固定和未决定课程';
      default:
        return 'none';
    }
  };
  
  // 获取变更类型的中文文本
  const getChangeTypeText = (type) => {
    const typeMap = {
      'add': '添加',
      'remove': '删除',
      'update': '修改',
      'rating': '评分'
    };
    return typeMap[type] || type;
  };
    // 添加 sessionId 的 computed 属性
    const sessionId = computed(() => {
    return localStorage.getItem('sessionId') || 'Not Set';
  });

  // 添加保存数据相关的变量和函数
  const isSaving = ref(false);

  // 分组级别的全选功能
  const isGroupAllSelected = (group) => {
    const groupCourses = getGroupCourses(group);
    return groupCourses.length > 0 && groupCourses.every(course => course.selected);
  };

  const isGroupPartiallySelected = (group) => {
    const groupCourses = getGroupCourses(group);
    const selectedCount = groupCourses.filter(course => course.selected).length;
    return selectedCount > 0 && selectedCount < groupCourses.length;
  };

  const toggleGroupSelection = (group) => {
    console.log('toggleGroupSelection 被调用，group:', group);
    
    const groupCourses = getGroupCourses(group);
    const shouldSelect = !isGroupAllSelected(group);
    
    console.log('groupCourses:', groupCourses);
    console.log('shouldSelect:', shouldSelect);
    
    groupCourses.forEach(course => {
      course.selected = shouldSelect;
    });
    
    // 记录分组checkbox操作 - 使用COURSE_CARD_CHECK action type
    console.log('准备记录分组action log...');
    logUserAction(ACTION_TYPES.COURSE_CARD_CHECK, {
      course_name: group.name.replace('的课程数量', '课程'),
      new_state: shouldSelect ? 'checked' : 'unchecked'
    });
    console.log('分组action log 已记录');
    
    addUserMessage(`${shouldSelect ? 'Checked' : 'Unchecked'} course group: ${group.name}`);
  };

  // 课程组级别的全选功能
  const isCourseGroupAllSelected = (courseName) => {
    const coursesInGroup = currentPreference.value.candidateItems.filter(item => item['课程名'] === courseName);
    return coursesInGroup.length > 0 && coursesInGroup.every(course => course.selected);
  };

  const isCourseGroupPartiallySelected = (courseName) => {
    const coursesInGroup = currentPreference.value.candidateItems.filter(item => item['课程名'] === courseName);
    const selectedCount = coursesInGroup.filter(course => course.selected).length;
    return selectedCount > 0 && selectedCount < coursesInGroup.length;
  };

  const toggleCourseGroupSelection = (courseName) => {
    console.log('toggleCourseGroupSelection 被调用，courseName:', courseName);
    
    const coursesInGroup = currentPreference.value.candidateItems.filter(item => item['课程名'] === courseName);
    const shouldSelect = !isCourseGroupAllSelected(courseName);
    
    coursesInGroup.forEach(course => {
      course.selected = shouldSelect;
    });
    
    logUserAction(ACTION_TYPES.COURSE_CARD_CHECK, {
      course_name: courseName,
      new_state: shouldSelect ? 'checked' : 'unchecked'
    });
    
    addUserMessage(`${shouldSelect ? 'Checked' : 'Unchecked'} course group: ${courseName}`);
  };

  const saveCurrentData = async () => {
    if (isSaving.value) return;
    
    isSaving.value = true;
    
    try {
      // 使用新的统一保存接口
      await saveDataToBackend(messages.value, currentPreference.value, modelNodes.value);
      
      // 获取当前时间戳用于显示
      const timestamp = new Date().toLocaleString('zh-CN');
      
      // 添加成功消息到对话框
      messages.value.push({
        id: generateMessageId('text'),
        sender: 'Bot',
        text: `数据已成功保存！保存时间: ${timestamp}。数据以时间戳格式保存，不会覆盖历史记录。`,
        type: 'text',
      });
      
      // 记录用户操作日志
      logUserAction(ACTION_TYPES.SAVE_DATA, {
        message_count: messages.value.length,
        candidate_courses_count: currentPreference.value.candidateItems.length
      });
      
      console.log('数据保存成功');
      
    } catch (error) {
      console.error('保存数据失败:', error);
      
      // 添加错误消息到对话框
      messages.value.push({
        id: generateMessageId('text'),
        sender: 'Bot', 
        text: '保存数据失败，请稍后再试。',
        type: 'error',
        content: null,
        confirmed: false
      });
    } finally {
      isSaving.value = false;
    }
  };
  </script>
  
  <style scoped>
  .solutions-table {
    width: 100%;
    border-collapse: collapse;
  }

  .solutions-table th,
  .solutions-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
    position: relative; /* 添加相对定位以支持边框样式 */
  }

  .histogram-cell {
    width: 200px;
    padding: 0px;
    vertical-align: middle;
  }

  .histogram-container {
    height: fit-content;
    padding: 0px;
    padding-bottom: 0px;
    padding-top: 11px;
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    display: flex;
    align-items: flex-end;
    justify-content: center;
  }

  .histogram-bar {
    position: relative;
    transition: all 0.3s ease;
  }

  .bar-value {
    position: absolute;
    top: -10px;
    width: 100%;
    text-align: center;
    font-size: 8px;
  }

  .x-label {
    font-size: 8px;
    margin-top: 2px;  /* 给x-label添加一点上边距 */
    text-align: center;
  }

  .radar-chart-row {
    height: 60px; /* 设置行高 */
  }

  .radar-chart-cell {
    padding: 5px;
    height: 60px;
    position: relative;
    cursor: pointer; /* 添加指针样式 */
  }

  canvas {
    width: 50px !important;
    height: 50px !important;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  /* 修改当前选中方案的样式，只保留背景色 */
  .solutions-table td.current-solution {
    background-color: #e9eaeb;  /* 使用更柔和的浅蓝色背景 */
  }

  .large-chart-popup {
    position: fixed;
    z-index: 1000;
    background: white;
    padding: 15px;  /* 增加内边距 */
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    pointer-events: none;
  }

  .large-chart-popup canvas {
    width: 300px !important;  /* 修改为更大的尺寸 */
    height: 300px !important; /* 修改为更大的尺寸 */
    position: static;
    transform: none;
  }

  .messages {
    height: 500px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 4px;
    scroll-behavior: smooth; /* 添加平滑滚动效果 */
  }

  /* 重写chat-box布局以确保Dialog部分始终有足够空间 */
  .chat-box {
    display: flex;
    flex-direction: column;
    height: 100%; /* 确保占满容器高度 */
    min-height: 600px; /* 设置最小高度 */
  }

  /* 为Preference组件设置最大高度限制 */
  .chat-box > :nth-child(2) {
    /* Preference组件 */
    max-height: 40%; /* 最多占用40%的空间 */
    overflow-y: auto; /* 内容过多时滚动 */
    flex-shrink: 0; /* 防止被压缩得太小 */
  }

  /* 确保Dialog标题不被压缩 */
  .chat-box h3 {
    flex-shrink: 0;
    margin: 10px 0 5px 0;
    padding: 5px 10px;
  }

  /* 重新定义messages样式，使用flex布局而非固定高度 */
  .messages {
    flex: 1; /* 占用剩余空间 */
    min-height: 200px; /* 确保最小高度 */
    height: auto; /* 移除固定高度 */
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 4px;
    scroll-behavior: smooth;
    margin-bottom: 10px;
    padding: 10px;
    background-color: #fff;
  }

  /* 确保输入框不被压缩 */
  .input-box {
    flex-shrink: 0;
    margin-top: auto; /* 推到底部 */
  }

  .enlarged-graph-overlay {
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

  .enlarged-graph-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    width: 90%;
    height: 90%;
    max-width: 1200px;
    display: flex;
    flex-direction: column;
  }

  .enlarged-graph-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
  }

  .enlarged-graph-content {
    flex: 1;
    overflow: auto;
    padding: 20px;
  }

  .enlarged-graph-wrapper {
    width: 100%;
    height: 100%;
  }

  .enlarged-model-node-graph {
    height: 80vh !important; /* 覆盖原始组件的高度设置 */
    max-height: none !important;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
  }

  .close-button:hover {
    color: #000;
  }

  .enlarge-button {
    margin-left: 10px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    transition: background-color 0.3s;
  }

  .enlarge-button:hover {
    background-color: #e0e0e0;
  }

  .enlarge-icon {
    margin-right: 4px;
    font-size: 14px;
  }

  /* 添加课程组控制相关样式 */
  .course-group-controls {
    display: flex;
    align-items: center;
    gap: 4px; /* 减小按钮之间的间距 */
    width: 100%; /* 确保控制区域占满整个宽度 */
    padding: 4px 0; /* 添加上下内边距 */
  }

  .course-group-btn {
    flex: 0.8;  
    text-align: left;
    margin-left: 0px;
    background: none;
    cursor: pointer;
    font-weight: bold;
    color: #333;
    display: flex;
    align-items: center;
    justify-content: flex-start; /* 从space-between改为flex-start，保证文本左对齐 */
    transition: all 0.3s ease;
    max-width: 200px; /* 添加最大宽度限制 */
    overflow: hidden; /* 处理文本溢出 */
    text-overflow: ellipsis; /* 文本溢出时显示省略号 */
    white-space: nowrap; /* 防止文本换行 */
    font-size: 12px;
  }

  .course-group-btn:hover {
    background-color: #f5f5f5;
    border-color: #999; /* 鼠标悬停时边框颜色加深 */
  }

  .course-group-btn.active {
    color: green;
    border-color: green; /* 激活状态时边框颜色为蓝色 */
  }

  .visibility-icon {
    margin-left: 8px;
    font-size: 16px;
  }

  .toggle-all-btn {
    border: none;
    margin-left: 12px;
  }

  .toggle-fold-btn  {
    width: 22px;
    height: 22px;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 10px;
    display: flex;
    align-items: center;
    transition: all 0.2s ease;
  }

  .toggle-fold-btn:hover {
    background: none;
  }

  .group-fold-btn {
    margin-right: 8px;
    color: #666;
    font-weight: bold;
  }

  .group-fold-btn:hover {
    color: #333;
    background-color: #f0f0f0;
    border-radius: 3px;
  }

  .course-group-header {
    background-color: #f5f5f5 !important;
    border: none !important;
    margin-bottom: 8px;
  }

  .course-group-header:hover {
    background-color: #f0f0f0;
  }

  /* 调整现有样式 */
  .filter-button {
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 0px;
  }


  .course-display-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 10px;
  }

  .course-toggle-btn {
    padding: 4px 8px;
    background-color: #f1f1f1;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
  }

  .course-toggle-btn.active {
    background-color: #e3f2fd;
    border-color: #1976D2;
    color: #1976D2;
  }

  .modal-info-content {
    white-space: pre-line;
    line-height: 1.5;
  }

  .info-btn {
    width: 22px;
    height: 22px;
    background: none;
    border: 1px solid #ccc;
    border-radius: 50%;
    cursor: pointer;
    font-size: 12px;
    font-weight: bold;
    font-style: italic;
    color: #666;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .info-btn:hover {
    background-color: #f0f0f0;
    border-color: #999;
    color: #333;
  }

  /* 添加闪烁动画 */
  @keyframes highlight-change {
    0% { background-color: rgba(255, 255, 0, 0.3); }
    50% { background-color: rgba(255, 255, 0, 0.7); }
    100% { background-color: rgba(255, 255, 0, 0.3); }
  }

  .highlight-change {
    animation: highlight-change 1.5s ease-in-out;
  }

  /* 删除按钮相关样式 - 已改为卡片布局，删除旧样式 */
  
  /* 新增卡片式课程样式 */
  .course-group-header-card {
    background-color: #f9f9f9;
    padding: 5px 10px;
    margin-bottom: 5px;
    border-radius: 5px;
    border: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .course-group-header-card .course-group-btn {
    flex: 1; /* 让按钮占据更多空间 */
    text-align: left;
    margin-left: 0;
    font-size: 14px;
    font-weight: bold;
    color: #333;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .course-group-header-card .course-group-btn:hover {
    background-color: #f0f0f0;
    border-color: #999;
  }

  .course-group-header-card .course-group-btn.active {
    color: green;
    border-color: green;
  }

  .course-group-header-card .visibility-icon {
    margin-left: 10px;
    font-size: 18px;
  }

  .course-cards-container {
    display: flex;
    flex-direction: column;
    gap: 8px; /* 卡片之间的间距 */
    padding: 0 10px 10px 10px; /* 卡片与标题之间的间距 */
    margin-bottom: 10px;
  }

  .course-card {
    background-color: #fff;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    gap: 8px; /* 卡片内容之间的间距 */
    position: relative;
    min-height: 80px;
  }

  .course-card:hover {
    background-color: #f8f9fa;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    transform: translateY(-1px); /* 轻微浮起效果 */
  }

  /* 不同课程状态的卡片样式 */
  .course-card.chosen {
    background-color: #f8fff8;
    font-weight: bold; /* chosen 状态字体加粗 */
  }

  .course-card.chosen:hover {
    background-color: #f0f8f0; /* 更协调的绿色悬停 */
  }

  .course-card.userSelected:not(.blocked) {
    border: 2px solid #1a73e8; /* 与 course-button 一致的边框样式 */
    background-color: #f3f8ff;
  }
  .course-card.userSelected.blocked {
    border: 2px solid #1a73e8;
    background-color: #1a73e8 !important; /* userSelected 且 blocked 时为蓝色 */
  }

  .course-card.userSelected:hover {
    background-color: #e8f2ff; /* 更协调的蓝色悬停 */
  }

  .course-card.fixed {
    background-color: #003366e4; /* 背景黑色 */
    color: #fff !important; /* 字体白色，使用!important确保优先级 */
  }

  .course-card.fixed:hover {
    background-color: #003366e4; /* 背景黑色 */
    color: #fff !important; /* 字体白色，使用!important确保优先级 */
  }

  .course-card.fixed .info-label,
  .course-card.fixed .info-value,
  .course-card.fixed .priority-label {
    color: #fff !important; /* 确保所有文本元素都是白色 */
  }

  .course-card.undecided {
    background-color: #fff8d4; /* 与 course-button 一致的浅黄色背景 */
  }

  .course-card.undecided:hover {
    background-color: #fff2c7; /* 更协调的黄色悬停 */
  }

  .course-card.blocked {
    background-color: #f0f0f0; /* 与 course-button 一致的浅灰色背景 */
  }

  .course-card.blocked:hover {
    background-color: #e8e8e8; /* 更协调的灰色悬停 */
  }

  /* 非chosen状态的课程颜色变灰 */
  .course-card:not(.chosen) {
    color: #808080;
  }

  /* checkmark 样式 */
  .checkmarkcard{
    position: absolute;
    bottom: 8px;
    right: 8px;
    font-size: 20px;
    color: white;
    /* color: #1a73e8; */
    font-weight: bold;
    
  }

  .course-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
  }

  .priority-section {
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .priority-label {
    font-size: 12px;
    color: #555;
  }

  .priority-input-card {
    width: 50px;
    padding: 4px 6px;
    border: 1px solid #ddd;
    border-radius: 4px;
    text-align: center;
    font-size: 12px;
    transition: all 0.2s ease;
  }

  .priority-input-card.default {
    background-color: #f5f5f5;
    color: #666;
    border-color: #ccc;
  }

  .priority-input-card.user {
    background-color: #e3f2fd;
    color: #1976d2;
    border-color: #1976d2;
    font-weight: 500;
  }

  .priority-input-card:focus {
    outline: none;
    border-width: 2px;
  }

  .priority-input-card.default:focus {
    border-color: #999;
  }

  .priority-input-card.user:focus {
    border-color: #1565c0;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
  }

  .priority-input-card:hover {
    border-color: #888;
  }

  .priority-input-card.user:hover {
    border-color: #1565c0;
  }

  /* 星级评分样式 */
  .star-rating {
    display: flex;
    align-items: center;
    gap: 2px;
    cursor: pointer;
  }

  .star {
    font-size: 16px;
    color: #ddd;
    transition: all 0.2s ease;
    cursor: pointer;
    user-select: none;
  }

  .star.active {
    color: #ffc107;
  }

  .star.active.user-set {
    color: #ff5900;
  }

  /* 简单的悬停效果 */
  .star:hover {
    color: #ffeb3b !important;
    transform: scale(1.1);
  }
     
   /* 状态标签样式 */
   .status-tag {
     position: absolute;
     top: 4px;
     left: 4px;
     font-size: 10px;
     font-weight: bold;
     padding: 2px 6px;
     border-radius: 4px;
     z-index: 10;
     line-height: 1;
     color: white;
     pointer-events: none; /* 防止标签影响点击 */
   }

   /* 新增：legend中的状态标签样式，不使用绝对定位 */
   .legend-status-tag {
     font-size: 10px;
     font-weight: bold;
     padding: 2px 6px;
     border-radius: 4px;
     line-height: 1;
     color: white;
     flex-shrink: 0; /* 防止标签被压缩 */
   }

   .added-tag {
     background-color: #4caf50; /* 绿色背景 */
     color: white;
   }

   .removed-tag {
     background-color: #f44336; /* 红色背景 */
     color: white;
   }

   .delete-course-btn-card {
     background-color: #ff4d4f;
     color: white;
     border: none;
     border-radius: 50%;
     width: 22px;
     height: 22px;
     font-size: 14px;
     font-weight: bold;
     cursor: pointer;
     display: flex;
     align-items: center;
     justify-content: center;
     transition: all 0.3s ease;
     opacity: 0; /* 默认隐藏 */
     transform: scale(0.7); /* 默认稍微缩小 */
     margin: 0 auto; /* 居中显示 */
     line-height: 1;
   }

   .course-card:hover .delete-course-btn-card {
     opacity: 0.8; /* 悬停时显示 */
     transform: scale(1); /* 悬停时恢复正常大小 */
   }

   .delete-course-btn-card:hover {
     background-color: #ff7875;
     opacity: 1 !important;
     transform: scale(1.15);
     box-shadow: 0 2px 6px rgba(255, 77, 79, 0.4);
   }

   .delete-course-btn-card:active {
     transform: scale(0.95);
     box-shadow: 0 1px 3px rgba(255, 77, 79, 0.3);
   }
     
   .course-card-content {
    display: flex;
    flex-direction: column;
    gap: 6px; /* 卡片内容之间的间距 */
  }

  .course-info-row {
    display: flex;
    align-items: flex-start;
    font-size: 13px;
    line-height: 1.4;
  }

  .info-label {
    font-weight: 600;
    color: #333;
    min-width: 80px;
    margin-right: 8px;
    flex-shrink: 0;
  }

  .info-value {
    font-weight: 400;
    color: #666;
    flex: 1;
    word-wrap: break-word;
    word-break: break-all;
  }

  /* chosen状态下的卡片内容加粗 */
  .course-card.chosen .info-label {
    font-weight: bold;
  }

  .course-card.chosen .info-value {
    font-weight: bold;
  }

  .course-card.chosen .priority-label {
    font-weight: bold;
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .course-info-row {
      flex-direction: column;
      gap: 2px;
    }
    
    .info-label {
      min-width: auto;
      margin-right: 0;
      font-size: 12px;
    }
    
    .info-value {
      font-size: 12px;
      margin-left: 10px;
    }
    
    .course-card {
      padding: 10px;
    }
    
    .priority-input-card {
      width: 45px;
    }
  }

  /* 保存数据按钮样式 */
  .save-data-btn {
    background-color: #a5abb3;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.3s ease;
    min-width: 120px;
    justify-content: center;
  }

  .save-data-btn:hover:not(:disabled) {
    background-color: #1557b0;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
  }

  .save-data-btn:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: 0 1px 4px rgba(26, 115, 232, 0.2);
  }

  .save-data-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  .save-data-btn:disabled:hover {
    background-color: #cccccc;
    transform: none;
  }

  /* 分组相关样式 */
  .group-header {
    background-color: #f5f5f5 !important;
    border: none !important;
    margin-bottom: 8px;
  }

  .group-label {
    font-size: 14px;
    font-weight: bold;
    color: #1976d2;
    margin-right: 8px;
  }

  .group-display-btn {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 3px;
    transition: background-color 0.3s;
  }

  .group-display-btn:hover {
    background-color: #e0e0e0;
  }

  /* 分组下的课程样式调整 - 只对分组内的课程添加缩进 */
  .grouped-course-header {
    margin-left: 20px;
    border-left: 3px solid #e3f2fd;
  }

  .grouped-course-cards {
    margin-left: 20px;
  }

  /* 删除课程组按钮样式 */
  .delete-course-group-btn {
    background-color: #ff4d4f;
    color: white;
    border: none;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    opacity: 0; /* 默认隐藏 */
    transform: scale(0.7); /* 默认稍微缩小 */
    line-height: 1;
    margin-left: 4px;
  }

  /* 当鼠标悬停在课程组控制区域时显示删除按钮 */
  .course-group-controls:hover .delete-course-group-btn {
    opacity: 0.8; /* 悬停时显示 */
    transform: scale(1); /* 悬停时恢复正常大小 */
  }

  .delete-course-group-btn:hover {
    background-color: #ff7875;
    opacity: 1 !important;
    transform: scale(1.15);
    box-shadow: 0 2px 6px rgba(255, 77, 79, 0.4);
  }

  .delete-course-group-btn:active {
    transform: scale(0.95);
    box-shadow: 0 1px 3px rgba(255, 77, 79, 0.3);
  }

  /* Checkbox 相关样式 */
  .course-checkbox-container {
    display: flex;
    align-items: center;
    margin-right: 8px;
    flex-shrink: 0;
  }

  .group-checkbox-container {
    display: flex;
    align-items: center;
    margin-right: 12px;
    flex-shrink: 0;
  }

  .course-checkbox, .course-group-checkbox, .group-checkbox {
    width: 12px;
    height: 12px;
    border: 2px solid #ddd;
    border-radius: 3px;
    background-color: white;
    cursor: pointer;
    transition: all 0.2s ease;
    margin: 0;
    flex-shrink: 0;
  }

  .course-checkbox:checked, .course-group-checkbox:checked, .group-checkbox:checked {
    background-color: #1a73e8;
    border-color: #1a73e8;
  }

  .course-checkbox:hover, .course-group-checkbox:hover, .group-checkbox:hover {
    border-color: #1a73e8;
    box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.1);
  }

  .course-checkbox:indeterminate, .course-group-checkbox:indeterminate, .group-checkbox:indeterminate {
    background-color: #1a73e8;
    border-color: #1a73e8;
  }

  /* 调整课程卡片布局以适应checkbox */
  .course-card {
    background-color: #fff;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    gap: 8px;
    position: relative;
    min-height: 80px;
  }

  .course-card .course-card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .course-card-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
    position: relative;
  }

  /* 调整分组控制区域的布局 */
  .course-group-controls {
    display: flex;
    align-items: right;
    gap: 4px; /* 减小按钮之间的间距 */
    width: 100%; /* 确保控制区域占满整个宽度 */
    padding: 4px 0; /* 添加上下内边距 */
  }

  .course-group-btn {
    flex: 0.8;  
    text-align: left;
    margin-left: 0px;
    background: none;
    cursor: pointer;
    font-weight: bold;
    color: #333;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    transition: all 0.3s ease;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 12px;
  }

  /* 课程状态说明样式 */
  .course-status-legend {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 16px 0;
    margin-bottom: 2px;
    font-size: 13px;
    text-align: left;
  }
  .course-status-legend h4 {
    text-align: left;
  }

  /* 新增：横向排布容器样式 */
  .legend-items-container {
    display: flex;
    gap: 20px; /* 两个legend-items之间的间距 */
    align-items: flex-start; /* 顶部对齐 */
  }

  .course-status-legend .legends{
    display: flex;
    flex-direction: row;
    gap: 16px;
  }

  .course-status-legend h4 {
    margin: 0 0 8px 0;
    color: #495057;
    font-size: 14px;
    font-weight: 600;
  }

  .legend-items {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .legend-color {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #dee2e6;
  }

  .fixed-color {
    background-color: #003366;
  }

  .undecided-color {
    background-color: #fff8d4;
  }

  .blocked-color {
    background-color: #f0f0f0;
  }

  .legend-item span {
    color: #495057;
    font-size: 12px;
    white-space: nowrap;
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .legend-items {
      flex-direction: column;
      gap: 8px;
    }
    
    .legend-item {
      gap: 6px;
    }
    
    .legend-color {
      width: 14px;
      height: 14px;
    }
    
    .legend-item span {
      font-size: 11px;
    }
  }
  .course-operation-legend-container{
    flex:0.8;
  }
  /* 课程操作方式说明样式 */
  .course-operation-legend {
    background-color: #f0f8ff; /* 使用浅蓝色背景，与课程状态说明区分 */
    border: 1px solid #b3d9ff;
    border-radius: 6px;
    font-size: 13px;
    height: 100px;
    padding: 10px 12px;
    margin-bottom: 4px;
  }

  .course-operation-legend h4 {
    margin: 0 0 8px 0;
    color: #1976d2;
    font-size: 14px;
    font-weight: 600;
  }

  .course-operation-legend .legend-items {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .course-operation-legend .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .legend-icon {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: bold;
    color: white;
    flex-shrink: 0;
  }

  .select-icon {
    background-color: #1a73e8; /* 蓝色背景，与选择状态一致 */
  }

  .remove-icon {
    background-color: #dc3545; /* 红色背景，与删除操作一致 */
  }

  .course-operation-legend .legend-item span {
    color: #495057;
    font-size: 12px;
    line-height: 1.4;
  }

  /* 课程说明容器 - 横向排布 */
  .course-legend-container {
    gap: 16px;
  }

  /* 课程状态说明样式 - 横向排布优化 */
  .course-status-legend {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 10px 12px;
    flex: 1;
    min-width: 300px; /* 设置最小宽度 */
    font-size: 12px;
  }

  .course-status-legend h4 {
    margin: 0 0 6px 0;
    color: #495057;
    font-size: 13px;
    font-weight: 600;
  }

  .course-status-legend .legend-items {
    display: flex;
    flex-direction: column;
    gap: 4px; /* 减少项目间距 */
  }

  .course-status-legend .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .course-status-legend .legend-color {
    width: 14px; /* 减小颜色方块尺寸 */
    height: 14px;
    border-radius: 2px;
    border: 1px solid #dee2e6;
    flex-shrink: 0;
  }

  .fixed-color {
    background-color: #003366;
  }

  .undecided-color {
    background-color: #fff8d4;
  }

  .blocked-color {
    background-color: #f0f0f0;
  }

  .course-status-legend .legend-item span {
    color: #495057;
    font-size: 11px; /* 减小字体大小 */
    white-space: nowrap;
    line-height: 1.2;
  }

  .legend-icon {
    width: 16px; /* 减小图标尺寸 */
    height: 16px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    color: white;
    flex-shrink: 0;
  }

  .select-icon {
    background-color: #1a73e8; /* 蓝色背景，与选择状态一致 */
  }

  .remove-icon {
    background-color: #dc3545; /* 红色背景，与删除操作一致 */
  }

  .course-operation-legend .legend-item span {
    color: #495057;
    font-size: 11px; /* 减小字体大小 */
    line-height: 1.2;
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .course-legend-container {
      flex-direction: column;
      gap: 8px;
    }
    
    .course-status-legend,
    .course-operation-legend {
      min-width: auto;
      padding: 8px 10px;
    }
    
    .course-status-legend .legend-items,
    .course-operation-legend .legend-items {
      gap: 3px;
    }
    
    .course-status-legend .legend-color {
      width: 12px;
      height: 12px;
    }
    
    .legend-icon {
      width: 14px;
      height: 14px;
      font-size: 10px;
    }
    
    .course-status-legend .legend-item span,
    .course-operation-legend .legend-item span {
      font-size: 10px;
    }
  }
  
  /* 变更信息面板样式 */
  .changes-panel {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    margin: 12px 0;
    padding: 16px;
    max-height: 300px;
    overflow-y: auto;
  }
  
  .changes-panel h4 {
    margin: 0 0 12px 0;
    color: #495057;
    font-size: 14px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .changes-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .change-section {
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 12px;
  }
  
  .change-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-weight: 600;
    color: #495057;
    font-size: 13px;
  }
  
  .change-icon {
    font-size: 16px;
  }
  
  .change-title {
    flex: 1;
  }
  
  .change-items {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  
  .change-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    background-color: #f8f9fa;
    border-radius: 4px;
    font-size: 12px;
  }
  
  .change-type {
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 600;
    color: white;
    min-width: 40px;
    text-align: center;
  }
  
  .change-type-add {
    background-color: #28a745;
  }
  
  .change-type-remove {
    background-color: #dc3545;
  }
  
  .change-type-update {
    background-color: #ffc107;
    color: #212529;
  }
  
  .change-type-rating {
    background-color: #17a2b8;
  }
  
  .change-detail {
    flex: 1;
    color: #495057;
  }
  
  .change-rating {
    color: #ffc107;
    font-weight: 600;
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .changes-panel {
      padding: 12px;
      margin: 8px 0;
    }
    
    .change-section {
      padding: 8px;
    }
    
    .change-header {
      font-size: 12px;
    }
    
    .change-item {
      font-size: 11px;
      padding: 4px 6px;
    }
    
    .change-type {
      font-size: 9px;
      min-width: 35px;
    }
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
    .course-legend-container {
      flex-direction: column;
      gap: 8px;
    }
    
    .course-status-legend,
    .course-operation-legend {
      min-width: auto;
      padding: 8px 10px;
    }
    
    .course-status-legend .legend-items,
    .course-operation-legend .legend-items {
      gap: 3px;
    }
    
    .course-status-legend .legend-color {
      width: 12px;
      height: 12px;
    }
    
    .legend-icon {
      width: 14px;
      height: 14px;
      font-size: 10px;
    }
    
    .course-status-legend .legend-item span,
    .course-operation-legend .legend-item span {
      font-size: 10px;
    }
  }

  /* Save Button 样式 */
  .save-button-container {
    display: flex;
    justify-content: right;
    margin: 5px 0;
    padding: 0 5px;
  }

  .save-button {
    width: 140px;
    background-color: #4a6fa5;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(74, 111, 165, 0.2);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .save-button:hover {
    background-color: #3a5a8a;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
  }

  .save-button:active {
    transform: translateY(0);
  }

  /* 课表单元格悬浮控制样式 */
  .schedule-cell {
    position: relative;
  }
  .slot-control {
    position: absolute;
    top: 2px;
    right: 2px;
    display: flex;
    gap: 4px;
    z-index: 5;
  }
  .slot-control-btn {
    padding: 2px 6px;
    font-size: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #f8f9fa;
    cursor: pointer;
  }
  .slot-control-btn:hover {
    background: #e9ecef;
  }

  /* 显示模式下拉菜单样式 */
  .dropdown-wrapper {
    position: relative;
    display: inline-block;
  }
  .display-menu {
    position: absolute;
    top: 28px;
    right: 0;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    z-index: 20;
    min-width: 160px;
    padding: 6px 0;
  }
  .display-menu-item {
    font-size: 12px;
    padding: 6px 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    white-space: nowrap;
  }
  .display-menu-item:hover {
    background: #f5f5f5;
  }
  .menu-check {
    margin-left: auto;
    color: #1a73e8;
    font-weight: 700;
  }
  </style>
  
  

