#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility to convert any explanation text into visual ASCII format
Provides fallback visual formatting for missing visual explanations
"""
import sys
import io

# Handle Unicode on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def format_text_visually(text: str, title: str = "Explanation") -> str:
    """
    Convert plain text explanation into visual ASCII art format with diagrams
    
    Args:
        text: Plain text explanation to visualize
        title: Title for the visualization
    
    Returns:
        Visually formatted text with ASCII diagrams and structure
    """
    if not text or len(text.strip()) < 10:
        return ""
    
    # Split text into sentences/paragraphs for better structure
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    if not paragraphs:
        paragraphs = text.split('. ')
    
    # Build visual representation using ASCII-safe characters only
    visual = []
    visual.append("=" * 80)
    visual.append(f"## {title.upper()}")
    visual.append("=" * 80)
    visual.append("")
    
    # Add overview box
    visual.append("+--- OVERVIEW " + "-" * 65 + "+")
    overview = paragraphs[0] if paragraphs else text[:100]
    if len(overview) > 76:
        # Wrap long text
        words = overview.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 74:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        for line in lines[:3]:  # Max 3 lines for overview
            visual.append(f"| {line:<76} |")
    else:
        visual.append(f"| {overview:<76} |")
    visual.append("+" + "-" * 78 + "+")
    visual.append("")
    
    # Add structure diagram
    visual.append("+--- KEY CONCEPT FLOW " + "-" * 57 + "+")
    visual.append("|                                                                              |")
    visual.append("|  +====================================+                                   |")
    visual.append("|  |    MAIN COMPONENTS                |                                   |")
    visual.append("|  +====================================+                                   |")
    
    # Extract key concepts or use paragraphs
    key_concepts = []
    for para in paragraphs[1:4]:  # Next 3 paragraphs
        first_sentence = para.split('.')[0] if '.' in para else para
        if len(first_sentence) > 10:
            key_concepts.append(first_sentence[:70])
    
    if key_concepts:
        for i, concept in enumerate(key_concepts, 1):
            visual.append(f"|  | {i}. {concept:<64} |                                   |")
    else:
        visual.append("|  | * Detailed explanation of core principles and concepts         |                                   |")
        visual.append("|  | * Practical applications and use cases                          |                                   |")
        visual.append("|  | * Benefits and advantages of understanding this topic          |                                   |")
    
    visual.append("|  +====================================+                                   |")
    visual.append("|                                                                              |")
    visual.append("+" + "-" * 78 + "+")
    visual.append("")
    
    # Add implementation layers
    visual.append("+--- IMPLEMENTATION STRUCTURE " + "-" * 50 + "+")
    visual.append("|                                                                              |")
    visual.append("|  +-----------------------------------+                                    |")
    visual.append("|  |  ABSTRACTION LAYER                |                                    |")
    visual.append("|  |  * High-level concepts and        |                                    |")
    visual.append("|  |    patterns                       |                                    |")
    visual.append("|  +-----------------------------------+                                    |")
    visual.append("|                       DOWN                                                  |")
    visual.append("|  +-----------------------------------+                                    |")
    visual.append("|  |  IMPLEMENTATION LAYER             |                                    |")
    visual.append("|  |  * Code structures and practical  |                                    |")
    visual.append("|  |    implementation                 |                                    |")
    visual.append("|  +-----------------------------------+                                    |")
    visual.append("|                       DOWN                                                  |")
    visual.append("|  +-----------------------------------+                                    |")
    visual.append("|  |  EXECUTION LAYER                  |                                    |")
    visual.append("|  |  * Runtime behavior and results   |                                    |")
    visual.append("|  +-----------------------------------+                                    |")
    visual.append("|                                                                              |")
    visual.append("+" + "-" * 78 + "+")
    visual.append("")
    
    # Add data flow diagram
    visual.append("+--- DATA & INFORMATION FLOW " + "-" * 50 + "+")
    visual.append("|                                                                              |")
    visual.append("|  INPUT ------+                                                             |")
    visual.append("|              +---> [PROCESSING] ---> [TRANSFORMATION] ---> OUTPUT         |")
    visual.append("|  RESOURCES ---+                                                            |")
    visual.append("|                                                                              |")
    visual.append("+" + "-" * 78 + "+")
    visual.append("")
    
    # Add final summary
    visual.append("=" * 80)
    visual.append("SUMMARY: This explanation provides comprehensive understanding")
    visual.append("through multiple perspectives - conceptual, practical, and operational.")
    visual.append("=" * 80)
    
    return "\n".join(visual)


def get_visual_explanation_with_fallback(topic: dict) -> str:
    """
    Get visual explanation from topic, with fallback to formatting other explanations
    
    Args:
        topic: Topic dictionary from database
    
    Returns:
        Visual explanation text (either original or formatted from fallback)
    """
    explanations = topic.get("explanations", {})
    
    # First, try to get the existing visual explanation
    visual = explanations.get("visual", "")
    if visual and len(str(visual).strip()) > 100:
        return visual
    
    # Fallback: Use other explanations in priority order
    fallback_order = ["logical", "analogy", "simplified"]
    
    for style in fallback_order:
        explanation_text = explanations.get(style, "")
        if explanation_text and len(str(explanation_text).strip()) > 50:
            # Format this explanation visually
            formatted = format_text_visually(
                str(explanation_text),
                title=f"Visual {style.capitalize()} Explanation"
            )
            if formatted:
                return formatted
    
    # Last resort: Create a basic visual from topic name
    topic_name = topic.get("name", "Topic")
    basic_visual = f"""
+================================================================================+
|                        {topic_name.upper():^76} |
+================================================================================+
|                                                                              |
|  This topic covers important concepts and practical applications related to:|
|  {topic_name:<76} |
|                                                                              |
|  +------------------------------------------------------------------------+ |
|  | KEY LEARNING AREAS:                                                    | |
|  | * Core concepts and definitions                                        | |
|  | * Practical implementation and examples                                | |
|  | * Best practices and common patterns                                   | |
|  | * Real-world applications and use cases                                | |
|  +------------------------------------------------------------------------+ |
|                                                                              |
+================================================================================+
"""
    return basic_visual.strip()


if __name__ == "__main__":
    # Test the utility
    sample_text = """
    Variables are containers for storing data values. In Python, you can create
    variables simply by assigning a value to a name. Variables can hold different
    types of data including strings, numbers, and boolean values. The syntax is
    straightforward and doesn't require type declarations.
    """
    
    visual = format_text_visually(sample_text, "Variables")
    print(visual)
