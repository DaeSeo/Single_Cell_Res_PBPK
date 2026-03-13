# # PBPK/equations.py
# import numpy as np

# def multi_cell_tmdd_ode(t, y, params, n_cells, v_cells_L, spec):
#     """
#     Standard Permeability-Limited TMDD Model
#     y[0]: Cc (Central Plasma), y[1]: Cv (Vascular), y[2]: Cisf (Interstitial)
#     """

#     C_c, C_v, C_isf = y[0], y[1], y[2]
#     R_vec = y[3 : 3+n_cells]
#     RC_vec = y[3+n_cells : 3+2*n_cells]

#     # 1. Central Plasma
#     dCc_dt = (params.Q / params.V_CENTRAL) * (C_v - C_c) - (params.CL_0 / params.V_CENTRAL) * C_c

#     # 2. Tissue Vascular (Cv) - FIXED: Use spec['V_total']
#     V_v = spec['V_total'] * spec['f_v'] 
#     dCv_dt = (params.Q / V_v) * (C_c - C_v) - (spec['PS'] / V_v) * (C_v - C_isf / spec['Kp'])

#     # 3. Interstitial Fluid (Cisf) - FIXED: Use spec['V_total']
#     V_isf = spec['V_total'] * spec['f_isf']
#     binding_flux = params.K_ON * C_isf * R_vec - params.K_OFF * RC_vec
    
#     # Mass Balance: binding_flux is nM/day. Multiply by single cell volume and divide by ISF volume
#     total_sink = np.sum(binding_flux * (v_cells_L / V_isf))
    
#     dCisf_dt = (spec['PS'] / V_isf) * (C_v - C_isf / spec['Kp']) - total_sink

#     # 4. Target Dynamics
#     dR_dt = params.ksyn_vec - params.K_DEG * R_vec - binding_flux
#     dRC_dt = binding_flux - params.K_INT * RC_vec

#     return np.concatenate([[dCc_dt, dCv_dt, dCisf_dt], dR_dt, dRC_dt])


import numpy as np

def full_body_pbpk_ode(t, y, params, system_data):
    """
    Integrated Whole-Body PBPK Model with TMDD & Cardiac Output Distribution
    
    y[0]: Cc (Central Serum Concentration)
    y[offset : offset+len]: State variables for each tissue (Cv, Cisf, R_vec, RC_vec)
    
    system_data: List of dictionaries containing tissue parameters and initial conditions.
    """
    
    Cc = y[0]
    all_derivatives = []
    
    # Starting offset for tissue-specific state variables
    offset = 1 
    
    # Total rate of drug return to the central compartment from all tissues
    total_venous_return_rate = 0.0

    for tissue in system_data:
        spec = tissue['spec']
        n_cells = tissue['n_cells']
        v_cells_L = tissue['v_cells']
        ksyn_vec = tissue['ksyn_vec']
        
        # 0. Apply Cardiac Output Fraction (f_q)
        # Q_organ = Total Cardiac Output * Fraction for this specific organ
        Q_organ = params.Q * spec.get('f_q', 0.05)
        
        # 1. Extract local state variables
        Cv = y[offset]
        Cisf = y[offset + 1]
        R_vec = y[offset + 2 : offset + 2 + n_cells]
        RC_vec = y[offset + 2 + n_cells : offset + 2 + 2 * n_cells]
        
        # 2. Local Volume Calculations
        V_v = spec['V_total'] * spec['f_v']
        V_isf = spec['V_total'] * spec['f_isf']
        
        # 3. Binding Dynamics (TMDD)
        # flux = nM / day
        binding_flux = params.K_ON * Cisf * R_vec - params.K_OFF * RC_vec
        total_sink = np.sum(binding_flux * (v_cells_L / V_isf))
        
        # 4. Local Differential Equations
        # dCv_dt: Inflow from Serum (Q_organ) - Outflow back to Serum - Permeability to ISF
        dCv_dt = (Q_organ / V_v) * (Cc - Cv) - (spec['PS'] / V_v) * (Cv - Cisf / spec['Kp'])
        
        # dCisf_dt: Permeability from Cv - Binding Sink
        dCisf_dt = (spec['PS'] / V_isf) * (Cv - Cisf / spec['Kp']) - total_sink
        
        # dR_dt & dRC_dt: Target dynamics
        dR_dt = ksyn_vec - params.K_DEG * R_vec - binding_flux
        dRC_dt = binding_flux - params.K_INT * RC_vec
        
        # 5. Accumulate Venous Feedback to Central Serum (Cc)
        # Summing the net drug flow from all vascular compartments
        total_venous_return_rate += (Q_organ / params.V_CENTRAL) * (Cv - Cc)
        
        # Store all derivatives for this tissue
        tissue_derivs = np.concatenate([[dCv_dt, dCisf_dt], dR_dt, dRC_dt])
        all_derivatives.append(tissue_derivs)
        
        # Move offset to the next tissue block in y
        offset += (2 + 2 * n_cells)

    # 6. Final Central Serum Equation (Cc)
    # Balanced by sum of all organ feedbacks and linear non-specific clearance (CL_0)
    dCc_dt = total_venous_return_rate - (params.CL_0 / params.V_CENTRAL) * Cc

    # Return as a flattened array for the ODE solver
    return np.concatenate([[dCc_dt], *all_derivatives])