# Gemini 2.5 Flash API Setup Guide

This guide will help you configure the Gemini 2.5 Flash API for the Pixel Pirates AI Tutor.

## Overview

The chatbot uses **Gemini 2.5 Flash** for:
- 💬 AI-powered conversational tutoring
- 📝 Quiz generation
- 📊 Quiz evaluation and feedback
- 🌍 Multi-language support
- 📚 Personalized explanations

## Step-by-Step Setup

### 1. Get a Free Gemini API Key

1. Visit: **[Google AI Studio](https://aistudio.google.com/apikey)**
2. Click **"Create API Key"** button
3. Select or create a Google Cloud project
4. Your API key will be generated automatically
5. Copy the key to a safe place

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cd backend
touch .env
```

Copy the following template and fill in your API key:

```env
# Gemini API Configuration (REQUIRED)
GEMINI_API_KEY=your_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-2.5-flash

# Other required variables
YOUTUBE_API_KEY=your_youtube_key_here
JWT_SECRET_KEY=change_this_to_random_string
```

### 3. Verify Configuration

Check that your `.env` file is in the `backend/` directory:

```bash
ls -la backend/.env
```

Should output something like:
```
-rw-r--r--  1 user  group  256 date backend/.env
```

### 4. Start the Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

If configured correctly, you should see:
```
✅ EduTwin AI Chat: ACTIVE (Gemini 2.5 Flash enabled)
```

## Features Enabled

### ✨ Friendly AI Tutor

The chatbot now features:

- **Warm & Encouraging**: Friendly tone for all interactions
- **Proper Structure**: 
  - 📚 Quick Answer
  - 🎯 Key Points
  - 💡 Example
  - 🚀 Next Step

- **Topic-Focused**: Guides out-of-topic questions back to learning
- **Multi-Language**: Supports 15+ languages
- **Adaptive Responses**: Different responses for greetings vs. complex questions

### API Response Format

All chat responses include:

```json
{
  "success": true,
  "message": "Chat response generated",
  "data": {
    "response": "The AI-generated tutoring response"
  }
}
```

## Troubleshooting

### Issue: "Gemini API key not configured"

**Solution**: Ensure your `.env` file is in the `backend/` directory and contains:
```env
GEMINI_API_KEY=your_actual_key
```

### Issue: "API_KEY_INVALID" error

**Solution**: 
1. Verify your API key is correct at [Google AI Studio](https://aistudio.google.com/apikey)
2. Make sure there are no extra spaces or newlines
3. Try generating a new API key

### Issue: "429 - Rate Limited"

**Solution**: The API has automatic retry logic with exponential backoff. This should resolve itself. If persistent, check your Google Cloud Project quota.

### Issue: Timeout error

**Solution**: The AI response time depends on:
- Model complexity
- Network latency
- Request size

Typical response time: 2-5 seconds. If consistently over 30 seconds, check your network connection.

## API Key Security

⚠️ **Never commit `.env` file to git!**

The `.env` file is added to `.gitignore`. Keep your API key private:

- ✅ Store in environment variables
- ✅ Store in `.env` file (local only)
- ❌ Never commit to version control
- ❌ Never share your API key publicly

## Rate Limits

Gemini 2.5 Flash API limits:
- **Free tier**: 60 requests per minute
- **Generous quota**: Best for development and testing
- **Production**: Consider Google Cloud plan for higher limits

Check your usage at: [Google AI Studio Dashboard](https://aistudio.google.com/)

## Test the Chatbot

### 1. Start both servers

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2 - Frontend (if running locally)
cd frontend
npm run dev
```

### 2. Access the Frontend

Open: `http://localhost:5173`

### 3. Test Chat

1. Sign up or log in
2. Go to Chat section
3. Ask a question like:
   - "Explain Python for loops with an example"
   - "What's the difference between list and tuple?"
   - "How do I debug JavaScript?"

### 4. Expected Response Format

The AI should respond with:

```
### 📚 Quick Answer
1-2 sentence direct answer

### 🎯 Key Points
- Point 1
- Point 2
- Point 3

### 💡 Example
Code example with explanation

### 🚀 Next Step
Practical action and follow-up question
```

## Advanced Configuration

### Custom Temperature (Creativity vs Consistency)

In `adaptive_engine_service.py`, adjust temperature:

```python
english_response = await self._call_gemini_text(
    english_prompt,
    temperature=0.8,  # 0.0-1.0 (higher = more creative)
    max_tokens=2000,
    timeout=30.0,
)
```

- **0.3-0.5**: More consistent, structured responses (recommended for coding)
- **0.7-0.9**: More creative and varied responses
- **1.0**: Maximum randomness

### Custom Max Tokens

Increase for detailed explanations:

```python
max_tokens=3000  # Default is 2000
```

### Retry Logic

Automatic retries on failure with exponential backoff:

```python
retries=3  # Number of retry attempts (current setting)
```

## FAQ

**Q: Is the API free?**
A: Yes! Google offers generous free tier. Check current pricing at [Google AI Pricing](https://ai.google.dev/pricing)

**Q: Can I use a different AI model?**
A: Yes! Change `GEMINI_MODEL` in `.env`:
- `gemini-2.5-flash` (recommended, fastest)
- `gemini-2.0-flash-lite`
- `gemini-2.0-pro` (more powerful, slower)

**Q: Does it support multiple languages?**
A: Yes! The backend automatically translates responses to 15+ languages based on the user's language preference.

**Q: Is there a fallback if Gemini fails?**
A: Yes! The system includes:
1. Automatic XML-based fallback responses
2. Ollama local model (if configured)
3. OpenRouter API (if configured)

## Support

For issues with:
- **Google API**: Visit [Google AI Studio Support](https://ai.google.dev/docs)
- **Pixel Pirates**: Check the `/docs` folder or contact the development team

---

**Happy Learning! 🚀**
