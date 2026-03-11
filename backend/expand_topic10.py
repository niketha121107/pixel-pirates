# Script to expand topic 10 subtopics in seed_database.py
import re

with open('seed_database.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find sub-10-1 position
idx = content.find('"id": "sub-10-1"')
print(f"sub-10-1 found at position: {idx}")

# Find sub-10-2 position
idx2 = content.find('"id": "sub-10-2"')
print(f"sub-10-2 found at position: {idx2}")

# Find sub-10-3 position
idx3 = content.find('"id": "sub-10-3"')
print(f"sub-10-3 found at position: {idx3}")

# Find the end of topic-10 subtopics section - look for the closing of the subtopics list
# We need to find the pattern after sub-10-3's recommendedVideos closing
end_marker = content.find('"recommendedVideos"', idx3)
print(f"sub-10-3 recommendedVideos at: {end_marker}")

# Find the line number for each
lines = content[:idx].count('\n') + 1
print(f"sub-10-1 is on line: {lines}")
lines2 = content[:idx2].count('\n') + 1
print(f"sub-10-2 is on line: {lines2}")
lines3 = content[:idx3].count('\n') + 1
print(f"sub-10-3 is on line: {lines3}")

# Show the exact old content for sub-10-1 overview to understand encoding
overview_start = content.find('"overview":', idx)
overview_end = content.find('",\n', overview_start)
print(f"\nOld sub-10-1 overview:\n{content[overview_start:overview_end+2]}")
