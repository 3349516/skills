#coding:gbk

STRATEGY_NAME = "basic_qmt_strategy"
ACCOUNT_ID = "6000000000"
ACCOUNT_TYPE = "STOCK"
UNIVERSE = ["510300.SH"]
BAR_PERIOD = "1d"
LOOKBACK = 20
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
    ContextInfo.last_order_remark = ""

    ContextInfo.set_universe(ContextInfo.universe)
    ContextInfo.set_account(ContextInfo.account_id)


def handlebar(ContextInfo):
    if not should_process_bar(ContextInfo):
        return

    code = ContextInfo.universe[0]
    closes = get_close_series(ContextInfo, code, ContextInfo.lookback)
    if len(closes) < ContextInfo.lookback:
        return

    signal = generate_signal(closes)
    if signal == "BUY" and not has_position(ContextInfo, code):
        submit_order(ContextInfo, code, 23, ContextInfo.order_volume, "basic-buy")
    elif signal == "SELL" and has_position(ContextInfo, code):
        submit_order(ContextInfo, code, 24, ContextInfo.order_volume, "basic-sell")


def stop(ContextInfo):
    print("strategy stopped:", ContextInfo.strategy_name)


def order_callback(ContextInfo, orderInfo):
    print("order callback:", getattr(orderInfo, "m_strRemark", ""))


def deal_callback(ContextInfo, dealInfo):
    print("deal callback:", getattr(dealInfo, "m_strRemark", ""))


def should_process_bar(ContextInfo):
    if ContextInfo.barpos <= ContextInfo.last_processed_bar:
        return False
    ContextInfo.last_processed_bar = ContextInfo.barpos
    return True


def get_close_series(ContextInfo, stock_code, count):
    data = ContextInfo.get_market_data_ex(
        ["close"],
        [stock_code],
        period=ContextInfo.bar_period,
        start_time="",
        end_time="",
        count=count,
        dividend_type="front",
        fill_data=True,
        subscribe=not ContextInfo.do_back_test,
    )
    if stock_code not in data:
        return []
    frame = data[stock_code]
    if "close" not in frame:
        return []
    return list(frame["close"])


def generate_signal(closes):
    short_ma = average(closes[-5:])
    long_ma = average(closes)
    if short_ma > long_ma:
        return "BUY"
    if short_ma < long_ma:
        return "SELL"
    return "HOLD"


def has_position(ContextInfo, stock_code):
    positions = get_trade_detail_data(
        ContextInfo.account_id,
        ContextInfo.account_type,
        "POSITION",
    )
    if not positions:
        return False
    for item in positions:
        if item.m_strInstrumentID == stock_code and item.m_nVolume > 0:
            return True
    return False


def submit_order(ContextInfo, stock_code, op_type, volume, remark):
    ContextInfo.last_order_remark = remark
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


def average(values):
    if not values:
        return 0
    return sum(values) / float(len(values))
