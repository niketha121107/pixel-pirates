"""
PROGRESS DASHBOARD - API EXAMPLES AND RESPONSES
Demonstrates all new endpoints with example requests and responses
"""

# =====================================================
# ENDPOINT 1: GET /progress/dashboard-metrics
# =====================================================
# Complete dashboard data in single call
# Used by: Student Progress page to render entire dashboard

REQUEST:
GET /progress/dashboard-metrics
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Accept: application/json

RESPONSE (200 OK):
{
  "success": true,
  "message": "Dashboard metrics retrieved",
  "data": {
    "metrics": {
      "topics_done": 2,
      "total_topics": 200,
      "avg_score": 31.7,
      "time_learned_seconds": 374494,      # 104:01:34
      "avg_understanding": 73.3,
      "completion_percentage": 1.0
    },
    "learning_progress_graph": [
      {
        "day": "Fri",
        "date": "2026-03-20",
        "engagement": 0
      },
      {
        "day": "Sat",
        "date": "2026-03-21",
        "engagement": 0
      },
      {
        "day": "Sun",
        "date": "2026-03-22",
        "engagement": 0
      },
      {
        "day": "Mon",
        "date": "2026-03-23",
        "engagement": 0
      },
      {
        "day": "Tue",
        "date": "2026-03-24",
        "engagement": 0
      },
      {
        "day": "Wed",
        "date": "2026-03-25",
        "engagement": 1.0
      },
      {
        "day": "Thu",
        "date": "2026-03-26",
        "engagement": 0.75
      }
    ],
    "pie_chart": {
      "completed": 2,
      "remaining": 198,
      "completion_percentage": 1.0
    },
    "completed_topics": [
      {
        "topic_name": "Control Structures",
        "topic_id": "control_structures",
        "score": 50,
        "total": 100,
        "percentage": 50.0,
        "date_completed": "26/03/2026",
        "understanding_level": 70,
        "time_spent": "02:00:00",
        "time_spent_seconds": 7200,
        "attempts": 1
      },
      {
        "topic_name": "Syntax & Variables",
        "topic_id": "syntax_vars",
        "score": 30,
        "total": 40,
        "percentage": 75.0,
        "date_completed": "25/03/2026",
        "understanding_level": 75,
        "time_spent": "00:30:00",
        "time_spent_seconds": 1800,
        "attempts": 1
      },
      {
        "topic_name": "Data Types",
        "topic_id": "data_types",
        "score": 30,
        "total": 40,
        "percentage": 75.0,
        "date_completed": "25/03/2026",
        "understanding_level": 85,
        "time_spent": "01:00:00",
        "time_spent_seconds": 3600,
        "attempts": 1
      }
    ],
    "understanding_feedback": {
      "has_feedback": true,
      "records": [
        {
          "user_id": "user_123",
          "topic_id": "data_types",
          "confidence_level": 85,
          "notes": "Understood well",
          "saved_at": "2026-03-25T14:45:00",
          "id": "641f..."
        },
        {
          "user_id": "user_123",
          "topic_id": "syntax_vars",
          "confidence_level": 75,
          "notes": "Need more practice",
          "saved_at": "2026-03-25T16:20:00",
          "id": "641f..."
        },
        {
          "user_id": "user_123",
          "topic_id": "control_structures",
          "confidence_level": 70,
          "notes": "Some concepts unclear",
          "saved_at": "2026-03-26T13:10:00",
          "id": "641f..."
        }
      ]
    }
  }
}

# =====================================================
# ENDPOINT 2: GET /progress/learning-progress-graph
# =====================================================
# Separate endpoint for just the graph data

REQUEST:
GET /progress/learning-progress-graph
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

RESPONSE (200 OK):
{
  "success": true,
  "message": "Learning progress graph retrieved",
  "data": [
    {
      "day": "Fri",
      "date": "2026-03-20",
      "engagement": 0
    },
    {
      "day": "Sat",
      "date": "2026-03-21",
      "engagement": 0
    },
    {
      "day": "Sun",
      "date": "2026-03-22",
      "engagement": 0
    },
    {
      "day": "Mon",
      "date": "2026-03-23",
      "engagement": 0
    },
    {
      "day": "Tue",
      "date": "2026-03-24",
      "engagement": 0
    },
    {
      "day": "Wed",
      "date": "2026-03-25",
      "engagement": 1.0
    },
    {
      "day": "Thu",
      "date": "2026-03-26",
      "engagement": 0.75
    }
  ]
}

# =====================================================
# ENDPOINT 3: GET /progress/completed-topics-scores
# =====================================================
# Separate endpoint for just completed topics

REQUEST:
GET /progress/completed-topics-scores
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

RESPONSE (200 OK):
{
  "success": true,
  "message": "Completed topics retrieved",
  "data": {
    "topics": [
      {
        "topic_name": "Control Structures",
        "topic_id": "control_structures",
        "score": 50,
        "total": 100,
        "percentage": 50.0,
        "date_completed": "26/03/2026",
        "understanding_level": 70,
        "time_spent": "02:00:00",
        "time_spent_seconds": 7200,
        "attempts": 1
      },
      {
        "topic_name": "Syntax & Variables",
        "topic_id": "syntax_vars",
        "score": 30,
        "total": 40,
        "percentage": 75.0,
        "date_completed": "25/03/2026",
        "understanding_level": 75,
        "time_spent": "00:30:00",
        "time_spent_seconds": 1800,
        "attempts": 1
      },
      {
        "topic_name": "Data Types",
        "topic_id": "data_types",
        "score": 30,
        "total": 40,
        "percentage": 75.0,
        "date_completed": "25/03/2026",
        "understanding_level": 85,
        "time_spent": "01:00:00",
        "time_spent_seconds": 3600,
        "attempts": 1
      }
    ]
  }
}

# =====================================================
# ENDPOINT 4: POST /progress/understanding-feedback
# =====================================================
# Save confidence slider values

REQUEST:
POST /progress/understanding-feedback
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "topic_id": "data_types",
  "confidence_level": 85,
  "notes": "Understood the basics"
}

RESPONSE (200 OK):
{
  "success": true,
  "message": "Understanding feedback saved",
  "data": {
    "feedback": {
      "user_id": "user_123",
      "topic_id": "data_types",
      "confidence_level": 85,
      "notes": "Understood the basics",
      "saved_at": "2026-03-26T14:45:32",
      "id": "641f7c3d4..."
    }
  }
}

# =====================================================
# ENDPOINT 5: GET /progress/understanding-feedback
# =====================================================
# Retrieve all understanding feedback

REQUEST:
GET /progress/understanding-feedback
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

RESPONSE (200 OK):
{
  "success": true,
  "message": "Understanding feedback retrieved",
  "data": {
    "feedback": [
      {
        "user_id": "user_123",
        "topic_id": "data_types",
        "confidence_level": 85,
        "notes": "Understood the basics",
        "saved_at": "2026-03-26T14:45:32",
        "id": "641f7c3d4..."
      },
      {
        "user_id": "user_123",
        "topic_id": "syntax_vars",
        "confidence_level": 75,
        "notes": "Need more practice",
        "saved_at": "2026-03-26T15:30:10",
        "id": "641f7c3e5..."
      },
      {
        "user_id": "user_123",
        "topic_id": "control_structures",
        "confidence_level": 60,
        "notes": "",
        "saved_at": "2026-03-26T16:15:45",
        "id": "641f7c3f6..."
      }
    ]
  }
}

# =====================================================
# ENDPOINT 6: GET /progress/understanding-feedback?topic_id=data_types
# =====================================================
# Retrieve feedback for specific topic

REQUEST:
GET /progress/understanding-feedback?topic_id=data_types
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

RESPONSE (200 OK):
{
  "success": true,
  "message": "Understanding feedback retrieved",
  "data": {
    "feedback": [
      {
        "user_id": "user_123",
        "topic_id": "data_types",
        "confidence_level": 85,
        "notes": "Understood the basics",
        "saved_at": "2026-03-26T14:45:32",
        "id": "641f7c3d4..."
      }
    ]
  }
}

# =====================================================
# ERROR RESPONSES
# =====================================================

# 401 Unauthorized - Missing or invalid token
STATUS: 401
{
  "success": false,
  "message": "Not authenticated",
  "data": {}
}

# 500 Internal Server Error - Database connection failed
STATUS: 500
{
  "success": false,
  "message": "Internal server error",
  "data": {"error": "Database connection failed"}
}

# =====================================================
# TYPESCRIPT USAGE EXAMPLES
# =====================================================

// React component example
import { useAuth } from '../context/AuthContext';
import { useEffect, useState } from 'react';

export const ProgressDashboard = () => {
  const { user, token } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      const response = await fetch('/progress/dashboard-metrics', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setMetrics(data.data);
      setLoading(false);
    };

    fetchMetrics();
  }, [token]);

  if (loading) return <div>Loading...</div>;

  const { metrics, completed_topics, understanding_feedback } = metrics;

  return (
    <div>
      {/* Topics Done Card */}
      <h2>{metrics.topics_done}/{metrics.total_topics}</h2>
      
      {/* Average Score Card */}
      <h2>{metrics.avg_score}%</h2>
      
      {/* Time Learned - convert seconds to HH:MM:SS */}
      <h2>{formatTime(metrics.time_learned_seconds)}</h2>
      
      {/* Average Understanding */}
      <h2>{metrics.avg_understanding}%</h2>
      
      {/* Pie Chart Data */}
      <PieChart data={metrics.pie_chart} />
      
      {/* Learning Progress Graph */}
      <LineChart data={metrics.learning_progress_graph} />
      
      {/* Completed Topics List */}
      <CompletedTopicsList topics={completed_topics} />
      
      {/* Understanding Feedback */}
      {understanding_feedback.has_feedback && (
        <FeedbackWidget data={understanding_feedback.records} />
      )}
    </div>
  );
};

// Save understanding feedback
const handleSaveFeedback = async (topicId, confidence) => {
  const response = await fetch('/progress/understanding-feedback', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      topic_id: topicId,
      confidence_level: confidence,
      notes: 'Optional note'
    })
  });

  if (response.ok) {
    console.log('Feedback saved!');
  }
};
