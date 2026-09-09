import numpy as np
import matplotlib.pyplot as plt
from classy import Class

# Configure matplotlib for publication quality
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.labelsize': 14,
    'legend.fontsize': 12,
    'xtick.direction': 'in',
    'ytick.direction': 'in'
})

print("Calculating LCDM Baseline...")
params_base = {'output': 'mPk', 'P_k_max_h/Mpc': 5.0, 'z_max_pk': 0.0, 'gauge': 'newtonian'}
lcdm = Class()
lcdm.set(params_base)
lcdm.compute()

print("Calculating Q-Rubin V3.2 (A0/B0 = 1e-12)...")
params_q = params_base.copy()
params_q.update({
    'M_Q': 1.0, 'a_t': 0.5, 'n_qrubin': 4.0, 'tau_Q': 1.0,
    'A0_qrubin': 1e-12, 'B0_qrubin': 1e-12, 
    'S0_qrubin': 1e-8, 'Gamma0_qrubin': 1e-4, 'D0_qrubin': 1e-4,
    'phi0_qrubin': 1.0
})
q_model = Class()
q_model.set(params_q)
q_model.compute()

k_grid = np.logspace(-3, 0.5, 200) # h/Mpc
pk_lcdm = np.array([lcdm.pk(k, 0.0) for k in k_grid])
pk_q = np.array([q_model.pk(k, 0.0) for k in k_grid])

ratio = pk_q / pk_lcdm

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
fig.subplots_adjust(hspace=0.05)

# Top Panel: Absolute Spectra
ax1.loglog(k_grid, pk_lcdm, 'k-', linewidth=2, label=r'Baseline $\Lambda$CDM')
ax1.loglog(k_grid, pk_q, 'r--', linewidth=2, label=r'Q-Rubin V3.2 ($A_0, B_0 = 10^{-12}$)')
ax1.set_ylabel(r'$P(k)$ $[(\mathrm{Mpc}/h)^3]$')
ax1.legend(loc='lower left')
ax1.grid(True, alpha=0.3)

# Bottom Panel: Ratio
ax2.semilogx(k_grid, ratio, 'r-', linewidth=2)
ax2.axhline(1.0, color='k', linestyle='--', linewidth=1)
ax2.set_xlabel(r'$k$ $[h/\mathrm{Mpc}]$')
ax2.set_ylabel(r'$P_{\mathrm{Q}}/P_{\Lambda\mathrm{CDM}}$')
ax2.set_ylim(0.85, 1.05)
ax2.grid(True, alpha=0.3)

plt.savefig('qrubin_pk_suppression.pdf', bbox_inches='tight', dpi=300)
print("Saved 'qrubin_pk_suppression.pdf'.")
