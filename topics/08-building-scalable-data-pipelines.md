# Topic 8: Building Scalable Data Pipelines

## 🎯 Learning Goals

- Choose **instance type and number of nodes** from data volume using simple formulas
- Size **executors, memory, and cores** for Spark/Databricks
- Decide **partition size and count** when writing tables (Delta/Parquet)
- Apply **batch vs real-time** config and key scaling practices

---

## 📑 Table of Contents

1. [What Scalable Pipelines Mean](#1-what-scalable-pipelines-mean)
2. [How to Pick Instance and Size the Cluster](#2-how-to-pick-instance-and-size-the-cluster)
3. [Executors, Memory, and Cores](#3-executors-memory-and-cores)
4. [Write-Back: Partition Size and Layout](#4-write-back-partition-size-and-layout)
5. [File Formats and Batch vs Real-Time](#5-file-formats-and-batch-vs-real-time)
6. [Checklist and Best Practices](#6-checklist-and-best-practices)

---

## 1. What Scalable Pipelines Mean

Building scalable data pipelines means designing pipelines that can handle increasing data volume, more sources, and more users without major redesign or performance issues. Interviewers want to hear how you think about architecture, performance, reliability, and cost.

**Scalable** = handle more data or higher throughput by adding/tuning resources instead of rewriting.

| Scale by | What to do |
|----------|------------|
| **Volume** | More workers, partition by time/key |
| **Velocity** | More consumers (Kafka), more nodes |
| **Compute** | `shuffle.partitions`, `maxPartitionBytes`, executors |

---

## 2. How to Pick Instance and Size the Cluster

### 2.1 Which Instance to Use (AWS)

Pick by **data volume per run** (e.g. per day), then set number of nodes.

| Instance | vCPU | RAM | Local NVMe | Use when |
|----------|------|-----|------------|----------|
| **i3.xlarge** | 4 | 30 GB | Yes | **&lt; 500 GB/day** — dev, small prod |
| **i3.2xlarge** | 8 | 61 GB | Yes | **500 GB – 2 TB/day** — standard prod |
| **i3.4xlarge** | 16 | 122 GB | Yes | **&gt; 2 TB/day** — fewer, bigger nodes |
| **r5d.2xlarge** | 8 | 64 GB | Yes | **Memory-heavy** — big joins, OOM on i3 |

**Rule**: Prefer **i3** (local SSD). Use **r5d** only when you hit OOM.

### 2.2 How to Calculate Number of Nodes

**Goal**: Finish within your SLA (e.g. 4–6 hours for daily batch).

**Simple formula:**

- **Throughput** (Parquet/Delta): ~100–200 MB/hour per vCPU (ballpark).
- **Total vCPUs** ≈ `data_GB / (hours_SLA × 0.15)`  
  Example: 1 TB in 4 h → 1000 / (4 × 0.15) ≈ **166 vCPUs**.
- **Number of workers** = `total_vCPUs / vCPUs_per_instance`.  
  Example: 166 / 8 (i3.2xlarge) ≈ **21 workers** (use autoscale min/max around this).

**Shuffle partitions**: Start with **2–4× total executor cores**; enable AQE so Spark can reduce at runtime.

**Quick reference (Parquet/Delta, ~4–6 h run):**

| Data per run | Instance | Workers (min–max) | Shuffle partitions |
|--------------|----------|-------------------|---------------------|
| 50 GB | i3.xlarge | 2 | 64 |
| 100 GB | i3.xlarge | 2–6 | 128 |
| 500 GB | i3.2xlarge | 4–16 | 256 |
| 1 TB | i3.2xlarge | 8–24 | 512 |
| 10 TB | i3.4xlarge | 20–50 | 800 |

### 2.3 Example: Calculate Workers and Set Spark Config

```python
# Input: data volume and SLA
data_gb = 500
hours_sla = 4
vcpu_per_node = 8  # e.g. i3.2xlarge

# Approximate vCPUs needed (~150 MB/h per vCPU)
total_vcpus = data_gb / (hours_sla * 0.15)
num_workers = max(2, int(total_vcpus / vcpu_per_node))
shuffle_partitions = num_workers * vcpu_per_node * 2  # 2x total cores

# Apply in job
spark.conf.set("spark.sql.shuffle.partitions", str(shuffle_partitions))
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")   # 128 MB read
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

**One cluster config template** (tune `node_type_id`, `min_workers`, `max_workers` from the table above):

```json
{
  "new_cluster": {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.2xlarge",
    "autoscale": { "min_workers": 4, "max_workers": 16 },
    "spark_conf": {
      "spark.sql.shuffle.partitions": "256",
      "spark.sql.files.maxPartitionBytes": "134217728",
      "spark.sql.adaptive.enabled": "true"
    }
  }
}
```

---

## 3. Executors, Memory, and Cores

On **Databricks**, executor count and memory are derived from the cluster; you can override with Spark config. On **plain Spark** (e.g. EMR), you set them explicitly.

### 3.1 Key Settings

| Setting | What it controls | Typical rule |
|---------|------------------|--------------|
| **Executors per node** | How many JVMs per worker | 1 per node (simplest) or leave to Databricks |
| **Executor memory** | RAM per executor | Leave ~10–20% for OS/overhead; e.g. 28 GB on 30 GB node |
| **Cores per executor** | Parallelism per executor | 4–5 for i3.xlarge (4 vCPU); 8 for i3.2xlarge |
| **Driver memory** | Driver JVM | 4–8 GB for most jobs; more for big collects/broadcasts |

### 3.2 Simple Formulas (plain Spark / EMR)

- **Executor memory** ≈ `(node_RAM - 2 GB) / num_executors_per_node`  
  Example: i3.xlarge 30 GB, 1 executor → **28g**.
- **Cores per executor** = `node_vCPUs` (if 1 executor per node).
- **Total executor cores** = `num_workers × cores_per_executor`; set `spark.sql.shuffle.partitions` to about **2–4×** this.

### 3.3 Example: Explicit Executor Config (EMR / Spark on EC2)

```python
# For i3.2xlarge: 8 vCPU, 61 GB RAM; 4 workers
spark.conf.set("spark.executor.instances", "4")
spark.conf.set("spark.executor.memory", "12g")       # leave headroom
spark.conf.set("spark.executor.cores", "2")         # 4 executors × 2 = 8 cores
spark.conf.set("spark.driver.memory", "4g")
spark.conf.set("spark.sql.shuffle.partitions", "64")  # 2–4× total cores
```

**Databricks**: Usually you only set `spark.sql.shuffle.partitions` and `spark.sql.files.maxPartitionBytes`; instance size defines memory and cores.

---

## 4. Write-Back: Partition Size and Layout

When you **write** a table (Delta/Parquet), partition size and count drive read performance and metadata overhead.

### 4.1 Target Partition Size

| Target | Size per partition | Why |
|--------|--------------------|-----|
| **Sweet spot** | **128 MB – 1 GB** | Good scan throughput; not too many files |
| **Avoid** | &lt; 32 MB | Too many small files; slow listing and opens |
| **Avoid** | &gt; 2 GB | Fewer tasks; less parallelism, bigger spills |

### 4.2 How Many Partitions When Writing?

**Rule of thumb:**  
`num_partitions ≈ output_data_size_GB / 0.5`  
Aim for ~500 MB–1 GB per partition. So 100 GB output → **100–200 partitions**.

```python
# Example: 100 GB output → aim for ~200 partitions (~500 MB each)
output_gb = 100
target_partition_size_gb = 0.5
num_partitions = max(1, int(output_gb / target_partition_size_gb))

df = spark.read.format("delta").load("/mnt/raw/events")
df = df.repartition(num_partitions)  # control total number of output files
df.write.format("delta").mode("overwrite").partitionBy("date").save("/mnt/silver/events")
```

**If you use `partitionBy("date")`:**  
You get one directory per date; **inside** each partition you still want 1–10 files of 128 MB–1 GB. Use `repartition` or `coalesce` so that each date gets a reasonable number of files.

### 4.3 Repartition vs Coalesce Before Write

| Operation | Use when | Effect |
|-----------|----------|--------|
| **repartition(n)** | Increase or set partition count | Full shuffle; even sizing |
| **coalesce(n)** | Reduce partition count (e.g. after filter) | No full shuffle; can be uneven |

```python
# Too many small files after a heavy filter? Coalesce before write.
df = spark.read.format("delta").load("/mnt/silver/events")
df_filtered = df.filter("date = '2025-03-01'")
df_filtered.coalesce(4).write.format("delta").mode("overwrite").save("/mnt/gold/daily_events")

# Target ~200 output partitions total when writing by date
df.repartition(200, "date").write.format("delta").partitionBy("date").save("/mnt/silver/events")
```

### 4.4 Delta: OPTIMIZE and Z-ORDER

After writes, compact small files and improve predicate pushdown:

```sql
OPTIMIZE delta.`/mnt/silver/events` ZORDER BY (date, user_id);
```

---

## 5. File Formats and Batch vs Real-Time

### 5.1 File Formats

| Format | Throughput | Sizing tip |
|--------|------------|------------|
| **Parquet / Delta / ORC** | Best | Use Section 2 as-is |
| **Avro** | ~1.2× slower | +20–50% workers or 1.2× runtime |
| **JSON / CSV** | ~1.5–2× slower | +50–100% workers or convert to Parquet first |

**Simple read/write:**

```python
# Parquet/Delta
df = spark.read.format("delta").load("/mnt/raw/events")
df.write.format("delta").partitionBy("date").save("/mnt/silver/events")

# JSON (pass schema for speed)
df = spark.read.schema(my_schema).json("/mnt/raw/events")
```

### 5.2 Batch vs Real-Time

| | Batch | Real-time |
|--|--------|-----------|
| **Cluster** | Job cluster; size by volume (Section 2) | Long-running; size by throughput/lag |
| **Kafka** | — | Consumers ≤ topic partitions |

```python
df.writeStream.format("delta").option("checkpointLocation", "/mnt/checkpoints/events").start("/mnt/silver/events")
```

---

## 6. Checklist and Best Practices

1. **Instance** → Data volume → table in 2.1; **workers** → formula in 2.2 or quick-reference table.
2. **Executors/memory** → Section 3; on Databricks often only shuffle + maxPartitionBytes.
3. **Write partition size** → 128 MB–1 GB per partition; use `repartition`/`coalesce` and OPTIMIZE (Section 4).
4. **Format** → Prefer Parquet/Delta; JSON/CSV need more workers.
5. **Skew** → Salting, split, or broadcast for hot keys.
6. **Idempotency** → Overwrite by partition or merge by key; checkpoint for streaming.
7. **Cost** → Right-size, job clusters, spot for batch.
