from pymongo import MongoClient
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

topics_collection = db["topics"]

# Get all topics with PDFs
topics_with_pdfs = list(topics_collection.find(
    {"pdf_path": {"$exists": True}},
    {"topicName": 1, "pdf_path": 1, "pdf_filename": 1}
).sort("topicName", 1))

print(f"\nALL {len(topics_with_pdfs)} TOPICS WITH VALID PDFS:\n")

invalid_pdfs = []
valid_pdfs = []

for i, topic in enumerate(topics_with_pdfs, 1):
    name = topic.get("topicName", "Unknown")
    pdf_path = topic.get("pdf_path", "")
    
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 500:  # At least 500 bytes
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"{i:2d}. [OK] {name:40s} ({size_kb:.1f} KB)")
        valid_pdfs.append(name)
    else:
        print(f"{i:2d}. [XX] {name:40s} (FILE NOT FOUND OR EMPTY)")
        invalid_pdfs.append(name)

print(f"\n{'='*70}")
print(f"SUMMARY:")
print(f"   Total PDFs: {len(topics_with_pdfs)}")
print(f"   [OK] Valid & Accessible: {len(valid_pdfs)}")
print(f"   [XX] Invalid or Missing: {len(invalid_pdfs)}")
print(f"   Coverage: {100*len(valid_pdfs)/len(topics_with_pdfs):.1f}%")

if invalid_pdfs:
    print(f"\n[XX] Invalid PDFs:")
    for name in invalid_pdfs:
        print(f"   - {name}")
