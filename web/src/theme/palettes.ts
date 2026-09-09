/**
 * 三套莫兰迪紫色板 —— 单一事实来源。
 * 色值逐项照抄 docs/superpowers/specs/2026-09-04-morandi-theme-design.md §3.1，禁止改动。
 * mist / mauve 的 accent.purple 设计稿标注为「—（主色即紫）」：
 * 依该备注由 primary 派生（bg = primary 20% 透明度叠底，text = primaryDeep），非自创色值。
 */

export interface AccentColor {
  /** 标签/提示块底色 */
  bg: string
  /** 标签/提示块文字色 */
  text: string
}

export interface Palette {
  /** 主题 id（与 PALETTES 键一致） */
  id: ThemeId
  /** 主题中文名 */
  name: string
  /** 主色：进行中/选中/主操作 */
  primary: string
  /** 主色深：hover/active/链接 */
  primaryDeep: string
  /** 强文字色 */
  textStrong: string
  /** 次文字色 */
  textSecondary: string
  /** 页面渐变底起 */
  bgFrom: string
  /** 页面渐变底止 */
  bgTo: string
  /** 辅助色（题型/来源标签、正确/错误态）。错误系为灰玫/灰粉/灰杏，禁高饱和红 */
  accent: {
    info: AccentColor
    purple: AccentColor
    success: AccentColor
    error: AccentColor
  }
  /** 卡片软阴影色（带主色调，不用黑灰） */
  shadow: string
}

export type ThemeId = 'iris' | 'mist' | 'mauve'

export const THEME_IDS = ['iris', 'mist', 'mauve'] as const satisfies readonly ThemeId[]

export const DEFAULT_THEME: ThemeId = 'iris'

/** 未知值守卫：localStorage / 外部输入经此校验，非法一律回落 iris */
export function isThemeId(value: unknown): value is ThemeId {
  return typeof value === 'string' && (THEME_IDS as readonly string[]).includes(value)
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
    shadow: 'rgba(125,127,168,.12)',
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
      // 设计稿：mist 的「紫」即主色本身 → primary 20% 叠底 + primaryDeep 文字
      purple: { bg: '#9F8BB833', text: '#8672A0' },
      success: { bg: '#C6CCB9', text: '#77805F' },
      error: { bg: '#E3C9CE', text: '#9A6E77' },
    },
    shadow: 'rgba(159,139,184,.12)',
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
      // 设计稿：mauve 的「紫」即主色本身 → primary 20% 叠底 + primaryDeep 文字
      purple: { bg: '#AC8DA533', text: '#96758F' },
      success: { bg: '#E5D3B8', text: '#9C7F5B' },
      error: { bg: '#E8CFC4', text: '#A57F6F' },
    },
    shadow: 'rgba(172,141,165,.12)',
  },
}
