# Supabase Schema Reference

## Normalized Database Schema

The database now uses a normalized structure with 4 tables to track insights and their testing status across products and regions.

### Table: `insights`

Core insight data storage.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each insight |
| `insight` | TEXT | NOT NULL | The core idea or tactic |
| `results` | JSONB | NOT NULL | Structured metrics and performance data |
| `limitations_context` | TEXT | NOT NULL | Situational constraints or limitations |
| `difference_score` | INTEGER | NOT NULL, CHECK (difference_score >= 0 AND difference_score <= 100) | Score indicating how different this is from current practices (0-100) |

### Table: `products`

Reference table for products.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each product |
| `name` | TEXT | NOT NULL, UNIQUE | Product name |

### Table: `regions`

Reference table for regions.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each region |
| `code` | TEXT | NOT NULL, UNIQUE | Region code (e.g., 'US', 'EU', 'APAC') |

### Table: `status`

Tracks testing status for each insight/product/region combination.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `insight_id` | UUID | FOREIGN KEY REFERENCES insights(id) | Reference to insight |
| `product_name` | TEXT | NOT NULL | Product name (denormalized for performance) |
| `region_code` | TEXT | NOT NULL | Region code (denormalized for performance) |
| `status` | status_enum | NOT NULL, DEFAULT 'greylist' | Current testing status |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last status update timestamp |

### Status Enum Values

- `greylist` - Default status for newly created insights
- `approved` - Insights that have been tested and approved
- `rejected` - Insights that have been tested and rejected
- `testing` - Insights currently being tested
- `archived` - Insights that are no longer active

### Sample SQL for Table Creation

```sql
-- Create status enum
CREATE TYPE status_enum AS ENUM ('greylist', 'approved', 'rejected', 'testing', 'archived');

-- Create insights table
CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight TEXT NOT NULL,
    results JSONB NOT NULL,
    limitations_context TEXT NOT NULL,
    difference_score INTEGER NOT NULL CHECK (difference_score >= 0 AND difference_score <= 100)
);

-- Create products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE
);

-- Create regions table
CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT NOT NULL UNIQUE
);

-- Create status table
CREATE TABLE status (
    insight_id UUID REFERENCES insights(id) ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    region_code TEXT NOT NULL,
    status status_enum NOT NULL DEFAULT 'greylist',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (insight_id, product_name, region_code)
);

-- Create indexes
CREATE INDEX idx_insights_text_search ON insights USING GIN(to_tsvector('english', insight || ' ' || (results->>'metrics') || ' ' || (results->>'context')));
CREATE INDEX idx_insights_results_gin ON insights USING GIN(results);
CREATE INDEX idx_status_status ON status(status);
CREATE INDEX idx_status_updated_at ON status(updated_at);
CREATE INDEX idx_status_product_region ON status(product_name, region_code);

-- Enable Row Level Security (RLS)
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE regions ENABLE ROW LEVEL SECURITY;
ALTER TABLE status ENABLE ROW LEVEL SECURITY;

-- Create policies to allow service role full access
CREATE POLICY "Service role can manage insights" ON insights FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage products" ON products FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage regions" ON regions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role can manage status" ON status FOR ALL USING (auth.role() = 'service_role');
```

### Workflow Logic

1. **Pipeline Stage**: New insights are inserted into the `insights` table only (greylist state)
2. **Testing Stage**: When insights are selected for testing, records are created in the `status` table
3. **Status Tracking**: Only insights being actively tested have entries in the `status` table

### Notes

- **Insights table**: Stores ALL insights (including greylist ones that haven't been tested yet)
- **Status table**: ONLY stores insights that are being actively tested (testing/approved/rejected)
- **Greylist insights**: Exist only in the insights table, no status table entry
- **Tested insights**: Have entries in both insights table (core data) and status table (testing results)
- Products and regions are normalized into reference tables
- The `status` table uses composite primary key (insight_id, product_name, region_code)
- Row Level Security (RLS) is enabled - use service role key for pipeline operations