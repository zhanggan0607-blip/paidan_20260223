<template>
  <div class="online-users-panel">
    <div class="online-header" @click="togglePanel">
      <div class="online-title">
        <span class="online-icon">👥</span>
        <span class="online-text">在线用户</span>
        <span class="online-badge" :class="{ 'has-users': totalCount > 0 }">
          {{ totalCount }}
        </span>
      </div>
      <div class="online-stats">
        <span class="stat-item pc">
          <span class="stat-dot pc-dot"></span>
          PC端: {{ pcCount }}
        </span>
        <span class="stat-item h5">
          <span class="stat-dot h5-dot"></span>
          H5端: {{ h5Count }}
        </span>
      </div>
      <span class="toggle-icon" :class="{ expanded: isExpanded }">▼</span>
    </div>
    
    <transition name="slide">
      <div class="online-body" v-if="isExpanded">
        <div class="users-section" v-if="pcUsers.length > 0">
          <div class="section-header">
            <span class="section-dot pc-dot"></span>
            PC端用户 ({{ pcUsers.length }})
          </div>
          <div class="users-list">
            <div class="user-item" v-for="user in pcUsers" :key="user.id">
              <div class="user-avatar">{{ getAvatar(user.user_name) }}</div>
              <div class="user-info">
                <div class="user-name">{{ user.user_name }}</div>
                <div class="user-meta">
                  <span class="user-dept" v-if="user.department">{{ user.department }}</span>
                  <span class="user-time">{{ formatTime(user.login_time) }}</span>
                </div>
              </div>
              <div class="user-status online">在线</div>
            </div>
          </div>
        </div>
        
        <div class="users-section" v-if="h5Users.length > 0">
          <div class="section-header">
            <span class="section-dot h5-dot"></span>
            H5端用户 ({{ h5Users.length }})
          </div>
          <div class="users-list">
            <div class="user-item" v-for="user in h5Users" :key="user.id">
              <div class="user-avatar">{{ getAvatar(user.user_name) }}</div>
              <div class="user-info">
                <div class="user-name">{{ user.user_name }}</div>
                <div class="user-meta">
                  <span class="user-dept" v-if="user.department">{{ user.department }}</span>
                  <span class="user-time">{{ formatTime(user.login_time) }}</span>
                </div>
              </div>
              <div class="user-status online">在线</div>
            </div>
          </div>
        </div>
        
        <div class="no-users" v-if="totalCount === 0">
          <span class="no-users-icon">😴</span>
          <span>暂无在线用户</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue'
import onlineUserService, { OnlineUser } from '@/services/onlineUser'

export default defineComponent({
  name: 'OnlineUsersPanel',
  setup() {
    const isExpanded = ref(false)
    const pcUsers = ref<OnlineUser[]>([])
    const h5Users = ref<OnlineUser[]>([])
    const totalCount = computed(() => pcUsers.value.length + h5Users.value.length)
    const pcCount = computed(() => pcUsers.value.length)
    const h5Count = computed(() => h5Users.value.length)
    
    let refreshInterval: number | null = null
    
    const fetchOnlineUsers = async () => {
      try {
        const stats = await onlineUserService.getOnlineStatistics()
        console.log('获取在线用户数据:', stats)
        pcUsers.value = stats.pc_users || []
        h5Users.value = stats.h5_users || []
        console.log('PC用户:', pcUsers.value.length, 'H5用户:', h5Users.value.length)
      } catch (error) {
        console.error('获取在线用户失败:', error)
      }
    }
    
    const togglePanel = () => {
      isExpanded.value = !isExpanded.value
    }
    
    const getAvatar = (name: string) => {
      return name ? name.charAt(0).toUpperCase() : '?'
    }
    
    const formatTime = (timeStr: string) => {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      const now = new Date()
      const diff = now.getTime() - date.getTime()
      const minutes = Math.floor(diff / 60000)
      
      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours}小时前`
      
      return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
    }
    
    onMounted(() => {
      console.log('OnlineUsersPanel mounted')
      fetchOnlineUsers()
      refreshInterval = window.setInterval(fetchOnlineUsers, 10000)
      window.addEventListener('user-changed', fetchOnlineUsers)
    })
    
    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
      window.removeEventListener('user-changed', fetchOnlineUsers)
    })
    
    return {
      isExpanded,
      pcUsers,
      h5Users,
      totalCount,
      pcCount,
      h5Count,
      togglePanel,
      getAvatar,
      formatTime
    }
  }
})
</script>

<style scoped>
.online-users-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  margin-bottom: 16px;
}

.online-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.online-header:hover {
  background-color: #f5f7fa;
}

.online-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.online-icon {
  font-size: 18px;
}

.online-text {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.online-badge {
  background: #e0e0e0;
  color: #666;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.online-badge.has-users {
  background: #4CAF50;
  color: white;
}

.online-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.pc-dot {
  background: #2196F3;
}

.h5-dot {
  background: #FF9800;
}

.toggle-icon {
  font-size: 12px;
  color: #999;
  transition: transform 0.3s;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
}

.online-body {
  border-top: 1px solid #f0f0f0;
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.users-section {
  margin-bottom: 16px;
}

.users-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.section-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-item:hover {
  background: #f0f2f5;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
}

.user-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #999;
}

.user-dept {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.user-status.online {
  background: #e8f5e9;
  color: #4CAF50;
}

.no-users {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  color: #999;
  gap: 8px;
}

.no-users-icon {
  font-size: 32px;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 300px;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
