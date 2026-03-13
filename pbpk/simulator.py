# import pandas as pd
# import numpy as np
# import os
# from scipy.integrate import solve_ivp
# from pbpk.equations import multi_cell_tmdd_ode
# from inference.cell_volume import get_total_volume_L

# class PBPKSimulator:
#     def __init__(self, data_path, config): 
#         self.df = pd.read_csv(data_path)
#         self.config = config  
#         print(f"[*] Loaded data from {data_path} with {len(self.df)} cell types.")

#     def run_all_and_save(self, output_filename="pbpk_results_all.csv", days=120):
#         all_results = []
#         tissues = self.df['tissue'].unique()

#         # Initial Central Concentration
#         total_nmol = (self.config.DOSE_MG_M2 * self.config.BSA / self.config.MW * 1e6)
#         C_init = total_nmol / self.config.V_CENTRAL

#         for tissue in tissues:
#             print(f"[*] Simulating: {tissue}")
#             tdf = self.df[self.df['tissue'] == tissue].copy()
#             n_cells = len(tdf)
#             R0 = tdf['nM_concentration'].values
            
#             # Each tissue has its own ksyn to maintain baseline R0
#             self.config.ksyn_vec = self.config.K_DEG * R0
            
#             v_cells = np.array([get_total_volume_L(r['cell_type'], r['cells']) for _, r in tdf.iterrows()])
#             spec = self.config.TISSUE_SPECS.get(tissue, self.config.TISSUE_SPECS['Default'])
            
#             # Initial conditions
#             y0 = np.concatenate([[C_init, 0.0, 0.0], R0, np.zeros(n_cells)])
            
#             sol = solve_ivp(
#                 multi_cell_tmdd_ode, (0, days), y0, 
#                 args=(self.config, n_cells, v_cells, spec),
#                 t_eval=np.linspace(0, days, 500), method='Radau'
#             )

#             for i, cell_type in enumerate(tdf['cell_type'].values):
#                 R_vals = sol.y[3 + i]
#                 RC_vals = sol.y[3 + n_cells + i] 
#                 occ = (RC_vals / (R_vals + RC_vals + 1e-9)) * 100
                
#                 all_results.append(pd.DataFrame({
#                     'time': sol.t, 
#                     'tissue': tissue, 
#                     'cell_type': cell_type, 
#                     'occupancy': occ,
#                     'bound_nM': RC_vals,
#                     'plasma_conc': sol.y[0] # To monitor central compartment
#                 }))

#         os.makedirs("data", exist_ok=True)
#         pd.concat(all_results, ignore_index=True).to_csv(os.path.join("data", output_filename), index=False)
#         print(f"✅ Full-body simulation saved to data/{output_filename}")


import pandas as pd
import numpy as np
import os
from scipy.integrate import solve_ivp
from pbpk.equations import full_body_pbpk_ode
from inference.cell_volume import get_total_volume_L

class PBPKSimulator:
    def __init__(self, data_path, config): 
        self.df = pd.read_csv(data_path)
        self.config = config  
        print(f"[*] Loaded data from {data_path} with {len(self.df)} cell types.")

    def run_all_and_save(self, output_filename="pbpk_results_all.csv", days=120):
        """
        Runs a single integrated simulation where all organs compete for the drug simultaneously.
        This captures the true systemic TMDD effect (The 'Sink' effect).
        """
        tissues = self.df['tissue'].unique()
        system_data = []
        
        # 1. Prepare Initial Conditions for the Central Compartment (Serum)
        total_nmol = (self.config.DOSE_MG_M2 * self.config.BSA / self.config.MW * 1e6)
        C_init = total_nmol / self.config.V_CENTRAL
        
        # y0 starts with the Central Serum Concentration (Cc)
        y0 = np.array([C_init])
        
        # 2. Construct System Data and State Vector (y0) for all tissues
        print(f"[*] Initializing system parameters for {len(tissues)} tissues...")
        for tissue in tissues:
            tdf = self.df[self.df['tissue'] == tissue].copy()
            n_cells = len(tdf)
            R0 = tdf['nM_concentration'].values
            
            # Calculate tissue-specific cell volumes and ksyn for baseline maintenance
            v_cells = np.array([get_total_volume_L(r['cell_type'], r['cells']) for _, r in tdf.iterrows()])
            ksyn_vec = self.config.K_DEG * R0
            
            # Retrieve tissue specs (including f_q for blood flow distribution)
            spec = self.config.TISSUE_SPECS.get(tissue, self.config.TISSUE_SPECS['Default'])
            
            # Metadata for ODE solver
            system_data.append({
                'name': tissue,
                'n_cells': n_cells,
                'v_cells': v_cells,
                'ksyn_vec': ksyn_vec,
                'spec': spec,
                'tdf': tdf # Stored for result mapping
            })
            
            # Append tissue initial states: [Cv=0, Cisf=0, R=R0, RC=0]
            tissue_y0 = np.concatenate([[0.0, 0.0], R0, np.zeros(n_cells)])
            y0 = np.concatenate([y0, tissue_y0])

        # 3. Execute Integrated Whole-Body Simulation
        print(f"[*] Starting solver: Whole-body Integrated PBPK ({days} days)...")
        sol = solve_ivp(
            full_body_pbpk_ode, (0, days), y0, 
            args=(self.config, system_data),
            t_eval=np.linspace(0, days, 500), method='Radau'
        )
        print(f"[*] Simulation complete. Unpacking results...")

        # 4. Unpack and Process Integrated Results
        all_results = []
        Cc_vals = sol.y[0] # Central Serum concentration (affected by ALL organs)
        
        offset = 1
        for tissue in system_data:
            n_cells = tissue['n_cells']
            tdf = tissue['tdf']
            
            # Map solver output back to specific cells within the tissue
            # Structure in y: [Cc, (Cv, Cisf, R1..n, RC1..n), (Cv, Cisf, R1..n, RC1..n), ...]
            for i, cell_type in enumerate(tdf['cell_type'].values):
                R_vals = sol.y[offset + 2 + i]
                RC_vals = sol.y[offset + 2 + n_cells + i]
                
                # Calculate Receptor Occupancy (%)
                occ = (RC_vals / (R_vals + RC_vals + 1e-9)) * 100
                
                all_results.append(pd.DataFrame({
                    'time': sol.t, 
                    'tissue': tissue['name'], 
                    'cell_type': cell_type, 
                    'occupancy': occ,
                    'bound_nM': RC_vals,
                    'plasma_conc': Cc_vals # Unified central serum concentration
                }))
            
            # Jump to the start of the next tissue block
            offset += (2 + 2 * n_cells)

        # 5. Save final integrated dataset
        os.makedirs("data", exist_ok=True)
        final_df = pd.concat(all_results, ignore_index=True)
        final_df.to_csv(os.path.join("data", output_filename), index=False)
        
        print(f"✅ Integrated PBPK simulation saved: data/{output_filename}")