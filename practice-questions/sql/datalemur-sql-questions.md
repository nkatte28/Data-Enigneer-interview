# DataLemur SQL Questions

Click **"Show solution and explanation"** to reveal the answer.  
*Source: [DataLemur](https://datalemur.com/)*

---

## Q1. User's third transaction (Medium)

**Question:** Assume you are given the table below on Uber transactions made by users. Write a query to obtain the **third transaction** of every user. Output the user id, spend and transaction date.

**Output columns:**  
`user_id`, `spend`, `transaction_date`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
select user_id, spend, transaction_date
from (
  select user_id, spend, transaction_date,
         row_number() over (partition by user_id order by transaction_date) as rn
  from transactions
) t
where rn = 3;
```

### Thought process

We need exactly the **third** transaction per user—one row per user (or no row if the user has fewer than 3 transactions). Order is by `transaction_date`, so "third" means the third in time.

**Why `ROW_NUMBER()`:** We need a strict position (1st, 2nd, 3rd) per user. `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_date)` assigns 1, 2, 3, … by chronological order. Filter `rn = 3` to get only the third transaction per user. Users with fewer than 3 transactions never get `rn = 3`, so they correctly don't appear. If there are ties on `transaction_date`, add a tie-breaker (e.g. `ORDER BY transaction_date, transaction_id`) so the third row is well-defined.

</details>

---

## Q2. Sending vs opening snaps by age group (Medium)

**Question:** Assume you're given tables with information on Snapchat users, including their ages and time spent sending and opening snaps. Write a query to obtain a breakdown of the time spent **sending vs. opening** snaps as a **percentage of total time** spent on these activities grouped by age group. Round the percentage to 2 decimal places.

**Notes:**
- **Percentages:** `time spent sending / (sending + opening)` and `time spent opening / (sending + opening)`.
- To avoid integer division, multiply by **100.0** (not 100).

**Output columns:**  
`age_bucket`, `send_perc`, `open_perc` (each as percentage, 2 decimals)

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
SELECT
  a.age_bucket AS age_bucket,
  round(100.0 * time_spent_sending
    / NULLIF(time_spent_sending + time_spent_opening, 0), 2) AS send_perc,
  round(100.0 * time_spent_opening
    / NULLIF(time_spent_sending + time_spent_opening, 0), 2) AS open_perc
FROM (
  SELECT user_id,
    SUM(CASE WHEN activity_type = 'open' THEN time_spent ELSE 0 END) AS time_spent_opening,
    SUM(CASE WHEN activity_type = 'send' THEN time_spent ELSE 0 END) AS time_spent_sending
  FROM activities
  GROUP BY user_id
) t
JOIN age_breakdown a ON a.user_id = t.user_id
ORDER BY age_bucket;
```

### Thought process

- **Pivot activity time per user:** From `activities` (rows like user_id, activity_type, time_spent), use `SUM(CASE WHEN activity_type = 'open' THEN time_spent ELSE 0 END)` and the same for `'send'` to get `time_spent_opening` and `time_spent_sending` per user. Group by `user_id`.
- **Join to age:** Join that to `age_breakdown` (user_id → age_bucket) so each user has an age group.
- **Percentages:** `send_perc = 100.0 * time_spent_sending / (time_spent_sending + time_spent_opening)`, and similarly for open. Use **100.0** so the division is float. **NULLIF(..., 0)** on the denominator avoids division by zero when both are 0.
- **Round:** `ROUND(..., 2)` for 2 decimal places.
- This version returns **one row per user** (with their age_bucket and their personal send/open %). If the problem expects **one row per age_bucket**, aggregate first: `SUM(time_spent_sending)` and `SUM(time_spent_opening)` grouped by `age_bucket`, then compute the two percentages from those totals.

</details>

---

## Q3. 3-day rolling average of tweets (DataLemur)

**Question:** Given a table of tweet data over a specified time period, calculate the **3-day rolling average** of tweets for each user. Output the user ID, tweet date, and rolling averages rounded to 2 decimal places.

**Notes:**
- A **rolling average** (moving average / running mean) looks at trends over a fixed window. Here we want how tweet count for each user changes over a 3-day period.

**Output columns:**  
`user_id`, `tweet_date`, `tweet_count` (the 3-day rolling average, rounded to 2 decimals)

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
SELECT user_id, tweet_date, round(tweet_count, 2) AS tweet_count
FROM (
  SELECT
    user_id,
    tweet_date,
    AVG(tweet_count) OVER (
      PARTITION BY user_id
      ORDER BY tweet_date
      ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS tweet_count
  FROM tweets
) k;
```

### Thought process

- **Rolling average:** For each row (user_id, tweet_date), we want the average of `tweet_count` over the **current day and the 2 preceding days** (3 days total). That’s a window: `AVG(tweet_count) OVER (PARTITION BY user_id ORDER BY tweet_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`.
- **ROWS BETWEEN 2 PRECEDING AND CURRENT ROW:** Exactly 3 rows—the current row and the 2 previous rows by `tweet_date` within that user. So we get a 3-day moving average. (If there are gaps in dates, ROWS still counts rows, not calendar days; for true “3 calendar days” you’d use a RANGE frame.)
- **Round:** `ROUND(tweet_count, 2)` for 2 decimal places in the output.

</details>

---

## Q4. Top two highest-grossing products per category in 2022 (DataLemur)

**Question:** Assume you're given a table containing data on Amazon customers and their spending on products in different categories. Write a query to identify the **top two highest-grossing products** within each category in the year **2022**. The output should include the category, product, and total spend.

**Table: `product_spend`**

| Column            | Type      |
|-------------------|-----------|
| category          | string    |
| product           | string    |
| user_id           | integer   |
| spend             | decimal   |
| transaction_date  | timestamp |

**Example output:**  
category | product          | total_spend  
appliance | refrigerator    | 299.99  
appliance | washing machine | 219.80  
electronics | vacuum        | 341.00  
electronics | wireless headset | 249.90  

**Output columns:**  
`category`, `product`, `total_spend`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
SELECT
  category,
  product,
  total_spend
FROM (
  SELECT
    category,
    product,
    SUM(spend) AS total_spend,
    RANK() OVER (PARTITION BY category ORDER BY SUM(spend) DESC) AS highest_grossing
  FROM product_spend
  WHERE EXTRACT(YEAR FROM transaction_date) = 2022
  GROUP BY category, product
) K
WHERE highest_grossing <= 2
ORDER BY category, highest_grossing;
```

### Thought process

- **Filter 2022:** `WHERE EXTRACT(YEAR FROM transaction_date) = 2022` (or `YEAR(transaction_date) = 2022` where supported).
- **Total spend per (category, product):** `GROUP BY category, product` and `SUM(spend) AS total_spend`.
- **Rank by total spend within category:** `RANK() OVER (PARTITION BY category ORDER BY SUM(spend) DESC)`. We need the top 2 per category; if there are ties at rank 2, we may return more than 2 rows per category (e.g. two products tied for 2nd). That matches “top two highest-grossing” including ties. Use `RANK()` or `DENSE_RANK()` for ties; for exactly 2 rows per category use `ROW_NUMBER()` with a tie-breaker.
- **Filter:** `WHERE highest_grossing <= 2`, then `ORDER BY category, highest_grossing` for clear output.

</details>

---

## Q5. High earners in each department (DataLemur)

**Question:** As part of an analysis of salary distribution, identify **high earners** in each department. A high earner is an employee whose salary ranks among the **top three salaries** within that department. Write a query to display the employee's name along with their department name and salary. Sort by department name ascending, then salary descending, then name ascending (to break ties).

**Note:** Use an appropriate ranking window function so duplicate salaries are handled correctly (e.g. two people with the same salary in a department get the same rank; all in top 3 are included).

**Table: `employee`**

| column_name   | type    | description            |
|---------------|---------|------------------------|
| employee_id   | integer | Unique ID              |
| name          | string  | Employee name          |
| salary        | integer | Salary                 |
| department_id | integer | Department ID          |
| manager_id    | integer | Manager ID             |

**Table: `department`**

| column_name     | type    |
|-----------------|---------|
| department_id   | integer |
| department_name | string  |

**Example output:**  
department_name | name            | salary  
Data Analytics  | James Anderson  | 4000  
Data Analytics  | Emma Thompson   | 3800  
Data Analytics  | Daniel Rodriguez| 2230  
Data Science    | Noah Johnson    | 6800  
Data Science    | William Davis   | 6800  

**Output columns:**  
`department_name`, `name`, `salary`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
WITH rnk_table AS (
  SELECT
    name,
    salary,
    department_id,
    DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank
  FROM employee
)
SELECT
  d.department_name,
  r.name,
  r.salary
FROM rnk_table r
LEFT JOIN department d ON r.department_id = d.department_id
WHERE rank <= 3
ORDER BY department_name ASC, salary DESC, name ASC;
```

### Thought process

- **Top 3 salaries per department, ties included:** Rank employees by salary descending within each department. Anyone in the “top 3” rank positions should be returned—so if two people are tied for 2nd, both are included. Use **DENSE_RANK()** (or RANK()): same salary → same rank, and we keep `rank <= 3`. ROW_NUMBER() would arbitrarily assign 1,2,3 and drop ties.
- **Join to department:** Join to `department` to get `department_name` (LEFT JOIN so employees without a matching department still appear if needed; INNER JOIN if every employee has a department_id).
- **Order:** `ORDER BY department_name ASC, salary DESC, name ASC` matches the requirement: department first, then salary high to low, then name for tie-break when salaries are equal.

</details>

---

## Q6. TikTok signup activation rate (DataLemur)

**Question:** New TikTok users sign up with their emails and confirm by replying to a text to activate their accounts. Users may receive multiple texts until they have confirmed. A senior analyst wants the **activation rate** of the users in the `emails` table. Write a query to find the activation rate and round the percentage to 2 decimal places.

**Definitions:**
- `emails`: user signup details.
- `texts`: activation information. **'Confirmed'** in `signup_action` means the user activated their account.

**Assumptions:**
- Activation rate is for the **specific users in the emails table** (not all users that might appear in `texts`). A user in `emails` may not appear in `texts`, and vice versa.

**Table: `emails`**

| Column      | Type     |
|-------------|----------|
| email_id    | integer  |
| user_id     | integer  |
| signup_date | datetime |

**Table: `texts`**

| Column        | Type    |
|---------------|---------|
| text_id       | integer |
| email_id      | integer |
| signup_action | varchar |

**Example output:**  
confirm_rate  
0.67  

**Output:** One value (or one row): activation rate as a decimal or percentage, rounded to 2 decimal places (e.g. 0.67 for 67%).

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
SELECT
  ROUND(
    COUNT(DISTINCT t.email_id)::DECIMAL / COUNT(DISTINCT e.email_id),
    2
  ) AS confirm_rate
FROM emails e
LEFT JOIN texts t
  ON e.email_id = t.email_id
  AND t.signup_action = 'Confirmed';
```

### Thought process

- **Denominator:** All signups we care about = rows in `emails`. So total count = `COUNT(DISTINCT e.email_id)` (or just `COUNT(*)` from emails if each email_id appears once).
- **Numerator:** Signups that ever confirmed = distinct `email_id`s that have at least one row in `texts` with `signup_action = 'Confirmed'`. Join `emails` to `texts` on `email_id` and restrict to `signup_action = 'Confirmed'`; then count distinct email_ids. Using **LEFT JOIN** keeps every email in the denominator; only those with a matching confirmed text contribute to the numerator. So numerator = `COUNT(DISTINCT t.email_id)` (NULLs from left join are not counted).
- **Rate:** `numerator / denominator`. Cast to DECIMAL (e.g. `::DECIMAL` or `* 1.0`) to avoid integer division. `ROUND(..., 2)` for 2 decimal places.
- **Multiple texts per user:** We count distinct `email_id` so a user who confirmed once (or multiple confirmations) counts once in the numerator.

</details>

---

## Q7. Fill null category in products (Accenture / DataLemur)

**Question:** The `category` column in the `products` table has nulls. Write a query that returns the product table with **all category values filled in**, assuming:
- The **first product in each category** always has a defined (non-null) category.
- Each category appears only once in the column; products in the same category are **grouped together by sequential product_id** (e.g. product 1 = Shoes, then 2 and 3 are Shoes; product 4 = Jeans, then 5 is Jeans; etc.).

**Table: `products`**

| Column     | Type    |
|------------|---------|
| product_id | integer |
| category   | varchar |
| name       | varchar |

**Example input:** product_id 1 has category 'Shoes', 2 and 3 null; 4 has 'Jeans', 5 null; 6 has 'Shirts', 7 null.

**Example output:** All rows with category filled (1–3 = Shoes, 4–5 = Jeans, 6–7 = Shirts).

**Output columns:**  
`product_id`, `category`, `name`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
SELECT
  product_id,
  COALESCE(
    category,
    MAX(category) OVER (PARTITION BY numbered_category)
  ) AS category,
  name
FROM (
  SELECT
    *,
    COUNT(category) OVER (ORDER BY product_id) AS numbered_category
  FROM products
) AS filled_category;
```

### Thought process

- **Group rows by “category block”:** Products in the same category are consecutive by `product_id`. The first row in each block has non-null `category`; the rest are null. We need a label that is the same for all rows in the same block. Use **COUNT(category) OVER (ORDER BY product_id)**. In standard SQL, COUNT(category) counts non-null values; with ORDER BY product_id, it’s a running count of how many non-null categories we’ve seen so far. So: product 1 (Shoes) → count 1; products 2, 3 (null) → still 1; product 4 (Jeans) → count 2; product 5 (null) → 2; product 6 (Shirts) → 3; product 7 (null) → 3. So `numbered_category` identifies each block (1, 1, 1, 2, 2, 3, 3).
- **Fill nulls:** Within each block, the first row has the category. So take **MAX(category) OVER (PARTITION BY numbered_category)** — the only non-null in that partition is that first row’s category, so MAX gives it. Then **COALESCE(category, that_max)**: rows that already have category stay as-is; nulls get the block’s category.
- **Result:** Every row gets the correct category; output columns product_id, category, name.

</details>

---

## Q8. Top 2 drugs per manufacturer by units sold (CVS Health / DataLemur)

**Question:** CVS Health wants to understand pharmacy sales and how well different drugs sell. Write a query to find the **top 2 drugs sold** (by units sold) for **each manufacturer**. List results in alphabetical order by manufacturer.

**Output columns:**  
`manufacturer`, `top_drugs` (or drug name). If there are ties for 2nd place, include all tied drugs (more than 2 rows per manufacturer allowed).

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
SELECT manufacturer, drug AS top_drugs
FROM (
  SELECT
    manufacturer,
    drug,
    DENSE_RANK() OVER (PARTITION BY manufacturer ORDER BY units_sold DESC) AS rnk
  FROM pharmacy_sales
) ps
WHERE rnk <= 2
ORDER BY manufacturer;
```

### Thought process

- **Top 2 per manufacturer:** Rank drugs by `units_sold` descending within each manufacturer. Keep rank 1 and 2. Use **DENSE_RANK()** so that if multiple drugs tie for 1st or 2nd, they all get the same rank and we return all of them (e.g. three drugs tied for 2nd → all three appear). `ROW_NUMBER()` would arbitrarily pick only two rows per manufacturer and drop ties.
- **Partition and order:** `PARTITION BY manufacturer ORDER BY units_sold DESC` then `WHERE rnk <= 2`.
- **Output:** `manufacturer` and drug name (as `top_drugs`). Final `ORDER BY manufacturer` for alphabetical order by manufacturer.

</details>

---

## Q9. Unique product combinations per transaction (Walmart / DataLemur)

**Question:** Given the Walmart `transactions` and `products` tables, write a query to find the **count of unique product combinations** that are purchased together in the same transaction. A transaction must have **at least two products** to form a combination. Display output in ascending order of the combinations (or report the count).

**Example:** If one transaction has apples and bananas, another has bananas and soy milk, the number of **unique combinations** is 2 (apples+bananas, bananas+soy milk). Same combination in different transactions counts once.

*You may or may not need the `products` table (product_id is enough to define a combination).*

**Table: `transactions`**

| Column           | Type     |
|------------------|----------|
| transaction_id   | integer  |
| product_id       | integer  |
| user_id          | integer  |
| transaction_date | datetime |

**Table: `products`**

| Column       | Type    |
|--------------|---------|
| product_id   | integer |
| product_name | string  |

**Example output (list of distinct combinations):**  
combination  
111","222","444  
(or similar string/array representation of product_id sets)

**Output:** Either (1) distinct combinations in ascending order, or (2) a single count: `unique_combo_count`.

<details>
<summary>Show solution and explanation</summary>

### Solution 1: Distinct combinations (array), ordered

```sql
WITH array_table AS (
  SELECT
    transaction_id,
    ARRAY_AGG(CAST(product_id AS TEXT) ORDER BY product_id) AS combination
  FROM transactions
  GROUP BY transaction_id
)
SELECT DISTINCT combination
FROM array_table
WHERE ARRAY_LENGTH(combination, 1) > 1
ORDER BY combination;
```

### Solution 2: Count of unique combinations

```sql
WITH per_txn AS (
  SELECT
    transaction_id,
    ARRAY_AGG(DISTINCT product_id ORDER BY product_id) AS products
  FROM transactions
  GROUP BY transaction_id
)
SELECT COUNT(DISTINCT products) AS unique_combo_count
FROM per_txn
WHERE ARRAY_LENGTH(products, 1) >= 2;
```

*(Use `>= 2` so only transactions with at least 2 products count. Some dialects use `CARDINALITY(products) >= 2` or `array_length(..., 1) > 1`.)*

### Solution 3: Distinct combinations (string), ordered

```sql
WITH dedup AS (
  SELECT DISTINCT transaction_id, product_id
  FROM transactions
),
per_txn AS (
  SELECT
    transaction_id,
    STRING_AGG('"' || product_id::text || '"', ',' ORDER BY product_id) AS combination,
    COUNT(*) AS product_count
  FROM dedup
  GROUP BY transaction_id
)
SELECT DISTINCT combination
FROM per_txn
WHERE product_count > 1
ORDER BY combination;
```

### Thought process

- **Combination = set of product_ids in one transaction:** For each transaction, aggregate product_ids into a single value (array or sorted string) so we can compare “same combination” across transactions. Sort (e.g. ORDER BY product_id) so (111, 222) and (222, 111) become the same.
- **At least 2 products:** Filter out transactions with only one product: `ARRAY_LENGTH(...) > 1` or `>= 2`, or `COUNT(*) > 1` after grouping.
- **Unique combinations:** Use `DISTINCT` on the combination (array or string). For **count** only: `COUNT(DISTINCT combination)` (or count distinct array/string per dialect).
- **Dedup within transaction:** If a transaction can have the same product_id twice, use `DISTINCT` in the aggregate (e.g. `ARRAY_AGG(DISTINCT product_id ...)` or a CTE that deduplicates (transaction_id, product_id) first, as in Solution 3.
- **Products table:** Optional; combination can be defined by product_id only. Use products if the output must show product names instead of ids.

</details>

---

## Q10. Supercloud customers (Microsoft Azure / DataLemur)

**Question:** A **Supercloud customer** is one who has purchased at least one product from **every product category** in the `products` table. Write a query to identify the **customer_id**s of these Supercloud customers.

**Table: `customer_contracts`**

| Column      | Type    |
|-------------|---------|
| customer_id | integer |
| product_id  | integer |
| amount      | integer |

**Table: `products`**

| Column            | Type    |
|-------------------|---------|
| product_id        | integer |
| product_category  | string  |
| product_name      | string  |

**Example output:**  
customer_id  
1  

(Only customers who have bought from all categories appear.)

**Output column:**  
`customer_id`

<details>
<summary>Show solution and explanation</summary>

### Solution 1: Count distinct categories

```sql
SELECT customer_id
FROM customer_contracts cc
JOIN products p ON cc.product_id = p.product_id
GROUP BY cc.customer_id
HAVING COUNT(DISTINCT p.product_category) = (
  SELECT COUNT(DISTINCT product_category) FROM products
);
```

### Solution 2: Match set of categories (array)

```sql
SELECT c.customer_id
FROM customer_contracts c
JOIN products p ON c.product_id = p.product_id
GROUP BY c.customer_id
HAVING ARRAY_AGG(DISTINCT product_category ORDER BY product_category) = (
  SELECT ARRAY_AGG(DISTINCT product_category ORDER BY product_category)
  FROM products
);
```

*(Syntax may vary by dialect; some support set equality or sorted array comparison.)*

### Thought process

- **Supercloud = has at least one product in every category:** For each customer, the set of categories they’ve bought from must equal the set of all categories in `products`. Join `customer_contracts` to `products` on `product_id` to get (customer_id, product_category).
- **Solution 1:** Count how many **distinct** categories each customer has: `COUNT(DISTINCT product_category)` in a GROUP BY customer_id. The total number of categories is `(SELECT COUNT(DISTINCT product_category) FROM products)`. A customer is Supercloud iff their distinct category count equals that total. Use **HAVING** to filter.
- **Solution 2:** Build the set of categories per customer (e.g. sorted `ARRAY_AGG(DISTINCT product_category ORDER BY product_category)`) and compare to the full set of categories from `products`. If the two arrays/sets are equal, the customer has all categories. Requires array/set comparison support.
- **Duplicate purchases:** Using DISTINCT category (or distinct in the aggregate) ensures multiple products in the same category don’t inflate the count or the set.

</details>

---

## Q11. Odd- vs even-numbered measurements per day (DataLemur)

**Question:** Write a query to calculate the **sum of odd-numbered** and **sum of even-numbered** measurements **separately** for each day, and display the results in two columns.

**Definition:** Within a day, the **1st, 3rd, 5th** measurements (by time) are **odd-numbered**; the **2nd, 4th, 6th** are **even-numbered**.

**Output columns:**  
`measurement_day`, `odd_sum`, `even_sum`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
WITH ranked_measurements AS (
  SELECT
    CAST(measurement_time AS DATE) AS measurement_day,
    measurement_value,
    ROW_NUMBER() OVER (
      PARTITION BY CAST(measurement_time AS DATE)
      ORDER BY measurement_time
    ) AS measurement_num
  FROM measurements
)
SELECT
  measurement_day,
  SUM(CASE WHEN measurement_num % 2 != 0 THEN measurement_value ELSE 0 END) AS odd_sum,
  SUM(CASE WHEN measurement_num % 2 = 0 THEN measurement_value ELSE 0 END) AS even_sum
FROM ranked_measurements
GROUP BY measurement_day;
```

### Thought process

- **Assign position within each day:** For each row, we need "1st, 2nd, 3rd…" by time on that day. Use **ROW_NUMBER() OVER (PARTITION BY CAST(measurement_time AS DATE) ORDER BY measurement_time)** so the earliest measurement that day is 1, next is 2, etc. Cast to DATE so all timestamps on the same calendar day are in one partition.
- **Odd vs even:** Odd positions (1, 3, 5, …) → `measurement_num % 2 != 0`; even (2, 4, 6, …) → `measurement_num % 2 = 0`.
- **Sums per day:** Group by `measurement_day`. Use **SUM(CASE WHEN … THEN measurement_value ELSE 0 END)** twice: once for odd positions (odd_sum), once for even (even_sum). Result: one row per day with odd_sum and even_sum.

</details>

---

## Q12. Correct swapped delivery items (Zomato / DataLemur)

**Question:** Due to an error, each item's order was **swapped with the item in the next row**. Correct this and return the proper pairing of **order_id** and **item**. If the **last** order_id is **odd**, that row stays unchanged (no swap); otherwise pairs are (1↔2), (3↔4), etc.

**Example:** After correction, order_id 1 should show the item that was in row 2, order_id 2 the item that was in row 1, and so on. Last row (e.g. order_id 7) if odd remains as-is.

**Output columns:**  
`order_id`, `item` (corrected)

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
WITH x AS (
  SELECT
    order_id,
    item,
    LEAD(item) OVER (ORDER BY order_id) AS next_item,
    LAG(item) OVER (ORDER BY order_id) AS prev_item,
    MAX(order_id) OVER () AS max_id
  FROM orders
)
SELECT
  order_id,
  CASE
    WHEN order_id % 2 = 1 AND order_id <> max_id THEN next_item
    WHEN order_id % 2 = 0 THEN prev_item
    ELSE item
  END AS item
FROM x
ORDER BY order_id;
```

### Thought process

- **Swap logic:** Rows were shifted: row 1 got row 2's item, row 2 got row 1's item, etc. So for **odd** order_id (1, 3, 5…), the corrected item is the **next** row's item; for **even** order_id (2, 4, 6…), the corrected item is the **previous** row's item. Exception: if the **last** order_id is odd, it has no "next" and stays as-is.
- **LEAD/LAG:** `LEAD(item) OVER (ORDER BY order_id)` = item from the next order_id; `LAG(item) OVER (ORDER BY order_id)` = item from the previous order_id. We need `max_id` to detect the last row: `MAX(order_id) OVER ()`.
- **CASE:** (1) Odd and not last → use `next_item`. (2) Even → use `prev_item`. (3) Else (odd and last) → keep `item`. Output order_id and this corrected item, ordered by order_id.

</details>

---

*More DataLemur questions can be added below.*
