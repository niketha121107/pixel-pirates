# Script to replace topic 10 subtopics with expanded content
import re

with open('seed_database.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# ===== SUB-10-1: Selecting Elements =====
old_10_1_start = content.find('"id": "sub-10-1"')
# Find the start of the enclosing dict (go back to find the '{' before it)
block_start_10_1 = content.rfind('{', 0, old_10_1_start)

# Find sub-10-2 start to know where sub-10-1 ends
old_10_2_start = content.find('"id": "sub-10-2"')
block_start_10_2 = content.rfind('{', 0, old_10_2_start)

# Find sub-10-3 start
old_10_3_start = content.find('"id": "sub-10-3"')
block_start_10_3 = content.rfind('{', 0, old_10_3_start)

# Find the end of all subtopics - after sub-10-3's closing
# Look for the pattern "},\n        ],\n    },\n]" after sub-10-3
# We need to find the closing of sub-10-3's dict and then the subtopics array
after_10_3 = content.find('"recommendedVideos"', old_10_3_start)
# Find the closing of the entire sub-10-3 dict block
# Pattern: "}],\n            },\n" after the last recommendedVideos
end_of_sub_10_3_videos = content.find('},\n        ],\n    },\n]', after_10_3)
if end_of_sub_10_3_videos == -1:
    # Try alternative pattern
    end_of_sub_10_3_videos = content.find('},\n        ],\n    },\n]\n', after_10_3)

print(f"block_start_10_1: {block_start_10_1}")
print(f"block_start_10_2: {block_start_10_2}")
print(f"block_start_10_3: {block_start_10_3}")
print(f"end_of_sub_10_3_videos: {end_of_sub_10_3_videos}")

# Show what's near the end
if end_of_sub_10_3_videos != -1:
    print(f"Content around end: {repr(content[end_of_sub_10_3_videos:end_of_sub_10_3_videos+60])}")

# Extract the old sub-10-1 block (from its { to sub-10-2's {)
old_sub_10_1 = content[block_start_10_1:block_start_10_2]
print(f"\nOld sub-10-1 block length: {len(old_sub_10_1)}")
print(f"Old sub-10-1 starts with: {repr(old_sub_10_1[:100])}")
print(f"Old sub-10-1 ends with: {repr(old_sub_10_1[-100:])}")
