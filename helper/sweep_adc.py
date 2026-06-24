#!/usr/bin/env python3
"""
sweep_adc.py

Runs one ngspice simulation per input voltage, extracts the 10-bit output
code from .meas results, and writes sweep_results.txt.

Place this file in the same directory as sar_adc_tb_v2.spice and run it.
Results are written to sweep_results.txt in the same directory, which
enob.py then reads.
"""

import subprocess
import re
import os

# ── Configuration ─────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE   = os.path.join(SCRIPT_DIR, "sar_adc_tb_v2.spice")
RESULTS    = os.path.join(SCRIPT_DIR, "sweep_results.txt")
TMPFILE    = os.path.join(SCRIPT_DIR, "_sweep_tmp.spice")

# 10mV steps from 0.0 to 1.8V — 181 points
VIN_STEPS  = [round(v * 0.01, 2) for v in range(0, 181)]

N_BITS     = 10
TIMEOUT_S  = 180       # seconds per sim before giving up

# ─────────────────────────────────────────────────────────────────────────────

def patch_netlist(vin: float) -> str:
    with open(TEMPLATE) as f:
        lines = f.readlines()

    out = []
    for line in lines:
        stripped = line.strip().lower()

        # Drop .probe lines — we only need .meas output, not waveforms.
        # This is the main memory-reduction measure.
        if stripped.startswith('.probe'):
            continue

        # Patch input voltage source
        if re.match(r'Vvin\s+vin\s+0\s+DC', line, re.IGNORECASE):
            line = f'Vvin vin 0 DC {vin}\n'

        # Patch .ic initial conditions — all bottom-plate nodes track vin.
        # vdac stays at vcm=0.9 (unchanged). Handles both the main .ic line
        # and any continuation lines starting with +.
        if stripped.startswith('.ic') or (stripped.startswith('+') and 'xcdac' in stripped):
            for node in ['vin_s', 'bp9', 'bp8', 'bp7', 'bp6', 'bp5',
                         'bp4', 'bp3', 'bp2', 'bp1', 'bp0', 'bpt']:
                line = re.sub(
                    rf'v\(xcdac\.{node}\)=[0-9.]+',
                    f'v(xcdac.{node})={vin}',
                    line, flags=re.IGNORECASE
                )

        out.append(line)

    return ''.join(out)


def parse_code(output: str):
    """
    Parse b9..b0 from ngspice .meas output and reconstruct the integer code.
    ngspice prints lines like:  b9                  =  1.800000e+00
    A voltage > 0.9 is logic 1, <= 0.9 is logic 0.
    """
    bits = {}
    for i in range(N_BITS):
        m = re.search(rf'\bb{i}\s*=\s*([0-9.e+\-]+)', output, re.IGNORECASE)
        if not m:
            return None
        bits[i] = 1 if float(m.group(1)) > 0.9 else 0

    return sum(bits[i] << i for i in range(N_BITS))


def run_sim(vin: float):
    netlist = patch_netlist(vin)
    with open(TMPFILE, 'w') as f:
        f.write(netlist)

    result = subprocess.run(
        ['ngspice', '-b', TMPFILE],
        capture_output=True, text=True, timeout=TIMEOUT_S
    )
    combined = result.stdout + result.stderr
    code = parse_code(combined)
    return code, combined


# ── Main sweep ────────────────────────────────────────────────────────────────

print(f"Template : {TEMPLATE}")
print(f"Results  : {RESULTS}")
print(f"Steps    : {len(VIN_STEPS)}  ({VIN_STEPS[0]}V to {VIN_STEPS[-1]}V, 10mV spacing)")
print()

with open(RESULTS, 'w') as rf:
    rf.write("# vin_V  code\n")

failed = []

for i, vin in enumerate(VIN_STEPS):
    print(f"[{i+1:3d}/{len(VIN_STEPS)}]  vin={vin:.2f}V ... ", end='', flush=True)
    try:
        code, raw = run_sim(vin)
        if code is None:
            print("PARSE FAILED")
            print("  Last 500 chars of ngspice output:")
            print("  " + raw[-500:].replace('\n', '\n  '))
            failed.append(vin)
        else:
            print(f"code={code:4d}  ({format(code, '010b')})")
            with open(RESULTS, 'a') as rf:
                rf.write(f"{vin:.2f}  {code}\n")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT (>{TIMEOUT_S}s)")
        failed.append(vin)
    except FileNotFoundError:
        print("\nERROR: ngspice not found. Check that ngspice is on your PATH.")
        break
    except Exception as e:
        print(f"ERROR: {e}")
        failed.append(vin)

print()
print(f"Done. {len(VIN_STEPS) - len(failed)}/{len(VIN_STEPS)} points collected.")
if failed:
    print(f"Failed points: {failed}")
print(f"Results written to: {RESULTS}")
