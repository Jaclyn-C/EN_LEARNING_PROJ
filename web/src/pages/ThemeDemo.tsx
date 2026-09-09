import { useCallback, useEffect, useState } from 'react'
import { Button, Input, Select, Switch, Tag } from 'antd'
import { ThemeSwitcher } from '../components/ThemeSwitcher'
import { checkHealth } from '../api/health'
import type { HealthResponse } from '../api/health'

/** accent 底/文字组合的 antd Tag 样式（引用 --enl-* 变量 → 轨道 2 生效） */
const accentTagStyle = (group: 'info' | 'purple' | 'success' | 'error') => ({
  background: `var(--enl-accent-${group}-bg)`,
  color: `var(--enl-accent-${group}-text)`,
  border: 'none',
  fontSize: 13,
  paddingInline: 10,
  paddingBlock: 3,
  borderRadius: 8,
})

type HealthPhase = 'checking' | 'ok' | 'down'

/** 后端连通卡片：调 /api/health，请求失败只改状态不算页面错误 */
function HealthCard() {
  const [phase, setPhase] = useState<HealthPhase>('checking')
  const [detail, setDetail] = useState<string>('')

  /** 发起检查；setState 都发生在异步回调里（effect 体内不同步 setState） */
  const performCheck = useCallback(() => {
    return checkHealth()
      .then((data: HealthResponse) => {
        setPhase('ok')
        setDetail(`GET ${import.meta.env.VITE_API_BASE ?? ''}/health → 200 ${JSON.stringify(data)}`)
      })
      .catch((err: unknown) => {
        setPhase('down')
        const message = err instanceof Error ? err.message : String(err)
        setDetail(`连接失败：${message}`)
      })
  }, [])

  const handleRetry = () => {
    setPhase('checking')
    setDetail('')
    void performCheck()
  }

  useEffect(() => {
    void performCheck()
  }, [performCheck])

  return (
    <section className="rounded-card bg-white p-6 shadow-card md:col-span-2">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-medium text-text-strong">后端连通</h2>
          <p className="mt-1 text-sm text-text-secondary">GET /api/health</p>
        </div>
        <div className="flex items-center gap-3">
          {phase === 'ok' && (
            <Tag style={accentTagStyle('success')}>后端已连接</Tag>
          )}
          {phase === 'down' && (
            <Tag style={accentTagStyle('error')}>后端未启动</Tag>
          )}
          {phase === 'checking' && (
            <Tag style={accentTagStyle('info')}>检测中…</Tag>
          )}
          <Button size="small" onClick={handleRetry}>
            重新检测
          </Button>
        </div>
      </div>
      <p className="mt-3 font-mono text-xs break-all text-text-secondary">
        {detail || '正在请求…'}
      </p>
    </section>
  )
}

/** M0 演示页：双轨主题（AntD token + --enl-* CSS 变量）效果验收 */
export default function ThemeDemo() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-strong">EN-learning</h1>
          <p className="mt-1 text-sm text-text-secondary">
            莫兰迪主题演示页 · 点右上角色点切换三套主题
          </p>
        </div>
        <ThemeSwitcher />
      </header>

      <main className="grid gap-6 md:grid-cols-2">
        {/* 1. 按钮组：主 CTA 胶囊 999px，次按钮随 token 12px */}
        <section className="rounded-card bg-white p-6 shadow-card">
          <h2 className="text-base font-medium text-text-strong">按钮</h2>
          <p className="mt-1 mb-4 text-sm text-text-secondary">
            主 CTA 胶囊圆角（999px），次按钮随控件 12px
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Button type="primary" size="large" style={{ borderRadius: 999 }}>
              开始练习
            </Button>
            <Button>保存草稿</Button>
            <Button type="text">稍后再说</Button>
          </div>
        </section>

        {/* 2. 表单：Input / Select / Switch */}
        <section className="rounded-card bg-white p-6 shadow-card">
          <h2 className="text-base font-medium text-text-strong">表单</h2>
          <p className="mt-1 mb-4 text-sm text-text-secondary">输入框与选项 12px 圆角</p>
          <div className="w-full max-w-xs space-y-4">
            <label className="block">
              <span className="mb-1 block text-sm text-text-secondary">关键词</span>
              <Input allowClear placeholder="划词查一查，如 morandi" />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm text-text-secondary">题型</span>
              <Select
                className="w-full"
                defaultValue="single"
                options={[
                  { value: 'single', label: '单选题' },
                  { value: 'blank', label: '填空题' },
                  { value: 'judge', label: '判断题' },
                ]}
              />
            </label>
            <div className="flex items-center gap-3">
              <Switch defaultChecked />
              <span className="text-sm text-text-strong">自动加入生词本</span>
            </div>
          </div>
        </section>

        {/* 3. 题型标签：三个 accent 底/文字组合轮换 */}
        <section className="rounded-card bg-white p-6 shadow-card">
          <h2 className="text-base font-medium text-text-strong">题型标签</h2>
          <p className="mt-1 mb-4 text-sm text-text-secondary">
            三个 accent 的底色/文字组合轮换（随主题换色）
          </p>
          <div className="flex flex-wrap gap-2">
            <Tag style={accentTagStyle('info')}>单选</Tag>
            <Tag style={accentTagStyle('purple')}>填空</Tag>
            <Tag style={accentTagStyle('success')}>判断</Tag>
          </div>
        </section>

        {/* 4. 错误与正确示例：灰玫/灰粉/灰杏，绝不用高饱和红 */}
        <section className="rounded-card bg-white p-6 shadow-card">
          <h2 className="text-base font-medium text-text-strong">反馈态</h2>
          <p className="mt-1 mb-4 text-sm text-text-secondary">
            错误用灰玫/灰粉/灰杏系，成功用灰绿/奶咖系（Tailwind 引用变量）
          </p>
          <div className="space-y-3">
            <div className="rounded-ctl bg-accent-error-bg px-4 py-3 text-sm text-accent-error-text">
              ✗ 回答有误 · 正确答案是 B。错误态用低饱和灰玫色，保住莫兰迪质感。
            </div>
            <div className="rounded-ctl bg-accent-success-bg px-4 py-3 text-sm text-accent-success-text">
              ✓ 回答正确 · 已收入错题本，明天复习。
            </div>
          </div>
        </section>

        {/* 5. 后端连通卡片 */}
        <HealthCard />
      </main>

      <footer className="mt-8 text-center text-xs text-text-secondary">
        色板单一事实来源：src/theme/palettes.ts · 双轨注入：AntD ConfigProvider token + --enl-* CSS 变量
      </footer>
    </div>
  )
}
