# Ad‑Creative Generation Pipeline

> **Goal** – Use a data‑driven LLM pipeline to scrape the web, clean and structure content into clear insights, and eventually generate CTR‑optimized headlines and descriptions. This document covers only the first part: data collection, cleaning, structuring, deduplication, and storing insights.

---

## 1. Executive Summary

| Function              | What it Does                                                    | Tech Choice                                |
|-----------------------|------------------------------------------------------------------|---------------------------------------------|
| **Data Collection**   | Pull raw text from websites, forums, social channels            | Scrapy + API wrappers                       |
| **Cleaning**          | Strip noise, extract clean text from raw content                | Custom code + LLM                           |
| **Structuring**       | Convert cleaned content into structured insight format          | GPT‑4o (prompt-based)                       |
| **Deduplication**     | Compare with Supabase DB, discard similar insights              | GPT similarity + Supabase lookup            |
| **Storage**           | Persist only unique structured insights with greylist status    | Supabase                                    |

---

## 2. Pipeline Flow (Current Scope)

| Step                   | Output                               | Description                                                        |
|------------------------|---------------------------------------|--------------------------------------------------------------------|
| **1. Data Collection** | Raw scraped content                  | Scraped directly from Reddit, blogs, etc. **Not stored**           |
| **2. Cleaning**        | Clean plain text                     | Remove noise, tags, metadata                                       |
| **3. Structuring**     | Formatted insight (INSIGHT, RESULTS, LIMITATIONS, SCORE) | Convert clean content into structured insights                    |
| **4. Deduplication**   | Unique insights only                 | Compare with Supabase records, discard duplicates                  |
| **5. Storage**         | Supabase entry (greylisted)          | Store new insights with `status = greylist`                        |

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
| **Structuring**  | Use prompt to create:                       | - INSIGHT                             |
|                  | - RESULTS                                   | - LIMITATIONS/CONTEXT                 |
|                  | - DIFFERENCE SCORE (0–100)                  | - Example (optional)                  |

> Example INSIGHT:  
> **INSIGHT:** Use Trojan Headlines…  
> **RESULTS:** 2x CTR uplift in pharma...  
> **LIMITATIONS:** Often leads to product pages...

---

### 3.3 Deduplication

| Action                     | Tool / Method            | Result                              |
|----------------------------|--------------------------|-------------------------------------|
| Compare new insights       | LLM similarity or GPT-4o | Filter out similar insights         |
| Search against Supabase DB| Supabase `insights` table| Prevent duplicates from being saved |

> Only **unique insights** proceed to storage.

---

### 3.4 Storage (Supabase)

| Field             | Type       | Notes                                       |
|-------------------|------------|---------------------------------------------|
| `id`              | UUID       | Primary key                                 |
| `insight`         | Text       | Full structured insight                     |
| `results`         | Text       | Any performance or case study info          |
| `limitations`     | Text       | Where/why this may fail                     |
| `difference_score`| Integer    | Value from 0–100 (how different it is)      |
| `status`          | Text       | `greylist` (default on insert)              |
| `created_at`      | Date       | Insert Date                                 |

---

## 4. What’s Not Yet Implemented (Future Phases)

- Insight review and human scoring  
- Headline + description generation using LLMs  
- A/B testing in ad platforms  
- Feedback loop with performance logging  

These will come after the initial insight pipeline is deployed.

---