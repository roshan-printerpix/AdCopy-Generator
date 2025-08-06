# Ad‑Creative Generation Pipeline  

> **Goal** – Use a data‑driven LLM pipeline to scrape the web, clean & structure the data, surface insights, and generate CTR‑optimized headlines and descriptions that leverage proven tactics (e.g., Trojan headlines).  

---

## 1. Executive Summary

| Function | What it Does | Tech Choice |
|----------|--------------|--------------|
| **Data Collection** | Pull raw text from websites, forums, social channels | Scrapy + API wrappers |
| **Cleaning** | Strip noise, enforce length limits, apply headline‑CTR rules | Custom code |
| **Structuring** | Cluster topics & annotate tags (e.g., “Trojan,” “Curiosity”) | GPT‑4o + prompt engineering |
| **Insight Management** | RAG + rule engine to evolve rules automatically | Pinecone + LangChain + durable‑rules |
| **Generation** | Produce headline + description pairs in one pass | GPT‑4o + prompt engineering |
| **Orchestration** | Schedule & monitor workflows | Prefect (Cloud or OSS) |
| **Storage** | Persist raw & processed data, rules, creatives | Supabase + Pinecone + Redis |

> 🔍 **CTR Boost Tip** – Trojan headlines that plant a “just‑one‑more‑click” curiosity point can deliver 2× uplift. The pipeline incorporates that knowledge into every rule & generation prompt.

---

## 2. Prioritised Pipeline Flow

| Step | Priority | Output | Key LLM Tasks |
|------|----------|--------|----------------|
| **1. Data Collection** | 1 | Raw JSON per source | Scrape, API calls |
| **2. Cleaning** | 2 | Cleaned text (≤ 8 k tokens) | Noise removal, length capping, relevance scoring |
| **3. Structuring** | 2 | Annotated document | Topic cluster, entity extraction, tag assignment |
| **4. Insight Management** | 2 | Updated rule set & archive | RAG lookup, conflict detection, rule creation |
| **5. Generation** | 3 | Headline + description pair | Prompt‑driven copy generation, rule‑based style constraints |

---

## 3. Detailed Component Design

### 3.1 Data Collection (Priority 1)

| Source | Tool | Notes |
|--------|------|-------|
| **Websites / Blogs** | *Scrapy* pipelines | Use middlewares for rotation & delay |
| **Reddit / Quora / Twitter** | `praw`, `quill`, `tweepy` | Rate‑limit adherence |
| **Social Pages (Meta, LinkedIn)** | Official Graph API (rate‑limit friendly) | Store post IDs for de‑dup |

*Scheduler* – **Prefect** DAG: nightly pulls, retry logic, metrics push.  

### 3.2 Cleaning (Priority 2)

| Raw Input | Cleaning Goal | LLM Prompt Example | Output |
|-----------|---------------|---------------------|--------|
| Long forum thread | Strip HTML, URLs, keep story core | “Condense this to 4 paragraphs, keep the hook. Remove tags URLs usernames.” | 4‑paragraph snippet (≤ 2 k tokens) |
| Misc. noise | Remove irrelevant sections | “Drop any question‑answer pairs, keep narrative.” | Clean body |
| Relevance scoring | Keep only content ≥ 7/10 relevance to ad context | “Rate relevance (0‑10). Keep ≥ 7.” | Boolean flag |

**Tech Choice** – Custom code for noise removal and filtering.  

### 3.3 Structuring & Annotation (Priority 2)

| Action | Tool | Stored Features |
|--------|------|-----------------|
| Topic clustering | **BERTopic** on TF‑IDF + UMAP | `cluster_id`, `cluster_desc` |
| Entity extraction | **spaCy** / `ner` | Product names, brand, sentiment |
| Tag generation | Custom prompt | `tags` = [“Trojan”, “Curiosity”, “Storytelling”, …] |
| Schema (JSON) | | `source`, `url`, `body`, `cluster`, `entities`, `tags`, `sentiment` |

> **Optional** – Persist cluster centroids in **Pinecone** to aid future similarity searches.

### 3.4 Insight Management (RAG + Rules Engine) (Priority 2)

1. **Embedding**  
   - Model: `text-embedding-3-small` (OpenAI).  
   - Store vector + metadata in **Pinecone**.

2. **RAG lookup** – Retrieve top‑k similar insights to new clean doc.

3. **Rule Engine** – `durable‑rules` in Python.
4. **Human‑in‑Loop** – Slack or email alert if `confidence < 0.7`.

5. **Archive** – Store last 7 days of rules + insights in **Supabase** (time‑series) for future RAG.

> **Insight Format** – JSON structure with id, tags, rule, score, and timestamp.

### 3.5 Content Generation (Priority 3)

| Output | Prompt Template | LLM | Constraints |
|--------|-----------------|-----|-------------|
| **Headline** | “Generate 3 headline variants that use the **Trojan** pattern for a *product X* targeting *audience Y* in **English**. Each headline ≤ 8 words.” | **GPT‑4o** | 8‑word max, curiosity focus, no generic filler |
| **Description** | “Write a 2‑sentence description supporting the headline above that emphasizes the *unique benefit* and ends with a *call‑to‑action*.” | **GPT‑4o** | 2 sentences, CTA present |

**Post‑Processing**  
- Length check → Trim or extend with LLM.  
- Sentiment & keyword check via spaCy.  

Output stored in JSON schema with creative_id, headline, description, tags, score, and timestamp.

---

## 4. Recommended Tools & LLMs Summary

| Layer | Tool | Rationale |
|-------|------|-----------|
| **Scraper** | Scrapy + API wrappers | Reliable, scalable, Python‑first |
| **Orchestration** | Prefect (Cloud or OSS) | Python-friendly DAGs, observability |
| **Vector Store** | Pinecone | Managed, low‑latency similarity |
| **Cleaning** | Custom code | Efficient noise removal and filtering |
| **LLM for Generation** | GPT‑4o | Proven copywriting quality |
| **Embedding** | `text-embedding-3-small` | Fast, low‑cost |
| **Rule Engine** | durable‑rules / business‑rules | Declarative logic with Python integration |
| **Databases** | Supabase (raw + archives), Redis (cache) | ACID, time‑series, fast reads |

> **Why GPT‑4o?**  
> - 8 k–32 k context (fits entire cleaned doc).  
> - Cheap inference, robust prompt flexibility.  
> - Supports “confidence” or “score” outputs (via chain‑of‑thought or `best_of`).  

---

## 5. Deployment & Operations

1. **Containerise** every component (Scraper, LLM workers, Prefect agent).  
2. **CI/CD** – GitHub Actions to push Docker images to registry (DockerHub / ECR).  
3. **Scaling** – Prefect Cloud + AWS Fargate; LLM calls routed through **OpenAI API**.  
4. **Observability** – Prefect UI + Prometheus/ Grafana for task metrics.  
5. **Security** – Store API keys in AWS Secrets Manager / Vault.  

---  

## 6. Example End‑to‑End Flow (One Day)

1. **Scraper** pulls 1200 Reddit posts about *“budget running shoes”*.  
2. **Cleaning** removes 45 % noise, keeps 3‑paragraph story for each post.  
3. **Structuring** → 5 clusters: “Athleisure”, “Ultramarathon”, “Lifestyle”. Tags added; one cluster flagged “Trojan”.  
4. **RAG** finds last 7 days rule: “Headlines that start with a question” → 0.89 score. New insight: ““Ready to see the twist?” → 0.92, so rule is replaced.  
5. **Generation** creates 3 headline/description pairs for each cluster, e.g.:

   *Headline:* “Ready to see the twist? Find it now!”  
   *Description:* “Discover the hidden feature that changes everything. Click to learn more.”

6. All creatives stored with tags, score, and scheduled for A/B testing.

---

## 7. Next Steps (Out of Scope Right Now)

| Item | Status |
|------|--------|
| Feedback‑loop from Google Ads | *Not implemented – to be added later* |
| Image Generation | *Excluded for now* |
| Real‑time streaming ingestion | *Potential future upgrade* |

---