#!/usr/bin/env python
"""Check local XtQuant XtData availability.

Default mode is read-only import/introspection for a broker MiniQMT baseline.
Use --include-extended to inspect permission/client-version dependent APIs.
Use --connect to call xtdata.connect() when MiniQMT should be running locally.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import sys
from typing import Any


DEFAULT_FUNCTIONS = [
    "connect",
    "reconnect",
    "subscribe_quote",
    "unsubscribe_quote",
    "run",
    "get_market_data",
    "get_market_data_ex",
    "get_local_data",
    "download_history_data",
    "download_history_data2",
    "get_financial_data",
    "download_financial_data",
    "download_financial_data2",
    "get_instrument_detail",
    "get_instrument_type",
    "get_trading_calendar",
    "get_trading_dates",
    "get_sector_list",
    "get_stock_list_in_sector",
    "download_sector_data",
    "get_index_weight",
    "download_index_weight",
]

EXTENDED_FUNCTIONS = [
    "subscribe_whole_quote",
    "get_full_tick",
    "get_full_kline",
]


def stringify(value: Any) -> str:
    try:
        return str(value)
    except Exception as exc:  # pragma: no cover - defensive
        return f"<unprintable {type(value).__name__}: {exc}>"


def get_signature(func: Any) -> str:
    try:
        return str(inspect.signature(func))
    except Exception:
        return "<signature unavailable>"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check XtQuant xtdata import, broker MiniQMT baseline functions, and optional connectivity.")
    parser.add_argument("--connect", action="store_true", help="Call xtdata.connect() after import.")
    parser.add_argument("--probe-code", default="", help="Call get_instrument_detail(PROBE_CODE, False) after optional connect.")
    parser.add_argument("--functions", nargs="*", default=DEFAULT_FUNCTIONS, help="Function names to check and print signatures for.")
    parser.add_argument("--include-extended", action="store_true", help="Also inspect extended/permission-dependent APIs such as whole quote and full tick.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    result: dict[str, Any] = {
        "python": sys.version,
        "import_xtquant": False,
        "import_xtdata": False,
        "xtquant_version": None,
        "functions": {},
        "connect": {"attempted": False, "ok": None, "result": None, "error": None},
        "probe": {"attempted": False, "code": args.probe_code, "ok": None, "result_preview": None, "error": None},
    }

    try:
        xtquant = importlib.import_module("xtquant")
        result["import_xtquant"] = True
        result["xtquant_version"] = getattr(xtquant, "__version__", None)
    except Exception as exc:
        result["import_error"] = stringify(exc)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"FAIL import xtquant: {exc}")
        return 2

    try:
        xtdata = importlib.import_module("xtquant.xtdata")
        result["import_xtdata"] = True
    except Exception as exc:
        result["import_error"] = stringify(exc)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"FAIL import xtquant.xtdata: {exc}")
        return 2

    functions = list(dict.fromkeys(args.functions + (EXTENDED_FUNCTIONS if args.include_extended else [])))

    for name in functions:
        obj = getattr(xtdata, name, None)
        result["functions"][name] = {
            "exists": obj is not None,
            "callable": callable(obj),
            "signature": get_signature(obj) if callable(obj) else None,
        }

    if args.connect:
        result["connect"]["attempted"] = True
        connect = getattr(xtdata, "connect", None)
        if not callable(connect):
            result["connect"]["ok"] = False
            result["connect"]["error"] = "xtdata.connect is unavailable"
        else:
            try:
                value = connect()
                result["connect"]["ok"] = True
                result["connect"]["result"] = stringify(value)
            except Exception as exc:
                result["connect"]["ok"] = False
                result["connect"]["error"] = stringify(exc)

    if args.probe_code:
        result["probe"]["attempted"] = True
        getter = getattr(xtdata, "get_instrument_detail", None)
        if not callable(getter):
            result["probe"]["ok"] = False
            result["probe"]["error"] = "xtdata.get_instrument_detail is unavailable"
        else:
            try:
                value = getter(args.probe_code, False)
                result["probe"]["ok"] = value is not None
                result["probe"]["result_preview"] = stringify(value)[:1200]
            except Exception as exc:
                result["probe"]["ok"] = False
                result["probe"]["error"] = stringify(exc)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Python: {result['python'].split()[0]}")
        print(f"xtquant import: {'OK' if result['import_xtquant'] else 'FAIL'}")
        print(f"xtdata import: {'OK' if result['import_xtdata'] else 'FAIL'}")
        print(f"xtquant version: {result['xtquant_version'] or '<unknown>'}")
        print("Functions:")
        for name, info in result["functions"].items():
            status = "OK" if info["exists"] and info["callable"] else "MISSING"
            sig = f" {info['signature']}" if info["signature"] else ""
            print(f"  {status} {name}{sig}")
        if result["connect"]["attempted"]:
            status = "OK" if result["connect"]["ok"] else "FAIL"
            detail = result["connect"]["result"] or result["connect"]["error"]
            print(f"connect: {status} {detail}")
        if result["probe"]["attempted"]:
            status = "OK" if result["probe"]["ok"] else "FAIL"
            detail = result["probe"]["result_preview"] or result["probe"]["error"]
            print(f"probe {args.probe_code}: {status} {detail}")

    if result["connect"]["attempted"] and not result["connect"]["ok"]:
        return 3
    if result["probe"]["attempted"] and not result["probe"]["ok"]:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
