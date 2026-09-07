#coding:gbk

STRATEGY_NAME = "signal_qmt_strategy"
ACCOUNT_ID = "6000000000"
ACCOUNT_TYPE = "STOCK"
UNIVERSE = ["510300.SH", "159915.SZ"]
BAR_PERIOD = "1d"
LOOKBACK = 30
ORDER_VOLUME = 100


def init(ContextInfo):
    ContextInfo.strategy_name = STRATEGY_NAME
    ContextInfo.account_id = ACCOUNT_ID
    ContextInfo.account_type = ACCOUNT_TYPE
    ContextInfo.universe = list(UNIVERSE)
    ContextInfo.bar_period = BAR_PERIOD
    ContextInfo.lookback = LOOKBACK
    ContextInfo.order_volume = ORDER_VOLUME
    ContextInfo.last_processed_bar = -1
    ContextInfo.pending_remarks = set()

    ContextInfo.set_universe(ContextInfo.universe)
    ContextInfo.set_account(ContextInfo.account_id)

    if not ContextInfo.do_back_test:
        ContextInfo.run_time("sync_runtime_state", "30nSecond", "2000-01-01 09:30:00", "SH")


def handlebar(ContextInfo):
    if not should_process_bar(ContextInfo):
        return

    data_map = load_market_state(ContextInfo)
    if not data_map:
        return

    actions = build_actions(ContextInfo, data_map)
    for action in actions:
        if not can_submit(ContextInfo, action):
            continue
        submit_stock_order(
            ContextInfo,
            action["stock_code"],
            action["op_type"],
            action["volume"],
            action["remark"],
        )


def sync_runtime_state(ContextInfo):
    print("runtime heartbeat:", ContextInfo.strategy_name)


def stop(ContextInfo):
    print("stop:", ContextInfo.strategy_name)


def order_callback(ContextInfo, orderInfo):
    remark = getattr(orderInfo, "m_strRemark", "")
    if remark in ContextInfo.pending_remarks:
        ContextInfo.pending_remarks.discard(remark)
    print("order callback:", remark)


def deal_callback(ContextInfo, dealInfo):
    remark = getattr(dealInfo, "m_strRemark", "")
    if remark in ContextInfo.pending_remarks:
        ContextInfo.pending_remarks.discard(remark)
    print("deal callback:", remark)


def should_process_bar(ContextInfo):
    if ContextInfo.barpos <= ContextInfo.last_processed_bar:
        return False
    ContextInfo.last_processed_bar = ContextInfo.barpos
    return True


def load_market_state(ContextInfo):
    data = ContextInfo.get_market_data_ex(
        ["close"],
        ContextInfo.universe,
        period=ContextInfo.bar_period,
        start_time="",
        end_time="",
        count=ContextInfo.lookback,
        dividend_type="front",
        fill_data=True,
        subscribe=not ContextInfo.do_back_test,
    )

    result = {}
    for stock_code in ContextInfo.universe:
        if stock_code not in data:
            continue
        frame = data[stock_code]
        if "close" not in frame:
            continue
        closes = list(frame["close"])
        if len(closes) < ContextInfo.lookback:
            continue
        result[stock_code] = {
            "close_series": closes,
            "latest_close": closes[-1],
            "ma5": average(closes[-5:]),
            "ma20": average(closes[-20:]),
        }
    return result


def build_actions(ContextInfo, data_map):
    actions = []
    positions = get_position_map(ContextInfo)

    for stock_code, metrics in data_map.items():
        has_pos = positions.get(stock_code, 0) > 0
        if metrics["ma5"] > metrics["ma20"] and not has_pos:
            actions.append(
                {
                    "stock_code": stock_code,
                    "op_type": 23,
                    "volume": ContextInfo.order_volume,
                    "remark": "buy-" + stock_code,
                }
            )
        elif metrics["ma5"] < metrics["ma20"] and has_pos:
            actions.append(
                {
                    "stock_code": stock_code,
                    "op_type": 24,
                    "volume": positions[stock_code],
                    "remark": "sell-" + stock_code,
                }
            )
    return actions


def can_submit(ContextInfo, action):
    if action["remark"] in ContextInfo.pending_remarks:
        return False
    if action["op_type"] == 23 and not has_enough_cash(ContextInfo, action["stock_code"], action["volume"]):
        return False
    return True


def submit_stock_order(ContextInfo, stock_code, op_type, volume, remark):
    ContextInfo.pending_remarks.add(remark)
    passorder(
        op_type,
        1101,
        ContextInfo.account_id,
        stock_code,
        5,
        0,
        volume,
        ContextInfo.strategy_name,
        0,
        remark,
        ContextInfo,
    )


def get_position_map(ContextInfo):
    result = {}
    positions = get_trade_detail_data(
        ContextInfo.account_id,
        ContextInfo.account_type,
        "POSITION",
    )
    if not positions:
        return result
    for item in positions:
        result[item.m_strInstrumentID] = item.m_nVolume
    return result


def has_enough_cash(ContextInfo, stock_code, volume):
    data = ContextInfo.get_market_data_ex(
        ["close"],
        [stock_code],
        period=ContextInfo.bar_period,
        start_time="",
        end_time="",
        count=1,
        dividend_type="front",
        fill_data=True,
        subscribe=not ContextInfo.do_back_test,
    )
    if stock_code not in data:
        return False
    frame = data[stock_code]
    if "close" not in frame or len(frame["close"]) == 0:
        return False
    latest = frame["close"].iloc[-1]
    cash = get_available_cash(ContextInfo)
    return cash >= float(latest) * float(volume)


def get_available_cash(ContextInfo):
    accounts = get_trade_detail_data(
        ContextInfo.account_id,
        ContextInfo.account_type,
        "ACCOUNT",
    )
    if not accounts:
        return 0
    return getattr(accounts[0], "m_dAvailable", 0)


def average(values):
    if not values:
        return 0
    return sum(values) / float(len(values))
