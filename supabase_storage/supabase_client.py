"""
Supabase Client Module
Initializes and manages Supabase connection and helpers.
"""

import os
from supabase import create_client, Client
from utils.config import Config

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
            url (str): Supabase project URL (optional, uses config if not provided)
            key (str): Supabase API key (optional, uses config if not provided)
        
        Returns:
            Client: Supabase client instance
        """
        self.url = url or Config.SUPABASE_URL
        self.key = key or Config.SUPABASE_KEY
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and key must be provided either as parameters or in configuration")
        
        print(f"Connecting to Supabase at: {self.url}")
        self.client = create_client(self.url, self.key)
        print("Supabase client initialized successfully")
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
        Test the Supabase connection with the new normalized schema.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            client = self.get_client()
            print("Testing Supabase connection...")
            
            # Test connection to all tables in the new schema
            tables_to_test = ['insights', 'products', 'regions', 'status']
            
            for table in tables_to_test:
                try:
                    result = client.table(table).select('*').limit(1).execute()
                    print(f"✓ {table} table accessible ({len(result.data)} records found)")
                except Exception as table_error:
                    print(f"✗ {table} table not accessible: {table_error}")
                    return False
            
            print("All tables accessible - connection test successful!")
            return True
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            print("This might be because the tables don't exist yet or credentials are incorrect.")
            
            # Try a more basic connection test
            try:
                # Test with a simple RPC call or auth check
                client.auth.get_session()
                print("Basic Supabase connection is working")
                return True
            except Exception as e2:
                print(f"Basic connection also failed: {e2}")
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
    Get the global Supabase client instance (anon key).
    
    Returns:
        Client: Supabase client instance
    """
    return supabase_manager.get_client()

def get_supabase_admin_client():
    """
    Get Supabase client with service role key for admin operations (bypasses RLS).
    
    Returns:
        Client: Supabase admin client instance
    """
    if not Config.SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("Service role key not configured - cannot create admin client")
    
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)

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