# Data USA API Reference

Condensed reference for the [Data USA Tesseract API](https://api.datausa.io/). Use this to build query strings and understand responses.

---

## Endpoints

| Endpoint | Purpose |
|----------|---------|
| `https://api.datausa.io/tesseract/cubes` | List all available data cubes |
| `https://api.datausa.io/tesseract/cubes/{name}` | Schema of a cube (measures, dimensions, levels) |
| `https://api.datausa.io/tesseract/members?cube=<name>&level=<level>` | Distinct values for a dimension level (for filters) |
| `https://api.datausa.io/tesseract/data.{format}` | **Main data endpoint** — fetch data |

### Data response formats

- `data.jsonrecords` — JSON array of objects (readable)
- `data.jsonarrays` — JSON array of arrays (compact)
- `data.csv` — Comma-separated values
- `data.tsv` — Tab-separated values
- `data.parquet` — Parquet (big data)
- `data.xlsx` — Excel spreadsheet

---

## Anatomy of a request

**Example:** Population by state in 2023, limit 100

```
https://api.datausa.io/tesseract/data.jsonrecords?cube=acs_yg_total_population_5&drilldowns=State,Year&measures=Population&include=Year:2023&limit=100,0
```

| Component | Example | Description |
|-----------|---------|-------------|
| **Root** | `https://api.datausa.io/tesseract/data.jsonrecords` | Base URL + format |
| **cube** | `?cube=acs_yg_total_population_5` | Dataset to query (from `/cubes`) |
| **drilldowns** | `&drilldowns=State,Year` | Columns/dimensions in the response |
| **measures** | `&measures=Population` | Metric columns (aggregated by cube default) |
| **include** | `&include=Year:2023` | Filter: only these dimension values (semicolon for multiple) |
| **exclude** | `&exclude=State:04000US01` | Filter: exclude these members |
| **limit** | `&limit=100,0` | Limit and offset: `limit,offset` |

---

## Anatomy of a response

```json
{
  "annotations": { "source_name", "dataset_name", "topic", ... },
  "page": { "limit", "offset", "total" },
  "columns": [ "State ID", "State", "Year", "Population" ],
  "data": [ { "State ID": "...", "State": "...", "Year": 2023, "Population": 5054253 }, ... ]
}
```

- **annotations** — Metadata (source, dataset name, etc.)
- **page** — Pagination (total count, limit, offset)
- **columns** — Column names (IDs included even if not in drilldowns)
- **data** — Array of record objects

---

## Advanced parameters

### Include (filter by dimension values)

- One member: `&include=Year:2023`
- Multiple members (OR): `&include=Year:2023,2022`
- Multiple dimensions: `&include=Year:2023;State:04000US01` or separate `&include=...&include=...`

### Exclude

- Same format as include: `&exclude=State:04000US01`

### Filters (on measures)

- Null: `&filters=Population.isnull` / `Population.isnotnull`
- Compare: `&filters=Population.gt.30000000` (gt, gte, lt, lte, eq, neq)
- Range: `&filters=Population.gt.250000.and.lt.750000`

### Sort

- `&sort=Population.asc` or `&sort=Population.desc`
- `&sort=Year.desc`

### Ranking

- `&ranking=Population` (asc) or `&ranking=-Population` (desc)

### TopK (top N per group)

- `&top=1.State.Population.desc` — one row per state (year with highest population)
- `&top=2.State.Population.desc` — top 2 years per state

### Time (time dimensions)

- `&time=Year.latest` or `&time=Year.latest.5`
- `&time=Year.oldest` or `&time=Year.oldest.3`
- `&time=Year.trailing.10` / `&time=Year.leading.10`

### Parents (hierarchical dimensions)

- `&parents=County` or `&parents=true`

---

## How to choose parameters

1. **List cubes:** `GET https://api.datausa.io/tesseract/cubes` → pick a `cube`.
2. **Cube schema:** `GET https://api.datausa.io/tesseract/cubes/{cube}` → see **measures** and **dimensions/levels** (for drilldowns).
3. **Member values:** `GET https://api.datausa.io/tesseract/members?cube={cube}&level={Level}` → values for `include`/`exclude`.
4. **Build URL:** base + `?cube=...&drilldowns=...&measures=...` + optional `include`, `limit`, `sort`, etc.

---

*Source: Data USA API documentation (endpoints, request/response anatomy, advanced parameters).*
