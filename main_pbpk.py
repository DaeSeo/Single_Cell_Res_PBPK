# main_pbpk.py
import argparse
import os
from PBPK.config import Config
from PBPK.simulator import PBPKSimulator # Ensure this matches your actual class name

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Single-Cell PBPK Platform")
    parser.add_argument('--File', type=str, default='data/Final_EGFR_Data.csv', help='Input scRNA/Proteomics data')
    
    # [Added] Parsers for Drug and Dose
    parser.add_argument('--Drug', type=str, default='Cetuximab', help='Target drug to simulate (e.g., Cetuximab)')
    parser.add_argument('--Dose', type=float, default=None, help='Custom dose in mg/m2 (overrides default drug dose)')
    
    args = parser.parse_args()

    print(f"\n🚀 Starting Single-Cell PBPK Simulation...")
    
    # 1. Initialize Config with parsed drug and dose
    config = Config(drug_name=args.Drug, dose_override=args.Dose)
    
    # 2. Inject config into the Simulator
    sim = PBPKSimulator(data_path=args.File, config=config)
    
    # 3. Generate a dynamic output filename to track drug and dose
    output_filename = f"pbpk_results_{config.drug_name}_{config.DOSE_MG_M2}mg.csv"
    
    # 4. Run simulation and save results
    sim.run_all_and_save(output_filename=output_filename, days=56)

if __name__ == "__main__":
    main()