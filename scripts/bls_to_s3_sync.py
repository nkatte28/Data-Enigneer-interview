import hashlib
import boto3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# defining parameters:
user_agent = "bls-sync/1.0 (contact: krishnaveni.nkatte@gmail.com)"
email = "krishnaveni.nkatte@gmail.com"
index_url = "https://download.bls.gov/pub/time.series/pr/"
prefix = "bls/pr"
bucket = "kbannu-test1"

# creating a session for web connection 
session = requests.Session()
session.headers["User-Agent"] = user_agent
session.headers["From"] = email

html = session.get(index_url).text
soup = BeautifulSoup(html, "html.parser")

# step 1: find all files in the directory so that they can be copied to s3
urls = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.endswith("/"):
        continue
    if href == "../":
        continue
    full_url = urljoin(index_url, href)
    urls.append(full_url)

urls = sorted(set(urls))


prefix = prefix.strip("/")
remotes = []  # each item will have url + s3_key + metadata

for url in urls:
    # Step 2 (URL -> S3 key)
    path = urlparse(url).path.lstrip("/")
    if not path:
        path = hashlib.sha256(url.encode("utf-8")).hexdigest()
    s3_key = f"{prefix}/{path}" if prefix else path
    # Step 3 get the metadata from the url for s3 updates/inserts/deletes
    try:
        info = session.head(url, timeout=60)
        if info.status_code in (403, 405):
            raise Exception()
    except Exception:
        info = session.get(url, stream=True, timeout=60)
    info.raise_for_status()
    last_modified = info.headers.get("Last-Modified")
    remotes.append({
        "url": url,
        "s3_key": s3_key,
        "last_modified": last_modified,
    })


# client for AWS S3
s3 = boto3.client("s3")

# Step 4: list S3 keys and get stored "source last modified" from metadata (only thing we use for compare)
existing_s3 = {}
resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix + "/")
for obj in resp.get("Contents") or []:
    key = obj["Key"]
    existing_s3[key] = {}

for key in existing_s3:
    try:
        head = s3.head_object(Bucket=bucket, Key=key)
        meta = head.get("Metadata") or {}
        existing_s3[key]["source_last_modified"] = meta.get("source-last-modified")
    except Exception:
        existing_s3[key]["source_last_modified"] = None

print(f"Found {len(existing_s3)} existing objects in S3")

# set of s3 keys that the source has right now
remote_keys = {r["s3_key"] for r in remotes}

# Step 5: for each file from source, compare key + source last_modified -> insert or update or skip
inserted = 0
updated = 0
for r in remotes:
    key = r["s3_key"]
    existing = existing_s3.get(key)
    need_upload = False
    if existing is None:
        need_upload = True   # insert: file not in S3
    else:
        # update if source last_modified changed (always use this)
        source_lm = r.get("last_modified")
        stored_lm = existing.get("source_last_modified")
        if source_lm and source_lm != stored_lm:
            need_upload = True   # update: source has newer/different last_modified
    if need_upload:
        action = "Insert" if existing is None else "Update"
        print(f"{action} {key}")
        if existing is None:
            inserted += 1
        else:
            updated += 1
        resp = session.get(r["url"], stream=True, timeout=60)
        resp.raise_for_status()
        meta = {}
        if r.get("last_modified"):
            meta["source-last-modified"] = r["last_modified"]
        s3.upload_fileobj(resp.raw, bucket, key, ExtraArgs={"Metadata": meta} if meta else {})

# Step 6: delete from S3 if file no longer at source
deleted = 0
for key in list(existing_s3.keys()):
    if key not in remote_keys:
        print(f"Delete {key}")
        s3.delete_object(Bucket=bucket, Key=key)
        deleted += 1

print(f"Inserted: {inserted}, Updated: {updated}, Deleted: {deleted}")
print("Done.")
