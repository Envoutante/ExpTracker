<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-input
          v-model="searchText"
          placeholder="搜索实验结果名称"
          clearable
          @clear="loadExperiments"
          @keyup.enter="loadExperiments"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-col>
      <el-col :span="4">
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadExperiments">
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-button type="success" @click="openAllTensorBoard" style="width: 100%;">
          <el-icon><Monitor /></el-icon>
          查看所有 TensorBoard
        </el-button>
      </el-col>
      <el-col :span="4">
        <el-button type="primary" @click="createNew" style="width: 100%;">
          <el-icon><CirclePlus /></el-icon>
          新建实验
        </el-button>
      </el-col>
    </el-row>

    <div v-if="selectedRows.length > 0" style="margin-bottom: 16px;">
      <el-alert type="info" :closable="false">
        <template #default>
          <span>已选中 {{ selectedRows.length }} 个实验结果</span>
          <el-button 
            type="warning" 
            size="small" 
            style="margin-left: 16px;"
            @click="openBatchEditDialog"
          >
            批量编辑
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            style="margin-left: 16px;"
            @click="createGroupFromSelected"
          >
            创建实验组
          </el-button>
          <el-button 
            type="success" 
            size="small" 
            style="margin-left: 16px;"
            @click="batchOpenTensorBoard"
            :disabled="!hasValidTensorBoardPaths"
          >
            批量打开 TensorBoard
          </el-button>
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

    <el-table 
      :data="experiments" 
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
      <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="name" label="实验名称" min-width="250" show-overflow-tooltip />
      <el-table-column label="所属实验组" width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.groups && row.groups.length > 0" style="color: #409eff;">
            {{ row.groups.map(g => g.name).join(', ') }}
          </span>
          <span v-else style="color: #c0c4cc;">未分组</span>
        </template>
      </el-table-column>
      <el-table-column prop="algorithm" label="算法" min-width="120" show-overflow-tooltip />
      <el-table-column prop="map" label="地图" min-width="120" show-overflow-tooltip />
      <el-table-column prop="environment" label="环境" min-width="120" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.status === 'running'" type="primary">运行中</el-tag>
          <el-tag v-else-if="row.status === 'completed'" type="success">已完成</el-tag>
          <el-tag v-else-if="row.status === 'failed'" type="danger">失败</el-tag>
          <el-tag v-else>{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Event 缓存" width="110" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.tb_local_cache_path" type="success" size="small">已下载</el-tag>
          <el-tag v-else type="info" size="small">未下载</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="340" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click.stop="viewExperiment(row.id)">查看</el-button>
          <el-button size="small" type="primary" @click.stop="editExperiment(row.id)">编辑</el-button>
          <el-button size="small" type="success" @click.stop="openTensorBoard(row)" :disabled="!row.tb_log_path">
            TensorBoard
          </el-button>
          <el-button size="small" type="danger" @click.stop="deleteExperiment(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="margin-top: 20px; justify-content: center;"
      @current-change="loadExperiments"
      @size-change="loadExperiments"
    />

    <!-- 批量编辑对话框 -->
    <el-dialog
      v-model="batchEditDialogVisible"
      title="批量编辑实验信息"
      width="500px"
    >
      <el-form :model="batchEditForm" label-width="80px">
        <el-form-item label="算法">
          <el-input v-model="batchEditForm.algorithm" placeholder="请输入算法名称" clearable />
        </el-form-item>
        <el-form-item label="地图">
          <el-input v-model="batchEditForm.map" placeholder="请输入地图名称" clearable />
        </el-form-item>
        <el-form-item label="环境">
          <el-input v-model="batchEditForm.environment" placeholder="请输入环境名称" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchEditDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmBatchEdit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { experimentApi } from '../api/experiments'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CirclePlus, Monitor } from '@element-plus/icons-vue'

const router = useRouter()

const experiments = ref([])
const loading = ref(false)
const searchText = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedRows = ref([])
const allSelected = ref(false)
const allExperimentIds = ref([])
const sortOrder = ref('desc') // 默认降序（最新的在前）

// 批量编辑相关
const batchEditDialogVisible = ref(false)
const batchEditForm = ref({
  algorithm: '',
  map: '',
  environment: ''
})

// 检查选中的实验是否有有效的 TensorBoard 路径
const hasValidTensorBoardPaths = computed(() => {
  return selectedRows.value.some(row => row.tb_log_path)
})

const loadExperiments = async () => {
  loading.value = true
  try {
    const { data } = await experimentApi.getExperiments({
      search: searchText.value,
      status: statusFilter.value,
      page: currentPage.value,
      per_page: pageSize.value,
      sort_by: 'created_at',
      sort_order: sortOrder.value
    })
    experiments.value = data.experiments
    total.value = data.total
  } catch (error) {
    console.error('加载实验列表失败:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error(`加载实验列表失败: ${error.response?.data?.error || error.message}`)
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
  loadExperiments()
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  // 如果取消选择，重置全选状态
  if (selection.length === 0) {
    allSelected.value = false
    allExperimentIds.value = []
  }
}

// 处理表格全选事件
const handleSelectAll = async (selection) => {
  // 判断是全选还是取消全选
  const isSelectingAllRows = selection.length > 0
  
  if (isSelectingAllRows) {
    // 全选所有实验（不仅仅是当前页）
    try {
      const { data } = await experimentApi.getExperiments({
        search: searchText.value,
        status: statusFilter.value,
        page: 1,
        per_page: total.value // 获取所有实验
      })
      
      allExperimentIds.value = data.experiments.map(exp => exp.id)
      selectedRows.value = data.experiments
      allSelected.value = true
      
      ElMessage.success(`已选中所有 ${data.experiments.length} 个实验结果`)
    } catch (error) {
      ElMessage.error('获取所有实验失败')
    }
  } else {
    // 取消全选
    selectedRows.value = []
    allSelected.value = false
    allExperimentIds.value = []
  }
}

const handleRowClick = (row, column) => {
  // 如果点击的是选择框列或 ID 列，不触发查看详情
  if (column && (column.type === 'selection' || column.property === 'id')) {
    return
  }
  viewExperiment(row.id)
}

const createNew = () => {
  router.push('/experiment/new')
}

const viewExperiment = (id) => {
  router.push(`/experiment/${id}?mode=view`)
}

const editExperiment = (id) => {
  router.push(`/experiment/${id}`)
}

const deleteExperiment = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个实验吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await experimentApi.deleteExperiment(id)
    ElMessage.success('删除成功')
    loadExperiments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const batchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的实验')
    return
  }

  const deleteCount = allSelected.value ? allExperimentIds.value.length : selectedRows.value.length

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${deleteCount} 个实验吗？此操作不可恢复！`, 
      '批量删除警告', 
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 批量删除
    const idsToDelete = allSelected.value 
      ? allExperimentIds.value 
      : selectedRows.value.map(row => row.id)
    
    const deletePromises = idsToDelete.map(id => 
      experimentApi.deleteExperiment(id)
    )
    
    await Promise.all(deletePromises)
    
    ElMessage.success(`成功删除 ${deleteCount} 个实验`)
    selectedRows.value = []
    allSelected.value = false
    allExperimentIds.value = []
    loadExperiments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const openTensorBoard = async (experiment) => {
  // 记录开始时间
  const startTime = Date.now()
  let timer = null
  let loadingInstance = null
  
  // 格式化时间为 00:00:00
  const formatElapsedTime = (seconds) => {
    const h = Math.floor(seconds / 3600).toString().padStart(2, '0')
    const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
    const s = (seconds % 60).toString().padStart(2, '0')
    return `${h}:${m}:${s}`
  }
  
  // 显示加载弹窗
  loadingInstance = ElMessageBox({
    title: '正在启动 TensorBoard',
    message: '<div style="text-align: center;">正在启动 TensorBoard，请稍候...<br/><span style="color: #909399; font-size: 14px;">耗时：<span id="elapsed-time">00:00:00</span></span></div>',
    showConfirmButton: false,
    showCancelButton: false,
    closeOnClickModal: false,
    closeOnPressEscape: false,
    center: true,
    dangerouslyUseHTMLString: true
  }).catch(() => {
    // 捕获关闭弹窗时的 reject，避免控制台报错
  })
  
  // 启动计时器更新耗时
  timer = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000)
    const elapsedSpan = document.getElementById('elapsed-time')
    if (elapsedSpan) {
      elapsedSpan.textContent = formatElapsedTime(elapsed)
    }
  }, 1000)
  
  try {
    // 如果有本地缓存路径，传递给 API（会使用本地 TensorBoard）
    await experimentApi.startTensorBoard(experiment.tb_log_path, experiment.tb_port, experiment.tb_local_cache_path)
    
    // 清除计时器
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    
    // 计算总耗时
    const totalElapsed = Math.floor((Date.now() - startTime) / 1000)
    
    // 关闭加载弹窗
    const closeBtn = document.querySelector('.el-message-box__headerbtn')
    if (closeBtn) closeBtn.click()
    
    // 显示成功消息
    ElMessage.success({
      message: `TensorBoard 启动成功，耗时 ${formatElapsedTime(totalElapsed)}`,
      duration: 5000
    })
    
    // 提供手动链接
    setTimeout(() => {
      ElMessage.info({
        dangerouslyUseHTMLString: true,
        message: `如果浏览器未自动打开，请手动访问：<a href="http://localhost:${experiment.tb_port || 6006}" target="_blank" style="color: #409eff; text-decoration: underline;">http://localhost:${experiment.tb_port || 6006}</a>`,
        duration: 10000
      })
    }, 3000)
  } catch (error) {
    // 清除计时器
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    
    // 关闭加载弹窗
    const closeBtn = document.querySelector('.el-message-box__headerbtn')
    if (closeBtn) closeBtn.click()
    
    // 显示错误消息
    const errorMsg = error.response?.data?.error || error.message || 'TensorBoard 启动失败'
    ElMessage.error({
      message: errorMsg,
      duration: 10000
    })
  }
}

const batchOpenTensorBoard = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要打开的实验')
    return
  }
  
  // 过滤出有 TensorBoard 路径的实验
  const validExperiments = selectedRows.value.filter(row => row.tb_log_path)
  
  if (validExperiments.length === 0) {
    ElMessage.warning('选中的实验都没有配置 TensorBoard 日志路径')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `将同时打开 ${validExperiments.length} 个实验的 TensorBoard，它们将在同一个窗口中显示。是否继续？`,
      '批量打开 TensorBoard',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 收集所有日志路径
    const logPaths = validExperiments.map(exp => exp.tb_log_path)
    
    // 使用第一个实验的端口，或默认端口 6006
    const port = validExperiments[0].tb_port || 6006
    
    // 记录开始时间
    const startTime = Date.now()
    let timer = null
    let loadingInstance = null
    
    // 格式化时间为 00:00:00
    const formatElapsedTime = (seconds) => {
      const h = Math.floor(seconds / 3600).toString().padStart(2, '0')
      const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
      const s = (seconds % 60).toString().padStart(2, '0')
      return `${h}:${m}:${s}`
    }
    
    // 显示加载弹窗
    loadingInstance = ElMessageBox({
      title: '正在启动 TensorBoard',
      message: '<div style="text-align: center;">正在启动 TensorBoard，请稍候...<br/><span style="color: #909399; font-size: 14px;">耗时：<span id="elapsed-time">00:00:00</span></span></div>',
      showConfirmButton: false,
      showCancelButton: false,
      closeOnClickModal: false,
      closeOnPressEscape: false,
      center: true,
      dangerouslyUseHTMLString: true
    }).catch(() => {
      // 捕获关闭弹窗时的 reject，避免控制台报错
    })
    
    // 启动计时器更新耗时
    timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000)
      const elapsedSpan = document.getElementById('elapsed-time')
      if (elapsedSpan) {
        elapsedSpan.textContent = formatElapsedTime(elapsed)
      }
    }, 1000)
    
    try {
      // 调用批量启动接口
      const experimentNames = validExperiments.map(exp => exp.name || exp.experiment_id)
      // 获取本地缓存路径（如果有的话）
      const localCachePaths = validExperiments.map(exp => exp.tb_local_cache_path)
      console.log('批量启动 TensorBoard')
      console.log('日志路径:', logPaths)
      console.log('本地缓存路径:', localCachePaths)
      console.log('实验名称:', experimentNames)
      console.log('端口:', port)
      
      await experimentApi.startTensorBoardMultiple(logPaths, experimentNames, port, localCachePaths)
      
      // 清除计时器
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      
      // 计算总耗时
      const totalElapsed = Math.floor((Date.now() - startTime) / 1000)
      
      // 关闭加载弹窗
      const closeBtn = document.querySelector('.el-message-box__headerbtn')
      if (closeBtn) closeBtn.click()
      
      // 显示成功消息
      ElMessage.success({
        message: `TensorBoard 启动成功，耗时 ${formatElapsedTime(totalElapsed)}`,
        duration: 5000
      })
      
      // 提供手动链接
      setTimeout(() => {
        ElMessage.info({
          dangerouslyUseHTMLString: true,
          message: `如果浏览器未自动打开，请手动访问：<a href="http://localhost:${port}" target="_blank" style="color: #409eff; text-decoration: underline;">http://localhost:${port}</a>`,
          duration: 10000
        })
      }, 3000)
    } catch (error) {
      // 清除计时器
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      
      // 关闭加载弹窗
      const closeBtn = document.querySelector('.el-message-box__headerbtn')
      if (closeBtn) closeBtn.click()
      
      // 输出详细错误信息到控制台
      console.error('批量启动 TensorBoard 失败:', error)
      console.error('错误响应:', error.response)
      console.error('错误数据:', error.response?.data)
      
      // 显示错误消息
      const errorMsg = error.response?.data?.error || error.message || '批量启动 TensorBoard 失败'
      ElMessage.error({
        message: errorMsg,
        duration: 10000  // 增加到 10 秒
      })
    }
  } catch (error) {
    console.error('外层错误:', error)
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || error.message || '批量启动 TensorBoard 失败'
      ElMessage.error({
        message: errorMsg,
        duration: 10000  // 增加到 10 秒
      })
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const createGroupFromSelected = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要加入实验组的实验')
    return
  }
  
  try {
    const { value: groupName } = await ElMessageBox.prompt('请输入实验组名称', '创建实验组', {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '实验组名称不能为空'
    })
    
    const experimentIds = selectedRows.value.map(row => row.id)
    
    await experimentApi.createGroup({
      name: groupName,
      experiment_ids: experimentIds
    })
    
    ElMessage.success(`成功创建实验组，包含 ${experimentIds.length} 个实验结果`)
    
    // 清空选择
    selectedRows.value = []
    
    // 跳转到实验组列表
    router.push('/groups')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('创建实验组失败')
    }
  }
}

const openAllTensorBoard = async () => {
  try {
    // 先获取系统配置，获取 TensorBoard 基础路径
    const { data: config } = await experimentApi.getConfig()
    
    const basePath = config.remote?.tensorboard_base_path
    if (!basePath) {
      ElMessage.warning('请先在系统设置中配置 TensorBoard 基础路径')
      return
    }
    
    // 使用默认端口 6006
    const port = 6006
    
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
    
    // 启动计时器更新耗时
    timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000)
      const elapsedSpan = document.getElementById('elapsed-time')
      if (elapsedSpan) {
        elapsedSpan.textContent = formatElapsedTime(elapsed)
      }
    }, 1000)
    
    try {
      // 直接使用基础路径启动 TensorBoard
      await experimentApi.startTensorBoard(basePath, port)
      
      // 清除计时器
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      
      // 计算总耗时
      const totalElapsed = Math.floor((Date.now() - startTime) / 1000)
      
      // 关闭加载弹窗
      const closeBtn = document.querySelector('.el-message-box__headerbtn')
      if (closeBtn) closeBtn.click()
      
      // 显示成功消息
      ElMessage.success({
        message: `TensorBoard 启动成功，正在查看所有实验结果，耗时 ${formatElapsedTime(totalElapsed)}`,
        duration: 5000
      })
      
      // 提供手动链接
      setTimeout(() => {
        ElMessage.info({
          dangerouslyUseHTMLString: true,
          message: `如果浏览器未自动打开，请手动访问：<a href="http://localhost:${port}" target="_blank" style="color: #409eff; text-decoration: underline;">http://localhost:${port}</a>`,
          duration: 10000
        })
      }, 3000)
    } catch (error) {
      // 清除计时器
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      
      // 关闭加载弹窗
      const closeBtn = document.querySelector('.el-message-box__headerbtn')
      if (closeBtn) closeBtn.click()
      
      // 显示错误消息
      const errorMsg = error.response?.data?.error || error.message || '启动 TensorBoard 失败'
      ElMessage.error({
        message: errorMsg,
        duration: 10000
      })
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.message || '获取配置失败'
    ElMessage.error({
      message: errorMsg,
      duration: 10000
    })
  }
}

// 打开批量编辑对话框
const openBatchEditDialog = () => {
  // 重置表单
  batchEditForm.value = {
    algorithm: '',
    map: '',
    environment: ''
  }
  batchEditDialogVisible.value = true
}

// 确认批量编辑
const confirmBatchEdit = async () => {
  if (!batchEditForm.value.algorithm && !batchEditForm.value.map && !batchEditForm.value.environment) {
    ElMessage.warning('请至少填写一个字段')
    return
  }

  try {
    // 准备更新数据
    const updateData = {}
    if (batchEditForm.value.algorithm) updateData.algorithm = batchEditForm.value.algorithm
    if (batchEditForm.value.map) updateData.map = batchEditForm.value.map
    if (batchEditForm.value.environment) updateData.environment = batchEditForm.value.environment

    // 获取要更新的实验 ID 列表
    const idsToUpdate = allSelected.value 
      ? allExperimentIds.value 
      : selectedRows.value.map(row => row.id)

    // 批量更新
    const updatePromises = idsToUpdate.map(id => 
      experimentApi.updateExperiment(id, updateData)
    )
    
    await Promise.all(updatePromises)
    
    ElMessage.success(`成功更新 ${idsToUpdate.length} 个实验`)
    batchEditDialogVisible.value = false
    
    // 清空选择
    selectedRows.value = []
    allSelected.value = false
    allExperimentIds.value = []
    
    // 重新加载数据
    loadExperiments()
  } catch (error) {
    console.error('批量更新失败:', error)
    ElMessage.error('批量更新失败')
  }
}

onMounted(() => {
  loadExperiments()
})
</script>
