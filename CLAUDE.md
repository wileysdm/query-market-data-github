# CLAUDE.md

Use `query-market-data/scripts/query_market_data.py` for read-only queries against the documented `market_data` tables in this package.

Before querying:

1. Copy `query-market-data/references/ck_config.example.py` to your own `ck_config.py`
2. Fill in your ClickHouse connection info
3. Set `MARKET_CH_CONFIG=/path/to/your/ck_config.py`
4. Ensure `clickhouse-connect` is installed

Primary references:

- `query-market-data/references/tables.md`
- `query-market-data/scripts/query_market_data.py`

Examples:

```bash
python3 query-market-data/scripts/query_market_data.py list-tables
python3 query-market-data/scripts/query_market_data.py describe market_data.cex_flow_1h
python3 query-market-data/scripts/query_market_data.py sample market_data.binance_notice --limit 5 --format json
```

Keep queries read-only and stay within the documented table whitelist.
