#!/usr/bin/env python
"""Debug quiz generation service directly"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.ai_content_service import ai_generator
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

async def test():
    print('Testing AIContentGenerator.generate_quiz_questions() directly...\n')
    
    questions = await ai_generator.generate_quiz_questions(
        topic_name="Python Variables",
        num_questions=3,
        difficulty="easy"
    )
    
    print(f'\nResult: Generated {len(questions)} questions')
    if questions:
        for i, q in enumerate(questions[:1], 1):
            print(f'\nQuestion {i}:')
            print(f'  Question: {q.get("question", "")[:80]}')
            print(f'  Options: {len(q.get("options", []))}')
            print(f'  Correct: {q.get("correctAnswer")}')
            print(f'  Difficulty: {q.get("difficulty")}')
    else:
        print('ERROR: No questions generated!')

# Load env before running
from dotenv import load_dotenv
load_dotenv()

asyncio.run(test())
