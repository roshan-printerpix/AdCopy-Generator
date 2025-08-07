# Supabase Schema Reference

## Insights Table Structure

The `insights` table stores structured ad creative insights with the following schema:

### Table: `insights`

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier for each insight |
| `insight` | TEXT | NOT NULL | The core idea or tactic |
| `results` | TEXT | NOT NULL | Any reported uplift, metrics, or performance data |
| `limitations_context` | TEXT | NOT NULL | Situational constraints or limitations |
| `difference_score` | INTEGER | NOT NULL, CHECK (difference_score >= 0 AND difference_score <= 100) | Score indicating how different this is from current practices (0-100) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'greylist' | Current status of the insight |
| `source_text` | TEXT | | Original cleaned text that generated this insight |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Timestamp when insight was created |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Timestamp when insight was last updated |
| `processing_metadata` | JSONB | | Additional metadata about processing |

### Indexes

- Primary key index on `id`
- Index on `created_at` for time-based queries
- Index on `status` for filtering by status
- GIN index on `processing_metadata` for JSONB queries
- Text search index on `insight` and `results` for similarity searches

### Status Values

- `greylist` - Default status for newly created insights
- `approved` - Insights that have been reviewed and approved
- `rejected` - Insights that have been reviewed and rejected
- `archived` - Insights that are no longer active

### Sample SQL for Table Creation

```sql
CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight TEXT NOT NULL,
    results TEXT NOT NULL,
    limitations_context TEXT NOT NULL,
    difference_score INTEGER NOT NULL CHECK (difference_score >= 0 AND difference_score <= 100),
    status VARCHAR(20) NOT NULL DEFAULT 'greylist',
    source_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    processing_metadata JSONB
);

-- Create indexes
CREATE INDEX idx_insights_created_at ON insights(created_at);
CREATE INDEX idx_insights_status ON insights(status);
CREATE INDEX idx_insights_processing_metadata ON insights USING GIN(processing_metadata);
CREATE INDEX idx_insights_text_search ON insights USING GIN(to_tsvector('english', insight || ' ' || results));
```

### Notes

- All new insights are created with `status = 'greylist'`
- The `difference_score` must be between 0 and 100 inclusive
- `processing_metadata` can store additional information like source URLs, processing timestamps, etc.
- Text search capabilities are available for finding similar insights