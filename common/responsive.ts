import { ref, onMounted, onUnmounted, computed } from 'vue'

export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

export interface BreakpointConfig {
  xs: number
  sm: number
  md: number
  lg: number
  xl: number
}

const defaultBreakpoints: BreakpointConfig = {
  xs: 0,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200
}

const currentWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 0)
const currentHeight = ref(typeof window !== 'undefined' ? window.innerHeight : 0)

let resizeHandler: (() => void) | null = null
let listenerCount = 0

function handleResize() {
  currentWidth.value = window.innerWidth
  currentHeight.value = window.innerHeight
}

export function useBreakpoints(breakpoints: BreakpointConfig = defaultBreakpoints) {
  const setupListener = () => {
    if (listenerCount === 0) {
      resizeHandler = handleResize
      window.addEventListener('resize', resizeHandler)
    }
    listenerCount++
  }

  const cleanupListener = () => {
    listenerCount--
    if (listenerCount === 0 && resizeHandler) {
      window.removeEventListener('resize', resizeHandler)
      resizeHandler = null
    }
  }

  onMounted(setupListener)
  onUnmounted(cleanupListener)

  const current = computed<Breakpoint>(() => {
    const width = currentWidth.value
    if (width < breakpoints.sm) return 'xs'
    if (width < breakpoints.md) return 'sm'
    if (width < breakpoints.lg) return 'md'
    if (width < breakpoints.xl) return 'lg'
    return 'xl'
  })

  const isXs = computed(() => current.value === 'xs')
  const isSm = computed(() => current.value === 'sm')
  const isMd = computed(() => current.value === 'md')
  const isLg = computed(() => current.value === 'lg')
  const isXl = computed(() => current.value === 'xl')

  const isMobile = computed(() => ['xs', 'sm'].includes(current.value))
  const isTablet = computed(() => current.value === 'md')
  const isDesktop = computed(() => ['lg', 'xl'].includes(current.value))

  const isPortrait = computed(() => currentHeight.value > currentWidth.value)
  const isLandscape = computed(() => currentWidth.value > currentHeight.value)

  const up = (breakpoint: Breakpoint): boolean => {
    const order: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl']
    return order.indexOf(current.value) >= order.indexOf(breakpoint)
  }

  const down = (breakpoint: Breakpoint): boolean => {
    const order: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl']
    return order.indexOf(current.value) <= order.indexOf(breakpoint)
  }

  return {
    width: currentWidth,
    height: currentHeight,
    current,
    isXs,
    isSm,
    isMd,
    isLg,
    isXl,
    isMobile,
    isTablet,
    isDesktop,
    isPortrait,
    isLandscape,
    up,
    down
  }
}

export function useMediaQuery(query: string) {
  const matches = ref(false)

  const checkMedia = () => {
    if (typeof window !== 'undefined') {
      matches.value = window.matchMedia(query).matches
    }
  }

  onMounted(() => {
    checkMedia()
    const mediaQueryList = window.matchMedia(query)
    const handler = (e: MediaQueryListEvent) => {
      matches.value = e.matches
    }
    mediaQueryList.addEventListener('change', handler)
  })

  return matches
}

export function useTouchDevice() {
  const isTouchDevice = ref(false)

  onMounted(() => {
    isTouchDevice.value = 'ontouchstart' in window || navigator.maxTouchPoints > 0
  })

  return isTouchDevice
}

export function useSafeArea() {
  const safeAreaTop = ref(0)
  const safeAreaBottom = ref(0)
  const safeAreaLeft = ref(0)
  const safeAreaRight = ref(0)

  const updateSafeArea = () => {
    const computedStyle = getComputedStyle(document.documentElement)
    
    safeAreaTop.value = parseInt(computedStyle.getPropertyValue('--sat') || '0', 10)
    safeAreaBottom.value = parseInt(computedStyle.getPropertyValue('--sab') || '0', 10)
    safeAreaLeft.value = parseInt(computedStyle.getPropertyValue('--sal') || '0', 10)
    safeAreaRight.value = parseInt(computedStyle.getPropertyValue('--sar') || '0', 10)
  }

  onMounted(() => {
    updateSafeArea()
    window.addEventListener('resize', updateSafeArea)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateSafeArea)
  })

  return {
    safeAreaTop,
    safeAreaBottom,
    safeAreaLeft,
    safeAreaRight
  }
}