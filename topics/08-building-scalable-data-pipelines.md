# Topic 8: Building Scalable Data Pipelines

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Define what **"building scalable data pipelines"** means and which dimensions to scale (ingestion, compute, storage, orchestration)
- Choose **cluster and job configuration** for given data volumes (e.g. 50 GB/day, 100 GB/day, 1 TB/day) for optimal performance and cost
- Explain how **file formats** (Parquet, ORC, Avro, JSON, CSV) affect throughput, I/O, and cluster sizing
- Compare **batch vs real-time** pipelines and when to use each; size clusters and jobs for both
- List the **key considerations** when building scalable systems: partitioning, parallelism, backpressure, monitoring, failure handling, and cost

---

## 📑 Table of Contents

1. [What Does "Building Scalable Data Pipelines" Mean?](#1-what-does-building-scalable-data-pipelines-mean)
2. [Cluster and Job Config by Data Volume](#2-cluster-and-job-config-by-data-volume)
3. [Impact of File Formats on Scaling](#3-impact-of-file-formats-on-scaling)
4. [Batch vs Real-Time: Scenarios and Config](#4-batch-vs-real-time-scenarios-and-config)
5. [What to Consider When Building Scalable Pipelines](#5-what-to-consider-when-building-scalable-pipelines)

---

## 1. What Does "Building Scalable Data Pipelines" Mean?

**Scalable data pipelines** handle **growth in data volume, velocity, or variety** without a full redesign—by adding resources (scale-out) or tuning rather than rewriting.

### 1.1 Dimensions of Scalability

| Dimension | What it means | How you scale |
|-----------|----------------|----------------|
| **Volume** | More data per run or per day | More workers, partitioning by time/keys |
| **Velocity** | Higher throughput (events/sec, GB/hour) | More consumers, more compute nodes |
| **Variety** | More sources, formats, schemas | Decoupled stages, schema evolution |
| **Concurrency** | More jobs at once | Isolated clusters, queue limits |

### 1.2 What You Actually Scale

- **Ingestion**: More partitions (Kafka/Kinesis), parallel reads from DB (split by key range)
- **Compute**: More workers, bigger instances, `spark.sql.shuffle.partitions`, `maxPartitionBytes`
- **Storage**: Partitioning, compaction, lifecycle
- **Orchestration**: DAG parallelism, retries, idempotency

### 1.3 "Optimal" Performance

- **Throughput**: Finish within the allowed window (e.g. daily batch in 4–6 hours)
- **Cost**: Right-size; use autoscaling and spot where appropriate
- **Stability**: No OOMs, no skew, predictable runtimes
- **Recoverability**: Retry by partition without reprocessing everything

---

## 2. Cluster and Job Config by Data Volume

### 2.1 Which Instance to Use When (AWS)

| Instance | vCPU | RAM | NVMe | Use when |
|----------|------|-----|------|----------|
| **i3.xlarge** | 4 | 30 GB | Yes | **< 500 GB/day** — dev, small prod, I/O-bound reads |
| **i3.2xlarge** | 8 | 61 GB | Yes | **500 GB – 2 TB/day** — standard production batch |
| **i3.4xlarge** | 16 | 122 GB | Yes | **> 2 TB/day** — large batch; fewer nodes, less shuffle overhead |
| **r5d.2xlarge** | 8 | 64 GB | Yes | **Memory-heavy** — big joins, OOM on i3; use only when needed |
| **m5d.2xlarge** | 8 | 32 GB | Yes | **Balanced** — if i3 unavailable; less local SSD than i3 |

**Rule**: Use **i3** for most Spark workloads. Switch to **r5d** only when you hit memory limits.

---

### 2.2 Quick Reference Table

| Volume | Instance | Workers | Shuffle | Runtime | When to use this instance |
|--------|----------|---------|---------|---------|---------------------------|
| 50 GB | i3.xlarge | 2 | 64 | ~20 min | Small workloads; cheapest |
| 100 GB | i3.xlarge | 2–6 (autoscale) | 128 | ~45 min | Standard small prod |
| 500 GB | i3.2xlarge | 4–16 (autoscale) | 256 | ~1.5 h | First time you need bigger nodes |
| 1 TB | i3.2xlarge | 8–24 (autoscale) | 512 | ~3 h | Same instance, more workers |
| 10 TB | i3.4xlarge | 20–50 (autoscale) | 800 | ~6 h | Big nodes to reduce shuffle overhead |

---

### 2.3 Scenario: 50 GB/day

**When**: Dev, small prod, nightly reports.

**Cluster config** (Databricks job cluster):

```json
{
  "new_cluster": {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 2,
    "autotermination_minutes": 0,
    "spark_conf": {
      "spark.sql.shuffle.partitions": "64",
      "spark.sql.files.maxPartitionBytes": "134217728",
      "spark.sql.adaptive.enabled": "true"
    }
  }
}
```

**Job code**:

```python
spark.conf.set("spark.sql.shuffle.partitions", "64")
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")  # 128 MB
spark.conf.set("spark.sql.adaptive.enabled", "true")

df = spark.read.format("delta").load("/mnt/lake/raw/events")
df.write.format("delta").mode("overwrite").partitionBy("date").save("/mnt/lake/silver/events")
```

---

### 2.4 Scenario: 100 GB/day

**When**: Common production batch (daily ETL).

**Cluster config**:

```json
{
  "new_cluster": {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "autoscale": { "min_workers": 2, "max_workers": 6 },
    "autotermination_minutes": 0,
    "spark_conf": {
      "spark.sql.shuffle.partitions": "128",
      "spark.sql.files.maxPartitionBytes": "134217728",
      "spark.sql.adaptive.enabled": "true"
    }
  }
}
```

**Job code**:

```python
spark.conf.set("spark.sql.shuffle.partitions", "128")
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

---

### 2.5 Scenario: 500 GB/day

**When**: Medium production. **Switch to i3.2xlarge** (8 vCPU, 61 GB RAM).

**Cluster config**:

```json
{
  "new_cluster": {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.2xlarge",
    "autoscale": { "min_workers": 4, "max_workers": 16 },
    "autotermination_minutes": 0,
    "spark_conf": {
      "spark.sql.shuffle.partitions": "256",
      "spark.sql.files.maxPartitionBytes": "134217728",
      "spark.sql.adaptive.enabled": "true"
    }
  }
}
```

**Job code**:

```python
spark.conf.set("spark.sql.shuffle.partitions", "256")
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

---

### 2.6 Scenario: 1 TB/day

**When**: Large production. Same instance as 500 GB, more workers.

**Cluster config**:

```json
{
  "new_cluster": {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.2xlarge",
    "autoscale": { "min_workers": 8, "max_workers": 24 },
    "autotermination_minutes": 0,
    "spark_conf": {
      "spark.sql.shuffle.partitions": "512",
      "spark.sql.files.maxPartitionBytes": "134217728",
      "spark.sql.adaptive.enabled": "true"
    }
  }
}
```

**Job code**:

```python
spark.conf.set("spark.sql.shuffle.partitions", "512")
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

**Cost tip**: Add spot instances (e.g. 50% spot) if the job can tolerate preemption.

---

### 2.7 Scenario: 10 TB/day

**When**: Very large batch. **Switch to i3.4xlarge** (16 vCPU, 122 GB) to reduce node count and shuffle overhead.

**Cluster config**:

```json
{
  "new_cluster": {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.4xlarge",
    "autoscale": { "min_workers": 20, "max_workers": 50 },
    "autotermination_minutes": 0,
    "spark_conf": {
      "spark.sql.shuffle.partitions": "800",
      "spark.sql.files.maxPartitionBytes": "134217728",
      "spark.sql.adaptive.enabled": "true"
    }
  }
}
```

**Job code**:

```python
spark.conf.set("spark.sql.shuffle.partitions", "800")
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

**Extra**: Consider splitting by partition (e.g. one job per day) and run `OPTIMIZE` + `Z-ORDER BY` on Delta tables.

---

## 3. Impact of File Formats on Scaling

### 3.1 Which Format, Which Instance/Workers

| Format | Throughput | Same 100 GB/day — what changes? |
|--------|------------|--------------------------------|
| **Parquet / Delta / ORC** | Fastest | Use Section 2 config as-is |
| **Avro** | ~1.2× slower | Add ~20–50% workers, or allow 1.2× longer runtime |
| **JSON** | ~1.5–2× slower | Add 50–100% workers, or allow 1.5–2× longer runtime |
| **CSV** | ~1.5–2× slower | Same as JSON; consider convert-to-Parquet first |

### 3.2 Simple Examples by Format

**Parquet** (use Section 2 as-is):

```python
df = spark.read.format("parquet").load("/mnt/raw/events")
df.write.format("delta").partitionBy("date").save("/mnt/silver/events")
```

**JSON** (need more workers or longer run; always pass schema):

```python
from pyspark.sql.types import StructType, StructField, StringType, LongType
schema = StructType([
    StructField("event_id", StringType()),
    StructField("user_id", StringType()),
    StructField("timestamp", LongType())
])
df = spark.read.schema(schema).json("/mnt/raw/events")
df.write.format("delta").partitionBy("date").save("/mnt/silver/events")
```

**CSV** (same as JSON; specify schema and options):

```python
df = spark.read.option("header", "true").option("delimiter", ",").csv("/mnt/raw/events")
df.write.format("delta").partitionBy("date").save("/mnt/silver/events")
```

**Delta** (run OPTIMIZE for small files):

```sql
OPTIMIZE delta.`/mnt/silver/events` ZORDER BY (date, user_id)
```

---

## 4. Batch vs Real-Time: Scenarios and Config

### 4.1 When to Use Which

| Need | Use | Example |
|------|-----|---------|
| Freshness in seconds/minutes | **Real-time (streaming)** | Alerts, live dashboards |
| Periodic bulk load (hourly/daily) | **Batch** | Nightly ETL, reporting |
| Both | **Hybrid (Lambda)** | Streaming for hot path, batch for backfill |

### 4.2 Batch vs Real-Time: Instance and Config

| Aspect | Batch | Real-time |
|--------|--------|------------|
| **Cluster** | Job cluster (spin up, run, terminate) | Long-running or serverless |
| **Sizing** | By volume per run (Section 2) | By events/sec and lag |
| **Instance** | i3.xlarge → i3.4xlarge by volume | Same family; size by throughput |
| **Config** | `shuffle.partitions`, `maxPartitionBytes`, AQE | Consumer count = partition count |

### 4.3 Example: Batch 100 GB/day

```json
{ "node_type_id": "i3.xlarge", "autoscale": { "min_workers": 2, "max_workers": 6 } }
```

### 4.4 Example: Real-time 100 GB/day (Kafka)

- 100 GB/day ≈ 1.2 MB/s average; with 3× peak ≈ 3.6 MB/s
- Kafka topic: e.g. 8 partitions
- Consumers: 4–8 (match or slightly under partition count)
- Cluster: 2–4 workers, i3.xlarge; monitor lag

```python
df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "...").load()
# ... transform ...
df.writeStream.format("delta").option("checkpointLocation", "/mnt/checkpoints/events").start("/mnt/silver/events")
```

---

## 5. What to Consider When Building Scalable Pipelines

### 5.1 Partitioning and Layout

- **Partition by time** (year/month/day) for time-range queries and partition-level retries
- **Avoid too many small files** — use `OPTIMIZE`, compaction, or coalesce
- **Avoid single huge files** (> 1 GB) — tune `maxPartitionBytes` or split writes
- **Z-order** (Delta) on hot filter columns

### 5.2 Parallelism and Skew

- **Shuffle partitions**: 2–4× total cores; use AQE
- **Skew**: Hot keys → use salting, split, or broadcast
- **Source parallelism**: DB = split by key range; Kafka = consumers ≤ partitions

### 5.3 Idempotency and Failure Handling

- **Writes**: Overwrite by partition or merge by key
- **Retries**: Retry by partition, not full pipeline
- **Streaming**: Checkpoint so restart resumes from last offset

### 5.4 Cost

- **Right-size**: Use the tables in Section 2; avoid 20 workers for 100 GB/day
- **Job clusters**: Prefer over always-on for batch
- **Spot**: Use for batch when jobs are retriable

### 5.5 Summary Checklist

1. **Volume** → pick instance and workers from Section 2
2. **Format** → Parquet/Delta best; JSON/CSV need more workers or conversion
3. **Batch vs real-time** → job cluster vs long-running; consumers = partitions for Kafka
4. **Partitioning** → time partitions, compaction, Z-order
5. **Skew** → salting, split, broadcast
6. **Idempotency** → overwrite by partition or merge by key
7. **Cost** → right-size, job clusters, spot
