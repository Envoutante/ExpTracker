<template>
  <div class="group-view">
    <!-- 顶部操作栏 -->
    <div class="header-bar">
      <el-button @click="goBack" text>
        <el-icon><ArrowLeft /></el-icon>
        返回实验组列表
      </el-button>
      <div class="header-actions">
        <el-button v-if="isView && !isNew" @click="exportToHTML">
          <el-icon><Download /></el-icon>
          导出 HTML
        </el-button>
        <el-button v-if="isView && !isNew" type="primary" @click="toggleEdit">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
        <el-button v-if="!isView && !isNew" @click="cancelEdit">
          <el-icon><Close /></el-icon>
          取消编辑
        </el-button>
        <el-button v-if="!isView" type="primary" @click="save" :loading="saving">
          <el-icon><Check /></el-icon>
          {{ isNew ? '创建' : '保存' }}
        </el-button>
      </div>
    </div>

    <div class="notebook-container" v-loading="loading">
      <!-- 实验组标题 -->
      <div class="notebook-title">
        <el-input 
          v-if="!isView"
          v-model="form.name" 
          placeholder="实验组名称"
          class="title-input"
          size="large"
        />
        <h1 v-else class="title-text">{{ form.name }}</h1>
      </div>

      <!-- 元信息 -->
      <div class="meta-info">
        <div class="meta-item">
          <span class="meta-label">实验结果数量：</span>
          <span class="meta-value">{{ form.experiments?.length || 0 }} 个</span>
        </div>
        
        <div class="meta-item">
          <span class="meta-label">创建时间：</span>
          <span class="meta-value">{{ formatDate(form.created_at) }}</span>
        </div>
      </div>

      <!-- 实验组描述 -->
      <div class="notebook-section">
        <div class="section-header">
          <el-icon><Document /></el-icon>
          <span>实验组描述</span>
        </div>
        <el-input 
          v-if="!isView"
          v-model="form.description" 
          type="textarea" 
          :rows="3" 
          placeholder="简要描述这组实验..."
          class="note-textarea"
        />
        <div v-else class="note-content">{{ form.description || '暂无描述' }}</div>
      </div>

      <!-- 实验目的 -->
      <div class="notebook-section">
        <div class="section-header">
          <el-icon><Aim /></el-icon>
          <span>实验目的</span>
        </div>
        <el-input 
          v-if="!isView"
          v-model="form.purpose" 
          type="textarea" 
          :rows="4" 
          placeholder="为什么要做这组实验？想验证什么假设？"
          class="note-textarea"
        />
        <div v-else class="note-content">{{ form.purpose || '暂无实验目的' }}</div>
      </div>

      <!-- 包含的实验结果列表 -->
      <div class="notebook-section">
        <div class="section-header">
          <el-icon><List /></el-icon>
          <span>包含的实验结果</span>
          <el-button 
            v-if="!isView"
            size="small" 
            type="primary"
            @click="showAddExperimentDialog"
            style="margin-left: 16px;"
          >
            <el-icon style="color: white;"><CirclePlus /></el-icon>
            添加实验结果
          </el-button>
          <el-button 
            v-if="form.experiments && form.experiments.length > 0" 
            type="success" 
            size="small" 
            @click="openGroupTensorBoard"
            style="margin-left: auto;"
          >
            <el-icon style="color: white;"><Monitor /></el-icon>
            批量打开 TensorBoard
          </el-button>
        </div>
        
        <el-table 
          v-if="form.experiments && form.experiments.length > 0"
          :data="form.experiments" 
          stripe 
          style="width: 100%"
        >
          <el-table-column prop="experiment_id" label="实验 ID" width="200" />
          <el-table-column prop="name" label="实验名称" min-width="250" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'running'" type="primary">运行中</el-tag>
              <el-tag v-else-if="row.status === 'completed'" type="success">已完成</el-tag>
              <el-tag v-else-if="row.status === 'failed'" type="danger">失败</el-tag>
              <el-tag v-else>{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" @click="viewExperiment(row.id)">查看</el-button>
              <el-button v-if="!isView" size="small" type="danger" @click="removeExperiment(row.id)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-else class="empty-experiments">
          暂无实验结果
        </div>
      </div>

      <!-- 观察记录 -->
      <div class="notebook-section">
        <div class="section-header">
          <el-icon><View /></el-icon>
          <span>观察记录</span>
        </div>
        <el-input 
          v-if="!isView"
          v-model="form.observations" 
          type="textarea" 
          :rows="6" 
          placeholder="记录对这组实验的整体观察..."
          class="note-textarea"
        />
        <div v-else class="note-content">{{ form.observations || '暂无观察记录' }}</div>
      </div>

      <!-- 结论 -->
      <div class="notebook-section">
        <div class="section-header">
          <el-icon><Finished /></el-icon>
          <span>结论与下一步</span>
        </div>
        <el-input 
          v-if="!isView"
          v-model="form.conclusion" 
          type="textarea" 
          :rows="5" 
          placeholder="实验组的整体结论和下一步计划..."
          class="note-textarea"
        />
        <div v-else class="note-content">{{ form.conclusion || '暂无结论' }}</div>
      </div>
    </div>

    <!-- 添加实验结果对话框 -->
    <el-dialog v-model="addExperimentDialogVisible" title="添加实验结果到实验组" width="900px">
      <el-table 
        :data="paginatedExperiments" 
        @selection-change="handleExperimentSelection"
        v-loading="loadingExperiments"
        height="400"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="experiment_id" label="实验 ID" width="200" />
        <el-table-column prop="name" label="实验名称" min-width="250" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'running'" type="primary">运行中</el-tag>
            <el-tag v-else-if="row.status === 'completed'" type="success">已完成</el-tag>
            <el-tag v-else-if="row.status === 'failed'" type="danger">失败</el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <div style="margin-top: 16px; display: flex; justify-content: center;">
        <el-pagination
          v-model:current-page="dialogCurrentPage"
          :page-size="dialogPageSize"
          :total="availableExperiments.length"
          layout="total, prev, pager, next"
          @current-change="handleDialogPageChange"
        />
      </div>
      
      <template #footer>
        <el-button @click="addExperimentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addSelectedExperiments" :disabled="selectedExperiments.length === 0">
          添加 {{ selectedExperiments.length > 0 ? `(${selectedExperiments.length})` : '' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { experimentApi } from '../api/experiments'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, Edit, Check, Close, Document, Aim, View, Finished, List, Monitor, Download, CirclePlus
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const form = ref({
  name: '',
  description: '',
  purpose: '',
  observations: '',
  conclusion: '',
  experiments: [],
  created_at: null
})

const loading = ref(false)
const saving = ref(false)
const isView = ref(false)  // 默认为 false，在 loadGroup 中根据情况设置
const originalForm = ref(null)

// 使用路由名称判断是否为新建模式，更可靠
const isNew = computed(() => route.name === 'NewGroup')

const loadGroup = async () => {
  if (isNew.value) {
    // 新建模式：重置表单
    form.value = {
      name: '',
      description: '',
      purpose: '',
      observations: '',
      conclusion: '',
      experiments: [],
      created_at: null
    }
    isView.value = false
    return
  }
  
  loading.value = true
  try {
    const { data } = await experimentApi.getGroup(route.params.id)
    form.value = data
    // 默认进入查看模式
    isView.value = true
  } catch (error) {
    ElMessage.error('加载实验组失败')
  } finally {
    loading.value = false
  }
}

const toggleEdit = () => {
  originalForm.value = JSON.parse(JSON.stringify(form.value))
  isView.value = false
}

const cancelEdit = () => {
  if (originalForm.value) {
    form.value = JSON.parse(JSON.stringify(originalForm.value))
  }
  isView.value = true
}

const save = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入实验组名称')
    return
  }
  
  saving.value = true
  try {
    if (isNew.value) {
      // 新建实验组
      const experimentIds = form.value.experiments?.map(exp => exp.id) || []
      const { data } = await experimentApi.createGroup({
        name: form.value.name,
        description: form.value.description,
        purpose: form.value.purpose,
        observations: form.value.observations,
        conclusion: form.value.conclusion,
        experiment_ids: experimentIds
      })
      ElMessage.success('创建成功')
      // 跳转到实验组列表
      router.push('/groups')
    } else {
      // 更新实验组
      await experimentApi.updateGroup(route.params.id, {
        name: form.value.name,
        description: form.value.description,
        purpose: form.value.purpose,
        observations: form.value.observations,
        conclusion: form.value.conclusion
      })
      ElMessage.success('保存成功')
      isView.value = true
      loadGroup()
    }
  } catch (error) {
    ElMessage.error(isNew.value ? '创建失败' : '保存失败')
  } finally {
    saving.value = false
  }
}

const removeExperiment = async (experimentId) => {
  try {
    await ElMessageBox.confirm('确定要从实验组中移除这个实验结果吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (isNew.value) {
      // 新建模式：直接从本地列表移除
      form.value.experiments = form.value.experiments.filter(exp => exp.id !== experimentId)
      ElMessage.success('移除成功')
    } else {
      // 编辑模式：调用 API
      await experimentApi.removeExperimentFromGroup(route.params.id, experimentId)
      ElMessage.success('移除成功')
      loadGroup()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败')
    }
  }
}

const viewExperiment = (id) => {
  router.push(`/experiment/${id}?mode=view`)
}

const openGroupTensorBoard = async () => {
  const validExperiments = form.value.experiments.filter(exp => exp.tb_log_path)
  
  if (validExperiments.length === 0) {
    ElMessage.warning('组内没有配置 TensorBoard 路径的实验结果')
    return
  }
  
  // 记录开始时间
  const startTime = Date.now()
  let timer = null
  
  // 格式化时间为 00:00:00
  const formatElapsedTime = (seconds) => {
    const h = Math.floor(seconds / 3600).toString().padStart(2, '0')
    const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
    const s = (seconds % 60).toString().padStart(2, '0')
    return `${h}:${m}:${s}`
  }
  
  // 显示加载弹窗
  const loadingInstance = ElMessageBox({
    title: '正在启动 TensorBoard',
    message: '<div style="text-align: center;">正在启动 TensorBoard，请稍候...<br/><span style="color: #909399; font-size: 14px;">耗时：<span id="elapsed-time">00:00:00</span></span></div>',
    showConfirmButton: false,
    showCancelButton: false,
    closeOnClickModal: false,
    closeOnPressEscape: false,
    center: true,
    dangerouslyUseHTMLString: true
  }).catch(() => {})
  
  // 启动计时器
  timer = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000)
    const elapsedSpan = document.getElementById('elapsed-time')
    if (elapsedSpan) {
      elapsedSpan.textContent = formatElapsedTime(elapsed)
    }
  }, 1000)
  
  try {
    const logPaths = validExperiments.map(exp => exp.tb_log_path)
    const experimentNames = validExperiments.map(exp => exp.name || exp.experiment_id)
    const localCachePaths = validExperiments.map(exp => exp.tb_local_cache_path)
    const port = validExperiments[0].tb_port || 6006
    
    await experimentApi.startTensorBoardMultiple(logPaths, experimentNames, port, localCachePaths)
    
    if (timer) clearInterval(timer)
    
    const totalElapsed = Math.floor((Date.now() - startTime) / 1000)
    const closeBtn = document.querySelector('.el-message-box__headerbtn')
    if (closeBtn) closeBtn.click()
    
    ElMessage.success({
      message: `TensorBoard 启动成功，耗时 ${formatElapsedTime(totalElapsed)}`,
      duration: 5000
    })
    
    setTimeout(() => {
      ElMessage.info({
        dangerouslyUseHTMLString: true,
        message: `如果浏览器未自动打开，请手动访问：<a href="http://localhost:${port}" target="_blank" style="color: #409eff; text-decoration: underline;">http://localhost:${port}</a>`,
        duration: 10000
      })
    }, 3000)
  } catch (error) {
    if (timer) clearInterval(timer)
    const closeBtn = document.querySelector('.el-message-box__headerbtn')
    if (closeBtn) closeBtn.click()
    
    ElMessage.error({
      message: error.response?.data?.error || '启动 TensorBoard 失败',
      duration: 10000
    })
  }
}

const goBack = () => {
  router.push('/groups')
}

const exportToHTML = () => {
  // 生成 HTML 内容
  const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${form.value.name} - 实验组报告</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
      line-height: 1.6;
      color: #333;
      background: #f5f7fa;
      padding: 20px;
    }
    .container {
      max-width: 1000px;
      margin: 0 auto;
      background: white;
      padding: 40px;
      border-radius: 8px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    }
    h1 {
      font-size: 32px;
      color: #303133;
      margin-bottom: 20px;
      border-bottom: 3px solid #409eff;
      padding-bottom: 10px;
    }
    .meta-info {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      margin-bottom: 30px;
      padding: 15px;
      background: #f9fafb;
      border-radius: 4px;
    }
    .meta-item {
      display: flex;
      gap: 8px;
    }
    .meta-label {
      font-weight: 600;
      color: #606266;
    }
    .meta-value {
      color: #303133;
    }
    .section {
      margin-bottom: 30px;
    }
    .section-title {
      font-size: 20px;
      font-weight: 600;
      color: #409eff;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e4e7ed;
    }
    .section-content {
      color: #606266;
      white-space: pre-wrap;
      line-height: 1.8;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #e4e7ed;
    }
    th {
      background: #f9fafb;
      font-weight: 600;
      color: #606266;
    }
    tr:hover {
      background: #f9fafb;
    }
    .tag {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 12px;
    }
    .tag-running { background: #ecf5ff; color: #409eff; }
    .tag-completed { background: #f0f9ff; color: #67c23a; }
    .tag-failed { background: #fef0f0; color: #f56c6c; }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #e4e7ed;
      text-align: center;
      color: #909399;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📁 ${form.value.name}</h1>
    
    <div class="meta-info">
      <div class="meta-item">
        <span class="meta-label">实验结果数量：</span>
        <span class="meta-value">${form.value.experiments?.length || 0} 个</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">创建时间：</span>
        <span class="meta-value">${formatDate(form.value.created_at)}</span>
      </div>
    </div>

    ${form.value.description ? `
    <div class="section">
      <div class="section-title">📝 实验组描述</div>
      <div class="section-content">${form.value.description}</div>
    </div>
    ` : ''}

    ${form.value.purpose ? `
    <div class="section">
      <div class="section-title">🎯 实验目的</div>
      <div class="section-content">${form.value.purpose}</div>
    </div>
    ` : ''}

    ${form.value.experiments && form.value.experiments.length > 0 ? `
    <div class="section">
      <div class="section-title">🧪 包含的实验结果</div>
      <table>
        <thead>
          <tr>
            <th>实验 ID</th>
            <th>实验结果名称</th>
            <th>状态</th>
            <th>创建时间</th>
          </tr>
        </thead>
        <tbody>
          ${form.value.experiments.map(exp => `
          <tr>
            <td><code>${exp.experiment_id}</code></td>
            <td>${exp.name}</td>
            <td><span class="tag tag-${exp.status}">${getStatusText(exp.status)}</span></td>
            <td>${formatDate(exp.created_at)}</td>
          </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    ` : ''}

    ${form.value.observations ? `
    <div class="section">
      <div class="section-title">👁️ 观察记录</div>
      <div class="section-content">${form.value.observations}</div>
    </div>
    ` : ''}

    ${form.value.conclusion ? `
    <div class="section">
      <div class="section-title">✅ 结论与下一步</div>
      <div class="section-content">${form.value.conclusion}</div>
    </div>
    ` : ''}

    <div class="footer">
      <p>导出时间：${new Date().toLocaleString('zh-CN')}</p>
      <p>由 ExpTracker 实验日志管理系统生成</p>
    </div>
  </div>
</body>
</html>
  `

  // 创建 Blob 并下载
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `实验组_${form.value.name}.html`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('HTML 文件已导出')
}

const getStatusText = (status) => {
  const map = {
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 添加实验对话框
const addExperimentDialogVisible = ref(false)
const availableExperiments = ref([])
const loadingExperiments = ref(false)
const selectedExperiments = ref([])
const dialogCurrentPage = ref(1)
const dialogPageSize = ref(10)

const paginatedExperiments = computed(() => {
  const start = (dialogCurrentPage.value - 1) * dialogPageSize.value
  const end = start + dialogPageSize.value
  return availableExperiments.value.slice(start, end)
})

const handleDialogPageChange = () => {
  // 翻页时清空当前页的选择
  // 注意：这里不清空 selectedExperiments，保留跨页选择
}

const showAddExperimentDialog = async () => {
  addExperimentDialogVisible.value = true
  loadingExperiments.value = true
  dialogCurrentPage.value = 1
  selectedExperiments.value = []
  
  try {
    const { data } = await experimentApi.getExperiments({
      page: 1,
      per_page: 1000
    })
    
    // 过滤掉已经在组内的实验
    const existingIds = new Set(form.value.experiments?.map(exp => exp.id) || [])
    availableExperiments.value = data.experiments.filter(exp => !existingIds.has(exp.id))
  } catch (error) {
    ElMessage.error('加载实验列表失败')
  } finally {
    loadingExperiments.value = false
  }
}

const handleExperimentSelection = (selection) => {
  selectedExperiments.value = selection
}

const addSelectedExperiments = async () => {
  if (selectedExperiments.value.length === 0) {
    return
  }
  
  try {
    if (isNew.value) {
      // 新建模式：直接添加到本地列表
      const newExperiments = selectedExperiments.value.map(exp => ({
        id: exp.id,
        experiment_id: exp.experiment_id,
        name: exp.name,
        status: exp.status,
        tb_log_path: exp.tb_log_path,
        tb_port: exp.tb_port,
        created_at: exp.created_at
      }))
      
      if (!form.value.experiments) {
        form.value.experiments = []
      }
      form.value.experiments.push(...newExperiments)
      
      ElMessage.success(`成功添加 ${newExperiments.length} 个实验结果`)
      addExperimentDialogVisible.value = false
      selectedExperiments.value = []
    } else {
      // 编辑模式：调用 API
      const experimentIds = selectedExperiments.value.map(exp => exp.id)
      await experimentApi.addExperimentsToGroup(route.params.id, experimentIds)
      
      ElMessage.success(`成功添加 ${experimentIds.length} 个实验结果`)
      addExperimentDialogVisible.value = false
      selectedExperiments.value = []
      loadGroup()
    }
  } catch (error) {
    ElMessage.error('添加实验结果失败')
  }
}

onMounted(() => {
  loadGroup()
})

// 监听路由变化，重新加载数据
watch(() => route.params.id, () => {
  loadGroup()
})
</script>

<style scoped>
.group-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.notebook-container {
  background: #fff;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.notebook-title {
  margin-bottom: 24px;
}

.title-input {
  font-size: 28px;
  font-weight: 600;
}

.title-input :deep(.el-input__wrapper) {
  box-shadow: none;
  border-bottom: 2px solid #dcdfe6;
  border-radius: 0;
  padding: 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.title-input :deep(.el-input__inner) {
  font-size: 28px;
  font-weight: 600;
}

.title-text {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  padding: 8px 0;
}

.meta-info {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 16px 0;
  margin-bottom: 32px;
  border-bottom: 1px solid #f0f0f0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.meta-value {
  font-size: 14px;
  color: #606266;
}

.notebook-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header .el-icon {
  font-size: 20px;
  color: #409eff;
}

.note-textarea :deep(.el-textarea__inner) {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
}

.note-content {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  padding: 12px 0;
  white-space: pre-wrap;
  word-break: break-word;
  min-height: 60px;
}

.empty-experiments {
  text-align: center;
  color: #c0c4cc;
  padding: 40px;
  font-size: 14px;
  background: #f9fafb;
  border-radius: 4px;
}
</style>
