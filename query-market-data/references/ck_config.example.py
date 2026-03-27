from __future__ import annotations

# Example ClickHouse connection config for query-market-data.
# Set MARKET_CH_CONFIG=/path/to/this/file when using file-based config.

CK_4A_MARKET = {
    "host": "your-clickhouse-host",
    "port": 8123,
    "username": "your-username",
    "password": "your-password",
    "secure": False,
    "protocol": "http",
}
