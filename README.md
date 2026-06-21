# SAR ADC Project — File Inventory

This README exists because the project directory can't be reorganized into
subfolders (xschem's relative-path conventions break if files move), and
because deleting things felt risky without a clear record of what's still
needed. Everything currently in the directory is listed below, grouped by
function, with status notes.

Status legend:
- **VERIFIED** — confirmed working correctly via simulation this project.
- **CURRENT** — actively in use, reflects the latest known-good design.
- **STALE** — superseded by a newer version; kept for reference only.

---

## Core verified building blocks

These are the individually-verified analog/digital blocks the rest of the
design is built from. All confirmed correct in isolation.

- **`bootstrapped_switch.sch`**, **`bootstrapped_switch.sym`** — xschem
  schematic and symbol for the bootstrapped sampling switch. **PENDING
  UPDATE**: the n-well forward-bias fix (see dedicated section below) has
  been applied at the SPICE level (inline in `cdac.spice`'s copy of
  `bootstrapped_switch`) but **not yet** to this schematic. Until updated,
  this schematic does not match the verified-correct circuit. To fix:
  add two more `sky130_fd_pr/pfet_01v8.sym` instances (`XWA`/`XWB`, wired
  per the `nwell_switch` subcircuit below), then move XQ1's and XQ2's bulk
  pin connections off the VDD net onto the new `nwell` net.
- **`bootstrapped_switch_tb.sch`**, **`bootstrapped_switch_tb.spice`**,
  **`bootstrapped_switch_tb.sym`** — testbench (schematic + exported
  SPICE + symbol) for the switch in isolation. VERIFIED (sampling
  behavior, ~156.8ns settling at full 25.6pF load) **but this predates
  the n-well fix** — `bootstrapped_switch_tb.spice` still contains the
  old, forward-bias-prone subcircuit (XQ1/XQ2 bulk tied to fixed VDD).
  Settling-time result is unaffected (different mechanism), but this file
  needs the same patch as `bootstrapped_switch.sch` before being trusted
  again for anything voltage-accuracy-related.
- **`bootstrapped_switch.png`** — rendered image of the schematic, likely
  for documentation/sharing. CURRENT (will go stale once the schematic
  above is updated — re-render after).
- **`strongarm_comparator.sch`**, **`strongarm_comparator.sym`** — xschem
  schematic and symbol for the StrongARM comparator. CURRENT, VERIFIED.
- **`strongarm_comparator_tb.sch`**, **`strongarm_comparator_tb.spice`** —
  testbench for the comparator in isolation. VERIFIED: correct polarity
  (VIN2>VIN1 → X high/Y low), fast resolution (sub-ns).
- **`cdac.spice`** — the real 10-bit CDAC subcircuit (bottom-plate
  sampling, no dummy compensation switch). **CURRENT, VERIFIED** — now
  includes the n-well bias fix (see below) inline in its embedded
  `bootstrapped_switch`/new `nwell_switch` subcircuits. Bottom-plate
  sampling and convert-phase switching confirmed accurate to sub-µV
  (cold-start tested). Known top-plate reset feedthrough kick (`XTOP_n`)
  is still present and still not fixed — see the open question at the
  end of the n-well section below, since with the much larger bootstrap
  bug now resolved, this kick (or something related to it) is the
  leading candidate for the remaining error at high `vin`, though its
  magnitude hasn't been directly re-confirmed by measurement yet.

## Bootstrap switch n-well forward-bias fix (this session)

**Bug.** `XQ1` and `XQ2` inside `bootstrapped_switch` had their bulk pins
tied directly to `VDD`, while their own source/drain terminals (`net1`,
`net3`) are designed to boost well above `VDD` during the sample phase.
This forward-biases the PMOS source/drain-to-bulk junction once the
boosted node exceeds `VDD` by more than a diode drop (~0.7V), clamping
the boost and bleeding real charge from the boost cap (`C_boot`) into the
VDD rail. This was the root cause of the originally-found -78 LSB error
at `vin`=1.5V.

**Diagnosis.** A standalone leakage testbench (`bootstrap_xq1_leakage_tb.
spice`, written this session, not yet copied into the main project
directory — currently only in chat outputs) isolated this via direct
current-sense measurement on XQ1/XQ2's bulk pins: ~382fC lost per cycle
at `vin`=1.5V, accounting for ~97% of the charge deficit measured
directly on `C_boot` (787.9mV settled-voltage drop against a precharged
1.8V, vs. only ~1fC attributable to XQ1's channel current alone — ruling
out the original turn-off-race-timing hypothesis and pointing instead at
the bulk junction).

**Fix.** New `nwell_switch` subcircuit generates a floating well-bias
node tracking `max(VDD, net1)`: `XWA` passes `VDD` through during
precharge, `XWB` passes `net1` through during boost, each device's own
bulk ties to the shared output node so the inactive device stays
reverse-biased by construction (the fix doesn't reintroduce the same
problem on itself). `XQ1`/`XQ2` bulk now routes through this node
instead of fixed `VDD`.

**Confirmation.** Standalone testbench: `vin_s` sampling error dropped
from 99.5mV to 0.94µV at `vin`=1.5V post-fix (`q_bulk_total` collapsed
from -382fC to +0.15fC). Full-ADC re-verification via `sar_adc_tb_v2.
spice` at three `vin` points (post-fix):

| vin   | measured D | ideal D | error    |
|-------|-----------|---------|----------|
| 0.6V  | 335       | 341     | -6 LSB   |
| 1.2V  | 671       | 682     | -11 LSB  |
| 1.5V  | 799       | 853     | -54 LSB  |

0.6V and 1.2V land close to the already-characterized benign top-plate
feedthrough baseline (~6-11 LSB) — effectively resolved. **1.5V does
not** — -54 LSB is far beyond that baseline, and the growth from
1.2V→1.5V is much steeper than 0.6V→1.2V, suggesting something
accelerating as `vin` approaches `VDD`.

**Open question, not yet resolved.** Direct measurement of `vin_s`
itself in the full-ADC context (`v(xcdac.vin_s)` at end of sample window)
came back clean at all three points — 0.11mV (1.2V), 1.22mV (0.6V,
oddly signed), 2.97mV (1.5V) — nowhere near large enough to explain the
1.5V residual on its own. So the n-well fix appears to have fully
resolved the mechanism it targeted; whatever remains at 1.5V is a
**separate** error source, most likely (not yet confirmed) the `XTOP_n`
top-plate reset feedthrough kick scaling up more steeply at high `vin`
than previously characterized (which only covered 0.3-0.9V). A
measurement was added to `sar_adc_tb_v2.spice` to test this directly
(`vdac_kick`, comparing `v(vdac)` just after the `phi_s` falling edge
against the ideal 0.9V reset target) but has **not yet been run**. Next
session: run it at all three `vin` points and check whether `vdac_kick`
scales in proportion to the 6/11/54 LSB pattern above.

## SAR logic — digital block

- **`sar_logic.v`** — original Verilog source for the SAR FSM.
- **`sar_logic_renamed.v`** — same logic, clock port renamed `clkin` to
  avoid a Yosys synthesis name collision. CURRENT source for synthesis.
- **`sar_logic_synth.v`** — Yosys-synthesized gate-level Verilog netlist
  (intermediate pipeline stage, before SPICE port-fixing).
- **`sar_logic.spice`** — synthesized netlist converted to SPICE
  (intermediate, before `fix_spice_ports.py` is applied).
- **`sar_logic_fixed.spice`** — final, power-pin-fixed SPICE netlist of
  the synthesized SAR logic. **CURRENT, VERIFIED** — this is the one
  actually `.include`d by the full ADC testbenches. Confirmed correct via
  Icarus Verilog simulation, a hand/Python trace of the binary-search
  algorithm, and direct inspection of the gate-level netlist (every
  register clocks on `clkin`'s rising edge; `comp_in` feeds combinationally
  into both `cdac_sw.*` and `result.*` logic, confirming the single-edge-
  per-bit pipelined structure assumed by the full ADC testbenches).
- **`fix_spice_ports.py`** — the script that turns `sar_logic.spice` into
  `sar_logic_fixed.spice` by fixing power pin connections. CURRENT, keep.
- **`sar_logic_tb.v`** — Verilog testbench source for the SAR logic
  (drives `sar_logic_tb`, the compiled binary below).
- **`sar_logic_tb`** — compiled `vvp` binary from `iverilog -o sar_logic_tb
  sar_logic_tb.v sar_logic.v`. This is a build artifact, not source —
  regenerable any time from the command above. Consider adding to
  `.gitignore` rather than tracking in version control.
- **`sar_logic_only_tb.spice`** — SPICE isolation testbench that drives
  the synthesized SAR logic directly with a forced `comp_in` sequence (no
  analog blocks). VERIFIED — confirmed the algorithm computes correctly
  bit-by-bit, independent of comparator timing.

## CDAC isolation testbenches (this session)

- **`cdac2.spice`** — a scaled-down 2-bit version of the CDAC, used for
  hand-verifiable charge-redistribution math and for the dummy-switch
  compensation experiment. Currently in its **post-experiment state** —
  the dummy compensation switch (`XTOP_dummy`) was added and tested in two
  configurations (gated by `phi_s`, gated by `phi_sb`), neither of which
  improved the offset (one made it worse). Status: **needs your decision**
  — either revert to a clean no-dummy baseline, or leave as-is as a record
  of the failed experiment. Not currently `.include`d by anything else.
- **`cdac2_tb.spice`** — testbench for `cdac2.spice`. VERIFIED the 2-bit
  charge-redistribution math (to ~2-40mV depending on code, before the
  feedthrough-kick mechanism was understood) and was the testbench used to
  first isolate the top-plate reset feedthrough kick via cold-start
  (`.ic`/`UIC`) testing.
- **`cdac10_tb.spice`** — single-`vin` (0.6V) testbench for the real
  10-bit `cdac.spice`. Includes `.ic`/`UIC` cold-start conditions (added
  after an uncontrolled DC-operating-point solve was found to produce a
  ~1.32V startup overshoot artifact on `vdac`). VERIFIED clean once
  cold-start was added.
- **`cdac10_tb_vin03.spice`**, **`cdac10_tb_vin06.spice`**,
  **`cdac10_tb_vin09.spice`** — same testbench, split into three separate
  files (one per `vin` value: 0.3V/0.6V/0.9V) because this ngspice build
  doesn't support `.step param`. VERIFIED: with cold-start conditions, the
  CDAC's feedthrough kick residual is small and grows mildly with `vin`
  (0.6mV → 4.8mV → 9.0mV across the three values) — this is the data that
  established the offset is *not* perfectly input-independent. (Note:
  this only covers 0.3-0.9V; whether the trend continues growing steeply
  enough to explain the 1.5V residual above is the open question flagged
  in the n-well fix section.)

## Comparator + CDAC chain testbenches (this session)

- **`bs_comp_oneshot_tb.spice`** — one-shot, cold-start isolation
  testbench combining the bootstrapped switch and comparator only (no
  CDAC, no SAR logic). VERIFIED: correct, fast, accurate sampling and
  resolution; found and explained a tiny (~350µV) physically-expected
  comparator kickback.
- **`cdac_comp_chain_tb.spice`** — CDAC + comparator chained together (no
  SAR logic), driving four fixed trial codes matching a real SAR search
  sequence at `vin`=1.2V. **VERIFIED**, after two rounds of fixing
  testbench-only bugs on Claude's part (an undriven floating `vdac` during
  a startup gap, and a `.meas` point placed before the comparator had
  actually evaluated) — once fixed, all four trials matched ideal
  predictions to ~1-2mV and the comparator's KEEP/CLEAR decisions were all
  correct. This is the test that confirmed the CDAC+comparator combination
  is sound, narrowing the full-ADC error down to the SAR-logic/SR-latch
  integration.

## Full ADC testbenches

- **`sar_adc_tb.spice`** — the original full-loop testbench (CDAC +
  comparator + SR latch + SAR logic). Reviewed carefully this session:
  clock structure, comparator polarity, and SR-latch wiring/logic all
  checked out as correct. Its one limitation is that it has **no
  cold-start treatment** and assumes a fixed `done` assertion time rather
  than verifying it. Running it as-is at `vin`=1.2V produced a -77 LSB
  (later corrected to -76 LSB against the true algorithmic target of
  D=682, not the naive rounding target of D=683) error. STALE relative to
  `sar_adc_tb_v2.spice` below, kept for reference/comparison.
- **`sar_adc_tb_v2.spice`** — **CURRENT.** Rebuilt this session with the
  same (verified-sound) circuit topology and clock timing as the original,
  plus: cold-start `.ic`/`UIC` conditions, a `.meas ... WHEN` check on the
  actual `done` assertion time instead of an assumed one, and full
  per-bit trace probes (`cdac_sw.*`, `comp_in`, `comp_x`/`comp_y`,
  `sr_qbar`) at each of the ten trial decisions. Originally run at
  vin=1.2V (before the n-well fix existed) gave -11 LSB, attributed at
  the time entirely to CDAC top-plate feedthrough. **Re-run after the
  n-well fix** at three `vin` points (0.6V/1.2V/1.5V): see the table in
  the n-well fix section above. 1.2V's -11 LSB matches the earlier
  pre-fix figure almost exactly — interesting cross-validation suggesting
  the bootstrap bug's contribution at 1.2V was small even before being
  fixed (consistent with the bug's severity growing with `vin`), while at
  1.5V the bug's contribution was apparently large enough that it can't
  be cleanly compared pre/post-fix the same way. **This remains the most
  current, most trustworthy full-ADC testbench in the directory**, but
  the 1.5V residual is an open item — see next steps.

---

## Next steps

- **Run the `vdac_kick` measurement** (already added to `sar_adc_tb_v2.
  spice`) at all three `vin` points to test whether the top-plate reset
  feedthrough kick explains the 1.5V residual, or whether there's still
  a third, unidentified mechanism.
- **Apply the n-well fix to the schematic**: `bootstrapped_switch.sch`
  and `bootstrapped_switch_tb.spice` both still have the old, forward-
  bias-prone bulk wiring. Only `cdac.spice`'s inline copy has been
  patched so far. Copy `bootstrap_xq1_leakage_tb.spice` from chat outputs
  into the project directory too, since it's the testbench that found
  and confirmed this fix and is referenced above.
- Decide on `cdac2.spice`'s fate: revert the dummy-switch experiment to a
  clean baseline, or leave it as a documented failed attempt.
- Quickly confirm what `comparator_chain_tb.spice`, `meas`, `output.log`,
  and `plot.xpm` actually are/contain, then update this README's entries
  for them (or delete them, now that they're at least flagged rather than
  silently ambiguous).
- Once you're confident `sar_adc_tb_v2.spice` is the one you'll keep using,
  consider renaming it to replace `sar_adc_tb.spice` outright (git history
  preserves the old version if you ever need to compare back), rather than
  keeping both indefinitely.
- `sar_logic_tb` (the compiled binary) is safe to delete any time — it
  regenerates from `sar_logic_tb.v` + `sar_logic.v` via the iverilog
  command noted above.
