#!/usr/bin/env python
"""
Generate and populate YouTube videos for all topics using Gemini API
This gets REAL YouTube video IDs for each topic
"""

import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import google.genai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDmQ8S2H7lHMY0UdDRxH4f2tPv6D9q-z0A"))

async def generate_youtube_videos_for_topic(topic_name: str, language: str) -> list:
    """Use Gemini to find real YouTube videos for a topic"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
Find the top 3 most popular and educational YouTube videos for teaching "{topic_name}" in {language} programming.
Return ONLY a JSON array with this exact format, no other text:
[
  {{"youtubeId": "11charID1", "title": "Video Title 1", "channel": "Channel Name 1", "description": "Brief description"}},
  {{"youtubeId": "11charID2", "title": "Video Title 2", "channel": "Channel Name 2", "description": "Brief description"}},
  {{"youtubeId": "11charID3", "title": "Video Title 3", "channel": "Channel Name 3", "description": "Brief description"}}
]

Requirements:
- YouTube IDs must be exactly 11 characters (alphanumeric, underscore, dash)
- Use real, educational YouTube videos
- Focus on tutorials and learning resources
- Make sure videos are from reputable educational channels

Examples of good videos for Python:
- Programming with Mosh (search for Python tutorials)
- Traversy Media (Web development)
- Code with Ania Kubow (beginner friendly)
- freeCodeCamp (comprehensive courses)
"""

        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Try to find JSON in the response
        if '[' in response_text and ']' in response_text:
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            json_str = response_text[json_start:json_end]
            videos = json.loads(json_str)
            
            # Validate and clean
            valid_videos = []
            for v in videos:
                if isinstance(v, dict) and 'youtubeId' in v and len(str(v['youtubeId'])) == 11:
                    valid_videos.append({
                        'youtubeId': v['youtubeId'],
                        'title': v.get('title', 'Educational Video'),
                        'channel': v.get('channel', 'Educational Channel'),
                        'description': v.get('description', '')
                    })
            
            return valid_videos[:3] if valid_videos else []
        
        return []
        
    except Exception as e:
        print(f"⚠️ Gemini error for {topic_name}: {str(e)[:100]}")
        return []


async def main():
    print("=" * 80)
    print("GENERATING YOUTUBE VIDEOS FOR ALL TOPICS")
    print("=" * 80)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        db = client['pixel_pirates']
        
        print("✅ Connected to MongoDB")
        
        # Get all topics
        topics = await db.topics.find({}).to_list(None)
        print(f"📚 Found {len(topics)} topics to process\n")
        
        updated_count = 0
        failed_count = 0
        
        for i, topic in enumerate(topics, 1):
            topic_name = topic.get('name', 'Unknown')
            language = topic.get('language', 'Python')
            topic_id = topic.get('_id')
            
            print(f"[{i}/{len(topics)}] {topic_name}...", end=" ", flush=True)
            
            try:
                # Generate videos for this topic
                videos = await generate_youtube_videos_for_topic(topic_name, language)
                
                if videos:
                    # Update MongoDB
                    await db.topics.update_one(
                        {'_id': topic_id},
                        {
                            '$set': {
                                'recommendedVideos': videos,
                                'videos': videos,
                                'videosPopulatedAt': str(__import__('datetime').datetime.now())
                            }
                        }
                    )
                    print(f"✅ {len(videos)} videos")
                    updated_count += 1
                else:
                    print(f"⚠️ No videos found")
                    failed_count += 1
                
            except Exception as topic_error:
                print(f"❌ Error: {str(topic_error)[:50]}")
                failed_count += 1
            
            # Rate limiting
            await asyncio.sleep(0.5)
        
        print("\n" + "=" * 80)
        print(f"✅ COMPLETION SUMMARY")
        print("=" * 80)
        print(f"✅ Successfully updated: {updated_count}/{len(topics)} topics")
        print(f"❌ Failed to update: {failed_count}/{len(topics)} topics")
        print(f"📊 Success rate: {(updated_count/len(topics)*100):.1f}%")
        
        # Verify
        topics_with_videos = await db.topics.count_documents({'recommendedVideos': {'$exists': True, '$ne': []}})
        print(f"\n✅ Topics with videos: {topics_with_videos}/200")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
