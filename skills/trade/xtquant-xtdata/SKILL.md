---
name: xtquant-xtdata
description: XtQuant.XtData 行情模块 API 查询与本机可用性检测。Use when Codex needs to answer questions about xtquant.xtdata functions, parameters, return shapes, periods, fields, data download/subscription workflows, or check whether the local Python environment can import xtquant and connect/query MiniQMT/XtData.
---

# XtQuant XtData

Use this skill for broker MiniQMT XtQuant `xtdata` market-data work: API lookup, usage examples, return-shape checks, and local environment diagnosis. Assume a normal broker-distributed MiniQMT client, not a VIP/full-data terminal, unless the user says otherwise.

## Quick Workflow

1. For API questions, read `references/xtdata-api.md` first and answer from that reference. If the user asks for a function not listed there, inspect the local `xtquant.xtdata` module with Python or consult the official page: `https://dict.thinktrader.net/nativeApi/xtdata.html`.
2. For local diagnostics, run `scripts/check_xtdata.py` with the narrowest needed flags.
3. For data retrieval guidance, always distinguish:
   - Historical/local cache: call `download_history_data` or another download API first, then query with `get_market_data_ex` or related getters.
   - Real-time flow: prefer `subscribe_quote` for a small symbol set, then keep the process alive with `run()` or user code.
   - Static metadata: contract/sector/calendar APIs are low-frequency; avoid unnecessary repeated downloads.
4. For broker MiniQMT compatibility, do not assume Level2, whole-market/full-push, full K-line, futures/options, or special topic data is available. Treat those as permission/client-version dependent.
5. For risky or live-market checks, prefer import/introspection checks before connection checks. Ask before adding long-running subscriptions.

## Local Detection

Run from the skill folder or pass the script path directly:

```powershell
python .\skills\xtquant-xtdata\scripts\check_xtdata.py
```

Useful options:

```powershell
python .\skills\xtquant-xtdata\scripts\check_xtdata.py --functions get_market_data_ex download_history_data
python .\skills\xtquant-xtdata\scripts\check_xtdata.py --include-extended
python .\skills\xtquant-xtdata\scripts\check_xtdata.py --connect
python .\skills\xtquant-xtdata\scripts\check_xtdata.py --connect --probe-code 000001.SZ
```

Interpretation:

- Import failure usually means `xtquant` is not installed in the active Python environment.
- Connection failure usually means MiniQMT/QMT is not running, the local data service is unavailable, or account/data permissions are missing.
- `get_instrument_detail` returning `None` for a probe code can mean missing contract metadata, unsupported market, or no active data connection.

## Common Guidance

- Stock codes use `code.market`, for example `000001.SZ`, `600000.SH`, `000300.SH`.
- Common level1 periods include `tick`, `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1w`, `1mon`, `1q`, `1hy`, `1y`.
- K-line dividend types include `none`, `front`, `back`, `front_ratio`, `back_ratio`.
- Time ranges are inclusive: `[start_time, end_time]`, with `count` limiting the number of returned rows. `count=-1` means all matching data; large ranges can be slow.
- For many symbols, first verify the broker MiniQMT client supports the required subscription mode. Do not assume whole-market/full-push APIs are available.

## Reference Files

- `references/xtdata-api.md`: curated API map, key signatures, return shapes, field lists, and examples.
