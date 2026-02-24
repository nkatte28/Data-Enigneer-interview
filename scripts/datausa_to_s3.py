"""
Fetch data from the Data USA API and save as JSON in S3.
API docs: https://datausa.io/about/api/

Run from project root: python3 scripts/datausa_to_s3.py
"""
import json
import requests
import boto3

# API URL (population by Year and Nation - from Data USA Tesseract API)
API_URL = (
    "https://honolulu-api.datausa.io/tesseract/data.jsonrecords"
    "?cube=acs_yg_total_population_1&drilldowns=Year%2CNation&locale=en&measures=Population"
)

# S3 settings
bucket = "kbannu-test1"
s3_key = "datausa/acs_yg_total_population_1.json"  # path of the JSON file in the bucket


def fetch_datausa(url=None, timeout=30):
    """Fetch JSON from the Data USA API."""
    if url is None:
        url = API_URL
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "DataEngineerInterview/1.0"})
    resp.raise_for_status()
    try:
        return resp.json()
    except json.JSONDecodeError as e:
        # Show what we got so you can debug (wrong URL often returns HTML or error text)
        preview = (resp.text or "")[:300]
        raise ValueError(f"Response is not valid JSON (err at char {e.pos}). First 300 chars: {preview!r}") from e


def save_json_to_s3(data, bucket_name, key):
    """Upload a Python object as JSON to S3."""
    body = json.dumps(data, indent=2)
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=body,
        ContentType="application/json",
    )


def main():
    print("Fetching from Data USA API...")
    data = fetch_datausa()
    print("Records in response:", len(data.get("data", [])))
    print("Columns:", data.get("columns", []))

    print(f"Uploading to s3://{bucket}/{s3_key}")
    save_json_to_s3(data, bucket, s3_key)
    print("Done. JSON saved to S3.")


if __name__ == "__main__":
    main()
