
name: Auto-Publish Blog Post via Proxy

on:
  push:
    paths:
      - "posts/**.md"

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install Dependencies
      run: pip install markdown requests

    - name: Publish Post via Proxy
      env:
        PROXY_URL: ${{ secrets.PROXY_URL }}
        PROXY_TOKEN: ${{ secrets.PROXY_TOKEN }}
      run: python scripts/publish_post.py

