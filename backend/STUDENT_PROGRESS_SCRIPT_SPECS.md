# 📊 Student Progress Script - Detailed Specifications

**Last Updated:** March 26, 2026  
**Status:** Implementation Complete ✅

---

## Overview

The Student Progress Script powers the Student Progress dashboard page with comprehensive metrics calculation, learning progress tracking, and understanding feedback integration. All features are implemented with user data isolation and security.

---

## How the Script Works

### 1. Learning Progress Graph

**Purpose:** Track engagement levels over time with score mapping

**Score Mapping:**
- 0% → 0 (No engagement)
- 1–25% → 0.25 (Low engagement)
- 26–50% → 0.5 (Medium engagement)
- 51–75% → 0.75 (High engagement)
- 76–100% → 1 (Full engagement)

**Implementation:**
- Plots engagement levels against completion dates
- Tracks the past 7 days of learning activity
- Each quiz score is mapped to an engagement value using the mapping above
- Daily engagement is accumulated from all completed quizzes on that day

**Output:** A line graph showing daily progress with engagement scores for each day

**API Endpoint:**
```
GET /progress/learning-progress-graph
```

**Response Data:**
```json
[
  {
    "day": "Wed",
    "date": "2026-03-26",
    "engagement": 0.75
  },
  {
    "day": "Thu",
    "date": "2026-03-27",
    "engagement": 1.0
  }
]
```

---

### 2. Metrics Updates

**Purpose:** Calculate and update all student performance metrics

**Metrics Calculated:**

1. **Topics Done**
   - Formula: Count of topics where status="completed" OR quiz_score ≥ 70%
   - Represents topics the student has mastered

2. **Avg Score**
   - Formula: Mean of all quiz_score percentages
   - Recalculated from all quiz attempts across all topics

3. **Time Learned**
   - Formula: Sum of all time_spent values per topic
   - Accumulated from every minute spent learning
   - Formatted as HH:MM:SS for display

4. **Avg Understanding**
   - Formula: Average of all self-assessed confidence values
   - Values collected from the confidence slider (0-100%)
   - Represents student's perceived comprehension level

5. **Completion Percentage**
   - Formula: (Topics Done / Total Topics) × 100
   - Direct visual representation of learning progress

**Output:** Metrics table with all calculated values

**API Endpoint:**
```
GET /progress/dashboard-metrics
```

**Response Data:**
```json
{
  "metrics": {
    "topics_done": 2,
    "total_topics": 200,
    "avg_score": 31.7,
    "time_learned_seconds": 374494,        // 104:01:34
    "avg_understanding": 73.3,
    "completion_percentage": 1.0
  }
}
```

---

### 3. Pie Chart Completion

**Purpose:** Visual representation of learning progress

**Formula:**
$$\text{Completion} = \frac{\text{Topics Done}}{\text{Total Topics}} \times 100$$

**Data Structure:**
- **completed:** Count of topics the student has completed
- **remaining:** Total topics minus completed topics
- **completion_percentage:** Calculated completion percentage

**Output:** Pie chart data showing completed vs remaining topics

**API Endpoint:**
```
GET /progress/dashboard-metrics (included in response)
```

**Response Data:**
```json
{
  "pie_chart": {
    "completed": 2,
    "remaining": 198,
    "completion_percentage": 1.0
  }
}
```

---

### 4. Completed Topics & Scores

**Purpose:** Detailed record of all completed topics with comprehensive metrics

**Data Included per Topic:**
1. **topic_name** - Display name of the topic
2. **date_completed** - Date of completion (formatted DD/MM/YYYY)
3. **score** - Numerical quiz score (e.g., 30/40)
4. **percentage** - Score as percentage (e.g., 75%)
5. **understanding_level** - Student's self-assessed confidence (0-100%)
6. **time_spent** - Time spent on topic (formatted HH:MM:SS)
7. **topic_id** - Unique identifier for the topic
8. **attempts** - Number of quiz attempts

**Special Rules:**
- Reattempts update score/date but don't increase Topics Done counter
- Only topics with status="completed" OR score ≥ 70% are included
- Sorted by date (most recent first)
- Prevents double-counting when students retake quizzes

**Output:** CSV file with all topic records and metrics

**API Endpoint:**
```
GET /progress/completed-topics-scores
```

**Response Data:**
```json
[
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
  },
  {
    "topic_name": "Syntax & Variables",
    "topic_id": "syntax_variables",
    "score": 30,
    "total": 40,
    "percentage": 75.0,
    "date_completed": "25/03/2026",
    "understanding_level": 80,
    "time_spent": "00:45:30",
    "time_spent_seconds": 2730,
    "attempts": 1
  }
]
```

**Date Format Examples:**
- March 25, 2026 → 25/03/2026
- January 5, 2026 → 05/01/2026

---

### 5. Understanding Feedback

**Purpose:** Integrate student self-assessment of comprehension

**Confidence Slider:**
- Range: 0-100% (represents how well student understands the topic)
- Stored after each quiz completion
- Optional but recommended for complete metrics

**Integration Points:**
1. **Saving Feedback**
   - API Endpoint: `POST /progress/understanding-feedback`
   - Stores confidence slider value with topic_id
   - Timestamp automatically recorded

2. **Retrieving Feedback**
   - API Endpoint: `GET /progress/understanding-feedback`
   - Returns all confidence values for the student

3. **Metrics Impact**
   - Avg Understanding is Average of all confidence values
   - If no feedback recorded, Avg Understanding = 0%
   - Feedback updates are immediate and reflected in next metrics call

**API Endpoints:**

Save Feedback:
```
POST /progress/understanding-feedback
```

Request Body:
```json
{
  "topic_id": "data_types",
  "confidence_level": 85
}
```

Retrieve Feedback:
```
GET /progress/understanding-feedback
```

Response:
```json
{
  "records": [
    {
      "topic_id": "data_types",
      "confidence_level": 85,
      "saved_at": "2026-03-25T10:30:00"
    },
    {
      "topic_id": "syntax_variables",
      "confidence_level": 80,
      "saved_at": "2026-03-25T11:45:00"
    }
  ]
}
```

---

### 6. Data Integrity

**Purpose:** Ensure data security and prevent cross-student data access

**User Isolation Enforcement:**
- All database queries are scoped to `CURRENT_USER_ID`
- Every function receives `user_id` parameter for validation
- Database filters applied at query time (prevents late-binding vulnerabilities)
- No student can see another student's data

**Security Features:**
1. **JWT Token Auth**
   - User identity extracted from token in every request
   - Token verified server-side before allowing data access

2. **Database Filtering**
   - Every query includes `WHERE user_id = CURRENT_USER_ID`
   - Applied at data layer before returning results

3. **Query Patterns:**
   ```python
   # CORRECT - Filtered by user
   progress_records = get_topic_progress(user_id)
   
   # Retrieved data is automatically scoped
   feedback = get_understanding_feedback(user_id)
   ```

4. **Prevents:**
   - Cross-student data leaks
   - Unauthorized access to other students' metrics
   - Data tampering or manipulation
   - Unauthorized score modifications

**Implementation:**
- All data layer functions validate `user_id` parameter
- API routes extract user from authentication token
- Query results filtered before serialization
- Logging includes user_id for audit trails

---

## Complete Dashboard Response

**All Dashboard Data in Single Call:**

```
GET /progress/dashboard-metrics
```

**Response Structure:**
```json
{
  "success": true,
  "message": "Dashboard metrics retrieved",
  "data": {
    "metrics": {
      "topics_done": 2,
      "total_topics": 200,
      "avg_score": 31.7,
      "time_learned_seconds": 374494,
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
        "engagement": 0.5
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
      },
      {
        "topic_name": "Syntax & Variables",
        "topic_id": "syntax_variables",
        "score": 30,
        "total": 40,
        "percentage": 75.0,
        "date_completed": "25/03/2026",
        "understanding_level": 80,
        "time_spent": "00:45:30",
        "time_spent_seconds": 2730,
        "attempts": 1
      }
    ],
    "understanding_feedback": {
      "has_feedback": true,
      "records": [
        {
          "topic_id": "data_types",
          "confidence_level": 85,
          "saved_at": "2026-03-25T10:30:00"
        }
      ]
    }
  }
}
```

---

## Implementation Files

| File | Purpose |
|------|---------|
| `app/routes/progress.py` | 5 API endpoints for progress data |
| `app/data/__init__.py` | 6 core data functions |
| `test_progress_dashboard.py` | Comprehensive test suite |

---

## Key Functions Reference

### `map_score_to_engagement(percentage: float) -> float`
Converts quiz score percentage to engagement level (0-1)

### `calculate_progress_metrics(user_id: str) -> dict`
Main function aggregating all dashboard data in single call

### `get_learning_progress_graph(user_id: str) -> list`
Generates 7-day engagement data with score mapping

### `get_completed_topics_with_scores(user_id: str) -> list`
Returns formatted list of completed topics with scores

### `save_understanding_feedback(user_id: str, topic_id: str, data: dict)`
Stores confidence slider values per user and topic

### `get_understanding_feedback(user_id: str, topic_id: str = None) -> list`
Retrieves understanding feedback records (all or specific topic)

---

## Testing

All 6 features are tested in `test_progress_dashboard.py`:
- ✅ Score mapping verification
- ✅ Metrics calculation accuracy
- ✅ Learning progress graph generation
- ✅ Completed topics list formatting
- ✅ Understanding feedback storage/retrieval
- ✅ Complete dashboard integration

Run tests with:
```bash
cd backend
python test_progress_dashboard.py
```

---

## Deployment Status

✅ **PRODUCTION READY**
- All features implemented and tested
- Zero breaking changes
- Backward compatible
- Security verified
- Performance optimized

---

*Specification Version: 1.0*  
*Last Updated: March 26, 2026*
