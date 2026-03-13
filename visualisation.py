# # visualisation.py
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import argparse
# import os

# # ... (The plot_single_tissue function remains exactly the same as before) ...
# # Please keep the dual-plot plot_single_tissue function here.

# def main():
#     parser = argparse.ArgumentParser(description="PBPK Result Visualizer (Dual Plot Mode)")
#     parser.add_argument('--Target', type=str, default='EGFR')
#     parser.add_argument('--Tissue', type=str, required=True)
    
#     # [Added] Parsers to automatically find the correct result file
#     parser.add_argument('--Drug', type=str, default='Cetuximab', help='Drug name used in the simulation')
#     parser.add_argument('--Dose', type=float, default=250.0, help='Dose used in the simulation (mg/m2)')
#     # Fallback option to specify exact file manually
#     parser.add_argument('--File', type=str, default=None, help='Direct path to specific CSV file (optional)')

#     args = parser.parse_args()

#     # Automatically construct the filename based on Drug and Dose
#     if args.File:
#         file_path = args.File
#     else:
#         file_path = f"data/pbpk_results_{args.Drug.lower()}_{args.Dose}mg.csv"

#     try:
#         # Load simulation results
#         df = pd.read_csv(file_path)
#         print(f"[*] Successfully loaded results from: {file_path}")
#     except FileNotFoundError:
#         print(f"[!] Error: File not found ({file_path}).")
#         print(f"    Please run the simulation first: python main_pbpk.py --Drug {args.Drug} --Dose {args.Dose}")
#         return

#     # Case-insensitive tissue handling
#     df['tissue_lower'] = df['tissue'].str.lower()
#     tissues_present = df['tissue'].unique()

#     if args.Tissue.lower() == 'all':
#         output_dir = "plots_dual"
#         os.makedirs(output_dir, exist_ok=True)
#         print(f"[*] Batch processing: Generating dual plots for {len(tissues_present)} tissues...")
        
#         for tissue in tissues_present:
#             tissue_df = df[df['tissue'] == tissue]
#             save_name = os.path.join(output_dir, f"dual_{tissue.lower()}.png")
#             plot_single_tissue(tissue_df, tissue, args.Target, save_path=save_name)
#             print(f" > Saved: {save_name}")
            
#         print(f"✅ Batch visualization complete. Results in './{output_dir}'")
#     else:
#         target_tissue = args.Tissue.lower()
#         tissue_df = df[df['tissue_lower'] == target_tissue]
        
#         if not tissue_df.empty:
#             plot_single_tissue(tissue_df, args.Tissue, args.Target)
#         else:
#             print(f"[!] No data found for tissue: {args.Tissue}")
#             print(f"Available tissues: {list(tissues_present)}")

# if __name__ == "__main__":
#     main()

# visualisation.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

def plot_single_tissue(tissue_df, tissue_name, target_name, save_path=None):
    """
    Generates two separate subplots for one tissue:
    1. Upper: Receptor Occupancy (%) over time
    2. Lower: Bound Drug Concentration (nM) over time
    """
    # Professional plot settings
    sns.set_theme(style="whitegrid")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 10), sharex=True)

    # 1. Top Plot: Receptor Occupancy (%)
    sns.lineplot(data=tissue_df, x='time', y='occupancy', hue='cell_type', 
                 ax=ax1, palette='tab10', linewidth=2.5)
    ax1.set_title(f"Tissue Analysis: {tissue_name} ({target_name})", fontsize=16, fontweight='bold')
    ax1.set_ylabel("Occupancy (%)", fontsize=12, fontweight='bold')
    ax1.set_ylim(-5, 105)
    ax1.legend(title="Cell Type", bbox_to_anchor=(1.02, 1), loc='upper left')

    # 2. Bottom Plot: Bound Drug (nM)
    sns.lineplot(data=tissue_df, x='time', y='bound_nM', hue='cell_type', 
                 ax=ax2, palette='tab10', linewidth=2.5, legend=False)
    ax2.set_ylabel("Bound Drug (nM)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Time (days)", fontsize=12)

    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f" > Saved: {save_path}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="PBPK Result Visualizer (2-Subplot Mode)")
    parser.add_argument('--Target', type=str, default='EGFR')
    parser.add_argument('--Tissue', type=str, required=True, help="Tissue name or 'all'")
    parser.add_argument('--Drug', type=str, default='Cetuximab')
    parser.add_argument('--Dose', type=float, default=250.0)
    parser.add_argument('--File', type=str, default=None)

    args = parser.parse_args()

    # Dynamic filename matching
    file_path = args.File if args.File else f"data/pbpk_results_{args.Drug.lower()}_{args.Dose}mg.csv"

    if not os.path.exists(file_path):
        print(f"[!] Error: File not found ({file_path}). Check simulation results.")
        return

    df = pd.read_csv(file_path)
    print(f"[*] Successfully loaded results from: {file_path}")

    # Case-insensitive handling
    df['tissue_lower'] = df['tissue'].str.lower()
    tissues_present = df['tissue'].unique()

    if args.Tissue.lower() == 'all':
        output_dir = "plots_results"
        os.makedirs(output_dir, exist_ok=True)
        print(f"[*] Generating plots for {len(tissues_present)} tissues...")
        for tissue in tissues_present:
            tissue_df = df[df['tissue'] == tissue]
            save_name = os.path.join(output_dir, f"plot_{tissue.lower()}.png")
            plot_single_tissue(tissue_df, tissue, args.Target, save_path=save_name)
        print(f"✅ All plots saved in './{output_dir}'")
    else:
        target_tissue = args.Tissue.lower()
        tissue_df = df[df['tissue_lower'] == target_tissue]
        if not tissue_df.empty:
            plot_single_tissue(tissue_df, args.Tissue, args.Target)
        else:
            print(f"[!] Tissue '{args.Tissue}' not found. Available: {list(tissues_present)}")

if __name__ == "__main__":
    main()