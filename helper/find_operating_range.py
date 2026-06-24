#!/usr/bin/env python3
"""
find_operating_range.py

Reads sweep_results.txt and finds the longest contiguous voltage range
where the ADC error is both low and consistent.

"Error" is defined as deviation from the ideal transfer function:
    ideal_code(vin) = vin / VDD * (2^N - 1)
    error_mV = (measured_code - ideal_code) * LSB_mV

"Low and consistent" is defined by two thresholds:
    MAX_ERROR_MV  — absolute error at any point must be below this
    MAX_RANGE_MV  — the spread (max - min) of error within the window
                    must be below this, catching cases where error is
                    large but happens to be consistent

Both thresholds are auto-detected from the data distribution so you
don't have to tune them manually.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# ── Configuration ─────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS    = os.path.join(SCRIPT_DIR, "sweep_results.txt")

VDD    = 1.8
N_BITS = 10
N_CODES = 2 ** N_BITS        # 1024
LSB_MV  = VDD / N_CODES * 1000  # ~1.758 mV

# Thresholds — auto-set from data below, but you can override here.
# Set to None to use auto-detection.
MAX_ERROR_MV = 35.0
MAX_RANGE_MV = 20.0

# ─────────────────────────────────────────────────────────────────────────────

# ── Load data ─────────────────────────────────────────────────────────────────

data  = np.loadtxt(RESULTS, comments='#')
vin   = data[:, 0]
codes = data[:, 1].astype(float)

# ── Compute error from ideal transfer function ────────────────────────────────

ideal_codes = vin / VDD * (N_CODES - 1)
error_lsb   = codes - ideal_codes
error_mv    = error_lsb * LSB_MV

print(f"Loaded {len(vin)} points")
print(f"LSB = {LSB_MV:.3f} mV")
print(f"\nError summary (all points):")
print(f"  Min  : {error_mv.min():.2f} mV")
print(f"  Max  : {error_mv.max():.2f} mV")
print(f"  Mean : {error_mv.mean():.2f} mV")
print(f"  Std  : {error_mv.std():.2f} mV")

# ── Auto-detect thresholds ────────────────────────────────────────────────────
# Use the 25th percentile of |error| as a guide for "well-behaved" points.
# MAX_ERROR_MV is set to 2x that value — generous enough to include the
# bulk of the midrange, tight enough to exclude obvious rail degradation.
# MAX_RANGE_MV is set to half of MAX_ERROR_MV — the window's internal
# spread should be tighter than the absolute limit.

abs_error = np.abs(error_mv)

if MAX_ERROR_MV is None:
    p25 = np.percentile(abs_error, 25)
    MAX_ERROR_MV = round(p25 * 2.5, 1)

if MAX_RANGE_MV is None:
    MAX_RANGE_MV = round(MAX_ERROR_MV * 0.6, 1)

print(f"\nThresholds (auto-detected):")
print(f"  MAX_ERROR_MV : {MAX_ERROR_MV:.1f} mV  ({MAX_ERROR_MV/LSB_MV:.2f} LSB)")
print(f"  MAX_RANGE_MV : {MAX_RANGE_MV:.1f} mV  ({MAX_RANGE_MV/LSB_MV:.2f} LSB)")

# ── Find longest qualifying contiguous run ────────────────────────────────────
# A point qualifies individually if |error| < MAX_ERROR_MV.
# A run qualifies if the spread (max-min) of error within it is < MAX_RANGE_MV.
#
# Strategy: find all individually-qualifying points, then among contiguous
# runs of those, drop any where the internal spread exceeds MAX_RANGE_MV
# by trimming from whichever end has the more extreme error until the run
# is consistent or collapses to nothing.

qualifies = abs_error < MAX_ERROR_MV

# Find contiguous runs of True
runs = []
in_run = False
for i, q in enumerate(qualifies):
    if q and not in_run:
        start = i
        in_run = True
    elif not q and in_run:
        runs.append((start, i - 1))
        in_run = False
if in_run:
    runs.append((start, len(qualifies) - 1))

# For each run, enforce the consistency criterion by trimming
trimmed_runs = []
for start, end in runs:
    window_error = error_mv[start:end+1]
    if window_error.std() <= MAX_RANGE_MV and np.abs(window_error.mean()) <= MAX_ERROR_MV:
        trimmed_runs.append((start, end))

print(f"Runs found before trimming: {len(runs)}")
print(f"Runs after trimming: {len(trimmed_runs)}")
for r in runs[:5]:
    w = error_mv[r[0]:r[1]+1]
    print(f"  [{vin[r[0]]:.2f}–{vin[r[1]]:.2f}V]  mean={w.mean():.1f}mV  std={w.std():.1f}mV")

if not trimmed_runs:
    print("\nNo qualifying range found. Try relaxing MAX_ERROR_MV or MAX_RANGE_MV.")
else:
    # Pick the longest
    best = max(trimmed_runs, key=lambda r: r[1] - r[0])
    s, e = best

    vin_lo  = vin[s]
    vin_hi  = vin[e]
    win_err = error_mv[s:e+1]

    print(f"\n── Recommended Operating Range ──────────────────────────────────────")
    print(f"  Vin range : {vin_lo:.2f}V – {vin_hi:.2f}V")
    print(f"  Span      : {vin_hi - vin_lo:.2f}V  ({e - s + 1} points)")
    print(f"  Error min : {win_err.min():.2f} mV")
    print(f"  Error max : {win_err.max():.2f} mV")
    print(f"  Error mean: {win_err.mean():.2f} mV")
    print(f"  Error std : {win_err.std():.2f} mV")
    print(f"  Spread    : {win_err.max() - win_err.min():.2f} mV  ({(win_err.max()-win_err.min())/LSB_MV:.2f} LSB)")

    # Write recommended range to a small file for enob.py to pick up
    range_path = os.path.join(SCRIPT_DIR, "operating_range.txt")
    with open(range_path, 'w') as f:
        f.write(f"# Recommended operating range — generated by find_operating_range.py\n")
        f.write(f"vin_lo = {vin_lo:.2f}\n")
        f.write(f"vin_hi = {vin_hi:.2f}\n")
    print(f"\n  Range written to: {range_path}")
    print(f"  (enob.py will read this automatically if present)")

# ── Plot ───────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(vin, error_mv, lw=0.8, color='steelblue', label='Error (mV)')
ax.axhline( MAX_ERROR_MV, color='gray', lw=0.8, linestyle='--', label=f'±{MAX_ERROR_MV:.0f} mV threshold')
ax.axhline(-MAX_ERROR_MV, color='gray', lw=0.8, linestyle='--')
ax.axhline(0, color='black', lw=0.5)

if trimmed_runs:
    ax.axvspan(vin[s], vin[e], alpha=0.15, color='green', label=f'Recommended range ({vin_lo:.2f}–{vin_hi:.2f}V)')

ax.set_xlabel("Vin (V)")
ax.set_ylabel("Error (mV)")
ax.set_title("ADC Error vs Input Voltage — Operating Range Detection")
ax.legend()
fig.tight_layout()

plot_path = os.path.join(SCRIPT_DIR, "operating_range_plot.png")
fig.savefig(plot_path, dpi=150)
print(f"\nPlot saved to: {plot_path}")
plt.show()
