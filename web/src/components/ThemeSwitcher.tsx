import { Tooltip } from 'antd'
import { PALETTES, THEME_IDS } from '../theme/palettes'
import { useThemeStore } from '../stores/theme'

/**
 * 顶栏主题色点切换器（设计稿 §5）：
 * 三个 20px 圆钮各取主题 primary 色，当前主题外圈 2px primaryDeep 描边，Tooltip 显示中文名。
 */
export function ThemeSwitcher() {
  const themeId = useThemeStore((s) => s.themeId)
  const setTheme = useThemeStore((s) => s.setTheme)

  return (
    <div className="flex items-center gap-3" role="radiogroup" aria-label="主题切换">
      {THEME_IDS.map((id) => {
        const palette = PALETTES[id]
        const active = id === themeId
        return (
          <Tooltip key={id} title={palette.name}>
            <button
              type="button"
              role="radio"
              aria-checked={active}
              aria-label={`切换主题：${palette.name}`}
              onClick={() => setTheme(id)}
              className="h-5 w-5 cursor-pointer rounded-full transition-transform hover:scale-125 focus:outline-none"
              style={{
                backgroundColor: palette.primary,
                boxShadow: active ? `0 0 0 2px ${palette.primaryDeep}` : 'none',
              }}
            />
          </Tooltip>
        )
      })}
    </div>
  )
}
