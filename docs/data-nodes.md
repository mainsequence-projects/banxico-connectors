# DataNodes

## Source DataNode

The repository currently defines one source DataNode:

- `BanxicoMXNOTR` in `banxico_connectors/data_nodes/nodes.py`

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
| `dirty_price` | Dirty price reported by Banxico |
| `current_coupon` | Current coupon or spread-like field reported by Banxico |

The implementation also appends a `type` column used by the downstream curve
bootstrapper. The main values are:

- `zero_coupon` for CETES
- `fixed_bond` for M Bonos
- `floating_bondes_d` for Bondes D
- `floating_bondes_f` for Bondes F
- `floating_bondes_g` for Bondes G
- `overnight_rate` for the Banxico target rate anchor

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
