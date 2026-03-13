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
    ax1.set_title(f"Tissue Analysis: {tissue_name.capitalize()} ({target_name.upper()})", 
                  fontsize=16, fontweight='bold')
    ax1.set_ylabel("Occupancy (%)", fontsize=12, fontweight='bold')
    ax1.set_ylim(-5, 105)
    ax1.legend(title="Cell Type", bbox_to_anchor=(1.02, 1), loc='upper left')

    # 2. Bottom Plot: Bound Drug (nM)
    sns.lineplot(data=tissue_df, x='time', y='bound_nM', hue='cell_type', 
                 ax=ax2, palette='tab10', linewidth=2.5, legend=False)
    ax2.set_ylabel("Bound Drug (nM)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Time (days)", fontsize=12)
    ax2.set_ylim(bottom=0)

    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f" └── 📸 Saved: {save_path}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="PBPK Result Visualizer (2-Subplot Mode)")
    parser.add_argument('--Target', type=str, default='EGFR', help="Target receptor (e.g., EGFR)")
    parser.add_argument('--Tissue', type=str, required=True, help="Tissue name or 'all'")
    parser.add_argument('--Drug', type=str, default='Cetuximab', help="Drug name")
    parser.add_argument('--Dose', type=float, default=250.0, help="Dose in mg/m2")
    parser.add_argument('--File', type=str, default=None, help="Custom result CSV path")

    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"📊 Starting PBPK Visualisation")
    print(f"{'='*50}")

    # Dynamic filename matching based on Target, Drug, and Dose
    file_path = args.File if args.File else f"data/pbpk_results_{args.Target.lower()}_{args.Drug.lower()}_{args.Dose}mg.csv"

    if not os.path.exists(file_path):
        print(f"[!] Error: File not found ({file_path}).")
        print(f"[*] Did you run main_pbpk.py for this combination first?")
        return

    df = pd.read_csv(file_path)
    print(f"[*] Successfully loaded results from: {file_path}")

    # Case-insensitive handling for tissue names
    df['tissue_lower'] = df['tissue'].str.lower()
    tissues_present = df['tissue'].unique()
    
    # Ensure output directory exists
    output_dir = "plots_results"
    os.makedirs(output_dir, exist_ok=True)

    if args.Tissue.lower() == 'all':
        print(f"[*] Generating plots for {len(tissues_present)} tissues...")
        for tissue in tissues_present:
            tissue_df = df[df['tissue'] == tissue]
            
            # Dynamic output naming
            filename = f"plot_{args.Target.lower()}_{args.Drug.lower()}_{tissue.lower()}_{args.Dose}mg.png"
            save_name = os.path.join(output_dir, filename)
            
            plot_single_tissue(tissue_df, tissue, args.Target, save_path=save_name)
        print(f"\n✅ All plots successfully generated and saved in './{output_dir}' directory.")
        
    else:
        target_tissue = args.Tissue.lower()
        tissue_df = df[df['tissue_lower'] == target_tissue]
        
        if not tissue_df.empty:
            filename = f"plot_{args.Target.lower()}_{args.Drug.lower()}_{target_tissue}_{args.Dose}mg.png"
            save_name = os.path.join(output_dir, filename)
            
            print(f"[*] Generating plot for specific tissue: {target_tissue.capitalize()}...")
            plot_single_tissue(tissue_df, args.Tissue, args.Target, save_path=save_name)
            print(f"\n✅ Plot successfully saved in './{output_dir}'")
        else:
            print(f"[!] Tissue '{args.Tissue}' not found in the dataset.")
            print(f"[*] Available tissues: {list(tissues_present)}")

if __name__ == "__main__":
    main()