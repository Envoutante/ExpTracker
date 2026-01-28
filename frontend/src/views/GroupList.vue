<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="16">
        <h2 style="margin: 0;">实验组列表</h2>
      </el-col>
      <el-col :span="4">
        <el-segmented v-model="viewMode" :options="viewModeOptions" size="default" style="width: 100%;">
          <template #default="{ item }">
            <div style="display: flex; align-items: center; justify-content: center; padding: 4px 12px;">
              <el-icon style="margin-right: 4px;">
                <component :is="item.icon" />
              </el-icon>
              <span>{{ item.label }}</span>
            </div>
          </template>
        </el-segmented>
      </el-col>
      <el-col :span="4">
        <el-button type="primary" @click="createNew" style="width: 100%;">
          <el-icon><CirclePlus /></el-icon>
          新建实验组
        </el-button>
      </el-col>
    </el-row>

    <div v-if="selectedGroups.length > 0" style="margin-bottom: 16px;">
      <el-alert type="info" :closable="false">
        <template #default>
          <span>已选中 {{ selectedGroups.length }} 个实验组</span>
          <el-button 
            type="danger" 
            size="small" 
            style="margin-left: 16px;"
            @click="batchDelete"
          >
            批量删除
          </el-button>
        </template>
      </el-alert>
    </div>

    <!-- 列表视图 -->
    <el-table 
      v-if="viewMode === 'list'" 
      :data="groups" 
      stripe 
      style="width: 100%" 
      v-loading="loading"
      @selection-change="handleSelectionChange"
      @select-all="handleSelectAll"
      @row-click="handleRowClick"
      @sort-change="handleSortChange"
      :row-style="{ cursor: 'pointer' }"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="实验组名称" min-width="250" show-overflow-tooltip />
      <el-table-column prop="experiment_count" label="实验结果数量" width="150" />
      <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click.stop="viewGroup(row)">查看</el-button>
          <el-button size="small" type="primary" @click.stop="editGroup(row.id)">编辑</el-button>
          <el-button size="small" type="danger" @click.stop="deleteGroup(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 卡片视图 -->
    <div v-else v-loading="loading" class="card-view-container">
      <div class="groups-grid">
        <div 
          v-for="group in groups" 
          :key="group.id" 
          class="group-card"
          @click="viewGroup(group)"
        >
          <div class="card-header">
            <div class="card-title-row">
              <el-checkbox 
                :model-value="isGroupSelected(group)"
                @change="toggleGroupSelection(group, $event)"
                @click.stop
                class="card-checkbox"
              />
              <h3 class="card-title">{{ group.name }}</h3>
            </div>
            <el-tag size="small" type="info">ID: {{ group.id }}</el-tag>
          </div>
          
          <div class="card-body">
            <div class="card-info-item" v-if="group.description">
              <div class="info-label">
                <el-icon><Document /></el-icon>
                描述
              </div>
              <div class="info-content">{{ truncateText(group.description, 100) }}</div>
            </div>
            
            <div class="card-info-item" v-if="group.purpose">
              <div class="info-label">
                <el-icon><Flag /></el-icon>
                目的
              </div>
              <div class="info-content">{{ truncateText(group.purpose, 100) }}</div>
            </div>
            
            <!-- 如果没有描述和目的，显示占位符 -->
            <div v-if="!group.description && !group.purpose" class="card-empty-hint">
              <el-icon><Document /></el-icon>
              <span>暂无描述或目的信息</span>
            </div>
            
            <div class="card-meta">
              <div class="meta-item">
                <el-icon><Files /></el-icon>
                <span>{{ group.experiment_count || 0 }} 个实验</span>
              </div>
              <div class="meta-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ formatDate(group.created_at) }}</span>
              </div>
            </div>
            
            <div class="card-preview" v-if="getObservationsPreview(group.observations) || getObservationsImages(group.observations).length > 0">
              <div class="preview-header">
                <div class="preview-label">
                  <el-icon><View /></el-icon>
                  观察记录
                </div>
                <div class="preview-time" v-if="getObservationsLastUpdated(group.observations)">
                  <el-icon><Clock /></el-icon>
                  {{ getObservationsLastUpdated(group.observations) }}
                </div>
              </div>
              <div class="preview-content" v-if="getObservationsPreview(group.observations)">{{ truncateText(getObservationsPreview(group.observations), 80) }}</div>
              <div class="preview-images" v-if="getObservationsImages(group.observations).length > 0" @click.stop>
                <el-image 
                  v-for="(img, idx) in getObservationsImages(group.observations).slice(0, 3)" 
                  :key="idx" 
                  :src="img" 
                  :preview-src-list="getObservationsImages(group.observations)"
                  :initial-index="idx"
                  class="preview-image"
                  fit="cover"
                  preview-teleported
                />
                <div v-if="getObservationsImages(group.observations).length > 3" class="more-images">
                  +{{ getObservationsImages(group.observations).length - 3 }}
                </div>
              </div>
            </div>
            
            <div class="card-preview" v-if="group.conclusion" style="background: #f0f9ff; border-left: 3px solid #409eff;">
              <div class="preview-label" style="color: #409eff;">
                <el-icon><Memo /></el-icon>
                结论
              </div>
              <div class="preview-content" style="color: #303133;">{{ truncateText(group.conclusion, 80) }}</div>
            </div>
          </div>
          
          <div class="card-footer" @click.stop>
            <el-button size="small" @click="viewGroup(group)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" type="primary" @click="editGroup(group.id)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteGroup(group.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>
      
      <el-empty v-if="groups.length === 0 && !loading" description="暂无实验组" />
    </div>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="margin-top: 20px; justify-content: center;"
      @current-change="loadGroups"
      @size-change="loadGroups"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { experimentApi } from '../api/experiments'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  CirclePlus, 
  List, 
  Grid,
  Document,
  Flag,
  Files,
  Calendar,
  View,
  Edit,
  Delete,
  Memo,
  Clock
} from '@element-plus/icons-vue'

const router = useRouter()

const groups = ref([])
const loading = ref(false)
const selectedGroups = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const sortOrder = ref('desc') // 默认降序（最新的在前）
const viewMode = ref('list') // 'list' 或 'card'

const viewModeOptions = [
  { label: '列表', value: 'list', icon: List },
  { label: '卡片', value: 'card', icon: Grid }
]

const isGroupSelected = (group) => {
  return selectedGroups.value.some(g => g.id === group.id)
}

const toggleGroupSelection = (group, checked) => {
  if (checked) {
    if (!isGroupSelected(group)) {
      selectedGroups.value.push(group)
    }
  } else {
    selectedGroups.value = selectedGroups.value.filter(g => g.id !== group.id)
  }
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 从观察记录中提取文本预览
const getObservationsPreview = (observations) => {
  if (!observations) return ''
  
  try {
    // 尝试解析 JSON 格式的观察记录
    const parsed = JSON.parse(observations)
    if (parsed.text) {
      return parsed.text
    }
  } catch (e) {
    // 如果不是 JSON，直接返回文本
    return observations
  }
  
  return ''
}

// 从观察记录中提取图片数组
const getObservationsImages = (observations) => {
  if (!observations) return []
  
  try {
    const parsed = JSON.parse(observations)
    if (parsed.images && Array.isArray(parsed.images)) {
      return parsed.images
    }
  } catch (e) {
    // 解析失败返回空数组
  }
  
  return []
}

// 从观察记录中提取最后编辑时间
const getObservationsLastUpdated = (observations) => {
  if (!observations) return ''
  
  try {
    const parsed = JSON.parse(observations)
    if (parsed.lastUpdated) {
      return new Date(parsed.lastUpdated).toLocaleString('zh-CN')
    }
  } catch (e) {
    // 解析失败返回空字符串
  }
  
  return ''
}

const handleSelectionChange = (selection) => {
  selectedGroups.value = selection
}

// 处理表格全选事件
const handleSelectAll = async (selection) => {
  // 判断是全选还是取消全选
  const isSelectingAllRows = selection.length > 0
  
  if (isSelectingAllRows) {
    // 全选所有实验组（不仅仅是当前页）
    try {
      const { data } = await experimentApi.getGroups({
        page: 1,
        per_page: total.value, // 获取所有实验组
        sort_by: 'created_at',
        sort_order: sortOrder.value
      })
      
      selectedGroups.value = data.groups
      ElMessage.success(`已选中所有 ${data.groups.length} 个实验组`)
    } catch (error) {
      ElMessage.error('获取所有实验组失败')
    }
  } else {
    // 取消全选
    selectedGroups.value = []
  }
}

const handleRowClick = (row, column) => {
  // 如果点击的是操作列或选择框列，不触发行点击
  if (column && (column.type === 'selection' || column.label === '操作')) {
    return
  }
  viewGroup(row)
}

const loadGroups = async () => {
  loading.value = true
  try {
    const { data } = await experimentApi.getGroups({
      page: currentPage.value,
      per_page: pageSize.value,
      sort_by: 'created_at',
      sort_order: sortOrder.value
    })
    groups.value = data.groups
    total.value = data.total
  } catch (error) {
    ElMessage.error('加载实验组列表失败')
  } finally {
    loading.value = false
  }
}

const handleSortChange = (sortInfo) => {
  // sortInfo 包含 column, prop, order
  const { order } = sortInfo
  
  // order 可能是 'ascending', 'descending', 或 null
  if (order === 'ascending') {
    sortOrder.value = 'asc'
  } else if (order === 'descending') {
    sortOrder.value = 'desc'
  } else {
    sortOrder.value = 'desc' // 默认降序
  }
  loadGroups()
}

const viewGroup = (row) => {
  router.push(`/group/${row.id}?mode=view`)
}

const editGroup = (id) => {
  router.push(`/group/${id}`)
}

const deleteGroup = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个实验组吗？删除后不会影响组内的实验结果。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await experimentApi.deleteGroup(id)
    ElMessage.success('删除成功')
    loadGroups()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const batchDelete = async () => {
  if (selectedGroups.value.length === 0) {
    ElMessage.warning('请先选择要删除的实验组')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedGroups.value.length} 个实验组吗？删除后不会影响组内的实验结果。`, 
      '批量删除确认', 
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        distinguishCancelAndClose: true
      }
    )
    
    // 批量删除
    const deletePromises = selectedGroups.value.map(group => 
      experimentApi.deleteGroup(group.id)
    )
    
    await Promise.all(deletePromises)
    
    ElMessage.success(`成功删除 ${selectedGroups.value.length} 个实验组`)
    selectedGroups.value = []
    loadGroups()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error('批量删除失败')
    }
  }
}

const createNew = () => {
  router.push('/group/new')
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 监听视图模式变化，保存到 localStorage
watch(viewMode, (newMode) => {
  localStorage.setItem('groupListViewMode', newMode)
})

onMounted(() => {
  // 恢复用户之前选择的视图模式
  const savedViewMode = localStorage.getItem('groupListViewMode')
  if (savedViewMode) {
    viewMode.value = savedViewMode
  }
  loadGroups()
})
</script>
<style scoped>
/* 卡片视图容器 */
.card-view-container {
  min-height: 400px;
}

/* 卡片网格布局 */
.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 20px;
}

/* 单个卡片 */
.group-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 300px;
  position: relative;
}

.group-card:hover {
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.12);
  border-color: #409eff;
  transform: translateY(-4px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.card-title-row {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 8px;
}

.card-checkbox {
  flex-shrink: 0;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  word-break: break-word;
  flex: 1;
}

/* 卡片主体 */
.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.info-label .el-icon {
  font-size: 14px;
  color: #909399;
}

.info-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  padding-left: 20px;
  word-break: break-word;
}

/* 空状态提示 */
.card-empty-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  color: #c0c4cc;
  font-size: 14px;
  border: 2px dashed #e4e7ed;
  border-radius: 8px;
  margin: 8px 0;
}

.card-empty-hint .el-icon {
  font-size: 18px;
}

/* 元数据行 */
.card-meta {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  margin: 8px 0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}

.meta-item .el-icon {
  font-size: 14px;
}

/* 观察记录预览 */
.card-preview {
  background: #f5f7fa;
  padding: 12px 14px;
  border-radius: 8px;
  margin-top: auto;
  transition: all 0.3s ease;
}

.card-preview:hover {
  background: #ecf5ff;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.preview-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.preview-label .el-icon {
  font-size: 13px;
}

.preview-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
}

.preview-time .el-icon {
  font-size: 12px;
}

.preview-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.preview-images {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.preview-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}

.preview-image:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1;
}

.more-images {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e4e7ed;
  border-radius: 4px;
  color: #606266;
  font-size: 12px;
  font-weight: 600;
}

/* 卡片底部操作按钮 */
.card-footer {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.card-footer .el-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.card-footer .el-button .el-icon {
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .groups-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 1200px) {
  .groups-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }
  
  .group-card {
    padding: 20px;
    min-height: 280px;
  }
}

@media (max-width: 768px) {
  .groups-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .group-card {
    min-height: auto;
  }
  
  .card-footer {
    flex-wrap: wrap;
  }
  
  .card-footer .el-button {
    flex: 1 1 calc(50% - 4px);
    min-width: 80px;
  }
}
</style>