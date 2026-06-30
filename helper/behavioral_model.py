import matplotlib
matplotlib.use('MacOSX')
import matplotlib.pyplot as plt
import numpy as np
import os

k = 1.38e-23  # Boltzmann constant

def find_minimum_capacitance(N, V_ref, T):
    # Calculate the minimum capacitance using the formula C_min = (k * T) / (V_ref^2 / (2^N))
    V_lsb = V_ref / (2 ** N)  # Least Significant Bit voltage
    C_min = (k * T) / ((V_lsb / 2) ** 2)
    return C_min

def perturb_capacitors(mismatch_std, N, C_unit, C_min_unit):
    weights = [2**(N-1-i) for i in range(N)] + [1]
    for i, w in enumerate(weights):
        n_cells = w * C_unit / C_min_unit  # total unit cells in this cap
        random_error = np.random.normal(0, mismatch_std / np.sqrt(n_cells))
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
        
def monte_carlo_simulation(N_trials, mismatch_std, N, C_unit, V_ref, C_min_unit):
    max_inl = []
    for i in range(N_trials):
        weights = perturb_capacitors(mismatch_std, N, C_unit, C_min_unit)
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

def monte_carlo_plot(max_inl, bin_no, yield_pct):
    plt.hist(max_inl, bin_no, edgecolor='black')

    plt.xlabel('Max INL')
    plt.ylabel('Amount of trials')

    plt.axvline(x=0.5, color='red', linestyle='--', label='0.5 LSB threshold')
    plt.title(f'Max INL Distribution — Yield: {yield_pct:.1f}%')

    plt.show()

def compute_yield(max_inl):
    return 100 * np.mean(np.array(max_inl) < 0.5)

def C_unit_array(C_min):
    return np.linspace(C_min * 3, C_min * 6, 20) 

def yield_vs_cap_data(C_unit, N_trials, mismatch_std, N, V_ref, C_min_unit):
    return [
        compute_yield(monte_carlo_simulation(N_trials, mismatch_std, N, c, V_ref, C_min_unit))
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

def plot_measured_transfer_function(sweep_file, V_ref, N, operating_range, figures_dir):
    """
    Plots the measured ADC transfer function (output code vs. input voltage)
    from a saved ngspice DC sweep, against the ideal straight-line transfer
    function. sweep_file is a two-column whitespace-separated text file:
    V_in (volts), output code.
    """
    data = np.loadtxt(sweep_file)
    vin, code = data[:, 0], data[:, 1]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot([0, V_ref], [0, 2**N - 1], color='gray', linestyle='--',
            linewidth=1.0, label='Ideal transfer function')
    ax.plot(vin, code, 'o', markersize=3, color='steelblue',
            label='Measured (ngspice sweep)')
    ax.axvspan(operating_range[0], operating_range[1], color='green', alpha=0.08,
               label=f'Operating range ({operating_range[0]:.2f}--{operating_range[1]:.2f} V)')
    ax.set_xlabel('$V_\\mathrm{in}$ (V)')
    ax.set_ylabel('Output code')
    ax.set_title('ADC Transfer Function, 10 mV DC Sweep')
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, V_ref)
    ax.set_ylim(0, 2**N - 1)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'transfer_function.pdf'), dpi=300)
    fig.savefig(os.path.join(figures_dir, 'transfer_function.png'), dpi=300)
    plt.close(fig)
    print(f"Saved transfer_function ({len(vin)} points)")

FIGURES_DIR = "."
os.makedirs(FIGURES_DIR, exist_ok=True)

N       = 10
V_ref   = 1.8
T       = 300
C_min   = find_minimum_capacitance(N, V_ref, T)

# ── Figure 1: Yield vs C_unit sweep ─────────────────────────────────────────
print("Running yield sweep (this takes a few minutes)...")
C_units    = np.linspace(C_min * 3, C_min * 6, 20)
yield_data = yield_vs_cap_data(C_units, 2000, 0.02, N, V_ref, C_min)

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(np.array(C_units) * 1e15, yield_data, color='steelblue', linewidth=1.8)
ax.axhline(y=99, color='red', linestyle='--', linewidth=1.2, label='99% yield target')
ax.axvline(x=25, color='gray', linestyle=':', linewidth=1.2, label='Design target (25 fF)')
ax.set_xlabel('$C_\mathrm{unit}$ (fF)')
ax.set_ylabel('Yield (%)')
ax.set_title('Yield vs Unit Capacitance (2% mismatch, 2000 trials)')
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'yield_vs_cunit.pdf'), dpi=300)
fig.savefig(os.path.join(FIGURES_DIR, 'yield_vs_cunit.png'), dpi=300)
plt.close(fig)
print("Saved yield_vs_cunit")

# ── Figure 2: Monte Carlo histogram at C_unit = 25 fF ───────────────────────
print("Running Monte Carlo histogram (10 000 trials)...")
max_inl   = monte_carlo_simulation(10000, 0.02, N, 25e-15, V_ref, C_min)
yield_pct = compute_yield(max_inl)

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.hist(max_inl, bins=40, edgecolor='black', color='steelblue', alpha=0.85)
ax.axvline(x=0.5, color='red', linestyle='--', linewidth=1.2,
           label='0.5 LSB threshold')
ax.set_xlabel('Max INL (LSB)')
ax.set_ylabel('Number of trials')
ax.set_title(f'Max INL Distribution at $C_{{unit}}$ = 25 fF — Yield: {yield_pct:.1f}%')
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'monte_carlo_histogram.pdf'), dpi=300)
fig.savefig(os.path.join(FIGURES_DIR, 'monte_carlo_histogram.png'), dpi=300)
plt.close(fig)
print("Saved monte_carlo_histogram")

# ── Figure 3: Example DNL / INL at C_unit = 25 fF ───────────────────────────
np.random.seed(42)   # fixed seed so figure is reproducible
weights   = perturb_capacitors(0.02, N, 25e-15, C_min)
dnl, inl  = compute_dnl_inl(weights, V_ref, N)
codes     = np.arange(2**N)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

ax1.plot(codes, dnl, linewidth=0.8, color='steelblue')
ax1.axhline(0,    color='black', linewidth=0.6)
ax1.axhline( 0.5, color='red',  linestyle='--', linewidth=0.8, label='±0.5 LSB')
ax1.axhline(-0.5, color='red',  linestyle='--', linewidth=0.8)
ax1.set_ylabel('DNL (LSB)')
ax1.set_title('DNL and INL — single trial at $C_\mathrm{unit}$ = 25 fF, 2% mismatch')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

ax2.plot(codes, inl, linewidth=0.8, color='darkorange')
ax2.axhline(0,    color='black', linewidth=0.6)
ax2.axhline( 0.5, color='red',  linestyle='--', linewidth=0.8, label='±0.5 LSB')
ax2.axhline(-0.5, color='red',  linestyle='--', linewidth=0.8)
ax2.set_xlabel('Output code')
ax2.set_ylabel('INL (LSB)')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'dnl_inl_example.pdf'), dpi=300)
fig.savefig(os.path.join(FIGURES_DIR, 'dnl_inl_example.png'), dpi=300)
plt.close(fig)
print("Saved dnl_inl_example")

# ── Figure 4: Measured transfer function (code vs. V_in, from ngspice sweep) ─
print("Plotting measured transfer function...")
plot_measured_transfer_function(
    sweep_file='sweep_results.txt',
    V_ref=V_ref,
    N=N,
    operating_range=(0.50, 1.39),
    figures_dir=FIGURES_DIR,
)

print(f"\nAll figures saved to {FIGURES_DIR}")
print(f"C_min = {C_min*1e15:.2f} fF")
print(f"C_unit (design) = 25 fF")
print(f"C_total = {1024 * 25:.0f} fF = {1024 * 25 / 1000:.3f} pF")
print(f"Yield at 25 fF = {yield_pct:.1f}%")
