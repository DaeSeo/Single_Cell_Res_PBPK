import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

class PaxDbBulkScraper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Fix window size to prevent elements from being hidden if the window is too small
        chrome_options.add_argument("--window-size=1920,1080") 
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        self.target_tissues = [
            "Brain", "Lung", "Liver", "Kidney", 
            "Breast", "Heart", "Skin", "Plasma"
        ]

    def scrape_target(self, url):
        target_name = url.split("/")[-1]
        all_data = []

        self.driver.get(url)

        try:
            # 1. Ensure the element is 'clickable', not just 'present', & specify selector (search box inside the table)
            search_box = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.footable-filtering-search input[type="text"]'))
            )
            
            # 2. Scroll the element to the center of the screen
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_box)
            time.sleep(1) # Wait briefly after scrolling
            
        except TimeoutException:
            print(f"  -> Timeout: Could not find clickable search box for {url}")
            return pd.DataFrame()

        for tissue in self.target_tissues:
            print(f"[{target_name}] Searching Bulk Data for: {tissue} ...")
            
            # Clear the search box value using Javascript (prevents clear() errors)
            self.driver.execute_script("arguments[0].value = '';", search_box)
            search_box.send_keys(tissue)
            
            # Allow time for the table to be filtered
            time.sleep(1.5)
            
            # Collect only visible rows
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.footable tbody tr")
            visible_rows = [r for r in rows if r.is_displayed()]
            
            if visible_rows:
                first_row = visible_rows[0]
                tds = first_row.find_elements(By.TAG_NAME, "td")
                
                if len(tds) >= 3:
                    abundance_td = tds[2]
                    
                    ppm_val = abundance_td.get_attribute("data-sort-value")
                    
                    if not ppm_val:
                        ppm_val = abundance_td.text.split(" ")[0]
                    
                    if "NA" in abundance_td.text or ppm_val == "0":
                        ppm_val = None 
                        
                    all_data.append({
                        "target": target_name,
                        "tissue": tissue,
                        "bulk_ppm": ppm_val
                    })
            else:
                all_data.append({
                    "target": target_name,
                    "tissue": tissue,
                    "bulk_ppm": None
                })

        df = pd.DataFrame(all_data, columns=["target", "tissue", "bulk_ppm"])
        return df

    def close(self):
        self.driver.quit()