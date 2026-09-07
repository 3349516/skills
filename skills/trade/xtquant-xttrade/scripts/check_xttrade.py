#!/usr/bin/env python
"""Check local XtQuant XtTrade availability.

Default mode is read-only import/introspection for a broker MiniQMT stock-trading
baseline. Use --include-extended to inspect account-type or permission-dependent
APIs. Connection and account queries require explicit flags. This script never
places orders, cancels orders, transfers funds, imports external trades, or
submits securities-lending applications.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import random
import sys
from typing import Any


DEFAULT_METHODS = [
    "register_callback",
    "start",
    "connect",
    "stop",
    "run_forever",
    "set_relaxed_response_order_enabled",
    "subscribe",
    "unsubscribe",
    "order_stock",
    "order_stock_async",
    "cancel_order_stock",
    "cancel_order_stock_sysid",
    "cancel_order_stock_async",
    "cancel_order_stock_sysid_async",
    "query_stock_asset",
    "query_stock_order",
    "query_stock_orders",
    "query_stock_trade",
    "query_stock_trades",
    "query_stock_position",
    "query_stock_positions",
    "query_position_statistics",
    "query_new_purchase_limit",
    "query_ipo_data",
    "query_account_infos",
    "query_account_status",
]

EXTENDED_METHODS = [
    "query_credit_detail",
    "query_stk_compacts",
    "query_credit_subjects",
    "query_credit_slo_code",
    "query_credit_assure",
    "query_com_fund",
    "query_com_position",
    "export_data",
    "query_data",
    "smt_query_quoter",
    "smt_negotiate_order_async",
    "smt_query_compact",
]

DEFAULT_CONSTANTS = [
    "STOCK_BUY",
    "STOCK_SELL",
    "FIX_PRICE",
    "LATEST_PRICE",
    "SECURITY_ACCOUNT",
]

EXTENDED_CONSTANTS = [
    "CREDIT_ACCOUNT",
    "FUTURE_ACCOUNT",
    "STOCK_OPTION_ACCOUNT",
    "HUGANGTONG_ACCOUNT",
    "SHENGANGTONG_ACCOUNT",
]

QUERY_NAMES = {
    "account_infos",
    "account_status",
    "asset",
    "orders",
    "trades",
    "positions",
    "ipo",
    "new_purchase_limit",
}


def stringify(value: Any) -> str:
    try:
        return str(value)
    except Exception as exc:  # pragma: no cover - defensive
        return f"<unprintable {type(value).__name__}: {exc}>"


def signature_of(obj: Any) -> str:
    try:
        return str(inspect.signature(obj))
    except Exception:
        return "<signature unavailable>"


def preview(value: Any, limit: int = 1500) -> str:
    text = stringify(value)
    return text if len(text) <= limit else text[:limit] + "...<truncated>"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check XtQuant xttrader imports, broker MiniQMT baseline method signatures, and optional connection/query.")
    parser.add_argument("--methods", nargs="*", default=DEFAULT_METHODS, help="XtQuantTrader method names to check.")
    parser.add_argument("--constants", nargs="*", default=DEFAULT_CONSTANTS, help="xtconstant names to check.")
    parser.add_argument("--include-extended", action="store_true", help="Also inspect account-type or permission-dependent APIs/constants.")
    parser.add_argument("--path", default="", help="MiniQMT userdata_mini path. Required for --connect.")
    parser.add_argument("--session-id", type=int, default=None, help="Session id for XtQuantTrader. Defaults to a random 6-digit id if --connect is used.")
    parser.add_argument("--connect", action="store_true", help="Instantiate XtQuantTrader, start it, and call connect().")
    parser.add_argument("--account-id", default="", help="Account id for subscribe/query checks.")
    parser.add_argument("--account-type", default="", help="Optional StockAccount account type, e.g. STOCK or CREDIT.")
    parser.add_argument("--subscribe", action="store_true", help="Call subscribe(account). Requires --connect and --account-id.")
    parser.add_argument("--query", choices=sorted(QUERY_NAMES), default=None, help="Run one safe query after --connect.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    result: dict[str, Any] = {
        "python": sys.version,
        "imports": {},
        "xtquant_version": None,
        "classes": {},
        "constants": {},
        "methods": {},
        "connect": {"attempted": False, "ok": None, "result": None, "error": None},
        "subscribe": {"attempted": False, "ok": None, "result": None, "error": None},
        "query": {"attempted": False, "name": args.query, "ok": None, "result_preview": None, "error": None},
    }

    modules: dict[str, Any] = {}
    for module_name in ["xtquant", "xtquant.xttrader", "xtquant.xttype", "xtquant.xtconstant"]:
        try:
            modules[module_name] = importlib.import_module(module_name)
            result["imports"][module_name] = {"ok": True, "error": None}
        except Exception as exc:
            result["imports"][module_name] = {"ok": False, "error": stringify(exc)}

    if not all(info["ok"] for info in result["imports"].values()):
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            for name, info in result["imports"].items():
                status = "OK" if info["ok"] else "FAIL"
                detail = "" if info["ok"] else f" {info['error']}"
                print(f"import {name}: {status}{detail}")
        return 2

    xtquant = modules["xtquant"]
    xttrader = modules["xtquant.xttrader"]
    xttype = modules["xtquant.xttype"]
    xtconstant = modules["xtquant.xtconstant"]
    result["xtquant_version"] = getattr(xtquant, "__version__", None)

    XtQuantTrader = getattr(xttrader, "XtQuantTrader", None)
    XtQuantTraderCallback = getattr(xttrader, "XtQuantTraderCallback", None)
    StockAccount = getattr(xttype, "StockAccount", None)

    for class_name, cls in {
        "XtQuantTrader": XtQuantTrader,
        "XtQuantTraderCallback": XtQuantTraderCallback,
        "StockAccount": StockAccount,
    }.items():
        result["classes"][class_name] = {
            "exists": cls is not None,
            "callable": callable(cls),
            "signature": signature_of(cls) if callable(cls) else None,
        }

    constants = list(dict.fromkeys(args.constants + (EXTENDED_CONSTANTS if args.include_extended else [])))
    methods = list(dict.fromkeys(args.methods + (EXTENDED_METHODS if args.include_extended else [])))

    for name in constants:
        exists = hasattr(xtconstant, name)
        result["constants"][name] = {
            "exists": exists,
            "value": preview(getattr(xtconstant, name), 200) if exists else None,
        }

    for name in methods:
        obj = getattr(XtQuantTrader, name, None) if XtQuantTrader is not None else None
        result["methods"][name] = {
            "exists": obj is not None,
            "callable": callable(obj),
            "signature": signature_of(obj) if callable(obj) else None,
        }

    trader = None
    account = None

    if args.connect:
        result["connect"]["attempted"] = True
        if not args.path:
            result["connect"]["ok"] = False
            result["connect"]["error"] = "--path is required for --connect"
        elif not callable(XtQuantTrader):
            result["connect"]["ok"] = False
            result["connect"]["error"] = "XtQuantTrader is unavailable"
        else:
            session_id = args.session_id if args.session_id is not None else random.randint(100000, 999999)
            try:
                trader = XtQuantTrader(args.path, session_id)
                trader.start()
                value = trader.connect()
                result["connect"]["ok"] = value == 0
                result["connect"]["result"] = stringify(value)
            except Exception as exc:
                result["connect"]["ok"] = False
                result["connect"]["error"] = stringify(exc)

    if (args.subscribe or args.query in {"asset", "orders", "trades", "positions", "new_purchase_limit"}) and not args.account_id:
        msg = "--account-id is required for subscribe/account-specific queries"
        if args.subscribe:
            result["subscribe"]["attempted"] = True
            result["subscribe"]["ok"] = False
            result["subscribe"]["error"] = msg
        if args.query:
            result["query"]["attempted"] = True
            result["query"]["ok"] = False
            result["query"]["error"] = msg

    if args.account_id and callable(StockAccount):
        try:
            account = StockAccount(args.account_id, args.account_type) if args.account_type else StockAccount(args.account_id)
        except Exception as exc:
            if args.subscribe:
                result["subscribe"]["attempted"] = True
                result["subscribe"]["ok"] = False
                result["subscribe"]["error"] = stringify(exc)
            if args.query:
                result["query"]["attempted"] = True
                result["query"]["ok"] = False
                result["query"]["error"] = stringify(exc)

    if args.subscribe and result["subscribe"]["error"] is None:
        result["subscribe"]["attempted"] = True
        if trader is None or not result["connect"]["ok"]:
            result["subscribe"]["ok"] = False
            result["subscribe"]["error"] = "--subscribe requires successful --connect"
        else:
            try:
                value = trader.subscribe(account)
                result["subscribe"]["ok"] = value == 0
                result["subscribe"]["result"] = stringify(value)
            except Exception as exc:
                result["subscribe"]["ok"] = False
                result["subscribe"]["error"] = stringify(exc)

    if args.query and result["query"]["error"] is None:
        result["query"]["attempted"] = True
        if trader is None or not result["connect"]["ok"]:
            result["query"]["ok"] = False
            result["query"]["error"] = "--query requires successful --connect"
        else:
            query_call = {
                "account_infos": lambda: trader.query_account_infos(),
                "account_status": lambda: trader.query_account_status(),
                "asset": lambda: trader.query_stock_asset(account),
                "orders": lambda: trader.query_stock_orders(account),
                "trades": lambda: trader.query_stock_trades(account),
                "positions": lambda: trader.query_stock_positions(account),
                "ipo": lambda: trader.query_ipo_data(),
                "new_purchase_limit": lambda: trader.query_new_purchase_limit(account),
            }[args.query]
            try:
                value = query_call()
                result["query"]["ok"] = True
                result["query"]["result_preview"] = preview(value)
            except Exception as exc:
                result["query"]["ok"] = False
                result["query"]["error"] = stringify(exc)

    if trader is not None:
        try:
            trader.stop()
        except Exception:
            pass

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Python: {result['python'].split()[0]}")
        print(f"xtquant version: {result['xtquant_version'] or '<unknown>'}")
        for name, info in result["imports"].items():
            print(f"import {name}: {'OK' if info['ok'] else 'FAIL'}")
        print("Classes:")
        for name, info in result["classes"].items():
            status = "OK" if info["exists"] and info["callable"] else "MISSING"
            sig = f" {info['signature']}" if info["signature"] else ""
            print(f"  {status} {name}{sig}")
        print("Constants:")
        for name, info in result["constants"].items():
            status = "OK" if info["exists"] else "MISSING"
            detail = f" = {info['value']}" if info["exists"] else ""
            print(f"  {status} {name}{detail}")
        print("Methods:")
        for name, info in result["methods"].items():
            status = "OK" if info["exists"] and info["callable"] else "MISSING"
            sig = f" {info['signature']}" if info["signature"] else ""
            print(f"  {status} {name}{sig}")
        if result["connect"]["attempted"]:
            status = "OK" if result["connect"]["ok"] else "FAIL"
            detail = result["connect"]["result"] or result["connect"]["error"]
            print(f"connect: {status} {detail}")
        if result["subscribe"]["attempted"]:
            status = "OK" if result["subscribe"]["ok"] else "FAIL"
            detail = result["subscribe"]["result"] or result["subscribe"]["error"]
            print(f"subscribe: {status} {detail}")
        if result["query"]["attempted"]:
            status = "OK" if result["query"]["ok"] else "FAIL"
            detail = result["query"]["result_preview"] or result["query"]["error"]
            print(f"query {args.query}: {status} {detail}")

    if not all(info["ok"] for info in result["imports"].values()):
        return 2
    if result["connect"]["attempted"] and not result["connect"]["ok"]:
        return 3
    if result["subscribe"]["attempted"] and not result["subscribe"]["ok"]:
        return 4
    if result["query"]["attempted"] and not result["query"]["ok"]:
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
