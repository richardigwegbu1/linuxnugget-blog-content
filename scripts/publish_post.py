import os
import markdown
import requests
from pathlib import Path

# Configuration for proxy server
PROXY_URL = os.environ.get("PROXY_URL", "http://YOUR_EC2_PUBLIC_IP:5050/publish")
PROXY_TOKEN = os.environ.get("PROXY_TOKEN", "secret-token")

# Find the latest modified .md file
md_files = sorted(Path("posts").rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
if not md_files:
    print("❌ No markdown files found.")
    exit(1)

latest_md = md_files[0]
category = latest_md.parts[1]  # posts/linux/xyz.md → 'linux'
title = latest_md.stem.replace("-", " ").title()

# Read and convert markdown to HTML
with open(latest_md, "r", encoding="utf-8") as f:
    md_content = f.read()
html_content = markdown.markdown(md_content)

# Prepare post data (we will inject tag_id later)
post_data = {
    "title": title,
    "content": html_content,
    "status": "publish"
}

# Send to proxy server with tag name
headers = {
    "Content-Type": "application/json",
    "X-Proxy-Token": PROXY_TOKEN
}

# First, ask the proxy to get or create the tag ID
tag_response = requests.post(
    f"{PROXY_URL}/get-tag-id",
    headers=headers,
    json={"tag_name": category}
)

if tag_response.status_code in [200, 201]:
    tag_id = tag_response.json().get("id")
    post_data["tags"] = [tag_id]
else:
    print("⚠️ Failed to fetch tag ID, publishing without tag.")
    post_data["tags"] = []

# Final blog post submission
response = requests.post(PROXY_URL, json=post_data, headers=headers)

if response.status_code == 201:
    print(f"✅ Successfully published via proxy: {title}")
else:
    print(f"❌ Failed to publish via proxy. Status: {response.status_code}, Response: {response.text}")

