from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import pandas as pd
import logging
import os
import random
import time

# Configure logging
logging.basicConfig(filename='news_scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# User-agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0"
]

# Keywords and page limits
KEYWORDS_WITH_PAGES = {
    "Devendra Fadnavis": 30,
    "देवेंद्र फडणवीस": 30,
    # ... (other keywords)
}

def setup_driver():
    """Initialize and configure Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")  # Required for Render
    options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    options.add_argument("start-maximized")
    
    try:
        driver = webdriver.Chrome(service=Service(), options=options)
        logging.info("WebDriver initialized successfully")
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        raise

def scrape_page(driver, keyword, page_num, seen_links):
    """Scrape news titles and links from a single page."""
    data = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='heading']"))
        )
        title_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='heading']")
        link_elements = driver.find_elements(By.CSS_SELECTOR, "a[jsname='YKoRaf']")
        for title_elem, link_elem in zip(title_elements, link_elements):
            link = link_elem.get_attribute("href")
            title = title_elem.text.strip()
            if not link or "google.com" in link or link in seen_links:
                continue
            seen_links.add(link)
            data.append({
                "Keyword": keyword,
                "Page": page_num,
                "Title": title,
                "Links": link
            })
        logging.info(f"Scraped {len(data)} articles from page {page_num} for '{keyword}'")
        return data
    except Exception as e:
        logging.warning(f"Error scraping page {page_num} for '{keyword}': {e}")
        return data

def scrape_keyword(driver, keyword, num_pages, start_date, end_date, seen_links):
    """Scrape all pages for a given keyword."""
    data = []
    search_query = keyword.replace(" ", "+")
    news_url = (
        f"https://www.google.co.in/search?q={search_query}&tbm=nws"
        f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
    )
    try:
        driver.get(news_url)
        logging.info(f"Starting scrape for '{keyword}' at {news_url}")
        for page in range(1, num_pages + 1):
            page_data = scrape_page(driver, keyword, page, seen_links)
            data.extend(page_data)
            if page < num_pages:
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "pnnext"))
                    )
                    next_url = next_button.get_attribute("href")
                    if not next_url:
                        logging.info(f"No more pages for '{keyword}' after page {page}")
                        break
                    driver.get(next_url)
                    time.sleep(random.uniform(1, 3))  # Anti-bot delay
                except Exception as e:
                    logging.info(f"No 'Next' button found for '{keyword}' after page {page}: {e}")
                    break
    except Exception as e:
        logging.error(f"Error processing keyword '{keyword}': {e}")
    return data