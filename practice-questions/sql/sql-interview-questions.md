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

*More questions can be added below using the same format: question → collapsed answer (solution, thought process, notes).*
