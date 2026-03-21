#!/usr/bin/env python3
# Direct .env file reader - no caching

with open("../../.env", "r") as f:
    for line in f:
        if line.startswith("YOUTUBE_API_KEY="):
            key = line.split("=", 1)[1].strip()
            print(f"Raw .env file key: {key[:30]}...")
            break
