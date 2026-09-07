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

## 其它命令

```bash
npx skills ls -g                              # 列出已安装（-g 全局；-a <agent> 按工具过滤；--json 机器可读）
npx skills find <关键词>                       # 搜索注册表（skills.sh）上的 skill；--owner 限定仓库主
npx skills use 3349516/skills@xtquant-xtdata  # 不安装，直接生成该 skill 的使用提示（可管道传给 agent）
npx skills init <name>                        # 在当前目录创建新 skill 骨架（SKILL.md）
npx skills check                              # 只检查已装 skill 是否有新版本，不实际更新
```

## Skill 清单

| 分类 | Skill | 说明 |
|---|---|---|
| `app` | `android-compose-mvvm` | Android Jetpack Compose 的 MVVM / UI 层架构规范（UiState、ViewModel、单向数据流、事件与导航） |
| `trade` | `xtquant-xtdata` | XtQuant.XtData 行情模块 API 查询与本机可用性检测 |
| `trade` | `xtquant-xttrade` | XtQuant.XtTrade 交易模块 API 查询与本机可用性检测 |
| `trade` | `qmt-builtin-strategy` | QMT 内置 Python 策略的设计、审查、重构（init/handlebar/ContextInfo/passorder 等） |
| `trade` | `ptrade-strategy` | PTrade Python 策略编写、审查与排查，支持回测迁移到模拟盘/实盘 |
