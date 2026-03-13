# # PBPK/config.py

# class CetuximabConfig:
#     """
#     Standard PBPK Parameters for Cetuximab (Monoclonal Antibody)
#     References:
#     - Shah & Betts (2013): Antibody Biodistribution Coefficients (ABC)
#     - Grisic et al. (2020): Population PK for Cetuximab
#     """
#     # --- Drug Specific (Cetuximab) ---
#     MW = 145781.6
#     K_ON = 0.112            # nM^-1 * day^-1
#     K_OFF = 0.0168          # day^-1
#     K_INT = 0.95            # day^-1
    
#     # --- System PK (Standard Human 70kg) ---
#     V_CENTRAL = 3.7         # Plasma volume (L)
#     V_PERIPHERAL = 2.7      # Total accessible tissue volume (L)
#     CL_0 = 0.42             # Non-specific clearance (L/day)
#     Q = 0.88                # Inter-compartmental clearance (L/day)
    
#     # --- Target (EGFR) ---
#     K_DEG = 1.0             # EGFR turnover rate (day^-1)

#     # --- Standard Antibody Biodistribution Coefficients (ABC / Kp) ---
#     # From Shah & Betts (2013) - These define the equilibrium partition
#     TISSUE_SPECS = {
#         'Skin':   {'f_v': 0.02, 'f_isf': 0.30, 'Kp': 0.157,   'PS': 0.001},
#         'Liver':  {'f_v': 0.14, 'f_isf': 0.16, 'Kp': 0.121,   'PS': 0.050}, # Leaky
#         'Lung':   {'f_v': 0.36, 'f_isf': 0.15, 'Kp': 0.149,   'PS': 0.020},
#         'Kidney': {'f_v': 0.16, 'f_isf': 0.10, 'Kp': 0.137,   'PS': 0.020},
#         'Brain':  {'f_v': 0.03, 'f_isf': 0.15, 'Kp': 0.00351, 'PS': 0.00001}, # Blood-Brain Barrier
#         'Default':{'f_v': 0.05, 'f_isf': 0.20, 'Kp': 0.100,   'PS': 0.005}
#     }

#     # --- Dosing ---
#     DOSE_MG_M2 = 200
#     BSA = 1.9


# PBPK/config.py

class Config:
    def __init__(self, drug_name="cetuximab", dose_override=None):
        """
        Initialize PBPK configuration.
        Integrates standard literature-based parameters (Shah & Betts 2013, Grisic et al. 2020)
        with a scalable multi-drug architecture and terminal-based dose overriding.
        """
        self.drug_name = drug_name.lower()
        
        # ---------------------------------------------------------
        # [1] System PK (Standard Human 70kg)
        # ---------------------------------------------------------
        self.BSA = 1.9               # Body Surface Area (m^2)
        self.V_CENTRAL = 3.7         # Plasma volume (L)
        self.V_PERIPHERAL = 2.7      # Total accessible tissue volume (L)
        
        # --- Target (EGFR) ---
        self.K_DEG = 1.0             # EGFR turnover rate (day^-1)

        # ---------------------------------------------------------
        # [2] Standard Antibody Biodistribution Coefficients (ABC / Kp)
        # Reference: Shah & Betts (2013) - Equilibrium partition definitions
        # ---------------------------------------------------------
        self.TISSUE_SPECS = {
            'Skin':   {'f_v': 0.02, 'f_isf': 0.30, 'Kp': 0.157,   'PS': 0.001},
            'Liver':  {'f_v': 0.14, 'f_isf': 0.16, 'Kp': 0.121,   'PS': 0.050}, # Leaky
            'Lung':   {'f_v': 0.36, 'f_isf': 0.15, 'Kp': 0.149,   'PS': 0.020},
            'Kidney': {'f_v': 0.16, 'f_isf': 0.10, 'Kp': 0.137,   'PS': 0.020},
            'Brain':  {'f_v': 0.03, 'f_isf': 0.15, 'Kp': 0.00351, 'PS': 0.00001}, # Blood-Brain Barrier
            'Default':{'f_v': 0.05, 'f_isf': 0.20, 'Kp': 0.100,   'PS': 0.005}
        }

        # ---------------------------------------------------------
        # [3] Drug Specific Database (DRUG_DB)
        # ---------------------------------------------------------
        DRUG_DB = {
            'cetuximab': {
                'DOSE_MG_M2': 250.0,     # Standard clinical dose
                'MW': 145781.6,          # Molecular weight (g/mol)
                'K_ON': 0.112,           # nM^-1 * day^-1
                'K_OFF': 0.0168,         # day^-1
                'K_INT': 0.95,           # day^-1
                'CL_0': 0.42,            # Non-specific clearance (L/day)
                'Q': 0.88                # Inter-compartmental clearance (L/day)
            },
            'panitumumab': {             # Scalable for future comparisons
                'DOSE_MG_M2': 6.0,       # Custom dummy dose
                'MW': 147000.0,
                'K_ON': 0.120,
                'K_OFF': 0.0150,
                'K_INT': 0.90,
                'CL_0': 0.40,
                'Q': 0.85
            }
        }

        # Validate drug selection
        if self.drug_name not in DRUG_DB:
            print(f"[!] Warning: '{self.drug_name}' not found in DRUG_DB. Defaulting to 'cetuximab'.")
            self.drug_name = 'cetuximab'
            
        # ---------------------------------------------------------
        # [4] Parameter Mapping
        # ---------------------------------------------------------
        params = DRUG_DB[self.drug_name]
        
        self.DOSE_MG_M2 = params['DOSE_MG_M2']
        self.MW = params['MW']
        self.K_ON = params['K_ON']
        self.K_OFF = params['K_OFF']
        self.K_INT = params['K_INT']
        self.CL_0 = params['CL_0']
        self.Q = params['Q']
        
        # ---------------------------------------------------------
        # [5] Apply Custom Dose Override (From Terminal Parser)
        # ---------------------------------------------------------
        if dose_override is not None:
            print(f"[*] Overriding default dose ({self.DOSE_MG_M2} mg/m2) with user input: {dose_override} mg/m2")
            self.DOSE_MG_M2 = float(dose_override)
            
        print(f"[*] Config loaded for: {self.drug_name.capitalize()} | Final Dose: {self.DOSE_MG_M2} mg/m2")