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
      @keydown="handleKeydown"
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
        :class="{ active: activeIndex === index }"
        @mousedown.prevent="selectItem(item)"
        @mouseover="activeIndex = index"
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
    const activeIndex = ref(-1)
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
      activeIndex.value = -1
    }
    
    const handleFocus = () => {
      loadHistory()
      showDropdown.value = true
    }
    
    const handleBlur = () => {
      setTimeout(() => {
        showDropdown.value = false
        activeIndex.value = -1
      }, 200)
    }
    
    const selectItem = (item: string) => {
      emit('update:modelValue', item)
      emit('search', item)
      searchHistory.save(item)
      showDropdown.value = false
    }
    
    const handleKeydown = (event: KeyboardEvent) => {
      if (!showDropdown.value || filteredHistory.value.length === 0) {
        if (event.key === 'Enter') {
          emit('search', props.modelValue)
          if (props.modelValue.trim()) {
            searchHistory.save(props.modelValue.trim())
          }
        }
        return
      }
      
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault()
          activeIndex.value = Math.min(activeIndex.value + 1, filteredHistory.value.length - 1)
          break
        case 'ArrowUp':
          event.preventDefault()
          activeIndex.value = Math.max(activeIndex.value - 1, -1)
          break
        case 'Enter':
          event.preventDefault()
          if (activeIndex.value >= 0) {
            selectItem(filteredHistory.value[activeIndex.value])
          } else {
            emit('search', props.modelValue)
            if (props.modelValue.trim()) {
              searchHistory.save(props.modelValue.trim())
            }
          }
          break
        case 'Escape':
          showDropdown.value = false
          activeIndex.value = -1
          break
      }
    }
    
    const handleClearHistory = () => {
      searchHistory.clear()
      history.value = []
      showDropdown.value = false
    }
    
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.value && !wrapperRef.value.contains(event.target as Node)) {
        showDropdown.value = false
        activeIndex.value = -1
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
      activeIndex,
      filteredHistory,
      handleInput,
      handleFocus,
      handleBlur,
      handleKeydown,
      selectItem,
      handleClearHistory
    }
  }
})
</script>

<style scoped>
.search-input-wrapper {
  position: relative;
  width: 200px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
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
  max-height: 300px;
  overflow-y: auto;
  margin-top: 4px;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
  color: #999;
}

.clear-link {
  color: #1976d2;
  text-decoration: none;
  font-size: 12px;
}

.clear-link:hover {
  text-decoration: underline;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.dropdown-item:hover,
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
