/**
 * Service 工厂函数
 * 用于生成基础的 CRUD service，减少 PC 端和 H5 端的重复代码
 */

export interface BaseServiceOptions {
  endpoints: {
    LIST: string
    DETAIL: (id: number) => string
    ALL?: string
  }
  request: {
    get: (url: string, config?: any) => Promise<any>
    post: (url: string, data?: any, config?: any) => Promise<any>
    put: (url: string, data?: any, config?: any) => Promise<any>
    patch: (url: string, data?: any, config?: any) => Promise<any>
    delete: (url: string, config?: any) => Promise<any>
  }
}

export interface PaginatedParams {
  page?: number
  size?: number
  [key: string]: any
}

export function createBaseService<T, CreateDTO = Partial<T>, UpdateDTO = Partial<T>>(
  options: BaseServiceOptions
) {
  const { endpoints, request } = options

  return {
    async getList(params?: PaginatedParams) {
      return await request.get(endpoints.LIST, { params })
    },

    async getAll() {
      if (!endpoints.ALL) {
        throw new Error('ALL endpoint is not defined')
      }
      return await request.get(endpoints.ALL)
    },

    async getById(id: number) {
      return await request.get(endpoints.DETAIL(id))
    },

    async create(data: CreateDTO) {
      return await request.post(endpoints.LIST, data)
    },

    async update(id: number, data: UpdateDTO) {
      return await request.put(endpoints.DETAIL(id), data)
    },

    async patch(id: number, data: Partial<UpdateDTO>) {
      return await request.patch(endpoints.DETAIL(id), data)
    },

    async delete(id: number) {
      return await request.delete(endpoints.DETAIL(id))
    },
  }
}

export function createSubmitApproveService<T, UpdateDTO = Partial<T>>(
  baseService: ReturnType<typeof createBaseService<T, any, UpdateDTO>>,
  endpoints: {
    SUBMIT: (id: number) => string
    APPROVE: (id: number) => string
  },
  request: BaseServiceOptions['request']
) {
  return {
    ...baseService,

    async submit(id: number) {
      return await request.post(endpoints.SUBMIT(id))
    },

    async approve(id: number, approved: boolean, rejectReason?: string) {
      return await request.post(endpoints.APPROVE(id), {
        approved,
        reject_reason: rejectReason,
      })
    },
  }
}
