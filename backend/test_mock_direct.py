#!/usr/bin/env python3
"""
Direct test of mock test generation without authentication
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_mock_generation():
    """Test the mock test service directly"""
    from app.services.mock_test_service import mock_test_service
    
    print("🧪 Testing Gemini-powered mock test generation...")
    print("=" * 60)
    
    topics = "Python Data Structures and Algorithms"
    num_questions = 5
    
    print(f"📝 Generating {num_questions} questions for: {topics}")
    print()
    
    try:
        questions = await mock_test_service.generate_mock_test_questions(
            topic_name=topics,
            num_questions=num_questions,
            question_types=["multiple_choice", "fill_blank", "short_answer"]
        )
        
        print(f"✅ SUCCESS! Generated {len(questions)} questions using Gemini AI\n")
        
        for i, q in enumerate(questions, 1):
            print(f"Question {i}:")
            print(f"  Type: {q.get('question_type', 'N/A')}")
            print(f"  Difficulty: {q.get('difficulty', 'N/A')}")
            
            question_text = q.get('question', 'N/A')
            if len(question_text) > 80:
                question_text = question_text[:77] + "..."
            print(f"  Q: {question_text}")
            
            if q.get('options'):
                print(f"  Options: {q.get('options')}")
            
            print(f"  Answer: {q.get('correct_answer', 'N/A')}")
            explanation = q.get('explanation', 'N/A')
            if len(explanation) > 80:
                explanation = explanation[:77] + "..."
            print(f"  Explanation: {explanation}")
            print()
        
        print("=" * 60)
        print("✅ All questions were generated using Gemini AI!")
        print("   The mock test now generates fresh questions instead of")
        print("   returning stored data.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mock_generation())
    sys.exit(0 if result else 1)
