"""
Insight Formatter Module
Prepares LLM prompts and parses output into structured fields.
"""

import json
import openai
from utils.config import Config

def create_structuring_prompt(cleaned_text):
    """
    Create LLM prompt for converting cleaned text into structured insight.
    
    Args:
        cleaned_text (str): Clean text ready for structuring
    
    Returns:
        str: Formatted prompt for LLM
    """
    prompt_template = """
    Analyze the following marketing content and create a new ad copy insight that breaks from current messaging, which focuses on product features, quality, and generic uses (e.g., "USA's #1 Store," "100+ Unique Designs," "Perfect Custom Gifts").

    Content to analyze:
    {content}

    Your task is to develop a completely different approach—an insight that could fundamentally change ad performance and potentially double click-through rate (CTR), not just improve it slightly.

    After generating the new insight, provide a Difference Score. This single score, from 0-100, combines how much the new idea diverges from current messaging with its potential to be a true game-changer and double CTR. (0 = minor tweak with no real impact, 100 = radical departure with a high probability of doubling CTR).

    Please provide a JSON response with the following structure:
    {{
        "insight": "The core breakthrough idea or tactic that breaks from standard messaging",
        "results": {{"metrics": "Any reported performance data, uplift percentages, or success metrics", "context": "Additional context about the results and testing conditions"}},
        "limitations": "Situational constraints, audience specifics, or conditions where this approach might not work",
        "difference_score": 75
    }}

    Guidelines:
    - insight: Focus on breakthrough messaging approaches that diverge from feature/quality-focused ads
    - results: Extract any performance metrics, conversion improvements, or testing data mentioned
    - limitations: Note audience constraints, market conditions, or situational factors
    - difference_score: Rate 0-100 based on how radically different this is from standard messaging AND its potential to double CTR

    Return only valid JSON, no additional text.
    """
    
    return prompt_template.format(content=cleaned_text)

def parse_llm_response(llm_response):
    """
    Parse LLM response into structured insight fields.
    
    Args:
        llm_response (str): Raw response from LLM
    
    Returns:
        dict: Structured insight data
    """
    try:
        # Clean the response - remove any markdown formatting or extra text
        cleaned_response = llm_response.strip()
        
        # Find JSON content if wrapped in markdown
        if "```json" in cleaned_response:
            start = cleaned_response.find("```json") + 7
            end = cleaned_response.find("```", start)
            cleaned_response = cleaned_response[start:end].strip()
        elif "```" in cleaned_response:
            start = cleaned_response.find("```") + 3
            end = cleaned_response.find("```", start)
            cleaned_response = cleaned_response[start:end].strip()
        
        # Parse JSON
        parsed_data = json.loads(cleaned_response)
        
        # Ensure results is properly formatted as JSON string for database
        if isinstance(parsed_data.get('results'), dict):
            parsed_data['results'] = json.dumps(parsed_data['results'])
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Raw response: {llm_response}")
        return None
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return None

def call_llm_api(prompt):
    """
    Make API call to LLM service.
    
    Args:
        prompt (str): Formatted prompt for LLM
    
    Returns:
        str: Raw LLM response
    """
    try:
        # Initialize OpenAI client
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing marketing content and extracting structured insights for ad creative purposes. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def format_insight(cleaned_text):
    """
    Complete pipeline to format cleaned text into structured insight.
    
    Args:
        cleaned_text (str): Clean text ready for structuring
    
    Returns:
        dict: Structured insight ready for validation
    """
    prompt = create_structuring_prompt(cleaned_text)
    llm_response = call_llm_api(prompt)
    structured_insight = parse_llm_response(llm_response)
    
    return structured_insight