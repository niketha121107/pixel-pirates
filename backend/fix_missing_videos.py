"""List topics without videos, then insert curated fallback videos."""
from pymongo import MongoClient

db = MongoClient("mongodb://localhost:27017/")["pixel_pirates"]

missing = []
for t in db.topics.find({}, {"_id": 0, "id": 1, "language": 1, "topicName": 1, "recommendedVideos": 1}):
    vids = t.get("recommendedVideos", [])
    if not vids or len(vids) == 0:
        missing.append({"id": t["id"], "lang": t.get("language", ""), "name": t.get("topicName", "")})

print(f"Total topics: {db.topics.count_documents({})}")
print(f"Missing videos: {len(missing)}")
for m in missing:
    print(f"  {m['id']} - {m['lang']} / {m['name']}")

# Well-known tutorial video IDs by language
LANG_VIDEOS = {
    "Go": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Programming - Golang Course with Bonus Projects"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Learn Go Programming - Golang Tutorial for Beginners"},
        {"youtubeId": "446E-r0rXHI", "title": "Go in 100 Seconds"},
    ],
    "SQL": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Tutorial - Full Database Course for Beginners"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL Tutorial for Beginners - Full Course"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL Full Course - Learn SQL in 4 Hours"},
    ],
    "TypeScript": [
        {"youtubeId": "BwuLxPH8IDs", "title": "TypeScript Course for Beginners"},
        {"youtubeId": "30LWjhZzg50", "title": "Learn TypeScript - Full Tutorial"},
        {"youtubeId": "d56mG7DezGs", "title": "TypeScript Tutorial - Traversy Media"},
    ],
    "Kotlin": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Course - Tutorial for Beginners"},
        {"youtubeId": "EExSSotojVI", "title": "Learn Kotlin Programming - Full Course"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Kotlin in 100 Seconds"},
    ],
    "HTML/CSS": [
        {"youtubeId": "mU6anWqZJcc", "title": "HTML & CSS Full Course - Beginner to Pro"},
        {"youtubeId": "G3e-cpL7ofc", "title": "HTML & CSS Full Course for Beginners"},
        {"youtubeId": "HGTJBPNC-Gw", "title": "Build Responsive Websites - HTML CSS"},
    ],
    "Ruby": [
        {"youtubeId": "t_ispmWmdjY", "title": "Ruby Programming Language - Full Course"},
        {"youtubeId": "fmyvWz5TUWg", "title": "Learn Ruby on Rails - Full Course"},
        {"youtubeId": "ml5sNqftiK4", "title": "Ruby in 100 Seconds"},
    ],
    "R": [
        {"youtubeId": "_V8eKsto3Ug", "title": "R Programming Tutorial - Learn R"},
        {"youtubeId": "KlsYCECWEWE", "title": "R Programming Full Course for Beginners"},
        {"youtubeId": "fDRa82lxzaU", "title": "R in 100 Seconds"},
    ],
    "Rust": [
        {"youtubeId": "BpPEoZW5IiY", "title": "Rust Programming Course for Beginners"},
        {"youtubeId": "OX9HJsJUDxA", "title": "Learn Rust Programming - Complete Course"},
        {"youtubeId": "5C_HPTJg5ek", "title": "Rust in 100 Seconds"},
    ],
    "Perl": [
        {"youtubeId": "WEghIXs8F6c", "title": "Perl Programming Tutorial for Beginners"},
        {"youtubeId": "PjMhcMBogCw", "title": "Learn Perl - Full Course"},
        {"youtubeId": "PjMhcMBogCw", "title": "Perl Tutorial - Complete Guide"},
    ],
    "Dart": [
        {"youtubeId": "Ej_Pcr4uC2Q", "title": "Dart Programming Tutorial - Full Course"},
        {"youtubeId": "VPvVD8t02U8", "title": "Flutter & Dart - Complete Guide"},
        {"youtubeId": "NrO0CJCbYLA", "title": "Dart in 100 Seconds"},
    ],
    "Bash": [
        {"youtubeId": "tK9Oc6AEnR4", "title": "Bash Scripting Tutorial for Beginners"},
        {"youtubeId": "SPwyp2NG-bE", "title": "Bash in 100 Seconds"},
        {"youtubeId": "oxuRxtrO2Ag", "title": "Linux Command Line Full Course"},
    ],
    "Java": [
        {"youtubeId": "grEKMHGYyns", "title": "Java Tutorial for Beginners - Full Course"},
        {"youtubeId": "eIrMbAQSU34", "title": "Java Programming Full Course"},
        {"youtubeId": "l9AzO1FMgM8", "title": "Java in 100 Seconds"},
    ],
    "Swift": [
        {"youtubeId": "comQ1-x2a1Q", "title": "Swift Programming Tutorial - Full Course"},
        {"youtubeId": "CwA1VWP0Ldw", "title": "Swift Tutorial for Beginners"},
        {"youtubeId": "nAchMctX4YA", "title": "Swift in 100 Seconds"},
    ],
    "C#": [
        {"youtubeId": "GhQdlMFjVpI", "title": "C# Tutorial - Full Course for Beginners"},
        {"youtubeId": "M5ugY7fWydE", "title": "C# Full Course - Learn C# in 10 Hours"},
        {"youtubeId": "ravLFzIGuCM", "title": "C# in 100 Seconds"},
    ],
    "MATLAB": [
        {"youtubeId": "7f50sQYjNRA", "title": "MATLAB Tutorial for Beginners - Full Course"},
        {"youtubeId": "T_ekAD7U-wA", "title": "Complete MATLAB Programming Course"},
        {"youtubeId": "0w9NKt6Fixk", "title": "MATLAB Crash Course"},
    ],
    "PHP": [
        {"youtubeId": "OK_JCtrrv-c", "title": "PHP For Beginners - Full Course"},
        {"youtubeId": "BUCiSSyIGGU", "title": "Learn PHP - Full Course for Beginners"},
        {"youtubeId": "a7_WFUlFS94", "title": "PHP in 100 Seconds"},
    ],
    "Python": [
        {"youtubeId": "rfscVS0vtbw", "title": "Learn Python - Full Course for Beginners"},
        {"youtubeId": "_uQrJ0TkZlc", "title": "Python Tutorial - Python Full Course"},
        {"youtubeId": "x7X9w_GIm1s", "title": "Python in 100 Seconds"},
    ],
    "JavaScript": [
        {"youtubeId": "PkZNo7MFNFg", "title": "Learn JavaScript - Full Course for Beginners"},
        {"youtubeId": "W6NZfCO5SIk", "title": "JavaScript Tutorial Full Course"},
        {"youtubeId": "DHjqpvDnNGE", "title": "JavaScript in 100 Seconds"},
    ],
    "C": [
        {"youtubeId": "KJgsSFOSQv0", "title": "C Programming Tutorial for Beginners"},
        {"youtubeId": "87SH2Cn0s9A", "title": "C Full Course - Learn C in 6 Hours"},
        {"youtubeId": "U3aXWizDbQ4", "title": "C in 100 Seconds"},
    ],
    "C++": [
        {"youtubeId": "vLnPwxZdW4Y", "title": "C++ Tutorial for Beginners - Full Course"},
        {"youtubeId": "8jLOx1hD3_o", "title": "C++ Full Course - freeCodeCamp"},
        {"youtubeId": "MNeX4EGtR5Y", "title": "C++ in 100 Seconds"},
    ],
}

# Fill missing
updated = 0
for m in missing:
    lang = m["lang"]
    vid_templates = LANG_VIDEOS.get(lang, [])
    if not vid_templates:
        print(f"  No fallback videos for language: {lang}")
        continue

    videos = []
    for v in vid_templates:
        videos.append({
            "id": f"yt_{v['youtubeId']}",
            "title": v["title"],
            "language": lang,
            "youtubeId": v["youtubeId"],
            "thumbnail": f"https://i.ytimg.com/vi/{v['youtubeId']}/mqdefault.jpg",
            "duration": "",
        })

    db.topics.update_one({"id": m["id"]}, {"$set": {"recommendedVideos": videos}})
    updated += 1

print(f"\nUpdated {updated}/{len(missing)} topics with curated videos.")

# Final verify
still = 0
for t in db.topics.find({}, {"_id": 0, "recommendedVideos": 1}):
    vids = t.get("recommendedVideos", [])
    if not vids or len(vids) == 0:
        still += 1
print(f"Still missing videos: {still}")
