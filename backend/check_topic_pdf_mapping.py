#!/usr/bin/env python
"""
Check topic-to-PDF mapping in database
"""
import os
from pymongo import MongoClient

# Connect
client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
db = client["pixel_pirates"]

print("\nCHECKING TOPIC-TO-PDF MAPPING...\n")

try:
    # Get all topics
    topics = list(db.topics.find({}, {"topicName": 1, "name": 1, "pdf_path": 1, "pdf_filename": 1, "_id": 1}))
    print(f"Total topics in DB: {len(topics)}\n")
    
    # Count different states
    with_pdf_path = sum(1 for t in topics if t.get("pdf_path"))
    with_pdf_filename = sum(1 for t in topics if t.get("pdf_filename"))
    
    print(f"Topics with pdf_path field: {with_pdf_path}")
    print(f"Topics with pdf_filename field: {with_pdf_filename}")
    
    # Check for missing
    missing_pdf = [t for t in topics if not t.get("pdf_path")]
    print(f"Topics WITHOUT pdf_path: {len(missing_pdf)}\n")
    
    if missing_pdf:
        print("Topics missing PDFs:")
        for t in missing_pdf[:15]:
            print(f"  - {t.get('topicName') or t.get('name', 'Unknown')}")
        if len(missing_pdf) > 15:
            print(f"  ... and {len(missing_pdf) - 15} more")
    
    # Check file existence
    existing_pdfs = sum(1 for t in topics if t.get("pdf_path") and os.path.exists(t.get("pdf_path", "")))
    print(f"\nPDFs that exist on disk: {existing_pdfs}/{with_pdf_path}")
    
    # Get actual PDF count on disk
    pdf_dir = "storage/pdfs"
    disk_pdfs = len([f for f in os.listdir(pdf_dir) if f.endswith(".pdf")])
    print(f"Actual PDF files on disk: {disk_pdfs}")
    print(f"\nCOVERAGE: {100*existing_pdfs/len(topics):.1f}% ({existing_pdfs}/{len(topics)})")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("\nFalling back to file system check...")
    pdf_count = len([f for f in os.listdir("storage/pdfs") if f.endswith(".pdf")])
    print(f"PDFs on disk: {pdf_count}")
