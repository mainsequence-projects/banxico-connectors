# Refactor Tasks

## Purpose

Track the SDK-alignment work needed after reviewing the current Main Sequence DataNode documentation with the `mainsequence-project` and `mainsequence-data-nodes` skills.

Success condition: the Banxico DataNode code follows the current `DataNodeConfiguration` contract, preserves the intended published table contract for `banxico_1d_otr_mxn`, and has a clear namespace-first validation path before any non-namespaced run.

## Docs Reviewed

- Main Sequence docs root: https://mainsequence-sdk.github.io/mainsequence-sdk/
- DataNode tutorial: `docs/tutorial/creating_a_simple_data_node.md`
- Asset MultiIndex tutorial: `docs/tutorial/multi_index_columns_working_with_assets.md`
- DataNode knowledge guide: `docs/knowledge/data_nodes.md`
- Assets knowledge guide: `docs/knowledge/markets/assets.md`

## Refactor Status

Code refactor status: implemented locally.

Local validation status: `py_compile`, config construction, and no-run namespaced constructor initialization passed.

Platform validation status: pending.

Initial finding: `BanxicoMXNOTR` in `banxico_connectors/data_nodes/banxico_mx_otr.py` was outdated relative to the current SDK documentation.

The main mismatch was constructor/config shape. Current docs say new DataNodes should accept a single `DataNodeConfiguration` object and call `super().__init__(config=config, ...)`. The node previously used `def __init__(self, *args, **kwargs)` and had no explicit config model.

The node also hardcoded first-run behavior with `dt.datetime(2010, 1, 1, tzinfo=UTC)` instead of using a documented `config.offset_start` field.

The node manually overrode `get_table_metadata()` and `get_column_metadata()`. This still can work, but current docs prefer config-driven `node_metadata` and `records` for simple static metadata through `DataNodeMetaData` and `RecordDefinition`.

The node used `UpdateStatistics.get_last_update_index_2d(uid=...)`. The current asset DataNode tutorial uses `update_statistics.get_asset_earliest_multiindex_update(asset=asset)` for per-asset incremental windows.

The output is a `(time_index, unique_identifier)` table, so `get_asset_list()` is not optional. The current implementation does register or reuse custom assets, which matches the current asset-discipline guidance, but validation should verify every emitted `unique_identifier` maps to the effective asset list.

Changing config shape may change `storage_hash`. The published identifier `banxico_1d_otr_mxn` should stay stable, but the backing table may rotate. Treat this as a migration-sensitive refactor, not a cosmetic edit.

## Required Refactor Tasks

- [x] Add `BanxicoMXNOTRConfig(DataNodeConfiguration)`.
- [x] Move first-run start date into `offset_start: dt.datetime` with a default of `2010-01-01T00:00:00Z`.
- [x] Mark `offset_start` with `json_schema_extra={"update_only": True}` because it controls updater/backfill scope, not dataset meaning.
- [x] Add `records: list[RecordDefinition]` for the eight published columns.
- [x] Add `node_metadata: DataNodeMetaData` with identifier `ON_THE_RUN_DATA_NODE_TABLE_NAME`, daily frequency, and the existing table description.
- [x] Mark `node_metadata` with `json_schema_extra={"runtime_only": True}`.
- [x] Refactor `BanxicoMXNOTR.__init__` to accept `config: BanxicoMXNOTRConfig`, plus `hash_namespace` and `test_node` keyword args.
- [x] Store `self.offset_start = config.offset_start`.
- [x] Call `super().__init__(config=config, hash_namespace=hash_namespace, test_node=test_node)`.
- [x] Update all call sites from `BanxicoMXNOTR()` to `BanxicoMXNOTR(config=BanxicoMXNOTRConfig())`.
- [x] Update `scripts/build_curves.py` imports and launcher code accordingly.
- [x] Replace `get_last_update_index_2d(uid=...)` usage with the current per-asset update-statistics method if confirmed available in the installed SDK.
- [x] Compute `effective_assets = update_statistics.asset_list or self.get_asset_list() or []` once and use it consistently for update-window calculation and output construction.
- [x] Use `self.offset_start` as the fallback start date when there are no previous per-asset updates.
- [x] Resolve `BANXICO_TOKEN` from a Main Sequence Secret at runtime. Do not put secrets in the config.
- [x] Confirm numeric output columns keep numeric dtypes. Avoid converting numeric missing values to Python `None` if it forces object dtype unnecessarily.
- [x] Keep `time_index` UTC-aware, named `time_index`, sorted ascending, and free of duplicate `(time_index, unique_identifier)` pairs.
- [x] Keep asset registration idempotent in `get_asset_list()`.
- [x] Keep the published identifier `banxico_1d_otr_mxn` unless we intentionally version the dataset.

## Migration And Compatibility Checks

- [ ] Before implementation, inspect the current platform table for `banxico_1d_otr_mxn`.
- [ ] Record current `DataNodeStorage` id, published identifier, `storage_hash`, and current schema.
- [ ] Run the refactored node only inside an explicit namespace first, for example `hash_namespace("banxico_mx_otr_config_refactor")`.
- [ ] Compare namespaced output schema against the current production schema.
- [ ] Confirm row index shape remains `(time_index, unique_identifier)`.
- [ ] Confirm no emitted `unique_identifier` is outside `get_asset_list()`.
- [ ] Decide whether a changed backing `storage_hash` is acceptable under the stable published identifier.
- [ ] If metadata changes are shipped, refresh the table search index after the production table is updated.

## Suggested Validation Commands

Run after implementation, not before:

```bash
mainsequence project refresh_token --path .
mainsequence project current --debug
mainsequence data-node list --filter identifier__contains=banxico_1d_otr_mxn
mainsequence data-node detail <DATA_NODE_STORAGE_ID>
```

For the first code validation, use a small namespaced run and bounded date range through `BanxicoMXNOTRConfig(offset_start=...)`.

## Follow-Up Documentation Tasks

- [x] Update `docs/data-nodes.md` once the DataNode config refactor is implemented.
- [x] Mention that `banxico_1d_otr_mxn` is the stable published identifier, while backing storage may change during migrations.
- [x] Add the namespace-first validation workflow to the DataNode docs.
- [x] Add a note to launcher documentation that DataNodes now require explicit config objects.

## 2026-04-20 OTR quote/rate split

- [x] Remove the Banxico target-rate synthetic asset from `BanxicoMXNOTR` so `banxico_1d_otr_mxn` stores only security quotes.
- [x] Add derived `yield_rate` and `yield_source` columns to the OTR quote table for plotting.
- [x] Keep the Banxico target rate out of the quote table and inject it only as the one-day anchor during curve bootstrapping.
- [x] Persist the Banxico target rate as its own fixing in `fixing_rates_1d`.
- [x] Make the curve builder read the stored `BANXICO_TARGET_RATE` fixing instead of fetching it directly from Banxico.
- [ ] Run a namespaced DataNode validation after confirming the desired persistent target-rate contract.
