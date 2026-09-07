# ll-skills

English | [简体中文](README.md)

## Install

Project-level (default, installs to `./.agents/skills/`, available only in that project):

```bash
# all
npx skills add 3349516/skills

# single
npx skills add 3349516/skills --skill <name>
```

Global (available in all projects):

```bash
# all
npx skills add 3349516/skills -g -y

# single
npx skills add 3349516/skills --skill <name> -g -y
```

## Update

```bash
npx skills update        # current project
npx skills update -g     # global
```

## Remove

```bash
npx skills remove <name>        # current project
npx skills remove <name> -g     # global
```

## More Commands

```bash
npx skills ls -g                              # List installed (-g global; -a <agent> filter; --json)
npx skills find <keyword>                     # Search the registry (skills.sh); --owner limits to a GitHub owner
npx skills use 3349516/skills@xtquant-xtdata  # Use a skill without installing (prints a prompt, pipe to an agent)
npx skills init <name>                        # Scaffold a new skill (SKILL.md) in the current directory
npx skills check                              # Check installed skills for updates without applying them
```

## Skills

| Category | Skill | Description |
|---|---|---|
| `app` | `android-compose-mvvm` | MVVM / UI-layer architecture guidelines for Android Jetpack Compose (UiState, ViewModel, unidirectional data flow, events & navigation) |
| `trade` | `xtquant-xtdata` | XtQuant.XtData market-data module API reference & local availability check |
| `trade` | `xtquant-xttrade` | XtQuant.XtTrade trading module API reference & local availability check |
| `trade` | `qmt-builtin-strategy` | Design, review & refactor QMT built-in Python strategies (init/handlebar/ContextInfo/passorder etc.) |
| `trade` | `ptrade-strategy` | Write, review & debug PTrade Python strategies; migrate backtests to paper/live trading |
