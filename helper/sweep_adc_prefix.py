#!/usr/bin/env python3
"""
sweep_adc_prefix.py

Same as sweep_adc.py but runs sar_adc_tb_prefix.spice (pre-nwell-fix
bootstrapped switch) and writes sweep_results_prefix.txt.

Place in the same directory as sar_adc_tb_prefix.spice and cdac_prefix.spice.
"""

import subprocess
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE   = os.path.join(SCRIPT_DIR, "sar_adc_tb_prefix.spice")
RESULTS    = os.path.join(SCRIPT_DIR, "sweep_results_prefix.txt")
TMPFILE    = os.path.join(SCRIPT_DIR, "_sweep_prefix_tmp.spice")

VIN_STEPS  = [round(v * 0.1, 1) for v in range(0, 19)]  # 0.0–1.8V, 0.1V steps
                                                          # coarser than post-fix
                                                          # sweep — just need the
                                                          # shape for the plot

N_BITS    = 10
TIMEOUT_S = 180


def patch_netlist(vin: float) -> str:
    with open(TEMPLATE) as f:
        lines = f.readlines()

    out = []
    for line in lines:
        stripped = line.strip().lower()

        if stripped.startswith('.probe'):
            continue

        if re.match(r'Vvin\s+vin\s+0\s+DC', line, re.IGNORECASE):
            line = f'Vvin vin 0 DC {vin}\n'

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


def parse_code(output: str) -> int:
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
    return parse_code(combined), combined


print(f"Template : {TEMPLATE}")
print(f"Results  : {RESULTS}")
print(f"Steps    : {len(VIN_STEPS)}  ({VIN_STEPS[0]}V to {VIN_STEPS[-1]}V, 0.1V spacing)")
print()

with open(RESULTS, 'w') as rf:
    rf.write("# vin_V  code  (pre-nwell-fix bootstrapped switch)\n")

failed = []

for i, vin in enumerate(VIN_STEPS):
    print(f"[{i+1:3d}/{len(VIN_STEPS)}]  vin={vin:.1f}V ... ", end='', flush=True)
    try:
        code, raw = run_sim(vin)
        if code is None:
            print("PARSE FAILED")
            print("  " + raw[-500:].replace('\n', '\n  '))
            failed.append(vin)
        else:
            print(f"code={code:4d}  ({format(code, '010b')})")
            with open(RESULTS, 'a') as rf:
                rf.write(f"{vin:.1f}  {code}\n")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT (>{TIMEOUT_S}s)")
        failed.append(vin)
    except FileNotFoundError:
        print("\nERROR: ngspice not found.")
        break
    except Exception as e:
        print(f"ERROR: {e}")
        failed.append(vin)

print(f"\nDone. {len(VIN_STEPS) - len(failed)}/{len(VIN_STEPS)} points collected.")
if failed:
    print(f"Failed: {failed}")
