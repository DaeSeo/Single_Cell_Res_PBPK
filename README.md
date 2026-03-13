# Single_Cell_Res_PBPK

This project is a data pipeline designed to estimate cell-type specific receptor concentrations ($nM$) by integrating single-cell RNA-seq data and bulk protein abundance.

## 📌 Project Overview
The goal of this pipeline is to bridge the gap between transcriptomics (RNA) and proteomics (Protein) to provide high-resolution input data for physiological modeling. It automates the collection of biological data and applies Bayesian scaling to estimate local concentrations.

## 📂 Folder Structure

```text
Main_Project/
├── Scraper/
│   ├── hpa_scraper.py      # Scrapes MW (via UniProt) and Single-cell RNA (nCPM) from HPA
│   └── paxdb_scraper.py    # Scrapes Bulk protein abundance (PPM) from PaxDb
├── Inference/
│   └── bayesian_ppm.py     # Bayesian MCMC model for Local PPM and nM conversion
├── data/                   # Directory where generated CSVs are stored
└── main.py                 # Main execution script
```

🛠 Installation
Ensure you have Python 3.9+ and the Chrome browser installed. Install the required libraries using pip:

```bash
pip install pandas numpy selenium beautifulsoup4 pymc arviz webdriver-manager
```

🚀 How to Run
Run the pipeline by providing the HPA and PaxDb URLs for your target protein.

```bash
python main.py --hpa [HPA_URL] --pax [PaxDb_URL]
```

Example (EGFR):
```bash
python main.py \
--hpa [https://www.proteinatlas.org/ENSG00000146648-EGFR](https://www.proteinatlas.org/ENSG00000146648-EGFR) \
--pax [https://pax-db.org/protein/9606/ENSP00000275493](https://pax-db.org/protein/9606/ENSP00000275493)
```
