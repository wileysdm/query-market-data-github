#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
from pathlib import Path

import clickhouse_connect


ALLOWED_TABLES = [
    "market_data.aave_loan",
    "market_data.binance_notice",
    "market_data.binance_open_interest_1h",
    "market_data.cex_flow_1h",
    "market_data.economic_calendar",
    "market_data.eth_staking_data_1h",
    "market_data.evm_basic_data_1h",
    "market_data.hyperliquid_open_interest_1h",
    "market_data.hyperliquid_wallet_distribution_10m",
    "market_data.hyperliquid_whale_alert_10m",
    "market_data.hyperliquid_whale_position_10m",
    "market_data.liquidation_1h",
    "market_data.social_sentiment",
    "market_data.sol_basic_data_1h",
    "market_data.sol_staking_data_1h",
    "market_data.whale_transfer_1h",
]
ALLOWED_TABLE_SET = set(ALLOWED_TABLES)
ORDER_COLUMNS = {
    "market_data.aave_loan": "start_ts DESC, collateral_symbol ASC",
    "market_data.binance_notice": "publish_ts DESC, ingested_ts DESC",
    "market_data.binance_open_interest_1h": "start_ts DESC, unified_symbol ASC",
    "market_data.cex_flow_1h": "start_ts DESC, exchange ASC, unified_symbol ASC",
    "market_data.economic_calendar": "timestamp DESC, event ASC",
    "market_data.eth_staking_data_1h": "start_ts DESC, chain ASC",
    "market_data.evm_basic_data_1h": "start_ts DESC, chain ASC",
    "market_data.hyperliquid_open_interest_1h": "start_ts DESC, unified_symbol ASC",
    "market_data.hyperliquid_wallet_distribution_10m": "start_ts DESC, distribution_type ASC, group_name ASC",
    "market_data.hyperliquid_whale_alert_10m": "start_ts DESC, symbol ASC",
    "market_data.hyperliquid_whale_position_10m": "start_ts DESC, symbol ASC",
    "market_data.liquidation_1h": "start_ts DESC, exchange ASC, unified_symbol ASC",
    "market_data.social_sentiment": "time DESC, symbol ASC",
    "market_data.sol_basic_data_1h": "start_ts DESC, chain ASC",
    "market_data.sol_staking_data_1h": "start_ts DESC, chain ASC",
    "market_data.whale_transfer_1h": "start_ts DESC, unified_symbol ASC",
}
BLOCKED_SQL_PATTERNS = [
    r"\balter\b",
    r"\battach\b",
    r"\bcreate\b",
    r"\bdelete\b",
    r"\bdetach\b",
    r"\bdrop\b",
    r"\binsert\b",
    r"\bgrant\b",
    r"\boptimize\b",
    r"\brename\b",
    r"\brevoke\b",
    r"\bsystem\b",
    r"\btruncate\b",
    r"\bupdate\b",
]


def load_ck_config() -> dict:
    env_path = os.environ.get("MARKET_CH_CONFIG")
    candidate_paths = []
    if env_path:
        candidate_paths.append(Path(env_path))
    candidate_paths.append(Path.home() / "cex" / "ck_config.py")

    for path in candidate_paths:
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location("market_ck_config", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cfg = getattr(module, "CK_4A_MARKET", None)
        if isinstance(cfg, dict):
            return cfg

    host = os.environ.get("MARKET_CH_HOST")
    if not host:
        checked = ", ".join(str(path) for path in candidate_paths)
        raise SystemExit(
            "Could not load ClickHouse config. Set MARKET_CH_CONFIG or MARKET_CH_HOST, "
            f"or ensure one of these files exists: {checked}"
        )

    return {
        "host": host,
        "port": int(os.environ.get("MARKET_CH_PORT", "8123")),
        "username": os.environ.get("MARKET_CH_USER", "default"),
        "password": os.environ.get("MARKET_CH_PASSWORD", ""),
        "secure": os.environ.get("MARKET_CH_SECURE", "false").lower() in {"1", "true", "yes"},
        "protocol": os.environ.get("MARKET_CH_PROTOCOL", "http"),
    }


def get_client():
    cfg = load_ck_config()
    return clickhouse_connect.get_client(
        host=cfg["host"],
        port=cfg.get("port", 8123),
        username=cfg.get("username", "default"),
        password=cfg.get("password", ""),
        secure=cfg.get("secure", False),
        interface=cfg.get("protocol", "http"),
        database="default",
    )


def ensure_allowed_table(table: str) -> None:
    if table not in ALLOWED_TABLE_SET:
        allowed = ", ".join(ALLOWED_TABLES)
        raise SystemExit(f"Unsupported table: {table}\nAllowed tables: {allowed}")


def normalize_sql(sql: str) -> str:
    query = sql.strip()
    if query.endswith(";"):
        query = query[:-1].rstrip()
    if ";" in query:
        raise SystemExit("Only one SQL statement is allowed.")
    if not re.match(r"^(select|with)\b", query, flags=re.IGNORECASE):
        raise SystemExit("Only read-only SELECT / WITH queries are allowed.")
    for pattern in BLOCKED_SQL_PATTERNS:
        if re.search(pattern, query, flags=re.IGNORECASE):
            raise SystemExit(f"Blocked SQL keyword matched pattern: {pattern}")
    referenced = {
        f"market_data.{name.lower()}"
        for name in re.findall(r"market_data\.([A-Za-z0-9_]+)", query, flags=re.IGNORECASE)
    }
    if not referenced:
        raise SystemExit("Query must reference at least one allowed market_data table.")
    disallowed = sorted(table for table in referenced if table not in ALLOWED_TABLE_SET)
    if disallowed:
        raise SystemExit(f"Query references tables outside the whitelist: {', '.join(disallowed)}")
    return query


def format_rows(result, output_format: str) -> None:
    columns = list(result.column_names)
    rows = list(result.result_rows)
    if output_format == "json":
        payload = [dict(zip(columns, row)) for row in rows]
        print(json.dumps(payload, ensure_ascii=False, default=str, indent=2))
        return

    print("	".join(columns))
    for row in rows:
        print("	".join("" if value is None else str(value) for value in row))


def cmd_list_tables(_: argparse.Namespace) -> None:
    for table in ALLOWED_TABLES:
        print(table)


def cmd_describe(args: argparse.Namespace) -> None:
    ensure_allowed_table(args.table)
    client = get_client()
    result = client.query(f"DESCRIBE TABLE {args.table}")
    format_rows(result, args.format)


def cmd_sample(args: argparse.Namespace) -> None:
    ensure_allowed_table(args.table)
    client = get_client()
    columns = args.columns.strip() or "*"
    query = f"SELECT {columns} FROM {args.table}"
    if args.where:
        query += f" WHERE {args.where}"
    order_by = args.order_by or ORDER_COLUMNS.get(args.table)
    if order_by:
        query += f" ORDER BY {order_by}"
    query += f" LIMIT {args.limit:d}"
    result = client.query(query)
    format_rows(result, args.format)


def cmd_sql(args: argparse.Namespace) -> None:
    client = get_client()
    query = normalize_sql(args.query)
    result = client.query(query)
    format_rows(result, args.format)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run read-only queries against the PDF-documented market_data tables."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_tables = subparsers.add_parser("list-tables", help="List the allowed market_data tables")
    list_tables.set_defaults(func=cmd_list_tables)

    describe = subparsers.add_parser("describe", help="Describe one allowed table")
    describe.add_argument("table", help="Fully qualified table name")
    describe.add_argument("--format", choices=["tsv", "json"], default="tsv")
    describe.set_defaults(func=cmd_describe)

    sample = subparsers.add_parser("sample", help="Fetch recent rows from one allowed table")
    sample.add_argument("table", help="Fully qualified table name")
    sample.add_argument("--columns", default="*", help="Column expression list")
    sample.add_argument("--where", help="Optional SQL predicate without the WHERE keyword")
    sample.add_argument("--order-by", help="Optional ORDER BY expression")
    sample.add_argument("--limit", type=int, default=5)
    sample.add_argument("--format", choices=["tsv", "json"], default="tsv")
    sample.set_defaults(func=cmd_sample)

    sql = subparsers.add_parser("sql", help="Run one read-only SELECT / WITH query")
    sql.add_argument("query", help="Single SQL statement in quotes")
    sql.add_argument("--format", choices=["tsv", "json"], default="tsv")
    sql.set_defaults(func=cmd_sql)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
