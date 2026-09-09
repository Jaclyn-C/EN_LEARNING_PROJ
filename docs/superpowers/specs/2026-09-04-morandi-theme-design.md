# EN-learning 前端视觉与主题系统设计（莫兰迪紫）

> 状态：**已确认**（2026-09-04，与用户经视觉伴侣逐项确认）
> 关联：`docs/PLAN.md`（母文档）；本文档是 M0 前端脚手架的视觉与主题部分的设计输入。

## 1. 背景与目标

`web/` 尚未创建（M0 未开始）。在脚手架动工前先定调全局视觉：**年轻、好看的莫兰迪紫风格**，并支持**运行时切换三套主题**。主题系统是前端基建的一部分，之后所有页面（做题页、生词本、AI 助手等）都按这套设计令牌开发。

## 2. 范围

**包含**：
- 三套莫兰迪紫色板与全局设计令牌（色/形/影/字体）
- 主题切换架构（AntD token + CSS 变量双轨注入）、持久化、切换器组件
- 随 M0 落地：Vite + TS 初始化、Tailwind/AntD 配置、主题系统、`ThemeSwitcher`、一个演示页（按钮/表单/标签/卡片 + 切换器）用于验收

**不包含**：
- 业务页面设计（做题页等随里程碑另出 DESIGN）
- 深色模式（仅结构预留，见 §6）
- 自定义 web 字体下载（用系统字体栈，本地自用不依赖外网）
- 插画/吉祥物素材（如需后补，不阻塞本设计）

## 3. 设计令牌

### 3.1 三套主题色板

主题 id：`iris`（默认）/ `mist` / `mauve`。

| 令牌 | iris 鸢尾蓝紫（默认） | mist 雾紫奶油 | mauve 藕紫奶茶 |
|---|---|---|---|
| `primary` | `#7D7FA8` | `#9F8BB8` | `#AC8DA5` |
| `primaryDeep`（hover/active） | `#66688F` | `#8672A0` | `#96758F` |
| `textStrong` | `#3E4157` | `#4B4256` | `#524A4E` |
| `textSecondary` | `#82859B` | `#8B8296` | `#94898E` |
| `bgFrom`（渐变底起） | `#F5F6FA` | `#FAF7F2` | `#FAF6F2` |
| `bgTo`（渐变底止） | `#EDECF4` | `#F2EEF6` | `#F4ECEA` |
| `accent.info`（底/文字） | `#D7DDEA` / `#66738F` | `#AEB9C9` / `#6D7A8C` | `#C9D2DA` / `#77889A` |
| `accent.purple`（底/文字） | `#DDD8E8` / `#76708C` | —（主色即紫） | — |
| `accent.success`（底/文字） | `#D6DDD3` / `#6F8170` | `#C6CCB9` / `#77805F` | `#E5D3B8` / `#9C7F5B`（奶咖） |
| `accent.error`（底/文字） | `#E3CFD6` / `#8F7080`（灰玫） | `#E3C9CE` / `#9A6E77`（灰粉） | `#E8CFC4` / `#A57F6F`（灰杏） |
| `shadow`（卡片软阴影） | `rgba(125,127,168,.12)` | `rgba(159,139,184,.12)` | `rgba(172,141,165,.12)` |

> 说明：mist 的"紫"即主色本身，其 accent 组合为灰粉/灰绿/灰蓝；mauve 为奶咖/灰蓝/灰杏；iris 为雾蓝/灰紫/灰绿。每套主题的辅助色即该主题的标签色（题型标签、来源标签等）。

### 3.2 语义色规则

- **正确**：accent.success 系（灰绿/奶咖）——不用高饱和绿
- **错误**：accent.error 系（灰粉/灰杏）——**禁止高饱和红**，这是保住莫兰迪感的关键取舍
- **进行中/选中/主操作**：primary 系
- 题型/来源等中性标签：轮换使用该主题的三个 accent

### 3.3 形状与质感（三套通用）

| 项 | 值 |
|---|---|
| 卡片圆角 | 18px（AntD `borderRadiusLG: 18`） |
| 输入框/选项圆角 | 12px（AntD `borderRadius: 12`） |
| 主按钮（CTA） | 胶囊（999px），其余按钮随控件 12px |
| 卡片阴影 | `0 8px 24px var(--enl-shadow)`（带主色调，不用黑灰） |
| 按钮悬浮阴影 | `0 4px 12px var(--enl-shadow)` |
| 页面底色 | 淡渐变 `linear-gradient(135deg, var(--enl-bg-from), var(--enl-bg-to))` 固定铺满 |
| 字体 | 系统圆润栈：`-apple-system, "PingFang SC", "HarmonyOS Sans SC", "MiSans", "Segoe UI", sans-serif`；数字/代码：`"SF Mono", ui-monospace, monospace` |
| 装饰 | 渐变底 + 色点/emoji 轻点缀，不引入插画库 |

## 4. 主题切换架构（TS 色板双轨注入）

```
web/src/
├─ theme/
│  ├─ palettes.ts        # Palette 接口 + PALETTES 记录（单一事实来源）+ DEFAULT_THEME='iris'
│  └─ ThemeProvider.tsx  # 双轨注入组件（见下）
├─ stores/theme.ts       # zustand + persist：{ themeId } / setTheme(id)，key='enl-theme'
└─ components/ThemeSwitcher.tsx  # 顶栏色点切换器
```

**数据流**：点击色点 → `setTheme(id)` → `ThemeProvider` 重渲染：

- **轨道 1（AntD）**：palette 映射 AntD `theme.token`（`colorPrimary`、`colorInfo`=primary、`colorLink`=primaryDeep、`colorText`、`colorTextSecondary`、`borderRadius: 12`、`borderRadiusLG: 18`、`fontFamily` 等），经 `<ConfigProvider>` 动态传入，全组件树自动变色。
- **轨道 2（自定义样式）**：同一 palette 写入根节点 CSS 变量：`--enl-primary`、`--enl-primary-deep`、`--enl-text-strong`、`--enl-text-secondary`、`--enl-bg-from`、`--enl-bg-to`、`--enl-accent-info-bg/-text`（其余 accent 同理）、`--enl-shadow`、`--enl-radius-card: 18px`、`--enl-radius-ctl: 12px`；同时设 `data-theme="<id>"` 与 body 渐变底。
- **Tailwind**：`tailwind.config` 中 `colors.primary: 'var(--enl-primary)'` 等全部引用 CSS 变量；自定义组件禁止写死色值。

**健壮性**：`setTheme` 收到未知 id → 回落 `iris`；localStorage 损坏/非法同理。切换即时生效、无刷新。

## 5. 切换器 UI

顶栏右侧三个色点圆钮（20px 圆、各自主题的 primary 色），当前主题外圈 2px 描边（primaryDeep）+ Tooltip 显示主题名；点击即切。

## 6. 深色模式预留（不实施）

- CSS 变量按**语义**命名（§4），未来加深色 = 每套 palette 增加一组暗色值 + `[data-theme-dark]` 变量覆盖，业务代码零改动。
- 本期不写任何暗色样式。

## 7. 验收标准

1. 演示页切换三主题：AntD 组件（按钮/输入框/选择器/标签）与自定义组件全部即时变色，无刷新
2. 刷新页面后主题保持（localStorage）
3. localStorage 写入非法值时回落 iris，应用不崩
4. 错误态无高饱和红（莫兰迪检查）
5. M0 脚手架完成后 `pnpm lint` + `pnpm build` 通过

## 8. 备注

- 本仓库尚未 `git init`（属 M0 范围）；届时提交本文档，且 `.gitignore` 需包含 `.superpowers/`（视觉伴侣产物目录）。
