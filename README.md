# query-market-data

Shareable helper package for querying the documented `market_data` ClickHouse tables.

## Structure

- `query-market-data/`: reusable query helper, schema notes, and Codex skill files
- `scripts/install.sh`: one-command installer for Codex users
- `CLAUDE.md`: Claude Code runtime instructions

## Install

1. Copy `query-market-data/references/ck_config.example.py` to your own `ck_config.py`
2. Fill in your ClickHouse connection info
3. Set:

```bash
export MARKET_CH_CONFIG=/path/to/your/ck_config.py
```

If you use Codex:

```bash
sh scripts/install.sh
```

Manual Codex install:

```bash
mkdir -p ~/.codex/skills
cp -R query-market-data ~/.codex/skills/query-market-data
```

Then restart Codex.

If you use Claude Code: keep this package structure and let Claude follow `CLAUDE.md`.

## Usage

Codex:

```text
Use $query-market-data to query the documented market_data tables.
```

Claude Code:

Use `query-market-data/scripts/query_market_data.py` as described in `CLAUDE.md`.

## Notes

- Only the documented `market_data` tables in this package are supported
- The helper only allows read-only queries
- No license has been selected yet; choose one before making the repository public
