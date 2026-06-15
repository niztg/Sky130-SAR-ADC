from helper.helper import *

## Parameters
N = 10  # Number of bits
V_ref = 1.8  # Reference voltage
T = 300 # Room temperature in Kelvin
N_trials = 10000

if __name__ == "__main__":
    C_min = find_minimum_capacitance(N, V_ref, T)
    print(f"Minimum Capacitance for {N}-bit SAR ADC: {format_si(C_min, 'F')}")
    print(f"V_lsb: {format_si(V_ref / 2**N, 'V')}")
    print(f"V_lsb/2 (max noise sigma): {format_si(V_ref / 2**(N+1), 'V')}")
    print(f"Minimum C_total from kT/C: {format_si(C_min, 'F')}")

    # max_inl = monte_carlo_simulation(N_trials, 0.01, N, C_min, V_ref)
    # monte_carlo_plot(max_inl, 40, compute_yield(max_inl))

    C_unit = C_unit_array(C_min)
    yield_vs_capacitance_plot(
        C_unit,
        yield_vs_cap_data(
            C_unit,
            2000,
            0.02,
            N,
            V_ref,
            C_min
        )
    )