import os
import markdown
import requests
from pathlib import Path

# Configuration for proxy server
PROXY_URL = os.environ.get("PROXY_URL", "http://YOUR_EC2_PUBLIC_IP:5050/publish")
PROXY_TOKEN = os.environ.get("PROXY_TOKEN", "secret-token")

# Get the specific post path from environment variable, if provided
target_path = os.environ.get("TARGET_POST")

if target_path:
    latest_md = Path(target_path)
    if not latest_md.exists():
        print(f"❌ Specified file does not exist: {target_path}")
        exit(1)
else:
    md_files = sorted(Path("posts").rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not md_files:
        print("❌ No markdown files found.")
        exit(1)
    latest_md = md_files[0]

# ✅ Debug: Show which file is selected
print(f"📄 Selected Markdown File: {latest_md}")

# Extract title and category
category = latest_md.parts[1]  # posts/linux/xyz.md → 'linux'
title = latest_md.stem.replace("-", " ").title()

# Read and convert markdown to HTML
with open(latest_md, "r", encoding="utf-8") as f:
    md_content = f.read()
html_content = markdown.markdown(md_content)

# Prepare post data
post_data = {
    "title": title,
    "content": html_content,
    "status": "publish",
    "tags": [category],  # Tag will be resolved on proxy via helper endpoint
}

# Send to proxy server
headers = {
    "Content-Type": "application/json",
    "X-Proxy-Token": PROXY_TOKEN
}

response = requests.post(PROXY_URL, json=post_data, headers=headers)

if response.status_code == 201:
    print(f"✅ Successfully published via proxy: {title}")
else:
    print(f"❌ Failed to publish via proxy. Status: {response.status_code}, Response: {response.text}")

