"""
Insight Inserter Module
Handles creation of UUIDs and insertion into Supabase.
"""

import uuid
from datetime import datetime, timezone

def generate_insight_id():
    """
    Generate a unique UUID for new insight.
    
    Returns:
        str: UUID string for new insight
    """
    return str(uuid.uuid4())

def prepare_insight_for_storage(structured_insight):
    """
    Prepare structured insight for database storage.
    
    Args:
        structured_insight (dict): Validated structured insight
    
    Returns:
        dict: Database-ready insight record
    """
    db_record = {
        'id': generate_insight_id(),
        'insight': structured_insight['INSIGHT'],
        'results': structured_insight['RESULTS'],
        'limitations_context': structured_insight['LIMITATIONS_CONTEXT'],
        'difference_score': structured_insight['DIFFERENCE_SCORE'],
        'status': 'greylist',
        'source_text': structured_insight.get('source_text'),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'processing_metadata': {
            'processing_timestamp': structured_insight.get('processing_timestamp'),
            'pipeline_version': '1.0'
        }
    }
    
    return db_record

def insert_single_insight(supabase_client, structured_insight):
    """
    Insert a single insight into Supabase.
    
    Args:
        supabase_client: Supabase client instance
        structured_insight (dict): Validated structured insight
    
    Returns:
        dict: Inserted record with ID, or None if failed
    """
    try:
        db_record = prepare_insight_for_storage(structured_insight)
        
        result = supabase_client.table('insights').insert(db_record).execute()
        
        if result.data:
            print(f"Successfully inserted insight with ID: {db_record['id']}")
            return result.data[0]
        else:
            print("Failed to insert insight - no data returned")
            return None
            
    except Exception as e:
        print(f"Error inserting insight: {e}")
        return None

def batch_insert_insights(supabase_client, structured_insights):
    """
    Insert multiple insights into Supabase in batch.
    
    Args:
        supabase_client: Supabase client instance
        structured_insights (list): List of validated structured insights
    
    Returns:
        tuple: (successful_inserts: list, failed_inserts: list)
    """
    successful_inserts = []
    failed_inserts = []
    
    # Prepare all records for batch insert
    db_records = []
    for insight in structured_insights:
        try:
            db_record = prepare_insight_for_storage(insight)
            db_records.append(db_record)
        except Exception as e:
            print(f"Error preparing insight for storage: {e}")
            failed_inserts.append(insight)
    
    # Batch insert
    if db_records:
        try:
            result = supabase_client.table('insights').insert(db_records).execute()
            
            if result.data:
                successful_inserts = result.data
                print(f"Successfully inserted {len(successful_inserts)} insights")
            else:
                print("Batch insert failed - no data returned")
                failed_inserts.extend(structured_insights)
                
        except Exception as e:
            print(f"Error during batch insert: {e}")
            failed_inserts.extend(structured_insights)
    
    return successful_inserts, failed_inserts