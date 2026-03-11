"""
Generate 200 programming topics and seed them into MongoDB.

Each topic has:
 - 4 explanation styles (simplified, logical, visual, analogy) with code examples
 - 10 quiz questions (MCQ)
 - Flowchart data
 - Overview, difficulty, language tag
 - Recommended videos placeholder

Run:  python generate_200_topics.py
"""

import json, uuid, pymongo, sys, os

# ── Topic definitions: 200 topics across languages ──────────────────
# Each entry: (language, topicName, difficulty, brief_seed)
TOPIC_DEFS = [
    # ── Python (50 topics) ──────────────────────────────────────────
    ("Python", "Variables & Data Types", "Beginner", "int, float, str, bool, type conversion, dynamic typing"),
    ("Python", "Strings & String Methods", "Beginner", "slicing, f-strings, split, join, replace, find, upper, lower"),
    ("Python", "Numbers & Math Operations", "Beginner", "arithmetic, floor division, modulus, math module, abs, round"),
    ("Python", "Boolean Logic & Comparisons", "Beginner", "and, or, not, truthiness, comparison operators, short-circuit"),
    ("Python", "If/Elif/Else Conditions", "Beginner", "branching, nested conditions, ternary operator, match-case"),
    ("Python", "For Loops", "Beginner", "range(), enumerate(), iterating lists/strings, nested loops, break/continue"),
    ("Python", "While Loops", "Beginner", "condition-based looping, infinite loops, break, sentinel values"),
    ("Python", "Lists & List Methods", "Beginner", "append, insert, remove, sort, reverse, slicing, list comprehension"),
    ("Python", "Tuples & Immutability", "Beginner", "packing, unpacking, named tuples, tuple vs list, hashability"),
    ("Python", "Dictionaries", "Beginner", "key-value pairs, get, items, keys, values, dict comprehension"),
    ("Python", "Sets & Set Operations", "Beginner", "union, intersection, difference, symmetric_difference, frozenset"),
    ("Python", "Functions & Parameters", "Intermediate", "def, return, default args, *args, **kwargs, docstrings"),
    ("Python", "Lambda & Higher-Order Functions", "Intermediate", "lambda, map, filter, reduce, functools"),
    ("Python", "List Comprehensions", "Intermediate", "filtering, nested comprehensions, dict/set comprehensions"),
    ("Python", "File Handling", "Intermediate", "open, read, write, with statement, CSV, JSON file I/O"),
    ("Python", "Error Handling & Exceptions", "Intermediate", "try/except/finally, raise, custom exceptions, traceback"),
    ("Python", "Modules & Packages", "Intermediate", "import, from, __init__.py, pip, virtual environments"),
    ("Python", "Object-Oriented Programming", "Intermediate", "classes, __init__, self, attributes, methods, encapsulation"),
    ("Python", "Inheritance & Polymorphism", "Intermediate", "super(), method overriding, isinstance, abstract classes"),
    ("Python", "Decorators", "Advanced", "function wrappers, @syntax, functools.wraps, decorator with args"),
    ("Python", "Generators & Iterators", "Advanced", "yield, next(), generator expressions, itertools, lazy evaluation"),
    ("Python", "Context Managers", "Advanced", "with statement, __enter__/__exit__, contextlib, resource management"),
    ("Python", "Regular Expressions", "Intermediate", "re module, patterns, match, search, findall, groups, substitution"),
    ("Python", "Recursion", "Intermediate", "base case, recursive case, stack overflow, memoization, tail recursion"),
    ("Python", "Closures & Scope", "Advanced", "LEGB rule, nonlocal, global, closure over variables, factory functions"),
    ("Python", "Type Hints & Annotations", "Intermediate", "typing module, Optional, List, Dict, Union, Protocol, mypy"),
    ("Python", "Virtual Environments & pip", "Beginner", "venv, pip install, requirements.txt, dependency management"),
    ("Python", "Working with APIs", "Intermediate", "requests library, REST APIs, JSON parsing, authentication, headers"),
    ("Python", "Unit Testing", "Intermediate", "unittest, pytest, assertions, fixtures, mocking, test coverage"),
    ("Python", "Data Classes", "Intermediate", "@dataclass, field defaults, frozen, __post_init__, comparison"),
    ("Python", "Concurrency - Threading", "Advanced", "threading module, GIL, locks, thread pool, race conditions"),
    ("Python", "Concurrency - Asyncio", "Advanced", "async/await, event loop, coroutines, aiohttp, gather"),
    ("Python", "Database with SQLite", "Intermediate", "sqlite3, CRUD, parameterized queries, cursor, connection"),
    ("Python", "Web Scraping", "Intermediate", "BeautifulSoup, requests, parsing HTML, selectors, ethical scraping"),
    ("Python", "NumPy Basics", "Intermediate", "arrays, broadcasting, slicing, vectorization, dtype, reshape"),
    ("Python", "Pandas Basics", "Intermediate", "DataFrame, Series, read_csv, filtering, groupby, merge"),
    ("Python", "Matplotlib Visualization", "Intermediate", "plot, bar, scatter, histogram, subplots, labels, styles"),
    ("Python", "Flask Web Framework", "Intermediate", "routes, templates, request/response, Jinja2, REST API"),
    ("Python", "FastAPI Basics", "Intermediate", "async routes, Pydantic models, dependency injection, OpenAPI docs"),
    ("Python", "Command Line Arguments", "Beginner", "sys.argv, argparse, click, CLI tool creation"),
    ("Python", "String Formatting", "Beginner", "f-strings, format(), %-formatting, template strings, alignment"),
    ("Python", "Collections Module", "Advanced", "Counter, defaultdict, OrderedDict, deque, namedtuple, ChainMap"),
    ("Python", "Magic Methods (Dunder)", "Advanced", "__str__, __repr__, __len__, __getitem__, __eq__, operator overloading"),
    ("Python", "Property Decorators", "Advanced", "@property, getter/setter, computed attributes, validation"),
    ("Python", "Metaclasses", "Advanced", "type(), __new__, __init_subclass__, class factories, ABCMeta"),
    ("Python", "Descriptors", "Advanced", "__get__, __set__, __delete__, data vs non-data descriptors"),
    ("Python", "Memory Management", "Advanced", "reference counting, garbage collection, gc module, weak references"),
    ("Python", "Logging Module", "Intermediate", "logging levels, handlers, formatters, rotating files, best practices"),
    ("Python", "Pathlib & OS Module", "Beginner", "Path objects, os.path, file system navigation, glob patterns"),
    ("Python", "Enum & Constants", "Intermediate", "Enum class, auto(), IntEnum, Flag, constant patterns"),

    # ── JavaScript (50 topics) ──────────────────────────────────────
    ("JavaScript", "Variables & Scope", "Beginner", "let, const, var, block scope, function scope, hoisting"),
    ("JavaScript", "Data Types & Coercion", "Beginner", "primitives, objects, typeof, ==, ===, type coercion rules"),
    ("JavaScript", "Strings & Template Literals", "Beginner", "backticks, interpolation, tagged templates, string methods"),
    ("JavaScript", "Arrays & Array Methods", "Beginner", "push, pop, map, filter, reduce, find, includes, spread"),
    ("JavaScript", "Objects & Object Methods", "Beginner", "properties, methods, this, Object.keys/values/entries, spread"),
    ("JavaScript", "Functions & Arrow Functions", "Beginner", "declaration, expression, arrow syntax, default params, rest"),
    ("JavaScript", "Conditionals & Ternary", "Beginner", "if/else, switch, ternary, nullish coalescing, optional chaining"),
    ("JavaScript", "Loops & Iteration", "Beginner", "for, for...of, for...in, while, do...while, forEach, break/continue"),
    ("JavaScript", "DOM Manipulation", "Intermediate", "querySelector, createElement, addEventListener, classList, attributes"),
    ("JavaScript", "Events & Event Handling", "Intermediate", "click, submit, keydown, bubbling, capturing, delegation, preventDefault"),
    ("JavaScript", "Promises", "Intermediate", "resolve, reject, then, catch, finally, Promise.all, Promise.race"),
    ("JavaScript", "Async/Await", "Intermediate", "async functions, await, error handling, sequential vs parallel"),
    ("JavaScript", "Fetch API & HTTP Requests", "Intermediate", "GET, POST, headers, JSON, error handling, AbortController"),
    ("JavaScript", "Closures", "Intermediate", "lexical scope, closure over variables, data privacy, module pattern"),
    ("JavaScript", "Prototypes & Inheritance", "Intermediate", "prototype chain, __proto__, Object.create, constructor functions"),
    ("JavaScript", "ES6 Classes", "Intermediate", "class syntax, constructor, methods, static, extends, super"),
    ("JavaScript", "Destructuring", "Intermediate", "array destructuring, object destructuring, nested, default values"),
    ("JavaScript", "Spread & Rest Operators", "Intermediate", "array spread, object spread, rest parameters, cloning"),
    ("JavaScript", "Modules (ES6)", "Intermediate", "import/export, default exports, named exports, dynamic import"),
    ("JavaScript", "Error Handling", "Intermediate", "try/catch/finally, throw, custom errors, error types"),
    ("JavaScript", "Local Storage & Session Storage", "Beginner", "setItem, getItem, removeItem, JSON stringify/parse, storage events"),
    ("JavaScript", "Regular Expressions", "Intermediate", "RegExp, test, match, replace, groups, flags, patterns"),
    ("JavaScript", "Map & Set", "Intermediate", "Map vs Object, Set vs Array, WeakMap, WeakSet, iteration"),
    ("JavaScript", "Iterators & Generators", "Advanced", "Symbol.iterator, yield, generator functions, for...of protocol"),
    ("JavaScript", "Proxy & Reflect", "Advanced", "handler traps, get/set, Reflect API, meta-programming"),
    ("JavaScript", "Web Workers", "Advanced", "dedicated workers, SharedArrayBuffer, postMessage, Transferable"),
    ("JavaScript", "Service Workers & PWA", "Advanced", "cache API, offline support, push notifications, install event"),
    ("JavaScript", "Canvas API", "Intermediate", "2D context, shapes, colors, animations, requestAnimationFrame"),
    ("JavaScript", "Web Components", "Advanced", "custom elements, shadow DOM, templates, slots, lifecycle callbacks"),
    ("JavaScript", "TypeScript Basics", "Intermediate", "types, interfaces, generics, enums, type guards, utility types"),
    ("JavaScript", "Node.js Basics", "Intermediate", "modules, fs, path, http, process, event loop, npm"),
    ("JavaScript", "Express.js Framework", "Intermediate", "routing, middleware, request/response, error handling, REST API"),
    ("JavaScript", "JSON & Data Formats", "Beginner", "JSON.parse, JSON.stringify, nested objects, validation"),
    ("JavaScript", "Date & Time Handling", "Beginner", "Date object, formatting, libraries (dayjs), timestamps, timezones"),
    ("JavaScript", "this Keyword", "Intermediate", "binding rules, call, apply, bind, arrow function this"),
    ("JavaScript", "Callback Functions", "Beginner", "callback pattern, callback hell, setTimeout, setInterval"),
    ("JavaScript", "Debounce & Throttle", "Intermediate", "rate limiting, event optimization, implementation, use cases"),
    ("JavaScript", "Symbols & Well-Known Symbols", "Advanced", "Symbol(), Symbol.iterator, Symbol.toPrimitive, unique keys"),
    ("JavaScript", "WeakRef & FinalizationRegistry", "Advanced", "weak references, garbage collection hooks, caching patterns"),
    ("JavaScript", "Intl API (Internationalization)", "Intermediate", "NumberFormat, DateTimeFormat, Collator, locale handling"),
    ("JavaScript", "Functional Programming", "Intermediate", "pure functions, immutability, composition, currying, pipe"),
    ("JavaScript", "Design Patterns", "Advanced", "singleton, observer, factory, strategy, module, MVC patterns"),
    ("JavaScript", "Event Loop & Microtasks", "Advanced", "call stack, task queue, microtask queue, requestAnimationFrame"),
    ("JavaScript", "Memory Management", "Advanced", "garbage collection, memory leaks, WeakMap patterns, profiling"),
    ("JavaScript", "Performance Optimization", "Advanced", "lazy loading, code splitting, tree shaking, memoization"),
    ("JavaScript", "Testing with Jest", "Intermediate", "test, expect, mocking, async testing, snapshots, coverage"),
    ("JavaScript", "React Fundamentals", "Intermediate", "components, JSX, props, state, hooks, virtual DOM"),
    ("JavaScript", "React Hooks Deep Dive", "Advanced", "useState, useEffect, useRef, useMemo, useCallback, custom hooks"),
    ("JavaScript", "State Management", "Advanced", "Context API, Redux, Zustand, state patterns, global vs local"),
    ("JavaScript", "Next.js Basics", "Intermediate", "pages, SSR, SSG, API routes, dynamic routing, deployment"),

    # ── Java (40 topics) ────────────────────────────────────────────
    ("Java", "Variables & Data Types", "Beginner", "primitive types, wrapper classes, type casting, constants"),
    ("Java", "Operators & Expressions", "Beginner", "arithmetic, relational, logical, bitwise, ternary, precedence"),
    ("Java", "Control Flow Statements", "Beginner", "if-else, switch, for, while, do-while, break, continue"),
    ("Java", "Arrays", "Beginner", "declaration, initialization, multidimensional, Arrays class, sorting"),
    ("Java", "Strings & StringBuilder", "Beginner", "String methods, immutability, StringBuilder, StringBuffer, pool"),
    ("Java", "Methods & Method Overloading", "Beginner", "parameters, return types, static, varargs, pass-by-value"),
    ("Java", "Object-Oriented Programming", "Intermediate", "classes, objects, constructors, this keyword, encapsulation"),
    ("Java", "Inheritance", "Intermediate", "extends, super, method overriding, IS-A relationship, Object class"),
    ("Java", "Polymorphism", "Intermediate", "compile-time, runtime, dynamic dispatch, instanceof, casting"),
    ("Java", "Abstraction", "Intermediate", "abstract classes, interfaces, default methods, functional interfaces"),
    ("Java", "Encapsulation", "Intermediate", "access modifiers, getters/setters, data hiding, immutable objects"),
    ("Java", "Exception Handling", "Intermediate", "try-catch-finally, throws, custom exceptions, checked vs unchecked"),
    ("Java", "Collections Framework", "Intermediate", "List, Set, Map, Queue, ArrayList, HashMap, TreeSet, Iterator"),
    ("Java", "Generics", "Intermediate", "type parameters, bounded types, wildcards, type erasure"),
    ("Java", "Java Streams API", "Advanced", "stream(), map, filter, reduce, collect, parallel streams"),
    ("Java", "Lambda Expressions", "Intermediate", "functional interfaces, method references, Predicate, Consumer"),
    ("Java", "File I/O", "Intermediate", "FileReader, BufferedReader, Files class, NIO, try-with-resources"),
    ("Java", "Multithreading", "Advanced", "Thread, Runnable, synchronized, volatile, ExecutorService"),
    ("Java", "JDBC & Database Access", "Intermediate", "Connection, Statement, PreparedStatement, ResultSet, transactions"),
    ("Java", "Design Patterns in Java", "Advanced", "singleton, factory, observer, builder, strategy, decorator"),
    ("Java", "Annotations", "Intermediate", "@Override, @Deprecated, custom annotations, retention, processing"),
    ("Java", "Enums", "Intermediate", "enum declaration, methods, constructors, EnumSet, EnumMap"),
    ("Java", "Inner Classes", "Intermediate", "static nested, non-static inner, anonymous, local, lambda equivalents"),
    ("Java", "Java Memory Model", "Advanced", "heap, stack, garbage collection, GC types, memory leaks"),
    ("Java", "Functional Programming in Java", "Advanced", "Optional, streams, immutability, function composition"),
    ("Java", "Concurrency Utilities", "Advanced", "CountDownLatch, CyclicBarrier, Semaphore, CompletableFuture"),
    ("Java", "Serialization", "Intermediate", "Serializable, ObjectInputStream, ObjectOutputStream, transient"),
    ("Java", "Networking in Java", "Intermediate", "Socket, ServerSocket, URL, HttpURLConnection, HTTP client"),
    ("Java", "JUnit Testing", "Intermediate", "@Test, assertions, @BeforeEach, mocking with Mockito, TDD"),
    ("Java", "Maven & Gradle", "Beginner", "pom.xml, build.gradle, dependencies, plugins, lifecycle"),
    ("Java", "Spring Boot Basics", "Intermediate", "@RestController, @Autowired, application.properties, REST API"),
    ("Java", "Java Records", "Intermediate", "record keyword, compact constructors, immutability, pattern matching"),
    ("Java", "Sealed Classes", "Advanced", "sealed, permits, pattern matching, exhaustive switch"),
    ("Java", "Virtual Threads (Project Loom)", "Advanced", "lightweight threads, structured concurrency, throughput"),
    ("Java", "Pattern Matching", "Advanced", "instanceof pattern, switch pattern, record patterns, guards"),
    ("Java", "Reflection API", "Advanced", "Class object, getMethod, invoke, getDeclaredFields, dynamic proxy"),
    ("Java", "Java Modules (JPMS)", "Advanced", "module-info.java, requires, exports, services, modulepath"),
    ("Java", "Java Collections Algorithms", "Intermediate", "sort, binarySearch, shuffle, Collections utility class"),
    ("Java", "Regular Expressions in Java", "Intermediate", "Pattern, Matcher, groups, flags, common patterns"),
    ("Java", "Date & Time API", "Intermediate", "LocalDate, LocalTime, Duration, Period, DateTimeFormatter, ZonedDateTime"),

    # ── HTML/CSS (30 topics) ────────────────────────────────────────
    ("HTML/CSS", "HTML Document Structure", "Beginner", "DOCTYPE, html, head, body, meta tags, semantic structure"),
    ("HTML/CSS", "HTML Elements & Tags", "Beginner", "headings, paragraphs, links, images, lists, tables, forms"),
    ("HTML/CSS", "HTML Forms & Input Types", "Beginner", "text, email, password, radio, checkbox, select, validation"),
    ("HTML/CSS", "Semantic HTML", "Beginner", "header, nav, main, section, article, aside, footer, accessibility"),
    ("HTML/CSS", "CSS Selectors", "Beginner", "element, class, id, descendant, child, sibling, pseudo-classes"),
    ("HTML/CSS", "CSS Box Model", "Beginner", "margin, padding, border, content, box-sizing, width/height"),
    ("HTML/CSS", "CSS Flexbox", "Intermediate", "flex container, flex items, justify-content, align-items, flex-wrap"),
    ("HTML/CSS", "CSS Grid", "Intermediate", "grid-template, fr unit, gap, grid-area, auto-fit, minmax"),
    ("HTML/CSS", "CSS Positioning", "Intermediate", "static, relative, absolute, fixed, sticky, z-index, stacking"),
    ("HTML/CSS", "CSS Animations & Transitions", "Intermediate", "transition, @keyframes, animation properties, transforms"),
    ("HTML/CSS", "Responsive Design", "Intermediate", "media queries, viewport, mobile-first, breakpoints, fluid grids"),
    ("HTML/CSS", "CSS Variables (Custom Properties)", "Intermediate", "--var-name, var(), theming, cascading, fallbacks"),
    ("HTML/CSS", "CSS Pseudo-classes & Pseudo-elements", "Intermediate", ":hover, :focus, :nth-child, ::before, ::after, ::placeholder"),
    ("HTML/CSS", "Typography & Web Fonts", "Beginner", "font-family, font-size, line-height, Google Fonts, @font-face"),
    ("HTML/CSS", "Colors & Backgrounds", "Beginner", "hex, rgb, hsl, gradients, background-image, opacity, blend modes"),
    ("HTML/CSS", "HTML Tables", "Beginner", "table, tr, td, th, colspan, rowspan, styling, accessibility"),
    ("HTML/CSS", "HTML Media Elements", "Beginner", "audio, video, source, iframe, picture, srcset, lazy loading"),
    ("HTML/CSS", "CSS Specificity & Cascade", "Intermediate", "specificity calculation, !important, cascade order, inheritance"),
    ("HTML/CSS", "CSS Transforms", "Intermediate", "translate, rotate, scale, skew, transform-origin, 3D transforms"),
    ("HTML/CSS", "CSS Filters & Blend Modes", "Intermediate", "blur, brightness, contrast, grayscale, mix-blend-mode"),
    ("HTML/CSS", "Accessibility (a11y)", "Intermediate", "ARIA roles, alt text, keyboard navigation, screen readers, contrast"),
    ("HTML/CSS", "CSS Preprocessors (SASS)", "Intermediate", "variables, nesting, mixins, extends, partials, functions"),
    ("HTML/CSS", "Tailwind CSS", "Intermediate", "utility classes, responsive modifiers, customization, dark mode"),
    ("HTML/CSS", "BEM Naming Convention", "Beginner", "block, element, modifier, naming patterns, maintainability"),
    ("HTML/CSS", "CSS Container Queries", "Advanced", "container-type, @container, size queries, style queries"),
    ("HTML/CSS", "HTML Canvas", "Advanced", "2D drawing, paths, shapes, text, images, animation loop"),
    ("HTML/CSS", "SVG Basics", "Intermediate", "viewBox, path, circle, rect, fill, stroke, SVG animation"),
    ("HTML/CSS", "CSS Clamp & Modern Functions", "Intermediate", "clamp(), min(), max(), calc(), fluid typography"),
    ("HTML/CSS", "CSS Scroll-Driven Animations", "Advanced", "scroll-timeline, animation-timeline, view-timeline"),
    ("HTML/CSS", "Web Performance & Optimization", "Advanced", "Critical CSS, lazy loading, minification, CLS, LCP, FID"),

    # ── C/C++ (15 topics) ──────────────────────────────────────────
    ("C/C++", "Variables & Data Types in C", "Beginner", "int, float, double, char, sizeof, typedef, constants"),
    ("C/C++", "Pointers & Memory", "Intermediate", "pointer declaration, dereferencing, pointer arithmetic, NULL, void*"),
    ("C/C++", "Arrays & Strings in C", "Beginner", "array declaration, string functions, strlen, strcpy, strcmp"),
    ("C/C++", "Functions in C", "Beginner", "function prototype, pass-by-value, pass-by-reference, recursion"),
    ("C/C++", "Structures & Unions", "Intermediate", "struct, union, typedef, nested structs, bit fields"),
    ("C/C++", "Dynamic Memory Allocation", "Intermediate", "malloc, calloc, realloc, free, memory leaks, valgrind"),
    ("C/C++", "File Handling in C", "Intermediate", "fopen, fclose, fread, fwrite, fprintf, fscanf, binary files"),
    ("C/C++", "C++ Classes & Objects", "Intermediate", "class definition, constructors, destructors, access specifiers"),
    ("C/C++", "C++ Inheritance", "Intermediate", "single, multiple, virtual, abstract classes, diamond problem"),
    ("C/C++", "C++ STL Containers", "Intermediate", "vector, list, map, set, unordered_map, stack, queue, deque"),
    ("C/C++", "C++ Templates", "Advanced", "function templates, class templates, specialization, SFINAE"),
    ("C/C++", "C++ Smart Pointers", "Advanced", "unique_ptr, shared_ptr, weak_ptr, RAII, ownership semantics"),
    ("C/C++", "C++ Move Semantics", "Advanced", "rvalue references, std::move, move constructor, perfect forwarding"),
    ("C/C++", "C++ Lambda Expressions", "Intermediate", "capture list, mutable, generic lambdas, std::function"),
    ("C/C++", "C Preprocessor", "Intermediate", "#define, #include, #ifdef, macros, conditional compilation"),

    # ── SQL & Database (15 topics) ──────────────────────────────────
    ("SQL", "SQL Basics & SELECT", "Beginner", "SELECT, FROM, WHERE, ORDER BY, LIMIT, DISTINCT, aliases"),
    ("SQL", "Filtering with WHERE", "Beginner", "comparison operators, AND/OR/NOT, IN, BETWEEN, LIKE, IS NULL"),
    ("SQL", "Aggregate Functions", "Beginner", "COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING"),
    ("SQL", "JOINs", "Intermediate", "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN, self join, CROSS JOIN"),
    ("SQL", "Subqueries", "Intermediate", "scalar subquery, column subquery, EXISTS, IN, correlated subquery"),
    ("SQL", "INSERT, UPDATE, DELETE", "Beginner", "INSERT INTO, UPDATE SET, DELETE FROM, MERGE, UPSERT"),
    ("SQL", "Table Creation & Constraints", "Intermediate", "CREATE TABLE, PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, DEFAULT"),
    ("SQL", "Indexes & Performance", "Intermediate", "CREATE INDEX, B-tree, hash index, composite index, EXPLAIN"),
    ("SQL", "Views & CTEs", "Intermediate", "CREATE VIEW, WITH clause, recursive CTE, materialized views"),
    ("SQL", "Window Functions", "Advanced", "ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, OVER, PARTITION BY"),
    ("SQL", "Transactions & ACID", "Intermediate", "BEGIN, COMMIT, ROLLBACK, isolation levels, deadlocks"),
    ("SQL", "Normalization", "Intermediate", "1NF, 2NF, 3NF, BCNF, denormalization, trade-offs"),
    ("SQL", "Stored Procedures & Functions", "Advanced", "CREATE PROCEDURE, parameters, cursors, triggers, CREATE FUNCTION"),
    ("SQL", "NoSQL vs SQL", "Intermediate", "document stores, key-value, graph, column-family, CAP theorem"),
    ("SQL", "MongoDB Basics", "Intermediate", "documents, collections, find, insert, update, aggregation pipeline"),
]

assert len(TOPIC_DEFS) == 200, f"Expected 200 topics, got {len(TOPIC_DEFS)}"

# ── Build full topic documents ──────────────────────────────────────

def _make_explanation(style, icon, topic_name, difficulty):
    """Return a placeholder explanation dict for one style."""
    level_map = {"Beginner": "simple everyday", "Intermediate": "moderate", "Advanced": "in-depth technical"}
    style_prompts = {
        "simplified": f"A clear, {level_map.get(difficulty, 'moderate')} explanation of {topic_name}. Uses plain language, avoids jargon, and walks through concepts step-by-step with practical examples.",
        "logical": f"A systematic, technical breakdown of {topic_name}. Covers internal mechanics, time/space complexity, formal definitions, and how things work under the hood.",
        "visual": f"A visual, diagram-oriented explanation of {topic_name}. Uses step-by-step walkthroughs, ASCII diagrams, flowcharts, and shows execution flow visually.",
        "analogy": f"A real-world analogy-based explanation of {topic_name}. Compares programming concepts to everyday objects and activities to build intuition.",
    }
    titles = {"simplified": "Simplified", "logical": "Logical", "visual": "Visual", "analogy": "Analogy"}
    return {
        "style": style,
        "title": titles[style],
        "icon": icon,
        "content": style_prompts[style],
        "codeExample": f"# Code example for {topic_name} ({style} style)\n# AI will generate this dynamically based on user level"
    }


def _make_quiz(topic_name, language, difficulty, count=10):
    """Generate 10 placeholder quiz questions per topic."""
    questions = []
    diff_label = difficulty.lower()
    for i in range(1, count + 1):
        questions.append({
            "id": f"q-{language.lower().replace('/', '-').replace(' ', '')}-{topic_name.lower().replace(' ', '-')[:20]}-{i}",
            "question": f"{topic_name} Quiz Q{i} ({diff_label}): [AI-generated question about {topic_name} in {language}]",
            "options": [
                f"Option A for Q{i}",
                f"Option B for Q{i}",
                f"Option C for Q{i}",
                f"Option D for Q{i}",
            ],
            "correctAnswer": 0,
            "explanation": f"Explanation for Q{i}: This tests understanding of {topic_name} at {difficulty} level.",
            "type": "mcq",
        })
    return questions


def _make_flowchart(topic_name):
    """Simple flowchart data for each topic."""
    return json.dumps({
        "nodes": [
            {"id": "s", "type": "start", "label": f"Start: {topic_name}", "detail": "Begin learning this concept"},
            {"id": "p1", "type": "process", "label": "Learn Core Concepts", "detail": "Read the explanation and understand fundamentals"},
            {"id": "d1", "type": "decision", "label": "Understood?", "detail": "Do you understand the basics?", "yes": "Practice coding", "no": "Re-read with different style"},
            {"id": "p2", "type": "process", "label": "Practice Coding", "detail": "Write code examples and experiment"},
            {"id": "p3", "type": "process", "label": "Take Quiz", "detail": "Test your knowledge with 10 questions"},
            {"id": "e1", "type": "end", "label": "Topic Mastered!", "detail": "Move to the next topic"},
        ]
    })


def build_topic(idx, language, topic_name, difficulty, brief_seed):
    """Build a complete topic document."""
    tid = f"topic-{idx}"
    lang_slug = language.lower().replace("/", "-").replace(" ", "")
    
    subtopic_id = f"sub-{idx}-1"
    
    subtopics = [{
        "id": subtopic_id,
        "name": topic_name,
        "pdfUrl": "internal",
        "pdfTitle": f"{topic_name} Study Guide",
        "overview": (
            f"{topic_name} is a {'fundamental' if difficulty == 'Beginner' else 'key' if difficulty == 'Intermediate' else 'advanced'} "
            f"concept in {language} programming. Key areas include: {brief_seed}. "
            f"Understanding this topic is essential for building real-world applications."
        ),
        "explanations": [
            _make_explanation("simplified", "📝", topic_name, difficulty),
            _make_explanation("logical", "🧠", topic_name, difficulty),
            _make_explanation("visual", "🎨", topic_name, difficulty),
            _make_explanation("analogy", "🔗", topic_name, difficulty),
        ],
        "flowchart": _make_flowchart(topic_name),
        "quiz": _make_quiz(topic_name, language, difficulty, count=10),
        "recommendedVideos": [],
    }]

    return {
        "id": tid,
        "language": language,
        "topicName": topic_name,
        "difficulty": difficulty,
        "overview": (
            f"Master {topic_name} in {language}. This {difficulty.lower()}-level topic covers: {brief_seed}. "
            f"Complete the explanations and take the 10-question quiz to test your understanding."
        ),
        "subtopics": subtopics,
        "explanations": [
            _make_explanation("simplified", "📝", topic_name, difficulty),
            _make_explanation("logical", "🧠", topic_name, difficulty),
            _make_explanation("visual", "🎨", topic_name, difficulty),
            _make_explanation("analogy", "🔗", topic_name, difficulty),
        ],
        "quiz": _make_quiz(topic_name, language, difficulty, count=10),
        "recommendedVideos": [],
    }


def main():
    # Build all 200 topics
    topics = []
    for idx, (lang, name, diff, seed) in enumerate(TOPIC_DEFS, start=1):
        topics.append(build_topic(idx, lang, name, diff, seed))

    print(f"✅ Built {len(topics)} topic documents")

    # Connect to MongoDB and insert
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client["pixel_pirates"]
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

    # Drop existing topics and insert fresh 200
    db.topics.drop()
    db.topics.insert_many(topics)
    print(f"✅ Inserted {len(topics)} topics into MongoDB")

    # Create indexes
    db.topics.create_index("id", unique=True)
    db.topics.create_index("language")
    db.topics.create_index("difficulty")
    print("✅ Created indexes on topics collection")

    # Update any existing users to have all 200 topic IDs as pending
    all_topic_ids = [t["id"] for t in topics]
    result = db.users.update_many(
        {},
        {"$set": {"pendingTopics": all_topic_ids, "completedTopics": [], "inProgressTopics": []}}
    )
    print(f"✅ Updated {result.modified_count} users with new topic IDs")

    # Create progress, notes, feedback, mock_results collections with indexes
    for coll_name in ["user_progress", "user_notes", "user_feedback", "mock_results"]:
        if coll_name not in db.list_collection_names():
            db.create_collection(coll_name)
    
    db.user_progress.create_index([("user_id", 1), ("topic_id", 1)], unique=True)
    db.user_notes.create_index([("user_id", 1), ("topic_id", 1)])
    db.user_feedback.create_index([("user_id", 1), ("topic_id", 1)])
    db.mock_results.create_index([("user_id", 1)])
    print("✅ Created collections and indexes for progress, notes, feedback, mock_results")

    print(f"\n🎉 Done! {len(topics)} topics seeded with 10 quiz questions each.")
    print("   Run the backend and all topics will be loaded.")


if __name__ == "__main__":
    main()
