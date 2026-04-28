/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_DINGTALK_CLIENT_ID: string
  readonly DEV: boolean
  readonly PROD: boolean
  readonly MODE: string
}

interface ScreenOrientation {
  lock(orientation: OrientationLockType): Promise<void>
  unlock(): void
  type: OrientationType
  onchange: EventListener
}

interface Screen {
  orientation: ScreenOrientation
  lockOrientation(orientation: string): boolean
  mozLockOrientation(orientation: string): boolean
  msLockOrientation(orientation: string): boolean
  unlockOrientation(): void
  mozUnlockOrientation(): void
  msUnlockOrientation(): void
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
