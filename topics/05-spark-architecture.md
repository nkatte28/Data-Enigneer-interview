# Topic 5: Apache Spark Architecture and Fundamentals

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Understand Spark's master-slave architecture (Driver and Executors)
- Explain how Spark executes programs internally (DAG, stages, tasks)
- Differentiate between RDD, DataFrame, and Dataset APIs
- Understand transformations (narrow vs wide) and actions
- Explain lazy evaluation and its benefits
- Understand Spark joins (broadcast, shuffle, sort-merge)
- Configure Spark resources and deployment modes
- Use shared variables (broadcast variables and accumulators)
- Understand partitioning strategies (coalesce, repartition, hash partitioning)

---

## 📖 Spark Architecture Overview

### Master-Slave Architecture

Spark follows a **master-slave architecture**:
- **Driver (Master)**: Controls the Spark application and creates SparkSession
- **Executors (Slaves)**: Worker nodes responsible for running individual tasks

### Components

**1. Driver**
- Main process that controls the Spark application
- Creates SparkSession/SparkContext
- Analyzes, distributes, schedules, and monitors work across executors
- Converts user program into tasks and schedules them on executors

**2. Executors**
- Worker nodes responsible for running individual tasks
- Launched at the beginning of a Spark application
- Run for the entire lifecycle of an application
- Execute tasks assigned by the driver
- Store computation results in-memory, cache, or on disk
- Return results to the driver after task completion

**3. Worker Node**
- A node that can run Spark application code in a cluster
- Executes tasks assigned by the Cluster Manager
- Returns results back to Spark Context

**4. Cluster Manager**
- Responsible for scheduling and allocation of resources across the cluster
- Types:
  - **Spark Standalone Cluster**
  - **YARN Mode**
  - **Apache Mesos**

---

## 🔧 Core Spark Components

### SparkSession

**SparkSession** provides a single point of entry to interact with underlying Spark functionality. It allows programs to:
- Create DataFrame, Dataset, RDD
- Execute SQL
- Perform Transformations & Actions

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()
```

### SparkConf

**SparkConf** stores configuration parameters that your Spark driver application will pass to SparkContext.

```python
from pyspark import SparkConf

conf = SparkConf().setAppName("MyApp").setMaster("local[*]")
conf.set("spark.executor.memory", "2g")
conf.set("spark.executor.cores", "4")
```

### SparkContext

**SparkContext** is created by Spark Driver for each Spark application when it is first submitted. It:
- Exists throughout the lifetime of the Spark application
- Is the main entry point into Spark functionality
- Allows Spark Driver to access the cluster through Cluster Resource Manager
- Can be used to create RDDs

**Note**: In Spark 2.0+, SparkContext is created automatically when you create a SparkSession. You can access it via `spark.sparkContext`.

---

## 📊 Spark Execution Model

### How Spark Internally Executes a Program

1. **User performs an action** on an RDD/DataFrame
2. **SparkContext** gives the program to the driver
3. **Driver creates DAG** (Directed Acyclic Graph) or execution plan (job)
4. **Driver divides DAG into stages** based on shuffle boundaries
5. **Stages are divided into tasks** (one task per partition)
6. **Tasks are assigned to executors** for execution
7. **Executors execute tasks** and return results to driver
8. **Driver aggregates results** and returns final output

### Key Concepts

**Job**: Created when you invoke an action on RDD/DataFrame. Jobs are the main function that has to be done and is submitted to Spark.

**Stage**: Jobs are divided into stages depending on how they can be separately carried out (mainly on shuffle boundaries). Stages are sets of parallel tasks.

**Task**: Stages are divided into tasks. Tasks are the smallest unit of work that has to be done by the executor. There is one task per partition.

**Partition**: A partition is a chunk of data that can be processed independently on a single executor.

### Example: Job → Stage → Task

```
Job (Action: count())
  ├── Stage 1 (Narrow transformations: map, filter)
  │     ├── Task 1 (Partition 1)
  │     ├── Task 2 (Partition 2)
  │     └── Task 3 (Partition 3)
  └── Stage 2 (Wide transformation: reduceByKey)
        ├── Task 1 (Partition 1)
        ├── Task 2 (Partition 2)
        └── Task 3 (Partition 3)
```

### How Many Tasks Does an Executor Have?

- `--executor-cores 5` means each executor can run a maximum of **5 tasks simultaneously**
- The number of tasks depends on the number of partitions in your RDD/DataFrame
- Each partition gets one task
- Tasks run in parallel up to the executor cores limit

---

## 🚀 Spark Application Submission

### spark-submit

**spark-submit** is a script used to launch Spark applications on the cluster. It:
- Can connect to different cluster managers
- Controls how many resources the application gets
- Can run the driver within the cluster (YARN) or on local machine

### spark-submit Steps

1. **User submits job** using `spark-submit`
2. **spark-submit launches Driver** which executes the `main()` method
3. **Driver contacts Cluster Manager** and requests resources to launch Executors
4. **Cluster Manager launches Executors** on behalf of the Driver
5. **Executors establish direct connection** with the Driver
6. **Driver determines total number of Tasks** by checking the Lineage
7. **Driver creates Logical and Physical Plan**
8. **Spark allocates Tasks to Executors**
9. **Tasks run on Executors** and return results to Driver
10. **When all Tasks complete**, `main()` method exits (calls `sparkContext.stop()`)
11. **Spark releases all resources** from the Cluster Manager

### Example spark-submit Command

```bash
spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master yarn \
  --deploy-mode cluster \
  --executor-memory 2g \
  --executor-cores 4 \
  --num-executors 10 \
  /path/to/spark-examples.jar \
  1000
```

---

## 🔄 Lazy Evaluation

### What is Lazy Evaluation?

**Lazy evaluation** means execution will not start until an action is triggered. Transformations are lazy in nature - when you call an operation on RDD/DataFrame, it does not execute immediately. Spark adds them to a DAG of computation, and only when the driver requests data, this DAG actually gets executed.

### Advantages of Lazy Evaluation

1. **Optimization**: Provides optimization by reducing the number of queries
2. **Resource Efficiency**: Helps optimize disk and memory usage in Spark
3. **Performance**: Saves back and forth between driver and cluster, speeding up the process
4. **Better Resource Utilization**: Resources are utilized better when Spark uses lazy evaluation

### Example

```python
# Transformations (lazy - not executed yet)
df_filtered = df.filter("age > 25")
df_selected = df_filtered.select("name", "age")
df_grouped = df_selected.groupBy("age").count()

# Action (triggers execution)
result = df_grouped.collect()  # Now all transformations execute
```

---

## 📈 Spark UI

**Spark UI** allows you to look at the details of each processing stage. It shows:
- Detail information and metrics about time taken to execute each task
- Amount of input data processed
- Amount of output data produced
- Task execution timeline
- Executor status and resource usage
- Shuffle read/write statistics

**Access**: `http://<driver-node>:4040` (default port)

---

## 💾 RDD (Resilient Distributed Dataset)

### What is RDD?

**RDD (Resilient Distributed Dataset)** is an immutable distributed collection of elements, partitioned across nodes in your cluster that can be operated in parallel with a low-level API that offers transformations and actions.

**Formally**: RDD is a read-only partitioned collection of records.

### RDD Characteristics

1. **Resilient**: Can rebuild lost data partitions using lineage
2. **Distributed**: Data is partitioned across cluster nodes
3. **Dataset**: Collection of data elements
4. **Immutable**: Cannot be modified after creation
5. **Lazy**: Transformations are lazy (executed only on actions)

### Creating RDDs

```python
# From parallelized collection
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5])

# From external data source
rdd = spark.sparkContext.textFile("hdfs://path/to/file.txt")

# From DataFrame
rdd = df.rdd
```

### RDD Lineage

**RDD Lineage** is a process that rebuilds lost data partitions. Spark does not support data replication in memory, so if any data is lost, it uses RDD lineage to rebuild it.

**Lineage Graph**: Tracks all transformations applied to create the RDD, allowing Spark to recompute lost partitions.

---

## 🔀 Transformations

**Transformations** are functions that produce new RDDs from existing RDDs. They:
- Take RDD as input and produce one or more RDDs as output
- Are **lazy** - do not execute until an action occurs
- Create a lineage graph

### Types of Transformations

#### Narrow Transformations

**Narrow transformations** don't require data to be shuffled across partitions.

**Characteristics**:
- All elements required to compute records in a single partition live in a single partition of parent RDD
- No data movement across network
- Examples: `map()`, `filter()`, `flatMap()`, `mapPartitions()`

```python
# Narrow transformation - no shuffle
rdd_filtered = rdd.filter(lambda x: x > 10)
rdd_mapped = rdd.map(lambda x: x * 2)
```

#### Wide Transformations

**Wide transformations** require data to be shuffled across partitions.

**Characteristics**:
- Elements required to compute records in a single partition may live in many partitions of parent RDD
- Requires data movement across network (shuffle)
- Examples: `groupByKey()`, `reduceByKey()`, `join()`, `repartition()`

```python
# Wide transformation - requires shuffle
rdd_grouped = rdd.groupByKey()
rdd_reduced = rdd.reduceByKey(lambda a, b: a + b)
```

### Common Transformations

**map()**: Applies a function to each element
```python
rdd.map(lambda x: x * 2)
```

**flatMap()**: Applies a function that returns a sequence, then flattens the results
```python
rdd.flatMap(lambda x: x.split(" "))
```

**filter()**: Returns elements that satisfy a predicate
```python
rdd.filter(lambda x: x > 10)
```

**mapPartitions()**: Applies a function to each partition (more efficient than map)
```python
def process_partition(iterator):
    # Process entire partition at once
    return [x * 2 for x in iterator]

rdd.mapPartitions(process_partition)
```

**Difference between map() and mapPartitions()**:
- **map()**: Function is applied to each element individually
  - If you have 50 lines in 5 partitions, function is called **50 times**
- **mapPartitions()**: Function is applied to each partition
  - If you have 50 lines in 5 partitions, function is called **5 times**
  - More efficient for operations that can process partitions as a whole

### Pair RDD Operations

**Pair RDD**: RDD containing key/value pairs. Spark provides special operations on Pair RDDs.

**reduceByKey()**: Reduces values for each key
```python
rdd.reduceByKey(lambda a, b: a + b)
```

**groupByKey()**: Groups values for each key
```python
rdd.groupByKey()
```

**Difference between reduceByKey() and groupByKey()**:
- **reduceByKey()**: 
  - Performs reduce operation within each partition first
  - Reduces network traffic
  - More efficient
  - Combines values before shuffling
- **groupByKey()**:
  - Cannot perform operation within each partition
  - Very expensive - gives more shuffles
  - Shuffles all key-value pairs
  - Groups all values first, then processes

**Best Practice**: Use `reduceByKey()` instead of `groupByKey()` when possible.

---

## ⚡ Actions

**Actions** are operations that return values to the driver program or write data to external storage. After an action is performed, data from RDD moves back to the local machine.

### Common Actions

**collect()**: Returns all elements to driver (use with caution - can cause OOM)
```python
result = rdd.collect()
```

**count()**: Returns number of elements
```python
count = rdd.count()
```

**take(n)**: Returns first n elements
```python
first_10 = rdd.take(10)
```

**reduce()**: Aggregates elements using a function
```python
sum = rdd.reduce(lambda a, b: a + b)
```

**saveAsTextFile()**: Saves RDD as text file
```python
rdd.saveAsTextFile("hdfs://path/to/output")
```

**foreach()**: Applies a function to each element
```python
rdd.foreach(lambda x: print(x))
```

---

## 📊 DataFrame

### What is DataFrame?

**DataFrame** is a distributed collection of data organized into named columns. Conceptually, it is equivalent to a table or schema in an RDBMS.

**Key Points**:
- Has a schema (structure) bound on top of RDDs
- Improves performance and provides structured operations
- Can be constructed from Hive tables, Structured Data files, external databases, or existing RDDs
- In Spark 2.0+, DataFrame APIs merged with Datasets APIs
- DataFrame = `Dataset[Row]` (untyped)

### Creating DataFrames

```python
# From RDD
df = spark.createDataFrame(rdd, schema)

# From external sources
df = spark.read.parquet("path/to/file.parquet")
df = spark.read.json("path/to/file.json")
df = spark.read.csv("path/to/file.csv")
df = spark.sql("SELECT * FROM table")
```

### DataFrame Advantages

- **Schema**: Has explicit schema
- **Optimization**: Catalyst Optimizer provides query optimization
- **Expressiveness**: More expressive than RDDs
- **Performance**: More efficient than RDDs

### DataFrame Limitations

- **Untyped**: Runtime errors possible (no compile-time type checking)
- **Analysis Errors**: Encountered only at runtime

---

## 🎯 Dataset API

### What is Dataset?

**Dataset API** is an extension to DataFrames that provides a type-safe, object-oriented programming interface. It is a strongly-typed, immutable collection of objects mapped to a relational schema.

**Key Points**:
- Strongly typed
- Partitioned across a cluster
- Can be cached in memory
- Provides compile-time type safety

### Dataset vs DataFrame

**DataFrame**:
- Untyped (`Dataset[Row]`)
- Runtime errors for analysis errors
- Syntax errors at compile time

**Dataset**:
- Typed (`Dataset[YourClass]`)
- Both syntax errors and analysis errors at compile time
- Type-safe operations on domain objects

### Example: Type Safety

```python
# DataFrame - Runtime error
df.select("wrong_column")  # Fails at runtime

# Dataset - Compile-time error
dataset.select("wrong_column")  # Fails at compile time
```

### When to Use DataFrame vs Dataset?

- **DataFrame**: Use when you only need SQL operations or don't need type safety
- **Dataset**: Use when you want type safety and compile-time error checking

---

## 📋 RDD vs DataFrame vs Dataset Comparison

| Feature | RDD | DataFrame | Dataset |
|---------|-----|-----------|---------|
| **Schema** | No schema | Has schema | Has schema |
| **Type Safety** | Typed (compile-time) | Untyped (runtime) | Typed (compile-time) |
| **API Level** | Low-level | High-level | High-level |
| **Optimization** | No optimization | Catalyst Optimizer | Catalyst Optimizer |
| **Performance** | Lower | Higher | Higher |
| **Expressiveness** | Less expressive | More expressive | More expressive |
| **Use Case** | Unstructured data | Structured data | Structured data with type safety |
| **Error Detection** | Compile-time | Runtime | Compile-time |

---

## 🔄 Caching and Persistence

### cache() vs persist()

**cache()**: Default saves to memory (`MEMORY_ONLY`)
```python
df_cached = df.cache()
```

**persist()**: Used to store to user-defined storage level
```python
from pyspark import StorageLevel

df_persist = df.persist(StorageLevel.MEMORY_ONLY)
# or
df_persist = df.persist(StorageLevel.MEMORY_AND_DISK)
```

### Storage Levels

- **MEMORY_ONLY**: Store RDD as deserialized Java objects in JVM
- **MEMORY_ONLY_SER**: Store RDD as serialized Java objects (one byte array per partition)
- **MEMORY_AND_DISK**: Store RDD as deserialized Java objects in JVM, spill to disk if memory is insufficient
- **MEMORY_AND_DISK_SER**: Store RDD as serialized Java objects, spill to disk if memory is insufficient
- **DISK_ONLY**: Store RDD only on disk

### Benefits of Caching/Persistence

- **Cost Efficient**: No need to recalculate results at every stage
- **Time Efficient**: Computation will be faster
- **Iterative Algorithms**: Helps reduce execution time of iterative algorithms on very large datasets

### When to Cache?

- Cache DataFrames/RDDs that are used **multiple times**
- Don't cache small DataFrames (overhead not worth it)
- Works well with large datasets
- Spark automatically monitors cache usage and drops unused data using LRU (Least Recently Used) algorithm

---

## 🔀 Partitioning

### Repartition vs Coalesce

#### Repartition

**repartition()**: Creates new partitions and performs full shuffle of data across network.

**Characteristics**:
- More expensive than coalesce
- Always shuffles all data over network
- Can be used to increase or decrease number of partitions
- Guarantees equal-sized partitions

**Use Cases**:
- When you want to create your own partitions
- When you need equal-sized partitions
- When increasing number of partitions

```python
# Repartition to 10 partitions
df_repartitioned = df.repartition(10)

# Repartition by column
df_repartitioned = df.repartition("date", "region")
```

#### Coalesce

**coalesce()**: Reduces number of partitions without full shuffle.

**Characteristics**:
- More efficient than repartition
- Avoids shuffle operation (minimizes shuffling)
- Can only decrease number of partitions
- Groups partitions that are present in same executor
- May result in unequal-sized files when saving data

**Use Cases**:
- When reducing number of partitions
- When you want to minimize shuffle operations
- Final write stage

```python
# Coalesce to 5 partitions
df_coalesced = df.coalesce(5)
```

### maxRecordsPerFile

**maxRecordsPerFile**: Limits number of records per output file (Spark 2.2+).

**Use Case**: Prevent files that are too large when writing data.

```python
# Method 1: Via option
df.write.option("maxRecordsPerFile", 10000) \
    .mode("overwrite").parquet("output_path")

# Method 2: Via configuration
spark.conf.set("spark.sql.files.maxRecordsPerFile", 10000)
df.write.mode("overwrite").parquet("output_path")
```

### Hash Partitioning

**Hash Partitioning**: Attempts to spread data evenly across partitions based on key.

**Formula**: `partition = key.hashCode() % numPartitions`

**Use Case**: When you want even distribution of data across partitions.

```python
# Hash partitioning by key
df_partitioned = df.repartition("user_id")
```

---

## 🔗 Spark Joins

### Broadcast Join

**Broadcast Join**: Sends smaller DataFrame to all worker nodes as a broadcast variable.

**How it works**:
- Smaller DataFrame is copied to all worker nodes (only once)
- Original parallelism of larger DataFrame is maintained
- No shuffle needed - join happens locally on each executor
- Spark automatically broadcasts DataFrames < 10MB

**Configuration**:
```python
# Increase broadcast threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50mb")

# Manual broadcast
from pyspark.sql.functions import broadcast
result = broadcast(small_df).join(large_df, "join_key", "left")
```

**When to use**:
- Smaller DataFrame fits in executor memory
- Smaller DataFrame < 10MB (or configured threshold)
- Join key distribution is even

**Advantages**:
- Reduces shuffle network traffic
- Fits in memory in single executor
- Faster than shuffle join for small DataFrames

### Shuffle Join

**Shuffle Join**: Requires data to be redistributed across worker nodes based on join key(s).

**How it works**:
1. **Partitioning**: Both datasets partitioned based on join key(s)
2. **Shuffle**: Partitions shuffled across network so rows with same join key are co-located
3. **Local Join**: Join performed locally on each worker node
4. **Result Aggregation**: Results collected and aggregated

**Characteristics**:
- Requires data movement across network
- Resource-intensive due to shuffling
- Uses hash-based or sort-merge join on each node

**Configuration**:
```python
# Set number of shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "200")
```

### Sort-Merge Join

**Sort-Merge Join**: Default join algorithm in Spark 2.3+.

**How it works**:
1. **Sort**: Both datasets sorted based on join key(s)
2. **Merge**: Sorted partitions scanned in parallel, rows with same join key merged

**Characteristics**:
- Does not require data shuffling (if partitions already co-located)
- Offers localized join operations
- Requires partitions to be co-located
- DataFrame should be distributed uniformly on joining columns

**Configuration**:
```python
# Enable/disable sort-merge join preference
spark.conf.set("spark.sql.join.preferSortMergeJoin", "true")
```

**Best Practices for Sort-Merge Join**:
- Ensure partitions are co-located
- DataFrame should be distributed uniformly on joining columns
- Have adequate number of unique keys for parallelism

### spark.sql.shuffle.partitions vs spark.default.parallelism

**spark.sql.shuffle.partitions**:
- Sets number of partitions used when shuffling data for joins or aggregations
- Default: 200
- Used for DataFrames/Datasets

**spark.default.parallelism**:
- Default number of partitions in RDDs returned by transformations like join, reduceByKey
- Default: 200
- **Note**: Only works for raw RDDs, ignored when working with DataFrames

```python
# For RDDs
spark.conf.set("spark.default.parallelism", "200")

# For DataFrames/Datasets
spark.conf.set("spark.sql.shuffle.partitions", "200")
```

---

## 📡 Shared Variables

### Broadcast Variables

**Broadcast Variables**: Read-only variables cached on each node once, rather than sending a copy for all tasks.

**Use Cases**:
- Large dataset or object that needs to be shared across multiple stages/tasks
- Enhancing efficiency of joins between small and large RDDs
- Lookup tables or reference data

**How it works**:
- Variable is serialized and sent to each node only once
- Cached for future reference
- All tasks can access broadcast variable locally
- No need to transfer data over network multiple times

**Example**:
```python
# Create broadcast variable
broadcast_var = spark.sparkContext.broadcast(lookup_dict)

# Use in transformations
def lookup_function(x):
    return broadcast_var.value.get(x, "default")

rdd.map(lookup_function)
```

### Accumulators

**Accumulators**: Variables that are only "added" to, such as counters and sums.

**Use Cases**:
- Aggregating values across distributed computations
- Counting events
- Summing values
- Tracking metrics (error counts, etc.)

**Characteristics**:
- Only associative and commutative operations ensure accurate results
- Useful for collecting statistics or metrics during Spark job execution

**Example**:
```python
# Create accumulator
counter = spark.sparkContext.accumulator(0)

# Use in transformations
def count_function(x):
    counter.add(1)
    return x

rdd.map(count_function).collect()

# Access value
print(counter.value)
```

---

## ⚙️ Resource Allocation

### How to Set Resources for a Spark Job

**Initial Approach**:
1. Start with test run: 4 cores and ~10GB per executor
2. Check metrics on Spark UI after job runs
3. Decide executor memory based on data going to each executor
4. Usually 4-5 cores per executor is optimum

**Number of Executors**:
- Depends mostly on number of partitions in RDD/DataFrame
- If very few partitions, allocating more executors won't improve performance
- Match executors to partition count

### Example: Resource Allocation Calculation

**Cluster Config**:
- 10 Nodes
- 16 cores per Node
- 64GB RAM per Node

**Calculation**:
1. Assign 5 cores per executor → `--executor-cores = 5` (good HDFS throughput)
2. Leave 1 core per node for Hadoop/YARN daemons
   - Available cores per node = 16 - 1 = 15
3. Total available cores = 15 × 10 = 150
4. Number of executors = 150 / 5 = 30
5. Leave 1 executor for ApplicationMaster → `--num-executors = 29`
6. Executors per node = 30 / 10 = 3
7. Memory per executor = 64GB / 3 = 21GB
8. Off-heap overhead = 7% of 21GB = 3GB
9. Actual executor memory = 21 - 3 = 18GB → `--executor-memory = 18g`

**Final Configuration**:
```bash
spark-submit \
  --executor-cores 5 \
  --num-executors 29 \
  --executor-memory 18g \
  ...
```

---

## 🚀 Deployment Modes

### Client Mode (Default)

**Client Mode**: Driver program runs on the same machine (client process) from which the job is submitted.

**Characteristics**:
- Application Master only used for requesting resources from YARN
- If driver program fails, entire job fails
- Supports both interactive shell mode and normal job submission
- **Worst performance** - not used in production

**Use Cases**:
- Development and testing
- Interactive shell mode

### Cluster Mode

**Cluster Mode**: Driver runs inside Application Master process managed by YARN on the cluster.

**Characteristics**:
- Driver program runs on cluster as sub-process of ApplicationMaster
- Client goes away once application is initialized
- Driver program can be re-instantiated in case of failure
- **Not supported in interactive shell mode**
- **Used in real-time production environment**

**Use Cases**:
- Production environments
- Long-running jobs

### Local Mode

**Local Mode**: Driver program and executor run on single JVM in single machine.

**Characteristics**:
- Useful for development, unit testing, debugging
- Limited resources
- High chance of running into out-of-memory
- Cannot be scaled up
- Spark will not re-run failed tasks

**Use Cases**:
- Development
- Unit testing
- Debugging

---

## 📝 Spark Limitations

1. **No File Management System**: 
   - No built-in file management system
   - Depends on other platforms (Hadoop, cloud platforms)

2. **No Real-Time Data Processing**:
   - Spark Streaming partitions live data stream into batches (RDDs)
   - Not true real-time processing

3. **Expensive**:
   - High memory consumption
   - Needs huge RAM for in-memory processing

4. **Small Files Issue**:
   - Problem with small files when using Spark with Hadoop
   - HDFS has limited number of large files but large number of small files
   - Affects processing efficiency

5. **Manual Optimization**:
   - Manual optimization of jobs and datasets required
   - Users must specify number of partitions
   - Partition procedure should be controlled manually

---

## 💾 How Spark Stores Data

**Important**: Spark is a **processing engine**, not a storage engine.

- Spark can retrieve data from any storage engine:
  - HDFS
  - S3
  - Other data resources
- Spark does not store data itself
- Data is read from storage, processed, and written back to storage

---

## 🔧 Spark Logging

### Log4j Configuration

Spark uses **log4j** as the standard library for logging.

**Configuration**:
- Template file: `SPARK_HOME/conf/log4j.properties.template`
- Create `log4j.properties` file in same directory

**Submit with Custom Logging**:
```bash
spark-submit \
  --conf 'spark.driver.extraJavaOptions=-Dlog4j.configuration=log4j.properties' \
  --conf 'spark.executor.extraJavaOptions=-Dlog4j.configuration=log4j.properties' \
  ...
```

---

## ✅ Check Your Understanding

1. What is the difference between Driver and Executor?
2. How does Spark execute a program internally (Job → Stage → Task)?
3. What is lazy evaluation and why is it beneficial?
4. What is the difference between narrow and wide transformations?
5. When should you use RDD vs DataFrame vs Dataset?
6. What is the difference between cache() and persist()?
7. When should you use repartition() vs coalesce()?
8. How does broadcast join differ from shuffle join?
9. What are broadcast variables and accumulators?
10. How do you calculate optimal resource allocation for a Spark job?

---

## 🎯 Next Steps

Once you're comfortable with Spark architecture, move on to:
- **Topic 6: Spark Issues and Troubleshooting** for common problems and solutions

**Study Time**: Spend 2-3 days on this topic, practice with Spark examples.

---

## 📚 Additional Resources

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Spark Programming Guide](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Spark Performance Tuning](https://spark.apache.org/docs/latest/tuning.html)
