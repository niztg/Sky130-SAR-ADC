#!/usr/bin/env python3
"""
plot_bootstrap_fix.py

Runs two ngspice simulations — pre-fix and post-fix bootstrapped switch —
at vin=1.5V DC and plots v(VOUT) for both on the same axes.

The pre-fix circuit has XQ1/XQ2 bulk tied to fixed VDD, causing the source/
drain-to-bulk junction to forward-bias when net1/net3 boost above VDD during
sampling. This clamps VOUT well below vin. The post-fix circuit uses a floating
well-bias (nwell_switch subcircuit) that tracks max(VDD, net1), eliminating
the clamp.

Place this file in the same directory as bootstrapped_switch.spice (the fixed
version) and run it. Both netlists are generated inline — no separate pre-fix
file needed.
"""

import subprocess
import os
import re
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TMPFILE    = os.path.join(SCRIPT_DIR, "_bootstrap_tmp.spice")
PDK_LIB    = "/Users/nizansari/.volare/sky130A/libs.tech/ngspice/sky130.lib.spice"

VIN        = 1.5   # V — chosen to show the clamping effect clearly
VDD        = 1.8
TSTOP      = "2u"  # two full sample cycles is enough
TSTEP      = "1n"

# ── Shared testbench footer (supplies, clocks, instance, sim command) ─────────

FOOTER = f"""
* Supplies and input
Vvdd VDD 0 DC {VDD}
Vvin VIN 0 DC {VIN}
* PHIBAR: HIGH during hold, LOW during sample
* Sample window: 100n–400n (300ns), then hold
Vphibar PHIBAR 0 PULSE(1.8 0 100n 1n 1n 300n 1000n)
* Load cap mimics CDAC total capacitance
C1 VOUT 0 25.6p

Xsw VDD PHIBAR VOUT VIN bootstrapped_switch

.lib {PDK_LIB} tt
.tran {TSTEP} {TSTOP} UIC
.print tran v(VIN) v(VOUT) v(PHIBAR)
.end
"""

# ── Pre-fix netlist: XQ1/XQ2 bulk = VDD ──────────────────────────────────────

PREFIX_NETLIST = """\
* Bootstrap switch — PRE-FIX (XQ1/XQ2 bulk tied to VDD)
.subckt bootstrapped_switch VDD PHIBAR VOUT VIN
XQ0 VIN net1 VOUT 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XC_boot net3 net2 sky130_fd_pr__cap_mim_m3_1 W=15.6 L=15.6 MF=1
XQ5 net1 PHIBAR 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XQ4 VIN net1 net2 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XQ1 VDD net1 net3 VDD sky130_fd_pr__pfet_01v8 L=0.15 W=2 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XQ3 net2 PHIBAR 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XQ2 net3 PHIBAR net1 VDD sky130_fd_pr__pfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
.ends bootstrapped_switch
""" + FOOTER

# ── Post-fix netlist: floating well-bias via nwell_switch ─────────────────────

POSTFIX_NETLIST = """\
* Bootstrap switch — POST-FIX (floating well-bias tracks max(VDD, net1))
.subckt nwell_switch out vdd_in net1_in
Xpass_vdd out vdd_in out vdd_in sky130_fd_pr__pfet_01v8 L=0.15 W=2 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
Xpass_net1 out net1_in out out sky130_fd_pr__pfet_01v8 L=0.15 W=2 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
.ends nwell_switch

.subckt bootstrapped_switch VDD PHIBAR VOUT VIN
Xnwell_sw nwell_bias VDD net1 nwell_switch
XQ0 VIN net1 VOUT 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XC_boot net3 net2 sky130_fd_pr__cap_mim_m3_1 W=15.6 L=15.6 MF=1
XQ5 net1 PHIBAR 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XQ4 VIN net1 net2 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XQ1 VDD net1 net3 nwell_bias sky130_fd_pr__pfet_01v8 L=0.15 W=2 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XQ3 net2 PHIBAR 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
XQ2 net3 PHIBAR net1 nwell_bias sky130_fd_pr__pfet_01v8 L=0.15 W=1 nf=1 ad='int((nf+1)/2) * W/nf * 0.29' as='int((nf+2)/2) * W/nf * 0.29' pd='2*int((nf+1)/2) * (W/nf + 0.29)' ps='2*int((nf+2)/2) * (W/nf + 0.29)' nrd='0.29 / W' nrs='0.29 / W' sa=0 sb=0 sd=0 mult=1
.ends bootstrapped_switch
""" + FOOTER


def run_and_parse(netlist: str, label: str):
    """Write netlist, run ngspice, parse time/VOUT/PHIBAR from .print output."""
    with open(TMPFILE, 'w') as f:
        f.write(netlist)

    print(f"Running {label} ... ", end='', flush=True)
    result = subprocess.run(
        ['ngspice', '-b', TMPFILE],
        capture_output=True, text=True, timeout=120
    )
    combined = result.stdout + result.stderr

    # Parse tabular .print output: Index  time  v(VIN)  v(VOUT)  v(PHIBAR)
    time, vout, phibar = [], [], []
    for line in combined.splitlines():
        parts = line.split()
        if len(parts) == 5:
            try:
                # ngspice .print columns: index  time  v(vin)  v(vout)  v(phibar)
                t  = float(parts[1])
                vo = float(parts[3])
                ph = float(parts[4])
                time.append(t)
                vout.append(vo)
                phibar.append(ph)
            except ValueError:
                continue

    if not time:
        print("FAILED — no data parsed")
        print(combined[-1000:])
        return None, None, None

    print(f"OK  ({len(time)} points)")
    return np.array(time), np.array(vout), np.array(phibar)


# ── Run both sims ─────────────────────────────────────────────────────────────

t_pre,  vout_pre,  ph_pre  = run_and_parse(PREFIX_NETLIST,  "pre-fix")
t_post, vout_post, ph_post = run_and_parse(POSTFIX_NETLIST, "post-fix")

if t_pre is None or t_post is None:
    print("One or both simulations failed — check ngspice output above.")
    exit(1)

# Convert time to µs for readability
t_pre_us  = t_pre  * 1e6
t_post_us = t_post * 1e6

# ── Plot ──────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(t_post_us, vout_post, lw=1.5, color='steelblue',
        label=f'Post-fix VOUT (floating well-bias)')
ax.plot(t_pre_us,  vout_pre,  lw=1.5, color='firebrick',
        label=f'Pre-fix VOUT  (bulk = VDD, junction clamp)')
ax.axhline(VIN, color='gray', lw=1.0, linestyle='--',
           label=f'Ideal VOUT = Vin = {VIN}V')

# Shade sample windows (PHIBAR low)
# Use post-fix phibar trace to mark windows
in_sample = False
for i in range(len(t_post_us)):
    if ph_post[i] < 0.9 and not in_sample:
        x_start = t_post_us[i]
        in_sample = True
    elif ph_post[i] >= 0.9 and in_sample:
        ax.axvspan(x_start, t_post_us[i], alpha=0.08, color='green')
        in_sample = False

ax.set_xlabel("Time (µs)", fontsize=12)
ax.set_ylabel("VOUT (V)", fontsize=12)
ax.set_title(f"Bootstrapped Switch Sampling — Vin = {VIN}V  |  N-Well Fix Comparison",
             fontsize=13)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

fig.tight_layout()
out_path = os.path.join(SCRIPT_DIR, "bootstrap_fix_waveform.png")
fig.savefig(out_path, dpi=150)
print(f"\nPlot saved to: {out_path}")
plt.show()
