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

### 2. Databricks Workflows

**Workflow**: A sequence of tasks that run together (like a DAG in Airflow).

#### 2.1 Creating a Workflow

**Nike Store Example - Sales Pipeline Workflow**:

```python
# Workflow: Daily Sales Processing
# Tasks:
# 1. Ingest raw sales data from S3
# 2. Clean and validate data
# 3. Transform to Silver layer
# 4. Aggregate to Gold layer
# 5. Send alerts if errors

from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Task 1: Ingest Raw Data
def ingest_raw_sales():
    spark = SparkSession.builder.appName("IngestSales").getOrCreate()
    
    raw_sales = spark.read.format("json").load("s3://nike-raw/sales/")
    raw_sales.write.format("delta").mode("append").save("/mnt/delta/bronze/sales")
    
    return raw_sales.count()

# Task 2: Clean Data
def clean_sales_data():
    spark = SparkSession.builder.appName("CleanSales").getOrCreate()
    
    bronze = spark.read.format("delta").load("/mnt/delta/bronze/sales")
    
    cleaned = bronze.filter(
        col("sale_id").isNotNull() &
        col("customer_id").isNotNull() &
        col("amount") > 0
    )
    
    cleaned.write.format("delta").mode("overwrite").save("/mnt/delta/silver/sales")
    
    return cleaned.count()

# Task 3: Transform to Gold
def create_gold_aggregates():
    spark = SparkSession.builder.appName("GoldAggregates").getOrCreate()
    
    silver = spark.read.format("delta").load("/mnt/delta/silver/sales")
    
    gold = silver.groupBy("date", "customer_id", "product_id") \
        .agg(
            sum("amount").alias("total_revenue"),
            sum("quantity").alias("total_quantity"),
            count("*").alias("transaction_count")
        )
    
    gold.write.format("delta").mode("overwrite").save("/mnt/delta/gold/sales_summary")
    
    return gold.count()
```

#### 2.2 Workflow Configuration (JSON)

```json
{
  "name": "Daily Sales Pipeline",
  "email_notifications": {
    "on_success": ["team@nike.com"],
    "on_failure": ["alerts@nike.com"]
  },
  "tasks": [
    {
      "task_key": "ingest_raw_sales",
      "spark_python_task": {
        "python_file": "dbfs:/scripts/ingest_sales.py",
        "parameters": ["--date", "{{yesterday}}"]
      },
      "libraries": [{"pypi": {"package": "boto3"}}],
      "new_cluster": {
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2
      }
    },
    {
      "task_key": "clean_sales_data",
      "depends_on": [{"task_key": "ingest_raw_sales"}],
      "spark_python_task": {
        "python_file": "dbfs:/scripts/clean_sales.py"
      },
      "existing_cluster_id": "cluster-123"
    },
    {
      "task_key": "create_gold_aggregates",
      "depends_on": [{"task_key": "clean_sales_data"}],
      "spark_sql_task": {
        "sql_file": "dbfs:/scripts/gold_aggregates.sql",
        "warehouse_id": "warehouse-456"
      }
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "America/New_York"
  },
  "max_concurrent_runs": 1
}
```

#### 2.3 Workflow Best Practices

**1. Task Dependencies**:
- Use `depends_on` to create execution order
- Parallelize independent tasks

**2. Error Handling**:
- Set retry policies
- Configure email alerts
- Use try-catch in code

**3. Resource Management**:
- Reuse clusters when possible
- Use job clusters for one-time jobs
- Set appropriate cluster sizes

**4. Monitoring**:
- Check workflow run history
- Monitor task durations
- Set up alerts for failures

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

**Nike Store Example - Why Delta Lake?**

**Problem with Parquet**:
```python
# Parquet: Can't update, no transactions
sales.write.format("parquet").mode("overwrite").save("/data/sales")
# If job fails halfway, data is corrupted!
```

**Solution with Delta Lake**:
```python
# Delta: ACID transactions, can update
sales.write.format("delta").mode("overwrite").save("/mnt/delta/sales")
# If job fails, previous version is intact!
```

#### 3.2 Creating Delta Tables

**Method 1: Write as Delta Format**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("DeltaExample").getOrCreate()

# Create Delta table from DataFrame
sales_df = spark.read.json("s3://nike-raw/sales/")

sales_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/mnt/delta/bronze/sales")

# Read Delta table
sales = spark.read.format("delta").load("/mnt/delta/bronze/sales")
```

**Method 2: Create Delta Table (SQL)**
```sql
-- Create Delta table
CREATE TABLE IF NOT EXISTS bronze.sales
USING DELTA
LOCATION '/mnt/delta/bronze/sales'
AS
SELECT * FROM json.`s3://nike-raw/sales/`;

-- Or create empty table with schema
CREATE TABLE bronze.sales (
    sale_id BIGINT,
    customer_id BIGINT,
    product_id BIGINT,
    amount DECIMAL(10,2),
    sale_date TIMESTAMP
) USING DELTA
LOCATION '/mnt/delta/bronze/sales';
```

**Method 3: Convert Existing Parquet to Delta**
```python
# Convert Parquet table to Delta
spark.sql("""
    CONVERT TO DELTA parquet.`/mnt/data/sales`
""")
```

#### 3.3 Delta Lake Operations

**Insert**:
```python
# Append new data
new_sales.write.format("delta").mode("append").save("/mnt/delta/bronze/sales")
```

**Update**:
```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")

# Update records
delta_table.update(
    condition="customer_id = 101",
    set={"amount": "amount * 1.1"}  # 10% discount
)
```

**Upsert (Merge)**:
```python
from delta.tables import DeltaTable
from pyspark.sql.functions import *

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")

# Merge new data with existing
delta_table.alias("target").merge(
    updates_df.alias("source"),
    "target.sale_id = source.sale_id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

**Delete**:
```python
delta_table.delete("sale_date < '2024-01-01'")  # Delete old records
```

---

### 4. Delta Lake Advanced Features

#### 4.1 Time Travel

**What is Time Travel?**
Query historical versions of your data.

**Nike Store Example**:

```python
# Read current version
current_sales = spark.read.format("delta").load("/mnt/delta/bronze/sales")

# Read version 5 (historical)
version_5 = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("/mnt/delta/bronze/sales")

# Read timestamp (as of specific time)
as_of_time = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 10:00:00") \
    .load("/mnt/delta/bronze/sales")
```

**SQL Time Travel**:
```sql
-- Query version 5
SELECT * FROM delta.`/mnt/delta/bronze/sales` VERSION AS OF 5;

-- Query as of timestamp
SELECT * FROM delta.`/mnt/delta/bronze/sales` TIMESTAMP AS OF '2024-01-15 10:00:00';

-- See history
DESCRIBE HISTORY delta.`/mnt/delta/bronze/sales`;
```

**Use Cases**:
- ✅ Audit: "What did the data look like yesterday?"
- ✅ Rollback: Restore to previous version
- ✅ Reproduce: Run same query on historical data
- ✅ Debug: Compare current vs historical

**Example - Restore Previous Version**:
```python
# Restore to version 10
spark.sql("""
    RESTORE TABLE delta.`/mnt/delta/bronze/sales` TO VERSION AS OF 10
""")
```

#### 4.2 VACUUM

**What is VACUUM?**
Removes old files that are no longer needed (after retention period).

**Why VACUUM?**
- Saves storage costs
- Improves performance (fewer files to scan)
- Cleans up deleted/updated data files

**Nike Store Example**:

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")

# VACUUM files older than 7 days (default retention)
delta_table.vacuum()

# VACUUM with custom retention (hours)
delta_table.vacuum(168)  # 7 days = 168 hours
```

**SQL VACUUM**:
```sql
-- VACUUM files older than retention period
VACUUM delta.`/mnt/delta/bronze/sales`;

-- VACUUM with custom retention (hours)
VACUUM delta.`/mnt/delta/bronze/sales` RETAIN 168 HOURS;

-- Dry run (see what would be deleted)
VACUUM delta.`/mnt/delta/bronze/sales` DRY RUN;
```

**Important Notes**:
- ⚠️ Default retention: 7 days (168 hours)
- ⚠️ Can't time travel beyond retention period after VACUUM
- ⚠️ Use `DRY RUN` first to see what will be deleted

**Best Practices**:
- Run VACUUM regularly (weekly/monthly)
- Set appropriate retention based on time travel needs
- Monitor storage savings

#### 4.3 OPTIMIZE

**What is OPTIMIZE?**
Compacts small files into larger files for better performance.

**Why OPTIMIZE?**
- Faster queries (fewer files to read)
- Better compression
- Improved performance

**Nike Store Example**:

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/mnt/delta/bronze/sales")

# Optimize table (compact files)
delta_table.optimize().execute()
```

**SQL OPTIMIZE**:
```sql
-- Optimize entire table
OPTIMIZE delta.`/mnt/delta/bronze/sales`;

-- Optimize specific partition
OPTIMIZE delta.`/mnt/delta/bronze/sales`
WHERE date = '2024-01-15';
```

**Z-ORDER (Multi-dimensional Clustering)**:
```sql
-- Z-ORDER on multiple columns (for better query performance)
OPTIMIZE delta.`/mnt/delta/bronze/sales`
ZORDER BY (customer_id, product_id, date);
```

**What Z-ORDER Does**:
- Co-locates related data in same files
- Improves filter performance
- Best for columns used in WHERE clauses

**Example - Z-ORDER Benefits**:
```sql
-- Before Z-ORDER: Scans all files
SELECT * FROM sales WHERE customer_id = 101 AND date = '2024-01-15';
-- Scans: 1000 files

-- After Z-ORDER: Scans only relevant files
SELECT * FROM sales WHERE customer_id = 101 AND date = '2024-01-15';
-- Scans: 10 files (90% reduction!)
```

**Best Practices**:
- Run OPTIMIZE after large writes
- Use Z-ORDER on frequently filtered columns
- Don't Z-ORDER too many columns (2-3 is optimal)
- Schedule OPTIMIZE regularly (daily/weekly)

#### 4.4 Delta Lake Schema Evolution

**What is Schema Evolution?**
Add columns without breaking existing data.

**Nike Store Example**:

```python
# Original schema
sales_df = spark.createDataFrame([
    (1, 101, 501, 150.00, "2024-01-15")
], ["sale_id", "customer_id", "product_id", "amount", "date"])

sales_df.write.format("delta").save("/mnt/delta/bronze/sales")

# Add new column (discount_amount)
new_sales_df = spark.createDataFrame([
    (2, 102, 502, 200.00, "2024-01-16", 20.00)  # Added discount_amount
], ["sale_id", "customer_id", "product_id", "amount", "date", "discount_amount"])

# Merge schema automatically
new_sales_df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/mnt/delta/bronze/sales")

# Old records have NULL for discount_amount
# New records have discount_amount value
```

**Schema Evolution Modes**:
```python
# Allow schema evolution
.option("mergeSchema", "true")

# Overwrite schema (drops old columns)
.option("overwriteSchema", "true")
```

---

### 5. Delta Live Tables (DLT)

**What is DLT?**
Declarative framework for building reliable data pipelines with automatic testing and monitoring.

#### 5.1 DLT Concepts

**Key Features**:
- ✅ Declarative: Define what you want, not how
- ✅ Automatic testing: Data quality checks built-in
- ✅ Monitoring: Built-in observability
- ✅ Incremental processing: Only process new/changed data
- ✅ Dependency management: Automatic DAG creation

**Nike Store Example - DLT Pipeline**:

```python
import dlt
from pyspark.sql.functions import *

# Bronze Layer: Raw data ingestion
@dlt.table(
    name="bronze_sales",
    comment="Raw sales data from S3"
)
def bronze_sales():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .option("cloudFiles.schemaLocation", "/mnt/delta/checkpoints/bronze_sales") \
        .load("s3://nike-raw/sales/")

# Silver Layer: Cleaned and validated data
@dlt.table(
    name="silver_sales",
    comment="Cleaned sales data with quality checks"
)
@dlt.expect("valid_sale_id", "sale_id IS NOT NULL")
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_sales():
    return dlt.read("bronze_sales") \
        .filter(col("sale_date").isNotNull()) \
        .withColumn("ingestion_timestamp", current_timestamp()) \
        .select(
            col("sale_id"),
            col("customer_id"),
            col("product_id"),
            col("amount"),
            col("quantity"),
            to_date(col("sale_date")).alias("sale_date"),
            col("ingestion_timestamp")
        )

# Gold Layer: Aggregated data
@dlt.table(
    name="gold_daily_sales_summary",
    comment="Daily sales aggregates by customer and product"
)
def gold_daily_sales_summary():
    return dlt.read("silver_sales") \
        .groupBy("sale_date", "customer_id", "product_id") \
        .agg(
            sum("amount").alias("total_revenue"),
            sum("quantity").alias("total_quantity"),
            count("*").alias("transaction_count"),
            max("ingestion_timestamp").alias("last_updated")
        )
```

#### 5.2 DLT Expectations (Data Quality)

**Expectation Types**:

```python
# Expect: Record violation but continue
@dlt.expect("valid_amount", "amount > 0")

# Expect or Drop: Drop records that fail
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")

# Expect or Fail: Fail pipeline if violation
@dlt.expect_or_fail("critical_check", "sale_id IS NOT NULL")
```

**Nike Store Example - Quality Checks**:

```python
@dlt.table(name="silver_sales")
@dlt.expect("positive_amount", "amount > 0")
@dlt.expect("valid_date", "sale_date >= '2020-01-01'")
@dlt.expect_or_drop("valid_customer_id", "customer_id BETWEEN 1 AND 1000000")
@dlt.expect_or_fail("no_duplicates", "sale_id IS NOT NULL")
def silver_sales():
    return dlt.read("bronze_sales")
```

#### 5.3 DLT Incremental Processing

**Incremental Tables**:
```python
@dlt.table(
    name="silver_sales_incremental",
    table_properties={
        "pipelines.autoOptimize.managed": "true"
    }
)
def silver_sales_incremental():
    return dlt.read_stream("bronze_sales") \
        .filter(col("sale_date") >= current_date() - 7)  # Last 7 days
```

**Incremental with Watermarks**:
```python
@dlt.table(name="silver_sales_streaming")
def silver_sales_streaming():
    return dlt.read_stream("bronze_sales") \
        .withWatermark("sale_timestamp", "1 hour") \
        .groupBy(
            window(col("sale_timestamp"), "1 hour"),
            col("customer_id")
        ) \
        .agg(sum("amount").alias("hourly_revenue"))
```

---

### 6. Spark Structured Streaming

**What is Structured Streaming?**
Real-time data processing with Spark SQL engine.

#### 6.1 Basic Streaming

**Nike Store Example - Stream from Kafka**:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("SalesStreaming") \
    .getOrCreate()

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

# Write to Delta Lake
query = sales_stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/mnt/delta/checkpoints/sales_stream") \
    .trigger(processingTime="10 seconds") \
    .start("/mnt/delta/bronze/sales_stream")

query.awaitTermination()
```

#### 6.2 Streaming Output Modes

**Append Mode** (Default):
```python
# Only new rows added
.writeStream.outputMode("append")
```

**Complete Mode**:
```python
# Entire result table written (for aggregations)
.writeStream.outputMode("complete")
```

**Update Mode**:
```python
# Only updated rows written
.writeStream.outputMode("update")
```

**Nike Store Example - Aggregations**:

```python
# Hourly sales aggregation
hourly_sales = sales_stream \
    .withWatermark("sale_timestamp", "1 hour") \
    .groupBy(
        window(col("sale_timestamp"), "1 hour"),
        col("customer_id")
    ) \
    .agg(sum("amount").alias("hourly_revenue"))

hourly_sales.writeStream \
    .format("delta") \
    .outputMode("update") \
    .option("checkpointLocation", "/mnt/delta/checkpoints/hourly_sales") \
    .start("/mnt/delta/silver/hourly_sales")
```

#### 6.3 Watermarks

**What are Watermarks?**
Threshold for handling late-arriving data.

**Nike Store Example**:

```python
# Watermark: Data up to 1 hour late is accepted
sales_stream \
    .withWatermark("sale_timestamp", "1 hour") \
    .groupBy(window("sale_timestamp", "1 hour")) \
    .agg(sum("amount").alias("hourly_revenue"))
```

**How Watermarks Work**:
- Tracks maximum event time seen
- Late data within watermark is processed
- Data older than watermark is dropped

---

### 7. Delta Live Tables with Structured Streaming

**Combining DLT + Streaming**:

**Nike Store Example**:

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
        .withWatermark("sale_timestamp", "1 hour") \
        .withColumn("ingestion_time", current_timestamp())

# Aggregated Gold layer (streaming)
@dlt.table(
    name="gold_hourly_sales",
    comment="Hourly sales aggregates"
)
def gold_hourly_sales():
    return dlt.read_stream("silver_sales_stream") \
        .groupBy(
            window(col("sale_timestamp"), "1 hour"),
            col("customer_id"),
            col("product_id")
        ) \
        .agg(
            sum("amount").alias("hourly_revenue"),
            sum("quantity").alias("hourly_quantity"),
            count("*").alias("transaction_count")
        )
```

**Benefits**:
- ✅ Automatic checkpointing
- ✅ Built-in monitoring
- ✅ Data quality checks
- ✅ Incremental processing

---

### 8. Unity Catalog

**What is Unity Catalog?**
Centralized data governance for data and AI assets.

#### 8.1 Unity Catalog Concepts

**Three-Level Namespace**:
```
catalog.schema.table
```

**Example**:
```
nike_prod.sales.raw_sales
nike_prod.sales.cleaned_sales
nike_prod.analytics.daily_summary
```

#### 8.2 Creating Catalogs and Schemas

```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS nike_prod
COMMENT 'Nike production data catalog';

-- Create schema
CREATE SCHEMA IF NOT EXISTS nike_prod.sales
COMMENT 'Sales data schema';

-- Create table
CREATE TABLE nike_prod.sales.raw_sales (
    sale_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10,2),
    sale_date TIMESTAMP
) USING DELTA
LOCATION '/mnt/delta/bronze/sales';
```

#### 8.3 Unity Catalog Permissions

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

#### 8.4 External Tables

**Register External Data**:
```sql
-- Register S3 location as external table
CREATE TABLE nike_prod.sales.external_sales
USING DELTA
LOCATION 's3://nike-data/sales/';

-- Register Snowflake table
CREATE TABLE nike_prod.sales.snowflake_sales
USING SNOWFLAKE
OPTIONS (
    'sfURL' 'nike.snowflakecomputing.com',
    'sfDatabase' 'PRODUCTION',
    'sfSchema' 'SALES',
    'sfWarehouse' 'COMPUTE_WH',
    'sfTable' 'SALES'
);
```

---

### 9. Reading from Different Sources

#### 9.1 Snowflake

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
    .option("query", "SELECT * FROM SALES WHERE DATE >= '2024-01-01'") \
    .load()

# Write to Delta Lake
snowflake_df.write.format("delta").save("/mnt/delta/bronze/snowflake_sales")
```

**Using Unity Catalog**:
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
-- Register Iceberg table
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

**Redshift**:
```python
redshift_df = spark.read \
    .format("io.github.spark_redshift_community.spark.redshift") \
    .option("url", "jdbc:redshift://cluster.region.redshift.amazonaws.com:5439/db") \
    .option("dbtable", "sales") \
    .option("tempdir", "s3://temp-bucket/") \
    .option("aws_iam_role", "arn:aws:iam::123:role/RedshiftRole") \
    .load()
```

---

### 10. Spark Job Optimization

#### 10.1 Performance Tuning

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

**Important Configs**:
- `spark.sql.shuffle.partitions`: Number of partitions after shuffle (default: 200)
- `spark.sql.adaptive.enabled`: Enable adaptive query execution
- `spark.sql.files.maxPartitionBytes`: Max bytes per partition (128MB default)
- `spark.serializer`: Use Kryo for better performance

#### 10.2 Handling Skew

**What is Skew?**
Uneven data distribution across partitions.

**Nike Store Example - Skewed Customer Data**:

```python
# Problem: Some customers have millions of transactions
# Solution 1: Salting
from pyspark.sql.functions import *

# Add random salt to customer_id
salted_df = sales_df.withColumn("salt", (rand() * 100).cast("int"))

# Group by salted customer_id
result = salted_df.groupBy("customer_id", "salt") \
    .agg(sum("amount").alias("total")) \
    .groupBy("customer_id") \
    .agg(sum("total").alias("grand_total"))

# Solution 2: Broadcast small tables
from pyspark.sql.functions import broadcast

# Broadcast customer dimension (small table)
customer_dim = spark.table("dim_customer")
sales_df.join(broadcast(customer_dim), "customer_id")

# Solution 3: Increase partitions for skewed keys
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

**Detecting Skew**:
```python
# Check partition sizes
sales_df.rdd.glom().map(len).collect()
# If sizes vary greatly, you have skew
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

**Memory Best Practices**:
- ✅ Cache only when needed: `df.cache()` or `df.persist()`
- ✅ Unpersist when done: `df.unpersist()`
- ✅ Use appropriate storage levels: `MEMORY_ONLY`, `MEMORY_AND_DISK`
- ✅ Monitor memory usage in Spark UI

**Nike Store Example**:
```python
# Cache frequently used table
customer_dim = spark.table("dim_customer").cache()

# Use in multiple operations
sales_with_customer = sales_df.join(customer_dim, "customer_id")
revenue_by_customer = sales_with_customer.groupBy("customer_name").sum("amount")

# Unpersist when done
customer_dim.unpersist()
```

#### 10.4 Processing Too Much Data

**Strategies**:

**1. Partition Pruning**:
```python
# Only read relevant partitions
sales_df = spark.read.format("delta").load("/mnt/delta/sales") \
    .filter(col("sale_date") >= "2024-01-01")
```

**2. Column Pruning**:
```python
# Only select needed columns
sales_df.select("sale_id", "customer_id", "amount")
```

**3. Predicate Pushdown**:
```python
# Filter early
sales_df.filter(col("amount") > 100) \
    .filter(col("sale_date") >= "2024-01-01")
```

**4. Incremental Processing**:
```python
# Only process new data
new_sales = spark.read.format("delta") \
    .option("versionAsOf", last_processed_version) \
    .load("/mnt/delta/sales")
```

**5. Sampling**:
```python
# Sample data for testing
sample_df = sales_df.sample(fraction=0.1, seed=42)
```

---

### 11. Multi-Cloud Data Sharing

**What is Multi-Cloud?**
Sharing data across different cloud providers (AWS, Azure, GCP).

#### 11.1 Delta Sharing

**Delta Sharing**: Open protocol for secure data sharing.

**Nike Store Example - Share Data Across Clouds**:

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

#### 11.2 Cross-Cloud Access

**S3 from Azure Databricks**:
```python
# Access S3 from Azure
spark.conf.set("fs.s3a.access.key", "aws-access-key")
spark.conf.set("fs.s3a.secret.key", "aws-secret-key")

s3_data = spark.read.format("delta").load("s3://nike-data/sales/")
```

**Azure Blob from AWS Databricks**:
```python
# Access Azure Blob from AWS
spark.conf.set("fs.azure.account.key.storageaccount.blob.core.windows.net", "azure-key")

blob_data = spark.read.format("delta").load("wasbs://container@storageaccount.blob.core.windows.net/sales/")
```

---

### 12. Data Governance & PII Protection

#### 12.1 Column-Level Security

**Mask PII Data**:

```sql
-- Create function to mask email
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

**Filter Rows Based on User**:

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

#### 12.3 Data Lineage

**Track Data Lineage**:

```python
# Unity Catalog automatically tracks lineage
# View lineage in UI or query:
spark.sql("DESCRIBE EXTENDED nike_prod.sales.raw_sales")
```

#### 12.4 Data Quality Monitoring

**DLT Expectations for PII**:

```python
@dlt.table(name="silver_customers")
@dlt.expect("valid_email_format", "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'")
@dlt.expect("no_ssn_exposure", "ssn IS NULL OR LENGTH(ssn) = 4")  # Only last 4 digits
@dlt.expect_or_drop("valid_phone", "phone RLIKE '^[0-9]{10}$'")
def silver_customers():
    return dlt.read("bronze_customers") \
        .withColumn("ssn_masked", 
            when(col("ssn").isNotNull(), 
                 concat(lit("***-**-"), substring(col("ssn"), -4, 4))
            ).otherwise(None)
        )
```

---

### 13. Cost Optimization

#### 13.1 Cluster Optimization

**Right-Size Clusters**:

```python
# Use appropriate instance types
cluster_config = {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",  # Right size for workload
    "num_workers": 2,  # Start small, scale up if needed
    "autotermination_minutes": 30,  # Auto-terminate idle clusters
    "enable_elastic_disk": True  # Scale disk with data
}
```

**Cluster Best Practices**:
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

#### 13.3 Storage Optimization

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

# 3. Use lifecycle policies
# Move old data to cheaper storage (S3 Glacier, Azure Archive)
```

#### 13.4 Monitoring Costs

**Track Costs**:

```python
# Use Databricks SQL to monitor
spark.sql("""
    SELECT 
        cluster_id,
        SUM(total_cost) as total_cost,
        AVG(avg_cpu_utilization) as avg_cpu
    FROM system.billing.usage
    WHERE date >= current_date() - 7
    GROUP BY cluster_id
    ORDER BY total_cost DESC
""")
```

**Cost Optimization Checklist**:
- ✅ Right-size clusters
- ✅ Use autoscaling
- ✅ Enable autotermination
- ✅ Optimize Delta tables regularly
- ✅ VACUUM old files
- ✅ Use appropriate storage classes
- ✅ Monitor and alert on costs

---

## 💡 Real-World Examples

### Example 1: Complete ETL Pipeline

**Nike Store - End-to-End Pipeline**:

```python
import dlt
from pyspark.sql.functions import *

# Bronze: Ingest from multiple sources
@dlt.table(name="bronze_sales")
def bronze_sales():
    # Read from S3
    s3_data = spark.read.format("json").load("s3://nike-raw/sales/")
    
    # Read from Kafka
    kafka_data = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "sales") \
        .load() \
        .select(from_json(col("value").cast("string"), schema).alias("data")) \
        .select("data.*")
    
    # Union and write
    return s3_data.union(kafka_data)

# Silver: Clean and validate
@dlt.table(name="silver_sales")
@dlt.expect("valid_amount", "amount > 0")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_sales():
    return dlt.read("bronze_sales") \
        .withColumn("ingestion_time", current_timestamp()) \
        .dropDuplicates(["sale_id"])

# Gold: Aggregates
@dlt.table(name="gold_daily_sales")
def gold_daily_sales():
    return dlt.read("silver_sales") \
        .groupBy("sale_date", "customer_id") \
        .agg(
            sum("amount").alias("daily_revenue"),
            sum("quantity").alias("daily_quantity")
        )
```

### Example 2: Streaming Pipeline

**Real-Time Sales Dashboard**:

```python
@dlt.table(name="bronze_sales_stream")
def bronze_sales_stream():
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "sales") \
        .load()

@dlt.table(name="silver_sales_stream")
@dlt.expect("valid_amount", "amount > 0")
def silver_sales_stream():
    return dlt.read_stream("bronze_sales_stream") \
        .withWatermark("sale_timestamp", "1 hour")

@dlt.table(name="gold_hourly_sales")
def gold_hourly_sales():
    return dlt.read_stream("silver_sales_stream") \
        .groupBy(
            window(col("sale_timestamp"), "1 hour"),
            col("customer_id")
        ) \
        .agg(sum("amount").alias("hourly_revenue"))
```

---

## ✅ Best Practices Summary

### Delta Lake
- ✅ Use Delta Lake for all tables
- ✅ Run OPTIMIZE regularly
- ✅ VACUUM old files
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
- ✅ Use appropriate storage classes

### Governance
- ✅ Use Unity Catalog
- ✅ Implement column-level security
- ✅ Mask PII data
- ✅ Track data lineage
- ✅ Set up data quality checks

---

## 🎯 Next Steps

Once you're comfortable with Databricks, practice:
- Building end-to-end pipelines
- Optimizing Spark jobs
- Implementing data governance
- Cost optimization

**Study Time**: Spend 1-2 weeks on Databricks, build real projects, then move to next topic!

---

## 📚 Additional Resources

- **Databricks Documentation**: https://docs.databricks.com/
- **Delta Lake Documentation**: https://delta.io/
- **Spark Documentation**: https://spark.apache.org/docs/latest/
- **Databricks Academy**: Free courses on Databricks

---

**Keep Building! 🚀**
