---
name: ptrade-strategy
description: 使用离线 PTrade API 文档编写、改写、审查和排查 PTrade Python 策略。适用于 initialize、before_trading_start、handle_data、after_trading_end、tick_data、定时任务、行情查询、委托下单、持仓与账户对象等 PTrade 策略开发任务，以及要求策略可从回测无缝迁移到 PTrade 模拟盘或实盘的场景。
---

# PTrade 策略开发

## 工作流

1. 先读取 `references/api-index.md`，定位生命周期和目标 API 所在章节；索引只用于导航，不能作为接口存在或签名正确的依据。
2. 必须在 `references/api-reference.md` 中找到目标 API 的标题，并逐项核对使用场景、函数签名、参数、返回值和注意事项后再写代码。
3. 需要完整策略结构或实战写法时，再参考仓库的 `strategies/PTradeDemo/`；接口签名冲突时以离线官方文档为准。
4. 只使用离线文档中明确存在的接口、参数和对象字段；不要凭其他平台经验补写同名 API。
5. 输出标准 PTrade 顶层函数，不包装为自定义 `Strategy` 类。
6. 默认以回测、模拟盘和实盘共用同一份策略源码为目标；平台差异必须集中隔离，并明确标注。
7. 完成后运行静态语法检查，并逐项核对生命周期、证券代码、频率、复权、下单单位、停牌涨跌停和异常处理。

## 编写约束

- 必须提供 `initialize(context)` 和 `handle_data(context, data)`。
- 仅在确有需求时添加 `before_trading_start`、`after_trading_end`、`tick_data` 和委托成交回调。
- 初始化、基准、股票池和调度注册放在 `initialize`；不要在每个行情周期重复注册。
- `set_commission`、`set_fixed_slippage` 和 `set_slippage` 仅用于回测；共用源码必须通过 `is_trade()` 隔离回测专用设置。
- A 股证券代码按文档规定的交易所后缀格式书写。
- 下单前检查可用资金、可卖数量、停牌、涨跌停和最小交易单位。
- 历史行情字段、返回结构和时间范围必须以离线接口文档为准。
- 不使用未来数据，不在策略中读取回测结束时点之后的数据。
- 禁止引入仅本地存在、PTrade 环境无法导入的第三方依赖。
- 本地示例出现乱码、接口名与官方文档不一致或缺少场景限制时，不得复制该写法。

## 文档导航

- `references/api-index.md`：生命周期、常用接口分类、检索关键词和来源信息。
- `references/api-reference.md`：从 PTrade 官方帮助页生成的完整离线文本。
- `strategies/PTradeDemo/`：项目内实战示例，仅用于参考策略结构和常见组合方式。
- `scripts/refresh_api_reference.py`：仅在用户明确要求更新文档时运行；平时不要再次访问网页。

文档原始地址：`http://180.169.107.9:7766/hub/help/api`
