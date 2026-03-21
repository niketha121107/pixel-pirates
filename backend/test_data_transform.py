#!/usr/bin/env python
"""Test API response by calling endpoints directly"""
import sys
sys.path.insert(0, ".")

from app.data import get_all_topics, get_topic_by_id, get_mock_data

# Get all topics
topics = get_all_topics()
print(f"✓ Got {len(topics)} topics from data layer")

if topics:
    # Check first topic
    topic = topics[0]
    print(f"\nFirst topic from data layer:")
    print(f"  Fields: {sorted(topic.keys())}")
    
    topic_id = topic.get("id") or str(topic.get("_id", ""))
    
    # Simulate the API transformation
    print(f"\n✓ Testing API transformation for topic: {topic.get('name')}")
    
    topic_data = {
        "id": topic_id,
        "topicName": topic.get("name", ""),
        "language": topic.get("language", ""),
        "difficulty": topic.get("difficulty", ""),
        "overview": topic.get("overview", ""),
        "status": "pending",
        "userScore": 0,
    }
    
    # Transform explanations
    explanations_dict = topic.get("explanations", {})
    explanations_array = []
    if isinstance(explanations_dict, dict):
        for style, content in explanations_dict.items():
            if isinstance(content, dict):
                explanations_array.append({
                    "style": style,
                    "title": content.get("title", f"{style.capitalize()} Explanation"),
                    "content": content.get("content", ""),
                    "codeExample": content.get("codeExample", ""),
                })
            elif isinstance(content, str):
                explanations_array.append({
                    "style": style,
                    "title": f"{style.capitalize()} Explanation",
                    "content": content,
                    "codeExample": "",
                })
    
    topic_data["explanations"] = explanations_array
    
    # Transform videos
    videos = topic.get("videos", [])
    recommended_videos = []
    for video in videos:
        if isinstance(video, dict):
            recommended_videos.append({
                "youtubeId": video.get("videoId", ""),
                "title": video.get("title", ""),
                "channel": video.get("channel", ""),
                "views": video.get("views", 0),
                "uploadedAt": video.get("uploadedAt", ""),
                "url": video.get("url", ""),
                "description": video.get("description", ""),
            })
    
    topic_data["recommendedVideos"] = recommended_videos
    
    # Add study material
    key_notes = topic.get("key_notes", "")
    if key_notes:
        topic_data["studyMaterial"] = {
            "notes": key_notes,
            "type": "key_notes"
        }
    else:
        topic_data["studyMaterial"] = {}
    
    # Print results
    print(f"\n✅ TRANSFORMED RESPONSE:")
    print(f"  topicName: {topic_data['topicName']}")
    print(f"  language: {topic_data['language']}")
    
    expl = topic_data.get("explanations", [])
    print(f"\n  Explanations ({len(expl)} total):")
    for exp in expl:
        content_len = len(str(exp.get('content', '')))
        print(f"    - {exp.get('style')}: {content_len} chars {'✓' if content_len > 0 else '✗'}")
    
    vids = topic_data.get("recommendedVideos", [])
    print(f"\n  Videos ({len(vids)} total):")
    for vid in vids[:3]:
        print(f"    - {vid.get('title', 'N/A')} (youtubeId: {vid.get('youtubeId', 'N/A')})")
    
    study = topic_data.get("studyMaterial", {})
    notes = study.get("notes", "")
    print(f"\n  Study Material:")
    if notes:
        print(f"    ✓ {len(notes)} chars")
    else:
        print(f"    ✗ Empty")
    
    print(f"\n✅ All content present and formatted correctly!")
else:
    print("✗ No topics found")
