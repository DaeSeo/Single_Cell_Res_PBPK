class Config:
    def __init__(self, drug_name="cetuximab", target_name="egfr", dose_override=None):
        """
        Initialize PBPK configuration.
        Integrates standard literature-based parameters (Shah & Betts 2013, Grisic et al. 2020)
        with a scalable multi-drug and multi-target architecture.
        """
        self.drug_name = drug_name.lower()
        self.target_name = target_name.lower()
        
        # ---------------------------------------------------------
        # [1] System PK (Standard Human 70kg)
        # ---------------------------------------------------------
        self.BSA = 1.9               # Body Surface Area (m^2)
        self.V_CENTRAL = 3.7         # Plasma volume (L)
        self.V_PERIPHERAL = 2.7      # Total accessible tissue volume (L)

        # ---------------------------------------------------------
        # [2] Target Specific Database (TARGET_DB)
        # ---------------------------------------------------------
        TARGET_DB = {
            'egfr': {
                'K_DEG': 1.0,         # EGFR turnover rate (day^-1)
            },
            'erbb2': {                # HER2 data prep
                'K_DEG': 0.25,        # Example ERBB2 turnover rate
            },
            'cd36': {
                'K_DEG': 3.47,         
            }
        }

        # Validate target selection
        if self.target_name not in TARGET_DB:
            print(f"[!] Warning: Target '{self.target_name}' not found in TARGET_DB. Defaulting to 'egfr'.")
            self.target_name = 'egfr'

        # Map Target Parameters
        target_params = TARGET_DB[self.target_name]
        self.K_DEG = target_params['K_DEG']

        # ---------------------------------------------------------
        # [3] Standard Antibody Biodistribution Coefficients (ABC / Kp)
        # Reference: Shah & Betts (2013)
        # ---------------------------------------------------------
        self.TISSUE_SPECS = {
            'Skin':   {'V_total': 10.0, 'f_v': 0.02, 'f_isf': 0.30, 'Kp': 0.157, 'PS': 0.001, 'f_q': 0.05},
            'Liver':  {'V_total': 1.82, 'f_v': 0.14, 'f_isf': 0.16, 'Kp': 0.121, 'PS': 0.050, 'f_q': 0.25}, 
            'Lung':   {'V_total': 0.53, 'f_v': 0.36, 'f_isf': 0.15, 'Kp': 0.149, 'PS': 0.020, 'f_q': 1.00}, 
            'Kidney': {'V_total': 0.31, 'f_v': 0.16, 'f_isf': 0.10, 'Kp': 0.137, 'PS': 0.020, 'f_q': 0.19},
            'Brain':  {'V_total': 1.45, 'f_v': 0.03, 'f_isf': 0.15, 'Kp': 0.00351, 'PS': 0.00001, 'f_q': 0.12}, 
            'Heart':  {'V_total': 0.33, 'f_v': 0.01, 'f_isf': 0.10, 'Kp': 0.100, 'PS': 0.010, 'f_q': 0.04},
            'Default':{'V_total': 2.00, 'f_v': 0.05, 'f_isf': 0.20, 'Kp': 0.100, 'PS': 0.005, 'f_q': 0.05}
        }
        # ---------------------------------------------------------
        # [4] Drug Specific Database (DRUG_DB)
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
                'DOSE_MG_M2': 221.0,     # Corrected dose for 70kg/1.9m2 BSA
                'MW': 147000.0,
                'K_ON': 0.120,
                'K_OFF': 0.0150,
                'K_INT': 0.90,
                'CL_0': 0.40,
                'Q': 0.85
            },
            'plt012': {
                'DOSE_MG_M2': 400.0,
                'MW': 150000.0,
                'K_ON': 0.150,          # Standard high-affinity mAb
                'K_OFF': 0.015,         # K_D = 0.1 nM
                'K_INT': 1.4,           # Complex internalization (t1/2 ~ 12h)
                'CL_0': 0.35,
                'Q': 0.90
            },
        }

        # Validate drug selection
        if self.drug_name not in DRUG_DB:
            print(f"[!] Warning: Drug '{self.drug_name}' not found in DRUG_DB. Defaulting to 'cetuximab'.")
            self.drug_name = 'cetuximab'
            
        # Map Drug Parameters
        drug_params = DRUG_DB[self.drug_name]
        self.DOSE_MG_M2 = drug_params['DOSE_MG_M2']
        self.MW = drug_params['MW']
        self.K_ON = drug_params['K_ON']
        self.K_OFF = drug_params['K_OFF']
        self.K_INT = drug_params['K_INT']
        self.CL_0 = drug_params['CL_0']
        self.Q = drug_params['Q']
        
        # ---------------------------------------------------------
        # [5] Apply Custom Dose Override (From Terminal Parser)
        # ---------------------------------------------------------
        if dose_override is not None:
            print(f"[*] Overriding default dose ({self.DOSE_MG_M2} mg/m2) with user input: {dose_override} mg/m2")
            self.DOSE_MG_M2 = float(dose_override)
            
        print(f"[*] Config loaded | Drug: {self.drug_name.capitalize()} | Target: {self.target_name.upper()} | Final Dose: {self.DOSE_MG_M2} mg/m2")