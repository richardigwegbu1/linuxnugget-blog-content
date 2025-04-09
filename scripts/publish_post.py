import os
import markdown
import requests
from pathlib import Path

PROXY_BASE_URL = os.environ.get("PROXY_URL", "http://YOUR_EC2_PUBLIC_IP:5050")
PROXY_TOKEN = os.environ.get("PROXY_TOKEN", "secret-token")
PROXY_TAG_ENDPOINT = f"{PROXY_BASE_URL}/publish/get-tag-id"
PROXY_POST_ENDPOINT = f"{PROXY_BASE_URL}/publish"

# Get target post from GitHub Action env or fallback to most recent
target_path = os.environ.get("TARGET_POST")

if target_path:
    md_file = Path(target_path)
    if not md_file.exists():
        print(f"❌ File not found: {target_path}")
        exit(1)
else:
    md_files = sorted(Path("posts").rglob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not md_files:
        print("❌ No Markdown files found.")
        exit(1)
    md_file = md_files[0]

print(f"📄 Selected Markdown File: {md_file}")

# Extract category from folder structure: posts/ansible/intro.md → ansible
category = md_file.parts[1]
title = md_file.stem.replace("-", " ").title()

# Convert Markdown to HTML
with open(md_file, "r", encoding="utf-8") as f:
    html_content = markdown.markdown(f.read())

# 🔗 Get tag ID from proxy
tag_payload = {"tag": category}
tag_headers = {
    "Content-Type": "application/json",
    "X-Proxy-Token": PROXY_TOKEN
}
tag_response = requests.post(PROXY_TAG_ENDPOINT, json=tag_payload, headers=tag_headers)

print(f"🏷️ Tag Response: {tag_response.status_code} → {tag_response.text}")
if tag_response.status_code not in [200, 400]:
    print("❌ Failed to get or resolve tag ID.")
    exit(1)

tag_id = tag_response.json().get("tag_id", 0)

# 📤 Publish post
post_payload = {
    "title": title,
    "content": html_content,
    "status": "publish",
    "tags": [tag_id]
}
post_headers = {
    "Content-Type": "application/json",
    "X-Proxy-Token": PROXY_TOKEN
}
post_response = requests.post(PROXY_POST_ENDPOINT, json=post_payload, headers=post_headers)

print(f"📬 WordPress Response: {post_response.status_code} → {post_response.text}")
if post_response.status_code == 201:
    print(f"✅ Post published: {title}")
else:
    print("❌ Post failed.")
    exit(1)

