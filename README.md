# 10-bit, 1 MS/s SAR ADC, SkyWater Sky130

A full-custom successive-approximation register (SAR) ADC designed transistor by transistor in the SkyWater Sky130 open-source 130nm process. The project covers the full front-end flow: Python behavioral modeling, transistor-level schematic capture in xschem, SPICE simulation in ngspice against real foundry device models, and SAR control logic synthesized from Verilog RTL to Sky130 standard cells via Yosys.

**Specs:** 10-bit resolution, 1 MS/s, 1.8V supply, 0 to 1.8V single-ended input.

**Architecture:** bootstrapped sampling switch, binary-weighted charge-redistribution CDAC, StrongARM latch comparator, and SAR control logic, closed in a successive-approximation loop.

The most substantial part of this project was debugging it. A 76 LSB conversion error in the full closed-loop simulation was traced through isolation-first testing to a PMOS body-diode forward-biasing bug in the bootstrapped switch. An initial hypothesis was tested, found to be off by roughly 400x via a charge-balance calculation, and discarded in favor of the real mechanism. The fix, a floating n-well bias network, cut the sampling error from about 89 mV to under a microvolt.

Full technical writeup with derivations, sizing decisions, and characterization results is in `documentation/sar_adc_design.pdf`.

---

## Repository structure

### Root directory

Core SPICE subcircuits, xschem schematics, and the current full-ADC testbench.

- **`bootstrapped_switch.spice`** the bootstrapped sampling switch subcircuit, including the n-well bias fix that resolves the body-diode bug described above.
- **`bootstrapped_switch.sch` / `.sym`** xschem schematic and symbol for the switch.
- **`bootstrapped_switch_tb.sch` / `.spice` / `.sym`** isolation testbench verifying sampling accuracy and settling time.
- **`cdac.spice`** the 10-bit charge-redistribution DAC, a binary-weighted bottom-plate-sampled capacitor array. Includes its own embedded copy of the bootstrapped switch with the n-well fix applied.
- **`strongarm_comparator.sch` / `.sym`** xschem schematic and symbol for the StrongARM latch comparator.
- **`strongarm_comparator_tb.sch` / `.spice`** isolation testbench verifying comparator polarity and resolution speed.
- **`sar_logic.spice`** SAR control logic, synthesized to a gate-level SPICE netlist by Yosys (intermediate file, before power-pin repair).
- **`sar_logic_fixed.spice`** the simulation-ready version of the above, with power pins repaired by `helper/fix_spice_ports.py`. This is the netlist actually used in the full-ADC testbench.
- **`sar_adc_tb_v2.spice`** the current, full closed-loop ADC testbench: cold-start initial conditions, done-verified readout, and per-bit decision probes across all ten trial comparisons.
- **`meas`, `output.log`, `plot.xpm`** ngspice simulation artifacts (measurement output, run log, and plot export) from the most recent testbench run.
- **`tcl8.6.16-src.tar.gz`** source tarball for the custom Tcl/Tk build xschem requires on this machine.

### `documentation/`

The written technical report and its build artifacts.

- **`sar_adc_design.pdf`** the complete writeup: specifications, architecture, block-level design and sizing, integration debugging (including the n-well bug), and static performance characterization.
- **`sar_adc_design.tex`** LaTeX source for the report.
- **`figures/`** plots and schematic captures referenced in the report.
- **`.aux`, `.fdb_latexmk`, `.fls`, `.log`, `.out`, `.synctex.gz`, `.toc`** LaTeX build artifacts, regenerated automatically on compile.

### `helper/`

Python utilities supporting the behavioral model and SPICE flow.

- **`behavioral_model.py`** the first-principles Python model: kT/C noise-floor sizing and Monte Carlo mismatch analysis used to size the unit capacitor.
- **`enob.py`** computes INL and static ENOB from sweep results.
- **`find_operating_range.py`** auto-detects the valid input operating range from sweep data.
- **`fix_spice_ports.py`** post-processes the Yosys-synthesized SAR logic netlist, since Yosys's `write_spice` output omits power pin connections that ngspice requires. Parses the Sky130 standard cell library directly to recover correct port ordering and produces `sar_logic_fixed.spice`.
- **`plot_bootstrap_fix.py`** generates the before/after comparison plot of the bootstrapped switch's sampling error around the n-well fix.
- **`plot_comparison.py`** generates comparison plots used in characterization.
- **`sweep_adc.py`** drives the per-point DC sweep across input voltage, spawning a separate ngspice process per point.

### `sar_logic_verilog/`

Verilog RTL source and synthesis artifacts for the SAR control logic.

- **`sar_logic.v`** original Verilog source for the SAR finite-state machine.
- **`sar_logic_renamed.v`** same logic with the clock port renamed to avoid a Yosys synthesis name collision. This is the file actually synthesized.
- **`sar_logic_synth.v`** Yosys-synthesized gate-level netlist (Sky130 standard cells), intermediate to SPICE conversion.
- **`sar_logic_tb.v`** Verilog testbench, verified against Icarus Verilog prior to synthesis.

### `testbenches/`

Archived isolation and pairwise-block testbenches used during debugging, individually verified, no longer included by the active full-ADC testbench, but kept for reference and reproducibility.

### `text/`

Plain-text logs of numerical results referenced in the report.

- **`operating_range.txt`** output of the operating-range auto-detection.
- **`sweep_results_prefix.txt`, `sweep_results.txt`** raw DC sweep output used to compute INL and ENOB.

### `magic/`, `netgen/`, `tcl-core-8-6-16/`, `xschem/`, `xschem_proj/`

Installed tools and xschem project files, excluded from version control via `.gitignore`. `xschem/` and `xschem_proj/` hold the actual schematic sources; per xschem's relative-path requirements, anything in here stays put rather than being folded into further reorganization.

---

## Key result: the n-well forward-bias bug

The bootstrapped switch's boost PMOS devices had their bulk pins tied to a fixed VDD rail, standard practice, except that these devices' own source/drain nodes are deliberately driven above VDD during the bootstrap phase. Once a boosted node exceeds VDD by more than a diode drop, the source/drain-to-bulk junction stops being reverse-biased and starts conducting, clamping the boost voltage and bleeding charge into the supply rail.

The initial hypothesis, a PMOS channel turn-off race, measured a real but small leakage current, about 400x too small to account for the missing charge. Current-sense probes directly on the bulk pins confirmed the actual mechanism and quantified it: roughly 382 fC lost per cycle at Vin = 1.5V, accounting for about 97% of the observed error.

The fix routes the bulk pins through a floating bias node that tracks max(VDD, boosted node) instead of a fixed rail, eliminating the forward-bias path entirely. Post-fix, the isolated switch's sampling error dropped from about 89 mV to 0.94 µV.

---

## Status

All four blocks are verified at the schematic and simulation level. Physical layout (Magic, DRC/LVS/PEX) was scoped out of this project, which targets schematic-level verification rather than tapeout. See `documentation/sar_adc_design.pdf` for full static characterization results and a discussion of a separate, smaller residual error (top-plate reset feedthrough) identified at high input voltages.