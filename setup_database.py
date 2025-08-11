#!/usr/bin/env python3
"""
Database setup script to create the insights table with the correct schema.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_storage.supabase_client import get_supabase_admin_client
from utils.config import Config

def create_insights_table():
    """Create the insights table with the simplified schema."""
    
    print("=== Setting up Insights Table ===\n")
    
    # Check configuration
    if not Config.SUPABASE_URL or not Config.SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Supabase configuration missing. Please check your .env file.")
        return False
    
    try:
        client = get_supabase_admin_client()
        
        # SQL to create the table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS insights (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            insight TEXT NOT NULL,
            results JSONB NOT NULL,
            limitations_context TEXT NOT NULL,
            difference_score INTEGER NOT NULL CHECK (difference_score >= 0 AND difference_score <= 100),
            status VARCHAR(20) NOT NULL DEFAULT 'greylist'
        );
        """
        
        # Create indexes
        create_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_insights_status ON insights(status);
        CREATE INDEX IF NOT EXISTS idx_insights_text_search ON insights USING GIN(to_tsvector('english', insight || ' ' || (results->>'metrics') || ' ' || (results->>'context')));
        CREATE INDEX IF NOT EXISTS idx_insights_results_gin ON insights USING GIN(results);
        """
        
        # Enable RLS and create policy
        rls_sql = """
        ALTER TABLE insights ENABLE ROW LEVEL SECURITY;
        
        DROP POLICY IF EXISTS "Service role can manage insights" ON insights;
        CREATE POLICY "Service role can manage insights" ON insights
            FOR ALL USING (auth.role() = 'service_role');
        """
        
        print("Creating insights table...")
        result = client.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ Table created successfully")
        
        print("Creating indexes...")
        result = client.rpc('exec_sql', {'sql': create_indexes_sql}).execute()
        print("✅ Indexes created successfully")
        
        print("Setting up Row Level Security...")
        result = client.rpc('exec_sql', {'sql': rls_sql}).execute()
        print("✅ RLS configured successfully")
        
        print("\n✅ Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\nYou may need to create the table manually using the SQL from schema_reference.md")
        return False

def test_table_access():
    """Test that we can access the insights table."""
    
    print("\n=== Testing Table Access ===\n")
    
    try:
        client = get_supabase_admin_client()
        
        # Try to select from the table
        result = client.table('insights').select('*').limit(1).execute()
        print(f"✅ Table access successful. Found {len(result.data)} records.")
        
        # Try to insert a test record
        test_record = {
            'insight': 'Test insight for database verification',
            'results': '{"metrics": "Test metrics", "context": "Test context"}',
            'limitations_context': 'Test limitations',
            'difference_score': 50,
            'status': 'greylist'
        }
        
        insert_result = client.table('insights').insert(test_record).execute()
        
        if insert_result.data:
            print("✅ Test insert successful")
            
            # Clean up test record
            test_id = insert_result.data[0]['id']
            client.table('insights').delete().eq('id', test_id).execute()
            print("✅ Test record cleaned up")
        else:
            print("❌ Test insert failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Table access test failed: {e}")
        return False

if __name__ == "__main__":
    print("Setting up database for Ad Creative Insights Pipeline...\n")
    
    success = create_insights_table()
    
    if success:
        test_table_access()
    else:
        print("\nPlease check your Supabase configuration and try again.")
        print("Required environment variables:")
        print("- SUPABASE_URL")
        print("- SUPABASE_SERVICE_ROLE_KEY")