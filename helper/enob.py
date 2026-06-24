#!/usr/bin/env python3
"""
enob.py

Reads sweep_results.txt and computes static ENOB from smoothed INL statistics.

The virtual sine FFT approach requires input step size << 1 LSB to correctly
characterise the transfer function. With 10mV steps and ~1.77mV/LSB the raw
INL oscillates ±10 LSB due to the measurement grid, not real ADC nonlinearity.

Instead, ENOB is estimated from the RMS of the smoothed INL:

  Signal power (full-scale sine) = (2^N)^2 / 8   [LSB^2]
  Noise power = sigma_INL^2 + 1/12               [LSB^2]
      where sigma_INL = RMS of smoothed INL
      and   1/12      = ideal quantisation noise

  SNDR = 10·log10(signal_power / noise_power)
  ENOB = (SNDR - 1.76) / 6.02

The smoothing window must be wide enough to average out the measurement-grid
quantisation (1 LSB / step_size points) but narrow enough to preserve real
low-frequency nonlinearity. SMOOTH_WINDOW = 7 at 10mV steps is appropriate
for this ADC (1 LSB ~ 1.77mV, so the grid oscillation period ~ 6 points).
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# ── Configuration ─────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS    = os.path.join(SCRIPT_DIR, "sweep_results.txt")

VDD     = 1.8
N_BITS  = 10
N_CODES = 2 ** N_BITS   # 1024

SMOOTH_WINDOW = 7   # points — wider than 1 LSB / step size (~6 pts at 10mV)

# ── 1. Load measurements ──────────────────────────────────────────────────────

data  = np.loadtxt(RESULTS, comments='#')
vin   = data[:, 0]
codes = data[:, 1].astype(float)

print(f"Loaded {len(vin)} points from {RESULTS}")
print(f"  Vin range : {vin[0]:.2f}V – {vin[-1]:.2f}V")
print(f"  Code range: {int(codes.min())} – {int(codes.max())}")

# ── 2. Operating range ────────────────────────────────────────────────────────

range_file = os.path.join(SCRIPT_DIR, "operating_range.txt")
if os.path.exists(range_file):
    range_cfg = {}
    with open(range_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=')
                range_cfg[k.strip()] = float(v.strip())
    vin_min = range_cfg['vin_lo']
    vin_max = range_cfg['vin_hi']
    print(f"\nOperating range loaded from {range_file}")
    print(f"  Using Vin = {vin_min:.2f}V – {vin_max:.2f}V")
else:
    vin_min = vin[0]
    vin_max = vin[-1]
    print(f"\nNo operating_range.txt found — using full range ({vin_min:.2f}–{vin_max:.2f}V)")

mask      = (vin >= vin_min) & (vin <= vin_max)
vin_fit   = vin[mask]
codes_fit = codes[mask]

# ── 3. Best-fit line and raw INL ──────────────────────────────────────────────

coeffs     = np.polyfit(vin_fit, codes_fit, 1)
gain_fit   = coeffs[0]   # LSB / V
offset_fit = coeffs[1]   # LSB

ideal_codes = np.polyval(coeffs, vin_fit)
inl_raw     = codes_fit - ideal_codes

print(f"\nBest-fit line:")
print(f"  Gain  : {gain_fit:.3f} LSB/V  ({1/gain_fit*1000:.4f} mV/LSB)")
print(f"  Offset: {offset_fit:.3f} LSB")

# ── 4. Smooth INL ─────────────────────────────────────────────────────────────
# Moving average removes the measurement-grid quantisation oscillation.
# mode='same' preserves array length but introduces edge effects — trim
# half a window from each end to avoid them.

inl_smooth = np.convolve(inl_raw, np.ones(SMOOTH_WINDOW) / SMOOTH_WINDOW, mode='same')
trim       = SMOOTH_WINDOW // 2
vin_trim   = vin_fit[trim:-trim]
inl_trim   = inl_smooth[trim:-trim]

print(f"\nINL summary (raw):")
print(f"  Peak : {inl_raw.max():+.2f} / {inl_raw.min():+.2f} LSB")
print(f"  RMS  : {np.sqrt(np.mean(inl_raw**2)):.2f} LSB")

print(f"\nINL summary (smoothed, {SMOOTH_WINDOW}-point moving average):")
print(f"  Peak : {inl_trim.max():+.2f} / {inl_trim.min():+.2f} LSB")
print(f"  RMS  : {np.sqrt(np.mean(inl_trim**2)):.2f} LSB")

# ── 5. ENOB from smoothed INL RMS ────────────────────────────────────────────

sigma_inl    = np.sqrt(np.mean(inl_trim**2))
signal_power = (N_CODES**2) / 8.0          # full-scale sine, in LSB²
noise_power  = sigma_inl**2 + 1.0/12.0     # nonlinearity + quantisation

sndr_db = 10 * np.log10(signal_power / noise_power)
enob    = (sndr_db - 1.76) / 6.02

print(f"\n── ENOB Results ─────────────────────────────────────────────────────")
print(f"  sigma_INL (smoothed) : {sigma_inl:.2f} LSB")
print(f"  Signal power         : {signal_power:.1f} LSB²")
print(f"  Noise power          : {noise_power:.2f} LSB²")
print(f"  SNDR                 : {sndr_db:.2f} dB")
print(f"  Static ENOB          : {enob:.2f} bits")
print(f"\nNote: static ENOB only — captures INL-driven distortion,")
print(f"not dynamic errors (jitter, metastability, charge injection, etc.).")

# ── 6. INL plot ───────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(vin_fit, inl_raw,    lw=0.8, color='lightsteelblue', label='Raw INL')
ax.plot(vin_trim, inl_trim,  lw=1.5, color='steelblue',      label=f'Smoothed INL ({SMOOTH_WINDOW}-pt avg)')
ax.axhline(0,    color='black', lw=0.5)
ax.axhline(+0.5, color='gray',  lw=0.7, linestyle='--', label='±0.5 LSB')
ax.axhline(-0.5, color='gray',  lw=0.7, linestyle='--')
ax.set_xlabel("Vin (V)")
ax.set_ylabel("INL (LSB)")
ax.set_title(f"INL — Static ENOB = {enob:.2f} bits  |  SNDR = {sndr_db:.2f} dB  |  σ_INL = {sigma_inl:.2f} LSB")
ax.legend()
fig.tight_layout()
inl_path = os.path.join(SCRIPT_DIR, "inl_plot.png")
fig.savefig(inl_path, dpi=150)
print(f"\nINL plot saved to: {inl_path}")

plt.show()
