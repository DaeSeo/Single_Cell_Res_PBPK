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
        Bayesian Inference Calculator for Local PPM and nM concentration.
        Note: K_organ constants already incorporate the average protein molecular weight (MW_avg).
        """
        # Literature-based K_organ values
        self.tissue_constants = {
            "Skin": 4.20, "Liver": 3.78, "Kidney": 3.36, "Heart": 2.52,
            "Lung": 2.10, "Brain": 2.10, "Breast": 1.68, "Blood": 0.08, "Plasma": 0.08
        }

    def run_inference(self, ncpm_values, bulk_ppm_val):
        """
        Estimates Local PPM per cell type using MCMC sampling.
        Model: Local_PPM = alpha * nCPM * theta
        """
        # Normalize nCPM to improve numerical stability during sampling
        max_ncpm = np.max(ncpm_values)
        scaled_ncpm = ncpm_values / (max_ncpm if max_ncpm > 0 else 1.0)

        with pm.Model() as model:
            # Global scaling factor (RNA to Protein ratio)
            alpha = pm.HalfNormal('alpha', sigma=bulk_ppm_val * 2)
            
            # Cell-type specific variation (Translation efficiency/Stability)
            theta = pm.Lognormal('theta', mu=0, sigma=0.4, shape=len(ncpm_values))
            
            # Deterministic calculation of Local PPM
            ppm_pred = pm.Deterministic('ppm_pred', alpha * scaled_ncpm * theta)
            
            # Expected Bulk PPM as the mean of Local PPMs
            bulk_pred = ppm_pred.mean()
            
            # Likelihood based on observed Bulk PPM
            obs = pm.Normal('obs', mu=bulk_pred, sigma=bulk_ppm_val * 0.1, observed=bulk_ppm_val)
            
            # Sampling with NUTS sampler
            trace = pm.sample(draws=1000, tune=1000, chains=1, progressbar=False, random_seed=42)

        # Extract the mean values from the posterior distribution
        summary = az.summary(trace, var_names=['ppm_pred'], kind='stats')
        return summary['mean'].values

    def calculate(self, df):
        """
        Processes the merged dataframe to compute Bayesian PPM and final nM concentration.
        Also calculates the nM concentration of the bulk tissue.
        """
        df = df.copy()
        
        # Preprocessing: Ensure numeric types and fill missing values
        df['nCPM'] = pd.to_numeric(df['nCPM'], errors='coerce').fillna(0)
        df['bulk_ppm'] = pd.to_numeric(df['bulk_ppm'], errors='coerce')
        
        # Initialize result columns
        df['local_ppm'] = 0.0
        df['nM_concentration'] = 0.0
        df['bulk_nM_concentration'] = 0.0

        # Iterate through each unique tissue in the dataset
        for tissue in df['tissue'].unique():
            mask = df['tissue'] == tissue
            tissue_data = df[mask]
            
            bulk_val = tissue_data['bulk_ppm'].iloc[0]
            ncpm_vals = tissue_data['nCPM'].values
            
            # Skip processing if critical data is missing
            if pd.isna(bulk_val) or bulk_val <= 0 or np.sum(ncpm_vals) == 0:
                continue

            print(f"[*] Inferring Local PPM for {tissue}...")

            try:
                # 1. Estimate Local PPM using Bayesian Inference
                inferred_ppms = self.run_inference(ncpm_vals, bulk_val)
                df.loc[mask, 'local_ppm'] = inferred_ppms
                
                # 2. Match the tissue name to its corresponding K_organ constant
                k_organ = next((v for k, v in self.tissue_constants.items() if k.lower() in tissue.lower()), None)
                
                if k_organ:
                    # 3. Unit Conversion: nM = PPM * K_organ
                    # Calculate cell-specific nM
                    df.loc[mask, 'nM_concentration'] = inferred_ppms * k_organ
                    
                    # 4. Calculate total tissue nM based on bulk value
                    # This represents the average nM concentration for the whole tissue
                    df.loc[mask, 'bulk_nM_concentration'] = bulk_val * k_organ
                else:
                    df.loc[mask, 'nM_concentration'] = np.nan
                    df.loc[mask, 'bulk_nM_concentration'] = np.nan
                    print(f"     -> [Warning] No K_organ constant found for {tissue}.")

            except Exception as e:
                print(f"     -> [Error] MCMC failed for {tissue}: {e}")

        return df