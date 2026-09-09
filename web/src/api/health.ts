import { request } from './request'

/** GET /api/health 响应体 */
export interface HealthResponse {
  status: string
}

/** 后端连通性检查：成功返回响应体，失败（网络错误/非 2xx）抛错由调用方捕获 */
export async function checkHealth(): Promise<HealthResponse> {
  const { data } = await request.get<HealthResponse>('/health')
  return data
}
