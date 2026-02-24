"""
Run this line-by-line in the terminal for understanding.

Option A: Python REPL
  $ python3
  >>> # then paste or type each block below, one at a time

Option B: Run as script (all steps at once)
  $ python3 scripts/datausa_to_s3_step_by_step.py
"""

# --- STEP 1: Set the full API URL (must include ?cube=...&drilldowns=... etc.) ---
url = "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?cube=acs_yg_total_population_1&drilldowns=Year%2CNation&locale=en&measures=Population"
print("URL:", url[:60], "...")

# --- STEP 2: Import requests ---
import requests

# --- STEP 3: GET the URL; response is stored in resp ---
resp = requests.get(url, timeout=30, headers={"User-Agent": "DataEngineerInterview/1.0"})
print("Status:", resp.status_code)

# --- STEP 4: Check what we got (optional - peek at first 200 chars) ---
print("First 200 chars of response:", resp.text[:200])

# --- STEP 5: Parse response body as JSON into a Python dict ---
import json
data = resp.json()
print("Type of data:", type(data))
print("Top-level keys:", list(data.keys()))

# --- STEP 6: Inspect the structure ---
print("Columns:", data.get("columns"))
print("Number of rows:", len(data.get("data", [])))
print("First row:", data["data"][0] if data.get("data") else None)

# --- STEP 7: S3 settings (change bucket/key if you need) ---
bucket = "kbannu-test1"
s3_key = "datausa/acs_yg_total_population_1.json"

# --- STEP 8: Turn the dict into a JSON string (so we can send bytes to S3) ---
json_string = json.dumps(data, indent=2)
print("JSON string length:", len(json_string), "chars")

# --- STEP 9: Create S3 client and upload ---
import boto3
s3 = boto3.client("s3")
s3.put_object(Bucket=bucket, Key=s3_key, Body=json_string, ContentType="application/json")
print("Uploaded to s3://" + bucket + "/" + s3_key)

# --- STEP 10: Done ---
print("Done.")
