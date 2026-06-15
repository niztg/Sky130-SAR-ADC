import matplotlib

matplotlib.use('MacOSX')

import matplotlib.pyplot as plt
import numpy as np

k = 1.38e-23  # Boltzmann constant

def find_minimum_capacitance(N, V_ref, T):
    # Calculate the minimum capacitance using the formula C_min = (k * T) / (V_ref^2 / (2^N))
    V_lsb = V_ref / (2 ** N)  # Least Significant Bit voltage
    C_min = (k * T) / ((V_lsb / 2) ** 2)
    return C_min

def perturb_capacitors(mismatch_std, N, C_unit):
    weights = [2**(N-1-i) for i in range(N)] + [1]
    
    for i, w in enumerate(weights):
        random_error = np.random.normal(0, mismatch_std / np.sqrt(w))
        weights[i] = w * C_unit * (1 + random_error) 

    return weights

def sar_convert_vectorized(V_in_array, cap_weights, V_ref, N):
    cap_weights = np.array(cap_weights)
    C_total = np.sum(cap_weights)
    
    codes = np.zeros(len(V_in_array), dtype=int)
    V_DAC = np.zeros(len(V_in_array))

    for i, cap in enumerate(cap_weights[:-1]):
        V_DAC_trial = V_DAC + (cap / C_total) * V_ref
        keep = V_in_array >= V_DAC_trial
        V_DAC = np.where(keep, V_DAC_trial, V_DAC)
        codes |= (keep.astype(int) << (N - 1 - i))

    return codes

def compute_dnl_inl(cap_weights, V_ref, N):
    V_sweep = np.linspace(0, V_ref, 64 * 2**N)  # 65536 points
    actual_codes = sar_convert_vectorized(V_sweep, cap_weights, V_ref, N)
    
    code_counts = np.bincount(actual_codes, minlength=2**N)
    ideal_counts = len(V_sweep) / (2**N)

    DNL = (code_counts / ideal_counts) - 1
    INL = np.cumsum(DNL)

    return DNL, INL
        
def monte_carlo_simulation(N_trials, mismatch_std, N, C_unit, V_ref):
    max_inl = []
    for i in range(N_trials):
        weights = perturb_capacitors(mismatch_std, N, C_unit)
        dnl, inl = compute_dnl_inl(weights, V_ref, N)
        max_inl.append(np.max(abs(inl)))
    
    return max_inl

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

def monte_carlo_plot(max_inl, bin_no):
    plt.hist(max_inl, bin_no, edgecolor='black')

    plt.xlabel('Max INL')
    plt.ylabel('Amount of trials')

    plt.axvline(x=0.5, color='red', linestyle='--', label='0.5 LSB threshold')

    yield_pct = 100 * np.sum(np.array(max_inl) < 0.5) / len(max_inl)
    plt.title(f'Max INL Distribution — Yield: {yield_pct:.1f}%')

    plt.show()

def compute_yield(max_inl):
    return 100 * np.mean(np.array(max_inl) < 0.5)

def C_unit_array(C_min):
    return np.linspace(C_min, C_min * 100, 20)

def yield_vs_cap_data(C_unit, N_trials, mismatch_std, N, V_ref):
    return [
        compute_yield(monte_carlo_simulation(N_trials, mismatch_std, N, c, V_ref))
        for c in C_unit
    ]

def yield_vs_capacitance_plot(C_unit, yield_data):
    plt.plot(np.array(C_unit) * 1e15, yield_data)
    plt.axhline(y=99, color='red', linestyle='--', label='99% yield target')
    plt.xlabel('C_unit (fF)')
    plt.ylabel('Yield (%)')
    plt.title('Yield vs Unit Capacitance')
    plt.legend()
    plt.grid()
    plt.show()