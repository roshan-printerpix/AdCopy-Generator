#!/usr/bin/env python3
"""
Test script for LLM structuring functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from structuring.structuring_controller import process_cleaned_content, structure_single_content
from supabase_storage.supabase_client import test_supabase_connection, get_supabase_admin_client
from supabase_storage.insight_inserter import insert_single_insight
from utils.config import Config

def test_structuring_pipeline():
    """Test the complete structuring pipeline."""
    
    print("=== Testing LLM Structuring Pipeline ===\n")
    
    # Test data
    sample_cleaned_content = [
        """
        A/B testing revealed that using customer testimonials in video ads increased click-through rates by 34% compared to product-focused content. The testimonials featured real customers discussing specific problems the product solved. This approach worked particularly well for B2B software companies targeting decision-makers. However, the effectiveness was limited to audiences who had already shown interest in the product category, as cold audiences showed minimal improvement.
        """,
        """
        Dynamic product ads with personalized recommendations based on browsing history generated 2.3x higher conversion rates than static catalog ads. The key was showing products that complemented items already in the user's cart or recently viewed items. Implementation required robust tracking and real-time data integration. This strategy worked best for e-commerce brands with diverse product catalogs but showed limited success for single-product companies.
        """
    ]
    
    print("1. Testing single content structuring...")
    
    # Test single content structuring
    for i, content in enumerate(sample_cleaned_content, 1):
        print(f"\n--- Processing Content {i} ---")
        print(f"Input: {content[:100]}...")
        
        structured_insight = structure_single_content(content.strip())
        
        if structured_insight:
            print("✅ Successfully structured content")
            print(f"Insight: {structured_insight.get('insight', 'N/A')}")
            print(f"Results: {structured_insight.get('results', 'N/A')}")
            print(f"Limitations: {structured_insight.get('limitations', 'N/A')}")
            print(f"Difference Score: {structured_insight.get('difference_score', 'N/A')}")
            print(f"Status: {structured_insight.get('status', 'N/A')}")
        else:
            print("❌ Failed to structure content")
    
    print("\n2. Testing batch processing...")
    
    # Test batch processing
    structured_insights = process_cleaned_content(sample_cleaned_content)
    print(f"✅ Processed {len(structured_insights)} insights from {len(sample_cleaned_content)} inputs")
    
    print("\n3. Testing database connection...")
    
    # Test Supabase connection
    connection_ok = test_supabase_connection()
    if connection_ok:
        print("✅ Supabase connection successful")
        
        print("\n4. Testing database insertion...")
        
        # Test inserting one insight
        if structured_insights:
            try:
                client = get_supabase_admin_client()
                result = insert_single_insight(client, structured_insights[0])
                
                if result:
                    print(f"✅ Successfully inserted insight with ID: {result.get('id')}")
                else:
                    print("❌ Failed to insert insight")
                    
            except Exception as e:
                print(f"❌ Database insertion error: {e}")
        else:
            print("❌ No structured insights to insert")
    else:
        print("❌ Supabase connection failed - skipping database tests")
    
    print("\n=== Test Complete ===")

def test_config_validation():
    """Test configuration validation."""
    print("\n=== Testing Configuration ===")
    
    is_valid, missing = Config.validate_required_settings()
    if is_valid:
        print("✅ All required configuration settings are present")
    else:
        print(f"❌ Missing required settings: {missing}")
    
    # Check OpenAI API key
    if Config.OPENAI_API_KEY:
        print("✅ OpenAI API key is configured")
    else:
        print("❌ OpenAI API key is missing")

if __name__ == "__main__":
    test_config_validation()
    test_structuring_pipeline()