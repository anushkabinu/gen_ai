"""
Web Scraper Agent - Fetches live phone data from Flipkart & GSMArena
Uses Selenium + BeautifulSoup + Gemini AI for intelligent scraping
"""
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import requests
from bs4 import BeautifulSoup

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data directory for caching
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


class WebScraperAgent:
    """Agent for scraping live phone data from multiple sources"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Initialize Gemini for intelligent data extraction
        self.model = None
        api_key = os.getenv('GOOGLE_API_KEY')
        if genai and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ Web Scraper: Gemini AI initialized")
            except Exception as e:
                logger.error(f"❌ Web Scraper: Failed to init Gemini: {e}")
    
    # ==================== FLIPKART SCRAPING ====================
    
    def close_flipkart_popup(self, driver):
        """Close Flipkart login popup"""
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✕')]"))
            ).click()
            time.sleep(1)
        except:
            pass
    
    def get_first_text(self, driver, selectors, by=By.CSS_SELECTOR):
        """Try multiple selectors to get text"""
        for selector in selectors:
            try:
                element = driver.find_element(by, selector)
                if element.text.strip():
                    return element.text.strip()
            except:
                continue
        return "N/A"
    
    def get_all_texts(self, driver, selector):
        """Get all texts from selector"""
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            return [e.text.strip() for e in elements if e.text.strip()]
        except:
            return []
    
    def scrape_flipkart_product_details(self, driver, link):
        """Scrape detailed product info from Flipkart including description"""
        driver.get(link)
        self.close_flipkart_popup(driver)
        time.sleep(2)

        # Multiple selectors for robustness
        name_selectors = ["span.VU-ZEz", "span.B_NuCI", "div._4rR01T", "span[class*='product-title']"]
        price_selectors = [
            ".Nx9bqj.CxhGGd", ".Nx9bqj", ".CxhGGd",
            "div._30jeq3", "div._1_WHN1", "div._16Jk6d"
        ]
        rating_selectors = [".ipqd2A", "div._3LWZlK", "div._2d4LTz", ".XQDdHH._6er70b"]
        features_selector = ".xFVion ._7eSDEz"
        
        # Description selectors - try multiple locations
        description_selectors = [
            "div._1mXcCf",  # Main description div
            "div._2418kt",  # Product description
            "div.UVia4p",   # Another description class
            "p._2aZlEw",    # Description paragraph
            "div[class*='description']",
            "div._3eAQiD p",  # Description paragraph in container
            "div._24d_e7 p",  # Another description location
            "div._3GnEXt p",  # Product details paragraph
            ".fMghDE",  # Description class
            "div._3eAQiD",  # Full description div
            "div._3GnEXt"   # Details container
        ]

        name = self.get_first_text(driver, name_selectors)
        price = self.get_first_text(driver, price_selectors)
        rating = self.get_first_text(driver, rating_selectors)
        features = self.get_all_texts(driver, features_selector)
        
        # Get description - try multiple methods
        description = self.get_first_text(driver, description_selectors)
        
        # If not found, try getting all paragraph texts from product details
        if not description or description == "N/A" or len(description.strip()) < 20:
            try:
                # Get all paragraphs that might contain description
                desc_elements = driver.find_elements(By.CSS_SELECTOR, "div._3eAQiD p, div._3GnEXt p, div._24d_e7 p")
                if desc_elements:
                    description = " ".join([e.text.strip() for e in desc_elements if e.text.strip() and len(e.text.strip()) > 10])
            except:
                pass
        
        # Last resort: try meta tags
        if not description or description == "N/A" or len(description.strip()) < 20:
            try:
                meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']")
                description = meta_desc.get_attribute("content") if meta_desc else "N/A"
            except:
                description = "N/A"

        return {
            "name": name,
            "price": price,
            "rating": rating,
            "features": features,
            "description": description,
            "url": link
        }
    
    def scrape_flipkart(self, query: str, max_products: int = 20, headless: bool = True) -> List[Dict]:
        """
        Scrape phones from Flipkart search
        
        Args:
            query: Search query (e.g., "smartphone 2024")
            max_products: Max number of products to scrape
            headless: Run browser in headless mode
            
        Returns:
            List of structured phone dictionaries
        """
        # Intelligent query processing
        search_query = query.strip()
        query_lower = search_query.lower()
        
        # Brand names that indicate we're looking for phones
        phone_brands = ['iphone', 'samsung', 'galaxy', 'redmi', 'realme', 'oneplus', 'vivo', 
                       'oppo', 'poco', 'nokia', 'motorola', 'xiaomi', 'nothing', 'iqoo', 
                       'pixel', 'apple', 'mi', 'honor']
        
        # Check if query already has phone/mobile keywords or is a specific model
        has_phone_keyword = any(word in query_lower for word in ['phone', 'mobile', 'smartphone'])
        has_brand = any(brand in query_lower for brand in phone_brands)
        
        # If it's just a brand name (no model), add "mobile phone"
        # If it's a specific model (has numbers/pro/max/ultra), keep as is
        has_model_indicator = any(indicator in query_lower for indicator in 
                                 ['pro', 'max', 'ultra', 'plus', 'lite', 'mini', 'note', 'edge', 'fold', 'flip']) or \
                             any(char.isdigit() for char in search_query)
        
        if not has_phone_keyword:
            if has_brand and not has_model_indicator:
                # Just a brand name: "Samsung" -> "Samsung mobile phone"
                search_query = f"{search_query} mobile phone"
            elif has_brand and has_model_indicator:
                # Specific model: "iPhone 15 Pro Max" -> keep as is (already specific)
                pass
            else:
                # Generic search: "gaming" -> "gaming mobile phone"
                search_query = f"{search_query} mobile phone"
        
        search_url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}&otracker=search&marketplace=FLIPKART"
        logger.info(f"🔍 Scraping Flipkart: '{query}' -> '{search_query}'")
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1400,900")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        driver = None
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            driver.get(search_url)
            self.close_flipkart_popup(driver)
            time.sleep(2)  # Give page time to load properly

            # Get product links - look for mobile/phone specific links
            product_links = []
            seen = set()
            
            # Try multiple selectors for product links
            selectors = [
                "//a[contains(@href, '/p/')]",
                "//a[@class='CGtC98']",  # Flipkart product link class
                "//a[contains(@class, 'wjcEIp')]"  # Another common class
            ]
            
            all_links = []
            for selector in selectors:
                try:
                    links = driver.find_elements(By.XPATH, selector)
                    all_links.extend(links)
                except:
                    continue

            # Filter for phone/mobile related products
            for l in all_links:
                try:
                    link = l.get_attribute("href")
                    if not link or link in seen or 'flipkart.com' not in link:
                        continue
                    
                    # Check if link contains /p/ (product page indicator)
                    if '/p/' in link:
                        product_links.append(link)
                        seen.add(link)
                    
                    if len(product_links) >= max_products:
                        break
                except:
                    continue

            logger.info(f"🧩 Found {len(product_links)} product links")

            # Scrape each product
            all_products = []
            for i, link in enumerate(product_links, 1):
                logger.info(f"📦 Scraping {i}/{len(product_links)}")
                try:
                    prod = self.scrape_flipkart_product_details(driver, link)
                    all_products.append(prod)
                    time.sleep(0.5)  # Reduced wait time for faster scraping
                except Exception as e:
                    logger.error(f"Error scraping {link}: {e}")
                    continue

            logger.info(f"✅ Scraped {len(all_products)} Flipkart products")
            
            # Convert to structured format
            structured_products = self._structure_flipkart_data(all_products)
            return structured_products
            
        except Exception as e:
            logger.error(f"❌ Flipkart scraping error: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def _structure_flipkart_data(self, raw_products: List[Dict]) -> List[Dict]:
        """Convert raw Flipkart data to structured phone data"""
        structured = []
        
        # Keywords that indicate non-phone items to filter out
        exclude_keywords = ['case', 'cover', 'charger', 'cable', 'screen guard', 'protector', 
                           'earphone', 'headphone', 'adapter', 'battery', 'power bank', 'stand',
                           'holder', 'tempered glass', 'pouch', 'flip cover', 'back cover']
        
        for prod in raw_products:
            try:
                product_name = prod['name'].lower()
                
                # Skip accessories and non-phone items
                if any(keyword in product_name for keyword in exclude_keywords):
                    logger.info(f"⏭️ Skipping accessory: {prod['name']}")
                    continue
                
                # Must have phone/mobile related keywords or be a brand name
                phone_keywords = ['phone', 'mobile', 'smartphone', 'iphone', 'galaxy', 'redmi', 
                                'realme', 'oneplus', 'vivo', 'oppo', 'poco', 'nokia', 'motorola',
                                'samsung', 'xiaomi', 'nothing', 'iqoo', 'pixel']
                
                if not any(keyword in product_name for keyword in phone_keywords):
                    logger.info(f"⏭️ Skipping non-phone: {prod['name']}")
                    continue
                
                # Extract price
                price_text = prod['price'].replace('₹', '').replace(',', '')
                price = int(re.search(r'\d+', price_text).group()) if re.search(r'\d+', price_text) else 0
                
                # Skip if price is too low (likely accessories) or too high (likely error)
                if price < 5000 or price > 200000:
                    logger.info(f"⏭️ Skipping invalid price: {prod['name']} - ₹{price}")
                    continue
                
                # Extract rating
                rating_text = prod['rating']
                rating = float(re.search(r'([\d.]+)', rating_text).group(1)) if re.search(r'([\d.]+)', rating_text) else 0.0
                
                # Use Gemini to extract specs from features
                specs = self._extract_specs_with_ai(prod['name'], prod['features'])
                
                if price > 0:  # Only add if valid
                    structured.append({
                        'full_name': prod['name'],
                        'brand': prod['name'].split()[0] if prod['name'] != 'N/A' else 'Unknown',
                        'model': ' '.join(prod['name'].split()[1:]) if prod['name'] != 'N/A' else 'Unknown',
                        'price': price,
                        'rating': rating,
                        'ram': specs.get('ram', 4),
                        'storage': specs.get('storage', 64),
                        'camera_mp': specs.get('camera_mp', 12),
                        'battery_mah': specs.get('battery_mah', 4000),
                        'display_inches': specs.get('display_inches', 6.5),
                        'processor': specs.get('processor', 'Unknown') if specs.get('processor') != 'Unknown' else prod.get('name', 'Unknown').split()[-1] if 'Snapdragon' in prod.get('name', '') or 'Dimensity' in prod.get('name', '') or 'Bionic' in prod.get('name', '') else 'Unknown',
                        'category': self._categorize_phone(price),
                        'source': 'Flipkart',
                        'url': prod['url'],
                        'description': prod.get('description', 'N/A')
                    })
            except Exception as e:
                logger.error(f"Error structuring product: {e}")
                continue
        
        return structured
    
    def _extract_specs_with_ai(self, name: str, features: List[str]) -> Dict:
        """Use Gemini AI to extract specs from features"""
        if not self.model or not features:
            return self._extract_specs_regex(features)
        
        try:
            features_text = "\n".join(features)
            prompt = f"""Extract phone specifications from these features:

Phone: {name}
Features:
{features_text}

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "ram": <number>,
  "storage": <number>,
  "camera_mp": <number>,
  "battery_mah": <number>,
  "display_inches": <number>,
  "processor": "<name>"
}}

Use defaults if not found: ram=4, storage=64, camera_mp=12, battery_mah=4000, display_inches=6.5, processor="Unknown"."""

            response = self.model.generate_content(prompt)
            text = response.text.strip().replace('```json', '').replace('```', '').strip()
            specs = json.loads(text)
            return specs
        except Exception as e:
            logger.warning(f"AI extraction failed, using regex: {e}")
            return self._extract_specs_regex(features)
    
    def _extract_specs_regex(self, features: List[str]) -> Dict:
        """Fallback: Extract specs using regex"""
        specs = {
            'ram': 4,
            'storage': 64,
            'camera_mp': 12,
            'battery_mah': 4000,
            'display_inches': 6.5,
            'processor': 'Unknown'
        }
        
        features_text = " ".join(features)
        
        # RAM
        ram_match = re.search(r'(\d+)\s*GB\s*RAM', features_text, re.I)
        if ram_match:
            specs['ram'] = int(ram_match.group(1))
        
        # Storage
        storage_match = re.search(r'(\d+)\s*GB\s*(ROM|Storage)', features_text, re.I)
        if storage_match:
            specs['storage'] = int(storage_match.group(1))
        
        # Camera
        camera_match = re.search(r'(\d+)\s*MP', features_text, re.I)
        if camera_match:
            specs['camera_mp'] = int(camera_match.group(1))
        
        # Battery
        battery_match = re.search(r'(\d+)\s*mAh', features_text, re.I)
        if battery_match:
            specs['battery_mah'] = int(battery_match.group(1))
        
        # Display
        display_match = re.search(r'([\d.]+)\s*(?:inch|")', features_text, re.I)
        if display_match:
            specs['display_inches'] = float(display_match.group(1))
        
        return specs
    
    def _categorize_phone(self, price: int) -> str:
        """Categorize phone based on price"""
        if price < 15000:
            return "Budget"
        elif price < 35000:
            return "Mid-range"
        else:
            return "Flagship"
    
    def get_cached_data(self) -> Optional[pd.DataFrame]:
        """Get cached phone data if available and recent"""
        cache_file = self.data_dir / "phones_cache.csv"
        
        if cache_file.exists():
            # Check if cache is less than 24 hours old
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age < 86400:  # 24 hours
                logger.info("📂 Loading cached phone data...")
                df = pd.read_csv(cache_file)
                logger.info(f"✅ Loaded {len(df)} phones from cache")
                return df
        
        return None
    
    def save_to_cache(self, df: pd.DataFrame):
        """Save phone data to cache"""
        cache_file = self.data_dir / "phones_cache.csv"
        df.to_csv(cache_file, index=False)
        logger.info(f"💾 Cached {len(df)} phones to {cache_file}")
    
    def scrape_all(self, max_phones: int = 30) -> pd.DataFrame:
        """
        Scrape phones from Flipkart with intelligent caching
        
        Args:
            max_phones: Maximum phones to scrape
            
        Returns:
            DataFrame with phone data
        """
        # Try cache first
        cached_data = self.get_cached_data()
        if cached_data is not None:
            return cached_data
        
        logger.info("=" * 60)
        logger.info("🌐 SCRAPING LIVE PHONE DATA FROM FLIPKART")
        logger.info("=" * 60)
        
        # Scrape Flipkart
        flipkart_phones = self.scrape_flipkart("smartphone 2024", max_products=max_phones)
        
        if not flipkart_phones:
            logger.error("❌ No phones scraped from Flipkart")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(flipkart_phones)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['full_name'], keep='first')
        
        # Cache for future use
        self.save_to_cache(df)
        
        logger.info("=" * 60)
        logger.info(f"✅ SCRAPING COMPLETE: {len(df)} phones")
        logger.info("=" * 60)
        
        return df
