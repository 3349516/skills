# QMT Builtin Python API Notes

This reference is for the official QMT built-in Python strategy API page at `https://qmt.ptradeapi.com/QMT_Python_API_Doc.html`.

Scope:

- Built-in strategy module only
- A-share and ETF ordinary stock-account scenarios first
- No MiniQMT, no `xtquant`, no external client runtime

## Core Structure

The official document requires the strategy script to start with:

```python
#coding:gbk
```

The built-in strategy structure is centered on two required functions:

```python
def init(ContextInfo):
    pass


def handlebar(ContextInfo):
    pass
```

Optional but important helpers include:

```python
def stop(ContextInfo):
    pass


def order_callback(ContextInfo, orderInfo):
    pass


def deal_callback(ContextInfo, dealInfo):
    pass
```

## Lifecycle Responsibilities

### `init(ContextInfo)`

Use for:

- setting strategy parameters
- binding stock universe
- binding account
- setting backtest-only display or commission settings
- registering runtime-only timers

Do not push account binding to later stages. The official doc states that `ContextInfo.set_account(account)` should be completed in `init`, and later calls will not subscribe trade pushes for newly added accounts.

### `handlebar(ContextInfo)`

Use for:

- bar-by-bar orchestration
- fetching current or historical data
- running signal logic
- calling risk guards
- routing final orders through one helper

Remember:

- historical bars are replayed first in backtest and run mode
- on the live last bar, `handlebar()` can be driven repeatedly by ticks
- repeated orders on one bar must be guarded explicitly

### `stop(ContextInfo)`

Use when the strategy started timers, quote subscriptions, or temporary state that needs cleanup before shutdown.

## High-Frequency `ContextInfo` APIs

### Universe and account

```python
ContextInfo.set_universe(stock_list)
ContextInfo.set_account(account_id)
```

Notes:

- `set_universe()` should run in `init`.
- `set_account()` should run in `init`.
- if `passorder()` receives an empty account ID, QMT uses the last account set by `set_account()`

### Backtest mode

```python
ContextInfo.do_back_test
```

Use this boolean to split behavior:

- backtest-safe data reads
- runtime-only timers
- runtime-only subscriptions
- log verbosity

### Bar state

```python
ContextInfo.barpos
ContextInfo.is_last_bar()
ContextInfo.is_new_bar()
```

Recommended use:

- use `barpos` or `is_new_bar()` to prevent duplicate execution on the same bar
- use `is_last_bar()` carefully when you only want live-bar behavior

### Timer

```python
ContextInfo.run_time(func_name, period, start_time, market)
```

Important constraint from the official doc:

- `run_time()` has no meaning in backtest mode

Treat timer callbacks as runtime-only helpers, not core backtest logic.

### Quote subscription

```python
ContextInfo.subscribe_quote(stock_code, period="follow", dividend_type="follow", callback=None)
```

Use when:

- the strategy depends on secondary symbols updating immediately
- `handlebar()` driven by the main chart symbol is not enough

Avoid unnecessary subscriptions in simple daily or bar-close strategies.

## Data Retrieval

### `ContextInfo.get_market_data_ex(...)`

Use this as the primary structured data loader for strategy templates.

Recommended pattern:

```python
data = ContextInfo.get_market_data_ex(
    ["close"],
    ["510300.SH"],
    period="1d",
    start_time="",
    end_time="",
    count=20,
    dividend_type="front",
    fill_data=True,
    subscribe=not ContextInfo.do_back_test,
)
```

Guidance:

- set `count` for rolling windows
- set `subscribe=False` in backtest-oriented reads
- check the returned dict by stock code
- keep one helper for converting returned frames into strategy inputs

## Trading APIs

### `passorder(...)`

Common stock operations:

- `23`: stock buy
- `24`: stock sell

Common stock `orderType`:

- `1101`: single stock, single account, share-based quantity
- `1102`: single stock, single account, amount-based quantity

Common `prType`:

- `5`: latest price
- `11`: model price

Recommended wrapper shape:

```python
def submit_order(ContextInfo, account_id, stock_code, op_type, volume, remark):
    passorder(
        op_type,
        1101,
        account_id,
        stock_code,
        5,
        0,
        volume,
        ContextInfo.strategy_name,
        0,
        remark,
        ContextInfo,
    )
```

Important behavior from the official doc:

- default `passorder()` behavior triggers on the next bar after the signal on the final completed K line
- `quickTrade=1` can trigger immediately on the non-historical last bar
- `quickTrade=2` can trigger even on historical bars and should be treated as high risk

For reusable templates, default to `quickTrade=0` unless the user explicitly needs immediate runtime behavior.

### `get_trade_detail_data(...)`

Use this to inspect:

- `POSITION`
- `ORDER`
- `DEAL`
- `ACCOUNT`
- `TASK`

Recommended ordinary stock-account call:

```python
positions = get_trade_detail_data(account_id, "STOCK", "POSITION")
```

Use this function in helper wrappers such as:

- `has_position(...)`
- `get_available_cash(...)`
- `list_open_orders(...)`

## Trade Callbacks

The official doc exposes:

- `account_callback(ContextInfo, accountInfo)`
- `order_callback(ContextInfo, orderInfo)`
- `deal_callback(ContextInfo, dealInfo)`
- `position_callback(ContextInfo, positionInfo)`
- `orderError_callback(ContextInfo, orderErrorInfo)`

Recommended practice:

- store only the minimum state needed for reconciliation
- log account/order/deal transitions
- use callbacks to clear pending-order markers and capture rejection reasons

## Template Conventions For This Repository

- Keep strategy parameters in `init(ContextInfo)`.
- Bind universe and account in `init(ContextInfo)`.
- Keep one centralized order helper.
- Split data, signal, risk, and execution helpers when strategy logic grows.
- Make backtest versus runtime behavior explicit.
- Prefer conservative defaults that are safe in backtest before enabling fast runtime behavior.
