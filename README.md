# ll-skills

[English](README.en.md) | 简体中文

## 安装

项目级（默认，装到当前项目 `./.agents/skills/`，仅该项目可用）：

```bash
# 全部
npx skills add 3349516/skills

# 单个
npx skills add 3349516/skills --skill <name>
```

全局（所有项目可用）：

```bash
# 全部
npx skills add 3349516/skills -g -y

# 单个
npx skills add 3349516/skills --skill <name> -g -y
```

## 同步更新

```bash
npx skills update        # 当前项目
npx skills update -g     # 全局
```

## 删除

```bash
npx skills remove <name>        # 当前项目
npx skills remove <name> -g     # 全局
```

## Skill 清单

| 分类 | Skill | 说明 |
|---|---|---|
| `app` | `android-compose-mvvm` | Android Jetpack Compose 的 MVVM / UI 层架构规范（UiState、ViewModel、单向数据流、事件与导航） |
| `trade` | `xtquant-xtdata` | XtQuant.XtData 行情模块 API 查询与本机可用性检测 |
| `trade` | `xtquant-xttrade` | XtQuant.XtTrade 交易模块 API 查询与本机可用性检测 |
