import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MaintenancePlanSearchForm from './MaintenancePlanSearchForm.vue'

describe('MaintenancePlanSearchForm', () => {
  it('renders search inputs correctly', () => {
    const wrapper = mount(MaintenancePlanSearchForm, {
      props: {
        projectName: '',
        clientName: '',
      },
    })
    
    expect(wrapper.find('.search-section').exists()).toBe(true)
    expect(wrapper.findAll('.search-item').length).toBe(2)
  })

  it('displays project name input', () => {
    const wrapper = mount(MaintenancePlanSearchForm, {
      props: {
        projectName: '测试项目',
        clientName: '',
      },
    })
    
    const inputs = wrapper.findAll('input')
    expect(inputs.length).toBeGreaterThan(0)
  })

  it('emits add event when button clicked', async () => {
    const wrapper = mount(MaintenancePlanSearchForm, {
      props: {
        projectName: '',
        clientName: '',
      },
    })
    
    const addButton = wrapper.find('.btn-add')
    await addButton.trigger('click')
    expect(wrapper.emitted('add')).toBeTruthy()
  })
})
