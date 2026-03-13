# Single_Cell_Res_PBPK
This project is a high-resolution Single-Cell Resolved PBPK (Physiologically Based Pharmacokinetic) Pipeline. It estimates cell-type specific receptor concentrations (nM) by integrating single-cell RNA-seq data with bulk protein abundance and simulates drug-target engagement (TMDD) at the cellular level.

## 📌 Project Overview
The pipeline bridges the gap between transcriptomics and proteomics to provide high-resolution inputs for mechanistic modeling. It automates data collection, applies Bayesian scaling for concentration estimation, and runs complex ODE-based simulations to predict drug occupancy across different tissues.


## 📂 Folder Structure

```text
Single_Cell_Res_PBPK/
├── Scraper/
│   ├── hpa_scraper.py      # Scrapes MW and Single-cell RNA (nCPM) from HPA
│   └── paxdb_scraper.py    # Scrapes Bulk protein abundance (PPM) from PaxDb
├── Inference/
│   ├── bayesian_ppm.py     # Bayesian MCMC model for Local PPM and nM conversion
│   └── cell_volume.py      # Cell volume database for concentration scaling
├── PBPK/
│   ├── config.py           # Master configuration (Drug/System PK parameters)
│   ├── equations.py        # Multi-cell TMDD ODE system
│   └── simulator.py        # Numerical solver engine (Scipy Radau)
├── data/                   # Generated CSVs (Input data & Simulation results)
├── plots_results/          # Generated dual-subplot PNG figures
├── main.py                 # Step 1: Data Acquisition & Preprocessing
├── main_pbpk.py            # Step 2: PBPK Simulation execution
└── visualisation.py        # Step 3: High-resolution Figure Generation
```

🛠 Installation
Ensure you have Python 3.8+ and Chrome browser installed.

```bash
pip install pandas numpy selenium beautifulsoup4 pymc arviz webdriver-manager scipy matplotlib seaborn
```

🚀 How to Run
Step 1: Data Acquisition

Scrape HPA and PaxDb to generate the cell-resolved receptor concentration dataset.


```bash
python main.py --hpa [HPA_URL] --pax [PaxDb_URL]

#Example: EGFR
python main.py --hpa "https://www.proteinatlas.org/ENSG00000146648-EGFR" --pax "https://pax-db.org/protein/9606/ENSP00000275493"
```

Step 2: PBPK Simulation

Run the ODE solver using literature-based PK parameters (e.g., Shah & Betts 2013).

```bash
# Example: Cetuximab at 250mg/m2
python main_pbpk.py --Drug Cetuximab --Dose 250.0
```

Step 3: Visualisation

Generate 2-subplot figures showing Receptor Occupancy (%) and Bound Drug (nM).

```bash
# Generate plots for all tissues
python visualisation.py --Drug Cetuximab --Dose 250.0 --Tissue all
```


