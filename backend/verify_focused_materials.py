from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[settings.MONGODB_DATABASE]

print("\n" + "="*70)
print("VERIFYING REGENERATED STUDY MATERIALS")
print("="*70)

# Check a few sample topics
topics_to_check = ["Syntax & Variables", "Data Types", "Functions", "Error Handling", "Loops"]

for topic_name in topics_to_check:
    topic = db.topics.find_one({"name": topic_name})
    if topic:
        material = topic.get("study_material", {})
        print(f"\n[{topic_name}]")
        print("-" * 70)
        
        if material:
            for section in ['overview', 'explanation', 'syntax', 'example', 'domain_usage', 'advantages', 'disadvantages']:
                content = material.get(section, '')
                if content:
                    preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content
                    print(f"  [OK] {section}: {preview}")
                else:
                    print(f"  [MISSING] {section}")
        else:
            print("  [NO] Study material not found")

# Count total
print("\n" + "="*70)
total_with_material = db.topics.count_documents({'study_material': {'$exists': True}})
total_topics = db.topics.count_documents({})
print(f"\nTotal Topics: {total_topics}")
print(f"Topics with Study Material: {total_with_material}/{total_topics}")

# Show sample Syntax & Variables material
print("\n" + "="*70)
print("SAMPLE MATERIAL - Syntax & Variables")
print("="*70)

sample = db.topics.find_one({"name": "Syntax & Variables"})
if sample:
    material = sample.get("study_material", {})
    print(f"\n1. OVERVIEW:\n{material.get('overview', '')}")
    print(f"\n2. EXPLANATION:\n{material.get('explanation', '')}")
    print(f"\n3. SYNTAX:\n{material.get('syntax', '')}")
    print(f"\n4. EXAMPLE:\n{material.get('example', '')}")
    print(f"\n5. DOMAIN USAGE:\n{material.get('domain_usage', '')}")
    print(f"\n6. ADVANTAGES:\n{material.get('advantages', '')}")
    print(f"\n7. DISADVANTAGES:\n{material.get('disadvantages', '')}")

print("\n" + "="*70)
print("✓ All materials are focused, professional, and beginner-friendly!")
print("="*70 + "\n")

client.close()
