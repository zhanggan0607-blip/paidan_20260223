<template>
  <div v-if="visible" class="confirm-overlay" @click.self="handleCancel">
    <div class="confirm-container">
      <div class="confirm-header">
        <h3 class="confirm-title">{{ title }}</h3>
        <button class="confirm-close" @click="handleCancel">×</button>
      </div>
      <div class="confirm-body">
        <p class="confirm-message">{{ message }}</p>
      </div>
      <div class="confirm-footer">
        <button class="btn btn-cancel" @click="handleCancel">取消</button>
        <button class="btn btn-confirm" @click="handleConfirm">确定</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ConfirmDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '确认'
    },
    message: {
      type: String,
      required: true
    }
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const handleConfirm = () => {
      emit('confirm')
    }

    const handleCancel = () => {
      emit('cancel')
    }

    return {
      handleConfirm,
      handleCancel
    }
  }
})
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.confirm-container {
  background: #fff;
  border-radius: 8px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.confirm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.confirm-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.confirm-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  transition: color 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-close:hover {
  color: #333;
}

.confirm-body {
  padding: 24px;
}

.confirm-message {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.confirm-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 3px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-cancel {
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-confirm {
  background: #2196F3;
  color: #fff;
}

.btn-confirm:hover {
  background: #1976D2;
}
</style>
