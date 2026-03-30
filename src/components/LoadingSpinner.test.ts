import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

describe('LoadingSpinner', () => {
  it('renders properly', () => {
    const wrapper = mount(LoadingSpinner)
    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
  })

  it('displays loading text when provided', () => {
    const wrapper = mount(LoadingSpinner, {
      props: {
        text: '加载中...',
      },
    })
    expect(wrapper.text()).toContain('加载中')
  })
})
