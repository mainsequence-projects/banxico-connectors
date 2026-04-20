# DataNodes

## Source DataNode

The repository currently defines one source DataNode:

- `BanxicoMXNOTR` in `banxico_connectors/data_nodes/banxico_mx_otr.py`

This node pulls Banxico SIE time series for on-the-run Mexican government
instruments and normalizes them into the table identified as
`banxico_1d_otr_mxn`.

The node uses `BanxicoMXNOTRConfig`, a `DataNodeConfiguration`, for SDK-aligned
construction. Instantiate it with:

```python
from banxico_connectors.data_nodes.banxico_mx_otr import BanxicoMXNOTR, BanxicoMXNOTRConfig

node = BanxicoMXNOTR(config=BanxicoMXNOTRConfig())
```

`banxico_1d_otr_mxn` is the stable published identifier. The physical backing
storage can still change during config or schema migrations, so refactors should
be validated in a hash namespace before any production-style run.

## What It Stores

The node stores daily observations indexed by:

- `time_index`
- `unique_identifier`

The core fields are:

| Field | Meaning |
| --- | --- |
| `days_to_maturity` | Days remaining to maturity for the instrument bucket |
| `clean_price` | Clean price reported by Banxico |
| `dirty_price` | Dirty price for quoted securities |
| `current_coupon` | Coupon or spread-like field reported by Banxico |
| `yield_rate` | Derived annual yield as a decimal rate when available |
| `yield_source` | Method used to derive `yield_rate` |
| `type` | Normalized instrument role used by the curve bootstrapper |
| `instrument_family` | Normalized Banxico family name |
| `quote_type` | Price/rate classification; this source node emits price rows only |
| `coupon_type` | Whether `current_coupon` is unused, coupon-based, or spread-like |

The normalized `type` values are:

- `zero_coupon` for CETES
- `fixed_bond` for M Bonos
- `inflation_linked_bond` for UDIBONOS
- `floating_bondes_d` for Bondes D
- `floating_bondes_f` for Bondes F
- `floating_bondes_g` for Bondes G

The helper semantic fields are:

- `instrument_family`: `cetes`, `bonos`, `udibonos`, `bondes_d`, `bondes_f`, or `bondes_g`
- `quote_type`: `price`
- `coupon_type`: `none`, `coupon`, or `spread_like_rate`

## Instrument Families Covered

The node fetches Banxico series for these groups:

- CETES: `28d`, `91d`, `182d`, `364d`, `2y`
- M Bonos: `0-3y`, `3-5y`, `5-7y`, `7-10y`, `10-20y`, `20-30y`
- UDIBONOS: `3y`, `10y`, `20y`, `30y`
- Bondes D: `1y`, `2y`, `3y`, `5y`
- Bondes F: `1y`, `2y`, `3y`, `5y`, `7y`
- Bondes G: `2y`, `4y`, `6y`, `8y`, `10y`

The Banxico target rate is intentionally not stored in this source quote node.
It is persisted through the `fixing_rates_1d` fixing storage and consumed by the
curve builder as the one-day anchor.

UDIBONOS are stored for quote monitoring and plotting. They are intentionally
excluded from the nominal MXN M Bonos zero-curve bootstrap because they are
inflation-linked securities.

## Update Behavior

`BanxicoMXNOTR.update()`:

- Requires a Main Sequence Secret named `BANXICO_TOKEN`
- Computes the update window from the last ingested date through yesterday UTC
- Uses `BanxicoMXNOTRConfig.offset_start` as the first-run fallback date
- Pulls Banxico series in batches to avoid oversized requests
- Normalizes Banxico metric names into the connector schema
- Registers or reuses MainSequence assets for the instrument universe
- Adds derived `yield_rate` and `yield_source` columns for plotting and
  downstream diagnostics

The node declares no upstream dependencies and acts as the source market-data
layer for the rest of the project.

The Banxico token is resolved at runtime with
`mainsequence.client.Secret.get(name="BANXICO_TOKEN").value`. It is not part of
the DataNode config, `storage_hash`, or `update_hash`.

For the first validation after a DataNode refactor, run the node inside an
explicit namespace, for example `hash_namespace("banxico_mx_otr_config_refactor")`,
and compare the resulting schema against the current published table before a
non-namespaced run.

If the backend shows no DataNode updates yet, that does not mean the repository
is missing the node. It means the project has not completed a successful remote
run for the current deployed state. See [Deployment And CLI](deployment.md).
