# Instruments

## How `mainsequence.instruments` Is Used

The connector integrates with `mainsequence.instruments` through explicit
registry wiring in `banxico_connectors/instruments/registry.py`.

`register_all()` performs two tasks:

- Registers ETL builders for fixings and curves
- Registers pricing-model index specifications used by MainSequence

This registration is intentionally explicit and import-safe: the module does not
mutate registries until `register_all()` is called.

## ETL Builder Mapping

The connector registers these MainSequence builders:

| MainSequence constant | Builder |
| --- | --- |
| `ZERO_CURVE__BANXICO_M_BONOS_OTR` | `build_banxico_mbonos_otr_zero_curve` |
| `BANXICO_TARGET_RATE` | `update_banxico_target_rate` |
| `REFERENCE_RATE__TIIE_OVERNIGHT` | `update_tiie_fixings` |
| `REFERENCE_RATE__TIIE_28` | `update_tiie_fixings` |
| `REFERENCE_RATE__TIIE_91` | `update_tiie_fixings` |
| `REFERENCE_RATE__TIIE_182` | `update_tiie_fixings` |
| `REFERENCE_RATE__CETE_28` | `update_cete_fixing` |
| `REFERENCE_RATE__CETE_91` | `update_cete_fixing` |
| `REFERENCE_RATE__CETE_182` | `update_cete_fixing` |

## Instrument Types Used In The Curve Bootstrapper

The Banxico quote DataNode and stored fixing datasets are combined into
instrument types that the bootstrapper understands:

| Type | Source family | Logic |
| --- | --- | --- |
| `overnight_rate` | Stored `BANXICO_TARGET_RATE` fixing | One-day anchor; value is injected into `dirty_price` as a decimal rate during bootstrapping |
| `zero_coupon` | CETES | Discount factor is derived directly from price using face value 10 |
| `fixed_bond` | M Bonos | Semiannual 182-day coupon bond bootstrapped from dirty price |
| `floating_bondes_d` | Bondes D | 28-day floating-rate note bootstrapped from overnight rate plus spread |
| `floating_bondes_f` | Bondes F | 28-day floating-rate note bootstrapped from overnight rate plus spread |
| `floating_bondes_g` | Bondes G | 28-day floating-rate note bootstrapped from overnight rate plus spread |

## Bootstrap Logic

`bootstrap_from_curve_df()` builds a zero curve one `time_index` at a time.
The key rules are:

- The stored `BANXICO_TARGET_RATE` fixing anchors the one-day discount factor.
- CETES are treated as zero-coupon instruments.
- M Bonos are treated as fixed-coupon bonds with 182-day coupon spacing.
- Bondes D, F, and G are treated as 28-day floaters that use the overnight rate
  plus the observed spread or coupon field.
- Discount factors between pillars are interpolated log-linearly.
- Zero rates are returned as simple money-market rates on an Act/360 basis in
  decimal form.

## Fixing Mapping

Banxico fixing updaters map MainSequence identifiers to Banxico SIE series ids:

- TIIE: overnight, 28d, 91d, 182d
- CETE: 28d, 91d, 182d
- Banxico target rate: one-day policy-rate anchor

The updater fetches only the requested series, converts the Banxico percentage
value into decimal form, and writes the result as a MainSequence fixing dataset.

## Pricing Index Specifications

The connector also registers pricing index specifications for:

- TIIE overnight, 28d, 91d, and 182d
- CETE 28d, 91d, and 182d
- Optional `REFERENCE_RATE__TIIE_OVERNIGHT_BONDES` when the constant exists

These specs use Mexican market conventions through QuantLib where available:

- Mexico calendar with a safe fallback
- MXN currency with a safe fallback
- `Actual360` day count
- One settlement day
- `ModifiedFollowing` for TIIE tenors
- `Following` for CETE tenors

## Pricing Runtime Prerequisites

MainSequence pricing still needs the platform-side storage contracts and
configuration described in the SDK docs.

The important prerequisites are:

- discount curves are stored through the `discount_curves` storage node
- fixings are stored through the `fixing_rates_1d` storage node
- platform instrument configuration must point pricing to those storage nodes
- ETL registration and pricing registration must both be present before runtime
  pricing can succeed

In practice, this means the repository alone is not enough. A healthy platform
state also needs:

- successful ETL runs for the Banxico source node, fixings, and zero curve
- current project resources for the remote head
- an instrument configuration that can resolve the stored curve and fixing data

## Storage Contract Notes

The connector owns Banxico-specific builders and index specifications, but the
runtime storage contracts remain the MainSequence ones:

- discount curves are consumed from `discount_curves`
- reference-rate fixings are consumed from `fixing_rates_1d`

Document and verify those platform settings whenever pricing fails even though
the repository code looks correct.
