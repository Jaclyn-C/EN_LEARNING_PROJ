import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import { DEFAULT_THEME, isThemeId, PALETTES } from '../theme/palettes'
import type { Palette, ThemeId } from '../theme/palettes'

export interface ThemeState {
  themeId: ThemeId
  setTheme: (id: ThemeId) => void
}

/** localStorage key（设计稿 §4：'enl-theme'） */
export const THEME_STORAGE_KEY = 'enl-theme'

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      themeId: DEFAULT_THEME,
      // 未知 id 一律回落 iris（设计稿 §4 健壮性）
      setTheme: (id) => set({ themeId: isThemeId(id) ? id : DEFAULT_THEME }),
    }),
    {
      name: THEME_STORAGE_KEY,
      version: 1,
      storage: createJSONStorage(() => localStorage),
      // 只持久化 themeId，函数不落盘
      partialize: (state) => ({ themeId: state.themeId }),
      // 重放校验：localStorage 为非法值/形状异常（含损坏 JSON 解析为 null）时回落 iris，应用不崩
      merge: (persisted, current) => {
        const raw = (persisted as { themeId?: unknown } | null | undefined)?.themeId
        return { ...current, themeId: isThemeId(raw) ? raw : DEFAULT_THEME }
      },
      // 双保险：rehydrate 完成后再校验一次
      onRehydrateStorage: () => (state) => {
        if (!state || !isThemeId(state.themeId)) {
          useThemeStore.setState({ themeId: DEFAULT_THEME })
        }
      },
    },
  ),
)

/** 取当前色板（带兜底，主题相关组件统一从这里拿） */
export function usePalette(): Palette {
  const themeId = useThemeStore((s) => s.themeId)
  return PALETTES[themeId] ?? PALETTES[DEFAULT_THEME]
}
