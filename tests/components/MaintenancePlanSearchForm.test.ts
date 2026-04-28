import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import MaintenancePlanSearchForm from '@/components/maintenance/MaintenancePlanSearchForm.vue'

describe('MaintenancePlanSearchForm', () => {
  it('renders correctly', () => {
    const wrapper = mount(MaintenancePlanSearchForm, {
      props: {
        projectName: '',
        clientName: '',
      },
    })
    expect(wrapper.find('.search-section').exists()).toBe(true)
  })

  it('emits search event when input changes', async () => {
    const wrapper = mount(MaintenancePlanSearchForm, {
      props: {
        projectName: '',
        clientName: '',
      },
    })
    
    const input = wrapper.find('input')
    await input.setValue('test project')
    
    expect(wrapper.emitted('update:projectName')).toBeTruthy()
    expect(wrapper.emitted('update:projectName')![0]).toEqual(['test project'])
  })

  it('emits add event when button clicked', async () => {
    const wrapper = mount(MaintenancePlanSearchForm, {
      props: {
        projectName: '',
        clientName: '',
      },
    })
    
    await wrapper.find('.btn-add').trigger('click')
    expect(wrapper.emitted('add')).toBeTruthy()
  })
})
