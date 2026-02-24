"""
Fetch data from the Data USA Tesseract API.
Run from project root: python3 scripts/fetch_datausa_api.py

Uses only standard library (no pip install needed).
Parameter choices follow the official API; see resources/datausa-api-reference.md.
"""
import json
import urllib.request
import urllib.parse

# Official Data USA API (see resources/datausa-api-reference.md)
BASE_URL = "https://api.datausa.io/tesseract/data.jsonrecords"

# Example from API docs: population by state in 2023 (limit 100)
# cube/drilldowns/measures come from /cubes and /cubes/{name}; include = filter; limit = limit,offset
PARAMS = {
    "cube": "acs_yg_total_population_5",
    "drilldowns": "State,Year",
    "measures": "Population",
    "include": "Year:2023",
    "limit": "100,0",
}


def fetch_datausa_population(url=BASE_URL, params=PARAMS, timeout=30):
    full_url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full_url, headers={"User-Agent": "DataEngineerInterview/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode())


def main():
    print("Fetching from DataUSA API...")
    payload = fetch_datausa_population()

    annotations = payload.get("annotations", {})
    page = payload.get("page", {})
    columns = payload.get("columns", [])
    data = payload.get("data", [])

    print("Source:", annotations.get("source_name"), "-", annotations.get("dataset_name"))
    print("Total records:", page.get("total"))
    print("Columns:", columns)
    print("\nData (first 3 rows):")
    for row in data[:3]:
        print(" ", row)

    # Optional: pandas (install with pip install pandas)
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        print("\nPandas DataFrame:")
        print(df.to_string())
    except ImportError:
        print("\n(Install pandas to get DataFrame: pip install pandas)")

    return data


if __name__ == "__main__":
    main()
