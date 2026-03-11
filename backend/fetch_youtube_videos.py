"""
Fetch YouTube recommended videos for all existing topics in the database.
Uses the YouTube Data API v3 to find the best educational videos.
"""

import os
import sys
import time
import re
from dotenv import load_dotenv

load_dotenv()

from pymongo import MongoClient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
MONGO_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DB_NAME = "pixel_pirates"

if not YOUTUBE_API_KEY:
    print("ERROR: YOUTUBE_API_KEY not set in .env")
    sys.exit(1)

# Initialize YouTube client
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Initialize MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def format_duration(duration: str) -> str:
    """Convert ISO 8601 duration (PT15M33S) to readable format."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return "0:00"
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def search_videos(language: str, topic_name: str, max_results: int = 3) -> list:
    """Search YouTube for the best educational videos for a topic."""
    query = f"{language} {topic_name} tutorial programming explained"

    try:
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results,
            type="video",
            videoDuration="medium",
            videoEmbeddable="true",
            videoSyndicated="true",
            relevanceLanguage="en",
            safeSearch="strict",
            order="relevance",
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        if not video_ids:
            return []

        # Get full details (duration, stats)
        details_response = youtube.videos().list(
            part="contentDetails,statistics,snippet",
            id=",".join(video_ids),
        ).execute()

        videos = []
        for item in details_response.get("items", []):
            videos.append({
                "id": f"yt_{item['id']}",
                "title": item["snippet"]["title"],
                "language": language,
                "youtubeId": item["id"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "duration": format_duration(item["contentDetails"]["duration"]),
            })

        return videos

    except HttpError as e:
        print(f"  YouTube API error: {e}")
        return []
    except Exception as e:
        print(f"  Unexpected error: {e}")
        return []


def main():
    topics = list(db.topics.find({}, {"_id": 0, "id": 1, "language": 1, "topicName": 1, "recommendedVideos": 1}))
    print(f"Found {len(topics)} topics in database.\n")

    updated = 0
    skipped = 0

    for i, topic in enumerate(topics):
        tid = topic["id"]
        lang = topic.get("language", "")
        name = topic.get("topicName", "")
        existing = topic.get("recommendedVideos", [])

        # Skip if already has videos
        if existing and len(existing) > 0 and existing[0].get("youtubeId"):
            print(f"[{i+1}/{len(topics)}] {tid} — {lang} / {name} — already has {len(existing)} videos, skipping")
            skipped += 1
            continue

        print(f"[{i+1}/{len(topics)}] {tid} — {lang} / {name} — fetching videos...")
        videos = search_videos(lang, name, max_results=3)

        if videos:
            db.topics.update_one({"id": tid}, {"$set": {"recommendedVideos": videos}})
            print(f"  ✓ Saved {len(videos)} videos")
            updated += 1
        else:
            print(f"  ✗ No videos found")

        # Respect API rate limits — small delay between requests
        time.sleep(0.5)

    print(f"\nDone! Updated: {updated}, Skipped (already had videos): {skipped}, Total: {len(topics)}")


if __name__ == "__main__":
    main()
