<template>
  <el-container style="height: 100vh">
    <el-header style="background: #409EFF; color: white; display: flex; align-items: center; padding: 0 20px;">
      <h2 style="margin: 0;">🧪 ExpTracker</h2>
      <span style="margin-left: 10px; font-size: 14px; opacity: 0.9;">实验日志管理系统</span>
    </el-header>
    <el-container>
      <el-aside width="200px" style="background: #f5f7fa; border-right: 1px solid #e4e7ed;">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/groups">
            <el-icon><Folder /></el-icon>
            <span>实验组列表</span>
          </el-menu-item>
          <el-menu-item index="/">
            <el-icon><List /></el-icon>
            <span>实验结果列表</span>
          </el-menu-item>
          <el-menu-item index="/calendar">
            <el-icon><Calendar /></el-icon>
            <span>日历视图</span>
          </el-menu-item>
          <el-menu-item index="/import">
            <el-icon><Download /></el-icon>
            <span>批量导入</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main style="padding: 20px;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Calendar, List, CirclePlus, Setting, Download, Folder } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
