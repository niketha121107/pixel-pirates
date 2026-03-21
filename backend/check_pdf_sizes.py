#!/usr/bin/env python
import os
from pathlib import Path

pdf_dir = Path("storage/pdfs")

# List all PDFs and check sizes
pdfs = list(pdf_dir.glob("*.pdf"))
print(f"\nTotal PDF files: {len(pdfs)}\n")

# Check sizes
sizes = []
for pdf in sorted(pdfs):
    size_kb = pdf.stat().st_size / 1024
    sizes.append(size_kb)
    if len([p for p in pdfs if p.stat().st_size < 500]) > 0:
        if pdf.stat().st_size < 500:
            print(f"SMALL: {pdf.name} ({size_kb:.1f}KB)")

if sizes:
    min_size = min(sizes)
    max_size = max(sizes)
    avg_size = sum(sizes) / len(sizes)
    print(f"\nFile Sizes:")
    print(f"  Minimum: {min_size:.1f}KB")
    print(f"  Maximum: {max_size:.1f}KB")
    print(f"  Average: {avg_size:.1f}KB")
    print(f"  Total: {sum(sizes):.1f}KB ({sum(sizes)/1024:.2f}MB)")
    
    small_files = [s for s in sizes if s < 1.0]
    if small_files:
        print(f"\nWARNING: {len(small_files)} PDFs are < 1KB (possibly incomplete)")
    else:
        print(f"\nAll PDFs appear to be complete (all > 1KB)")
