# main_pbpk.py
import argparse
import os
from pbpk import Config, PBPKSimulator 

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Single-Cell PBPK Platform")
    parser.add_argument('--File', type=str, default='data/Final_EGFR_Data.csv', help='Input scRNA/Proteomics data')
    parser.add_argument('--Drug', type=str, default='Cetuximab', help='Target drug to simulate (e.g., Cetuximab, Panitumumab)')
    parser.add_argument('--Target', type=str, default='EGFR', help='Target receptor (e.g., EGFR, ERBB2)')
    parser.add_argument('--Dose', type=float, default=None, help='Custom dose in mg/m2 (overrides default drug dose)')
    args = parser.parse_args()

    print(f"\n🚀 Starting Single-Cell PBPK Simulation...")
    
    # 1. Initialize Config with parsed drug, target, and dose
    config = Config(
        drug_name=args.Drug, 
        target_name=args.Target, 
        dose_override=args.Dose
    )
    
    # 2. Inject config into the Simulator
    sim = PBPKSimulator(data_path=args.File, config=config)
    
    # 3. Generate a dynamic output filename to track target, drug, and dose
    # added target_name to prevent overwriting results between different targets
    output_filename = f"pbpk_results_{config.target_name}_{config.drug_name}_{config.DOSE_MG_M2}mg.csv"
    
    # 4. Run simulation and save results
    sim.run_all_and_save(output_filename=output_filename, days=56)

if __name__ == "__main__":
    main()