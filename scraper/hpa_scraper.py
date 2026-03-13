import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class HPASingleCellScraper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        self.target_tissues = {
            "Brain": "brain", "Lung": "lung", "Liver": "liver",
            "Kidney": "kidney", "Breast": "breast", "Heart": "heart+muscle", 
            "Skin": "skin", "Blood": "blood"
        }

    def _extract_mw(self, base_url):
        """
        1. Navigate to HPA structure page.
        2. Find the first SwissProt link in the 'PROTEIN INFORMATION' table.
        3. Jump to UniProt #sequences and extract Mass (Da).
        """
        # Ensure we are looking at the structure page
        struct_url = base_url.rstrip('/') + "/structure"
        print(f"[*] Navigating to HPA Structure: {struct_url}")
        self.driver.get(struct_url)
        
        try:
            # Step 1: Find the first SwissProt (UniProt) link in the table
            wait = WebDriverWait(self.driver, 15)
            # Find the table with class 'dark border' and locate the first uniprot link
            uniprot_link_elem = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//table[contains(@class, 'dark border')]//a[contains(@href, 'uniprot.org')]")
            ))
            uniprot_url = uniprot_link_elem.get_attribute("href")
            
            # Step 2: Append #sequences for direct access
            if "#sequences" not in uniprot_url:
                uniprot_url = uniprot_url.split('?')[0].rstrip('/') + "#sequences"
            
            print(f"[*] Found SwissProt link. Jumping to: {uniprot_url}")
            self.driver.get(uniprot_url)
            
            # Step 3: Extract Mass (Da) from UniProt
            # Wait for the 'Mass (Da)' title div
            wait_uni = WebDriverWait(self.driver, 20)
            mass_title_xpath = "//div[contains(@class, 'decorated-list-item__title') and text()='Mass (Da)']"
            title_elem = wait_uni.until(EC.presence_of_element_located((By.XPATH, mass_title_xpath)))
            
            # Get the sibling content div
            content_elem = title_elem.find_element(By.XPATH, "./following-sibling::div[contains(@class, 'decorated-list-item__content')]")
            
            # Clean text: "134,277" -> 134277.0
            raw_mass = content_elem.text.replace(',', '').strip()
            mw_value_da = float(raw_mass)
            mw_kda = mw_value_da / 1000.0
            
            print(f"  -> SUCCESS! Extracted Mass: {mw_kda} kDa ({mw_value_da} Da)")
            return mw_kda

        except Exception as e:
            print(f"  -> [Fail] MW extraction failed: {e}")
            return None

    def _parse_title_attribute(self, title_str):
        if not title_str or "nCPM" not in title_str: return None, None, None
        try:
            parts = [p.strip() for p in title_str.split("<br>") if p.strip()]
            return parts[0], parts[1].replace("cells", "").strip(), parts[2].replace("nCPM", "").strip()
        except: return None, None, None

    def scrape_target(self, base_url):
        target_name = base_url.split("-")[-1].split("/")[0]
        base_url = base_url.rstrip('/')
        
        # Get MW first
        mw_kda = self._extract_mw(base_url)
        all_data = []

        # Scrape tissue data (Same as before)
        for tissue_name, url_path in self.target_tissues.items():
            tissue_url = f"{base_url}/single+cell/{url_path}"
            print(f"[{target_name}] Scraping single cell: {tissue_name}...")
            self.driver.get(tissue_url)
            try:
                time.sleep(2)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                for g in soup.select("svg.barchart g.bar_g"):
                    cell_type, cells, ncpm = self._parse_title_attribute(g.get('title', ''))
                    if cell_type:
                        all_data.append({
                            "target": target_name, "tissue": tissue_name, "cell_type": cell_type, 
                            "cells": cells, "nCPM": ncpm, "MW_kDa": mw_kda
                        })
            except: continue

        return pd.DataFrame(all_data)

    def close(self):
        self.driver.quit()