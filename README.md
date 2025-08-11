# Ad‑Creative Insight Pipeline

> **Status: ✅ FULLY IMPLEMENTED** – Complete data‑driven LLM pipeline that scrapes content, cleans and structures it into breakthrough ad creative insights, removes duplicates, and stores unique insights in Supabase.

---

## 1. Executive Summary

| Function              | What it Does                                                    | Tech Choice                                | Status |
|-----------------------|------------------------------------------------------------------|---------------------------------------------|---------|
| **Data Collection**   | Pull raw text from Reddit r/ppc and other sources              | PRAW + Scrapy + API wrappers               | ✅ Complete |
| **Cleaning**          | Strip noise, extract clean text from raw content                | Custom regex + text processing             | ✅ Complete |
| **Structuring**       | Convert cleaned content into breakthrough ad insights           | OpenAI GPT-3.5-turbo (custom prompt)       | ✅ Complete |
| **Deduplication**     | Compare with Supabase DB using similarity scoring              | TF-IDF + Cosine similarity + DB lookup     | ✅ Complete |
| **Storage**           | Persist only unique structured insights with greylist status    | Supabase (simplified schema)               | ✅ Complete |

---

## 2. Pipeline Flow

| Step                   | Output                               | Description                                                        |
|------------------------|---------------------------------------|--------------------------------------------------------------------|
| **1. Data Collection** | Raw scraped content                  | Scrapes Reddit r/ppc for marketing insights. **Not stored**        |
| **2. Cleaning**        | Clean plain text                     | Removes HTML, URLs, usernames, emojis. Limits to 2-4 paragraphs   |
| **3. Structuring**     | Breakthrough ad insights             | Uses custom LLM prompt to extract insights that break from standard messaging |
| **4. Deduplication**   | Unique insights only                 | TF-IDF similarity scoring against existing Supabase records        |
| **5. Storage**         | Supabase entry (greylisted)          | Stores unique insights with `status = greylist`                    |

---

## 3. Detailed Component Design

### 3.1 Data Collection

| Source                  | Tool           | Notes                                 |
|-------------------------|----------------|---------------------------------------|
| **Websites / Blogs**    | Scrapy         | Use middlewares for rotation & delay |
| **Reddit / Quora / Twitter** | `praw`, `quill`, `tweepy` | Rate-limit adherence |
| **Social Pages** (Meta, LinkedIn) | Graph API      | No storage; feeds directly into cleaning |

> **Note:** Scraped content is not persisted. It is immediately sent to the cleaning module.

---

### 3.2 Cleaning & Structuring

| Sub-step         | Action                                      | Output                                |
|------------------|---------------------------------------------|----------------------------------------|
| **Cleaning**     | Remove HTML, usernames, URLs, emojis        | Clean 2–4 paragraph text               |
| **Structuring**  | Custom LLM prompt focused on breakthrough messaging that diverges from standard feature/quality ads | - INSIGHT (breakthrough tactic)      |
|                  | Calculates difference score based on divergence from current messaging + potential to double CTR | - RESULTS (structured JSON)          |
|                  |                                             | - LIMITATIONS (constraints/context)   |
|                  |                                             | - DIFFERENCE SCORE (0–100)            |

> **Custom Prompt Focus**: Creates insights that break from current messaging which focuses on product features, quality, and generic uses. Identifies approaches that could fundamentally change ad performance and potentially double CTR.

> Example INSIGHT:  
> **INSIGHT:** "Use emotional transformation stories showing customer before/after scenarios without mentioning product features"  
> **RESULTS:** {"metrics": "45% engagement rate increase", "context": "Tested on lifestyle brands"}  
> **LIMITATIONS:** "Requires authentic customer stories, doesn't work for purely functional products"  
> **DIFFERENCE SCORE:** 78

---

### 3.3 Deduplication

| Action                     | Tool / Method            | Result                              |
|----------------------------|--------------------------|-------------------------------------|
| Extract keywords from new insight | Custom keyword extraction | Target relevant existing insights |
| Fetch similar insights from DB | Supabase text search + keyword matching | Get comparison candidates |
| Calculate similarity scores | TF-IDF + Cosine similarity | Weighted scoring (insight 60%, results 25%, limitations 15%) |
| Apply threshold filter | Configurable threshold (default 0.8) | Filter out duplicates above threshold |

> **Similarity Algorithm**: Uses TF-IDF vectorization with cosine similarity for text comparison. Preprocesses text by removing special characters and normalizing whitespace. Only **unique insights** below the similarity threshold proceed to storage.

---

### 3.4 Storage (Supabase)

| Field                 | Type       | Notes                                       |
|-----------------------|------------|---------------------------------------------|
| `id`                  | UUID       | Primary key (auto-generated)               |
| `insight`             | TEXT       | Breakthrough ad creative tactic             |
| `results`             | JSONB      | Structured performance data and context     |
| `limitations_context` | TEXT       | Constraints and situational factors         |
| `difference_score`    | INTEGER    | 0–100 score (divergence + CTR potential)   |
| `status`              | VARCHAR(20)| `greylist` (default), `approved`, `rejected`, `archived` |

> **Simplified Schema**: Removed `source_url`, `source_hash`, `created_at`, and `updated_at` fields for streamlined storage. The `results` field uses JSONB for structured metrics and context data.

---

## 4. What’s Not Yet Implemented (Future Phases)

- Insight review and human scoring  
- Headline + description generation using LLMs  
- A/B testing in ad platforms  
- Feedback loop with performance logging  

These will come after the initial insight pipeline is deployed.

---## 4. Q
uick Start

### 4.1 Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY=your_openai_key
# - SUPABASE_URL=your_supabase_url  
# - SUPABASE_SERVICE_ROLE_KEY=your_service_key
# - REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, etc.
```

3. **Setup Database**
```bash
python setup_database.py
```

### 4.2 Run Pipeline

```bash
python main.py
```

The pipeline will:
1. Scrape Reddit r/ppc for marketing insights
2. Clean and structure the content using LLM
3. Check for duplicates against existing insights
4. Store unique insights in Supabase with `status = 'greylist'`

### 4.3 Configuration

Edit the `sources_config` in `main.py` to customize:
- **Reddit**: Subreddits, post limits, time filters
- **Web Scraping**: URLs and selectors (currently disabled)
- **APIs**: Twitter, Meta, LinkedIn integration (currently disabled)

## 5. Architecture & Implementation Status

### ✅ Completed Components
- **Data Collection**: Reddit scraping with PRAW
- **Text Cleaning**: HTML/noise removal, text normalization
- **LLM Structuring**: OpenAI integration with custom breakthrough messaging prompt
- **Deduplication**: TF-IDF similarity scoring with database lookup
- **Database Storage**: Supabase integration with simplified schema
- **Pipeline Orchestration**: Complete end-to-end workflow

### 🔄 Future Enhancements
- Insight review and human scoring interface
- Headline + description generation using LLMs  
- A/B testing integration with ad platforms
- Performance feedback loop and optimization
- Web frontend for insight management
- Additional data sources (Twitter, Meta, LinkedIn)