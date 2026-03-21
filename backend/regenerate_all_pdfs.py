"""
Improved Batch PDF Generation Script
Ensures all 99 topics have valid, complete PDF files
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient

# Setup
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(__file__))

from app.services.study_material_service import study_material_generator
from app.services.pdf_generator_service import pdf_generator

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

# Storage
PDF_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage/pdfs")
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)

class ImprovedPDFGenerator:
    def __init__(self):
        self.success = 0
        self.failed = []
        self.skipped = 0
        
    async def generate_all(self):
        logger.info("\n" + "="*70)
        logger.info("REGENERATING PDFS FOR ALL 99 TOPICS")
        logger.info("="*70 + "\n")
        
        # Get all topics
        topics = list(db.topics.find({}, {"topicName": 1, "name": 1, "_id": 1}).sort("topicName", 1))
        logger.info(f"Found {len(topics)} topics\n")
        
        for idx, topic in enumerate(topics, 1):
            name = topic.get("topicName") or topic.get("name")
            topic_id = str(topic["_id"])
            
            logger.info(f"[{idx:2d}/{len(topics)}] {name:50s}", end=" ... ")
            
            try:
                # Generate study material
                study_material = await study_material_generator.generate_study_material(
                    name,
                    learning_level="adaptive"
                )
                
                if not study_material:
                    raise Exception("Study material is empty")
                
                # Generate PDF
                pdf_file = f"study_{topic_id}_all.pdf"
                pdf_path = os.path.join(PDF_STORAGE_DIR, pdf_file)
                
                success = pdf_generator.generate_pdf(study_material, pdf_path)
                
                if not success:
                    raise Exception("PDF generation returned False")
                
                # Verify PDF was created
                if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 500:
                    raise Exception(f"PDF file invalid (size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0} bytes)")
                
                # Update database
                db.topics.update_one(
                    {"_id": topic["_id"]},
                    {
                        "$set": {
                            "pdf_path": pdf_path,
                            "pdf_filename": pdf_file
                        }
                    }
                )
                
                size_kb = os.path.getsize(pdf_path) / 1024
                logger.info(f"OK ({size_kb:.1f}KB)")
                self.success += 1
                
            except Exception as e:
                logger.info(f"FAILED - {str(e)[:50]}")
                self.failed.append((name, str(e)))
            
            # Rate limiting
            await asyncio.sleep(1.5)
        
        self._print_report(len(topics))
    
    def _print_report(self, total):
        logger.info("\n" + "="*70)
        logger.info("GENERATION COMPLETE")
        logger.info("="*70)
        logger.info(f"\nResults:")
        logger.info(f"  Total Topics: {total}")
        logger.info(f"  Success: {self.success}")
        logger.info(f"  Failed: {len(self.failed)}")
        logger.info(f"  Coverage: {100*self.success/total:.1f}%\n")
        
        if self.failed:
            logger.info("Failed Topics:")
            for name, error in self.failed:
                logger.info(f"  - {name}: {error[:60]}")
        
        # Verify database
        with_pdf = db.topics.count_documents({"pdf_path": {"$exists": True}})
        total_topics = db.topics.count_documents({})
        
        logger.info(f"\nDatabase Verification:")
        logger.info(f"  Topics with PDF: {with_pdf}/{total_topics}")
        logger.info(f"  Coverage: {100*with_pdf/total_topics:.1f}%")
        logger.info("="*70 + "\n")

async def main():
    gen = ImprovedPDFGenerator()
    await gen.generate_all()

if __name__ == "__main__":
    asyncio.run(main())
