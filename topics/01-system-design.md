# Topic 1: System Design & Architecture for Data Platforms

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Design scalable data platforms from scratch
- Choose between data lakes, warehouses, and lakehouses
- Handle petabyte-scale data efficiently
- Implement data quality measures at scale
- Explain trade-offs in architectural decisions

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
