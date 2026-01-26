import { createRouter, createWebHistory } from 'vue-router'
import ExperimentList from './views/ExperimentList.vue'
import ExperimentView from './views/ExperimentView.vue'
import CalendarView from './views/CalendarView.vue'
import Settings from './views/Settings.vue'
import ImportExperiments from './views/ImportExperiments.vue'
import GroupList from './views/GroupList.vue'
import GroupView from './views/GroupView.vue'

const routes = [
  {
    path: '/',
    name: 'ExperimentList',
    component: ExperimentList
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: CalendarView
  },
  {
    path: '/experiment/new',
    name: 'NewExperiment',
    component: ExperimentView
  },
  {
    path: '/experiment/:id',
    name: 'Experiment',
    component: ExperimentView
  },
  {
    path: '/groups',
    name: 'Groups',
    component: GroupList
  },
  {
    path: '/group/new',
    name: 'NewGroup',
    component: GroupView
  },
  {
    path: '/group/:id',
    name: 'Group',
    component: GroupView
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/import',
    name: 'Import',
    component: ImportExperiments
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
