# Markets

## MainSequence Market Interaction

This project interacts with the MainSequence platform in three ways:

- It registers Banxico-specific `Asset` objects for the source market data.
- It seeds `Constant` identifiers used by fixings, curves, and pricing indices.
- It creates managed fixing and curve datasets through MainSequence ETL nodes.

## Assets Created

`BanxicoMXNOTR.get_asset_list()` registers or reuses custom assets with:

- `exchange_code="MEXICO"`
- `security_market_sector=GOVT`
- `security_type=DOMESTIC`
- `security_type_2=GOVT`

The asset universe follows these identifier patterns:

| Pattern | Coverage |
| --- | --- |
| `MCET_<tenor>_OTR` | CETES on-the-run buckets |
| `MBONO_<bucket>_OTR` | M Bonos on-the-run buckets |
| `BONDES_D_<tenor>_OTR` | Bondes D on-the-run buckets |
| `BONDES_F_<tenor>_OTR` | Bondes F on-the-run buckets |
| `BONDES_G_<tenor>_OTR` | Bondes G on-the-run buckets |

`BANXICO_TARGET_RATE` is not part of the OTR asset universe. It is stored as a
fixing in `fixing_rates_1d` and used as the one-day curve anchor.

## Constants Seeded

`banxico_connectors.instruments.scafold.seed_defaults()` creates the Banxico
constants expected by the connector:

- `REFERENCE_RATE__TIIE_OVERNIGHT`
- `REFERENCE_RATE__TIIE_28`
- `REFERENCE_RATE__TIIE_91`
- `REFERENCE_RATE__TIIE_182`
- `REFERENCE_RATE__CETE_28`
- `REFERENCE_RATE__CETE_91`
- `REFERENCE_RATE__CETE_182`
- `REFERENCE_RATE__TIIE_OVERNIGHT_BONDES`
- `BANXICO_TARGET_RATE`
- `ZERO_CURVE__BANXICO_M_BONOS_OTR`

## Platform Datasets Created

When `scripts/build_curves.py` runs, it creates or refreshes:

- A source DataNode table: `banxico_1d_otr_mxn`
- Fixing datasets for:
  - Banxico target rate
  - TIIE overnight
  - TIIE 28d
  - TIIE 91d
  - TIIE 182d
  - CETE 28d
  - CETE 91d
  - CETE 182d
- A discount curve dataset for `ZERO_CURVE__BANXICO_M_BONOS_OTR`

## Portfolios

The current repository does not create MainSequence portfolios, positions, or
strategy containers. Its scope is market-data ingestion, fixing publication,
and curve construction.

## Other Market Objects Not Created

The current repository also does not create:

- asset translation tables
- portfolio groups
- virtual-fund workflows
