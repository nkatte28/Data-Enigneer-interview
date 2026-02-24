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

*More questions can be added below using the same format: question → collapsed answer (solution, thought process, notes).*
