# 10-bit, 1 MS/s SAR ADC — SkyWater Sky130

A full-custom successive-approximation register (SAR) ADC designed transistor-by-transistor in the SkyWater Sky130 open-source 130nm process. The project covers the complete front-end flow: behavioral modeling in Python, transistor-level schematic capture in xschem, SPICE simulation in ngspice against real foundry device models, and SAR control logic synthesized from Verilog RTL to Sky130 standard cells via Yosys.

**Specs:** 10-bit resolution, 1 MS/s, 1.8V supply, 0–1.8V single-ended input.

**Architecture:** bootstrapped sampling switch → binary-weighted charge-redistribution CDAC → StrongARM latch comparator → SAR control logic, closed in a successive-approximation loop.

The most substantial part of this project was debugging it. A 76 LSB conversion error in the full closed-loop simulation was traced through isolation-first testing down to a PMOS body-diode forward-biasing bug in the bootstrapped switch — an initial hypothesis was tested, found to be off by roughly 400x via a charge-balance calculation, and discarded in favor of the real mechanism. The fix (a floating n-well bias network) cut the sampling error from ~89 mV to under a microvolt.

---

## Repository structure

### Root directory

Top-level SPICE subcircuits, xschem schematics, and the current full-ADC testbench.

- **`bootstrapped_switch.spice`** — the bootstrapped sampling switch subcircuit, including the n-well bias fix (`nwell_switch`) that resolves the body-diode bug described above.
- **`bootstrapped_switch.sch` / `.sym`** — xschem schematic and symbol for the switch.
- **`bootstrapped_switch_tb.sch` / `.spice` / `.sym`** — isolation testbench verifying sampling accuracy and settling time.
- **`bootstrap_xq1_leakage_tb.spice`** — diagnostic testbench used to find and confirm the n-well fix, via current-sense probes on the switch's bulk pins.
- **`cdac.spice`** — the 10-bit charge-redistribution DAC, binary-weighted bottom-plate-sampled capacitor array. Includes its own embedded copy of the bootstrapped switch with the n-well fix applied.
- **`cdac2.spice`** — a scaled-down 2-bit CDAC used for hand-verifiable charge-balance math during debugging.
- **`strongarm_comparator.sch` / `.sym`** — xschem schematic and symbol for the StrongARM latch comparator.
- **`strongarm_comparator_tb.sch` / `.spice`** — isolation testbench verifying comparator polarity and resolution speed.
- **`sar_logic.spice`** — SAR control logic, synthesized to a gate-level SPICE netlist by Yosys (pre-port-fix, intermediate file).
- **`sar_logic_fixed.spice`** — the simulation-ready version of the above, with power pins repaired (see `helper/fix_spice_ports.py`). This is the netlist actually used in the full-ADC testbench.
- **`sar_adc_tb_v2.spice`** — the current, full closed-loop ADC testbench: cold-start initial conditions, done-verified readout, and per-bit decision probes across all ten trial comparisons.

### `helper/`

Python utilities supporting the SPICE flow.

- **`fix_spice_ports.py`** — post-processes the Yosys-synthesized SAR logic netlist, since Yosys's `write_spice` output omits power pin connections that ngspice requires. Parses the Sky130 standard cell library directly to recover correct port ordering and produces `sar_logic_fixed.spice`.
- **`helper.py`** — supporting functions for the Python behavioral model (sizing equations, Monte Carlo mismatch analysis, DNL/INL computation).

### `sar_logic_verilog/`

Verilog RTL source and synthesis artifacts for the SAR control logic.

- **`sar_logic.v`** — original Verilog source for the SAR finite-state machine.
- **`sar_logic_renamed.v`** — same logic with the clock port renamed to avoid a Yosys synthesis name collision; this is the file actually synthesized.
- **`sar_logic_synth.v`** — Yosys-synthesized gate-level netlist (Sky130 standard cells), intermediate to SPICE conversion.
- **`sar_logic_tb.v`** — Verilog testbench, verified against Icarus Verilog prior to synthesis.

### `testbenches/`

Archived isolation and pairwise-block testbenches used during the debugging process described above — individually verified, no longer included by the active full-ADC testbench, but kept for reference and reproducibility.

### `documentation/`

LaTeX document and associated files including figures.

### `text/`

Text files used to store data from iteratively executed testbenches.

---

## Key result: the n-well forward-bias bug

The bootstrapped switch's boost PMOS devices had their bulk pins tied to a fixed VDD rail — standard practice, except that these devices' own source/drain nodes are deliberately driven above VDD during the bootstrap phase. Once a boosted node exceeds VDD by more than a diode drop, the source/drain-to-bulk junction stops being reverse-biased and starts conducting, clamping the boost voltage and bleeding charge into the supply rail.

The initial hypothesis (a PMOS channel turn-off race) measured a real but small leakage current — about 400x too small to account for the missing charge. Adding current-sense probes directly on the bulk pins confirmed the actual mechanism and quantified it: roughly 382 fC lost per cycle at Vin = 1.5V, accounting for ~97% of the observed error.

The fix routes the bulk pins through a floating bias node that tracks `max(VDD, boosted node)` instead of a fixed rail, eliminating the forward-bias path entirely. Post-fix, the isolated switch's sampling error dropped from ~89 mV to 0.94 µV.

---

## Status

All four blocks are verified at the schematic/simulation level. Physical layout (Magic, DRC/LVS/PEX) was scoped out of this project, which targets schematic-level verification rather than tapeout. See the technical report in `text/` for full static characterization results and a discussion of a separate, smaller residual error (top-plate reset feedthrough) identified at high input voltages.