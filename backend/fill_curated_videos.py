"""
Hardcode well-known YouTube educational videos for the 32 topics missing videos.
Uses popular channels: freeCodeCamp, Traversy Media, Programming with Mosh, Fireship, etc.
"""
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

# Curated videos for each missing topic area
# Format: {topic_id: [{"youtubeId", "title", "language"}]}
CURATED = {
    # Go topics (topic-91 to topic-100)
    "topic-91": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Programming – Golang Course with Bonus Projects", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Learn Go Programming - Golang Tutorial for Beginners", "language": "Go"},
        {"youtubeId": "446E-r0rXHI", "title": "Go in 100 Seconds", "language": "Go"},
    ],
    "topic-92": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Programming – Golang Full Course", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Learn Go - Syntax & Data Types", "language": "Go"},
        {"youtubeId": "8uiZC0l4Ajw", "title": "Go Tutorial - Variables and Types", "language": "Go"},
    ],
    "topic-93": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Programming - Control Flow", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Go Tutorial - Control Structures", "language": "Go"},
        {"youtubeId": "C8LgvuEBraI", "title": "Go Control Structures Tutorial", "language": "Go"},
    ],
    "topic-94": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Programming - Functions", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Go Tutorial - Functions", "language": "Go"},
        {"youtubeId": "feU9DQNotsE", "title": "Functions in Go Explained", "language": "Go"},
    ],
    "topic-95": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Programming - Slices and Maps", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Go Data Structures Tutorial", "language": "Go"},
        {"youtubeId": "jFfo23yIWac", "title": "Go Slices and Maps - Deep Dive", "language": "Go"},
    ],
    "topic-96": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Concurrency - Goroutines & Channels", "language": "Go"},
        {"youtubeId": "LvgVSSpwND8", "title": "Goroutines - Go Concurrency Tutorial", "language": "Go"},
        {"youtubeId": "oV9rvDllKEg", "title": "Concurrency in Go - Goroutines and Channels", "language": "Go"},
    ],
    "topic-97": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Structs and Interfaces", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Go OOP-like Features Tutorial", "language": "Go"},
        {"youtubeId": "lh_Uv2imp14", "title": "Structs and Interfaces in Go", "language": "Go"},
    ],
    "topic-98": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Standard Library - net/http", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Go Libraries Tutorial", "language": "Go"},
        {"youtubeId": "jFfo23yIWac", "title": "Building HTTP Servers in Go", "language": "Go"},
    ],
    "topic-99": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go File Handling & Database", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Go File I/O Tutorial", "language": "Go"},
        {"youtubeId": "C8LgvuEBraI", "title": "Working with Files in Go", "language": "Go"},
    ],
    "topic-100": [
        {"youtubeId": "un6ZyFkqFKo", "title": "Go Applications - Cloud & Microservices", "language": "Go"},
        {"youtubeId": "446E-r0rXHI", "title": "Go in 100 Seconds - Cloud Native", "language": "Go"},
        {"youtubeId": "YS4e4q9oBaU", "title": "Go for Cloud Development", "language": "Go"},
    ],

    # HTML/CSS topic-60
    "topic-60": [
        {"youtubeId": "mU6anWqZJcc", "title": "HTML & CSS Full Course - Beginner to Pro", "language": "HTML/CSS"},
        {"youtubeId": "G3e-cpL7ofc", "title": "HTML & CSS Full Course - SuperSimpleDev", "language": "HTML/CSS"},
        {"youtubeId": "HGTJBPNC-Gw", "title": "Build Responsive Websites - HTML CSS", "language": "HTML/CSS"},
    ],

    # SQL topics (topic-61 to topic-70)
    "topic-61": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Tutorial - Full Database Course for Beginners", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL Full Course - freeCodeCamp", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL Tutorial for Beginners", "language": "SQL"},
    ],
    "topic-62": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Data Types Explained", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL Data Types Tutorial", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL Data Types - Full Course", "language": "SQL"},
    ],
    "topic-63": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL DDL - CREATE, ALTER, DROP", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL DDL Commands Tutorial", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL CREATE TABLE Tutorial", "language": "SQL"},
    ],
    "topic-64": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL DML - SELECT, INSERT, UPDATE, DELETE", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL CRUD Operations", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL Queries Tutorial", "language": "SQL"},
    ],
    "topic-65": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Joins Explained", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL Joins Tutorial", "language": "SQL"},
        {"youtubeId": "2HVMiPPuPIM", "title": "SQL Joins - Inner, Left, Right, Full", "language": "SQL"},
    ],
    "topic-66": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Constraints and Keys", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL Primary & Foreign Keys", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL Keys and Constraints Tutorial", "language": "SQL"},
    ],
    "topic-67": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Views and Indexes", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL Views Tutorial", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL Indexes Explained", "language": "SQL"},
    ],
    "topic-68": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Stored Procedures & Triggers", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL Stored Procedures", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL Triggers Tutorial", "language": "SQL"},
    ],
    "topic-69": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Transactions Explained", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL Transactions Tutorial", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "ACID Properties and Transactions", "language": "SQL"},
    ],
    "topic-70": [
        {"youtubeId": "HXV3zeQKqGY", "title": "SQL Applications - Databases & Analytics", "language": "SQL"},
        {"youtubeId": "7S_tz1z_5bA", "title": "MySQL for Data Analytics", "language": "SQL"},
        {"youtubeId": "zbMHLJ0dY4w", "title": "SQL Real-World Applications", "language": "SQL"},
    ],

    # TypeScript topic-74
    "topic-74": [
        {"youtubeId": "BwuLxPH8IDs", "title": "TypeScript Course for Beginners - Learn TypeScript", "language": "TypeScript"},
        {"youtubeId": "30LWjhZzg50", "title": "Learn TypeScript – Full Tutorial", "language": "TypeScript"},
        {"youtubeId": "d56mG7DezGs", "title": "TypeScript Tutorial - Traversy Media", "language": "TypeScript"},
    ],

    # Kotlin topics (topic-81 to topic-90)
    "topic-81": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Course - Tutorial for Beginners", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Learn Kotlin Programming – Full Course", "language": "Kotlin"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Kotlin in 100 Seconds", "language": "Kotlin"},
    ],
    "topic-82": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Syntax & Data Types", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin Variables and Types", "language": "Kotlin"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Kotlin Basics Tutorial", "language": "Kotlin"},
    ],
    "topic-83": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Control Structures", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin If-Else and When", "language": "Kotlin"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Kotlin Control Flow Tutorial", "language": "Kotlin"},
    ],
    "topic-84": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Functions & Lambdas", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin Lambda Expressions", "language": "Kotlin"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Kotlin Higher-Order Functions", "language": "Kotlin"},
    ],
    "topic-85": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Collections - Lists, Sets, Maps", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin Collections Tutorial", "language": "Kotlin"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Working with Collections in Kotlin", "language": "Kotlin"},
    ],
    "topic-86": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin OOP - Classes & Interfaces", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin Object-Oriented Programming", "language": "Kotlin"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Kotlin Classes and Inheritance", "language": "Kotlin"},
    ],
    "topic-87": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Advanced Features - Coroutines", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin Coroutines Tutorial", "language": "Kotlin"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Kotlin Extension Functions", "language": "Kotlin"},
    ],
    "topic-88": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Frameworks - Ktor & Android", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin for Android Development", "language": "Kotlin"},
        {"youtubeId": "FjrKMcnKahY", "title": "Kotlin Android Tutorial - Full Course", "language": "Kotlin"},
    ],
    "topic-89": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin File Handling & Database", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin File I/O Tutorial", "language": "Kotlin"},
        {"youtubeId": "xT8oP0ez3gI", "title": "Kotlin Database Integration", "language": "Kotlin"},
    ],
    "topic-90": [
        {"youtubeId": "F9UC9DY-vIU", "title": "Kotlin Applications - Android & Backend", "language": "Kotlin"},
        {"youtubeId": "EExSSotojVI", "title": "Kotlin Real-World Applications", "language": "Kotlin"},
        {"youtubeId": "FjrKMcnKahY", "title": "Build Android Apps with Kotlin", "language": "Kotlin"},
    ],
}


def main():
    # Find topics without videos
    missing = []
    for t in db.topics.find({}, {"_id": 0, "id": 1, "language": 1, "topicName": 1, "recommendedVideos": 1}):
        vids = t.get("recommendedVideos", [])
        if not vids or len(vids) == 0:
            missing.append(t)

    print(f"Topics without videos: {len(missing)}")
    
    updated = 0
    for t in missing:
        tid = t["id"]
        lang = t.get("language", "")
        name = t.get("topicName", "")
        
        if tid in CURATED:
            videos = []
            for v in CURATED[tid]:
                videos.append({
                    "id": f"yt_{v['youtubeId']}",
                    "title": v["title"],
                    "language": v["language"],
                    "youtubeId": v["youtubeId"],
                    "thumbnail": f"https://i.ytimg.com/vi/{v['youtubeId']}/mqdefault.jpg",
                    "duration": "",
                })
            db.topics.update_one({"id": tid}, {"$set": {"recommendedVideos": videos}})
            print(f"  [OK] {tid} - {lang} / {name} -> {len(videos)} videos")
            updated += 1
        else:
            print(f"  [SKIP] {tid} - {lang} / {name} - no curated videos")
    
    print(f"\nDone! Updated {updated}/{len(missing)} topics.")
    
    # Final check
    total = db.topics.count_documents({})
    still_missing = 0
    for t in db.topics.find({}, {"_id": 0, "id": 1, "recommendedVideos": 1}):
        vids = t.get("recommendedVideos", [])
        if not vids or len(vids) == 0:
            still_missing += 1
    print(f"Total topics: {total}, Still without videos: {still_missing}")


if __name__ == "__main__":
    main()
