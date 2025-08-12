"""
Schema Manager Module
Utilities for managing the normalized database schema.
"""

from supabase_storage.supabase_client import get_supabase_admin_client
from datetime import datetime, timezone

def initialize_reference_tables():
    """
    Initialize the products and regions reference tables with common values.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_supabase_admin_client()
        
        # Common products
        products = [
            {'name': 'Facebook Ads'},
            {'name': 'Google Ads'},
            {'name': 'TikTok Ads'},
            {'name': 'LinkedIn Ads'},
            {'name': 'Twitter Ads'},
            {'name': 'Snapchat Ads'},
            {'name': 'Pinterest Ads'},
            {'name': 'YouTube Ads'}
        ]
        
        # Common regions
        regions = [
            {'code': 'US'},
            {'code': 'EU'},
            {'code': 'APAC'},
            {'code': 'LATAM'},
            {'code': 'MENA'},
            {'code': 'CA'},
            {'code': 'UK'},
            {'code': 'AU'}
        ]
        
        # Insert products (ignore duplicates)
        try:
            result = client.table('products').upsert(products, on_conflict='name').execute()
            print(f"Initialized {len(result.data)} products")
        except Exception as e:
            print(f"Error initializing products: {e}")
        
        # Insert regions (ignore duplicates)
        try:
            result = client.table('regions').upsert(regions, on_conflict='code').execute()
            print(f"Initialized {len(result.data)} regions")
        except Exception as e:
            print(f"Error initializing regions: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error initializing reference tables: {e}")
        return False

def get_all_products():
    """
    Get all products from the products table.
    
    Returns:
        list: List of product records
    """
    try:
        client = get_supabase_admin_client()
        result = client.table('products').select('*').execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

def get_all_regions():
    """
    Get all regions from the regions table.
    
    Returns:
        list: List of region records
    """
    try:
        client = get_supabase_admin_client()
        result = client.table('regions').select('*').execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching regions: {e}")
        return []

def add_product(product_name):
    """
    Add a new product to the products table.
    
    Args:
        product_name (str): Name of the product
    
    Returns:
        dict: Inserted product record or None if failed
    """
    try:
        client = get_supabase_admin_client()
        result = client.table('products').insert({'name': product_name}).execute()
        
        if result.data:
            print(f"Added product: {product_name}")
            return result.data[0]
        else:
            print(f"Failed to add product: {product_name}")
            return None
            
    except Exception as e:
        print(f"Error adding product {product_name}: {e}")
        return None

def add_region(region_code):
    """
    Add a new region to the regions table.
    
    Args:
        region_code (str): Code of the region
    
    Returns:
        dict: Inserted region record or None if failed
    """
    try:
        client = get_supabase_admin_client()
        result = client.table('regions').insert({'code': region_code}).execute()
        
        if result.data:
            print(f"Added region: {region_code}")
            return result.data[0]
        else:
            print(f"Failed to add region: {region_code}")
            return None
            
    except Exception as e:
        print(f"Error adding region {region_code}: {e}")
        return None

def get_status_overview():
    """
    Get an overview of all status records grouped by status type.
    
    Returns:
        dict: Status overview with counts
    """
    try:
        client = get_supabase_admin_client()
        result = client.table('status').select('*').execute()
        
        if result.data:
            overview = {}
            for record in result.data:
                status = record['status']
                if status not in overview:
                    overview[status] = {
                        'count': 0,
                        'products': set(),
                        'regions': set()
                    }
                
                overview[status]['count'] += 1
                overview[status]['products'].add(record['product_name'])
                overview[status]['regions'].add(record['region_code'])
            
            # Convert sets to lists for JSON serialization
            for status in overview:
                overview[status]['products'] = list(overview[status]['products'])
                overview[status]['regions'] = list(overview[status]['regions'])
            
            return overview
        else:
            return {}
            
    except Exception as e:
        print(f"Error getting status overview: {e}")
        return {}

def bulk_update_status(insight_ids, new_status, product_name=None, region_code=None):
    """
    Bulk update status for multiple insights.
    
    Args:
        insight_ids (list): List of insight UUIDs
        new_status (str): New status to set
        product_name (str): Specific product to update (optional)
        region_code (str): Specific region to update (optional)
    
    Returns:
        int: Number of records updated
    """
    try:
        client = get_supabase_admin_client()
        
        # Build the update query
        query = client.table('status').update({
            'status': new_status,
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        
        # Apply filters
        query = query.in_('insight_id', insight_ids)
        
        if product_name:
            query = query.eq('product_name', product_name)
        if region_code:
            query = query.eq('region_code', region_code)
        
        result = query.execute()
        
        if result.data:
            count = len(result.data)
            print(f"Updated {count} status records to '{new_status}'")
            return count
        else:
            print("No records were updated")
            return 0
            
    except Exception as e:
        print(f"Error bulk updating status: {e}")
        return 0

def cleanup_orphaned_status_records():
    """
    Remove status records that reference non-existent insights.
    
    Returns:
        int: Number of orphaned records removed
    """
    try:
        client = get_supabase_admin_client()
        
        # This would require a more complex query in production
        # For now, just return 0 as a placeholder
        print("Orphaned record cleanup not implemented yet")
        return 0
        
    except Exception as e:
        print(f"Error cleaning up orphaned records: {e}")
        return 0

def get_schema_stats():
    """
    Get statistics about the current database schema.
    
    Returns:
        dict: Schema statistics
    """
    try:
        client = get_supabase_admin_client()
        
        stats = {}
        
        # Count insights
        insights_result = client.table('insights').select('id', count='exact').execute()
        stats['insights_count'] = insights_result.count if insights_result.count else 0
        
        # Count products
        products_result = client.table('products').select('id', count='exact').execute()
        stats['products_count'] = products_result.count if products_result.count else 0
        
        # Count regions
        regions_result = client.table('regions').select('id', count='exact').execute()
        stats['regions_count'] = regions_result.count if regions_result.count else 0
        
        # Count status records
        status_result = client.table('status').select('insight_id', count='exact').execute()
        stats['status_records_count'] = status_result.count if status_result.count else 0
        
        # Calculate expected vs actual status records
        expected_status_records = stats['insights_count'] * stats['products_count'] * stats['regions_count']
        stats['expected_status_records'] = expected_status_records
        stats['status_coverage_percentage'] = (
            (stats['status_records_count'] / expected_status_records * 100) 
            if expected_status_records > 0 else 0
        )
        
        return stats
        
    except Exception as e:
        print(f"Error getting schema stats: {e}")
        return {}

if __name__ == "__main__":
    # Quick test of the schema manager
    print("Testing Schema Manager...")
    
    # Initialize reference tables
    print("\n1. Initializing reference tables...")
    initialize_reference_tables()
    
    # Get stats
    print("\n2. Getting schema statistics...")
    stats = get_schema_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Get status overview
    print("\n3. Getting status overview...")
    overview = get_status_overview()
    for status, data in overview.items():
        print(f"   {status}: {data['count']} records")