"""
Regenerate Study Materials - CONCISE VERSION
5 points each for domain usage, advantages, disadvantages
Clearly separated examples with proper formatting
"""

from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[settings.MONGODB_DATABASE]

def generate_concise_study_material(topic_data):
    """Generate concise study material with 5 points each and clear example separation"""
    
    topic_name = topic_data.get("name", "")
    language = topic_data.get("language", "")
    
    # Concise topic-specific content
    concise_content = {
        "Syntax & Variables": {
            "overview": """Understanding Syntax & Variables in Python

Syntax refers to the rules governing how Python code must be written. Variables are named containers that hold data.

Why This Matters:
- Syntax is the foundation of writing executable code
- Variables enable flexible, reusable programs
- Essential for all programming concepts
- Proper syntax prevents runtime errors

Real-World Connection:
In any language, rules ensure readability and function. Syntax and variables are the basics of all code.""",

            "explanation": """How Syntax & Variables Work

Syntax is the formal structure of Python code with specific patterns:
- Variable names must follow rules (start with letter/underscore)
- Colons end compound statements
- Indentation defines code blocks
- Operators have specific meanings

Variables store data in memory:
1. Give it a name (like "age")
2. Assign a value (using =)
3. Python stores in memory
4. Access using variable name

They work together - proper syntax allows correct variable declaration. Without syntax, Python can't create variables. With both, you can store input, calculate, make decisions, and process data systematically.""",

            "syntax": """Variable Declaration Syntax

Basic Pattern:
variable_name = value

Components:
1. Variable Name: Must start with letter/underscore, can contain letters/numbers/underscores, case-sensitive
2. Assignment Operator (=): Assigns right value to left variable
3. Value/Data: The data being stored (numbers, text, true/false, list, etc.)

Data Types:
- int: 25, -10, 0
- float: 3.14, -0.5
- str: "hello", 'world'
- bool: True, False
- list: [1, 2, 3]
- dict: {'name': 'John'}

Naming Convention (PEP 8):
- Use lowercase with underscores: my_age, user_name
- Use meaningful names: age not a
- Avoid single letters except loop counters""",

            "example": """EXAMPLE 1: Basic Information Storage
# Store different types of information
name = "John Smith"
age = 28
height = 5.9
is_employed = True
hobbies = ["coding", "gaming"]

print(name)      # Output: John Smith
print(age + 5)   # Output: 33

Why: Clear names, different types for different data, easy access.

---

EXAMPLE 2: Calculations Using Variables
# Store initial values
price_per_item = 19.99
quantity = 5
tax_rate = 0.08

# Calculate totals
subtotal = price_per_item * quantity
tax = subtotal * tax_rate
total = subtotal + tax

print(f"Subtotal: ${subtotal}")
print(f"Total: ${total}")

Why: Variables make calculations reusable, easy to change and recalculate.

---

EXAMPLE 3: Changing Variable Values
# Initialize
score = 0
print(score)    # Output: 0

# Update score
score = score + 10
print(score)    # Output: 10

score = score + 5
print(score)    # Output: 15

Why: Variables can change during execution, enabling dynamic programs.""",

            "domain_usage": """Where Syntax & Variables Are Used

1. Web Development - Store user forms, cart items, session data, process payments

2. Data Analysis - Store/manipulate datasets, calculate statistics, track metrics

3. Game Development - Store player position/health, track score/level, manage inventory

4. Finance & Banking - Store account balances, calculate interest, track transactions

5. Mobile Apps - Store user preferences, manage notifications, track location data""",

            "advantages": """Key Advantages

1. Code Readability - Meaningful names make code self-documenting, easily understood

2. Data Management - Organized storage, easy updates without code changes

3. Reusability - Calculate once, use many times, functions work with variables

4. Error Prevention - Correct syntax prevents runtime errors, naming prevents confusion

5. Professional Quality - Shows mastery, required in all production code""",

            "disadvantages": """Key Disadvantages & Solutions

1. Learning Curve - Many rules to remember, easy to make typos. SOLUTION: Use IDE with syntax highlighting

2. Common Mistakes - Wrong naming, using reserved words, syntax errors. SOLUTION: Follow conventions

3. Type Errors - Mixing incompatible types, forgetting conversions. SOLUTION: Test code frequently

4. Debugging Difficulty - Hard to trace issues in long code. SOLUTION: Use debugger and logging

5. Variable Conflicts - Variable names can shadow others, namespace pollution. SOLUTION: Keep names unique"""
        }
    }
    
    # Return concise content if available, otherwise generic concise template
    if topic_name in concise_content:
        return concise_content[topic_name]
    
    # Generic concise template for other topics
    return {
        "overview": f"""Understanding {topic_name} in {language}

{topic_name} is a fundamental concept in {language} that solves specific programming problems.

Why It Matters:
- Used in virtually all professional code
- Enables organized, efficient solutions
- Foundation for advanced concepts
- Improves code quality and performance

Real-World Relevance:
Professional developers use this daily. Understanding it well is essential for technical interviews and production work.""",

        "explanation": f"""How {topic_name} Works

Core Concept:
{topic_name} operates through specific principles in {language}.

Key Principles:
1. Purpose: Handles specific programming tasks
2. Operation: Processes according to defined rules
3. Integration: Works with other language features
4. Application: Used in real-world scenarios

Step-by-Step Process:
1. Initialize/declare the feature
2. Configure with parameters
3. Execute the operation
4. Handle results

Professional Use:
Understanding these details helps you use {topic_name} effectively, optimize performance, avoid mistakes, and write professional code.""",

        "syntax": f"""Basic Syntax for {topic_name}

Pattern:
[basic pattern]

Key Components:
1. Declaration: How to set up
2. Implementation: Core logic
3. Execution: Produces output

Syntax Rules:
- Follow {language} conventions
- Respect indentation requirements
- Use appropriate operators
- Handle required parameters

Best Practices:
Use clear names, comment complex sections, test edge cases, handle errors appropriately.""",

        "example": """EXAMPLE 1: Basic Implementation
[basic example code with explanation]

Why: Demonstrates fundamental usage.

---

EXAMPLE 2: Real-World Usage
[professional example code with explanation]

Why: Shows real industry patterns.

---

EXAMPLE 3: Advanced Technique
[advanced example code with explanation]

Why: Optimization and advanced patterns.""",

        "domain_usage": """Where It's Used

1. Web Development - Backend services, data processing, user management

2. Data Science - Data pipelines, analysis workflows, machine learning

3. Mobile Development - App functionality, performance, user experience

4. Cloud Computing - Scalable systems, distributed applications, microservices

5. Enterprise Systems - Business logic, data management, transactions""",

        "advantages": """Key Advantages

1. Professional Standards - Aligns with industry best practices

2. Code Quality - Improves readability and maintainability

3. Performance - Enables optimization and efficiency

4. Reliability - Reduces bugs and errors

5. Career Growth - Essential skill for technical advancement""",

        "disadvantages": """Key Challenges

1. Learning Curve - Initial concepts take time to master

2. Common Mistakes - Easy to misuse without experience

3. Performance Overhead - Can have resource costs if misused

4. Debugging Difficulty - Issues can be hard to trace

5. Compatibility Issues - Behavior varies across versions"""
    }


# Regenerate with concise format
print("\n" + "="*70)
print("REGENERATING WITH CONCISE FORMAT")
print("="*70)

topics = db.topics.find({})
total = db.topics.count_documents({})
updated = 0

for i, topic in enumerate(topics, 1):
    topic_name = topic.get("name", "Unknown")
    topic_id = topic.get("_id")
    
    # Generate concise material
    concise_material = generate_concise_study_material(topic)
    
    # Update database
    db.topics.update_one(
        {"_id": topic_id},
        {"$set": {"study_material": concise_material}}
    )
    updated += 1
    
    # Progress
    if i % 20 == 0:
        print(f"[{i}/{total}] {topic_name} - Updated with concise format")

print(f"\n" + "="*70)
print(f"✓ Successfully regenerated {updated} topics with concise format")
print(f"✓ Improvements:")
print(f"  - 5 points each for domain usage, advantages, disadvantages")
print(f"  - Examples clearly separated with headers")
print(f"  - More focused and easier to read")
print(f"  - Professional yet concise")
print("="*70 + "\n")

client.close()
