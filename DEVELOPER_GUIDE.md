# Ad-Creative Insight Pipeline - Developer Guide

## 📋 Overview

**Status: ✅ FULLY IMPLEMENTED**

This developer guide provides a comprehensive overview of the completed Ad-Creative Insight Pipeline project structure, explaining the purpose of each file, module dependencies, and the data flow through the system. All core components are implemented and functional.

## 🏗️ Project Architecture

The pipeline follows a modular, step-by-step architecture with clean separation of concerns:

```
Raw Content → Cleaning → Structuring → Deduplication → Storage
```

Each step is isolated in its own module with clear interfaces, making the system maintainable and testable.

## 📁 Project Structure

```
ad-creative-insight-pipeline/
├── data_collection/          # Step 1: Data Collection
│   ├── reddit_scraper.py
│   ├── web_scraper.py
│   ├── api_scraper.py
│   └── pipeline_entry.py
├── cleaning/                 # Step 2: Text Cleaning
│   ├── cleaner.py
│   └── cleaning_controller.py
├── structuring/              # Step 3: LLM Structuring
│   ├── insight_formatter.py
│   ├── insight_schema.py
│   └── structuring_controller.py
├── deduplication/            # Step 4: Duplicate Detection
│   ├── similarity_checker.py
│   ├── supabase_lookup.py
│   └── deduplication_controller.py
├── supabase_storage/         # Step 5: Database Storage
│   ├── supabase_client.py
│   ├── insight_inserter.py
│   └── schema_reference.md
├── utils/                    # Shared Utilities
│   ├── __init__.py
│   ├── config.py
│   ├── helpers.py
│   └── logger.py
├── main.py                   # Pipeline Entry Point
├── requirements.txt          # Dependencies
├── .env.example             # Environment Variables Template
└── README.md                # Project Documentation
```

## 🔄 Data Flow & Module Hierarchy

### Pipeline Flow
1. **Data Collection** → Raw text content (list of strings)
2. **Cleaning** → Cleaned text content (list of strings)
3. **Structuring** → Structured insights (list of dicts)
4. **Deduplication** → Unique insights (filtered list of dicts)
5. **Storage** → Stored insights with UUIDs

### Module Dependencies
```
main.py
├── data_collection/pipeline_entry.py
│   ├── data_collection/reddit_scraper.py
│   ├── data_collection/web_scraper.py
│   └── data_collection/api_scraper.py
├── cleaning/cleaning_controller.py
│   └── cleaning/cleaner.py
├── structuring/structuring_controller.py
│   ├── structuring/insight_formatter.py
│   └── structuring/insight_schema.py
├── deduplication/deduplication_controller.py
│   ├── deduplication/similarity_checker.py
│   └── deduplication/supabase_lookup.py
├── supabase_storage/insight_inserter.py
│   └── supabase_storage/supabase_client.py
└── utils/ (used across all modules)
    ├── config.py
    ├── helpers.py
    └── logger.py
```

## 📄 File-by-File Breakdown

### 🎯 Entry Point

#### `main.py`
**Purpose**: Main pipeline orchestrator that ties together all 5 steps
**Key Functions**:
- `run_pipeline(sources_config)` - Executes complete pipeline
- `main()` - Entry point with example configuration
**Dependencies**: All module controllers
**Data Flow**: Orchestrates data through all pipeline steps

---

### 🔁 Step 1: Data Collection (`data_collection/`)

#### `pipeline_entry.py`
**Purpose**: Single entry point for all data collection activities
**Key Functions**:
- `collect_and_process_data(sources_config)` - Main collection orchestrator
**Dependencies**: All scraper modules
**Output**: List of raw text strings

#### `reddit_scraper.py`
**Purpose**: Scrape Reddit posts and comments for ad creative insights
**Key Functions**:
- `scrape_reddit_posts(subreddits, keywords, limit)` - Scrape posts from subreddits
- `scrape_reddit_comments(post_url, max_depth)` - Scrape comment threads
**Dependencies**: PRAW (Reddit API), utils/config
**Output**: Raw Reddit content

#### `web_scraper.py`
**Purpose**: Scrape blogs, websites, and Quora for content
**Key Functions**:
- `scrape_blog_posts(urls)` - Scrape blog content
- `scrape_website_content(url, selectors)` - Targeted website scraping
- `scrape_quora_answers(topic_urls)` - Quora answer extraction
**Dependencies**: BeautifulSoup, Selenium, requests
**Output**: Raw web content

#### `api_scraper.py`
**Purpose**: Pull content from social media APIs
**Key Functions**:
- `scrape_twitter_posts(hashtags, keywords, limit)` - Twitter/X API integration
- `scrape_meta_ads_library(search_terms, ad_type)` - Meta Ad Library
- `scrape_linkedin_posts(company_pages, keywords)` - LinkedIn content
**Dependencies**: Platform-specific API clients
**Output**: Raw social media content

---

### 🧹 Step 2: Cleaning (`cleaning/`)

#### `cleaning_controller.py`
**Purpose**: Main controller for text cleaning pipeline
**Key Functions**:
- `process_raw_content(raw_content_list)` - Process multiple raw texts
- `clean_single_text(raw_text)` - Clean individual text piece
**Dependencies**: cleaning/cleaner
**Input**: Raw text strings
**Output**: Cleaned text strings

#### `cleaner.py`
**Purpose**: Core text sanitization and normalization functions
**Key Functions**:
- `remove_html_tags(text)` - Strip HTML markup
- `remove_usernames_and_mentions(text)` - Remove @mentions and usernames
- `remove_urls(text)` - Strip URLs and links
- `remove_emojis_and_symbols(text)` - Clean emojis and special characters
- `truncate_to_paragraphs(text, max_paragraphs)` - Limit to 2-4 paragraphs
- `normalize_whitespace(text)` - Fix spacing and line breaks
**Dependencies**: re (regex), potentially NLTK
**Input**: Raw text
**Output**: Clean text

---

### 🧠 Step 3: Structuring (`structuring/`)

#### `structuring_controller.py`
**Purpose**: Main controller for converting clean text to structured insights
**Key Functions**:
- `process_cleaned_content(cleaned_content_list)` - Process multiple texts
- `structure_single_content(cleaned_text)` - Structure individual text
**Dependencies**: insight_formatter, insight_schema
**Input**: Cleaned text strings
**Output**: Validated structured insights (dicts)

#### `insight_formatter.py`
**Purpose**: LLM integration for text-to-structure conversion
**Key Functions**:
- `create_structuring_prompt(cleaned_text)` - Generate LLM prompt
- `call_llm_api(prompt)` - Make API call to LLM service
- `parse_llm_response(llm_response)` - Parse LLM JSON response
- `format_insight(cleaned_text)` - Complete formatting pipeline
**Dependencies**: OpenAI/Anthropic/Google APIs, utils/config
**Input**: Cleaned text
**Output**: Raw structured insight dict

#### `insight_schema.py`
**Purpose**: Define and validate insight data structure
**Key Functions**:
- `validate_insight_structure(insight_data)` - Validate required fields and types
- `sanitize_insight_data(insight_data)` - Clean and normalize data
**Schema**: insight, results (JSONB), limitations, difference_score (0-100), status
**Input**: Raw insight dict
**Output**: Validated insight dict
**Status**: ✅ Implemented with simplified schema

---

### 🚫 Step 4: Deduplication (`deduplication/`)

#### `deduplication_controller.py`
**Purpose**: Main controller for duplicate detection
**Key Functions**:
- `check_for_duplicates(new_insight)` - Check single insight for duplicates
- `batch_check_duplicates(new_insights)` - Process multiple insights
- `get_duplicate_statistics(new_insights)` - Generate duplicate stats
**Dependencies**: similarity_checker, supabase_lookup
**Input**: Structured insights
**Output**: Boolean (is_duplicate) or filtered unique insights

#### `similarity_checker.py`
**Purpose**: Calculate similarity between insights using various algorithms
**Key Functions**:
- `calculate_text_similarity(text1, text2)` - Text similarity scoring
- `calculate_insight_similarity(insight1, insight2)` - Overall insight similarity
- `is_duplicate_insight(new_insight, existing_insights, threshold)` - Duplicate detection
- `preprocess_for_comparison(insight)` - Normalize for comparison
**Dependencies**: sentence-transformers, scikit-learn, NLTK
**Algorithms**: Cosine similarity, semantic embeddings, fuzzy matching

#### `supabase_lookup.py`
**Purpose**: Query existing insights from database for comparison
**Key Functions**:
- `fetch_existing_insights(limit)` - Get all existing insights
- `fetch_insights_by_keywords(keywords, limit)` - Targeted keyword search
- `fetch_recent_insights(days, limit)` - Recent insights for comparison
- `get_relevant_insights_for_comparison(new_insight)` - Smart insight retrieval
**Dependencies**: supabase_storage/supabase_client
**Output**: List of existing insights for comparison

---

### 🗃️ Step 5: Storage (`supabase_storage/`)

#### `supabase_client.py`
**Purpose**: Manage Supabase database connection and client
**Key Classes**:
- `SupabaseManager` - Connection management class
**Key Functions**:
- `initialize_supabase(url, key)` - Initialize client with credentials
- `get_supabase_client()` - Get global client instance
- `test_supabase_connection()` - Test database connectivity
**Dependencies**: supabase-py, utils/config
**Output**: Supabase client instance

#### `insight_inserter.py`
**Purpose**: Handle UUID generation and database insertion
**Key Functions**:
- `generate_insight_id()` - Create UUID for new insights
- `prepare_insight_for_storage(structured_insight)` - Format for database
- `insert_single_insight(client, insight)` - Insert one insight
- `batch_insert_insights(client, insights)` - Batch insert multiple insights
**Dependencies**: uuid, datetime, supabase_client
**Database Fields**: id, insight, results, limitations_context, difference_score, status='greylist', created_at, updated_at

#### `schema_reference.md`
**Purpose**: Complete documentation of Supabase database schema
**Contents**:
- Table structure and field definitions
- Indexes and constraints
- Sample SQL for table creation
- Status values and their meanings
**Use Case**: Reference for database setup and maintenance

---

### 🧩 Utilities (`utils/`)

#### `config.py`
**Purpose**: Centralized configuration management
**Key Classes**:
- `Config` - Main configuration class with all settings
**Key Functions**:
- `validate_required_settings()` - Check for missing config
- `get_api_config(service)` - Get service-specific API config
**Environment Variables**: API keys, thresholds, pipeline settings
**Dependencies**: python-dotenv

#### `helpers.py`
**Purpose**: General utility functions used across modules
**Key Functions**:
- `generate_uuid()` - UUID generation
- `get_current_timestamp()` - Timestamp utilities
- `retry_on_failure(max_retries, delay, backoff)` - Retry decorator
- `chunk_list(lst, chunk_size)` - List chunking for batch processing
- `measure_execution_time(func)` - Performance measurement decorator
**Use Cases**: Common operations, error handling, performance monitoring

#### `logger.py`
**Purpose**: Logging configuration and utilities
**Key Functions**:
- `setup_logger(name, level, log_file)` - Configure logger with console and file output
- `log_pipeline_step(logger, step_name, start_time, end_time)` - Log pipeline execution
**Features**: Console and file logging, configurable levels, timing information

---

### 📋 Configuration Files

#### `requirements.txt`
**Purpose**: Python package dependencies
**Categories**:
- Core: supabase, python-dotenv
- Web scraping: requests, beautifulsoup4, selenium, scrapy
- APIs: praw, tweepy, facebook-sdk
- NLP: nltk, spacy, sentence-transformers
- LLM: openai, anthropic, google-generativeai
- Development: pytest, black, flake8

#### `.env.example`
**Purpose**: Template for environment variables
**Categories**:
- Database: Supabase URL and key
- APIs: Reddit, Twitter, Meta, LinkedIn credentials
- LLM: OpenAI, Anthropic, Google API keys
- Pipeline: Similarity thresholds, batch sizes, logging config

## 🔄 Development Workflow

### 1. Setup
```bash
# Clone and setup environment
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 2. Implementation Order
1. **Utils first** - config, helpers, logger
2. **Storage setup** - supabase_client, database schema
3. **Individual modules** - implement each step independently
4. **Integration** - connect modules through controllers
5. **Main pipeline** - orchestrate complete flow

### 3. Testing Strategy
- **Unit tests** for individual functions
- **Integration tests** for module interactions
- **End-to-end tests** for complete pipeline
- **Mock external APIs** during development

### 4. Data Validation
- **Input validation** at each step
- **Schema validation** for structured data
- **Error handling** with graceful degradation
- **Logging** for debugging and monitoring

## 🎯 Key Design Principles

1. **Modularity**: Each step is independent and testable
2. **Clean Interfaces**: Clear input/output contracts between modules
3. **Error Handling**: Graceful failure with detailed logging
4. **Configurability**: Environment-based configuration
5. **Scalability**: Batch processing and efficient algorithms
6. **Maintainability**: Clear documentation and consistent patterns

## 🚀 Getting Started

1. **Read this guide** to understand the architecture
2. **Set up your environment** with API keys and dependencies
3. **Start with utils** to establish common functionality
4. **Implement one module at a time** following the data flow
5. **Test each module** before moving to the next
6. **Integrate gradually** using the controller pattern
7. **Run the complete pipeline** with `python main.py`

This modular design ensures that you can develop, test, and maintain each component independently while maintaining a clean, scalable architecture for the entire pipeline.
##
 ✅ Implementation Status

### Completed Components

| Component | Status | Key Features |
|-----------|--------|--------------|
| **Data Collection** | ✅ Complete | Reddit scraping with PRAW, configurable subreddits and limits |
| **Text Cleaning** | ✅ Complete | HTML/noise removal, text normalization, paragraph limiting |
| **LLM Structuring** | ✅ Complete | OpenAI GPT-3.5-turbo integration, custom breakthrough messaging prompt |
| **Deduplication** | ✅ Complete | TF-IDF + cosine similarity, keyword-based DB lookup, configurable threshold |
| **Database Storage** | ✅ Complete | Supabase integration, simplified schema, batch operations |
| **Pipeline Orchestration** | ✅ Complete | End-to-end workflow, error handling, logging |
| **Configuration Management** | ✅ Complete | Environment-based config, API key management |
| **Database Setup** | ✅ Complete | Automated table creation, indexing, RLS policies |

### Key Implementation Details

#### LLM Structuring
- **Custom Prompt**: Focuses on breakthrough messaging that diverges from standard feature/quality ads
- **Difference Score**: Combines divergence from current messaging + potential to double CTR (0-100)
- **Structured Output**: JSON format with insight, results (JSONB), limitations, and score
- **Error Handling**: Graceful parsing of malformed LLM responses

#### Deduplication Algorithm
- **Text Preprocessing**: Lowercase, special character removal, whitespace normalization
- **Similarity Scoring**: TF-IDF vectorization with cosine similarity
- **Weighted Comparison**: Insight text (60%), results (25%), limitations (15%)
- **Database Optimization**: Keyword-based lookup to reduce comparison set

#### Database Schema (Simplified)
```sql
CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight TEXT NOT NULL,
    results JSONB NOT NULL,
    limitations_context TEXT NOT NULL,
    difference_score INTEGER NOT NULL CHECK (difference_score >= 0 AND difference_score <= 100),
    status VARCHAR(20) NOT NULL DEFAULT 'greylist'
);
```

### Quick Start Commands

```bash
# 1. Setup environment
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# 2. Setup database
python setup_database.py

# 3. Run pipeline
python main.py
```

### Configuration Examples

#### Reddit-focused Configuration (Current Default)
```python
sources_config = {
    'reddit': {
        'enabled': True,
        'subreddits': ['ppc'],
        'limit': 50,
        'time_filter': 'week',
        'sort': 'hot'
    },
    'web': {'enabled': False},
    'apis': {'enabled': False}
}
```

#### Multi-source Configuration (Future)
```python
sources_config = {
    'reddit': {
        'enabled': True,
        'subreddits': ['ppc', 'marketing', 'advertising'],
        'limit': 100
    },
    'web': {
        'enabled': True,
        'urls': ['https://blog.example.com/marketing']
    },
    'apis': {
        'enabled': True,
        'twitter': {'hashtags': ['#ppc', '#advertising'], 'limit': 50}
    }
}
```

### Monitoring and Debugging

#### Pipeline Execution Results
The pipeline returns detailed execution statistics:
```python
{
    'raw_content_count': 45,
    'cleaned_content_count': 38,
    'structured_insights_count': 32,
    'unique_insights_count': 28,
    'stored_insights_count': 28,
    'errors': []
}
```

#### Common Issues and Solutions

1. **OpenAI API Errors**
   - Check API key configuration
   - Monitor rate limits and quotas
   - Verify model availability

2. **Supabase Connection Issues**
   - Verify URL and service role key
   - Check RLS policies
   - Ensure table exists with correct schema

3. **Reddit API Limits**
   - Respect rate limits (1 request per second)
   - Use appropriate user agent
   - Handle authentication errors gracefully

4. **Similarity Threshold Tuning**
   - Default: 0.8 (80% similarity)
   - Lower values = more strict deduplication
   - Higher values = allow more similar insights

### Performance Considerations

- **Batch Processing**: Insights are processed and stored in batches for efficiency
- **Database Indexing**: Text search and status indexes for fast queries
- **Memory Usage**: Large content is processed in chunks to manage memory
- **API Rate Limits**: Built-in delays and retry logic for external APIs

### Future Enhancement Areas

1. **Additional Data Sources**: Twitter, Meta, LinkedIn API integration
2. **Advanced Similarity**: Semantic embeddings with sentence transformers
3. **Human Review Interface**: Web UI for insight approval/rejection
4. **Performance Optimization**: Caching, parallel processing
5. **Analytics Dashboard**: Insight performance tracking and metrics