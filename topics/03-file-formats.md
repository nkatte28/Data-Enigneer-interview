# Topic 3: Data File Formats

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Understand key data file formats: ORC, Parquet, Avro, JSON, and CSV
- Choose the right format for storage, streaming, analytics, and exchange
- Compare columnar vs row-based formats and when to use each
- Explain schema evolution support across formats
- Apply compression and performance trade-offs in practice

---

## 📖 Core Concepts

### 1. Why File Formats Matter

The choice of file format significantly impacts:
- **Storage efficiency** (compression, size)
- **Query performance** (read/write speed, predicate pushdown)
- **Schema evolution** (adding/removing columns over time)
- **Use case fit** (streaming, analytics, data exchange)

---

### 2. Comparison Table: File Formats Overview

| File Format | Type | Best For | Supports Schema Evolution? | Compression |
|-------------|------|----------|---------------------------|-------------|
| **ORC** | Columnar | Apache Hive, ACID Transactions | ✅ Yes | ✅ High |
| **Parquet** | Columnar | Data Warehousing (Snowflake, Redshift, BigQuery) | ✅ Yes | ✅ High |
| **Avro** | Row-based | Streaming & Schema Evolution (Kafka, Spark, Flink) | ✅ Yes | ✅ Medium |
| **JSON** | Semi-Structured | APIs, Log Data | ✅ Yes | ❌ No (unless compressed) |
| **CSV** | Row-based | Simple Data Exchange | ❌ No | ❌ No |

---

### 3. ORC (Optimized Row Columnar)

**Best For**: Apache Hive, ACID Transactions in Hive

**Key Characteristics**:
- **Columnar Format**: Stores data in columns → Faster query performance
- **Predicate Pushdown**: Only reads relevant data for queries
- **Highly Compressed**: Better compression than Parquet for Hive workloads
- **ACID Support**: Supports transactions, updates, and deletes in Hive
- **Metadata Storage**: Stores metadata for fast schema discovery

**✅ Pros**:
- ✔️ Best for Hive tables (supports updates & deletes with ACID)
- ✔️ High compression & indexing → Reduces storage & speeds up queries
- ✔️ Stores metadata (fast schema discovery)
- ✔️ More compression efficient than Parquet
- ✔️ Better predicate pushdown capabilities
- ✔️ Reduces NameNode load (single file per task)

**❌ Cons**:
- ❌ Not as widely used as Parquet outside Hive
- ❌ Slower than Parquet for cloud-based analytics (Snowflake, BigQuery)
- ❌ Less capable of storing nested data compared to Parquet

**When to Use**:
- Working with Apache Hive
- Need ACID transaction support
- Hive-based data warehouses
- When predicate pushdown is critical

**Example Use Case**: Hive data warehouse with frequent updates and deletes

---

### 4. Parquet

**Best For**: Cloud-based Data Warehouses (Snowflake, Redshift, BigQuery, Databricks)

**Key Characteristics**:
- **Columnar Format**: Optimized for read-heavy workloads
- **Distributed File Systems**: Better for HDFS, S3, ADLS
- **Metadata Storage**: Stores file structure, schema, and column statistics
- **Compression**: Uses Snappy compression by default
- **Schema Evolution**: Supports schema append (adding columns)

**✅ Pros**:
- ✔️ Faster queries in OLAP systems (BI, analytics)
- ✔️ Highly compressed (stores only relevant columns in queries)
- ✔️ Supports schema evolution (adding columns)
- ✔️ Better retrieval time compared to Avro
- ✔️ Better in-built functionality in Spark
- ✔️ More capable of storing nested data than ORC
- ✔️ Ideal for analytical querying (reads are much more efficient than writes)

**❌ Cons**:
- ❌ Not the best for Hive ACID transactions (use ORC for that)
- ❌ Writes are slower compared to Avro
- ❌ Only supports schema append (not full schema evolution like Avro)
- ❌ Less compression efficient than ORC

**When to Use**:
- Cloud data warehouses (Snowflake, Redshift, BigQuery)
- Analytical workloads with large-scale data processing
- Querying a subset of columns in multi-column tables
- Read-heavy workloads

**Technical Details**:
- **Columnar Storage**: Values from the same column are stored together
- **Efficient Compression**: Columnar format enables efficient compression and encoding
- **Data Skipping**: Query engines can skip unnecessary data blocks based on statistics
- **Query Planning**: Metadata enables optimized query planning and execution

**Example Use Case**: Data warehouse analytics with frequent columnar queries

---

### 5. Avro

**Best For**: Streaming, Kafka, Schema Evolution

**Key Characteristics**:
- **Row-based Format**: Good for fast data writes
- **Schema Storage**: Stores schema with the data (JSON format)
- **Schema Evolution**: Robust support for schema changes over time
- **Random Access**: Supports random access despite compression
- **Backward & Forward Compatibility**: Handles schema changes gracefully

**✅ Pros**:
- ✔️ Best for streaming & real-time pipelines (Kafka, Spark, Flink)
- ✔️ Supports comprehensive schema evolution (adding/modifying columns, missing fields)
- ✔️ Compressed format with random access support
- ✔️ Faster writes compared to Parquet
- ✔️ More mature schema evolution than Parquet
- ✔️ Ideal for ETL operations where all columns are queried
- ✔️ Schema stored in JSON format (easy to read and interpret)

**❌ Cons**:
- ❌ Not optimized for analytics (use Parquet or ORC for that)
- ❌ Slower reads compared to Parquet
- ❌ Less compression than Parquet/ORC
- ❌ Not ideal for querying subset of columns

**When to Use**:
- Streaming data pipelines (Kafka, Kinesis)
- Real-time data processing
- When schema changes frequently
- ETL operations requiring all columns
- Data lake landing zones (write-heavy)

**Schema Evolution Features**:
- Handles missing fields
- Handles added fields
- Handles changed fields
- Backward compatibility (old readers can read new data)
- Forward compatibility (new readers can read old data)

**Example Use Case**: Kafka streaming pipeline with evolving schemas

---

### 6. JSON (JavaScript Object Notation)

**Best For**: Semi-Structured Data, API Logs

**Key Characteristics**:
- **Self-Describing**: Schema stored with data
- **Flexible Schema**: Not optimized for fast queries
- **Human-Readable**: Easy to read and write
- **Widely Supported**: Works with many systems

**✅ Pros**:
- ✔️ Easy to read & write
- ✔️ Supports schema evolution (flexible structure)
- ✔️ Best for NoSQL & API data (MongoDB, Elasticsearch, Kafka, Cloud Storage)
- ✔️ Human-readable format
- ✔️ Self-describing (schema embedded in data)

**❌ Cons**:
- ❌ Not efficient for analytics (slow queries)
- ❌ Takes more storage than columnar formats (Parquet, ORC)
- ❌ No built-in compression (unless compressed externally)
- ❌ Requires full file scan for queries
- ❌ No indexing support

**When to Use**:
- API responses and logs
- NoSQL databases (MongoDB, Elasticsearch)
- Data exchange between systems
- Semi-structured data
- Small to medium datasets

**Example Use Case**: API log storage, NoSQL database exports

---

### 7. CSV (Comma-Separated Values)

**Best For**: Small Datasets & Data Exchange

**Key Characteristics**:
- **Plain Text Format**: Separated by commas
- **Widely Supported**: Universal compatibility
- **No Indexing**: Lacks built-in indexing
- **No Compression**: Uncompressed format

**✅ Pros**:
- ✔️ Simple & human-readable
- ✔️ Good for data exchange (Excel, Google Sheets, APIs)
- ✔️ Universal compatibility
- ✔️ Easy to import/export

**❌ Cons**:
- ❌ Not efficient for big data processing (no compression)
- ❌ Slow queries (needs full file scan)
- ❌ No schema evolution support
- ❌ No compression
- ❌ No indexing
- ❌ Large file sizes

**When to Use**:
- Small datasets
- Data exchange between systems
- Excel/Google Sheets integration
- Simple data import/export
- Prototyping and testing

**Example Use Case**: Small data exports, Excel integration, simple data exchange

---

## 🔄 File Format Comparisons

### Avro vs. Parquet

| Aspect | Avro | Parquet |
|--------|------|---------|
| **Storage Format** | Row-based | Columnar |
| **Best For** | Streaming, ETL (all columns) | Analytics, querying subset of columns |
| **Write Performance** | ✅ Faster writes | ❌ Slower writes |
| **Read Performance** | ❌ Slower reads | ✅ Faster reads |
| **Compression** | Medium | High |
| **Schema Evolution** | ✅ Comprehensive (add/modify columns, missing fields) | ⚠️ Limited (schema append only) |
| **Query Performance** | ❌ Not optimized for analytics | ✅ Optimized for analytical querying |
| **Use Case** | ETL operations, streaming | Analytical workloads, OLAP |

**Key Differences**:
- **Avro**: Row-based, faster writes, better schema evolution, ideal for streaming and ETL
- **Parquet**: Columnar, faster reads, better compression, ideal for analytics and OLAP

**When to Choose**:
- **Choose Avro** when: Streaming data, frequent schema changes, ETL operations requiring all columns
- **Choose Parquet** when: Analytical queries, querying subset of columns, read-heavy workloads

---

### ORC vs. Parquet

| Aspect | ORC | Parquet |
|--------|-----|---------|
| **Storage Format** | Columnar | Columnar |
| **Best For** | Apache Hive, ACID Transactions | Cloud Data Warehouses |
| **Compression** | ✅ More compression efficient | ⚠️ Less compression efficient |
| **ACID Support** | ✅ Yes (Hive) | ❌ No |
| **Nested Data** | ⚠️ Less capable | ✅ More capable |
| **Predicate Pushdown** | ✅ Better | ⚠️ Good |
| **Cloud Analytics** | ❌ Slower (Snowflake, BigQuery) | ✅ Faster |
| **Hive Performance** | ✅ Optimized for Hive | ⚠️ Not optimized for Hive ACID |

**Key Differences**:
- **ORC**: Better compression, ACID support, better predicate pushdown, optimized for Hive
- **Parquet**: Better nested data support, faster in cloud analytics, more widely adopted

**When to Choose**:
- **Choose ORC** when: Working with Hive, need ACID transactions, Hive-based data warehouse
- **Choose Parquet** when: Cloud data warehouses (Snowflake, Redshift), need nested data support, cloud analytics

---

## 📋 File Format Selection Guide

**Choose ORC when**:
- Using Apache Hive
- Need ACID transaction support
- Working with Hive-based data warehouses
- Predicate pushdown is critical

**Choose Parquet when**:
- Using cloud data warehouses (Snowflake, Redshift, BigQuery)
- Analytical workloads with read-heavy operations
- Querying subset of columns
- Need nested data support
- Cloud-based analytics

**Choose Avro when**:
- Streaming data pipelines (Kafka, Kinesis)
- Frequent schema changes
- ETL operations requiring all columns
- Write-heavy workloads
- Real-time data processing

**Choose JSON when**:
- API responses and logs
- NoSQL databases (MongoDB, Elasticsearch)
- Semi-structured data
- Data exchange between systems
- Small to medium datasets

**Choose CSV when**:
- Small datasets
- Simple data exchange
- Excel/Google Sheets integration
- Prototyping and testing
- Human-readable requirements

---

## 📊 Compression and Performance Summary

**File Formats with Compression**:
- ✅ **ORC**: High compression, best for Hive
- ✅ **Parquet**: High compression (Snappy by default), best for analytics
- ✅ **Avro**: Medium compression, best for streaming

**Performance Characteristics**:
- **Write Performance**: Avro > Parquet > ORC
- **Read Performance**: Parquet ≈ ORC > Avro
- **Compression**: ORC > Parquet > Avro
- **Schema Evolution**: Avro > Parquet (append only) > ORC

---

## ✅ Check Your Understanding

1. When would you choose Parquet over Avro?
2. What is the main advantage of ORC over Parquet in a Hive environment?
3. Why is Avro better for streaming than Parquet?
4. What are the trade-offs between row-based and columnar formats?
5. Which format supports the most flexible schema evolution?

---

## 🎯 Next Steps

Once you're comfortable with file formats, move on to:
- **Topic 4: Advanced SQL** (or next topic in your study plan)

**Study Time**: Spend 1–2 days on this topic, then practice choosing formats in design scenarios.

---

## 📚 Additional Resources

- [Apache Parquet Format](https://parquet.apache.org/)
- [Apache Avro Documentation](https://avro.apache.org/)
- [ORC File Format](https://orc.apache.org/)
- [Delta Lake File Format](https://delta.io/) (built on Parquet)
