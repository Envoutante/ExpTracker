<template>
  <div class="experiment-view">
    <!-- 顶部操作栏 -->
    <div class="header-bar">
      <el-button @click="goBack" text>
        <el-icon><ArrowLeft /></el-icon>
        返回实验结果列表
      </el-button>
      <div class="header-actions">
        <el-button v-if="isView && !isNew" @click="exportToHTML">
          <el-icon><Download /></el-icon>
          导出 HTML
        </el-button>
        <el-button v-if="isView" type="primary" @click="toggleEdit">
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
      <!-- 实验标题 -->
      <div class="notebook-title">
        <el-input 
          v-if="!isView"
          v-model="form.name" 
          placeholder="实验名称"
          class="title-input"
          size="large"
        />
        <h1 v-else class="title-text">{{ form.name }}</h1>
      </div>

      <!-- 元信息 -->
      <div class="meta-info">
        <div class="meta-item">
          <span class="meta-label">状态：</span>
          <el-select v-if="!isView" v-model="form.status" size="small" style="width: 120px;">
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
          <el-tag v-else :type="getStatusType(form.status)">{{ getStatusText(form.status) }}</el-tag>
        </div>
        
        <div class="meta-item">
          <span class="meta-label">标签：</span>
          <el-select 
            v-if="!isView"
            v-model="form.tags" 
            multiple 
            placeholder="选择标签"
            size="small"
            style="width: 120px;"
          >
            <el-option 
              v-for="tag in availableTags" 
              :key="tag" 
              :label="tag" 
              :value="tag"
            />
          </el-select>
          
          <div v-else class="tags-display">
            <el-tag v-for="tag in form.tags" :key="tag" size="small" style="margin-right: 8px;">{{ tag }}</el-tag>
            <span v-if="form.tags.length === 0" class="empty-text">无标签</span>
          </div>
        </div>

        <div class="meta-item">
          <span class="meta-label">创建时间：</span>
          <span class="meta-value">{{ formatDate(form.created_at) }}</span>
        </div>
      </div>

      <!-- 动态渲染模块 -->
      <template v-for="module in sortedModules" :key="module.id">
        <!-- 实验配置 -->
        <div v-if="module.id === 'config' && isModuleEnabled('config')" class="notebook-section">
          <div class="section-header">
            <el-icon><Setting /></el-icon>
            <span>实验配置</span>
          </div>
          
          <!-- 实验 ID -->
          <div v-if="form.experiment_id" class="experiment-id-section">
            <div class="experiment-id-label">实验 ID</div>
            <div class="experiment-id-value">
              <code>{{ form.experiment_id }}</code>
              <el-button size="small" text @click="copyExperimentId">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
            </div>
          </div>
          
          <!-- 命令参数配置 -->
          <div class="command-params-section">
            <div class="section-subtitle">
              <span>命令参数 (-- 开头)</span>
              <el-button v-if="!isView" size="small" @click="addCommandParam">
                <el-icon><CirclePlus /></el-icon>
                添加参数
              </el-button>
            </div>
            
            <el-alert
              title="命令参数：以 -- 开头的参数，如 --config=vdn、--env-config=sc2"
              type="info"
              :closable="false"
              style="margin-bottom: 12px;"
            />
            
            <!-- 编辑模式 -->
            <div v-if="!isView" class="command-params-table">
              <div class="command-params-header">
                <div class="param-col-checkbox">启用</div>
                <div class="param-col-key">参数名</div>
                <div class="param-col-value">值类型</div>
                <div class="param-col-desc">参数值</div>
                <div class="param-col-actions">操作</div>
              </div>
              <div v-for="(param, index) in commandParams" :key="index" class="command-params-row">
                <div class="param-col-checkbox">
                  <el-checkbox 
                    v-model="param.enabled" 
                    @change="generateCommandRealtime"
                  />
                </div>
                <div class="param-col-key">
                  <el-input 
                    v-model="param.name" 
                    placeholder="如: config"
                    size="small"
                    @input="generateCommandRealtime"
                  />
                </div>
                <div class="param-col-value">
                  <el-select 
                    v-model="param.type" 
                    size="small"
                    @change="onParamTypeChange(index)"
                  >
                    <el-option label="自定义值" value="fixed" />
                    <el-option label="绑定算法" value="algorithm" />
                    <el-option label="绑定环境" value="environment" />
                    <el-option label="绑定地图" value="map" />
                  </el-select>
                </div>
                <div class="param-col-desc">
                  <!-- 自定义值 -->
                  <el-input 
                    v-if="param.type === 'fixed'"
                    v-model="param.value" 
                    placeholder="参数值"
                    size="small"
                    @input="generateCommandRealtime"
                  />
                  <!-- 绑定算法 -->
                  <el-select 
                    v-else-if="param.type === 'algorithm'"
                    v-model="param.value" 
                    filterable 
                    allow-create
                    placeholder="选择或输入算法"
                    size="small"
                    @change="generateCommandRealtime"
                  >
                    <el-option 
                      v-for="algo in presetAlgorithms" 
                      :key="algo" 
                      :label="algo" 
                      :value="algo"
                    />
                  </el-select>
                  <!-- 绑定环境 -->
                  <el-select 
                    v-else-if="param.type === 'environment'"
                    v-model="param.value" 
                    filterable 
                    allow-create
                    placeholder="选择或输入环境"
                    size="small"
                    @change="onEnvironmentParamChange(index)"
                  >
                    <el-option 
                      v-for="env in presetEnvironments" 
                      :key="env.name" 
                      :label="env.name" 
                      :value="env.name"
                    />
                  </el-select>
                  <!-- 绑定地图 -->
                  <el-select 
                    v-else-if="param.type === 'map'"
                    v-model="param.value" 
                    filterable 
                    allow-create
                    placeholder="选择或输入地图"
                    size="small"
                    @change="generateCommandRealtime"
                    clearable
                  >
                    <el-option 
                      v-for="map in getAvailableMapsForParam(index)" 
                      :key="map" 
                      :label="map" 
                      :value="map"
                    />
                  </el-select>
                </div>
                <div class="param-col-actions">
                  <el-button 
                    size="small" 
                    type="danger" 
                    text
                    @click="removeCommandParam(index)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div v-if="commandParams.length === 0" class="command-params-empty">
                暂无参数，点击"添加参数"开始配置
              </div>
            </div>
            
            <!-- 查看模式 -->
            <div v-else class="command-params-view">
              <div v-if="commandParams.length > 0">
                <div class="params-view-row" v-for="(param, index) in commandParams" :key="index">
                  <div class="param-view-key">--{{ param.name }}</div>
                  <div class="param-view-value">{{ param.value || '未设置' }}</div>
                  <div class="param-view-desc">
                    <el-tag v-if="param.type !== 'fixed'" size="small" type="info">
                      {{ getParamTypeLabel(param.type) }}
                    </el-tag>
                  </div>
                </div>
              </div>
              <div v-else class="command-params-empty">
                无命令参数
              </div>
            </div>
          </div>
          
          <!-- 配置参数表格 -->
          <div class="config-item full-width">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <label>配置参数 (with 后面)</label>
              <el-button v-if="!isView" size="small" @click="addConfigParam">
                <el-icon><CirclePlus /></el-icon>
                添加参数
              </el-button>
            </div>
            
            <el-alert
              title="配置参数：在 with 后面的参数，如 env_args.map_name=2s3z、lr=0.001"
              type="info"
              :closable="false"
              style="margin-bottom: 12px;"
            />
            
            <!-- 编辑模式：表格形式 -->
            <div v-if="!isView" class="params-table">
              <div class="params-table-header">
                <div class="param-col-checkbox">启用</div>
                <div class="param-col-key">参数名</div>
                <div class="param-col-value">参数值</div>
                <div class="param-col-desc">说明</div>
                <div class="param-col-actions">操作</div>
              </div>
              <div v-for="(param, index) in configParams" :key="index" class="params-table-row">
                <div class="param-col-checkbox">
                  <el-checkbox 
                    v-model="param.enabled" 
                    @change="updateConfigJson"
                  />
                </div>
                <div class="param-col-key">
                  <el-input 
                    v-model="param.key" 
                    placeholder="如: lr" 
                    size="small"
                    @input="updateConfigJson"
                  />
                </div>
                <div class="param-col-value">
                  <el-input 
                    v-model="param.value" 
                    placeholder="如: 0.001" 
                    size="small"
                    @input="updateConfigJson"
                  />
                </div>
                <div class="param-col-desc">
                  <el-input 
                    v-model="param.description" 
                    placeholder="参数说明（可选）" 
                    size="small"
                  />
                </div>
                <div class="param-col-actions">
                  <el-button 
                    size="small" 
                    type="danger" 
                    text
                    @click="removeConfigParam(index)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div v-if="configParams.length === 0" class="params-table-empty">
                暂无参数，点击"添加参数"开始配置
              </div>
            </div>
            
            <!-- 查看模式：表格显示 -->
            <div v-else class="params-view-table">
              <div v-if="configParams.length > 0">
                <div class="params-view-row" v-for="(param, index) in configParams" :key="index">
                  <div class="param-view-key">{{ param.key }}</div>
                  <div class="param-view-value">{{ param.value }}</div>
                  <div v-if="param.description" class="param-view-desc">{{ param.description }}</div>
                </div>
              </div>
              <div v-else class="params-table-empty">
                无配置参数
              </div>
            </div>
          </div>
          
          <!-- 输出文件名配置 -->
          <div v-if="!isView" class="config-item full-width" style="margin-top: 24px;">
            <label>输出文件名</label>
            <el-input 
              v-model="form.output_filename" 
              placeholder="默认为实验 ID，如需自定义请输入（不含 .out 后缀）"
              @input="generateCommandRealtime"
            >
              <template #suffix>
                <span style="color: #909399;">.out</span>
              </template>
            </el-input>
            <div style="font-size: 12px; color: #909399; margin-top: 4px;">
              留空则使用实验 ID 作为文件名，如：{{ form.experiment_id || 'exp_YYYYMMDD_NNN' }}_train.out
            </div>
          </div>
          
          <!-- 运行命令 -->
          <div v-if="!isView" class="command-section">
            <div class="command-header">
              <span class="command-label">运行命令</span>
              <div class="command-actions">
                <el-button size="small" @click="showImportCommandDialog">
                  <el-icon><Upload /></el-icon>
                  导入命令
                </el-button>
                <el-button size="small" type="primary" @click="copyCommand" :disabled="!generatedCommand">
                  <el-icon><CopyDocument /></el-icon>
                  复制完整命令
                </el-button>
              </div>
            </div>
            <pre v-if="generatedCommand" class="command-block">{{ generatedCommand }}</pre>
            <div v-else class="command-block command-placeholder">
              填写算法、环境和参数后，命令将自动生成...
            </div>
            <div class="command-tip">
              💡 复制此命令到服务器运行，确保 TensorBoard 日志路径与实验 ID 关联
            </div>
          </div>
        </div>

        <!-- TensorBoard -->
        <div v-if="module.id === 'tensorboard' && isModuleEnabled('tensorboard') && !isNew" class="notebook-section">
          <div class="section-header">
            <el-icon><Monitor /></el-icon>
            <span>TensorBoard</span>
          </div>
          <div class="config-item">
            <label>日志路径</label>
            <el-input v-if="!isView" v-model="form.tb_log_path" placeholder="/path/to/tensorboard/logs" />
            <div v-else class="config-value path-value">{{ form.tb_log_path || '未设置' }}</div>
          </div>
          <div class="config-item" style="margin-top: 12px;">
            <label>端口</label>
            <el-input-number v-if="!isView" v-model="form.tb_port" :min="6000" :max="9999" />
            <div v-else class="config-value">{{ form.tb_port }}</div>
          </div>
          <div v-if="!isNew && form.tb_log_path" style="margin-top: 16px;">
            <el-button type="success" @click="startTB" :loading="tbLoading" size="small">
              <el-icon><VideoPlay /></el-icon> 启动 TensorBoard
            </el-button>
            <el-button type="warning" @click="stopTB" :loading="tbLoading" size="small">
              <el-icon><VideoPause /></el-icon> 停止
            </el-button>
            <el-button 
              v-if="tbRunning" 
              type="primary" 
              size="small"
              @click="openTBInBrowser"
            >
              <el-icon><Link /></el-icon> 在浏览器中打开
            </el-button>
            <div v-if="tbLoading || tbRunning" style="display: inline-flex; align-items: center; margin-left: 10px;">
              <el-tag v-if="tbLoading" type="warning" size="small">启动中...</el-tag>
              <el-tag v-else-if="tbRunning" type="success" size="small">运行中</el-tag>
              <span style="margin-left: 8px; color: #606266; font-size: 13px;">
                <el-icon style="vertical-align: middle;"><Timer /></el-icon>
                {{ tbRunningTime }}
              </span>
            </div>
          </div>
        </div>

        <!-- 实验描述 -->
        <div v-if="module.id === 'description' && isModuleEnabled('description')" class="notebook-section">
          <div class="section-header">
            <el-icon><Document /></el-icon>
            <span>实验描述</span>
          </div>
          <el-input 
            v-if="!isView"
            v-model="form.description" 
            type="textarea" 
            :rows="3" 
            placeholder="简要描述这个实验..."
            class="note-textarea"
          />
          <div v-else class="note-content">{{ form.description || '暂无描述' }}</div>
        </div>

        <!-- 实验目的 -->
        <div v-if="module.id === 'purpose' && isModuleEnabled('purpose')" class="notebook-section">
          <div class="section-header">
            <el-icon><Aim /></el-icon>
            <span>实验目的</span>
          </div>
          <el-input 
            v-if="!isView"
            v-model="form.purpose" 
            type="textarea" 
            :rows="4" 
            placeholder="为什么要做这个实验？想验证什么假设？"
            class="note-textarea"
          />
          <div v-else class="note-content">{{ form.purpose || '暂无实验目的' }}</div>
        </div>

        <!-- 观察记录 -->
        <div v-if="module.id === 'observations' && isModuleEnabled('observations') && !isNew" class="notebook-section">
          <div class="section-header">
            <el-icon><View /></el-icon>
            <span>观察记录</span>
          </div>
          
          <!-- 查看模式 -->
          <div v-if="isView" class="observation-view">
            <div v-if="observations.lastUpdated" class="observation-time">
              {{ formatObservationTime(observations.lastUpdated) }}
            </div>
            
            <div v-if="observations.text || (observations.images && observations.images.length > 0) || (observations.attachments && observations.attachments.length > 0)" class="observation-content">
              <div v-if="observations.text" class="observation-text">{{ observations.text }}</div>
              <div v-if="observations.images && observations.images.length > 0" class="observation-images">
                <el-image
                  v-for="(img, imgIndex) in observations.images"
                  :key="imgIndex"
                  :src="img"
                  :preview-src-list="observations.images"
                  :initial-index="imgIndex"
                  fit="cover"
                  class="observation-image"
                  lazy
                >
                  <template #error>
                    <div class="image-error">
                      <el-icon><Picture /></el-icon>
                      <span>加载失败</span>
                    </div>
                  </template>
                </el-image>
              </div>
              
              <!-- 附件列表（查看模式） -->
              <div v-if="observations.attachments && observations.attachments.length > 0" class="attachments-section">
                <div class="attachments-title">📎 附件</div>
                <div class="attachments-list">
                  <div v-for="(att, index) in observations.attachments" :key="att.id || index" class="attachment-item attachment-item-view">
                    <div class="attachment-icon">
                      <el-icon><Document /></el-icon>
                    </div>
                    <div class="attachment-info">
                      <span class="attachment-name">{{ att.name }}</span>
                      <span class="attachment-size">{{ formatFileSize(att.size) }}</span>
                    </div>
                    <div class="attachment-actions">
                      <el-button 
                        size="small" 
                        type="primary"
                        text 
                        @click="downloadAttachment(att)"
                      >
                        <el-icon><Download /></el-icon>
                        下载
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="empty-observations">
              暂无观察记录
            </div>
          </div>
          
          <!-- 编辑模式 -->
          <div v-else class="observation-edit">
            <el-input
              v-model="newObservation.text"
              type="textarea"
              :rows="6"
              placeholder="记录你的观察和发现..."
              class="observation-input"
            />
            <div class="observation-actions">
              <el-upload
                :auto-upload="false"
                :on-change="handleImageSelect"
                :show-file-list="false"
                accept="image/*"
                multiple
              >
                <el-button size="small">
                  <el-icon><Picture /></el-icon>
                  上传图片
                </el-button>
              </el-upload>
              <el-upload
                :auto-upload="false"
                :on-change="handleCsvSelect"
                :show-file-list="false"
                accept=".csv"
                multiple
              >
                <el-button size="small">
                  <el-icon><Document /></el-icon>
                  上传 CSV
                </el-button>
              </el-upload>
              <span class="image-count" v-if="newObservation.images.length > 0">
                已选择 {{ newObservation.images.length }} 张图片
              </span>
            </div>
            <div v-if="newObservation.images.length > 0" class="preview-images">
              <div v-for="(img, index) in newObservation.images" :key="index" class="preview-image-item">
                <img :src="img" alt="预览" />
                <el-button 
                  type="danger" 
                  size="small" 
                  circle 
                  @click="removePreviewImage(index)"
                  class="remove-btn"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </div>
            
            <!-- 附件列表（编辑模式） -->
            <div v-if="newObservation.attachments.length > 0" class="attachments-section">
              <div class="attachments-title">附件</div>
              <div class="attachments-list">
                <div v-for="(att, index) in newObservation.attachments" :key="att.id || index" class="attachment-item">
                  <div class="attachment-icon">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="attachment-info">
                    <span class="attachment-name">{{ att.name }}</span>
                    <span class="attachment-size">{{ formatFileSize(att.size) }}</span>
                  </div>
                  <div class="attachment-actions">
                    <el-button 
                      v-if="att.id" 
                      size="small" 
                      text 
                      @click="downloadAttachment(att)"
                    >
                      <el-icon><Download /></el-icon>
                    </el-button>
                    <el-button 
                      size="small" 
                      type="danger" 
                      text 
                      @click="removeAttachment(index)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 结果数据 -->
        <div v-if="module.id === 'results' && isModuleEnabled('results') && !isNew" class="notebook-section">
          <div class="section-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>结果数据</span>
          </div>
          <el-input 
            v-if="!isView"
            v-model="form.results" 
            type="textarea" 
            :rows="5" 
            placeholder="关键指标、数值结果等..."
            class="note-textarea"
          />
          <div v-else class="note-content">{{ form.results || '暂无结果数据' }}</div>
        </div>

        <!-- 结论 -->
        <div v-if="module.id === 'conclusion' && isModuleEnabled('conclusion') && !isNew" class="notebook-section">
          <div class="section-header">
            <el-icon><Finished /></el-icon>
            <span>结论与下一步</span>
          </div>
          <el-input 
            v-if="!isView"
            v-model="form.conclusion" 
            type="textarea" 
            :rows="5" 
            placeholder="实验结论和下一步计划..."
            class="note-textarea"
          />
          <div v-else class="note-content">{{ form.conclusion || '暂无结论' }}</div>
        </div>
      </template>
    </div>
    
    <!-- 导入命令对话框 -->
    <el-dialog
      v-model="importCommandDialogVisible"
      title="导入命令"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="粘贴完整的运行命令，系统将自动解析参数"
        type="info"
        :closable="false"
        style="margin-bottom: 16px;"
      />
      <el-input
        v-model="importCommandText"
        type="textarea"
        :rows="6"
        placeholder="例如：nohup python3 -u src/main.py --tag=210M_qmix --config=qmix --env-config=sc2 with env_args.map_name=MMM2 t_max=2100000 &> output.out &"
      />
      <div style="margin-top: 12px; color: #909399; font-size: 12px;">
        <p>支持解析的参数格式：</p>
        <ul style="margin: 4px 0 0 20px;">
          <li>命令参数：<code>--param=value</code> 或 <code>--param value</code></li>
          <li>配置参数：<code>with key=value key2=value2</code></li>
        </ul>
      </div>
      <template #footer>
        <el-button @click="importCommandDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="parseAndImportCommand">
          解析并导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { experimentApi } from '../api/experiments'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, Edit, Check, Close, Setting, Monitor, Document, 
  Aim, View, DataAnalysis, Finished, VideoPlay, VideoPause, Link, Timer,
  Picture, CopyDocument, CirclePlus, Delete, Download, Upload
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const form = ref({
  experiment_id: '',
  name: '',
  description: '',
  purpose: '',
  status: 'running',
  tags: [],
  command_params_json: '',  // 存储命令参数的 JSON
  config_json: '',
  output_filename: '',  // 输出文件名（不含 .out 后缀）
  tb_log_path: '',
  tb_port: 6006,
  results: '',
  observations: '',
  conclusion: '',
  created_at: new Date().toISOString()
})

const loading = ref(false)
const saving = ref(false)
const tbLoading = ref(false)
const tbRunning = ref(false)
const tbStartTime = ref(null)
const tbRunningTime = ref('00:00:00')
const availableTags = ref([])
const isView = ref(true)
const originalForm = ref(null)
let timerIntervalId = null
const statusCheckInterval = ref(null)
const observations = ref({
  text: '',
  images: [],
  attachments: [],  // CSV 附件列表
  lastUpdated: null
})
const newObservation = ref({
  text: '',
  images: [],
  attachments: []  // 待上传的附件
})
const generatedCommand = ref('')
const configParams = ref([])  // 配置参数数组（with 参数）
const commandParams = ref([])  // 命令参数数组（-- 参数）
const isGeneratingCommand = ref(false)  // 命令生成状态
let generateCommandTimer = null  // 防抖定时器
const presetAlgorithms = ref([])  // 常用算法列表
const presetEnvironments = ref([])  // 常用环境列表
const availableMaps = ref([])  // 当前环境的地图列表

// 导入命令相关
const importCommandDialogVisible = ref(false)
const importCommandText = ref('')

// 笔记模块配置
const notebookModules = ref([
  { id: 'config', name: '实验配置', enabled: true, order: 1 },
  { id: 'tensorboard', name: 'TensorBoard', enabled: true, order: 2 },
  { id: 'description', name: '实验描述', enabled: true, order: 3 },
  { id: 'purpose', name: '实验目的', enabled: true, order: 4 },
  { id: 'observations', name: '观察记录', enabled: true, order: 5 },
  { id: 'results', name: '结果数据', enabled: true, order: 6 },
  { id: 'conclusion', name: '结论与下一步', enabled: true, order: 7 }
])

const isNew = computed(() => route.name === 'NewExperiment' || route.params.id === 'new')

// 根据配置排序的模块列表
const sortedModules = computed(() => {
  // 如果是新建模式，使用新建实验页模块配置
  if (isNew.value) {
    const saved = localStorage.getItem('newExpModules')
    if (saved) {
      try {
        const modules = JSON.parse(saved)
        return modules.sort((a, b) => a.order - b.order)
      } catch (e) {
        console.error('加载新建实验页模块配置失败', e)
      }
    }
    // 默认配置
    return [
      { id: 'config', name: '实验配置', enabled: true, order: 1 },
      { id: 'description', name: '实验描述', enabled: true, order: 2 },
      { id: 'purpose', name: '实验目的', enabled: true, order: 3 }
    ]
  }
  // 查看/编辑模式，使用笔记模块配置
  return [...notebookModules.value].sort((a, b) => a.order - b.order)
})

// 检查模块是否启用
const isModuleEnabled = (moduleId) => {
  // 如果是新建模式，检查新建实验页模块配置
  if (isNew.value) {
    const modules = sortedModules.value
    const module = modules.find(m => m.id === moduleId)
    return module ? module.enabled : true
  }
  // 查看/编辑模式，检查笔记模块配置
  const module = notebookModules.value.find(m => m.id === moduleId)
  return module ? module.enabled : true
}

const getStatusType = (status) => {
  const map = {
    running: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
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

const toggleEdit = () => {
  originalForm.value = JSON.parse(JSON.stringify(form.value))
  // 解析配置参数
  parseConfigJson()
  parseCommandParamsJson()
  // 编辑时，将当前观察记录复制到编辑区
  newObservation.value = {
    text: observations.value.text || '',
    images: [...(observations.value.images || [])],
    attachments: [...(observations.value.attachments || [])]
  }
  isView.value = false
}

const cancelEdit = () => {
  if (originalForm.value) {
    form.value = JSON.parse(JSON.stringify(originalForm.value))
  }
  // 清空编辑区
  newObservation.value = {
    text: '',
    images: [],
    attachments: []
  }
  isView.value = true
}

const loadExperiment = async () => {
  if (isNew.value) {
    // 新建模式，重置表单
    form.value = {
      experiment_id: '',
      name: '',
      description: '',
      purpose: '',
      status: 'running',
      tags: [],
      command_params_json: '',
      config_json: '',
      output_filename: '',
      tb_log_path: '',
      tb_port: 6006,
      results: '',
      observations: '',
      conclusion: ''
    }
    
    // 重置其他状态
    commandParams.value = []
    configParams.value = []
    observations.value = {
      text: '',
      images: [],
      lastUpdated: null
    }
    
    isView.value = false
    
    // 新建模式，初始化默认参数
    parseCommandParamsJson()
    
    // 生成实验 ID 并设置为默认名称
    try {
      const { data } = await experimentApi.generateExperimentId()
      form.value.experiment_id = data.experiment_id
      form.value.name = data.experiment_id  // 实验名称默认为实验 ID
    } catch (error) {
      console.error('生成实验 ID 失败', error)
    }
    return
  }
  
  loading.value = true
  try {
    const { data } = await experimentApi.getExperiment(route.params.id)
    form.value = data
    
    // 解析配置参数
    parseConfigJson()
    parseCommandParamsJson()
    
    // 解析观察记录
    if (data.observations) {
      try {
        const parsed = JSON.parse(data.observations)
        // 兼容旧格式（数组）和新格式（对象）
        if (Array.isArray(parsed)) {
          // 如果是旧格式的数组，取第一条或创建空记录
          observations.value = parsed.length > 0 ? parsed[0] : { text: '', images: [], attachments: [], lastUpdated: null }
        } else {
          // 确保 attachments 存在
          observations.value = {
            ...parsed,
            attachments: parsed.attachments || []
          }
        }
      } catch (e) {
        // 如果是旧格式的纯文本，转换为新格式
        observations.value = {
          text: data.observations,
          images: [],
          attachments: [],
          lastUpdated: data.created_at
        }
      }
    } else {
      // 如果没有观察记录，初始化为空对象
      observations.value = { text: '', images: [], attachments: [], lastUpdated: null }
    }
    
    // 生成运行命令
    if (data.experiment_id) {
      await generateCommand()
    }
    
    isView.value = route.query.mode === 'view'
    checkTBStatus()
  } catch (error) {
    ElMessage.error('加载实验失败')
  } finally {
    loading.value = false
  }
}

const loadTags = async () => {
  // 从 localStorage 加载配置的标签
  const saved = localStorage.getItem('experimentTags')
  if (saved) {
    try {
      availableTags.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载标签配置失败', e)
    }
  }
  
  // 同时从后端加载已使用的标签（用于补充）
  try {
    const { data } = await experimentApi.getTags()
    // 合并配置的标签和已使用的标签，去重
    const allTags = [...new Set([...availableTags.value, ...data])]
    availableTags.value = allTags
  } catch (error) {
    console.error('加载标签失败', error)
  }
}

const save = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入实验名称')
    return
  }
  
  // 保存命令参数
  form.value.command_params_json = JSON.stringify(commandParams.value)
  
  saving.value = true
  try {
    if (isNew.value) {
      // 新建实验
      const response = await experimentApi.createExperiment(form.value)
      ElMessage.success('创建成功')
      // 跳转到实验列表页面
      router.push('/')
    } else {
      // 如果在编辑模式，先上传新附件
      if (!isView.value && newObservation.value.attachments.some(att => att.isNew)) {
        await uploadNewAttachments()
      }
      
      // 更新观察记录
      if (!isView.value) {
        const hasContent = newObservation.value.text || newObservation.value.images.length > 0 || newObservation.value.attachments.length > 0
        observations.value = {
          text: newObservation.value.text,
          images: [...newObservation.value.images],
          attachments: newObservation.value.attachments.map(att => ({
            id: att.id,
            name: att.name,
            size: att.size
          })),
          lastUpdated: hasContent ? new Date().toISOString() : observations.value.lastUpdated
        }
      }
      
      // 将观察记录转换为 JSON 字符串
      form.value.observations = JSON.stringify(observations.value)
      
      await experimentApi.updateExperiment(route.params.id, form.value)
      ElMessage.success('保存成功')
      isView.value = true
      loadExperiment()
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const startTB = async () => {
  tbLoading.value = true
  tbStartTime.value = Date.now()
  console.log('启动计时器，开始时间:', tbStartTime.value)
  startTimer()
  
  try {
    ElMessage.info('正在启动 TensorBoard，请稍候...')
    // 如果有本地缓存路径，传递给 API（会使用本地 TensorBoard）
    const response = await experimentApi.startTensorBoard(form.value.tb_log_path, form.value.tb_port, form.value.tb_local_cache_path)
    tbRunning.value = true
    
    // 启动状态检查
    startStatusCheck()
    
    const elapsedSeconds = Math.floor((Date.now() - tbStartTime.value) / 1000)
    // 格式化时间为 00:00:00
    const formatTime = (seconds) => {
      const h = Math.floor(seconds / 3600).toString().padStart(2, '0')
      const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
      const s = (seconds % 60).toString().padStart(2, '0')
      return `${h}:${m}:${s}`
    }
    ElMessage.success({
      message: `${response.data.message}，耗时 ${formatTime(elapsedSeconds)}`,
      duration: 5000
    })
    
    // 如果浏览器没有自动打开，提供手动链接
    setTimeout(() => {
      ElMessage.info({
        dangerouslyUseHTMLString: true,
        message: `如果浏览器未自动打开，请手动访问：<a href="http://localhost:${form.value.tb_port}" target="_blank" style="color: #409eff; text-decoration: underline;">http://localhost:${form.value.tb_port}</a>`,
        duration: 10000
      })
    }, 3000)
  } catch (error) {
    tbRunning.value = false
    stopTimer()
    const errorMsg = error.response?.data?.error || 'TensorBoard 启动失败'
    ElMessage.error({
      message: errorMsg,
      duration: 5000
    })
  } finally {
    tbLoading.value = false
  }
}

const stopTB = async () => {
  tbLoading.value = true
  try {
    await experimentApi.stopTensorBoard(form.value.tb_port)
    ElMessage.success('TensorBoard 已停止（浏览器标签页需手动关闭）')
    tbRunning.value = false
    stopTimer()
    stopStatusCheck()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || 'TensorBoard 停止失败')
  } finally {
    tbLoading.value = false
  }
}

const startTimer = () => {
  // 先清除旧的计时器，但不重置 tbStartTime
  if (timerIntervalId) {
    clearInterval(timerIntervalId)
    timerIntervalId = null
  }
  
  console.log('startTimer 被调用, tbStartTime.value =', tbStartTime.value)
  
  timerIntervalId = setInterval(() => {
    if (tbStartTime.value) {
      const elapsed = Date.now() - tbStartTime.value
      const hours = Math.floor(elapsed / 3600000)
      const minutes = Math.floor((elapsed % 3600000) / 60000)
      const seconds = Math.floor((elapsed % 60000) / 1000)
      const newTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
      tbRunningTime.value = newTime
    }
  }, 1000)
  console.log('计时器 ID:', timerIntervalId)
}

const stopTimer = () => {
  if (timerIntervalId) {
    clearInterval(timerIntervalId)
    timerIntervalId = null
  }
  tbStartTime.value = null
  tbRunningTime.value = '00:00:00'
}

const startStatusCheck = () => {
  stopStatusCheck()
  // 每 10 秒检查一次 TensorBoard 状态
  statusCheckInterval.value = setInterval(async () => {
    try {
      const { data } = await experimentApi.getTensorBoardStatus(form.value.tb_port)
      if (!data.running && tbRunning.value) {
        // TensorBoard 已停止但界面还显示运行中
        tbRunning.value = false
        stopTimer()
        ElMessage.warning('TensorBoard 已停止运行')
      }
    } catch (error) {
      console.error('检查 TensorBoard 状态失败:', error)
    }
  }, 10000)
}

const stopStatusCheck = () => {
  if (statusCheckInterval.value) {
    clearInterval(statusCheckInterval.value)
    statusCheckInterval.value = null
  }
}

const openTBInBrowser = () => {
  window.open(`http://localhost:${form.value.tb_port}`, '_blank')
  ElMessage.success('已在新标签页中打开 TensorBoard')
}

const formatObservationTime = (timestamp) => {
  if (!timestamp) return '尚未编辑'
  return '最后编辑：' + new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleImageSelect = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    newObservation.value.images.push(e.target.result)
  }
  reader.readAsDataURL(file.raw)
}

const removePreviewImage = (index) => {
  newObservation.value.images.splice(index, 1)
}

// CSV 附件处理
const handleCsvSelect = (file) => {
  // 添加到待上传列表
  newObservation.value.attachments.push({
    file: file.raw,
    name: file.name,
    size: file.size,
    isNew: true  // 标记为新文件，需要上传
  })
}

const removeAttachment = async (index) => {
  const att = newObservation.value.attachments[index]
  
  // 如果是已上传的文件，需要从服务器删除
  if (att.id && !att.isNew) {
    try {
      await experimentApi.deleteAttachment(route.params.id, att.id)
    } catch (error) {
      console.error('删除附件失败', error)
      ElMessage.error('删除附件失败')
      return
    }
  }
  
  newObservation.value.attachments.splice(index, 1)
}

const downloadAttachment = (att) => {
  const url = experimentApi.getAttachmentUrl(route.params.id, att.id)
  window.open(url, '_blank')
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 上传新的附件
const uploadNewAttachments = async () => {
  const newAttachments = newObservation.value.attachments.filter(att => att.isNew)
  
  for (const att of newAttachments) {
    try {
      const { data } = await experimentApi.uploadAttachment(route.params.id, att.file)
      // 更新附件信息
      att.id = data.id
      att.isNew = false
      delete att.file
    } catch (error) {
      console.error('上传附件失败', error)
      ElMessage.error(`上传 ${att.name} 失败`)
    }
  }
}

const checkTBStatus = async () => {
  try {
    const { data } = await experimentApi.getTensorBoardStatus(form.value.tb_port)
    tbRunning.value = data.running
  } catch (error) {
    console.error('检查 TensorBoard 状态失败', error)
  }
}

const goBack = () => {
  router.push('/')
}

const exportToHTML = async () => {
  // 获取附件内容（如果有）
  let attachmentsData = []
  if (observations.value.attachments && observations.value.attachments.length > 0) {
    for (const att of observations.value.attachments) {
      try {
        // 下载附件内容
        const response = await fetch(experimentApi.getAttachmentUrl(route.params.id, att.id))
        const blob = await response.blob()
        const reader = new FileReader()
        
        await new Promise((resolve) => {
          reader.onload = () => {
            attachmentsData.push({
              name: att.name,
              size: att.size,
              content: reader.result // Base64 编码的内容
            })
            resolve()
          }
          reader.readAsDataURL(blob)
        })
      } catch (error) {
        console.error(`读取附件 ${att.name} 失败`, error)
      }
    }
  }
  
  // 生成 HTML 内容
  const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${form.value.name} - 实验报告</title>
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
      max-width: 900px;
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
    .code-block {
      background: #f5f7fa;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      padding: 15px;
      font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
      font-size: 13px;
      overflow-x: auto;
      line-height: 1.6;
    }
    .tag {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 12px;
      margin-right: 8px;
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
    .observation-images {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }
    .observation-images img {
      width: 100%;
      border-radius: 4px;
      border: 1px solid #e4e7ed;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .attachments-section-export {
      margin-top: 16px;
      padding: 12px 16px;
      background: #f9fafb;
      border-radius: 6px;
      border: 1px solid #e5e7eb;
    }
    .attachments-title-export {
      font-size: 14px;
      font-weight: 600;
      color: #374151;
      margin-bottom: 12px;
    }
    .attachments-list-export {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .attachment-item-export {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 12px;
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
    }
    .attachment-info-export {
      flex: 1;
      min-width: 0;
    }
    .attachment-name-export {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: #374151;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .attachment-size-export {
      display: block;
      font-size: 12px;
      color: #9ca3af;
      margin-top: 2px;
    }
    .download-btn {
      padding: 6px 16px;
      background: #10b981;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: background 0.2s;
    }
    .download-btn:hover {
      background: #059669;
    }
    .download-btn span {
      font-size: 16px;
    }
    }
    .observation-images img:hover {
      transform: scale(1.05);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* 图片查看器样式 */
    .image-viewer {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.9);
      z-index: 9999;
      justify-content: center;
      align-items: center;
    }
    .image-viewer.active {
      display: flex;
    }
    .image-viewer img {
      max-width: 90%;
      max-height: 90%;
      object-fit: contain;
      border-radius: 4px;
    }
    .image-viewer-close {
      position: absolute;
      top: 20px;
      right: 30px;
      color: white;
      font-size: 40px;
      font-weight: bold;
      cursor: pointer;
      user-select: none;
    }
    .image-viewer-close:hover {
      color: #ccc;
    }
    .image-viewer-nav {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      color: white;
      font-size: 40px;
      font-weight: bold;
      cursor: pointer;
      user-select: none;
      padding: 20px;
      background: rgba(0, 0, 0, 0.5);
      border-radius: 4px;
    }
    .image-viewer-nav:hover {
      background: rgba(0, 0, 0, 0.7);
    }
    .image-viewer-prev {
      left: 20px;
    }
    .image-viewer-next {
      right: 20px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>${form.value.name}</h1>
    
    <div class="meta-info">
      <div class="meta-item">
        <span class="meta-label">实验 ID：</span>
        <span class="meta-value">${form.value.experiment_id}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">状态：</span>
        <span class="tag tag-${form.value.status}">${getStatusText(form.value.status)}</span>
      </div>
      ${form.value.tags && form.value.tags.length > 0 ? `
      <div class="meta-item">
        <span class="meta-label">标签：</span>
        <span class="meta-value">${form.value.tags.join(', ')}</span>
      </div>
      ` : ''}
      <div class="meta-item">
        <span class="meta-label">创建时间：</span>
        <span class="meta-value">${formatDate(form.value.created_at)}</span>
      </div>
    </div>

    ${form.value.description ? `
    <div class="section">
      <div class="section-title">📝 实验描述</div>
      <div class="section-content">${form.value.description}</div>
    </div>
    ` : ''}

    ${form.value.purpose ? `
    <div class="section">
      <div class="section-title">🎯 实验目的</div>
      <div class="section-content">${form.value.purpose}</div>
    </div>
    ` : ''}

    ${generatedCommand.value ? `
    <div class="section">
      <div class="section-title">⚙️ 运行命令</div>
      <pre class="code-block">${generatedCommand.value}</pre>
    </div>
    ` : ''}

    ${observations.value.text || (observations.value.images && observations.value.images.length > 0) || (observations.value.attachments && observations.value.attachments.length > 0) ? `
    <div class="section">
      <div class="section-title">👁️ 观察记录</div>
      ${observations.value.text ? `<div class="section-content">${observations.value.text}</div>` : ''}
      ${observations.value.images && observations.value.images.length > 0 ? `
      <div class="observation-images">
        ${observations.value.images.map((img, index) => `<img src="${img}" alt="观察图片" onclick="openImageViewer(${index})" />`).join('')}
      </div>
      ` : ''}
      ${observations.value.attachments && observations.value.attachments.length > 0 ? `
      <div class="attachments-section-export">
        <div class="attachments-title-export">📎 附件</div>
        <div class="attachments-list-export">
          ${attachmentsData.map((att, index) => `
          <div class="attachment-item-export">
            <div class="attachment-info-export">
              <span class="attachment-name-export">${att.name}</span>
              <span class="attachment-size-export">${formatFileSize(att.size)}</span>
            </div>
            <button class="download-btn" onclick="downloadAttachment(${index})">
              <span>⬇</span> 下载
            </button>
          </div>
          `).join('')}
        </div>
      </div>
      ` : ''}
    </div>
    ` : ''}

    ${form.value.results ? `
    <div class="section">
      <div class="section-title">📊 结果数据</div>
      <div class="section-content">${form.value.results}</div>
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

  <!-- 图片查看器 -->
  <div class="image-viewer" id="imageViewer" onclick="closeImageViewer(event)">
    <span class="image-viewer-close" onclick="closeImageViewer(event)">&times;</span>
    <span class="image-viewer-nav image-viewer-prev" onclick="prevImage(event)">&#10094;</span>
    <img id="viewerImage" src="" alt="查看图片" onclick="event.stopPropagation()" />
    <span class="image-viewer-nav image-viewer-next" onclick="nextImage(event)">&#10095;</span>
  </div>

  <script>
    const images = ${JSON.stringify(observations.value.images || [])};
    const attachments = ${JSON.stringify(attachmentsData)};
    let currentImageIndex = 0;

    function openImageViewer(index) {
      currentImageIndex = index;
      document.getElementById('viewerImage').src = images[index];
      document.getElementById('imageViewer').classList.add('active');
    }

    function closeImageViewer(event) {
      if (event.target.id === 'imageViewer' || event.target.classList.contains('image-viewer-close')) {
        document.getElementById('imageViewer').classList.remove('active');
      }
    }

    function prevImage(event) {
      event.stopPropagation();
      currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
      document.getElementById('viewerImage').src = images[currentImageIndex];
    }

    function nextImage(event) {
      event.stopPropagation();
      currentImageIndex = (currentImageIndex + 1) % images.length;
      document.getElementById('viewerImage').src = images[currentImageIndex];
    }
    
    // 下载附件函数
    function downloadAttachment(index) {
      const att = attachments[index];
      if (!att || !att.content) {
        alert('附件内容不可用');
        return;
      }
      
      // 创建一个临时链接并触发下载
      const link = document.createElement('a');
      link.href = att.content;
      link.download = att.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    // 键盘导航
    document.addEventListener('keydown', function(e) {
      const viewer = document.getElementById('imageViewer');
      if (viewer.classList.contains('active')) {
        if (e.key === 'Escape') {
          viewer.classList.remove('active');
        } else if (e.key === 'ArrowLeft') {
          prevImage(e);
        } else if (e.key === 'ArrowRight') {
          nextImage(e);
        }
      }
    });
  <\/script>
</body>
</html>
  `

  // 创建 Blob 并下载
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${form.value.experiment_id}_${form.value.name}.html`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('HTML 文件已导出')
}

const loadNotebookConfig = () => {
  const saved = localStorage.getItem('notebookModules')
  if (saved) {
    try {
      notebookModules.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载笔记配置失败', e)
    }
  }
}

const generateCommand = async () => {
  if (!form.value.experiment_id) return
  
  try {
    const { data } = await experimentApi.generateCommand({
      experiment_id: form.value.experiment_id,
      command_params: commandParams.value,
      config_json: form.value.config_json,
      tb_log_path: form.value.tb_log_path
    })
    generatedCommand.value = data.command
  } catch (error) {
    console.error('生成命令失败', error)
  }
}

const copyCommand = async () => {
  try {
    await navigator.clipboard.writeText(generatedCommand.value)
    ElMessage.success('命令已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const copyExperimentId = async () => {
  try {
    await navigator.clipboard.writeText(form.value.experiment_id)
    ElMessage.success('实验 ID 已复制')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 命令参数管理
const addCommandParam = () => {
  commandParams.value.push({
    name: '',
    type: 'fixed',  // fixed, algorithm, environment, map
    value: '',
    enabled: true  // 默认启用
  })
}

const removeCommandParam = (index) => {
  commandParams.value.splice(index, 1)
  updateCommandParamsJson()
}

const onParamTypeChange = (index) => {
  // 类型改变时清空值
  commandParams.value[index].value = ''
  generateCommandRealtime()
}

const onEnvironmentParamChange = (index) => {
  const envName = commandParams.value[index].value
  // 更新可用地图列表
  updateAvailableMaps(envName)
  generateCommandRealtime()
}

const getAvailableMapsForParam = (index) => {
  // 查找是否有环境参数
  const envParam = commandParams.value.find(p => p.type === 'environment')
  if (envParam && envParam.value) {
    const env = presetEnvironments.value.find(e => e.name === envParam.value)
    return env ? env.maps : []
  }
  return availableMaps.value
}

const getParamTypeLabel = (type) => {
  const labels = {
    fixed: '自定义值',
    algorithm: '绑定算法',
    environment: '绑定环境',
    map: '绑定地图'
  }
  return labels[type] || type
}

const updateCommandParamsJson = () => {
  form.value.command_params_json = JSON.stringify(commandParams.value)
  generateCommandRealtime()
}

const parseCommandParamsJson = () => {
  commandParams.value = []
  if (form.value.command_params_json) {
    try {
      const parsed = JSON.parse(form.value.command_params_json)
      // 确保每个参数都有 enabled 属性
      commandParams.value = parsed.map(param => ({
        ...param,
        enabled: param.enabled !== undefined ? param.enabled : true
      }))
    } catch (e) {
      console.error('解析命令参数失败', e)
    }
  }
  
  // 如果是新建模式且没有参数，添加默认参数
  if (isNew.value && commandParams.value.length === 0) {
    commandParams.value = [
      { name: 'config', type: 'algorithm', value: '', enabled: true },
      { name: 'env-config', type: 'fixed', value: 'sc2', enabled: true }
    ]
  }
}

// 导入命令功能
const showImportCommandDialog = () => {
  importCommandText.value = ''
  importCommandDialogVisible.value = true
}

const parseAndImportCommand = () => {
  const cmd = importCommandText.value.trim()
  if (!cmd) {
    ElMessage.warning('请输入命令')
    return
  }
  
  // 解析命令
  const parsedParams = parseCommand(cmd)
  
  if (parsedParams.commandParams.length === 0 && parsedParams.configParams.length === 0) {
    ElMessage.warning('未能解析出任何参数，请检查命令格式')
    return
  }
  
  // 创建已有参数名的 Set（用于快速查找）
  const existingCommandParamNames = new Set(commandParams.value.map(p => p.name))
  const existingConfigParamKeys = new Set(configParams.value.map(p => p.key))
  
  // 先将所有已有参数设置为不启用
  commandParams.value.forEach(p => {
    p.enabled = false
  })
  configParams.value.forEach(p => {
    p.enabled = false
  })
  
  let importedCount = 0
  
  // 导入命令参数（-- 参数）
  parsedParams.commandParams.forEach(newParam => {
    const existingIndex = commandParams.value.findIndex(p => p.name === newParam.name)
    if (existingIndex !== -1) {
      // 已存在，更新值并启用
      commandParams.value[existingIndex].value = newParam.value
      commandParams.value[existingIndex].enabled = true
    } else {
      // 新参数，添加到列表
      commandParams.value.push({
        name: newParam.name,
        type: 'fixed',
        value: newParam.value,
        enabled: true
      })
    }
    importedCount++
  })
  
  // 导入配置参数（with 参数）
  parsedParams.configParams.forEach(newParam => {
    const existingIndex = configParams.value.findIndex(p => p.key === newParam.key)
    if (existingIndex !== -1) {
      // 已存在，更新值并启用
      configParams.value[existingIndex].value = newParam.value
      configParams.value[existingIndex].enabled = true
    } else {
      // 新参数，添加到列表
      configParams.value.push({
        key: newParam.key,
        value: newParam.value,
        description: '',
        enabled: true
      })
    }
    importedCount++
  })
  
  // 更新 JSON
  updateCommandParamsJson()
  updateConfigJson()
  
  // 关闭对话框并提示
  importCommandDialogVisible.value = false
  ElMessage.success(`成功导入 ${importedCount} 个参数`)
}

// 解析命令字符串
const parseCommand = (cmd) => {
  const result = {
    commandParams: [],  // -- 参数
    configParams: []    // with 后的参数
  }
  
  // 移除开头的 nohup 和结尾的 &> ... & 部分
  let cleanCmd = cmd
    .replace(/^nohup\s+/, '')
    .replace(/&>\s*\S+\s*&?\s*$/, '')
    .replace(/>\s*\S+\s*2>&1\s*&?\s*$/, '')
    .replace(/\s*&\s*$/, '')
    .trim()
  
  // 查找 with 的位置，分割命令参数和配置参数
  const withIndex = cleanCmd.indexOf(' with ')
  let commandPart = cleanCmd
  let configPart = ''
  
  if (withIndex !== -1) {
    commandPart = cleanCmd.substring(0, withIndex)
    configPart = cleanCmd.substring(withIndex + 6).trim()  // 6 = ' with '.length
  }
  
  // 解析命令参数（-- 开头的参数）
  // 匹配 --param=value 或 --param value 格式
  const commandParamRegex = /--([a-zA-Z_][a-zA-Z0-9_-]*)(?:=|\s+)([^\s-][^\s]*|"[^"]*"|'[^']*')?/g
  let match
  
  while ((match = commandParamRegex.exec(commandPart)) !== null) {
    const name = match[1]
    let value = match[2] || ''
    // 移除引号
    value = value.replace(/^["']|["']$/g, '')
    result.commandParams.push({ name, value })
  }
  
  // 解析配置参数（with 后面的 key=value 格式）
  if (configPart) {
    // 匹配 key=value 格式，支持点号分隔的键名
    const configParamRegex = /([a-zA-Z_][a-zA-Z0-9_.]*)=([^\s]+|"[^"]*"|'[^']*')/g
    
    while ((match = configParamRegex.exec(configPart)) !== null) {
      const key = match[1]
      let value = match[2]
      // 移除引号
      value = value.replace(/^["']|["']$/g, '')
      result.configParams.push({ key, value })
    }
  }
  
  return result
}

// 配置参数管理（with 参数）
const addConfigParam = () => {
  configParams.value.push({
    key: '',
    value: '',
    description: '',
    enabled: true  // 默认启用
  })
}

const removeConfigParam = (index) => {
  configParams.value.splice(index, 1)
  updateConfigJson()
}

const updateConfigJson = () => {
  // 将参数数组转换为 JSON 字符串（只包含启用的参数）
  const params = {}
  configParams.value.forEach(param => {
    if (param.enabled && param.key && param.value) {
      // 尝试解析数值
      let value = param.value
      if (!isNaN(value) && value !== '') {
        value = Number(value)
      } else if (value === 'true') {
        value = true
      } else if (value === 'false') {
        value = false
      }
      params[param.key] = value
    }
  })
  form.value.config_json = Object.keys(params).length > 0 ? JSON.stringify(params, null, 2) : ''
  
  // 保存参数模板到 localStorage
  saveParamsTemplate()
  
  // 实时生成命令
  generateCommandRealtime()
}

const parseConfigJson = () => {
  // 将 JSON 字符串解析为参数数组
  configParams.value = []
  if (form.value.config_json) {
    try {
      const params = JSON.parse(form.value.config_json)
      Object.keys(params).forEach(key => {
        configParams.value.push({
          key: key,
          value: String(params[key]),
          description: '',
          enabled: true
        })
      })
    } catch (e) {
      console.error('解析配置参数失败', e)
    }
  }
}

const saveParamsTemplate = () => {
  // 保存参数模板到 localStorage（包含所有参数，不管是否启用）
  localStorage.setItem('experimentParamsTemplate', JSON.stringify(configParams.value))
}

const loadParamsTemplate = () => {
  // 加载参数模板
  const saved = localStorage.getItem('experimentParamsTemplate')
  if (saved && isNew.value) {
    try {
      const template = JSON.parse(saved)
      if (template.length > 0) {
        configParams.value = template.map(param => ({
          ...param,
          enabled: param.enabled !== undefined ? param.enabled : true
        }))
        updateConfigJson()
      }
    } catch (e) {
      console.error('加载参数模板失败', e)
    }
  }
}

const generateCommandRealtime = async () => {
  // 清除之前的定时器
  if (generateCommandTimer) {
    clearTimeout(generateCommandTimer)
  }
  
  // 防抖：500ms 后执行
  generateCommandTimer = setTimeout(async () => {
    if (isGeneratingCommand.value) return
    
    isGeneratingCommand.value = true
    try {
      // 如果是新建模式且没有 experiment_id，先获取一个预览 ID
      let expId = form.value.experiment_id
      if (!expId && isNew.value) {
        // 调用后端生成一个临时的实验 ID 用于预览
        try {
          const { data } = await experimentApi.generateExperimentId()
          expId = data.experiment_id
          // 将生成的 ID 保存到表单中，这样用户保存时就会使用这个 ID
          form.value.experiment_id = expId
        } catch (error) {
          console.error('生成实验 ID 失败', error)
          expId = 'exp_YYYYMMDD_NNN'
        }
      }
      
      const config = await experimentApi.getConfig()
      const basePath = config.data.remote?.tensorboard_base_path || '/path/to/tensorboard'
      const tempTbPath = form.value.tb_log_path || `${basePath}/${expId}`
      
      const { data } = await experimentApi.generateCommand({
        experiment_id: expId,
        command_params: commandParams.value,
        config_json: form.value.config_json,
        output_filename: form.value.output_filename,  // 传递输出文件名
        tb_log_path: tempTbPath
      })
      generatedCommand.value = data.command
    } catch (error) {
      console.error('生成命令失败', error)
    } finally {
      isGeneratingCommand.value = false
    }
  }, 500)
}

const loadPresetsConfig = () => {
  const saved = localStorage.getItem('experimentPresets')
  if (saved) {
    try {
      const presets = JSON.parse(saved)
      presetAlgorithms.value = presets.algorithms || []
      // 兼容旧格式和新格式
      if (presets.environments && presets.environments.length > 0) {
        if (typeof presets.environments[0] === 'string') {
          // 旧格式：字符串数组
          presetEnvironments.value = presets.environments.map(name => ({ name, maps: [] }))
        } else {
          // 新格式：对象数组
          presetEnvironments.value = presets.environments
        }
      }
      
      // 如果已经选择了环境，加载对应的地图列表
      if (form.value.environment) {
        updateAvailableMaps(form.value.environment)
      }
    } catch (e) {
      console.error('加载常用配置失败', e)
    }
  }
}



const updateAvailableMaps = (envName) => {
  const env = presetEnvironments.value.find(e => e.name === envName)
  availableMaps.value = env ? env.maps : []
}

onMounted(() => {
  loadExperiment()
  loadTags()
  loadNotebookConfig()
  loadPresetsConfig()
  
  // 新建模式下加载参数模板
  if (isNew.value) {
    loadParamsTemplate()
  }
})

// 监听路由变化，重新加载数据
watch(() => route.params.id, () => {
  loadExperiment()
  if (isNew.value) {
    loadParamsTemplate()
  }
})

onUnmounted(() => {
  stopTimer()
  stopStatusCheck()
})
</script>

<style scoped>
.experiment-view {
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
  box-shadow: none !important;
  border: none !important;
  border-bottom: 2px solid #dcdfe6 !important;
  border-radius: 0;
  padding: 8px 0;
  font-size: 28px;
  font-weight: 600;
  background-color: transparent !important;
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

.tags-display {
  display: flex;
  align-items: center;
}

.empty-text {
  font-size: 14px;
  color: #c0c4cc;
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

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item.full-width {
  grid-column: 1 / -1;
}

.config-item label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.config-value {
  font-size: 15px;
  color: #303133;
  padding: 8px 0;
  min-height: 32px;
  line-height: 1.6;
}

.path-value {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  color: #606266;
  word-break: break-all;
}

.config-code {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.code-input :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
}

.note-textarea :deep(.el-textarea__inner) {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
}

.note-textarea :deep(.el-textarea__inner):focus {
  border-color: #409eff;
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

.note-content:empty::before {
  content: '暂无内容';
  color: #c0c4cc;
}

/* 观察记录样式 */
.observation-view {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
}

.observation-time {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.observation-content {
  line-height: 1.8;
}

.observation-text {
  font-size: 15px;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 12px;
}

.observation-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.observation-image {
  width: 100%;
  height: 150px;
  border-radius: 4px;
  cursor: pointer;
}

.observation-image :deep(.el-image__inner) {
  transition: opacity 0.2s;
}

.observation-image:hover :deep(.el-image__inner) {
  opacity: 0.85;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
  font-size: 14px;
}

.image-error .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.empty-observations {
  text-align: center;
  color: #c0c4cc;
  padding: 40px;
  font-size: 14px;
}

.observation-edit {
  background: #fff;
}

.observation-input {
  margin-bottom: 12px;
}

.observation-input :deep(.el-textarea__inner) {
  font-size: 15px;
  line-height: 1.8;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.observation-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.image-count {
  font-size: 13px;
  color: #606266;
}

.preview-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.preview-image-item {
  position: relative;
  width: 100%;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
}

.preview-image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-image-item .remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  color: white;
}

.preview-image-item .remove-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}

/* 附件样式 */
.attachments-section {
  margin-top: 16px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.attachments-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  transition: all 0.2s;
}

.attachment-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.attachment-item-view {
  background: #f8fafc;
}

.attachment-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #ecfdf5;
  border-radius: 6px;
  color: #10b981;
  font-size: 18px;
}

.attachment-info {
  flex: 1;
  min-width: 0;
}

.attachment-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-size {
  display: block;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.attachment-actions {
  display: flex;
  gap: 4px;
}

/* 实验 ID 样式 */
.experiment-id-section {
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.experiment-id-label {
  font-size: 13px;
  font-weight: 500;
  color: #1e40af;
  margin-right: 12px;
}

.experiment-id-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.experiment-id-value code {
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 14px;
  font-weight: 600;
}

/* 命令区域样式 */
.command-section {
  margin-top: 24px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.command-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.command-actions {
  display: flex;
  gap: 8px;
}

.command-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.command-block {
  background: #f5f7fa;
  color: #4b5563;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0 0 12px 0;
  overflow-x: auto;
}

.command-placeholder {
  color: #9ca3af;
  font-style: italic;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.command-tip {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
}

/* 命令参数配置样式 */
.command-params-section {
  margin-bottom: 24px;
}

.section-subtitle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.command-params-table {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.command-params-header {
  display: grid;
  grid-template-columns: 60px 2fr 2fr 3fr 80px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.command-params-header > div {
  padding: 10px 12px;
}

.command-params-row {
  display: grid;
  grid-template-columns: 60px 2fr 2fr 3fr 80px;
  border-bottom: 1px solid #f3f4f6;
  align-items: center;
}

.command-params-row:last-child {
  border-bottom: none;
}

.command-params-row > div {
  padding: 8px 12px;
}

.param-col-checkbox {
  display: flex;
  justify-content: center;
  align-items: center;
}

.param-col-key,
.param-col-value,
.param-col-desc {
  display: flex;
  align-items: center;
}

.param-col-actions {
  display: flex;
  justify-content: center;
  align-items: center;
}

.command-params-empty {
  padding: 40px;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
  background: #f9fafb;
}

.command-params-view {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.command-params-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.command-param-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
}

.param-name {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  font-weight: 600;
  color: #667eea;
  min-width: 120px;
}

.param-value {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  color: #374151;
  flex: 1;
}

/* 配置参数表格样式 */
.params-table {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.params-table-header {
  display: grid;
  grid-template-columns: 60px 2fr 2fr 3fr 80px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.params-table-header > div {
  padding: 10px 12px;
}

.params-table-row {
  display: grid;
  grid-template-columns: 60px 2fr 2fr 3fr 80px;
  border-bottom: 1px solid #f3f4f6;
  align-items: center;
}

.params-table-row:last-child {
  border-bottom: none;
}

.params-table-row > div {
  padding: 8px 12px;
}

.param-col-checkbox {
  display: flex;
  justify-content: center;
  align-items: center;
}

.param-col-key,
.param-col-value,
.param-col-desc {
  display: flex;
  align-items: center;
}

.param-col-actions {
  display: flex;
  justify-content: center;
  align-items: center;
}

.params-table-empty {
  padding: 40px;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
  background: #f9fafb;
}

/* 查看模式参数表格 */
.params-view-table {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.params-view-row {
  display: grid;
  grid-template-columns: 2fr 3fr 4fr;
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  align-items: center;
  gap: 12px;
}

.params-view-row:last-child {
  border-bottom: none;
}

.param-view-key {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
}

.param-view-value {
  font-size: 14px;
  color: #1f2937;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.param-view-desc {
  font-size: 13px;
  color: #6b7280;
  font-style: italic;
  display: flex;
  justify-content: flex-end;
}

.param-view-desc .el-tag {
  height: 28px;
  line-height: 28px;
  padding: 0 12px;
}

</style>
