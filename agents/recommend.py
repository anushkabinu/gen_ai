"""
Recommender Agent - Ranks and filters phones based on user preferences
Powered by Google Gemini for perfect explanations
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging
import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommenderAgent:
    """Agent responsible for ranking phones based on user priorities and Gemini AI"""
    
    def __init__(self):
        self.priority_weights = {
            'Performance': {
                'ram': 0.35,
                'processor_score': 0.35,
                'storage': 0.15,
                'price': 0.15
            },
            'Camera': {
                'camera_mp': 0.50,
                'price': 0.20,
                'rating': 0.30
            },
            'Battery': {
                'battery_mah': 0.60,
                'price': 0.20,
                'rating': 0.20
            },
            'Display': {
                'display_inches': 0.50,
                'rating': 0.30,
                'price': 0.20
            },
            'Value for Money': {
                'price': 0.40,
                'rating': 0.30,
                'ram': 0.15,
                'battery_mah': 0.15
            }
        }
        
        # Processor scoring (higher is better)
        self.processor_scores = {
            'Snapdragon 8 Gen 3': 100,
            'A17 Pro': 100,
            'Snapdragon 8+ Gen 1': 95,
            'Dimensity 8300': 90,
            'A16 Bionic': 95,
            'Exynos 2400': 90,
            'Dimensity 8200': 88,
            'Snapdragon 782G': 85,
            'A15 Bionic': 90,
            'Dimensity 7200': 80,
            'Snapdragon 7s Gen 2': 78,
            'Snapdragon 7 Gen 3': 80,
            'Exynos 1380': 75,
            'Dimensity 7050': 72,
            'Snapdragon 695': 70,
            'Snapdragon 685': 68,
            'Snapdragon 6 Gen 1': 65,
            'Snapdragon 6s Gen 3': 65,
            'Dimensity 6020': 60,
            'Exynos 1280': 65,
            'Helio G85': 55
        }
        
        # Initialize Gemini
        self.model = None
        api_key = os.getenv('GOOGLE_API_KEY')
        if genai and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ Recommender Agent: Gemini AI initialized")
            except Exception as e:
                logger.error(f"❌ Recommender Agent: Failed to init Gemini: {e}")
                self.model = None
    
    def calculate_score(self, 
                       phone: pd.Series, 
                       priority: str,
                       max_price: float,
                       max_values: Dict[str, float]) -> float:
        """
        Calculate score for a phone based on priority
        
        Args:
            phone: Phone data as pandas Series
            priority: User's priority (Performance, Camera, Battery, Display, Value for Money)
            max_price: Maximum price in the dataset for normalization
            max_values: Dictionary of maximum values for each metric
            
        Returns:
            Normalized score (0-100)
        """
        if priority not in self.priority_weights:
            priority = 'Value for Money'
        
        weights = self.priority_weights[priority]
        score = 0.0
        
        for metric, weight in weights.items():
            if metric == 'processor_score':
                processor = phone.get('processor', '')
                metric_score = self.processor_scores.get(processor, 50)
                normalized = metric_score / 100
            elif metric == 'price':
                # Lower price is better, so invert
                normalized = 1 - (phone.get('price', max_price) / max_price)
            elif metric == 'rating':
                normalized = phone.get('rating', 0) / 5.0
            else:
                max_val = max_values.get(metric, 1)
                if max_val > 0:
                    normalized = phone.get(metric, 0) / max_val
                else:
                    normalized = 0
            
            score += normalized * weight
        
        return score * 100
    
    def recommend_phones(self,
                        phones_df: pd.DataFrame,
                        priority: str = 'Value for Money',
                        top_n: int = 5) -> pd.DataFrame:
        """
        Recommend top N phones based on priority
        
        Args:
            phones_df: DataFrame of phones to rank
            priority: User's priority
            top_n: Number of recommendations to return
            
        Returns:
            DataFrame of top recommended phones with scores
        """
        if len(phones_df) == 0:
            logger.warning("No phones to recommend")
            return pd.DataFrame()
        
        # Calculate max values for normalization
        max_values = {
            'ram': phones_df['ram'].max(),
            'storage': phones_df['storage'].max(),
            'camera_mp': phones_df['camera_mp'].max(),
            'battery_mah': phones_df['battery_mah'].max(),
            'display_inches': phones_df['display_inches'].max()
        }
        
        max_price = phones_df['price'].max()
        
        # Calculate scores
        phones_df = phones_df.copy()
        phones_df['recommendation_score'] = phones_df.apply(
            lambda phone: self.calculate_score(phone, priority, max_price, max_values),
            axis=1
        )
        
        # Sort by score and rating
        recommended = phones_df.sort_values(
            by=['recommendation_score', 'rating'],
            ascending=False
        ).head(top_n)
        
        logger.info(f"Generated {len(recommended)} recommendations for priority: {priority}")
        return recommended
    
    def get_priority_explanation(self, priority: str) -> str:
        """Get explanation of what each priority means"""
        explanations = {
            'Performance': 'Focuses on RAM, processor power, and storage for smooth multitasking and gaming.',
            'Camera': 'Prioritizes camera megapixels and image quality for photography enthusiasts.',
            'Battery': 'Emphasizes battery capacity for long-lasting usage without frequent charging.',
            'Display': 'Optimizes for screen size and quality for media consumption and viewing.',
            'Value for Money': 'Balanced approach considering price, features, and overall ratings.'
        }
        return explanations.get(priority, explanations['Value for Money'])
    
    def get_ai_recommendation_reason(self, phone: Dict, priority: str) -> str:
        """Get AI-generated reason why this phone is recommended"""
        if not self.model:
            return f"Perfect fit for {priority} priority!"
        
        try:
            prompt = f"""Provide a one-line recommendation reason for why this phone is perfect for someone prioritizing {priority}:

Phone: {phone['full_name']}
Price: ₹{phone['price']:,}
RAM: {phone['ram']}GB
Camera: {phone['camera_mp']}MP
Battery: {phone['battery_mah']}mAh
Display: {phone['display_inches']}\"
Processor: {phone['processor']}
Rating: {phone['rating']}/5

Give concise, compelling reason (max 2 lines, with emoji)."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip() if response.text else f"Great choice for {priority}!"
        except Exception as e:
            logger.error(f"Error getting AI recommendation: {e}")
            return f"Excellent option for {priority}!"
    
    def compare_phones(self, phone1: Dict, phone2: Dict) -> Dict[str, str]:
        """
        Compare two phones across different metrics using Gemini AI for perfect explanations
        
        Returns:
            Dictionary with comparison results
        """
        # If Gemini available, use AI for better explanations
        if self.model:
            return self._ai_compare_phones(phone1, phone2)
        else:
            return self._rule_based_compare_phones(phone1, phone2)
    
    def _ai_compare_phones(self, phone1: Dict, phone2: Dict) -> Dict[str, str]:
        """Use Gemini AI for detailed phone comparison"""
        try:
            prompt = f"""Compare these two phones concisely and objectively:

Phone 1: {phone1['full_name']}
- Price: ₹{phone1['price']:,}
- RAM: {phone1['ram']}GB | Storage: {phone1['storage']}GB
- Camera: {phone1['camera_mp']}MP | Battery: {phone1['battery_mah']}mAh
- Display: {phone1['display_inches']}\" | Processor: {phone1['processor']}
- Rating: {phone1['rating']}/5

Phone 2: {phone2['full_name']}
- Price: ₹{phone2['price']:,}
- RAM: {phone2['ram']}GB | Storage: {phone2['storage']}GB
- Camera: {phone2['camera_mp']}MP | Battery: {phone2['battery_mah']}mAh
- Display: {phone2['display_inches']}\" | Processor: {phone2['processor']}
- Rating: {phone2['rating']}/5

Provide comparison in this exact format:
Price: [comparison]
Performance: [comparison]
Camera: [comparison]
Battery: [comparison]
Overall Winner: [who wins and why in one line]"""

            response = self.model.generate_content(prompt)
            lines = response.text.split('\n')
            comparisons = {}
            
            for line in lines:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    comparisons[key.lower().strip()] = value.strip()
            
            return comparisons if comparisons else self._rule_based_compare_phones(phone1, phone2)
        
        except Exception as e:
            logger.error(f"AI comparison error: {e}")
            return self._rule_based_compare_phones(phone1, phone2)
    
    def _rule_based_compare_phones(self, phone1: Dict, phone2: Dict) -> Dict[str, str]:
        """Compare two phones using rule-based approach"""
        comparisons = {}
        
        # Price comparison
        if phone1['price'] < phone2['price']:
            comparisons['price'] = f"{phone1['full_name']} is cheaper by ₹{phone2['price'] - phone1['price']:,}"
        elif phone1['price'] > phone2['price']:
            comparisons['price'] = f"{phone2['full_name']} is cheaper by ₹{phone1['price'] - phone2['price']:,}"
        else:
            comparisons['price'] = "Both phones have the same price"
        
        # RAM comparison
        if phone1['ram'] > phone2['ram']:
            comparisons['ram'] = f"{phone1['full_name']} has {phone1['ram'] - phone2['ram']}GB more RAM"
        elif phone1['ram'] < phone2['ram']:
            comparisons['ram'] = f"{phone2['full_name']} has {phone2['ram'] - phone1['ram']}GB more RAM"
        else:
            comparisons['ram'] = "Both have the same RAM"
        
        # Camera comparison
        if phone1['camera_mp'] > phone2['camera_mp']:
            comparisons['camera'] = f"{phone1['full_name']} has {phone1['camera_mp'] - phone2['camera_mp']}MP better camera"
        elif phone1['camera_mp'] < phone2['camera_mp']:
            comparisons['camera'] = f"{phone2['full_name']} has {phone2['camera_mp'] - phone1['camera_mp']}MP better camera"
        else:
            comparisons['camera'] = "Both have similar camera specs"
        
        # Battery comparison
        if phone1['battery_mah'] > phone2['battery_mah']:
            comparisons['battery'] = f"{phone1['full_name']} has {phone1['battery_mah'] - phone2['battery_mah']}mAh more battery"
        elif phone1['battery_mah'] < phone2['battery_mah']:
            comparisons['battery'] = f"{phone2['full_name']} has {phone2['battery_mah'] - phone1['battery_mah']}mAh more battery"
        else:
            comparisons['battery'] = "Both have the same battery capacity"
        
        # Rating comparison
        if phone1['rating'] > phone2['rating']:
            comparisons['rating'] = f"{phone1['full_name']} has better ratings"
        elif phone1['rating'] < phone2['rating']:
            comparisons['rating'] = f"{phone2['full_name']} has better ratings"
        else:
            comparisons['rating'] = "Both have similar ratings"
        
        return comparisons