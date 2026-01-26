<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="20">
        <h2 style="margin: 0;">实验组列表</h2>
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

    <el-table 
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { experimentApi } from '../api/experiments'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CirclePlus } from '@element-plus/icons-vue'

const router = useRouter()

const groups = ref([])
const loading = ref(false)
const selectedGroups = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const sortOrder = ref('desc') // 默认降序（最新的在前）

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

onMounted(() => {
  loadGroups()
})
</script>
