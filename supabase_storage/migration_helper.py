"""
Migration Helper
Utilities to help migrate from the old single-table schema to the new normalized schema.
"""

from supabase_storage.supabase_client import get_supabase_admin_client
from supabase_storage.schema_manager import initialize_reference_tables, get_all_products, get_all_regions

def migrate_old_insights_to_new_schema():
    """
    Migrate insights from old schema (with status column) to new normalized schema.
    This assumes you have a backup of the old insights table.
    
    Returns:
        dict: Migration results
    """
    try:
        client = get_supabase_admin_client()
        
        # First, ensure reference tables are initialized
        print("Initializing reference tables...")
        initialize_reference_tables()
        
        # Get available products and regions
        products = [p['name'] for p in get_all_products()]
        regions = [r['code'] for r in get_all_regions()]
        
        if not products or not regions:
            print("Error: No products or regions found. Please initialize reference tables first.")
            return {'success': False, 'error': 'Missing reference data'}
        
        print(f"Found {len(products)} products and {len(regions)} regions")
        
        # This is a placeholder for the actual migration logic
        # In practice, you would:
        # 1. Read from the old insights table (or backup)
        # 2. Insert into the new insights table (without status)
        # 3. Create status records for each insight/product/region combination
        
        print("Migration logic would go here...")
        print("Steps would be:")
        print("1. Read old insights with status")
        print("2. Insert into new insights table (without status)")
        print("3. Create status records for each product/region combination")
        
        return {
            'success': True,
            'migrated_insights': 0,
            'created_status_records': 0,
            'products_used': products,
            'regions_used': regions
        }
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return {'success': False, 'error': str(e)}

def validate_new_schema():
    """
    Validate that the new schema is properly set up.
    
    Returns:
        dict: Validation results
    """
    try:
        client = get_supabase_admin_client()
        
        validation_results = {
            'tables_exist': {},
            'reference_data': {},
            'relationships': {},
            'overall_valid': True
        }
        
        # Check if all tables exist and are accessible
        tables = ['insights', 'products', 'regions', 'status']
        for table in tables:
            try:
                result = client.table(table).select('*').limit(1).execute()
                validation_results['tables_exist'][table] = True
            except Exception as e:
                validation_results['tables_exist'][table] = False
                validation_results['overall_valid'] = False
                print(f"Table {table} not accessible: {e}")
        
        # Check reference data
        try:
            products = get_all_products()
            regions = get_all_regions()
            validation_results['reference_data']['products_count'] = len(products)
            validation_results['reference_data']['regions_count'] = len(regions)
            
            if len(products) == 0 or len(regions) == 0:
                validation_results['overall_valid'] = False
                print("Warning: Missing reference data in products or regions tables")
        except Exception as e:
            validation_results['reference_data']['error'] = str(e)
            validation_results['overall_valid'] = False
        
        # Check relationships (basic test)
        try:
            # Try to get insights with status (tests the relationship)
            result = client.table('insights').select('''
                id,
                status!left(
                    product_name,
                    region_code,
                    status
                )
            ''').limit(1).execute()
            validation_results['relationships']['insights_status_join'] = True
        except Exception as e:
            validation_results['relationships']['insights_status_join'] = False
            validation_results['overall_valid'] = False
            print(f"Relationship test failed: {e}")
        
        return validation_results
        
    except Exception as e:
        print(f"Error during validation: {e}")
        return {'overall_valid': False, 'error': str(e)}

def create_sample_data():
    """
    Create sample data for testing the new schema.
    
    Returns:
        dict: Results of sample data creation
    """
    try:
        client = get_supabase_admin_client()
        
        # Ensure reference tables are set up
        initialize_reference_tables()
        
        # Create a sample insight
        sample_insight = {
            'insight': 'Use bright colors and bold text to increase click-through rates',
            'results': {
                'metrics': {
                    'ctr_improvement': '15%',
                    'engagement_increase': '23%'
                },
                'context': 'Tested across social media platforms'
            },
            'limitations_context': 'Works best for younger demographics (18-35)',
            'difference_score': 75
        }
        
        # Insert the insight
        insight_result = client.table('insights').insert(sample_insight).execute()
        
        if insight_result.data:
            insight_id = insight_result.data[0]['id']
            print(f"Created sample insight with ID: {insight_id}")
            
            # Create status records for this insight
            products = ['Facebook Ads', 'Google Ads']
            regions = ['US', 'EU']
            
            status_records = []
            for product in products:
                for region in regions:
                    status_records.append({
                        'insight_id': insight_id,
                        'product_name': product,
                        'region_code': region,
                        'status': 'greylist'
                    })
            
            status_result = client.table('status').insert(status_records).execute()
            
            return {
                'success': True,
                'insight_id': insight_id,
                'status_records_created': len(status_result.data) if status_result.data else 0
            }
        else:
            return {'success': False, 'error': 'Failed to create sample insight'}
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    print("Migration Helper - Testing New Schema")
    
    print("\n1. Validating new schema...")
    validation = validate_new_schema()
    
    if validation['overall_valid']:
        print("✓ Schema validation passed")
        
        print("\n2. Creating sample data...")
        sample_result = create_sample_data()
        
        if sample_result['success']:
            print(f"✓ Sample data created successfully")
            print(f"   Insight ID: {sample_result['insight_id']}")
            print(f"   Status records: {sample_result['status_records_created']}")
        else:
            print(f"✗ Sample data creation failed: {sample_result.get('error')}")
    else:
        print("✗ Schema validation failed")
        print("Please ensure all tables are created and reference data is initialized")