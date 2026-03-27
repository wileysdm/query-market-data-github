# Documented `market_data` Tables

This reference is derived from `the provided PDF data document` plus live `DESCRIBE TABLE` output captured on 2026-03-27 UTC.

Use this file for business meaning, grain, and caveats. Use `scripts/query_market_data.py describe <table>` for exact live column names and types.

## Table Index

- `market_data.cex_flow_1h`
- `market_data.whale_transfer_1h`
- `market_data.evm_basic_data_1h`
- `market_data.sol_basic_data_1h`
- `market_data.eth_staking_data_1h`
- `market_data.sol_staking_data_1h`
- `market_data.aave_loan`
- `market_data.social_sentiment`
- `market_data.binance_notice`
- `market_data.binance_open_interest_1h`
- `market_data.hyperliquid_open_interest_1h`
- `market_data.liquidation_1h`
- `market_data.economic_calendar`
- `market_data.hyperliquid_wallet_distribution_10m`
- `market_data.hyperliquid_whale_position_10m`
- `market_data.hyperliquid_whale_alert_10m`

## Cross-Table Rules

- All documented time fields use UTC.
- Many tables are aggregates, not raw events. Do not treat one row as one transaction or one address unless the section says it is an event-detail table.
- `ingested_at` and `ingested_ts` are ingestion times.
- Verify live freshness before stating data is current.

## market_data.cex_flow_1h

- Grain: hourly aggregate, one row per `exchange + unified_symbol + hour`.
- Time fields: `start_ts`, `end_ts`.
- Dimensions: `exchange`, `unified_symbol`.
- Main metrics: `inflow_usd`, `outflow_usd`, `netflow_usd`, `n_tx`.
- Query notes: `netflow_usd > 0` means stronger net inflow; `netflow_usd < 0` means stronger net outflow.
- Caveat: `unified_symbol` is asset-level, not contract-level.

## market_data.whale_transfer_1h

- Grain: hourly aggregate, one row per `unified_symbol + hour`.
- Time fields: `start_ts`, `end_ts`.
- Dimension: `unified_symbol`.
- Main metrics: `whale_tx_cnt_1h`, `whale_amount_usd_1h`, `whale_asset_quantity_1h`.
- Query notes: count and notional are separate; `whale_asset_quantity_1h` is asset-denominated quantity.

## market_data.evm_basic_data_1h

- Grain: hourly aggregate, one row per `chain + hour`.
- Time field: `start_ts`.
- Dimensions: `chain`, `type`.
- Main metrics: `base_fee_gwei`, `priority_fee_gwei_p50`, `suggested_gas_gwei`, `total_tx`, `tps`, `active_address`.
- Query notes: `type` is currently `evm`; fee fields are in `gwei`.
- Caveat: `active_address` is singular in the schema.

## market_data.sol_basic_data_1h

- Grain: hourly aggregate, one row per `chain + hour`.
- Time field: `start_ts`.
- Dimensions: `chain`, `type`.
- Main metrics: `avg_fee_sol`, `total_tx`, `tps`, `active_address`.
- Query notes: `chain` and `type` are both currently `sol`; fee unit is `SOL`, not `gwei`.
- Caveat: `active_address` is singular in the schema.

## market_data.eth_staking_data_1h

- Grain: hourly aggregate, one row per `chain + hour`.
- Time field: `start_ts`.
- Dimension: `chain` (currently `eth`).
- Main metrics: `consensus_stake_in_eth`, `consensus_unstake_out_eth`, `consensus_net_stake_eth`, `lst_mint_amount`, `lst_burn_amount`, `lst_net_mint`, `lrt_mint_amount`, `lrt_burn_amount`, `lrt_net_mint`.
- Query notes: `consensus_*` fields are ETH staking flows; `lst_*` and `lrt_*` fields are token mint/burn aggregates.
- Caveat: net fields can be negative.

## market_data.sol_staking_data_1h

- Grain: hourly aggregate, one row per `chain + hour`.
- Time field: `start_ts`.
- Dimension: `chain` (currently `sol`).
- Main metrics: `lst_mint_amount`, `lst_burn_amount`, `lst_net_mint`.
- Query notes: this covers selected Solana LST mint/burn aggregates; units are `SOL`.
- Caveat: `lst_net_mint` can be negative.

## market_data.aave_loan

- Grain: hourly aggregate, one row per `collateral_asset + hour`.
- Time field: `start_ts`.
- Dimensions: `collateral_asset`, `collateral_symbol`.
- Main metrics: `users_cnt`, `total_debt_usd_backed`, `near_liq_debt_usd_*`, `near_liq_debt_ratio_*`, `drop_to_liq_pct_p50`.
- Query notes: risk statistics are grouped by collateral asset, not by user.
- Caveat: smaller `drop_to_liq_pct_p50` means positions are closer to liquidation.

## market_data.social_sentiment

- Grain: hourly time series, one row per `symbol + time`.
- Time field: `time`.
- Dimension: `symbol`.
- Main metrics: `sentiment`, `social_dominance`, `contributors_active`, `posts_active`, `interactions`, `galaxy_score`, plus price and market-cap fields such as `open`, `high`, `low`, `close`, `market_cap`, `volume_24h`.
- Query notes: nulls mean the source did not provide a value for that field in that hour.
- Caveat: this is not per-post detail.

## market_data.binance_notice

- Grain: event detail, one row per parsed notice event.
- Time fields: `publish_ts`, `effective_ts`, `ingested_ts`.
- Dimensions: `exchange`, `category`, `event_type`, `market_type`, `asset`, `symbol`, `base_asset`, `quote_asset`, `code`.
- Main attributes: `title`, `url`, `effective_time_text`.
- Query notes: one source notice can expand to multiple rows.
- Caveat: `code` identifies the notice, not a unique row.
- Caveat: completeness of `symbol`, `asset`, `base_asset`, and `quote_asset` depends on the notice type.

## market_data.binance_open_interest_1h

- Grain: hourly snapshot, one row per `unified_symbol + hour`.
- Time fields: `start_ts`, `end_ts`, `exch_ts`, `ingested_at`.
- Dimension: `unified_symbol`.
- Main metric: `open_interest`.
- Query notes: `exch_ts` is the original exchange timestamp.
- Caveat: this is a snapshot table, not a cumulative flow table.

## market_data.hyperliquid_open_interest_1h

- Grain: hourly snapshot, one row per `unified_symbol + hour`.
- Time fields: `start_ts`, `end_ts`, `exch_ts`, `ingested_at`.
- Dimension: `unified_symbol`.
- Main metric: `open_interest`.
- Query notes: `exch_ts` is the original timestamp from the source.
- Caveat: this is a snapshot table, not a cumulative flow table.

## market_data.liquidation_1h

- Grain: hourly aggregate, one row per `exchange + unified_symbol + hour`.
- Time fields: `start_ts`, `end_ts`.
- Dimensions: `exchange`, `unified_symbol`.
- Main metrics: `liquidation_1h`, `long_liquidation_1h`, `short_liquidation_1h`.
- Query notes: long and short liquidation amounts are already split into separate columns.
- Caveat: `unified_symbol` is contract-level here.

## market_data.economic_calendar

- Grain: event detail, one row per `timestamp + event`.
- Time field: `timestamp`.
- Dimension: `event`.
- Query notes: this is a deduplicated event table, not an aggregate.
- Caveat: if the user asks for counts over time, aggregate from `timestamp`.

## market_data.hyperliquid_wallet_distribution_10m

- Grain: 10-minute aggregate, one row per `start_ts + end_ts + distribution_type + group_name`.
- Time fields: `start_ts`, `end_ts`.
- Dimensions: `distribution_type`, `group_name`.
- Main metrics: `all_address_count`, `position_address_count`, `position_address_percent`, `bias_score`, `minimum_amount`, `maximum_amount`, `long_position_usd`, `short_position_usd`, `position_usd`, `profit_address_count`, `loss_address_count`.
- Query notes: `distribution_type` must be filtered before interpretation because the meaning of some fields depends on the distribution family.
- Caveat: the PDF notes that some fields may be effectively absent for some `distribution_type` values.

## market_data.hyperliquid_whale_position_10m

- Grain: 10-minute aggregate, one row per `start_ts + end_ts + symbol`.
- Time fields: `start_ts`, `end_ts`.
- Dimension: `symbol`.
- Main metrics: `whale_addr_cnt`, `whale_gross_position_usd_sum`, `whale_net_position_usd_sum`, `whale_net_position_size_sum`, `whale_mark_price`, `whale_avg_leverage`, `whale_unrealized_pnl_sum`, `whale_avg_liq_price_valid`, `whale_liq_price_zero_cnt`.
- Query notes: gross position and net position are different concepts; net position is direction-offset.
- Caveat: `whale_avg_leverage` and `whale_avg_liq_price_valid` are weighted by position size.

## market_data.hyperliquid_whale_alert_10m

- Grain: 10-minute aggregate, one row per `start_ts + end_ts + symbol`.
- Time fields: `start_ts`, `end_ts`.
- Dimension: `symbol`.
- Main metrics: `whale_alert_cnt`, `whale_alert_open_cnt`, `whale_alert_close_cnt`, `whale_alert_position_usd_sum`, `whale_alert_max_position_usd`, `whale_alert_avg_liq_price_valid`, `whale_alert_liq_price_zero_cnt`.
- Query notes: this is aggregated alert activity within a 10-minute window, not raw alert detail.
- Caveat: `whale_alert_avg_liq_price_valid` only uses rows with valid liquidation prices.
