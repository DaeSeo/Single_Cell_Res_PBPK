"""
Web Scraping Package
Automates data collection from Human Protein Atlas (HPA) and PaxDb.
"""

from .hpa_scraper import HPASingleCellScraper
from .paxdb_scraper import PaxDbBulkScraper

__all__ = ['HPASingleCellScraper', 'PaxDbBulkScraper']