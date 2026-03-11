"""
Generate 200 programming topics across 20 languages using Gemini API.

Each topic gets:
 - 4 explanation styles (simplified, logical, visual, analogy) with code examples
 - 10 quiz questions (MCQ) with correct answers and explanations
 - Flowchart data
 - YouTube video recommendations via YouTube Data API
 - Full overview and PDF-quality content

Run:  python generate_all_200.py
"""

import json, os, sys, time, re, traceback
import pymongo, httpx
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "pixel_pirates")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not set. Add it to .env file.")
    sys.exit(1)

# ── 200 Topic Definitions (20 languages × 10 topics) ───────────────
TOPIC_DEFS = [
    # ── Python (10) ─────────────────────────────────────────────────
    ("Python", "History & Philosophy", "Beginner",
     "Python creation by Guido van Rossum, Zen of Python, PEP 8, design philosophy, interpreted language, dynamic typing, Python 2 vs 3"),
    ("Python", "Syntax & Basics", "Beginner",
     "variables, data types (int, float, str, bool), type conversion, input/output, comments, indentation, operators"),
    ("Python", "Control Structures", "Beginner",
     "if/elif/else, for loops, while loops, range(), break, continue, pass, nested conditions, match-case"),
    ("Python", "Functions & Recursion", "Intermediate",
     "def, return, parameters, *args, **kwargs, default values, lambda, recursion, base case, memoization, call stack"),
    ("Python", "Data Structures (lists, dicts, sets)", "Intermediate",
     "lists, tuples, dictionaries, sets, list comprehension, dict comprehension, slicing, methods, frozenset, deque"),
    ("Python", "OOP (classes, inheritance, dunder methods)", "Intermediate",
     "classes, __init__, self, inheritance, super(), polymorphism, encapsulation, __str__, __repr__, __len__, abstract classes"),
    ("Python", "Advanced Features (decorators, generators, async)", "Advanced",
     "decorators, @syntax, generators, yield, async/await, asyncio, context managers, closures, itertools"),
    ("Python", "Libraries (NumPy, Pandas, Flask, TensorFlow)", "Advanced",
     "NumPy arrays, Pandas DataFrames, Flask routes, TensorFlow basics, pip install, virtual environments, popular packages"),
    ("Python", "File Handling & DB (CSV, JSON, SQLite)", "Intermediate",
     "open(), read, write, with statement, csv module, json module, sqlite3, CRUD operations, parameterized queries"),
    ("Python", "Applications (AI/ML, automation, web dev)", "Advanced",
     "machine learning with scikit-learn, web scraping with BeautifulSoup, Django/Flask web apps, automation scripts, data science"),

    # ── JavaScript (10) ─────────────────────────────────────────────
    ("JavaScript", "History & ECMAScript", "Beginner",
     "creation by Brendan Eich, ECMAScript standards, ES6+, browser vs Node.js, V8 engine, TC39 process"),
    ("JavaScript", "Syntax & Basics (ES6+)", "Beginner",
     "let/const/var, data types, template literals, operators, type coercion, strict mode, console.log, comments"),
    ("JavaScript", "Control Structures", "Beginner",
     "if/else, switch, for, while, do-while, for...of, for...in, break, continue, ternary operator"),
    ("JavaScript", "Functions (closures, arrow functions)", "Intermediate",
     "function declaration, expression, arrow functions, closures, IIFE, higher-order functions, callback pattern, this binding"),
    ("JavaScript", "Data Structures (arrays, objects, maps)", "Intermediate",
     "arrays, objects, Map, Set, WeakMap, WeakSet, destructuring, spread/rest, JSON, array methods (map, filter, reduce)"),
    ("JavaScript", "OOP (prototypes, ES6 classes)", "Intermediate",
     "prototypes, prototype chain, ES6 classes, constructor, extends, super, static methods, getters/setters, instanceof"),
    ("JavaScript", "Advanced Features (async/await, promises, event loop)", "Advanced",
     "promises, async/await, event loop, microtasks, macrotasks, Promise.all, Promise.race, callbacks, error handling"),
    ("JavaScript", "Libraries (React, Node.js, Express)", "Advanced",
     "React components, JSX, hooks, Node.js modules, Express routing, middleware, npm, REST API building"),
    ("JavaScript", "File Handling & DB (JSON, APIs, MongoDB)", "Intermediate",
     "fetch API, JSON parsing, localStorage, REST APIs, MongoDB with Mongoose, CRUD operations, async database calls"),
    ("JavaScript", "Applications (web apps, mobile apps, servers)", "Advanced",
     "SPA frameworks, React Native mobile apps, Node.js servers, Electron desktop apps, serverless functions, full-stack development"),

    # ── C (10) ──────────────────────────────────────────────────────
    ("C", "History & Basics", "Beginner",
     "Dennis Ritchie, Bell Labs, ANSI C, C99/C11/C17, compiled language, gcc, structure of a C program, main()"),
    ("C", "Syntax & Data Types", "Beginner",
     "int, float, double, char, sizeof, constants, type casting, printf/scanf, format specifiers, operators"),
    ("C", "Control Structures", "Beginner",
     "if/else, switch, for, while, do-while, break, continue, goto, nested loops, conditional expressions"),
    ("C", "Functions & Pointers", "Intermediate",
     "function declaration, definition, prototypes, pass-by-value, pointers, pointer arithmetic, NULL, function pointers"),
    ("C", "Arrays & Strings", "Intermediate",
     "array declaration, multidimensional arrays, string functions (strlen, strcpy, strcmp, strcat), char arrays, string.h"),
    ("C", "Structures & Unions", "Intermediate",
     "struct, union, typedef, nested structures, bit fields, structure pointers, sizeof with structs, enum"),
    ("C", "Memory Management (malloc, free)", "Advanced",
     "malloc, calloc, realloc, free, memory leaks, dangling pointers, stack vs heap, valgrind, buffer overflow"),
    ("C", "File Handling", "Intermediate",
     "fopen, fclose, fread, fwrite, fprintf, fscanf, fgets, binary files, file modes, EOF, error handling"),
    ("C", "Standard Libraries", "Intermediate",
     "stdio.h, stdlib.h, string.h, math.h, ctype.h, time.h, assert.h, limits.h, standard library functions"),
    ("C", "Applications (system programming, embedded systems)", "Advanced",
     "operating systems, device drivers, embedded systems, microcontrollers, real-time systems, Linux kernel, IoT"),

    # ── C++ (10) ────────────────────────────────────────────────────
    ("C++", "History & Basics", "Beginner",
     "Bjarne Stroustrup, C with Classes, C++11/14/17/20, compiled language, g++, namespaces, iostream"),
    ("C++", "Syntax & Data Types", "Beginner",
     "auto, int, float, double, string, bool, references, const, constexpr, type inference, cin/cout"),
    ("C++", "Control Structures", "Beginner",
     "if/else, switch, for, while, do-while, range-based for, break, continue, structured bindings"),
    ("C++", "Functions & Templates", "Intermediate",
     "function overloading, default parameters, inline, templates, function templates, class templates, specialization"),
    ("C++", "STL Data Structures", "Intermediate",
     "vector, list, map, set, unordered_map, stack, queue, deque, priority_queue, pair, tuple, iterators"),
    ("C++", "OOP (classes, inheritance, polymorphism)", "Intermediate",
     "classes, constructors, destructors, inheritance, virtual functions, pure virtual, abstract classes, access specifiers"),
    ("C++", "Advanced Features (operator overloading, smart pointers)", "Advanced",
     "operator overloading, smart pointers (unique_ptr, shared_ptr, weak_ptr), RAII, move semantics, rvalue references"),
    ("C++", "Libraries (STL, Boost, OpenCV)", "Advanced",
     "STL algorithms, Boost libraries, OpenCV image processing, Qt GUI, Eigen linear algebra, third-party libraries"),
    ("C++", "File Handling & DB", "Intermediate",
     "fstream, ifstream, ofstream, binary file I/O, serialization, SQLite with C++, database connectivity"),
    ("C++", "Applications (games, OS, compilers)", "Advanced",
     "game development with Unreal Engine, operating system components, compiler design, high-performance computing, robotics"),

    # ── PHP (10) ────────────────────────────────────────────────────
    ("PHP", "History & Basics", "Beginner",
     "Rasmus Lerdorf, PHP evolution, server-side scripting, LAMP stack, PHP 8.x features, interpreted language"),
    ("PHP", "Syntax & Variables", "Beginner",
     "$variables, data types, echo/print, string interpolation, type juggling, constants, operators, comments"),
    ("PHP", "Control Structures", "Beginner",
     "if/elseif/else, switch, match, for, while, do-while, foreach, break, continue, alternative syntax"),
    ("PHP", "Functions", "Intermediate",
     "function declaration, parameters, return types, type hints, anonymous functions, closures, arrow functions, variadic"),
    ("PHP", "Arrays & Strings", "Intermediate",
     "indexed arrays, associative arrays, multidimensional arrays, array functions, string functions, regex, preg_match"),
    ("PHP", "OOP in PHP", "Intermediate",
     "classes, __construct, properties, methods, inheritance, interfaces, traits, abstract classes, namespaces, autoloading"),
    ("PHP", "Advanced Features (sessions, cookies)", "Advanced",
     "sessions, cookies, authentication, security (XSS, CSRF, SQL injection prevention), password hashing, file uploads"),
    ("PHP", "Frameworks (Laravel, Symfony)", "Advanced",
     "Laravel MVC, Eloquent ORM, Blade templates, Artisan CLI, Symfony components, routing, middleware, Composer"),
    ("PHP", "Database Integration (MySQL)", "Intermediate",
     "PDO, mysqli, prepared statements, CRUD operations, transactions, migrations, query builders, database design"),
    ("PHP", "Applications (websites, CMS)", "Advanced",
     "WordPress development, custom CMS, e-commerce with WooCommerce, RESTful APIs, microservices, SaaS applications"),

    # ── HTML/CSS (10) ───────────────────────────────────────────────
    ("HTML/CSS", "History & Basics", "Beginner",
     "Tim Berners-Lee, HTML evolution, CSS history, W3C standards, browser rendering, DOCTYPE, semantic web"),
    ("HTML/CSS", "HTML Elements & Attributes", "Beginner",
     "headings, paragraphs, links, images, lists, tables, divs, spans, attributes (id, class, src, href, alt)"),
    ("HTML/CSS", "Forms & Input", "Beginner",
     "form element, input types (text, email, password, radio, checkbox), select, textarea, validation, labels"),
    ("HTML/CSS", "Semantic HTML", "Intermediate",
     "header, nav, main, section, article, aside, footer, figure, figcaption, accessibility benefits, SEO impact"),
    ("HTML/CSS", "CSS Selectors & Properties", "Beginner",
     "element, class, id selectors, descendant, child, sibling, pseudo-classes (:hover, :focus), specificity, cascade"),
    ("HTML/CSS", "Layouts (Flexbox, Grid)", "Intermediate",
     "Flexbox (justify-content, align-items, flex-wrap), CSS Grid (grid-template, fr unit, gap), responsive patterns"),
    ("HTML/CSS", "Responsive Design", "Intermediate",
     "media queries, viewport meta tag, mobile-first approach, breakpoints, fluid grids, responsive images, srcset"),
    ("HTML/CSS", "Advanced CSS (animations, transitions)", "Advanced",
     "transitions, @keyframes, animation properties, transforms (translate, rotate, scale), cubic-bezier, performance"),
    ("HTML/CSS", "Frameworks (Bootstrap, Tailwind)", "Intermediate",
     "Bootstrap grid system, components, Tailwind utility classes, customization, responsive modifiers, dark mode"),
    ("HTML/CSS", "Applications (web design, UI/UX)", "Advanced",
     "design principles, color theory, typography, accessibility (WCAG), performance optimization, modern CSS features"),

    # ── SQL (10) ────────────────────────────────────────────────────
    ("SQL", "History & Basics", "Beginner",
     "Edgar Codd, relational model, SQL standardization, RDBMS (MySQL, PostgreSQL, SQLite), SQL vs NoSQL"),
    ("SQL", "Data Types", "Beginner",
     "INT, VARCHAR, TEXT, DATE, DATETIME, FLOAT, DECIMAL, BOOLEAN, BLOB, NULL, type casting, constraints"),
    ("SQL", "DDL (CREATE, ALTER, DROP)", "Intermediate",
     "CREATE TABLE, ALTER TABLE (ADD, MODIFY, DROP COLUMN), DROP TABLE, TRUNCATE, schema design, naming conventions"),
    ("SQL", "DML (SELECT, INSERT, UPDATE, DELETE)", "Beginner",
     "SELECT with WHERE, ORDER BY, LIMIT, INSERT INTO, UPDATE SET, DELETE FROM, DISTINCT, aliases, wildcards"),
    ("SQL", "Joins & Subqueries", "Intermediate",
     "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN, CROSS JOIN, self join, subqueries, correlated subqueries, EXISTS"),
    ("SQL", "Constraints & Keys", "Intermediate",
     "PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK, DEFAULT, AUTO_INCREMENT, composite keys, referential integrity"),
    ("SQL", "Views & Indexes", "Intermediate",
     "CREATE VIEW, updatable views, CREATE INDEX, B-tree indexes, composite indexes, EXPLAIN, query optimization"),
    ("SQL", "Stored Procedures & Triggers", "Advanced",
     "CREATE PROCEDURE, parameters (IN, OUT, INOUT), cursors, CREATE TRIGGER, BEFORE/AFTER triggers, events"),
    ("SQL", "Transactions", "Intermediate",
     "BEGIN, COMMIT, ROLLBACK, SAVEPOINT, ACID properties, isolation levels, deadlocks, concurrent access"),
    ("SQL", "Applications (databases, analytics)", "Advanced",
     "data warehousing, ETL processes, business intelligence, reporting, database administration, performance tuning"),

    # ── TypeScript (10) ─────────────────────────────────────────────
    ("TypeScript", "History & Basics", "Beginner",
     "Microsoft creation, Anders Hejlsberg, TypeScript vs JavaScript, compilation, tsconfig.json, strict mode"),
    ("TypeScript", "Syntax & Types", "Beginner",
     "type annotations, primitive types, union types, literal types, type aliases, type assertions, any vs unknown"),
    ("TypeScript", "Control Structures", "Beginner",
     "if/else, switch with type narrowing, for loops, while, for...of, type guards, discriminated unions"),
    ("TypeScript", "Functions", "Intermediate",
     "typed parameters, return types, optional parameters, overloads, generic functions, rest parameters, void"),
    ("TypeScript", "Interfaces & Generics", "Intermediate",
     "interface declaration, optional properties, readonly, extending interfaces, generics, generic constraints, utility types"),
    ("TypeScript", "OOP (classes, inheritance)", "Intermediate",
     "classes, access modifiers (public, private, protected), abstract classes, implements, static members, decorators"),
    ("TypeScript", "Advanced Features (decorators, namespaces)", "Advanced",
     "decorators, metadata reflection, namespaces, declaration merging, conditional types, mapped types, template literal types"),
    ("TypeScript", "Frameworks (Angular, NestJS)", "Advanced",
     "Angular components, dependency injection, NestJS modules, controllers, services, decorators in frameworks"),
    ("TypeScript", "Compilation & Tooling", "Intermediate",
     "tsc compiler, tsconfig options, source maps, declaration files (.d.ts), ESLint, Prettier, build tools"),
    ("TypeScript", "Applications (large-scale web apps)", "Advanced",
     "monorepo management, type-safe APIs, full-stack TypeScript, microservices, library authoring, migration strategies"),

    # ── Go (Golang) (10) ───────────────────────────────────────────
    ("Go", "History & Basics", "Beginner",
     "Google creation, Rob Pike, Ken Thompson, Go philosophy, simplicity, fast compilation, static typing, go run"),
    ("Go", "Syntax & Data Types", "Beginner",
     "variables (:=, var), basic types (int, float64, string, bool), constants, zero values, type conversion, fmt package"),
    ("Go", "Control Structures", "Beginner",
     "if/else (no parentheses), switch (no break needed), for (only loop), range, break, continue, defer"),
    ("Go", "Functions", "Intermediate",
     "multiple return values, named returns, variadic functions, closures, methods, function types, error handling patterns"),
    ("Go", "Data Structures (slices, maps)", "Intermediate",
     "arrays, slices (append, len, cap), maps, structs, make(), new(), nil slices, slice of structs"),
    ("Go", "Concurrency (goroutines, channels)", "Advanced",
     "goroutines, channels, buffered channels, select, sync package (Mutex, WaitGroup), race conditions, context"),
    ("Go", "OOP-like features (structs, interfaces)", "Intermediate",
     "structs as classes, methods on structs, interfaces, implicit implementation, embedding, composition over inheritance"),
    ("Go", "Libraries (net/http, fmt)", "Intermediate",
     "net/http server, http.HandleFunc, JSON encoding/decoding, fmt formatting, os package, io package, testing"),
    ("Go", "File Handling & DB", "Intermediate",
     "os.Open, bufio.Scanner, ioutil (deprecated), os.ReadFile, database/sql, PostgreSQL/MySQL drivers, GORM"),
    ("Go", "Applications (cloud, microservices)", "Advanced",
     "Docker, Kubernetes, microservices, gRPC, REST APIs, cloud-native development, CLI tools, DevOps tooling"),

    # ── Swift (10) ──────────────────────────────────────────────────
    ("Swift", "History & Basics", "Beginner",
     "Apple creation, Chris Lattner, Swift vs Objective-C, Xcode, playgrounds, type safety, optionals intro"),
    ("Swift", "Syntax & Data Types", "Beginner",
     "let/var, Int, Double, String, Bool, type inference, string interpolation, tuples, typealias, print()"),
    ("Swift", "Control Structures", "Beginner",
     "if/else, guard, switch (pattern matching), for-in, while, repeat-while, where clause, fallthrough"),
    ("Swift", "Functions", "Intermediate",
     "func declaration, parameter labels, default values, inout parameters, variadic, closures, trailing closure syntax"),
    ("Swift", "Collections (arrays, sets, dictionaries)", "Intermediate",
     "Array, Set, Dictionary, subscript access, iteration, filter/map/reduce, mutating vs non-mutating, collection protocols"),
    ("Swift", "OOP (classes, structs, protocols)", "Intermediate",
     "classes vs structs (reference vs value), protocols, extensions, protocol-oriented programming, initializers, deinit"),
    ("Swift", "Advanced Features (optionals, closures)", "Advanced",
     "Optional chaining, nil coalescing, force unwrapping, if let, guard let, closures capturing, escaping closures, Result type"),
    ("Swift", "Frameworks (UIKit, SwiftUI)", "Advanced",
     "UIKit views, UIViewController, SwiftUI declarative syntax, @State, @Binding, @ObservedObject, Combine framework"),
    ("Swift", "File Handling & DB (CoreData)", "Intermediate",
     "FileManager, reading/writing files, UserDefaults, CoreData model, NSManagedObject, fetch requests, SQLite"),
    ("Swift", "Applications (iOS/macOS apps)", "Advanced",
     "iOS app lifecycle, App Store deployment, UI design patterns (MVC, MVVM), networking with URLSession, push notifications"),

    # ── Ruby (10) ───────────────────────────────────────────────────
    ("Ruby", "History & Basics", "Beginner",
     "Yukihiro Matsumoto (Matz), happiness philosophy, interpreted language, dynamic typing, IRB, everything is an object"),
    ("Ruby", "Syntax & Data Types", "Beginner",
     "variables, integers, floats, strings, symbols, nil, puts/print, string interpolation, operators, comments"),
    ("Ruby", "Control Structures", "Beginner",
     "if/elsif/else, unless, case/when, while, until, for, each, times, loop, break, next, redo"),
    ("Ruby", "Functions & Blocks", "Intermediate",
     "def methods, return, default parameters, blocks with do/end and {}, yield, procs, lambdas, closures"),
    ("Ruby", "Collections (arrays, hashes)", "Intermediate",
     "arrays, hashes (symbol keys), ranges, each, map, select, reject, inject/reduce, sort, flatten, group_by"),
    ("Ruby", "OOP (classes, modules, mixins)", "Intermediate",
     "classes, initialize, attr_accessor, inheritance, modules, include/extend, mixins, super, method_missing"),
    ("Ruby", "Advanced Features (metaprogramming)", "Advanced",
     "define_method, method_missing, open classes, monkey patching, DSLs, eval, send, respond_to?, reflection"),
    ("Ruby", "Frameworks (Rails, Sinatra)", "Advanced",
     "Rails MVC, ActiveRecord, migrations, routes, controllers, views (ERB), Sinatra DSL, REST API, gems"),
    ("Ruby", "File Handling & DB (ActiveRecord)", "Intermediate",
     "File.open, read/write, CSV, JSON parsing, ActiveRecord ORM, migrations, associations, validations, queries"),
    ("Ruby", "Applications (web apps, automation)", "Advanced",
     "web applications with Rails, DevOps with Chef/Puppet, testing with RSpec, CI/CD, API development, scripting"),

    # ── R (10) ──────────────────────────────────────────────────────
    ("R", "History & Basics", "Beginner",
     "Ross Ihaka, Robert Gentleman, statistical computing, RStudio IDE, CRAN, R vs Python, interactive console"),
    ("R", "Syntax & Data Types", "Beginner",
     "assignment (<-), numeric, character, logical, integer, factor, NA/NULL, print(), cat(), typeof(), class()"),
    ("R", "Control Structures", "Beginner",
     "if/else, ifelse() vectorized, for, while, repeat, break, next, switch, tryCatch error handling"),
    ("R", "Functions", "Intermediate",
     "function() definition, arguments, default values, ..., return(), anonymous functions, apply family, scope"),
    ("R", "Data Structures (vectors, lists, data frames)", "Intermediate",
     "vectors, matrices, lists, data frames, tibbles, factors, indexing, subsetting, names(), str(), summary()"),
    ("R", "OOP (S3, S4, R6 classes)", "Advanced",
     "S3 classes (informal), S4 classes (formal), R6 classes (reference), methods, dispatch, setClass, setMethod"),
    ("R", "Advanced Features (apply family, tidyverse)", "Advanced",
     "sapply, lapply, mapply, tapply, dplyr verbs (filter, mutate, select, arrange, summarize), pipe operator %>%"),
    ("R", "Libraries (ggplot2, dplyr)", "Intermediate",
     "ggplot2 grammar of graphics, geom layers, aesthetics, dplyr data manipulation, tidyr pivoting, readr, stringr"),
    ("R", "File Handling & DB (CSV, SQL)", "Intermediate",
     "read.csv, write.csv, readRDS, readxl, jsonlite, DBI package, RSQLite, database connections, SQL queries from R"),
    ("R", "Applications (statistics, ML, visualization)", "Advanced",
     "statistical testing, linear/logistic regression, caret/tidymodels, random forests, data visualization, Shiny web apps"),

    # ── C# (10) ─────────────────────────────────────────────────────
    ("C#", "History & Basics", "Beginner",
     "Microsoft creation, Anders Hejlsberg, .NET platform, C# evolution, Visual Studio, managed code, CLR"),
    ("C#", "Syntax & Data Types", "Beginner",
     "int, float, double, string, bool, char, var, nullable types, const, readonly, Console.WriteLine, operators"),
    ("C#", "Control Structures", "Beginner",
     "if/else, switch (pattern matching), for, foreach, while, do-while, break, continue, goto, ternary"),
    ("C#", "Functions", "Intermediate",
     "methods, parameters (ref, out, in), return types, overloading, optional parameters, expression-bodied members, local functions"),
    ("C#", "Collections (arrays, lists, dictionaries)", "Intermediate",
     "arrays, List<T>, Dictionary<K,V>, HashSet<T>, Queue<T>, Stack<T>, LINQ, IEnumerable, foreach patterns"),
    ("C#", "OOP (classes, inheritance, interfaces)", "Intermediate",
     "classes, constructors, properties, inheritance, virtual/override, abstract, interfaces, sealed, partial classes"),
    ("C#", "Advanced Features (LINQ, async/await)", "Advanced",
     "LINQ queries, lambda expressions, async/await, Task, delegates, events, extension methods, nullable reference types"),
    ("C#", "Frameworks (.NET, ASP.NET)", "Advanced",
     "ASP.NET Core, MVC pattern, Razor Pages, Web API, dependency injection, middleware, Entity Framework Core"),
    ("C#", "File Handling & DB (Entity Framework)", "Intermediate",
     "File class, StreamReader/Writer, System.IO, Entity Framework Core, DbContext, migrations, LINQ to Entities"),
    ("C#", "Applications (desktop, web, games with Unity)", "Advanced",
     "WPF/WinForms desktop apps, ASP.NET web apps, Unity game development, Xamarin/MAUI mobile, Azure cloud services"),

    # ── Rust (10) ───────────────────────────────────────────────────
    ("Rust", "History & Basics", "Beginner",
     "Mozilla creation, Graydon Hoare, memory safety without GC, Cargo, rustc, ownership intro, zero-cost abstractions"),
    ("Rust", "Syntax & Ownership Model", "Intermediate",
     "let/mut, ownership rules, borrowing (&, &mut), move semantics, Copy trait, clone, lifetime basics, String vs &str"),
    ("Rust", "Control Structures", "Beginner",
     "if/else (expression), loop, while, for, match (pattern matching), if let, while let, break with values"),
    ("Rust", "Functions", "Intermediate",
     "fn declaration, parameters, return types, expressions vs statements, closures (Fn, FnMut, FnOnce), impl blocks"),
    ("Rust", "Data Structures (vectors, hashmaps)", "Intermediate",
     "Vec<T>, HashMap<K,V>, HashSet, String, arrays, slices, tuples, Option<T>, Result<T,E>, enum as ADT"),
    ("Rust", "OOP-like features (traits, structs)", "Intermediate",
     "structs, impl blocks, traits, trait objects (dyn), generics with trait bounds, derive macros, Display, Debug"),
    ("Rust", "Advanced Features (lifetimes, macros)", "Advanced",
     "lifetime annotations, 'static, lifetime elision, declarative macros (macro_rules!), procedural macros, unsafe Rust"),
    ("Rust", "Libraries (Cargo ecosystem)", "Advanced",
     "Cargo.toml, crates.io, serde (serialization), tokio (async runtime), actix-web, reqwest, popular crates"),
    ("Rust", "File Handling & DB", "Intermediate",
     "std::fs, File::open, BufReader, serde_json, diesel ORM, sqlx, database connectivity, error handling with Result"),
    ("Rust", "Applications (systems programming, web assembly)", "Advanced",
     "systems programming, WebAssembly with wasm-pack, CLI tools with clap, embedded (no_std), network programming"),

    # ── Perl (10) ───────────────────────────────────────────────────
    ("Perl", "History & Basics", "Beginner",
     "Larry Wall, 'Swiss Army Chainsaw', Perl 5, interpreted language, CPAN, practical extraction, shebang line"),
    ("Perl", "Syntax & Variables", "Beginner",
     "$scalar, @array, %hash, my/local/our, sigils, context (scalar vs list), print, say, chomp, operators"),
    ("Perl", "Control Structures", "Beginner",
     "if/elsif/else, unless, while, until, for, foreach, next, last, redo, given/when, statement modifiers"),
    ("Perl", "Functions", "Intermediate",
     "sub declaration, @_ arguments, return, references, anonymous subs, closures, wantarray, prototypes"),
    ("Perl", "Arrays & Hashes", "Intermediate",
     "array operations (push, pop, shift, unshift, splice), hash operations, slices, sort, map, grep, reverse"),
    ("Perl", "Regular Expressions", "Intermediate",
     "pattern matching (=~), substitution (s///), modifiers (g, i, m, x), capture groups, lookahead, lookbehind, qr//"),
    ("Perl", "Advanced Features (modules, CPAN)", "Advanced",
     "use/require, package, Exporter, CPAN ecosystem, Moose OOP, Try::Tiny, Module::Build, distribution creation"),
    ("Perl", "File Handling", "Intermediate",
     "open/close, diamond operator <>, file tests (-e, -f, -d), directory handling, glob, binmode, encoding"),
    ("Perl", "DB Integration (DBI)", "Intermediate",
     "DBI module, database-independent interface, prepare/execute, placeholders, DBD drivers, transactions, fetchrow"),
    ("Perl", "Applications (text processing, web scripts)", "Advanced",
     "text processing, log analysis, CGI scripting, system administration, bioinformatics, one-liners, Catalyst web framework"),

    # ── MATLAB (10) ─────────────────────────────────────────────────
    ("MATLAB", "History & Basics", "Beginner",
     "Cleve Moler, MathWorks, matrix laboratory, interpreted environment, workspace, command window, scripts vs functions"),
    ("MATLAB", "Syntax & Data Types", "Beginner",
     "variables, double, char, logical, cell arrays, structures, matrices, semicolon suppression, disp(), fprintf()"),
    ("MATLAB", "Control Structures", "Beginner",
     "if/elseif/else, switch/case, for, while, break, continue, try/catch, return, nested loops"),
    ("MATLAB", "Functions & Scripts", "Intermediate",
     "function files, multiple outputs, nargin/nargout, anonymous functions, nested functions, function handles"),
    ("MATLAB", "Arrays & Matrices", "Intermediate",
     "matrix creation, indexing, slicing, matrix operations, element-wise operations (.*, ./, .^), reshape, cat, size"),
    ("MATLAB", "Visualization (plots, graphs)", "Intermediate",
     "plot(), bar(), scatter(), histogram(), subplot(), title/xlabel/ylabel, legend, figure properties, 3D plots"),
    ("MATLAB", "Advanced Features (toolboxes, Simulink)", "Advanced",
     "Signal Processing Toolbox, Image Processing Toolbox, Simulink block diagrams, Stateflow, code generation"),
    ("MATLAB", "File Handling", "Intermediate",
     "load/save, xlsread/xlswrite, csvread, fopen/fclose, textscan, MAT files, importing data, export formats"),
    ("MATLAB", "DB Integration", "Intermediate",
     "Database Toolbox, database(), fetch(), exec(), ODBC connections, SQL queries from MATLAB, data import"),
    ("MATLAB", "Applications (engineering, simulations)", "Advanced",
     "signal processing, control systems, image processing, numerical methods, finite element analysis, robotics"),

    # ── Dart (10) ───────────────────────────────────────────────────
    ("Dart", "History & Basics", "Beginner",
     "Google creation, Lars Bak, Kasper Lund, Dart SDK, dart run, AOT and JIT compilation, sound null safety"),
    ("Dart", "Syntax & Data Types", "Beginner",
     "var, int, double, String, bool, dynamic, final/const, type inference, null safety (?), print(), string interpolation"),
    ("Dart", "Control Structures", "Beginner",
     "if/else, switch/case, for, for-in, while, do-while, break, continue, assert, pattern matching (Dart 3)"),
    ("Dart", "Functions", "Intermediate",
     "named parameters, optional positional, default values, arrow functions (=>), anonymous, closures, typedef"),
    ("Dart", "Collections (lists, maps)", "Intermediate",
     "List, Set, Map, spread operator (...), collection if/for, Iterable, where, map, fold, toList()"),
    ("Dart", "OOP (classes, inheritance)", "Intermediate",
     "classes, constructors (named, factory), inheritance, abstract, mixins, interfaces (implicit), extension methods"),
    ("Dart", "Advanced Features (async, isolates)", "Advanced",
     "Future, async/await, Stream, StreamController, Isolate (parallel execution), compute(), generators (sync*/async*)"),
    ("Dart", "Frameworks (Flutter)", "Advanced",
     "Flutter widgets, StatelessWidget, StatefulWidget, MaterialApp, Scaffold, navigation, state management (Provider, Riverpod)"),
    ("Dart", "File Handling & DB", "Intermediate",
     "dart:io File, reading/writing, path package, sqflite (SQLite for Flutter), Hive, shared_preferences, Firebase"),
    ("Dart", "Applications (mobile/web apps)", "Advanced",
     "Flutter mobile apps, Flutter web, Flutter desktop, cross-platform development, pub.dev packages, deployment"),

    # ── Bash (10) ───────────────────────────────────────────────────
    ("Bash", "History & Basics", "Beginner",
     "Brian Fox, GNU project, Bourne Again Shell, terminal, shell vs terminal, shebang (#!/bin/bash), chmod, running scripts"),
    ("Bash", "Syntax & Variables", "Beginner",
     "variable assignment (no spaces), $VAR, ${VAR}, quoting ('single' vs \"double\"), read, echo, export, env"),
    ("Bash", "Control Structures (if, loops)", "Beginner",
     "if/then/elif/else/fi, test/[ ], [[ ]], for/do/done, while, until, case/esac, break, continue"),
    ("Bash", "Functions & Scripts", "Intermediate",
     "function declaration, arguments ($1, $2, $@, $#), return, local variables, source, script organization"),
    ("Bash", "File Handling", "Intermediate",
     "cat, head, tail, less, wc, touch, mkdir, rm, cp, mv, find, file permissions, chmod, chown"),
    ("Bash", "Process Management", "Intermediate",
     "ps, top, kill, signals, background (&), fg, bg, jobs, nohup, wait, exit codes ($?), trap"),
    ("Bash", "Text Processing (grep, awk, sed)", "Intermediate",
     "grep (regex search), sed (stream editor), awk (pattern scanning), cut, sort, uniq, tr, xargs"),
    ("Bash", "Advanced Features (pipes, redirection)", "Advanced",
     "pipes (|), stdin/stdout/stderr, redirection (>, >>, 2>, &>), here documents, process substitution, tee"),
    ("Bash", "System Administration Tasks", "Advanced",
     "cron jobs, systemd, log management, disk usage (df, du), network tools (curl, wget, ssh), user management"),
    ("Bash", "Applications (automation, DevOps)", "Advanced",
     "CI/CD pipelines, Docker scripts, deployment automation, monitoring scripts, backup scripts, infrastructure as code"),

    # ── Java (10) ───────────────────────────────────────────────────
    ("Java", "History & Basics", "Beginner",
     "James Gosling, Sun Microsystems, JVM, JRE, JDK, Write Once Run Anywhere, Java editions (SE, EE, ME), bytecode"),
    ("Java", "Syntax & Data Types", "Beginner",
     "primitive types (int, double, char, boolean), String, type casting, operators, System.out.println, Scanner, comments"),
    ("Java", "Control Structures", "Beginner",
     "if/else, switch (enhanced in Java 14+), for, enhanced for, while, do-while, break, continue, labels"),
    ("Java", "Functions & Methods", "Intermediate",
     "method declaration, parameters, return types, overloading, static methods, varargs, pass-by-value, recursion"),
    ("Java", "Collections (arrays, ArrayList, HashMap)", "Intermediate",
     "arrays, ArrayList, LinkedList, HashMap, TreeMap, HashSet, Collections utility class, Iterator, for-each, Comparable"),
    ("Java", "OOP (classes, inheritance, interfaces)", "Intermediate",
     "classes, constructors, encapsulation, inheritance, polymorphism, abstract classes, interfaces, final, Object class"),
    ("Java", "Advanced Features (generics, multithreading)", "Advanced",
     "generics, bounded types, wildcards, threads, Runnable, synchronized, volatile, ExecutorService, CompletableFuture"),
    ("Java", "Frameworks (Spring, Hibernate)", "Advanced",
     "Spring Boot, @RestController, dependency injection, Spring Data JPA, Hibernate ORM, annotations, REST APIs"),
    ("Java", "File Handling & DB (JDBC)", "Intermediate",
     "java.io, BufferedReader, FileWriter, NIO (Path, Files), JDBC (Connection, PreparedStatement, ResultSet), transactions"),
    ("Java", "Applications (enterprise apps, Android)", "Advanced",
     "enterprise applications, Android development, microservices, cloud deployment, Jakarta EE, build tools (Maven, Gradle)"),

    # ── Kotlin (10) ─────────────────────────────────────────────────
    ("Kotlin", "History & Basics", "Beginner",
     "JetBrains creation, Andrey Breslav, Google endorsement for Android, JVM interop, Kotlin/JS, Kotlin/Native"),
    ("Kotlin", "Syntax & Data Types", "Beginner",
     "val/var, type inference, Int, Double, String, Boolean, nullable types (?), string templates, println, when"),
    ("Kotlin", "Control Structures", "Beginner",
     "if as expression, when (pattern matching), for, while, do-while, ranges (..), break, continue, labels"),
    ("Kotlin", "Functions & Lambdas", "Intermediate",
     "fun declaration, default arguments, named parameters, extension functions, lambdas, higher-order functions, inline, it"),
    ("Kotlin", "Collections (lists, sets, maps)", "Intermediate",
     "listOf, mutableListOf, setOf, mapOf, filter, map, flatMap, groupBy, fold, sortedBy, sequences, destructuring"),
    ("Kotlin", "OOP (classes, inheritance, interfaces)", "Intermediate",
     "classes, data classes, sealed classes, object declaration, companion object, inheritance, interfaces, delegation"),
    ("Kotlin", "Advanced Features (coroutines, extensions)", "Advanced",
     "coroutines (launch, async), suspend functions, Flow, Dispatchers, scope functions (let, apply, run, also, with)"),
    ("Kotlin", "Frameworks (Ktor, Android SDK)", "Advanced",
     "Ktor server framework, Android Jetpack, Compose UI, ViewModel, LiveData, Room database, Retrofit"),
    ("Kotlin", "File Handling & DB", "Intermediate",
     "java.io interop, File.readText(), bufferedReader, kotlinx.serialization, Exposed ORM, Room (Android), SQLDelight"),
    ("Kotlin", "Applications (Android, backend services)", "Advanced",
     "Android app development, Kotlin Multiplatform, server-side with Ktor/Spring, Gradle build scripts, testing with JUnit"),
]

assert len(TOPIC_DEFS) == 200, f"Expected 200 topics, got {len(TOPIC_DEFS)}"

# ── Gemini API helper ───────────────────────────────────────────────

def call_gemini(prompt: str, max_tokens: int = 8000, retries: int = 5) -> str:
    """Call Gemini API and return text response."""
    url = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent"
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": max_tokens,
        },
    }
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=180.0) as client:
                res = client.post(url, params=params, json=payload)
                if res.status_code == 429:
                    wait = 15 + 15 * (attempt + 1)
                    print(f"  ⏳ Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                if res.status_code >= 500:
                    print(f"  ⚠️ Server error {res.status_code}, retrying...")
                    time.sleep(10)
                    continue
                res.raise_for_status()
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"  ⚠️ Gemini API attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(10 * (attempt + 1))
    return ""


def extract_json(text: str) -> dict | list | None:
    """Extract JSON from Gemini response (handles markdown code blocks)."""
    # Remove markdown code fences
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object or array in the text
        for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
    return None


# ── YouTube API helper ──────────────────────────────────────────────

def fetch_youtube_videos(topic_name: str, language: str, max_results: int = 3) -> list:
    """Fetch YouTube videos for a topic using YouTube Data API v3."""
    if not YOUTUBE_API_KEY:
        return []
    
    query = f"{language} {topic_name} tutorial programming"
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "q": query,
        "part": "id,snippet",
        "maxResults": max_results,
        "type": "video",
        "videoDuration": "medium",
        "videoEmbeddable": "true",
        "relevanceLanguage": "en",
        "safeSearch": "strict",
        "order": "relevance",
    }
    
    try:
        with httpx.Client(timeout=15.0) as client:
            res = client.get(url, params=params)
            if res.status_code != 200:
                print(f"  ⚠️ YouTube search failed ({res.status_code})")
                return []
            data = res.json()
        
        video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
        if not video_ids:
            return []
        
        # Get video details (duration, views)
        details_url = "https://www.googleapis.com/youtube/v3/videos"
        details_params = {
            "key": YOUTUBE_API_KEY,
            "id": ",".join(video_ids),
            "part": "contentDetails,statistics,snippet",
        }
        
        with httpx.Client(timeout=15.0) as client:
            dres = client.get(details_url, params=details_params)
            if dres.status_code != 200:
                return []
            ddata = dres.json()
        
        videos = []
        for item in ddata.get("items", []):
            duration_iso = item.get("contentDetails", {}).get("duration", "PT0S")
            duration = _format_duration(duration_iso)
            views = int(item.get("statistics", {}).get("viewCount", 0))
            
            videos.append({
                "id": f"yt_{item['id']}",
                "title": item["snippet"]["title"],
                "language": language,
                "youtubeId": item["id"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "duration": duration,
                "description": item["snippet"]["description"][:200],
                "channelTitle": item["snippet"]["channelTitle"],
                "viewCount": views,
            })
        
        return videos
    except Exception as e:
        print(f"  ⚠️ YouTube API error: {e}")
        return []


def _format_duration(iso_duration: str) -> str:
    """Convert ISO 8601 duration like PT15M33S to 15:33."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if not match:
        return "0:00"
    h, m, s = match.groups(default='0')
    h, m, s = int(h), int(m), int(s)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


# ── Content generation ──────────────────────────────────────────────

def generate_explanations(topic_name: str, language: str, difficulty: str, seed: str) -> list:
    """Generate 4 explanation styles using Gemini API."""
    prompt = f"""Generate 4 educational explanations for the programming topic "{topic_name}" in {language} ({difficulty} level).
Key concepts to cover: {seed}

Return a JSON array with exactly 4 objects, one for each style:
1. "simplified" - Clear, beginner-friendly explanation using plain language. 150-250 words.
2. "logical" - Technical, systematic breakdown with formal definitions and complexity analysis. 150-250 words.
3. "visual" - Step-by-step walkthrough with ASCII diagrams or execution traces. 150-250 words.
4. "analogy" - Real-world analogy comparing programming concepts to everyday objects. 150-250 words.

Each object must have these exact fields:
- "style": one of "simplified", "logical", "visual", "analogy"
- "title": "Simplified", "Logical", "Visual", or "Analogy"
- "icon": "📝" for simplified, "🧠" for logical, "🎨" for visual, "🔗" for analogy
- "content": the explanation text (150-250 words, educational, accurate)
- "codeExample": a complete, runnable code example in {language} (15-30 lines with comments)

IMPORTANT: Return ONLY valid JSON array. No markdown, no extra text. Make code examples real and runnable."""

    response = call_gemini(prompt)
    if not response:
        return _fallback_explanations(topic_name, language, difficulty, seed)
    
    parsed = extract_json(response)
    if isinstance(parsed, list) and len(parsed) >= 4:
        # Validate and fix icons
        icon_map = {"simplified": "📝", "logical": "🧠", "visual": "🎨", "analogy": "🔗"}
        title_map = {"simplified": "Simplified", "logical": "Logical", "visual": "Visual", "analogy": "Analogy"}
        for exp in parsed[:4]:
            style = exp.get("style", "simplified")
            exp["icon"] = icon_map.get(style, "📝")
            exp["title"] = title_map.get(style, exp.get("title", "Explanation"))
        return parsed[:4]
    
    return _fallback_explanations(topic_name, language, difficulty, seed)


def _fallback_explanations(topic_name: str, language: str, difficulty: str, seed: str) -> list:
    """Fallback explanations if Gemini fails."""
    level_desc = {"Beginner": "simple everyday", "Intermediate": "moderate", "Advanced": "in-depth technical"}
    desc = level_desc.get(difficulty, "moderate")
    
    return [
        {"style": "simplified", "title": "Simplified", "icon": "📝",
         "content": f"A clear, {desc} explanation of {topic_name} in {language}. This topic covers: {seed}. Understanding these concepts step-by-step with practical examples helps build a solid foundation for real-world programming.",
         "codeExample": f"# {topic_name} example in {language}\n# Key concepts: {seed}\n# Run this code to see the output"},
        {"style": "logical", "title": "Logical", "icon": "🧠",
         "content": f"A systematic, technical breakdown of {topic_name} in {language}. Covers internal mechanics, formal definitions, and how things work under the hood. Key areas: {seed}.",
         "codeExample": f"# Technical example for {topic_name}\n# Demonstrates: {seed}"},
        {"style": "visual", "title": "Visual", "icon": "🎨",
         "content": f"A visual, diagram-oriented explanation of {topic_name} in {language}. Uses step-by-step walkthroughs and execution flow visualization. Covers: {seed}.",
         "codeExample": f"# Step-by-step visual example for {topic_name}\n# Follow the execution flow"},
        {"style": "analogy", "title": "Analogy", "icon": "🔗",
         "content": f"A real-world analogy-based explanation of {topic_name} in {language}. Compares programming concepts to everyday objects to build intuition. Relates to: {seed}.",
         "codeExample": f"# Analogy-based example for {topic_name}\n# Real-world connection"},
    ]


def generate_quiz(topic_name: str, language: str, difficulty: str, seed: str) -> list:
    """Generate 10 quiz questions using Gemini API."""
    prompt = f"""Generate exactly 10 multiple-choice quiz questions for "{topic_name}" in {language} programming ({difficulty} level).
Key concepts: {seed}

Return a JSON array of 10 objects. Each object must have these exact fields:
- "question": A clear, specific question about {topic_name} (not generic)
- "options": An array of exactly 4 answer choices (strings)
- "correctAnswer": The index (0-3) of the correct option
- "explanation": A brief explanation (1-2 sentences) of why the correct answer is right

Requirements:
- Questions must be specific to {topic_name} in {language}
- Mix difficulty: 3 easy, 4 medium, 3 hard questions
- Include code snippets in questions where appropriate
- All 4 options should be plausible (no obviously wrong answers)
- Each question tests a different aspect of the topic

IMPORTANT: Return ONLY valid JSON array. No markdown, no extra text."""

    response = call_gemini(prompt, max_tokens=4000)
    if not response:
        return _fallback_quiz(topic_name, language, difficulty)
    
    parsed = extract_json(response)
    if isinstance(parsed, list) and len(parsed) >= 5:
        questions = []
        slug = language.lower().replace("/", "-").replace(" ", "")
        topic_slug = topic_name.lower().replace(" ", "-")[:20]
        for i, q in enumerate(parsed[:10], 1):
            questions.append({
                "id": f"q-{slug}-{topic_slug}-{i}",
                "question": q.get("question", f"Q{i} about {topic_name}"),
                "options": q.get("options", [f"Option A", f"Option B", f"Option C", f"Option D"])[:4],
                "correctAnswer": min(max(q.get("correctAnswer", 0), 0), 3),
                "explanation": q.get("explanation", f"Tests understanding of {topic_name}."),
                "type": "mcq",
            })
        # Pad if fewer than 10
        while len(questions) < 10:
            idx = len(questions) + 1
            questions.append({
                "id": f"q-{slug}-{topic_slug}-{idx}",
                "question": f"{topic_name} Quiz Q{idx}: What is a key concept in {topic_name}?",
                "options": [f"Concept A", f"Concept B", f"Concept C", f"Concept D"],
                "correctAnswer": 0,
                "explanation": f"Tests understanding of {topic_name}.",
                "type": "mcq",
            })
        return questions
    
    return _fallback_quiz(topic_name, language, difficulty)


def _fallback_quiz(topic_name: str, language: str, difficulty: str) -> list:
    """Fallback quiz if Gemini fails."""
    slug = language.lower().replace("/", "-").replace(" ", "")
    topic_slug = topic_name.lower().replace(" ", "-")[:20]
    questions = []
    for i in range(1, 11):
        questions.append({
            "id": f"q-{slug}-{topic_slug}-{i}",
            "question": f"{topic_name} Quiz Q{i} ({difficulty}): [Question about {topic_name} in {language}]",
            "options": [f"Option A", f"Option B", f"Option C", f"Option D"],
            "correctAnswer": 0,
            "explanation": f"Tests understanding of {topic_name} at {difficulty} level.",
            "type": "mcq",
        })
    return questions


def generate_overview(topic_name: str, language: str, difficulty: str, seed: str) -> str:
    """Generate a comprehensive topic overview using Gemini."""
    prompt = f"""Write a comprehensive educational overview for the programming topic "{topic_name}" in {language} ({difficulty} level).
Key concepts: {seed}

Requirements:
- 100-200 words
- Explain what the topic is and why it matters
- Mention key sub-concepts from: {seed}
- Include practical applications
- Suitable for a student at {difficulty} level

Return ONLY the overview text, no JSON, no formatting."""

    response = call_gemini(prompt, max_tokens=500)
    if response and len(response) > 50:
        return response
    
    return (
        f"{topic_name} is a {'fundamental' if difficulty == 'Beginner' else 'key' if difficulty == 'Intermediate' else 'advanced'} "
        f"concept in {language} programming. Key areas include: {seed}. "
        f"Understanding this topic is essential for building real-world applications and advancing your programming skills."
    )


def make_flowchart(topic_name: str) -> str:
    """Create flowchart JSON for a topic."""
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


# ── Build single topic ─────────────────────────────────────────────

def build_topic(idx: int, language: str, topic_name: str, difficulty: str, seed: str) -> dict:
    """Build a complete topic document with a SINGLE Gemini call + YouTube videos."""
    tid = f"topic-{idx}"
    subtopic_id = f"sub-{idx}-1"
    slug = language.lower().replace("/", "-").replace(" ", "")
    topic_slug = topic_name.lower().replace(" ", "-")[:20]
    
    print(f"\n📚 [{idx}/200] Generating: {language} - {topic_name} ({difficulty})")
    
    # SINGLE COMBINED Gemini call for overview + explanations + quiz
    print(f"  🤖 Generating all content in one API call...")
    prompt = f"""You are a programming education expert. Generate complete educational content for the topic "{topic_name}" in {language} ({difficulty} level).
Key concepts: {seed}

Return a JSON object with these exact fields:

{{
  "overview": "A 100-200 word educational overview of {topic_name} in {language}. Explain what it is, why it matters, and mention key concepts: {seed}.",
  "explanations": [
    {{
      "style": "simplified",
      "title": "Simplified",
      "icon": "📝",
      "content": "A 150-250 word clear, beginner-friendly explanation using plain language with concrete examples.",
      "codeExample": "A complete, runnable 15-30 line code example in {language} with comments."
    }},
    {{
      "style": "logical",
      "title": "Logical",
      "icon": "🧠",
      "content": "A 150-250 word technical, systematic breakdown with formal definitions and how things work under the hood.",
      "codeExample": "A different complete code example showing technical aspects."
    }},
    {{
      "style": "visual",
      "title": "Visual",
      "icon": "🎨",
      "content": "A 150-250 word step-by-step walkthrough with ASCII diagrams or execution traces.",
      "codeExample": "A code example that demonstrates step-by-step execution."
    }},
    {{
      "style": "analogy",
      "title": "Analogy",
      "icon": "🔗",
      "content": "A 150-250 word real-world analogy comparing {topic_name} concepts to everyday objects.",
      "codeExample": "A code example that relates to the analogy."
    }}
  ],
  "quiz": [
    {{
      "question": "A specific question about {topic_name} in {language}",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctAnswer": 0,
      "explanation": "Why the correct answer is right (1-2 sentences)."
    }}
  ]
}}

IMPORTANT RULES:
- The quiz array must have exactly 10 questions
- Each quiz question must be specific to {topic_name} in {language}
- Include code snippets in questions where appropriate
- All code examples must be real, runnable {language} code
- Mix quiz difficulty: 3 easy, 4 medium, 3 hard
- Return ONLY valid JSON, no markdown fences, no extra text"""

    response = call_gemini(prompt, max_tokens=10000)
    
    overview = ""
    explanations = []
    quiz = []
    
    if response:
        parsed = extract_json(response)
        if isinstance(parsed, dict):
            overview = parsed.get("overview", "")
            raw_exp = parsed.get("explanations", [])
            raw_quiz = parsed.get("quiz", [])
            
            # Validate explanations
            icon_map = {"simplified": "📝", "logical": "🧠", "visual": "🎨", "analogy": "🔗"}
            title_map = {"simplified": "Simplified", "logical": "Logical", "visual": "Visual", "analogy": "Analogy"}
            if isinstance(raw_exp, list) and len(raw_exp) >= 4:
                for exp in raw_exp[:4]:
                    style = exp.get("style", "simplified")
                    exp["icon"] = icon_map.get(style, "📝")
                    exp["title"] = title_map.get(style, exp.get("title", "Explanation"))
                explanations = raw_exp[:4]
            
            # Validate quiz
            if isinstance(raw_quiz, list) and len(raw_quiz) >= 5:
                quiz = []
                for i, q in enumerate(raw_quiz[:10], 1):
                    quiz.append({
                        "id": f"q-{slug}-{topic_slug}-{i}",
                        "question": q.get("question", f"Q{i} about {topic_name}"),
                        "options": q.get("options", ["A", "B", "C", "D"])[:4],
                        "correctAnswer": min(max(q.get("correctAnswer", 0), 0), 3),
                        "explanation": q.get("explanation", f"Tests {topic_name} knowledge."),
                        "type": "mcq",
                    })
    
    # Fallbacks
    if not overview:
        diff_word = 'fundamental' if difficulty == 'Beginner' else 'key' if difficulty == 'Intermediate' else 'advanced'
        overview = f"{topic_name} is a {diff_word} concept in {language}. Key areas: {seed}. Understanding this is essential for real-world programming."
    if not explanations:
        explanations = _fallback_explanations(topic_name, language, difficulty, seed)
    if len(quiz) < 10:
        quiz = quiz + _fallback_quiz(topic_name, language, difficulty)[len(quiz):]
    
    # Fetch YouTube videos
    print(f"  🎥 Fetching YouTube recommendations...")
    videos = fetch_youtube_videos(topic_name, language, max_results=3)
    if not videos:
        videos = [
            {"id": f"yt_placeholder_{idx}", "title": f"{topic_name} - {language} Tutorial",
             "language": language, "youtubeId": "", "thumbnail": "", "duration": "10:00",
             "description": f"Tutorial video about {topic_name} in {language}"}
        ]
    
    subtopic = {
        "id": subtopic_id,
        "name": topic_name,
        "pdfUrl": "internal",
        "pdfTitle": f"{topic_name} Study Guide",
        "overview": overview,
        "explanations": explanations,
        "flowchart": make_flowchart(topic_name),
        "quiz": quiz,
        "recommendedVideos": videos,
    }
    
    topic_doc = {
        "id": tid,
        "language": language,
        "topicName": topic_name,
        "difficulty": difficulty,
        "overview": overview,
        "subtopics": [subtopic],
        "explanations": explanations,
        "quiz": quiz,
        "recommendedVideos": videos,
    }
    
    print(f"  ✅ Done! ({len(explanations)} explanations, {len(quiz)} questions, {len(videos)} videos)")
    
    # Rate limit: pause between topics
    time.sleep(6)
    
    return topic_doc


# ── Main ────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🚀 Pixel Pirates - 200 Topic Generator")
    print(f"   Using Gemini model: {GEMINI_MODEL}")
    print(f"   YouTube API: {'✅ Available' if YOUTUBE_API_KEY else '❌ Not set'}")
    print("=" * 60)
    
    # Connect to MongoDB
    try:
        client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[DB_NAME]
        print(f"✅ Connected to MongoDB ({DB_NAME})")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Check for existing progress (resume capability)
    existing_topics = list(db.topics.find({}, {"id": 1, "_id": 0}))
    existing_ids = {t["id"] for t in existing_topics}
    
    # Build all 200 topics
    topics = []
    skipped = 0
    failed = 0
    
    for idx, (lang, name, diff, seed) in enumerate(TOPIC_DEFS, start=1):
        tid = f"topic-{idx}"
        
        # Skip if already exists (resume mode)
        if tid in existing_ids:
            print(f"  ⏭️ [{idx}/200] Skipping {lang} - {name} (already exists)")
            skipped += 1
            continue
        
        try:
            topic = build_topic(idx, lang, name, diff, seed)
            topics.append(topic)
            
            # Save to DB after each topic (in case of crash)
            db.topics.replace_one({"id": tid}, topic, upsert=True)
            
        except Exception as e:
            print(f"  ❌ Failed to generate topic {idx}: {e}")
            traceback.print_exc()
            failed += 1
            # Still create a minimal topic so the count is correct
            minimal = {
                "id": tid,
                "language": lang,
                "topicName": name,
                "difficulty": diff,
                "overview": f"Learn {name} in {lang}. Key concepts: {seed}.",
                "subtopics": [{
                    "id": f"sub-{idx}-1",
                    "name": name,
                    "pdfUrl": "internal",
                    "pdfTitle": f"{name} Study Guide",
                    "overview": f"{name} covers: {seed}.",
                    "explanations": _fallback_explanations(name, lang, diff, seed),
                    "flowchart": make_flowchart(name),
                    "quiz": _fallback_quiz(name, lang, diff),
                    "recommendedVideos": [],
                }],
                "explanations": _fallback_explanations(name, lang, diff, seed),
                "quiz": _fallback_quiz(name, lang, diff),
                "recommendedVideos": [],
            }
            db.topics.replace_one({"id": tid}, minimal, upsert=True)
    
    # Create indexes
    db.topics.create_index("id", unique=True)
    db.topics.create_index("language")
    db.topics.create_index("difficulty")
    print("\n✅ Created indexes on topics collection")
    
    # Update users with all 200 topic IDs
    all_topic_ids = [f"topic-{i}" for i in range(1, 201)]
    result = db.users.update_many(
        {},
        {"$set": {"pendingTopics": all_topic_ids, "completedTopics": [], "inProgressTopics": []}}
    )
    print(f"✅ Updated {result.modified_count} users with 200 topic IDs")
    
    # Create helper collections with indexes
    for coll_name in ["user_progress", "user_notes", "user_feedback", "mock_results"]:
        if coll_name not in db.list_collection_names():
            db.create_collection(coll_name)
    
    db.user_progress.create_index([("user_id", 1), ("topic_id", 1)], unique=True)
    db.user_notes.create_index([("user_id", 1), ("topic_id", 1)])
    db.user_feedback.create_index([("user_id", 1), ("topic_id", 1)])
    db.mock_results.create_index([("user_id", 1)])
    print("✅ Created collections and indexes")
    
    # Summary
    total_in_db = db.topics.count_documents({})
    print("\n" + "=" * 60)
    print(f"🎉 Generation Complete!")
    print(f"   New topics generated: {len(topics)}")
    print(f"   Skipped (already existed): {skipped}")
    print(f"   Failed (fallback used): {failed}")
    print(f"   Total topics in database: {total_in_db}")
    print(f"   Each topic has: 4 explanations, 10 quiz questions, YouTube videos")
    print("=" * 60)


if __name__ == "__main__":
    main()
