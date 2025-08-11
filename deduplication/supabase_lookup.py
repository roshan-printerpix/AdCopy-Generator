"""
Supabase Lookup Module
Queries existing Supabase entries for potential matches.
"""

from supabase_storage.supabase_client import get_supabase_admin_client
import re
from collections import Counter

def fetch_existing_insights(limit=1000):
    """
    Fetch existing insights from Supabase for comparison.
    
    Args:
        limit (int): Maximum number of insights to fetch
    
    Returns:
        list: List of existing insights from database
    """
    try:
        client = get_supabase_admin_client()
        result = client.table('insights').select('*').limit(limit).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching existing insights: {e}")
        return []

def fetch_insights_by_keywords(keywords, limit=100):
    """
    Fetch insights containing specific keywords for targeted comparison.
    
    Args:
        keywords (list): List of keywords to search for
        limit (int): Maximum number of insights to fetch
    
    Returns:
        list: List of matching insights from database
    """
    if not keywords:
        return []
    
    try:
        client = get_supabase_admin_client()
        
        # Create search query using PostgreSQL full-text search
        search_terms = ' | '.join(keywords)  # OR search for any keyword
        
        result = client.table('insights').select('*').text_search(
            'insight', search_terms
        ).limit(limit).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching insights by keywords: {e}")
        # Fallback to simple text matching
        try:
            client = get_supabase_admin_client()
            all_insights = client.table('insights').select('*').limit(limit * 2).execute()
            
            if all_insights.data:
                # Filter insights that contain any of the keywords
                matching_insights = []
                for insight in all_insights.data:
                    insight_text = insight.get('insight', '').lower()
                    if any(keyword.lower() in insight_text for keyword in keywords):
                        matching_insights.append(insight)
                        if len(matching_insights) >= limit:
                            break
                return matching_insights
            return []
        except Exception as e2:
            print(f"Fallback keyword search also failed: {e2}")
            return []

def fetch_recent_insights(days=30, limit=500):
    """
    Fetch recently created insights for comparison.
    
    Args:
        days (int): Number of days back to fetch
        limit (int): Maximum number of insights to fetch
    
    Returns:
        list: List of recent insights from database
    """
    try:
        client = get_supabase_admin_client()
        
        # Since we removed created_at, just fetch the most recent insights by ID
        result = client.table('insights').select('*').order('id', desc=True).limit(limit).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching recent insights: {e}")
        return []

def extract_keywords_from_insight(insight):
    """
    Extract key terms from insight for targeted database queries.
    
    Args:
        insight (dict): Structured insight
    
    Returns:
        list: List of extracted keywords
    """
    keywords = []
    
    try:
        # Extract from insight text
        insight_text = insight.get('insight', '')
        if insight_text:
            # Remove common words and extract meaningful terms
            words = re.findall(r'\b[a-zA-Z]{3,}\b', insight_text.lower())
            
            # Filter out common stop words
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
            
            meaningful_words = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Get most common words
            word_counts = Counter(meaningful_words)
            keywords.extend([word for word, count in word_counts.most_common(5)])
        
        # Extract from limitations if available
        limitations = insight.get('limitations', '')
        if limitations:
            limitation_words = re.findall(r'\b[a-zA-Z]{4,}\b', limitations.lower())
            keywords.extend(limitation_words[:3])  # Add top 3 limitation keywords
        
        # Remove duplicates and return
        return list(set(keywords))
        
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return []

def get_relevant_insights_for_comparison(new_insight):
    """
    Get most relevant existing insights for comparison with new insight.
    
    Args:
        new_insight (dict): New insight to find matches for
    
    Returns:
        list: List of relevant existing insights
    """
    # Extract keywords from new insight
    keywords = extract_keywords_from_insight(new_insight)
    
    # Fetch targeted insights based on keywords
    if keywords:
        relevant_insights = fetch_insights_by_keywords(keywords)
    else:
        # Fallback to recent insights
        relevant_insights = fetch_recent_insights()
    
    return relevant_insights