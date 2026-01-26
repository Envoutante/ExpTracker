import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_BASE = '/api'

// 全局计时器引用，不在组件中
let globalScanTimer = null
let globalImportTimer = null
let globalPollingTimer = null
let currentTaskId = null

export const useImportStore = defineStore('import', () => {
  const scannedExperiments = ref([])
  const selectedExperiments = ref([])
  const scanProgress = ref(0)
  const isScanning = ref(false)
  const scanStartTime = ref(0)
  const scanElapsedTime = ref('00:00:00')
  const scanStatus = ref('准备扫描...')
  const scanTip = ref('')
  
  // 导入相关状态
  const isImporting = ref(false)
  const importStartTime = ref(0)
  const importElapsedTime = ref('00:00:00')
  const importProgress = ref(0)
  const importTotal = ref(0)
  const importCurrent = ref(0)
  const importStatus = ref('')
  const importTaskId = ref(null)  // 当前导入任务ID

  // 从 localStorage 恢复数据
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem('importStore')
      if (stored) {
        const data = JSON.parse(stored)
        scannedExperiments.value = data.scannedExperiments || []
        selectedExperiments.value = data.selectedExperiments || []
        scanStartTime.value = data.scanStartTime || 0
        scanElapsedTime.value = data.scanElapsedTime || '00:00:00'
        scanStatus.value = data.scanStatus || '准备扫描...'
        scanTip.value = data.scanTip || ''
        
        // 恢复导入状态
        importStartTime.value = data.importStartTime || 0
        importElapsedTime.value = data.importElapsedTime || '00:00:00'
        importProgress.value = data.importProgress || 0
        importTotal.value = data.importTotal || 0
        importCurrent.value = data.importCurrent || 0
        importStatus.value = data.importStatus || ''
        importTaskId.value = data.importTaskId || null
        
        // 如果之前正在扫描，恢复计时器
        if (data.isScanning && data.scanStartTime) {
          isScanning.value = true
          startScanTimer(data.scanStartTime)
        }
        
        // 如果之前正在导入且有任务ID，恢复轮询
        if (data.isImporting && data.importTaskId) {
          isImporting.value = true
          currentTaskId = data.importTaskId
          startImportTimer(data.importStartTime)
          startPolling(data.importTaskId)
        }
      }
    } catch (error) {
      console.error('Failed to load from storage:', error)
    }
  }

  // 保存到 localStorage
  const saveToStorage = () => {
    try {
      const data = {
        scannedExperiments: scannedExperiments.value,
        selectedExperiments: selectedExperiments.value,
        scanStartTime: scanStartTime.value,
        scanElapsedTime: scanElapsedTime.value,
        isScanning: isScanning.value,
        scanStatus: scanStatus.value,
        scanTip: scanTip.value,
        // 导入状态
        isImporting: isImporting.value,
        importStartTime: importStartTime.value,
        importElapsedTime: importElapsedTime.value,
        importProgress: importProgress.value,
        importTotal: importTotal.value,
        importCurrent: importCurrent.value,
        importStatus: importStatus.value,
        importTaskId: importTaskId.value
      }
      localStorage.setItem('importStore', JSON.stringify(data))
    } catch (error) {
      console.error('Failed to save to storage:', error)
    }
  }

  const setScannedExperiments = (experiments) => {
    scannedExperiments.value = experiments
    saveToStorage()
  }

  const setSelectedExperiments = (experiments) => {
    selectedExperiments.value = experiments
    saveToStorage()
  }

  const setScanProgress = (progress) => {
    scanProgress.value = progress
  }

  const setIsScanning = (scanning) => {
    isScanning.value = scanning
    saveToStorage()
  }

  const setScanStartTime = (time) => {
    scanStartTime.value = time
    saveToStorage()
  }

  const setScanElapsedTime = (time) => {
    scanElapsedTime.value = time
    saveToStorage()
  }

  const setScanStatus = (status) => {
    scanStatus.value = status
    saveToStorage()
  }

  const setScanTip = (tip) => {
    scanTip.value = tip
    saveToStorage()
  }

  const formatElapsedTime = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }

  const startScanTimer = (startTime = null) => {
    // 清除旧的计时器
    if (globalScanTimer) {
      clearInterval(globalScanTimer)
    }
    
    if (startTime) {
      // 恢复之前的计时器
      scanStartTime.value = startTime
    } else {
      // 新的计时器
      scanStartTime.value = Date.now()
    }
    scanElapsedTime.value = '00:00:00'
    
    globalScanTimer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - scanStartTime.value) / 1000)
      scanElapsedTime.value = formatElapsedTime(elapsed)
      saveToStorage()
    }, 1000)
  }

  const stopScanTimer = () => {
    if (globalScanTimer) {
      clearInterval(globalScanTimer)
      globalScanTimer = null
    }
    saveToStorage()
  }

  const clearScannedExperiments = () => {
    scannedExperiments.value = []
    selectedExperiments.value = []
    scanProgress.value = 0
    scanStartTime.value = 0
    scanElapsedTime.value = '00:00:00'
    isScanning.value = false
    scanStatus.value = '准备扫描...'
    scanTip.value = ''
    stopScanTimer()
    saveToStorage()
  }

  // 导入计时器
  const startImportTimer = (startTime = null) => {
    if (globalImportTimer) {
      clearInterval(globalImportTimer)
    }
    
    if (startTime) {
      importStartTime.value = startTime
    } else {
      importStartTime.value = Date.now()
    }
    importElapsedTime.value = '00:00:00'
    
    globalImportTimer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - importStartTime.value) / 1000)
      importElapsedTime.value = formatElapsedTime(elapsed)
      saveToStorage()
    }, 1000)
  }

  const stopImportTimer = () => {
    if (globalImportTimer) {
      clearInterval(globalImportTimer)
      globalImportTimer = null
    }
    saveToStorage()
  }

  // 停止轮询
  const stopPolling = () => {
    if (globalPollingTimer) {
      clearInterval(globalPollingTimer)
      globalPollingTimer = null
    }
    currentTaskId = null
  }

  // 开始轮询任务状态
  const startPolling = (taskId) => {
    stopPolling()  // 先清除之前的轮询
    currentTaskId = taskId
    
    const poll = async () => {
      if (!currentTaskId || currentTaskId !== taskId) {
        return  // 任务已取消或已更换
      }
      
      try {
        const { data } = await axios.get(`${API_BASE}/import-status/${taskId}`)
        
        // 更新进度
        importProgress.value = data.progress || 0
        importTotal.value = data.total || importTotal.value
        importCurrent.value = data.current || 0
        importStatus.value = data.message || ''
        saveToStorage()
        
        // 检查是否完成
        if (data.status === 'completed') {
          stopPolling()
          stopImportTimer()
          isImporting.value = false
          importProgress.value = 100
          importTaskId.value = null
          selectedExperiments.value = []
          saveToStorage()
          
          // 触发完成回调
          if (importCompleteCallback) {
            importCompleteCallback({ 
              success: true, 
              message: data.message,
              data 
            })
            importCompleteCallback = null
          }
          return
        }
        
        if (data.status === 'failed') {
          stopPolling()
          stopImportTimer()
          isImporting.value = false
          importTaskId.value = null
          saveToStorage()
          
          if (importCompleteCallback) {
            importCompleteCallback({ 
              success: false, 
              message: data.message || '导入失败'
            })
            importCompleteCallback = null
          }
          return
        }
        
        // 继续轮询
        globalPollingTimer = setTimeout(poll, 1000)  // 每秒轮询一次
      } catch (error) {
        console.error('轮询任务状态失败:', error)
        // 网络错误时继续重试，但降低频率
        globalPollingTimer = setTimeout(poll, 3000)
      }
    }
    
    // 立即执行第一次轮询
    poll()
  }

  // 完成回调
  let importCompleteCallback = null

  // 执行导入（异步任务 + 轮询）
  const executeImport = async (experimentsToImport) => {
    if (isImporting.value) {
      return { success: false, message: '正在导入中，请稍候' }
    }
    
    isImporting.value = true
    importTotal.value = experimentsToImport.length
    importCurrent.value = 0
    importProgress.value = 0
    importStatus.value = `正在启动导入任务...`
    startImportTimer()
    saveToStorage()
    
    try {
      // 发起导入请求，立即返回任务ID
      const { data } = await axios.post(`${API_BASE}/import-experiments`, {
        experiments: experimentsToImport
      }, {
        timeout: 30000  // 30秒足够获取任务ID
      })
      
      if (!data.task_id) {
        throw new Error('未获取到任务ID')
      }
      
      // 保存任务ID并开始轮询
      importTaskId.value = data.task_id
      currentTaskId = data.task_id
      importStatus.value = '导入任务已启动，正在处理...'
      saveToStorage()
      
      // 返回 Promise，在轮询完成时 resolve
      return new Promise((resolve) => {
        importCompleteCallback = resolve
        startPolling(data.task_id)
      })
      
    } catch (error) {
      stopImportTimer()
      isImporting.value = false
      importTaskId.value = null
      
      const message = error.response?.data?.error || error.message || '启动导入任务失败'
      importStatus.value = message
      saveToStorage()
      
      return { 
        success: false, 
        message
      }
    }
  }

  // 取消导入
  const cancelImport = () => {
    stopPolling()
    stopImportTimer()
    isImporting.value = false
    importProgress.value = 0
    importStatus.value = '导入已取消'
    importTaskId.value = null
    
    // 取消回调
    if (importCompleteCallback) {
      importCompleteCallback({ success: false, message: '导入已取消', cancelled: true })
      importCompleteCallback = null
    }
    
    saveToStorage()
  }

  const resetImportState = () => {
    stopPolling()
    stopImportTimer()
    isImporting.value = false
    importStartTime.value = 0
    importElapsedTime.value = '00:00:00'
    importProgress.value = 0
    importTotal.value = 0
    importCurrent.value = 0
    importStatus.value = ''
    importTaskId.value = null
    importCompleteCallback = null
    saveToStorage()
  }

  // 初始化时加载数据
  loadFromStorage()

  return {
    scannedExperiments,
    selectedExperiments,
    scanProgress,
    isScanning,
    scanStartTime,
    scanElapsedTime,
    scanStatus,
    scanTip,
    // 导入相关
    isImporting,
    importStartTime,
    importElapsedTime,
    importProgress,
    importTotal,
    importCurrent,
    importStatus,
    importTaskId,
    // 方法
    setScannedExperiments,
    setSelectedExperiments,
    setScanProgress,
    setIsScanning,
    setScanStartTime,
    setScanElapsedTime,
    setScanStatus,
    setScanTip,
    startScanTimer,
    stopScanTimer,
    clearScannedExperiments,
    loadFromStorage,
    // 导入方法
    startImportTimer,
    stopImportTimer,
    executeImport,
    cancelImport,
    resetImportState
  }
})
