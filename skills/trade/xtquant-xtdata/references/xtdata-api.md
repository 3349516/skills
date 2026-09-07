# XtQuant.XtData API Reference

Source: XtQuant native API page, `https://dict.thinktrader.net/nativeApi/xtdata.html`. This reference is adapted for broker MiniQMT usage. Do not assume VIP/full-data terminal permissions unless the user confirms them.

## Mental Model

`xtdata` talks to the local MiniQMT/QMT client. In this project, assume a broker-distributed MiniQMT client. Historical daily/minute/tick availability, special periods, Level2, whole-market push, futures/options, and full-data functions depend on the broker package, market permission, and local client version. For historical retrieval, ensure the local client has the required data first; if not, download/supplement data before calling getters.

## Broker MiniQMT Baseline

Prefer these as the default capability set:

- Import and inspect `xtquant.xtdata`.
- Query normal A-share contract metadata with `get_instrument_detail`.
- Download/query ordinary K-line data with `download_history_data`, `download_history_data2`, `get_market_data_ex`, or `get_local_data`.
- Use `subscribe_quote` for a modest number of symbols when real-time quotes are needed.
- Use trading-calendar, sector, and financial-data APIs only after confirming the broker package provides the relevant data.

Treat these as extended or permission-dependent:

- `subscribe_whole_quote`, `get_full_tick`, `get_full_kline`
- Level2 fields and `l2*` periods
- Futures/options/history-contract special periods
- Northbound, interactive Q&A, transaction-count, and other special topic periods

## Common Types

- `stock_code`: `code.market`, examples: `000001.SZ`, `600000.SH`, `000300.SH`.
- `period`: `tick`, `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1w`, `1mon`, `1q`, `1hy`, `1y`.
- Special periods include `warehousereceipt`, `futureholderrank`, `interactiveqa`, `transactioncount1m`, `transactioncount1d`, `northfinancechange1m`, `northfinancechange1d`, `dividendplaninfo`, `historycontract`, `optionhistorycontract`, `historymaincontract`, `stoppricedata`, `snapshotindex`.
- Time range: `[start_time, end_time]`, limited by `count`. Empty start means earliest, empty end means latest, `count=-1` means all.
- `dividend_type`: `none`, `front`, `back`, `front_ratio`, `back_ratio`.

## API Map

### Subscription and Real-Time

```python
subscribe_quote(stock_code, period='1d', start_time='', end_time='', count=0, callback=None)
subscribe_whole_quote(code_list, callback=None)
unsubscribe_quote(seq)
run()
```

- `subscribe_quote` subscribes one instrument and returns a positive subscription id on success, `-1` on failure. Callback shape: `{stock_code: [data1, data2, ...]}`.
- `subscribe_whole_quote` subscribes whole-market/full-push tick snapshots when supported by the client and permission package. `code_list` can contain market codes like `['SH', 'SZ']` or specific contracts. Callback shape: `{stock_code: data}`.
- `run()` blocks the current thread to keep receiving callbacks.
- Single-stock subscriptions should stay modest. For many instruments, first verify that the broker MiniQMT package supports the required whole-quote/full-push mode.

### Formula/VBA Model APIs

```python
subscribe_formula(formula_name, stock_code, period, start_time='', end_time='', count=-1, dividend_type=None, extend_param={}, callback=None)
unsubscribe_formula(subID)
call_formula(formula_name, stock_code, period, start_time='', end_time='', count=-1, dividend_type='none', extend_param={})
call_formula_batch(formula_names, stock_codes, period, start_time='', end_time='', count=-1, dividend_type='none', extend_params=[])
```

- Requires local K-line/tick data to be present.
- `extend_param` can include model parameters and optional `__basket` weights.
- `call_formula` returns a dict with data type, time list, and output variables.

### Market Data Retrieval

```python
get_market_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)
get_market_data_ex(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)
get_local_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)
get_full_tick(code_list)
get_divid_factors(stock_code, start_time='', end_time='')
get_full_kline(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)
```

Typical return shapes:

- K-line `get_market_data`: `{field: pd.DataFrame}`, each frame index is `stock_list`, columns are `time_list`.
- Tick `get_market_data`: `{stock_code: np.ndarray}` or equivalent list-like tick records.
- `get_market_data_ex`: commonly easier for per-stock processing, returning `{stock_code: pd.DataFrame}` for K-line periods.
- `get_full_tick`: latest full-push tick snapshot keyed by contract when supported.

### Data Download / Supplement

```python
download_history_data(stock_code, period='1d', start_time='', end_time='', incrementally=None)
download_history_data2(stock_list, period='1d', start_time='', end_time='', callback=None)
download_history_contracts()
download_cb_data()
download_etf_info()
download_holiday_data()
```

- Download before querying local historical data if the cache may be incomplete.
- `download_history_data2` callback reports progress, typically including total, finished, stockcode, and message.

### Calendar and Trading Days

```python
get_holidays()
get_trading_calendar(market, start_time='', end_time='')
get_trading_dates(market, start_time='', end_time='', count=-1)
get_trading_time(stockcode)
```

- `get_trading_calendar` returns calendar/trading-day information for a market.
- `get_trading_dates` returns trading date list for a market and range.

### Convertible Bonds, IPO, ETF

```python
get_cb_info(stockcode='')
get_ipo_info()
get_period_list()
get_etf_info(stockCode)
```

- `download_cb_data` is needed before complete convertible-bond metadata queries.
- `download_etf_info` is needed before complete ETF creation/redemption info queries.

### Financial Data

```python
get_financial_data(stock_list, table_list=[], start_time='', end_time='', report_type='report_time')
download_financial_data(stock_list, table_list=[])
download_financial_data2(stock_list, table_list=[], start_time='', end_time='', callback=None)
```

Financial tables:

- `Balance`: balance sheet
- `Income`: income statement
- `CashFlow`: cash-flow statement
- `Capital`: capital/share table
- `Holdernum`: shareholder count
- `Top10holder`: top 10 holders
- `Top10flowholder`: top 10 tradable holders
- `Pershareindex`: per-share indicators

Return shape for `get_financial_data`: `{stock_code: {table_name: pd.DataFrame}}`.

### Contract and Sector Metadata

```python
get_instrument_detail(stock_code, iscomplete=False)
get_instrument_type(stock_code)
get_sector_list()
get_stock_list_in_sector(sector_name, real_timetag=0)
download_sector_data()
add_sector_folder(folder_name)
add_sector(sector_name)
add_sector_stock(sector_name, stock_list)
remove_sector_stock(sector_name, stock_list)
remove_sector(sector_name)
reset_sector()
get_index_weight(index_code)
download_index_weight()
```

`get_instrument_detail(..., iscomplete=False)` returns core fields such as exchange id, instrument id/name, product id/name, dates, previous close, settlement, limit prices, capital/volume fields, margin ratios, price tick, contract multiplier, main-contract marker, instrument status, and trading flags. `iscomplete=True` adds more fields such as fee and option details.

## Field Lists

### Tick

`time`, `lastPrice`, `open`, `high`, `low`, `lastClose`, `amount`, `volume`, `pvolume`, `stockStatus`, `openInt`, `lastSettlementPrice`, `askPrice`, `bidPrice`, `askVol`, `bidVol`, `transactionNum`.

### K-Line

`time`, `open`, `high`, `low`, `close`, `volume`, `amount`, `settelementPrice`, `openInterest`, `preClose`, `suspendFlag`.

### Dividend Factors

`interest`, `stockBonus`, `stockGift`, `allotNum`, `allotPrice`, `gugai`, `dr`.

### Level2

Level2 fields require the corresponding market data permission and may be unavailable in broker MiniQMT packages.

- `l2quote`: `time`, `lastPrice`, `open`, `high`, `low`, `amount`, `volume`, `pvolume`, `openInt`, `stockStatus`, `transactionNum`, `lastClose`, `lastSettlementPrice`, `settlementPrice`, `pe`, `askPrice`, `bidPrice`, `askVol`, `bidVol`.
- `l2order`: `time`, `price`, `volume`, `entrustNo`, `entrustType`, `entrustDirection`.
- `l2transaction`: `time`, `price`, `volume`, `amount`, `tradeIndex`, `buyNo`, `sellNo`, `tradeType`, `tradeFlag`.
- `l2quoteaux`: `time`, `avgBidPrice`, `totalBidQuantity`, `avgOffPrice`, `totalOffQuantity`, `withdrawBidQuantity`, `withdrawBidAmount`, `withdrawOffQuantity`, `withdrawOffAmount`.

## Examples

### Download and Query Daily K-Line

```python
from xtquant import xtdata

stock = '000001.SZ'
xtdata.download_history_data(stock, period='1d', start_time='20240101', end_time='20240131')
data = xtdata.get_market_data_ex(['open', 'high', 'low', 'close'], [stock], period='1d')
df = data[stock]
print(df.tail())
```

### Subscribe to One Symbol

```python
from xtquant import xtdata

def on_data(datas):
    for stock_code, rows in datas.items():
        print(stock_code, rows[-1] if isinstance(rows, list) and rows else rows)

seq = xtdata.subscribe_quote('000001.SZ', period='tick', count=0, callback=on_data)
if seq <= 0:
    raise RuntimeError('subscribe_quote failed')
xtdata.run()
```

### Inspect Contract Metadata

```python
from xtquant import xtdata

detail = xtdata.get_instrument_detail('000001.SZ', False)
print(detail)
```
