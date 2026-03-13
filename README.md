# Single_Cell_Res_PBPK
This project is a high-resolution Single-Cell Resolved PBPK (Physiologically Based Pharmacokinetic) Pipeline. It estimates cell-type specific receptor concentrations (nM) by integrating single-cell RNA-seq data with bulk protein abundance and simulates drug-target engagement (TMDD) at the cellular level.

## 📌 Project Overview
The pipeline bridges the gap between transcriptomics and proteomics to provide high-resolution inputs for mechanistic modeling. It automates data collection, applies Bayesian scaling for concentration estimation utilizing literature-based cell volumes (BioNumbers), and runs complex ODE-based simulations to predict drug occupancy across different tissues.

The system features a scalable multi-drug and multi-target architecture, allowing seamless comparisons between different monoclonal antibodies and receptor dynamics.

## 📂 Folder Structure

```text
Single_Cell_Res_PBPK/
├── Scraper/
│   ├── __init__.py
│   ├── hpa_scraper.py      # Scrapes MW and Single-cell RNA (nCPM) from HPA
│   └── paxdb_scraper.py    # Scrapes Bulk protein abundance (PPM) from PaxDb
├── Inference/
│   ├── __init__.py
│   ├── bayesian_ppm.py     # Bayesian MCMC model for Local PPM and nM conversion
│   └── cell_volume.py      # BioNumbers-based cell volume DB (e.g., Fibroblasts: 4000 um3)
├── PBPK/
│   ├── __init__.py
│   ├── config.py           # Master configuration (Drug/Target DB & System PK parameters)
│   ├── equations.py        # Multi-cell TMDD ODE system
│   └── simulator.py        # Numerical solver engine (Scipy Radau)
├── data/                   # Generated CSVs (Input data & Simulation results)
├── plots_results/          # Generated dual-subplot PNG figures
├── .gitignore              # Excludes cache, virtual envs, and generated data
├── requirements.txt        # Core dependencies
├── main.py                 # Step 1: Data Acquisition & Preprocessing
├── main_pbpk.py            # Step 2: PBPK Simulation execution
└── visualisation.py        # Step 3: High-resolution Figure Generation
```

## 🛠 Installation
Ensure you have Python 3.8+ and the Chrome browser installed. We recommend creating a virtual environment before installing the dependencies.


```bash
# Clone the repository
git clone [YOUR_REPO_URL]
cd Single_Cell_Res_PBPK

# Install required dependencies
pip install -r requirements.txt
```

## 🚀 How to Run
Step 1: Data Acquisition & Inference

Scrape HPA and PaxDb, merge datasets, and run Bayesian inference to generate the cell-resolved receptor concentration dataset.

```bash
python main.py --hpa [HPA_URL] --pax [PaxDb_URL]

# Example: EGFR Dataset Generation
python main.py --hpa "https://www.proteinatlas.org/ENSG00000146648-EGFR" --pax "https://pax-db.org/protein/9606/ENSP00000275493"
```

Step 2: PBPK Simulation

Run the ODE solver using literature-based PK parameters (e.g., Shah & Betts 2013). You can explicitly define the target receptor, drug, and custom dose.

```bash
# Example 1: Cetuximab targeting EGFR at standard dose (250mg/m2)
python main_pbpk.py --Target EGFR --Drug Cetuximab --Dose 250.0

# Example 2: Panitumumab targeting EGFR at custom dose
python main_pbpk.py --Target EGFR --Drug Panitumumab --Dose 221.0
```
Results are automatically saved to data/pbpk_results_[target]_[drug]_[dose]mg.csv to prevent overwriting.


Step 3: Visualisation

Generate 2-subplot figures showing Receptor Occupancy (%) and Bound Drug (nM). The y-axis is zero-anchored for clarity, and output files are dynamically named.

```bash
# Generate and save plots for all tissues
python visualisation.py --Target EGFR --Drug Cetuximab --Dose 250.0 --Tissue all

# Generate and save a plot for a specific tissue
python visualisation.py --Target EGFR --Drug Cetuximab --Dose 250.0 --Tissue Kidney
```
Plots are saved in the plots_results/ directory (e.g., plot_egfr_cetuximab_kidney_250.0mg.png).
