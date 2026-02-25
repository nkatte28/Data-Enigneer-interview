# Topic 4: AWS Data Engineering - Complete Guide

## 📑 Table of Contents

### Part 1: Fundamentals
1. [AWS Overview & Architecture](#1-aws-overview--architecture)
2. [Understanding Your Data](#2-understanding-your-data-sample-raw-data)
3. [AWS Storage Services](#3-aws-storage-services)

### Part 2: Data Processing
4. [AWS Glue - Serverless ETL](#4-aws-glue---serverless-etl)
5. [Amazon EMR - Big Data Processing](#5-amazon-emr---big-data-processing)
6. [AWS Lambda - Serverless Functions](#6-aws-lambda---serverless-functions)

### Part 3: Data Warehousing & Analytics
7. [Amazon Redshift - Data Warehouse](#7-amazon-redshift---data-warehouse)
8. [Amazon Athena - Query S3 Data](#8-amazon-athena---query-s3-data)
9. [Amazon DynamoDB - NoSQL Database](#9-amazon-dynamodb---nosql-database)
10. [Amazon Kinesis - Real-Time Streaming](#10-amazon-kinesis---real-time-streaming)

### Part 4: Orchestration & Workflow
11. [AWS Step Functions - Workflow Orchestration](#11-aws-step-functions---workflow-orchestration)
12. [AWS Data Pipeline - ETL Orchestration](#12-aws-data-pipeline---etl-orchestration)

### Part 5: Security & Networking
13. [IAM - Identity & Access Management](#13-iam---identity--access-management)
14. [VPC & Networking](#13-vpc--networking) (incl. CloudFront, VPC endpoints)

### Part 6: Integration & Optimization
15. [Connecting Services Together](#14-connecting-services-together) (incl. [Multi-Cloud: AWS + Databricks](#145-multi-cloud-integration-aws--databricks), [Real-World Scenarios](#146-real-world-data-engineering-scenarios))
16. [Cost Optimization](#16-cost-optimization)
17. [Performance Tuning](#17-performance-tuning)

### Part 7: Interview & Practical
18. [Interview Questions & Answers](#18-aws-interview-questions--answers)
19. [System Design with AWS](#19-system-design-with-aws)
20. [Troubleshooting Common Issues](#20-troubleshooting-common-issues)
21. [Hands-On Exercises](#21-hands-on-exercises)

---

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Understand AWS data engineering architecture
- Master S3 storage patterns and best practices
- Build ETL pipelines with AWS Glue
- Process big data with Amazon EMR
- Design real-time streaming with Kinesis
- Query data with Athena and Redshift
- Orchestrate workflows with Step Functions
- Implement security with IAM and VPC (subnets, endpoints, security groups)
- Use CloudFront for APIs and dashboards; EventBridge and Secrets Manager where relevant
- Integrate AWS with Databricks (S3 lake, optional Glue Catalog) for multi-engine analytics
- Relate real-world scenarios (retail, healthcare, media) to architecture choices
- Optimize costs and performance
- Design scalable data architectures on AWS

---

## 📖 Core Concepts

### 1. AWS Overview & Architecture

**What is AWS?**
Amazon Web Services (AWS) is a cloud computing platform providing on-demand computing resources, storage, and services for data engineering.

**Key AWS Services for Data Engineering**:
- **S3**: Object storage (data lake)
- **Glue**: Serverless ETL
- **EMR**: Big data processing (Spark, Hadoop)
- **Redshift**: Data warehouse
- **Kinesis**: Real-time streaming
- **Athena**: Query S3 with SQL
- **Lambda**: Serverless functions
- **Step Functions**: Workflow orchestration

**AWS Data Engineering Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Data Sources                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  APIs    │  │ Databases │  │  Files   │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Amazon S3                │
        │  (Data Lake - Raw Storage)    │
        │  ┌────────────────────────┐  │
        │  │  Bronze Layer           │  │
        │  │  (Raw Data)             │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   AWS Glue / EMR              │
        │   (ETL Processing)            │
        │  ┌────────────────────────┐  │
        │  │  Transform & Clean      │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Amazon S3                │
        │  (Data Lake - Processed)      │
        │  ┌────────────────────────┐  │
        │  │  Silver/Gold Layers    │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Amazon Redshift / Athena    │
        │   (Query & Analytics)         │
        │  ┌──────────┐  ┌──────────┐ │
        │  │ Redshift │  │  Athena    │ │
        │  └──────────┘  └──────────┘ │
        └──────────────────────────────┘
```

**Key Flow**:
1. **Ingestion**: Data from sources → S3 (Bronze)
2. **Processing**: Glue/EMR transforms data
3. **Storage**: Processed data → S3 (Silver/Gold)
4. **Analytics**: Redshift/Athena query data
5. **Orchestration**: Step Functions coordinate workflow

---

### 2. Understanding Your Data: Sample Raw Data

**Before we start, let's see what we're working with!**

**Sample Raw Sales Data (JSON from API)**:
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
1. Ingest raw data → S3 Bronze layer (as-is)
2. Transform and clean → S3 Silver layer (quality checked)
3. Aggregate and enrich → S3 Gold layer (business-ready)
4. Query and analyze → Redshift/Athena

---

### 3. AWS Storage Services

#### 3.1 Amazon S3 - Object Storage

**What is S3?**
Simple Storage Service - object storage for any amount of data, accessible from anywhere.

**Key Concepts**:
- **Bucket**: Container for objects (like a folder)
- **Object**: File stored in bucket
- **Key**: Object name/path
- **Region**: Geographic location

**S3 Structure**:
```
s3://nike-data-bucket/
├── bronze/
│   ├── sales/
│   │   ├── year=2024/
│   │   │   ├── month=01/
│   │   │   │   ├── day=15/
│   │   │   │   │   └── sales_20240115.json
│   │   │   │   └── day=16/
│   │   │   └── month=02/
│   │   └── customers/
│   └── products/
├── silver/
│   └── sales_cleaned/
└── gold/
    └── sales_aggregated/
```

**Create S3 Bucket** (AWS CLI):
```bash
# Create bucket
aws s3 mb s3://nike-data-bucket --region us-east-1

# Upload file
aws s3 cp sales.json s3://nike-data-bucket/bronze/sales/

# List files
aws s3 ls s3://nike-data-bucket/bronze/sales/ --recursive
```

**Create S3 Bucket** (Python boto3):
```python
import boto3

# Create S3 client
s3_client = boto3.client('s3', region_name='us-east-1')

# Create bucket
s3_client.create_bucket(
    Bucket='nike-data-bucket',
    CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
)

# Upload file
s3_client.upload_file(
    'local_sales.json',
    'nike-data-bucket',
    'bronze/sales/sales_20240115.json'
)

# List objects
response = s3_client.list_objects_v2(
    Bucket='nike-data-bucket',
    Prefix='bronze/sales/'
)
for obj in response.get('Contents', []):
    print(obj['Key'])
```

**S3 Storage Classes** (Cost Optimization):

| Class | Use Case | Cost | Access Time |
|-------|----------|------|-------------|
| **Standard** | Frequently accessed | Highest | Instant |
| **Standard-IA** | Infrequently accessed | Medium | Instant |
| **Glacier** | Archive (rarely accessed) | Low | 3-5 hours |
| **Glacier Deep Archive** | Long-term archive | Lowest | 12 hours |

**Example**:
```python
# Upload to Standard-IA (cheaper for infrequent access)
s3_client.upload_file(
    'sales.json',
    'nike-data-bucket',
    'bronze/sales/sales_20240115.json',
    ExtraArgs={'StorageClass': 'STANDARD_IA'}
)

# Move to Glacier for archive
s3_client.copy_object(
    Bucket='nike-data-bucket',
    CopySource={'Bucket': 'nike-data-bucket', 'Key': 'bronze/sales/sales_20240115.json'},
    Key='archive/sales/sales_20240115.json',
    StorageClass='GLACIER'
)
```

**S3 Best Practices**:
- ✅ Use prefixes (folders) for organization
- ✅ Enable versioning for important data
- ✅ Use lifecycle policies (move old data to Glacier)
- ✅ Enable encryption (SSE-S3 or SSE-KMS)
- ✅ Use appropriate storage classes
- ✅ Partition by date (year/month/day) for efficient queries

---

#### 3.2 S3 Partitioning Strategy

**Why Partition?**
- Faster queries (only read relevant partitions)
- Lower costs (less data scanned)
- Better performance (parallel processing)

**Partitioning Example**:
```
# Bad: No partitioning
s3://nike-data-bucket/sales/sales.json  # All data in one file

# Good: Partitioned by date
s3://nike-data-bucket/sales/
├── year=2024/
│   ├── month=01/
│   │   ├── day=15/
│   │   │   └── sales_20240115.json
│   │   └── day=16/
│   │       └── sales_20240116.json
│   └── month=02/
│       └── day=01/
│           └── sales_20240201.json
```

**Query Benefits**:
```sql
-- Query only January 2024 data (only scans month=01 partition)
SELECT * FROM sales
WHERE year = 2024 AND month = 01;

-- Without partitioning: Scans ALL data
-- With partitioning: Scans only month=01 partition ✅
```

---

### 4. AWS Glue - Serverless ETL

**What is AWS Glue?**
Fully managed ETL service that makes it easy to prepare and transform data for analytics.

**Key Components**:
- **Glue Data Catalog**: Metadata repository (like Hive Metastore)
- **Glue Jobs**: ETL scripts (Python or Scala)
- **Glue Crawlers**: Auto-discover schema
- **Glue Studio**: Visual ETL builder

**Glue Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Source Data                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   S3     │  │  RDS     │  │  JDBC    │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Glue Crawler                │
        │   (Discover Schema)           │
        │  ┌────────────────────────┐  │
        │  │  Scan Data              │  │
        │  │  Infer Schema          │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Glue Data Catalog           │
        │   (Metadata Store)            │
        │  ┌────────────────────────┐  │
        │  │  Tables & Schemas      │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Glue Job                    │
        │   (ETL Processing)            │
        │  ┌────────────────────────┐  │
        │  │  Read from Catalog      │  │
        │  │  Transform Data        │  │
        │  │  Write to S3           │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Amazon S3                │
        │  (Transformed Data)           │
        └──────────────────────────────┘
```

#### 4.1 Glue Data Catalog

**What is Data Catalog?**
Centralized metadata repository that stores table definitions and schemas.

**Create Table Manually**:
```python
import boto3

glue_client = boto3.client('glue')

# Create database
glue_client.create_database(
    DatabaseInput={
        'Name': 'nike_sales_db',
        'Description': 'Nike sales data database'
    }
)

# Create table
glue_client.create_table(
    DatabaseName='nike_sales_db',
    TableInput={
        'Name': 'raw_sales',
        'StorageDescriptor': {
            'Columns': [
                {'Name': 'sale_id', 'Type': 'string'},
                {'Name': 'customer_id', 'Type': 'bigint'},
                {'Name': 'product_id', 'Type': 'bigint'},
                {'Name': 'amount', 'Type': 'double'},
                {'Name': 'sale_date', 'Type': 'string'}
            ],
            'Location': 's3://nike-data-bucket/bronze/sales/',
            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'SerdeInfo': {
                'SerializationLibrary': 'org.openx.data.jsonserde.JsonSerDe'
            }
        },
        'PartitionKeys': [
            {'Name': 'year', 'Type': 'string'},
            {'Name': 'month', 'Type': 'string'},
            {'Name': 'day', 'Type': 'string'}
        ]
    }
)
```

**Use Glue Crawler** (Automatic):
```python
# Create crawler to auto-discover schema
glue_client.create_crawler(
    Name='nike-sales-crawler',
    Role='arn:aws:iam::123456789012:role/GlueServiceRole',
    DatabaseName='nike_sales_db',
    Targets={
        'S3Targets': [
            {
                'Path': 's3://nike-data-bucket/bronze/sales/'
            }
        ]
    }
)

# Run crawler
glue_client.start_crawler(Name='nike-sales-crawler')
```

#### 4.2 Glue Jobs - ETL Scripts

**What are Glue Jobs?**
Python or Scala scripts that run on serverless Spark to transform data.

**Simple Glue Job (Python)**:
```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read from Glue Data Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="nike_sales_db",
    table_name="raw_sales"
)

# Transform: Filter valid sales (amount > 0)
def filter_valid_sales(record):
    return record["amount"] > 0

filtered = Filter.apply(
    frame=datasource,
    f=filter_valid_sales
)

# Transform: Add ingestion timestamp
from awsglue.transforms import Map
from datetime import datetime

def add_timestamp(record):
    record["ingestion_time"] = datetime.now().isoformat()
    return record

with_timestamp = Map.apply(
    frame=filtered,
    f=add_timestamp
)

# Write to S3 (Silver layer)
glueContext.write_dynamic_frame.from_options(
    frame=with_timestamp,
    connection_type="s3",
    connection_options={
        "path": "s3://nike-data-bucket/silver/sales_cleaned/"
    },
    format="json"
)

job.commit()
```

**Glue Job with Spark DataFrame**:
```python
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Read from S3
df = spark.read.json("s3://nike-data-bucket/bronze/sales/")

# Transform
cleaned_df = df \
    .filter(F.col("amount") > 0) \
    .filter(F.col("customer_id").isNotNull()) \
    .withColumn("ingestion_time", F.current_timestamp()) \
    .withColumn("year", F.year(F.to_date("sale_date"))) \
    .withColumn("month", F.month(F.to_date("sale_date"))) \
    .withColumn("day", F.dayofmonth(F.to_date("sale_date")))

# Write to S3 (partitioned)
cleaned_df.write \
    .mode("overwrite") \
    .partitionBy("year", "month", "day") \
    .parquet("s3://nike-data-bucket/silver/sales_cleaned/")
```

**Create Glue Job** (boto3):
```python
glue_client.create_job(
    Name='nike-sales-etl-job',
    Role='arn:aws:iam::123456789012:role/GlueServiceRole',
    Command={
        'Name': 'glueetl',
        'ScriptLocation': 's3://nike-glue-scripts/sales_etl.py',
        'PythonVersion': '3'
    },
    DefaultArguments={
        '--job-language': 'python',
        '--job-bookmark-option': 'job-bookmark-enable'
    },
    GlueVersion='3.0',
    NumberOfWorkers=2,
    WorkerType='G.1X'
)

# Start job
glue_client.start_job_run(JobName='nike-sales-etl-job')
```

**Glue Job Bookmarks** (Incremental Processing):
```python
# Enable bookmarks to track processed data
# Only process new data since last run

# In job arguments:
# --job-bookmark-option job-bookmark-enable

# Glue automatically tracks:
# - Last processed file
# - Last processed record
# - Only processes new data ✅
```

**Best Practices**:
- ✅ Use Glue Data Catalog for metadata
- ✅ Use Crawlers for schema discovery
- ✅ Enable job bookmarks for incremental processing
- ✅ Right-size workers (G.1X, G.2X, G.025X)
- ✅ Use appropriate file formats (Parquet for analytics)
- ✅ Partition output data

---

### 5. Amazon EMR - Big Data Processing

**What is Amazon EMR?**
Elastic MapReduce - managed big data platform for processing large datasets using Spark, Hadoop, Hive, etc.

**Key Components**:
- **Cluster**: Group of EC2 instances (master + core nodes)
- **Spark**: Distributed processing engine
- **Hive**: SQL on Hadoop
- **Hadoop**: Distributed storage and processing

**EMR Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Master Node                                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Resource Manager (YARN)                          │ │
│  │  NameNode (HDFS)                                   │ │
│  │  Spark Master                                      │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Core Node 1  │  │ Core Node 2  │  │ Core Node 3  │
│ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │
│ │Executor  │ │  │ │Executor  │ │  │ │Executor  │ │
│ │DataNode  │ │  │ │DataNode  │ │  │ │DataNode  │ │
│ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ↓
        ┌──────────────────────────────┐
        │      Amazon S3                │
        │  (Read/Write Data)           │
        └──────────────────────────────┘
```

#### 5.1 Create EMR Cluster

**Create Cluster** (AWS CLI):
```bash
aws emr create-cluster \
  --name "nike-sales-processing" \
  --release-label emr-6.15.0 \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --applications Name=Spark Name=Hive \
  --ec2-attributes KeyName=my-key-pair \
  --log-uri s3://nike-emr-logs/ \
  --steps Type=Spark,Name="Process Sales",ActionOnFailure=CONTINUE,Args=[s3://nike-scripts/process_sales.py]
```

**Create Cluster** (boto3):
```python
import boto3

emr_client = boto3.client('emr', region_name='us-east-1')

response = emr_client.run_job_flow(
    Name='nike-sales-processing',
    ReleaseLabel='emr-6.15.0',
    Applications=[
        {'Name': 'Spark'},
        {'Name': 'Hive'}
    ],
    Instances={
        'InstanceGroups': [
            {
                'Name': 'Master',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'MASTER',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1
            },
            {
                'Name': 'Core',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'CORE',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 2
            }
        ],
        'Ec2KeyName': 'my-key-pair',
        'Ec2SubnetId': 'subnet-12345678'
    },
    LogUri='s3://nike-emr-logs/',
    ServiceRole='EMR_DefaultRole',
    JobFlowRole='EMR_EC2_DefaultRole',
    Steps=[
        {
            'Name': 'Process Sales Data',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'spark-submit',
                    '--deploy-mode', 'cluster',
                    's3://nike-scripts/process_sales.py'
                ]
            }
        }
    ]
)

cluster_id = response['JobFlowId']
print(f"Cluster ID: {cluster_id}")
```

#### 5.2 Spark Job on EMR

**Spark Job Script** (process_sales.py):
```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Create Spark session
spark = SparkSession.builder \
    .appName("Nike Sales Processing") \
    .getOrCreate()

# Read from S3
sales_df = spark.read.json("s3://nike-data-bucket/bronze/sales/")

# Transform
cleaned_df = sales_df \
    .filter(F.col("amount") > 0) \
    .filter(F.col("customer_id").isNotNull()) \
    .withColumn("year", F.year(F.to_date("sale_date"))) \
    .withColumn("month", F.month(F.to_date("sale_date"))) \
    .withColumn("day", F.dayofmonth(F.to_date("sale_date")))

# Aggregate
daily_sales = cleaned_df \
    .groupBy("year", "month", "day", "customer_id") \
    .agg(
        F.sum("amount").alias("daily_revenue"),
        F.count("*").alias("transaction_count")
    )

# Write to S3 (Parquet format)
daily_sales.write \
    .mode("overwrite") \
    .partitionBy("year", "month", "day") \
    .parquet("s3://nike-data-bucket/gold/daily_sales/")

spark.stop()
```

**Submit Job to Running Cluster**:
```python
# Submit Spark job to running EMR cluster
emr_client.add_job_flow_steps(
    JobFlowId=cluster_id,
    Steps=[
        {
            'Name': 'Process Sales',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'spark-submit',
                    '--deploy-mode', 'cluster',
                    's3://nike-scripts/process_sales.py'
                ]
            }
        }
    ]
)
```

**EMR vs Glue**:

| Aspect | EMR | Glue |
|-------|-----|------|
| **Control** | Full control | Managed |
| **Setup** | More complex | Simple |
| **Cost** | Pay for cluster time | Pay per job |
| **Use Case** | Complex processing | Standard ETL |
| **Scaling** | Manual | Automatic |

**Best Practices**:
- ✅ Use spot instances for cost savings (up to 90%)
- ✅ Right-size cluster (don't over-provision)
- ✅ Use S3 for storage (not HDFS)
- ✅ Terminate cluster when done
- ✅ Use appropriate instance types (m5 for compute, r5 for memory)

---

### 6. AWS Lambda - Serverless Functions

**What is Lambda?**
Serverless compute service that runs code in response to events without managing servers.

**Key Features**:
- ✅ Pay per execution (no idle costs)
- ✅ Auto-scaling
- ✅ Event-driven
- ✅ Multiple languages (Python, Node.js, Java, etc.)

**Lambda Use Cases**:
- Trigger ETL jobs
- Process S3 events
- Transform data on-the-fly
- API endpoints

**Lambda Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Event Sources                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   S3     │  │  API     │  │  Kinesis │            │
│  │ (Upload) │  │ Gateway  │  │ (Stream) │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   AWS Lambda Function         │
        │  ┌────────────────────────┐  │
        │  │  Process Event         │  │
        │  │  Transform Data        │  │
        │  │  Trigger Next Step    │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Destination               │
        │  ┌──────────┐  ┌──────────┐ │
        │  │   S3     │  │  Glue    │ │
        │  │  DynamoDB│  │  SNS     │ │
        │  └──────────┘  └──────────┘ │
        └──────────────────────────────┘
```

#### 6.1 Lambda Function Example

**Lambda Function** (Python):
```python
import json
import boto3

s3_client = boto3.client('s3')
glue_client = boto3.client('glue')

def lambda_handler(event, context):
    """
    Triggered when file uploaded to S3
    Processes file and triggers Glue job
    """
    
    # Get S3 event details
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    print(f"File uploaded: s3://{bucket}/{key}")
    
    # Validate file (check if it's sales data)
    if 'sales' in key.lower():
        # Trigger Glue job
        response = glue_client.start_job_run(
            JobName='nike-sales-etl-job',
            Arguments={
                '--input_path': f's3://{bucket}/{key}',
                '--output_path': 's3://nike-data-bucket/silver/sales_cleaned/'
            }
        )
        
        print(f"Glue job started: {response['JobRunId']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Glue job started: {response["JobRunId"]}')
        }
    else:
        print(f"Ignoring file: {key}")
        return {
            'statusCode': 200,
            'body': json.dumps('File ignored')
        }
```

**Configure S3 Trigger**:
```python
import boto3

lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')

# Add S3 event notification to trigger Lambda
s3_client.put_bucket_notification_configuration(
    Bucket='nike-data-bucket',
    NotificationConfiguration={
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:process-sales',
                'Events': ['s3:ObjectCreated:*'],
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {
                                'Name': 'prefix',
                                'Value': 'bronze/sales/'
                            }
                        ]
                    }
                }
            }
        ]
    }
)
```

**Lambda Best Practices**:
- ✅ Keep functions small and focused
- ✅ Use environment variables for configuration
- ✅ Set appropriate timeout and memory
- ✅ Use Lambda layers for shared code
- ✅ Handle errors gracefully
- ✅ Use dead-letter queues for failed invocations

---

### 7. Amazon Redshift - Data Warehouse

**What is Redshift?**
Fully managed data warehouse for analytics at petabyte scale.

**Key Features**:
- ✅ Columnar storage (fast analytics)
- ✅ Massively parallel processing (MPP)
- ✅ SQL interface
- ✅ Scales from GB to PB

**Redshift Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Leader Node                                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Query Coordinator                                 │ │
│  │  - Receives queries                                │ │
│  │  - Distributes to compute nodes                   │ │
│  │  - Aggregates results                              │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Compute Node 1│  │Compute Node 2│  │Compute Node 3│
│ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │
│ │Data     │ │  │ │Data     │ │  │ │Data     │ │
│ │Storage  │ │  │ │Storage  │ │  │ │Storage  │ │
│ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ↓
        ┌──────────────────────────────┐
        │      Amazon S3                │
        │  (Data Lake)                  │
        └──────────────────────────────┘
```

#### 7.1 Create Redshift Cluster

**Create Cluster** (boto3):
```python
import boto3

redshift_client = boto3.client('redshift', region_name='us-east-1')

response = redshift_client.create_cluster(
    ClusterIdentifier='nike-sales-warehouse',
    NodeType='dc2.large',  # Node type
    NumberOfNodes=2,  # Number of compute nodes
    MasterUsername='admin',
    MasterUserPassword='SecurePassword123!',
    DBName='nike_sales',
    VpcSecurityGroupIds=['sg-12345678'],
    ClusterSubnetGroupName='default',
    PubliclyAccessible=False
)

print(f"Cluster created: {response['Cluster']['ClusterIdentifier']}")
```

#### 7.2 Load Data into Redshift

**COPY Command** (Load from S3):
```sql
-- Create table
CREATE TABLE sales (
    sale_id VARCHAR(50),
    customer_id BIGINT,
    product_id BIGINT,
    amount DECIMAL(10,2),
    sale_date DATE,
    year INTEGER,
    month INTEGER,
    day INTEGER
)
DISTKEY (customer_id)  -- Distribute by customer_id
SORTKEY (sale_date);   -- Sort by sale_date

-- Load data from S3
COPY sales
FROM 's3://nike-data-bucket/silver/sales_cleaned/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftS3Role'
FORMAT PARQUET
PARTITION BY (year, month, day);
```

**Query Redshift**:
```sql
-- Daily sales summary
SELECT 
    sale_date,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction
FROM sales
WHERE year = 2024 AND month = 1
GROUP BY sale_date
ORDER BY sale_date;
```

**Redshift Best Practices**:
- ✅ Use DISTKEY for even data distribution
- ✅ Use SORTKEY for query performance
- ✅ Use appropriate node types (dc2 for compute, ra3 for storage)
- ✅ Use COPY command (faster than INSERT)
- ✅ Use columnar compression
- ✅ Vacuum and analyze regularly

---

### 8. Amazon Athena - Query S3 Data

**What is Athena?**
Serverless interactive query service to analyze data in S3 using SQL.

**Key Features**:
- ✅ Pay per query (no infrastructure)
- ✅ Query S3 directly
- ✅ Standard SQL
- ✅ Works with Glue Data Catalog

**Athena Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              User Query (SQL)                            │
│  SELECT * FROM sales WHERE year = 2024                 │
└──────────────────────────┬──────────────────────────────┘
                           ↓
        ┌──────────────────────────────┐
        │   Amazon Athena               │
        │  ┌────────────────────────┐  │
        │  │  Query Engine           │  │
        │  │  - Parse SQL            │  │
        │  │  - Plan execution       │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Glue Data Catalog           │
        │  (Table Metadata)             │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Amazon S3                │
        │  (Read Data)                  │
        └──────────────────────────────┘
```

#### 8.1 Query S3 with Athena

**Create Table in Athena**:
```sql
-- Create table pointing to S3
CREATE EXTERNAL TABLE sales (
    sale_id string,
    customer_id bigint,
    product_id bigint,
    amount double,
    sale_date string
)
PARTITIONED BY (
    year string,
    month string,
    day string
)
STORED AS PARQUET
LOCATION 's3://nike-data-bucket/silver/sales_cleaned/';

-- Add partitions
MSCK REPAIR TABLE sales;
```

**Query Data**:
```sql
-- Query sales data
SELECT 
    year,
    month,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue
FROM sales
WHERE year = '2024' AND month = '01'
GROUP BY year, month;
```

**Athena vs Redshift**:

| Aspect | Athena | Redshift |
|-------|--------|----------|
| **Infrastructure** | Serverless | Managed cluster |
| **Cost** | Pay per query | Pay for cluster |
| **Performance** | Good for ad-hoc | Excellent for analytics |
| **Use Case** | Ad-hoc queries | Data warehouse |
| **Setup** | None | Cluster setup |

**Best Practices**:
- ✅ Use Parquet format (columnar, compressed)
- ✅ Partition data properly
- ✅ Use columnar formats
- ✅ Optimize query patterns
- ✅ Use appropriate file sizes (128MB-1GB)

---

### 9. Amazon DynamoDB - NoSQL Database

**What is DynamoDB?**
Fully managed NoSQL database service providing fast, predictable performance with seamless scalability.

**Key Features**:
- ✅ Serverless (no infrastructure management)
- ✅ Single-digit millisecond latency
- ✅ Auto-scaling
- ✅ Built-in security, backup, and restore
- ✅ Key-value and document database

**DynamoDB Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Application Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Web     │  │  Mobile  │  │  API     │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Amazon DynamoDB             │
        │  ┌────────────────────────┐  │
        │  │  Tables                 │  │
        │  │  - Partition Key        │  │
        │  │  - Sort Key (optional)  │  │
        │  │  - Attributes           │  │
        │  └───────────┬────────────┘  │
        │              ↓                │
        │  ┌────────────────────────┐  │
        │  │  Global Secondary      │  │
        │  │  Indexes (GSI)         │  │
        │  └───────────┬────────────┘  │
        │              ↓                │
        │  ┌────────────────────────┐  │
        │  │  Local Secondary       │  │
        │  │  Indexes (LSI)         │  │
        │  └────────────────────────┘  │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Auto-Scaling                │
        │   (Handles Traffic Spikes)    │
        └──────────────────────────────┘
```

#### 9.1 DynamoDB Core Concepts

**Key Concepts**:
- **Table**: Collection of items
- **Item**: Single record (like a row)
- **Attribute**: Field in an item (like a column)
- **Partition Key**: Primary key (required)
- **Sort Key**: Secondary key (optional, for composite primary key)
- **GSI**: Global Secondary Index (different partition key)
- **LSI**: Local Secondary Index (same partition key, different sort key)

**Nike Store Example - Sales Table**:

**Table Structure**:
```
Table: nike_sales
Partition Key: customer_id
Sort Key: sale_date
```

**Sample Items**:
```json
{
  "customer_id": 101,
  "sale_date": "2024-01-15",
  "sale_id": "SALE-001",
  "product_id": 501,
  "amount": 150.00,
  "quantity": 2,
  "store_id": 1
}

{
  "customer_id": 101,
  "sale_date": "2024-01-16",
  "sale_id": "SALE-002",
  "product_id": 502,
  "amount": 200.00,
  "quantity": 1,
  "store_id": 1
}
```

#### 9.2 Create DynamoDB Table

**Create Table** (boto3):
```python
import boto3

dynamodb = boto3.client('dynamodb', region_name='us-east-1')

# Create table
response = dynamodb.create_table(
    TableName='nike_sales',
    KeySchema=[
        {
            'AttributeName': 'customer_id',
            'KeyType': 'HASH'  # Partition key
        },
        {
            'AttributeName': 'sale_date',
            'KeyType': 'RANGE'  # Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'customer_id',
            'AttributeType': 'N'  # Number
        },
        {
            'AttributeName': 'sale_date',
            'AttributeType': 'S'  # String
        }
    ],
    BillingMode='PAY_PER_REQUEST',  # On-demand pricing
    # Or use Provisioned:
    # ProvisionedThroughput={
    #     'ReadCapacityUnits': 5,
    #     'WriteCapacityUnits': 5
    # }
)

print(f"Table created: {response['TableDescription']['TableName']}")
```

**Create Table with GSI**:
```python
response = dynamodb.create_table(
    TableName='nike_sales',
    KeySchema=[
        {'AttributeName': 'customer_id', 'KeyType': 'HASH'},
        {'AttributeName': 'sale_date', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'customer_id', 'AttributeType': 'N'},
        {'AttributeName': 'sale_date', 'AttributeType': 'S'},
        {'AttributeName': 'product_id', 'AttributeType': 'N'}  # For GSI
    ],
    BillingMode='PAY_PER_REQUEST',
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'product-sales-index',
            'KeySchema': [
                {'AttributeName': 'product_id', 'KeyType': 'HASH'},
                {'AttributeName': 'sale_date', 'KeyType': 'RANGE'}
            ],
            'Projection': {
                'ProjectionType': 'ALL'  # Include all attributes
            }
        }
    ]
)
```

#### 9.3 DynamoDB Operations

**Put Item** (Insert/Update):
```python
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('nike_sales')

# Put item
table.put_item(
    Item={
        'customer_id': 101,
        'sale_date': '2024-01-15',
        'sale_id': 'SALE-001',
        'product_id': 501,
        'amount': Decimal('150.00'),
        'quantity': 2,
        'store_id': 1
    }
)
```

**Get Item** (Read):
```python
# Get item by primary key
response = table.get_item(
    Key={
        'customer_id': 101,
        'sale_date': '2024-01-15'
    }
)

item = response.get('Item')
print(item)
```

**Query** (Read multiple items with same partition key):
```python
# Query all sales for customer 101
response = table.query(
    KeyConditionExpression='customer_id = :cid',
    ExpressionAttributeValues={
        ':cid': 101
    }
)

items = response['Items']
for item in items:
    print(item)
```

**Query with Sort Key**:
```python
# Query sales for customer 101 in January 2024
response = table.query(
    KeyConditionExpression='customer_id = :cid AND sale_date BETWEEN :start AND :end',
    ExpressionAttributeValues={
        ':cid': 101,
        ':start': '2024-01-01',
        ':end': '2024-01-31'
    }
)
```

**Scan** (Read all items - use sparingly):
```python
# Scan entire table (expensive!)
response = table.scan()

items = response['Items']
for item in items:
    print(item)
```

**Update Item**:
```python
# Update item
table.update_item(
    Key={
        'customer_id': 101,
        'sale_date': '2024-01-15'
    },
    UpdateExpression='SET amount = :new_amount',
    ExpressionAttributeValues={
        ':new_amount': Decimal('175.00')
    }
)
```

**Delete Item**:
```python
# Delete item
table.delete_item(
    Key={
        'customer_id': 101,
        'sale_date': '2024-01-15'
    }
)
```

#### 9.4 Global Secondary Index (GSI)

**What is GSI?**
Index with different partition key and optional sort key. Enables queries on different attributes.

**Use Case**: Query sales by product_id (not customer_id)

**Create GSI**:
```python
# Already created in table definition above
# Query using GSI
response = table.query(
    IndexName='product-sales-index',
    KeyConditionExpression='product_id = :pid',
    ExpressionAttributeValues={
        ':pid': 501
    }
)
```

**GSI vs LSI**:

| Aspect | GSI | LSI |
|--------|-----|-----|
| **Partition Key** | Can be different | Must be same |
| **Sort Key** | Can be different | Can be different |
| **Consistency** | Eventually consistent | Strongly consistent |
| **Use Case** | Different access patterns | Same partition, different sort |

#### 9.5 DynamoDB Streams

**What are DynamoDB Streams?**
Time-ordered sequence of item-level changes (INSERT, UPDATE, DELETE) in a table.

**Use Cases**:
- Real-time processing
- Replication
- Analytics
- Trigger Lambda functions

**Enable Streams**:
```python
# Enable streams when creating table
response = dynamodb.create_table(
    TableName='nike_sales',
    # ... other parameters ...
    StreamSpecification={
        'StreamEnabled': True,
        'StreamViewType': 'NEW_AND_OLD_IMAGES'  # Include old and new values
    }
)
```

**Process Stream with Lambda**:
```python
import json
import boto3

def lambda_handler(event, context):
    """
    Process DynamoDB stream events
    """
    for record in event['Records']:
        # Check event type
        if record['eventName'] == 'INSERT':
            new_item = record['dynamodb']['NewImage']
            print(f"New sale: {new_item}")
            # Process new sale
        
        elif record['eventName'] == 'MODIFY':
            old_item = record['dynamodb']['OldImage']
            new_item = record['dynamodb']['NewImage']
            print(f"Updated sale: {old_item} -> {new_item}")
            # Process update
        
        elif record['eventName'] == 'REMOVE':
            old_item = record['dynamodb']['OldImage']
            print(f"Deleted sale: {old_item}")
            # Process deletion
    
    return {'statusCode': 200}
```

#### 9.6 DynamoDB Best Practices

**1. Design for Access Patterns**:
```python
# Design table based on how you'll query it
# Example: Query sales by customer
# Partition Key: customer_id
# Sort Key: sale_date
```

**2. Use GSI for Different Access Patterns**:
```python
# If you need to query by product_id, create GSI
# Don't scan the table!
```

**3. Avoid Scans**:
```python
# Bad: Scan entire table (expensive!)
table.scan()

# Good: Query with partition key
table.query(KeyConditionExpression='customer_id = :cid', ...)
```

**4. Use Batch Operations**:
```python
# Batch write (up to 25 items)
with table.batch_writer() as batch:
    for sale in sales:
        batch.put_item(Item=sale)
```

**5. Use On-Demand Billing for Variable Workloads**:
```python
# On-demand: Pay per request
BillingMode='PAY_PER_REQUEST'

# Provisioned: Fixed capacity (cheaper for steady workloads)
ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
```

**6. Use Appropriate Data Types**:
```python
# Use Decimal for money (not float)
amount = Decimal('150.00')

# Use strings for dates (ISO format)
sale_date = '2024-01-15'
```

#### 9.7 DynamoDB vs RDS

**When to Use DynamoDB**:
- ✅ NoSQL data model
- ✅ Single-digit millisecond latency
- ✅ Auto-scaling
- ✅ Serverless
- ✅ Key-value or document data

**When to Use RDS**:
- ✅ Relational data
- ✅ Complex queries (JOINs)
- ✅ ACID transactions across tables
- ✅ SQL interface

**Comparison**:

| Aspect | DynamoDB | RDS |
|--------|----------|-----|
| **Data Model** | NoSQL | Relational |
| **Latency** | Single-digit ms | 10-100ms |
| **Scaling** | Automatic | Manual |
| **Queries** | Key-based | SQL (complex) |
| **Transactions** | Single table | Multi-table |

#### 9.8 DynamoDB Integration with Other Services

**DynamoDB → S3 (Export)**:
```python
# Export DynamoDB table to S3
# Use AWS Data Pipeline or AWS DMS
```

**DynamoDB → Redshift (ETL)**:
```python
# Use AWS Glue to read from DynamoDB and write to Redshift
datasource = glueContext.create_dynamic_frame.from_options(
    connection_type="dynamodb",
    connection_options={
        "dynamodb.input.tableName": "nike_sales",
        "dynamodb.throughput.read.percent": "0.5"
    }
)

# Write to Redshift
glueContext.write_dynamic_frame.from_jdbc_conf(
    frame=datasource,
    catalog_connection="redshift-connection",
    connection_options={
        "dbtable": "sales",
        "database": "nike_sales"
    }
)
```

**DynamoDB → Kinesis (Streams)**:
```python
# DynamoDB Streams → Kinesis → S3
# Process changes in real-time
```

---

### 10. Amazon Kinesis - Real-Time Streaming

**What is Kinesis?**
Platform for streaming data in real-time.

**Kinesis Services**:
- **Kinesis Data Streams**: Real-time streaming
- **Kinesis Data Firehose**: Load streaming data to destinations
- **Kinesis Data Analytics**: Analyze streaming data with SQL

**Kinesis Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Data Producers                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Apps    │  │  IoT     │  │  Logs    │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Kinesis Data Streams        │
        │  ┌────────────────────────┐ │
        │  │  Shards (Partitions)    │ │
        │  │  - Shard 1              │ │
        │  │  - Shard 2              │ │
        │  │  - Shard 3              │ │
        │  └───────────┬────────────┘ │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Kinesis Data Firehose       │
        │  (Load to Destinations)        │
        │  ┌──────────┐  ┌──────────┐ │
        │  │   S3     │  │ Redshift │ │
        │  │  Lambda  │  │  ES      │ │
        │  └──────────┘  └──────────┘ │
        └──────────────────────────────┘
```

#### 9.1 Kinesis Data Streams

**Create Stream**:
```python
import boto3

kinesis_client = boto3.client('kinesis', region_name='us-east-1')

# Create stream
response = kinesis_client.create_stream(
    StreamName='nike-sales-stream',
    ShardCount=3  # Number of shards (partitions)
)

print(f"Stream created: {response}")
```

**Put Records** (Producer):
```python
import json
import boto3

kinesis_client = boto3.client('kinesis')

# Put record to stream
def put_sale_record(sale_data):
    response = kinesis_client.put_record(
        StreamName='nike-sales-stream',
        Data=json.dumps(sale_data),
        PartitionKey=str(sale_data['customer_id'])  # Partition by customer
    )
    return response

# Example: Send sale event
sale_event = {
    "sale_id": "SALE-001",
    "customer_id": 101,
    "amount": 150.00,
    "sale_date": "2024-01-15T10:30:00Z"
}

put_sale_record(sale_event)
```

**Read Records** (Consumer):
```python
import boto3
import json

kinesis_client = boto3.client('kinesis')

# Get shard iterator
response = kinesis_client.get_shard_iterator(
    StreamName='nike-sales-stream',
    ShardId='shardId-000000000000',
    ShardIteratorType='LATEST'  # or 'TRIM_HORIZON' for beginning
)

shard_iterator = response['ShardIterator']

# Read records
while True:
    response = kinesis_client.get_records(
        ShardIterator=shard_iterator,
        Limit=100
    )
    
    for record in response['Records']:
        data = json.loads(record['Data'])
        print(f"Received: {data}")
        # Process record
    
    shard_iterator = response['NextShardIterator']
```

#### 9.2 Kinesis Data Firehose

**Create Firehose Delivery Stream**:
```python
firehose_client = boto3.client('firehose', region_name='us-east-1')

response = firehose_client.create_delivery_stream(
    DeliveryStreamName='nike-sales-firehose',
    DeliveryStreamType='DirectPut',
    S3DestinationConfiguration={
        'RoleARN': 'arn:aws:iam::123456789012:role/FirehoseS3Role',
        'BucketARN': 'arn:aws:s3:::nike-data-bucket',
        'Prefix': 'bronze/sales/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/',
        'BufferingHints': {
            'SizeInMBs': 128,
            'IntervalInSeconds': 60
        },
        'CompressionFormat': 'GZIP',
        'DataFormatConversionConfiguration': {
            'Enabled': True,
            'OutputFormatConfiguration': {
                'Serializer': {
                    'ParquetSerDe': {}
                }
            },
            'SchemaConfiguration': {
                'RoleARN': 'arn:aws:iam::123456789012:role/FirehoseGlueRole',
                'DatabaseName': 'nike_sales_db',
                'TableName': 'raw_sales'
            }
        }
    }
)
```

**Put Records to Firehose**:
```python
def put_to_firehose(record):
    response = firehose_client.put_record(
        DeliveryStreamName='nike-sales-firehose',
        Record={
            'Data': json.dumps(record)
        }
    )
    return response

# Send record
sale_event = {
    "sale_id": "SALE-001",
    "customer_id": 101,
    "amount": 150.00
}

put_to_firehose(sale_event)
# Firehose automatically:
# - Buffers records
# - Converts to Parquet
# - Writes to S3
# - Partitions by date ✅
```

**Best Practices**:
- ✅ Right-size shards (1 shard = 1MB/s write, 2MB/s read)
- ✅ Use partition keys for even distribution
- ✅ Use Firehose for simple ETL to S3
- ✅ Use Data Streams for custom processing
- ✅ Enable compression (GZIP, Snappy)
- ✅ Use Parquet format for analytics

---

### 10. AWS Step Functions - Workflow Orchestration

**What are Step Functions?**
Serverless orchestration service to coordinate multiple AWS services into workflows.

**Key Features**:
- ✅ Visual workflow builder
- ✅ Error handling
- ✅ Retry logic
- ✅ Parallel execution

**Step Functions Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              State Machine (Workflow)                    │
│                                                          │
│  Start                                                   │
│    ↓                                                     │
│  ┌────────────────────┐                                 │
│  │  Glue Job          │  (Process Data)                │
│  └─────────┬──────────┘                                 │
│            ↓                                             │
│  ┌────────────────────┐                                 │
│  │  Choice            │  (Check Status)                │
│  └─────────┬──────────┘                                 │
│            ├── Success → Continue                        │
│            └── Failure → Retry                          │
│            ↓                                             │
│  ┌────────────────────┐                                 │
│  │  Parallel          │  (Run Multiple)                │
│  │  ├─ Lambda 1       │                                 │
│  │  ├─ Lambda 2       │                                 │
│  │  └─ Lambda 3       │                                 │
│  └─────────┬──────────┘                                 │
│            ↓                                             │
│  ┌────────────────────┐                                 │
│  │  SNS Notification  │  (Send Alert)                  │
│  └─────────┬──────────┘                                 │
│            ↓                                             │
│  End                                                      │
└─────────────────────────────────────────────────────────┘
```

#### 10.1 Create Step Function

**State Machine Definition** (JSON):
```json
{
  "Comment": "Nike Sales ETL Pipeline",
  "StartAt": "ProcessSalesData",
  "States": {
    "ProcessSalesData": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "nike-sales-etl-job"
      },
      "Next": "CheckStatus"
    },
    "CheckStatus": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.JobRun.State",
          "StringEquals": "SUCCEEDED",
          "Next": "LoadToRedshift"
        },
        {
          "Variable": "$.JobRun.State",
          "StringEquals": "FAILED",
          "Next": "SendFailureAlert"
        }
      ],
      "Default": "WaitAndRetry"
    },
    "LoadToRedshift": {
      "Type": "Task",
      "Resource": "arn:aws:states:::aws-sdk:redshiftdata:executeStatement",
      "Parameters": {
        "ClusterIdentifier": "nike-sales-warehouse",
        "Database": "nike_sales",
        "Sql": "COPY sales FROM 's3://nike-data-bucket/silver/sales_cleaned/' IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftS3Role' FORMAT PARQUET;"
      },
      "Next": "SendSuccessNotification"
    },
    "SendSuccessNotification": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:nike-etl-alerts",
        "Message": "Sales ETL pipeline completed successfully"
      },
      "End": true
    },
    "SendFailureAlert": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:nike-etl-alerts",
        "Message": "Sales ETL pipeline failed!"
      },
      "End": true
    },
    "WaitAndRetry": {
      "Type": "Wait",
      "Seconds": 60,
      "Next": "ProcessSalesData"
    }
  }
}
```

**Create State Machine** (boto3):
```python
import boto3
import json

sfn_client = boto3.client('stepfunctions', region_name='us-east-1')

# Read state machine definition
with open('sales_etl_state_machine.json', 'r') as f:
    definition = json.dumps(json.load(f))

# Create state machine
response = sfn_client.create_state_machine(
    name='nike-sales-etl-workflow',
    definition=definition,
    roleArn='arn:aws:iam::123456789012:role/StepFunctionsExecutionRole'
)

state_machine_arn = response['stateMachineArn']
print(f"State machine created: {state_machine_arn}")

# Start execution
execution = sfn_client.start_execution(
    stateMachineArn=state_machine_arn,
    input=json.dumps({})
)

print(f"Execution started: {execution['executionArn']}")
```

**Best Practices**:
- ✅ Use for complex workflows
- ✅ Handle errors gracefully
- ✅ Use retry logic for transient failures
- ✅ Send notifications on completion/failure
- ✅ Use parallel execution when possible

---

### 11. AWS Data Pipeline - ETL Orchestration

**What is Data Pipeline?**
Orchestration service for data-driven workflows (legacy, consider Step Functions instead).

**Note**: AWS recommends Step Functions for new workflows, but Data Pipeline is still used.

---

### 12. IAM - Identity & Access Management

**What is IAM?**
Service for managing access to AWS resources.

**Key Concepts**:
- **Users**: People or applications
- **Groups**: Collection of users
- **Roles**: Permissions for services/resources
- **Policies**: Permissions documents

**IAM Policy Example**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::nike-data-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::nike-data-bucket"
    }
  ]
}
```

**Create IAM Role for Glue**:
```python
import boto3

iam_client = boto3.client('iam')

# Create role
role_response = iam_client.create_role(
    RoleName='GlueServiceRole',
    AssumeRolePolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "glue.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
)

# Attach policy
iam_client.attach_role_policy(
    RoleName='GlueServiceRole',
    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole'
)

# Add S3 access
iam_client.put_role_policy(
    RoleName='GlueServiceRole',
    PolicyName='S3Access',
    PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::nike-data-bucket/*"
            }
        ]
    })
)
```

**Best Practices**:
- ✅ Principle of least privilege
- ✅ Use roles (not users) for services
- ✅ Use IAM policies for fine-grained access
- ✅ Rotate access keys regularly
- ✅ Enable MFA for users

---

### 13. VPC & Networking

**What is VPC?**
Virtual Private Cloud (VPC) is your isolated network in AWS. For data engineering, VPC controls how Glue, EMR, Redshift, Lambda, and other services talk to each other and to S3—often without sending traffic over the public internet.

**Key concepts**:
- **VPC**: Isolated network (CIDR, e.g. 10.0.0.0/16)
- **Subnet**: Segment of VPC (e.g. 10.0.1.0/24). **Public** = has internet gateway; **Private** = no direct internet, use NAT for outbound
- **Security Group**: Stateful firewall (allow/deny by port and source)
- **NACL**: Optional subnet-level stateless firewall
- **NAT Gateway**: Gives private subnets outbound internet (e.g. for updates, external APIs)

**Why VPC matters for data engineering**:
- Glue, EMR, and Lambda run inside your VPC (or VPC-attached). Redshift clusters live in a subnet. Keeping them in **private subnets** improves security.
- **VPC endpoints** let services reach S3, Glue, Athena, Redshift, or Kinesis without going over the internet—lower latency, no NAT cost, and traffic stays on the AWS network.

**Typical data-engineering layout**:
```
VPC (10.0.0.0/16)
├── Private subnet A (Glue, EMR, Lambda)
│   └── S3 / Glue / Athena via VPC endpoints (no internet)
├── Private subnet B (Redshift, RDS if used)
│   └── S3 via VPC endpoint for COPY/UNLOAD
└── Public subnet (optional: NAT Gateway, bastion)
```

**VPC endpoints (two types)**:
- **Gateway endpoint**: For S3 and DynamoDB only. Free, no NAT. Attach to route tables; traffic to S3 stays in AWS.
- **Interface endpoint (PrivateLink)**: For Glue, Athena, Kinesis, Redshift Data API, Secrets Manager, etc. Uses ENIs in your subnets; you pay per AZ/hour and data processed. Use when you want private access without NAT/internet.

**Example: S3 gateway endpoint (no internet for S3)**:
```python
# Create gateway endpoint for S3 (boto3)
ec2 = boto3.client('ec2')
ec2.create_vpc_endpoint(
    VpcId='vpc-xxxxx',
    ServiceName='com.amazonaws.us-east-1.s3',
    RouteTableIds=['rtb-xxxxx'],
    VpcEndpointType='Gateway'
)
# Now Glue/EMR/Lambda in private subnet can reach S3 without NAT/internet
```

**Security groups for data services**:
- **Glue**: Allow outbound to S3 (or use endpoint), and to Glue/Athena if using interface endpoints. Restrict inbound to only what’s needed (e.g. no 0.0.0.0/0).
- **EMR**: Allow master/worker communication (e.g. 0–65535 within security group), and outbound to S3 and optional endpoints.
- **Redshift**: Allow inbound 5439 from BI/ETL only (e.g. specific security group or CIDR), outbound to S3 for COPY/UNLOAD.

**VPC best practices for data engineering**:
- ✅ Put Glue, EMR, Lambda, Redshift in **private subnets** where possible.
- ✅ Use **S3 gateway endpoint** (and DynamoDB if needed) to avoid NAT and internet for S3.
- ✅ Use **interface endpoints** for Glue, Athena, Kinesis, Secrets Manager if you need private access.
- ✅ Enable **VPC Flow Logs** for troubleshooting and compliance.
- ✅ Use **security groups** with least privilege (no 0.0.0.0/0 unless required).

---

#### 13.1 CloudFront (CDN) for Data & APIs

**What is CloudFront?**
Amazon CloudFront is a CDN (content delivery network): it caches content at edge locations and can terminate HTTPS. For data engineering it’s useful for **APIs and dashboards**, not for moving bulk data.

**Data-engineering use cases**:
- **API in front of data**: Lambda (or API Gateway + Lambda) that returns aggregated or cached query results; CloudFront caches responses by URL/query string to reduce load and latency for repeated queries.
- **Dashboards and static assets**: Serve BI dashboards (e.g. QuickSight embedded, or static exports), login pages, or small assets from S3 or Lambda@Edge with low latency worldwide.
- **Secure delivery**: Restrict access with signed URLs or signed cookies; use OAC (Origin Access Control) so only CloudFront can read from S3 (no direct S3 public access).

**What CloudFront is not for**:
- ❌ Bulk data transfer (use S3 transfer acceleration or direct S3 if needed).
- ❌ Replacing S3/Glue/Redshift for ETL or analytics storage.

**Example: Cache API responses from Lambda**:
- Origin: API Gateway + Lambda that queries Athena/Redshift or reads from S3.
- CloudFront distribution with that API as origin; set TTL (e.g. 60–300 seconds) for cacheable GET responses. Repeated requests for the same URL get a cached response at the edge.

**Other AWS services useful in data engineering**:
- **EventBridge**: Event bus for event-driven pipelines (e.g. “file landed in S3”, “Glue job finished”). Triggers Lambda, Step Functions, or other targets. Use instead of or in addition to S3 event notifications when you need routing, filtering, or multiple consumers.
- **Secrets Manager**: Store DB credentials, API keys; Glue/EMR/Lambda/Redshift can retrieve secrets at runtime. Prefer over hardcoding or plain environment variables.
- **QuickSight**: BI and dashboards on top of S3, Athena, Redshift. Embed dashboards in apps; use SPICE for fast in-memory analytics.

---

### 14. Connecting Services Together

**Complete ETL Pipeline**:
```
1. Data arrives → S3 (Bronze)
   ↓
2. S3 event → Lambda
   ↓
3. Lambda → Triggers Glue Job
   ↓
4. Glue Job → Processes data → S3 (Silver)
   ↓
5. Step Functions → Orchestrates workflow
   ↓
6. Redshift → Loads from S3
   ↓
7. Athena → Queries S3
```

**Example Integration**:
```python
# Complete pipeline
# 1. S3 upload triggers Lambda
# 2. Lambda starts Glue job
# 3. Glue processes and writes to S3
# 4. Step Functions monitors and loads to Redshift

def lambda_handler(event, context):
    # Trigger Glue job
    glue_client.start_job_run(
        JobName='nike-sales-etl-job',
        Arguments={
            '--input_path': event['Records'][0]['s3']['object']['key'],
            '--output_path': 's3://nike-data-bucket/silver/sales_cleaned/'
        }
    )
    
    # Start Step Functions execution
    sfn_client.start_execution(
        stateMachineArn='arn:aws:states:::stateMachine:nike-sales-etl-workflow',
        input=json.dumps({'s3_path': event['Records'][0]['s3']['object']['key']})
    )
```

---

### 14.5 Multi-Cloud Integration: AWS + Databricks

Many organizations use **AWS for storage and ingestion** and **Databricks for processing and analytics** in the same data lake. Databricks on AWS runs in your VPC and reads/writes S3 natively, so you get a single lake (S3) with multiple engines.

**Why AWS + Databricks together**:
- **S3 as single source of truth**: Ingest with Kinesis, Glue, or Lambda; store raw and curated data in S3. Databricks reads the same S3 paths for Spark/Delta.
- **Best of both**: Use AWS for serverless ETL (Glue), streaming (Kinesis), and warehouse (Redshift/Athena); use Databricks for advanced Spark, ML, and Delta Lake without re-ingesting.
- **Optional shared catalog**: Databricks can use **AWS Glue Data Catalog** as the metastore, so tables created by Glue or Athena are visible in Databricks and vice versa (with configuration).

**Architecture: Data lake on S3, processed by both Glue and Databricks**:
```
                    ┌─────────────────────────────────────────────────────────┐
                    │  Ingestion (AWS)                                        │
                    │  Kinesis / S3 events / Lambda / Glue Crawler            │
                    └───────────────────────────┬─────────────────────────────┘
                                              ↓
                    ┌─────────────────────────────────────────────────────────┐
                    │  S3 Data Lake (single source of truth)                   │
                    │  s3://bucket/bronze/  s3://bucket/silver/  s3://.../gold/│
                    └───────────┬─────────────────────────────┬─────────────────┘
                                │                             │
              ┌─────────────────┘                             └─────────────────┐
              ↓                                                                   ↓
   ┌──────────────────────┐                                        ┌──────────────────────┐
   │  AWS (Glue / Athena  │                                        │  Databricks on AWS   │
   │  Redshift)           │                                        │  (Spark, Delta, ML)  │
   │  - Glue ETL → S3     │                                        │  - Read/write S3     │
   │  - Athena query S3   │                                        │  - Delta on S3       │
   │  - Redshift COPY S3  │                                        │  - Optional: Glue   │
   └──────────────────────┘                                        │    Data Catalog     │
                                                                     └──────────────────────┘
```

**Real-world scenario 1: Hybrid ETL — Glue for simple, Databricks for heavy**
- **Setup**: Raw data lands in S3 (e.g. from Kinesis Firehose or batch uploads). Glue Crawler catalogs it; Glue jobs do light cleansing and write to `s3://bucket/silver/` in Parquet.
- **Databricks**: Reads from `s3://bucket/silver/`, runs Spark jobs (joins, ML, Delta), writes Delta tables under `s3://bucket/gold/`. Same S3 bucket; no copy of raw data.
- **Use case**: Standard ETL in Glue (low ops), complex pipelines and ML in Databricks.

**Real-world scenario 2: Redshift + Databricks on the same S3 lake**
- **Setup**: S3 holds bronze/silver/gold (Parquet/Delta). Redshift Spectrum or external tables point to S3 for ad-hoc SQL. Redshift also loads key tables via COPY from S3 for fast dashboards.
- **Databricks**: Runs batch and streaming jobs, writes aggregated/ML outputs to S3 (Delta). Analysts use Athena or Redshift to query; data scientists use Databricks on the same paths.
- **Use case**: Operational reporting in Redshift/Athena; advanced analytics and ML in Databricks; one lake, multiple query engines.

**Config: Databricks reading S3 (with IAM)**:
```python
# In Databricks (AWS): use instance profile or IAM role for S3
# Spark config (or cluster config)
spark.conf.set("spark.databricks.delta.preview.enabled", "true")

# Read from S3 (same bucket Glue writes to)
df = spark.read.format("parquet").load("s3://my-data-bucket/silver/sales/")

# Write Delta on S3
df.write.format("delta").mode("overwrite").save("s3://my-data-bucket/gold/sales_daily/")
```

**Using Glue Data Catalog from Databricks** (optional):
- In Databricks workspace settings, set the metastore to use **AWS Glue**. Then tables created in Glue or Athena (e.g. from Glue Crawler) appear in Databricks; tables created in Databricks can be exposed to Athena/Glue. Keeps one catalog across AWS and Databricks.

**Summary**:
- ✅ S3 as shared lake; AWS services and Databricks read/write the same paths.
- ✅ Use Glue for catalog and simple ETL; Databricks for Spark, Delta, ML.
- ✅ Redshift/Athena for SQL; Databricks for advanced analytics—all on top of S3.
- ✅ Optionally unify metadata with Glue Data Catalog as the metastore for Databricks.

---

### 14.6 Real-World Data Engineering Scenarios

**Scenario A: Retail — batch and streaming with a single lake**
- **Goal**: Ingest store and online sales (batch files + Kafka), clean and aggregate, serve to BI and ML.
- **Flow**: (1) Batch files land in S3 (bronze); Kafka → Kinesis Data Streams → Lambda or Firehose → S3 (bronze). (2) Glue jobs run on a schedule: bronze → silver (cleaned, partitioned by date). (3) Aggregations and ML features in Databricks or Glue → gold on S3. (4) Redshift Spectrum or Athena query gold; Redshift also COPYs key tables for dashboards. (5) Step Functions or EventBridge orchestrate Glue and notify on failure.
- **Takeaway**: One S3 lake; Kinesis + Glue for ingestion and ETL; add Databricks or Redshift as needed for analytics.

**Scenario B: Healthcare — governed lake with multiple consumers**
- **Goal**: Ingest HL7/EDI and application events; store in a governed lake; support analytics and reporting without duplicating PHI.
- **Flow**: (1) Events land in S3 with encryption (SSE-KMS) and bucket policies restricting access by IAM. (2) Glue Crawler catalogs data; Glue jobs apply masking or de-identification and write to silver/gold. (3) Lake Formation (or IAM + Glue) controls who can see which tables. (4) Athena and Redshift Spectrum query only allowed tables; Databricks uses the same S3 paths with the same IAM/Lake Formation policies. (5) Audit via CloudTrail and VPC Flow Logs.
- **Takeaway**: Encryption, access control, and a single catalog (Glue) with multiple engines (Glue, Athena, Redshift, Databricks) on one lake.

**Scenario C: Media — real-time events and batch backfill**
- **Goal**: Stream click/play events in real time; backfill historical data; serve both to analytics and ML.
- **Flow**: (1) Kinesis Data Streams (or Firehose) for real-time events → S3 (partitioned by hour). (2) Lambda or Glue for light normalization → silver. (3) Batch backfill: historical files in S3; Glue or EMR for large backfills into the same silver/gold layout. (4) Athena for ad-hoc SQL; Databricks for sessionization and ML. (5) CloudFront in front of an API that serves pre-aggregated metrics (cached) for dashboards.
- **Takeaway**: Kinesis + S3 for streaming and batch; same schema and partitions; use CloudFront only for API/dashboard caching, not bulk data.

---

### 15. Cost Optimization

**S3 Cost Optimization**:
- ✅ Use appropriate storage classes
- ✅ Enable lifecycle policies (move to Glacier)
- ✅ Delete old data
- ✅ Compress data (Parquet, GZIP)

**Glue Cost Optimization**:
- ✅ Right-size workers
- ✅ Use job bookmarks (incremental processing)
- ✅ Terminate jobs when done

**EMR Cost Optimization**:
- ✅ Use spot instances (up to 90% savings)
- ✅ Right-size cluster
- ✅ Terminate when idle
- ✅ Use S3 (not HDFS)

**Redshift Cost Optimization**:
- ✅ Use appropriate node types
- ✅ Pause cluster when not in use
- ✅ Use compression
- ✅ Right-size cluster

---

### 16. Performance Tuning

**S3 Performance**:
- ✅ Use multipart upload for large files
- ✅ Use appropriate file sizes (128MB-1GB)
- ✅ Use Parquet format

**Glue Performance**:
- ✅ Right-size workers
- ✅ Use appropriate file formats
- ✅ Partition data

**Redshift Performance**:
- ✅ Use DISTKEY and SORTKEY
- ✅ Use COPY command
- ✅ Vacuum and analyze

---

### 17. AWS Interview Questions & Answers

#### Q1: Explain S3 Storage Classes

**Question**: "When would you use different S3 storage classes? Walk me through your decision."

**Answer Structure**:

**1. S3 Storage Classes**:

| Class | Use Case | Cost | Access Time |
|-------|----------|------|-------------|
| **Standard** | Frequently accessed | Highest | Instant |
| **Standard-IA** | Infrequently accessed | Medium | Instant |
| **Glacier** | Archive | Low | 3-5 hours |
| **Glacier Deep Archive** | Long-term archive | Lowest | 12 hours |

**2. Decision Framework**:

**Use Standard When**:
- ✅ Data accessed frequently (> once per month)
- ✅ Need instant access
- ✅ Active data processing

**Use Standard-IA When**:
- ✅ Data accessed infrequently (< once per month)
- ✅ Need instant access
- ✅ Can tolerate retrieval costs

**Use Glacier When**:
- ✅ Archive data (rarely accessed)
- ✅ Can wait 3-5 hours for retrieval
- ✅ Compliance/regulatory requirements

**3. Real-World Example**:

**Scenario**: Sales data pipeline

```python
# Bronze layer: Raw data (Standard - frequently accessed)
s3_client.upload_file(
    'sales.json',
    'nike-data-bucket',
    'bronze/sales/sales_20240115.json',
    ExtraArgs={'StorageClass': 'STANDARD'}
)

# Silver layer: Processed data (Standard-IA - less frequent)
s3_client.upload_file(
    'sales_cleaned.json',
    'nike-data-bucket',
    'silver/sales_cleaned/sales_20240115.json',
    ExtraArgs={'StorageClass': 'STANDARD_IA'}
)

# Archive: Old data (> 2 years) → Glacier
s3_client.copy_object(
    Bucket='nike-data-bucket',
    CopySource={'Bucket': 'nike-data-bucket', 'Key': 'silver/sales_cleaned/sales_20220115.json'},
    Key='archive/sales/sales_20220115.json',
    StorageClass='GLACIER'
)
```

**4. Lifecycle Policies** (Automatic):

```python
# Automatically move data to cheaper storage
s3_client.put_bucket_lifecycle_configuration(
    Bucket='nike-data-bucket',
    LifecycleConfiguration={
        'Rules': [
            {
                'Id': 'MoveToIA',
                'Status': 'Enabled',
                'Transitions': [
                    {
                        'Days': 30,
                        'StorageClass': 'STANDARD_IA'
                    }
                ],
                'Filter': {'Prefix': 'silver/'}
            },
            {
                'Id': 'MoveToGlacier',
                'Status': 'Enabled',
                'Transitions': [
                    {
                        'Days': 365,
                        'StorageClass': 'GLACIER'
                    }
                ],
                'Filter': {'Prefix': 'archive/'}
            }
        ]
    }
)
```

**Key Points**:
- ✅ Standard: Frequent access, instant
- ✅ Standard-IA: Infrequent access, instant
- ✅ Glacier: Archive, 3-5 hour retrieval
- ✅ Use lifecycle policies for automatic transitions

---

#### Q2: Glue vs EMR - When to Use Each?

**Question**: "When would you choose AWS Glue vs Amazon EMR? What are the trade-offs?"

**Answer Structure**:

**1. AWS Glue - Use When**:

✅ **Use Glue When**:
- Standard ETL patterns
- Want serverless (no infrastructure)
- Need automatic schema discovery
- Prefer managed service
- Cost-effective for occasional jobs

**Example**:
```python
# Glue: Simple ETL
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="nike_sales_db",
    table_name="raw_sales"
)

# Transform
cleaned = Filter.apply(frame=datasource, f=lambda x: x["amount"] > 0)

# Write
glueContext.write_dynamic_frame.from_options(
    frame=cleaned,
    connection_type="s3",
    connection_options={"path": "s3://nike-data-bucket/silver/"}
)
```

**2. Amazon EMR - Use When**:

✅ **Use EMR When**:
- Complex processing logic
- Need full control
- Custom Spark/Hadoop configurations
- Long-running jobs
- Need HDFS or custom tools

**Example**:
```python
# EMR: Full Spark control
spark = SparkSession.builder \
    .appName("Complex Processing") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()

# Complex transformations
df = spark.read.json("s3://nike-data-bucket/bronze/")
# Custom logic...
```

**3. Comparison Table**:

| Aspect | Glue | EMR |
|-------|------|-----|
| **Setup** | None (serverless) | Cluster setup required |
| **Control** | Limited | Full control |
| **Cost** | Pay per job | Pay for cluster time |
| **Use Case** | Standard ETL | Complex processing |
| **Scaling** | Automatic | Manual |
| **Learning Curve** | Low | Medium |

**4. Real-World Decision**:

**Scenario**: Daily sales ETL pipeline

**Glue Approach** (Recommended):
```python
# Simple, managed, cost-effective
# Perfect for standard ETL patterns
```

**EMR Approach** (If needed):
```python
# Only if you need:
# - Custom Spark configurations
# - Complex processing logic
# - HDFS storage
# - Long-running jobs
```

**Key Points**:
- ✅ Glue: Serverless, simple, standard ETL
- ✅ EMR: Full control, complex processing
- ✅ Choose based on requirements

---

#### Q3: Design a Real-Time Streaming Pipeline

**Question**: "Design a real-time streaming pipeline on AWS. Walk me through your architecture."

**Answer Structure**:

**1. Requirements**:
- Real-time sales events
- Process and aggregate
- Store in S3 and Redshift
- Handle 10,000 events/second

**2. Architecture**:

```
Data Producers (Apps)
    ↓
Kinesis Data Streams (3 shards)
    ↓
Kinesis Data Firehose
    ├── S3 (Bronze - Raw)
    └── Lambda (Process)
        ↓
    Kinesis Data Analytics (SQL)
        ↓
    S3 (Silver - Processed)
        ↓
    Redshift (Gold - Analytics)
```

**3. Implementation**:

**Step 1: Create Kinesis Stream**:
```python
kinesis_client.create_stream(
    StreamName='nike-sales-stream',
    ShardCount=3  # 3 shards = 3MB/s write, 6MB/s read
)
```

**Step 2: Producers Send Events**:
```python
kinesis_client.put_record(
    StreamName='nike-sales-stream',
    Data=json.dumps(sale_event),
    PartitionKey=str(sale_event['customer_id'])
)
```

**Step 3: Firehose to S3**:
```python
firehose_client.create_delivery_stream(
    DeliveryStreamName='nike-sales-firehose',
    S3DestinationConfiguration={
        'BucketARN': 'arn:aws:s3:::nike-data-bucket',
        'Prefix': 'bronze/sales/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/',
        'BufferingHints': {
            'SizeInMBs': 128,
            'IntervalInSeconds': 60
        }
    }
)
```

**Step 4: Process with Lambda**:
```python
def lambda_handler(event, context):
    for record in event['Records']:
        data = json.loads(record['kinesis']['data'])
        # Process and aggregate
        process_sale(data)
```

**4. Key Decisions**:
- ✅ Kinesis Streams: Real-time processing
- ✅ Firehose: Simple ETL to S3
- ✅ Lambda: Custom processing
- ✅ Right-size shards (1 shard = 1MB/s)

**Key Points**:
- ✅ Kinesis for real-time streaming
- ✅ Firehose for simple ETL
- ✅ Lambda for custom processing
- ✅ Right-size for throughput

---

#### Q4: How Do You Optimize Redshift Performance?

**Question**: "Your Redshift queries are slow. Walk me through your optimization strategy."

**Answer Structure**:

**1. Redshift Performance Factors**:
- DISTKEY (data distribution)
- SORTKEY (data sorting)
- Compression
- Query patterns
- Cluster size

**2. DISTKEY Strategy**:

**What is DISTKEY?**
Column used to distribute data across nodes.

**Choose DISTKEY When**:
- ✅ Frequently joined column
- ✅ Even distribution
- ✅ Avoid high-cardinality columns

**Example**:
```sql
-- Good: customer_id (even distribution, frequently joined)
CREATE TABLE sales (
    sale_id VARCHAR(50),
    customer_id BIGINT,
    amount DECIMAL(10,2),
    sale_date DATE
)
DISTKEY (customer_id);  -- Distribute by customer_id

-- Bad: sale_id (high cardinality, unique)
-- Would create too many small files
```

**3. SORTKEY Strategy**:

**What is SORTKEY?**
Column used to sort data within each node.

**Choose SORTKEY When**:
- ✅ Frequently filtered column
- ✅ Used in WHERE clauses
- ✅ Date columns (for time-based queries)

**Example**:
```sql
CREATE TABLE sales (
    sale_id VARCHAR(50),
    customer_id BIGINT,
    amount DECIMAL(10,2),
    sale_date DATE
)
DISTKEY (customer_id)
SORTKEY (sale_date);  -- Sort by date for fast date queries

-- Query benefits:
SELECT * FROM sales WHERE sale_date = '2024-01-15';
-- Only scans relevant date range ✅
```

**4. Compression**:

**Enable Compression**:
```sql
-- Redshift automatically compresses, but you can optimize
COPY sales
FROM 's3://nike-data-bucket/sales/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftS3Role'
COMPUPDATE ON  -- Auto-compress
```

**5. Query Optimization**:

**Use COPY Command** (Not INSERT):
```sql
-- Good: COPY (parallel, fast)
COPY sales FROM 's3://nike-data-bucket/sales/' IAM_ROLE '...';

-- Bad: INSERT (slow, single-threaded)
INSERT INTO sales VALUES (...);
```

**Use Appropriate WHERE Clauses**:
```sql
-- Good: Uses SORTKEY
SELECT * FROM sales WHERE sale_date = '2024-01-15';

-- Bad: Full table scan
SELECT * FROM sales WHERE amount > 100;
```

**6. Vacuum and Analyze**:

```sql
-- Vacuum: Reclaim space, resort data
VACUUM sales;

-- Analyze: Update statistics
ANALYZE sales;
```

**Key Points**:
- ✅ DISTKEY: Even distribution, frequently joined
- ✅ SORTKEY: Frequently filtered columns
- ✅ Use COPY (not INSERT)
- ✅ Vacuum and analyze regularly

---

#### Q5: Explain S3 Lifecycle Policies

**Question**: "How do you manage data lifecycle in S3? Explain lifecycle policies."

**Answer Structure**:

**1. What are Lifecycle Policies?**
Automated rules to transition or delete objects based on age or other criteria.

**2. Lifecycle Actions**:

**Transition Actions**:
- Move to Standard-IA (after 30 days)
- Move to Glacier (after 90 days)
- Move to Glacier Deep Archive (after 365 days)

**Expiration Actions**:
- Delete objects after specified days

**3. Example Lifecycle Policy**:

```python
s3_client.put_bucket_lifecycle_configuration(
    Bucket='nike-data-bucket',
    LifecycleConfiguration={
        'Rules': [
            {
                'Id': 'MoveToIA',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'silver/'},
                'Transitions': [
                    {
                        'Days': 30,
                        'StorageClass': 'STANDARD_IA'
                    }
                ]
            },
            {
                'Id': 'MoveToGlacier',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'archive/'},
                'Transitions': [
                    {
                        'Days': 90,
                        'StorageClass': 'GLACIER'
                    }
                ]
            },
            {
                'Id': 'DeleteOldData',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'temp/'},
                'Expiration': {
                    'Days': 7  # Delete after 7 days
                }
            }
        ]
    }
)
```

**4. Real-World Example**:

**Scenario**: Sales data pipeline

```python
# Bronze: Keep in Standard for 7 days (frequent access)
# Then move to Standard-IA for 30 days
# Then move to Glacier for archive

{
    'Id': 'BronzeLifecycle',
    'Filter': {'Prefix': 'bronze/sales/'},
    'Transitions': [
        {'Days': 7, 'StorageClass': 'STANDARD_IA'},
        {'Days': 37, 'StorageClass': 'GLACIER'}
    ]
}

# Silver: Keep in Standard-IA (less frequent access)
{
    'Id': 'SilverLifecycle',
    'Filter': {'Prefix': 'silver/sales/'},
    'Transitions': [
        {'Days': 0, 'StorageClass': 'STANDARD_IA'},
        {'Days': 365, 'StorageClass': 'GLACIER'}
    ]
}

# Temp: Delete after 1 day
{
    'Id': 'TempLifecycle',
    'Filter': {'Prefix': 'temp/'},
    'Expiration': {'Days': 1}
}
```

**5. Cost Savings**:

**Example**:
- 1TB data in Standard: $23/month
- 1TB data in Standard-IA: $12.50/month (46% savings)
- 1TB data in Glacier: $4/month (83% savings)

**Key Points**:
- ✅ Automate transitions to cheaper storage
- ✅ Delete temporary data automatically
- ✅ Significant cost savings
- ✅ No manual intervention needed

---

#### Q6: How Do You Handle Glue Job Failures?

**Question**: "Your Glue job failed. Walk me through your troubleshooting process."

**Answer Structure**:

**1. Check Job Run Status**:

```python
import boto3

glue_client = boto3.client('glue')

# Get job run details
response = glue_client.get_job_run(
    JobName='nike-sales-etl-job',
    RunId='jr_1234567890'
)

status = response['JobRun']['JobRunState']
print(f"Status: {status}")  # SUCCEEDED, FAILED, RUNNING, STOPPED
```

**2. Common Failure Causes**:

**Cause 1: Insufficient Permissions**:
```python
# Error: AccessDeniedException
# Solution: Check IAM role permissions
# Ensure role has:
# - s3:GetObject, s3:PutObject
# - glue:GetTable, glue:GetDatabase
```

**Cause 2: Schema Mismatch**:
```python
# Error: AnalysisException: cannot resolve column
# Solution: Check schema in Data Catalog
# Ensure columns match between source and target
```

**Cause 3: Out of Memory**:
```python
# Error: OutOfMemoryError
# Solution: Increase workers or worker type
glue_client.update_job(
    JobName='nike-sales-etl-job',
    NumberOfWorkers=10,  # Was 2
    WorkerType='G.2X'  # Was G.1X
)
```

**Cause 4: Data Quality Issues**:
```python
# Error: NullPointerException
# Solution: Add data quality checks
def filter_valid_data(record):
    return record.get("customer_id") is not None and \
           record.get("amount") is not None

filtered = Filter.apply(frame=datasource, f=filter_valid_data)
```

**3. Debugging Steps**:

**Step 1: Check CloudWatch Logs**:
```python
# Glue logs are in CloudWatch
# Log group: /aws-glue/jobs/
# Check for error messages
```

**Step 2: Check Job Metrics**:
```python
# Check job metrics in Glue console
# - Execution time
# - Data processed
# - Errors
```

**Step 3: Test with Sample Data**:
```python
# Test job with small sample first
# Use job bookmarks to process incrementally
```

**4. Retry Strategy**:

```python
# Configure retry in Step Functions or EventBridge
# Or implement in Lambda trigger

def lambda_handler(event, context):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = glue_client.start_job_run(
                JobName='nike-sales-etl-job'
            )
            # Monitor job
            job_run_id = response['JobRunId']
            # Wait and check status
            return {'statusCode': 200}
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                # Send alert
                send_alert(f"Job failed after {max_retries} retries")
                raise
            time.sleep(60)  # Wait before retry
```

**Key Points**:
- ✅ Check CloudWatch logs
- ✅ Verify IAM permissions
- ✅ Check schema compatibility
- ✅ Right-size workers
- ✅ Add data quality checks

---

#### Q7: Design a Data Lake Architecture on AWS

**Question**: "Design a data lake architecture on AWS for 1TB/day. Walk me through your design."

**Answer Structure**:

**1. Requirements**:
- Volume: 1TB/day
- Sources: APIs, databases, files
- Processing: Batch (hourly) + Real-time (optional)
- Analytics: Ad-hoc queries + Reporting
- Retention: 2 years

**2. Architecture Design**:

```
┌─────────────────────────────────────────────────────────┐
│              Data Sources                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  APIs    │  │  RDS     │  │  Files   │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼──────────────┼──────────────┼──────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   S3 Bronze Layer            │
        │   (Raw Data - Partitioned)   │
        │   year/month/day/hour        │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   AWS Glue (ETL)              │
        │   - Clean data                │
        │   - Validate schema          │
        │   - Deduplicate              │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   S3 Silver Layer            │
        │   (Cleaned Data - Parquet)    │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   AWS Glue (Aggregation)      │
        │   - Aggregate by date        │
        │   - Business metrics         │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   S3 Gold Layer              │
        │   (Aggregated - Parquet)     │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Analytics Layer             │
        │  ┌──────────┐  ┌──────────┐ │
        │  │  Athena  │  │ Redshift │ │
        │  └──────────┘  └──────────┘ │
        └──────────────────────────────┘
```

**3. Component Details**:

**Storage (S3)**:
```python
# Bronze: Raw data (Standard storage)
s3://nike-data-lake/bronze/sales/year=2024/month=01/day=15/hour=10/

# Silver: Cleaned data (Standard-IA after 30 days)
s3://nike-data-lake/silver/sales/year=2024/month=01/day=15/

# Gold: Aggregated data (Standard-IA)
s3://nike-data-lake/gold/daily_sales/year=2024/month=01/
```

**Processing (Glue)**:
```python
# Bronze to Silver: Daily job
glue_job_bronze_to_silver = {
    'Name': 'bronze-to-silver',
    'Workers': 10,  # For 1TB/day
    'WorkerType': 'G.2X',
    'Schedule': 'cron(0 2 * * ? *)'  # Daily at 2 AM
}

# Silver to Gold: Daily aggregation
glue_job_silver_to_gold = {
    'Name': 'silver-to-gold',
    'Workers': 5,
    'WorkerType': 'G.1X',
    'Schedule': 'cron(0 4 * * ? *)'  # Daily at 4 AM
}
```

**Analytics**:
```python
# Athena: Ad-hoc queries on S3
# Redshift: Data warehouse for reporting
# Load from S3 Gold layer
```

**4. Cost Estimate**:

**Storage**:
- 1TB/day × 730 days = 730TB
- Bronze (Standard): 365TB × $0.023/GB = $8,395/month
- Silver (Standard-IA): 365TB × $0.0125/GB = $4,563/month
- **Total Storage**: ~$13,000/month

**Processing (Glue)**:
- Bronze to Silver: 10 workers × $0.44/hour × 2 hours = $8.80/day
- Silver to Gold: 5 workers × $0.44/hour × 1 hour = $2.20/day
- **Total Processing**: ~$11/day = $330/month

**Analytics**:
- Athena: $5/TB scanned (pay per query)
- Redshift: 2-node dc2.large = ~$300/month

**Total**: ~$13,630/month

**5. Optimization Strategies**:
- ✅ Use lifecycle policies (move to Glacier)
- ✅ Compress data (Parquet)
- ✅ Partition properly
- ✅ Use appropriate storage classes

**Key Points**:
- ✅ Medallion architecture (Bronze/Silver/Gold)
- ✅ Partition by date
- ✅ Use Parquet format
- ✅ Glue for ETL
- ✅ Athena/Redshift for analytics

---

#### Q8: Explain Kinesis Sharding Strategy

**Question**: "How do you determine the number of shards for a Kinesis stream?"

**Answer Structure**:

**1. Kinesis Shard Limits**:
- **Write**: 1MB/second per shard
- **Read**: 2MB/second per shard
- **Records**: 1,000 records/second per shard

**2. Calculate Shards Needed**:

**Formula**:
```
Shards = MAX(
    Write Throughput (MB/s) / 1,
    Read Throughput (MB/s) / 2,
    Records/second / 1000
)
```

**Example**:
```
Requirements:
- Write: 5MB/second
- Read: 10MB/second
- Records: 5,000/second

Shards = MAX(
    5 / 1 = 5,
    10 / 2 = 5,
    5000 / 1000 = 5
) = 5 shards
```

**3. Partition Key Strategy**:

**Even Distribution**:
```python
# Good: Even distribution
partition_key = str(customer_id)  # Many customers = even distribution

# Bad: Skewed distribution
partition_key = "sales"  # All records go to one shard!
```

**4. Real-World Example**:

**Scenario**: Sales events, 10,000 events/second

```python
# Calculate shards
events_per_second = 10000
avg_record_size = 1  # KB
write_throughput = (events_per_second * avg_record_size) / 1024  # MB/s
# = 10MB/s

shards_needed = write_throughput / 1  # 1MB/s per shard
# = 10 shards

# Create stream
kinesis_client.create_stream(
    StreamName='nike-sales-stream',
    ShardCount=10
)

# Use customer_id as partition key (even distribution)
kinesis_client.put_record(
    StreamName='nike-sales-stream',
    Data=json.dumps(sale_event),
    PartitionKey=str(sale_event['customer_id'])
)
```

**5. Scaling Shards**:

**Increase Shards** (Split):
```python
# Split shard when approaching limits
kinesis_client.split_shard(
    StreamName='nike-sales-stream',
    ShardToSplit='shardId-000000000000',
    NewStartingHashKey='340282366920938463463374607431768211456'  # Halfway point
)
```

**Decrease Shards** (Merge):
```python
# Merge shards when underutilized
kinesis_client.merge_shards(
    StreamName='nike-sales-stream',
    ShardToMerge='shardId-000000000000',
    AdjacentShardToMerge='shardId-000000000001'
)
```

**Key Points**:
- ✅ 1 shard = 1MB/s write, 2MB/s read
- ✅ Calculate based on throughput
- ✅ Use even partition keys
- ✅ Scale up/down as needed

---

### 18. System Design with AWS

#### 18.1 Medallion Architecture on AWS

**Architecture**:
```
S3 Bronze (Raw)
    ↓
Glue/EMR (ETL)
    ↓
S3 Silver (Cleaned)
    ↓
Glue/EMR (Aggregation)
    ↓
S3 Gold (Aggregated)
    ↓
Redshift/Athena (Analytics)
```

**Implementation**:
```python
# Bronze: Raw ingestion
s3_client.upload_file('sales.json', 'nike-data-bucket', 'bronze/sales/')

# Silver: Glue ETL
glue_client.start_job_run(JobName='bronze-to-silver')

# Gold: Aggregation
glue_client.start_job_run(JobName='silver-to-gold')

# Analytics: Redshift
redshift_client.execute_statement(
    Sql="SELECT * FROM sales WHERE year = 2024"
)
```

---

### 19. Troubleshooting Common Issues

#### 19.1 S3 Access Denied

**Problem**: Cannot access S3 bucket

**Symptoms**:
- Error: `AccessDenied`
- Cannot read/write objects

**Debugging Steps**:

**Step 1: Check IAM Permissions**:
```python
# Verify IAM role has S3 permissions
iam_client.get_role_policy(
    RoleName='GlueServiceRole',
    PolicyName='S3Access'
)

# Should have:
# - s3:GetObject
# - s3:PutObject
# - s3:ListBucket
```

**Step 2: Check Bucket Policy**:
```python
# Check bucket policy
s3_client.get_bucket_policy(Bucket='nike-data-bucket')

# Ensure allows access from your role
```

**Step 3: Check Resource ARN**:
```python
# Verify ARN is correct
# Format: arn:aws:s3:::bucket-name/*
```

**Solution**:
```python
# Add S3 permissions to IAM role
iam_client.put_role_policy(
    RoleName='GlueServiceRole',
    PolicyName='S3Access',
    PolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::nike-data-bucket/*"
            }
        ]
    })
)
```

---

#### 19.2 Glue Job Slow

**Problem**: Glue job taking too long

**Symptoms**:
- Job runs for hours
- High CloudWatch costs
- Timeout errors

**Debugging Steps**:

**Step 1: Check Worker Count**:
```python
# Check current workers
response = glue_client.get_job(JobName='nike-sales-etl-job')
workers = response['Job']['NumberOfWorkers']
print(f"Current workers: {workers}")
```

**Step 2: Check Data Volume**:
```python
# Check input data size
# Large data = need more workers
```

**Step 3: Check File Format**:
```python
# JSON is slower than Parquet
# Check if using appropriate format
```

**Solutions**:

**Solution 1: Increase Workers**:
```python
glue_client.update_job(
    JobName='nike-sales-etl-job',
    NumberOfWorkers=20,  # Was 5
    WorkerType='G.2X'  # Larger workers
)
```

**Solution 2: Use Parquet Format**:
```python
# Convert to Parquet (10x faster reads)
cleaned_df.write.parquet("s3://nike-data-bucket/silver/sales/")
```

**Solution 3: Partition Data**:
```python
# Partition for parallel processing
cleaned_df.write.partitionBy("year", "month", "day") \
    .parquet("s3://nike-data-bucket/silver/sales/")
```

**Solution 4: Enable Job Bookmarks**:
```python
# Only process new data
# Reduces processing time
glue_client.update_job(
    JobName='nike-sales-etl-job',
    DefaultArguments={
        '--job-bookmark-option': 'job-bookmark-enable'
    }
)
```

---

#### 19.3 Redshift Query Slow

**Problem**: Redshift queries taking too long

**Symptoms**:
- Queries run for minutes
- High CPU usage
- Timeout errors

**Debugging Steps**:

**Step 1: Check Query Plan**:
```sql
EXPLAIN SELECT * FROM sales WHERE sale_date = '2024-01-15';
-- Look for: Seq Scan (bad!) vs Index Scan (good!)
```

**Step 2: Check DISTKEY**:
```sql
-- Check if DISTKEY is appropriate
SELECT 
    "column", 
    distkey 
FROM SVV_TABLE_INFO 
WHERE "table" = 'sales';
```

**Step 3: Check SORTKEY**:
```sql
-- Check if SORTKEY is used in WHERE clause
SELECT * FROM sales WHERE sale_date = '2024-01-15';
-- sale_date should be SORTKEY
```

**Solutions**:

**Solution 1: Fix DISTKEY**:
```sql
-- Recreate table with correct DISTKEY
CREATE TABLE sales_new
DISTKEY (customer_id)  -- Even distribution
AS SELECT * FROM sales;

DROP TABLE sales;
ALTER TABLE sales_new RENAME TO sales;
```

**Solution 2: Fix SORTKEY**:
```sql
-- Recreate table with correct SORTKEY
CREATE TABLE sales_new
DISTKEY (customer_id)
SORTKEY (sale_date)  -- For date queries
AS SELECT * FROM sales;
```

**Solution 3: Vacuum and Analyze**:
```sql
-- Reclaim space and update statistics
VACUUM sales;
ANALYZE sales;
```

**Solution 4: Use COPY (Not INSERT)**:
```sql
-- COPY is much faster
COPY sales FROM 's3://nike-data-bucket/sales/' IAM_ROLE '...';
```

---

#### 19.4 Kinesis Throttling

**Problem**: Kinesis stream throttling errors

**Symptoms**:
- Error: `ProvisionedThroughputExceededException`
- Records rejected
- High latency

**Debugging Steps**:

**Step 1: Check Shard Count**:
```python
# Check current shards
response = kinesis_client.describe_stream(StreamName='nike-sales-stream')
shard_count = len(response['StreamDescription']['Shards'])
print(f"Current shards: {shard_count}")
```

**Step 2: Check Throughput**:
```python
# Calculate required throughput
# 1 shard = 1MB/s write, 2MB/s read
required_shards = write_throughput_mbps / 1
```

**Solutions**:

**Solution 1: Increase Shards**:
```python
# Split shards to increase capacity
kinesis_client.split_shard(
    StreamName='nike-sales-stream',
    ShardToSplit='shardId-000000000000',
    NewStartingHashKey='340282366920938463463374607431768211456'
)
```

**Solution 2: Fix Partition Key**:
```python
# Use even distribution
# Bad: All records to one shard
partition_key = "sales"

# Good: Even distribution
partition_key = str(customer_id)
```

---

#### 19.5 Lambda Timeout

**Problem**: Lambda function timing out

**Symptoms**:
- Error: `Task timed out`
- Function doesn't complete
- High costs

**Solutions**:

**Solution 1: Increase Timeout**:
```python
lambda_client.update_function_configuration(
    FunctionName='process-sales',
    Timeout=300  # 5 minutes (was 3 minutes)
)
```

**Solution 2: Optimize Code**:
```python
# Process in batches
# Use async operations
# Avoid blocking operations
```

**Solution 3: Use Step Functions**:
```python
# For long-running tasks, use Step Functions
# Lambda triggers Step Functions
# Step Functions orchestrates workflow
```

---

#### 19.6 Athena Query Slow

**Problem**: Athena queries taking too long

**Symptoms**:
- Queries run for minutes
- High costs
- Timeout errors

**Solutions**:

**Solution 1: Use Parquet Format**:
```python
# Parquet is columnar, compressed
# Much faster than JSON/CSV
df.write.parquet("s3://nike-data-bucket/sales/")
```

**Solution 2: Partition Data**:
```python
# Partition for partition pruning
df.write.partitionBy("year", "month", "day") \
    .parquet("s3://nike-data-bucket/sales/")

# Query only scans relevant partitions
```

**Solution 3: Optimize File Sizes**:
```python
# Target: 128MB - 1GB per file
# Too small: Too many files (overhead)
# Too large: Slow processing
```

**Solution 4: Use Columnar Formats**:
```sql
-- Parquet is columnar (faster for analytics)
-- Only reads columns needed
SELECT customer_id, amount FROM sales;
-- Only reads customer_id and amount columns ✅
```

---

### 20. Hands-On Exercises

#### Exercise 1: Build S3 Data Lake

**Objective**: Create partitioned S3 structure

**Tasks**:
1. Create S3 bucket
2. Upload data with partitioning (year/month/day)
3. List and query partitioned data

#### Exercise 2: Create Glue ETL Pipeline

**Objective**: Build ETL pipeline with Glue

**Tasks**:
1. Create Glue database and table
2. Create Glue job
3. Transform data
4. Write to S3

---

## ✅ Best Practices Summary

### S3
- ✅ Use appropriate storage classes
- ✅ Enable lifecycle policies
- ✅ Partition data properly
- ✅ Use Parquet format

### Glue
- ✅ Use Data Catalog
- ✅ Enable job bookmarks
- ✅ Right-size workers
- ✅ Use appropriate file formats

### EMR
- ✅ Use spot instances
- ✅ Right-size cluster
- ✅ Use S3 (not HDFS)
- ✅ Terminate when done

### Redshift
- ✅ Use DISTKEY and SORTKEY
- ✅ Use COPY command
- ✅ Compress data
- ✅ Vacuum regularly

### Kinesis
- ✅ Right-size shards
- ✅ Use partition keys
- ✅ Enable compression
- ✅ Use Firehose for simple ETL

---

## 🎯 Next Steps

Practice building:
- End-to-end ETL pipelines
- Real-time streaming
- Data lake architecture
- Cost optimization

**Study Time**: Spend 2-3 weeks on AWS, build real projects!

---

## 📚 Additional Resources

- **AWS Documentation**: https://docs.aws.amazon.com/
- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/
- **AWS Training**: https://aws.amazon.com/training/

---

**Keep Building! 🚀**
