# Student Progress Script Update

## Overview
Updated the progress script to implement comprehensive dashboard metrics, learning progress tracking, and understanding feedback system according to specifications.

## How the Script Works

### 1. Learning Progress Graph
- **Score Mapping:**
  - 0% → 0
  - 1–25% → 0.25
  - 26–50% → 0.5
  - 51–75% → 0.75
  - 76–100% → 1
- **Feature:** Plots engagement levels against completion dates for the past 7 days
- **Output:** Line graph showing daily progress with engagement scores

### 2. Metrics Updates
- **Topics Done:** Counts completed topics (status="completed" OR score ≥ 70%)
- **Avg Score:** Calculated from all quiz scores across completed topics
- **Time Learned:** Accumulated from time spent per topic (converted to HH:MM:SS format)
- **Avg Understanding:** Average of self-assessed confidence values from the understanding slider
- **Output:** Metrics table with formatted values for dashboard display

### 3. Pie Chart Completion
- **Formula:** Completion = (Topics Done / Total Topics) × 100
- **Calculation:** Automatically updated based on completed topics count
- **Output:** Pie chart showing completed vs remaining topics with percentage

### 4. Completed Topics & Scores
- **Fields per Topic:**
  - Topic name
  - Completion date (DD/MM/YYYY format)
  - Quiz score and total (e.g., 30/40)
  - Score percentage
  - Understanding level (from confidence slider)
  - Time spent (HH:MM:SS format)
  - Number of attempts
- **Reattempts Behavior:** Update score/date but don't increase Topics Done
- **Output:** CSV-exportable list of all completed topics sorted by date (most recent first)

### 5. Understanding Feedback
- **Data Source:** Confidence slider values saved per topic (0-100%)
- **Integration:** 
  - Feeds into Avg Understanding calculation
  - Displayed in topic records
  - Stored in dedicated understanding_feedback collection
- **Output:** Integrated into metrics and topic records

### 6. Data Integrity
- **User Isolation:** All queries scoped to `user_id` from JWT token
- **Prevention:** One student's data cannot be visible to another
- **Implementation:** Enforced at database query level in all functions

## New Endpoints

### 1. `/progress/dashboard-metrics` (GET)
Returns complete dashboard metrics in a single call:
```json
{
  "metrics": {
    "topics_done": 2,
    "total_topics": 200,
    "avg_score": 31.7,
    "time_learned_seconds": 374494,
    "avg_understanding": 0.0,
    "completion_percentage": 1.0
  },
  "learning_progress_graph": [...],
  "pie_chart": {...},
  "completed_topics": [...],
  "understanding_feedback": {...}
}
```

### 2. `/progress/learning-progress-graph` (GET)
Returns 7-day learning progress data with engagement levels:
```json
{
  "day": "Wed",
  "date": "2026-03-26",
  "engagement": 0.75
}
```

### 3. `/progress/completed-topics-scores` (GET)
Returns detailed list of completed topics with all metrics

### 4. `/progress/understanding-feedback` (POST)
Saves confidence slider feedback for a topic:
```json
{
  "topic_id": "data_types",
  "confidence_level": 75,
  "notes": "Optional notes"
}
```

### 5. `/progress/understanding-feedback` (GET)
Retrieves saved understanding feedback

## Data Model Updates

### Understanding Feedback Collection
```json
{
  "user_id": "user123",
  "topic_id": "data_types",
  "confidence_level": 75,
  "notes": "",
  "saved_at": "2026-03-26T10:30:00",
  "created_at": "2026-03-26T10:30:00"
}
```

### Progress Record (Enhanced)
```json
{
  "user_id": "user123",
  "topic_id": "data_types",
  "time_spent": 3600,
  "quiz_score": 30,
  "quiz_total": 40,
  "status": "completed",
  "attempts": 1,
  "updated_at": "2026-03-25T15:30:00",
  "created_at": "2026-03-25T14:00:00"
}
```

## Key Functions

### `calculate_progress_metrics(user_id)`
Main function that aggregates all dashboard data:
- Fetches all progress records
- Calculates metrics
- Generates learning graph data
- Compiles completed topics list
- Retrieves understanding feedback

### `map_score_to_engagement(percentage)`
Converts quiz scores to engagement levels (0-1)

### `get_learning_progress_graph(user_id)`
Generates 7-day engagement data with score mapping

### `get_completed_topics_with_scores(user_id)`
Returns formatted list of completed topics

### `save_understanding_feedback(user_id, topic_id, data)`
Stores confidence slider values

### `get_understanding_feedback(user_id, topic_id=None)`
Retrieves understanding feedback records

## Frontend Integration

The Progress.tsx component now fetches from the `/progress/dashboard-metrics` endpoint which provides all required data in a single call, improving performance and data consistency.

## Testing

Test the endpoints with:
```bash
# Get dashboard metrics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/progress/dashboard-metrics

# Save understanding feedback
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic_id": "data_types", "confidence_level": 75}' \
  http://localhost:8000/progress/understanding-feedback

# Get learning progress graph
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/progress/learning-progress-graph

# Get completed topics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/progress/completed-topics-scores
```

## Files Modified

1. **backend/app/routes/progress.py**
   - Added 5 new endpoints
   - Updated data models
   - Added Pydantic models for feedback

2. **backend/app/data/__init__.py**
   - Added understanding feedback management functions
   - Added score mapping function
   - Added comprehensive metrics calculation
   - Added learning progress graph generation
   - Added completed topics aggregation

## Notes

- All time values are stored in seconds internally and converted to HH:MM:SS for display
- Topics are marked as completed when status="completed" OR score ≥ 70%
- Understanding feedback is optional but enhances the Avg Understanding metric
- Data is isolated per user through user_id from JWT token
- Graph data always covers the past 7 days
