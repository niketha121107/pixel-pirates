from pymongo import MongoClient
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

topics_collection = db["topics"]

# Get all topics with PDFs
topics_with_pdfs = list(topics_collection.find(
    {"pdf_path": {"$exists": True}},
    {"topicName": 1, "pdf_path": 1}
))

print(f"\nVERIFYING {len(topics_with_pdfs)} PDFS...\n")

invalid_count = 0
valid_count = 0

for topic in topics_with_pdfs:
    pdf_path = topic.get("pdf_path", "")
    
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 500:
        valid_count += 1
    else:
        invalid_count += 1
        print(f"MISSING: {topic.get('topicName')}")

print(f"\n" + "="*60)
print(f"RESULTS:")
print(f"  Total Topics: {len(topics_with_pdfs)}")
print(f"  Valid PDFs: {valid_count}")
print(f"  Invalid PDFs: {invalid_count}")
print(f"  Coverage: {100*valid_count/len(topics_with_pdfs):.1f}%")
print("="*60)
