# SQL Interview Questions & Answers

Click **"Show solution and explanation"** to reveal the answer.

---

## Q1. Cumulative amount spent per customer by order date

**Question:** Write an SQL query that returns each order along with the cumulative amount spent by that customer up to that order date.

**Expected output columns:**  
`order_id`, `customer_id`, `order_date`, `amount`, `cumulative_spend`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
select
  order_id,
  customer_id,
  order_date,
  amount,
  sum(amount) over (
    partition by customer_id
    order by order_date
  ) as cumulative_spend
from orders;
```

### Thought process

"Cumulative … by that customer up to that order date" means: for each row, sum all `amount` for the same `customer_id` where `order_date` is on or before the current row's date. That's a window sum: `SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date)`. No `ROWS` or `RANGE` is specified, so the default is `RANGE UNBOUNDED PRECEDING` (all rows from the start of the partition up to the current row), which gives the running total per customer by date.

### Performance note (senior-level)

On large tables:

- Make sure `customer_id` and `order_date` are indexed / clustered.
- In Spark/Databricks: repartition by `customer_id` before the window.

</details>

---

## Q2. Highest spending order(s) per customer

**Question:** Write an SQL query that returns the highest spending order(s) per customer. If a customer has multiple orders tied for highest amount, return all tied orders.

**Output columns:**  
`customer_id`, `order_id`, `amount`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
select customer_id, order_id, amount
from (
  select
    customer_id,
    order_id,
    amount,
    dense_rank() over (
      partition by customer_id
      order by amount desc
    ) as rnk
  from orders
) r
where rnk = 1;
```

### Thought process

We need "highest spending order(s)" per customer and **all tied orders** when there's a tie. So we rank orders by `amount` descending within each `customer_id`, then keep only the top rank.

**Reason for using `DENSE_RANK()`:**  
- `DENSE_RANK()` assigns the same rank to rows with the same `amount` (e.g. two orders of $100 both get 1) and leaves no gap (next distinct amount gets 2). So `WHERE rnk = 1` returns every order that is tied for the max amount per customer.  
- `RANK()` would also give ties the same rank, so it would work here too.  
- `ROW_NUMBER()` would arbitrarily assign 1, 2, 3… and only one row per customer would get 1, so we’d miss tied top orders. So we use `DENSE_RANK()` (or `RANK()`) to include all ties.

</details>

---

## Q3. Top N per group with ties

**Question:** Return the top 2 products per category by amount, but include ties (so you might return more than 2 rows per category).

**Output columns:**  
`category`, `product`, `amount`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
select category, product, amount
from (
  select
    category,
    product,
    amount,
    dense_rank() over (
      partition by category
      order by amount desc
    ) as rnk
  from product_sales
) r
where rnk <= 2;
```

### Thought process

"Top 2 per category" with ties means: within each category, rank products by `amount` descending, then keep rank 1 and rank 2—but if multiple products share rank 1 or rank 2, return all of them. So we need a ranking function that assigns the **same rank to ties**.

**Why `DENSE_RANK()`:**  
- `DENSE_RANK()` gives the same rank to equal values and no gaps (1, 1, 2, 2, 3…). So `WHERE rnk <= 2` returns every product that is in the top two *rank positions* per category, including all products tied for 1st or 2nd.  
- `RANK()` would also work (ties get same rank; next rank after ties might be 3, but we only filter `rnk <= 2`).  
- `ROW_NUMBER()` would assign 1, 2, 3… with no ties, so we’d get exactly 2 rows per category and drop any ties. Using `DENSE_RANK()` (or `RANK()`) keeps all tied rows.

</details>

---

## Q4. "Exactly N rows per group" even with ties

**Question:** Return exactly 2 rows per category with highest amounts. If there's a tie at the cutoff, break ties by lowest `sale_id`.

**Output columns:**  
`category`, `product`, `amount`, `sale_id`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
select category, product, amount, sale_id
from (
  select
    category,
    product,
    amount,
    sale_id,
    row_number() over (
      partition by category
      order by amount desc, sale_id asc
    ) as rn
  from product_sales
) ps
where rn <= 2
order by category, amount desc, sale_id asc;
```

### Thought process

Here we need **exactly** 2 rows per category—no more, even when amounts tie. So we must assign a unique position (1, 2, 3, …) within each category. That’s `ROW_NUMBER()`, not `DENSE_RANK()` or `RANK()`.

**Tie-breaking:** The problem says "if there’s a tie at the cutoff, break ties by lowest sale_id". So ordering must be deterministic: `ORDER BY amount DESC, sale_id ASC`. Same amount then sorts by `sale_id` ascending, so the row with the smallest `sale_id` gets the better row number. That gives a well-defined "top 2" per category. The final `ORDER BY category, amount desc, sale_id asc` is for readable output.

</details>

---

## Q5. 2nd highest distinct salary per dept (ties included)

**Question:** Return employees who have the **second-highest distinct salary** in their department. Include all employees tied at that salary.

**Output columns:**  
`dept`, `emp_id`, `salary`

<details>
<summary>Show solution and explanation</summary>

### Solution

```sql
select dept, emp_id, salary
from (
  select dept, emp_id, salary,
         dense_rank() over (partition by dept order by salary desc) rnk
  from employee_salary
) es
where rnk = 2;
```

### Thought process

"Second-highest **distinct** salary" means: sort salaries in descending order, the 1st distinct value is the max, the 2nd distinct value is the second-highest. We want every employee whose salary equals that second-highest value.

**Why `DENSE_RANK()`:**  
- Ranks are 1, 2, 3… by **distinct** values (no gaps). So the highest salary gets 1, the next distinct salary gets 2, etc.  
- `WHERE rnk = 2` returns all rows with the second-highest salary per dept, including every employee tied at that salary.  
- `RANK()` would also assign the same rank to ties but could leave gaps (e.g. two people at 1st → 1, 1, 3). For "2nd distinct" we only care about `rnk = 2`, so `RANK()` could work too, but `DENSE_RANK()` matches the "distinct" wording: rank 2 = second distinct value.  
- `ROW_NUMBER()` would give only one row per rank, so we’d lose ties.

</details>

---

*More questions can be added below using the same format: question → collapsed answer (solution, thought process, notes).*
