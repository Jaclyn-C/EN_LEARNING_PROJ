# 莫兰迪紫主题系统实现计划（M0 前端脚手架·视觉部分）

> **执行状态（2026-09-04）：待执行——尚未开始任何 Task，git 未初始化，无任何提交。**
> 用户已要求**暂不提交任何代码**；开始执行前先与用户确认 git 提交策略（Task 1 的 git init 及各 Task 的提交步骤需用户点头再做）。
> 规格已获用户逐项确认：`docs/superpowers/specs/2026-09-04-morandi-theme-design.md`。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零创建 `web/` 前端工程，落地莫兰迪紫三主题系统（iris/mist/mauve，默认 iris，运行时可切换）+ 演示页。

**Architecture:** TS 色板对象为单一事实来源（`src/theme/palettes.ts`），双轨注入：AntD `ConfigProvider` token（轨道 1，全组件树变色）+ 根节点语义化 CSS 变量（轨道 2，Tailwind v4 `@theme` 引用变量）；zustand persist 持久化到 localStorage。

**Tech Stack:** React 18（**必须 18，模板默认 19 需降级**）+ Vite + TypeScript + Ant Design 5 + Tailwind CSS v4（`@tailwindcss/vite`，CSS-first 配置）+ zustand v5 + Vitest + @testing-library/react。

**规格来源:** `docs/superpowers/specs/2026-09-04-morandi-theme-design.md`（色值以此为准，实现中的两处细化：① mist/mauve 的 purple 标签色补齐具体值；② 阴影拆为 `shadowCard`/`shadowBtn` 两个完整值令牌，按钮阴影透明度用 .30）。

**工程纪律:** 包管理一律 pnpm；提交信息 `type(scope): 中文描述`，scope 用 `web`；禁止提交 `.env`/`node_modules`/`dist`/`.superpowers/`。

---

### Task 1: Git 初始化与根 .gitignore

**Files:**
- Create: `.gitignore`（仓库根）

- [ ] **Step 1: 初始化 git 仓库**

```bash
cd /Users/jaclyn/Desktop/ESG-proj/EN-learning && git init
```

Expected: `Initialized empty Git repository ...`

- [ ] **Step 2: 写根 .gitignore**

```gitignore
# 密钥与本地配置
.env
.claude/settings.local.json

# 前端
node_modules/
dist/

# 后端
__pycache__/
.venv/
*.db
server/uploads/

# 工具产物
.superpowers/
.DS_Store
```

- [ ] **Step 3: 首次提交（文档 + Agent 配置）**

```bash
git add .gitignore CLAUDE.md README.md docs/ .claude/
git commit -m "chore: 初始化仓库（总规则、方案文档与 Agent 配置）"
```

Expected: 提交成功。若因缺少 git 用户身份失败，停下来问用户，不要擅自改 global 配置。

---

### Task 2: Vite 脚手架 + 依赖 + 测试环境

**Files:**
- Create: `web/`（Vite react-ts 模板生成）
- Modify: `web/package.json`（scripts 加 test）、`web/vite.config.ts`、删除模板演示代码

- [ ] **Step 1: 生成脚手架并装依赖**

```bash
pnpm create vite web --template react-ts
cd web && pnpm install
```

- [ ] **Step 2: React 降级到 18（CLAUDE.md 规定 React 18，模板默认 19）**

```bash
pnpm add react@18 react-dom@18 antd zustand
pnpm add -D @types/react@18 @types/react-dom@18 tailwindcss @tailwindcss/vite vitest jsdom @testing-library/react
```

Expected: package.json 中 react 为 ^18.x。

- [ ] **Step 3: 改 vite.config.ts（tailwind 插件 + vitest 配置）**

```ts
/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: { '/api': 'http://localhost:8000' },
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
```

- [ ] **Step 4: 写测试 setup（AntD 在 jsdom 下需要 matchMedia）**

Create `web/src/test/setup.ts`:

```ts
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
})
```

- [ ] **Step 5: package.json scripts 加 `"test": "vitest run"`**（与既有 build/lint 平级）

- [ ] **Step 6: 清理模板演示代码**

删除 `src/App.css`、`src/assets/react.svg`；`src/index.css` 与 `src/App.tsx` 会被后续任务整体重写，此处先清空为占位：

`src/App.tsx`:
```tsx
function App() {
  return <div>EN-learning</div>
}
export default App
```

`src/index.css`: 清空为空文件（Task 7 会整体重写）。

- [ ] **Step 7: 验证三件套**

```bash
pnpm lint && pnpm test && pnpm build
```

Expected: 三项全过（视觉效果的浏览器检查统一放在 Task 7 Step 5，此处不起 dev 服务器）。

- [ ] **Step 8: 提交**

```bash
git add web/ && git commit -m "feat(web): Vite+TS 脚手架，React 18 + AntD5 + Tailwind v4 + Vitest"
```

---

> **执行目录说明：** Task 3-8 的所有命令与相对路径均在 `web/` 目录下执行（Task 2 已 `cd web`）。

### Task 3: 色板定义 palettes.ts

**Files:**
- Create: `web/src/theme/palettes.ts`
- Test: `web/src/theme/palettes.test.ts`

- [ ] **Step 1: 写失败测试**

```ts
import { describe, expect, it } from 'vitest'
import { DEFAULT_THEME, PALETTES, THEME_IDS, normalizeThemeId } from './palettes'

describe('palettes', () => {
  it('包含且仅包含三套主题', () => {
    expect(THEME_IDS.sort()).toEqual(['iris', 'mauve', 'mist'])
  })

  it('默认主题是 iris', () => {
    expect(DEFAULT_THEME).toBe('iris')
  })

  it('每套色板字段完整且为合法 hex 色', () => {
    const hex = /^#[0-9A-Fa-f]{6}$/
    for (const id of THEME_IDS) {
      const p = PALETTES[id]
      expect(p.id).toBe(id)
      expect(p.name).toBeTruthy()
      for (const key of ['primary', 'primaryDeep', 'textStrong', 'textSecondary', 'bgFrom', 'bgTo'] as const) {
        expect(p[key]).toMatch(hex)
      }
      for (const a of ['info', 'purple', 'success', 'error'] as const) {
        expect(p.accent[a].bg).toMatch(hex)
        expect(p.accent[a].text).toMatch(hex)
      }
      expect(p.shadowCard).toMatch(/^0 8px 24px /)
      expect(p.shadowBtn).toMatch(/^0 4px 12px /)
    }
  })

  it('normalizeThemeId：合法值原样返回，非法值回落 iris', () => {
    expect(normalizeThemeId('mauve')).toBe('mauve')
    expect(normalizeThemeId('nope')).toBe('iris')
    expect(normalizeThemeId(undefined)).toBe('iris')
    expect(normalizeThemeId(42)).toBe('iris')
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm test`
Expected: FAIL，`Failed to resolve import "./palettes"`

- [ ] **Step 3: 实现 palettes.ts**

```ts
export type ThemeId = 'iris' | 'mist' | 'mauve'

export interface AccentColor {
  bg: string
  text: string
}

export interface Palette {
  id: ThemeId
  name: string
  primary: string
  primaryDeep: string
  textStrong: string
  textSecondary: string
  bgFrom: string
  bgTo: string
  accent: { info: AccentColor; purple: AccentColor; success: AccentColor; error: AccentColor }
  shadowCard: string
  shadowBtn: string
}

export const PALETTES: Record<ThemeId, Palette> = {
  iris: {
    id: 'iris',
    name: '鸢尾蓝紫',
    primary: '#7D7FA8',
    primaryDeep: '#66688F',
    textStrong: '#3E4157',
    textSecondary: '#82859B',
    bgFrom: '#F5F6FA',
    bgTo: '#EDECF4',
    accent: {
      info: { bg: '#D7DDEA', text: '#66738F' },
      purple: { bg: '#DDD8E8', text: '#76708C' },
      success: { bg: '#D6DDD3', text: '#6F8170' },
      error: { bg: '#E3CFD6', text: '#8F7080' },
    },
    shadowCard: '0 8px 24px rgba(125,127,168,.12)',
    shadowBtn: '0 4px 12px rgba(125,127,168,.30)',
  },
  mist: {
    id: 'mist',
    name: '雾紫奶油',
    primary: '#9F8BB8',
    primaryDeep: '#8672A0',
    textStrong: '#4B4256',
    textSecondary: '#8B8296',
    bgFrom: '#FAF7F2',
    bgTo: '#F2EEF6',
    accent: {
      info: { bg: '#AEB9C9', text: '#6D7A8C' },
      purple: { bg: '#EFE9F4', text: '#7C6995' },
      success: { bg: '#C6CCB9', text: '#77805F' },
      error: { bg: '#E3C9CE', text: '#9A6E77' },
    },
    shadowCard: '0 8px 24px rgba(159,139,184,.12)',
    shadowBtn: '0 4px 12px rgba(159,139,184,.30)',
  },
  mauve: {
    id: 'mauve',
    name: '藕紫奶茶',
    primary: '#AC8DA5',
    primaryDeep: '#96758F',
    textStrong: '#524A4E',
    textSecondary: '#94898E',
    bgFrom: '#FAF6F2',
    bgTo: '#F4ECEA',
    accent: {
      info: { bg: '#C9D2DA', text: '#77889A' },
      purple: { bg: '#F0E7EE', text: '#93708A' },
      success: { bg: '#E5D3B8', text: '#9C7F5B' },
      error: { bg: '#E8CFC4', text: '#A57F6F' },
    },
    shadowCard: '0 8px 24px rgba(172,141,165,.12)',
    shadowBtn: '0 4px 12px rgba(172,141,165,.30)',
  },
}

export const DEFAULT_THEME: ThemeId = 'iris'

export const THEME_IDS = Object.keys(PALETTES) as ThemeId[]

export function normalizeThemeId(v: unknown): ThemeId {
  return typeof v === 'string' && v in PALETTES ? (v as ThemeId) : DEFAULT_THEME
}
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm test`
Expected: PASS（4 个用例）

- [ ] **Step 5: 提交**

```bash
git add src/theme/ && git commit -m "feat(web): 莫兰迪紫三套色板定义（iris/mist/mauve）"
```

---

### Task 4: 主题状态 stores/theme.ts

**Files:**
- Create: `web/src/stores/theme.ts`
- Test: `web/src/stores/theme.test.ts`

- [ ] **Step 1: 写失败测试**

```ts
import { afterEach, describe, expect, it } from 'vitest'
import { useThemeStore } from './theme'

afterEach(() => {
  useThemeStore.setState({ themeId: 'iris' })
  localStorage.clear()
})

describe('theme store', () => {
  it('默认主题 iris', () => {
    expect(useThemeStore.getState().themeId).toBe('iris')
  })

  it('setTheme 切换合法主题', () => {
    useThemeStore.getState().setTheme('mauve')
    expect(useThemeStore.getState().themeId).toBe('mauve')
  })

  it('setTheme 收到非法值回落 iris', () => {
    useThemeStore.getState().setTheme('hacker' as never)
    expect(useThemeStore.getState().themeId).toBe('iris')
  })

  it('persist 写入 localStorage（key=enl-theme）', () => {
    useThemeStore.getState().setTheme('mist')
    expect(localStorage.getItem('enl-theme')).toContain('"themeId":"mist"')
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm test`
Expected: FAIL，`Failed to resolve import "./theme"`

- [ ] **Step 3: 实现 stores/theme.ts**

```ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { DEFAULT_THEME, normalizeThemeId, type ThemeId } from '../theme/palettes'

interface ThemeState {
  themeId: ThemeId
  setTheme: (id: ThemeId) => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      themeId: DEFAULT_THEME,
      setTheme: (id) => set({ themeId: normalizeThemeId(id) }),
    }),
    {
      name: 'enl-theme',
      merge: (persisted, current) => ({
        ...current,
        themeId: normalizeThemeId((persisted as { themeId?: unknown })?.themeId),
      }),
    },
  ),
)
```

> `merge` 是 localStorage 损坏/非法值的兜底：无论持久化了什么，都经 `normalizeThemeId` 校验，保底 iris。

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm test`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add src/stores/ && git commit -m "feat(web): 主题状态 store（zustand persist，非法值回落 iris）"
```

---

### Task 5: CSS 变量生成 theme/cssVariables.ts

**Files:**
- Create: `web/src/theme/cssVariables.ts`
- Test: `web/src/theme/cssVariables.test.ts`

- [ ] **Step 1: 写失败测试**

```ts
import { afterEach, describe, expect, it } from 'vitest'
import { PALETTES } from './palettes'
import { applyTheme, toCssVariables } from './cssVariables'

afterEach(() => {
  document.documentElement.removeAttribute('style')
  delete document.documentElement.dataset.theme
})

describe('toCssVariables', () => {
  it('iris 色板生成完整 --enl-* 变量', () => {
    const vars = toCssVariables(PALETTES.iris)
    expect(vars['--enl-primary']).toBe('#7D7FA8')
    expect(vars['--enl-primary-deep']).toBe('#66688F')
    expect(vars['--enl-bg-from']).toBe('#F5F6FA')
    expect(vars['--enl-accent-error-bg']).toBe('#E3CFD6')
    expect(vars['--enl-radius-card']).toBe('18px')
    expect(vars['--enl-radius-ctl']).toBe('12px')
    expect(Object.keys(vars).filter((k) => k.startsWith('--enl-'))).toHaveLength(18)
  })
})

describe('applyTheme', () => {
  it('把变量写到 documentElement 并设置 data-theme', () => {
    applyTheme(PALETTES.mauve)
    const root = document.documentElement
    expect(root.dataset.theme).toBe('mauve')
    expect(root.style.getPropertyValue('--enl-primary')).toBe('#AC8DA5')
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm test`
Expected: FAIL，`Failed to resolve import "./cssVariables"`

- [ ] **Step 3: 实现 cssVariables.ts**

```ts
import type { Palette } from './palettes'

const RADIUS_CARD = '18px'
const RADIUS_CTL = '12px'

export function toCssVariables(p: Palette): Record<string, string> {
  return {
    '--enl-primary': p.primary,
    '--enl-primary-deep': p.primaryDeep,
    '--enl-text-strong': p.textStrong,
    '--enl-text-secondary': p.textSecondary,
    '--enl-bg-from': p.bgFrom,
    '--enl-bg-to': p.bgTo,
    '--enl-accent-info-bg': p.accent.info.bg,
    '--enl-accent-info-text': p.accent.info.text,
    '--enl-accent-purple-bg': p.accent.purple.bg,
    '--enl-accent-purple-text': p.accent.purple.text,
    '--enl-accent-success-bg': p.accent.success.bg,
    '--enl-accent-success-text': p.accent.success.text,
    '--enl-accent-error-bg': p.accent.error.bg,
    '--enl-accent-error-text': p.accent.error.text,
    '--enl-shadow-card': p.shadowCard,
    '--enl-shadow-btn': p.shadowBtn,
    '--enl-radius-card': RADIUS_CARD,
    '--enl-radius-ctl': RADIUS_CTL,
  }
}

export function applyTheme(p: Palette): void {
  const root = document.documentElement
  for (const [key, value] of Object.entries(toCssVariables(p))) {
    root.style.setProperty(key, value)
  }
  root.dataset.theme = p.id
}
```

> 变量按语义命名（primary/success/error…）而非字面色名——这是深色模式的预留口子（规格 §6）：未来加 `[data-theme-dark]` 变量覆盖组即可，业务代码零改动。

- [ ] **Step 4: 跑测试确认通过**

Run: `pnpm test`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add src/theme/cssVariables.ts src/theme/cssVariables.test.ts && git commit -m "feat(web): 色板→语义 CSS 变量生成与应用（深色模式预留口）"
```

---

### Task 6: ThemeProvider 双轨注入 + main.tsx 接线

**Files:**
- Create: `web/src/theme/ThemeProvider.tsx`
- Modify: `web/src/main.tsx`
- Test: `web/src/theme/ThemeProvider.test.tsx`

- [ ] **Step 1: 写失败测试**

```tsx
import { cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { ThemeProvider } from './ThemeProvider'
import { useThemeStore } from '../stores/theme'

afterEach(() => {
  cleanup()
  useThemeStore.setState({ themeId: 'iris' })
  localStorage.clear()
})

describe('ThemeProvider', () => {
  it('渲染 children 并在根节点注入默认主题变量', () => {
    const { getByText } = render(
      <ThemeProvider>
        <div>hello</div>
      </ThemeProvider>,
    )
    expect(getByText('hello')).toBeTruthy()
    expect(document.documentElement.dataset.theme).toBe('iris')
    expect(document.documentElement.style.getPropertyValue('--enl-primary')).toBe('#7D7FA8')
  })

  it('store 切换后 data-theme 与变量跟随变化', () => {
    render(
      <ThemeProvider>
        <div>x</div>
      </ThemeProvider>,
    )
    useThemeStore.getState().setTheme('mist')
    expect(document.documentElement.dataset.theme).toBe('mist')
    expect(document.documentElement.style.getPropertyValue('--enl-primary')).toBe('#9F8BB8')
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `pnpm test`
Expected: FAIL，`Failed to resolve import "./ThemeProvider"`

- [ ] **Step 3: 实现 ThemeProvider.tsx**

```tsx
import { ConfigProvider } from 'antd'
import { useEffect, type ReactNode } from 'react'
import { PALETTES } from './palettes'
import { applyTheme } from './cssVariables'
import { useThemeStore } from '../stores/theme'

const FONT_STACK =
  "-apple-system, 'PingFang SC', 'HarmonyOS Sans SC', 'MiSans', 'Segoe UI', sans-serif"

export function ThemeProvider({ children }: { children: ReactNode }) {
  const themeId = useThemeStore((s) => s.themeId)
  const palette = PALETTES[themeId]

  useEffect(() => {
    applyTheme(palette)
  }, [palette])

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: palette.primary,
          colorInfo: palette.primary,
          colorLink: palette.primaryDeep,
          colorText: palette.textStrong,
          colorTextSecondary: palette.textSecondary,
          colorTextTertiary: palette.textSecondary,
          borderRadius: 12,
          borderRadiusLG: 18,
          fontFamily: FONT_STACK,
          boxShadowSecondary: palette.shadowCard,
        },
      }}
    >
      {children}
    </ConfigProvider>
  )
}
```

- [ ] **Step 4: 改 main.tsx 接线**

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'
import { ThemeProvider } from './theme/ThemeProvider'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </StrictMode>,
)
```

- [ ] **Step 5: 跑全部测试确认通过**

Run: `pnpm test`
Expected: PASS（含此前所有用例）

- [ ] **Step 6: 提交**

```bash
git add src/theme/ThemeProvider.tsx src/theme/ThemeProvider.test.tsx src/main.tsx && git commit -m "feat(web): ThemeProvider 双轨注入（AntD token + CSS 变量）"
```

---

### Task 7: Tailwind 主题映射 + 切换器 + 演示页

**Files:**
- Modify: `web/src/index.css`（整体重写）
- Create: `web/src/components/ThemeSwitcher.tsx`
- Modify: `web/src/App.tsx`（整体重写为演示页）

- [ ] **Step 1: 重写 index.css（Tailwind v4 @theme 引用运行时变量）**

```css
@import 'tailwindcss';

@theme {
  --color-primary: var(--enl-primary);
  --color-primary-deep: var(--enl-primary-deep);
  --color-text-strong: var(--enl-text-strong);
  --color-text-secondary: var(--enl-text-secondary);
  --color-accent-info-bg: var(--enl-accent-info-bg);
  --color-accent-info-text: var(--enl-accent-info-text);
  --color-accent-purple-bg: var(--enl-accent-purple-bg);
  --color-accent-purple-text: var(--enl-accent-purple-text);
  --color-accent-success-bg: var(--enl-accent-success-bg);
  --color-accent-success-text: var(--enl-accent-success-text);
  --color-accent-error-bg: var(--enl-accent-error-bg);
  --color-accent-error-text: var(--enl-accent-error-text);
  --radius-card: var(--enl-radius-card);
  --radius-ctl: var(--enl-radius-ctl);
  --shadow-card: var(--enl-shadow-card);
  --shadow-btn: var(--enl-shadow-btn);
}

body {
  font-family:
    -apple-system, 'PingFang SC', 'HarmonyOS Sans SC', 'MiSans', 'Segoe UI', sans-serif;
  color: var(--enl-text-strong);
  background: linear-gradient(135deg, var(--enl-bg-from), var(--enl-bg-to)) fixed;
  min-height: 100vh;
}
```

> 由此生成的工具类：`bg-primary`、`text-primary-deep`、`rounded-card`、`shadow-card` 等，全部运行时读 CSS 变量，换主题零重编译。自定义组件**禁止写死色值**（规格 §4）。

- [ ] **Step 2: 实现 ThemeSwitcher.tsx**

```tsx
import { Tooltip } from 'antd'
import { PALETTES, THEME_IDS } from '../theme/palettes'
import { useThemeStore } from '../stores/theme'

export function ThemeSwitcher() {
  const themeId = useThemeStore((s) => s.themeId)
  const setTheme = useThemeStore((s) => s.setTheme)

  return (
    <div className="flex items-center gap-2">
      {THEME_IDS.map((id) => {
        const p = PALETTES[id]
        const active = id === themeId
        return (
          <Tooltip key={id} title={p.name}>
            <button
              type="button"
              aria-label={`切换主题：${p.name}`}
              aria-pressed={active}
              onClick={() => setTheme(id)}
              className="h-5 w-5 cursor-pointer rounded-full transition-transform hover:scale-110"
              style={{
                background: p.primary,
                boxShadow: active ? `0 0 0 2px #fff, 0 0 0 4px ${p.primaryDeep}` : 'none',
              }}
            />
          </Tooltip>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 3: 重写 App.tsx 为演示页**

要求覆盖两条轨道的组件样例，页面结构：

```tsx
import { Button, Input, Segmented, Select, Tag } from 'antd'
import { ThemeSwitcher } from './components/ThemeSwitcher'

function App() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-primary shadow-btn" />
          <h1 className="text-xl font-semibold text-text-strong">EN-learning</h1>
        </div>
        <ThemeSwitcher />
      </header>

      <section className="mb-6 rounded-card bg-white p-6 shadow-card">
        <h2 className="mb-4 text-base font-semibold text-text-strong">AntD 组件（轨道 1）</h2>
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <Button type="primary">主要按钮</Button>
          <Button type="primary" className="rounded-full!">
            胶囊 CTA
          </Button>
          <Button>默认按钮</Button>
        </div>
        <div className="mb-4 flex flex-wrap gap-3">
          <Input placeholder="输入框（圆角 12）" className="w-56" />
          <Select placeholder="选择器" className="w-40" options={[{ value: 1, label: '选项一' }]} />
          <Segmented options={['单选', '填空', '判断']} />
        </div>
        <div className="flex flex-wrap gap-2">
          <Tag color="processing">单选</Tag>
          <Tag>来源 P2</Tag>
          <span className="rounded-full bg-accent-success-bg px-2.5 py-0.5 text-xs text-accent-success-text">
            答对
          </span>
          <span className="rounded-full bg-accent-error-bg px-2.5 py-0.5 text-xs text-accent-error-text">
            答错（灰玫，非艳红）
          </span>
        </div>
      </section>

      <section className="rounded-card bg-white p-6 shadow-card">
        <h2 className="mb-4 text-base font-semibold text-text-strong">
          自定义题目卡（轨道 2 · Tailwind）
        </h2>
        <p className="mb-3 text-sm text-text-secondary">单选 · 第 3 题 · 来源 P2</p>
        <p className="mb-4 leading-relaxed text-text-strong">
          The word "ubiquitous" in paragraph 2 is closest in meaning to…
        </p>
        <div className="space-y-2">
          <div className="rounded-ctl bg-accent-info-bg px-4 py-2 text-sm text-accent-info-text">
            A. everywhere
          </div>
          <div className="rounded-ctl bg-primary px-4 py-2 text-sm text-white">B. rare（选中态）</div>
          <div className="rounded-ctl bg-accent-purple-bg px-4 py-2 text-sm text-accent-purple-text">
            C. hidden
          </div>
        </div>
      </section>
    </div>
  )
}

export default App
```

- [ ] **Step 4: lint + build + 全部测试**

```bash
pnpm lint && pnpm test && pnpm build
```

Expected: 三项全过。

- [ ] **Step 5: 手动验收（对照规格 §7）**

```bash
pnpm dev
```

打开 http://localhost:5173 逐项检查：
1. 默认 iris（鸢尾蓝紫）；点三个色点切换，**AntD 按钮和自定义卡片全部即时变色**，无刷新
2. 切到 mist/mauve 后刷新页面，主题保持
3. 错误态标签是灰粉/灰玫，无高饱和红
4. DevTools → Application → Local Storage 手动把 `enl-theme` 改成 `{"themeId":"xxx"}` 再刷新 → 回落 iris 且不白屏

验收完杀掉 dev 进程。

- [ ] **Step 6: 提交**

```bash
git add src/index.css src/App.tsx src/components/ && git commit -m "feat(web): Tailwind 主题映射、主题切换器与演示页"
```

---

### Task 8: 总验收与收尾

**Files:**
- 无新增（如验收发现问题就地修复并提交）

- [ ] **Step 1: 对照规格逐条验收**

| 规格 §7 验收标准 | 对应动作 |
|---|---|
| 三主题切换全组件即时变色 | Task 7 Step 5 已验，复核一遍 |
| 刷新主题保持 | 同上 |
| 非法值回落 iris 不崩 | 同上第 4 条 |
| 错误态无高饱和红 | 目视检查三主题 |
| lint + build 通过 | 终端执行确认 |

- [ ] **Step 2: 更新记忆**

`.claude/memory/architecture.md` 前端小节追加一行：「主题系统已随 M0 前端落地（2026-09-04），演示页可切换验证」。

- [ ] **Step 3: 最终提交**

```bash
git add -A && git status   # 确认没有 .superpowers/、node_modules/ 等被跟踪
git commit -m "feat(web): 莫兰迪紫主题系统完成，通过规格验收"
```

---

## 任务依赖

Task 1 → Task 2 → (3 → 4 → 5 → 6) → 7 → 8。Task 3-5 相互独立可并行，但 4 依赖 3（normalizeThemeId）、6 依赖 3/4/5。
