#!/usr/bin/env python
"""Generate comprehensive explanations for all 200 topics using Gemini API"""
import asyncio
import logging
from pymongo import MongoClient
from app.core.config import Settings
import google.generativeai as genai
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure API
settings = Settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

# MongoDB connection
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
topics_col = db.topics

# Semaphore for rate limiting
SEMAPHORE = asyncio.Semaphore(2)
GENERATION_DELAY = 0.5  # seconds between API calls

async def generate_explanation(topic_name: str, language: str, style: str) -> str:
    """Generate a single explanation using Gemini API"""
    async with SEMAPHORE:
        await asyncio.sleep(GENERATION_DELAY)
        
        style_prompts = {
            'simplified': f"Explain {topic_name} in {language} in the simplest way possible, using plain language that anyone can understand. No jargon. 200-300 words.",
            'logical': f"Provide a logical, step-by-step explanation of {topic_name} in {language}. Break it down into clear logical steps or components. 200-300 words.",
            'visual': f"Describe {topic_name} in {language} in a way that could be visualized or diagrammed. Describe the structure, relationships, and flow. Include ASCII art or structural descriptions. 200-300 words.",
            'analogy': f"Explain {topic_name} in {language} using real-world analogies and comparisons. Make it relatable with everyday examples. 200-300 words.",
        }
        
        prompt = style_prompts.get(style, "")
        if not prompt:
            return ""
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = await asyncio.to_thread(model.generate_content, prompt)
            return response.text.strip() if response.text else ""
        except Exception as e:
            logger.error(f"Failed to generate {style} for {topic_name}: {e}")
            return ""

async def generate_all_explanations(topic_id: str, topic_name: str, language: str) -> dict:
    """Generate all 4 explanation types for a topic"""
    explanations = {}
    
    for style in ['simplified', 'logical', 'visual', 'analogy']:
        logger.info(f"Generating {style} explanation for {topic_name}...")
        content = await generate_explanation(topic_name, language, style)
        explanations[style] = content
    
    return explanations

async def process_topics():
    """Process all topics and generate explanations"""
    topics = list(topics_col.find({}))
    total = len(topics)
    
    logger.info(f"Processing {total} topics...")
    
    for idx, topic in enumerate(topics, 1):
        topic_id = str(topic.get('_id', ''))
        topic_name = topic.get('name', '')
        language = topic.get('language', '')
        
        logger.info(f"[{idx}/{total}] Processing: {topic_name} ({language})")
        
        # Generate explanations
        explanations = await generate_all_explanations(topic_id, topic_name, language)
        
        # Filter out empty explanations
        valid_explanations = {k: v for k, v in explanations.items() if v}
        
        if valid_explanations:
            logger.info(f"✓ Generated {len(valid_explanations)} explanations for {topic_name}")
            
            # Update MongoDB
            try:
                topics_col.update_one(
                    {'_id': topic.get('_id')},
                    {
                        '$set': {
                            'explanations': valid_explanations,
                            'generated_at': datetime.now()
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Failed to save explanations for {topic_name}: {e}")
        else:
            logger.warning(f"✗ No explanations generated for {topic_name}")
    
    logger.info(f"✅ Completed processing all {total} topics!")

if __name__ == '__main__':
    try:
        asyncio.run(process_topics())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        client.close()
