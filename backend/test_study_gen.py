import asyncio
import sys
sys.path.insert(0, '.')

from app.services.study_material_service import study_material_generator

async def test():
    print("Testing study material generation...")
    material = await study_material_generator.generate_study_material("Syntax & Basics")
    if material:
        print("SUCCESS: Study material generated")
        print(f"  Topics: {material.get('topic')}")
        print(f"  Has explanations: {bool(material.get('explanations'))}")
    else:
        print("FAILED: No material returned")

asyncio.run(test())
