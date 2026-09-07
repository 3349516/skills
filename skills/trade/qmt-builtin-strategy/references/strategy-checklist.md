# QMT Builtin Strategy Review Checklist

Use this checklist before generating or approving QMT built-in Python strategy code.

## 1. Scope and Assumptions

- Is this definitely a QMT built-in strategy, not MiniQMT or an external Python client?
- Is the target account type ordinary A-share or ETF stock account?
- Are the trading universe, frequency, and execution style stated explicitly?
- Are the account ID and chart period treated as configurable inputs instead of hidden constants?

## 2. Lifecycle Placement

- Does the script include both `init(ContextInfo)` and `handlebar(ContextInfo)`?
- Are account binding and universe binding done in `init(ContextInfo)`?
- Is `run_time()` used only for runtime behavior, not as a core backtest mechanism?
- Is cleanup moved into `stop(ContextInfo)` when timers or subscriptions are used?

## 3. Data Access

- Does the strategy define its data lookback window clearly?
- Does it use one helper to fetch and normalize market data?
- Does backtest logic avoid unnecessary real-time subscription behavior?
- If multiple symbols are involved, is the update trigger model clear: `handlebar()` only, `subscribe_quote()`, or both?

## 4. Signal Design

- Is the signal computation separated from raw data retrieval?
- Are thresholds, windows, and ranking rules explicit?
- Is the signal stable on repeated ticks for the same bar?
- Does the code avoid mixing signal generation with direct `passorder()` calls in many branches?

## 5. Risk and Position Control

- Is there a guard against repeated orders on the same bar?
- Is there a position check before buying again?
- Is there a cash or exposure check before submitting orders?
- Are minimum lot size and share-based quantity rules respected?
- Is the sell path defined as clearly as the buy path?

## 6. Order Execution

- Are all orders routed through one helper such as `submit_order(...)`?
- Does the helper make `opType`, `orderType`, `prType`, and `remark` easy to inspect?
- Is `quickTrade` left at a conservative default unless the strategy truly needs immediate execution?
- Are strategy name and user remark used consistently for traceability?

## 7. Trade State and Callbacks

- If the strategy depends on fill or reject state, does it implement `order_callback()` or `deal_callback()`?
- Are pending-order markers cleared when callbacks arrive?
- Are callback side effects limited and easy to reason about?

## 8. Backtest Versus Runtime Differences

- Does the code branch on `ContextInfo.do_back_test` where behavior differs?
- Does the strategy avoid relying on `run_time()` in backtest mode?
- If `subscribe_quote()` is used, is the reason tied to runtime-only freshness needs?
- Is live tick repetition handled safely so that one bar does not create multiple duplicate actions?

## 9. Logging and Maintainability

- Are logs and comments short, intentional, and helpful?
- Are helper function names based on business meaning rather than implementation detail?
- Can another developer identify where data, signal, risk, and execution live without reading the whole file?
- Are user-specific constants isolated so a new strategy can be cloned safely?

## 10. Review Output Format

When reviewing existing code, prefer this order:

1. lifecycle and account-binding errors
2. repeated-order or backtest/runtime mismatch risks
3. data-shape and position-query mistakes
4. structure and maintainability improvements

If no major bug is found, still report residual risks:

- missing callbacks
- missing cleanup
- insufficient position or cash guards
- hard-coded parameters that should be configurable
