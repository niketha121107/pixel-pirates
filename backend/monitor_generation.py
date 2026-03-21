#!/usr/bin/env python
"""
Monitor the content generation progress in real-time
"""
import os
import time
from pathlib import Path
import subprocess
import sys

print("\n" + "="*80)
print("📊 CONTENT GENERATION PROGRESS MONITOR")
print("="*80 + "\n")

log_file = Path("generation_progress.log")
last_lines = 0

while True:
    try:
        # Check if log file exists
        if log_file.exists():
            with open(log_file, "r") as f:
                lines = f.readlines()
            
            # Show last 20 lines
            if len(lines) > last_lines:
                print("📝 Latest Progress:")
                print("-" * 80)
                for line in lines[-20:]:
                    print(line.rstrip())
                print("-" * 80)
                last_lines = len(lines)
                
                # Check if completed
                if any("GENERATION REPORT" in line for line in lines):
                    print("\n✅ GENERATION COMPLETED!")
                    print("\n📊 Final Status:")
                    for line in lines[-15:]:
                        if line.strip():
                            print(f"  {line.rstrip()}")
                    break
            
        else:
            print("⏳ Waiting for generation to start...")
        
        # Wait before next check
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
        break
    except Exception as e:
        print(f"⚠️  Error: {e}")
        time.sleep(5)

print("\n" + "="*80)
print("Full log available in: generation_progress.log")
print("="*80 + "\n")
