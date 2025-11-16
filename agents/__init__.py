# Agents module for Smart Gadget Advisor
"""
Smart Gadget Advisor - Agent Package
Contains all AI agents for the recommendation system
"""
from .fetch_data import DataFetchAgent
from .recommend import RecommenderAgent
from .chat_agent import ChatAdvisorAgent
from .web_scraper import WebScraperAgent

__all__ = ['DataFetchAgent', 'RecommenderAgent', 'ChatAdvisorAgent', 'WebScraperAgent']