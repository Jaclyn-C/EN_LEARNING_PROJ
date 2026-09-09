/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 后端 API 基地址（.env.development / .env.production），禁止在代码里硬编码 */
  readonly VITE_API_BASE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
