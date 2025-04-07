
import os
import requests
import base64
import markdown
from pathlib import Path

# Environment variables from GitHub Secrets
wp_user = os.environ.get("WP_USER")
wp_app_password = os.environ.get("WP_APP_PASSWORD")
wp_domain = os.environ.get("WP_DOMAIN", "https://linuxnugget.com")

# Authentication
credentials = f"{wp_user}:{wp_app_password}"
token = base64.b64encode(credentials.encode())
headers = {
    "Authorization": f"Basic {token.decode('utf-8')}",
    "Content-Type": "application/json"
}

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

# Prepare WordPress API endpoint
wp_api_url = f"{wp_domain}/wp-json/wp/v2/posts"

# Post payload
post_data = {
    "title": title,
    "content": html_content,
    "status": "publish",
    "tags": [category],
}

# POST to WordPress
response = requests.post(wp_api_url, headers=headers, json=post_data)

if response.status_code == 201:
    print(f"✅ Successfully published: {title}")
else:
    print(f"❌ Failed to publish. Status: {response.status_code}, Response: {response.text}")

