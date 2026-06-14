from helper.helper import *

## Parameters
N = 10  # Number of bits
V_ref = 1.8  # Reference voltage
T = 300 # Room temperature in Kelvin

C_min = find_minimum_capacitance(N, V_ref, T)
print(f"Minimum Capacitance for {N}-bit SAR ADC: {format_si(C_min, 'F')}")
print(f"V_lsb: {format_si(V_ref / 2**N, 'V')}")
print(f"V_lsb/2 (max noise sigma): {format_si(V_ref / 2**(N+1), 'V')}")
print(f"Minimum C_total from kT/C: {format_si(C_min, 'F')}")