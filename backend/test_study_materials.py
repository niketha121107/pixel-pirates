#!/usr/bin/env python
"""Test study material generation and PDF creation"""

import asyncio
import sys
import io
import os

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.services.study_material_service import study_material_generator
from app.services.pdf_generator_service import pdf_generator

async def test_study_material_generation():
    """Test generating study material for a sample topic"""
    
    print("=" * 70)
    print("TESTING STUDY MATERIAL GENERATION")
    print("=" * 70)
    
    test_topic = "Python Functions and Scope"
    
    print(f"\n1. Generating study material for: '{test_topic}'")
    print("-" * 70)
    
    study_material = await study_material_generator.generate_study_material(test_topic)
    
    if not study_material:
        print("ERROR: Failed to generate study material")
        return False
    
    print("✓ Study material generated successfully")
    print(f"  - Learning level: {study_material.get('learning_level')}")
    print(f"  - Explanations: {len(study_material.get('explanations', {}))} levels")
    print(f"  - Key concepts: {len(study_material.get('key_concepts', []))} concepts")
    print(f"  - Practice questions: {len(study_material.get('practice_questions', []))} questions")
    print(f"  - Real-world examples: {len(study_material.get('real_world_examples', []))} examples")
    
    # Print sample beginner explanation
    beginner_exp = study_material.get('explanations', {}).get('beginner', {})
    if beginner_exp.get('content'):
        print("\n2. Sample Beginner Explanation (first 300 chars):")
        print("-" * 70)
        content = beginner_exp.get('content', '')
        print(content[:300] + "..." if len(content) > 300 else content)
    
    # Print sample key concept
    concepts = study_material.get('key_concepts', [])
    if concepts:
        print("\n3. Sample Key Concepts:")
        print("-" * 70)
        for concept in concepts[:2]:
            print(f"  • {concept.get('name')}: {concept.get('definition')}")
    
    # Print sample practice question
    questions = study_material.get('practice_questions', [])
    if questions:
        print("\n4. Sample Practice Question:")
        print("-" * 70)
        q = questions[0]
        print(f"  Q: {q.get('question')}")
        print(f"  A: {q.get('correct_answer')}")
    
    # Test PDF generation
    print("\n5. Testing PDF Generation:")
    print("-" * 70)
    
    os.makedirs("storage/pdfs", exist_ok=True)
    pdf_path = "storage/pdfs/test_study_material.pdf"
    
    success = pdf_generator.generate_pdf(study_material, pdf_path)
    
    if success and os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"✓ PDF generated successfully")
        print(f"  - Path: {pdf_path}")
        print(f"  - Size: {file_size} bytes")
    else:
        print("ERROR: Failed to generate PDF")
        return False
    
    # Test feedback analysis
    print("\n6. Testing Feedback Analysis and Regeneration:")
    print("-" * 70)
    
    user_feedback = {
        "difficulty_rating": 3,
        "clarity_score": 4,
        "comments": "Too technical, needs simpler explanation",
        "struggled_concepts": ["scope", "closures"],
        "understood_concepts": ["function basics"]
    }
    
    print(f"  Feedback: {user_feedback}")
    print("\n  Analyzing and regenerating...")
    
    regenerated = await study_material_generator.analyze_feedback_and_regenerate(
        study_material,
        user_feedback
    )
    
    print(f"✓ Regeneration completed")
    print(f"  - New learning level: {regenerated.get('learning_level')}")
    print(f"  - Regeneration count: {regenerated.get('regeneration_count')}")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_study_material_generation())
        
        if success:
            print("\n" + "=" * 70)
            print("ALL TESTS PASSED!")
            print("=" * 70)
        else:
            print("\nTESTS FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
