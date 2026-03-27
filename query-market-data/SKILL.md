---
name: 'query-market-data'
description: 'Query the documented ClickHouse `market_data` tables on this machine and answer questions about their schema, business meaning, time grain, and SQL usage. Use when Codex needs to inspect or query only these tables: `market_data.cex_flow_1h`, `market_data.whale_transfer_1h`, `market_data.evm_basic_data_1h`, `market_data.sol_basic_data_1h`, `market_data.eth_staking_data_1h`, `market_data.sol_staking_data_1h`, `market_data.aave_loan`, `market_data.social_sentiment`, `market_data.binance_notice`, `market_data.binance_open_interest_1h`, `market_data.hyperliquid_open_interest_1h`, `market_data.liquidation_1h`, `market_data.economic_calendar`, `market_data.hyperliquid_wallet_distribution_10m`, `market_data.hyperliquid_whale_position_10m`, and `market_data.hyperliquid_whale_alert_10m`.'
---

# Query Market Data

Use this skill to answer read-only questions about the PDF-documented `market_data` tables and to run live ClickHouse queries against those same tables.

## Quick Workflow

1. Confirm the request is about one or more tables in the whitelist below.
2. Read `references/tables.md` only for the table sections you need.
3. Inspect the live schema before writing non-trivial SQL:

```bash
python3 scripts/query_market_data.py describe market_data.cex_flow_1h
```

4. Use a small sample query to verify grain, time columns, and freshness:

```bash
python3 scripts/query_market_data.py sample market_data.cex_flow_1h --limit 5
```

5. Run the final read-only query with explicit UTC time filters and a `LIMIT` when appropriate:

```bash
python3 scripts/query_market_data.py sql "SELECT start_ts, exchange, unified_symbol, netflow_usd FROM market_data.cex_flow_1h WHERE start_ts >= now() - INTERVAL 24 HOUR ORDER BY start_ts DESC LIMIT 50"
```

## Whitelist

- `market_data.aave_loan`
- `market_data.binance_notice`
- `market_data.binance_open_interest_1h`
- `market_data.cex_flow_1h`
- `market_data.economic_calendar`
- `market_data.eth_staking_data_1h`
- `market_data.evm_basic_data_1h`
- `market_data.hyperliquid_open_interest_1h`
- `market_data.hyperliquid_wallet_distribution_10m`
- `market_data.hyperliquid_whale_alert_10m`
- `market_data.hyperliquid_whale_position_10m`
- `market_data.liquidation_1h`
- `market_data.social_sentiment`
- `market_data.sol_basic_data_1h`
- `market_data.sol_staking_data_1h`
- `market_data.whale_transfer_1h`

If the user asks for any other table, say this skill does not cover it.

## Query Rules

- Keep queries read-only. The helper script rejects non-`SELECT` / non-`WITH` SQL.
- Prefer the helper script over ad hoc connection code so the table whitelist stays enforced.
- Treat `ingested_at` and `ingested_ts` as load timestamps, not business timestamps.
- Use the correct time column for each table family:
  - `start_ts` / `end_ts` for hourly or 10-minute aggregates
  - `time` for `market_data.social_sentiment`
  - `timestamp` for `market_data.economic_calendar`
  - `publish_ts` or `effective_ts` for `market_data.binance_notice`
- Distinguish table shapes before aggregating:
  - Snapshot tables: `market_data.binance_open_interest_1h`, `market_data.hyperliquid_open_interest_1h`
  - Event-detail tables: `market_data.binance_notice`, `market_data.economic_calendar`
  - 10-minute aggregate tables: the three `market_data.hyperliquid_*_10m` tables
  - Hourly aggregate tables: the remaining `_1h` aggregate tables
- When the PDF mentions delayed or partial coverage, verify freshness first with `max(start_ts)`, `max(time)`, or `max(timestamp)` before claiming the data is current.
- Explain the grain you used in the answer. If you aggregate further, say so explicitly.

## Helper Script

Use `scripts/query_market_data.py` for live access to ClickHouse. Set `MARKET_CH_CONFIG` to a Python file shaped like `references/ck_config.example.py` before running queries.

Available commands:

- `list-tables`: print the 16 allowed tables
- `describe <table>`: print live column names and types
- `sample <table>`: fetch recent rows with optional `--columns`, `--where`, and `--limit`
- `sql "<query>"`: run a read-only query that references only allowed tables

Examples:

```bash
python3 scripts/query_market_data.py list-tables
python3 scripts/query_market_data.py describe market_data.social_sentiment
python3 scripts/query_market_data.py sample market_data.binance_notice --where "category = 'listing'" --limit 10
python3 scripts/query_market_data.py sql "SELECT symbol, sentiment, social_dominance FROM market_data.social_sentiment WHERE time >= now() - INTERVAL 12 HOUR ORDER BY time DESC LIMIT 20"
```

## Reference

Read `references/tables.md` for business meaning, time grain, and common caveats. Keep it lazy:

- Read only the sections for the tables named in the request.
- Use the live `describe` output for exact column types.
- Use the PDF-derived notes to avoid wrong interpretations such as treating snapshots as flows or using load timestamps as event time.
