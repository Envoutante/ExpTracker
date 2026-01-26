<template>
  <div>
    <h2 style="margin-bottom: 20px;">📅 实验日历</h2>
    
    <!-- 快速跳转 -->
    <el-card style="margin-bottom: 20px;">
      <div style="display: flex; align-items: center; gap: 16px;">
        <span style="font-weight: 500;">快速跳转：</span>
        <el-date-picker
          v-model="selectedDate"
          type="month"
          placeholder="选择年月"
          format="YYYY年MM月"
          value-format="YYYY-MM"
          style="width: 200px;"
        />
        <el-button @click="jumpToToday" type="primary" plain>
          <el-icon><Calendar /></el-icon>
          回到今天
        </el-button>
        <div style="flex: 1;"></div>
        <el-tag type="info" effect="plain">
          共 {{ experiments.length }} 个实验
        </el-tag>
      </div>
    </el-card>

    <el-calendar v-model="selectedDate">
      <template #date-cell="{ data }">
        <div class="calendar-day" @click="showDayExperiments(data.day)">
          <div class="day-number">{{ data.day.split('-').slice(-1)[0] }}</div>
          <div v-if="getExperimentsForDay(data.day).length > 0" class="experiment-dots">
            <el-badge :value="getExperimentsForDay(data.day).length" type="primary" />
          </div>
        </div>
      </template>
    </el-calendar>

    <el-drawer
      v-model="drawerVisible"
      :title="`${selectedDayFormatted} 的实验`"
      size="50%"
    >
      <div v-if="selectedDayExperiments.length === 0" style="text-align: center; color: #909399; padding: 40px;">
        这一天没有实验记录
      </div>
      <el-timeline v-else>
        <el-timeline-item
          v-for="exp in selectedDayExperiments"
          :key="exp.id"
          :timestamp="formatTime(exp.created_at)"
          placement="top"
        >
          <el-card>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <h4 style="margin: 0 0 8px 0;">{{ exp.name }}</h4>
                <div style="font-size: 14px; color: #606266;">
                  <span v-if="exp.algorithm">算法: {{ exp.algorithm }}</span>
                  <span v-if="exp.map" style="margin-left: 16px;">地图: {{ exp.map }}</span>
                  <span v-if="exp.environment" style="margin-left: 16px;">环境: {{ exp.environment }}</span>
                </div>
                <div style="margin-top: 8px;">
                  <el-tag v-if="exp.status === 'running'" type="primary" size="small">运行中</el-tag>
                  <el-tag v-else-if="exp.status === 'completed'" type="success" size="small">已完成</el-tag>
                  <el-tag v-else-if="exp.status === 'failed'" type="danger" size="small">失败</el-tag>
                </div>
              </div>
              <div>
                <el-button size="small" @click="viewExperiment(exp.id)">查看详情</el-button>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { experimentApi } from '../api/experiments'
import { ElMessage } from 'element-plus'
import { Calendar } from '@element-plus/icons-vue'

const router = useRouter()

const selectedDate = ref(new Date())
const experiments = ref([])
const drawerVisible = ref(false)
const selectedDay = ref('')

const selectedDayExperiments = computed(() => {
  return getExperimentsForDay(selectedDay.value)
})

const selectedDayFormatted = computed(() => {
  if (!selectedDay.value) return ''
  return new Date(selectedDay.value).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const loadExperiments = async () => {
  try {
    const { data } = await experimentApi.getExperiments({
      page: 1,
      per_page: 1000
    })
    experiments.value = data.experiments
  } catch (error) {
    ElMessage.error('加载实验数据失败')
  }
}

const getExperimentsForDay = (day) => {
  return experiments.value.filter(exp => {
    if (!exp.created_at) return false
    const expDate = new Date(exp.created_at).toISOString().split('T')[0]
    return expDate === day
  })
}

const showDayExperiments = (day) => {
  selectedDay.value = day
  drawerVisible.value = true
}

const jumpToToday = () => {
  selectedDate.value = new Date()
}

const viewExperiment = (id) => {
  router.push(`/experiment/${id}?mode=view`)
  drawerVisible.value = false
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadExperiments()
})
</script>

<style scoped>
.calendar-day {
  height: 100%;
  padding: 4px;
  cursor: pointer;
  position: relative;
}

.calendar-day:hover {
  background: #f0f9ff;
}

.day-number {
  font-size: 14px;
}

.experiment-dots {
  position: absolute;
  top: 4px;
  right: 4px;
}

:deep(.el-calendar-table .el-calendar-day) {
  height: 80px;
}
</style>
