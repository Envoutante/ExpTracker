<template>
  <div>
    <h2 style="margin-bottom: 20px;">📥 批量导入实验结果</h2>
    
    <!-- 全局导入状态提示（切换页面后回来仍然显示） -->
    <el-alert
      v-if="importStore.isImporting"
      type="info"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      <template #title>
        <div style="display: flex; align-items: center; gap: 12px;">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在导入实验数据，请勿关闭浏览器...</span>
          <span style="color: #409eff; font-weight: bold; font-family: 'Consolas', 'Courier New', Courier, monospace; min-width: 60px;">{{ importStore.importElapsedTime }}</span>
          <el-button type="danger" size="small" @click="cancelImport" style="margin-left: 12px;">
            取消导入
          </el-button>
        </div>
      </template>
      <div style="margin-top: 8px;">
        <el-progress 
          :percentage="importStore.importProgress" 
          :stroke-width="10"
          style="margin-bottom: 8px;"
        />
        <span>{{ importStore.importStatus }}</span>
      </div>
    </el-alert>
    
    <el-card style="margin-bottom: 20px;">
      <div style="display: flex; align-items: center; gap: 16px;">
        <el-button type="primary" @click="scanExperiments" :loading="importStore.isScanning" :disabled="importStore.isImporting">
          <el-icon><Search /></el-icon>
          <span v-if="!importStore.isScanning">扫描远程实验日志</span>
          <span v-else>扫描中... {{ importStore.scanElapsedTime }}</span>
        </el-button>
        <span style="color: #909399; font-size: 14px;">
          将自动扫描系统设置中配置的 TensorBoard 基础路径下的实验结果日志
        </span>
      </div>
      
      <!-- 扫描进度和状态 -->
      <div v-if="importStore.isScanning" style="margin-top: 20px;">
        <el-progress 
          :percentage="importStore.scanProgress" 
          :status="importStore.scanProgress === 100 ? 'success' : undefined"
          :indeterminate="importStore.scanProgress >= 90 && importStore.scanProgress < 100"
        >
          <template #default="{ percentage }">
            <span style="font-size: 14px;">{{ percentage }}%</span>
          </template>
        </el-progress>
        <div style="margin-top: 12px; color: #606266; font-size: 14px;">
          <div style="margin-bottom: 4px;">{{ importStore.scanStatus }}</div>
          <div style="color: #909399; font-size: 12px;">{{ importStore.scanTip }}</div>
        </div>
      </div>
      
      <el-alert
        v-if="!hasConfig"
        title="请先配置远程服务器"
        type="warning"
        :closable="false"
        style="margin-top: 16px;"
      >
        请前往"系统设置"页面配置远程服务器和 TensorBoard 基础路径
      </el-alert>
    </el-card>

    <el-card v-if="importStore.scannedExperiments.length > 0" style="min-height: 400px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>扫描结果（共 {{ importStore.scannedExperiments.length }} 个实验结果）</span>
          <div>
            <el-button 
              size="small" 
              @click="showBatchSetDialog"
              :disabled="importStore.selectedExperiments.length === 0 || importStore.isImporting"
            >
              批量设置
            </el-button>
            <el-button 
              size="small" 
              @click="clearResults"
              :disabled="importStore.isImporting"
            >
              清空结果
            </el-button>
            <el-button type="primary" size="small" @click="importSelected" :loading="importStore.isImporting" :disabled="importStore.selectedExperiments.length === 0 || importStore.isImporting">
              <span v-if="!importStore.isImporting">导入选中的 {{ importStore.selectedExperiments.length }} 个实验结果</span>
              <span v-else>导入中...</span>
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="paginatedExperiments" 
        @selection-change="handleSelectionChange"
        @select-all="handleSelectAll"
        style="width: 100%"
        stripe
        ref="tableRef"
      >
        <el-table-column 
          type="selection" 
          width="55" 
          :selectable="(row) => !importStore.isImporting"
          :reserve-selection="false"
        />
        <el-table-column prop="timestamp" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatTimestamp(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="实验结果名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="algorithm" label="算法" width="110">
          <template #default="{ row }">
            <el-input 
              v-model="row.algorithm" 
              size="small" 
              placeholder="算法"
              class="borderless-input"
            />
          </template>
        </el-table-column>
        <el-table-column prop="map" label="地图" width="110">
          <template #default="{ row }">
            <el-input 
              v-model="row.map" 
              size="small" 
              placeholder="地图"
              class="borderless-input"
            />
          </template>
        </el-table-column>
        <el-table-column prop="environment" label="环境" width="110">
          <template #default="{ row }">
            <el-input 
              v-model="row.environment" 
              size="small" 
              placeholder="环境"
              class="borderless-input"
            />
          </template>
        </el-table-column>
        <el-table-column prop="tb_log_path" label="TensorBoard 路径" min-width="300" show-overflow-tooltip />
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="importStore.scannedExperiments.length"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>
    
    <el-card v-else style="min-height: 400px;">
      <div style="display: flex; align-items: center; justify-content: center; min-height: 350px;">
        <el-empty description="当前没有扫描到实验结果日志">
          <template #image>
            <el-icon :size="80" style="color: #c0c4cc;">
              <FolderOpened />
            </el-icon>
          </template>
          <template #default>
            <p style="color: #909399; margin-bottom: 16px;">
              点击上方"扫描远程实验日志"按钮开始扫描
            </p>
          </template>
        </el-empty>
      </div>
    </el-card>
    
    <!-- 批量设置对话框 -->
    <el-dialog v-model="batchSetDialogVisible" title="批量设置" width="500px">
      <el-form label-width="80px">
        <el-form-item label="算法">
          <el-input v-model="batchSetForm.algorithm" placeholder="留空表示不修改" clearable />
        </el-form-item>
        <el-form-item label="地图">
          <el-input v-model="batchSetForm.map" placeholder="留空表示不修改" clearable />
        </el-form-item>
        <el-form-item label="环境">
          <el-input v-model="batchSetForm.environment" placeholder="留空表示不修改" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchSetDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="applyBatchSet">应用到选中的 {{ importStore.selectedExperiments.length }} 个实验结果</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useImportStore } from '../stores/importStore'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search, FolderOpened, Loading } from '@element-plus/icons-vue'

const API_BASE = '/api'
const router = useRouter()
const importStore = useImportStore()

const hasConfig = ref(true)
const tableRef = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const batchSetDialogVisible = ref(false)
const batchSetForm = ref({
  algorithm: '',
  map: '',
  environment: ''
})
const isSelectingAll = ref(false) // 标记是否正在执行全选操作

const paginatedExperiments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return importStore.scannedExperiments.slice(start, end)
})

// 监听分页变化，恢复选中状态
watch([currentPage, pageSize], () => {
  nextTick(() => {
    if (tableRef.value && importStore.selectedExperiments.length > 0) {
      // 恢复当前页的选中状态
      paginatedExperiments.value.forEach(row => {
        const isSelected = importStore.selectedExperiments.some(exp => exp.tb_log_path === row.tb_log_path)
        tableRef.value.toggleRowSelection(row, isSelected)
      })
    }
  })
})

const formatElapsedTime = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

const scanStatusMessages = [
  { progress: 0, status: '连接远程服务器...', tip: '正在建立 SSH 连接' },
  { progress: 20, status: '读取基础路径配置...', tip: '验证 TensorBoard 日志目录' },
  { progress: 40, status: '扫描实验目录...', tip: '查找包含 TensorBoard 日志的目录' },
  { progress: 60, status: '分析实验文件...', tip: '识别有效的实验日志文件' },
  { progress: 80, status: '获取文件元数据...', tip: '读取实验创建时间和路径信息' },
  { progress: 90, status: '整理扫描结果...', tip: '这可能需要一些时间，请耐心等待' },
  { progress: 100, status: '扫描完成！', tip: '已成功获取所有实验信息' }
]

const updateScanStatus = (progress) => {
  const statusMsg = scanStatusMessages.find(msg => msg.progress <= progress) || scanStatusMessages[0]
  const nextMsg = scanStatusMessages.find(msg => msg.progress > progress)
  
  if (nextMsg) {
    importStore.setScanStatus(nextMsg.status)
    importStore.setScanTip(nextMsg.tip)
  } else {
    importStore.setScanStatus(statusMsg.status)
    importStore.setScanTip(statusMsg.tip)
  }
}

const checkConfig = async () => {
  try {
    const { data } = await axios.get(`${API_BASE}/config`)
    hasConfig.value = data.mode !== 'local' && data.remote.tensorboard_base_path
  } catch (error) {
    hasConfig.value = false
  }
}

const scanExperiments = async () => {
  // 如果正在导入，禁止扫描
  if (importStore.isImporting) {
    ElMessage.warning('正在导入中，请稍候')
    return
  }
  
  // 清空之前的扫描结果
  importStore.clearScannedExperiments()
  currentPage.value = 1
  
  importStore.setIsScanning(true)
  importStore.setScanProgress(0)
  updateScanStatus(0)
  
  // 使用 store 中的计时器
  importStore.startScanTimer()
  
  try {
    // 更智能的进度更新
    let currentProgress = 0
    const progressInterval = setInterval(() => {
      if (currentProgress < 40) {
        // 前期快速推进
        currentProgress += 20
      } else if (currentProgress < 80) {
        // 中期稳定推进
        currentProgress += 10
      } else if (currentProgress < 90) {
        // 后期缓慢推进
        currentProgress += 5
      }
      // 90% 后不再自动增长，等待实际完成
      
      if (currentProgress <= 90) {
        importStore.setScanProgress(currentProgress)
        updateScanStatus(currentProgress)
      }
    }, 500)
    
    const { data } = await axios.post(`${API_BASE}/scan-experiments`)
    
    clearInterval(progressInterval)
    importStore.stopScanTimer()
    
    importStore.setScanProgress(100)
    updateScanStatus(100)
    
    importStore.setScannedExperiments(data.experiments)
    currentPage.value = 1  // 重置到第一页
    
    const totalElapsed = Math.floor((Date.now() - importStore.scanStartTime) / 1000)
    ElMessage.success(`扫描完成，找到 ${data.total} 个实验结果，耗时 ${formatElapsedTime(totalElapsed)}`)
    
    // 进度条显示完成后再重置
    setTimeout(() => {
      importStore.setScanProgress(0)
    }, 1500)
  } catch (error) {
    importStore.stopScanTimer()
    ElMessage.error(error.response?.data?.error || '扫描失败')
    importStore.setScanProgress(0)
    importStore.setScanStatus('扫描失败')
    importStore.setScanTip(error.response?.data?.error || '请检查网络连接和服务器配置')
  } finally {
    importStore.setIsScanning(false)
  }
}

const handleSelectionChange = (selection) => {
  // 如果正在导入，阻止选择变更
  if (importStore.isImporting) {
    return
  }
  
  // 如果正在执行全选操作，忽略表格的选择变化事件
  if (isSelectingAll.value) {
    return
  }
  importStore.setSelectedExperiments(selection)
}

// 处理表格全选事件
const handleSelectAll = async (selection) => {
  // 如果正在导入，阻止全选
  if (importStore.isImporting) {
    ElMessage.warning('正在导入中，无法选择')
    // 清除表格选择
    nextTick(() => {
      tableRef.value?.clearSelection()
    })
    return
  }
  
  isSelectingAll.value = true
  
  // 判断是全选还是取消全选
  const isSelectingAllRows = selection.length > 0
  
  if (isSelectingAllRows) {
    // 全选所有实验（不仅仅是当前页）
    importStore.setSelectedExperiments([...importStore.scannedExperiments])
    
    // 同步表格的选中状态
    await nextTick()
    if (tableRef.value) {
      paginatedExperiments.value.forEach(row => {
        tableRef.value.toggleRowSelection(row, true)
      })
    }
    
    ElMessage.success(`已选中所有 ${importStore.scannedExperiments.length} 个实验结果`)
  } else {
    // 取消全选
    importStore.setSelectedExperiments([])
    
    await nextTick()
    if (tableRef.value) {
      tableRef.value.clearSelection()
    }
  }
  
  // 延迟重置标记，确保表格事件处理完成
  setTimeout(() => {
    isSelectingAll.value = false
  }, 100)
}

const showBatchSetDialog = () => {
  // 重置表单
  batchSetForm.value = {
    algorithm: '',
    map: '',
    environment: ''
  }
  batchSetDialogVisible.value = true
}

const applyBatchSet = () => {
  if (importStore.selectedExperiments.length === 0) {
    ElMessage.warning('请先选择要设置的实验结果')
    return
  }
  
  // 应用批量设置到选中的实验
  importStore.selectedExperiments.forEach(exp => {
    if (batchSetForm.value.algorithm) {
      exp.algorithm = batchSetForm.value.algorithm
    }
    if (batchSetForm.value.map) {
      exp.map = batchSetForm.value.map
    }
    if (batchSetForm.value.environment) {
      exp.environment = batchSetForm.value.environment
    }
  })
  
  batchSetDialogVisible.value = false
  ElMessage.success(`已为 ${importStore.selectedExperiments.length} 个实验结果设置属性`)
}

const importSelected = async () => {
  if (importStore.selectedExperiments.length === 0) {
    ElMessage.warning('请先选择要导入的实验结果')
    return
  }
  
  if (importStore.isImporting) {
    ElMessage.warning('正在导入中，请稍候')
    return
  }
  
  // 使用 store 中的方法执行导入（切换页面不会中断）
  const result = await importStore.executeImport([...importStore.selectedExperiments])
  
  if (result.success) {
    ElMessage.success(`${result.message}，耗时 ${importStore.importElapsedTime}`)
    
    // 清空表格选中状态
    if (tableRef.value) {
      tableRef.value.clearSelection()
    }
    
    // 3 秒后重置导入状态
    setTimeout(() => {
      importStore.resetImportState()
    }, 3000)
  } else if (!result.cancelled) {
    ElMessage.error(result.message)
  } else {
    ElMessage.warning('导入已取消')
  }
}

// 取消导入
const cancelImport = () => {
  importStore.cancelImport()
  ElMessage.warning('正在取消导入...')
}

const clearResults = () => {
  if (importStore.isImporting) {
    ElMessage.warning('正在导入中，无法清空')
    return
  }
  importStore.clearScannedExperiments()
  importStore.resetImportState()
  currentPage.value = 1
  ElMessage.success('已清空扫描结果')
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '未知'
  return new Date(timestamp * 1000).toLocaleString('zh-CN')
}

// 恢复之前的选中状态
onMounted(async () => {
  await checkConfig()
  
  // 如果有之前选中的实验，恢复选中状态
  if (importStore.selectedExperiments.length > 0) {
    await nextTick()
    if (tableRef.value) {
      importStore.selectedExperiments.forEach(row => {
        tableRef.value.toggleRowSelection(row, true)
      })
    }
  }
})
</script>

<style scoped>
/* 无边框输入框样式 - 仅底部横线 */
.borderless-input :deep(.el-input__wrapper) {
  box-shadow: none;
  background-color: transparent;
  border-bottom: 1px solid #dcdfe6;
  border-radius: 0;
  padding: 0 4px;
  transition: border-color 0.3s;
}

.borderless-input :deep(.el-input__wrapper:hover) {
  border-bottom-color: #c0c4cc;
}

.borderless-input :deep(.el-input__wrapper.is-focus) {
  border-bottom-color: #409eff;
  border-bottom-width: 2px;
}

.borderless-input :deep(.el-input__inner) {
  text-align: center;
}
</style>
