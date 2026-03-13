# PBPK/simulator.py
import pandas as pd
import numpy as np
import os
from scipy.integrate import solve_ivp
from pbpk.equations import multi_cell_tmdd_ode
from inference.cell_volume import get_total_volume_L

class PBPKSimulator:
    def __init__(self, data_path, config): 
        self.df = pd.read_csv(data_path)
        self.config = config  
        print(f"[*] Loaded data from {data_path} with {len(self.df)} cell types.")

    def run_all_and_save(self, output_filename="pbpk_results_all.csv", days=56):
        all_results = []
        tissues = self.df['tissue'].unique()

        total_nmol = (self.config.DOSE_MG_M2 * self.config.BSA / self.config.MW * 1e6)
        C_init = total_nmol / self.config.V_CENTRAL

        for tissue in tissues:
            print(f"[*] Simulating: {tissue}")
            tdf = self.df[self.df['tissue'] == tissue].copy()
            n_cells = len(tdf)
            R0 = tdf['nM_concentration'].values
            self.config.ksyn_vec = self.config.K_DEG * R0
            v_cells = np.array([get_total_volume_L(r['cell_type'], r['cells']) for _, r in tdf.iterrows()])
            spec = self.config.TISSUE_SPECS.get(tissue, self.config.TISSUE_SPECS['Default'])
            
            y0 = np.concatenate([[C_init, 0.0, 0.0], R0, np.zeros(n_cells)])
            
            sol = solve_ivp(
                multi_cell_tmdd_ode, (0, days), y0, 
                args=(self.config, n_cells, v_cells, spec),
                t_eval=np.linspace(0, days, 500), method='Radau'
            )

            for i, cell_type in enumerate(tdf['cell_type'].values):
                R_vals = sol.y[3 + i]
                RC_vals = sol.y[3 + n_cells + i] 
                occ = (RC_vals / (R_vals + RC_vals + 1e-9)) * 100
                
                all_results.append(pd.DataFrame({
                    'time': sol.t, 
                    'tissue': tissue, 
                    'cell_type': cell_type, 
                    'occupancy': occ,
                    'bound_nM': RC_vals 
                }))

        os.makedirs("data", exist_ok=True)
        pd.concat(all_results, ignore_index=True).to_csv(os.path.join("data", output_filename), index=False)
        print(f"✅ Full-body simulation saved to data/{output_filename}")