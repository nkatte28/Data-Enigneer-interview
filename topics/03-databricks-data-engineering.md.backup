# Topic 3: Databricks Data Engineering - Complete Guide

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Understand Databricks architecture and workflows
- Master Delta Lake concepts (ACID, time travel, optimization)
- Design and implement Delta Live Tables (DLT)
- Build real-time pipelines with Spark Structured Streaming
- Optimize Spark jobs for performance and cost
- Implement data governance with Unity Catalog
- Connect to multiple data sources (Snowflake, Iceberg, etc.)
- Design multi-cloud data architectures
- Protect PII data and optimize costs

---

## 📖 Core Concepts

### 1. Databricks Overview & Architecture

**What is Databricks?**
Databricks is a unified analytics platform built on Apache Spark, designed for data engineering, data science, and analytics.

**Key Components**:
- **Workspace**: Web-based interface for notebooks, jobs, and collaboration
- **Clusters**: Compute resources (can be shared or single-user)
- **Jobs**: Scheduled or triggered Spark applications
- **Notebooks**: Interactive coding environment (Python, Scala, SQL, R)
- **DBFS**: Databricks File System (distributed file system)
- **Unity Catalog**: Centralized data governance

#### 1.1 Cluster Types

**Two Types of Clusters**:

**1. All-Purpose Clusters**:
- ✅ For interactive development (notebooks)
- ✅ Shared by multiple users
- ✅ Stays running until manually terminated
- ✅ Use for: Development, ad-hoc queries, exploration

**Example**:
```python
# Create all-purpose cluster (via UI or API)
# Good for: Interactive notebooks, development
```

**2. Job Clusters**:
- ✅ For scheduled/automated jobs
- ✅ Single-user (one job at a time)
- ✅ Terminates automatically after job completes
- ✅ Use for: Production pipelines, scheduled jobs

**Example**:
```json
{
  "new_cluster": {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 2,
    "autotermination_minutes": 0  // Terminates after job
  }
}
```

**When to Use Each**:
- **All-Purpose**: Development, testing, exploration
- **Job Clusters**: Production workflows, scheduled jobs (cost-effective!)

**Nike Store Example - Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Data Sources                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   S3     │  │  Kafka   │  │ Databases │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Databricks Workspace       │
        │  ┌────────────────────────┐  │
        │  │  Unity Catalog         │  │ ← Governance Foundation
        │  │  (catalog.schema.table)│  │
        │  └───────────┬────────────┘  │
        │              ↓                │
        │  ┌────────────────────────┐  │
        │  │  Delta Lake            │  │
        │  │  (Bronze/Silver/Gold)  │  │
        │  └───────────┬────────────┘  │
        │              ↓                │
        │  ┌────────────────────────┐  │
        │  │  DLT Pipelines          │  │
        │  │  (Data Quality Checks)  │  │
        │  └───────────┬────────────┘  │
        │              ↓                │
        │  ┌────────────────────────┐  │
        │  │  Spark Clusters         │  │
        │  │  (Compute)              │  │
        │  └────────────────────────┘  │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Analytics & ML          │
        │  ┌──────────┐  ┌──────────┐ │
        │  │ BI Tools │  │ ML Models │ │
        │  └──────────┘  └──────────┘ │
        └──────────────────────────────┘
```

**Key Flow**:
1. **Data Ingestion**: Raw data from S3, Kafka, databases
2. **Unity Catalog**: Register and govern all data assets
3. **Delta Lake**: Store data in Bronze/Silver/Gold layers
4. **DLT**: Build reliable pipelines with quality checks
5. **Processing**: Spark clusters process the data
6. **Analytics**: BI tools and ML models consume data

---

### 2. Understanding Your Data: Sample Raw Data

**Before we start coding, let's see what we're working with!**

**Sample Raw Sales Data (JSON from S3)**:
```json
{
  "sale_id": "SALE-001",
  "customer_id": 101,
  "product_id": 501,
  "product_name": "Air Max 270",
  "amount": 150.00,
  "quantity": 2,
  "sale_date": "2024-01-15T10:30:00Z",
  "store_id": 1,
  "discount": 0.0
}
```

**Sample Raw Customer Data**:
```json
{
  "customer_id": 101,
  "name": "Sarah Johnson",
  "email": "sarah.johnson@email.com",
  "phone": "555-1234",
  "city": "New York",
  "registration_date": "2020-01-15"
}
```

**What We're Trying to Achieve**:
1. Ingest raw data → Bronze layer (as-is)
2. Clean and validate → Silver layer (quality checked)
3. Aggregate and enrich → Gold layer (business-ready)

---

### 3. Delta Lake Fundamentals

**Delta Lake**: Open-source storage layer that brings ACID transactions to data lakes.

#### 3.1 What Makes Delta Lake Special?

**Key Features**:
- ✅ **ACID Transactions**: Ensures data consistency
- ✅ **Time Travel**: Query historical versions
- ✅ **Schema Evolution**: Add columns without breaking existing data
- ✅ **Upserts**: Update and insert in one operation
- ✅ **Optimization**: Z-order, compaction, partitioning

**Why Delta Lake? - Real Example**:

**Problem with Parquet**:
```python
# Parquet: Can't update, no transactions
sales.write.format("parquet").mode("overwrite").save("/data/sales")
# If job fails halfway, data is corrupted! ❌
```

**Solution with Delta Lake**:
```python
# Delta: ACID transactions, can update
sales.write.format("delta").mode("overwrite").save("/mnt/delta/sales")
# If job fails, previous version is intact! ✅
```

#### 3.2 Creating Delta Tables - Step by Step

**What We're Doing**: Convert raw JSON data into a Delta table.

**Sample Raw Data** (from S3 `s3://nike-raw/sales/2024-01-15.json`):
```json
[
  {"sale_id": "SALE-001", "customer_id": 101, "product_id": 501, "amount": 150.00, "sale_date": "2024-01-15"},
  {"sale_id": "SALE-002", "customer_id": 102, "product_id": 502, "amount": 200.00, "sale_date": "2024-01-15"}
]
```

**Step 1: Read Raw Data**:
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("DeltaExample").getOrCreate()

# Read JSON from S3
raw_sales = spark.read.format("json").load("s3://nike-raw/sales/")
raw_sales.show()
```

**Output**:
```
+----------+-----------+----------+------+----------+
|sale_id   |customer_id|product_id|amount|sale_date |
+----------+-----------+----------+------+----------+
|SALE-001  |101        |501       |150.00|2024-01-15|
|SALE-002  |102        |502       |200.00|2024-01-15|
+----------+-----------+----------+------+----------+
```

**Step 2: Write as Delta Table**:
```python
# Write to Delta Lake (Bronze layer)
raw_sales.write.format("delta") \
    .mode("overwrite") \
    .save("/mnt/delta/bronze/sales")

# Read back from Delta
sales = spark.read.format("delta").load("/mnt/delta/bronze/sales")
sales.show()
```

**What Happened?**
- ✅ Data written to `/mnt/delta/bronze/sales/`
- ✅ Transaction log created (`_delta_log/`)
- ✅ Can now update, delete, time travel!

#### 3.3 Delta Lake Operations with Examples

**Operation 1: Insert (Append New Data)**

**What We're Doing**: Add new sales records without overwriting existing data.

**Use Cases**:
- ✅ Daily batch ingestion (new sales each day)
- ✅ Streaming data (append new events)
- ✅ Incremental loads (only new data)

**Example 1: Daily Batch Append**

**Scenario**: Every day, new sales data arrives. We want to add it to existing data.

**Existing Data**:
```
sale_id   | customer_id | amount | sale_date
SALE-001  | 101         | 150.00 | 2024-01-15
SALE-002  | 102         | 200.00 | 2024-01-15
```

**New Data to Add** (today's sales):
```python
new_sales = spark.createDataFrame([
    ("SALE-003", 103, 503, 120.00, "2024-01-16"),
    ("SALE-004", 101, 501, 150.00, "2024-01-16")
], ["sale_id", "customer_id", "product_id", "amount", "sale_date"])

# Append to existing Delta table
new_sales.write.format("delta") \
    .mode("append") \
    .save("/mnt/delta/bronze/sales")

# Verify: Should have 4 records now
spark.read.format("delta").load("/mnt/delta/bronze/sales").count()
# Output: 4
```

**Result**:
```
sale_id   | customer_id | amount | sale_date
SALE-001  | 101         | 150.00 | 2024-01-15  ← Existing
SALE-002  | 102         | 200.00 | 2024-01-15  ← Existing
SALE-003  | 103         | 120.00 | 2024-01-16  ← Appended!
SALE-004  | 101         | 150.00 | 2024-01-16  ← Appended!
```

**Example 2: Streaming Append**

**Scenario**: Real-time sales events from Kafka, append as they arrive.

```python
# Stream from Kafka and append to Delta
sales_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "nike-sales") \
    .load()

# Parse and append
parsed_stream = sales_stream.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Append mode (only new rows)
parsed_stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/mnt/delta/checkpoints/sales") \
    .start("/mnt/delta/bronze/sales")
```

**Example 3: Partitioned Append**

**Scenario**: Append data to specific partitions (faster queries).

```python
# Append with partitioning
new_sales.write.format("delta") \
    .mode("append") \
    .partitionBy("sale_date") \
    .save("/mnt/delta/bronze/sales")

# Benefits:
# - Faster queries (only read relevant partitions)
# - Easier data management (delete old partitions)
```

**Best Practices for Append**:
- ✅ Use partitioning for large tables
- ✅ Validate data before appending (schema, constraints)
- ✅ Monitor append performance (many small appends = slow)
- ✅ Batch small appends together when possible

**Operation 2: Update Existing Records**

**What We're Doing**: Fix a mistake - customer 101 got a 10% discount we forgot to apply.

**Before Update**:
```
+----------+-----------+----------+------+
|sale_id   |customer_id|amount   |
+----------+-----------+----------+
|SALE-001  |101        |150.00   |  ← Need to apply 10% discount
|SALE-004  |101        |150.00   |  ← Need to apply 10% discount
+----------+-----------+----------+
```

**Update Code**:
```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")

# Update: Apply 10% discount to customer 101
delta_table.update(
    condition="customer_id = 101",
    set={"amount": "amount * 0.9"}  # 10% discount
)

# Verify
spark.read.format("delta").load("/mnt/delta/bronze/sales") \
    .filter("customer_id = 101").show()
```

**After Update**:
```
+----------+-----------+----------+
|sale_id   |customer_id|amount   |
+----------+-----------+----------+
|SALE-001  |101        |135.00   |  ← Updated!
|SALE-004  |101        |135.00   |  ← Updated!
+----------+-----------+----------+
```

**Operation 3: Upsert (Merge) - Most Important!**

**What We're Doing**: Update existing records if they exist, insert if they don't.

**Use Cases**:
- ✅ Change Data Capture (CDC) - sync changes from source
- ✅ Idempotent writes - safe to rerun
- ✅ Slowly Changing Dimensions (SCD Type 1)
- ✅ Deduplication - update duplicates

**Use Case 1: Basic Upsert (Update or Insert)**

**Scenario**: We receive updated sales data. Some sales already exist (update), some are new (insert).

**Existing Data**:
```
sale_id   | customer_id | amount | sale_date
SALE-001  | 101         | 135.00 | 2024-01-15
SALE-002  | 102         | 200.00 | 2024-01-15
```

**New/Updated Data**:
```python
updates_df = spark.createDataFrame([
    ("SALE-001", 101, 140.00, "2024-01-15"),  # Updated amount
    ("SALE-003", 103, 120.00, "2024-01-16")   # New sale
], ["sale_id", "customer_id", "amount", "sale_date"])
```

**Basic Merge Code**:
```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")

# Merge: Update if exists, insert if new
delta_table.alias("target").merge(
    updates_df.alias("source"),
    "target.sale_id = source.sale_id"  # Match on sale_id
).whenMatchedUpdateAll() \    # If match found → update all columns
 .whenNotMatchedInsertAll() \  # If no match → insert all columns
 .execute()
```

**Result**:
```
sale_id   | customer_id | amount | sale_date
SALE-001  | 101         | 140.00 | 2024-01-15  ← Updated!
SALE-002  | 102         | 200.00 | 2024-01-15  ← Unchanged
SALE-003  | 103         | 120.00 | 2024-01-16  ← Inserted!
```

**Use Case 2: Conditional Merge (Update Only If Changed)**

**Scenario**: Only update if values actually changed (avoid unnecessary writes).

**Existing Data**:
```
sale_id   | customer_id | amount | last_updated
SALE-001  | 101         | 140.00 | 2024-01-15 10:00:00
```

**New Data**:
```python
updates_df = spark.createDataFrame([
    ("SALE-001", 101, 140.00, "2024-01-15 11:00:00"),  # Same amount, new timestamp
    ("SALE-002", 102, 250.00, "2024-01-15 11:00:00")   # New sale
], ["sale_id", "customer_id", "amount", "last_updated"])
```

**Conditional Merge**:
```python
delta_table.alias("target").merge(
    updates_df.alias("source"),
    "target.sale_id = source.sale_id"
).whenMatchedUpdate(
    condition="target.amount != source.amount",  # Only update if amount changed
    set={
        "amount": "source.amount",
        "last_updated": "source.last_updated"
    }
).whenNotMatchedInsertAll() \
 .execute()
```

**Result**:
```
sale_id   | customer_id | amount | last_updated
SALE-001  | 101         | 140.00 | 2024-01-15 10:00:00  ← Not updated (amount same)
SALE-002  | 102         | 250.00 | 2024-01-15 11:00:00  ← Inserted!
```

**Use Case 3: Selective Column Updates**

**Scenario**: Update only specific columns, keep others unchanged.

**Existing Data**:
```
sale_id   | customer_id | amount | discount | sale_date
SALE-001  | 101         | 150.00 | 0.0      | 2024-01-15
```

**New Data** (only discount changed):
```python
updates_df = spark.createDataFrame([
    ("SALE-001", 101, 150.00, 10.0, "2024-01-15")  # Only discount changed
], ["sale_id", "customer_id", "amount", "discount", "sale_date"])
```

**Selective Update**:
```python
delta_table.alias("target").merge(
    updates_df.alias("source"),
    "target.sale_id = source.sale_id"
).whenMatchedUpdate(
    set={
        "discount": "source.discount"  # Only update discount
        # amount and sale_date stay unchanged
    }
).whenNotMatchedInsertAll() \
 .execute()
```

**Result**:
```
sale_id   | customer_id | amount | discount | sale_date
SALE-001  | 101         | 150.00 | 10.0     | 2024-01-15  ← Only discount updated!
```

**Use Case 4: Merge with Delete (Soft Delete)**

**Scenario**: Mark records as deleted instead of actually deleting them.

**Existing Data**:
```
sale_id   | customer_id | amount | is_deleted
SALE-001  | 101         | 150.00 | false
SALE-002  | 102         | 200.00 | false
```

**Delete Request**:
```python
deletes_df = spark.createDataFrame([
    ("SALE-001",)  # Sale to delete
], ["sale_id"])
```

**Soft Delete Merge**:
```python
delta_table.alias("target").merge(
    deletes_df.alias("source"),
    "target.sale_id = source.sale_id"
).whenMatchedUpdate(
    set={"is_deleted": "true"}  # Mark as deleted
).execute()
```

**Result**:
```
sale_id   | customer_id | amount | is_deleted
SALE-001  | 101         | 150.00 | true   ← Soft deleted!
SALE-002  | 102         | 200.00 | false
```

**Use Case 5: Deduplication with Merge**

**Scenario**: Remove duplicates, keep the latest record.

**Problem Data** (duplicates):
```
sale_id   | customer_id | amount | ingestion_time
SALE-001  | 101         | 150.00 | 2024-01-15 10:00:00
SALE-001  | 101         | 150.00 | 2024-01-15 11:00:00  ← Duplicate!
SALE-001  | 101         | 150.00 | 2024-01-15 12:00:00  ← Duplicate!
```

**Deduplication Merge**:
```python
# Group by sale_id, keep latest
deduplicated = updates_df.groupBy("sale_id") \
    .agg(
        max("ingestion_time").alias("latest_time"),
        first("customer_id").alias("customer_id"),
        first("amount").alias("amount")
    )

delta_table.alias("target").merge(
    deduplicated.alias("source"),
    "target.sale_id = source.sale_id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

**Best Practices for Merge**:
- ✅ Use specific match conditions (avoid full table scans)
- ✅ Use conditional updates (only update if changed)
- ✅ Index/partition on merge keys for performance
- ✅ Test merge logic on sample data first
- ✅ Monitor merge performance (can be slow on large tables)

**Operation 4: Delete**

**What We're Doing**: Remove old sales data (older than 2 years).

**Use Cases**:
- ✅ Data retention policies (delete old data)
- ✅ Remove bad data
- ✅ Cleanup after testing

**Example 1: Delete by Condition**:
```python
# Delete sales older than 2 years
delta_table.delete("sale_date < '2022-01-01'")
```

**Example 2: Delete Specific Records**:
```python
# Delete specific sale
delta_table.delete("sale_id = 'SALE-001'")
```

**Example 3: Delete in Merge**:
```python
# Delete records that exist in source
delta_table.alias("target").merge(
    deletes_df.alias("source"),
    "target.sale_id = source.sale_id"
).whenMatchedDelete() \  # Delete matched records
 .execute()
```

---

### 3.4 Change Data Feed (CDF) - Track All Changes

**What is Change Data Feed?**
Tracks all changes (inserts, updates, deletes) to a Delta table. Like an audit log!

**Why CDF?**
- ✅ CDC (Change Data Capture) - sync changes to downstream systems
- ✅ Audit trail - see what changed and when
- ✅ Incremental processing - only process changed records
- ✅ Data replication - sync to other systems

#### 3.4.1 Enable Change Data Feed

**Enable CDF on Table**:
```python
# Enable CDF when creating table
spark.sql("""
    CREATE TABLE bronze.sales (
        sale_id BIGINT,
        customer_id BIGINT,
        amount DECIMAL(10,2),
        sale_date DATE
    ) USING DELTA
    LOCATION '/mnt/delta/bronze/sales'
    TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
```

**Enable CDF on Existing Table**:
```python
# Enable on existing table
spark.sql("""
    ALTER TABLE delta.`/mnt/delta/bronze/sales`
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
```

#### 3.4.2 Reading Change Data Feed

**What We're Doing**: See all changes made to the table.

**Sample Operations**:
1. Inserted: SALE-003
2. Updated: SALE-001 (amount changed)
3. Deleted: SALE-002

**Read CDF**:
```python
# Read all changes since version 0
changes_df = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 0) \
    .load("/mnt/delta/bronze/sales")

changes_df.show()
```

**Output**:
```
+----+----------+-----------+----------+------+----------+------------------+
|_change_type|sale_id    |customer_id|amount |sale_date |_commit_version   |
+----+----------+-----------+----------+------+----------+------------------+
|insert      |SALE-003   |103        |120.00 |2024-01-16|5                 |
|update_preimage|SALE-001|101        |150.00 |2024-01-15|6                 |  ← Old value
|update_postimage|SALE-001|101       |140.00 |2024-01-15|6                 |  ← New value
|delete      |SALE-002   |102        |200.00 |2024-01-15|7                 |
+----+----------+-----------+----------+------+----------+------------------+
```

**CDF Columns**:
- `_change_type`: `insert`, `update_preimage`, `update_postimage`, `delete`
- `_commit_version`: Version when change occurred
- `_commit_timestamp`: When change occurred

#### 3.4.3 Use Case 1: Incremental Processing

**What We're Doing**: Only process records that changed, not the entire table.

**Scenario**: Daily pipeline. Yesterday processed 1M records. Today only 10K records changed.

**Without CDF** (Slow):
```python
# Process ALL 1,010,000 records every day!
silver = spark.read.format("delta").load("/mnt/delta/bronze/sales")
```

**With CDF** (Fast):
```python
# Only process changed records (10K)
changes = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", last_processed_version) \
    .load("/mnt/delta/bronze/sales")

# Filter only inserts and updates
new_and_updated = changes.filter(
    col("_change_type").isin("insert", "update_postimage")
)

# Process only changed records
silver = new_and_updated.select(
    col("sale_id"),
    col("customer_id"),
    col("amount")
)
```

**Performance**:
- Without CDF: Process 1M records → 10 minutes
- With CDF: Process 10K records → 1 minute ✅

#### 3.4.4 Use Case 2: Sync to Downstream System

**What We're Doing**: Sync changes from Delta Lake to another system (e.g., Snowflake, Redshift).

**Scenario**: Delta Lake is source of truth. Need to sync changes to Snowflake.

**CDF Sync Pipeline**:
```python
# Read changes since last sync
changes = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", last_synced_version) \
    .load("/mnt/delta/bronze/sales")

# Handle inserts
inserts = changes.filter(col("_change_type") == "insert")
inserts.write.format("snowflake") \
    .option("dbtable", "sales") \
    .mode("append") \
    .save()

# Handle updates
updates = changes.filter(col("_change_type") == "update_postimage")
updates.write.format("snowflake") \
    .option("dbtable", "sales") \
    .mode("overwrite") \
    .save()

# Handle deletes
deletes = changes.filter(col("_change_type") == "delete")
# Delete from Snowflake using merge or delete statement
```

#### 3.4.5 Use Case 3: Audit Trail

**What We're Doing**: Track who changed what and when.

**Audit Query**:
```python
# See all changes with timestamps
audit_trail = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 0) \
    .load("/mnt/delta/bronze/sales")

# Who changed sale_id = 'SALE-001'?
audit_trail.filter("sale_id = 'SALE-001'") \
    .select("_change_type", "amount", "_commit_version", "_commit_timestamp") \
    .orderBy("_commit_version") \
    .show()
```

**Output**:
```
+----+----------+------+----------------+-------------------+
|_change_type|amount|_commit_version|_commit_timestamp   |
+----+----------+------+----------------+-------------------+
|insert      |150.00|1              |2024-01-15 10:00:00|  ← Created
|update_postimage|140.00|6          |2024-01-16 11:00:00|  ← Updated
|update_postimage|135.00|8          |2024-01-16 15:00:00|  ← Updated again
+----+----------+------+----------------+-------------------+
```

#### 3.4.6 Use Case 4: Real-Time Change Streaming

**What We're Doing**: Stream changes in real-time to downstream systems.

**Stream CDF Changes**:
```python
# Stream changes as they happen
changes_stream = spark.readStream \
    .format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", latest_version) \
    .load("/mnt/delta/bronze/sales")

# Process changes
changes_stream.writeStream \
    .format("kafka") \
    .option("topic", "sales-changes") \
    .option("checkpointLocation", "/mnt/delta/checkpoints/cdf") \
    .start()
```

**Best Practices for CDF**:
- ✅ Enable CDF on tables that need change tracking
- ✅ Use CDF for incremental processing (much faster!)
- ✅ Monitor CDF storage (adds some overhead)
- ✅ Clean up old CDF data periodically
- ✅ Use version ranges for efficient reads

---

### 4. Delta Lake Advanced Features

#### 4.1 Time Travel - See Your Data History

**What We're Doing**: Query what your data looked like at any point in time.

**Real Scenario**: Yesterday, someone accidentally updated all sales amounts. Today, you need to see what the data looked like before that mistake.

**Step 1: Check History**:
```python
# See all versions of the table
spark.sql("DESCRIBE HISTORY delta.`/mnt/delta/bronze/sales`").show()
```

**Output**:
```
+-------+-------------------+--------+--------+------------------+
|version|timestamp          |operation|operationMetrics|
+-------+-------------------+--------+--------+------------------+
|5      |2024-01-16 10:00:00|UPDATE  |{"numUpdatedRows":100}|
|4      |2024-01-15 15:00:00|MERGE   |{"numInsertedRows":50}|
|3      |2024-01-15 10:00:00|DELETE  |{"numDeletedRows":10}|
|2      |2024-01-14 10:00:00|APPEND  |{"numFiles":5}|
|1      |2024-01-13 10:00:00|CREATE TABLE|{"numFiles":1}|
+-------+-------------------+--------+--------+------------------+
```

**Step 2: Query Historical Version**:
```python
# Read version 3 (before the UPDATE mistake)
version_3 = spark.read.format("delta") \
    .option("versionAsOf", 3) \
    .load("/mnt/delta/bronze/sales")

# Compare current vs version 3
current = spark.read.format("delta").load("/mnt/delta/bronze/sales")
print(f"Current total: ${current.agg(sum('amount')).collect()[0][0]}")
print(f"Version 3 total: ${version_3.agg(sum('amount')).collect()[0][0]}")
```

**Step 3: Restore Previous Version** (if needed):
```python
# Restore to version 3
spark.sql("""
    RESTORE TABLE delta.`/mnt/delta/bronze/sales` TO VERSION AS OF 3
""")
```

**Use Cases**:
- ✅ **Audit**: "What did sales look like last week?"
- ✅ **Debug**: "Why did this calculation change?"
- ✅ **Rollback**: "Undo that bad update"

#### 4.2 VACUUM - Clean Up Old Files

**What We're Doing**: Remove old files that are no longer needed to save storage costs.

**Why VACUUM?**
- When you UPDATE or DELETE, Delta keeps old files for time travel
- After retention period, these files are safe to delete
- Saves storage costs!

**Example**:

**Before VACUUM**:
```
/mnt/delta/bronze/sales/
├── part-00000.parquet  (current data)
├── part-00001.parquet  (old, deleted data - 10 days old)
├── part-00002.parquet  (old, deleted data - 8 days old)
└── _delta_log/
```

**VACUUM Code**:
```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")

# VACUUM files older than 7 days (default retention)
delta_table.vacuum()

# Or with custom retention (hours)
delta_table.vacuum(168)  # 7 days = 168 hours
```

**SQL VACUUM**:
```sql
-- VACUUM files older than retention period
VACUUM delta.`/mnt/delta/bronze/sales`;

-- Dry run first (see what would be deleted)
VACUUM delta.`/mnt/delta/bronze/sales` DRY RUN;
```

**After VACUUM**:
```
/mnt/delta/bronze/sales/
├── part-00000.parquet  (current data only)
└── _delta_log/
```

**⚠️ Important**:
- Default retention: 7 days (168 hours)
- Can't time travel beyond retention period after VACUUM
- Always use `DRY RUN` first!

#### 4.3 OPTIMIZE - Make Queries Faster

**What We're Doing**: Compact many small files into fewer large files for better performance.

**Problem**: After many small writes, you have thousands of tiny files:
```
/mnt/delta/bronze/sales/
├── part-00000.parquet  (1 MB)
├── part-00001.parquet  (1 MB)
├── part-00002.parquet  (1 MB)
... (1000 files!)
```

**Why This is Bad**:
- Slow queries (reading 1000 files is slow)
- More metadata overhead
- Poor compression

**Solution: OPTIMIZE**:
```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")
delta_table.optimize().execute()
```

**SQL OPTIMIZE**:
```sql
-- Optimize entire table
OPTIMIZE delta.`/mnt/delta/bronze/sales`;

-- Optimize specific partition (faster!)
OPTIMIZE delta.`/mnt/delta/bronze/sales`
WHERE sale_date = '2024-01-15';
```

**After OPTIMIZE**:
```
/mnt/delta/bronze/sales/
├── part-00000.parquet  (128 MB)  ← Compacted!
├── part-00001.parquet  (128 MB)
├── part-00002.parquet  (128 MB)
... (only 10 files now!)
```

**Table Properties** (Advanced):
```sql
-- Set table properties for optimization
ALTER TABLE delta.`/mnt/delta/bronze/sales` 
SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.deletedFileRetentionDuration' = 'interval 7 days'
);

-- Auto-optimize writes (compact small files automatically)
-- Auto-compact: Merge small files during writes
-- Retention: How long to keep deleted files for time travel
```

**Performance Improvement**:
- Before: Query scans 1000 files → 30 seconds
- After: Query scans 10 files → 3 seconds ✅

**Z-ORDER: Multi-Dimensional Clustering**

**What We're Doing**: Organize data so related rows are in the same files.

**Example**: If you often query by `customer_id` and `sale_date`, Z-ORDER helps!

**Before Z-ORDER**:
```sql
-- Query: Get sales for customer 101 on 2024-01-15
SELECT * FROM sales 
WHERE customer_id = 101 AND sale_date = '2024-01-15';
-- Scans: 1000 files (slow!)
```

**Z-ORDER Code**:
```sql
-- Z-ORDER on columns you filter by
OPTIMIZE delta.`/mnt/delta/bronze/sales`
ZORDER BY (customer_id, sale_date);
```

**After Z-ORDER**:
```sql
-- Same query
SELECT * FROM sales 
WHERE customer_id = 101 AND sale_date = '2024-01-15';
-- Scans: 10 files (90% reduction!) ✅
```

**Best Practices**:
- ✅ Run OPTIMIZE after large writes
- ✅ Use Z-ORDER on 2-3 frequently filtered columns
- ✅ Don't Z-ORDER too many columns (diminishing returns)
- ✅ Schedule OPTIMIZE daily/weekly

#### 4.5 Liquid Clustering - Modern Clustering (Latest!)

**What is Liquid Clustering?**
A new clustering method (replacing Z-ORDER) that automatically maintains optimal data organization without manual OPTIMIZE runs.

**Why Liquid Clustering?**
- ✅ **Automatic**: No need to run OPTIMIZE manually
- ✅ **Flexible**: Can add/remove clustering columns anytime
- ✅ **Better Performance**: Optimized for modern query patterns
- ✅ **Simpler**: One-time setup, automatic maintenance

**Z-ORDER vs Liquid Clustering**:
```
Z-ORDER:
- Manual OPTIMIZE required
- Fixed clustering columns
- Can't change after creation

Liquid Clustering:
- Automatic optimization
- Can change clustering columns
- Better for evolving schemas
```

**Enable Liquid Clustering**:

**When Creating Table**:
```sql
CREATE TABLE nike_prod.sales.raw_sales (
    sale_id BIGINT,
    customer_id BIGINT,
    product_id BIGINT,
    amount DECIMAL(10,2),
    sale_date DATE
) USING DELTA
CLUSTER BY (customer_id, sale_date)  -- Liquid clustering!
LOCATION '/mnt/delta/bronze/sales';
```

**On Existing Table**:
```sql
-- Enable liquid clustering on existing table
ALTER TABLE nike_prod.sales.raw_sales
CLUSTER BY (customer_id, sale_date);
```

**What Happens?**
- ✅ Data automatically organized by clustering columns
- ✅ New writes automatically clustered
- ✅ No manual OPTIMIZE needed!
- ✅ Queries automatically benefit

**Example Query Performance**:
```sql
-- Query benefits from liquid clustering automatically
SELECT * FROM nike_prod.sales.raw_sales
WHERE customer_id = 101 AND sale_date = '2024-01-15';
-- Automatically uses clustering for fast lookup!
```

**Change Clustering Columns**:
```sql
-- Change clustering columns (flexible!)
ALTER TABLE nike_prod.sales.raw_sales
CLUSTER BY (product_id, sale_date);
```

**Best Practices**:
- ✅ Use for frequently filtered columns
- ✅ 2-4 clustering columns recommended
- ✅ Choose columns with high cardinality
- ✅ Works great with Unity Catalog tables

#### 4.4 Schema Evolution - Add Columns Safely

**What We're Doing**: Add new columns to existing Delta table without breaking existing data.

**Scenario**: Your sales data now includes a `discount_amount` field, but old records don't have it.

**Original Data**:
```python
# Original schema
sales_df = spark.createDataFrame([
    (1, 101, 501, 150.00, "2024-01-15")
], ["sale_id", "customer_id", "product_id", "amount", "sale_date"])

sales_df.write.format("delta").save("/mnt/delta/bronze/sales")
```

**New Data with Extra Column**:
```python
# New data has discount_amount
new_sales_df = spark.createDataFrame([
    (2, 102, 502, 200.00, "2024-01-16", 20.00)  # Added discount_amount
], ["sale_id", "customer_id", "product_id", "amount", "sale_date", "discount_amount"])
```

**Merge Schema**:
```python
# Allow schema evolution
new_sales_df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/mnt/delta/bronze/sales")

# Result:
# - Old records: discount_amount = NULL
# - New records: discount_amount = 20.00
```

---

### 5. Unity Catalog - Data Governance Foundation

**What is Unity Catalog?**
Unity Catalog is the **foundation** for data governance in Databricks. It provides centralized metadata management, access control, and data lineage across all your data assets.

**Why Unity Catalog First?**
- ✅ **Foundation**: All Delta tables should be registered in Unity Catalog
- ✅ **Governance**: Centralized permissions and security
- ✅ **Organization**: Three-level namespace (catalog.schema.table)
- ✅ **Integration**: Works seamlessly with Delta Lake, DLT, and all Databricks features

**Architecture Flow**:
```
Delta Lake Tables
    ↓
Unity Catalog (Register & Govern)
    ↓
Access Control & Lineage
    ↓
Databricks Features (DLT, SQL, ML)
```

#### 5.1 Three-Level Namespace

**Structure**:
```
catalog.schema.table
```

**Nike Store Example**:
```
nike_prod.sales.raw_sales          ← Production sales data
nike_prod.sales.cleaned_sales      ← Cleaned sales data
nike_prod.analytics.daily_summary ← Analytics aggregates
nike_dev.sales.test_sales          ← Development/test data
```

**Why This Matters**:
- ✅ Clear organization (prod vs dev)
- ✅ Easy permissions (grant at catalog/schema/table level)
- ✅ Separate environments
- ✅ Better data discovery

**Flow Diagram**:
```
Catalog (nike_prod)
    ├── Schema (sales)
    │   ├── Table (raw_sales)
    │   ├── Table (cleaned_sales)
    │   └── Table (aggregated_sales)
    └── Schema (analytics)
        └── Table (daily_summary)
```

#### 5.2 Creating Catalogs and Schemas

**Step-by-Step Setup**:

```sql
-- Step 1: Create catalog (top-level container)
CREATE CATALOG IF NOT EXISTS nike_prod
COMMENT 'Nike production data catalog';

-- Step 2: Create schema (database-like container)
CREATE SCHEMA IF NOT EXISTS nike_prod.sales
COMMENT 'Sales data schema';

-- Step 3: Create Delta table (registered in Unity Catalog)
CREATE TABLE nike_prod.sales.raw_sales (
    sale_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10,2),
    sale_date TIMESTAMP
) USING DELTA
LOCATION '/mnt/delta/bronze/sales';
```

**What Happened?**
- ✅ Table created in Delta Lake format
- ✅ Registered in Unity Catalog
- ✅ Can now query with `nike_prod.sales.raw_sales`
- ✅ Governed with permissions

**Query the Table**:
```sql
SELECT * FROM nike_prod.sales.raw_sales;
```

#### 5.3 Registering Existing Delta Tables

**What We're Doing**: Register an existing Delta table in Unity Catalog.

**Scenario**: You have a Delta table at `/mnt/delta/bronze/sales` but it's not in Unity Catalog yet.

**Register Existing Table**:
```sql
-- Register existing Delta table
CREATE TABLE nike_prod.sales.raw_sales
USING DELTA
LOCATION '/mnt/delta/bronze/sales';
```

**Now You Can**:
- ✅ Query with catalog path: `nike_prod.sales.raw_sales`
- ✅ Apply permissions
- ✅ Track lineage
- ✅ Use in DLT pipelines

#### 5.4 Permissions - Who Can Access What

**What We're Doing**: Control who can read/write/modify data.

**Grant Permissions**:
```sql
-- Grant SELECT on table (read-only)
GRANT SELECT ON TABLE nike_prod.sales.raw_sales TO `analysts@nike.com`;

-- Grant ALL on schema (full access)
GRANT ALL PRIVILEGES ON SCHEMA nike_prod.sales TO `data_engineers@nike.com`;

-- Grant USE CATALOG (can access catalog)
GRANT USE CATALOG ON CATALOG nike_prod TO `readers@nike.com`;

-- Grant MODIFY on table (can write)
GRANT MODIFY ON TABLE nike_prod.sales.raw_sales TO `data_engineers@nike.com`;
```

**Revoke Permissions**:
```sql
REVOKE SELECT ON TABLE nike_prod.sales.raw_sales FROM `analysts@nike.com`;
```

**Permission Hierarchy**:
```
Catalog Level
    ↓
Schema Level
    ↓
Table Level
    ↓
Column Level (advanced)
```

#### 5.5 Unity Catalog with Delta Lake

**Best Practice**: Always register Delta tables in Unity Catalog!

**Why?**
- ✅ Centralized governance
- ✅ Better security
- ✅ Data lineage tracking
- ✅ Integration with all Databricks features

**Example - Creating Delta Table with Unity Catalog**:
```python
# Create Delta table
sales_df.write.format("delta") \
    .save("/mnt/delta/bronze/sales")

# Register in Unity Catalog
spark.sql("""
    CREATE TABLE nike_prod.sales.raw_sales
    USING DELTA
    LOCATION '/mnt/delta/bronze/sales'
""")
```

**Now Use in DLT**:
```python
import dlt

@dlt.table(name="silver_sales")
def silver_sales():
    # Read from Unity Catalog table
    return spark.table("nike_prod.sales.raw_sales")
```

---

### 6. Delta Sharing - Share Data Across Clouds

**What is Delta Sharing?**
Open protocol for secure data sharing across organizations, clouds, and platforms. Share Delta tables without copying data!

**Why Delta Sharing?**
- ✅ Share data across clouds (AWS → Azure → GCP)
- ✅ Share with external partners
- ✅ No data copying (read directly from source)
- ✅ Secure (token-based authentication)

**Architecture Flow**:
```
Provider (AWS Databricks)
    ├── Delta Table: nike_prod.sales.raw_sales
    ├── Create Share
    └── Grant Access
         ↓
Consumer (Azure Databricks / Snowflake / Power BI)
    ├── Connect to Share
    ├── Query Shared Data
    └── No Data Copy!
```

#### 6.1 Provider Side - Share Your Data

**What We're Doing**: Share a Delta table with external consumers.

**Step 1: Create Share**:
```sql
-- Create a share
CREATE SHARE nike_sales_share
COMMENT 'Share Nike sales data with partners';
```

**Step 2: Add Table to Share**:
```sql
-- Add Delta table to share
ALTER SHARE nike_sales_share 
ADD TABLE nike_prod.sales.raw_sales;
```

**Step 3: Create Recipient**:
```sql
-- Create recipient (external consumer)
CREATE RECIPIENT partner_company
COMMENT 'Partner company access';
```

**Step 4: Grant Access**:
```sql
-- Grant access to recipient
GRANT SELECT ON SHARE nike_sales_share 
TO RECIPIENT partner_company;
```

**Step 5: Get Share URL**:
```sql
-- Get share URL (for consumer)
SHOW SHARES;
-- Returns: https://sharing-server.com/delta-sharing/shares/nike_sales_share
```

#### 6.2 Consumer Side - Access Shared Data

**What We're Doing**: Access data shared by another organization.

**Step 1: Create Catalog from Share**:
```sql
-- Create catalog from shared data
CREATE CATALOG partner_nike
USING DELTASHARING
LOCATION 'https://sharing-server.com/delta-sharing/'
WITH CREDENTIAL (
    'bearerToken' = 'your-token-here'
);
```

**Step 2: Query Shared Data**:
```python
# Query shared data as regular table
shared_sales = spark.table("partner_nike.nike_sales_share.raw_sales")
shared_sales.show()
```

**Or SQL**:
```sql
SELECT * FROM partner_nike.nike_sales_share.raw_sales;
```

**What Happens?**
- ✅ Data read directly from provider (no copy!)
- ✅ Secure token authentication
- ✅ Works across clouds
- ✅ Real-time access

#### 6.3 Use Cases

**Use Case 1: Multi-Cloud Data Sharing**
```
AWS Databricks (Provider)
    ↓ Delta Sharing
Azure Databricks (Consumer)
    ↓ Query
GCP Databricks (Consumer)
```

**Use Case 2: Partner Data Sharing**
```
Nike (Provider)
    ↓ Share sales data
Retail Partners (Consumers)
    ↓ Access via Delta Sharing
```

**Use Case 3: Data Marketplace**
```
Data Provider
    ↓ Share datasets
Multiple Consumers
    ↓ Pay-per-use access
```

**Benefits**:
- ✅ No data duplication
- ✅ Real-time access
- ✅ Secure sharing
- ✅ Cross-platform (works with Snowflake, Power BI, etc.)

---

### 7. Delta Live Tables (DLT) - Declarative Pipelines

**What is DLT?**
A declarative framework for building reliable data pipelines. You define **what** you want, DLT handles **how**.

#### 5.1 Your First DLT Pipeline

**What We're Building**: A simple Bronze → Silver → Gold pipeline.

**Sample Raw Data** (from S3):
```json
{"sale_id": "SALE-001", "customer_id": 101, "amount": 150.00, "sale_date": "2024-01-15"}
{"sale_id": "SALE-002", "customer_id": null, "amount": -50.00, "sale_date": "2024-01-15"}  ← Bad data!
{"sale_id": "SALE-003", "customer_id": 103, "amount": 200.00, "sale_date": "2024-01-15"}
```

**DLT Pipeline**:
```python
import dlt
from pyspark.sql.functions import *

# Bronze Layer: Raw data ingestion
@dlt.table(
    name="bronze_sales",
    comment="Raw sales data from S3 - as-is"
)
def bronze_sales():
    return spark.read.format("json").load("s3://nike-raw/sales/")

# Silver Layer: Cleaned and validated
@dlt.table(
    name="silver_sales",
    comment="Cleaned sales data with quality checks"
)
@dlt.expect("valid_sale_id", "sale_id IS NOT NULL")      # Must have sale_id
@dlt.expect("valid_amount", "amount > 0")                # Amount must be positive
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")  # Drop if no customer
def silver_sales():
    return dlt.read("bronze_sales") \
        .filter(col("sale_date").isNotNull()) \
        .withColumn("ingestion_timestamp", current_timestamp())

# Gold Layer: Aggregated
@dlt.table(
    name="gold_daily_sales_summary",
    comment="Daily sales aggregates"
)
def gold_daily_sales_summary():
    return dlt.read("silver_sales") \
        .groupBy("sale_date", "customer_id") \
        .agg(
            sum("amount").alias("daily_revenue"),
            count("*").alias("transaction_count")
        )
```

**What Happens**:
1. **Bronze**: Ingests all 3 records (including bad one)
2. **Silver**: 
   - `SALE-001` ✅ Passes all checks
   - `SALE-002` ❌ Dropped (null customer_id, negative amount)
   - `SALE-003` ✅ Passes all checks
3. **Gold**: Aggregates the 2 good records

**Result**:
```
gold_daily_sales_summary:
sale_date  | customer_id | daily_revenue | transaction_count
2024-01-15 | 101         | 150.00        | 1
2024-01-15 | 103         | 200.00        | 1
```

#### 5.2 DLT Expectations Explained

**Three Types of Expectations**:

**1. `@dlt.expect`** - Record violation, continue:
```python
@dlt.expect("valid_amount", "amount > 0")
# If violation: Recorded in metrics, pipeline continues
```

**2. `@dlt.expect_or_drop`** - Drop bad records:
```python
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
# If violation: Record dropped, pipeline continues
```

**3. `@dlt.expect_or_fail`** - Fail pipeline:
```python
@dlt.expect_or_fail("critical_check", "sale_id IS NOT NULL")
# If violation: Pipeline fails, stops processing
```

**Real Example**:
```python
@dlt.table(name="silver_sales")
@dlt.expect("positive_amount", "amount > 0")                    # Warn if negative
@dlt.expect("valid_date", "sale_date >= '2020-01-01'")          # Warn if old date
@dlt.expect_or_drop("valid_customer_id", "customer_id BETWEEN 1 AND 1000000")  # Drop invalid IDs
@dlt.expect_or_fail("no_duplicates", "sale_id IS NOT NULL")     # Fail if duplicate
def silver_sales():
    return dlt.read("bronze_sales")
```

#### 5.3 DLT Incremental Processing

**What We're Doing**: Only process new/changed data, not everything.

**Scenario**: Daily sales pipeline. Yesterday processed 1M records. Today only 10K new records arrived.

**Without Incremental** (Slow):
```python
# Processes ALL 1,010,000 records every day!
@dlt.table(name="silver_sales")
def silver_sales():
    return dlt.read("bronze_sales")  # Reads everything!
```

**With Incremental** (Fast):
```python
# Only processes new records!
@dlt.table(name="silver_sales")
def silver_sales():
    return dlt.read_stream("bronze_sales") \
        .filter(col("sale_date") >= current_date() - 1)  # Only last 24 hours
```

**Benefits**:
- ✅ 100x faster (processes 10K vs 1M records)
- ✅ Lower costs
- ✅ Faster updates

#### 5.4 Error Handling in DLT Pipelines

**What We're Doing**: Handle failures gracefully so pipelines don't crash.

**Pattern 1: Try-Catch in Functions**:
```python
import dlt
from pyspark.sql.functions import *

@dlt.table(name="silver_sales")
def silver_sales():
    try:
        bronze = dlt.read("bronze_sales")
        cleaned = bronze.filter(col("amount") > 0)
        return cleaned
    except Exception as e:
        # Log error
        print(f"Error processing sales: {str(e)}")
        # Return empty DataFrame or raise
        raise
```

**Pattern 2: Dead Letter Queue**:
```python
@dlt.table(name="silver_sales")
@dlt.expect_or_drop("valid_amount", "amount > 0")
def silver_sales():
    return dlt.read("bronze_sales")

# Bad records are automatically dropped by DLT
# You can query dropped records from DLT metrics
```

**Pattern 3: Retry Logic**:
```python
# In workflow configuration (JSON)
{
  "task_key": "silver_sales",
  "retry_on_timeout": true,
  "max_retries": 3,
  "min_retry_interval_millis": 60000
}
```

---

### 8. Spark Structured Streaming - Real-Time Processing

**What is Structured Streaming?**
Process data in real-time as it arrives (like Kafka streams).

#### 6.1 Your First Streaming Pipeline

**What We're Building**: Read sales events from Kafka and write to Delta Lake in real-time.

**Sample Kafka Messages**:
```json
{"sale_id": "SALE-001", "customer_id": 101, "amount": 150.00, "timestamp": "2024-01-15T10:30:00Z"}
{"sale_id": "SALE-002", "customer_id": 102, "amount": 200.00, "timestamp": "2024-01-15T10:31:00Z"}
```

**Streaming Code**:
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("SalesStreaming") \
    .getOrCreate()

# Define schema
from pyspark.sql.types import *
sales_schema = StructType([
    StructField("sale_id", StringType()),
    StructField("customer_id", IntegerType()),
    StructField("amount", DoubleType()),
    StructField("timestamp", TimestampType())
])

# Read stream from Kafka
stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-server:9092") \
    .option("subscribe", "nike-sales") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON
sales_stream = stream_df.select(
    from_json(col("value").cast("string"), sales_schema).alias("data")
).select("data.*")

# Write to Delta Lake (streaming)
query = sales_stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/mnt/delta/checkpoints/sales_stream") \
    .trigger(processingTime="10 seconds") \
    .start("/mnt/delta/bronze/sales_stream")

query.awaitTermination()
```

**What Happens**:
- Every 10 seconds, reads new messages from Kafka
- Parses JSON
- Writes to Delta Lake
- Checkpoint tracks progress (so if it crashes, resumes where it left off)

**Understanding Checkpoints**:
- Checkpoint saves: Current Kafka offset, processing state, metadata
- If stream crashes: Resumes from last checkpoint (no duplicates!)
- ⚠️ Never delete checkpoint directory! If deleted, stream restarts from beginning
- Location: `/mnt/delta/checkpoints/sales_stream`

#### 6.2 Understanding Checkpoints

**What is a Checkpoint?**
A checkpoint saves the current position in the stream so you can resume after a failure.

**Why Checkpoints Matter**:
```
Without checkpoint:
- Stream crashes at message 1000
- Restarts → processes messages 1-1000 again (duplicates!)

With checkpoint:
- Stream crashes at message 1000
- Checkpoint saved position: message 1000
- Restarts → processes from message 1001 (no duplicates!)
```

**Checkpoint Location**:
```python
.option("checkpointLocation", "/mnt/delta/checkpoints/sales_stream")
```

**What's Stored**:
- Current offset in Kafka
- Processing state
- Metadata

**⚠️ Important**: Never delete checkpoint directory! If deleted, stream will restart from beginning.

#### 6.3 Output Modes Explained

**Three Output Modes**:

**1. Append Mode** (Default):
```python
.writeStream.outputMode("append")
```
- Only new rows added
- Use for: Simple writes, no aggregations

**2. Complete Mode**:
```python
.writeStream.outputMode("complete")
```
- Entire result table rewritten
- Use for: Aggregations (e.g., hourly totals)

**3. Update Mode**:
```python
.writeStream.outputMode("update")
```
- Only updated rows written
- Use for: Aggregations where you update existing rows

**Example - Hourly Aggregations**:
```python
# Aggregate sales by hour
hourly_sales = sales_stream \
    .withWatermark("timestamp", "1 hour") \
    .groupBy(
        window(col("timestamp"), "1 hour"),
        col("customer_id")
    ) \
    .agg(sum("amount").alias("hourly_revenue"))

# Use UPDATE mode (updates existing hour windows)
hourly_sales.writeStream \
    .format("delta") \
    .outputMode("update") \
    .option("checkpointLocation", "/mnt/delta/checkpoints/hourly_sales") \
    .start("/mnt/delta/silver/hourly_sales")
```

#### 6.4 Watermarks - Handling Late Data

**What is a Watermark?**
A threshold for accepting late-arriving data.

**Scenario**: Sales events arrive late (network delay, retries).

**Example**:
```
Current time: 10:00 AM
Watermark: 1 hour
Accepts data: 9:00 AM - 10:00 AM
Rejects data: Before 9:00 AM (too late!)
```

**Code**:
```python
sales_stream \
    .withWatermark("timestamp", "1 hour") \
    .groupBy(window("timestamp", "1 hour")) \
    .agg(sum("amount").alias("hourly_revenue"))
```

**How It Works**:
- Tracks maximum event time seen
- Late data within watermark → processed ✅
- Data older than watermark → dropped ❌

---

### 9. Delta Live Tables + Structured Streaming

**Combining DLT + Streaming**:

**What We're Building**: Real-time pipeline with automatic quality checks.

**Sample Kafka Stream**:
```json
{"sale_id": "SALE-001", "customer_id": 101, "amount": 150.00, "timestamp": "2024-01-15T10:30:00Z"}
{"sale_id": "SALE-002", "customer_id": null, "amount": -50.00, "timestamp": "2024-01-15T10:31:00Z"}  ← Bad!
```

**DLT + Streaming Pipeline**:
```python
import dlt
from pyspark.sql.functions import *

# Stream from Kafka to Bronze
@dlt.table(
    name="bronze_sales_stream",
    comment="Real-time sales stream from Kafka"
)
def bronze_sales_stream():
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka-server:9092") \
        .option("subscribe", "nike-sales") \
        .load() \
        .select(
            from_json(col("value").cast("string"), sales_schema).alias("data")
        ) \
        .select("data.*")

# Stream from Bronze to Silver (with quality checks)
@dlt.table(
    name="silver_sales_stream",
    comment="Cleaned streaming sales data"
)
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_sales_stream():
    return dlt.read_stream("bronze_sales_stream") \
        .withWatermark("timestamp", "1 hour") \
        .withColumn("ingestion_time", current_timestamp())

# Aggregated Gold layer (streaming)
@dlt.table(
    name="gold_hourly_sales",
    comment="Hourly sales aggregates"
)
def gold_hourly_sales():
    return dlt.read_stream("silver_sales_stream") \
        .groupBy(
            window(col("timestamp"), "1 hour"),
            col("customer_id")
        ) \
        .agg(
            sum("amount").alias("hourly_revenue"),
            count("*").alias("transaction_count")
        )
```

**Benefits**:
- ✅ Automatic checkpointing
- ✅ Built-in monitoring
- ✅ Data quality checks
- ✅ Incremental processing

---

### 10. Reading from Different Sources

**What is Unity Catalog?**
Centralized data governance for all your data assets.

#### 8.1 Three-Level Namespace

**Structure**:
```
catalog.schema.table
```

**Nike Store Example**:
```
nike_prod.sales.raw_sales          ← Production sales data
nike_prod.sales.cleaned_sales      ← Cleaned sales data
nike_prod.analytics.daily_summary ← Analytics aggregates
nike_dev.sales.test_sales          ← Development/test data
```

**Why This Matters**:
- ✅ Clear organization
- ✅ Easy permissions
- ✅ Separate prod/dev environments

#### 8.2 Creating Catalogs and Schemas

**Step-by-Step**:

```sql
-- Step 1: Create catalog
CREATE CATALOG IF NOT EXISTS nike_prod
COMMENT 'Nike production data catalog';

-- Step 2: Create schema
CREATE SCHEMA IF NOT EXISTS nike_prod.sales
COMMENT 'Sales data schema';

-- Step 3: Create table
CREATE TABLE nike_prod.sales.raw_sales (
    sale_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10,2),
    sale_date TIMESTAMP
) USING DELTA
LOCATION '/mnt/delta/bronze/sales';
```

**Now Query**:
```sql
SELECT * FROM nike_prod.sales.raw_sales;
```

#### 8.3 Permissions - Who Can Access What

**Grant Permissions**:
```sql
-- Grant SELECT on table
GRANT SELECT ON TABLE nike_prod.sales.raw_sales TO `analysts@nike.com`;

-- Grant ALL on schema
GRANT ALL PRIVILEGES ON SCHEMA nike_prod.sales TO `data_engineers@nike.com`;

-- Grant USE CATALOG
GRANT USE CATALOG ON CATALOG nike_prod TO `readers@nike.com`;
```

**Revoke Permissions**:
```sql
REVOKE SELECT ON TABLE nike_prod.sales.raw_sales FROM `analysts@nike.com`;
```

---

### 11. Spark Job Optimization

#### 10.1 Snowflake

**What We're Doing**: Read data from Snowflake and write to Delta Lake.

**Sample Snowflake Table** (`PRODUCTION.SALES.SALES`):
```
SALE_ID | CUSTOMER_ID | AMOUNT | SALE_DATE
--------|-------------|--------|-----------
1       | 101         | 150.00 | 2024-01-15
2       | 102         | 200.00 | 2024-01-15
```

**Read from Snowflake**:
```python
# Using Spark connector
snowflake_df = spark.read \
    .format("snowflake") \
    .option("sfURL", "nike.snowflakecomputing.com") \
    .option("sfUser", "databricks_user") \
    .option("sfPassword", "password") \
    .option("sfDatabase", "PRODUCTION") \
    .option("sfSchema", "SALES") \
    .option("sfWarehouse", "COMPUTE_WH") \
    .option("query", "SELECT * FROM SALES WHERE SALE_DATE >= '2024-01-01'") \
    .load()

# Write to Delta Lake
snowflake_df.write.format("delta").save("/mnt/delta/bronze/snowflake_sales")
```

**Using Unity Catalog** (Better!):
```sql
-- Create external table pointing to Snowflake
CREATE TABLE nike_prod.sales.snowflake_sales
USING SNOWFLAKE
OPTIONS (
    'sfURL' 'nike.snowflakecomputing.com',
    'sfDatabase' 'PRODUCTION',
    'sfSchema' 'SALES',
    'sfTable' 'SALES'
);

-- Query as regular table
SELECT * FROM nike_prod.sales.snowflake_sales;
```

#### 10.2 Apache Iceberg

**Read from Iceberg**:
```python
# Read Iceberg table
iceberg_df = spark.read \
    .format("iceberg") \
    .load("s3://nike-data/iceberg/sales/")

# Write to Delta Lake
iceberg_df.write.format("delta").save("/mnt/delta/bronze/iceberg_sales")
```

**Using Unity Catalog**:
```sql
CREATE TABLE nike_prod.sales.iceberg_sales
USING ICEBERG
LOCATION 's3://nike-data/iceberg/sales/';
```

#### 10.3 Other Sources

**PostgreSQL**:
```python
postgres_df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://db-server:5432/nike") \
    .option("dbtable", "sales") \
    .option("user", "user") \
    .option("password", "password") \
    .load()
```

**MongoDB**:
```python
mongo_df = spark.read \
    .format("mongo") \
    .option("uri", "mongodb://mongo-server:27017") \
    .option("database", "nike") \
    .option("collection", "sales") \
    .load()
```

---

### 12. Latest Optimizations - Predictive Optimization

**What is Predictive Optimization?**
AI-powered feature that automatically optimizes your Delta tables based on query patterns. No manual tuning needed!

**Why Predictive Optimization?**
- ✅ **Automatic**: Learns from your queries and optimizes automatically
- ✅ **Intelligent**: Uses ML to predict optimal file sizes and clustering
- ✅ **Zero Maintenance**: Runs in background, no manual intervention
- ✅ **Cost Effective**: Reduces storage and compute costs

**How It Works**:
```
Query Patterns
    ↓
ML Model (Learns)
    ↓
Predictive Optimization
    ↓
Auto-OPTIMIZE & Auto-Compact
    ↓
Better Performance
```

**Enable Predictive Optimization**:
```sql
-- Enable on table
ALTER TABLE nike_prod.sales.raw_sales
SET TBLPROPERTIES (
    'delta.predictiveOptimization.enabled' = 'true'
);
```

**What It Does Automatically**:
- ✅ Optimizes file sizes based on query patterns
- ✅ Auto-compacts small files
- ✅ Suggests optimal clustering columns
- ✅ Monitors and adjusts continuously

**Benefits**:
- Before: Manual OPTIMIZE runs → 30 min/week
- After: Automatic optimization → 0 min/week ✅
- Performance: 2-5x faster queries
- Cost: 20-30% storage reduction

**Best Practices**:
- ✅ Enable on frequently queried tables
- ✅ Let it run for 1-2 weeks to learn patterns
- ✅ Monitor results in Databricks UI
- ✅ Works great with Unity Catalog

---

### 11. Spark Job Optimization

#### 11.1 Performance Tuning - Key Configs

**What We're Doing**: Make Spark jobs run faster.

**Key Configuration Parameters**:

```python
spark = SparkSession.builder \
    .appName("OptimizedJob") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.files.maxPartitionBytes", "134217728") \
    .getOrCreate()
```

**What Each Config Does**:
- `spark.sql.shuffle.partitions`: Number of partitions after shuffle (default: 200)
- `spark.sql.adaptive.enabled`: Enable adaptive query execution (auto-tunes)
- `spark.sql.files.maxPartitionBytes`: Max bytes per partition (128MB default)
- `spark.serializer`: Use Kryo for better performance

#### 11.2 Auto Scaling - Dynamic Cluster Sizing

**What is Auto Scaling?**
Automatically add or remove cluster nodes based on workload demand.

**Why Auto Scaling?**
- ✅ **Cost Effective**: Scale down when idle, scale up when busy
- ✅ **Performance**: Always right-sized for workload
- ✅ **Automatic**: No manual intervention needed

**Enable Auto Scaling**:
```python
cluster_config = {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "autoscale": {
        "min_workers": 1,      # Minimum nodes
        "max_workers": 10,     # Maximum nodes
        "target_workers": 4    # Target nodes
    }
}
```

**How It Works**:
```
Low Load → Scale Down (1 node)
    ↓
Medium Load → Scale Up (4 nodes)
    ↓
High Load → Scale Up (10 nodes)
    ↓
Load Decreases → Scale Down
```

**Benefits**:
- ✅ Pay only for what you use
- ✅ Faster job completion (scale up for big jobs)
- ✅ Lower costs (scale down when idle)

**Best Practices**:
- ✅ Set min_workers based on baseline load
- ✅ Set max_workers based on peak load
- ✅ Monitor scaling behavior
- ✅ Use with autotermination

#### 11.2 Performance Tuning - Key Configs

**What We're Doing**: Make Spark jobs run faster.

**Key Configuration Parameters**:

```python
spark = SparkSession.builder \
    .appName("OptimizedJob") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.files.maxPartitionBytes", "134217728") \
    .getOrCreate()
```

**What Each Config Does**:
- `spark.sql.shuffle.partitions`: Number of partitions after shuffle (default: 200)
- `spark.sql.adaptive.enabled`: Enable adaptive query execution (auto-tunes)
- `spark.sql.files.maxPartitionBytes`: Max bytes per partition (128MB default)
- `spark.serializer`: Use Kryo for better performance

**What is Auto Scaling?**
Automatically add or remove cluster nodes based on workload demand.

**Why Auto Scaling?**
- ✅ **Cost Effective**: Scale down when idle, scale up when busy
- ✅ **Performance**: Always right-sized for workload
- ✅ **Automatic**: No manual intervention needed

**Enable Auto Scaling**:
```python
cluster_config = {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "autoscale": {
        "min_workers": 1,      # Minimum nodes
        "max_workers": 10,     # Maximum nodes
        "target_workers": 4    # Target nodes
    }
}
```

**How It Works**:
```
Low Load → Scale Down (1 node)
    ↓
Medium Load → Scale Up (4 nodes)
    ↓
High Load → Scale Up (10 nodes)
    ↓
Load Decreases → Scale Down
```

**Benefits**:
- ✅ Pay only for what you use
- ✅ Faster job completion (scale up for big jobs)
- ✅ Lower costs (scale down when idle)

**Best Practices**:
- ✅ Set min_workers based on baseline load
- ✅ Set max_workers based on peak load
- ✅ Monitor scaling behavior
- ✅ Use with autotermination

#### 11.3 Handling Data Skew

**What is Skew?**
Uneven data distribution across partitions.

**Problem Example**:
```
Partition 1: 10,000 rows (customer_id = 101)  ← Hot partition!
Partition 2: 100 rows
Partition 3: 100 rows
... (most partitions have 100 rows)
```

**Why This is Bad**:
- One partition takes forever (bottleneck)
- Other partitions finish quickly
- Overall job is slow

**Solution 1: Salting**:
```python
from pyspark.sql.functions import *

# Add random salt to customer_id
salted_df = sales_df.withColumn("salt", (rand() * 100).cast("int"))

# Group by salted customer_id
result = salted_df.groupBy("customer_id", "salt") \
    .agg(sum("amount").alias("total")) \
    .groupBy("customer_id") \
    .agg(sum("total").alias("grand_total"))
```

**Solution 2: Broadcast Small Tables**:
```python
from pyspark.sql.functions import broadcast

# Broadcast customer dimension (small table)
customer_dim = spark.table("dim_customer")  # 10K rows
sales_df.join(broadcast(customer_dim), "customer_id")
```

**Solution 3: Enable Skew Join**:
```python
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

#### 11.4 Memory Optimization

**Memory Configuration**:
```python
spark = SparkSession.builder \
    .config("spark.executor.memory", "8g") \
    .config("spark.executor.memoryFraction", "0.8") \
    .config("spark.executor.cores", "4") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()
```

**Best Practices**:
- ✅ Cache only when needed: `df.cache()`
- ✅ Unpersist when done: `df.unpersist()`
- ✅ Monitor memory in Spark UI

**Example**:
```python
# Cache frequently used table
customer_dim = spark.table("dim_customer").cache()

# Use in multiple operations
sales_with_customer = sales_df.join(customer_dim, "customer_id")
revenue_by_customer = sales_with_customer.groupBy("customer_name").sum("amount")

# Unpersist when done
customer_dim.unpersist()
```

#### 11.5 Processing Too Much Data - Strategies

**Problem**: Table has 1 billion rows, but you only need last 30 days.

**Strategy 1: Partition Pruning**:
```python
# Only read relevant partitions
sales_df = spark.read.format("delta").load("/mnt/delta/sales") \
    .filter(col("sale_date") >= "2024-01-01")
```

**Strategy 2: Column Pruning**:
```python
# Only select needed columns
sales_df.select("sale_id", "customer_id", "amount")
```

**Strategy 3: Incremental Processing**:
```python
# Only process new data
new_sales = spark.read.format("delta") \
    .option("versionAsOf", last_processed_version) \
    .load("/mnt/delta/sales")
```

---

### 13. Data Governance & PII Protection

#### 11.1 Delta Sharing

**What We're Doing**: Share data securely across different clouds (AWS → Azure).

**Provider Side (AWS)**:
```python
# Create share
spark.sql("CREATE SHARE nike_sales_share")

# Add table to share
spark.sql("ALTER SHARE nike_sales_share ADD TABLE nike_prod.sales.raw_sales")

# Create recipient
spark.sql("CREATE RECIPIENT azure_consumer")

# Grant access
spark.sql("GRANT SELECT ON SHARE nike_sales_share TO RECIPIENT azure_consumer")
```

**Consumer Side (Azure)**:
```python
# Create catalog from share
spark.sql("""
    CREATE CATALOG azure_nike
    USING DELTASHARING
    LOCATION 'https://sharing-server.com/delta-sharing/'
    WITH CREDENTIAL (
        'bearerToken' = 'token-here'
    )
""")

# Query shared data
shared_sales = spark.table("azure_nike.nike_sales_share.raw_sales")
```

---

### 14. Cost Optimization

#### 12.1 Column-Level Security

**What We're Doing**: Mask PII data (emails, phone numbers).

**Sample Customer Data**:
```
customer_id | name          | email                    | phone
------------|---------------|--------------------------|----------
101         | Sarah Johnson | sarah.johnson@email.com  | 555-1234
102         | Mike Chen     | mike.chen@email.com      | 555-5678
```

**Mask Email**:
```sql
-- Create masking function
CREATE FUNCTION mask_email(email STRING)
RETURNS STRING
RETURN CONCAT(
    SUBSTRING(email, 1, 2),
    '***',
    SUBSTRING(email, POSITION('@' IN email))
);

-- Apply masking
SELECT 
    customer_id,
    mask_email(email) AS masked_email,
    name
FROM nike_prod.sales.customers;
```

**Result**:
```
customer_id | masked_email        | name
------------|---------------------|-------------
101         | sa***@email.com     | Sarah Johnson
102         | mi***@email.com     | Mike Chen
```

**Column-Level Permissions**:
```sql
-- Grant access to non-PII columns only
GRANT SELECT(customer_id, name, city) ON TABLE nike_prod.sales.customers 
TO `analysts@nike.com`;

-- Deny access to PII columns
DENY SELECT(email, phone, ssn) ON TABLE nike_prod.sales.customers 
TO `analysts@nike.com`;
```

#### 12.2 Row-Level Security

**What We're Doing**: Users can only see their own data.

```sql
-- Create row filter
CREATE FUNCTION nike_prod.sales.customer_filter()
RETURNS BOOLEAN
RETURN current_user() = email OR 
       is_member('data_engineers@nike.com');

-- Apply filter
ALTER TABLE nike_prod.sales.customers
SET ROW FILTER nike_prod.sales.customer_filter ON (email);
```

---

### 15. Cost Optimization

#### 13.1 Cluster Optimization

**Right-Size Clusters**:
```python
cluster_config = {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",  # Right size for workload
    "num_workers": 2,  # Start small, scale up if needed
    "autotermination_minutes": 30,  # Auto-terminate idle clusters
    "enable_elastic_disk": True  # Scale disk with data
}
```

**Best Practices**:
- ✅ Use autoscaling: `min_workers=1, max_workers=10`
- ✅ Enable autotermination: `autotermination_minutes=30`
- ✅ Use spot instances for non-critical jobs
- ✅ Right-size instances (don't over-provision)

#### 13.2 Job Optimization

**Optimize Job Costs**:
```python
# 1. Use job clusters (terminate after job)
job_cluster = {
    "new_cluster": {
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2,
        "autotermination_minutes": 0  # Terminate immediately after job
    }
}

# 2. Optimize Delta tables regularly
spark.sql("OPTIMIZE delta.`/mnt/delta/sales`")

# 3. VACUUM old files
spark.sql("VACUUM delta.`/mnt/delta/sales` RETAIN 7 DAYS")

# 4. Use Z-ORDER for better query performance
spark.sql("OPTIMIZE delta.`/mnt/delta/sales` ZORDER BY (customer_id, date)")
```

#### 13.3 Serverless Compute

**What is Serverless?**
Compute that automatically scales and manages infrastructure for you.

**Benefits**:
- ✅ No cluster management
- ✅ Auto-scaling
- ✅ Pay only for what you use
- ✅ Faster startup times

**When to Use**:
- ✅ SQL warehouses (Databricks SQL)
- ✅ Serverless workflows
- ✅ On-demand compute

**Example**:
```python
# Serverless SQL Warehouse (via UI)
# Automatically scales based on query load
# No cluster management needed!
```

#### 13.4 Photon Engine

**What is Photon?**
Databricks' native vectorized query engine (faster than Spark for some workloads).

**Benefits**:
- ✅ 2-10x faster for SQL workloads
- ✅ Better performance for aggregations
- ✅ Automatic optimization

**When Photon Helps**:
- ✅ SQL queries (SELECT, JOIN, GROUP BY)
- ✅ Aggregations
- ✅ Filtering and sorting

**Enable Photon**:
```python
# Enable Photon in cluster config
cluster_config = {
    "spark_version": "13.3.x-scala2.12",
    "photon": True,  # Enable Photon engine
    "node_type_id": "i3.xlarge"
}
```

**Note**: Photon is automatically enabled in Databricks SQL warehouses.

#### 13.5 Storage Optimization

**Reduce Storage Costs**:
```python
# 1. Compress data
sales_df.write.format("delta") \
    .option("compression", "zstd") \
    .save("/mnt/delta/sales")

# 2. Partition efficiently
sales_df.write.format("delta") \
    .partitionBy("year", "month", "day") \
    .save("/mnt/delta/sales")
```

---

## 🎯 Tier 1: Critical Sections for Interview Success

### 16. Databricks Interview Questions & Answers

**Why This Section?**
These are the most common Databricks questions asked in senior data engineer interviews. Master these to ace your interview!

---

#### Q1: Explain Delta Lake ACID Transactions

**Question**: "How does Delta Lake implement ACID transactions? Walk me through the mechanism."

**Answer Structure**:

**1. What is ACID?**
- **Atomicity**: All operations succeed or all fail
- **Consistency**: Data remains valid after transaction
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed changes persist

**2. How Delta Lake Implements ACID**:

**Transaction Log Mechanism**:
```
Write Operation
    ↓
Create Transaction Log Entry (_delta_log/)
    ↓
Write Data Files (Parquet)
    ↓
Commit Transaction (Update Log)
    ↓
ACID Guarantee ✅
```

**Example**:
```python
# Transaction 1: Insert 1000 records
sales_df.write.format("delta").mode("append").save("/mnt/delta/sales")
# Creates: 00000000000000000000.json in _delta_log/

# Transaction 2: Update 100 records
delta_table.update(condition="amount < 0", set={"amount": "0"})
# Creates: 00000000000000000001.json in _delta_log/

# If update fails halfway → Transaction log not updated
# Previous version (00000000000000000000.json) still valid!
```

**3. Key Components**:
- **Transaction Log**: JSON files in `_delta_log/` directory
- **Versioning**: Each transaction = new version
- **Atomic Writes**: All-or-nothing file operations
- **Isolation**: Readers see consistent snapshots

**4. Real-World Example**:
```python
# Scenario: Update 1M records, job fails at 500K
delta_table.update(condition="date = '2024-01-15'", set={"status": "processed"})

# What Happens:
# - Job fails at 500K records
# - Transaction log NOT updated
# - Previous version still intact
# - No partial updates! ✅
```

**Key Points to Emphasize**:
- ✅ Transaction log ensures atomicity
- ✅ Versioning enables time travel
- ✅ Readers always see consistent state
- No partial writes possible

---

#### Q2: When Would You Use DLT vs Spark?

**Question**: "When should I use Delta Live Tables (DLT) vs regular Spark? What are the trade-offs?"

**Answer Structure**:

**1. Delta Live Tables (DLT) - Use When**:

✅ **Use DLT When**:
- Building new pipelines from scratch
- Need built-in data quality checks
- Want automatic dependency management
- Need pipeline monitoring out-of-the-box
- Team prefers declarative approach

**Example**:
```python
# DLT: Declarative, automatic quality checks
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("invalid_customer", "customer_id IS NOT NULL")
def silver_sales():
    return dlt.read("bronze_sales")
```

**2. Regular Spark - Use When**:

✅ **Use Spark When**:
- Need fine-grained control
- Complex custom logic required
- Legacy codebase migration
- Performance-critical custom optimizations
- Need RDD-level operations

**Example**:
```python
# Spark: Full control, manual quality checks
bronze = spark.read.format("delta").load("/mnt/delta/bronze/sales")
silver = bronze.filter(col("amount") > 0) \
    .filter(col("customer_id").isNotNull()) \
    .withColumn("quality_score", custom_quality_function())
silver.write.format("delta").save("/mnt/delta/silver/sales")
```

**3. Comparison Table**:

| Feature | DLT | Spark |
|---------|-----|-------|
| **Setup** | Easy (decorators) | More code |
| **Data Quality** | Built-in expectations | Manual checks |
| **Dependency Management** | Automatic | Manual |
| **Monitoring** | Built-in UI | Custom setup |
| **Flexibility** | Limited | Full control |
| **Learning Curve** | Low | Medium |
| **Performance** | Good | Excellent (with tuning) |

**4. Real-World Decision**:

**Scenario**: Build a new sales pipeline with quality checks

**DLT Approach** (Recommended):
```python
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
def silver_sales():
    return dlt.read("bronze_sales")
```
- ✅ Faster development
- ✅ Built-in quality monitoring
- ✅ Less code

**Spark Approach** (If needed):
```python
# Only if you need custom logic DLT can't handle
```

**5. Hybrid Approach**:
```python
# Use DLT for standard pipelines
# Use Spark for custom/legacy code
# Best of both worlds!
```

**Key Points**:
- ✅ DLT: Faster development, built-in quality
- ✅ Spark: More control, better for complex logic
- ✅ Choose based on requirements, not preference

---

#### Q3: How Do You Handle Data Skew in Databricks?

**Question**: "Your Spark job is slow. You suspect data skew. How do you identify and fix it?"

**Answer Structure**:

**1. What is Data Skew?**
Uneven data distribution across partitions. One partition has way more data than others.

**Example**:
```
Partition 1: 1,000,000 rows (customer_id = 101) ← Hot partition!
Partition 2: 1,000 rows
Partition 3: 1,000 rows
... (most partitions have 1,000 rows)
```

**2. How to Identify Skew**:

**Method 1: Check Partition Sizes**:
```python
# Check data distribution
df.groupBy("customer_id").count().orderBy(desc("count")).show()

# Output:
# customer_id | count
# 101         | 1000000  ← Skewed!
# 102         | 1000
# 103         | 1000
```

**Method 2: Spark UI**:
- Check "Stages" tab
- Look for tasks with much longer duration
- One task taking 10x longer = skew!

**Method 3: Check Partition Stats**:
```python
# Check partition sizes
spark.sql("ANALYZE TABLE sales COMPUTE STATISTICS FOR ALL COLUMNS")
spark.sql("DESCRIBE EXTENDED sales").show()
```

**3. Solutions**:

**Solution 1: Salting** (Most Common):
```python
from pyspark.sql.functions import *

# Add random salt to skewed column
salted_df = df.withColumn("salt", (rand() * 100).cast("int"))

# Group by salted key
result = salted_df.groupBy("customer_id", "salt") \
    .agg(sum("amount").alias("total")) \
    .groupBy("customer_id") \
    .agg(sum("total").alias("grand_total"))
```

**Solution 2: Broadcast Small Tables**:
```python
from pyspark.sql.functions import broadcast

# Broadcast dimension table (small)
customer_dim = spark.table("dim_customer")  # 10K rows
df.join(broadcast(customer_dim), "customer_id")
```

**Solution 3: Enable Skew Join**:
```python
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

**Solution 4: Repartition**:
```python
# Repartition to more partitions
df.repartition(200, "customer_id")
```

**4. Real-World Example**:

**Problem**: Sales table has 1M rows for customer 101, but only 1K for others.

**Solution**:
```python
# Step 1: Identify skew
df.groupBy("customer_id").count().orderBy(desc("count")).show(10)

# Step 2: Apply salting
salted = df.withColumn("salt", (rand() * 50).cast("int"))

# Step 3: Process with salt
result = salted.groupBy("customer_id", "salt") \
    .agg(sum("amount")) \
    .groupBy("customer_id") \
    .agg(sum("amount").alias("total"))

# Result: Even distribution across partitions!
```

**Key Points**:
- ✅ Identify: Check partition sizes, Spark UI
- ✅ Fix: Salting (most common), broadcast, skew join
- ✅ Monitor: Always check for skew in production

---

#### Q4: Design a Databricks Pipeline for 1TB/Day

**Question**: "Design a Databricks pipeline that processes 1TB of data per day. Walk me through your architecture."

**Answer Structure**:

**1. Requirements Gathering**:
- **Volume**: 1TB/day = ~42GB/hour = ~700MB/minute
- **Sources**: Multiple (S3, Kafka, databases)
- **Latency**: Batch (hourly) + Real-time (optional)
- **Retention**: 2 years
- **Users**: 100+ analysts, 10+ data engineers

**2. Architecture Design**:

```
┌─────────────────────────────────────────────────────────┐
│                    Data Sources                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   S3     │  │  Kafka   │  │   DBs    │            │
│  │ (Batch)  │  │(Streaming)│ │ (JDBC)   │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Databricks Workspace       │
        │                              │
        │  ┌────────────────────────┐ │
        │  │  Unity Catalog          │ │
        │  │  (Governance)           │ │
        │  └───────────┬────────────┘ │
        │              ↓               │
        │  ┌────────────────────────┐ │
        │  │  DLT Pipelines          │ │
        │  │  (Bronze/Silver/Gold)  │ │
        │  └───────────┬────────────┘ │
        │              ↓               │
        │  ┌────────────────────────┐ │
        │  │  Spark Clusters         │ │
        │  │  (Auto-scaling)         │ │
        │  └────────────────────────┘ │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Delta Lake Storage      │
        │  ┌────────────────────────┐ │
        │  │  Bronze (Raw)          │ │
        │  │  Partitioned by date   │ │
        │  └───────────┬────────────┘ │
        │              ↓               │
        │  ┌────────────────────────┐ │
        │  │  Silver (Cleaned)      │ │
        │  │  Quality checked       │ │
        │  └───────────┬────────────┘ │
        │              ↓               │
        │  ┌────────────────────────┐ │
        │  │  Gold (Aggregated)     │ │
        │  │  Business-ready        │ │
        │  └────────────────────────┘ │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Analytics Layer         │
        │  ┌──────────┐  ┌──────────┐ │
        │  │ BI Tools │  │ ML Models│ │
        │  └──────────┘  └──────────┘ │
        └──────────────────────────────┘
```

**3. Component Selection**:

**Ingestion**:
- **S3 (Batch)**: Daily/hourly files
- **Kafka (Streaming)**: Real-time events
- **JDBC (Databases)**: Incremental loads

**Processing**:
- **DLT Pipelines**: Bronze → Silver → Gold
- **Spark Clusters**: Auto-scaling (2-20 workers)
- **Scheduling**: Databricks Workflows

**Storage**:
- **Delta Lake**: All layers
- **Partitioning**: `year/month/day/hour`
- **Optimization**: Daily OPTIMIZE + VACUUM

**Governance**:
- **Unity Catalog**: All tables registered
- **Permissions**: Role-based access
- **Lineage**: Automatic tracking

**4. Implementation Details**:

**Bronze Layer**:
```python
@dlt.table(name="bronze_sales")
def bronze_sales():
    # Batch from S3
    batch = spark.read.format("json").load("s3://raw/sales/")
    
    # Streaming from Kafka
    stream = spark.readStream.format("kafka") \
        .option("subscribe", "sales") \
        .load()
    
    return batch.union(stream)
```

**Silver Layer**:
```python
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_sales():
    return dlt.read("bronze_sales") \
        .withColumn("ingestion_time", current_timestamp())
```

**Gold Layer**:
```python
@dlt.table(name="gold_daily_sales")
def gold_daily_sales():
    return dlt.read("silver_sales") \
        .groupBy("sale_date", "customer_id") \
        .agg(sum("amount").alias("daily_revenue"))
```

**5. Scalability Considerations**:

**Partitioning Strategy**:
```python
# Partition by date for efficient queries
sales_df.write.format("delta") \
    .partitionBy("year", "month", "day") \
    .save("/mnt/delta/bronze/sales")
```

**Auto-Scaling**:
```python
cluster_config = {
    "autoscale": {
        "min_workers": 2,
        "max_workers": 20,  # Scale up for 1TB/day
        "target_workers": 8
    }
}
```

**Optimization Schedule**:
```python
# Daily OPTIMIZE
spark.sql("OPTIMIZE delta.`/mnt/delta/silver/sales`")

# Weekly VACUUM
spark.sql("VACUUM delta.`/mnt/delta/silver/sales` RETAIN 7 DAYS")
```

**6. Cost Optimization**:
- Use job clusters (terminate after job)
- Auto-scaling (scale down when idle)
- Optimize Delta tables (reduce storage)
- Partition efficiently (reduce scan costs)

**7. Monitoring**:
- DLT pipeline health dashboard
- Query performance metrics
- Cost monitoring
- Data quality metrics

**Key Points**:
- ✅ Medallion architecture (Bronze/Silver/Gold)
- ✅ Partitioning strategy critical
- ✅ Auto-scaling for variable load
- ✅ Unity Catalog for governance
- ✅ Daily optimization schedule

---

#### Q5: Explain Delta Lake Time Travel

**Question**: "How does Delta Lake time travel work? Give me a practical example."

**Answer Structure**:

**1. What is Time Travel?**
Query historical versions of your data at any point in time.

**2. How It Works**:

**Transaction Log Versioning**:
```
Version 1: CREATE TABLE (00000000000000000000.json)
Version 2: INSERT 1000 rows (00000000000000000001.json)
Version 3: UPDATE 100 rows (00000000000000000002.json)
Version 4: DELETE 50 rows (00000000000000000003.json)
```

**3. Query Historical Versions**:

**By Version Number**:
```python
# Read version 2 (before UPDATE)
version_2 = spark.read.format("delta") \
    .option("versionAsOf", 2) \
    .load("/mnt/delta/sales")
```

**By Timestamp**:
```python
# Read data as of specific time
version_time = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 10:00:00") \
    .load("/mnt/delta/sales")
```

**SQL Syntax**:
```sql
-- Query version 2
SELECT * FROM delta.`/mnt/delta/sales` VERSION AS OF 2;

-- Query as of timestamp
SELECT * FROM delta.`/mnt/delta/sales` TIMESTAMP AS OF '2024-01-15 10:00:00';
```

**4. Practical Example**:

**Scenario**: Yesterday, someone accidentally updated all sales amounts. Today, you need to see what data looked like before that mistake.

**Step 1: Check History**:
```python
spark.sql("DESCRIBE HISTORY delta.`/mnt/delta/sales`").show()
```

**Output**:
```
+-------+-------------------+----------+------------------+
|version|timestamp          |operation|operationMetrics  |
+-------+-------------------+----------+------------------+
|5      |2024-01-16 10:00:00|UPDATE   |{"numUpdatedRows":1000000}|
|4      |2024-01-15 15:00:00|INSERT   |{"numInsertedRows":50000}|
|3      |2024-01-15 10:00:00|CREATE   |{"numFiles":1}|
+-------+-------------------+----------+------------------+
```

**Step 2: Query Before Mistake**:
```python
# Version 4 (before the bad UPDATE)
before_mistake = spark.read.format("delta") \
    .option("versionAsOf", 4) \
    .load("/mnt/delta/sales")

# Compare
current_total = spark.read.format("delta").load("/mnt/delta/sales") \
    .agg(sum("amount")).collect()[0][0]

before_total = before_mistake.agg(sum("amount")).collect()[0][0]

print(f"Current: ${current_total}")
print(f"Before mistake: ${before_total}")
```

**Step 3: Restore if Needed**:
```sql
-- Restore to version 4
RESTORE TABLE delta.`/mnt/delta/sales` TO VERSION AS OF 4;
```

**5. Use Cases**:
- ✅ **Audit**: "What did sales look like last week?"
- ✅ **Debug**: "Why did this calculation change?"
- ✅ **Rollback**: "Undo that bad update"
- ✅ **Reproducibility**: "Recreate last month's report"

**6. Limitations**:
- ⚠️ VACUUM removes old versions (default: 7 days)
- ⚠️ Can't time travel beyond retention period
- ⚠️ Storage cost (keeps old files)

**Key Points**:
- ✅ Version-based and timestamp-based queries
- ✅ Transaction log enables time travel
- ✅ Practical for audit, debug, rollback
- ⚠️ Limited by VACUUM retention

---

#### Q6: Unity Catalog vs Hive Metastore

**Question**: "What's the difference between Unity Catalog and Hive Metastore? When should you migrate?"

**Answer Structure**:

**1. Hive Metastore (Legacy)**:
- Traditional metadata store
- Limited to single workspace
- Basic permissions
- No cross-cloud support

**2. Unity Catalog (Modern)**:
- Centralized governance
- Multi-cloud support
- Fine-grained permissions
- Data lineage tracking
- Better security

**3. Key Differences**:

| Feature | Hive Metastore | Unity Catalog |
|---------|---------------|---------------|
| **Scope** | Single workspace | Multi-workspace, multi-cloud |
| **Permissions** | Basic (table-level) | Fine-grained (column/row-level) |
| **Lineage** | Limited | Full lineage tracking |
| **Security** | Basic | Advanced (PII masking, etc.) |
| **Cross-Cloud** | No | Yes (Delta Sharing) |
| **Future** | Legacy | Active development |

**4. When to Migrate**:

✅ **Migrate When**:
- Starting new projects
- Need fine-grained permissions
- Multi-cloud requirements
- Need data lineage
- Security compliance requirements

❌ **Don't Migrate When**:
- Legacy systems (too risky)
- Simple use cases (overkill)
- No governance requirements
- Small team (< 5 people)

**5. Migration Path**:

**Step 1: Register Existing Tables**:
```sql
-- Register Hive table in Unity Catalog
CREATE TABLE nike_prod.sales.raw_sales
USING DELTA
LOCATION '/mnt/delta/bronze/sales';
```

**Step 2: Update Code**:
```python
# Old (Hive)
spark.table("sales.raw_sales")

# New (Unity Catalog)
spark.table("nike_prod.sales.raw_sales")
```

**Step 3: Migrate Permissions**:
```sql
-- Migrate permissions
GRANT SELECT ON TABLE nike_prod.sales.raw_sales TO `analysts@nike.com`;
```

**Key Points**:
- ✅ Unity Catalog: Modern, multi-cloud, better security
- ✅ Hive: Legacy, single workspace, basic
- ✅ Migrate for new projects, stay on Hive for legacy

---

#### Q7: Troubleshoot Slow Delta Queries

**Question**: "A Delta query that used to take 30 seconds now takes 5 minutes. How do you debug this?"

**Answer Structure**:

**1. Common Causes**:
- Too many small files
- Data skew
- Missing partitions
- Outdated statistics
- Cluster resource issues

**2. Debugging Steps**:

**Step 1: Check Execution Plan**:
```python
# See what Spark is doing
spark.sql("EXPLAIN SELECT * FROM sales WHERE date = '2024-01-15'").show(truncate=False)
```

**Look for**:
- Full table scans (bad!)
- Partition pruning (good!)
- File count (too many = slow)

**Step 2: Check File Sizes**:
```python
# Check table details
spark.sql("DESCRIBE DETAIL delta.`/mnt/delta/sales`").show()

# Check file count
spark.sql("SELECT COUNT(*) as file_count FROM delta.`/mnt/delta/sales`").show()
```

**Step 3: Check Partitions**:
```python
# Verify partition pruning
spark.sql("SHOW PARTITIONS sales").show()

# Check if query uses partitions
# Good: Only scans relevant partitions
# Bad: Scans all partitions
```

**Step 4: Check Data Skew**:
```python
# Check data distribution
spark.sql("""
    SELECT date, COUNT(*) as row_count
    FROM sales
    GROUP BY date
    ORDER BY row_count DESC
""").show()
```

**3. Solutions**:

**Solution 1: Run OPTIMIZE** (Most Common):
```sql
-- Compact small files
OPTIMIZE delta.`/mnt/delta/sales`;

-- With Z-ORDER for better clustering
OPTIMIZE delta.`/mnt/delta/sales` ZORDER BY (customer_id, date);
```

**Solution 2: Fix Partitioning**:
```python
# Repartition if needed
df.repartition("date").write.format("delta").mode("overwrite").save("/mnt/delta/sales")
```

**Solution 3: Increase Cluster Size**:
```python
# More workers = faster
cluster_config = {"num_workers": 10}  # Was 2
```

**Solution 4: Use Liquid Clustering**:
```sql
-- Enable liquid clustering
ALTER TABLE sales CLUSTER BY (customer_id, date);
```

**4. Real-World Debugging**:

**Problem**: Query slow after many small appends

**Debug**:
```python
# Step 1: Check file count
spark.sql("DESCRIBE DETAIL sales").show()
# Result: 10,000 files! (was 100)

# Step 2: Check execution plan
spark.sql("EXPLAIN SELECT * FROM sales WHERE date = '2024-01-15'").show()
# Result: Scans 10,000 files

# Solution: OPTIMIZE
spark.sql("OPTIMIZE sales")
# Result: 100 files, query fast again!
```

**Key Points**:
- ✅ Check execution plan first
- ✅ Too many small files = slow
- ✅ OPTIMIZE is usually the fix
- ✅ Monitor file count regularly

---

#### Q8: Delta Lake vs Parquet - When to Use Each?

**Question**: "When should I use Delta Lake vs Parquet? What are the trade-offs?"

**Answer Structure**:

**1. Feature Comparison**:

| Feature | Delta Lake | Parquet |
|---------|-----------|---------|
| **Updates** | ✅ Yes (UPDATE, DELETE, MERGE) | ❌ No (append-only) |
| **ACID Transactions** | ✅ Yes | ❌ No |
| **Time Travel** | ✅ Yes | ❌ No |
| **Schema Evolution** | ✅ Yes | ⚠️ Limited |
| **Performance** | ✅ Excellent | ✅ Excellent |
| **Storage Cost** | ⚠️ Slightly higher | ✅ Lower |
| **Complexity** | ⚠️ More complex | ✅ Simpler |

**2. When to Use Delta Lake**:

✅ **Use Delta Lake When**:
- Need to update/delete data
- Need ACID guarantees
- Need time travel
- Building data lakehouse
- Multiple concurrent writers
- Need schema evolution

**Example**:
```python
# Need to update customer records
delta_table.update(condition="customer_id = 101", set={"status": "active"})
```

**3. When to Use Parquet**:

✅ **Use Parquet When**:
- Append-only workloads
- No updates needed
- Cost-sensitive projects
- Simple use cases
- One-time data exports
- Legacy systems

**Example**:
```python
# Simple append-only log
logs_df.write.format("parquet").mode("append").save("/data/logs")
```

**4. Real-World Decision**:

**Scenario**: Sales data that needs updates vs. audit logs (append-only)

**Sales Data → Delta Lake**:
```python
# Need to update/correct sales
sales_df.write.format("delta").save("/mnt/delta/sales")
# Can update, delete, time travel ✅
```

**Audit Logs → Parquet**:
```python
# Append-only, never update
logs_df.write.format("parquet").mode("append").save("/data/logs")
# Simpler, cheaper ✅
```

**5. Migration Path**:

**Parquet → Delta Lake**:
```python
# Read Parquet
parquet_df = spark.read.format("parquet").load("/data/sales")

# Write as Delta
parquet_df.write.format("delta").save("/mnt/delta/sales")
```

**Key Points**:
- ✅ Delta: Updates, ACID, time travel
- ✅ Parquet: Append-only, simpler, cheaper
- ✅ Choose based on requirements

---

#### Q9: How Do You Optimize a DLT Pipeline?

**Question**: "Your DLT pipeline is slow. How do you optimize it?"

**Answer Structure**:

**1. Common Performance Issues**:
- Processing all data instead of incremental
- Too many expectations
- No partitioning
- Large cluster overhead

**2. Optimization Strategies**:

**Strategy 1: Incremental Processing**:
```python
# Bad: Processes ALL data every run
@dlt.table(name="silver_sales")
def silver_sales():
    return dlt.read("bronze_sales")  # Reads everything!

# Good: Only process new data
@dlt.table(name="silver_sales")
def silver_sales():
    return dlt.read_stream("bronze_sales") \
        .filter(col("sale_date") >= current_date() - 1)  # Only last 24h
```

**Strategy 2: Optimize Expectations**:
```python
# Bad: Too many expensive expectations
@dlt.expect("check1", "complex_function(col1)")
@dlt.expect("check2", "another_complex_function(col2)")
# ... 20 more expectations

# Good: Essential expectations only
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
```

**Strategy 3: Partition Efficiently**:
```python
@dlt.table(name="silver_sales")
def silver_sales():
    return dlt.read("bronze_sales") \
        .withColumn("year", year("sale_date")) \
        .withColumn("month", month("sale_date")) \
        .withColumn("day", dayofmonth("sale_date"))
# Partition by date for faster queries
```

**Strategy 4: Right-Size Clusters**:
```python
# Use appropriate cluster size
# Too small = slow
# Too large = wasted cost
cluster_config = {
    "num_workers": 4,  # Right-sized for workload
    "node_type_id": "i3.xlarge"
}
```

**3. Monitoring**:
- Check DLT pipeline metrics
- Monitor execution time
- Check data quality violations
- Review cluster utilization

**4. Real-World Example**:

**Problem**: Pipeline takes 2 hours, processes 1M records daily

**Before**:
```python
@dlt.table(name="silver_sales")
def silver_sales():
    return dlt.read("bronze_sales")  # Processes 1M every day
```

**After**:
```python
@dlt.table(name="silver_sales")
def silver_sales():
    return dlt.read_stream("bronze_sales") \
        .filter(col("sale_date") >= current_date() - 1)  # Only 10K new
```

**Result**: 2 hours → 10 minutes ✅

**Key Points**:
- ✅ Use incremental processing
- ✅ Optimize expectations
- ✅ Partition efficiently
- ✅ Right-size clusters

---

#### Q10: Explain Change Data Feed (CDF)

**Question**: "What is Change Data Feed? Give me a practical use case."

**Answer Structure**:

**1. What is CDF?**
Tracks all changes (inserts, updates, deletes) to a Delta table.

**2. How to Enable**:
```sql
ALTER TABLE sales SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

**3. Reading CDF**:
```python
# Read all changes
changes = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 0) \
    .load("/mnt/delta/sales")
```

**4. CDF Output**:
```
+----+----------+-----------+----------+------------------+
|_change_type|sale_id    |customer_id|amount |_commit_version|
+----+----------+-----------+----------+------------------+
|insert      |SALE-003   |103        |120.00 |5               |
|update_preimage|SALE-001|101        |150.00 |6               | ← Old
|update_postimage|SALE-001|101       |140.00 |6               | ← New
|delete      |SALE-002   |102        |200.00 |7               |
+----+----------+-----------+----------+------------------+
```

**5. Use Case: Incremental Processing**:
```python
# Only process changed records (10K) instead of all (1M)
changes = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", last_processed_version) \
    .load("/mnt/delta/sales")

# Filter only inserts and updates
new_and_updated = changes.filter(
    col("_change_type").isin("insert", "update_postimage")
)

# Process only changed records
process(new_and_updated)  # 10K records instead of 1M!
```

**6. Use Case: Sync to Downstream**:
```python
# Sync changes to Snowflake
changes = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .load("/mnt/delta/sales")

# Handle inserts
inserts = changes.filter(col("_change_type") == "insert")
inserts.write.format("snowflake").mode("append").save()

# Handle updates
updates = changes.filter(col("_change_type") == "update_postimage")
updates.write.format("snowflake").mode("overwrite").save()
```

**Key Points**:
- ✅ Tracks all changes automatically
- ✅ Great for incremental processing
- ✅ Perfect for CDC (Change Data Capture)
- ✅ 10-100x faster than full table scan

---

### 17. System Design with Databricks

**Why This Section?**
System design questions are critical for senior roles. Master these patterns to design scalable Databricks architectures.

---

#### 17.1 Design Pattern: Medallion Architecture

**What is Medallion Architecture?**
A data organization pattern: Bronze (raw) → Silver (cleaned) → Gold (aggregated).

**Architecture Flow**:
```
┌─────────────────────────────────────────────────┐
│           Data Sources                          │
│  (S3, Kafka, Databases, APIs)                  │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│           BRONZE LAYER                         │
│  - Raw data (as-is)                            │
│  - No transformations                          │
│  - Partitioned by ingestion time               │
│  - Long retention (2+ years)                   │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│           SILVER LAYER                         │
│  - Cleaned & validated                         │
│  - Data quality checks                         │
│  - Schema enforcement                          │
│  - Deduplicated                                │
│  - Partitioned by business key                │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│           GOLD LAYER                           │
│  - Business-ready aggregates                  │
│  - Star schema (facts & dimensions)            │
│  - Optimized for queries                       │
│  - Partitioned for performance                 │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│           Analytics & ML                       │
│  (BI Tools, ML Models, APIs)                    │
└─────────────────────────────────────────────────┘
```

**Implementation with DLT**:
```python
import dlt
from pyspark.sql.functions import *

# BRONZE: Raw ingestion
@dlt.table(name="bronze_sales")
def bronze_sales():
    return spark.read.format("json").load("s3://raw/sales/")

# SILVER: Cleaned & validated
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_sales():
    return dlt.read("bronze_sales") \
        .withColumn("ingestion_time", current_timestamp()) \
        .dropDuplicates(["sale_id"])

# GOLD: Aggregated
@dlt.table(name="gold_daily_sales")
def gold_daily_sales():
    return dlt.read("silver_sales") \
        .groupBy("sale_date", "customer_id") \
        .agg(
            sum("amount").alias("daily_revenue"),
            count("*").alias("transaction_count")
        )
```

**When to Use**:
- ✅ Building data lakehouse
- ✅ Need data quality enforcement
- ✅ Multiple downstream consumers
- ✅ Long-term data retention

**Benefits**:
- ✅ Clear data lineage
- ✅ Quality enforcement at each layer
- ✅ Flexible for different use cases
- ✅ Easy to debug (check each layer)

---

#### 17.2 Real-World Design: 1TB/Day Pipeline

**Requirements**:
- **Volume**: 1TB/day = ~42GB/hour
- **Sources**: S3 (batch), Kafka (streaming), Databases (JDBC)
- **Latency**: Batch (hourly) + Real-time (optional)
- **Retention**: 2 years
- **Users**: 100+ analysts, 10+ engineers

**Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│                    Data Sources                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   S3     │  │  Kafka   │  │   DBs    │            │
│  │(42GB/hr) │  │(Streaming)│ │ (JDBC)   │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Databricks Workspace       │
        │                              │
        │  ┌────────────────────────┐ │
        │  │  Unity Catalog          │ │
        │  │  (Governance)           │ │
        │  └───────────┬────────────┘ │
        │              ↓               │
        │  ┌────────────────────────┐ │
        │  │  DLT Pipelines          │ │
        │  │  (Bronze/Silver/Gold)  │ │
        │  └───────────┬────────────┘ │
        │              ↓               │
        │  ┌────────────────────────┐ │
        │  │  Spark Clusters         │ │
        │  │  Auto-scaling (2-20)    │ │
        │  └────────────────────────┘ │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Delta Lake (S3)         │
        │  ┌────────────────────────┐ │
        │  │  Bronze: Partitioned   │ │
        │  │  by year/month/day/hour │ │
        │  └───────────┬────────────┘ │
        │              ↓               │
        │  ┌────────────────────────┐ │
        │  │  Silver: Quality       │ │
        │  │  checked, deduplicated  │ │
        │  └───────────┬────────────┘ │
        │              ↓               │
        │  ┌────────────────────────┐ │
        │  │  Gold: Aggregated     │ │
        │  │  Business-ready        │ │
        │  └────────────────────────┘ │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Analytics Layer         │
        │  ┌──────────┐  ┌──────────┐ │
        │  │ BI Tools │  │ ML Models│ │
        │  └──────────┘  └──────────┘ │
        └──────────────────────────────┘
```

**Component Details**:

**1. Ingestion**:
```python
# Batch from S3 (hourly)
@dlt.table(name="bronze_sales_batch")
def bronze_sales_batch():
    return spark.read.format("json") \
        .load("s3://raw/sales/hourly/") \
        .withColumn("source", lit("s3"))

# Streaming from Kafka
@dlt.table(name="bronze_sales_stream")
def bronze_sales_stream():
    return spark.readStream.format("kafka") \
        .option("subscribe", "sales") \
        .load() \
        .select(from_json(col("value").cast("string"), schema).alias("data")) \
        .select("data.*") \
        .withColumn("source", lit("kafka"))
```

**2. Processing**:
```python
# Silver: Cleaned
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_sales():
    batch = dlt.read("bronze_sales_batch")
    stream = dlt.read_stream("bronze_sales_stream")
    return batch.union(stream) \
        .withColumn("year", year("sale_date")) \
        .withColumn("month", month("sale_date")) \
        .withColumn("day", dayofmonth("sale_date"))
```

**3. Storage Strategy**:
```python
# Partition by date for efficient queries
sales_df.write.format("delta") \
    .partitionBy("year", "month", "day") \
    .save("/mnt/delta/silver/sales")
```

**4. Optimization Schedule**:
```python
# Daily OPTIMIZE (compact files)
spark.sql("OPTIMIZE delta.`/mnt/delta/silver/sales`")

# Weekly VACUUM (clean old files)
spark.sql("VACUUM delta.`/mnt/delta/silver/sales` RETAIN 7 DAYS")

# Enable Liquid Clustering
spark.sql("ALTER TABLE sales CLUSTER BY (customer_id, sale_date)")
```

**5. Scalability**:
- **Auto-scaling**: 2-20 workers based on load
- **Partitioning**: By date (year/month/day)
- **Optimization**: Daily OPTIMIZE, weekly VACUUM
- **Monitoring**: DLT dashboard, query performance

**6. Cost Optimization**:
- Job clusters (terminate after job)
- Auto-scaling (scale down when idle)
- Efficient partitioning (reduce scans)
- Regular optimization (reduce storage)

**Key Design Decisions**:
- ✅ Medallion architecture (Bronze/Silver/Gold)
- ✅ Partitioning by date (efficient queries)
- ✅ Auto-scaling clusters (handle variable load)
- ✅ Unity Catalog (governance)
- ✅ Daily optimization (performance)

---

#### 17.3 Design Pattern: Lambda Architecture (Batch + Streaming)

**What is Lambda Architecture?**
Process same data with both batch and streaming pipelines, then merge results.

**Architecture**:
```
Data Source (Kafka)
    ├── Batch Path (Spark)
    │   └── Process historical data
    └── Streaming Path (Spark Streaming)
        └── Process real-time data
    ↓
Merge Results
    ↓
Unified View
```

**Implementation**:
```python
# Batch path (processes all data daily)
@dlt.table(name="batch_sales_summary")
def batch_sales_summary():
    return spark.read.format("delta").load("/mnt/delta/bronze/sales") \
        .groupBy("sale_date") \
        .agg(sum("amount").alias("daily_revenue"))

# Streaming path (processes new data in real-time)
@dlt.table(name="streaming_sales_summary")
def streaming_sales_summary():
    return spark.readStream.format("kafka") \
        .option("subscribe", "sales") \
        .load() \
        .groupBy(window("timestamp", "1 day"), "sale_date") \
        .agg(sum("amount").alias("daily_revenue"))

# Merge (unified view)
@dlt.table(name="unified_sales_summary")
def unified_sales_summary():
    batch = dlt.read("batch_sales_summary")
    stream = dlt.read_stream("streaming_sales_summary")
    return batch.union(stream)
```

**When to Use**:
- ✅ Need both historical and real-time views
- ✅ Different processing logic for batch vs stream
- ✅ High accuracy requirements

---

#### 17.4 Design Pattern: Kappa Architecture (Streaming-Only)

**What is Kappa Architecture?**
Single streaming pipeline handles both real-time and historical data.

**Architecture**:
```
Data Source (Kafka)
    ↓
Single Streaming Pipeline
    ↓
Unified Results
```

**Implementation**:
```python
# Single streaming pipeline
@dlt.table(name="sales_summary")
def sales_summary():
    return spark.readStream.format("kafka") \
        .option("subscribe", "sales") \
        .option("startingOffsets", "earliest")  # Process all data
        .load() \
        .groupBy(window("timestamp", "1 day")) \
        .agg(sum("amount").alias("daily_revenue"))
```

**When to Use**:
- ✅ Simple use case
- ✅ Same logic for batch and stream
- ✅ Lower complexity

---

#### 17.5 Design Decisions & Trade-offs

**Decision 1: DLT vs Spark**

| Aspect | DLT | Spark |
|--------|-----|-------|
| **Development Speed** | Fast | Slower |
| **Data Quality** | Built-in | Manual |
| **Flexibility** | Limited | High |
| **Maintenance** | Low | High |
| **Use Case** | Standard pipelines | Custom logic |

**Decision 2: Delta vs Parquet**

| Aspect | Delta | Parquet |
|--------|-------|---------|
| **Updates** | Yes | No |
| **ACID** | Yes | No |
| **Performance** | Excellent | Excellent |
| **Cost** | Higher | Lower |
| **Use Case** | Data lakehouse | Append-only |

**Decision 3: Unity Catalog vs Hive**

| Aspect | Unity Catalog | Hive |
|--------|---------------|------|
| **Multi-cloud** | Yes | No |
| **Security** | Advanced | Basic |
| **Future** | Active | Legacy |
| **Use Case** | New projects | Legacy systems |

---

### 18. Troubleshooting Common Issues

**Why This Section?**
Real-world problems require real-world solutions. Master these to handle production issues confidently.

---

#### 18.1 Slow Query Performance

**Symptoms**:
- Query takes > 5 minutes (used to be 30 seconds)
- High CPU usage
- Timeout errors
- Spark UI shows long-running tasks

**Debugging Steps**:

**Step 1: Check Execution Plan**:
```python
# See what Spark is doing
spark.sql("EXPLAIN SELECT * FROM sales WHERE date = '2024-01-15'").show(truncate=False)
```

**Look for**:
- `Scan Delta` with high file count (bad!)
- `PartitionFilters` (good - partition pruning)
- `PushedFilters` (good - filter pushdown)

**Step 2: Check File Count**:
```python
# Check table details
spark.sql("DESCRIBE DETAIL delta.`/mnt/delta/sales`").show()

# Check number of files
# Good: < 100 files per partition
# Bad: > 1000 files per partition
```

**Step 3: Check Partition Pruning**:
```python
# Verify query uses partitions
spark.sql("SHOW PARTITIONS sales").show()

# Check if filter uses partition column
# Good: WHERE date = '2024-01-15' (date is partition)
# Bad: WHERE customer_id = 101 (not partitioned)
```

**Step 4: Check Data Skew**:
```python
# Check data distribution
spark.sql("""
    SELECT date, COUNT(*) as row_count, COUNT(DISTINCT customer_id) as customers
    FROM sales
    GROUP BY date
    ORDER BY row_count DESC
""").show()
```

**Solutions**:

**Solution 1: Run OPTIMIZE** (Most Common Fix):
```sql
-- Compact small files
OPTIMIZE delta.`/mnt/delta/sales`;

-- With Z-ORDER for better clustering
OPTIMIZE delta.`/mnt/delta/sales` ZORDER BY (customer_id, date);
```

**Solution 2: Enable Liquid Clustering**:
```sql
-- Better than Z-ORDER (automatic)
ALTER TABLE sales CLUSTER BY (customer_id, date);
```

**Solution 3: Increase Cluster Size**:
```python
# More workers = faster
cluster_config = {
    "num_workers": 10,  # Was 2
    "node_type_id": "i3.xlarge"
}
```

**Solution 4: Fix Partitioning**:
```python
# Repartition if needed
df.repartition("date").write.format("delta").mode("overwrite").save("/mnt/delta/sales")
```

**Real-World Example**:

**Problem**: Query slow after many small appends

**Before**:
```python
# 10,000 small files (1MB each)
spark.sql("SELECT * FROM sales WHERE date = '2024-01-15'")
# Time: 5 minutes
```

**After OPTIMIZE**:
```sql
OPTIMIZE delta.`/mnt/delta/sales`;
-- Result: 100 files (128MB each)
```

**After Query**:
```python
spark.sql("SELECT * FROM sales WHERE date = '2024-01-15'")
# Time: 30 seconds ✅
```

---

#### 18.2 Out of Memory (OOM) Errors

**Symptoms**:
- `java.lang.OutOfMemoryError: Java heap space`
- `java.lang.OutOfMemoryError: Unable to acquire X bytes of memory`
- Job fails with memory errors
- Spark UI shows high memory usage

**Common Causes**:
1. Too much data in single partition
2. Data skew (one partition huge)
3. Insufficient cluster memory
4. Broadcasting large table
5. Collecting too much data to driver

**Solutions**:

**Solution 1: Increase Executor Memory**:
```python
spark = SparkSession.builder \
    .config("spark.executor.memory", "16g") \
    .config("spark.executor.memoryFraction", "0.8") \
    .getOrCreate()
```

**Solution 2: Fix Data Skew**:
```python
# Add salt to skewed column
df.withColumn("salt", (rand() * 100).cast("int")) \
    .repartition(200, "customer_id", "salt")
```

**Solution 3: Avoid Broadcasting Large Tables**:
```python
# Bad: Broadcasting 10M row table
large_table = spark.table("large_table")  # 10M rows
df.join(broadcast(large_table), "id")  # OOM!

# Good: Regular join
df.join(large_table, "id")
```

**Solution 4: Repartition**:
```python
# Increase partitions to reduce data per partition
df.repartition(200)  # Was 50 partitions
```

**Solution 5: Avoid Collecting to Driver**:
```python
# Bad: Collecting 1M rows to driver
results = df.collect()  # OOM!

# Good: Write to storage
df.write.format("delta").save("/mnt/delta/results")
```

**Real-World Example**:

**Problem**: OOM error when joining sales with customers

**Before**:
```python
# Broadcasting 10M row customer table
customers = spark.table("customers")  # 10M rows
sales.join(broadcast(customers), "customer_id")  # OOM!
```

**After**:
```python
# Regular join (Spark handles it)
sales.join(customers, "customer_id")  # Works! ✅
```

---

#### 18.3 DLT Pipeline Failures

**Symptoms**:
- Pipeline fails repeatedly
- Data quality violations
- Timeout errors
- "Expectation failed" errors

**Debugging**:

**Step 1: Check DLT Logs**:
```python
# View pipeline run history
# In Databricks UI: Workflows → Your Pipeline → Runs
```

**Step 2: Check Data Quality Metrics**:
```python
# View expectation violations
# In Databricks UI: Data Quality tab
```

**Step 3: Check Source Data**:
```python
# Verify source data quality
bronze = spark.read.format("delta").load("/mnt/delta/bronze/sales")
bronze.filter(col("amount") < 0).count()  # Check for violations
```

**Solutions**:

**Solution 1: Adjust Expectations**:
```python
# Too strict? Relax expectations
@dlt.expect("valid_amount", "amount > 0")  # Was: amount > 100
```

**Solution 2: Use expect_or_drop**:
```python
# Drop bad records instead of failing
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
```

**Solution 3: Add Error Handling**:
```python
@dlt.table(name="silver_sales")
def silver_sales():
    try:
        return dlt.read("bronze_sales").filter(col("amount") > 0)
    except Exception as e:
        # Log error, return empty DataFrame
        print(f"Error: {e}")
        return spark.createDataFrame([], schema)
```

**Solution 4: Increase Timeout**:
```python
# In workflow configuration
{
    "timeout_seconds": 3600  # Was 1800
}
```

---

#### 18.4 Delta Table Corruption

**Symptoms**:
- Can't read table
- `DeltaTableException: Table not found`
- Transaction log errors
- Missing files

**Solutions**:

**Solution 1: Use FSCK to Repair**:
```python
# Check and repair table
spark.sql("REPAIR TABLE sales")
```

**Solution 2: Restore from Backup**:
```python
# Restore to previous version
spark.sql("RESTORE TABLE sales TO VERSION AS OF 10")
```

**Solution 3: Recreate Table**:
```python
# Last resort: Recreate from source
source_data = spark.read.format("delta").load("/mnt/delta/bronze/sales")
source_data.write.format("delta").mode("overwrite").save("/mnt/delta/silver/sales")
```

**Prevention**:
- ✅ Never delete `_delta_log/` directory
- ✅ Use VACUUM carefully (check retention)
- ✅ Backup important tables
- ✅ Monitor table health

---

#### 18.5 Streaming Checkpoint Issues

**Symptoms**:
- Duplicate records
- Lost data
- Can't resume stream
- Checkpoint errors

**Solutions**:

**Solution 1: Never Delete Checkpoint Directory**:
```python
# ⚠️ NEVER DO THIS:
# dbutils.fs.rm("/mnt/delta/checkpoints/sales", True)

# If deleted, stream restarts from beginning (duplicates!)
```

**Solution 2: Use Idempotent Writes**:
```python
# Use MERGE instead of INSERT
delta_table.alias("target").merge(
    stream_df.alias("source"),
    "target.id = source.id"
).whenNotMatchedInsertAll().execute()
```

**Solution 3: Monitor Checkpoint Health**:
```python
# Check checkpoint directory
dbutils.fs.ls("/mnt/delta/checkpoints/sales")
```

**Solution 4: Handle Checkpoint Corruption**:
```python
# If checkpoint corrupted, start from specific offset
stream_df = spark.readStream \
    .format("kafka") \
    .option("startingOffsets", "{\"sales\":{\"0\":12345}}") \
    .load()
```

---

#### 18.6 Cost Issues

**Symptoms**:
- Unexpected high costs
- Cluster running 24/7
- Too many small files (storage cost)
- Inefficient queries

**Solutions**:

**Solution 1: Enable Autotermination**:
```python
cluster_config = {
    "autotermination_minutes": 30  # Auto-terminate idle clusters
}
```

**Solution 2: Use Job Clusters**:
```python
# Job clusters terminate after job (cost-effective)
job_cluster = {
    "new_cluster": {
        "autotermination_minutes": 0  # Terminate immediately
    }
}
```

**Solution 3: Optimize Delta Tables**:
```sql
-- Reduce storage costs
OPTIMIZE delta.`/mnt/delta/sales`;
VACUUM delta.`/mnt/delta/sales` RETAIN 7 DAYS;
```

**Solution 4: Monitor Costs**:
```python
# Use Databricks SQL to query usage
# Track cluster hours, storage, compute
```

**Solution 5: Right-Size Clusters**:
```python
# Don't over-provision
cluster_config = {
    "num_workers": 2,  # Start small, scale up if needed
    "node_type_id": "i3.xlarge"  # Right size
}
```

---

### 19. Hands-On Exercises

**Why This Section?**
Practice makes perfect! These exercises help you apply what you've learned.

---

#### Exercise 1: Build Your First Delta Table

**Objective**: Create a Delta table from raw JSON data.

**Given**:
- Raw data: `s3://nike-raw/sales/2024-01-15.json`
- Schema: `sale_id`, `customer_id`, `amount`, `sale_date`

**Task**:
1. Read JSON data
2. Write as Delta table
3. Query the table
4. Check table history

**Solution**:
```python
# Step 1: Read JSON
raw_sales = spark.read.format("json").load("s3://nike-raw/sales/2024-01-15.json")

# Step 2: Write as Delta
raw_sales.write.format("delta").save("/mnt/delta/bronze/sales")

# Step 3: Query
sales = spark.read.format("delta").load("/mnt/delta/bronze/sales")
sales.show()

# Step 4: Check history
spark.sql("DESCRIBE HISTORY delta.`/mnt/delta/bronze/sales`").show()
```

---

#### Exercise 2: Create a DLT Pipeline

**Objective**: Build Bronze → Silver → Gold pipeline with data quality checks.

**Given**:
- Bronze table: `bronze_sales` (already exists)
- Requirements:
  - Silver: Clean data (amount > 0, customer_id not null)
  - Gold: Daily aggregates (sum of amount by date)

**Task**:
1. Create Silver table with quality checks
2. Create Gold table with aggregates
3. Test with sample data

**Solution**:
```python
import dlt
from pyspark.sql.functions import *

# Silver: Cleaned
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_sales():
    return dlt.read("bronze_sales") \
        .withColumn("ingestion_time", current_timestamp())

# Gold: Aggregated
@dlt.table(name="gold_daily_sales")
def gold_daily_sales():
    return dlt.read("silver_sales") \
        .groupBy("sale_date") \
        .agg(
            sum("amount").alias("daily_revenue"),
            count("*").alias("transaction_count")
        )
```

---

#### Exercise 3: Optimize a Slow Query

**Objective**: Optimize a query that takes 5 minutes.

**Given**:
- Query: `SELECT * FROM sales WHERE customer_id = 101 AND date = '2024-01-15'`
- Problem: Takes 5 minutes, scans 10,000 files

**Task**:
1. Identify the problem
2. Apply optimization
3. Verify improvement

**Solution**:
```python
# Step 1: Check file count
spark.sql("DESCRIBE DETAIL delta.`/mnt/delta/sales`").show()
# Result: 10,000 files (problem!)

# Step 2: Run OPTIMIZE
spark.sql("OPTIMIZE delta.`/mnt/delta/sales` ZORDER BY (customer_id, date)")

# Step 3: Verify
spark.sql("SELECT * FROM sales WHERE customer_id = 101 AND date = '2024-01-15'")
# Result: 30 seconds ✅
```

---

#### Exercise 4: Design a Pipeline

**Objective**: Design architecture for 100GB/day pipeline.

**Given**:
- Volume: 100GB/day
- Sources: S3 (batch), Kafka (streaming)
- Requirements: Bronze/Silver/Gold layers

**Task**:
1. Design architecture
2. Choose components
3. Implement pipeline

**Solution**:
```python
# Architecture: Medallion (Bronze/Silver/Gold)

# Bronze: Raw ingestion
@dlt.table(name="bronze_sales")
def bronze_sales():
    batch = spark.read.format("json").load("s3://raw/sales/")
    stream = spark.readStream.format("kafka") \
        .option("subscribe", "sales").load()
    return batch.union(stream)

# Silver: Cleaned
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
def silver_sales():
    return dlt.read("bronze_sales")

# Gold: Aggregated
@dlt.table(name="gold_daily_sales")
def gold_daily_sales():
    return dlt.read("silver_sales") \
        .groupBy("sale_date") \
        .agg(sum("amount").alias("daily_revenue"))
```

---

### 20. Edge Cases & Advanced Scenarios

**Why This Section?**
Real-world scenarios that test your deep understanding.

---

#### 20.1 Handling Schema Evolution

**Scenario**: Your sales data now includes a new `discount_code` field, but old records don't have it.

**Solution**:
```python
# Enable schema evolution
new_sales_df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/mnt/delta/sales")

# Result:
# - Old records: discount_code = NULL
# - New records: discount_code = "SAVE10"
```

**Best Practice**:
- ✅ Always enable `mergeSchema` for evolving schemas
- ✅ Use nullable columns for new fields
- ✅ Monitor schema changes

---

#### 20.2 Migrating from Hive to Unity Catalog

**Scenario**: You have 100 tables in Hive Metastore. How do you migrate to Unity Catalog?

**Solution**:
```python
# Step 1: List all Hive tables
hive_tables = spark.sql("SHOW TABLES IN default").collect()

# Step 2: Register each in Unity Catalog
for table in hive_tables:
    table_name = table.tableName
    location = spark.sql(f"DESCRIBE FORMATTED {table_name}") \
        .filter(col("col_name") == "Location") \
        .select("data_type").collect()[0][0]
    
    # Register in Unity Catalog
    spark.sql(f"""
        CREATE TABLE nike_prod.sales.{table_name}
        USING DELTA
        LOCATION '{location}'
    """)
```

**Best Practice**:
- ✅ Migrate incrementally (test with few tables first)
- ✅ Update code to use new catalog paths
- ✅ Keep Hive tables until migration verified

---

#### 20.3 Multi-Region Deployment

**Scenario**: Your data is in US, but you need to serve users in EU. How do you handle this?

**Solution**:
```python
# Option 1: Delta Sharing (read-only)
# Share US data with EU workspace
CREATE SHARE nike_sales_share;
ALTER SHARE nike_sales_share ADD TABLE nike_prod.sales.raw_sales;

# EU workspace accesses via Delta Sharing
CREATE CATALOG eu_nike USING DELTASHARING LOCATION '...';
SELECT * FROM eu_nike.nike_sales_share.raw_sales;

# Option 2: Replicate data (write to both regions)
# US: Primary write
sales_df.write.format("delta").save("s3://us-bucket/sales")

# EU: Replicate (async)
sales_df.write.format("delta").save("s3://eu-bucket/sales")
```

**Best Practice**:
- ✅ Use Delta Sharing for read-only cross-region
- ✅ Replicate for write access in multiple regions
- ✅ Consider latency and cost

---

#### 20.4 Disaster Recovery

**Scenario**: Your Delta table is corrupted. How do you recover?

**Solution**:
```python
# Step 1: Check if recoverable
spark.sql("REPAIR TABLE sales")

# Step 2: If not, restore from backup
spark.sql("RESTORE TABLE sales TO VERSION AS OF 10")

# Step 3: If no backup, recreate from source
source = spark.read.format("delta").load("/mnt/delta/bronze/sales")
source.write.format("delta").mode("overwrite").save("/mnt/delta/silver/sales")
```

**Best Practice**:
- ✅ Regular backups (copy `_delta_log/` directory)
- ✅ Test restore procedures
- ✅ Monitor table health

---

#### 20.5 Handling Large Schema Changes

**Scenario**: You need to rename 50 columns in a 1TB table. How do you do it?

**Solution**:
```python
# Option 1: Use ALTER TABLE (if supported)
spark.sql("ALTER TABLE sales RENAME COLUMN old_name TO new_name")

# Option 2: Recreate table (for large changes)
# Step 1: Read with new schema
new_schema_df = spark.read.format("delta").load("/mnt/delta/sales") \
    .withColumnRenamed("old_name", "new_name")

# Step 2: Write to new location
new_schema_df.write.format("delta").save("/mnt/delta/sales_v2")

# Step 3: Swap tables
spark.sql("DROP TABLE sales")
spark.sql("ALTER TABLE sales_v2 RENAME TO sales")
```

**Best Practice**:
- ✅ Test schema changes on sample data first
- ✅ Use versioning for large changes
- ✅ Plan downtime if needed

---

## 💡 Complete End-to-End Example

**What We're Building**: Complete ETL pipeline from raw data to analytics.

**Step 1: Raw Data** (S3):
```json
{"sale_id": "SALE-001", "customer_id": 101, "product_id": 501, "amount": 150.00, "sale_date": "2024-01-15"}
{"sale_id": "SALE-002", "customer_id": 102, "product_id": 502, "amount": 200.00, "sale_date": "2024-01-15"}
```

**Step 2: Bronze Layer** (Raw ingestion):
```python
import dlt

@dlt.table(name="bronze_sales")
def bronze_sales():
    return spark.read.format("json").load("s3://nike-raw/sales/")
```

**Step 3: Silver Layer** (Cleaned):
```python
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_sales():
    return dlt.read("bronze_sales") \
        .withColumn("ingestion_time", current_timestamp())
```

**Step 4: Gold Layer** (Aggregated):
```python
@dlt.table(name="gold_daily_sales")
def gold_daily_sales():
    return dlt.read("silver_sales") \
        .groupBy("sale_date", "customer_id") \
        .agg(
            sum("amount").alias("daily_revenue"),
            count("*").alias("transaction_count")
        )
```

**Final Result**:
```
gold_daily_sales:
sale_date  | customer_id | daily_revenue | transaction_count
2024-01-15 | 101         | 150.00        | 1
2024-01-15 | 102         | 200.00        | 1
```

---

## ✅ Best Practices Summary

### Delta Lake
- ✅ Use Delta Lake for all tables
- ✅ Run OPTIMIZE regularly (daily/weekly)
- ✅ VACUUM old files (weekly/monthly)
- ✅ Use Z-ORDER on filtered columns
- ✅ Enable schema evolution carefully

### DLT
- ✅ Use DLT for new pipelines
- ✅ Add data quality expectations
- ✅ Use incremental processing
- ✅ Monitor pipeline health

### Performance
- ✅ Right-size clusters
- ✅ Optimize Spark configs
- ✅ Handle data skew
- ✅ Use broadcast joins for small tables
- ✅ Partition data efficiently

### Cost
- ✅ Use autoscaling
- ✅ Enable autotermination
- ✅ Optimize Delta tables
- ✅ Monitor costs regularly

### Governance
- ✅ Use Unity Catalog
- ✅ Implement column-level security
- ✅ Mask PII data
- ✅ Track data lineage

---

## 🎯 Next Steps

Practice building:
- End-to-end pipelines
- Real-time streaming
- Data quality checks
- Cost optimization

**Study Time**: Spend 1-2 weeks on Databricks, build real projects!

---

## 📚 Additional Resources

- **Databricks Documentation**: https://docs.databricks.com/
- **Delta Lake Documentation**: https://delta.io/
- **Spark Documentation**: https://spark.apache.org/docs/latest/

---

**Keep Building! 🚀**
