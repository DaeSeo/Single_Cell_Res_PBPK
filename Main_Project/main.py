import os
import argparse
import pandas as pd

# Imports following the local project folder structure
from Scraper.hpa_scraper import HPASingleCellScraper
from Scraper.paxdb_scraper import PaxDbBulkScraper
from Inference.bayesian_ppm import BayesianPPMCalculator

def main():
    # 1. Argument parsing configuration
    parser = argparse.ArgumentParser(description="PBPK Bayesian Data Pipeline")
    parser.add_argument("--hpa", required=True, help="HPA Target URL")
    parser.add_argument("--pax", required=True, help="PaxDb Target URL")
    parser.add_argument("--show-browser", action="store_true", help="Run browser in normal mode (not headless)")
    args = parser.parse_args()

    # Set browser mode
    is_headless = not args.show_browser
    
    # 2. Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Extract target name from the URL (e.g., ENSG00000146648-EGFR -> EGFR)
    target_name = args.hpa.split("-")[-1].split("/")[0] if "-" in args.hpa else "Target"
    
    print(f"\n{'='*50}")
    print(f"🚀 Starting Pipeline for: {target_name}")
    print(f"{'='*50}")

    # ==========================================
    # [Step 1] HPA Scraping (MW & Single Cell RNA)
    # ==========================================
    print(f"\n[Step 1] Scraping HPA Data...")
    hpa_scraper = HPASingleCellScraper(headless=is_headless)
    try:
        hpa_df = hpa_scraper.scrape_target(args.hpa)
        # Use the specific naming convention without number prefixes
        hpa_path = f"data/HPA_SingleCell_{target_name}.csv"
        hpa_df.to_csv(hpa_path, index=False)
        print(f"✅ HPA data saved to {hpa_path}")
    finally:
        hpa_scraper.close()

    # ==========================================
    # [Step 2] PaxDb Scraping (Bulk Protein PPM)
    # ==========================================
    print(f"\n[Step 2] Scraping PaxDb Data...")
    pax_scraper = PaxDbBulkScraper(headless=is_headless)
    try:
        pax_df = pax_scraper.scrape_target(args.pax)
        pax_path = f"data/PaxDb_Bulk_{target_name}.csv"
        pax_df.to_csv(pax_path, index=False)
        print(f"✅ PaxDb data saved to {pax_path}")
    finally:
        pax_scraper.close()

    # ==========================================
    # [Step 3] Data Merging
    # ==========================================
    print(f"\n[Step 3] Merging Datasets...")
    # Merge datasets on the 'tissue' column
    # Only taking 'tissue' and 'bulk_ppm' from PaxDb to join with HPA data
    merged_df = pd.merge(hpa_df, pax_df[['tissue', 'bulk_ppm']], on='tissue', how='left')
    merged_path = f"data/Merged_{target_name}.csv"
    merged_df.to_csv(merged_path, index=False)
    print(f"✅ Merged data saved to {merged_path}")

    # ==========================================
    # [Step 4] Bayesian Inference (Local PPM & nM)
    # ==========================================
    print(f"\n[Step 4] Running Bayesian MCMC Inference...")
    calculator = BayesianPPMCalculator()
    
    # Execute Bayesian inference and nM concentration calculation
    final_df = calculator.calculate(merged_df)
    
    # Save the final processed results
    final_path = f"data/Final_{target_name}_Data.csv"
    final_df.to_csv(final_path, index=False)

    print(f"\n{'='*50}")
    print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"📍 Final Result: {final_path}")
    print(f"{'='*50}")

    # Display a preview of the final dataset
    print("\n[Preview of Final Result]")
    # Ensure standard output columns are visible
    cols_to_show = ['tissue', 'cell_type', 'local_ppm', 'nM_concentration']
    print(final_df[cols_to_show].head(15))

if __name__ == "__main__":
    main()