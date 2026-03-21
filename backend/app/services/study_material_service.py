"""
Study Material Generator with 4 Explanation Types
Generates beginner, intermediate, advanced, and expert level explanations
Uses OpenRouter for better rate limits and reliability
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from app.core.config import settings
from app.services.openrouter_service import openrouter_service

logger = logging.getLogger(__name__)

class ExplanationLevel(Enum):
    """Explanation difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class StudyMaterialGenerator:
    """Generate study materials with multiple explanation levels"""
    
    def __init__(self):
        self.api_service = openrouter_service
    
    async def generate_study_material(
        self,
        topic_name: str,
        learning_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate complete study material for a topic with all 4 levels"""
        try:
            logger.info(f"Generating study material for topic: {topic_name}")
            
            # Generate explanations for all 4 levels
            explanations = {}
            for level in ExplanationLevel:
                logger.info(f"  Generating {level.value} explanation...")
                explanations[level.value] = await self._generate_explanation(
                    topic_name,
                    level,
                    learning_level
                )
                await asyncio.sleep(0.5)  # Rate limiting
            
            # Generate key concepts
            concepts = await self._generate_key_concepts(topic_name)
            await asyncio.sleep(0.5)
            
            # Generate practice questions
            questions = await self._generate_practice_questions(topic_name)
            await asyncio.sleep(0.5)
            
            # Generate real-world examples
            examples = await self._generate_real_world_examples(topic_name)
            
            study_material = {
                "topic": topic_name,
                "generated_at": datetime.now().isoformat(),
                "learning_level": learning_level or "adaptive",
                "explanations": explanations,
                "key_concepts": concepts,
                "practice_questions": questions,
                "real_world_examples": examples,
                "feedback": None,
                "regeneration_count": 0
            }
            
            logger.info(f"✅ Study material generated for: {topic_name}")
            return study_material
            
        except Exception as e:
            logger.error(f"Error generating study material: {e}")
            return {}
    
    async def _generate_explanation(
        self,
        topic_name: str,
        level: ExplanationLevel,
        learning_level: Optional[str]
    ) -> Dict[str, Any]:
        """Generate explanation at specific difficulty level"""
        
        prompts = {
            ExplanationLevel.BEGINNER: f"""Explain '{topic_name}' for a complete beginner with NO technical background.
Use:
- Very simple words (no jargon)
- Everyday analogies and examples
- Short sentences (max 2 lines each)
- Visual description of concepts

Format:
1. What is it? (1 paragraph max)
2. Why does it matter? (1 paragraph max)
3. Simple example (1 paragraph max)
4. Common misconceptions (bullet points)""",
            ExplanationLevel.INTERMEDIATE: f"""Explain '{topic_name}' for someone with basic knowledge in this field.
Use:
- Technical terms with brief definitions
- Step-by-step breakdown
- Connections to related concepts
- Practical applications

Format:
1. Definition and context (2 paragraphs)
2. How it works (3-4 steps)
3. Key components (detailed)
4. Common use cases (bullet points)
5. Limitations to be aware of""",
            ExplanationLevel.ADVANCED: f"""Provide an advanced technical explanation of '{topic_name}'.
Use:
- Industry-standard terminology
- Implementation details
- Performance considerations
- Edge cases and trade-offs

Format:
1. Technical definition (2 paragraphs)
2. Architecture and design (with pseudocode if applicable)
3. Performance analysis (time/space complexity)
4. Advanced patterns and techniques
5. Integration with other systems
6. Optimization strategies""",
            ExplanationLevel.EXPERT: f"""Provide an expert-level deep dive into '{topic_name}'.
Use:
- Research-backed explanations
- Recent developments and innovations
- Academic references
- Cutting-edge techniques

Format:
1. Theoretical foundations (academic depth)
2. Current research and trends
3. Advanced implementation strategies
4. Future directions
5. Critical analysis of limitations
6. Comparative study with alternatives"""
        }
        
        try:
            messages = [{"role": "user", "content": prompts[level]}]
            response = await asyncio.to_thread(
                self.api_service.chat,
                messages
            )
            
            content = response.get("content", "") if response else ""
            
            return {
                "level": level.value,
                "content": content,
                "generated_at": datetime.now().isoformat(),
                "usage_feedback": None
            }
        except Exception as e:
            logger.error(f"Error generating {level.value} explanation: {e}")
            return {
                "level": level.value,
                "content": f"Error generating {level.value} explanation",
                "error": str(e)
            }
    
    async def _generate_key_concepts(self, topic_name: str) -> List[Dict[str, str]]:
        """Generate key concepts for the topic"""
        prompt = f"""For the topic '{topic_name}', list 10 key concepts that learners MUST understand.
For each concept, provide:
1. Name of concept
2. One-line definition
3. Why it's important

Format as JSON array with objects containing: name, definition, importance
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(
                self.api_service.chat,
                messages
            )
            
            text = response.get("content", "") if response else ""
            # Remove markdown code blocks if present
            text = text.replace("```json", "").replace("```", "").strip()
            
            concepts = json.loads(text)
            return concepts if isinstance(concepts, list) else []
        except Exception as e:
            logger.error(f"Error generating key concepts: {e}")
            return []
    
    async def _generate_practice_questions(self, topic_name: str) -> List[Dict[str, Any]]:
        """Generate practice questions at different difficulty levels"""
        prompt = f"""Generate 10 practice questions for '{topic_name}':
- 3 easy questions (test basic understanding)
- 3 medium questions (require application)
- 4 hard questions (require analysis/synthesis)

For each question provide:
- question: the question text
- difficulty: easy/medium/hard
- correct_answer: brief answer
- explanation: why this is correct

Format as JSON array of objects.
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(
                self.api_service.chat,
                messages
            )
            
            text = response.get("content", "") if response else ""
            text = text.replace("```json", "").replace("```", "").strip()
            
            questions = json.loads(text)
            return questions if isinstance(questions, list) else []
        except Exception as e:
            logger.error(f"Error generating practice questions: {e}")
            return []
    
    async def _generate_real_world_examples(self, topic_name: str) -> List[Dict[str, str]]:
        """Generate real-world examples"""
        prompt = f"""Provide 5 real-world examples demonstrating '{topic_name}' in practice.
For each example:
- scenario: real-life situation where this is used
- application: how {topic_name} is applied
- outcome: what happens as a result

Format as JSON array of objects.
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(
                self.api_service.chat,
                messages
            )
            
            text = response.get("content", "") if response else ""
            text = text.replace("```json", "").replace("```", "").strip()
            
            examples = json.loads(text)
            return examples if isinstance(examples, list) else []
        except Exception as e:
            logger.error(f"Error generating real-world examples: {e}")
            return []
    
    async def analyze_feedback_and_regenerate(
        self,
        original_material: Dict[str, Any],
        user_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user feedback and regenerate material at appropriate level"""
        
        try:
            logger.info("Analyzing user feedback and determining learning level...")
            
            # Analyze feedback to determine understanding level
            understanding_level = await self._analyze_user_understanding(
                original_material,
                user_feedback
            )
            
            logger.info(f"Determined understanding level: {understanding_level}")
            
            # Add feedback to material
            original_material["feedback"] = user_feedback
            original_material["regeneration_count"] = original_material.get("regeneration_count", 0) + 1
            
            # Regenerate study material at appropriate level
            if understanding_level != original_material.get("learning_level"):
                logger.info(f"Regenerating material at {understanding_level} level...")
                
                regenerated_material = await self.generate_study_material(
                    original_material["topic"],
                    understanding_level
                )
                
                regenerated_material["previous_feedback"] = user_feedback
                regenerated_material["regeneration_count"] = original_material["regeneration_count"]
                
                return regenerated_material
            
            return original_material
            
        except Exception as e:
            logger.error(f"Error in feedback analysis and regeneration: {e}")
            return original_material
    
    async def _analyze_user_understanding(
        self,
        material: Dict[str, Any],
        feedback: Dict[str, Any]
    ) -> str:
        """Analyze user feedback to determine understanding level"""
        
        prompt = f"""Based on this user feedback about study material, determine their understanding level:

Topic: {material.get('topic')}
User Feedback:
- Difficulty rating (1-10): {feedback.get('difficulty_rating', 5)}
- Clarity score (1-10): {feedback.get('clarity_score', 5)}
- Comments: {feedback.get('comments', 'None')}
- Questions asked: {feedback.get('questions_asked', [])}
- Concepts they struggled with: {feedback.get('struggled_concepts', [])}
- Concepts they understood well: {feedback.get('understood_concepts', [])}

Based on this feedback, determine if the user needs:
- BEGINNER level (too complex, needs simpler explanation)
- INTERMEDIATE level (good balance)
- ADVANCED level (too simple, needs more depth)
- EXPERT level (wants research-level content)

Respond with ONLY the single word level name (BEGINNER, INTERMEDIATE, ADVANCED, or EXPERT)
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await asyncio.to_thread(
                self.api_service.chat,
                messages
            )
            
            level_text = response.get("content", "").strip().upper() if response else "INTERMEDIATE"
            
            # Map to our enum
            level_map = {
                "BEGINNER": "beginner",
                "INTERMEDIATE": "intermediate",
                "ADVANCED": "advanced",
                "EXPERT": "expert"
            }
            
            return level_map.get(level_text, "intermediate")
        except Exception as e:
            logger.error(f"Error analyzing user understanding: {e}")
            return "intermediate"

# Global instance
study_material_generator = StudyMaterialGenerator()
