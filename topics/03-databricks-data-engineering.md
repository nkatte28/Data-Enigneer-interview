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

**Nike Store Example - Architecture**:
```
Data Sources (S3, Kafka, Databases)
    ↓
Databricks Workspace
    ├── Notebooks (ETL code)
    ├── Jobs (Scheduled pipelines)
    ├── Clusters (Compute)
    └── Unity Catalog (Governance)
    ↓
Delta Lake (Bronze/Silver/Gold)
    ↓
Analytics (BI Tools, ML Models)
```

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

**New Data to Add**:
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

**Scenario**: We receive updated sales data. Some sales already exist (update), some are new (insert).

**Existing Data**:
```
sale_id   | customer_id | amount
SALE-001  | 101         | 135.00
SALE-002  | 102         | 200.00
```

**New/Updated Data**:
```python
updates_df = spark.createDataFrame([
    ("SALE-001", 101, 140.00),  # Updated amount
    ("SALE-003", 103, 120.00)   # New sale
], ["sale_id", "customer_id", "amount"])
```

**Merge Code**:
```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")

# Merge: Update if exists, insert if new
delta_table.alias("target").merge(
    updates_df.alias("source"),
    "target.sale_id = source.sale_id"  # Match on sale_id
).whenMatchedUpdateAll() \    # If match found → update
 .whenNotMatchedInsertAll() \  # If no match → insert
 .execute()
```

**Result**:
```
sale_id   | customer_id | amount
SALE-001  | 101         | 140.00  ← Updated!
SALE-002  | 102         | 200.00  ← Unchanged
SALE-003  | 103         | 120.00  ← Inserted!
```

**Operation 4: Delete**

**What We're Doing**: Remove old sales data (older than 2 years).

```python
# Delete sales older than 2 years
delta_table.delete("sale_date < '2022-01-01'")
```

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

### 5. Delta Live Tables (DLT) - Declarative Pipelines

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

### 6. Spark Structured Streaming - Real-Time Processing

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

### 7. Delta Live Tables + Structured Streaming

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

### 8. Unity Catalog - Data Governance

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

### 9. Reading from Different Sources

#### 9.1 Snowflake

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

#### 9.2 Apache Iceberg

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

#### 9.3 Other Sources

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

### 10. Spark Job Optimization

#### 10.1 Performance Tuning - Key Configs

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

#### 10.2 Handling Data Skew

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

#### 10.3 Memory Optimization

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

#### 10.4 Processing Too Much Data - Strategies

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

### 11. Multi-Cloud Data Sharing

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

### 12. Data Governance & PII Protection

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

### 13. Cost Optimization

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
