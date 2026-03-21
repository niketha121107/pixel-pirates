from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

# Check PDF coverage in database
topics_collection = db["topics"]

with_pdfs = topics_collection.count_documents({"pdf_path": {"$exists": True}})
without_pdfs = topics_collection.count_documents({"pdf_path": {"$exists": False}})
total = topics_collection.count_documents({})

print(f"\n📊 PDF Database Status:")
print(f"   Total topics: {total}")
print(f"   ✅ Topics with PDF: {with_pdfs}")
print(f"   ❌ Topics without PDF: {without_pdfs}")
print(f"   📈 Coverage: {100*with_pdfs/total:.1f}%\n")

# Sample topics with PDFs
sample = list(topics_collection.find(
    {"pdf_path": {"$exists": True}},
    {"topicName": 1, "pdf_filename": 1}
).limit(5))

print("Sample topics with PDFs:")
for topic in sample:
    print(f"   • {topic.get('topicName')}: {topic.get('pdf_filename')}")
