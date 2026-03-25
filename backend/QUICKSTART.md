# Quick Start - Chatbot Setup (2 Minutes)

## 1️⃣ Get Gemini API Key (1 minute)

Visit: **https://aistudio.google.com/apikey**

Click **"Create API Key"** and **copy it**.

## 2️⃣ Create .env File (1 minute)

Create `backend/.env` file and add:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
YOUTUBE_API_KEY=your_youtube_key_or_leave_blank
JWT_SECRET_KEY=change_this_to_something_random
```

## 3️⃣ Start Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

✅ **Done!** Your AI tutor is ready.

---

## Test It

### Using Frontend (Recommended)
1. Start frontend: `cd frontend && npm run dev`
2. Open: http://localhost:5173
3. Go to Chat section
4. Ask: "Explain Python for loops"

### Using curl
```bash
curl -X POST "http://localhost:8000/chat/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "Explain Python for loops", "history": [], "language": "en"}'
```

---

## What's New? 🎉

✅ **Friendly AI Tutor**
- Warm, encouraging responses
- Says "I'm your AI tutor and I'm here for training you"
- Out-of-topic questions redirected positively

✅ **Better Structured Responses**
- 📚 Quick Answer
- 🎯 Key Points
- 💡 Example
- 🚀 Next Step

✅ **Using Gemini 2.5 Flash**
- Fastest, most affordable
- Great for educational content
- Multi-language support

✅ **Gen Z Slang Support** 🔥
- AI understands Gen Z vocabulary naturally
- Responds professionally to casual language
- Examples: "no cap", "bussin", "sus", "lowkey", "fr fr", and 50+ more terms
- See: `GENZ_SLANG_GUIDE.md` for full list

✅ **Progressive Learning Flow** 📚
- Ask "What is Python?" → AI explains + lists 8 beginner topics to choose from
- Select a topic → AI provides detailed explanation with code examples
- Natural guided learning path from basics to intermediate
- Topics: Variables, Data Types, If/Else, Loops, Functions, Lists, Dicts
- See: `PROGRESSIVE_LEARNING_GUIDE.md` for details

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "API key not valid" | Verify key at https://aistudio.google.com/apikey |
| "API key not configured" | Check `.env` file in `backend/` directory |
| Timeout (30s) | Check internet connection |
| Rate limited (429) | Automatic retry works; check quota online |

---

## Full Documentation

📖 Detailed guide: `backend/GEMINI_SETUP_GUIDE.md`
📝 Complete summary: `backend/CHATBOT_FIXES_SUMMARY.md`

---

**Questions? Check the docs or contact support! 🚀**
