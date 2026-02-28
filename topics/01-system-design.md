# Topic 1: System Design & Architecture for Data Platforms

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Design scalable data platforms from scratch
- Choose between data lakes, warehouses, and lakehouses
- Map data volumes and data types (structured/semi/unstructured) to storage and processing choices
- Decide when to use single-cloud vs multi-cloud and when to apply Medallion vs Lambda
- Handle petabyte-scale data efficiently
- Implement data quality measures at scale
- Explain trade-offs in architectural decisions using simple flow diagrams and examples

---

## 📖 Core Concepts

### 1. Scalability Fundamentals

#### Horizontal Scaling (Scale-Out)
- **What**: Add more machines/nodes
- **Pros**: No hardware limits, cost-effective
- **Cons**: Network overhead, data distribution complexity
- **Example**: Adding more Spark workers, Redshift nodes

#### Vertical Scaling (Scale-Up)
- **What**: Increase resources on existing machine
- **Pros**: Simpler, no data distribution needed
- **Cons**: Hardware limits, expensive
- **Example**: Upgrading EC2 instance size

**For Data Engineering**: Always prefer horizontal scaling for data platforms.

---

### 2. Data Storage Architectures

#### Data Lake
**Definition**: Centralized repository storing raw data in native format

**Characteristics**:
- Schema-on-read (schema applied when querying)
- Stores structured, semi-structured, unstructured data
- Cost-effective storage (S3, HDFS)
- Flexible but requires processing

**Use Cases**:
- Raw data ingestion
- Data exploration
- ML/AI workloads
- Long-term archival

**Example**: AWS S3 with Parquet files

```python
# Data Lake Structure
s3://data-lake/
  ├── raw/
  │   ├── events/
  │   │   ├── year=2024/
  │   │   │   ├── month=01/
  │   │   │   │   ├── day=15/
  │   │   │   │   │   └── events_20240115.parquet
  │   ├── users/
  │   └── transactions/
  ├── processed/
  └── curated/
```

#### Data Warehouse
**Definition**: Centralized repository of structured, processed data

**Characteristics**:
- Schema-on-write (schema enforced on ingestion)
- Optimized for SQL queries
- Columnar storage (faster analytics)
- More expensive storage

**Use Cases**:
- Business intelligence
- Reporting
- Analytics dashboards
- Ad-hoc queries

**Example**: AWS Redshift, Snowflake, BigQuery

#### Data Lakehouse
**Definition**: Hybrid combining lake flexibility with warehouse performance

**Characteristics**:
- Open table formats (Delta Lake, Iceberg, Hudi)
- ACID transactions
- Schema evolution
- Both batch and streaming

**Example**: Databricks Delta Lake, Apache Iceberg

---

### 3. Partitioning Strategies

#### Why Partition?
- **Performance**: Query only relevant partitions
- **Cost**: Reduce data scanned
- **Maintenance**: Easier to manage/delete old data

#### Partition Types:

**1. Time-Based Partitioning** (Most Common)
```
s3://data/events/year=2024/month=01/day=15/hour=10/
```
- **Pros**: Natural for time-series data, easy to prune
- **Cons**: Can create too many small files

**2. Hash-Based Partitioning**
```
s3://data/users/user_id_hash=abc123/
```
- **Pros**: Even distribution, good for lookups
- **Cons**: Hard to prune by time

**3. Range Partitioning**
```
s3://data/transactions/amount_range=0-1000/
```
- **Pros**: Good for range queries
- **Cons**: Can create hot partitions

**Best Practice**: Combine time + hash for gaming data
```
s3://data/game_events/
  year=2024/month=01/day=15/
    player_id_hash=abc/
      events.parquet
```

---

### 4. Handling Petabyte-Scale Data

#### Key Principles:

**1. Distributed Processing**
- Use Spark, Flink, or similar
- Process data in parallel across nodes
- Example: Spark on EMR, Databricks

**2. Columnar Storage**
- Parquet, ORC formats
- Column compression
- Only read needed columns

**3. Incremental Processing**
- Process only new/changed data
- Avoid full table scans
- Use change data capture (CDC)

**4. Caching Strategy**
- Cache frequently accessed data
- Use Spark caching, Redis
- Materialized views in warehouse

**5. Data Lifecycle Management**
- Hot data: Fast storage (SSD)
- Warm data: Standard storage (S3)
- Cold data: Glacier/archive storage
- Delete old data based on retention policy

---

### 5. Data Quality at Scale

#### Quality Dimensions:

**1. Completeness**
- Are all expected records present?
- Check: Count validation, null checks

**2. Accuracy**
- Is data correct?
- Check: Range validation, format checks

**3. Consistency**
- Is data consistent across sources?
- Check: Cross-table validation

**4. Timeliness**
- Is data arriving on time?
- Check: SLA monitoring, latency alerts

**5. Validity**
- Does data conform to schema?
- Check: Schema validation, type checks

#### Implementation Strategies:

**1. Schema Validation**
```python
from pydantic import BaseModel, validator

class GameEvent(BaseModel):
    event_id: str
    player_id: str
    timestamp: datetime
    event_type: str
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed = ['login', 'purchase', 'level_complete']
        if v not in allowed:
            raise ValueError(f'Invalid event_type: {v}')
        return v
```

**2. Data Quality Checks**
```python
# Using Great Expectations
expectation_suite = {
    "expect_table_row_count_to_be_between": [1000, 10000],
    "expect_column_values_to_not_be_null": ["player_id"],
    "expect_column_values_to_be_in_set": {
        "column": "event_type",
        "value_set": ["login", "purchase", "level_complete"]
    }
}
```

**3. Monitoring & Alerting**
- Set up data quality dashboards
- Alert on anomalies (sudden drops, spikes)
- Track data quality metrics over time

---

## 🏗️ Design Patterns

### Pattern 1: Lambda Architecture
**Components**:
- **Batch Layer**: Processes all data (accurate but slow)
- **Speed Layer**: Processes recent data (fast but approximate)
- **Serving Layer**: Combines both views

**Use Case**: Real-time analytics with historical accuracy

### Pattern 2: Kappa Architecture
**Components**:
- Single stream processing pipeline
- Replay events for reprocessing
- Simpler than Lambda

**Use Case**: When batch and real-time logic are similar

### Pattern 3: Medallion Architecture (Bronze/Silver/Gold)
**Components**:
- **Bronze**: Raw data (data lake)
- **Silver**: Cleaned, validated data
- **Gold**: Business-level aggregates

**Use Case**: Modern data lakehouse approach

---

## 🔧 Data Engineering System Design (Practical Frame)

A compact frame for designing data systems: **modeling**, **volumes**, **data types**, **cloud choice**, and **when to use which design**. Use this to scope a solution before diving into a specific cloud or tool.

### 1. Data Volumes → Design Fit

| Volume (approx) | Design focus | Typical choices |
|-----------------|--------------|------------------|
| **Small (&lt; 100 GB/day)** | Single pipeline, minimal ops | Serverless (Glue, Lambda), Athena or single-warehouse (Redshift/BigQuery), one cloud |
| **Medium (100 GB – 1 TB/day)** | Partitioning, incremental processing | Medallion on S3/ADLS/GCS; Spark (EMR/Databricks) for transforms; warehouse for BI |
| **Large (&gt; 1 TB/day)** | Distributed, scalable ingest + process | Streaming (Kinesis/Kafka) + batch; multiple workers; consider multi-region and lifecycle policies |

**Takeaway**: Scale drives whether you need streaming, how many workers, and how strict partitioning and lifecycle must be.

---

### 2. Types of Data → Where It Goes

| Type | Examples | Storage | Processing |
|------|----------|---------|------------|
| **Structured** | DB tables, CSV, fixed schema | Warehouse, or lake (Parquet/Delta) | ETL, CDC, SQL |
| **Semi-structured** | JSON, XML, logs | Data lake (object store) | Schema-on-read, Spark/Glue |
| **Unstructured** | Images, PDFs, audio | Object store (S3, Blob, GCS) | ML pipelines, search, minimal “schema” |

**Modeling note**: For analytics, structured and semi-structured usually land in **star/snowflake** or **one-big-table** in the gold layer (see Topic 2: Data Modeling). Bronze/silver stay closer to source shape; gold is modeled for consumption.

---

### 3. Cloud and Design Choices

| Scenario | Prefer | Why |
|----------|--------|-----|
| **Single org, one cloud** | One cloud (AWS, GCP, or Azure) | Simpler, fewer moving parts, native integrations |
| **Compliance / data residency** | Region-specific or sovereign cloud | Keep data in required geography |
| **Multi-org or post-merger** | Multi-cloud or hybrid | Different teams/contracts; gradual migration |
| **Best “default” design** | **Medallion (Bronze/Silver/Gold)** on object store + optional warehouse | Clear layers, schema evolution, batch + streaming possible |

**When to add Lambda (batch + speed layer)**:
- You need **real-time** views and **historically correct** batch views and can maintain two code paths. Otherwise prefer **Kappa** (single stream) or **batch + materialized views**.

---

### 4. Sample Examples (Small Flows)

**Example A: Retail — batch files + streaming events**

- **Data**: Batch sales files (CSV/Parquet) daily; real-time click/order events (Kafka or Kinesis). Volume ~500 GB/day.
- **Modeling**: Gold = star (sales fact, product/customer/store dims); silver = cleaned, deduplicated events and batch loads.

```
  Batch files          Streaming events
       │                      │
       ▼                      ▼
  ┌─────────┐            ┌──────────┐
  │  S3 /   │            │ Kinesis │
  │  inbox  │            │ Kafka   │
  └────┬────┘            └────┬────┘
       │                      │
       ▼                      ▼
  ┌────────────────────────────────┐
  │  Object store (Bronze)          │
  │  Partitioned by date            │
  └────────────┬───────────────────┘
               ▼
  ┌────────────────────────────────┐
  │  Spark / Glue / Databricks     │
  │  Silver: clean, dedupe, join    │
  └────────────┬───────────────────┘
               ▼
  ┌────────────────────────────────┐
  │  Gold: star schema / aggregates │
  │  → Warehouse or Athena/Delta    │
  └────────────────────────────────┘
```

**Example B: Single-cloud analytics (Medallion)**

- **Data**: Mix of DB dumps (structured) and app logs (JSON). One cloud (e.g. AWS). Volume ~200 GB/day.
- **Design**: Medallion on S3; Glue or Databricks for ETL; Athena or Redshift for SQL; optional Glue Catalog.

```
  DB (CDC/dump)    App logs (JSON)
       │                 │
       ▼                 ▼
  ┌─────────────────────────────┐
  │  Bronze (raw, partitioned)   │  ← S3
  └─────────────┬───────────────┘
                ▼
  ┌─────────────────────────────┐
  │  Silver (typed, validated)   │  ← Parquet/Delta
  └─────────────┬───────────────┘
                ▼
  ┌─────────────────────────────┐
  │  Gold (star / aggregates)     │  ← Delta or warehouse
  └─────────────┬───────────────┘
                ▼
  ┌─────────────┴─────────────┐
  │  Athena / Redshift / BI   │
  └──────────────────────────┘
```

**Example C: Governed lake, multiple consumers**

- **Data**: Sensitive (e.g. PII). Need access control and audit. Same medallion layout; access via IAM/Lake Formation or Unity Catalog.
- **Flow**: Same as B, plus encryption (SSE-KMS), table/column-level permissions, and audit logs (CloudTrail / equivalent). No extra diagram—same flow, add governance layer.

---

### 5. Quick Checklist for Data Engineering System Design

- **Volume**: Order of magnitude (GB vs TB/day) → drives serverless vs. cluster, and streaming vs. batch.
- **Data types**: Structured vs. semi vs. unstructured → storage format and schema-on-read vs -write.
- **Modeling**: Gold layer = star/snowflake or OBT for analytics (Topic 2); bronze/silver = source-aligned and cleaned.
- **Cloud**: Single cloud first; multi-cloud only if needed (compliance, org boundaries).
- **Pattern**: Prefer Medallion; add Lambda only if you need both real-time and batch-correct views and accept two pipelines.
- **Governance**: Encryption, access control, and audit when data is sensitive or regulated.

---

## 💡 Interview Questions & Answers

### Q1: Design a data platform for a gaming company processing 1TB/day

**Answer Structure**:

1. **Requirements**:
   - 1TB/day ingestion
   - Real-time analytics (last hour)
   - Historical analysis (2+ years)
   - Multiple data sources (game events, user data, transactions)

2. **Architecture**:
   ```
   Data Sources → Kinesis/Kafka → Processing → Storage
                    ↓
              Real-time Analytics (Elasticsearch)
                    ↓
              Batch Processing (Spark) → Data Lake (S3)
                    ↓
              ETL → Data Warehouse (Redshift)
                    ↓
              BI Tools (Tableau, Looker)
   ```

3. **Components**:
   - **Ingestion**: Kinesis Data Streams (real-time), S3 (batch)
   - **Processing**: Kinesis Analytics (real-time), EMR Spark (batch)
   - **Storage**: S3 (data lake), Redshift (warehouse)
   - **Partitioning**: Time-based (year/month/day/hour)
   - **Data Quality**: Great Expectations, DataDog monitoring

4. **Scalability**:
   - Horizontal scaling: Add Kinesis shards, Spark workers
   - Auto-scaling based on load
   - Partition data to avoid hot spots

---

### Q2: How do you ensure data quality in a real-time pipeline?

**Answer**:

1. **Schema Validation**: Validate on ingestion (JSON schema, Avro)
2. **Anomaly Detection**: Monitor metrics (count, nulls, duplicates)
3. **Data Quality Checks**: 
   - Completeness: Expected record count
   - Accuracy: Range checks, format validation
   - Timeliness: Latency monitoring
4. **Alerting**: Set thresholds, alert on violations
5. **Dead Letter Queue**: Route bad data for investigation
6. **Monitoring Dashboard**: Track quality metrics over time

---

## 📝 Practice Exercises

### Exercise 1: Design a Data Lake Structure
Design the S3 structure for:
- Game events (1B events/day)
- User profiles (100M users)
- Transaction data (10M transactions/day)
- Need to support queries by: date, game_id, player_id

**Solution Approach**:
```
s3://gaming-data-lake/
  ├── raw/
  │   ├── events/
  │   │   └── year=2024/month=01/day=15/game_id=123/
  │   ├── users/
  │   │   └── year=2024/month=01/day=15/
  │   └── transactions/
  │       └── year=2024/month=01/day=15/
  ├── processed/
  │   └── events_aggregated/
  │       └── year=2024/month=01/day=15/
  └── curated/
      └── player_analytics/
          └── year=2024/month=01/day=15/
```

---

## ✅ Check Your Understanding

1. **What's the difference between a data lake and data warehouse?**
2. **When would you use time-based vs hash-based partitioning?**
3. **How do you handle a sudden 10x increase in data volume?**
4. **What are the key data quality dimensions?**
5. **Explain the Medallion architecture pattern.**

---

## 🎯 Next Steps

Once you're comfortable with this topic, we'll move to:
- **Topic 2: Data Modeling** (Normalization, Star Schema, SCD Types)

**Study Time**: Spend 2-3 days on this topic, then let me know when you're ready to move on!

---

## 📚 Additional Resources

- [AWS Data Lake Architecture](https://aws.amazon.com/solutions/implementations/data-lake-foundation/)
- [Designing Data-Intensive Applications - Chapter 1-3](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/)
- [Delta Lake Documentation](https://delta.io/)
