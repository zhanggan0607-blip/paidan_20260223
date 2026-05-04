<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
import { useHeartbeat } from '@/composables/useHeartbeat'
import { useMenu } from '@/composables/useMenu'

const route = useRoute()
const { filteredMenuItems, expandedMenus, activeMenu, currentBreadcrumb, toggleMenu, handleMenuClick } = useMenu()
useHeartbeat()

watch(
  () => route.path,
  (newPath) => {
    for (const menu of filteredMenuItems.value) {
      if (menu.children) {
        const child = menu.children.find((c) => c.path === newPath)
        if (child) {
          activeMenu.value = child.id
          if (!expandedMenus.value.includes(menu.id)) {
            expandedMenus.value = [...expandedMenus.value, menu.id]
          }
          return
        }
      } else if (menu.path === newPath) {
        activeMenu.value = menu.id
        return
      }
    }
  },
  { immediate: true }
)
</script>

<template>
  <div class="layout">
    <Sidebar
      :filtered-menu-items="filteredMenuItems"
      :expanded-menus="expandedMenus"
      :active-menu="activeMenu"
      @toggle-menu="toggleMenu"
      @handle-menu-click="handleMenuClick"
    />
    <div class="layout__main">
      <Topbar :current-breadcrumb="currentBreadcrumb" />
      <main class="layout__content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--color-bg-page);
}

.layout__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.layout__content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}
</style>
