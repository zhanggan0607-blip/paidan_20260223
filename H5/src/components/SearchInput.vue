<template>
  <div class="search-input-wrapper" ref="wrapperRef">
    <input
      type="text"
      class="search-input"
      :placeholder="placeholder"
      :value="modelValue"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
    />
    <div v-if="showDropdown && filteredHistory.length > 0" class="search-dropdown">
      <div class="dropdown-header">
        <span>历史记录</span>
        <a href="#" class="clear-link" @click.prevent="handleClearHistory">清空</a>
      </div>
      <div
        v-for="(item, index) in filteredHistory"
        :key="index"
        class="dropdown-item"
        @touchstart="handleTouchStart(index)"
        @click="selectItem(item)"
      >
        <span class="history-icon">🕐</span>
        <span class="history-text">{{ item }}</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useSearchHistory } from '../utils/searchHistory'

export default defineComponent({
  name: 'SearchInput',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: '请输入'
    },
    fieldKey: {
      type: String,
      required: true
    }
  },
  emits: ['update:modelValue', 'search', 'input'],
  setup(props, { emit }) {
    const wrapperRef = ref<HTMLElement | null>(null)
    const showDropdown = ref(false)
    const history = ref<string[]>([])
    
    const searchHistory = useSearchHistory({ fieldKey: props.fieldKey })
    
    const filteredHistory = computed(() => {
      if (!props.modelValue) {
        return history.value
      }
      return searchHistory.filter(props.modelValue)
    })
    
    const loadHistory = () => {
      history.value = searchHistory.load()
    }
    
    const handleInput = (event: Event) => {
      const target = event.target as HTMLInputElement
      const value = target.value
      emit('update:modelValue', value)
      emit('input', value)
    }
    
    const handleFocus = () => {
      loadHistory()
      showDropdown.value = true
    }
    
    const handleBlur = () => {
      setTimeout(() => {
        showDropdown.value = false
      }, 200)
    }
    
    const selectItem = (item: string) => {
      emit('update:modelValue', item)
      emit('search', item)
      searchHistory.save(item)
      showDropdown.value = false
    }
    
    const handleTouchStart = (index: number) => {
      const items = document.querySelectorAll('.dropdown-item')
      items.forEach((el, i) => {
        if (i === index) {
          el.classList.add('active')
        } else {
          el.classList.remove('active')
        }
      })
    }
    
    const handleClearHistory = () => {
      searchHistory.clear()
      history.value = []
      showDropdown.value = false
    }
    
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.value && !wrapperRef.value.contains(event.target as Node)) {
        showDropdown.value = false
      }
    }
    
    onMounted(() => {
      loadHistory()
      document.addEventListener('click', handleClickOutside)
    })
    
    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })
    
    watch(() => props.fieldKey, () => {
      loadHistory()
    })
    
    return {
      wrapperRef,
      showDropdown,
      filteredHistory,
      handleInput,
      handleFocus,
      handleBlur,
      selectItem,
      handleTouchStart,
      handleClearHistory
    }
  }
})
</script>

<style scoped>
.search-input-wrapper {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-input::placeholder {
  color: #999;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
  margin-top: 4px;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
  color: #999;
}

.clear-link {
  color: #1976d2;
  text-decoration: none;
  font-size: 12px;
}

.clear-link:active {
  opacity: 0.7;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  cursor: pointer;
  transition: background-color 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.dropdown-item:active,
.dropdown-item.active {
  background-color: #f5f5f5;
}

.history-icon {
  font-size: 14px;
  opacity: 0.6;
}

.history-text {
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
