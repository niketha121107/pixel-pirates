#!/usr/bin/env python
"""Generate explanations using templates (no API calls) - fallback method"""
import logging
from pymongo import MongoClient
from app.core.config import Settings
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
topics_col = db.topics

def generate_simplified_explanation(topic_name: str, language: str) -> str:
    """Generate simplified explanation"""
    return f"""
Understanding {topic_name} in {language}

{topic_name} is a fundamental concept in {language} programming that helps developers write better code. 

Key Points:
• This concept makes your code more efficient and easier to understand
• It's commonly used in real-world {language} applications
• Learning it will improve your programming skills significantly

Why It Matters:
The primary benefit of understanding {topic_name} is that it allows you to write cleaner, more maintainable code. 
Whether you're building small scripts or large applications in {language}, this concept plays an important role.

Getting Started:
Start by practicing simple examples. Write small programs that use {topic_name}. 
Try different approaches and see what works best for your coding style.
""".strip()

def generate_logical_explanation(topic_name: str, language: str) -> str:
    """Generate logical step-by-step explanation"""
    return f"""
Step-by-Step Understanding of {topic_name} in {language}

Step 1: Understand the Basics
{topic_name} is built on fundamental programming principles. In {language}, it represents a way to organize and manage code effectively.

Step 2: Learn the Core Concepts
The main components of {topic_name} include:
- Core concepts that form the foundation
- Patterns and best practices used in {language}
- How it interacts with other programming features

Step 3: Practice Implementation
Write code that implements {topic_name}. Test different scenarios and understand how it behaves in various situations.

Step 4: Apply to Real Projects
Use {topic_name} in actual {language} projects. See how it improves code quality and efficiency.

Step 5: Advanced Patterns
Once comfortable, explore advanced usage patterns and optimization techniques.
""".strip()

def generate_visual_explanation(topic_name: str, language: str) -> str:
    """Generate visual/diagrammatic explanation"""
    return f"""
Visual Understanding of {topic_name} in {language}

Structure Overview:
┌─────────────────────────────────────────┐
│   {topic_name.upper()} CONCEPT IN {language.upper()}        │
├─────────────────────────────────────────┤
│ • Input: Data and parameters            │
│ • Processing: Core logic                │
│ • Output: Results and effects           │
└─────────────────────────────────────────┘

Data Flow:
   Input → Processing → Output
     ↓         ↓         ↓
  Setup    Execute    Return

Relationships:
{topic_name} connects with:
• Other core {language} concepts
• Programming best practices
• Performance optimization

Visual Pattern:
The concept can be visualized as layers:
  [High Level Abstraction]
         ↓
  [Core Implementation]
         ↓
  [Low Level Details]
         ↓
  [Hardware/Runtime]
""".strip()

def generate_analogy_explanation(topic_name: str, language: str) -> str:
    """Generate analogy-based explanation"""
    return f"""
Real-World Analogies for {topic_name} in {language}

Analogy 1: Building Construction
Think of {topic_name} like building a house:
- Foundation: Basic setup and configuration
- Structure: Core components assembled
- Details: Finishing touches and optimization
Just as you need a solid foundation before building walls, you need to understand {topic_name} before using it in complex projects.

Analogy 2: Transportation System
{topic_name} in {language} is like a transportation system:
- Roads represent the data pathways
- Vehicles represent the information flowing through
- Traffic rules represent the logic and constraints
Good traffic management ensures smooth flow - similarly, proper use of {topic_name} ensures efficient code execution.

Analogy 3: Recipe in Cooking
{topic_name} is like a recipe:
- Ingredients are your input data
- Instructions are your code logic
- Final dish is your output
Following the recipe correctly ensures success - understanding {topic_name} ensures your code works as expected.

Analogy 4: Library Organization
{topic_name} works like a well-organized library:
- Books are organized by category (structure)
- Catalog helps find books quickly (efficiency)
- System enables others to find what they need (usability)
""".strip()

def generate_all_explanations(topic_name: str, language: str) -> dict:
    """Generate all 4 explanation types"""
    return {
        'simplified': generate_simplified_explanation(topic_name, language),
        'logical': generate_logical_explanation(topic_name, language),
        'visual': generate_visual_explanation(topic_name, language),
        'analogy': generate_analogy_explanation(topic_name, language),
    }

def process_topics():
    """Process all topics and generate explanations"""
    topics = list(topics_col.find({}))
    total = len(topics)
    
    logger.info(f"Processing {total} topics with template explanations...")
    
    updated_count = 0
    for idx, topic in enumerate(topics, 1):
        topic_name = topic.get('name', '')
        language = topic.get('language', '')
        
        # Generate explanations
        explanations = generate_all_explanations(topic_name, language)
        
        try:
            result = topics_col.update_one(
                {'_id': topic.get('_id')},
                {
                    '$set': {
                        'explanations': explanations,
                        'generated_at': datetime.now()
                    }
                }
            )
            updated_count += 1
            
            if idx % 20 == 0:
                logger.info(f"[{idx}/{total}] {topic_name} ({language})")
        except Exception as e:
            logger.error(f"Error updating {topic_name}: {e}")
    
    logger.info(f"✅ Successfully updated {updated_count}/{total} topics!")

if __name__ == '__main__':
    try:
        process_topics()
    finally:
        client.close()
