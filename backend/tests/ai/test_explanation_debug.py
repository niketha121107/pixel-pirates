#!/usr/bin/env python
"""Debug explanation generation"""

import os
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

async def test():
    print('Testing Gemini explanation generation...')
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'
    params = {'key': api_key}
    
    payload = {
        'contents': [{
            'parts': [{'text': "Explain Python Variables in very simple language for beginners. Keep under 200 words."}]
        }],
        'generationConfig': {
            'temperature': 0.6,
            'maxOutputTokens': 400
        }
    }
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, params=params, json=payload)
        print(f'Status: {resp.status_code}')
        if resp.status_code == 200:
            data = resp.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                print(f'Response length: {len(text)} chars')
                print(f'First 500 chars:\n{text[:500]}')
            else:
                print(f'No candidates: {data}')
        else:
            print(f'Error: {resp.json()}')

asyncio.run(test())
