# XtQuant.XtTrade API Reference

Source: XtQuant native API page, `https://dict.thinktrader.net/nativeApi/xttrader.html`. This reference is adapted for broker MiniQMT usage. Do not assume VIP/full-service terminal permissions unless the user confirms them.

## Broker MiniQMT Baseline

Prefer these as the default capability set:

- Import and inspect `xtquant.xttrader`, `xtquant.xttype`, and `xtquant.xtconstant`.
- Create `XtQuantTrader(path, session_id)`, `start()`, and `connect()` only when the user provides a real `userdata_mini` path.
- Use `StockAccount(account_id)` for normal stock/security accounts.
- Use `subscribe(account)` and stock query APIs such as `query_stock_asset`, `query_stock_orders`, `query_stock_trades`, and `query_stock_positions`.
- Use `order_stock` or `order_stock_async` only when the user explicitly asks to place a live order.

Treat these as extended, broker-permission-dependent, or account-type-dependent:

- Credit/margin APIs and constants
- Futures/options APIs and constants
- Hong Kong Connect account constants
- Common-data export/query APIs
- Securities-lending appointment APIs
- ETF purchase/redemption

## Basic Imports

```python
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
```

## Runtime Lifecycle

```python
path = r'D:\...\userdata_mini'
session_id = 123456
xt_trader = XtQuantTrader(path, session_id)
xt_trader.register_callback(MyCallback())
xt_trader.start()
connect_result = xt_trader.connect()  # 0 means success
subscribe_result = xt_trader.subscribe(account)  # 0 means success, -1 means failure
xt_trader.run_forever()
```

- `path` is the broker MiniQMT client `userdata_mini` directory.
- `session_id` should be unique per strategy/process.
- Do not retry with an unbounded infinite loop; each connection can create docking files.
- Use `stop()` to stop running when shutting down.
- `set_relaxed_response_order_enabled(True)` allows synchronous query responses to return from a dedicated thread, useful when calling sync query APIs inside push callbacks. It relaxes event ordering; prefer async query APIs in callbacks when available.

## Data Dictionaries

### Account Types

- `xtconstant.FUTURE_ACCOUNT`: futures
- `xtconstant.SECURITY_ACCOUNT`: stock/security
- `xtconstant.CREDIT_ACCOUNT`: margin/credit
- `xtconstant.FUTURE_OPTION_ACCOUNT`: futures option
- `xtconstant.STOCK_OPTION_ACCOUNT`: stock option
- `xtconstant.HUGANGTONG_ACCOUNT`: Shanghai-Hong Kong Stock Connect
- `xtconstant.SHENGANGTONG_ACCOUNT`: Shenzhen-Hong Kong Stock Connect

`StockAccount('1000000365')` can be used for a normal stock/security account. Use credit or other account types only after confirming the broker account is enabled for that business.

### Common Order Types

- Stock: `xtconstant.STOCK_BUY`, `xtconstant.STOCK_SELL`
- Credit: `CREDIT_BUY`, `CREDIT_SELL`, `CREDIT_FIN_BUY`, `CREDIT_SLO_SELL`, `CREDIT_BUY_SECU_REPAY`, `CREDIT_DIRECT_SECU_REPAY`, `CREDIT_SELL_SECU_REPAY`, `CREDIT_DIRECT_CASH_REPAY`
- Futures common forms: `FUTURE_OPEN_LONG`, `FUTURE_CLOSE_LONG_HISTORY`, `FUTURE_CLOSE_LONG_TODAY`, `FUTURE_OPEN_SHORT`, `FUTURE_CLOSE_SHORT_HISTORY`, `FUTURE_CLOSE_SHORT_TODAY`
- ETF: `ETF_PURCHASE`, `ETF_REDEMPTION`
- Stock options include `STOCK_OPTION_BUY_OPEN`, `STOCK_OPTION_SELL_CLOSE`, `STOCK_OPTION_SELL_OPEN`, `STOCK_OPTION_BUY_CLOSE`, covered and exercise constants.

### Price Types

- `xtconstant.LATEST_PRICE`: latest price
- `xtconstant.FIX_PRICE`: fixed/limit price
- Market price constants vary by exchange and may only work in real trading environments, not simulation. Examples include `MARKET_BEST`, `MARKET_CANCEL`, `MARKET_CANCEL_ALL`, `MARKET_CANCEL_1`, `MARKET_CANCEL_5`, `MARKET_CONVERT_1`, `MARKET_CONVERT_5`.

## System Methods

```python
XtQuantTrader(path, session_id, callback=None)
register_callback(callback)
start()
connect()
stop()
run_forever()
set_relaxed_response_order_enabled(enabled)
```

## Operation APIs

### Account Subscription

```python
subscribe(account)
unsubscribe(account)
```

- `subscribe` pushes fund, order, trade, position, and account updates.
- Success returns `0`, failure returns `-1`.

### Stock Orders

```python
order_stock(account, stock_code, order_type, order_volume, price_type, price, strategy_name, order_remark)
order_stock_async(account, stock_code, order_type, order_volume, price_type, price, strategy_name, order_remark)
```

- `order_stock` returns an order id. Successful order id is a positive integer; `-1` means failure.
- `order_stock_async` returns a request sequence id. Successful seq is a positive integer; `-1` means failure.
- Async order feedback arrives through `on_order_stock_async_response`.
- Order failures can arrive through `on_order_error`.

### Cancellation

```python
cancel_order_stock(account, order_id)
cancel_order_stock_sysid(account, market, order_sysid)
cancel_order_stock_async(account, order_id)
cancel_order_stock_sysid_async(account, market, order_sysid)
```

- Sync cancellation returns `0` when the cancellation instruction is sent successfully, `-1` on failure.
- For futures, `order_id` may correspond to the `order_sysid` field in order data.
- Async cancellation feedback can arrive through cancel response/error callbacks depending on the method and version.

### Fund Transfer and External Data

```python
fund_transfer(account, transfer_direction, price)
sync_transaction_from_external(account, sync_transaction_list)
```

These are operational APIs. Do not use them as diagnostics.

## Stock Query APIs

```python
query_stock_asset(account)
query_stock_order(account, order_id)
query_stock_orders(account, cancelable_only=False)
query_stock_trade(account, trade_id)
query_stock_trades(account)
query_stock_position(account, stock_code)
query_stock_positions(account)
query_position_statistics(account)
```

Common returns:

- `query_stock_asset`: `XtAsset`
- `query_stock_order`: `XtOrder`
- `query_stock_orders`: list of `XtOrder`
- `query_stock_trade`: `XtTrade`
- `query_stock_trades`: list of `XtTrade`
- `query_stock_position`: `XtPosition`
- `query_stock_positions`: list of `XtPosition`
- `query_position_statistics`: list of `XtPositionStatistics`

## Credit Query APIs

```python
query_credit_detail(account)
query_stk_compacts(account)
query_credit_subjects(account)
query_credit_slo_code(account)
query_credit_assure(account)
```

Use for margin/credit account assets, liabilities, financing/securities-lending subjects, lendable securities, and collateral queries only when the broker account has credit permissions.

## Other Query APIs

```python
query_new_purchase_limit(account)
query_ipo_data()
query_account_infos()
query_account_status()
query_com_fund(account)
query_com_position(account)
export_data(account, result_path, data_type, start_time=None, end_time=None, user_param={})
query_data(account, result_path, data_type, start_time=None, end_time=None, user_param={})
```

- `query_ipo_data` returns current IPO/convertible-bond subscription info keyed by code.
- `query_account_infos` returns all fund account info objects.
- `query_account_status` returns account status objects.
- `export_data` writes a CSV and returns a result dict.
- `query_data` exports, reads, then deletes the exported file and returns the data.

## Securities Lending Appointment APIs

```python
smt_query_quoter(account)
smt_negotiate_order_async(account, src_group_id, order_code, date, amount, apply_rate, dict_param={})
smt_query_compact(account)
```

- `smt_query_quoter`: query securities lending source quotes when enabled.
- `smt_negotiate_order_async`: create an asynchronous inventory securities-lending appointment. This is an operational API, not a diagnostic.
- `smt_query_compact`: query lending appointment contracts when enabled.

## Callback Class

Subclass `XtQuantTraderCallback` and override needed methods:

```python
class MyCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print("connection lost")

    def on_account_status(self, status):
        print(status.account_id, status.account_type, status.status)

    def on_stock_order(self, order):
        print(order.stock_code, order.order_status, order.order_sysid)

    def on_stock_trade(self, trade):
        print(trade.account_id, trade.stock_code, trade.order_id)

    def on_order_error(self, order_error):
        print(order_error.order_id, order_error.error_id, order_error.error_msg)

    def on_cancel_error(self, cancel_error):
        print(cancel_error.order_id, cancel_error.error_id, cancel_error.error_msg)

    def on_order_stock_async_response(self, response):
        print(response.account_id, response.order_id, response.seq)

    def on_smt_appointment_async_response(self, response):
        print(response.account_id, response.order_sysid, response.error_id, response.error_msg, response.seq)
```

## Data Structures

Common structures listed by the official docs include:

- `XtAsset`: account asset information
- `XtOrder`: order information
- `XtTrade`: trade/fill information
- `XtPosition`: position information
- `XtPositionStatistics`: futures position statistics
- `XtOrderResponse`: async order response
- `XtCancelOrderResponse`: async cancellation response
- `XtOrderError`: order failure
- `XtCancelError`: cancellation failure
- `XtCreditDetail`, `StkCompacts`, `CreditSubjects`, `CreditSloCode`, `CreditAssure`
- `XtAccountStatus`, `XtAccountInfo`
- `XtSmtAppointmentResponse`

## Minimal Safe Query Example

```python
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

class Callback(XtQuantTraderCallback):
    def on_disconnected(self):
        print("connection lost")

path = r'D:\...\userdata_mini'
session_id = 123456
account = StockAccount('1000000365')

trader = XtQuantTrader(path, session_id)
trader.register_callback(Callback())
trader.start()

if trader.connect() != 0:
    raise RuntimeError("XtQuantTrader connect failed")

if trader.subscribe(account) != 0:
    raise RuntimeError("account subscribe failed")

asset = trader.query_stock_asset(account)
print(asset.cash if asset else None)
trader.stop()
```

## Live Order Example Pattern

Only use this pattern when the user explicitly asks to place orders:

```python
order_id = trader.order_stock(
    account,
    '600000.SH',
    xtconstant.STOCK_BUY,
    1000,
    xtconstant.FIX_PRICE,
    10.5,
    'strategy1',
    'order_test',
)
```

Prefer async order APIs when you need to correlate request `seq` with callback feedback.
