"""
Enrich all 180 topics with:
  1. Gemini-generated study material (stored as `studyMaterial` field)
  2. Real YouTube videos via YouTube Data API v3

Usage:
    python enrich_topics.py
"""

import os, sys, time, json, re, logging
from dotenv import load_dotenv
from pymongo import MongoClient
import httpx

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGODB_DATABASE", "pixel_pirates")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
YT_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YT_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# Rate limit: free tier = ~15 RPM for Gemini.  Wait between calls.
GEMINI_DELAY = 5  # seconds between Gemini calls

db = MongoClient(MONGO_URL)[MONGO_DB]
client = httpx.Client(timeout=60)


# ── Gemini helper ───────────────────────────────────────────────
def call_gemini(prompt: str, retries: int = 3) -> str:
    """Call Gemini and return the text response."""
    for attempt in range(retries):
        try:
            resp = client.post(GEMINI_URL, json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096},
            })
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                log.warning(f"  Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
                continue
            if resp.status_code == 500 or resp.status_code == 503:
                wait = 10 * (attempt + 1)
                log.warning(f"  Server error ({resp.status_code}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text.strip()
        except Exception as e:
            log.error(f"  Gemini error (attempt {attempt+1}): {e}")
            time.sleep(10 * (attempt + 1))
    return ""


def generate_study_material(topic_name: str, language: str, overview: str) -> dict:
    """Generate comprehensive study material for a topic."""
    prompt = f"""Create a comprehensive study material document for the programming topic below.

Topic: {topic_name}
Language: {language}
Overview: {overview}

Return a JSON object with EXACTLY these keys (no markdown fences, just raw JSON):
{{
  "title": "Study material title",
  "overview": "A 2-3 paragraph detailed overview of this topic",
  "syntax": "The core syntax/pattern for this topic with proper code formatting",
  "codeExample": "A complete, runnable code example demonstrating this topic (10-20 lines)",
  "explanation": "A detailed multi-paragraph explanation covering how this works internally, key concepts, and common patterns",
  "implementation": ["Where/how this is used in real projects - item 1", "item 2", "item 3", "item 4"],
  "advantages": ["Advantage 1", "Advantage 2", "Advantage 3", "Advantage 4"],
  "disadvantages": ["Disadvantage 1", "Disadvantage 2", "Disadvantage 3"],
  "keyPoints": ["Key takeaway 1", "Key takeaway 2", "Key takeaway 3", "Key takeaway 4", "Key takeaway 5"],
  "commonMistakes": ["Common mistake 1", "Common mistake 2", "Common mistake 3"]
}}

IMPORTANT: Return ONLY valid JSON. No markdown code fences. No extra text."""

    raw = call_gemini(prompt)
    if not raw:
        return {}

    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        match = re.search(r"\{[\s\S]+\}", raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        log.error(f"  Failed to parse Gemini JSON for {topic_name}")
        return {}


# ── YouTube helper ──────────────────────────────────────────────
def format_duration(iso: str) -> str:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m:
        return "0:00"
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    if h:
        return f"{h}:{mi:02d}:{s:02d}"
    return f"{mi}:{s:02d}"


def search_youtube(topic_name: str, language: str, max_results: int = 3) -> list:
    """Search YouTube for tutorial videos. Returns list of video dicts."""
    if not YOUTUBE_API_KEY:
        return []

    query = f"{language} {topic_name} tutorial programming"
    try:
        resp = client.get(YT_SEARCH_URL, params={
            "key": YOUTUBE_API_KEY,
            "q": query,
            "part": "id,snippet",
            "maxResults": max_results,
            "type": "video",
            "videoDuration": "medium",
            "videoEmbeddable": "true",
            "safeSearch": "strict",
            "order": "relevance",
        })
        if resp.status_code == 403:
            log.error("  YouTube API quota exceeded!")
            return []
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items:
            return []

        # Get video details (duration, stats)
        video_ids = [it["id"]["videoId"] for it in items]
        details_resp = client.get(YT_VIDEOS_URL, params={
            "key": YOUTUBE_API_KEY,
            "id": ",".join(video_ids),
            "part": "contentDetails,statistics,snippet",
        })
        details_resp.raise_for_status()
        detail_map = {it["id"]: it for it in details_resp.json().get("items", [])}

        videos = []
        for vid_id in video_ids:
            det = detail_map.get(vid_id)
            if not det:
                continue
            videos.append({
                "id": f"yt_{vid_id}",
                "title": det["snippet"]["title"],
                "language": language,
                "youtubeId": vid_id,
                "thumbnail": det["snippet"]["thumbnails"].get("medium", {}).get("url", ""),
                "duration": format_duration(det["contentDetails"]["duration"]),
                "description": det["snippet"].get("description", "")[:200],
            })
        return videos

    except Exception as e:
        log.error(f"  YouTube search error for '{topic_name}': {e}")
        return []


# ── Main ────────────────────────────────────────────────────────
def main():
    topics = list(db.topics.find({}, {"_id": 0}))
    total = len(topics)
    log.info(f"Found {total} topics to enrich")

    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY not set in .env — cannot generate study material")
        sys.exit(1)
    if not YOUTUBE_API_KEY:
        log.warning("YOUTUBE_API_KEY not set — will skip YouTube video enrichment")

    study_done = 0
    study_skip = 0
    video_done = 0
    video_skip = 0
    yt_quota_hit = False

    for idx, topic in enumerate(topics, 1):
        tid = topic["id"]
        name = topic.get("topicName", "")
        lang = topic.get("language", "")
        overview = topic.get("overview", "")
        log.info(f"[{idx}/{total}] {tid}: {name} ({lang})")

        updates = {}

        # ── 1. Study Material ──────────────────────────────────
        if topic.get("studyMaterial"):
            log.info(f"  Study material already exists, skipping")
            study_skip += 1
        else:
            log.info(f"  Generating study material via Gemini...")
            material = generate_study_material(name, lang, overview)
            if material:
                updates["studyMaterial"] = material
                study_done += 1
                log.info(f"  ✅ Study material generated")
            else:
                log.warning(f"  ⚠️  Failed to generate study material")

        # ── 2. YouTube Videos ──────────────────────────────────
        existing_vids = topic.get("recommendedVideos", [])
        has_real_video = any(v.get("youtubeId") for v in existing_vids)

        if has_real_video:
            log.info(f"  YouTube videos already present, skipping")
            video_skip += 1
        elif yt_quota_hit:
            log.info(f"  Skipping YouTube (quota exhausted)")
        elif YOUTUBE_API_KEY:
            log.info(f"  Searching YouTube...")
            videos = search_youtube(name, lang)
            if videos:
                updates["recommendedVideos"] = videos
                video_done += 1
                log.info(f"  ✅ Found {len(videos)} videos")
            elif not videos and YOUTUBE_API_KEY:
                # Check if it was a quota issue (search_youtube logs error)
                # Try a simpler query
                videos = search_youtube(name, lang, max_results=1)
                if videos:
                    updates["recommendedVideos"] = videos
                    video_done += 1
                    log.info(f"  ✅ Found {len(videos)} video (fallback)")
                else:
                    log.warning(f"  ⚠️  No videos found")

        # ── Save to MongoDB ────────────────────────────────────
        if updates:
            db.topics.update_one({"id": tid}, {"$set": updates})
            log.info(f"  💾 Saved updates: {list(updates.keys())}")

        # Rate limit: delay between Gemini calls to stay under free tier limits
        if "studyMaterial" in updates:
            time.sleep(GEMINI_DELAY)

    log.info(f"\n{'='*50}")
    log.info(f"DONE!")
    log.info(f"  Study material: {study_done} generated, {study_skip} already existed")
    log.info(f"  YouTube videos: {video_done} fetched, {video_skip} already existed")
    log.info(f"{'='*50}")


if __name__ == "__main__":
    main()
