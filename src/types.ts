export interface ProjectInfo {
  id: string
  name: string
  completionDate: string
  maintenanceEndDate: string
  maintenancePeriod: string
  clientName: string
  address: string
}

export interface MenuItem {
  id: string
  label: string
  icon?: string
  children?: MenuItem[]
  path?: string
}

export interface FormField {
  key: keyof ProjectInfo
  label: string
  value: string
  inputType?: string
  editing: boolean
}
