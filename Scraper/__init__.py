"""
Web Scraping Package
Automates data collection from Human Protein Atlas (HPA) and PaxDb.
"""

from .hpa_scraper import HPAScraper
from .paxdb_scraper import PaxDbScraper

__all__ = ['HPASingleCellScraper', 'PaxDbBulkScraper']