import numpy as np
from classy import Class

print("="*70)
print("Q-RUBIN V3.2: S_8 TENSION SUPPRESSION SWEEP")
print("="*70)

# Base LCDM parameters
params_base = {
    'output': 'mPk',
    'P_k_max_h/Mpc': 1.0,
    'z_max_pk': 0.0,
    'gauge': 'newtonian'
}

# 1. Run LCDM Baseline
lcdm = Class()
lcdm.set(params_base)
lcdm.compute()
sigma8_lcdm = lcdm.sigma8()
Omega_m_lcdm = lcdm.Omega_m()
S8_lcdm = sigma8_lcdm * np.sqrt(Omega_m_lcdm / 0.3)
print(f"LCDM Baseline | S_8: {S8_lcdm:.4f} | sigma_8: {sigma8_lcdm:.4f} | Omega_m: {Omega_m_lcdm:.4f}")
lcdm.struct_cleanup()

# 2. Sweep Q-Rubin Couplings (Logarithmic steps)
print("-" * 70)
print(f"{'Coupling A0/B0':<15} | {'S_8':<8} | {'sigma_8':<8} | {'Delta S_8 (%)':<15}")
print("-" * 70)

couplings = [1e-14, 1e-13, 1e-12, 1e-11, 5e-11]

for c in couplings:
    params_q = params_base.copy()
    params_q.update({
        'M_Q': 1.0, 'a_t': 0.5, 'n_qrubin': 4.0, 'tau_Q': 1.0,
        'A0_qrubin': c, 'B0_qrubin': c, 
        'S0_qrubin': 1e-8, 'Gamma0_qrubin': 1e-4, 'D0_qrubin': 1e-4,
        'phi0_qrubin': 1.0
    })
    
    q_model = Class()
    q_model.set(params_q)
    try:
        q_model.compute()
        sig8 = q_model.sigma8()
        Om_m = q_model.Omega_m()
        s8 = sig8 * np.sqrt(Om_m / 0.3)
        shift = ((s8 - S8_lcdm) / S8_lcdm) * 100
        
        print(f"{c:<15.1e} | {s8:<8.4f} | {sig8:<8.4f} | {shift:>8.2f} %")
    except Exception as e:
        print(f"{c:<15.1e} | FAILED INTEGRATION")
        
    q_model.struct_cleanup()
    q_model.empty()

print("="*70)
