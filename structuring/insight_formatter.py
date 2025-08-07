"""
Insight Formatter Module
Prepares LLM prompts and parses output into structured fields.
"""

def create_structuring_prompt(cleaned_text):
    """
    Create LLM prompt for converting cleaned text into structured insight.
    
    Args:
        cleaned_text (str): Clean text ready for structuring
    
    Returns:
        str: Formatted prompt for LLM
    """
    prompt_template = """
    Please analyze the following content and extract a structured insight for ad creative purposes.
    
    Content:
    {content}
    
    Please provide a JSON response with the following structure:
    {{
        "INSIGHT": "The core idea or tactic described",
        "RESULTS": "Any reported uplift, metrics, or performance data",
        "LIMITATIONS_CONTEXT": "Situational constraints or limitations mentioned",
        "DIFFERENCE_SCORE": "A number from 0-100 indicating how different this is from current practices"
    }}
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
    pass

def call_llm_api(prompt):
    """
    Make API call to LLM service.
    
    Args:
        prompt (str): Formatted prompt for LLM
    
    Returns:
        str: Raw LLM response
    """
    pass

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