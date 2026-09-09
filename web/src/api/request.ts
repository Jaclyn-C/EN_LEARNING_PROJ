import axios from 'axios'

/**
 * 统一 axios 实例：全项目 HTTP 请求必须经 src/api/ 各模块复用此实例，
 * 组件内禁止裸调 fetch/axios，禁止硬编码后端地址。
 * baseURL 走 Vite 环境变量 VITE_API_BASE（.env.development / .env.production）。
 */
export const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  timeout: 15_000,
})

// 响应拦截器：统一错误出口（打日志后原样上抛，由调用方决定 UI 呈现）
request.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    const axiosError = axios.isAxiosError(error) ? error : null
    console.error(
      '[api]',
      axiosError?.config?.url ?? '(unknown url)',
      axiosError?.message ?? error,
    )
    return Promise.reject(error)
  },
)
