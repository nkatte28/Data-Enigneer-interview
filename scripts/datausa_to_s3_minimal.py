"""
Minimal: fetch Data USA API -> save JSON to S3.
Only the lines you need.
"""
import json
import requests
import boto3

url = "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?cube=acs_yg_total_population_1&drilldowns=Year%2CNation&locale=en&measures=Population"

resp = requests.get(url, timeout=30, headers={"User-Agent": "DataEngineerInterview/1.0"})
data = resp.json()

bucket = "kbannu-test1"
s3_key = "datausa/acs_yg_total_population_1.json"

json_string = json.dumps(data, indent=2)   # or json.dumps(data) for no indent

s3 = boto3.client("s3")
s3.put_object(Bucket=bucket, Key=s3_key, Body=json_string, ContentType="application/json")
print("Uploaded to s3://" + bucket + "/" + s3_key)
