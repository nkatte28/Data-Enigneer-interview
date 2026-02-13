# Topic 3: Data File Formats

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Understand key data file formats: ORC, Parquet, Avro, JSON, and CSV
- Explain **row-based vs column-based** storage and why **row = faster writes**, **column = faster reads**
- Describe **predicate pushdown**, **data skipping**, and **partition pruning** and how they improve query performance
- Compare **compression types** (e.g. Snappy, GZIP, LZ4) and when to use each
- Choose the right format for storage, streaming, analytics, and exchange
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

### 2. Key Concepts: Row vs Column, Predicate Pushdown, Compression, Data Skipping

#### Row-based vs column-based storage

**Row-based storage**
- Data is stored **one row at a time**: all columns for a row are stored together, then the next row, and so on.
- **Example:** Row 1: `[id=1, name=Alice, city=NYC, age=30]` → Row 2: `[id=2, name=Bob, city=LA, age=25]` → …
- **Good for:** Reading or writing **full rows** (e.g. one customer record, one event).
- **Used by:** Avro, CSV, traditional relational row stores.

**Column-based (columnar) storage**
- Data is stored **one column at a time**: all values for column A, then all values for column B, etc.
- **Example:** `id: [1,2,3,...]` then `name: [Alice,Bob,...]` then `city: [NYC,LA,...]` then `age: [30,25,...]`.
- **Good for:** Reading **a subset of columns** or aggregating one column (e.g. `SUM(amount)`, `WHERE region = 'US'`).
- **Used by:** Parquet, ORC.

---

#### Why row-based = faster writes, column-based = faster reads

**Row-based → faster writes**
- **One row = one write unit.** To insert a record you append one contiguous block (all columns for that row).
- No need to touch every column file; minimal seeks and I/O per row.
- **Streaming / transactional workloads** often write full rows → row-based is a natural fit (e.g. Avro, Kafka).

**Column-based → faster reads (for analytics)**
- **One column = one read unit.** A query like `SELECT SUM(revenue) WHERE year = 2024` only needs:
  - The `revenue` column (and maybe `year` for filtering).
- You **skip entire columns** you don’t need → less I/O and better cache use.
- Same column values are stored together → **better compression** (repeated patterns) and **vectorized execution**.
- **Analytical queries** often need few columns and many rows → column-based wins (e.g. Parquet, ORC).

**Summary**

| Operation     | Row-based        | Column-based     |
|--------------|------------------|------------------|
| **Write one row** | ✅ Fast (one block) | ❌ Slower (update many column chunks) |
| **Read few columns** | ❌ Read full rows   | ✅ Read only those columns |
| **Aggregations**   | ❌ Scan full rows   | ✅ Scan only needed columns |

---

#### Predicate pushdown

**What it means**
- **Predicate pushdown** = pushing **filter conditions down** to the storage layer (file format / reader) so that:
  - Only **rows (or row groups) that can satisfy the filter** are read and passed to the engine.
- The query engine says: “I only need rows where `region = 'US'` and `year >= 2023`.”  
  The file format (e.g. Parquet, ORC) uses **metadata (min/max, statistics)** and **skips** row groups or stripes that cannot contain such rows.

**Why it helps**
- Less data read from disk → **faster queries** and lower I/O cost.
- Works best when the format stores **per-block (or per-stripe) statistics** (e.g. min/max per column). Parquet and ORC both support this; ORC is often cited as having strong predicate pushdown.

**Example**
- Query: `SELECT * FROM sales WHERE date = '2024-01-15'`.
- With predicate pushdown: the reader checks each Parquet row group’s (or ORC stripe’s) min/max for `date`; if `'2024-01-15'` is not in that range, the **entire block is skipped** and not read.

---

#### Data skipping

**What it means**
- **Data skipping** = avoiding reading **data that cannot contribute to the result**, using **metadata** (statistics) stored with the data.
- Common metadata: **min/max** per column per block, **null counts**, sometimes **bloom filters**.
- The engine (or the format reader) uses this metadata to **skip files, row groups, or stripes** before reading actual column data.

**How data skipping differs from predicate pushdown**

| | Predicate pushdown | Data skipping |
|---|--------------------|----------------|
| **What it is** | A **technique**: sending the filter (predicate) *down* to the storage layer instead of applying it only in the engine. | An **outcome**: not reading data that can’t match the query (skipping files, row groups, or stripes). |
| **Focus** | *Where* the filter is applied (at scan/read time, close to the data). | *What* we achieve (less I/O by skipping irrelevant data). |
| **Scope** | Specifically about **filters** (e.g. `WHERE`, join conditions) being pushed to the reader. | Can include **any** use of metadata to skip data: filters (via pushdown), **partition pruning**, **file listing** (e.g. skip by path), etc. |
| **Analogy** | “Give the storage layer the filter so it can decide what to read.” | “We skipped 80% of row groups” — the result of that decision. |

So: **predicate pushdown** is the *mechanism* (push predicate to storage); **data skipping** is the *effect* (skip blocks/rows using metadata). Predicate pushdown is one way to get data skipping; data skipping can also come from partition pruning or other metadata-based skipping without a pushed predicate.

**How it relates in practice**
- Predicate pushdown is the **mechanism**: “push the predicate down to the storage layer.”
- Data skipping is the **effect**: “skip blocks/rows that don’t match the predicate using metadata.”
- So **predicate pushdown enables data skipping** when the format stores the right statistics (e.g. Parquet row group stats, ORC stripe stats).

**Example**
- Table partitioned by `date`, stored as Parquet with row group statistics.
- Query: `WHERE amount > 1000`.
- Engine uses **min/max of `amount`** in each row group: if `max(amount) < 1000` in a row group, that whole row group is **skipped** (data skipping via predicate pushdown).

---

#### Partition pruning

**What it means**
- **Partition pruning** = not reading **entire partitions** that cannot contain rows matching the query.
- Data is stored in a **partitioned layout** (e.g. by date, region): each partition is a separate directory or set of files (e.g. `year=2024/month=01/day=15/`).
- The engine looks at the query filter (e.g. `WHERE date = '2024-01-15'`) and **lists only the partition paths** that can match; it never opens other partition directories. That’s partition pruning.

**How it works**
- **Partition columns** are usually in the path or in metadata (e.g. `date=2024-01-15`).
- Query has a predicate on the partition column → engine converts it to a **list of partition paths** and only reads those.
- No need to open every file: **whole partitions are skipped** at the directory/metadata level, before reading any row data.

**Example**
- Layout: `s3://bucket/events/year=2024/month=01/day=01/`, `.../day=02/`, …, `.../day=31/`.
- Query: `SELECT * FROM events WHERE year = 2024 AND month = 1 AND day = 15`.
- With partition pruning: only `.../year=2024/month=01/day=15/` is read; all other `day=*` directories are **skipped** (no listing, no scan).

**How it relates to predicate pushdown and data skipping**
- **Predicate pushdown** can push the partition-column filter down so the **catalog or file listing** only returns matching partition paths → that’s partition pruning.
- **Data skipping** = “skip data that can’t match.” Partition pruning is a form of data skipping: we skip **whole partitions** using partition metadata (path/metadata), not per-block stats. So:
  - **Partition pruning** = data skipping at the **partition** level (skip entire partition dirs).
  - **Predicate pushdown on non-partition columns** = data skipping at **row group / stripe** level (skip blocks within a partition).

**Best practice**
- Put frequently filtered columns (e.g. `date`, `region`) in the **partition key** so the engine can prune whole partitions and read far less data.

---

#### Compression types and what Snappy means

**Why compress**
- **Smaller files** → less storage, less I/O, often **faster** reads (and sometimes writes) when the cost of decompression is less than the I/O saved.

**Common compression types**

| Compression   | Speed        | Ratio   | Typical use                          |
|---------------|-------------|--------|--------------------------------------|
| **None**      | Fastest     | 1x     | When I/O is cheap or data already small |
| **Snappy**    | Fast        | Good   | Default in Parquet; balance of speed and size |
| **GZIP**      | Slower      | Better | When storage matters more than CPU   |
| **LZ4**       | Very fast   | Good   | Low-latency, fast decompression      |
| **ZSTD**      | Configurable| Better| Newer format; good ratio and speed    |
| **Brotli**    | Slower      | High   | When max compression is desired      |

**What Snappy compression means**
- **Snappy** is a **fast** compression algorithm (by Google):
  - **Fast encode and decode** → low CPU overhead, good for interactive and batch workloads.
  - **Moderate compression ratio** → smaller than no compression, but not as small as GZIP or ZSTD at high levels.
- **Parquet** often uses Snappy by default so that:
  - Files are smaller than uncompressed and I/O is reduced.
  - Compression/decompression stays cheap so that **scan speed** and **query latency** remain good.
- Trade-off: Snappy favors **speed over maximum compression**; for colder data you can switch to GZIP or ZSTD for better ratio.

**In file formats**
- **Parquet:** Often Snappy by default; can use GZIP, LZ4, ZSTD, etc. per column.
- **ORC:** Uses internal compression (e.g. Zlib); typically high ratio.
- **Avro:** Supports codecs like Snappy, Deflate (GZIP); medium ratio, good for streaming.

---

### 3. Comparison Table: File Formats Overview

| File Format | Type | Best For | Supports Schema Evolution? | Compression |
|-------------|------|----------|---------------------------|-------------|
| **ORC** | Columnar | Apache Hive, ACID Transactions | ✅ Yes | ✅ High |
| **Parquet** | Columnar | Data Warehousing (Snowflake, Redshift, BigQuery) | ✅ Yes | ✅ High |
| **Avro** | Row-based | Streaming & Schema Evolution (Kafka, Spark, Flink) | ✅ Yes | ✅ Medium |
| **JSON** | Semi-Structured | APIs, Log Data | ✅ Yes | ❌ No (unless compressed) |
| **CSV** | Row-based | Simple Data Exchange | ❌ No | ❌ No |

---

### 4. ORC (Optimized Row Columnar)

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

### 5. Parquet

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

### 6. Avro

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

### 7. JSON (JavaScript Object Notation)

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

### 8. CSV (Comma-Separated Values)

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
