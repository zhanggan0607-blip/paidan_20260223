/* eslint-disable */
/* prettier-ignore */
// @ts-nocheck
export {}

declare module 'vue' {
  export interface GlobalComponents {
    ConfirmDialog: typeof import('./components/ConfirmDialog.vue')['default']
    Layout: typeof import('./components/Layout.vue')['default']
    RouterLink: typeof import('vue-router')['RouterLink']
    RouterView: typeof import('vue-router')['RouterView']
  }
}
