"""
Deduplication Controller
Takes structured insight and returns boolean indicating if it's a duplicate.
"""

from . import similarity_checker, supabase_lookup

def check_for_duplicates(new_insight):
    """
    Main function to check if new insight is a duplicate.
    
    Args:
        new_insight (dict): New structured insight to check
    
    Returns:
        bool: True if insight is duplicate, False if unique
    """
    try:
        # Get relevant existing insights for comparison
        existing_insights = supabase_lookup.get_relevant_insights_for_comparison(new_insight)
        
        if not existing_insights:
            return False  # No existing insights to compare against
        
        # Check for duplicates
        is_duplicate, similar_insight = similarity_checker.is_duplicate_insight(
            new_insight, 
            existing_insights
        )
        
        if is_duplicate:
            print(f"Duplicate insight detected. Similar to insight ID: {similar_insight.get('id', 'unknown')}")
        
        return is_duplicate
        
    except Exception as e:
        print(f"Error during deduplication check: {e}")
        # In case of error, assume not duplicate to avoid losing potentially unique insights
        return False

def batch_check_duplicates(new_insights):
    """
    Check multiple insights for duplicates in batch.
    
    Args:
        new_insights (list): List of new structured insights
    
    Returns:
        list: List of unique insights (duplicates removed)
    """
    unique_insights = []
    
    for insight in new_insights:
        if not check_for_duplicates(insight):
            unique_insights.append(insight)
        else:
            print(f"Skipping duplicate insight: {insight.get('INSIGHT', 'Unknown')[:50]}...")
    
    return unique_insights

def get_duplicate_statistics(new_insights):
    """
    Get statistics about duplicates in a batch of insights.
    
    Args:
        new_insights (list): List of new structured insights
    
    Returns:
        dict: Statistics about duplicates found
    """
    total_insights = len(new_insights)
    duplicates_found = 0
    
    for insight in new_insights:
        if check_for_duplicates(insight):
            duplicates_found += 1
    
    return {
        'total_insights': total_insights,
        'duplicates_found': duplicates_found,
        'unique_insights': total_insights - duplicates_found,
        'duplicate_rate': duplicates_found / total_insights if total_insights > 0 else 0
    }