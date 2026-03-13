# PBPK/equations.py
import numpy as np

def multi_cell_tmdd_ode(t, y, params, n_cells, v_cells_L, spec):
    """
    Standard Permeability-Limited TMDD Model
    y[0]: Cc (Central Plasma), y[1]: Cv (Vascular), y[2]: Cisf (Interstitial)
    """
    C_c, C_v, C_isf = y[0], y[1], y[2]
    R_vec = y[3 : 3+n_cells]
    RC_vec = y[3+n_cells : 3+2*n_cells]

    # 1. Central Plasma (Whole-body elimination)
    dCc_dt = (params.Q / params.V_CENTRAL) * (C_v - C_c) - (params.CL_0 / params.V_CENTRAL) * C_c

    # 2. Tissue Vascular (Cv)
    V_v = params.V_PERIPHERAL * spec['f_v']
    # Kp defines the partition ratio. Drug moves until Cisf = Cv * Kp
    # PS: Permeability-Surface area product
    dCv_dt = (params.Q / V_v) * (C_c - C_v) - (spec['PS'] / V_v) * (C_v - C_isf / spec['Kp'])

    # 3. Interstitial Fluid (Cisf) - Binding with Single Cells
    V_isf = params.V_PERIPHERAL * spec['f_isf']
    binding_flux = params.K_ON * C_isf * R_vec - params.K_OFF * RC_vec
    total_sink = np.sum(binding_flux * (v_cells_L / V_isf))
    
    dCisf_dt = (spec['PS'] / V_isf) * (C_v - C_isf / spec['Kp']) - total_sink

    # 4. Single-Cell Target Dynamics
    dR_dt = params.ksyn_vec - params.K_DEG * R_vec - binding_flux
    dRC_dt = binding_flux - params.K_INT * RC_vec

    return np.concatenate([[dCc_dt, dCv_dt, dCisf_dt], dR_dt, dRC_dt])