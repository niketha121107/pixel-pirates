"""
Batch PDF Generation for All Topics
Generates study materials and PDFs for all 99 topics
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any
from pymongo import MongoClient
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.study_material_service import study_material_generator
from app.services.pdf_generator_service import pdf_generator
from app.core.config import settings

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

# PDF storage directory
PDF_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage/pdfs")
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)

class BatchPDFGenerator:
    """Generate PDFs for all topics in batch"""
    
    def __init__(self):
        self.success_count = 0
        self.failed_topics = []
        self.skipped_topics = []
        self.start_time = datetime.now()
    
    async def generate_all_pdfs(self):
        """Generate PDFs for all topics"""
        
        logger.info("=" * 80)
        logger.info("🌱 Starting batch PDF generation for all topics")
        logger.info("=" * 80)
        
        try:
            # Get all topics
            topics_collection = db["topics"]
            all_topics = list(topics_collection.find({}, {"topicName": 1, "name": 1, "_id": 1}))
            
            if not all_topics:
                logger.warning("No topics found in database!")
                return
            
            logger.info(f"\n📊 Found {len(all_topics)} topics to process\n")
            
            # Process each topic
            for idx, topic in enumerate(all_topics, 1):
                topic_name = topic.get("topicName") or topic.get("name")
                topic_id = str(topic.get("_id"))
                
                logger.info(f"[{idx:2d}/{len(all_topics)}] Processing: {topic_name}")
                
                try:
                    # Check if PDF already exists
                    pdf_filename = f"study_{topic_id}_all.pdf"
                    pdf_path = os.path.join(PDF_STORAGE_DIR, pdf_filename)
                    
                    if os.path.exists(pdf_path):
                        logger.info(f"     ⏭️  PDF exists, skipping")
                        self.skipped_topics.append(topic_name)
                        continue
                    
                    # Generate study material
                    logger.info(f"     📝 Generating study material...")
                    study_material = await study_material_generator.generate_study_material(
                        topic_name,
                        learning_level="adaptive"
                    )
                    
                    if not study_material:
                        logger.error(f"     ❌ Failed to generate study material")
                        self.failed_topics.append((topic_name, "Study material generation failed"))
                        await asyncio.sleep(1)
                        continue
                    
                    # Generate PDF
                    logger.info(f"     📄 Generating PDF...")
                    pdf_success = pdf_generator.generate_pdf(study_material, pdf_path)
                    
                    if pdf_success:
                        logger.info(f"     ✅ PDF generated: {pdf_filename}")
                        self.success_count += 1
                        
                        # Store PDF reference in database
                        topics_collection.update_one(
                            {"_id": topic.get("_id")},
                            {"$set": {"pdf_path": pdf_path, "pdf_filename": pdf_filename}}
                        )
                    else:
                        logger.error(f"     ❌ PDF generation failed")
                        self.failed_topics.append((topic_name, "PDF generation failed"))
                    
                    # Rate limiting - be nice to APIs
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"     ❌ Error: {str(e)[:100]}")
                    self.failed_topics.append((topic_name, str(e)[:100]))
                    await asyncio.sleep(1)
            
            # Print summary
            self._print_summary(len(all_topics))
            
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
    
    def _print_summary(self, total_topics: int):
        """Print summary of PDF generation"""
        
        elapsed = datetime.now() - self.start_time
        total_seconds = elapsed.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 BATCH PDF GENERATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Successfully generated: {self.success_count} PDFs")
        logger.info(f"⏭️  Already existed: {len(self.skipped_topics)} PDFs")
        logger.info(f"❌ Failed: {len(self.failed_topics)} topics")
        logger.info(f"📈 Total coverage: {self.success_count + len(self.skipped_topics)}/{total_topics} ({100*(self.success_count + len(self.skipped_topics))/total_topics:.1f}%)")
        logger.info(f"⏱️  Time elapsed: {minutes}m {seconds}s")
        
        if self.failed_topics:
            logger.info("\n❌ Failed Topics:")
            for topic, reason in self.failed_topics[:10]:
                logger.info(f"   - {topic}: {reason}")
            
            if len(self.failed_topics) > 10:
                logger.info(f"   ... and {len(self.failed_topics) - 10} more")
        
        logger.info("\n" + "=" * 80)
        
        # Save results to file
        log_file = os.path.join(os.path.dirname(__file__), "pdf_generation_summary.log")
        with open(log_file, "w") as f:
            f.write(f"PDF Generation Summary - {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total topics: {total_topics}\n")
            f.write(f"Successfully generated: {self.success_count}\n")
            f.write(f"Already existed: {len(self.skipped_topics)}\n")
            f.write(f"Failed: {len(self.failed_topics)}\n")
            f.write(f"Coverage: {100*(self.success_count + len(self.skipped_topics))/total_topics:.1f}%\n")
            f.write(f"Time: {minutes}m {seconds}s\n\n")
            
            if self.failed_topics:
                f.write("Failed topics:\n")
                for topic, reason in self.failed_topics:
                    f.write(f"  - {topic}: {reason}\n")
        
        logger.info(f"✅ Summary saved to: {log_file}")

async def main():
    """Main entry point"""
    
    generator = BatchPDFGenerator()
    await generator.generate_all_pdfs()

if __name__ == "__main__":
    asyncio.run(main())
