#!/usr/bin/env python
"""
🚀 PIXEL PIRATES - MASTER CONTENT GENERATION SCRIPT
Orchestrates complete content generation for all 200 topics

This script:
1. Verifies & generates 200 base topics (if needed)
2. Generates YouTube videos for each topic
3. Generates 4 types of explanations per topic
4. Generates PDF study guides
5. Generates mock tests
6. Stores everything in MongoDB

Run: python generate_all_content.py
"""

import asyncio
import sys
import time
import subprocess
from datetime import datetime


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*80)
    print("🚀 PIXEL PIRATES - COMPLETE CONTENT GENERATION SYSTEM")
    print("="*80)
    print("\nGeneration Pipeline:")
    print("  1️⃣  VERIFY & GENERATE 200 BASE TOPICS")
    print("  2️⃣  GENERATE YOUTUBE VIDEOS")
    print("  3️⃣  GENERATE 4-TYPE EXPLANATIONS")
    print("  4️⃣  GENERATE PDF STUDY GUIDES")
    print("  5️⃣  GENERATE MOCK TESTS")
    print("  6️⃣  STORE IN MONGODB")
    print("\nConfiguration:")
    print("  📝 Topics: 200 across 20 programming languages")
    print("  🎥 Videos: From YouTube (highly recommended)")
    print("  📚 Explanations: Visual, Simplified, Logical, Analogy")
    print("  📄 PDFs: Professional study guides")
    print("  ✅ Mock Tests: Comprehensive question banks")
    print("="*80 + "\n")


def run_step(step_num: int, step_name: str, script_name: str) -> bool:
    """
    Run a generation step.
    Returns True if successful, False otherwise.
    """
    print(f"\n{'='*80}")
    print(f"STEP {step_num}/2: {step_name}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ {step_name} completed successfully!")
            print(f"⏱️  Time elapsed: {elapsed:.1f}s")
            return True
        else:
            print(f"\n❌ {step_name} failed with exit code {result.returncode}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Script not found: {script_name}")
        return False
    except Exception as e:
        print(f"❌ Error running {step_name}: {e}")
        return False


def print_final_report(results: dict):
    """Print final generation report"""
    print("\n" + "="*80)
    print("📊 GENERATION REPORT")
    print("="*80)
    
    step1 = results.get("step1", False)
    step2 = results.get("step2", False)
    
    status_icon_1 = "✅" if step1 else "❌"
    status_icon_2 = "✅" if step2 else "❌"
    
    print(f"\n{status_icon_1} Step 1: Topic Verification & Generation")
    if step1:
        print("   └─ 200 base topics ready in MongoDB")
        print("   └─ All topics have overview and key points")
    else:
        print("   └─ Failed - Please check configuration")
    
    print(f"\n{status_icon_2} Step 2: Complete Content Generation")
    if step2:
        print("   ├─ YouTube videos generated for all topics")
        print("   ├─ 4-type explanations (visual, simplified, logical, analogy)")
        print("   ├─ Professional PDF study guides")
        print("   ├─ Mock test question banks")
        print("   └─ All content stored in MongoDB")
    else:
        print("   └─ Failed - Please check API keys and MongoDB")
    
    print("\n" + "="*80)
    
    if step1 and step2:
        print("✅ ALL GENERATION COMPLETE!")
        print("\n📱 Next Steps:")
        print("  1. Start your backend server: python main.py")
        print("  2. Generate mock test components in frontend:")
        print("     - MockTestRules.tsx")
        print("     - MockTest.tsx")
        print("     - MockTestResults.tsx")
        print("  3. Deploy to production!")
        return True
    else:
        print("⚠️  GENERATION INCOMPLETE")
        print("\nTroubleshooting:")
        print("  ❌ Step 1 failed:")
        print("     - Check MongoDB is running")
        print("     - Check GEMINI_API_KEY in .env")
        print("  ❌ Step 2 failed:")
        print("     - Check YouTube API key: IzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc")
        print("     - Check GEMINI_API_KEY is valid")
        print("     - Ensure MongoDB has 200 topics")
        print("     - Check internet connection")
        print("     - Check rate limits (YouTube & Gemini)")
        return False


def main():
    """Main orchestration function"""
    
    print_banner()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    results = {}
    
    # Step 1: Verify and generate topics
    results["step1"] = run_step(
        1,
        "Topic Verification & Generation",
        "verify_and_generate_topics.py"
    )
    
    if not results["step1"]:
        print("\n⚠️  Step 1 failed. Cannot proceed without topics.")
        print_final_report(results)
        sys.exit(1)
    
    # Small delay between steps
    print("\n⏸️  Waiting 5 seconds before Step 2...")
    time.sleep(5)
    
    # Step 2: Generate complete content
    results["step2"] = run_step(
        2,
        "Complete Content Generation (Videos, Explanations, PDFs, Tests)",
        "generate_complete_content.py"
    )
    
    # Print final report
    success = print_final_report(results)
    
    print("\n" + "="*80 + "\n")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
