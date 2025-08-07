"""
Configuration management utilities.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for pipeline settings.
    """
    
    # Supabase settings
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # API keys
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'AdCreativeBot/1.0')
    
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    
    META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
    META_APP_ID = os.getenv('META_APP_ID')
    META_APP_SECRET = os.getenv('META_APP_SECRET')
    
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    # LLM API keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Pipeline settings
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.8'))
    MAX_PARAGRAPHS = int(os.getenv('MAX_PARAGRAPHS', '4'))
    MIN_TEXT_LENGTH = int(os.getenv('MIN_TEXT_LENGTH', '50'))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10'))
    
    # Web scraping settings
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (compatible; AdCreativeBot/1.0)')
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'pipeline.log')
    
    @classmethod
    def validate_required_settings(cls):
        """
        Validate that required configuration settings are present.
        
        Returns:
            tuple: (is_valid: bool, missing_settings: list)
        """
        required_settings = [
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(cls, setting):
                missing_settings.append(setting)
        
        return len(missing_settings) == 0, missing_settings
    
    @classmethod
    def get_api_config(cls, service):
        """
        Get API configuration for a specific service.
        
        Args:
            service (str): Service name (reddit, twitter, meta, linkedin, openai, etc.)
        
        Returns:
            dict: API configuration for the service
        """
        configs = {
            'reddit': {
                'client_id': cls.REDDIT_CLIENT_ID,
                'client_secret': cls.REDDIT_CLIENT_SECRET,
                'user_agent': cls.REDDIT_USER_AGENT
            },
            'twitter': {
                'bearer_token': cls.TWITTER_BEARER_TOKEN,
                'api_key': cls.TWITTER_API_KEY,
                'api_secret': cls.TWITTER_API_SECRET
            },
            'meta': {
                'access_token': cls.META_ACCESS_TOKEN,
                'app_id': cls.META_APP_ID,
                'app_secret': cls.META_APP_SECRET
            },
            'linkedin': {
                'client_id': cls.LINKEDIN_CLIENT_ID,
                'client_secret': cls.LINKEDIN_CLIENT_SECRET
            },
            'openai': {
                'api_key': cls.OPENAI_API_KEY
            },
            'anthropic': {
                'api_key': cls.ANTHROPIC_API_KEY
            },
            'google': {
                'api_key': cls.GOOGLE_API_KEY
            }
        }
        
        return configs.get(service, {})