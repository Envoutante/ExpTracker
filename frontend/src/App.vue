<template>
  <el-container style="height: 100vh" :class="themeClass">
    <el-header class="app-header">
      <div class="header-left">
        <h2 style="margin: 0;">🧪 ExpTracker</h2>
        <span style="margin-left: 10px; font-size: 14px; opacity: 0.9;">实验日志管理系统</span>
      </div>
      <div class="header-right">
        <el-switch
          v-model="isDark"
          class="theme-toggle-switch"
          inline-prompt
          :active-icon="MoonSvgIcon"
          :inactive-icon="SunSvgIcon"
          @change="toggleTheme"
          size="large"
        />
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="app-aside">
        <el-menu :default-active="activeMenu" router class="app-menu">
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
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, h, markRaw } from 'vue'
import { useRoute } from 'vue-router'
import { Calendar, List, Setting, Download, Folder } from '@element-plus/icons-vue'

import sunUrl from './static/sun.svg?url'
import moonUrl from './static/moon.svg?url'

const SunSvgIcon = markRaw({
  name: 'SunSvgIcon',
  render() {
    return h('img', { src: sunUrl, alt: 'sun', class: 'theme-toggle-icon' })
  },
})

const MoonSvgIcon = markRaw({
  name: 'MoonSvgIcon',
  render() {
    return h('img', { src: moonUrl, alt: 'moon', class: 'theme-toggle-icon' })
  },
})

const route = useRoute()
const activeMenu = computed(() => route.path)

// 主题管理
const isDark = ref(false)
const themeClass = computed(() => isDark.value ? 'dark-theme' : 'light-theme')

const toggleTheme = (value) => {
  isDark.value = value
  localStorage.setItem('theme', value ? 'dark' : 'light')
  // 为 document.documentElement 添加主题类，以便全局使用
  if (value) {
    document.documentElement.classList.add('dark-theme')
    document.documentElement.classList.remove('light-theme')
  } else {
    document.documentElement.classList.add('light-theme')
    document.documentElement.classList.remove('dark-theme')
  }
}

onMounted(() => {
  // 恢复主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark-theme')
  } else {
    document.documentElement.classList.add('light-theme')
  }
})
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

/* CSS 变量 - 日间模式 */
:root,
.light-theme {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f7fa;
  --bg-tertiary: #ecf5ff;
  --text-primary: #303133;
  --text-secondary: #606266;
  --text-tertiary: #909399;
  --border-color: #e4e7ed;
  --border-color-light: #ebeef5;
  --header-bg: #409EFF;
  --header-text: #ffffff;
  --aside-bg: #f5f7fa;
  --main-bg: #ffffff;
  --card-bg: #ffffff;
  --hover-bg: #ecf5ff;

  /* 语义色（与 Element Plus 默认日间色一致） */
  --accent-primary: #409eff;
  --accent-primary-hover: #66b1ff;
  --accent-primary-active: #337ecc;
  --accent-success: #67c23a;
  --accent-success-hover: #85ce61;
  --accent-success-active: #529b2e;
  --accent-warning: #e6a23c;
  --accent-warning-hover: #ebb563;
  --accent-warning-active: #b88230;
  --accent-danger: #f56c6c;
  --accent-danger-hover: #f78989;
  --accent-danger-active: #c45656;
  --accent-info: #909399;
  --accent-info-hover: #a6a9ad;
  --accent-info-active: #73767a;

  /* Element Plus token 对齐（让其它组件也能用同一套语义色） */
  --el-color-primary: var(--accent-primary);
  --el-color-success: var(--accent-success);
  --el-color-warning: var(--accent-warning);
  --el-color-danger: var(--accent-danger);
  --el-color-info: var(--accent-info);
}

/* CSS 变量 - 夜间模式 */
.dark-theme {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-tertiary: #363636;
  --text-primary: #e8e8e8;
  --text-secondary: #b8b8b8;
  --text-tertiary: #888888;
  --border-color: #4a4a4a;
  --border-color-light: #3a3a3a;
  --header-bg: #2c5282;
  --header-text: #ffffff;
  --aside-bg: #2d2d2d;
  --main-bg: #1a1a1a;
  --card-bg: #2d2d2d;
  --hover-bg: #363636;

  /* 语义色：保持与日间一致的“语义”（蓝/绿/橙/红/灰），但调整亮度/饱和度以适配暗黑背景 */
  --accent-primary: #3a8ee6;
  --accent-primary-hover: #5aa6ff;
  --accent-primary-active: #2f73b8;
  --accent-success: #5daf34;
  --accent-success-hover: #79c35a;
  --accent-success-active: #4a8f2b;
  --accent-warning: #cf9236;
  --accent-warning-hover: #e0aa4f;
  --accent-warning-active: #a8742c;
  --accent-danger: #dd6161;
  --accent-danger-hover: #f07b7b;
  --accent-danger-active: #b44d4d;
  --accent-info: #7f8287;
  --accent-info-hover: #9a9da3;
  --accent-info-active: #666a70;

  --el-color-primary: var(--accent-primary);
  --el-color-success: var(--accent-success);
  --el-color-warning: var(--accent-warning);
  --el-color-danger: var(--accent-danger);
  --el-color-info: var(--accent-info);
}

/* 应用主题变量 */
.light-theme,
.dark-theme {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s, color 0.3s;
}

.app-header {
  background: var(--header-bg) !important;
  color: var(--header-text) !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px !important;
  transition: background-color 0.3s;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 顶部日夜切换：日间（未选中）状态下轨道更浅、太阳图标更深 */
.theme-toggle-switch:not(.is-checked) {
  --el-switch-off-color: rgba(255, 255, 255, 0.55);
  --el-switch-border-color: rgba(255, 255, 255, 0.75);
}

.theme-toggle-switch:not(.is-checked) .el-switch__core .el-switch__inner-wrapper {
  color: #303133;
}

.theme-toggle-switch:not(.is-checked) .theme-toggle-icon {
  filter: brightness(0.88) saturate(1.08) contrast(1.1);
}

.theme-toggle-switch .el-switch__core .el-switch__inner,
.theme-toggle-switch .el-switch__core .el-switch__inner-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
}

.theme-toggle-switch .theme-toggle-icon {
  width: 14px;
  height: 14px;
  padding: 1px;
  display: block;
  object-fit: contain;
}

.app-aside {
  background: var(--aside-bg) !important;
  border-right: 1px solid var(--border-color) !important;
  transition: background-color 0.3s, border-color 0.3s;
}

.app-menu {
  background: var(--aside-bg) !important;
  border-right: none !important;
}

.dark-theme .app-menu .el-menu-item {
  color: var(--text-primary);
}

.dark-theme .app-menu .el-menu-item:hover {
  background-color: var(--hover-bg);
}

.dark-theme .app-menu .el-menu-item.is-active {
  background-color: transparent;
  color: #409EFF;
}

.app-main {
  background: var(--main-bg) !important;
  padding: 20px !important;
  transition: background-color 0.3s;
}

/* 为 Element Plus 组件应用暗色主题 */
.dark-theme .el-table {
  --el-table-bg-color: var(--card-bg);
  --el-table-tr-bg-color: var(--card-bg);
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-row-hover-bg-color: var(--hover-bg);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-primary);
  --el-table-border-color: var(--border-color);
}

.dark-theme .el-card {
  --el-card-bg-color: var(--card-bg);
  --el-card-border-color: var(--border-color);
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.dark-theme .el-input {
  --el-input-bg-color: var(--bg-secondary);
  --el-input-border-color: var(--border-color);
  --el-input-text-color: var(--text-primary);
  --el-input-placeholder-color: var(--text-tertiary);
}

.dark-theme .el-textarea {
  --el-input-bg-color: var(--bg-secondary);
  --el-input-border-color: var(--border-color);
  --el-input-text-color: var(--text-primary);
}

.dark-theme .el-select {
  --el-select-input-focus-border-color: var(--accent-primary);
}

/* 按钮字号统一：日间/夜间一致，并按 size 规格化 */
.el-button {
  font-size: 14px;
}

.el-button--small {
  font-size: 12px;
}

.el-button--default {
  font-size: 14px;
}

.el-button--large {
  font-size: 16px;
}

/* 仅对“默认按钮”（无 type / 非 text/link）应用深灰配色，避免把所有按钮都染灰 */
.dark-theme .el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--warning):not(.el-button--danger):not(.el-button--info):not(.is-text):not(.is-link) {
  --el-button-bg-color: var(--bg-secondary);
  --el-button-border-color: var(--border-color);
  --el-button-text-color: var(--text-primary);
  --el-button-hover-bg-color: var(--bg-tertiary);
  --el-button-hover-border-color: var(--border-color);
  --el-button-hover-text-color: var(--text-primary);
  --el-button-active-bg-color: var(--bg-tertiary);
  --el-button-active-text-color: var(--text-primary);
  --el-button-disabled-text-color: var(--text-tertiary);
}

/* 彩色 type 按钮（filled） */
.dark-theme .el-button--primary:not(.is-text):not(.is-link) {
  --el-button-bg-color: var(--accent-primary);
  --el-button-border-color: var(--accent-primary);
  --el-button-text-color: #ffffff;
  --el-button-hover-bg-color: var(--accent-primary-hover);
  --el-button-hover-border-color: var(--accent-primary-hover);
  --el-button-hover-text-color: #ffffff;
  --el-button-active-bg-color: var(--accent-primary-active);
  --el-button-active-border-color: var(--accent-primary-active);
}

.dark-theme .el-button--success:not(.is-text):not(.is-link) {
  --el-button-bg-color: var(--accent-success);
  --el-button-border-color: var(--accent-success);
  --el-button-text-color: #ffffff;
  --el-button-hover-bg-color: var(--accent-success-hover);
  --el-button-hover-border-color: var(--accent-success-hover);
  --el-button-hover-text-color: #ffffff;
  --el-button-active-bg-color: var(--accent-success-active);
  --el-button-active-border-color: var(--accent-success-active);
}

.dark-theme .el-button--warning:not(.is-text):not(.is-link) {
  --el-button-bg-color: var(--accent-warning);
  --el-button-border-color: var(--accent-warning);
  --el-button-text-color: #ffffff;
  --el-button-hover-bg-color: var(--accent-warning-hover);
  --el-button-hover-border-color: var(--accent-warning-hover);
  --el-button-hover-text-color: #ffffff;
  --el-button-active-bg-color: var(--accent-warning-active);
  --el-button-active-border-color: var(--accent-warning-active);
}

.dark-theme .el-button--danger:not(.is-text):not(.is-link) {
  --el-button-bg-color: var(--accent-danger);
  --el-button-border-color: var(--accent-danger);
  --el-button-text-color: #ffffff;
  --el-button-hover-bg-color: var(--accent-danger-hover);
  --el-button-hover-border-color: var(--accent-danger-hover);
  --el-button-hover-text-color: #ffffff;
  --el-button-active-bg-color: var(--accent-danger-active);
  --el-button-active-border-color: var(--accent-danger-active);
}

.dark-theme .el-button--info:not(.is-text):not(.is-link) {
  --el-button-bg-color: var(--accent-info);
  --el-button-border-color: var(--accent-info);
  --el-button-text-color: #ffffff;
  --el-button-hover-bg-color: var(--accent-info-hover);
  --el-button-hover-border-color: var(--accent-info-hover);
  --el-button-hover-text-color: #ffffff;
  --el-button-active-bg-color: var(--accent-info-active);
  --el-button-active-border-color: var(--accent-info-active);
}

/* 统一按钮文字/图标观感：图标大小一致，并继承按钮文字色 */
.el-button .el-icon {
  color: currentColor;
}

.el-button--small .el-icon {
  font-size: 12px;
}

.el-button--default .el-icon {
  font-size: 14px;
}

.el-button--large .el-icon {
  font-size: 16px;
}

/* text/link 按钮：默认是浅灰文字；但如果带 type，则使用对应的彩色文字 */
.dark-theme .el-button.is-text:not(.el-button--primary):not(.el-button--success):not(.el-button--warning):not(.el-button--danger):not(.el-button--info),
.dark-theme .el-button.is-link:not(.el-button--primary):not(.el-button--success):not(.el-button--warning):not(.el-button--danger):not(.el-button--info) {
  color: var(--text-secondary) !important;
}

.dark-theme .el-button.is-text:hover,
.dark-theme .el-button.is-link:hover {
  background-color: var(--hover-bg) !important;
}

.dark-theme .el-button.is-text:active,
.dark-theme .el-button.is-link:active {
  background-color: var(--bg-tertiary) !important;
}

.dark-theme .el-button--primary.is-text,
.dark-theme .el-button--primary.is-link {
  color: var(--accent-primary) !important;
}

.dark-theme .el-button--success.is-text,
.dark-theme .el-button--success.is-link {
  color: var(--accent-success) !important;
}

.dark-theme .el-button--warning.is-text,
.dark-theme .el-button--warning.is-link {
  color: var(--accent-warning) !important;
}

.dark-theme .el-button--danger.is-text,
.dark-theme .el-button--danger.is-link {
  color: var(--accent-danger) !important;
}

.dark-theme .el-button--info.is-text,
.dark-theme .el-button--info.is-link {
  color: var(--accent-info) !important;
}

.dark-theme .el-dialog {
  --el-dialog-bg-color: var(--card-bg);
  background-color: var(--card-bg);
}

.dark-theme .el-pagination {
  --el-pagination-button-bg-color: var(--bg-secondary);
  --el-pagination-bg-color: var(--card-bg);
  --el-pagination-button-disabled-bg-color: var(--bg-secondary);
}

.dark-theme .el-tag {
  --el-tag-bg-color: var(--bg-tertiary);
  --el-tag-border-color: var(--border-color);
  --el-tag-text-color: var(--text-primary);
}

.dark-theme .el-alert {
  background-color: var(--bg-tertiary);
  border-color: var(--border-color);
}

.dark-theme .el-empty {
  --el-empty-fill-color-0: var(--bg-secondary);
  --el-empty-fill-color-1: var(--bg-tertiary);
}

/* 表格隔行样式 */
.dark-theme .el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background: var(--bg-tertiary) !important;
}

.dark-theme .el-table__row {
  background-color: var(--card-bg) !important;
}

.dark-theme .el-table__body tr:hover > td.el-table__cell {
  background-color: var(--hover-bg) !important;
}

/* 输入框深度样式覆盖 */
.dark-theme .el-input__wrapper {
  background-color: var(--bg-secondary) !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
}

.dark-theme .el-input__wrapper:hover {
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
}

.dark-theme .el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px #409EFF inset !important;
}

.dark-theme .el-input__inner {
  color: var(--text-primary) !important;
  background-color: transparent !important;
}

.dark-theme .el-input__inner::placeholder {
  color: var(--text-tertiary) !important;
}

/* ImportExperiments 扫描结果：无边框输入框（仅底部横线）
   说明：暗黑模式下全局 .el-input__wrapper 使用 box-shadow 画边框，这里需要覆盖掉 */
.dark-theme .borderless-input .el-input__wrapper {
  background-color: transparent !important;
  box-shadow: none !important;
  border: none !important;
  border-bottom: 1px solid var(--border-color) !important;
  border-radius: 0 !important;
}

.dark-theme .borderless-input .el-input__wrapper:hover {
  border-bottom-color: #606060 !important;
}

.dark-theme .borderless-input .el-input__wrapper.is-focus {
  border-bottom-color: #409EFF !important;
  border-bottom-width: 2px !important;
}

.dark-theme .borderless-input .el-input__inner {
  color: var(--text-primary) !important;
  background-color: transparent !important;
}

.dark-theme .el-textarea__inner {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: none !important;
}

.dark-theme .el-textarea__inner:hover {
  border-color: var(--border-color) !important;
  box-shadow: none !important;
}

.dark-theme .el-textarea__inner:focus {
  border-color: #409EFF !important;
  box-shadow: none !important;
}

/* Select 组件 */
.dark-theme .el-select .el-input__wrapper {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .el-select-dropdown {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-select-dropdown__item {
  color: var(--text-primary) !important;
}

.dark-theme .el-select-dropdown__item:hover {
  background-color: var(--hover-bg) !important;
}

.dark-theme .el-select-dropdown__item.selected {
  background-color: var(--bg-tertiary) !important;
}

/* Settings 页面特定样式 */
.dark-theme .settings-container {
  background-color: var(--main-bg) !important;
  color: var(--text-primary) !important;
}

.dark-theme .settings-content {
  background-color: var(--main-bg) !important;
  color: var(--text-primary) !important;
}

.dark-theme .settings-sidebar {
  background-color: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  border: none !important;
}

.dark-theme .settings-sidebar .el-menu {
  background-color: transparent !important;
  border: none !important;
  border-right: 1px solid var(--border-color) !important;
  overflow: hidden;
}

.dark-theme .settings-sidebar .el-menu-item {
  color: var(--text-primary) !important;
}

.dark-theme .settings-sidebar .el-menu-item:hover {
  background-color: var(--hover-bg) !important;
}

.dark-theme .settings-sidebar .el-menu-item.is-active {
  background-color: transparent !important;
  color: #409EFF !important;
}

.dark-theme .param-section {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .param-section-title {
  color: var(--text-primary) !important;
}

.dark-theme .tutorial-step {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .code-block {
  background-color: #1e1e1e !important;
  border-color: var(--border-color) !important;
}

/* Form 相关 */
.dark-theme .el-form-item__label {
  color: var(--text-primary) !important;
}

.dark-theme .el-form-item__content {
  color: var(--text-primary) !important;
}

/* Card header */
.dark-theme .el-card__header {
  background-color: var(--bg-secondary) !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .card-title {
  color: var(--text-primary) !important;
}

/* Checkbox */
.dark-theme .el-checkbox__label {
  color: var(--text-primary) !important;
}

/* Radio */
.dark-theme .el-radio__label {
  color: var(--text-primary) !important;
}

/* Switch label */
.dark-theme .el-switch__label {
  color: var(--text-secondary) !important;
}

/* Descriptions */
.dark-theme .el-descriptions {
  --el-descriptions-item-bordered-label-background: var(--bg-secondary);
}

.dark-theme .el-descriptions__label {
  background-color: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}

.dark-theme .el-descriptions__content {
  background-color: var(--card-bg) !important;
  color: var(--text-primary) !important;
}

/* Divider */
.dark-theme .el-divider {
  border-color: var(--border-color) !important;
}

.dark-theme .el-divider__text {
  background-color: var(--card-bg) !important;
  color: var(--text-secondary) !important;
}

/* Input Group（el-input append/prepend 区域，如“测试连接”里的复制按钮） */
.dark-theme .el-input-group__append,
.dark-theme .el-input-group__prepend {
  background-color: var(--bg-tertiary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .el-input-group__append .el-button,
.dark-theme .el-input-group__prepend .el-button {
  background-color: var(--bg-tertiary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .el-input-group__append .el-button:hover,
.dark-theme .el-input-group__prepend .el-button:hover {
  background-color: var(--hover-bg) !important;
  border-color: var(--border-color) !important;
  color: #409EFF !important;
}

/* Message Box / Dialog */
.dark-theme .el-message-box {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-message-box__title {
  color: var(--text-primary) !important;
}

.dark-theme .el-message-box__content {
  color: var(--text-secondary) !important;
}

/* Popover */
.dark-theme .el-popover {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-popover__title {
  color: var(--text-primary) !important;
}

/* Tooltip */
.dark-theme .el-tooltip__popper {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-primary) !important;
}

/* Tabs */
.dark-theme .el-tabs__item {
  color: var(--text-secondary) !important;
}

.dark-theme .el-tabs__item.is-active {
  color: #409EFF !important;
}

.dark-theme .el-tabs__nav-wrap::after {
  background-color: var(--border-color) !important;
}

/* Collapse */
.dark-theme .el-collapse {
  border-color: var(--border-color) !important;
}

.dark-theme .el-collapse-item__header {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-collapse-item__wrap {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-collapse-item__content {
  color: var(--text-secondary) !important;
}

/* Menu in settings */
.dark-theme .module-list,
.dark-theme .module-item {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
}

/* 通用文本和背景 */
.dark-theme h1,
.dark-theme h2,
.dark-theme h3,
.dark-theme h4,
.dark-theme h5,
.dark-theme h6 {
  color: var(--text-primary) !important;
}

.dark-theme p,
.dark-theme span,
.dark-theme div {
  color: inherit;
}

/* 为卡片视图应用暗色主题 */
.dark-theme .group-card,
.dark-theme .experiment-card {
  background: var(--card-bg) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .group-card:hover,
.dark-theme .experiment-card:hover {
  border-color: #409EFF !important;
}

.dark-theme .card-preview {
  background: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}

.dark-theme .card-preview:hover {
  background: var(--bg-tertiary) !important;
}

.dark-theme .card-empty-hint {
  color: var(--text-tertiary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .meta-item {
  color: var(--text-secondary) !important;
}

.dark-theme .info-content {
  color: var(--text-secondary) !important;
}

.dark-theme .preview-content {
  color: var(--text-secondary) !important;
}

.dark-theme .info-label {
  color: var(--text-secondary) !important;
}

/* 实验组卡片内部横线和边框 */
.dark-theme .card-header {
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .card-meta {
  border-top-color: var(--border-color) !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .card-footer {
  border-top-color: var(--border-color) !important;
}

/* 观察结果预览区域边框 */
.dark-theme .card-preview {
  background: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border-color) !important;
}

.dark-theme .card-preview:hover {
  background: var(--bg-tertiary) !important;
}

/* Note content areas */
.dark-theme .note-content {
  background-color: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}

/* Segmented control */
.dark-theme .el-segmented {
  background-color: var(--bg-secondary) !important;
  border: 1px solid var(--border-color) !important;
  --el-segmented-bg-color: var(--bg-secondary);
  --el-segmented-item-color: var(--text-secondary);
  --el-segmented-item-hover-bg-color: var(--bg-tertiary);
  --el-segmented-item-selected-bg-color: var(--bg-tertiary);
  --el-segmented-item-selected-color: var(--text-primary);
}

.dark-theme .el-segmented__item {
  color: var(--text-secondary) !important;
}

.dark-theme .el-segmented__item:hover {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-primary) !important;
}

.dark-theme .el-segmented__item.is-selected {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-primary) !important;
}

/* 实验组列表：列表/卡片切换按钮在暗黑模式下使用主色高亮 */
.dark-theme .group-viewmode-segmented.el-segmented {
  border-color: var(--border-color) !important;
  background-color: var(--bg-secondary) !important;
  --el-segmented-bg-color: var(--bg-secondary);
  --el-segmented-item-color: var(--text-secondary);
  --el-segmented-item-hover-bg-color: var(--bg-tertiary);
  --el-segmented-item-hover-color: var(--text-primary);
  --el-segmented-item-selected-bg-color: var(--accent-primary);
  --el-segmented-item-selected-color: #ffffff;
}

.dark-theme .group-viewmode-segmented .el-segmented__item.is-selected {
  color: #ffffff !important;
}

.dark-theme .group-viewmode-segmented .el-segmented__item.is-selected .el-icon {
  color: currentColor !important;
}

.dark-theme .group-viewmode-segmented .el-segmented__item:hover {
  background-color: var(--bg-tertiary) !important;
}

/* ========== 分页组件 ========== */
.dark-theme .el-pagination {
  --el-pagination-button-bg-color: var(--bg-secondary);
  --el-pagination-bg-color: var(--card-bg);
  --el-pagination-button-disabled-bg-color: var(--bg-tertiary);
  --el-pagination-text-color: var(--text-primary);
  --el-pagination-button-color: var(--text-primary);
  color: var(--text-primary) !important;
}

.dark-theme .el-pagination button,
.dark-theme .el-pagination .btn-prev,
.dark-theme .el-pagination .btn-next {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
}

.dark-theme .el-pagination button:disabled,
.dark-theme .el-pagination .btn-prev:disabled,
.dark-theme .el-pagination .btn-next:disabled {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-tertiary) !important;
}

.dark-theme .el-pager li {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
}

.dark-theme .el-pager li:hover {
  color: #409EFF !important;
}

.dark-theme .el-pager li.is-active {
  background-color: #409EFF !important;
  color: #ffffff !important;
}

.dark-theme .el-pagination__total {
  color: var(--text-primary) !important;
}

.dark-theme .el-pagination__jump {
  color: var(--text-primary) !important;
}

.dark-theme .el-pagination__sizes .el-input__wrapper {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .el-pagination__editor .el-input__wrapper {
  background-color: var(--bg-secondary) !important;
}

/* ========== 下拉框组件（状态筛选等） ========== */
.dark-theme .el-select__wrapper {
  background-color: var(--bg-secondary) !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
}

.dark-theme .el-select__wrapper:hover {
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
}

.dark-theme .el-select__wrapper.is-focused {
  box-shadow: 0 0 0 1px #409EFF inset !important;
}

.dark-theme .el-select__placeholder {
  color: var(--text-tertiary) !important;
}

.dark-theme .el-select__selected-item {
  color: var(--text-primary) !important;
}

.dark-theme .el-select-dropdown {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-select-dropdown__item {
  color: var(--text-primary) !important;
}

.dark-theme .el-select-dropdown__item:hover {
  background-color: var(--hover-bg) !important;
}

.dark-theme .el-select-dropdown__item.is-selected {
  color: #409EFF !important;
  background-color: var(--bg-tertiary) !important;
}

.dark-theme .el-select-dropdown__item.hover,
.dark-theme .el-select-dropdown__item.is-hovering {
  background-color: var(--hover-bg) !important;
}

/* ========== 日历组件 ========== */
.dark-theme .el-calendar {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-calendar__header {
  background-color: var(--bg-secondary) !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .el-calendar__title {
  color: var(--text-primary) !important;
}

.dark-theme .el-calendar__body {
  background-color: var(--card-bg) !important;
}

.dark-theme .el-calendar-table {
  background-color: var(--card-bg) !important;
}

.dark-theme .el-calendar-table thead th {
  color: var(--text-secondary) !important;
  background-color: var(--bg-secondary) !important;
}

.dark-theme .el-calendar-table td {
  border-color: var(--border-color) !important;
}

.dark-theme .el-calendar-table .el-calendar-day {
  background-color: var(--card-bg) !important;
  color: var(--text-primary) !important;
}

.dark-theme .el-calendar-table .el-calendar-day:hover {
  background-color: var(--hover-bg) !important;
}

.dark-theme .el-calendar-table td.is-selected .el-calendar-day {
  background-color: var(--bg-tertiary) !important;
}

.dark-theme .el-calendar-table td.is-today .el-calendar-day {
  color: #409EFF !important;
}

.dark-theme .el-calendar-table td.prev .el-calendar-day,
.dark-theme .el-calendar-table td.next .el-calendar-day {
  color: var(--text-tertiary) !important;
}

.dark-theme .calendar-day {
  color: var(--text-primary) !important;
}

.dark-theme .day-number {
  color: inherit !important;
}

/* ========== 日期选择器 ========== */
.dark-theme .el-date-editor .el-input__wrapper {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .el-picker-panel {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .el-picker-panel__header {
  color: var(--text-primary) !important;
}

.dark-theme .el-picker-panel__icon-btn {
  color: var(--text-primary) !important;
}

.dark-theme .el-date-picker__header-label {
  color: var(--text-primary) !important;
}

.dark-theme .el-date-table th {
  color: var(--text-secondary) !important;
}

.dark-theme .el-date-table td {
  color: var(--text-primary) !important;
}

.dark-theme .el-date-table td.prev-month,
.dark-theme .el-date-table td.next-month {
  color: var(--text-tertiary) !important;
}

.dark-theme .el-date-table td.today span {
  color: #409EFF !important;
}

.dark-theme .el-date-table td.current span {
  background-color: #409EFF !important;
}

.dark-theme .el-date-table td:hover span {
  background-color: var(--hover-bg) !important;
}

.dark-theme .el-month-table td .cell {
  color: var(--text-primary) !important;
}

.dark-theme .el-month-table td.current .cell {
  background-color: #409EFF !important;
  color: #ffffff !important;
}

.dark-theme .el-month-table td .cell:hover {
  background-color: var(--hover-bg) !important;
}

.dark-theme .el-year-table td .cell {
  color: var(--text-primary) !important;
}

.dark-theme .el-year-table td.current .cell {
  background-color: #409EFF !important;
  color: #ffffff !important;
}

.dark-theme .el-year-table td .cell:hover {
  background-color: var(--hover-bg) !important;
}

/* ========== Drawer 抽屉 ========== */
.dark-theme .el-drawer {
  background-color: var(--card-bg) !important;
}

.dark-theme .el-drawer__header {
  color: var(--text-primary) !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .el-drawer__title {
  color: var(--text-primary) !important;
}

.dark-theme .el-drawer__body {
  background-color: var(--card-bg) !important;
}

/* ========== Timeline 时间线 ========== */
.dark-theme .el-timeline-item__content {
  color: var(--text-primary) !important;
}

.dark-theme .el-timeline-item__timestamp {
  color: var(--text-secondary) !important;
}

/* ========== 服务器连接设置补充 ========== */
.dark-theme .tutorial-section,
.dark-theme .config-section,
.dark-theme .presets-section,
.dark-theme .notebook-section {
  background-color: var(--bg-primary) !important;
}

.dark-theme .params-config {
  background-color: var(--bg-secondary) !important;
  border: 1px solid var(--border-color) !important;
}

.dark-theme .params-config .param-section-title {
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .el-form-item {
  --el-text-color-regular: var(--text-primary);
}

.dark-theme .el-input.is-disabled .el-input__wrapper {
  background-color: var(--bg-tertiary) !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
}

.dark-theme .el-input.is-disabled .el-input__inner {
  color: var(--text-tertiary) !important;
  -webkit-text-fill-color: var(--text-tertiary) !important;
}

.dark-theme .step-title {
  color: var(--text-primary) !important;
}

.dark-theme .step-content {
  color: var(--text-secondary) !important;
}

.dark-theme .code-block pre {
  background-color: #1e1e1e !important;
  color: #d4d4d4 !important;
}

.dark-theme .code-block code {
  color: #d4d4d4 !important;
}

/* Badge */
.dark-theme .el-badge__content {
  background-color: #409EFF !important;
}

/* 数字输入框 */
.dark-theme .el-input-number {
  --el-input-number-bg-color: var(--bg-secondary);
}

.dark-theme .el-input-number .el-input__wrapper {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .el-input-number__decrease,
.dark-theme .el-input-number__increase {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-input-number__decrease:hover,
.dark-theme .el-input-number__increase:hover {
  color: #409EFF !important;
}

/* Upload 上传组件 */
.dark-theme .el-upload-dragger {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-upload-dragger:hover {
  border-color: #409EFF !important;
}

.dark-theme .el-upload__text {
  color: var(--text-secondary) !important;
}

/* Loading */
.dark-theme .el-loading-mask {
  background-color: rgba(0, 0, 0, 0.7) !important;
}

/* 确保所有 popper 下拉层也应用暗色 */
.dark-theme .el-popper {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-popper.is-light {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-popper.is-light .el-popper__arrow::before {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

/* ========== 日历悬浮样式修复 ========== */
.dark-theme .el-calendar-day:hover {
  background-color: var(--hover-bg) !important;
}

.dark-theme .el-calendar-table td .el-calendar-day:hover {
  background-color: var(--hover-bg) !important;
}

.dark-theme .calendar-day:hover {
  background-color: var(--hover-bg) !important;
}

/* ========== 实验组/实验结果详情页和新建页 ========== */
.dark-theme .group-view,
.dark-theme .experiment-view {
  background-color: var(--bg-primary) !important;
  color: var(--text-primary) !important;
}

.dark-theme .notebook-container {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .header-bar {
  background-color: var(--bg-primary) !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .notebook-title .title-text {
  color: var(--text-primary) !important;
}

.dark-theme .notebook-title .title-input :deep(.el-input__wrapper) {
  background-color: transparent !important;
  box-shadow: none !important;
  border: none !important;
  border-bottom: 2px solid #606060 !important;
  border-radius: 0 !important;
}

.dark-theme .notebook-title .title-input :deep(.el-input__inner) {
  color: var(--text-primary) !important;
}

.dark-theme .meta-info {
  color: var(--text-secondary) !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .meta-info .meta-label {
  color: var(--text-tertiary) !important;
}

.dark-theme .meta-info .meta-value {
  color: var(--text-primary) !important;
}

.dark-theme .notebook-section {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

/* config-item label (配置参数、输出文件名等标题) */
.dark-theme .config-item label {
  color: var(--text-primary) !important;
}

.dark-theme .section-header {
  color: var(--text-primary) !important;
  background-color: transparent !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .note-textarea :deep(.el-textarea__inner) {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: none !important;
}

.dark-theme .note-content {
  background-color: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}

.dark-theme .empty-experiments {
  color: var(--text-tertiary) !important;
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
}

/* 观察记录区域 */
.dark-theme .observation-view {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .observation-time {
  color: var(--text-tertiary) !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .observation-text {
  color: var(--text-secondary) !important;
}

.dark-theme .observation-edit {
  background-color: transparent !important;
}

.dark-theme .observation-input :deep(.el-textarea__inner) {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: none !important;
}

.dark-theme .observation-actions {
  color: var(--text-secondary) !important;
}

.dark-theme .image-count {
  color: var(--text-tertiary) !important;
}

.dark-theme .observation-images img {
  border-color: var(--border-color) !important;
}

.dark-theme .attachments-section {
  background-color: var(--bg-tertiary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .attachments-title {
  color: var(--text-primary) !important;
}

.dark-theme .attachment-icon {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-secondary) !important;
}

.dark-theme .attachment-item {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .attachment-item:hover {
  border-color: var(--border-color) !important;
  box-shadow: none !important;
}

.dark-theme .attachment-name {
  color: var(--text-primary) !important;
}

.dark-theme .attachment-size {
  color: var(--text-tertiary) !important;
}

/* 附件删除按钮 */
.dark-theme .attachment-actions .el-button--danger:hover {
  background-color: rgba(245, 108, 108, 0.2) !important;
  color: #f56c6c !important;
}

.dark-theme .attachment-actions .el-button--danger.is-text:hover {
  background-color: rgba(245, 108, 108, 0.2) !important;
}

/* 附件下载按钮 */
.dark-theme .attachment-actions .el-button--primary:hover,
.dark-theme .attachment-actions .el-button--primary.is-text:hover {
  background-color: rgba(64, 158, 255, 0.2) !important;
  color: #409EFF !important;
}

.dark-theme .preview-image-item .remove-btn {
  background: rgba(0, 0, 0, 0.8) !important;
  color: white !important;
}

.dark-theme .preview-image-item .remove-btn:hover {
  background: rgba(255, 0, 0, 0.8) !important;
}

/* ========== 实验配置区域暗黑模式 ========== */
/* 实验 ID 区块 */
.dark-theme .experiment-id-section {
  background-color: var(--bg-tertiary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .experiment-id-label {
  color: #60a5fa !important;
}

.dark-theme .experiment-id-value code {
  background-color: var(--bg-secondary) !important;
  color: #60a5fa !important;
}

/* 实验 ID 复制按钮 */
.dark-theme .experiment-id-value .el-button:hover {
  background-color: rgba(64, 158, 255, 0.2) !important;
  color: #409EFF !important;
}

/* 命令参数表格 */
.dark-theme .command-params-table {
  border-color: var(--border-color) !important;
}

.dark-theme .command-params-header {
  background-color: var(--bg-tertiary) !important;
  border-bottom-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .command-params-row {
  border-bottom-color: var(--border-color) !important;
}

/* 命令参数表格内的输入框和下拉框 */
.dark-theme .command-params-row .el-input__wrapper,
.dark-theme .params-table-row .el-input__wrapper {
  background-color: var(--bg-secondary) !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
}

.dark-theme .command-params-row .el-input__inner,
.dark-theme .params-table-row .el-input__inner {
  color: var(--text-primary) !important;
}

.dark-theme .command-params-row .el-select .el-input__wrapper,
.dark-theme .params-table-row .el-select .el-input__wrapper {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .command-params-empty {
  background-color: var(--bg-secondary) !important;
  color: var(--text-tertiary) !important;
}

/* 配置参数表格 (params-table) */
.dark-theme .params-table {
  border-color: var(--border-color) !important;
}

.dark-theme .params-table-header {
  background-color: var(--bg-tertiary) !important;
  border-bottom-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .params-table-row {
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .params-table-empty {
  background-color: var(--bg-secondary) !important;
  color: var(--text-tertiary) !important;
}

/* 运行命令区域 */
.dark-theme .command-section {
  background-color: var(--bg-tertiary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .command-label {
  color: var(--text-primary) !important;
}

.dark-theme .command-block {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .command-placeholder {
  color: var(--text-tertiary) !important;
}

.dark-theme .command-tip {
  color: var(--text-secondary) !important;
}

/* section-subtitle */
.dark-theme .section-subtitle {
  color: var(--text-secondary) !important;
}

/* ========== 查看模式参数表格暗黑 ========== */
/* 命令参数查看表格 */
.dark-theme .command-params-view {
  border-color: var(--border-color) !important;
}

.dark-theme .params-view-row {
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .param-view-key {
  color: var(--text-primary) !important;
}

.dark-theme .param-view-value {
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
}

.dark-theme .param-view-desc {
  color: var(--text-tertiary) !important;
}

/* 配置参数查看表格 */
.dark-theme .params-view-table {
  border-color: var(--border-color) !important;
}

/* 命令参数项 */
.dark-theme .command-param-item {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .param-name {
  color: #60a5fa !important;
}

.dark-theme .param-value {
  color: var(--text-primary) !important;
}

/* config-value 查看模式值 */
.dark-theme .config-value {
  color: var(--text-primary) !important;
}

.dark-theme .path-value {
  color: var(--text-primary) !important;
}

/* 命令参数空状态 */
.dark-theme .command-params-empty {
  background-color: var(--bg-secondary) !important;
  color: var(--text-tertiary) !important;
}

/* ========== 服务器连接教程完整暗黑 ========== */
.dark-theme .tutorial-block {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .tutorial-block h3 {
  color: var(--text-primary) !important;
}

/* 系统设置：标题中的图标在暗黑模式下使用白色（避免沿用日间蓝色标题 icon） */
.dark-theme .settings-content h2 .el-icon,
.dark-theme .settings-content h3 .el-icon,
.dark-theme .settings-content h4 .el-icon,
.dark-theme .settings-content .preset-section-title > .el-icon {
  color: var(--text-primary) !important;
}

.dark-theme .tutorial-desc {
  color: var(--text-secondary) !important;
}

.dark-theme .tutorial-desc code {
  background-color: var(--bg-tertiary) !important;
  color: #409EFF !important;
}

.dark-theme .tutorial-content {
  color: var(--text-secondary) !important;
}

.dark-theme .tutorial-content h4 {
  color: var(--text-primary) !important;
}

.dark-theme .tutorial-content p,
.dark-theme .tutorial-content .tip {
  color: var(--text-secondary) !important;
}

.dark-theme .tutorial-content code {
  background-color: var(--bg-tertiary) !important;
  color: #409EFF !important;
}

.dark-theme .code-block-wrapper {
  background-color: #1e1e1e !important;
  border-color: var(--border-color) !important;
}

.dark-theme .code-block-wrapper .code-block {
  background-color: #1e1e1e !important;
  color: #d4d4d4 !important;
}

.dark-theme .code-block-wrapper pre {
  background-color: #1e1e1e !important;
  color: #d4d4d4 !important;
}

.dark-theme .copy-btn {
  background-color: var(--bg-tertiary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .copy-btn:hover {
  background-color: var(--hover-bg) !important;
  color: #409EFF !important;
}

/* 故障排查 warning-box */
.dark-theme .warning-box {
  background-color: rgba(245, 108, 108, 0.12) !important;
  border: 1px solid rgba(245, 108, 108, 0.35) !important;
  color: #f56c6c !important;
}

.dark-theme .warning-box strong {
  color: #f56c6c !important;
}

.dark-theme .warning-box code {
  background-color: var(--bg-secondary) !important;
  color: #f56c6c !important;
}

/* Tabs 在教程中 */
.dark-theme .el-tabs--border-card {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .el-tabs--border-card > .el-tabs__header {
  background-color: var(--bg-secondary) !important;
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .el-tabs--border-card > .el-tabs__header .el-tabs__item {
  color: var(--text-secondary) !important;
  border-color: var(--border-color) !important;
  background-color: var(--bg-secondary) !important;
}

.dark-theme .el-tabs--border-card > .el-tabs__header .el-tabs__item.is-active {
  color: var(--text-primary) !important;
  background-color: var(--card-bg) !important;
  border-bottom-color: var(--card-bg) !important;
}

.dark-theme .el-tabs--border-card > .el-tabs__content {
  background-color: var(--card-bg) !important;
}

/* ========== TensorBoard 配置 ========== */
.dark-theme .config-form-item {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .config-label {
  color: var(--text-primary) !important;
}

.dark-theme .config-help {
  color: var(--text-tertiary) !important;
}

/* 说明区域（提示框） */
.dark-theme .el-alert--info.is-light {
  background-color: rgba(64, 158, 255, 0.1) !important;
  color: var(--text-primary) !important;
}

.dark-theme .el-alert--info.is-light .el-alert__title {
  color: var(--text-primary) !important;
}

.dark-theme .el-alert--info.is-light .el-alert__description {
  color: var(--text-secondary) !important;
}

/* ========== 常用配置 ========== */
.dark-theme .preset-section {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .preset-section-title {
  color: var(--text-primary) !important;
}

.dark-theme .preset-section-title span {
  color: var(--text-primary) !important;
}

.dark-theme .algo-edit-list,
.dark-theme .algo-view-list {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .algo-edit-item {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .algo-view-item {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-primary) !important;
}

.dark-theme .preset-empty {
  color: var(--text-tertiary) !important;
}

/* 环境配置 */
.dark-theme .env-edit-list,
.dark-theme .env-view-list {
  background-color: var(--bg-secondary) !important;
}

.dark-theme .env-edit-item {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .env-item-header {
  background-color: var(--card-bg) !important;
}

.dark-theme .env-item-left {
  color: var(--text-primary) !important;
}

.dark-theme .env-map-count {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-secondary) !important;
}

.dark-theme .env-maps-content {
  background-color: var(--bg-secondary) !important;
  border-top-color: var(--border-color) !important;
}

.dark-theme .maps-label {
  color: var(--text-secondary) !important;
}

.dark-theme .map-edit-item {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .map-edit-item:hover {
  border-color: #409EFF !important;
}

.dark-theme .map-edit-item .el-input :deep(.el-input__inner) {
  color: var(--text-primary) !important;
}

.dark-theme .env-maps-empty {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-tertiary) !important;
}

/* 环境配置 - 查看模式 */
.dark-theme .env-view-item {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .env-view-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

.dark-theme .env-view-header {
  border-bottom-color: var(--border-color) !important;
}

.dark-theme .env-view-name {
  color: #10b981 !important;
}

.dark-theme .env-view-count {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-secondary) !important;
}

.dark-theme .env-view-map-item {
  background-color: rgba(16, 185, 129, 0.15) !important;
  border-color: rgba(16, 185, 129, 0.3) !important;
  color: #34d399 !important;
}

.dark-theme .env-view-map-item:hover {
  background-color: rgba(16, 185, 129, 0.25) !important;
  border-color: rgba(16, 185, 129, 0.5) !important;
}

.dark-theme .env-view-maps-empty {
  color: var(--text-tertiary) !important;
}

/* 环境名输入框 */
.dark-theme .env-name-input-inline :deep(.el-input__wrapper) {
  background: transparent !important;
}

.dark-theme .env-name-input-inline :deep(.el-input__wrapper):hover {
  background-color: var(--bg-tertiary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .env-name-input-inline :deep(.el-input__wrapper.is-focus) {
  background-color: var(--card-bg) !important;
  border-color: #10b981 !important;
}

.dark-theme .env-name-input-inline :deep(.el-input__inner) {
  color: #10b981 !important;
}

/* 使用说明区域 */
.dark-theme div[style*="background: #f5f7fa"],
.dark-theme div[style*="background:#f5f7fa"] {
  background-color: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}

/* 帮助文本（注释栏） */
.dark-theme .help-text {
  background-color: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}

.dark-theme .help-text strong {
  color: var(--text-primary) !important;
}

/* 标签配置 */
.dark-theme .tag-edit-item {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .tag-edit-item:hover {
  border-color: #409EFF !important;
}

.dark-theme .tags-empty {
  color: var(--text-tertiary) !important;
}

/* 模块配置 */
.dark-theme .module-list {
  background-color: var(--card-bg) !important;
}

.dark-theme .module-item {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .module-item:hover {
  background-color: var(--bg-tertiary) !important;
  border-color: #606060 !important;
}

/* 模块配置编辑模式：上下移动按钮 */
.dark-theme .module-actions .el-button {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

.dark-theme .module-actions .el-button:hover {
  background-color: var(--bg-tertiary) !important;
  border-color: #606060 !important;
}

/* ========== 额外表单元素 ========== */
.dark-theme .el-form-item__error {
  color: #f56c6c !important;
}

/* 确保详情页内的所有文字可见 */
.dark-theme .experiment-info,
.dark-theme .experiment-detail {
  color: var(--text-primary) !important;
}

.dark-theme .info-row {
  color: var(--text-primary) !important;
}

.dark-theme .info-row .label {
  color: var(--text-secondary) !important;
}

.dark-theme .info-row .value {
  color: var(--text-primary) !important;
}

/* 配置展示区域 */
.dark-theme .config-display,
.dark-theme .params-display {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
  color: var(--text-primary) !important;
}

/* JSON 展示 */
.dark-theme pre {
  background-color: #1e1e1e !important;
  color: #d4d4d4 !important;
}

/* 小标题 */
.dark-theme .sub-title,
.dark-theme .section-subtitle {
  color: var(--text-primary) !important;
}

/* param-section 参数区域 */
.dark-theme .param-section {
  background-color: var(--bg-secondary) !important;
  border-color: var(--border-color) !important;
}

.dark-theme .param-section-title {
  color: var(--text-primary) !important;
}
</style>
