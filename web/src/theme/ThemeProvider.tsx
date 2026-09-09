import { useEffect, useMemo } from 'react'
import type { PropsWithChildren } from 'react'
import { ConfigProvider, theme as antdTheme } from 'antd'
import type { ThemeConfig } from 'antd'
import { DEFAULT_THEME, PALETTES } from './palettes'
import { useThemeStore } from '../stores/theme'

/** 系统圆润字体栈（设计稿 §3.3） */
export const FONT_FAMILY = `-apple-system, "PingFang SC", "HarmonyOS Sans SC", "MiSans", "Segoe UI", sans-serif`

/**
 * 轨道 2：palette → 根节点 CSS 变量 + data-theme。
 * 自定义样式（Tailwind 语义类 / 内联 var() 引用）全部走这组变量，组件禁止写死色值。
 */
function applyCssVars(themeId: keyof typeof PALETTES) {
  const p = PALETTES[themeId]
  const root = document.documentElement
  const vars: Record<string, string> = {
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
    '--enl-shadow': p.shadow,
    '--enl-radius-card': '18px',
    '--enl-radius-ctl': '12px',
  }
  for (const [key, value] of Object.entries(vars)) {
    root.style.setProperty(key, value)
  }
  root.dataset.theme = p.id
}

/**
 * 主题双轨注入（设计稿 §4）：
 * 轨道 1 = AntD ConfigProvider token；轨道 2 = 根节点 CSS 变量。
 * 切主题只改 store，两轨随之即时生效，无刷新。
 */
export function ThemeProvider({ children }: PropsWithChildren) {
  const themeId = useThemeStore((s) => s.themeId)
  const palette = PALETTES[themeId] ?? PALETTES[DEFAULT_THEME]

  useEffect(() => {
    applyCssVars(palette.id)
  }, [palette])

  const themeConfig = useMemo<ThemeConfig>(
    () => ({
      // 保持默认浅色算法（本期不做深色）
      algorithm: antdTheme.defaultAlgorithm,
      token: {
        colorPrimary: palette.primary,
        colorInfo: palette.primary,
        colorLink: palette.primaryDeep,
        colorText: palette.textStrong,
        colorTextSecondary: palette.textSecondary,
        colorError: palette.accent.error.text,
        colorSuccess: palette.accent.success.text,
        borderRadius: 12,
        borderRadiusLG: 18,
        controlHeight: 40,
        fontFamily: FONT_FAMILY,
      },
    }),
    [palette],
  )

  return <ConfigProvider theme={themeConfig}>{children}</ConfigProvider>
}
