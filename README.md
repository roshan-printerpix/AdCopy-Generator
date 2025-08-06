# Ad‑Creative Generation Pipeline

> **Goal** – Use a data‑driven LLM pipeline to scrape the web, clean & structure the data, surface insights, and generate CTR‑optimized headlines and descriptions that leverage proven tactics (e.g., Trojan headlines).

---

## 1. Executive Summary

| Function              | What it Does                                                    | Tech Choice                                |
|-----------------------|------------------------------------------------------------------|---------------------------------------------|
| **Data Collection**   | Pull raw text from websites, forums, social channels            | Scrapy + API wrappers                       |
| **Cleaning**          | Strip noise, deduplicate insights, apply length & CTR filters   | Custom code + LLM                           |
| **Structuring**       | Cluster topics & annotate tags (e.g., “Trojan,” “Curiosity”)    | GPT‑4o + BERTopic + spaCy                   |
| **Insight Management**| RAG + rule engine to evolve rules, score insights               | Pinecone + LangChain + durable‑rules + Supabase |
| **Generation**        | Produce headline + description pairs from top insights          | GPT‑4o + prompt engineering                 |
| **Feedback Loop**     | Use Google Ads performance data to refine insight scoring       | Manual (now), later automated via API       |
| **Orchestration**     | Schedule & monitor workflows                                    | Prefect (Cloud or OSS)                      |
| **Storage**           | Persist raw & processed data, rules, creatives                  | Supabase + Pinecone + Redis                 |

> 🔍 **CTR Boost Tip** – Trojan headlines that plant a “just‑one‑more‑click” curiosity point can deliver 2× uplift. This tactic is built into cleaning, structuring, scoring, and generation steps.

---

## 2. Prioritized Pipeline Flow

| Step                 | Priority | Output                        | Key LLM Tasks                                      |
|----------------------|----------|-------------------------------|----------------------------------------------------|
| **1. Data Collection** | 1        | Raw JSON per source           | Scrape, API calls                                  |
| **2. Cleaning**        | 2        | Cleaned text + relevance score| Noise removal, deduplication, trimming             |
| **3. Structuring**     | 2        | Annotated document            | Clustering, NER, tagging                           |
| **4. Insight Management** | 2    | Ranked insights + rules       | Similarity check, diff score, whitelist/blacklist  |
| **5. Generation**      | 3        | Headline + description pair   | Prompt-driven content generation                   |

---

## 3. Detailed Component Design

### 3.1 Data Collection (Priority 1)

| Source                  | Tool           | Notes                                 |
|-------------------------|----------------|---------------------------------------|
| **Websites / Blogs**    | Scrapy         | Use middlewares for rotation & delay |
| **Reddit / Quora / Twitter** | `praw`, `quill`, `tweepy` | Rate-limit adherence |
| **Social Pages** (Meta, LinkedIn) | Graph API      | Store post IDs for deduplication     |

> **Scheduler** – Prefect (DAGs): nightly jobs, retry logic, metrics push.

---

### 3.2 Cleaning (Priority 2)

| Raw Input           | Cleaning Goal                                   | Output                                |
|---------------------|--------------------------------------------------|----------------------------------------|
| Forum posts         | Strip HTML, trim to core story                  | Max 3–4 paragraphs, clean core text    |
| Duplicate insights  | Remove if similar to archived items (Supabase)  | Unique filtered dataset                |
| Low relevance posts | Drop if relevance < 7/10                        | Filtered by LLM                        |

> Uses custom filters + LLM scoring prompts.

---

### 3.3 Structuring & Annotation (Priority 2)

| Action            | Tool                    | Output Fields                             |
|-------------------|-------------------------|-------------------------------------------|
| Topic clustering  | BERTopic (TF-IDF + UMAP)| `cluster_id`, `desc`                      |
| Entity extraction | spaCy / GPT NER         | `entities`, `brands`, `sentiment`         |
| Tagging           | GPT-4o (prompted)       | `tags`: ["Trojan", "Curiosity", "Story"]  |
| JSON Schema       | N/A                     | `url`, `body`, `cluster`, `tags`, `score` |

> Optional: Store cluster centroids in Pinecone for similarity comparisons.

---

### 3.4 Insight Management (Priority 2)

1. **RAG Lookup**
   - Embeddings via `text-embedding-3-small`
   - Stored in **Pinecone**

2. **Rule Evolution**
   - Compare new insight to past using `durable-rules`
   - Use **diff score**: if new > old → replace rule

3. **List Categorization**
   - Whitelist: performed well
   - Blacklist: poor CTR
   - Greylist: untested insights

4. **Insight Archive**
   - Store last 7 days in **Supabase**

5. **Human-in-the-Loop**
   - Alert via email/Slack when confidence < 0.7
   - Manual override for blacklists or preferred rules

---

### 3.5 Generation (Priority 3)

| Output         | Prompt Template                                                                 | Constraints                            |
|----------------|----------------------------------------------------------------------------------|-----------------------------------------|
| **Headline**   | “Generate 3 headlines using the **Trojan** pattern for *product X*, targeting *audience Y*. Each ≤ 8 words.” | Trojan-style, curiosity, no filler      |
| **Description**| “Write 2 sentences supporting the headline above, include a *unique benefit* and a *CTA*.”  | Max 2 sentences, must end with CTA     |

> Output is checked for length, tone, keywords. Stored with `creative_id`, `score`, and metadata.

---

## 4. Feedback Loop (Phase 6)

| Input                     | Action                                      | Output                                     |
|---------------------------|---------------------------------------------|--------------------------------------------|
| Google Ads Performance    | Analyze CTR & map to insight + headline     | Update insight tags: Whitelist / Blacklist |
| Manual Review (optional)  | Tweak prompt, override blacklist            | New prompt version fed back into pipeline  |

> Manual now, with planned automation via Google Ads API.

---

## 5. Tooling Summary

| Layer             | Tool                   | Why                                                   |
|-------------------|------------------------|--------------------------------------------------------|
| Scraping          | Scrapy + APIs          | Python-first, scalable                                |
| Vector Store      | Pinecone               | Fast, managed similarity search                        |
| Storage DB        | Supabase               | Time-series friendly, flexible JSON schema             |
| Cache (optional)  | Redis                  | Fast reads & lookups                                  |
| Rule Engine       | durable-rules          | Easy conflict logic with Python integration            |
| LLM               | GPT-4o                 | Reliable, long context, score-based prompting support  |
| Orchestration     | Prefect                | Scheduling, retry, observability                       |

---

## 6. Example End‑to‑End Flow (One Day)

1. **Scraping** collects 1,200 Reddit posts about *“budget running shoes”*
2. **Cleaning** removes 50% of irrelevant or duplicate data
3. **Structuring** clusters insights into “Ultramarathon”, “Athleisure”, etc.  
   - One insight gets tag: `"Trojan"`
4. **RAG** matches last week’s best scoring insight at 0.86  
   - New insight scores 0.93 → rule replaced
5. **Generation** output:
   - **Headline**: “She Tried These. Her Feet Thanked Her.”
   - **Description**: “Discover what runners are raving about. See why everyone’s switching.”
6. Stored with tags, scheduled for A/B test, result fed back into pipeline

---