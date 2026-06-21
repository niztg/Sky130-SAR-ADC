# SAR ADC Project — File Inventory

Status legend:
- **VERIFIED** — confirmed working correctly via simulation this project.
- **CURRENT** — actively in use, reflects the latest known-good design.
- **STALE** — superseded by a newer version; kept for reference only.
---

## Root directory

- **`bootstrapped_switch.sch`**, **`bootstrapped_switch.sym`** — xschem
  schematic/symbol for the bootstrapped sampling switch, without 
  the nwell forward bias fix which only exists at the SPICE-level
- **`bootstrapped_switch.spice`** — standalone copy of the fixed
  subcircuit (`nwell_switch` + `bootstrapped_switch` with XQ1/XQ2 bulk on
  `nwell`). There was never an unfixed standalone version of this file —
  the original unfixed circuit only ever existed embedded inline inside
  other files. This is simply the `_fixed` file from earlier in the
  session, renamed. **Not currently `.include`d by anything** — `cdac.
  spice` has its own separate inline copy of the same fix, which is the
  one actually exercised by `sar_adc_tb_v2.spice` and the verification
  table below. Two copies of the same fix now exist in the project; worth
  consolidating (have `cdac.spice` `.include` this file instead of
  embedding its own copy) if you want a single source of truth rather
  than two things that could silently drift apart if one gets edited
  later and the other doesn't.
- **`bootstrapped_switch.png`** — rendered image of the schematic. Will
  go stale once the schematic above is updated to match the fix —
  re-render after.
- **`bootstrapped_switch_tb.sch`**, **`bootstrapped_switch_tb.spice`**,
  **`bootstrapped_switch_tb.sym`** — isolation testbench for the switch.
  VERIFIED sampling behavior and settling time (~156.8ns at 25.6pF load),
  but **predates the n-well fix** — still has the old, forward-bias-prone
  subcircuit. Settling-time result is unaffected (different mechanism),
  but needs the same patch as the schematic above before being trusted
  for anything voltage-accuracy-related.
- **`bootstrap_xq1_leakage_tb.spice`** — the diagnostic testbench that
  found and confirmed the n-well fix (current-sense probes on XQ1/XQ2's
  bulk pins). Not stale — keep at root and rerun once the schematic fix
  above is applied, to confirm the schematic-level version matches what
  was validated here at the SPICE level.
- **`cdac.spice`** — the 10-bit CDAC subcircuit (bottom-plate sampling).
  **CURRENT, VERIFIED**, and already includes the n-well fix inline (its
  embedded copy of `bootstrapped_switch` plus the new `nwell_switch`
  subcircuit) — this is currently the only place in the project where the
  fix is actually applied. Bottom-plate sampling and convert-phase
  switching confirmed accurate to sub-µV. Still has the known, not-yet-
  fully-explained top-plate reset feedthrough kick (`XTOP_n`) — see the
  open question in the write-up below.
- **`cdac2.spice`** — scaled-down 2-bit CDAC, used for hand-verifiable
  charge math and the dummy-switch compensation experiment. In its
  **post-experiment state** — `XTOP_dummy` was added and tested in two
  configurations, neither helped (one made it worse). **Needs your
  decision**: revert to a clean no-dummy baseline, or leave as a
  documented failed attempt. Its testbench (`cdac2_tb.spice`) is now in
  `testbenches/` — these two are currently split across locations.
- **`cdac10_tb.spice`**, **`cdac10_tb_vin03.spice`**,
  **`cdac10_tb_vin06.spice`**, **`cdac10_tb_vin09.spice`** — single-`vin`
  CDAC-only testbenches (split into separate files since this ngspice
  build doesn't support `.step param`). VERIFIED with cold-start
  conditions: feedthrough kick grows mildly with `vin` over the
  0.3–0.9V range tested (0.6mV → 4.8mV → 9.0mV). Doesn't yet cover
  1.2V/1.5V — extending this pattern upward is the fastest way to test
  whether the kick explains the still-open 1.5V full-ADC residual (see
  below), much faster than rerunning the full ADC loop each time.
- **`.gitignore`** — excludes installed tool directories (`magic/`,
  `netgen/`, `tcl-core-8-6-16/`, `xschem/`, `xschem_proj/`) from version
  control.
- **`README.md`** — this file.
- **`sar_adc_tb_v2.spice`** — **CURRENT, most trustworthy full-ADC
  testbench in the project.** Cold-start `.ic`/`UIC` conditions, a
  `.meas ... WHEN` check on the actual `done` assertion time, full
  per-bit trace probes at each of the ten trial decisions, and (added
  this session) the `vdac_kick` measurement described below. This is the
  file the n-well fix re-verification table above was run against, and
  the one to run the `vdac_kick` check on next.
- **`sar_logic.spice`** — synthesized SAR logic netlist converted to
  SPICE (intermediate, before `fix_spice_ports.py` is applied). Confirmed
  still present — `helper/fix_spice_ports.py` depends on this exact
  filename existing here.
- **`sar_logic_fixed.spice`** — final, power-pin-fixed SPICE netlist of
  the synthesized SAR logic, output of `fix_spice_ports.py`. **CURRENT,
  VERIFIED** — the one actually `.include`d by `sar_adc_tb_v2.spice`.
  Confirmed correct via Icarus Verilog simulation, a hand/Python trace of
  the binary-search algorithm, and direct inspection of the gate-level
  netlist.
- **`sar_logic_tb`** — compiled `vvp` binary, built from
  `sar_logic_verilog/sar_logic_tb.v` + `sar_logic_verilog/sar_logic.v`.
  Build artifact, not source — safe to delete any time, regenerable via
  `iverilog`.
- **`strongarm_comparator.sch`**, **`strongarm_comparator.sym`** — xschem
  schematic and symbol for the StrongARM comparator. CURRENT, VERIFIED,
  unaffected by the n-well fix (that's specific to the bootstrapped
  switch).
- **`strongarm_comparator_tb.sch`**, **`strongarm_comparator_tb.spice`**
  — testbench for the comparator in isolation. VERIFIED: correct polarity
  (VIN2>VIN1 → X high/Y low), fast resolution (sub-ns).
- **`tcl8.6.16-src.tar.gz`** — looks like the source tarball from
  building the custom Tcl/Tk 8.6.16 install xschem requires on this
  machine. Likely safe to delete once the build it produced
  (`/usr/local/tcl86`) is confirmed working, but worth confirming it's
  not still needed for anything before removing it.

## `helper/`

- **`fix_spice_ports.py`** — turns `sar_logic.spice` into
  `sar_logic_fixed.spice` by fixing power pin connections (Yosys output
  doesn't wire `VPWR`/`VGND` the way ngspice needs). Uses hardcoded
  absolute paths for `INPUT`/`OUTPUT`/`SPICE_LIB`, so moving the script
  itself doesn't change what it reads or writes — just run it as
  `python3 helper/fix_spice_ports.py` instead of from the root directly.
  CURRENT, keep.
- **`__init__.py`**, **`helper.py`** 

## `sar_logic_verilog/`

- **`sar_logic.v`** — original Verilog source for the SAR FSM.
- **`sar_logic_renamed.v`** — same logic, clock port renamed `clkin` to
  avoid a Yosys synthesis name collision. CURRENT source for synthesis.
- **`sar_logic_synth.v`** — Yosys-synthesized gate-level netlist
  (intermediate, before SPICE port-fixing).
- **`sar_logic_tb.v`** — Verilog testbench source for the SAR logic.

If the compiled `sar_logic_tb` binary still exists somewhere, it was
built via `iverilog -o sar_logic_tb sar_logic_tb.v sar_logic.v` — if you
rerun that command from a different working directory now, update the
paths to point in here. It's a regenerable build artifact either way,
safe to delete or `.gitignore`.

## `testbenches/`

Archived here this session — VERIFIED, done with their jobs, none
currently `.include`d by anything still active (except where noted):

- **`bs_comp_oneshot_tb.spice`** — bootstrapped switch + comparator only,
  one-shot/cold-start. VERIFIED correct, fast, accurate sampling and
  resolution; explained a tiny (~350µV) physically-expected comparator
  kickback.
- **`cdac_comp_chain_tb.spice`** — CDAC + comparator chained (no SAR
  logic), four fixed trial codes at `vin`=1.2V. VERIFIED all four trials
  against ideal predictions to ~1-2mV, all KEEP/CLEAR decisions correct.
  Confirmed the CDAC+comparator combination was sound, narrowing the
  original full-ADC error down to the SAR-logic/comparator-capture
  integration.
- **`cdac2_tb.spice`** — testbench for `cdac2.spice` (still at the
  root, undecided fate — see above). VERIFIED the 2-bit charge-
  redistribution math and was the test that first isolated the top-plate
  feedthrough kick via cold-start.
- **`comparator_chain_tb.spice`** — tested whether capturing the
  StrongARM comparator's decision via a bare DFF (`comp_in`) versus
  through an SR latch first (`comp_in_srl`) mattered, since the
  comparator's outputs reset every cycle rather than holding. Resolved:
  the production full-ADC testbench uses the SR-latch approach this file
  validated (same two-NAND structure). The recorded pass/fail output of
  this specific run wasn't preserved, so that conclusion rests on the
  production circuit matching this test's proposed fix rather than a
  directly observed result from this file.
- **`comparator_metastability_tb.spice`** — isolated DC test ruling out
  a comparator-level offset bug.
- **`sar_adc_tb.spice`** — **CONFIRMED STALE.** This is the original,
  pre-cold-start full-loop testbench (-77 LSB result), correctly archived
  here. The current, trustworthy testbench is `sar_adc_tb_v2.spice`,
  which lives at the project root (see Root directory above) — these two
  are not the same file despite the similar name.
- **`sar_logic_only_tb.spice`** — drives the synthesized SAR logic
  directly with a forced `comp_in` sequence, no analog blocks. VERIFIED —
  confirmed the algorithm computes correctly bit-by-bit, independent of
  comparator timing.

## `magic/`, `netgen/`, `tcl-core-8-6-16/`, `xschem/`, `xschem_proj/`

Installed tools and xschem project files, excluded from version control
via `.gitignore`. `xschem/` and `xschem_proj/` hold the actual schematic
sources; per xschem's relative-path requirements, anything in here should
stay put rather than being folded into further reorganization.

---

## Bootstrap switch n-well forward-bias fix

**Bug.** `XQ1` and `XQ2` inside `bootstrapped_switch` had their bulk pins
tied directly to `VDD`, while their own source/drain terminals (`net1`,
`net3`) are designed to boost well above `VDD` during the sample phase.
This forward-biases the PMOS source/drain-to-bulk junction once the
boosted node exceeds `VDD` by more than a diode drop (~0.7V), clamping
the boost and bleeding real charge from the boost cap (`C_boot`) into the
VDD rail. This was the root cause of the originally-found -78 LSB error
at `vin`=1.5V.

**Diagnosis.** The standalone leakage testbench (`bootstrap_xq1_
leakage_tb.spice`, root directory) isolated this via direct current-sense
measurement on XQ1/XQ2's bulk pins: ~382fC lost per cycle at `vin`=1.5V,
accounting for ~97% of the charge deficit measured directly on `C_boot`
(787.9mV settled-voltage drop against a precharged 1.8V, vs. only ~1fC
attributable to XQ1's channel current alone — ruling out the original
turn-off-race-timing hypothesis and pointing instead at the bulk
junction).

**Fix.** New `nwell_switch` subcircuit generates a floating well-bias
node tracking `max(VDD, net1)`: `XWA` passes `VDD` through during
precharge, `XWB` passes `net1` through during boost, each device's own
bulk ties to the shared output node so the inactive device stays
reverse-biased by construction (the fix doesn't reintroduce the same
problem on itself). `XQ1`/`XQ2` bulk now routes through this node
instead of fixed `VDD`. Currently applied only in `cdac.spice`'s inline
copy of `bootstrapped_switch` — not yet ported to the standalone
`bootstrapped_switch.spice`/`.sch` (status of the former is one of the
[NEEDS CONFIRMATION] items above; the latter is a confirmed open task).

**Confirmation.** Standalone testbench: `vin_s` sampling error dropped
from 99.5mV to 0.94µV at `vin`=1.5V post-fix (`q_bulk_total` collapsed
from -382fC to +0.15fC). Full-ADC re-verification at three `vin` points
(post-fix; via `sar_adc_tb_v2.spice`, root directory):

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
measurement (`vdac_kick`, comparing `v(vdac)` just after the `phi_s`
falling edge against the ideal 0.9V reset target) was added to the full
ADC testbench but has **not yet been run**.

---

## Next steps


- **Run the `vdac_kick` measurement** on `sar_adc_tb_v2.spice` at all
  three `vin` points to test whether the top-plate reset feedthrough kick
  explains the 1.5V residual, or whether there's a third, unidentified
  mechanism.
- **Port the n-well fix to `bootstrapped_switch.sch`** in xschem, then
  rerun `bootstrap_xq1_leakage_tb.spice` to confirm the schematic-level
  fix matches what was validated at the SPICE level.
- Decide `cdac2.spice`'s fate (clean revert vs. documented failed
  experiment); consider moving it into `testbenches/` alongside
  `cdac2_tb.spice` once decided, so they're not split across locations.
- Confirm what `meas`, `output.log`, and `plot.xpm` are, then document or
  delete.
