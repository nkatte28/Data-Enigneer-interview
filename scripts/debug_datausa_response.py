"""
Run this to see exactly what the API returns.
  python3 scripts/debug_datausa_response.py

Paste the output if you still get JSONDecodeError when using resp.json().
"""
import requests

url = "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?cube=acs_yg_total_population_1&drilldowns=Year%2CNation&locale=en&measures=Population"

resp = requests.get(url, timeout=30, headers={"User-Agent": "DataEngineerInterview/1.0"})
print("Status:", resp.status_code)
print("Content-Type:", resp.headers.get("Content-Type"))
print("Length:", len(resp.text))
print()
print("First 400 chars (repr):")
print(repr(resp.text[:400]))
print()
print("Characters 0-20 (around column 17 where JSON failed):")
s = resp.text[:25]
for i, c in enumerate(s):
    print(f"  {i}: {repr(c)} (ord={ord(c)})")
