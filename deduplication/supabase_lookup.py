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
    Note: With the new schema, insights don't have status directly - 
    status is tracked separately in the status table.
    
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

def fetch_insights_with_status(status_filter=None, product_name=None, region_code=None, limit=500):
    """
    Fetch insights with their status information from the normalized schema.
    
    Args:
        status_filter (str): Filter by status (e.g., 'greylist', 'approved')
        product_name (str): Filter by product name
        region_code (str): Filter by region code
        limit (int): Maximum number of insights to fetch
    
    Returns:
        list: List of insights with status information
    """
    try:
        client = get_supabase_admin_client()
        
        # Build query to join insights with status
        query = client.table('insights').select('''
            *,
            status!inner(
                product_name,
                region_code,
                status,
                updated_at
            )
        ''')
        
        # Apply filters if provided
        if status_filter:
            query = query.eq('status.status', status_filter)
        if product_name:
            query = query.eq('status.product_name', product_name)
        if region_code:
            query = query.eq('status.region_code', region_code)
        
        result = query.limit(limit).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching insights with status: {e}")
        return []

def get_insight_status_summary(insight_id):
    """
    Get a summary of status across all products and regions for a specific insight.
    
    Args:
        insight_id (str): UUID of the insight
    
    Returns:
        dict: Status summary with counts by status type
    """
    try:
        client = get_supabase_admin_client()
        
        result = client.table('status').select('*').eq('insight_id', insight_id).execute()
        
        if result.data:
            status_counts = {}
            for record in result.data:
                status = record['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_combinations': len(result.data),
                'status_breakdown': status_counts,
                'records': result.data
            }
        else:
            return {'total_combinations': 0, 'status_breakdown': {}, 'records': []}
            
    except Exception as e:
        print(f"Error getting insight status summary: {e}")
        return {'total_combinations': 0, 'status_breakdown': {}, 'records': []}

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