# DataNodes

## Source DataNode

The repository currently defines one source DataNode:

- `BanxicoMXNOTR` in `banxico_connectors/data_nodes/banxico_mx_otr.py`

This node pulls Banxico SIE time series for on-the-run Mexican government
instruments and normalizes them into the table identified as
`banxico_1d_otr_mxn`.

## What It Stores

The node stores daily observations indexed by:

- `time_index`
- `unique_identifier`

The core fields are:

| Field | Meaning |
| --- | --- |
| `days_to_maturity` | Days remaining to maturity for the instrument bucket |
| `clean_price` | Clean price reported by Banxico |
| `dirty_price` | Dirty price for bonds, or decimal overnight rate when `quote_type=rate` |
| `current_coupon` | Coupon or spread-like field reported by Banxico |
| `type` | Normalized instrument role used by the curve bootstrapper |
| `instrument_family` | Normalized Banxico family name |
| `quote_type` | Whether `dirty_price` should be read as `price` or `rate` |
| `coupon_type` | Whether `current_coupon` is unused, coupon-based, or spread-like |

The normalized `type` values are:

- `zero_coupon` for CETES
- `fixed_bond` for M Bonos
- `floating_bondes_d` for Bondes D
- `floating_bondes_f` for Bondes F
- `floating_bondes_g` for Bondes G
- `overnight_rate` for the Banxico target rate anchor

The helper semantic fields are:

- `instrument_family`: `cetes`, `bonos`, `bondes_d`, `bondes_f`, `bondes_g`,
  or `banxico_target_rate`
- `quote_type`: `price` or `rate`
- `coupon_type`: `none`, `coupon`, or `spread_like_rate`

## Instrument Families Covered

The node fetches Banxico series for these groups:

- CETES: `28d`, `91d`, `182d`, `364d`, `2y`
- M Bonos: `0-3y`, `3-5y`, `5-7y`, `7-10y`, `10-20y`, `20-30y`
- Bondes D: `1y`, `2y`, `3y`, `5y`
- Bondes F: `1y`, `2y`, `3y`, `5y`, `7y`
- Bondes G: `2y`, `4y`, `6y`, `8y`, `10y`
- Banxico target rate: stored as a one-day `overnight_rate`

## Update Behavior

`BanxicoMXNOTR.update()`:

- Requires `BANXICO_TOKEN`
- Computes the update window from the last ingested date through yesterday UTC
- Pulls Banxico series in batches to avoid oversized requests
- Normalizes Banxico metric names into the connector schema
- Registers or reuses MainSequence assets for the instrument universe
- Adds the Banxico target rate as the overnight anchor used by the curve
  bootstrapper

The node declares no upstream dependencies and acts as the source market-data
layer for the rest of the project.

If the backend shows no DataNode updates yet, that does not mean the repository
is missing the node. It means the project has not completed a successful remote
run for the current deployed state. See [Deployment And CLI](deployment.md).
