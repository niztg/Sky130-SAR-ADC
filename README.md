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
  schematic and symbol for the bootstrapped sampling switch. CURRENT,
  VERIFIED.
- **`bootstrapped_switch_tb.sch`**, **`bootstrapped_switch_tb.spice`**,
  **`bootstrapped_switch_tb.sym`** — testbench (schematic + exported
  SPICE + symbol) for the switch in isolation. VERIFIED: correct sampling
  behavior, settling time measured (~156.8ns for 10-bit settling at the
  full 25.6pF array load).
- **`bootstrapped_switch.png`** — rendered image of the schematic, likely
  for documentation/sharing. CURRENT.
- **`strongarm_comparator.sch`**, **`strongarm_comparator.sym`** — xschem
  schematic and symbol for the StrongARM comparator. CURRENT, VERIFIED.
- **`strongarm_comparator_tb.sch`**, **`strongarm_comparator_tb.spice`** —
  testbench for the comparator in isolation. VERIFIED: correct polarity
  (VIN2>VIN1 → X high/Y low), fast resolution (sub-ns).
- **`cdac.spice`** — the real 10-bit CDAC subcircuit (bottom-plate
  sampling, no dummy compensation switch). CURRENT, VERIFIED: bottom-plate
  sampling and convert-phase switching both confirmed accurate to
  sub-microvolt level (cold-start tested). Has a known, small (~mV-scale,
  mildly input-dependent), well-characterized feedthrough kick on the
  top-plate reset switch — documented, not yet fixed, candidate for
  digital calibration.

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
  established the offset is *not* perfectly input-independent.

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
  `sr_qbar`) at each of the ten trial decisions. Running this at vin=1.2V
  dropped the error from -76/-77 LSB down to **-11 LSB**, and the
  per-bit trace pinpointed the first divergence from the ideal search
  trajectory at the bit5 decision (trial D=672, predicted margin from
  threshold only ~18.75mV) — consistent with the small, already-
  characterized CDAC feedthrough kick finally being large enough to flip
  a close call as the binary search's margins naturally tighten.
  **This is the most current, most trustworthy full-ADC testbench in the
  directory.**

---

## Next steps

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