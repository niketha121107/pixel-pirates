"""Find and fill remaining topics that have no YouTube videos using Gemini to suggest video IDs."""
import os, sys, json, time, re, httpx
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
MONGO_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)
db = client["pixel_pirates"]

# Try YouTube API first, fall back to Gemini-suggested curated videos
def try_youtube_api(language, topic_name):
    """Try YouTube API; return [] if quota exceeded."""
    if not YOUTUBE_API_KEY:
        return []
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        query = f"{language} {topic_name} tutorial programming explained"
        resp = youtube.search().list(
            q=query, part="id,snippet", maxResults=3, type="video",
            videoDuration="medium", videoEmbeddable="true", safeSearch="strict", order="relevance"
        ).execute()
        video_ids = [item["id"]["videoId"] for item in resp.get("items", [])]
        if not video_ids:
            return []
        details = youtube.videos().list(part="contentDetails,snippet", id=",".join(video_ids)).execute()
        videos = []
        for item in details.get("items", []):
            dur = item["contentDetails"]["duration"]
            match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur)
            h, m, s = (int(match.group(i) or 0) for i in (1, 2, 3)) if match else (0, 0, 0)
            fmt = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
            videos.append({
                "id": f"yt_{item['id']}",
                "title": item["snippet"]["title"],
                "language": language,
                "youtubeId": item["id"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "duration": fmt,
            })
        return videos
    except Exception as e:
        if "quota" in str(e).lower():
            return None  # Signal quota exceeded
        print(f"  YouTube error: {e}")
        return []


def gemini_suggest_videos(language, topic_name):
    """Use Gemini to suggest well-known YouTube video IDs for a topic."""
    if not GEMINI_API_KEY:
        return []
    
    prompt = f"""Find 3 popular YouTube tutorial videos about "{language} {topic_name}" programming.
For each video, provide the exact YouTube video ID (the 11-character code from the URL).
Only suggest real, well-known educational videos from popular channels like freeCodeCamp, Traversy Media, Programming with Mosh, Corey Schafer, The Coding Train, Fireship, etc.

Return ONLY valid JSON array, no markdown:
[
  {{"youtubeId": "VIDEO_ID_HERE", "title": "Video Title", "channel": "Channel Name"}},
  {{"youtubeId": "VIDEO_ID_HERE", "title": "Video Title", "channel": "Channel Name"}},
  {{"youtubeId": "VIDEO_ID_HERE", "title": "Video Title", "channel": "Channel Name"}}
]"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 500},
    }
    
    try:
        resp = httpx.post(url, params=params, json=payload, timeout=30.0)
        if resp.status_code != 200:
            print(f"  Gemini error {resp.status_code}")
            return []
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if not json_match:
            return []
        suggestions = json.loads(json_match.group())
        
        videos = []
        for s in suggestions[:3]:
            vid_id = s.get("youtubeId", "")
            if len(vid_id) == 11:
                videos.append({
                    "id": f"yt_{vid_id}",
                    "title": s.get("title", f"{language} {topic_name} Tutorial"),
                    "language": language,
                    "youtubeId": vid_id,
                    "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
                    "duration": "",
                })
        return videos
    except Exception as e:
        print(f"  Gemini suggest error: {e}")
        return []


def main():
    # Find topics without videos
    missing = []
    for t in db.topics.find({}, {"_id": 0, "id": 1, "language": 1, "topicName": 1, "recommendedVideos": 1}):
        vids = t.get("recommendedVideos", [])
        if not vids or len(vids) == 0:
            missing.append(t)
    
    print(f"Topics without videos: {len(missing)}")
    if not missing:
        print("All topics already have videos!")
        return
    
    youtube_quota_exceeded = False
    updated = 0
    
    for i, topic in enumerate(missing):
        tid = topic["id"]
        lang = topic.get("language", "")
        name = topic.get("topicName", "")
        print(f"[{i+1}/{len(missing)}] {tid} - {lang} / {name}")
        
        videos = []
        
        # Try YouTube API first (if quota not exceeded)
        if not youtube_quota_exceeded:
            result = try_youtube_api(lang, name)
            if result is None:
                youtube_quota_exceeded = True
                print("  YouTube quota exceeded, switching to Gemini suggestions")
            elif result:
                videos = result
                print(f"  YouTube API: {len(videos)} videos")
        
        # Fall back to Gemini suggestions
        if not videos:
            videos = gemini_suggest_videos(lang, name)
            if videos:
                print(f"  Gemini suggested: {len(videos)} videos")
            else:
                print(f"  No videos found")
        
        if videos:
            db.topics.update_one({"id": tid}, {"$set": {"recommendedVideos": videos}})
            updated += 1
        
        time.sleep(1)  # Rate limit
    
    print(f"\nDone! Updated {updated}/{len(missing)} topics.")


if __name__ == "__main__":
    main()
