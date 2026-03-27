"""
Test script for new Progress Dashboard Endpoints
Tests all new metrics calculation and feedback functions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from app.data import (
    save_topic_progress,
    get_topic_progress,
    save_understanding_feedback,
    get_understanding_feedback,
    calculate_progress_metrics,
    get_learning_progress_graph,
    get_completed_topics_with_scores,
    map_score_to_engagement,
    MOCK_USERS,
    MOCK_TOPICS,
)

def setup_test_data():
    """Create test user and topics"""
    test_user_id = "test_user_123"
    
    # Create mock user
    MOCK_USERS[test_user_id] = {
        "id": test_user_id,
        "name": "Test Student",
        "completedTopics": [],
        "inProgressTopics": [],
        "quizScores": {},
        "totalHours": 0,
    }
    
    # Create mock topics
    topics = [
        {"id": "data_types", "topicName": "Data Types"},
        {"id": "syntax_vars", "topicName": "Syntax & Variables"},
        {"id": "control_structures", "topicName": "Control Structures"},
    ]
    
    for topic in topics:
        MOCK_TOPICS[topic["id"]] = topic
    
    return test_user_id, topics

def test_score_mapping():
    """Test score to engagement mapping"""
    print("\n" + "="*60)
    print("TEST 1: Score to Engagement Mapping")
    print("="*60)
    
    test_cases = [
        (0, 0),
        (10, 0.25),
        (25, 0.25),
        (50, 0.5),
        (75, 0.75),
        (100, 1.0),
    ]
    
    for score, expected in test_cases:
        result = map_score_to_engagement(score)
        status = "✓" if result == expected else "✗"
        print(f"{status} Score {score}% → Engagement {result} (expected {expected})")

def test_topic_progress():
    """Test saving and retrieving topic progress"""
    print("\n" + "="*60)
    print("TEST 2: Topic Progress Tracking")
    print("="*60)
    
    test_user_id, topics = setup_test_data()
    
    # Save progress for Data Types
    progress_1 = save_topic_progress(test_user_id, "data_types", {
        "time_spent": 3600,  # 1 hour
        "quiz_score": 30,
        "quiz_total": 40,
        "status": "completed",
    })
    print(f"✓ Saved progress for Data Types: {progress_1['quiz_score']}/{progress_1['quiz_total']}")
    
    # Save progress for Syntax & Variables
    progress_2 = save_topic_progress(test_user_id, "syntax_vars", {
        "time_spent": 1800,  # 30 minutes
        "quiz_score": 30,
        "quiz_total": 40,
        "status": "completed",
    })
    print(f"✓ Saved progress for Syntax & Variables: {progress_2['quiz_score']}/{progress_2['quiz_total']}")
    
    # Save progress for Control Structures
    progress_3 = save_topic_progress(test_user_id, "control_structures", {
        "time_spent": 7200,  # 2 hours
        "quiz_score": 50,
        "quiz_total": 100,
        "status": "completed",
    })
    print(f"✓ Saved progress for Control Structures: {progress_3['quiz_score']}/{progress_3['quiz_total']}")
    
    # Retrieve all progress
    all_progress = get_topic_progress(test_user_id)
    print(f"✓ Retrieved all progress records: {len(all_progress)} topics")
    
    return test_user_id

def test_understanding_feedback(test_user_id):
    """Test understanding feedback"""
    print("\n" + "="*60)
    print("TEST 3: Understanding Feedback (Confidence Slider)")
    print("="*60)
    
    # Save feedback for different topics
    feedback_1 = save_understanding_feedback(test_user_id, "data_types", {
        "confidence_level": 85,
        "notes": "Understood well"
    })
    print(f"✓ Data Types understanding: {feedback_1['confidence_level']}%")
    
    feedback_2 = save_understanding_feedback(test_user_id, "syntax_vars", {
        "confidence_level": 75,
        "notes": "Need more practice"
    })
    print(f"✓ Syntax & Variables understanding: {feedback_2['confidence_level']}%")
    
    feedback_3 = save_understanding_feedback(test_user_id, "control_structures", {
        "confidence_level": 60,
    })
    print(f"✓ Control Structures understanding: {feedback_3['confidence_level']}%")
    
    # Retrieve all feedback
    all_feedback = get_understanding_feedback(test_user_id)
    print(f"✓ Retrieved understanding feedback: {len(all_feedback)} records")

def test_learning_progress_graph(test_user_id):
    """Test learning progress graph generation"""
    print("\n" + "="*60)
    print("TEST 4: Learning Progress Graph (7-Day Engagement)")
    print("="*60)
    
    graph_data = get_learning_progress_graph(test_user_id)
    print(f"✓ Generated 7-day learning progress graph: {len(graph_data)} days")
    
    for entry in graph_data:
        print(f"  {entry['day']}: Engagement {entry['engagement']}")

def test_completed_topics(test_user_id):
    """Test completed topics retrieval"""
    print("\n" + "="*60)
    print("TEST 5: Completed Topics with Scores")
    print("="*60)
    
    completed = get_completed_topics_with_scores(test_user_id)
    print(f"✓ Retrieved completed topics: {len(completed)} topics")
    
    for topic in completed:
        print(f"\n  Topic: {topic['topic_name']}")
        print(f"  Score: {topic['score']}/{topic['total']} ({topic['percentage']}%)")
        print(f"  Understanding: {topic['understanding_level']}%")
        print(f"  Time Spent: {topic['time_spent']}")
        print(f"  Attempts: {topic['attempts']}")

def test_dashboard_metrics(test_user_id):
    """Test complete dashboard metrics calculation"""
    print("\n" + "="*60)
    print("TEST 6: Complete Dashboard Metrics")
    print("="*60)
    
    metrics = calculate_progress_metrics(test_user_id)
    
    print("\n📊 METRICS:")
    m = metrics['metrics']
    print(f"  Topics Done: {m['topics_done']}/{m['total_topics']}")
    print(f"  Average Score: {m['avg_score']}%")
    print(f"  Time Learned: {m['time_learned_seconds']} seconds")
    print(f"  Average Understanding: {m['avg_understanding']}%")
    print(f"  Completion: {m['completion_percentage']}%")
    
    print("\n📈 PIE CHART:")
    pie = metrics['pie_chart']
    print(f"  Completed: {pie['completed']}")
    print(f"  Remaining: {pie['remaining']}")
    print(f"  Percentage: {pie['completion_percentage']}%")
    
    print("\n✅ COMPLETED TOPICS:")
    for topic in metrics['completed_topics']:
        print(f"  • {topic['topic_name']}: {topic['score']}/{topic['total']}")
    
    print("\n📝 UNDERSTANDING FEEDBACK:")
    fb = metrics['understanding_feedback']
    print(f"  Has Feedback: {fb['has_feedback']}")
    print(f"  Records: {len(fb['records'])}")

def main():
    """Run all tests"""
    print("\n" + "🎓 PROGRESS DASHBOARD TESTS 🎓".center(60))
    print("="*60)
    
    # Test 1: Score mapping
    test_score_mapping()
    
    # Test 2: Topic progress
    test_user_id = test_topic_progress()
    
    # Test 3: Understanding feedback
    test_understanding_feedback(test_user_id)
    
    # Test 4: Learning progress graph
    test_learning_progress_graph(test_user_id)
    
    # Test 5: Completed topics
    test_completed_topics(test_user_id)
    
    # Test 6: Dashboard metrics
    test_dashboard_metrics(test_user_id)
    
    print("\n" + "="*60)
    print("✅ All tests completed successfully!")
    print("="*60)

if __name__ == "__main__":
    main()
