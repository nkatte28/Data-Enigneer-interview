# Topic 10: KV Specific

*Personal interview prep — tailored for your role and experience.*

---

## 👋 Intro

Hi, I'm Krishna. I'm a Senior Data Engineer based in Raleigh, NC, currently open to remote or Raleigh-based opportunities.

I have over six years of experience working across data engineering and distributed systems, with strong hands-on expertise in Databricks, Spark, Delta Lake, Snowflake, Python, SQL, Airflow, and AWS.

I started my career at Amazon right after college as a Seller Support Associate. While it wasn’t a technical role, it gave me strong exposure to corporate work culture, cross-functional collaboration, and understanding business requirements from a customer-centric perspective.

After about a year, I transitioned into a technical role at Wells Fargo as a Systems Engineer, where I began working on enterprise Big Data platforms. That’s where I built my foundation in distributed systems, Hadoop ecosystems, monitoring frameworks, and production support.

When I moved to the U.S., I had the opportunity at Nike to formally transition into a Data Engineering role. There, I worked extensively with Spark, large-scale analytics pipelines, and modern data platforms.

Most recently, I’ve been working at Converse as a Senior Data Engineer.

Most recently, at Converse, I own a data product called the Marketing Insights Platform. The intent of the platform is to validate marketing spend effectiveness by measuring how much we spend across channels like Meta, Twitter, Google, Bing, and other digital channels — and directly correlating that with revenue performance.

The key KPIs include spend, orders, clicks, revenue, impressions, and channel-level performance metrics. I helped build the product end-to-end — from data ingestion and modeling to enabling dashboards used by business stakeholders to guide marketing investment decisions.

Beyond just delivering dashboards, I focused heavily on scalability and future-proofing the platform. Initially, the business required reporting at a channel level, but I architected the data model to support campaign-level granularity so that we could provide deeper insights as the business matured. That allowed us to move from high-level reporting to more granular attribution analysis.

I also enabled Genie-based analysis capabilities so business users could explore data without writing SQL queries. That initiative is still evolving and requires additional ML tuning and training, but it’s part of our broader effort to make data more accessible and self-serve.

In parallel with owning this product, I also led the engineering efforts behind migrating over 40 production pipelines from Matillion and Snowflake to Databricks. I owned the migration end-to-end — architecture design, PySpark development, orchestration, optimization — resulting in roughly a 35% performance improvement and 25% infrastructure cost reduction.

At Nike and Converse more broadly,
I've worked extensively on high-volume Spark workloads powering supply chain, inventory, and marketing analytics. 
For example, I supported platforms that enabled executive dashboards and marketing insights, helping guide spend decisions with reliable and timely data. I enjoy partnering closely with analytics, product, and business stakeholders to translate evolving requirements into production-grade solutions.

On the platform side, I've contributed to orchestration frameworks using Airflow and Brickflow, built DDL utilities as part of an internal Data Common Utils framework to auto-generate schemas across Databricks and Snowflake, and developed a Databricks PyDABs proof of concept to improve automation and developer productivity.

My background blends software engineering discipline with modern Lakehouse platform design, so I approach data systems not just from a pipeline perspective
Overall, I enjoy building scalable, reliable systems, owning pipelines end-to-end, and contributing to long-term platform direction rather than just delivering isolated tasks.

---

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Articulate your value proposition clearly
- Confidently communicate your unique strengths and differentiators
- Connect your experience to specific business outcomes

---

## 💡 Interview Questions & Answers

**Quick index:** click a question to jump to the answer.

| # | Question |
|---|----------|
| 1 | [Why should we hire you?](#1-why-should-we-hire-you) |
| 2 | [What are your top three expectations and priorities in the next role?](#2-what-are-your-top-three-expectations-and-priorities-in-the-next-role) |
| 3 | [How are you upskilling in AI?](#3-how-are-you-upskilling-in-ai) |
| 4 | [What did you learn from building those AI apps?](#4-what-did-you-learn-from-building-those-ai-apps) |
| 5 | [What is your 3-year roadmap?](#5-what-is-your-3-year-roadmap) |
| 6 | [What is your biggest weakness?](#6-what-is-your-biggest-weakness) |
| 7 | [Why Rearc specifically?](#7-why-rearc-specifically) |
| 8 | [Tell me about a time you changed your mind after seeing new data](#8-tell-me-about-a-time-you-changed-your-mind-after-seeing-new-data) |
| 9 | [Tell me about a time you raised the bar on quality](#9-tell-me-about-a-time-you-raised-the-bar-on-quality) |
| 10 | [Tell me about a time you disagreed with a teammate and how you resolved it](#10-tell-me-about-a-time-you-disagreed-with-a-teammate-and-how-you-resolved-it) |
| 11 | [Tell me about a time you made a decision with incomplete information](#11-tell-me-about-a-time-you-made-a-decision-with-incomplete-information) |
| 12 | [Tell me about a time you reduced toil for a team](#12-tell-me-about-a-time-you-reduced-toil-for-a-team) |
| 13 | [Tell me about a time you owned a mistake and what you changed](#13-tell-me-about-a-time-you-owned-a-mistake-and-what-you-changed) |
| 14 | [Idempotent pipeline design for reprocessing](#14-idempotent-pipeline-design-for-reprocessing) |

---

### 1. Why should we hire you?

You should hire me because I don't just build pipelines — I build reliable data platforms that businesses can depend on.

Over the past several years, I've worked on large-scale data migrations and lakehouse implementations, including moving enterprise workloads from Snowflake and Matillion to Databricks. I've handled production systems processing high-volume supply chain and inventory data across multiple geographies.

What differentiates me is ownership. I think beyond just writing code — I focus on performance optimization, cost efficiency, data modeling best practices, governance, and long-term maintainability.

I'm comfortable collaborating cross-functionally with analysts, product managers, and leadership. I simplify complex technical concepts and align solutions with business goals.

I also actively explore AI-driven productivity improvements — for example, building internal tooling and even launching an AI-powered iOS app — so I'm always thinking about how to leverage new technologies responsibly.

I bring strong technical depth, platform-level thinking, and a calm, accountable mindset — especially in production-critical environments.

---

### 2. What are your top three expectations and priorities in the next role?

In my next role, I’m looking for three main things.

First, meaningful ownership. I want to contribute beyond writing pipelines — I’m interested in designing and improving scalable data platforms end-to-end, including performance, reliability, and governance.

Second, technically challenging problems. I enjoy working on distributed systems, streaming, and large-scale data transformations. I’m especially interested in environments where I can work on real-time systems or platform-level optimizations.

Third, exposure to AI-driven systems and continuous learning. I’ve already been exploring AI-assisted development and LLM integrations, and I’m very keen on deepening my understanding of how AI can enhance data platforms — whether through intelligent automation, data enrichment, or building AI-ready architectures. I value teams that encourage learning and staying ahead of industry shifts.

---

### 3. How are you upskilling in AI?

My upskilling in AI has been very hands-on and experimental. I’ve been building small AI-assisted apps using modern coding tools and AI copilots, which has helped me understand how LLMs support code generation, prompt refinement, and rapid prototyping.

Through that work, I’ve learned a lot about prompt clarity, iteration cycles, and output reliability — specifically where AI adds real leverage and where solid engineering judgment is still required. I’m now going deeper into how AI systems work architecturally and how they integrate with scalable data platforms. Since my core strength is data engineering, I’m intentionally growing at the intersection of AI and data infrastructure.

---

### 4. What did you learn from building those AI apps?

Building those AI-assisted apps taught me a few important lessons:

- Prompt clarity is critical: The quality of the output depends heavily on how clearly the problem is framed — vague inputs lead to inconsistent or shallow results.
- AI accelerates, but doesn’t replace, engineering judgment: I still had to validate logic, refactor code, design interfaces, and think about edge cases and failure modes.
- Iteration speed increases, but guardrails are essential: It’s easy to build something that “works” on the surface, but isn’t maintainable or production-ready without structure, tests, and review.

Overall, the experience helped me see both the power and the limitations of AI in real-world engineering workflows.

---

### 5. What is your 3-year roadmap?

Over the next three years, I want to focus on strong fundamentals and adaptability, especially as AI evolves quickly. Rather than anchoring myself to a specific tool or model, I’m deepening my expertise in scalable data platforms and distributed systems, because robust data foundations will remain critical regardless of which AI technologies win.

In parallel, I want to stay close to AI advancements and understand how they integrate into real data systems — designing AI-ready architectures and using automation where it creates clear business value. My goal is not to chase every trend, but to operate at the intersection of solid engineering principles and emerging AI capabilities.

---

### 6. What is your biggest weakness?

I tend to prefer having clear requirements before executing, which earlier in my career made me spend more time analyzing and refining the problem upfront. In fast-moving environments, that could slow down initial progress.

As I’ve gained experience, I’ve become more comfortable operating in ambiguity — starting with a reasonable assumption, iterating quickly, and validating with stakeholders rather than waiting for perfect clarity. I’m still deliberate in my planning, but I now balance that with bias for action and fast feedback loops.

---

### 7. Why Rearc specifically?

What stood out to me about this role at Rearc is the engineer-owned culture. I’m at a stage where I want to work in an environment where engineering decisions are driven by technical depth and pragmatism, not just process. From my conversation with the recruiter, it sounded like engineers here have real ownership and influence over architecture and tooling, which is exactly the kind of environment where I do my best work.

I was also excited by Rearc’s focus on modern technologies and forward-looking infrastructure. I enjoy working on scalable systems and evolving platforms, so contributing to a team that’s building forward rather than just maintaining legacy systems is very motivating to me.

Finally, the emphasis on work-life balance signals a healthy engineering culture. I’ve seen that sustainable teams produce better long-term results, and that philosophy aligns strongly with how I like to work and lead.

---

### 8. Tell me about a time you changed your mind after seeing new data.

One example was while working on the Marketing Insights Platform that I own at Converse. The goal of the platform was to measure the effectiveness of marketing spend across channels like Meta, Google, and other digital platforms by analyzing KPIs such as spend, impressions, clicks, orders, and revenue.

Initially, I believed that aggregating performance metrics at the channel level would be sufficient for the business to evaluate marketing ROI. So the first version of our data model and dashboards were designed around channel-level reporting.

However, after analyzing additional campaign-level data and reviewing how marketing teams actually made decisions, it became clear that channel-level aggregation was masking important performance differences between campaigns. Some campaigns within the same channel were performing very differently, and the marketing team needed more granular insights.

Based on that new data, I revisited the data model and redesigned parts of the pipeline to support campaign-level granularity instead of only channel-level reporting. This required changes to the ingestion logic, partitioning strategy, and downstream tables to maintain scalability while supporting the increased level of detail.

The result was that the business gained much more actionable insights, allowing them to better allocate marketing budgets across campaigns rather than just channels. It also made the platform more future-proof as the marketing team continued to expand their campaigns.

---

### 9. Tell me about a time you raised the bar on quality.

During our migration from legacy pipelines to Databricks, one of the data sources we relied on was SAP HANA. In the legacy system, the pipeline connected to SAP using a special "heavy user" account because jobs were frequently failing with out-of-memory errors on the HANA side.

When I began migrating the pipeline to Databricks, I initially tried to follow the same approach, but we did not have access to the heavy user. This forced me to investigate the root cause instead of simply replicating the existing setup.

When I analyzed the data volume, I noticed that the dataset was only a few million records, which should not normally cause memory issues. That led me to look deeper into the source system. After getting access to the HANA tables and working with the SAP SME team, I discovered that the data we were querying came from multiple nested views — essentially views built on top of other views.

Because of that structure, every query triggered multiple layers of computation in HANA before returning the data, which significantly increased memory usage and execution time.

Instead of continuing to rely on the heavy user workaround, I redesigned the ingestion approach. I materialized the underlying source views into intermediate tables so the expensive computations happened once rather than on every query. Since storage was not a constraint on our side but compute on HANA was, this change reduced query complexity and significantly improved the stability of the pipeline.

As a result, we eliminated the dependency on the heavy SAP user, reduced the time required to extract data from HANA, and made the ingestion process much more reliable for the Databricks pipelines.

**Another example (Nike supply planning):**

One example was when I joined Nike to help form a new data engineering team focused on supply planning. The previous team had transitioned several products to us because they were moving on to new initiatives.

Since our team was new to the domain — including engineers, managers, and product managers — we spent time understanding the existing pipelines and how the data was being used.

We noticed that there were around ten different pipelines that had been built over time as new requirements came in. While they worked individually, there was a lot of redundancy. Many of the pipelines were reading from the same sources and performing very similar transformations, with only minor differences in joins or aggregations.

Instead of continuing to build more pipelines on top of that structure, we saw an opportunity to improve the overall quality of the system. We analyzed the sources, target tables, key data elements, and relationships between the datasets to understand how we could design the data model more efficiently.

Based on that analysis, we redesigned the data layer and consolidated the pipelines. Instead of maintaining ten separate final tables, we created four well-structured base tables that captured the core datasets. On top of those, we exposed aggregated views that could serve specific business needs either directly in the data layer or through Tableau dashboards.

This significantly reduced redundancy, simplified maintenance, and made the pipelines easier to extend as new requirements came in. More importantly, it helped establish better data modeling standards for the new team as we continued building the supply planning platform.

---

### 10. Tell me about a time you disagreed with a teammate and how you resolved it.

During our migration from legacy pipelines to Databricks, we encountered a situation where several datasets were built using deeply nested views. The existing approach was to overwrite the final tables after running a series of transformations on those views.

I felt that this approach would become difficult to maintain and inefficient as the platform scaled. Since we were moving to Delta Lake, I suggested using Delta Merge instead of full overwrites so we could perform incremental updates and reduce unnecessary compute.

Some teammates initially preferred keeping the existing structure because it had been working reliably in the legacy system and they wanted to minimize risk during the migration.

In situations like this, I try to stay calm and avoid turning the discussion into an argument. Instead, I focus on understanding the reasoning behind the other perspective and finding a practical way to evaluate both options. Rather than pushing my approach, I suggested that we test both solutions on a sample dataset.

I demonstrated how using Delta Merge could reduce the amount of data processed and make the pipeline easier to manage when handling incremental updates. At the same time, we also evaluated the existing overwrite approach so we could compare the operational behavior objectively.

After reviewing the results and discussing factors like reprocessing, performance, and long-term scalability, we agreed that the Delta Merge approach provided better efficiency for this pipeline. We adopted it for that workload and gradually applied it to similar pipelines where it made sense.

This approach allowed us to modernize parts of the platform without disrupting the migration process, while also ensuring the team aligned around the best solution based on evidence rather than opinion.

---

### 11. Tell me about a time you made a decision with incomplete information.

During our migration of legacy pipelines to Databricks, one of the data sources we relied on was SAP HANA. When I first started migrating the pipeline, I noticed that the legacy system used a special "heavy user" account to read data from SAP because jobs were frequently failing with out-of-memory errors on the HANA side.

At that stage, I didn't have full visibility into why the heavy user was required, and initially it seemed like the simplest solution would be to request the same access for the Databricks pipelines. However, before doing that, I decided to investigate further because the dataset itself was only a few million records, which normally shouldn't cause memory issues.

Since I didn't have complete information about the source system, I started gathering more context. I obtained access to the HANA source tables and worked with the SAP SME team to analyze how the data was being queried. During that process, I discovered that the source datasets were actually built on multiple nested views — essentially views built on top of other views.

Because of this structure, every query triggered several layers of computation in HANA before returning results, which was causing high memory usage and slow reads.

Based on that understanding, I made the decision to change our ingestion strategy. Instead of querying the final nested view directly, I materialized intermediate layers closer to the base tables so the expensive computations were executed once rather than repeatedly.

This significantly reduced the load on HANA, eliminated the need for the heavy user account, and improved the reliability of the pipeline.

The key takeaway for me was that when information is incomplete, it's important to move forward by gathering incremental evidence, validating assumptions, and choosing the lowest-risk solution rather than simply replicating legacy behavior.

---

### 12. Tell me about a time you reduced toil for a team.

One example was when I was working on the data platform supporting Converse analytics workloads. As more datasets were onboarded to the platform, engineers frequently had to write similar code across multiple pipelines, such as connection logic for different data sources, shared configurations, and workflow setup.

This often led to duplicated code across different products and made the pipelines harder to maintain over time.

To help reduce this repetitive work, our team created a shared module called Data Common Utils, which centralized commonly used utilities and platform logic. I contributed to parts of this effort for my team by adding reusable components and helping organize some of the common code so that it could be shared across multiple data products.

For example, we centralized connection logic for sources like SQL Server, SAP HANA, Snowflake, and Box so engineers didn't have to reimplement those integrations in each pipeline. We also moved some shared workflow-related logic and common configuration attributes into the shared module.

Since we were supporting around ten different data products, this allowed engineers to reuse the same utilities instead of duplicating code across repositories.

As a result, it reduced repetitive development work, improved consistency across pipelines, and made it easier for engineers to onboard new datasets without rewriting the same boilerplate logic.

---

### 13. Tell me about a time you owned a mistake and what you changed.

One example happened while I was working on a data pipeline supporting analytics workloads. Early in the implementation, I made a design decision to apply several transformations and aggregations in a single stage of the pipeline because it seemed simpler at the time.

When the pipeline started running in production, we noticed that debugging issues became difficult because multiple transformations were happening in one step. It also made partial reprocessing harder when a downstream issue occurred.

After reviewing the pipeline and discussing it with the team, I realized that the design decision I had made earlier was contributing to the operational complexity. I owned that mistake and proposed restructuring the pipeline to better align with a layered approach, separating ingestion, transformation, and aggregation stages.

We refactored the pipeline so that intermediate datasets were clearly defined and could be rerun independently. This made debugging much easier and improved the reliability of the pipeline.

From that experience, I became more deliberate about designing pipelines with maintainability and operational visibility in mind, not just initial simplicity.

---

### 14. Idempotent pipeline design for reprocessing

**What it means:** An idempotent pipeline means: if I run the same pipeline again with the same input, I should get the same final result — not duplicates, not corrupted data, not double counts. That is very important for reprocessing, retries, backfills, and late-arriving data.

**Simple interview answer:**

For idempotent pipeline design, I make sure the pipeline can be safely rerun for the same data window without producing duplicate records or inconsistent outputs. I usually do this by defining a clear business key, processing data in deterministic batches or partitions, and using merge/upsert logic instead of blind inserts. I also separate raw ingestion from curated layers so that if reprocessing is needed, I can reload only the impacted partitions or business dates. The goal is that retries, backfills, or late data handling produce the same final state every time.

**How to design it:**

1. **Use a stable business key**  
   Every record should have something that uniquely identifies it (e.g. `order_id`, `customer_id + effective_date`, `event_id`). Without a stable key, reruns can create duplicates.

2. **Keep raw data immutable**  
   In bronze/raw layer, store the source data as-is. You always have a recovery point and can replay from raw if something breaks.

3. **Use merge/upsert in curated layers**  
   Instead of `INSERT INTO target_table SELECT * FROM source_data`, use `MERGE INTO target t USING source s ON t.id = s.id WHEN MATCHED THEN UPDATE SET ... WHEN NOT MATCHED THEN INSERT ...`. If the same data comes again, it updates or does nothing instead of duplicating.

4. **Reprocess by window or partition**  
   Rerun only the impacted range: specific date, partition, or batch id (e.g. rerun 2026-03-01 to 2026-03-03, or recompute only `region='US'`). This keeps reprocessing efficient.

5. **Track event time and load time separately**  
   Use `event_time` (when the business event happened) and `ingestion_time` (when it arrived). This helps with late-arriving data, backfills, and auditing.

6. **Avoid non-deterministic logic**  
   Avoid depending on random numbers, current timestamp in transformations, or unordered dedup logic, because reruns may produce different results.

7. **Make aggregates replaceable**  
   For summary tables, either recompute the full impacted partition and overwrite it, or use deterministic merge logic (e.g. for daily sales, recompute only that day and overwrite that partition).

**Real example:**  
Suppose daily orders come from SAP. **Bad design:** every rerun inserts all records again → duplicates in target. **Better design:** bronze stores raw extract; silver deduplicates using `order_id`; gold uses `MERGE INTO` fact table; if March 1 data was bad, rerun only March 1 → final table stays correct.

**Short version for interview:**  
I design pipelines so reruns are safe. That usually means using stable business keys, keeping raw data immutable, and using merge or overwrite-by-partition strategies instead of append-only inserts. For reprocessing, I rerun only the affected window or partition, so the final state remains correct without duplications.

---

## 📝 Notes

*Add more KV-specific questions and answers as you prepare.*
