"""
Fix all broken YouTube videos across all 102 topics.
Uses multiple strategies:
1. YouTube Data API v3 (if quota available)
2. Invidious public API (free, no quota)
"""
import os
import sys
import time
import re
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
db = MongoClient('mongodb://localhost:27017')['pixel_pirates']

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# Public Invidious instances (free YouTube API, no quota)
INVIDIOUS_INSTANCES = [
    "https://vid.puffyan.us",
    "https://invidious.snopyta.org",
    "https://inv.nadeko.net",
    "https://invidious.fdn.fr",
    "https://invidious.privacyredirect.com",
]

youtube_quota_exhausted = False


def search_via_invidious(query: str, max_results: int = 5) -> list:
    """Search via Invidious public API (no quota limits)."""
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"{instance}/api/v1/search"
            params = {
                'q': query,
                'type': 'video',
                'sort_by': 'relevance',
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            videos = []
            for item in data[:max_results]:
                if item.get('type') != 'video':
                    continue
                vid_id = item.get('videoId', '')
                if not vid_id:
                    continue
                title = item.get('title', '')
                thumbs = item.get('videoThumbnails', [])
                thumb = ''
                for th in thumbs:
                    if th.get('quality') == 'medium':
                        thumb = th.get('url', '')
                        break
                if not thumb and thumbs:
                    thumb = thumbs[0].get('url', '')
                # Convert invidious thumbnail URL to YouTube thumbnail
                if thumb and 'ytimg' not in thumb:
                    thumb = f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg"
                length = item.get('lengthSeconds', 0)
                duration = format_duration_secs(length)
                videos.append({
                    'id': f'yt_{vid_id}',
                    'title': title,
                    'language': '',
                    'youtubeId': vid_id,
                    'thumbnail': thumb or f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
                    'duration': duration,
                })
            if videos:
                return videos
        except Exception:
            continue
    return []


def search_via_youtube_api(query: str, max_results: int = 5) -> list:
    """Search YouTube via official API (quota limited)."""
    global youtube_quota_exhausted
    if youtube_quota_exhausted or not API_KEY:
        return []

    params = {
        'part': 'id,snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'videoEmbeddable': 'true',
        'videoSyndicated': 'true',
        'videoDuration': 'medium',
        'relevanceLanguage': 'en',
        'safeSearch': 'strict',
        'order': 'relevance',
        'key': API_KEY,
    }
    resp = requests.get(SEARCH_URL, params=params)
    data = resp.json()

    if 'error' in data:
        msg = data['error'].get('message', '')
        if 'quota' in msg.lower():
            youtube_quota_exhausted = True
            print("  [YouTube API quota exhausted, switching to Invidious]")
        return []

    video_ids = [item['id']['videoId'] for item in data.get('items', [])]
    if not video_ids:
        return []

    det_params = {
        'part': 'snippet,contentDetails,status',
        'id': ','.join(video_ids),
        'key': API_KEY,
    }
    det_resp = requests.get(VIDEOS_URL, params=det_params)
    det_data = det_resp.json()

    videos = []
    for item in det_data.get('items', []):
        status = item.get('status', {})
        if not status.get('embeddable', False):
            continue
        vid_id = item['id']
        snippet = item['snippet']
        thumb = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
        duration = format_duration(item['contentDetails']['duration'])
        videos.append({
            'id': f'yt_{vid_id}',
            'title': snippet['title'],
            'language': '',
            'youtubeId': vid_id,
            'thumbnail': thumb,
            'duration': duration,
        })
    return videos


def search_videos(query: str, max_results: int = 5) -> list:
    """Try YouTube API first, fall back to Invidious."""
    videos = search_via_youtube_api(query, max_results)
    if videos:
        return videos
    return search_via_invidious(query, max_results)


def format_duration(iso_dur: str) -> str:
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_dur)
    if not match:
        return "0:00"
    h, m, s = [int(x) if x else 0 for x in match.groups()]
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_duration_secs(total_secs: int) -> str:
    h = total_secs // 3600
    m = (total_secs % 3600) // 60
    s = total_secs % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def main():
    topics = list(db.topics.find({}, {
        'id': 1, 'topicName': 1, 'language': 1, 'recommendedVideos': 1, '_id': 0
    }))
    print(f"Processing {len(topics)} topics...")

    fixed = 0
    failed = 0

    for i, t in enumerate(topics):
        topic_id = t['id']
        name = t.get('topicName', '')
        lang = t.get('language', '')

        query = f"{lang} {name} tutorial programming"
        print(f"[{i+1}/{len(topics)}] {topic_id}: {name} ({lang})")

        videos = search_videos(query, max_results=5)

        if not videos:
            query2 = f"{lang} {name} tutorial"
            videos = search_videos(query2, max_results=5)

        if not videos:
            query3 = f"{lang} programming tutorial beginner"
            videos = search_videos(query3, max_results=5)

        if not videos:
            print(f"  FAILED - no videos found")
            failed += 1
            continue

        for v in videos:
            v['language'] = lang

        videos = videos[:5]
        print(f"  OK - {len(videos)} videos (source: {'API' if not youtube_quota_exhausted else 'Invidious'})")

        db.topics.update_one(
            {'id': topic_id},
            {'$set': {'recommendedVideos': videos}}
        )
        fixed += 1

        time.sleep(0.3)

    print(f"\nDone! Fixed: {fixed}, Failed: {failed}")
    print("Restart the backend to reload data: GET /api/database/reload")


if __name__ == '__main__':
    main()
