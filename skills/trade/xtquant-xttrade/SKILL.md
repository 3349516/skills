---
name: xtquant-xttrade
description: XtQuant.XtTrade 交易模块 API 查询与本机可用性检测。Use when Codex needs to answer questions about xtquant.xttrader, XtQuantTrader, StockAccount, xtconstant order/price/account constants, order/cancel/query APIs, callbacks, credit trading APIs, or check whether the local Python environment can import xtquant trading modules and optionally connect/query MiniQMT.
---

# XtQuant XtTrade

Use this skill for broker MiniQMT XtQuant trading-interface work: API lookup, safe examples, callback wiring, account/query diagnostics, and local environment checks. Assume a normal broker-distributed MiniQMT client, not a VIP/full-service terminal, unless the user says otherwise.

## Safety Rules

- Treat `order_*`, `cancel_*`, `fund_transfer`, `sync_transaction_from_external`, `smt_negotiate_order_async`, and similar operation APIs as live trading actions.
- Do not run order, cancel, transfer, or securities-lending application calls as a "test".
- Default to import/introspection checks. Only create a trader connection when the user explicitly asks to test connection and provides a MiniQMT `userdata_mini` path or a config source.
- Query APIs can reveal account data. Use them only when the user explicitly provides an account id and asks for account/query validation.
- Do not assume credit, futures, options, Hong Kong Connect, ETF purchase/redemption, common-data export, or securities-lending appointment APIs are enabled in a broker MiniQMT package.

## Quick Workflow

1. For API questions, read `references/xttrade-api.md` first and answer from that reference. If the user asks about a method not listed there, inspect the local `xtquant.xttrader` module with Python or consult the official page: `https://dict.thinktrader.net/nativeApi/xttrader.html`.
2. For local diagnostics, run `scripts/check_xttrade.py` with the narrowest needed flags.
3. For implementation guidance, prefer this lifecycle:
   - subclass `XtQuantTraderCallback`
   - create `XtQuantTrader(path, session_id)`
   - `register_callback(callback)`
   - `start()`
   - `connect()`, where `0` means success
   - create `StockAccount(account_id, account_type)` as needed
   - `subscribe(account)` before relying on pushes
   - use query APIs for state, async APIs for order submission when callbacks are required
4. When designing reconnection logic, use a finite `session_id` range; do not loop forever creating new sessions.

## Local Detection

Default mode checks imports, classes, constants, and method signatures only:

```powershell
python .\skills\xtquant-xttrade\scripts\check_xttrade.py
```

Useful options:

```powershell
python .\skills\xtquant-xttrade\scripts\check_xttrade.py --methods query_stock_asset order_stock_async
python .\skills\xtquant-xttrade\scripts\check_xttrade.py --include-extended
python .\skills\xtquant-xttrade\scripts\check_xttrade.py --path "D:\path\to\userdata_mini" --session-id 123456 --connect
python .\skills\xtquant-xttrade\scripts\check_xttrade.py --path "D:\path\to\userdata_mini" --session-id 123456 --connect --account-id 1000000365 --account-type STOCK --query account_status
```

Interpretation:

- Import failure usually means `xtquant` is not installed in the active Python environment.
- Constructor or connection failure usually means wrong `userdata_mini` path, MiniQMT/QMT is not running, duplicate `session_id`, or broker/client permission problems.
- `connect()` returning `0` means success; nonzero or exceptions indicate failure.
- `subscribe(account)` returning `0` means success; `-1` means failure.

## Reference Files

- `references/xttrade-api.md`: curated API map, lifecycle, constants, callbacks, return conventions, and examples.
