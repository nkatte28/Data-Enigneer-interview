# Topic 2: Data Modeling

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Understand what data modeling is and why it's important
- Design conceptual, logical, and physical data models
- Apply normalization techniques (1NF, 2NF, 3NF)
- Design dimensional models (Star Schema, Snowflake Schema)
- Implement Slowly Changing Dimensions (SCD Types 0-6)
- Choose appropriate modeling techniques for different use cases
- Explain trade-offs between normalized and denormalized models

---

## 📖 Core Concepts

### 1. What is Data Modeling?

**Definition**: Data modeling is the process of creating a visual representation of either a whole information system or parts of it to communicate connections between data points and structures.

**Purpose**:
- Illustrate types of data used and stored within the system
- Show relationships among data types
- Organize data in formats and attributes
- Translate business requirements into database design

**Key Benefits**:
- Reduces errors in software and database development
- Increases consistency in documentation and system design
- Improves application and database performance
- Eases data mapping throughout the organization
- Improves communication between developers and business intelligence teams

**Data Model as a Blueprint**: A data model can be compared to a roadmap, an architect's blueprint, or any formal diagram that facilitates understanding of what is being designed.

---

### 1.1 Understanding Data Storage Systems: Database, Data Warehouse, Data Lake, and Delta Lake

Before diving into data modeling, it's important to understand the different types of data storage systems and their characteristics. Each system serves different purposes and requires different modeling approaches.

#### Comparison Table: Database (OLTP) vs Data Warehouse (OLAP) vs Data Lake vs Delta Lake

| Feature | Database (OLTP) | Data Warehouse (OLAP) | Data Lake | Delta Lake |
|---------|----------------|----------------------|-----------|------------|
| **Primary Use** | Transactions | Analytics | Raw storage | Unified analytics |
| **Workload** | OLTP | OLAP | Mixed | Mixed |
| **Purpose** | Stores real-time transactional data | Stores & analyzes structured data (often from a data warehouse) | Stores raw, unstructured data | Combines Data Warehouse & Data Lake functionalities |
| **Schema** | Strict (Predefined/Schema-on-Write) | Strict (Predefined/Schema-on-Write) | Flexible (Schema-on-Read) | Enforced (Supports Schema Evolution) |
| **Data Types** | Structured (Tables) | Structured (Tables) | Any (Structured, Semi-Structured, Unstructured) | Any (Structured & Semi-Structured) |
| **Updates** | Row-level (Fast CRUD operations) | Limited (Append-heavy, some updates) | Hard (Immutable, append-only) | Easy (MERGE operations, ACID transactions) |
| **ACID** | Yes | Yes | No | Yes |
| **Processing** | Fast transactions (CRUD operations: Create, Read, Update, Delete) | Fast analytics (Business Intelligence, Reporting) | Big Data Processing | Streaming + Batch Processing |
| **Query Performance** | Fast for small queries | Optimized for Aggregations | Slower (due to raw data) | Faster Queries (Indexed) |
| **Cost** | Medium | High | Low (storage is cheap) | Low–Medium (Optimized cost-performance) |
| **Modeling** | ER (Entity-Relationship, Normalized) | Star/Snowflake (Dimensional) | None (Less formal, partitioning-focused) | Star on top (Dimensional modeling with schema evolution) |
| **Examples** | MySQL, PostgreSQL, MongoDB | Snowflake, Redshift, BigQuery | AWS S3, Azure Data Lake | Databricks, Delta Lake |

#### Database (OLTP) - Online Transaction Processing

**Purpose**: Handle day-to-day operational transactions

**Key Characteristics**:
- **Schema-on-Write**: Schema must be defined before data insertion
- **ACID Compliance**: Ensures data integrity for transactions
- **Normalized Structure**: Reduces redundancy, ensures consistency
- **Fast CRUD Operations**: Optimized for Create, Read, Update, Delete
- **Row-Oriented Storage**: Efficient for transactional queries

**Use Cases**:
- E-commerce order processing
- Banking transactions
- User account management
- Inventory management

**Data Modeling Approach**: Normalized relational model (3NF)

#### Data Warehouse (OLAP) - Online Analytical Processing

**Purpose**: Store and analyze historical data for business intelligence

**Key Characteristics**:
- **Schema-on-Write**: Structured schema enforced on ingestion
- **Columnar Storage**: Optimized for analytical queries
- **Denormalized Structure**: Star/Snowflake schemas for faster queries
- **Historical Data**: Stores time-series data for trend analysis
- **Pre-aggregated Data**: Materialized views for common queries

**Use Cases**:
- Business intelligence dashboards
- Sales analytics and reporting
- Financial reporting
- Trend analysis

**Data Modeling Approach**: Dimensional modeling (Star/Snowflake schema)

#### Data Lake

**Purpose**: Store raw data in its native format for future processing

**Key Characteristics**:
- **Schema-on-Read**: Schema applied when querying, not on ingestion
- **Flexible Storage**: Handles structured, semi-structured, and unstructured data
- **Cost-Effective**: Cheap storage (object storage like S3)
- **Scalable**: Handles petabytes of data
- **Raw Data**: Stores data as-is without transformation

**Use Cases**:
- Raw data ingestion
- Data exploration and discovery
- Machine learning and AI workloads
- Long-term data archival
- Big data processing

**Data Modeling Approach**: Less formal modeling, focuses on data organization and partitioning

#### Delta Lake

**Purpose**: Combine the flexibility of data lakes with the reliability of data warehouses

**Key Characteristics**:
- **Schema Evolution**: Can evolve schema over time
- **ACID Transactions**: Ensures data consistency
- **Time Travel**: Query historical versions of data
- **Unified Batch & Streaming**: Handles both batch and real-time processing
- **Indexed Queries**: Faster query performance than traditional data lakes
- **Open Format**: Built on open-source Parquet format

**Use Cases**:
- Modern data lakehouse architecture
- Streaming analytics
- Data engineering pipelines
- ML feature stores

**Data Modeling Approach**: Supports both normalized and dimensional models, with schema evolution capabilities

#### When to Use Each System

**Use Database (OLTP)** when:
- You need real-time transaction processing
- Data integrity is critical (ACID compliance)
- You're handling operational workloads
- Queries are simple and fast

**Use Data Warehouse (OLAP)** when:
- You need business intelligence and analytics
- You're analyzing historical trends
- You need fast aggregations and reporting
- Data is structured and well-defined

**Use Data Lake** when:
- You're ingesting raw data from multiple sources
- You need cost-effective storage for large volumes
- Data structure is unknown or changing
- You're doing data exploration and ML

**Use Delta Lake** when:
- You need both flexibility and reliability
- You're building modern data lakehouse architecture
- You need schema evolution capabilities
- You're processing both batch and streaming data

---

### 2. Different Levels of Data Models

Data modeling employs a layered approach, progressing from abstract to concrete:

#### 2.1 Conceptual Data Models (Domain Models)

**Purpose**: High-level, big-picture view of what the system will contain from a **business perspective**

**Characteristics**:
- Focus on **business concepts and rules** (WHAT, not HOW)
- **No technical implementation details** - uses business language
- Simple notation (often Entity-Relationship diagrams)
- Created during initial requirements gathering with business stakeholders
- **Independent of any technology or database system**

**Components**:
- **Entity Classes**: Types of things important for the business (e.g., Customer, Product, Order)
- **Attributes**: Business characteristics (e.g., Customer Name, Product Price) - **no data types**
- **Relationships**: How business entities relate (e.g., Customer places Order)
- **Constraints**: Business rules (e.g., Order must have at least one Product)
- **Security Requirements**: Who can access what data (business-level)

**Key Distinction**: Conceptual models answer "What data do we need?" not "How do we store it?"

**Example**:
```
Business Entities:
  - Customer
  - Order  
  - Product

Business Relationships: 
  - A Customer can place many Orders (1:many)
  - An Order can contain many Products (many:many)
  - A Product can be in many Orders (many:many)

Business Attributes (conceptual level):
  - Customer: Name, Email Address, Mailing Address
  - Order: Date Placed, Total Amount
  - Product: Product Name, Price, Category

Business Rules:
  - Every Order must have at least one Product
  - Every Order must belong to one Customer
  - Customer Email must be unique
```

**Note**: No data types, no technical structure - purely business-focused!

#### 2.2 Logical Data Models

**Purpose**: Detailed representation of data structures with **generic data types** but **independent of specific database system**

**Characteristics**:
- More detailed than conceptual models
- Uses formal notation (UML, IDEF1X, etc.)
- Specifies **generic data types** (INT, VARCHAR, DATE) - **not DBMS-specific**
- Shows relationships with cardinality
- **Independent of database management system (DBMS)** - could work with PostgreSQL, MySQL, Oracle, etc.
- Includes normalization structure

**Key Distinction**: Logical models answer "What is the structure?" using generic types, but don't specify "Which database system?"

**Components**:
- **Entities**: Detailed entity definitions (tables)
- **Attributes**: Generic data types (INT, VARCHAR, DATE), lengths, constraints
- **Relationships**: Cardinality (1:1, 1:many, many:many) with foreign keys
- **Keys**: Primary keys, foreign keys
- **Normalization**: Up to 3NF typically

**Example** (Generic data types - not DBMS-specific):
```
Customer Entity:
  - customer_id: Integer, Primary Key
  - first_name: String(50), Required
  - last_name: String(50), Required
  - email: String(100), Unique, Required
  - phone: String(20), Optional
  - created_date: DateTime, Required

Order Entity:
  - order_id: Integer, Primary Key
  - customer_id: Integer, Foreign Key -> Customer.customer_id
  - order_date: DateTime, Required
  - total_amount: Decimal(10,2)

OrderItem Entity (for many-to-many):
  - order_id: Integer, Foreign Key -> Order.order_id
  - product_id: Integer, Foreign Key -> Product.product_id
  - quantity: Integer
  - unit_price: Decimal(10,2)
```

**When Used**: 
- Highly procedural implementation environments
- Data warehouse design
- Reporting system development
- Often skipped in agile/DevOps practices

**Note**: Uses generic types (Integer, String, DateTime) that can be implemented in any DBMS

#### 2.3 Physical Data Models

**Purpose**: **DBMS-specific** schema for how data will be **physically stored** in a particular database system

**Characteristics**:
- Most concrete and detailed
- **DBMS-specific** (PostgreSQL uses SERIAL, MySQL uses AUTO_INCREMENT, Oracle uses SEQUENCE)
- Includes **performance tuning considerations** (indexes, partitioning)
- **Finalized design ready for implementation**
- Includes storage optimization

**Key Distinction**: Physical models answer "How do we implement this in PostgreSQL/MySQL/Oracle?" with specific syntax and optimizations.

**Components**:
- **Tables**: Actual table structures with DBMS-specific syntax
- **Columns**: Data types **specific to chosen DBMS** (SERIAL in PostgreSQL, AUTO_INCREMENT in MySQL)
- **Indexes**: For performance optimization (specific index types per DBMS)
- **Partitioning**: Table partitioning strategies (DBMS-specific syntax)
- **Storage**: Storage parameters, compression (DBMS-specific)
- **Keys**: Primary keys, foreign keys, unique constraints (with DBMS syntax)
- **Associative Tables**: For many-to-many relationships

**Example**:
```sql
-- PostgreSQL Physical Model
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_email (email),
    INDEX idx_customer_name (last_name, first_name)
) PARTITION BY RANGE (created_date);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) CHECK (total_amount >= 0),
    INDEX idx_order_customer (customer_id),
    INDEX idx_order_date (order_date)
);
```

**Performance Considerations**:
- Indexing strategies
- Partitioning schemes
- Denormalization for query performance
- Materialized views
- Column storage vs row storage

---

#### Comparison: Conceptual vs Logical vs Physical

| Aspect | Conceptual | Logical | Physical |
|--------|------------|---------|----------|
| **Focus** | Business concepts | Data structure | Database implementation |
| **Language** | Business terms | Generic technical terms | DBMS-specific syntax |
| **Data Types** | None (business attributes) | Generic (INT, VARCHAR, DATE) | DBMS-specific (SERIAL, AUTO_INCREMENT) |
| **Keys** | Relationships only | Primary/Foreign keys defined | Primary/Foreign keys with DBMS syntax |
| **Indexes** | No | No | Yes (performance optimization) |
| **Normalization** | Not applicable | Up to 3NF | May denormalize for performance |
| **DBMS Independent** | Yes | Yes | No (specific to PostgreSQL/MySQL/etc.) |
| **Example** | "Customer has Name and Email" | `customer_id: Integer, email: String(100)` | `customer_id SERIAL PRIMARY KEY` |

**Key Takeaway**: 
- **Conceptual** = Business view (WHAT data)
- **Logical** = Generic structure (HOW data is organized - any DBMS)
- **Physical** = Specific implementation (HOW data is stored - specific DBMS)

---

### 3. Data Modeling Process

The data modeling process follows a systematic workflow:

#### Step 1: Identify the Entities

**What**: Identify things, events, or concepts represented in the dataset

**Guidelines**:
- Each entity should be cohesive and logically discrete
- Entities represent nouns (Customer, Product, Order, Transaction)
- Avoid overlapping entities

**Example**: For an e-commerce system
- Entities: Customer, Product, Order, Payment, Shipment, Review

#### Step 2: Identify Key Properties of Each Entity

**What**: Determine unique properties (attributes) that differentiate entities

**Guidelines**:
- Attributes describe characteristics of entities
- Each attribute should belong to one entity
- Identify unique identifiers (keys)

**Example**:
```
Customer Entity:
  - customer_id (unique identifier)
  - first_name
  - last_name
  - email
  - phone
  - address
  - registration_date

Product Entity:
  - product_id (unique identifier)
  - name
  - description
  - price
  - category
  - stock_quantity
```

#### Step 3: Identify Relationships Among Entities

**What**: Determine how entities relate to each other

**Relationship Types**:
- **One-to-One (1:1)**: One instance of Entity A relates to one instance of Entity B
- **One-to-Many (1:N)**: One instance of Entity A relates to many instances of Entity B
- **Many-to-Many (M:N)**: Many instances of Entity A relate to many instances of Entity B

**Documentation**: Usually documented via Unified Modeling Language (UML) or Entity-Relationship Diagrams (ERD)

**Example**:
```
Customer (1) ----< places >---- (many) Order
Order (many) ----< contains >---- (many) Product
Customer (1) ----< has >---- (1) Account
```

#### Step 4: Map Attributes to Entities Completely

**What**: Ensure all attributes are properly assigned to entities

**Guidelines**:
- Ensure model reflects how business will use the data
- Follow formal data modeling patterns
- Object-oriented developers: Use analysis/design patterns
- Data warehouse: Use dimensional modeling patterns

**Patterns**:
- **OLTP Systems**: Normalized patterns (3NF)
- **OLAP Systems**: Dimensional patterns (Star/Snowflake)
- **NoSQL**: Document, key-value, graph patterns

#### Step 5: Assign Keys and Normalize

**What**: Assign primary keys and decide on normalization level

**Key Types**:
- **Primary Key**: Unique identifier for each row
- **Foreign Key**: Reference to another table's primary key
- **Composite Key**: Multiple columns forming a key
- **Surrogate Key**: Artificial key (auto-increment, UUID)
- **Natural Key**: Business-meaningful key (email, SSN)

**Normalization**:
- Balance between reducing redundancy and performance
- Normalized: Less storage, more joins
- Denormalized: More storage, fewer joins, faster queries

**Example**:
```sql
-- Normalized (3NF)
Customers: customer_id (PK), name, email
Orders: order_id (PK), customer_id (FK), order_date
OrderItems: order_id (FK), product_id (FK), quantity, price

-- Denormalized (for analytics)
OrderSummary: order_id, customer_name, order_date, product_name, quantity, price
```

#### Step 6: Finalize and Validate the Data Model

**What**: Review, refine, and validate the model

**Validation Checklist**:
- ✅ All business requirements captured
- ✅ Relationships correctly defined
- ✅ Keys properly assigned
- ✅ Normalization appropriate for use case
- ✅ Performance considerations addressed
- ✅ Data integrity constraints defined
- ✅ Model reviewed by stakeholders

**Iterative Process**: Data modeling is iterative - refine as business needs change

---

### 4. Types of Data Modeling

Data modeling has evolved with database management systems:

#### 4.1 Relational Data Models

**History**: Proposed by IBM researcher E.F. Codd in 1970

**Characteristics**:
- Data organized in tables (relations)
- Explicit joins through foreign keys
- Reduces database complexity
- Maintains data integrity
- Minimizes redundancy through normalization

**Use Cases**:
- Transactional systems (OLTP)
- Point-of-sale systems
- Enterprise applications
- Most common database type

**Example**:
```sql
-- Relational Model
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE,
    total DECIMAL(10,2)
);
```

**SQL**: Relational databases use Structured Query Language (SQL)

#### 4.2 Entity-Relationship (ER) Data Models

**Purpose**: Visual representation of database structure

**Components**:
- **Entities**: Rectangles
- **Attributes**: Ovals
- **Relationships**: Diamonds
- **Cardinality**: Lines with notation (1, N, M)

**Tools**: ER modeling tools create visual maps
- ER/Studio
- Lucidchart
- dbdiagram.io
- Draw.io

**Example ER Diagram Notation**:
```
[Customer] ----<places>---- [Order]
    1                          N

[Order] ----<contains>---- [Product]
    M                          N
```

#### 4.3 Dimensional Data Models

**History**: Developed by Ralph Kimball for data warehouses

**Purpose**: Optimize data retrieval speeds for analytics

**Characteristics**:
- Designed for OLAP systems
- Increases redundancy for faster queries
- Focus on reporting and retrieval
- Star and Snowflake schemas

**Components**:
- **Fact Tables**: Measurable business events (sales, clicks, orders)
- **Dimension Tables**: Descriptive attributes (time, customer, product)

**Use Cases**:
- Data warehouses
- Business intelligence
- Analytics dashboards
- Reporting systems

#### 4.4 Star Schema

**Structure**: Central fact table surrounded by dimension tables

**Characteristics**:
- Denormalized dimensions
- Single level of dimensions
- Faster query performance
- Fewer JOIN operations
- More storage space

**Example**:
```
Fact Table: Sales
  - sale_id (PK)
  - date_id (FK -> Date)
  - customer_id (FK -> Customer)
  - product_id (FK -> Product)
  - store_id (FK -> Store)
  - quantity
  - revenue

Dimension Tables:
  - Date: date_id, year, quarter, month, day
  - Customer: customer_id, name, city, state
  - Product: product_id, name, category, brand
  - Store: store_id, name, location, region
```

**Visual Representation**:
```
        [Date]
           |
           |
[Product]--[Sales]--[Customer]
           |
           |
        [Store]
```

**Pros**:
- Simple to understand
- Fast queries (fewer joins)
- Easy for business users
- Optimized for analytics

**Cons**:
- Data redundancy in dimensions
- Storage overhead
- Harder to maintain consistency

#### 4.5 Snowflake Schema

**Structure**: Normalized star schema with hierarchical dimensions

**Characteristics**:
- Normalized dimension tables
- Multiple levels of dimensions
- Reduces data redundancy
- More memory efficient
- More complex queries

**Example**:
```
Fact Table: Sales
  - sale_id
  - date_id (FK)
  - customer_id (FK)
  - product_id (FK)
  - store_id (FK)
  - quantity, revenue

Dimension Tables:
  - Date: date_id, month_id (FK -> Month)
  - Month: month_id, quarter_id (FK -> Quarter)
  - Quarter: quarter_id, year_id (FK -> Year)
  - Year: year_id, year_value
  
  - Customer: customer_id, city_id (FK -> City)
  - City: city_id, state_id (FK -> State)
  - State: state_id, country_id (FK -> Country)
```

**Visual Representation**:
```
        [Year]
           |
        [Quarter]
           |
        [Month]
           |
        [Date]
           |
           |
[Product]--[Sales]--[Customer]
           |            |
           |         [City]
           |            |
        [Store]      [State]
                         |
                      [Country]
```

**Pros**:
- Reduced storage space
- Easier to maintain
- Better data integrity
- Less redundancy

**Cons**:
- More complex queries (more joins)
- Slower query performance
- Harder for business users to understand

**When to Use**:
- Large dimension tables
- Many attributes in dimensions
- Storage is a concern
- Dimension data changes frequently

#### 4.6 Hierarchical Data Models

**Structure**: Tree-like format representing one-to-many relationships

**Characteristics**:
- Each record has single root/parent
- Maps to one or more child tables
- Less efficient than modern models
- Still used in specific systems

**Use Cases**:
- XML systems
- Geographic Information Systems (GIS)
- File systems
- Organizational charts

**Example**: IBM Information Management System (IMS) - introduced 1966

#### 4.7 Object-Oriented Data Models

**History**: Gained traction in mid-1990s with OOP popularity

**Characteristics**:
- Objects as abstractions of real-world entities
- Grouped in class hierarchies
- Support complex data relationships
- Can incorporate tables

**Use Cases**:
- Multimedia databases
- Hypertext databases
- Complex data structures
- Object-oriented applications

#### 4.8 One Big Table (OBT) / Wide Table Approach

**Purpose**: Denormalize everything into a single wide table

**Characteristics**:
- All dimensions flattened into fact table
- Maximum denormalization
- Very fast queries (no joins)
- Massive storage overhead
- Difficult to maintain

**Use Cases**:
- Small datasets
- Simple analytics
- Columnar databases (BigQuery, Redshift)
- When joins are expensive

**Example**:
```sql
CREATE TABLE sales_wide (
    sale_id,
    sale_date,
    year, quarter, month, day,
    customer_id, customer_name, customer_city, customer_state,
    product_id, product_name, product_category, product_brand,
    store_id, store_name, store_location, store_region,
    quantity,
    revenue
);
```

**Trade-offs**:
- ✅ Fastest queries
- ✅ Simple for users
- ❌ Massive storage
- ❌ Data redundancy
- ❌ Hard to update

---

### 5. Normalization

**Purpose**: Organize data to reduce redundancy and improve data integrity

**Normal Forms**: Progressive levels of normalization

#### First Normal Form (1NF)

**Rules**:
1. Each column contains atomic (indivisible) values
2. Each row is unique
3. No repeating groups

**Example - Violating 1NF**:
```
Order Table:
order_id | customer_id | products
---------|-------------|------------------
1        | 101         | Laptop, Mouse, Keyboard
2        | 102         | Phone, Case
```

**Fixed (1NF)**:
```
Order Table:
order_id | customer_id
---------|-------------
1        | 101
2        | 102

OrderItems Table:
order_id | product_name
---------|-------------
1        | Laptop
1        | Mouse
1        | Keyboard
2        | Phone
2        | Case
```

#### Second Normal Form (2NF)

**Rules**:
1. Must be in 1NF
2. All non-key attributes fully dependent on primary key
3. No partial dependencies

**Example - Violating 2NF**:
```
OrderItems Table:
order_id | product_id | product_name | quantity | price
---------|------------|--------------|----------|-------
1        | P001       | Laptop       | 1        | 1000
1        | P002       | Mouse        | 2        | 20
```

**Problem**: `product_name` depends on `product_id`, not `order_id`

**Fixed (2NF)**:
```
OrderItems Table:
order_id | product_id | quantity | price
---------|------------|----------|-------
1        | P001       | 1        | 1000
1        | P002       | 2        | 20

Products Table:
product_id | product_name
-----------|-------------
P001       | Laptop
P002       | Mouse
```

#### Third Normal Form (3NF)

**Rules**:
1. Must be in 2NF
2. No transitive dependencies
3. Non-key attributes don't depend on other non-key attributes

**Example - Violating 3NF**:
```
Customers Table:
customer_id | name | city | state | zip_code | state_tax_rate
------------|------|------|-------|----------|---------------
101         | John | NYC  | NY    | 10001    | 0.08
102         | Jane | LA   | CA    | 90001    | 0.10
```

**Problem**: `state_tax_rate` depends on `state`, not `customer_id`

**Fixed (3NF)**:
```
Customers Table:
customer_id | name | city | zip_code | state_id
------------|------|------|----------|----------
101         | John | NYC  | 10001    | NY
102         | Jane | LA   | 90001    | CA

States Table:
state_id | state_name | tax_rate
---------|------------|----------
NY       | New York   | 0.08
CA       | California | 0.10
```

#### Boyce-Codd Normal Form (BCNF)

**Rules**:
1. Must be in 3NF
2. Every determinant is a candidate key

**When Needed**: When 3NF doesn't eliminate all redundancy

#### Fourth Normal Form (4NF)

**Rules**:
1. Must be in BCNF
2. No multi-valued dependencies

#### Fifth Normal Form (5NF)

**Rules**:
1. Must be in 4NF
2. No join dependencies

**Note**: 4NF and 5NF are rarely used in practice

---

### 6. Denormalization

**Purpose**: Intentionally introduce redundancy to improve query performance

**When to Denormalize**:
- Read-heavy workloads
- Analytics/OLAP systems
- Joins are expensive
- Storage cost is acceptable
- Data doesn't change frequently

**Techniques**:
1. **Flatten Dimensions**: Store dimension attributes in fact table
2. **Pre-compute Aggregates**: Store calculated values
3. **Duplicate Data**: Copy frequently accessed data
4. **Materialized Views**: Pre-computed query results

**Trade-offs**:
- ✅ Faster queries
- ✅ Simpler queries
- ❌ More storage
- ❌ Data redundancy
- ❌ Update anomalies
- ❌ Consistency challenges

---

### 7. Slowly Changing Dimensions (SCD)

**Problem**: How to handle changes to dimension data over time?

**Example**: Customer changes address, product price changes, employee gets promoted

#### SCD Type 0: Fixed/Static

**Behavior**: Dimension never changes

**Use Case**: Historical data that should never change

**Example**: Customer's original registration date

#### SCD Type 1: Overwrite

**Behavior**: Old value is overwritten with new value

**Use Case**: 
- Corrections to errors
- When history is not important
- Simple dimensions

**Example**:
```
Before:
customer_id | name  | city
------------|-------|------
101         | John  | NYC

After address change:
customer_id | name  | city
------------|-------|------
101         | John  | LA
```

**Pros**: Simple, no history tracking needed
**Cons**: Loses historical data

#### SCD Type 2: Add New Row

**Behavior**: Create new row with new values, keep old row

**Use Case**: 
- When history is important
- Most common SCD type
- Audit requirements

**Implementation**:
- Add `effective_date` and `expiry_date` columns
- Add `is_current` flag
- Add surrogate key or version number

**Example**:
```
customer_id | name | city | effective_date | expiry_date | is_current
------------|------|------|----------------|-------------|------------
101         | John | NYC  | 2020-01-01     | 2023-06-30  | N
101         | John | LA   | 2023-07-01     | NULL        | Y
```

**Pros**: Complete history preserved
**Cons**: More storage, more complex queries

#### SCD Type 3: Add New Column

**Behavior**: Add column to store previous value

**Use Case**: 
- Limited history needed (only previous value)
- When only one change is tracked

**Example**:
```
customer_id | name | current_city | previous_city
------------|------|--------------|--------------
101         | John | LA           | NYC
```

**Pros**: Simple, preserves one previous value
**Cons**: Limited history (only one previous value)

#### SCD Type 4: History Table

**Behavior**: Separate table for historical values

**Use Case**: 
- Current values in main table
- History in separate table

**Example**:
```
Customers (Current):
customer_id | name | city
------------|------|------
101         | John | LA

CustomerHistory:
customer_id | city | effective_date | expiry_date
------------|------|----------------|-------------
101         | NYC  | 2020-01-01     | 2023-06-30
101         | LA   | 2023-07-01    | NULL
```

**Pros**: Clean separation, fast current lookups
**Cons**: Requires joins for history

#### SCD Type 5: Mini-Dimension

**Behavior**: Separate table for frequently changing attributes

**Use Case**: 
- Some attributes change frequently
- Others change rarely

**Example**:
```
Customers (Static):
customer_id | name | birth_date

CustomerDemographics (Changing):
customer_id | age_group | income_range | effective_date
```

#### SCD Type 6: Hybrid

**Behavior**: Combination of Type 1, 2, and 3

**Use Case**: 
- Different attributes need different SCD types
- Complex requirements

**Example**:
```
customer_id | name | current_city | previous_city | effective_date | is_current
------------|------|--------------|---------------|----------------|------------
101         | John | LA           | NYC           | 2023-07-01     | Y
```

---

### 8. Data Modeling Methodologies

#### Kimball Methodology (Bottom-Up)

**Approach**: 
- Start with business processes
- Build data marts first
- Combine into data warehouse
- Dimensional modeling focus

**Principles**:
- Business process oriented
- Dimensional models (star schema)
- Conformed dimensions
- Incremental development

**Best For**:
- Quick delivery
- Business user focused
- Iterative development

#### Inmon Methodology (Top-Down)

**Approach**:
- Start with enterprise data model
- Build normalized data warehouse
- Create data marts from warehouse
- 3NF normalized

**Principles**:
- Enterprise-wide view
- Normalized warehouse
- Single source of truth
- Data marts as views

**Best For**:
- Large enterprises
- Complex requirements
- Long-term projects

#### Data Vault Methodology

**Approach**:
- Hub (business keys)
- Link (relationships)
- Satellite (descriptive attributes)
- Designed for scalability

**Best For**:
- Large-scale data warehouses
- Agile development
- Historical tracking

---

### 9. OLTP vs OLAP Data Modeling

#### OLTP (Online Transaction Processing)

**Purpose**: Support day-to-day operations

**Characteristics**:
- Normalized (3NF)
- Many small transactions
- Fast writes
- Current data
- Row-oriented storage

**Modeling Approach**:
- Relational model
- Normalized tables
- Foreign keys
- Indexes for lookups

**Example**: E-commerce order processing system

#### OLAP (Online Analytical Processing)

**Purpose**: Support analytics and reporting

**Characteristics**:
- Denormalized (star schema)
- Few large queries
- Fast reads
- Historical data
- Column-oriented storage

**Modeling Approach**:
- Dimensional model
- Star/Snowflake schema
- Fact and dimension tables
- Pre-aggregated data

**Example**: Sales analytics data warehouse

---

### 10. Benefits of Data Modeling

#### For Development
- **Reduces Errors**: Catch issues early in design phase
- **Consistency**: Standardized approach across organization
- **Documentation**: Visual representation of data structure
- **Communication**: Common language for stakeholders

#### For Performance
- **Query Optimization**: Proper indexing and structure
- **Storage Efficiency**: Normalization reduces redundancy
- **Scalability**: Design supports growth

#### For Business
- **Requirements Alignment**: Model reflects business needs
- **Data Quality**: Constraints ensure data integrity
- **Analytics**: Dimensional models enable fast reporting
- **Governance**: Clear data ownership and rules

#### For Maintenance
- **Easier Updates**: Clear structure makes changes easier
- **Troubleshooting**: Models help identify issues
- **Onboarding**: New team members understand structure quickly

---

## 🏗️ Design Patterns

### Pattern 1: Star Schema for Analytics

**When**: Building data warehouse for business intelligence

**Structure**:
- Central fact table
- Surrounding dimension tables
- Denormalized dimensions

**Example**: Sales analytics
```
Fact: Sales
Dimensions: Date, Customer, Product, Store, Promotion
```

### Pattern 2: Snowflake Schema for Large Dimensions

**When**: Dimension tables are very large with many attributes

**Structure**:
- Normalized dimensions
- Hierarchical relationships
- Reduced storage

**Example**: Time dimension with Year → Quarter → Month → Day

### Pattern 3: Fact Constellation (Galaxy Schema)

**When**: Multiple fact tables share dimensions

**Structure**:
- Multiple fact tables
- Shared conformed dimensions
- More complex than star schema

**Example**: Sales and Inventory facts sharing Product and Date dimensions

### Pattern 4: One Big Table for Simple Analytics

**When**: 
- Small to medium datasets
- Simple analytics needs
- Columnar database (BigQuery, Redshift)

**Structure**:
- Single wide table
- All dimensions flattened
- Maximum denormalization

---

## 💡 Interview Questions & Answers

### Q1: Explain the difference between Star Schema and Snowflake Schema

**Answer**:

**Star Schema**:
- Denormalized structure
- Single level of dimensions
- Dimension tables don't reference other tables
- Faster queries (fewer joins)
- More storage (data redundancy)
- Easier to understand

**Snowflake Schema**:
- Normalized structure
- Hierarchical dimensions
- Dimension tables reference other dimension tables
- More joins (slower queries)
- Less storage (normalized)
- More complex

**When to Use**:
- **Star**: Most analytics use cases, faster queries needed
- **Snowflake**: Large dimensions, storage is concern, dimension data changes frequently

**Example**:
```sql
-- Star Schema
SELECT 
    d.year,
    c.city,
    SUM(s.revenue) as total_revenue
FROM sales s
JOIN date_dim d ON s.date_id = d.date_id
JOIN customer_dim c ON s.customer_id = c.customer_id
GROUP BY d.year, c.city;

-- Snowflake Schema (more joins)
SELECT 
    y.year_value,
    ci.city_name,
    SUM(s.revenue) as total_revenue
FROM sales s
JOIN date_dim d ON s.date_id = d.date_id
JOIN month_dim m ON d.month_id = m.month_id
JOIN quarter_dim q ON m.quarter_id = q.quarter_id
JOIN year_dim y ON q.year_id = y.year_id
JOIN customer_dim c ON s.customer_id = c.customer_id
JOIN city_dim ci ON c.city_id = ci.city_id
GROUP BY y.year_value, ci.city_name;
```

---

### Q2: What is normalization and why is it important?

**Answer**:

**Normalization**: Process of organizing data to reduce redundancy and improve data integrity

**Normal Forms**:
1. **1NF**: Atomic values, no repeating groups
2. **2NF**: No partial dependencies
3. **3NF**: No transitive dependencies
4. **BCNF**: Every determinant is a candidate key

**Benefits**:
- Reduces data redundancy
- Prevents update anomalies
- Ensures data consistency
- Saves storage space
- Maintains referential integrity

**Trade-offs**:
- More tables = more joins
- Can impact query performance
- More complex queries

**When to Normalize**:
- OLTP systems (transactional)
- When data integrity is critical
- When storage is expensive
- When updates are frequent

**When to Denormalize**:
- OLAP systems (analytics)
- Read-heavy workloads
- When joins are expensive
- When storage is cheap

---

### Q3: Explain Slowly Changing Dimensions (SCD) Types

**Answer**:

**SCD Types**:

1. **Type 0**: Fixed - never changes
2. **Type 1**: Overwrite - lose history
3. **Type 2**: Add row - preserve history (most common)
4. **Type 3**: Add column - store previous value
5. **Type 4**: History table - separate table
6. **Type 5**: Mini-dimension - separate changing attributes
7. **Type 6**: Hybrid - combination

**Type 2 Example** (Most Important):
```sql
-- Customer dimension with SCD Type 2
CREATE TABLE customer_dim (
    customer_sk SERIAL PRIMARY KEY,  -- Surrogate key
    customer_id INT,                  -- Natural key
    name VARCHAR(100),
    city VARCHAR(100),
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE
);

-- When customer moves from NYC to LA
-- Old record
INSERT INTO customer_dim VALUES 
(1, 101, 'John', 'NYC', '2020-01-01', '2023-06-30', FALSE);

-- New record
INSERT INTO customer_dim VALUES 
(2, 101, 'John', 'LA', '2023-07-01', NULL, TRUE);
```

**When to Use Each**:
- **Type 1**: Corrections, history not needed
- **Type 2**: Most common, full history needed
- **Type 3**: Only previous value needed
- **Type 4**: Clean separation needed

---

### Q4: Design a data model for an e-commerce system

**Answer**:

**Requirements**:
- Customers place orders
- Orders contain multiple products
- Track order history
- Support analytics

**Approach**:

1. **Identify Entities**:
   - Customer, Order, Product, OrderItem, Payment, Shipment

2. **Design OLTP Model** (Normalized):
```sql
-- Customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INT REFERENCES categories(category_id),
    stock_quantity INT DEFAULT 0
);

-- Orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10,2)
);

-- Order Items
CREATE TABLE order_items (
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id)
);
```

3. **Design OLAP Model** (Star Schema):
```sql
-- Fact Table
CREATE TABLE fact_sales (
    sale_id SERIAL PRIMARY KEY,
    date_id INT REFERENCES dim_date(date_id),
    customer_id INT REFERENCES dim_customer(customer_id),
    product_id INT REFERENCES dim_product(product_id),
    order_id INT,
    quantity INT,
    revenue DECIMAL(10,2),
    discount_amount DECIMAL(10,2)
);

-- Dimension Tables
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date_value DATE,
    year INT,
    quarter INT,
    month INT,
    day INT,
    day_of_week VARCHAR(10)
);

CREATE TABLE dim_customer (
    customer_sk SERIAL PRIMARY KEY,
    customer_id INT,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN
);

CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(50),
    brand VARCHAR(50),
    price DECIMAL(10,2)
);
```

---

### Q5: When would you choose normalization vs denormalization?

**Answer**:

**Choose Normalization When**:
- **OLTP Systems**: Transactional databases
- **Data Integrity Critical**: Financial, healthcare systems
- **Frequent Updates**: Data changes often
- **Storage Expensive**: Need to minimize storage
- **Consistency Important**: Prevent update anomalies

**Choose Denormalization When**:
- **OLAP Systems**: Analytics, data warehouses
- **Read-Heavy**: Mostly SELECT queries
- **Performance Critical**: Query speed is priority
- **Storage Cheap**: Can afford redundancy
- **Simple Queries**: Want to avoid complex joins

**Hybrid Approach**:
- Normalize OLTP source systems
- Denormalize for analytics (data warehouse)
- Use ETL to transform normalized → denormalized

**Example**:
```
OLTP (Normalized):
customers → orders → order_items → products

OLAP (Denormalized):
fact_sales with flattened customer and product attributes
```

---

### Q6: What is a fact table and dimension table?

**Answer**:

**Fact Table**:
- Contains measurable business events
- Stores metrics/measures (sales, clicks, orders)
- Foreign keys to dimension tables
- Usually large (millions/billions of rows)
- Additive measures (can be summed)

**Characteristics**:
- Grain: Level of detail (e.g., one row per sale)
- Measures: Numeric values (revenue, quantity)
- Foreign keys: Links to dimensions

**Example**:
```sql
CREATE TABLE fact_sales (
    sale_id INT PRIMARY KEY,
    date_id INT,           -- FK to dim_date
    customer_id INT,       -- FK to dim_customer
    product_id INT,        -- FK to dim_product
    store_id INT,          -- FK to dim_store
    quantity INT,          -- Measure
    revenue DECIMAL(10,2), -- Measure
    discount DECIMAL(10,2) -- Measure
);
```

**Dimension Table**:
- Contains descriptive attributes
- Provides context for facts
- Usually smaller than fact tables
- Text attributes (names, descriptions)
- Used for filtering and grouping

**Characteristics**:
- Descriptive attributes
- Hierarchical relationships possible
- Used in WHERE and GROUP BY clauses

**Example**:
```sql
CREATE TABLE dim_customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    customer_segment VARCHAR(20)
);
```

**Relationship**:
- Fact table references dimension tables via foreign keys
- Star schema: Fact in center, dimensions around it
- Typical query: Join fact with dimensions, filter/group by dimensions, aggregate measures

---

## 📝 Practice Exercises

### Exercise 1: Design a Star Schema

**Scenario**: Design a data warehouse for a gaming company tracking player events

**Requirements**:
- Track game events (login, purchase, level_complete)
- Analyze by: date, player, game, device
- Metrics: event_count, revenue, play_time_minutes

**Solution Approach**:

```sql
-- Fact Table
CREATE TABLE fact_game_events (
    event_id BIGINT PRIMARY KEY,
    date_id INT REFERENCES dim_date(date_id),
    player_id INT REFERENCES dim_player(player_id),
    game_id INT REFERENCES dim_game(game_id),
    device_id INT REFERENCES dim_device(device_id),
    event_type VARCHAR(50),
    event_count INT DEFAULT 1,
    revenue DECIMAL(10,2),
    play_time_minutes INT
);

-- Dimension Tables
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date_value DATE,
    year INT,
    quarter INT,
    month INT,
    week INT,
    day INT,
    day_of_week VARCHAR(10),
    is_weekend BOOLEAN
);

CREATE TABLE dim_player (
    player_id INT PRIMARY KEY,
    player_name VARCHAR(100),
    registration_date DATE,
    country VARCHAR(50),
    player_segment VARCHAR(20), -- casual, regular, premium
    total_spent DECIMAL(10,2)
);

CREATE TABLE dim_game (
    game_id INT PRIMARY KEY,
    game_name VARCHAR(100),
    genre VARCHAR(50),
    platform VARCHAR(50),
    release_date DATE
);

CREATE TABLE dim_device (
    device_id INT PRIMARY KEY,
    device_type VARCHAR(50), -- mobile, desktop, console
    os VARCHAR(50),
    manufacturer VARCHAR(50)
);
```

---

### Exercise 2: Normalize a Table to 3NF

**Given Table** (Violates normalization):
```
Orders:
order_id | customer_name | customer_email | product_name | category | quantity | price | order_date
```

**Solution**:

```sql
-- Step 1: 1NF - Separate order items
Orders:
order_id | customer_id | order_date

OrderItems:
order_id | product_id | quantity | price

-- Step 2: 2NF - Remove partial dependencies
Customers:
customer_id | customer_name | customer_email

Products:
product_id | product_name | category_id

Categories:
category_id | category_name

-- Step 3: 3NF - Remove transitive dependencies
-- Already in 3NF after step 2

-- Final Normalized Schema:
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100) UNIQUE
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200),
    category_id INT REFERENCES categories(category_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE
);

CREATE TABLE order_items (
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT,
    price DECIMAL(10,2),
    PRIMARY KEY (order_id, product_id)
);
```

---

### Exercise 3: Implement SCD Type 2

**Scenario**: Track customer address changes over time

**Requirements**:
- Preserve full history
- Easy to query current address
- Support point-in-time queries

**Solution**:

```sql
CREATE TABLE dim_customer (
    customer_sk SERIAL PRIMARY KEY,  -- Surrogate key
    customer_id INT NOT NULL,         -- Natural key
    customer_name VARCHAR(100),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    effective_date DATE NOT NULL,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial record
INSERT INTO dim_customer 
(customer_id, customer_name, address, city, state, zip_code, effective_date)
VALUES 
(101, 'John Doe', '123 Main St', 'New York', 'NY', '10001', '2020-01-01');

-- When customer moves (SCD Type 2)
-- Step 1: Expire old record
UPDATE dim_customer 
SET expiry_date = '2023-06-30', is_current = FALSE
WHERE customer_id = 101 AND is_current = TRUE;

-- Step 2: Insert new record
INSERT INTO dim_customer 
(customer_id, customer_name, address, city, state, zip_code, effective_date)
VALUES 
(101, 'John Doe', '456 Oak Ave', 'Los Angeles', 'CA', '90001', '2023-07-01');

-- Query current address
SELECT * FROM dim_customer 
WHERE customer_id = 101 AND is_current = TRUE;

-- Query historical address at specific date
SELECT * FROM dim_customer 
WHERE customer_id = 101 
  AND '2022-06-15' BETWEEN effective_date AND COALESCE(expiry_date, '9999-12-31');
```

---

## ✅ Check Your Understanding

1. **What are the three levels of data models and their purposes?**
2. **Explain the difference between Star Schema and Snowflake Schema.**
3. **What is normalization and what are the first three normal forms?**
4. **When would you use SCD Type 1 vs Type 2?**
5. **What is the difference between a fact table and dimension table?**
6. **When should you normalize vs denormalize?**
7. **Explain the Kimball vs Inmon methodology.**
8. **What is the difference between OLTP and OLAP data modeling?**
9. **How do you determine the grain of a fact table?**
10. **What are the benefits of data modeling?**

---

## 🎯 Next Steps

Once you're comfortable with this topic, we'll move to:
- **Topic 3: Data File Formats** (ORC, Parquet, Avro, JSON, CSV)

**Study Time**: Spend 3-4 days on this topic, practice designing schemas, then let me know when you're ready to move on!

---

## 📚 Additional Resources

### Official Documentation & Guides
- [IBM Data Modeling Guide](https://www.ibm.com/think/topics/data-modeling) - Comprehensive guide on data modeling concepts
- [Kimball Group Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) - Official Kimball methodology resources
- [Ralph Kimball's Data Warehouse Toolkit](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/) - The definitive guide to dimensional modeling

### Online Courses & Tutorials
- **DataCamp**: [Introduction to Data Modeling in Snowflake](https://www.datacamp.com/courses/introduction-to-data-modeling-in-snowflake) - Hands-on exercises for dimensional modeling
- **Microsoft Learn**: [Data Warehouse Labs](https://microsoftlearning.github.io/mslearn-fabric/Instructions/Labs/06-data-warehouse.html) - Practice data warehouse design
- **Coursera**: Data Modeling courses from top universities

### Practice Platforms
- **TestDome**: [Data Warehouse Online Test](https://www.testdome.com/tests/data-warehouse-online-test/210) - Assess your data modeling skills
- **LeetCode**: SQL problems that test normalization and schema design
- **StrataScratch**: Real-world data modeling problems from companies

### Books
- **"The Data Warehouse Toolkit"** by Ralph Kimball - Essential for dimensional modeling
- **"Data Modeling Made Simple"** by Steve Hoberman - Practical guide
- **"Data Modeling Essentials"** by Graeme Simsion - Comprehensive textbook

### Tools for Data Modeling
- **dbdiagram.io** - Free ER diagram tool
- **Lucidchart** - Professional diagramming
- **ER/Studio** - Enterprise data modeling
- **Draw.io** - Free diagramming tool
- **pgAdmin** - PostgreSQL schema design
- **MySQL Workbench** - MySQL schema design

### Interview Preparation
- **InterviewQuery**: [Data Modeling Interview Questions](https://interviewquery.com/learning-paths/data-engineering-interview/dimensional-modeling/) - Practice questions
- **Adaface**: [92 Data Modeling Interview Questions](https://www.adaface.com/blog/data-modeling-interview-questions/) - Comprehensive question bank
- **InterviewKickstart**: [90+ Data Modeling Interview Questions](https://interviewkickstart.com/blogs/interview-questions/data-modeling-interview-questions) - Detailed answers

### Community & Forums
- **Stack Overflow**: Data modeling tag for Q&A
- **Reddit**: r/dataengineering, r/Database
- **Data Engineering Podcast**: Episodes on data modeling

---

**Keep Modeling! 📊**
