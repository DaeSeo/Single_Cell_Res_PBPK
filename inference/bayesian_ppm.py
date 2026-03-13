import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import warnings

# Suppress PyMC and specific library warnings
warnings.filterwarnings("ignore")

class BayesianPPMCalculator:
    def __init__(self):
        """
        Bayesian Inference Calculator using Cell Fractions derived from 'cells' count.
        """
        # Literature-based K_organ values
        self.tissue_constants = {
            "Skin": 4.20, "Liver": 3.78, "Kidney": 3.36, "Heart": 2.52,
            "Lung": 2.10, "Brain": 2.10, "Breast": 1.68, "Blood": 0.08, "Plasma": 0.08
        }

    def run_inference(self, ncpm_values, bulk_ppm_val, fractions):
        """
        Estimates Local PPM using cell fractions.
        Likelihood is based on: Bulk_PPM = sum(Local_PPM_i * Fraction_i)
        """
        # Normalize nCPM for numerical stability
        max_ncpm = np.max(ncpm_values)
        scaled_ncpm = ncpm_values / (max_ncpm if max_ncpm > 0 else 1.0)

        with pm.Model() as model:
            # Global scaling factor
            alpha = pm.HalfNormal('alpha', sigma=bulk_ppm_val * 2)
            
            # Cell-type specific variation (Translation efficiency/Stability)
            theta = pm.Lognormal('theta', mu=0, sigma=0.4, shape=len(ncpm_values))
            
            # Deterministic calculation of Local PPM
            ppm_pred = pm.Deterministic('ppm_pred', alpha * scaled_ncpm * theta)
            
            # [KEY CHANGE] Use Dot Product with fractions instead of arithmetic mean
            # Expected Bulk PPM = sum(PPM_i * Fraction_i)
            bulk_pred = pm.math.dot(ppm_pred, fractions)
            
            # Likelihood based on observed Bulk PPM
            obs = pm.Normal('obs', mu=bulk_pred, sigma=bulk_ppm_val * 0.1, observed=bulk_ppm_val)
            
            # Sampling
            trace = pm.sample(draws=1000, tune=1000, chains=1, progressbar=False, random_seed=42)

        summary = az.summary(trace, var_names=['ppm_pred'], kind='stats')
        return summary['mean'].values

    def calculate(self, df):
        """
        Processes the dataframe to compute results using weighted cell fractions.
        """
        df = df.copy()
        
        # Preprocessing: Ensure numeric types
        df['nCPM'] = pd.to_numeric(df['nCPM'], errors='coerce').fillna(0)
        df['bulk_ppm'] = pd.to_numeric(df['bulk_ppm'], errors='coerce')
        # Handle 'cells' column (remove commas if present)
        df['cells'] = pd.to_numeric(df['cells'].astype(str).str.replace(',', ''), errors='coerce').fillna(1)
        
        df['local_ppm'] = 0.0
        df['nM_concentration'] = 0.0
        df['bulk_nM_concentration'] = 0.0

        for tissue in df['tissue'].unique():
            mask = df['tissue'] == tissue
            tissue_data = df[mask]
            
            bulk_val = tissue_data['bulk_ppm'].iloc[0]
            ncpm_vals = tissue_data['nCPM'].values
            cell_counts = tissue_data['cells'].values
            
            if pd.isna(bulk_val) or bulk_val <= 0 or np.sum(ncpm_vals) == 0:
                continue

            # Calculate Fraction per cell type within the tissue
            total_cells = np.sum(cell_counts)
            fractions = cell_counts / total_cells if total_cells > 0 else np.ones(len(cell_counts))/len(cell_counts)

            print(f"[*] Inferring Local PPM for {tissue} (Weighted by Cell Fractions)...")

            try:
                # 1. Estimate Local PPM using weighted inference
                inferred_ppms = self.run_inference(ncpm_vals, bulk_val, fractions)
                df.loc[mask, 'local_ppm'] = inferred_ppms
                
                # 2. Get K_organ constant
                k_organ = next((v for k, v in self.tissue_constants.items() if k.lower() in tissue.lower()), None)
                
                if k_organ:
                    # 3. Unit Conversion: nM = PPM * K_organ
                    df.loc[mask, 'nM_concentration'] = inferred_ppms * k_organ
                    df.loc[mask, 'bulk_nM_concentration'] = bulk_val * k_organ
                else:
                    df.loc[mask, 'nM_concentration'] = np.nan
                    df.loc[mask, 'bulk_nM_concentration'] = np.nan

            except Exception as e:
                print(f"     -> [Error] MCMC failed for {tissue}: {e}")

        return df