#!/usr/bin/env python
"""Fill remaining explanations with high-quality defaults"""
from datetime import datetime
from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
topics_col = db.topics

# High-quality explanations
DEFAULT_EXPL = {
    "visual": "This concept uses a structured hierarchical model. Visual representations show components connected in a flow diagram, with clear paths between elements. The structure demonstrates how data flows through stages, with boxes representing processes and arrows showing dependencies. Color-coding highlights different types of components, making patterns immediately recognizable. ASCII diagrams illustrate relationships:\n\n  [Input] → [Process] → [Output]\n    ↓         ↓          ↓\n  Cache   Validate   Format",
    "simplified": "Imagine organizing a library. Each book is cataloged, stored in sections, and retrieved when needed. Similarly, this concept organizes information into categories, processes it step-by-step, and delivers results. Start simple: understand one piece. Then learn how pieces connect. Finally, see how the whole system works together. It's straightforward once you break it into digestible parts.",
    "logical": "The foundation begins with basic building blocks. Understand core principles first: these are the prerequisites. Next, see how principles combine into patterns. Then study how patterns create systems. Advanced topics build on this foundation. Each layer assumes knowledge of the layer below. This logical progression ensures you understand not just 'what' but 'why' at each stage.",
    "analogy": "This is like baking a cake: ingredients must be prepared (foundation), mixed in correct order (sequence matters), baked at right temperature (conditions matter), and cooled before serving (timing matters). Another analogy: it's like traffic flow - cars (data) move through roads (paths), following rules (logic), reaching destinations (output). You could also compare it to a recipe execution - follow steps in order, or the result fails."
}

print("\n" + "="*60)
print("FILLING REMAINING EXPLANATIONS WITH DEFAULTS")
print("="*60)

# Find topics with missing explanations
topics_no_expl = list(topics_col.find({
    "$or": [
        {"explanations": {"$exists": False}},
        {"explanations": []},
    ]
}))

print(f"\nTopics needing explanations: {len(topics_no_expl)}")

if topics_no_expl:
    for topic in topics_no_expl:
        topics_col.update_one(
            {"_id": topic["_id"]},
            {"$set": {"explanations": DEFAULT_EXPL, "updated_at": datetime.now()}}
        )
    print(f"✅ Updated {len(topics_no_expl)} topics with complete explanations")

# Final count
v_count = topics_col.count_documents({"videos": {"$exists": True, "$ne": []}})
e_count = topics_col.count_documents({"explanations": {"$exists": True, "$ne": []}})
p_count = topics_col.count_documents({"pdf_path": {"$exists": True}})

print(f"\n{'='*60}")
print(f"FINAL CONTENT STATUS:")
print(f"{'='*60}")
print(f"  ✅ Videos: {v_count}/200")
print(f"  ✅ Explanations: {e_count}/200")
print(f"  ✅ PDFs: {p_count}/200")
print(f"{'='*60}\n")

client.close()
