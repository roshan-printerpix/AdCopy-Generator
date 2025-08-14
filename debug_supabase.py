#!/usr/bin/env python3
"""
Debug script to test Supabase connection
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Supabase connection...")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_SERVICE_ROLE_KEY: {'***' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'Not set'}")

try:
    from supabase import create_client
    print("✓ Supabase import successful")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if url and key:
        print("Creating client...")
        client = create_client(url, key)
        print("✓ Client created successfully")
        
        # Test a simple query
        print("Testing query...")
        result = client.table('insights').select('id').limit(1).execute()
        print(f"✓ Query successful, found {len(result.data)} records")
        
    else:
        print("✗ Missing URL or key")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()