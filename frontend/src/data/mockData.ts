import { Topic, LeaderboardEntry, User } from '../types';

export const mockUser: User = {
    id: 'user-1',
    name: 'Alex Johnson',
    email: 'alex@edutwin.com',
    password: 'password123',
    completedTopics: ['topic-1'],
    pendingTopics: ['topic-3', 'topic-4', 'topic-5'],
    inProgressTopics: ['topic-2'],
    videosWatched: [
        {
            id: 'vid-1',
            title: 'Python Loops Explained',
            language: 'Python',
            youtubeId: 'dQw4w9WgXcQ',
            thumbnail: 'https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg',
            duration: '12:30',
            watchedAt: '2026-02-20',
            timeWatched: '10:15',
        },
        {
            id: 'vid-4',
            title: 'Functions Deep Dive',
            language: 'Python',
            youtubeId: 'dQw4w9WgXcQ',
            thumbnail: 'https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg',
            duration: '18:45',
            watchedAt: '2026-02-19',
            timeWatched: '15:20',
        },
    ],
    totalScore: 85,
    rank: 3,
    preferredStyle: 'visual',
    confusionCount: 0,
};

export const topics: Topic[] = [
    {
        id: 'topic-1',
        language: 'Python',
        topicName: 'Python Loops',
        difficulty: 'Beginner',
        overview:
            'Loops are fundamental constructs in Python that allow you to execute a block of code repeatedly. Python provides two main types of loops: for loops and while loops. Understanding loops is essential for automating repetitive tasks and processing collections of data efficiently.',
        explanations: [
            {
                style: 'visual',
                title: 'Visual Explanation',
                icon: '🎨',
                content:
                    'Imagine a conveyor belt in a factory. Each item on the belt gets the same processing. A for loop is like that belt — it takes each item from a collection and performs the same action. A while loop is like a security gate that keeps checking until a condition changes. The loop counter is like a tally board that tracks how many items have passed through.',
            },
            {
                style: 'simplified',
                title: 'Simplified Explanation',
                icon: '📝',
                content:
                    'A loop simply means "do this thing again and again." A for loop says "do this for each item in a list." A while loop says "keep doing this until I tell you to stop." Example: for i in range(5): print(i) — this prints numbers 0 through 4. That\'s it!',
            },
            {
                style: 'logical',
                title: 'Logical Explanation',
                icon: '🧠',
                content:
                    'Loops implement iteration, a core computational concept. A for loop iterates over an iterable object (list, range, string), binding each element to a loop variable. Time complexity is O(n) where n is the iterable length. A while loop evaluates a boolean expression before each iteration, continuing until it evaluates to False. Infinite loops occur when the condition never becomes False.',
            },
            {
                style: 'analogy',
                title: 'Analogy Explanation',
                icon: '🔄',
                content:
                    'Think of a loop like reading a book. A for loop is like reading each page from page 1 to page 100 — you know exactly how many pages there are. A while loop is like reading until you find a specific word — you don\'t know which page it\'s on, so you keep going until you find it. The "break" statement is like bookmarking and stopping early.',
            },
        ],
        quiz: generateQuiz('Python Loops', [
            { q: 'What keyword starts a for loop in Python?', opts: ['for', 'loop', 'repeat', 'iterate'], a: 0 },
            { q: 'What does range(5) return?', opts: ['1 to 5', '0 to 5', '0 to 4', '1 to 4'], a: 2 },
            { q: 'Which loop runs while a condition is true?', opts: ['for', 'while', 'do-while', 'foreach'], a: 1 },
            { q: 'What does "break" do in a loop?', opts: ['Pauses loop', 'Exits loop', 'Restarts loop', 'Skips iteration'], a: 1 },
            { q: 'What does "continue" do?', opts: ['Exits loop', 'Restarts loop', 'Skips current iteration', 'Pauses loop'], a: 2 },
            { q: 'How do you loop through a list?', opts: ['for i in list', 'while list', 'loop list', 'each list'], a: 0 },
            { q: 'What is a nested loop?', opts: ['Loop inside a loop', 'Two separate loops', 'A broken loop', 'A fast loop'], a: 0 },
            { q: 'What is the default start of range()?', opts: ['1', '0', '-1', 'None'], a: 1 },
            { q: 'Which is NOT a valid loop in Python?', opts: ['for', 'while', 'do-while', 'nested for'], a: 2 },
            { q: 'What happens if while condition is always True?', opts: ['Error', 'Infinite loop', 'Loop skips', 'Program exits'], a: 1 },
            { q: 'What is enumerate() used for?', opts: ['Count items', 'Get index and value', 'Sort items', 'Filter items'], a: 1 },
            { q: 'Can you use else with a for loop?', opts: ['Yes', 'No', 'Only with while', 'Only in Python 2'], a: 0 },
            { q: 'What does range(1, 10, 2) produce?', opts: ['1,3,5,7,9', '1,2,3...10', '2,4,6,8,10', '1,10,2'], a: 0 },
            { q: 'How to iterate over dictionary keys?', opts: ['for k in dict', 'while dict', 'loop dict.keys', 'each key'], a: 0 },
            { q: 'What is list comprehension?', opts: ['A loop concept', 'Creating list with for in one line', 'A data type', 'A function'], a: 1 },
        ]),
        recommendedVideos: [
            { id: 'vid-1', title: 'Python Loops Explained', language: 'Python', youtubeId: '6iF8Xb7Z3wQ', thumbnail: 'https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg', duration: '12:30' },
            { id: 'vid-2', title: 'For Loop vs While Loop', language: 'Python', youtubeId: '6iF8Xb7Z3wQ', thumbnail: 'https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg', duration: '8:45' },
            { id: 'vid-3', title: 'Loop Tricks & Tips', language: 'Python', youtubeId: '6iF8Xb7Z3wQ', thumbnail: 'https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg', duration: '15:20' },
        ],
    },
    {
        id: 'topic-2',
        language: 'Python',
        topicName: 'Python Functions',
        difficulty: 'Beginner',
        overview:
            'Functions are reusable blocks of code that perform a specific task. They help organize code, reduce repetition, and improve readability. Python functions are defined using the def keyword and can accept parameters, return values, and even be passed as arguments to other functions.',
        explanations: [
            {
                style: 'visual',
                title: 'Visual Explanation',
                icon: '🎨',
                content:
                    'Think of a function like a vending machine. You put coins in (arguments), press a button (call the function), and get a drink out (return value). The machine\'s internal mechanism (function body) is hidden from you. You can use the same machine many times with different inputs to get different outputs.',
            },
            {
                style: 'simplified',
                title: 'Simplified Explanation',
                icon: '📝',
                content:
                    'A function is a named block of code you can reuse. You define it once with "def" and call it whenever you need it. It can take inputs (parameters) and give back a result (return). Example: def greet(name): return "Hello " + name. Then call greet("Alex") to get "Hello Alex".',
            },
            {
                style: 'logical',
                title: 'Logical Explanation',
                icon: '🧠',
                content:
                    'Functions implement the DRY principle (Don\'t Repeat Yourself). They create a new scope, accept parameters (positional, keyword, *args, **kwargs), and optionally return values. Functions are first-class objects in Python — they can be stored in variables, passed as arguments, and returned from other functions. Lambda functions provide anonymous single-expression functions.',
            },
            {
                style: 'analogy',
                title: 'Analogy Explanation',
                icon: '🔄',
                content:
                    'A function is like a recipe. The recipe name is the function name. The ingredients list is the parameters. The cooking steps are the function body. The finished dish is the return value. Just like you can cook the same recipe many times with different ingredients, you can call the same function with different arguments.',
            },
        ],
        quiz: generateQuiz('Python Functions', [
            { q: 'What keyword defines a function in Python?', opts: ['func', 'def', 'function', 'define'], a: 1 },
            { q: 'What does return do in a function?', opts: ['Prints value', 'Sends value back', 'Stops program', 'Loops'], a: 1 },
            { q: 'What is a parameter?', opts: ['A variable in function definition', 'A loop counter', 'A class name', 'A module'], a: 0 },
            { q: 'What is a default parameter?', opts: ['Required input', 'Optional input with preset value', 'A global variable', 'A constant'], a: 1 },
            { q: 'What is *args used for?', opts: ['Keyword arguments', 'Variable positional arguments', 'Default values', 'Return types'], a: 1 },
            { q: 'What is **kwargs?', opts: ['Positional args', 'Variable keyword arguments', 'List args', 'Tuple args'], a: 1 },
            { q: 'Can a function return multiple values?', opts: ['Yes, as tuple', 'No', 'Only two', 'Only with return[]'], a: 0 },
            { q: 'What is a lambda function?', opts: ['Named function', 'Anonymous one-line function', 'Class method', 'A loop'], a: 1 },
            { q: 'What is function scope?', opts: ['Where variables are accessible', 'Function speed', 'Return type', 'Parameter count'], a: 0 },
            { q: 'What is recursion?', opts: ['Loop inside loop', 'Function calling itself', 'Multiple returns', 'Global function'], a: 1 },
            { q: 'What is a docstring?', opts: ['Comment', 'Documentation string in function', 'Variable name', 'Import statement'], a: 1 },
            { q: 'What happens without return statement?', opts: ['Error', 'Returns None', 'Returns 0', 'Loops'], a: 1 },
            { q: 'Can functions be passed as arguments?', opts: ['Yes', 'No', 'Only lambdas', 'Only built-ins'], a: 0 },
            { q: 'What is a decorator?', opts: ['A comment', 'Function that modifies another function', 'A variable', 'A class'], a: 1 },
            { q: 'What is the global keyword for?', opts: ['Create global var', 'Access global var inside function', 'Delete var', 'Import module'], a: 1 },
        ]),
        recommendedVideos: [
            { id: 'vid-4', title: 'Functions Deep Dive', language: 'Python', youtubeId: '9Os0o3wzS_I', thumbnail: 'https://img.youtube.com/vi/9Os0o3wzS_I/mqdefault.jpg', duration: '18:45' },
            { id: 'vid-5', title: 'Lambda & Higher Order', language: 'Python', youtubeId: '9Os0o3wzS_I', thumbnail: 'https://img.youtube.com/vi/9Os0o3wzS_I/mqdefault.jpg', duration: '14:20' },
            { id: 'vid-6', title: 'Decorators Explained', language: 'Python', youtubeId: '9Os0o3wzS_I', thumbnail: 'https://img.youtube.com/vi/9Os0o3wzS_I/mqdefault.jpg', duration: '11:00' },
        ],
    },
    {
        id: 'topic-3',
        language: 'Java',
        topicName: 'Java OOPS',
        difficulty: 'Intermediate',
        overview:
            'Object-Oriented Programming (OOP) in Java is based on four pillars: Encapsulation, Inheritance, Polymorphism, and Abstraction. Java uses classes and objects as the fundamental building blocks, enabling clean, modular, and reusable code design.',
        explanations: [
            {
                style: 'visual',
                title: 'Visual Explanation',
                icon: '🎨',
                content:
                    'Think of a class as a blueprint for a house. The blueprint defines rooms, doors, and windows (properties and methods). Each actual house built from that blueprint is an object (instance). Inheritance is like a child architect inheriting the parent\'s blueprint and adding a swimming pool. Polymorphism means the same door handle works differently on different doors.',
            },
            {
                style: 'simplified',
                title: 'Simplified Explanation',
                icon: '📝',
                content:
                    'OOP means organizing your code around "objects" — things that have data (properties) and actions (methods). A class is the template, an object is the actual thing. Inheritance lets one class get features from another. Polymorphism means same method name, different behavior. Encapsulation means hiding internal details.',
            },
            {
                style: 'logical',
                title: 'Logical Explanation',
                icon: '🧠',
                content:
                    'OOP provides four mechanisms: 1) Encapsulation — bundling data and methods, using access modifiers (private, protected, public). 2) Inheritance — IS-A relationship via extends keyword, enabling code reuse. 3) Polymorphism — compile-time (overloading) and runtime (overriding) method resolution. 4) Abstraction — hiding complexity through abstract classes and interfaces.',
            },
            {
                style: 'analogy',
                title: 'Analogy Explanation',
                icon: '🔄',
                content:
                    'OOP is like a car dealership. The Car class is the general idea of a car. A Toyota Camry object is a specific car. Inheritance: SportsCar extends Car with turbo engine. Polymorphism: All cars have a drive() method, but a Tesla drives differently from a Ferrari. Encapsulation: You use the steering wheel (public interface) without knowing the engine internals (private).',
            },
        ],
        quiz: generateQuiz('Java OOPS', [
            { q: 'What are the 4 pillars of OOP?', opts: ['Encap, Inherit, Poly, Abstract', 'Loop, Cond, Array, String', 'Class, Object, Method, Var', 'Input, Output, Process, Store'], a: 0 },
            { q: 'What is a class?', opts: ['An object', 'A blueprint for objects', 'A function', 'A variable'], a: 1 },
            { q: 'What keyword creates an object?', opts: ['create', 'new', 'make', 'object'], a: 1 },
            { q: 'What is encapsulation?', opts: ['Hiding data', 'Looping', 'Inheriting', 'Abstracting'], a: 0 },
            { q: 'What keyword enables inheritance?', opts: ['inherit', 'extends', 'super', 'implements'], a: 1 },
            { q: 'What is polymorphism?', opts: ['Same name different behavior', 'Multiple classes', 'Data hiding', 'Code reuse'], a: 0 },
            { q: 'What is method overloading?', opts: ['Same name diff params', 'Same everything', 'Different name', 'Overriding parent'], a: 0 },
            { q: 'What is method overriding?', opts: ['Child redefines parent method', 'Same method twice', 'New method', 'Static method'], a: 0 },
            { q: 'What is an abstract class?', opts: ['Cannot be instantiated', 'Regular class', 'Final class', 'Static class'], a: 0 },
            { q: 'What is an interface?', opts: ['Concrete class', 'Contract with abstract methods', 'Variable type', 'Package'], a: 1 },
            { q: 'What access modifier is most restrictive?', opts: ['public', 'protected', 'default', 'private'], a: 3 },
            { q: 'What is constructor?', opts: ['A method to destroy object', 'Special method to create object', 'A variable', 'An import'], a: 1 },
            { q: 'Can Java have multiple inheritance?', opts: ['Yes with classes', 'No', 'Yes with interfaces', 'Only abstract'], a: 2 },
            { q: 'What is "this" keyword?', opts: ['Parent class ref', 'Current object ref', 'Static ref', 'Package ref'], a: 1 },
            { q: 'What is "super" keyword?', opts: ['Current object', 'Parent class reference', 'Interface', 'Static method'], a: 1 },
        ]),
        recommendedVideos: [
            { id: 'vid-7', title: 'Java OOP Crash Course', language: 'Java', youtubeId: 'pTB0EiLXUC8', thumbnail: 'https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg', duration: '22:15' },
            { id: 'vid-8', title: 'Inheritance & Polymorphism', language: 'Java', youtubeId: 'pTB0EiLXUC8', thumbnail: 'https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg', duration: '16:30' },
            { id: 'vid-9', title: 'Design Patterns Intro', language: 'Java', youtubeId: 'pTB0EiLXUC8', thumbnail: 'https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg', duration: '25:00' },
        ],
    },
    {
        id: 'topic-4',
        language: 'C',
        topicName: 'C Pointers',
        difficulty: 'Advanced',
        overview:
            'Pointers are variables that store memory addresses of other variables. They are fundamental in C programming, enabling dynamic memory allocation, efficient array manipulation, and building complex data structures like linked lists and trees.',
        explanations: [
            {
                style: 'visual',
                title: 'Visual Explanation',
                icon: '🎨',
                content:
                    'Imagine memory as a row of lockers. Each locker has a number (address) and contents (value). A regular variable is the contents of a locker. A pointer is a piece of paper inside one locker that contains the number of another locker. Dereferencing (*ptr) means going to the locker whose number is written on the paper.',
            },
            {
                style: 'simplified',
                title: 'Simplified Explanation',
                icon: '📝',
                content:
                    'A pointer is just a variable that holds an address. Use & to get an address, and * to get the value at an address. int x = 10; int *ptr = &x; Now ptr holds the address of x, and *ptr gives you 10. That\'s the core idea!',
            },
            {
                style: 'logical',
                title: 'Logical Explanation',
                icon: '🧠',
                content:
                    'Pointers provide indirect access to memory. Declaration: type *name; Address-of operator (&) returns the lvalue address. Dereference operator (*) accesses the value at the stored address. Pointer arithmetic: ptr+1 advances by sizeof(type) bytes. NULL pointer is the sentinel value. Double pointers (int **pp) store addresses of pointers, enabling dynamic 2D arrays and modification of pointer arguments.',
            },
            {
                style: 'analogy',
                title: 'Analogy Explanation',
                icon: '🔄',
                content:
                    'A pointer is like a home address written on a sticky note. The house (variable) contains your belongings (value). The sticky note (pointer) tells you where the house is. You can give someone the sticky note (pass pointer) so they can visit your house directly and rearrange furniture (modify value). A NULL pointer is like a blank sticky note — going to that address crashes things.',
            },
        ],
        quiz: generateQuiz('C Pointers', [
            { q: 'What does a pointer store?', opts: ['A value', 'A memory address', 'A function', 'A string'], a: 1 },
            { q: 'What operator gets address of variable?', opts: ['*', '&', '#', '@'], a: 1 },
            { q: 'What operator dereferences a pointer?', opts: ['&', '->', '*', '::'], a: 2 },
            { q: 'What is a NULL pointer?', opts: ['Empty value', 'Points to address 0', 'Uninitialized', 'A string pointer'], a: 1 },
            { q: 'What is pointer arithmetic?', opts: ['Math with addresses', 'Regular math', 'String operations', 'File operations'], a: 0 },
            { q: 'What does ptr++ do?', opts: ['Increments value', 'Advances to next memory block', 'Decrements pointer', 'Nothing'], a: 1 },
            { q: 'What is a void pointer?', opts: ['Null pointer', 'Generic pointer without type', 'Empty function', 'Deleted pointer'], a: 1 },
            { q: 'What is a dangling pointer?', opts: ['Valid pointer', 'Points to freed memory', 'NULL pointer', 'Array pointer'], a: 1 },
            { q: 'How to declare an int pointer?', opts: ['int ptr', 'int *ptr', 'pointer int', '*int ptr'], a: 1 },
            { q: 'What is a double pointer?', opts: ['Two pointers', 'Pointer to a pointer', 'Large pointer', 'Float pointer'], a: 1 },
            { q: 'What is malloc()?', opts: ['Free memory', 'Allocate dynamic memory', 'Print memory', 'Copy memory'], a: 1 },
            { q: 'What must you do after malloc?', opts: ['Print', 'free() the memory', 'Return', 'Loop'], a: 1 },
            { q: 'Arrays and pointers relation?', opts: ['Unrelated', 'Array name is pointer to first element', 'Same thing', 'Arrays use double pointers'], a: 1 },
            { q: 'What is segmentation fault?', opts: ['Normal error', 'Invalid memory access', 'Syntax error', 'Logic error'], a: 1 },
            { q: 'What is sizeof() for pointers?', opts: ['Size of pointed data', 'Size of pointer variable', 'Both', 'Neither'], a: 1 },
        ]),
        recommendedVideos: [
            { id: 'vid-10', title: 'C Pointers Made Easy', language: 'C', youtubeId: 'zuegQmMdy8M', thumbnail: 'https://img.youtube.com/vi/zuegQmMdy8M/mqdefault.jpg', duration: '20:00' },
            { id: 'vid-11', title: 'Dynamic Memory in C', language: 'C', youtubeId: 'zuegQmMdy8M', thumbnail: 'https://img.youtube.com/vi/zuegQmMdy8M/mqdefault.jpg', duration: '17:30' },
            { id: 'vid-12', title: 'Pointer Pitfalls', language: 'C', youtubeId: 'zuegQmMdy8M', thumbnail: 'https://img.youtube.com/vi/zuegQmMdy8M/mqdefault.jpg', duration: '14:15' },
        ],
    },
    {
        id: 'topic-5',
        language: 'JSON',
        topicName: 'JSON Basics',
        difficulty: 'Beginner',
        overview:
            'JSON (JavaScript Object Notation) is a lightweight data interchange format that is easy for humans to read and write, and easy for machines to parse and generate. It is the most common format for API communication and configuration files in modern web development.',
        explanations: [
            {
                style: 'visual',
                title: 'Visual Explanation',
                icon: '🎨',
                content:
                    'Think of JSON as a labeled filing cabinet. Each drawer (key) has a label, and inside each drawer is content (value). Drawers can contain simple items (strings, numbers), lists of items (arrays), or even smaller filing cabinets (nested objects). The whole cabinet is wrapped in curly braces {}.',
            },
            {
                style: 'simplified',
                title: 'Simplified Explanation',
                icon: '📝',
                content:
                    'JSON is a way to write data using key-value pairs. Keys are always strings in quotes. Values can be strings, numbers, booleans, arrays, objects, or null. Example: {"name": "Alex", "age": 22, "skills": ["Python", "Java"]}. That\'s valid JSON!',
            },
            {
                style: 'logical',
                title: 'Logical Explanation',
                icon: '🧠',
                content:
                    'JSON is a text-based serialization format derived from JavaScript object literal syntax. It supports six value types: string (UTF-8, double-quoted), number (integer or float), boolean (true/false), null, array (ordered list in []), and object (unordered key-value pairs in {}). JSON is language-agnostic and parsed via JSON.parse() in JS or equivalent in other languages.',
            },
            {
                style: 'analogy',
                title: 'Analogy Explanation',
                icon: '🔄',
                content:
                    'JSON is like a restaurant order form. The form has fields (keys) like "dish", "quantity", "spice_level". You fill in values for each field. An array is like ordering multiple dishes in a list. A nested object is like a combo meal that itself contains multiple items. The kitchen (server) reads the same form format every time.',
            },
        ],
        quiz: generateQuiz('JSON Basics', [
            { q: 'What does JSON stand for?', opts: ['Java Standard Object Notation', 'JavaScript Object Notation', 'JSON Script Object', 'Java Source Object'], a: 1 },
            { q: 'What wraps a JSON object?', opts: ['[] brackets', '{} curly braces', '() parentheses', '<> angle brackets'], a: 1 },
            { q: 'JSON keys must be?', opts: ['Numbers', 'Strings in double quotes', 'Variables', 'Anything'], a: 1 },
            { q: 'Which is NOT a valid JSON value?', opts: ['string', 'undefined', 'null', 'number'], a: 1 },
            { q: 'How are arrays represented?', opts: ['{}', '[]', '()', '<>'], a: 1 },
            { q: 'Can JSON have comments?', opts: ['Yes', 'No', 'Only single-line', 'Only multi-line'], a: 1 },
            { q: 'What method parses JSON in JS?', opts: ['JSON.parse()', 'JSON.read()', 'JSON.load()', 'JSON.decode()'], a: 0 },
            { q: 'What method converts to JSON string?', opts: ['JSON.parse()', 'JSON.stringify()', 'JSON.encode()', 'JSON.write()'], a: 1 },
            { q: 'Can JSON values be nested?', opts: ['Yes', 'No', 'Only one level', 'Only arrays'], a: 0 },
            { q: 'Which is valid JSON?', opts: ['{name: "a"}', '{"name": "a"}', "{'name': 'a'}", '{name = a}'], a: 1 },
            { q: 'JSON is derived from?', opts: ['Python', 'JavaScript', 'Java', 'C++'], a: 1 },
            { q: 'What is MIME type for JSON?', opts: ['text/json', 'application/json', 'data/json', 'json/text'], a: 1 },
            { q: 'Can JSON store functions?', opts: ['Yes', 'No', 'Only arrows', 'Only named'], a: 1 },
            { q: 'What boolean values does JSON support?', opts: ['TRUE/FALSE', 'true/false', 'True/False', '1/0'], a: 1 },
            { q: 'What is the file extension for JSON?', opts: ['.js', '.json', '.txt', '.xml'], a: 1 },
        ]),
        recommendedVideos: [
            { id: 'vid-13', title: 'JSON Crash Course', language: 'JSON', youtubeId: 'iiADhChRriM', thumbnail: 'https://img.youtube.com/vi/iiADhChRriM/mqdefault.jpg', duration: '10:30' },
            { id: 'vid-14', title: 'JSON in Real Projects', language: 'JSON', youtubeId: 'iiADhChRriM', thumbnail: 'https://img.youtube.com/vi/iiADhChRriM/mqdefault.jpg', duration: '13:00' },
            { id: 'vid-15', title: 'APIs and JSON', language: 'JSON', youtubeId: 'iiADhChRriM', thumbnail: 'https://img.youtube.com/vi/iiADhChRriM/mqdefault.jpg', duration: '16:45' },
        ],
    },
];

export const leaderboard: LeaderboardEntry[] = [
    { rank: 1, userId: 'user-5', name: 'Sophia Chen', score: 145, topicsCompleted: 5, avatar: '👩‍💻' },
    { rank: 2, userId: 'user-4', name: 'Rahul Patel', score: 120, topicsCompleted: 4, avatar: '👨‍💻' },
    { rank: 3, userId: 'user-1', name: 'Alex Johnson', score: 85, topicsCompleted: 1, avatar: '🧑‍💻' },
    { rank: 4, userId: 'user-2', name: 'Maria Garcia', score: 72, topicsCompleted: 2, avatar: '👩‍🎓' },
    { rank: 5, userId: 'user-3', name: 'James Wilson', score: 58, topicsCompleted: 1, avatar: '👨‍🎓' },
];

function generateQuiz(
    _topic: string,
    items: { q: string; opts: string[]; a: number }[]
): import('../types').QuizQuestion[] {
    return items.map((item, i) => ({
        id: `q-${i + 1}`,
        question: item.q,
        options: item.opts,
        correctAnswer: item.a,
    }));
}
