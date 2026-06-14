import matplotlib.pyplot as plt
import numpy as np

k = 1.38e-23  # Boltzmann constant

def find_minimum_capacitance(N, V_ref, T):
    # Calculate the minimum capacitance using the formula C_min = (k * T) / (V_ref^2 / (2^N))
    V_lsb = V_ref / (2 ** N)  # Least Significant Bit voltage
    C_min = (k * T) / ((V_lsb / 2) ** 2)
    return C_min

def format_si(value, unit):
    prefixes = [
        (1e0,  ''),
        (1e-3, 'm'),
        (1e-6, 'µ'),
        (1e-9, 'n'),
        (1e-12, 'p'),
        (1e-15, 'f'),
    ]
    for factor, prefix in prefixes:
        if value >= factor:
            return f"{value / factor:.2f} {prefix}{unit}"
    return f"{value:.2e} {unit}"