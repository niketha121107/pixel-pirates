#!/usr/bin/env python
"""Improve visual explanations with better structure"""
import logging
from pymongo import MongoClient
from app.core.config import Settings
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
topics_col = db.topics

def generate_visual_explanation(topic_name: str, language: str) -> str:
    """Generate improved visual explanation with ASCII diagrams"""
    
    return f"""
## Visual Structure of {topic_name} in {language}

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    {topic_name.upper()}                        │
│                        in {language.upper()}                         │
└────────────────────────────────────────────────────────────────┘
         │
         ├─────────────┬──────────────┬──────────────┐
         │             │              │              │
    Component 1   Component 2    Component 3    Component 4
    ┌─────────┐  ┌─────────┐  ┌─────────────┐  ┌──────────┐
    │ Input   │  │ Process │  │ Error       │  │Optimize  │
    │ Setup   │  │ Logic   │  │ Handling    │  │Performance
    └─────────┘  └─────────┘  └─────────────┘  └──────────┘
         │             │              │              │
         └─────────────┴──────────────┴──────────────┘
                       │
                  ┌────▼─────┐
                  │  Output   │
                  │  Results  │
                  └───────────┘
```

### Conceptual Flow Diagram

```
START
  │
  ├──> Initialize Resources
  │         │
  │         ├──> Load configuration
  │         ├──> Set up variables
  │         └──> Prepare data structures
  │
  ├──> Main Processing
  │         │
  │         ├──> Process data
  │         ├──> Apply logic
  │         └──> Handle operations
  │
  ├──> Error Handling
  │         │
  │         ├──> Check for errors
  │         ├──> Log error information
  │         └──> Apply recovery strategies
  │
  ├──> Finalization
  │         │
  │         ├──> Optimize results
  │         ├──> Format output
  │         └──> Clean up resources
  │
  └──> Return Results
        │
        └──> (DONE)
```

### Module Relationships

```
Code Layer                    Purpose Layer
┌──────────────┐              ┌──────────────────┐
│   {topic_name}              │  Core Purpose    │
│   Functions  │◄────────────►│  Logic           │
└──────────────┘              └──────────────────┘
        │                             │
        ▼                             ▼
┌──────────────┐              ┌──────────────────┐
│Data Structs  │◄────────────►│Memory Management │
│Container     │              │and Optimization  │
└──────────────┘              └──────────────────┘
```

### Data Flow Visualization

```
INPUT DATA
    │
    ▼
┌─────────────────┐
│  Validation     │◄──── Check constraints
│  & Constraints  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Transformation  │◄──── Apply logic
│ & Processing    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Caching &      │◄──── Optimize access
│  Storage        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Output         │◄──── Format results
│  Generation     │
└─────────────────┘
    │
    ▼
OUTPUT & RESULTS
```

### Typical Implementation Structure

```
┌────────────────────────────────────────┐
│        Class/Module Definition         │
├────────────────────────────────────────┤
│                                        │
│  Properties & Variables               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Variable 1: [Type] Purpose          │
│  • Variable 2: [Type] Purpose          │
│  • Variable 3: [Type] Purpose          │
│                                        │
│  Methods & Functions                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Initialize()        Set up          │
│  • Process()           Main logic      │
│  • Validate()          Check inputs    │
│  • Transform()         Convert data    │
│  • Optimize()          Improve perf    │
│  • Cleanup()           Finalize        │
│                                        │
└────────────────────────────────────────┘
```

### Key Visual Concepts

**Concept 1: Layered Architecture**
```
┌─────────────────────────┐
│  Application Layer      │  ◄─── User Interface
├─────────────────────────┤
│  Business Logic Layer   │  ◄─── {topic_name}
├─────────────────────────┤
│  Data Access Layer      │  ◄─── Database
├─────────────────────────┤
│  Infrastructure Layer   │  ◄─── Runtime
└─────────────────────────┘
```

**Concept 2: Interaction Pattern**
```
Entity A          Entity B         Entity C
  │ │                │              │
  │ │─── Request ────▶              │
  │ │◄─── Response ───              │
  │ │                               │
  │ │───────── Forward ─────────────▶
  │ │                               │
  │ │◄────── Feedback ──────────────│
```

**Concept 3: State Transitions**
```
    [IDLE]
      │
      ├─ Initialize ─▶ [READY]
                        │
                        ├─ Process ─▶ [RUNNING]
                        │               │
                        │               └─ Error ─▶ [ERROR]
                        │                   │
                        │                   └─ Recover ─▶ [RUNNING]
                        │
                        └─ Complete ─▶ [DONE]
```
""".strip()

def process_topics():
    """Update all topics with improved visual explanations"""
    topics = list(topics_col.find({}))
    total = len(topics)
    
    logger.info(f"Improving visual explanations for {total} topics...")
    
    updated_count = 0
    for idx, topic in enumerate(topics, 1):
        topic_name = topic.get('name', '')
        language = topic.get('language', '')
        
        # Generate improved visual explanation
        visual_explanation = generate_visual_explanation(topic_name, language)
        
        try:
            # Update the visual explanation in the explanations dict
            result = topics_col.update_one(
                {'_id': topic.get('_id')},
                {
                    '$set': {
                        'explanations.visual': visual_explanation,
                        'updated_at': datetime.now()
                    }
                }
            )
            updated_count += 1
            
            if idx % 20 == 0:
                logger.info(f"[{idx}/{total}] Updated visual explanation for {topic_name} ({language})")
        except Exception as e:
            logger.error(f"Error updating {topic_name}: {e}")
    
    logger.info(f"✅ Successfully updated visual explanations for {updated_count}/{total} topics!")

if __name__ == '__main__':
    try:
        process_topics()
    finally:
        client.close()
