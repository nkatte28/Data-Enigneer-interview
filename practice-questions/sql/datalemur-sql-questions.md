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

*More DataLemur questions can be added below.*
