"""
Ad-Creative Insight Pipeline - Main Entry Point
Orchestrates the complete pipeline from data collection to storage.
"""

from data_collection.pipeline_entry import collect_and_process_data
from cleaning.cleaning_controller import process_raw_content
from structuring.structuring_controller import process_cleaned_content
from deduplication.deduplication_controller import batch_check_duplicates
from supabase_storage.supabase_client import get_supabase_admin_client
from supabase_storage.insight_inserter import batch_insert_insights

def run_pipeline(sources_config):
    """
    Run the complete ad-creative insight pipeline.
    
    Args:
        sources_config (dict): Configuration for data sources
    
    Returns:
        dict: Pipeline execution results
    """
    print("Starting Ad-Creative Insight Pipeline...")
    
    results = {
        'raw_content_count': 0,
        'cleaned_content_count': 0,
        'structured_insights_count': 0,
        'unique_insights_count': 0,
        'stored_insights_count': 0,
        'errors': []
    }
    
    try:
        # Step 1: Data Collection
        print("Step 1: Collecting data from sources...")
        raw_content = collect_and_process_data(sources_config)
        results['raw_content_count'] = len(raw_content) if raw_content else 0
        print(f"Collected {results['raw_content_count']} pieces of raw content")
        
        if not raw_content:
            print("No raw content collected. Exiting pipeline.")
            return results
        
        # Step 2: Cleaning
        print("Step 2: Cleaning raw content...")
        cleaned_content = process_raw_content(raw_content)
        results['cleaned_content_count'] = len(cleaned_content)
        print(f"Cleaned content: {results['cleaned_content_count']} pieces")
        
        if not cleaned_content:
            print("No content survived cleaning. Exiting pipeline.")
            return results
        
        # Step 3: Structuring
        print("Step 3: Structuring cleaned content...")
        structured_insights = process_cleaned_content(cleaned_content)
        results['structured_insights_count'] = len(structured_insights)
        print(f"Structured insights: {results['structured_insights_count']} insights")
        
        if not structured_insights:
            print("No structured insights created. Exiting pipeline.")
            return results
        
        # Step 4: Deduplication
        print("Step 4: Checking for duplicates...")
        unique_insights = batch_check_duplicates(structured_insights)
        results['unique_insights_count'] = len(unique_insights)
        print(f"Unique insights: {results['unique_insights_count']} insights")
        
        if not unique_insights:
            print("No unique insights found. Exiting pipeline.")
            return results
        
        # Step 5: Storage
        print("Step 5: Storing insights in Supabase...")
        supabase_admin_client = get_supabase_admin_client()
        successful_inserts, failed_inserts = batch_insert_insights(supabase_admin_client, unique_insights)
        results['stored_insights_count'] = len(successful_inserts)
        
        if failed_inserts:
            results['errors'].append(f"Failed to store {len(failed_inserts)} insights")
        
        print(f"Successfully stored {results['stored_insights_count']} insights")
        
    except Exception as e:
        error_msg = f"Pipeline error: {str(e)}"
        results['errors'].append(error_msg)
        print(error_msg)
    
    print("Pipeline execution completed.")
    print(f"Results: {results}")
    
    return results

def main():
    """
    Main function with example configuration.
    """
    # Configuration focused on r/ppc
    sources_config = {
        'reddit': {
            'enabled': True,
            'subreddits': ['ppc'],  # Focus on r/ppc subreddit
            'limit': 50,
            'time_filter': 'week',
            'sort': 'hot'
        },
        'web': {
            'enabled': False,  # Disabled for now
            'urls': []
        },
        'apis': {
            'enabled': False,  # Disabled for now
            'twitter': {
                'hashtags': ['#ppc', '#advertising'],
                'limit': 20
            }
        }
    }
    
    # Run the pipeline
    results = run_pipeline(sources_config)
    
    return results

if __name__ == "__main__":
    main()