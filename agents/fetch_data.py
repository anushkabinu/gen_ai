"""
Data Fetch Agent - Retrieves LIVE smartphone data from web scraping
Enhanced with Gemini AI for intelligent data extraction
"""
import pandas as pd
import requests
from typing import List, Dict, Optional
import logging
import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Import the web scraper and cache
try:
    from .web_scraper import WebScraperAgent
except ImportError:
    WebScraperAgent = None

try:
    from .phone_cache import PhoneCache
except ImportError:
    PhoneCache = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetchAgent:
    """Agent responsible for fetching LIVE smartphone data with Gemini AI enhancement and ChromaDB caching"""
    
    def __init__(self):
        """Initialize Data Fetch Agent with ChromaDB cache"""
        self.web_scraper = WebScraperAgent() if WebScraperAgent else None
        self.phone_database = pd.DataFrame()  # In-memory database
        
        # Initialize ChromaDB cache
        self.cache = PhoneCache() if PhoneCache else None
        if self.cache:
            # Load all cached phones into memory on startup
            cached_df = self.cache.get_all_cached_phones()
            if not cached_df.empty:
                self.phone_database = cached_df
                logger.info(f"📦 Loaded {len(cached_df)} phones from cache")
        
        # Initialize Gemini
        self.model = None
        api_key = os.getenv('GOOGLE_API_KEY')
        if genai and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ DataFetch Agent: Gemini AI initialized")
            except Exception as e:
                logger.error(f"❌ DataFetch Agent: Failed to init Gemini: {e}")
                self.model = None
        
        logger.info("📱 DataFetch Agent initialized with ChromaDB cache.")
    
    def scrape_live_phones(self, query: str = "smartphone", max_phones: int = 20, max_budget: int = None) -> pd.DataFrame:
        """
        Scrape LIVE phone data from Flipkart (called from frontend on demand)
        First checks cache, only scrapes if not found
        Uses AI to enhance query understanding
        
        Args:
            query: Search query for Flipkart
            max_phones: Maximum phones to scrape
            max_budget: Maximum budget to help filter results
            
        Returns:
            DataFrame with phones (from cache or freshly scraped)
        """
        # Enhance query with AI understanding
        enhanced_query = self._enhance_query_with_ai(query, max_budget)
        # Check cache first with enhanced query
        if self.cache:
            cached_phones = self.cache.search_in_cache(enhanced_query, limit=max_phones)
            if cached_phones and len(cached_phones) > 0:
                logger.info(f"✅ Found {len(cached_phones)} phones in cache for '{enhanced_query}' (original: '{query}')")
                df = pd.DataFrame(cached_phones)
                
                # Add to in-memory database
                self.phone_database = pd.concat([self.phone_database, df], ignore_index=True)
                self.phone_database = self.phone_database.drop_duplicates(subset=['full_name'], keep='last')
                
                return df
        
        # Not in cache - scrape from web
        if not self.web_scraper:
            logger.error("❌ Web scraper not available")
            return pd.DataFrame()
        
        try:
            logger.info(f"🌐 Not in cache. Scraping live data from Flipkart: '{enhanced_query}'...")
            scraped_data = self.web_scraper.scrape_flipkart(enhanced_query, max_products=max_phones)
            
            # Convert list to DataFrame
            if scraped_data and len(scraped_data) > 0:
                df = pd.DataFrame(scraped_data)
                
                # Add to cache
                if self.cache:
                    self.cache.add_phones(scraped_data)
                    logger.info(f"💾 Cached {len(scraped_data)} phones")
                
                # Add to in-memory database
                self.phone_database = pd.concat([self.phone_database, df], ignore_index=True)
                self.phone_database = self.phone_database.drop_duplicates(subset=['full_name'], keep='last')
                logger.info(f"✅ Scraped {len(df)} new phones. Total in database: {len(self.phone_database)}")
                return df
            else:
                logger.warning("⚠️ No phones found during scraping")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"❌ Error scraping live data: {e}")
            return pd.DataFrame()
    
    def fetch_phones(self, 
                     min_price: Optional[int] = None,
                     max_price: Optional[int] = None,
                     brands: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Fetch phones based on filters
        
        Args:
            min_price: Minimum price filter
            max_price: Maximum price filter
            brands: List of preferred brands
            
        Returns:
            Filtered DataFrame of phones
        """
        df = self.phone_database.copy()
        
        # Apply price filters
        if min_price is not None:
            df = df[df['price'] >= min_price]
        if max_price is not None:
            df = df[df['price'] <= max_price]
        
        # Apply brand filter
        if brands and len(brands) > 0:
            df = df[df['brand'].isin(brands)]
        
        logger.info(f"Fetched {len(df)} phones matching criteria")
        return df
    
    def _enhance_query_with_ai(self, query: str, max_budget: int = None) -> str:
        """
        Use AI to enhance user query for better phone search
        Understands intent: gaming, photography, budget, premium, etc.
        """
        if not self.model or not query:
            return query
        
        try:
            budget_hint = f" under ₹{max_budget:,}" if max_budget and max_budget > 0 else ""
            
            prompt = f"""You are a phone search expert. Enhance this search query for better Flipkart results.

User Query: "{query}"{budget_hint}

Rules:
1. If user says "gaming" -> add "gaming phone" or specific gaming phones
2. If user says "camera" or "photography" -> add "camera phone" or phones known for cameras
3. If user mentions brand only (Samsung, iPhone) -> keep brand but make it specific
4. If user mentions specific model (iPhone 15 Pro) -> keep exact model name
5. If budget mentioned -> prefer mid-range or flagship terms accordingly
6. Keep query SHORT and SEARCHABLE (max 4-5 words)
7. Don't add price in query, just phone characteristics

Return ONLY the enhanced search query, nothing else."""
            
            response = self.model.generate_content(prompt)
            enhanced = response.text.strip().strip('"').strip("'")
            
            # Validate enhancement
            if len(enhanced) > 50 or not enhanced:
                return query
            
            logger.info(f"🧠 Query enhanced: '{query}' -> '{enhanced}'")
            return enhanced
            
        except Exception as e:
            logger.error(f"Query enhancement failed: {e}")
            return query
    
    def fetch_phones_by_specs(self,
                               brands: Optional[List[str]] = None,
                               max_price: Optional[int] = None,
                               min_ram: Optional[int] = None,
                               min_camera: Optional[int] = None,
                               min_battery: Optional[int] = None,
                               min_storage: Optional[int] = None,
                               min_display: Optional[float] = None) -> pd.DataFrame:
        """
        Fetch phones based on user-specified specs
        
        Args:
            brands: List of preferred brands
            max_price: Maximum price (budget)
            min_ram: Minimum RAM in GB
            min_camera: Minimum camera MP
            min_battery: Minimum battery mAh
            min_storage: Minimum storage GB
            min_display: Minimum display inches
            
        Returns:
            Filtered DataFrame of phones
        """
        df = self.phone_database.copy()
        
        if df.empty:
            return df
        
        # Apply brand filter
        if brands and len(brands) > 0:
            df = df[df['brand'].isin(brands)]
        
        # Apply budget filter - prioritize phones near max budget
        if max_price is not None and max_price > 0:
            # Filter out phones way over budget
            df = df[df['price'] <= max_price * 1.1]  # Allow 10% over for better options
            # Add a score favoring phones closer to max budget
            df['budget_match_score'] = df['price'].apply(lambda p: 100 - abs(max_price - p) / max_price * 100)
        
        # Apply spec filters
        if min_ram is not None and min_ram > 0:
            df = df[df['ram'] >= min_ram]
        
        if min_camera is not None and min_camera > 0:
            df = df[df['camera_mp'] >= min_camera]
        
        if min_battery is not None and min_battery > 0:
            df = df[df['battery_mah'] >= min_battery]
        
        if min_storage is not None and min_storage > 0:
            df = df[df['storage'] >= min_storage]
        
        if min_display is not None and min_display > 0:
            df = df[df['display_inches'] >= min_display]
        
        logger.info(f"Fetched {len(df)} phones matching spec criteria")
        return df
    
    def get_phone_details(self, phone_name: str) -> Optional[Dict]:
        """Get detailed information about a specific phone"""
        result = self.phone_database[
            self.phone_database['full_name'].str.contains(phone_name, case=False)
        ]
        
        if len(result) > 0:
            return result.iloc[0].to_dict()
        return None
    
    def search_phones(self, 
                     query: str,
                     brand: Optional[str] = None,
                     min_ram: Optional[int] = None,
                     max_ram: Optional[int] = None,
                     min_camera: Optional[int] = None,
                     min_battery: Optional[int] = None) -> pd.DataFrame:
        """
        Search for phones by name and optional specifications
        
        Args:
            query: Phone name or model to search for
            brand: Optional brand filter
            min_ram: Minimum RAM in GB
            max_ram: Maximum RAM in GB
            min_camera: Minimum camera MP
            min_battery: Minimum battery mAh
            
        Returns:
            DataFrame with matching phones
        """
        df = self.phone_database.copy()
        
        # Return empty if database is empty
        if df.empty:
            return df
        
        # Search by name or model
        if query and query.strip():
            df = df[df['full_name'].str.contains(query, case=False, na=False) | 
                    df['model'].str.contains(query, case=False, na=False)]
        
        # Apply additional filters
        if brand:
            df = df[df['brand'].str.contains(brand, case=False, na=False)]
        
        if min_ram is not None:
            df = df[df['ram'] >= min_ram]
        
        if max_ram is not None:
            df = df[df['ram'] <= max_ram]
        
        if min_camera is not None:
            df = df[df['camera_mp'] >= min_camera]
        
        if min_battery is not None:
            df = df[df['battery_mah'] >= min_battery]
        
        logger.info(f"Found {len(df)} phones matching search criteria: {query}")
        return df
    
    def get_all_brands(self) -> List[str]:
        """Get list of all available brands"""
        if self.phone_database.empty:
            return []
        return sorted(self.phone_database['brand'].unique().tolist())
    
    def get_price_range(self) -> tuple:
        """Get the min and max price in database"""
        if self.phone_database.empty:
            return (0, 200000)  # Default range
        return (
            int(self.phone_database['price'].min()),
            int(self.phone_database['price'].max())
        )
    
    def get_ai_phone_insight(self, phone: Dict) -> str:
        """Get AI-generated insight about a specific phone"""
        if not self.model:
            return self._default_phone_insight(phone)
        
        try:
            prompt = f"""Provide a brief, compelling insight about this phone (max 3 lines):

{phone['full_name']} - ₹{phone['price']:,}
Specs: {phone['ram']}GB RAM, {phone['storage']}GB Storage, {phone['camera_mp']}MP Camera, {phone['battery_mah']}mAh Battery
Display: {phone['display_inches']}\", Processor: {phone['processor']}
Rating: {phone['rating']}/5, Category: {phone.get('category', 'Flagship')}

Focus on:
1. Real-world performance
2. Who should buy it
3. Best feature"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip() if response.text else self._default_phone_insight(phone)
        
        except Exception as e:
            logger.error(f"Error getting phone insight: {e}")
            return self._default_phone_insight(phone)
    
    def _default_phone_insight(self, phone: Dict) -> str:
        """Default phone insight when AI is unavailable"""
        insight = f"📱 **{phone['full_name']}** ({phone.get('category', 'Flagship')})\n"
        insight += f"💰 At ₹{phone['price']:,}, this phone offers {phone['ram']}GB RAM and {phone['camera_mp']}MP camera.\n"
        insight += f"⭐ Rated {phone['rating']}/5 - {'Perfect for everyday use' if phone['price'] < 30000 else 'Premium experience'}"
        return insight