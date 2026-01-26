import axios from 'axios'

const API_BASE = '/api'

export const experimentApi = {
  // 获取实验列表
  getExperiments(params) {
    return axios.get(`${API_BASE}/experiments`, { params })
  },
  
  // 获取实验详情
  getExperiment(id) {
    return axios.get(`${API_BASE}/experiments/${id}`)
  },
  
  // 创建实验
  createExperiment(data) {
    return axios.post(`${API_BASE}/experiments`, data)
  },
  
  // 更新实验
  updateExperiment(id, data) {
    return axios.put(`${API_BASE}/experiments/${id}`, data)
  },
  
  // 删除实验
  deleteExperiment(id) {
    return axios.delete(`${API_BASE}/experiments/${id}`)
  },
  
  // 启动 TensorBoard
  // local_cache_path: 可选的本地缓存路径，如果提供则使用本地 TensorBoard
  startTensorBoard(log_path, port, local_cache_path = null) {
    return axios.post(`${API_BASE}/tensorboard/start`, { log_path, port, local_cache_path })
  },
  
  // 批量启动 TensorBoard（多个实验）
  // local_cache_paths: 可选的本地缓存路径数组
  startTensorBoardMultiple(log_paths, experiment_names, port, local_cache_paths = null) {
    return axios.post(`${API_BASE}/tensorboard/start`, { log_paths, experiment_names, port, local_cache_paths })
  },
  
  // 停止 TensorBoard
  stopTensorBoard(port) {
    return axios.post(`${API_BASE}/tensorboard/stop`, { port })
  },
  
  // 获取 TensorBoard 状态
  getTensorBoardStatus(port) {
    return axios.get(`${API_BASE}/tensorboard/status`, { params: { port } })
  },
  
  // 获取所有标签
  getTags() {
    return axios.get(`${API_BASE}/tags`)
  },
  
  // 导出数据
  exportData() {
    return axios.post(`${API_BASE}/export`)
  },
  
  // 生成运行命令
  generateCommand(data) {
    return axios.post(`${API_BASE}/generate-command`, data)
  },
  
  // 生成实验 ID
  generateExperimentId() {
    return axios.get(`${API_BASE}/generate-experiment-id`)
  },
  
  // 获取系统配置
  getConfig() {
    return axios.get(`${API_BASE}/config`)
  },
  
  // ==================== 实验组 API ====================
  
  // 获取所有实验组（支持分页）
  getGroups(params = {}) {
    return axios.get(`${API_BASE}/groups`, { params })
  },
  
  // 获取实验组详情
  getGroup(id) {
    return axios.get(`${API_BASE}/groups/${id}`)
  },
  
  // 创建实验组
  createGroup(data) {
    return axios.post(`${API_BASE}/groups`, data)
  },
  
  // 更新实验组
  updateGroup(id, data) {
    return axios.put(`${API_BASE}/groups/${id}`, data)
  },
  
  // 删除实验组
  deleteGroup(id) {
    return axios.delete(`${API_BASE}/groups/${id}`)
  },
  
  // 向实验组添加实验
  addExperimentsToGroup(groupId, experimentIds) {
    return axios.post(`${API_BASE}/groups/${groupId}/experiments`, { experiment_ids: experimentIds })
  },
  
  // 从实验组移除实验
  removeExperimentFromGroup(groupId, experimentId) {
    return axios.delete(`${API_BASE}/groups/${groupId}/experiments/${experimentId}`)
  },
  
  // ==================== 附件 API ====================
  
  // 上传附件
  uploadAttachment(experimentId, file) {
    const formData = new FormData()
    formData.append('file', file)
    return axios.post(`${API_BASE}/experiments/${experimentId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 下载附件（返回下载链接）
  getAttachmentUrl(experimentId, attachmentId) {
    return `${API_BASE}/experiments/${experimentId}/attachments/${attachmentId}`
  },
  
  // 删除附件
  deleteAttachment(experimentId, attachmentId) {
    return axios.delete(`${API_BASE}/experiments/${experimentId}/attachments/${attachmentId}`)
  }
}
