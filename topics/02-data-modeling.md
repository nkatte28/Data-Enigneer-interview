# Topic 2: Data Modeling - The Complete Guide

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

### 1. What is Data Modeling? (Simple Explanation)

**Think of it like this**: If you're building a Nike store, you need a blueprint showing:
- Where the shoes go
- Where the apparel goes
- How customers move through the store
- How inventory connects to sales

**Data modeling is the blueprint for your data.**

**Definition**: Data modeling is creating a visual representation of how data is organized and connected in your system.
✔ what data exists
✔ how data is organized
✔ how data elements relate to one another
✔ attributes and structure of each data type

**Real-World Example - Nike Store**:
```
Business Question: "How do we track what Nike products customers buy?"

Data Model Answer:
- Customers table (who buys)
- Products table (what they buy - Air Max, Jordan, etc.)
- Sales table (the transaction - connects customer + product)
- Stores table (where they buy - NYC, LA, etc.)
```

**Key Benefits**:
- ✅ Reduces errors (catch problems before building)
- ✅ Improves performance (organized data = faster queries)
- ✅ Better communication (everyone understands the structure)
- ✅ Easier maintenance (clear structure = easier updates)

---

### 2. Different Levels of Data Models

Data modeling has **three levels**, from abstract (business view) to concrete (database code).

#### 2.1 Conceptual Data Model - "What Does the Business Need?"

conceptual data models define entities and their relationships at a high level.

**Purpose**: High-level business view (WHAT, not HOW)

created as part of the process of gathering requirements, 
Describe what data exists and how entities relate, without technical details.

Audience:
Business stakeholders
Product managers
Architects

Characteristics:
No tables or columns

**Nike Store Example**:

**Business Entities**:
- Customer (people who buy)
- Product (Nike items sold)
- Sale (the transaction)
- Store (where sales happen)

**Business Relationships**:
- A Customer can make many Sales (1:many)
- A Sale contains many Products (many:many)
- A Product can be in many Sales (many:many)
- A Store has many Sales (1:many)

**Business Rules**:
- Every Sale must have at least one Product
- Every Sale must belong to one Customer
  - Customer Email must be unique
In strict modeling, attributes are introduced in the logical model. However, some conceptual models may include high-level business attributes without technical details.

**Key Point**: No technical details - just business concepts!

#### 2.2 Logical Data Model - "How is Data Organized?"

**Purpose**: Detailed structure with generic data types (any database system)

A more detailed model that adds structure and defines attributes and relationships between entities without being tied to any specific database system.

Includes:
Entities
Attributes (fields)
Relationships (with cardinalities)
Rules and constraints
Business definitions

This model describes what will be stored in more detail — but still not how it is stored technically.

**Nike Store Example**:

```sql
-- Generic data types (works with PostgreSQL, MySQL, Oracle, etc.)

Customer Entity:
  - customer_id: Integer, Primary Key
  - first_name: String(50), Required
  - last_name: String(50), Required
  - email: String(100), Unique, Required
  - city: String(50), Optional
  - registration_date: DateTime, Required

Product Entity:
  - product_id: Integer, Primary Key
  - product_name: String(200), Required
  - category: String(50), Required  -- Running, Basketball, Apparel
  - brand_line: String(50), Required  -- Air Max, Jordan, Dri-FIT
  - price: Decimal(10,2), Required
  - color: String(30), Optional

Sale Entity:
  - sale_id: Integer, Primary Key
  - customer_id: Integer, Foreign Key -> Customer.customer_id
  - store_id: Integer, Foreign Key -> Store.store_id
  - sale_date: DateTime, Required
  - total_amount: Decimal(10,2), Required

SaleItem Entity (for many-to-many):
  - sale_id: Integer, Foreign Key -> Sale.sale_id
  - product_id: Integer, Foreign Key -> Product.product_id
  - quantity: Integer, Required
  - unit_price: Decimal(10,2), Required
```

**Key Point**: Uses generic types (Integer, String, DateTime) - not specific to any database!

#### 2.3 Physical Data Model - "How is it Stored in PostgreSQL/MySQL?"

**Purpose**: DBMS-specific implementation with performance optimizations
The most concrete level; a database-specific design ready to be implemented.

Includes:
Table definitions
Primary keys and foreign keys
Data types (e.g., INT, VARCHAR)
Indexes, constraints
Storage decisions

**Nike Store Example - PostgreSQL**:

```sql
-- PostgreSQL-specific syntax

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,  -- SERIAL = PostgreSQL auto-increment
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    city VARCHAR(50),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Performance indexes
    INDEX idx_customer_email (email),
    INDEX idx_customer_city (city)
) PARTITION BY RANGE (registration_date);  -- Partitioning for performance

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    brand_line VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    color VARCHAR(30),
    INDEX idx_product_category (category),
    INDEX idx_product_brand (brand_line)
);

CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    store_id INTEGER NOT NULL REFERENCES stores(store_id),
    sale_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    INDEX idx_sale_customer (customer_id),
    INDEX idx_sale_date (sale_date),
    INDEX idx_sale_store (store_id)
) PARTITION BY RANGE (sale_date);
```

**Key Differences**:
- ✅ Uses `SERIAL` (PostgreSQL-specific)
- ✅ Includes indexes for performance
- ✅ Includes partitioning strategy
- ✅ Includes constraints (CHECK, NOT NULL)

**Comparison Table**:

| Aspect | Conceptual | Logical | Physical |
|--------|------------|---------|----------|
| **Focus** | Business concepts | Data structure | Database implementation |
| **Language** | Business terms | Generic technical | DBMS-specific syntax |
| **Data Types** | None | Generic (INT, VARCHAR) | Specific (SERIAL, TIMESTAMP) |
| **Example** | "Customer has Name" | `customer_id: Integer` | `customer_id SERIAL PRIMARY KEY` |

---

### 3. Facts and Dimensions: The Foundation for Analytics (Nike Store Example)

> **Note**: Facts and Dimensions are the foundation of **dimensional modeling (OLAP/analytics)**. We'll cover **normalized modeling (OLTP/transactions)** in the next section. Understanding both approaches helps you choose the right model for your use case.

**The Simplest Way to Understand**:

Think of a **sales receipt at a Nike store**:
- **Facts** = The numbers on the receipt (what happened)
- **Dimensions** = The context around those numbers (who, what, when, where)

#### Facts (Fact Tables) - "What Happened?"

**Facts are measurable, numeric events.**

**Nike Store Example**:
```
Sale Receipt:
- Sale Amount: $150
- Quantity: 2 pairs
- Discount: $20
- Profit: $80
```

**Characteristics**:
- ✅ Numbers you can add, count, or average
- ✅ Usually MANY rows (millions of sales)
- ✅ Change frequently (new sales every day)
- ✅ Examples: sales amount, quantity sold, profit, revenue

#### Dimensions (Dimension Tables) - "Who/What/When/Where?"

**Dimensions provide context about the facts.**

**Nike Store Example**:
```
Sale Receipt Context:
- Customer: Sarah Johnson (who)
- Product: Air Max 270 (what)
- Date: January 15, 2024 (when)
- Store: Nike Store NYC (where)
- Salesperson: Mike Chen (who sold it)
```

**Characteristics**:
- ✅ Descriptive attributes (text, categories)
- ✅ Usually FEWER rows (thousands of customers, not millions)
- ✅ Change less frequently
- ✅ Examples: customer name, product name, store location, date

#### Complete Nike Store Example

**Fact Table: `sales_fact`** (The Numbers)
| sale_id | customer_id | product_id | date_id | store_id | amount | quantity | profit |
|---------|-------------|------------|---------|----------|--------|----------|--------|
| 1 | 101 | 501 | 20240115 | 1 | $150 | 2 | $80 |
| 2 | 102 | 502 | 20240115 | 2 | $200 | 1 | $100 |
| 3 | 101 | 503 | 20240116 | 1 | $120 | 1 | $60 |

**Facts**: `amount`, `quantity`, `profit` ← These are the numbers!

**Dimension Table: `customer_dim`** (Who)
| customer_id | name | age | city | country | customer_segment |
|-------------|------|-----|------|---------|------------------|
| 101 | Sarah Johnson | 28 | New York | USA | Premium |
| 102 | Mike Chen | 35 | Los Angeles | USA | Regular |

**Dimension Table: `product_dim`** (What)
| product_id | product_name | category | brand_line | price | color |
|------------|---------------|----------|------------|-------|-------|
| 501 | Air Max 270 | Running Shoes | Air Max | $150 | Black/White |
| 502 | Jordan 1 Retro | Basketball | Jordan | $200 | Red/Black |
| 503 | Dri-FIT T-Shirt | Apparel | Performance | $120 | Blue |

**Dimension Table: `store_dim`** (Where)
| store_id | store_name | city | state | country | store_type |
|----------|------------|------|-------|---------|------------|
| 1 | Nike Store NYC | New York | NY | USA | Flagship |
| 2 | Nike Store LA | Los Angeles | CA | USA | Standard |

**Dimension Table: `date_dim`** (When)
| date_id | date | day | month | year | quarter | day_of_week |
|---------|------|-----|-------|------|---------|-------------|
| 20240115 | 2024-01-15 | 15 | January | 2024 | Q1 | Monday |
| 20240116 | 2024-01-16 | 16 | January | 2024 | Q1 | Tuesday |

#### Why This Structure Works

**Query Example**: "What's the total sales by customer city?"
```sql
SELECT 
    c.city,
    SUM(f.amount) as total_sales
FROM sales_fact f
JOIN customer_dim c ON f.customer_id = c.customer_id
GROUP BY c.city
```

**Result**:
| city | total_sales |
|------|-------------|
| New York | $270 |
| Los Angeles | $200 |

**Why it's fast**: Small dimension table (few cities) joined to fact table, then aggregated.

**Memory Trick**:
- **Facts** = "What happened?" → Numbers, metrics, measurements
- **Dimensions** = "Who/What/When/Where?" → Descriptions, attributes, context

---

### 4. Normalization: Organizing Data Efficiently
Normalization is the process of organizing data

✅ Reduce redundancy (duplicate data)
✅ Improve data integrity
✅ Avoid update anomalies
✅ Maintain consistency

**The Problem**: Without normalization, data gets messy and redundant.

**Nike Store Example - Before Normalization**:

```
Bad Table (Everything in one place):
sale_id | customer_name | customer_email | product_name | category | quantity | price | sale_date
--------|---------------|----------------|--------------|----------|----------|-------|-----------
1       | Sarah Johnson | sarah@email.com| Air Max 270  | Running  | 2        | $150  | 2024-01-15
1       | Sarah Johnson | sarah@email.com| Dri-FIT Shirt| Apparel  | 1        | $30   | 2024-01-15
2       | Mike Chen     | mike@email.com | Jordan 1     | Basketball| 1       | $200  | 2024-01-16
```

**Problems**:
- ❌ Customer info repeated (Sarah appears twice)
- ❌ Product info repeated (if Air Max 270 sold 1000 times, name appears 1000 times)
- ❌ Hard to update (change customer email? Update 1000 rows!)
- ❌ Wastes storage space

**Solution**: Normalize into separate tables!

#### First Normal Form (1NF) - Atomic Values

**Rule**: Each column must contain atomic (indivisible) values. No repeating groups(in a column).

**Nike Store Example - Violating 1NF**:

```
Bad:
sale_id | customer_id | products
--------|------------|------------------
1       | 101        | Air Max 270, Dri-FIT Shirt
2       | 102        | Jordan 1, Socks
```

**Problem**: `products` column has multiple values!

**Fixed (1NF)**:

```
Sales Table:
sale_id | customer_id | sale_date
--------|-------------|-----------
1       | 101         | 2024-01-15
2       | 102         | 2024-01-16

SaleItems Table:
sale_id | product_name
--------|-------------
1       | Air Max 270
1       | Dri-FIT Shirt
2       | Jordan 1
2       | Socks
```

**Key Point**: One fact per row!

#### Second Normal Form (2NF) - No Partial Dependencies

**Rule**: Must be in 1NF + 
all non-key attributes fully depend on primary key + 
Relationship between tables should be formed using FK

**Nike Store Example - Violating 2NF**:

```
SaleItems Table:
sale_id | product_id | product_name | category | quantity | price
--------|------------|--------------|----------|----------|-------
1       | 501        | Air Max 270  | Running  | 2        | $150
1       | 502        | Dri-FIT Shirt| Apparel  | 1        | $30
```

**Problem**: `product_name` and `category` depend on `product_id`, NOT on `sale_id`!

**Fixed (2NF)**:

```
SaleItems Table:
sale_id | product_id | quantity | unit_price
--------|------------|----------|------------
1       | 501        | 2        | $150
1       | 502        | 1        | $30

Products Table:
product_id | product_name | category
-----------|--------------|----------
501        | Air Max 270  | Running
502        | Dri-FIT Shirt| Apparel
```

**Key Point**: Product details belong in Products table, not SaleItems!

#### Third Normal Form (3NF) - No Transitive Dependencies

**Rule**: Must be in 2NF + no non-key attribute depends on another non-key attribute(Avoid Transitive dependency A = B = C so A = C).

**Nike Store Example - Violating 3NF**:

```
Customers Table:
customer_id | name | city | state | zip_code | state_tax_rate
------------|------|------|-------|----------|---------------
101         | Sarah| NYC  | NY    | 10001    | 0.08
102         | Mike | LA   | CA    | 90001    | 0.10
```

**Problem**: `state_tax_rate` depends on `state`, NOT on `customer_id`!

**Fixed (3NF)**:

```
Customers Table:
customer_id | name | city | zip_code | state_id
------------|------|------|-----------|----------
101         | Sarah| NYC  | 10001    | NY
102         | Mike | LA   | 90001    | CA

States Table:
state_id | state_name | tax_rate
---------|------------|----------
NY       | New York   | 0.08
CA       | California | 0.10
```

**Key Point**: Tax rate belongs in States table, not Customers!

#### Complete Normalized Nike Store Schema (3NF)

```sql
-- Customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    city VARCHAR(50),
    state_id VARCHAR(2) REFERENCES states(state_id),
    zip_code VARCHAR(10),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- States
CREATE TABLE states (
    state_id VARCHAR(2) PRIMARY KEY,
    state_name VARCHAR(50) NOT NULL,
    tax_rate DECIMAL(5,4) NOT NULL
);

-- Products
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INT REFERENCES categories(category_id),
    brand_line_id INT REFERENCES brand_lines(brand_line_id),
    price DECIMAL(10,2) NOT NULL,
    color VARCHAR(30)
);

-- Categories
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL  -- Running, Basketball, Apparel
);

-- Brand Lines
CREATE TABLE brand_lines (
    brand_line_id SERIAL PRIMARY KEY,
    brand_line_name VARCHAR(50) NOT NULL  -- Air Max, Jordan, Dri-FIT
);

-- Stores
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    state_id VARCHAR(2) REFERENCES states(state_id),
    store_type VARCHAR(20)  -- Flagship, Standard, Outlet
);

-- Sales
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    store_id INT REFERENCES stores(store_id),
    sale_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL
);

-- Sale Items
CREATE TABLE sale_items (
    sale_id INT REFERENCES sales(sale_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (sale_id, product_id)
);
```

**Benefits of Normalization**:
- ✅ No data redundancy (customer info stored once)
- ✅ Easy to update (change product name? One row!)
- ✅ Data consistency (no conflicting information)
- ✅ Saves storage space

**Trade-offs**:
- ❌ More tables = more joins (can be slower for analytics)
- ❌ More complex queries

---

### 5. Denormalization: When to Break the Rules

**The Problem**: Normalized data is great for transactions, but slow for analytics!

**Nike Store Analytics Query (Normalized)**:
```sql
-- To get "Total sales by customer city", need 2 joins!
SELECT 
    c.city,
    SUM(si.quantity * si.unit_price) as total_sales
FROM sale_items si
JOIN sales s ON si.sale_id = s.sale_id
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.city;
```

**This is SLOW** with millions of rows!

**Solution**: Denormalize for analytics (data warehouse)!

#### Denormalized Star Schema for Analytics

**Fact Table: `fact_sales`** (Denormalized for speed)
```sql
CREATE TABLE fact_sales (
    sale_id BIGINT PRIMARY KEY,
    -- Foreign Keys
    date_id INT,
    customer_id INT,
    product_id INT,
    store_id INT,
    -- Measures (the numbers)
    quantity INT,
    revenue DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    profit DECIMAL(10,2),
    -- Denormalized attributes (for faster queries)
    customer_city VARCHAR(50),      -- Denormalized from customer_dim
    product_category VARCHAR(50),  -- Denormalized from product_dim
    store_city VARCHAR(50)          -- Denormalized from store_dim
);
```

**Now the same query is FAST**:
```sql
-- No joins needed! Everything in one table!
SELECT 
    customer_city,
    SUM(revenue) as total_sales
FROM fact_sales
GROUP BY customer_city;
```

**When to Denormalize**:
- ✅ Analytics/OLAP systems (read-heavy)
- ✅ Data warehouses (not transactional systems)
- ✅ When joins are expensive
- ✅ When storage is cheap

**When to Normalize**:
- ✅ Transactional/OLTP systems (write-heavy)
- ✅ When data integrity is critical
- ✅ When storage is expensive
- ✅ When updates are frequent

---

### 6. Star Schema: The Analytics Powerhouse

**Structure**: Central fact table surrounded by dimension tables (like a star ⭐)

A dimensional model where:
One central Fact table
Connected directly to multiple Denormalized Dimension tables

**Nike Store Star Schema**:

```
        [Date Dimension]
              |
              |
[Product]--[Sales Fact]--[Customer]
              |
              |
        [Store Dimension]
```

#### Fact Table: `fact_sales`

```sql
CREATE TABLE fact_sales (
    sale_id BIGINT PRIMARY KEY,
    -- Foreign Keys (point to dimensions)
    date_id INT NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    -- Measures (the numbers we analyze)
    quantity INT NOT NULL,
    revenue DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    profit DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL
);
```

**Sample Data**:
| sale_id | date_id | customer_id | product_id | store_id | quantity | revenue | profit |
|---------|---------|-------------|------------|----------|----------|---------|--------|
| 1 | 20240115 | 101 | 501 | 1 | 2 | $300 | $160 |
| 2 | 20240115 | 102 | 502 | 2 | 1 | $200 | $100 |
| 3 | 20240116 | 101 | 503 | 1 | 1 | $120 | $60 |

#### Dimension Tables

**Date Dimension**:
```sql
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date_value DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20),
    day INT NOT NULL,
    day_of_week VARCHAR(10),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);
```

**Sample Data**:
| date_id | date_value | year | quarter | month | month_name | day | day_of_week | is_weekend |
|---------|------------|------|---------|-------|------------|-----|-------------|------------|
| 20240115 | 2024-01-15 | 2024 | 1 | 1 | January | 15 | Monday | false |
| 20240116 | 2024-01-16 | 2024 | 1 | 1 | January | 16 | Tuesday | false |

**Customer Dimension**:
```sql
CREATE TABLE dim_customer (
    customer_sk SERIAL PRIMARY KEY,  -- Surrogate key
    customer_id INT NOT NULL,        -- Natural key
    customer_name VARCHAR(100),
    age INT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    customer_segment VARCHAR(20),  -- Premium, Regular, Casual
    registration_date DATE
);
```

**Sample Data**:
| customer_sk | customer_id | customer_name | city | state | customer_segment |
|--------------|-------------|---------------|------|-------|------------------|
| 1 | 101 | Sarah Johnson | New York | NY | Premium |
| 2 | 102 | Mike Chen | Los Angeles | CA | Regular |

**Product Dimension**:
```sql
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),      -- Running, Basketball, Apparel
    brand_line VARCHAR(50),    -- Air Max, Jordan, Dri-FIT
    color VARCHAR(30),
    size VARCHAR(10),
    price DECIMAL(10,2),
    cost DECIMAL(10,2)
);
```

**Sample Data**:
| product_id | product_name | category | brand_line | color | price |
|------------|--------------|----------|------------|-------|-------|
| 501 | Air Max 270 | Running | Air Max | Black/White | $150 |
| 502 | Jordan 1 Retro | Basketball | Jordan | Red/Black | $200 |
| 503 | Dri-FIT T-Shirt | Apparel | Dri-FIT | Blue | $120 |

**Store Dimension**:
```sql
CREATE TABLE dim_store (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    store_type VARCHAR(20),  -- Flagship, Standard, Outlet
    store_size_sqft INT,
    opening_date DATE
);
```

**Sample Data**:
| store_id | store_name | city | state | store_type |
|----------|------------|------|-------|------------|
| 1 | Nike Store NYC | New York | NY | Flagship |
| 2 | Nike Store LA | Los Angeles | CA | Standard |

#### Star Schema Query Examples

**Query 1**: "Total revenue by customer city"
```sql
SELECT 
    c.city,
    SUM(f.revenue) as total_revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.city
ORDER BY total_revenue DESC;
```

**Result**:
| city | total_revenue |
|------|--------------|
| New York | $420 |
| Los Angeles | $200 |

**Query 2**: "Sales by product category and month"
```sql
SELECT 
    d.month_name,
    p.category,
    SUM(f.quantity) as total_quantity,
    SUM(f.revenue) as total_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY d.month_name, p.category
ORDER BY d.month_name, p.category;
```

**Query 3**: "Top 10 customers by revenue"
```sql
SELECT 
    c.customer_name,
    c.city,
    SUM(f.revenue) as total_revenue,
    SUM(f.quantity) as total_items
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_name, c.city
ORDER BY total_revenue DESC
LIMIT 10;
```

**Star Schema Benefits**:
- ✅ Simple to understand (business users love it!)
- ✅ Fast queries (fewer joins)
- ✅ Easy to add new dimensions
- ✅ Optimized for analytics

**Star Schema Drawbacks**:
- ❌ Data redundancy in dimensions
- ❌ More storage space
- ❌ Harder to maintain consistency

---

### 7. Snowflake Schema: Normalized Dimensions

**Structure**: Normalized star schema (dimensions reference other dimensions)

A dimensional model where:
Fact table in center
Dimensions are normalized into multiple related tables

**Nike Store Snowflake Schema**:

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
[Product]--[Sales Fact]--[Customer]
          |                |
          |             [City]
          |                |
       [Category]       [State]
                            |
                         [Country]
```

**Key Difference**: Dimensions are normalized (broken into smaller tables)

#### Snowflake Example: Date Dimension

**Star Schema** (Denormalized):
```sql
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date_value DATE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    day INT,
    day_of_week VARCHAR(10)
);
```

**Snowflake Schema** (Normalized):
```sql
-- Date (lowest level)
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date_value DATE,
    day INT,
    day_of_week VARCHAR(10),
    month_id INT REFERENCES dim_month(month_id)
);

-- Month
CREATE TABLE dim_month (
    month_id INT PRIMARY KEY,
    month_number INT,
    month_name VARCHAR(20),
    quarter_id INT REFERENCES dim_quarter(quarter_id)
);

-- Quarter
CREATE TABLE dim_quarter (
    quarter_id INT PRIMARY KEY,
    quarter_number INT,
    quarter_name VARCHAR(10),
    year_id INT REFERENCES dim_year(year_id)
);

-- Year
CREATE TABLE dim_year (
    year_id INT PRIMARY KEY,
    year_value INT
);
```

#### Snowflake Example: Customer Dimension

**Star Schema** (Denormalized):
```sql
CREATE TABLE dim_customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50)
);
```

**Snowflake Schema** (Normalized):
```sql
-- Customer
CREATE TABLE dim_customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city_id INT REFERENCES dim_city(city_id)
);

-- City
CREATE TABLE dim_city (
    city_id INT PRIMARY KEY,
    city_name VARCHAR(50),
    state_id INT REFERENCES dim_state(state_id)
);

-- State
CREATE TABLE dim_state (
    state_id INT PRIMARY KEY,
    state_name VARCHAR(50),
    country_id INT REFERENCES dim_country(country_id)
);

-- Country
CREATE TABLE dim_country (
    country_id INT PRIMARY KEY,
    country_name VARCHAR(50)
);
```

#### Snowflake Query Example

**Query**: "Total revenue by country"
```sql
-- More joins needed!
SELECT 
    co.country_name,
    SUM(f.revenue) as total_revenue
FROM fact_sales f
JOIN dim_customer cu ON f.customer_id = cu.customer_id
JOIN dim_city ci ON cu.city_id = ci.city_id
JOIN dim_state st ON ci.state_id = st.state_id
JOIN dim_country co ON st.country_id = co.country_id
GROUP BY co.country_name;
```

**Snowflake Benefits**:
- ✅ Less storage (normalized = no redundancy)
- ✅ Easier to maintain (update country name? One row!)
- ✅ Better data integrity

**Snowflake Drawbacks**:
- ❌ More complex queries (more joins)
- ❌ Slower performance (more joins = slower)
- ❌ Harder for business users to understand

**When to Use Snowflake**:
- ✅ Large dimension tables (millions of rows)
- ✅ Storage is a concern
- ✅ Dimension data changes frequently
- ✅ When normalization benefits outweigh performance cost

**When to Use Star**:
- ✅ Most analytics use cases (default choice!)
- ✅ When query performance is priority
- ✅ When dimensions are small to medium
- ✅ When business users need simple queries


---

### Diffrent types of Data Models:

<img width="814" height="364" alt="Screenshot 2026-02-26 at 16 18 34" src="https://github.com/user-attachments/assets/1f61497d-cbe7-48e0-83ca-407d9c019cb3" />

A) Structural Models (older database theory)
Hierarchical
Network
Relational

B) Design / Analytical Models
ER model
Dimensional model
Data Vault

**Hierarchical Model**
<img width="1043" height="552" alt="Screenshot 2026-02-26 at 16 15 36" src="https://github.com/user-attachments/assets/df023e26-9998-49db-98c7-bf70282fc3b5" />

Structure:

Tree-like (parent → child)
One-to-many relationships
Each child has only one parent

**Example**:
Company
→ Department
→ Employee
![Uploading HDM.svg…]()

Used in:
Early mainframe systems
IBM IMS

**Limitation**:
Difficult to represent many-to-many relationships


**Entity–Relationship (ER) Model**
<img width="1024" height="528" alt="Screenshot 2026-02-26 at 16 16 38" src="https://github.com/user-attachments/assets/fca3f396-5019-4a57-9196-73a92d6b7206" />


Entities
Attributes
Relationships
Cardinality (1:1, 1:N, M:N)

Used during:
Database design phase
System architecture planning

Important:
ER model is not a storage model, it’s a design model.

**Dimensional Model (Kimball)**
Structure:
Fact tables
Dimension tables
Optimized for analytics

Used in:
Data warehouses
BI systems
Reporting

---

### 8. Slowly Changing Dimensions (SCD): Handling Changes Over Time

It’s a technique used in dimensional models (Star/Snowflake) to handle changes in dimension attributes over time.

**The Problem**: What happens when dimension data changes?

**Nike Store Example**:
- Customer Sarah moves from NYC to LA
- Product "Air Max 270" price changes from $150 to $140
- Store "Nike NYC" changes from Standard to Flagship

**Question**: Do we overwrite the old value? Keep history? How?

#### SCD Type 0: Fixed/Static (Never Changes)

**Behavior**: Dimension never changes, even if source data changes.

**Use Case**: Historical data that should never change.

**Nike Store Example**:
```sql
-- Customer's original registration date
customer_id | registration_date
------------|------------------
101         | 2020-01-15  -- Never changes, even if customer updates profile
```

#### SCD Type 1: Overwrite (Lose History)

**Behavior**: Old value is overwritten with new value. History is lost.

📘 Concept
When a change happens:
Just update the record.
No historical tracking.
Old data is lost.

**Nike Store Example**:

**Before**:
```
customer_id | name | city
------------|------|------
101         | Sarah| NYC
```

**After customer moves to LA**:
```
customer_id | name | city
------------|------|------
101         | Sarah| LA   -- NYC is gone!
```

**Use Case**:
- ✅ Corrections to errors
- ✅ When history is not important
- ✅ Simple dimensions

**Pros**: Simple, no history tracking needed  
**Cons**: Loses historical data (can't answer "Where did Sarah live in 2023?")

🧠 When to Use Type 1
Use when:
History doesn’t matter.
Correction of typo (wrong email, spelling mistake).
Non-analytical attributes.

Example:
Fixing customer email
Updating phone number

#### SCD Type 2: Add New Row (Preserve History) - MOST COMMON - Full History

**Behavior**: Create new row with new values, keep old row. Full history preserved.

📘 Concept
Instead of updating the row:
Close old record
Insert new record
Track time validity

We add:
Surrogate Key
Start Date
End Date
Current Flag

**Nike Store Example**:

**Before**:
```
customer_sk | customer_id | name | city | effective_date | expiry_date | is_current
------------|-------------|------|------|----------------|-------------|------------
1           | 101         | Sarah| NYC  | 2020-01-01     | NULL        | Y
```

**After customer moves to LA (July 1, 2023)**:
```
customer_sk | customer_id | name | city | effective_date | expiry_date | is_current
------------|-------------|------|------|----------------|-------------|------------
1           | 101         | Sarah| NYC  | 2020-01-01     | 2023-06-30  | N
2           | 101         | Sarah| LA   | 2023-07-01     | NULL        | Y
```

**Key Columns**:
- `customer_sk`: Surrogate key (unique for each version)
- `customer_id`: Natural key (same for all versions)
- `effective_date`: When this version became active
- `expiry_date`: When this version expired (NULL = current)
- `is_current`: Flag for current version (Y/N)

**Use Case**: 
- ✅ When history is important (MOST COMMON!)
- ✅ Audit requirements
- ✅ Point-in-time analysis

**Query Current Address**:
```sql
SELECT * FROM dim_customer 
WHERE customer_id = 101 AND is_current = TRUE;
```

**Query Historical Address**:
```sql
-- Where did Sarah live on June 15, 2023?
SELECT * FROM dim_customer 
WHERE customer_id = 101 
  AND '2023-06-15' BETWEEN effective_date AND COALESCE(expiry_date, '9999-12-31');
```

**Pros**: Complete history preserved
**Cons**: More storage, more complex queries

#### SCD Type 3: Add New Column (Store Previous Value)

**Behavior**: Add column to store previous value. Only one previous value kept.

📘 Concept
Instead of new rows,
We add extra columns to store previous value.

**Nike Store Example**:

**Before**:
```
customer_id | name | city
------------|------|------
101         | Sarah| NYC
```

**After customer moves to LA**:
```
customer_id | name | current_city | previous_city
------------|------|--------------|--------------
101         | Sarah| LA           | NYC
```

**Use Case**:
- ✅ Limited history needed (only previous value)
- ✅ When only one change is tracked

**Pros**: Simple, preserves one previous value
**Cons**: Limited history (only one previous value)

#### SCD Type 4: History Table (Separate Table)

**Behavior**: Current values in main table, history in separate table.

**Nike Store Example**:

**Current Table**:
```
customer_id | name | city
------------|------|------
101         | Sarah| LA
```

**History Table**:
```
customer_id | city | effective_date | expiry_date
------------|------|----------------|-------------
101         | NYC  | 2020-01-01     | 2023-06-30
101         | LA   | 2023-07-01     | NULL
```

**Use Case**:
- ✅ Clean separation needed
- ✅ Keeps main dimension table small and clean
- ✅ Faster queries for “current state” reporting/lookups
- ✅ History is stored separately for deep audits

**Pros**: Clean separation, fast current lookups
**Cons**: Requires joins for history

In heavily audited systems:
Banking
Healthcare
Regulatory compliance
Sometimes history is rarely queried but must be preserved.

#### SCD Type 5: Mini-Dimension (Separate Changing Attributes) - Type 1 + Type 4 Hybrid

**Behavior**: Separate table for frequently changing attributes. The changing attributes table uses SCD Type 2 style (with time tracking), while static attributes stay in the main table.

📘 Concept
Maintain a current dimension table (Type 1 style)
Maintain a separate historical table (Type 4)
But also allow fact table to join current attributes directly
So:
Current attributes always reflect latest values
Historical deep dive available separately

**Nike Store Example**:

**Customer (Static)** - rarely changes:
```
customer_id | name | birth_date
------------|------|------------
101         | Sarah| 1995-05-20
```

**Customer Demographics (Changing)** - frequently changes, with time tracking:
```
customer_id | age_group | income_range | effective_date | expiry_date | is_current
------------|-----------|--------------|----------------|-------------|------------
101         | 25-30     | $50k-$75k    | 2020-01-01     | 2022-12-31  | N
101         | 28-33     | $75k-$100k   | 2023-01-01     | NULL        | Y
```

**Key Points**:
- ✅ Tables are related by `customer_id`
- ✅ Changing attributes table tracks history (effective_date, expiry_date, is_current)
- ✅ Static attributes don't need history tracking
- ✅ SCD Type 5 = SCD Type 2 for changing attributes only

**Query Example** - Get customer with current demographics:
```sql
SELECT 
    c.customer_id,
    c.name,
    c.birth_date,
    cd.age_group,
    cd.income_range
FROM customer c
JOIN customer_demographics cd ON c.customer_id = cd.customer_id
WHERE cd.is_current = TRUE;
```

**Query Example** - Get customer demographics at a specific date:
```sql
SELECT 
    c.customer_id,
    c.name,
    cd.age_group,
    cd.income_range
FROM customer c
JOIN customer_demographics cd ON c.customer_id = cd.customer_id
WHERE c.customer_id = 101
  AND '2021-06-15' BETWEEN cd.effective_date AND COALESCE(cd.expiry_date, '9999-12-31');
```

**Use Case**: 
- ✅ Some attributes change frequently (age, income, customer_segment)
- ✅ Others change rarely (name, birth date, registration_date)
- ✅ Want to avoid Type 2 overhead for static attributes

#### SCD Type 6: Hybrid (Combination)

**Behavior**: Combination of Type 1, 2, and 3.

**Nike Store Example**:
```
customer_sk | customer_id | name | current_city | previous_city | effective_date | is_current
------------|-------------|------|--------------|---------------|----------------|------------
1           | 101         | Sarah| LA           | NYC           | 2023-07-01     | Y
```

**Has**:
- Type 1: Overwrites some attributes
- Type 2: Adds new row with effective_date
- Type 3: Stores previous_city

**Use Case**:
- ✅ Different attributes need different SCD types
- ✅ Complex requirements

---

### 9. Complete Nike Store Data Model Example

#### OLTP Model (Normalized - For Transactions)

**Purpose**: Handle daily sales transactions

```sql
-- Customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50),
    state_id VARCHAR(2) REFERENCES states(state_id),
    zip_code VARCHAR(10),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INT REFERENCES categories(category_id),
    brand_line_id INT REFERENCES brand_lines(brand_line_id),
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    color VARCHAR(30),
    size VARCHAR(10),
    stock_quantity INT DEFAULT 0
);

-- Categories
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL  -- Running, Basketball, Apparel
);

-- Brand Lines
CREATE TABLE brand_lines (
    brand_line_id SERIAL PRIMARY KEY,
    brand_line_name VARCHAR(50) NOT NULL  -- Air Max, Jordan, Dri-FIT
);

-- Stores
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    address VARCHAR(200),
    city VARCHAR(50),
    state_id VARCHAR(2) REFERENCES states(state_id),
    zip_code VARCHAR(10),
    store_type VARCHAR(20),  -- Flagship, Standard, Outlet
    phone VARCHAR(20)
);

-- Sales
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    store_id INT REFERENCES stores(store_id),
    sale_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    payment_method VARCHAR(20)  -- Cash, Credit, Debit
);

-- Sale Items
CREATE TABLE sale_items (
    sale_id INT REFERENCES sales(sale_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    PRIMARY KEY (sale_id, product_id)
);
```

#### OLAP Model (Star Schema - For Analytics)

**Purpose**: Fast analytics and reporting

```sql
-- Fact Table
CREATE TABLE fact_sales (
    sale_id BIGINT PRIMARY KEY,
    -- Foreign Keys
    date_id INT NOT NULL REFERENCES dim_date(date_id),
    customer_id INT NOT NULL REFERENCES dim_customer(customer_id),
    product_id INT NOT NULL REFERENCES dim_product(product_id),
    store_id INT NOT NULL REFERENCES dim_store(store_id),
    -- Measures
    quantity INT NOT NULL,
    revenue DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    cost DECIMAL(10,2) NOT NULL,
    profit DECIMAL(10,2) NOT NULL
);

-- Date Dimension
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date_value DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20),
    day INT NOT NULL,
    day_of_week VARCHAR(10),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- Customer Dimension (SCD Type 2)
CREATE TABLE dim_customer (
    customer_sk SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    customer_name VARCHAR(100),
    age INT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    customer_segment VARCHAR(20),
    effective_date DATE NOT NULL,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE
);

-- Product Dimension
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    brand_line VARCHAR(50),
    color VARCHAR(30),
    size VARCHAR(10),
    price DECIMAL(10,2),
    cost DECIMAL(10,2)
);

-- Store Dimension
CREATE TABLE dim_store (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    store_type VARCHAR(20),
    store_size_sqft INT
);
```

---

### 10. Data Modeling Best Practices

#### 1. Choose the Right Model for the Use Case

**OLTP (Transactions)** → Normalized (3NF)
- ✅ Fast writes
- ✅ Data integrity
- ✅ No redundancy

**OLAP (Analytics)** → Star/Snowflake Schema
- ✅ Fast reads
- ✅ Simple queries
- ✅ Optimized for aggregations

#### 2. Design Fact Tables Carefully

**Grain (Level of Detail)**:
- ✅ One row per sale (transaction grain)
- ✅ One row per day per product (daily grain)
- ❌ Don't mix grains!

**Measures**:
- ✅ Additive: Can be summed (revenue, quantity)
- ✅ Semi-additive: Can be summed in some dimensions (bank balance)
- ✅ Non-additive: Cannot be summed (ratios, percentages)

#### 3. Design Dimension Tables Thoughtfully

**Surrogate Keys**:
- ✅ Use surrogate keys (auto-increment) for dimensions
- ✅ Natural keys can change (customer email)
- ✅ Surrogate keys never change

**SCD Strategy**:
- ✅ Most dimensions: SCD Type 2 (preserve history)
- ✅ Reference data: SCD Type 1 (overwrite)
- ✅ Rarely changing: SCD Type 0 (fixed)

#### 4. Performance Considerations

**Indexes**:
- ✅ Index foreign keys in fact tables
- ✅ Index dimension keys
- ✅ Index frequently filtered columns

**Partitioning**:
- ✅ Partition fact tables by date
- ✅ Improves query performance
- ✅ Easier data management

---

## 💡 Interview Questions & Answers

### Q1: Explain the difference between Star Schema and Snowflake Schema

**Answer**:

**Star Schema**:
- Denormalized dimensions (all attributes in one table)
- Single level of dimensions
- Faster queries (fewer joins)
- More storage (data redundancy)
- Easier to understand

**Snowflake Schema**:
- Normalized dimensions (broken into multiple tables)
- Hierarchical dimensions
- More joins (slower queries)
- Less storage (normalized)
- More complex

**Nike Store Example**:

**Star Schema**:
```sql
-- One table with all date info
dim_date: date_id, date, year, quarter, month, day

-- Query: 1 join
SELECT d.year, SUM(f.revenue)
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year;
```

**Snowflake Schema**:
```sql
-- Multiple tables
dim_date: date_id, date, day, month_id
dim_month: month_id, month, quarter_id
dim_quarter: quarter_id, quarter, year_id
dim_year: year_id, year

-- Query: 4 joins!
SELECT y.year, SUM(f.revenue)
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_month m ON d.month_id = m.month_id
JOIN dim_quarter q ON m.quarter_id = q.quarter_id
JOIN dim_year y ON q.year_id = y.year_id
GROUP BY y.year;
```

**When to Use**:
- **Star**: Most analytics (default choice!)
- **Snowflake**: Large dimensions, storage concern

---

### Q2: What is normalization and why is it important?

**Answer**:

**Normalization**: Organizing data to reduce redundancy and improve integrity.

**Normal Forms**:
1. **1NF**: Atomic values, no repeating groups
2. **2NF**: No partial dependencies
3. **3NF**: No transitive dependencies

**Nike Store Example - Before Normalization**:
```
Bad Table:
sale_id | customer_name | customer_email | product_name | price
--------|---------------|----------------|--------------|-------
1       | Sarah         | sarah@email.com| Air Max 270  | $150
1       | Sarah         | sarah@email.com| Dri-FIT Shirt| $30
```

**Problems**:
- ❌ Customer info repeated
- ❌ Product info repeated
- ❌ Hard to update

**After Normalization (3NF)**:
```
Customers: customer_id, name, email
Products: product_id, name, price
Sales: sale_id, customer_id, date
SaleItems: sale_id, product_id, quantity
```

**Benefits**:
- ✅ No redundancy
- ✅ Easy to update
- ✅ Data consistency
- ✅ Saves storage

**Trade-offs**:
- ❌ More tables = more joins
- ❌ Can be slower for analytics

---

### Q3: Explain SCD Type 2 (Most Important!)

**Answer**:

**SCD Type 2**: Add new row when dimension changes. Preserves full history.

**Nike Store Example**:

**Customer moves from NYC to LA**:

**Before**:
```
customer_sk | customer_id | name | city | effective_date | expiry_date | is_current
------------|-------------|------|------|----------------|-------------|------------
1           | 101         | Sarah| NYC  | 2020-01-01     | NULL        | Y
```

**After (July 1, 2023)**:
```
customer_sk | customer_id | name | city | effective_date | expiry_date | is_current
------------|-------------|------|------|----------------|-------------|------------
1           | 101         | Sarah| NYC  | 2020-01-01     | 2023-06-30  | N
2           | 101         | Sarah| LA   | 2023-07-01     | NULL        | Y
```

**Key Columns**:
- `customer_sk`: Surrogate key (unique per version)
- `customer_id`: Natural key (same for all versions)
- `effective_date`: When version became active
- `expiry_date`: When version expired (NULL = current)
- `is_current`: Flag for current version

**Query Current**:
```sql
SELECT * FROM dim_customer 
WHERE customer_id = 101 AND is_current = TRUE;
```

**Query Historical**:
```sql
SELECT * FROM dim_customer 
WHERE customer_id = 101 
  AND '2023-06-15' BETWEEN effective_date AND COALESCE(expiry_date, '9999-12-31');
```

**When to Use**:
- ✅ When history is important (MOST COMMON!)
- ✅ Audit requirements
- ✅ Point-in-time analysis

---

### Q4: Design a data model for a retail store (Nike Store)

**Answer**:

**Requirements**:
- Track sales transactions
- Analyze by customer, product, store, date
- Support both transactions and analytics

**Approach**: Two models!

**1. OLTP Model (Normalized - For Transactions)**:
```sql
-- Normalized tables for daily operations
customers → sales → sale_items → products
```

**2. OLAP Model (Star Schema - For Analytics)**:
```sql
-- Star schema for analytics
fact_sales (center)
  ↓
dim_customer, dim_product, dim_store, dim_date (around it)
```

**Complete Design**:
- See "Complete Nike Store Data Model Example" section above

---

### Q5: What is a fact table and dimension table?

**Answer**:

**Fact Table**:
- Contains measurable business events (sales, clicks, orders)
- Stores metrics/measures (revenue, quantity, profit)
- Foreign keys to dimension tables
- Usually large (millions/billions of rows)
- Additive measures (can be summed)

**Nike Store Example**:
```sql
fact_sales:
  sale_id, date_id, customer_id, product_id, store_id,
  quantity (measure), revenue (measure), profit (measure)
```

**Dimension Table**:
- Contains descriptive attributes
- Provides context for facts
- Usually smaller than fact tables
- Text attributes (names, descriptions)
- Used for filtering and grouping

**Nike Store Example**:
```sql
dim_customer:
  customer_id, customer_name, city, state, customer_segment

dim_product:
  product_id, product_name, category, brand_line, price
```

**Relationship**:
- Fact table references dimensions via foreign keys
- Star schema: Fact in center, dimensions around it
- Query: Join fact with dimensions, filter/group by dimensions, aggregate measures

---

## 📝 Practice Exercises

### Exercise 1: Design a Star Schema for Nike Store

**Scenario**: Design a data warehouse for Nike store sales analytics

**Requirements**:
- Track sales by: date, customer, product, store
- Metrics: quantity, revenue, profit, discount
- Support queries like:
  - Total sales by customer city
  - Sales by product category and month
  - Top 10 customers by revenue

**Solution**: See "Star Schema" section above for complete design.

---

### Exercise 2: Normalize a Table to 3NF

**Given Table** (Violates normalization):
```
sales:
sale_id | customer_name | customer_email | product_name | category | quantity | price | sale_date
```

**Solution**:

**Step 1: 1NF** - Separate sale items
```
sales: sale_id, customer_id, sale_date
sale_items: sale_id, product_id, quantity, price
```

**Step 2: 2NF** - Remove partial dependencies
```
customers: customer_id, customer_name, customer_email
products: product_id, product_name, category_id
categories: category_id, category_name
```

**Step 3: 3NF** - Remove transitive dependencies
```
-- Already in 3NF after step 2
```

---

### Exercise 3: Implement SCD Type 2

**Scenario**: Track customer address changes over time

**Solution**: See "SCD Type 2" section above for complete implementation.

---

## ✅ Check Your Understanding

1. **What are facts and dimensions? Give a Nike store example.**
2. **Explain the difference between Star Schema and Snowflake Schema.**
3. **What is normalization? What are 1NF, 2NF, 3NF?**
4. **When would you use SCD Type 1 vs Type 2? How would you implement SCD Type 2 using MERGE in Delta Lake? **
5. **What is the difference between OLTP and OLAP data modeling?**
6. **When should you normalize vs denormalize?**
7. **What is the grain of a fact table?**
8. **Explain surrogate keys vs natural keys.**
9. **What are the three levels of data models?**
10. **How do you design a fact table?**
11.  **What is data modeling and why is it important? What happens if you skip proper modeling? How does modeling impact performance and cost in cloud warehouses?.**
12.  **Factless fact tables.**
13.  **What are surrogate keys and why use them?**

## 🎯 Next Steps

Once you're comfortable with this topic, we'll move to:
- **Topic 3: Advanced SQL** (Window functions, complex queries, optimization)

**Study Time**: Spend 3-4 days on this topic, practice designing schemas, then let me know when you're ready to move on!

---

## 📚 Additional Resources

- **"The Data Warehouse Toolkit"** by Ralph Kimball - Essential for dimensional modeling
- **"Designing Data-Intensive Applications"** by Martin Kleppmann - Chapter 2-3
- **Kimball Group**: Dimensional modeling techniques
- **dbdiagram.io**: Free ER diagram tool

---


✅ 1️⃣ How Do You Design a Fact Table?
Step-by-step approach
“I always start by defining the grain of the fact table. Then I identify measurable metrics, link dimensions using surrogate keys, and design for performance and scalability.”

Can a fact table change grain later?
No. Grain must remain consistent. If business needs change, you create a new fact table.

🔹 Step 1: Define the Grain (Most Important)
Grain answers:
What does one row represent?
Is it per order? Per transaction? Per event? Per day snapshot?
Example:
One row per order line item
One row per bank transaction
One row per ride event

If you don’t define grain first → interviewer concern 🚩

🔹 Step 2: Identify Measures (Facts)
Facts should be:
Numeric
Aggregatable (if possible)
Examples:
Revenue
Quantity
Ride distance
Transaction amount
Inventory count

🔹 Step 3: Identify Dimensions

Link via surrogate keys:
Date
Customer
Product
Store
Account
Driver
Location

🔹 Step 4: Handle Additivity
Decide if measures are:
Additive
Semi-additive
Non-additive

🔹 Step 5: Performance Strategy
Partition by date
Use surrogate keys (integers)
Avoid text joins
Consider snapshot vs transactional modeling


---

**Explain how ER converts into Dimensional**
To convert an ER model to a dimensional model, I first identify the business process and define the grain. Then I derive the fact table from transactional tables like order_items. Next, I denormalize related entity tables into wide dimension tables, introduce surrogate keys, flatten hierarchies, and optimize for read performance using a star schema structure.

<img width="697" height="317" alt="Screenshot 2026-02-26 at 16 21 06" src="https://github.com/user-attachments/assets/498eb83c-fb8d-4e6f-82a4-ae3969898c65" />

🔹 Step 1: Understand the ER Model (Source System)

An ER model is usually:
Highly normalized (3NF)
Designed for transactions
Optimized for writes
Many small tables
Lots of joins

Example: E-commerce ER Model

Tables might look like:
Customers
Orders
Order_Items
Products
Categories
Payments
Addresses

Highly normalized.
Lots of relationships.
Great for OLTP.
Bad for analytics performance.

🔹 Step 2: Identify Business Process (Very Important)

Dimensional modeling starts with:
What business process are we analyzing?

Examples:
Sales
Inventory
Transactions
Rides
Shipments

This becomes your fact table.

🔹 Step 3: Define the Grain

Example:
For e-commerce:

One row per order line item.
Grain drives everything.

🔹 Step 4: Create Fact Table

From ER:
Order_Items table usually becomes your core fact table.
Fact_Sales:
order_key
product_key
customer_key
date_key
quantity
sales_amount
discount_amount

🔹 Step 5: Denormalize Dimensions

This is where conversion really happens.
In ER:
Customer data might be split across:
customer
customer_address
customer_contact
loyalty_status
In dimensional model:
👉 All that becomes ONE wide Dim_Customer table.

Example:

Dim_Customer:
customer_key (surrogate)
customer_id (natural key)

name
city
state
loyalty_tier
effective_date (if SCD)

🔹 Step 6: Replace Natural Keys with Surrogate Keys

In ER:
customer_id = C123

In Dimensional:
customer_key = 101

Why?
Performance
SCD handling
Decoupling from source

🔹 Step 7: Flatten Hierarchies

In ER:
Product → Subcategory → Category (separate tables)
In Dimensional:
Dim_Product contains:
product_name
subcategory
category

Flattened.
Fewer joins.
Faster queries.

Now instead of 15 normalized tables,
you have:

1 Fact table
5–8 Dimension tables

**Keep Modeling! 📊**
