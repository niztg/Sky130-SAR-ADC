#!/usr/bin/env python3
"""
plot_comparison.py

Plots ADC error (mV) vs Vin for the pre-fix and post-fix bootstrapped switch,
side by side on the same axes. Intended as a document figure showing the impact
of the nwell floating well-bias fix on sampling accuracy.

Reads:
  sweep_results_prefix.txt  -- pre-fix (XQ1/XQ2 bulk tied to fixed VDD)
  sweep_results.txt         -- post-fix (floating well-bias via nwell_switch)

Both files must be in the same directory as this script.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

VDD     = 1.8
N_BITS  = 10
N_CODES = 2 ** N_BITS
LSB_MV  = VDD / N_CODES * 1000   # ~1.758 mV/LSB


def load_error(filename: str):
    """Load sweep results and compute error vs ideal transfer function."""
    path = os.path.join(SCRIPT_DIR, filename)
    data  = np.loadtxt(path, comments='#')
    vin   = data[:, 0]
    codes = data[:, 1].astype(float)
    ideal = vin / VDD * (N_CODES - 1)
    error_mv = (codes - ideal) * LSB_MV
    return vin, error_mv


# ── Load both datasets ────────────────────────────────────────────────────────

print("Loading pre-fix results...")
vin_pre,  err_pre  = load_error("sweep_results_prefix.txt")

print("Loading post-fix results...")
vin_post, err_post = load_error("sweep_results.txt")

print(f"\nPre-fix  : {len(vin_pre)} points, "
      f"error range {err_pre.min():.1f} to {err_pre.max():.1f} mV")
print(f"Post-fix : {len(vin_post)} points, "
      f"error range {err_post.min():.1f} to {err_post.max():.1f} mV")

# ── Plot ──────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(11, 5))

ax.plot(vin_pre,  err_pre,  lw=1.2, color='firebrick',  label='Pre-fix  (XQ1/XQ2 bulk = VDD)')
ax.plot(vin_post, err_post, lw=1.2, color='steelblue',  label='Post-fix (floating well-bias)')

ax.axhline(0, color='black', lw=0.5)
ax.set_xlabel("Vin (V)", fontsize=12)
ax.set_ylabel("Error (mV)", fontsize=12)
ax.set_title("ADC Sampling Error: Before and After N-Well Bootstrap Fix", fontsize=13)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

fig.tight_layout()
out_path = os.path.join(SCRIPT_DIR, "nwell_fix_comparison.png")
fig.savefig(out_path, dpi=150)
print(f"\nPlot saved to: {out_path}")
plt.show()
