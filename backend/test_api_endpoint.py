#!/usr/bin/env python3
"""Test study material API endpoint"""

import requests
import json
import time

# Test API endpoint
API_BASE_URL = "http://localhost:8000"

def test_study_material_api():
    """Test generating study materials via API"""
    
    print("=" * 60)
    print("TESTING STUDY MATERIAL API")
    print("=" * 60)
    
    # First, get all topics to find one to use
    print("\n1. Fetching topics from API...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/topics")
        topics = response.json()
        
        if topics and len(topics) > 0:
            topic = topics[0]
            topic_id = str(topic.get("_id", topic.get("id")))
            topic_name = topic.get("name", topic.get("title", "Unknown"))
            print(f"   ✓ Found {len(topics)} topics")
            print(f"   ✓ Testing with topic: {topic_name} (ID: {topic_id})")
        else:
            print("   ✗ No topics found")
            return
    except Exception as e:
        print(f"   ✗ Error fetching topics: {e}")
        return
    
    # Now test generating study materials
    print(f"\n2. Generating study materials for: {topic_name}")
    print("   (This will make API calls to OpenRouter - please wait...)")
    
    try:
        payload = {
            "learning_level": "beginner"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/study-materials/generate/{topic_id}",
            json=payload,
            timeout=120  # 2 minute timeout
        )
        
        if response.status_code == 200:
            material = response.json()
            print(f"   ✓ Study material generated successfully!")
            print(f"   ✓ Generated at: {material.get('generated_at')}")
            print(f"   ✓ Learning level: {material.get('learning_level')}")
            
            # Check for explanations
            explanations = material.get('explanations', {})
            if explanations:
                print(f"   ✓ Explanations generated: {list(explanations.keys())}")
                for level, exp in explanations.items():
                    content_len = len(exp.get('content', ''))
                    print(f"     - {level}: {content_len} characters")
            
            # Check for other content
            concepts = material.get('key_concepts', [])
            questions = material.get('practice_questions', [])
            examples = material.get('real_world_examples', [])
            
            print(f"   ✓ Key concepts: {len(concepts)} generated")
            print(f"   ✓ Practice questions: {len(questions)} generated")
            print(f"   ✓ Real-world examples: {len(examples)} generated")
            
            print("\n✅ API TEST PASSED!")
            return True
        else:
            print(f"   ✗ API error: {response.status_code}")
            print(f"   ✗ Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ✗ Request timed out (API call took too long)")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_study_material_api()
