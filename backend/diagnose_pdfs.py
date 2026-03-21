from pymongo import MongoClient
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

# Check PDF coverage
topics_collection = db["topics"]

# Count topics
total_topics = topics_collection.count_documents({})
with_pdf = topics_collection.count_documents({"pdf_path": {"$exists": True, "$ne": None}})
without_pdf = total_topics - with_pdf

print(f"\n📊 DATABASE PDF STATUS:")
print(f"   Total topics: {total_topics}")
print(f"   ✅ With PDF: {with_pdf}")
print(f"   ❌ Without PDF: {without_pdf}")
print(f"   Coverage: {100*with_pdf/total_topics:.1f}%\n")

if without_pdf > 0:
    print(f"❌ {without_pdf} topics MISSING PDFs:\n")
    missing = list(topics_collection.find(
        {"pdf_path": {"$exists": False}},
        {"topicName": 1, "name": 1}
    ))
    
    for i, topic in enumerate(missing, 1):
        name = topic.get("topicName") or topic.get("name", "Unknown")
        print(f"   {i:2d}. {name}")

# Check file system
print(f"\n📁 FILE SYSTEM:")
pdf_dir = "storage/pdfs"
actual_pdfs = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
print(f"   PDFs on disk: {actual_pdfs}")

# Check for orphaned PDFs (in filesystem but not in DB)
print(f"\n🔗 LINKING STATUS:")
db_pdfs = set()
for topic in topics_collection.find({"pdf_filename": {"$exists": True}}, {"pdf_filename": 1}):
    db_pdfs.add(topic.get("pdf_filename"))

disk_pdfs = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
orphaned = disk_pdfs - db_pdfs

if orphaned:
    print(f"   ⚠️  {len(orphaned)} orphaned PDFs (on disk but not linked in DB)")
    for pdf in list(orphaned)[:5]:
        print(f"      - {pdf}")
else:
    print(f"   ✅ All PDFs properly linked")
