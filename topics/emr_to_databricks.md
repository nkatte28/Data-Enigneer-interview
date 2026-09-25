# EMR to Databricks Migration Guide

## 🎯 Learning Goals



1. Developer productivity → faster time to production
Instead of saying “Databricks has notebooks and better debugging,” say:
“We wanted to reduce the engineering effort required to take a Spark pipeline from development to production.”

On EMR, the lifecycle could involve:
Develop Spark code
      ↓
Package dependencies
      ↓
Configure EMR
      ↓
Bootstrap scripts
      ↓
Deploy
      ↓
Run
      ↓
Collect logs
      ↓
Debug failure
      ↓
Modify configuration
      ↓
Redeploy

With Databricks, more of that lifecycle is integrated:
Develop
   ↓
Test
   ↓
Run
   ↓
Debug
   ↓
Deploy as workflow
   ↓
Monitor

So the benefit isn't just “easier development.”
The actual outcome is:
shorter development/debug/deployment cycles → faster productionization of data pipelines.

That sounds much stronger in an interview.
2. Reduce infrastructure and operational overhead
Your second point is exactly right.
With EMR, even though AWS manages the service, your engineering/platform team may still have to own decisions around:
Instance families
Core vs task nodes
Spot vs On-Demand
Min/max cluster size
EBS configuration
Bootstrap scripts
Spark configuration
EMR versions
Spark upgrades
Dependency compatibility
Cluster startup / shutdown
Scaling policies

Those things don't directly create business data products.
So frame it as:
“We wanted data engineers spending less time operating Spark infrastructure and more time building data products.”

Instead of:
“EMR was difficult to manage.”

The first is much more professional and defensible.
3. Standardize the data platform / lakehouse architecture
This becomes your longer-term architectural reason.
Before:
Spark job A → S3 parquet
Spark job B → S3 parquet
Spark job C → S3 parquet

Different configurations
Different dependencies
Different deployment patterns
Different monitoring

The goal was to move toward:
                 Databricks
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
       Ingest     Transform   Serve
          ↓          ↓          ↓
       Bronze →    Silver →    Gold
                     │
                  Delta
                     │
              Governed platform

So you can say:
“The migration was also part of standardizing on a lakehouse architecture rather than treating each Spark ETL pipeline as an independently operated workload.”

Put the three together
This is the story I would use:
“The migration wasn't because EMR couldn't run Spark workloads. Technically, EMR was capable. The main issue was the operating model around it.”

“From a developer perspective, we wanted to shorten the path from development to production. Development, testing, debugging, deployment, orchestration, and monitoring were more fragmented in our EMR setup. Moving to Databricks gave us a more integrated engineering workflow, which reduced the effort and turnaround time required to productionize pipelines.”

“From an operations perspective, we also wanted to reduce how much infrastructure responsibility the data engineering team carried — things like EC2 instance selection, core and task node configuration, Spot strategy, bootstrap scripts, cluster lifecycle, EMR upgrades, Spark upgrades, and configuration management.”

“And strategically, this was part of moving toward a standardized lakehouse architecture, where we could organize data into Bronze, Silver, and Gold layers and manage pipelines and datasets through a common platform rather than maintaining isolated Spark jobs.”


By the end of this topic, you should be able to:
- Explain **why** teams migrate from EMR (Spark/Hive on AWS) to Databricks
- Compare EMR vs Databricks across compute, orchestration, storage, and operations
- Describe a **migration flow** (phases, order of operations)
- Articulate trade-offs and interview-ready answers in 30 seconds

---

## 📑 Table of Contents

1. [Why Migrate: EMR vs Databricks](#1-why-migrate-emr-vs-databricks)
2. [Architecture: Before vs After](#2-architecture-before-vs-after)
3. [Migration Flow and Phases](#3-migration-flow-and-phases)
4. [Reasons to Migrate (Interview-Ready)](#4-reasons-to-migrate-interview-ready)
5. [Risks and Considerations](#5-risks-and-considerations)
6. [30-Second Interview Answer](#6-30-second-interview-answer)

---

## 1. Why Migrate: EMR vs Databricks

### 1.1 Quick Comparison

| Aspect | EMR (Spark/Hive on AWS) | Databricks |
|--------|--------------------------|------------|
| **Compute** | EC2 clusters you manage; bootstrap, AMI, config | Managed clusters; job / all-purpose; policies |
| **Orchestration** | Step Functions, Airflow, or custom | Built-in Workflows, DAG, retries, params |
| **Storage** | S3 + Hive metastore; you handle atomicity | S3 + Delta Lake (ACID, MERGE, time travel) |
| **Dev experience** | Notebooks optional; lots of glue code | Unified workspace, repos, collaboration |
| **Cost model** | Pay for EC2 + EMR; often always-on clusters | Job clusters (spin up/down), autoscale, spot |
| **Governance** | DIY (IAM, Lake Formation, etc.) | Unity Catalog, centralized permissions |

### 1.2 When Migration Makes Sense

- You have **many pipelines** with **SLAs** and **multiple teams**
- You want **less ops** (cluster lifecycle, bootstrap, failure recovery)
- You need **ACID, upserts, CDC** (Delta Lake) without building it yourself
- You want **unified batch + streaming** and better **cost utilization**

---

## 2. Architecture: Before vs After

### 2.1 Before (EMR-Centric)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           EMR-CENTRIC ETL                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Sources          Ingestion           Compute              Storage     │
│   ───────          ─────────           ───────              ───────     │
│                                                                          │
│   ┌──────┐         ┌─────────────┐     ┌─────────────────┐   ┌─────┐    │
│   │ DB   │────────│ Lambda/     │────│                  │   │     │    │
│   └──────┘        │ Glue / Kinesis│   │  EMR Cluster    │───│ S3  │    │
│   ┌──────┐         └─────────────┘     │  (Spark/Hive)   │   │     │    │
│   │ Kafka│─────────────────────────────│  - Bootstrap    │   │Raw  │    │
│   └──────┘         ┌─────────────┐     │  - Config drift │   │Curated│   │
│   ┌──────┐         │ Step Fn /   │────│  - Manual scale │   └─────┘    │
│   │ APIs │         │ Airflow     │     └─────────────────┘       │      │
│   └──────┘         └─────────────┘              │                │      │
│                          │                       │                │      │
│                          ▼                       ▼                ▼      │
│                   Cluster lifecycle         Hive Metastore    No ACID   │
│                   and failure recovery      (schema, tables)  (custom)  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 After (Databricks-Centric)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABRICKS-CENTRIC ETL                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Sources          Ingestion           Compute              Storage     │
│   ───────          ─────────           ───────              ───────     │
│                                                                          │
│   ┌──────┐         ┌─────────────┐     ┌─────────────────┐   ┌─────┐   │
│   │ DB   │────────│  Databricks │     │  Job Clusters   │   │     │   │
│   └──────┘        │  Connectors │────│  - Spin up/down  │───│ S3  │   │
│   ┌──────┐         │  / Delta    │     │  - Autoscale    │   │     │   │
│   │ Kafka│────────│  Streaming  │     │  - Policies     │   │Delta│   │
│   └──────┘         └─────────────┘     └─────────────────┘   │Lake │   │
│   ┌──────┐                │                    │            │ACID │   │
│   │ APIs │                │             ┌───────┴───────┐    └─────┘   │
│   └──────┘                ▼             │  Workflows   │         │     │
│                          ┌─────────────┐│  DAG, retry  │         │     │
│                          │  Workspace  ││  params      │         │     │
│                          │  Notebooks  │└──────────────┘         │     │
│                          │  Repos      │                         │     │
│                          └─────────────┘    Unity Catalog       │     │
│                                                (governance)       │     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Data Flow: EMR vs Databricks

```
EMR:
  Source → S3 (raw) → EMR Spark job (scheduled by Step Fn/Airflow) → S3 (Parquet) → Hive metastore
  Problems: no ACID, small files, schema drift, custom upsert logic

Databricks:
  Source → S3/ADLS (raw) → Databricks Job (Workflows) → Delta tables (ACID, MERGE, OPTIMIZE)
  Benefits: transactional writes, time travel, Z-ORDER, fewer custom patterns
```

---

## 3. Migration Flow and Phases

### 3.1 High-Level Migration Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Assess &   │────▶│  Foundation │────▶│  Migrate    │────▶│  Cutover &  │
│  Plan       │     │  (Catalog,  │     │  Pipelines  │     │  Decommission│
│             │     │   clusters) │     │  (batch 1..n)│     │  EMR        │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
  • Inventory         • Unity Catalog     • Convert Spark     • Redirect
    pipelines         • Cluster policies    to Delta           consumers
  • Pick pilot       • S3/ADLS mounts     • Workflows DAGs   • Turn off EMR
  • Define SLAs      • Dev/prod workspaces • Test & validate
```

### 3.2 Phase 1: Assess & Plan

| Step | Action |
|------|--------|
| 1.1 | Inventory pipelines (batch, streaming, dependencies) |
| 1.2 | Map EMR config (instance types, worker count, Spark config) to Databricks equivalents |
| 1.3 | Choose pilot (1–2 pipelines, non-critical or high-value) |
| 1.4 | Define success: SLA, cost, reliability metrics |

### 3.3 Phase 2: Foundation

| Step | Action |
|------|--------|
| 2.1 | Set up Databricks workspace(s); connect to S3/ADLS |
| 2.2 | Configure Unity Catalog (or Hive metastore) and mounts |
| 2.3 | Define cluster policies (instance types, autoscale, spot) |
| 2.4 | Create dev/prod separation and CI/CD for notebooks/jobs |

### 3.4 Phase 3: Migrate Pipelines

| Step | Action |
|------|--------|
| 3.1 | Convert reads/writes from Parquet/ORC to Delta where needed |
| 3.2 | Replace custom upsert/merge logic with Delta MERGE |
| 3.3 | Recreate DAGs in Workflows (task dependencies, retries, params) |
| 3.4 | Tune clusters (job clusters, autoscale) and Spark config |
| 3.5 | Run in parallel with EMR; compare outputs and performance |

### 3.5 Phase 4: Cutover & Decommission

| Step | Action |
|------|--------|
| 4.1 | Switch consumers to Databricks-produced tables |
| 4.2 | Stop EMR schedules; keep EMR available for rollback short term |
| 4.3 | Decommission EMR clusters and clean up Step Functions/Airflow |

---

## 4. Reasons to Migrate (Interview-Ready)

### 1) Platform productivity and faster delivery

- **Unified workspace**: notebooks, jobs, repos, collaboration in one place
- **Built-in Workflows**: task dependencies, retries, alerts, parameters—less glue
- **Less custom code**: no stitching EMR + Step Functions/Airflow + bootstrap scripts

**Interview line:** *"We reduced operational overhead because Databricks gives first-class orchestration and dev experience; engineers spent less time babysitting clusters and more time shipping features."*

---

### 2) Better reliability and simpler operations

- **EMR pain**: cluster lifecycle, bootstrap actions, AMI/library drift, failure recovery
- **Databricks**: consistent retry semantics, cluster policies, clearer dependency management

**Interview line:** *"Databricks reduced failure modes tied to cluster bring-up and configuration drift, improving SLA adherence."*

---

### 3) Delta Lake (ACID) and simpler incremental processing

- **EMR + Hive/S3**: you manage atomicity, small files, schema drift, upserts, late data
- **Databricks + Delta**: ACID, MERGE for upserts (CDC), time travel, schema enforcement/evolution, OPTIMIZE/VACUUM

**Interview line:** *"Delta made CDC and upserts robust—transactional MERGE and versioning removed a lot of custom logic."*

---

### 4) Performance

- **Faster ETL**: optimized runtime, better shuffle and adaptive query execution
- **Storage**: Z-ORDER, liquid clustering, compaction (OPTIMIZE) for better read performance

**Interview line:** *"We improved runtime by tuning partition strategy and using Delta optimizations and maintenance workflows."*

---

### 5) Cost and resource utilization

- **EMR**: often always-on clusters, underutilization, extra ops cost
- **Databricks**: job clusters (spin up/down), autoscaling, cluster policies, better utilization for bursty workloads

**Interview line:** *"Cost came down through better utilization (job clusters + autoscaling) and fewer reruns from flaky infra."*

---

### 6) Governance and access control

- **EMR**: DIY (IAM, Lake Formation, etc.)
- **Databricks**: Unity Catalog, centralized permissions, auditability, lineage

**Interview line:** *"We needed consistent governance across regions and teams—Databricks gave stronger centralized controls."*

---

### 7) Batch + streaming unification

- **EMR**: often separate patterns and glue for Kafka → lake → curated
- **Databricks**: consistent streaming + batch (checkpoints, monitoring, job configs)

**Interview line:** *"We standardized batch and streaming in one platform and reduced bespoke code paths."*

---

## 5. Risks and Considerations

| Risk | Mitigation |
|------|------------|
| **Vendor lock-in** | Use open Delta Lake and Spark; keep data in S3/ADLS |
| **Cost surprise** | Start with job clusters and autoscale; set budget alerts |
| **Migration timeline** | Pilot first; migrate in waves; run EMR and Databricks in parallel |
| **Team skills** | Training on Workflows, Delta, cluster policies; reuse existing Spark skills |
| **Hive compatibility** | Use Unity Catalog or external Hive metastore; plan table migration |

---

## 6. 30-Second Interview Answer

**"We migrated from EMR to Databricks to reduce operational overhead, improve reliability, and standardize ETL with Delta Lake. Databricks gave us a unified dev and orchestration experience, strong support for CDC and upserts via Delta MERGE, and better performance tuning. The combination of simpler operations, fewer failure modes, and better compute utilization helped us hit SLAs more consistently and lower cost."**

---

## Quick Reference: EMR → Databricks Mapping

| EMR | Databricks |
|-----|------------|
| EMR cluster | Job cluster or all-purpose cluster |
| Step Functions / Airflow | Workflows (DAG, tasks, retries) |
| S3 + Hive tables | S3 + Delta tables (Unity Catalog or Hive metastore) |
| Custom upsert/merge | Delta MERGE |
| Bootstrap scripts | Cluster init scripts or cluster policies |
| Spot instances | Same (configure in cluster policy) |
