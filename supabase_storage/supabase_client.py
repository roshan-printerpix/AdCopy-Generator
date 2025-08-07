"""
Supabase Client Module
Initializes and manages Supabase connection and helpers.
"""

import os
from supabase import create_client, Client

class SupabaseManager:
    """
    Manages Supabase client connection and provides helper methods.
    """
    
    def __init__(self):
        self.client = None
        self.url = None
        self.key = None
    
    def initialize_client(self, url=None, key=None):
        """
        Initialize Supabase client with credentials.
        
        Args:
            url (str): Supabase project URL (optional, uses env var if not provided)
            key (str): Supabase API key (optional, uses env var if not provided)
        
        Returns:
            Client: Supabase client instance
        """
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and key must be provided either as parameters or environment variables")
        
        self.client = create_client(self.url, self.key)
        return self.client
    
    def get_client(self):
        """
        Get the current Supabase client instance.
        
        Returns:
            Client: Supabase client instance
        """
        if not self.client:
            self.initialize_client()
        
        return self.client
    
    def test_connection(self):
        """
        Test the Supabase connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            client = self.get_client()
            # Try a simple query to test connection
            result = client.table('insights').select('id').limit(1).execute()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_table_info(self, table_name='insights'):
        """
        Get information about a table structure.
        
        Args:
            table_name (str): Name of the table to inspect
        
        Returns:
            dict: Table information
        """
        try:
            client = self.get_client()
            # This would need to be implemented based on Supabase's schema inspection capabilities
            # For now, return basic info
            return {
                'table_name': table_name,
                'status': 'accessible'
            }
        except Exception as e:
            print(f"Error getting table info: {e}")
            return None

# Global instance for easy access
supabase_manager = SupabaseManager()

def get_supabase_client():
    """
    Get the global Supabase client instance.
    
    Returns:
        Client: Supabase client instance
    """
    return supabase_manager.get_client()

def initialize_supabase(url=None, key=None):
    """
    Initialize the global Supabase client.
    
    Args:
        url (str): Supabase project URL
        key (str): Supabase API key
    
    Returns:
        Client: Supabase client instance
    """
    return supabase_manager.initialize_client(url, key)

def test_supabase_connection():
    """
    Test the Supabase connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    return supabase_manager.test_connection()