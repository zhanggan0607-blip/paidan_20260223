/**
 * 页面状态管理 Composable
 * 提供统一的页面加载、保存、模态框状态管理
 */
import { ref, computed } from 'vue'

interface PageStateOptions {
  onLoadingChange?: (loading: boolean) => void
}

export function usePageState(options: PageStateOptions = {}) {
  const loading = ref(false)
  const saving = ref(false)
  const isModalOpen = ref(false)
  const isViewModalOpen = ref(false)
  const isEditMode = ref(false)
  const editingId = ref<number | null>(null)

  const isBusy = computed(() => loading.value || saving.value)

  const openModal = (editId?: number) => {
    isEditMode.value = editId !== undefined
    editingId.value = editId ?? null
    isModalOpen.value = true
  }

  const closeModal = () => {
    isModalOpen.value = false
    isEditMode.value = false
    editingId.value = null
  }

  const openViewModal = () => {
    isViewModalOpen.value = true
  }

  const closeViewModal = () => {
    isViewModalOpen.value = false
  }

  const withLoading = async <T>(fn: () => Promise<T>): Promise<T | undefined> => {
    loading.value = true
    options.onLoadingChange?.(true)
    try {
      return await fn()
    } finally {
      loading.value = false
      options.onLoadingChange?.(false)
    }
  }

  const withSaving = async <T>(fn: () => Promise<T>): Promise<T | undefined> => {
    saving.value = true
    try {
      return await fn()
    } finally {
      saving.value = false
    }
  }

  return {
    loading,
    saving,
    isModalOpen,
    isViewModalOpen,
    isEditMode,
    editingId,
    isBusy,
    openModal,
    closeModal,
    openViewModal,
    closeViewModal,
    withLoading,
    withSaving,
  }
}
