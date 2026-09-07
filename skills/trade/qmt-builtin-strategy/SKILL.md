---
name: qmt-builtin-strategy
description: Use when Codex needs to design, review, refactor, or template QMT built-in Python strategies that run inside the QMT strategy module with init(ContextInfo), handlebar(ContextInfo), ContextInfo methods, passorder(), and trade callbacks, especially for A-share or ETF strategies under project-specific development conventions.
---

# QMT Builtin Strategy

Use this skill only for QMT built-in Python strategies that run inside the platform strategy module.

Do not use this skill for:

- MiniQMT
- `xtquant`
- `xtdata` or `xttrader`
- external Python client scripts

## Read First

1. Read `references/qmt-builtin-api.md` for the built-in lifecycle and high-frequency APIs.
2. Read `references/strategy-checklist.md` before reviewing strategy ideas or code.
3. Use `assets/templates/basic_strategy.py` for the smallest compliant skeleton.
4. Use `assets/templates/signal_strategy.py` when the user wants a strategy that separates data, signal, risk, and execution.

## Workflow

### 1. Classify the request

- Strategy idea review: convert the idea into a fixed card with universe, frequency, data needs, signal, risk limits, order mode, and backtest versus run behavior.
- Code review: inspect lifecycle placement first, then run the checklist and report the highest-risk problems before suggesting cleanup.
- Template generation: choose the nearest asset template, then fill in parameters and strategy-specific helper functions.

### 2. Enforce QMT built-in boundaries

- Keep the first line as `#coding:gbk`.
- Treat `init(ContextInfo)` and `handlebar(ContextInfo)` as required entry points.
- Treat `stop(ContextInfo)` as optional but recommended when the strategy holds timers, subscriptions, or cleanup state.
- Use QMT built-in trade functions such as `passorder()` and built-in trade callbacks such as `order_callback()` and `deal_callback()`.

### 3. Put code in the right lifecycle

- `init(ContextInfo)`: strategy parameters, universe, account binding, backtest settings, and runtime-only timer registration.
- `handlebar(ContextInfo)`: bar-driven orchestration only. Fetch data, evaluate signal, run risk guards, and call one centralized order helper.
- Quote callbacks: handle symbol-specific intraday refresh logic only when `handlebar()` is not sufficient.
- Trade callbacks: update local state, log fills or rejects, and reconcile pending orders.
- `stop(ContextInfo)`: release runtime resources or print final summaries.

### 4. Apply generation rules

- Set account and universe in `init(ContextInfo)`, not later.
- If multiple accounts are needed, set all accounts inside `init(ContextInfo)` before strategy execution continues.
- Use `ContextInfo.do_back_test` to branch runtime-only logic.
- Do not rely on `run_time()` for backtest behavior. The official documentation states it has no meaning in backtest mode.
- Prevent repeated orders on the same bar. Track `ContextInfo.barpos`, pending order IDs, or a strategy-level cooldown marker.
- Keep one order submission helper such as `submit_order(...)`. Do not scatter raw `passorder()` calls across many branches.
- Separate data retrieval, signal calculation, risk checks, and order execution into dedicated helpers once the strategy exceeds a few dozen lines.
- Prefer `get_trade_detail_data()` for account, position, order, and deal inspection.
- When the user asks for review, prioritize lifecycle errors, repeated-order risks, account binding mistakes, and backtest/runtime mismatches.

## Output Expectations

- Default to Chinese explanations when talking to the user.
- When generating strategy code, preserve the QMT built-in structure and keep comments short and practical.
- When reviewing code, list findings first, ordered by severity, with file references when available.
- When creating a new strategy, explain which template you started from and which parts still need user-specific parameters such as account ID, universe, or thresholds.
