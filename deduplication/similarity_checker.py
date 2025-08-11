"""
Similarity Checker Module
Responsible for checking similarity between insights.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json

def calculate_text_similarity(text1, text2):
    """
    Calculate similarity score between two text strings.
    
    Args:
        text1 (str): First text to compare
        text2 (str): Second text to compare
    
    Returns:
        float: Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Preprocess texts
    text1_clean = preprocess_text(text1)
    text2_clean = preprocess_text(text2)
    
    if not text1_clean or not text2_clean:
        return 0.0
    
    # Use TF-IDF vectorization and cosine similarity
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    
    try:
        tfidf_matrix = vectorizer.fit_transform([text1_clean, text2_clean])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except Exception as e:
        print(f"Error calculating text similarity: {e}")
        return 0.0

def calculate_insight_similarity(insight1, insight2):
    """
    Calculate overall similarity between two structured insights.
    
    Args:
        insight1 (dict): First insight to compare
        insight2 (dict): Second insight to compare
    
    Returns:
        float: Similarity score between 0 and 1
    """
    try:
        # Extract text fields for comparison
        insight1_text = insight1.get('insight', '')
        insight2_text = insight2.get('insight', '')
        
        # Calculate similarity for main insight text (weighted heavily)
        insight_similarity = calculate_text_similarity(insight1_text, insight2_text)
        
        # Extract results text for comparison
        results1 = extract_results_text(insight1.get('results', ''))
        results2 = extract_results_text(insight2.get('results', ''))
        results_similarity = calculate_text_similarity(results1, results2)
        
        # Calculate limitations similarity
        limitations1 = insight1.get('limitations', '')
        limitations2 = insight2.get('limitations', '')
        limitations_similarity = calculate_text_similarity(limitations1, limitations2)
        
        # Weighted average (insight text is most important)
        overall_similarity = (
            insight_similarity * 0.6 +
            results_similarity * 0.25 +
            limitations_similarity * 0.15
        )
        
        return overall_similarity
        
    except Exception as e:
        print(f"Error calculating insight similarity: {e}")
        return 0.0

def is_duplicate_insight(new_insight, existing_insights, threshold=0.8):
    """
    Check if new insight is duplicate of any existing insights.
    
    Args:
        new_insight (dict): New insight to check
        existing_insights (list): List of existing insights
        threshold (float): Similarity threshold for duplicate detection
    
    Returns:
        tuple: (is_duplicate: bool, most_similar_insight: dict or None)
    """
    if not existing_insights:
        return False, None
    
    max_similarity = 0
    most_similar = None
    
    for existing_insight in existing_insights:
        similarity = calculate_insight_similarity(new_insight, existing_insight)
        
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar = existing_insight
    
    is_duplicate = max_similarity >= threshold
    
    return is_duplicate, most_similar if is_duplicate else None

def preprocess_text(text):
    """
    Clean and preprocess text for similarity comparison.
    
    Args:
        text (str): Raw text to preprocess
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Remove extra spaces again
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_results_text(results):
    """
    Extract text from results field (which might be JSON).
    
    Args:
        results (str or dict): Results data
    
    Returns:
        str: Extracted text from results
    """
    if not results:
        return ""
    
    try:
        # If it's a JSON string, parse it
        if isinstance(results, str):
            try:
                results_dict = json.loads(results)
                # Extract text from all values
                text_parts = []
                for value in results_dict.values():
                    if isinstance(value, str):
                        text_parts.append(value)
                return " ".join(text_parts)
            except json.JSONDecodeError:
                # If not JSON, return as is
                return str(results)
        elif isinstance(results, dict):
            # Extract text from all values
            text_parts = []
            for value in results.values():
                if isinstance(value, str):
                    text_parts.append(value)
            return " ".join(text_parts)
        else:
            return str(results)
    except Exception as e:
        print(f"Error extracting results text: {e}")
        return str(results) if results else ""

def preprocess_for_comparison(insight):
    """
    Preprocess insight data for more accurate similarity comparison.
    
    Args:
        insight (dict): Insight to preprocess
    
    Returns:
        dict: Preprocessed insight data
    """
    preprocessed = {}
    
    # Preprocess text fields
    preprocessed['insight'] = preprocess_text(insight.get('insight', ''))
    preprocessed['limitations'] = preprocess_text(insight.get('limitations', ''))
    
    # Extract and preprocess results text
    results_text = extract_results_text(insight.get('results', ''))
    preprocessed['results_text'] = preprocess_text(results_text)
    
    # Keep other fields as is
    preprocessed['difference_score'] = insight.get('difference_score', 0)
    preprocessed['status'] = insight.get('status', 'greylist')
    
    return preprocessed