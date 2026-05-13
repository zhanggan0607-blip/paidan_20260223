<template>
  <div
    class="worker-entry-overlay"
    @click.self="$emit('close')"
  >
  <div class="worker-entry-modal">
    <div class="modal-header">
      <h3 class="modal-title">
        施工人员录入
      </h3>
      <button
        class="modal-close"
        @click="$emit('close')"
      >
        ×
      </button>
    </div>
    <div class="modal-body">
      <div class="info-bar">
        <span>项目：{{ projectName }}</span>
        <span>用工周期：{{ workDateStart }} 至 {{ workDateEnd }}</span>
        <span>已录入：<strong>{{ workers.length }}</strong> 人</span>
      </div>

      <div class="workers-section">
        <table
          v-if="workers.length > 0"
          class="workers-table"
        >
          <thead>
            <tr>
              <th>序号</th>
              <th>姓名</th>
              <th>性别</th>
              <th>身份证号码</th>
              <th>住址</th>
              <th>身份证正面</th>
              <th>身份证反面</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(worker, index) in workers"
              :key="index"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ worker.name || '-' }}</td>
              <td>{{ worker.gender || '-' }}</td>
              <td>{{ maskIdCard(worker.idCardNumber) }}</td>
              <td>{{ worker.address || '-' }}</td>
              <td>
                <img
                  v-if="worker.idCardFront"
                  :src="worker.idCardFront"
                  class="id-card-thumb"
                  @click="previewImage(worker.idCardFront)"
                  @error="onImageError($event, worker, 'idCardFront')"
                >
                <span
                  v-else
                  class="no-photo"
                >未上传</span>
              </td>
              <td>
                <img
                  v-if="worker.idCardBack"
                  :src="worker.idCardBack"
                  class="id-card-thumb"
                  @click="previewImage(worker.idCardBack)"
                  @error="onImageError($event, worker, 'idCardBack')"
                >
                <span
                  v-else
                  class="no-photo"
                >未上传</span>
              </td>
              <td>
                <button
                  class="btn-small btn-edit"
                  @click="editWorker(index)"
                >
                  编辑
                </button>
                <button
                  class="btn-small btn-delete"
                  @click="deleteWorker(index)"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div
          v-else
          class="no-workers"
        >
          暂无施工人员，请点击下方按钮添加
        </div>
      </div>

      <div class="add-worker-section">
        <button
          class="btn btn-add-worker"
          @click="showAddWorkerForm = true"
        >
          + 添加施工人员
        </button>
      </div>
    </div>
    <div class="modal-footer">
      <button
        class="btn btn-cancel"
        @click="$emit('close')"
      >
        取消
      </button>
      <button
        class="btn btn-save"
        @click="handleConfirm"
      >
        确认（{{ workers.length }}人）
      </button>
    </div>

    <div
      v-if="showAddWorkerForm"
      class="worker-form-overlay"
      @click.self="showAddWorkerForm = false"
    >
      <div class="worker-form-container">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ editingIndex >= 0 ? '编辑施工人员' : '添加施工人员' }}
          </h3>
          <button
            class="modal-close"
            @click="closeWorkerForm"
          >
            ×
          </button>
        </div>
        <div class="worker-form-body">
          <div class="form-row">
            <div class="form-item">
              <label
                for="name"
                class="form-label"
              ><span class="required">*</span> 姓名</label>
              <input
                id="name"
               
                v-model="currentWorker.name"
                name="name"
                type="text"
                class="form-input"
                placeholder="请输入姓名"
                autocomplete="name"
              >
            </div>
            <div class="form-item">
              <label
                for="gender"
                class="form-label"
              ><span class="required">*</span> 性别</label>
              <select
                id="gender"
                v-model="currentWorker.gender"
                name="gender"
                class="form-input"
              >
                <option value="">
                  请选择
                </option>
                <option value="男">
                  男
                </option>
                <option value="女">
                  女
                </option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label
                for="idCardNumber"
                class="form-label"
              ><span class="required">*</span> 身份证号码</label>
              <input
                id="idCardNumber"
               
                v-model="currentWorker.idCardNumber"
                name="idCardNumber"
                type="text"
                class="form-input"
                placeholder="请输入18位身份证号码"
                maxlength="18"
                autocomplete="off"
                @input="handleIdCardChange"
              >
              <span
                v-if="idCardError"
                class="error-msg"
              >{{ idCardError }}</span>
            </div>
            <div class="form-item">
              <label
                for="birthDate"
                class="form-label"
              ><span class="required">*</span> 出生日期</label>
              <input
                id="birthDate"
               
                v-model="currentWorker.birthDate"
                name="birthDate"
                type="date"
                class="form-input"
                autocomplete="bday"
              >
            </div>
          </div>
          <div class="form-row">
            <div class="form-item full-width">
              <label
                for="address"
                class="form-label"
              ><span class="required">*</span> 住址</label>
              <input
                id="address"
                v-model="currentWorker.address"
                name="address"
                type="text"
                class="form-input"
                placeholder="请输入住址"
              >
            </div>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label
                for="issuingAuthority"
                class="form-label"
              ><span class="required">*</span> 签发机关</label>
              <input
                id="issuingAuthority"
               
                v-model="currentWorker.issuingAuthority"
                name="issuingAuthority"
                type="text"
                class="form-input"
                placeholder="请输入签发机关"
                autocomplete="organization"
              >
            </div>
            <div class="form-item">
              <label
                for="validPeriod"
                class="form-label"
              ><span class="required">*</span> 有效期限</label>
              <input
                id="validPeriod"
               
                v-model="currentWorker.validPeriod"
                name="validPeriod"
                type="text"
                class="form-input"
                placeholder="请输入有效期限"
                autocomplete="cc-exp"
              >
            </div>
          </div>
          <div class="form-row id-card-photos">
            <div class="form-item">
              <label
                for="idCardFront"
                class="form-label"
              ><span class="required">*</span> 身份证正面</label>
              <div class="photo-upload-area">
                <input
                  id="idCardFront"
                  ref="frontInputRef"
                  name="idCardFront"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  :disabled="ocrLoading"
                  @change="handleIdCardUpload('front', $event)"
                >
                <div
                  v-if="currentWorker.idCardFront"
                  class="photo-preview"
                >
                  <img
                    :src="currentWorker.idCardFront"
                    @click="previewImage(currentWorker.idCardFront)"
                    @error="onImageError($event, currentWorker, 'idCardFront')"
                  >
                  <button
                    class="remove-btn"
                    @click="currentWorker.idCardFront = ''"
                  >
                    ×
                  </button>
                </div>
                <button
                  v-else
                  class="upload-btn"
                  :disabled="ocrLoading"
                  @click="triggerUpload('front')"
                >
                  <span
                    v-if="ocrLoading && ocrLoadingSide === 'front'"
                    class="loading-spinner"
                  />
                  <span v-else>+</span>
                  <span>{{
                    ocrLoading && ocrLoadingSide === 'front' ? '识别中...' : '上传正面'
                  }}</span>
                </button>
              </div>
            </div>
            <div class="form-item">
              <label
                for="idCardBack"
                class="form-label"
              ><span class="required">*</span> 身份证反面</label>
              <div class="photo-upload-area">
                <input
                  id="idCardBack"
                  ref="backInputRef"
                  name="idCardBack"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  :disabled="ocrLoading"
                  @change="handleIdCardUpload('back', $event)"
                >
                <div
                  v-if="currentWorker.idCardBack"
                  class="photo-preview"
                >
                  <img
                    :src="currentWorker.idCardBack"
                    @click="previewImage(currentWorker.idCardBack)"
                    @error="onImageError($event, currentWorker, 'idCardBack')"
                  >
                  <button
                    class="remove-btn"
                    @click="currentWorker.idCardBack = ''"
                  >
                    ×
                  </button>
                </div>
                <button
                  v-else
                  class="upload-btn"
                  :disabled="ocrLoading"
                  @click="triggerUpload('back')"
                >
                  <span
                    v-if="ocrLoading && ocrLoadingSide === 'back'"
                    class="loading-spinner"
                  />
                  <span v-else>+</span>
                  <span>{{
                    ocrLoading && ocrLoadingSide === 'back' ? '识别中...' : '上传反面'
                  }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="closeWorkerForm"
          >
            取消
          </button>
          <button
            class="btn btn-save"
            @click="saveWorker"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import { request } from '@/api/request'
import type { ApiResponse } from '@/types/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { maskIdCard, compressImage, blobToFile } from '@sstcp/shared'

interface WorkerInfo {
  id?: number
  name: string
  gender: string
  birthDate: string
  address: string
  idCardNumber: string
  issuingAuthority: string
  validPeriod: string
  idCardFront: string
  idCardBack: string
}

export default defineComponent({
  name: 'WorkerEntryModal',
  props: {
    projectId: {
      type: String,
      required: true,
    },
    projectName: {
      type: String,
      required: true,
    },
    workDateStart: {
      type: String,
      required: true,
    },
    workDateEnd: {
      type: String,
      required: true,
    },
    initialWorkers: {
      type: Array as () => WorkerInfo[],
      default: (): any[] => [],
    },
  },
  emits: ['close', 'confirm'],
  setup(props, { emit }) {
    const workers = ref<WorkerInfo[]>([...props.initialWorkers])
    const showAddWorkerForm = ref(false)
    const editingIndex = ref(-1)
    const idCardError = ref('')
    const frontInputRef = ref<HTMLInputElement | null>(null)
    const backInputRef = ref<HTMLInputElement | null>(null)
    const ocrLoading = ref(false)
    const ocrLoadingSide = ref<'front' | 'back' | ''>('')

    const currentWorker = ref<WorkerInfo>({
      name: '',
      gender: '',
      birthDate: '',
      address: '',
      idCardNumber: '',
      issuingAuthority: '',
      validPeriod: '',
      idCardFront: '',
      idCardBack: '',
    })

    watch(
      () => props.initialWorkers,
      (newVal) => {
        workers.value = [...newVal]
      }
    )

    const handleIdCardChange = () => {
      const idCard = currentWorker.value.idCardNumber
      if (!idCard) {
        idCardError.value = ''
        return
      }

      if (idCard.length === 18) {
        const year = parseInt(idCard.substring(6, 10))
        const month = idCard.substring(10, 12)
        const day = idCard.substring(12, 14)
        const genderCode = parseInt(idCard.substring(16, 17))

        currentWorker.value.birthDate = `${year}-${month}-${day}`
        currentWorker.value.gender = genderCode % 2 === 1 ? '男' : '女'
        idCardError.value = ''
      } else if (idCard.length > 0) {
        idCardError.value =
          idCard.length < 18
            ? `已输入${idCard.length}位，还需${18 - idCard.length}位`
            : '身份证号码超出18位'
      }
    }

    const fileToBase64 = (file: File): Promise<string> => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
          const result = reader.result as string
          const base64 = result.split(',')[1] || ''
          resolve(base64)
        }
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
    }

    const handleIdCardUpload = async (side: 'front' | 'back', event: Event) => {
      const target = event.target as HTMLInputElement
      if (!target?.files?.[0]) return

      const file = target.files[0]
      ocrLoading.value = true
      ocrLoadingSide.value = side

      try {
        let compressedFile: File | null = null
        let compressedBase64: string
        try {
          const compressedBlob = await compressImage(file, 200)
          compressedFile = blobToFile(compressedBlob, file.name)
          compressedBase64 = await fileToBase64(compressedFile)
        } catch {
          compressedBase64 = await fileToBase64(file)
        }

        const localPreview = `data:image/jpeg;base64,${compressedBase64}`
        if (side === 'front') {
          currentWorker.value.idCardFront = localPreview
        } else {
          currentWorker.value.idCardBack = localPreview
        }

        const ocrPromise = (async () => {
          try {
            const ocrResponse = (await request.post('/ocr/idcard', {
              imageBase64: compressedBase64,
              side: side === 'front' ? 'face' : 'back',
            })) as unknown as ApiResponse<{
              name?: string
              gender?: string
              birthDate?: string
              address?: string
              idCardNumber?: string
              issuingAuthority?: string
              validPeriod?: string
            }>

            if (ocrResponse.code === 200 && ocrResponse.data) {
              const ocrData = ocrResponse.data

              if (side === 'front') {
                if (ocrData.name) currentWorker.value.name = ocrData.name
                if (ocrData.gender) currentWorker.value.gender = ocrData.gender
                if (ocrData.birthDate) currentWorker.value.birthDate = ocrData.birthDate
                if (ocrData.address) currentWorker.value.address = ocrData.address
                if (ocrData.idCardNumber) {
                  currentWorker.value.idCardNumber = ocrData.idCardNumber
                  handleIdCardChange()
                  
                  request.get(
                    `/spot-work/workers/check-id-card?id_card_number=${ocrData.idCardNumber}&project_id=${props.projectId}&start_date=${props.workDateStart}&end_date=${props.workDateEnd}`
                  ).then((checkResponse) => {
                    const resp = checkResponse as unknown as ApiResponse<{
                      exists: boolean
                      can_reuse: boolean
                      duplicate_in_work?: boolean
                      name?: string
                      project_name?: string
                      work_status?: string
                      work_id?: string
                    }>
                    if (resp.code === 200 && resp.data?.exists) {
                      const existingInfo = resp.data
                      if (existingInfo.duplicate_in_work) {
                        idCardError.value = '该身份证号码已在本工单中录入，不能重复上传'
                        ElMessage.warning(
                          `该身份证已在本工单中录入！姓名：${existingInfo.name}，同一工单中同一身份证只能上传一次`
                        )
                      } else if (!existingInfo.can_reuse) {
                        idCardError.value = '该身份证号码已存在，不能重复录入'
                        ElMessage.warning(
                          `该身份证已录入未完成工单！姓名：${existingInfo.name}，项目：${existingInfo.project_name}，工单号：${existingInfo.work_id}，状态：${existingInfo.work_status}`
                        )
                      } else {
                        ElMessage.info(
                          `该身份证已完成工单，可继续录入。姓名：${existingInfo.name}，原工单：${existingInfo.work_id}`
                        )
                      }
                    }
                  }).catch((checkError) => {
                    console.error('检查身份证失败:', checkError)
                  })
                }
              } else {
                if (ocrData.issuingAuthority)
                  currentWorker.value.issuingAuthority = ocrData.issuingAuthority
                if (ocrData.validPeriod) currentWorker.value.validPeriod = ocrData.validPeriod
              }

              if (side === 'front' && !ocrData.name && !ocrData.idCardNumber) {
                ElMessage.warning('身份证识别失败，请确保图片清晰')
              } else if (side === 'back' && !ocrData.issuingAuthority && !ocrData.validPeriod) {
                ElMessage.warning('身份证反面识别失败，请确保图片清晰')
              }
            } else if (ocrResponse.code !== 200) {
              ElMessage.error(ocrResponse.message || 'OCR识别失败')
            }
          } catch (ocrError) {
            console.error('OCR识别失败:', ocrError)
            ElMessage.warning('OCR识别失败，请手动填写信息')
          }
        })()

        const uploadFile = compressedFile || file
        const uploadPromise = (async () => {
          try {
            const formData = new FormData()
            formData.append('file', uploadFile)

            const response = (await request.post('/upload', formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
            })) as unknown as ApiResponse<{ url: string }>

            if (response.code === 200 && response.data) {
              if (side === 'front') {
                currentWorker.value.idCardFront = response.data.url
              } else {
                currentWorker.value.idCardBack = response.data.url
              }
            } else {
              console.error('图片上传失败:', response.message)
            }
          } catch (uploadError) {
            console.error('图片上传失败:', uploadError)
          }
        })()

        await ocrPromise
        uploadPromise.catch(() => {})
      } catch (error) {
        console.error('上传失败:', error)
        if (side === 'front') {
          currentWorker.value.idCardFront = ''
        } else {
          currentWorker.value.idCardBack = ''
        }
        ElMessage.error('上传失败，请重试')
      } finally {
        ocrLoading.value = false
        ocrLoadingSide.value = ''
      }

      target.value = ''
    }

    const triggerUpload = (side: 'front' | 'back') => {
      if (side === 'front' && frontInputRef.value) {
        frontInputRef.value.click()
      } else if (side === 'back' && backInputRef.value) {
        backInputRef.value.click()
      }
    }

    const previewImage = (url: string) => {
      window.open(url, '_blank')
    }

    const onImageError = (event: Event, worker: any, field: 'idCardFront' | 'idCardBack') => {
      const img = event.target as HTMLImageElement
      img.style.display = 'none'
      const placeholder = document.createElement('span')
      placeholder.className = 'no-photo'
      placeholder.textContent = '图片加载失败'
      img.parentNode?.insertBefore(placeholder, img)
    }

    const editWorker = (index: number) => {
      editingIndex.value = index
      currentWorker.value = { ...workers.value[index] }
      showAddWorkerForm.value = true
    }

    const deleteWorker = async (index: number) => {
      if (!confirm('请确认是否要删除该施工人员？')) return
      const worker = workers.value[index]
      if (worker.id) {
        try {
          const response = (await request.delete(
            `/spot-work/workers/${worker.id}`
          )) as unknown as ApiResponse<null>
          if (response.code !== 200) {
            ElMessage.error(response.message || '删除失败')
            return
          }
        } catch (error) {
          ElMessage.error('删除失败，请重试')
          return
        }
      }
      workers.value.splice(index, 1)
    }

    const closeWorkerForm = () => {
      showAddWorkerForm.value = false
      editingIndex.value = -1
      currentWorker.value = {
        name: '',
        gender: '',
        birthDate: '',
        address: '',
        idCardNumber: '',
        issuingAuthority: '',
        validPeriod: '',
        idCardFront: '',
        idCardBack: '',
      }
      idCardError.value = ''
    }

    const saveWorker = () => {
      if (!currentWorker.value.name) {
        ElMessage.warning('请输入姓名')
        return
      }
      if (!currentWorker.value.gender) {
        ElMessage.warning('请选择性别')
        return
      }
      if (!currentWorker.value.idCardNumber || currentWorker.value.idCardNumber.length !== 18) {
        ElMessage.warning('请输入正确的18位身份证号码')
        return
      }
      if (!currentWorker.value.birthDate) {
        ElMessage.warning('请选择出生日期')
        return
      }
      if (!currentWorker.value.address) {
        ElMessage.warning('请输入住址')
        return
      }
      if (!currentWorker.value.issuingAuthority) {
        ElMessage.warning('请输入签发机关')
        return
      }
      if (!currentWorker.value.validPeriod) {
        ElMessage.warning('请输入有效期限')
        return
      }
      if (!currentWorker.value.idCardFront) {
        ElMessage.warning('请上传身份证正面照片')
        return
      }
      if (!currentWorker.value.idCardBack) {
        ElMessage.warning('请上传身份证反面照片')
        return
      }

      const duplicateInList = workers.value.some(
        (w, idx) => w.idCardNumber === currentWorker.value.idCardNumber && idx !== editingIndex.value
      )
      if (duplicateInList) {
        ElMessage.warning('该身份证号码已在当前列表中，同一工单中同一身份证只能上传一次')
        return
      }

      if (editingIndex.value >= 0) {
        workers.value[editingIndex.value] = { ...currentWorker.value }
      } else {
        workers.value.push({ ...currentWorker.value })
      }

      closeWorkerForm()
    }

    const handleConfirm = () => {
      emit('confirm', [...workers.value])
    }

    return {
      workers,
      showAddWorkerForm,
      editingIndex,
      currentWorker,
      idCardError,
      frontInputRef,
      backInputRef,
      ocrLoading,
      ocrLoadingSide,
      handleIdCardChange,
      handleIdCardUpload,
      triggerUpload,
      previewImage,
      onImageError,
      editWorker,
      deleteWorker,
      closeWorkerForm,
      saveWorker,
      handleConfirm,
      maskIdCard,
    }
  },
})
</script>

<style scoped>
.worker-entry-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.worker-entry-modal {
  background: var(--color-bg-card);
  border-radius: 8px;
  width: 900px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: var(--color-text-placeholder);
  cursor: pointer;
}

.modal-close:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: 24px;
}

.info-bar {
  display: flex;
  gap: 24px;
  padding: 12px 16px;
  background: var(--color-bg-page);
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.info-bar strong {
  color: var(--color-primary);
}

.workers-section {
  margin-bottom: 16px;
}

.workers-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.workers-table th,
.workers-table td {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  text-align: left;
}

.workers-table th {
  background: var(--color-bg-page);
  font-weight: 500;
}

.id-card-thumb {
  width: 60px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
}

.no-photo {
  color: var(--color-text-placeholder);
  font-size: 12px;
}

.btn-small {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  margin-right: 4px;
}

.btn-edit {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-delete {
  background: var(--color-danger);
  color: var(--color-bg-card);
}

.no-workers {
  text-align: center;
  padding: 40px;
  color: var(--color-text-placeholder);
  background: var(--color-bg-page);
  border-radius: 4px;
}

.add-worker-section {
  text-align: center;
}

.btn-add-worker {
  background: var(--color-bg-card);
  color: var(--color-primary);
  border: 1px dashed var(--color-primary);
  padding: 12px 24px;
}

.btn-add-worker:hover {
  background: var(--color-primary-subtle);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--color-border);
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-cancel {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-save {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-save:hover {
  background: var(--color-primary-dark);
}

.worker-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.worker-form-container {
  background: var(--color-bg-card);
  border-radius: 8px;
  width: 700px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
}

.worker-form-body {
  padding: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.form-row.id-card-photos {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.full-width {
  grid-column: span 2;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-regular);
}

.required {
  color: var(--color-danger);
  margin-right: 4px;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.error-msg {
  color: var(--color-danger);
  font-size: 12px;
}

.photo-upload-area {
  display: flex;
  gap: 12px;
}

.photo-preview {
  position: relative;
  width: 120px;
  height: 80px;
}

.photo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-danger);
  color: var(--color-bg-card);
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.upload-btn {
  width: 120px;
  height: 80px;
  border: 2px dashed #d0d7de;
  border-radius: 4px;
  background: var(--color-bg-page);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--color-text-secondary);
  font-size: 12px;
}

.upload-btn span:first-child {
  font-size: 24px;
}

.upload-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
