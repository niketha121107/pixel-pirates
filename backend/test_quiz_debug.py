#!/usr/bin/env python
"""Debug quiz JSON generation"""

import os
from dotenv import load_dotenv
import httpx
import json
import asyncio

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

async def test():
    print('Testing quiz generation response format...\n')
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'
    params = {'key': api_key}
    
    prompt = """Generate exactly 2 multiple-choice quiz questions about Python Variables.

Requirements:
- Each question has exactly 4 options
- Only ONE option is correct
- Include explanation for correct answer
- Difficulty: easy

Return ONLY raw JSON array, no markdown code blocks. Fields MUST be:
- "question": The question text
- "options": Array of 4 option strings
- "correctAnswer": Index (0-3) of correct option
- "explanation": Why answer is correct
- "difficulty": easy

Example:
[
  {
    "question": "What is a variable?",
    "options": ["Container for data", "Function", "Loop", "Import"],
    "correctAnswer": 0,
    "explanation": "A variable stores data",
    "difficulty": "easy"
  }
]"""
    
    payload = {
        'contents': [{
            'parts': [{'text': prompt}]
        }],
        'generationConfig': {
            'temperature': 0.5,
            'maxOutputTokens': 1500
        }
    }
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, params=params, json=payload)
        print(f'Status: {resp.status_code}')
        if resp.status_code == 200:
            data = resp.json()
            if 'candidates' in data:
                text = data['candidates'][0]['content']['parts'][0]['text']
                print(f'Response length: {len(text)} chars')
                print(f'\nFull response:\n{text}\n')
                
                # Try to clean and parse
                cleaned = text.strip()
                if '```json' in text:
                    cleaned = text.split('```json')[1].split('```')[0].strip()
                elif '```' in text:
                    cleaned = text.split('```')[1].split('```')[0].strip()
                
                print(f'Cleaned response:\n{cleaned}\n')
                
                try:
                    parsed = json.loads(cleaned)
                    print(f'JSON parsing: SUCCESS')
                    print(f'Parsed: {json.dumps(parsed, indent=2)[:500]}')
                    
                    # Check structure
                    if isinstance(parsed, list):
                        q = parsed[0]
                        print(f'\nFirst question fields: {list(q.keys())}')
                        print(f'Options count: {len(q.get("options", []))}')
                        print(f'Has correctAnswer: {"correctAnswer" in q}')
                except Exception as e:
                    print(f'JSON parsing: FAILED - {e}')
            else:
                print(f'No candidates in response')
        else:
            print(f'Error: {resp.json()}')

asyncio.run(test())
