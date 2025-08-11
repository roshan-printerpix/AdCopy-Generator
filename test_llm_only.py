#!/usr/bin/env python3
"""
Simple test script for LLM structuring functionality only.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from structuring.insight_formatter import format_insight, create_structuring_prompt, call_llm_api, parse_llm_response
from structuring.insight_schema import validate_insight_structure, sanitize_insight_data
from utils.config import Config

def test_llm_structuring():
    """Test just the LLM structuring without database operations."""
    
    print("=== Testing LLM Structuring Only ===\n")
    
    # Check configuration
    if not Config.OPENAI_API_KEY:
        print("❌ OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")
        return
    
    print("✅ OpenAI API key is configured")
    
    # Test data
    sample_text = """
    A/B testing revealed that using customer testimonials in video ads increased click-through rates by 34% compared to product-focused content. The testimonials featured real customers discussing specific problems the product solved. This approach worked particularly well for B2B software companies targeting decision-makers. However, the effectiveness was limited to audiences who had already shown interest in the product category, as cold audiences showed minimal improvement.
    """
    
    print(f"Input text: {sample_text.strip()[:100]}...\n")
    
    # Test prompt creation
    print("1. Creating LLM prompt...")
    prompt = create_structuring_prompt(sample_text.strip())
    print("✅ Prompt created successfully")
    print(f"Prompt length: {len(prompt)} characters\n")
    
    # Test LLM API call
    print("2. Calling OpenAI API...")
    try:
        llm_response = call_llm_api(prompt)
        if llm_response:
            print("✅ LLM API call successful")
            print(f"Response: {llm_response}\n")
        else:
            print("❌ LLM API call failed")
            return
    except Exception as e:
        print(f"❌ LLM API call error: {e}")
        return
    
    # Test response parsing
    print("3. Parsing LLM response...")
    try:
        parsed_data = parse_llm_response(llm_response)
        if parsed_data:
            print("✅ Response parsed successfully")
            print(f"Parsed data: {parsed_data}\n")
        else:
            print("❌ Failed to parse LLM response")
            return
    except Exception as e:
        print(f"❌ Response parsing error: {e}")
        return
    
    # Test data sanitization
    print("4. Sanitizing data...")
    try:
        sanitized_data = sanitize_insight_data(parsed_data)
        print("✅ Data sanitized successfully")
        print(f"Sanitized data: {sanitized_data}\n")
    except Exception as e:
        print(f"❌ Data sanitization error: {e}")
        return
    
    # Test validation
    print("5. Validating structure...")
    try:
        is_valid, errors = validate_insight_structure(sanitized_data)
        if is_valid:
            print("✅ Structure validation passed")
        else:
            print(f"❌ Structure validation failed: {errors}")
            return
    except Exception as e:
        print(f"❌ Structure validation error: {e}")
        return
    
    # Test complete pipeline
    print("6. Testing complete pipeline...")
    try:
        final_insight = format_insight(sample_text.strip())
        if final_insight:
            print("✅ Complete pipeline successful")
            print(f"Final insight: {final_insight}")
        else:
            print("❌ Complete pipeline failed")
    except Exception as e:
        print(f"❌ Complete pipeline error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_llm_structuring()