subtopics_9 = [
    {
        "id": "sub-9-1", "name": "Decorators",
        "pdfUrl": "internal", "pdfTitle": "Python Decorators Guide",
        "overview": "A decorator is a function that takes another function as an argument, wraps it with additional behavior, and returns the modified function. Python uses the @decorator syntax as shorthand for func = decorator(func). Decorators are built on two key Python features: functions are first-class objects (they can be passed around like variables) and closures (inner functions can capture variables from the enclosing scope). They are used extensively in frameworks like Flask (@app.route), Django (@login_required), and testing (@pytest.fixture). The functools.wraps decorator should be used inside custom decorators to preserve the original function's metadata like __name__ and __doc__.",
        "explanations": [
            {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "A decorator adds extra behavior to a function without changing its code. Place @my_decorator above a function definition, and Python automatically wraps that function. For example, a @timer decorator can measure how long a function takes to run. A @login_required decorator can check if a user is logged in before allowing access. The decorator receives the original function, defines a new wrapper function that does something extra before or after calling the original, and returns that wrapper. Always use @functools.wraps(func) inside your decorator to keep the original function's name and documentation intact.", "codeExample": "import functools\nimport time\n\ndef timer(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        elapsed = time.time() - start\n        print(f'{func.__name__} took {elapsed:.2f}s')\n        return result\n    return wrapper\n\n@timer\ndef slow_function():\n    \"\"\"A function that sleeps for 1 second.\"\"\"\n    time.sleep(1)\n    return 'done'\n\nresult = slow_function()  # prints: slow_function took 1.00s\nprint(slow_function.__name__)  # 'slow_function' (preserved!)"},
            {"style": "logical", "title": "Logical", "icon": "🧠", "content": "Decorators leverage two Python concepts: first-class functions and closures. The @decorator syntax is syntactic sugar for func = decorator(func). A decorator receives a function object, defines an inner wrapper function (a closure that captures the original function), adds pre- or post-processing logic, and returns the wrapper. Multiple decorators stack bottom-up: @a then @b on func means func = a(b(func)). Decorators with arguments require an extra nesting level: the outer function takes arguments and returns the actual decorator. functools.wraps copies __name__, __doc__, __module__, and __qualname__ from the wrapped function to the wrapper, which is essential for debugging and introspection.", "codeExample": "import functools\n\n# Decorator WITH arguments (extra nesting level)\ndef repeat(n):\n    def decorator(func):\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            for _ in range(n):\n                result = func(*args, **kwargs)\n            return result\n        return wrapper\n    return decorator\n\n@repeat(3)\ndef greet(name):\n    print(f'Hello {name}')\n\ngreet('Alice')\n# Hello Alice\n# Hello Alice\n# Hello Alice\n\n# Stacking decorators\n@timer      # applied second: timer(repeat(2)(say_hi))\n@repeat(2)  # applied first:  repeat(2)(say_hi)\ndef say_hi():\n    print('Hi')"},
            {"style": "visual", "title": "Visual", "icon": "🎨", "content": "How @decorator works step by step:\n\nStep 1: Define the decorator function\n  def my_decorator(func):     # receives original function\n      def wrapper():           # defines wrapper\n          print('Before')      # extra behavior\n          func()               # call original\n          print('After')       # extra behavior\n      return wrapper           # return wrapper\n\nStep 2: Apply with @ syntax\n  @my_decorator\n  def say_hello():             # say_hello = my_decorator(say_hello)\n      print('Hello!')\n\nStep 3: Calling say_hello() now runs wrapper:\n  Before\n  Hello!\n  After", "codeExample": "# Step-by-step visualization\ndef my_decorator(func):\n    def wrapper(*args, **kwargs):\n        print('--- Before function call ---')\n        result = func(*args, **kwargs)\n        print('--- After function call ---')\n        return result\n    return wrapper\n\n@my_decorator\ndef say_hello(name):\n    print(f'Hello, {name}!')\n    return 42\n\nvalue = say_hello('Alice')\n# Output:\n# --- Before function call ---\n# Hello, Alice!\n# --- After function call ---\nprint(value)  # 42"},
            {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "A decorator is like gift wrapping a present. The present (your function) stays exactly the same inside, but you add wrapping paper (extra behavior) around it. @timer is like putting a stopwatch on any function to measure its speed. @login_required is like adding a bouncer at the door of a VIP room: the room (function) stays the same, but now only authorized people (logged-in users) can enter. Stacking decorators is like adding multiple layers of wrapping: first tissue paper (@repeat), then a gift box (@timer). When unwrapping, you go outside-in: timer runs first, then repeat.", "codeExample": "# Decorator as a bouncer analogy\ndef login_required(func):\n    @functools.wraps(func)\n    def wrapper(user, *args, **kwargs):\n        if not user.get('is_logged_in'):\n            print('Access denied! Please log in.')\n            return None\n        print(f'Welcome {user[\"name\"]}!')\n        return func(user, *args, **kwargs)\n    return wrapper\n\n@login_required\ndef view_dashboard(user):\n    return f'Dashboard data for {user[\"name\"]}'\n\nguest = {'name': 'Guest', 'is_logged_in': False}\nmember = {'name': 'Alice', 'is_logged_in': True}\n\nview_dashboard(guest)   # Access denied! Please log in.\nview_dashboard(member)  # Welcome Alice! -> Dashboard data"},
        ],
        # ...existing quiz and recommendedVideos for sub-9-1...
    },
    {
        "id": "sub-9-2", "name": "Generators & yield",
        "pdfUrl": "internal", "pdfTitle": "Python Generators & yield",
        "overview": "Generators are special Python functions that use the yield keyword to produce values one at a time, pausing execution between each value. Unlike regular functions that compute all results at once and return a list, generators compute each value on demand (lazy evaluation), using O(1) memory regardless of how many values they produce. When a generator function is called, it returns a generator object without executing the body. Each call to next() resumes execution until the next yield statement. When the function exits, StopIteration is raised. Generators implement the iterator protocol automatically, so they work seamlessly with for loops, list(), sum(), and other iteration tools. The send() method can push values into a running generator.",
        "explanations": [
            {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "A generator is a function that uses yield instead of return. Each time you ask for a value (using next() or a for loop), the function runs until the next yield, gives you that value, and then pauses. When you ask for the next value, it resumes from exactly where it paused. This is incredibly memory-efficient for large datasets because only one value exists in memory at a time. When there are no more values to yield, the generator is 'exhausted' and a StopIteration exception is raised. For loops handle this automatically. Think of generators as lazy sequences that compute values on the fly.", "codeExample": "def count_up(n):\n    \"\"\"Generator that counts from 0 to n-1\"\"\"\n    i = 0\n    while i < n:\n        yield i    # pause here, give i to caller\n        i += 1     # resume here on next() call\n\n# Using with next()\ngen = count_up(4)\nprint(next(gen))  # 0\nprint(next(gen))  # 1\nprint(next(gen))  # 2\nprint(next(gen))  # 3\n# next(gen) would raise StopIteration\n\n# Using with for loop (handles StopIteration)\nfor num in count_up(4):\n    print(num)  # 0, 1, 2, 3"},
            {"style": "logical", "title": "Logical", "icon": "🧠", "content": "Generator functions implement the iterator protocol (__iter__ and __next__) automatically. Calling a generator function does NOT execute the body; it returns a generator object. Each next() call executes the body until the next yield, which suspends the stack frame (preserving all local variables and the instruction pointer). The yielded value becomes the return value of next(). When the function body completes (falls off the end or hits return), StopIteration is raised. Memory is O(1) because only the current state is stored, not all values. send(value) resumes the generator and makes yield evaluate to value. throw() injects an exception. close() raises GeneratorExit inside the generator.", "codeExample": "# Generator protocol internals\ndef fibonacci():\n    a, b = 0, 1\n    while True:       # infinite generator!\n        yield a\n        a, b = b, a + b\n\nfib = fibonacci()\nprint([next(fib) for _ in range(10)])\n# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]\n\n# send() example: coroutine-like behavior\ndef accumulator():\n    total = 0\n    while True:\n        value = yield total  # yield current, receive next\n        total += value\n\nacc = accumulator()\nnext(acc)          # prime the generator -> yields 0\nprint(acc.send(10))  # 10\nprint(acc.send(20))  # 30\nprint(acc.send(5))   # 35"},
            {"style": "visual", "title": "Visual", "icon": "🎨", "content": "Generator execution flow:\n\ndef my_gen():\n    print('A')       # Step 1: runs on first next()\n    yield 1          # Step 2: pauses, returns 1\n    print('B')       # Step 3: runs on second next()\n    yield 2          # Step 4: pauses, returns 2\n    print('C')       # Step 5: runs on third next()\n                     # Step 6: StopIteration raised\n\ngen = my_gen()       # Nothing printed yet!\nnext(gen)            # prints 'A', returns 1\nnext(gen)            # prints 'B', returns 2\nnext(gen)            # prints 'C', raises StopIteration", "codeExample": "# Memory comparison: list vs generator\nimport sys\n\n# List: stores ALL values in memory\nbig_list = [x * x for x in range(1_000_000)]\nprint(sys.getsizeof(big_list))  # ~8,000,000 bytes (8 MB)\n\n# Generator: stores only current state\nbig_gen = (x * x for x in range(1_000_000))\nprint(sys.getsizeof(big_gen))   # ~200 bytes (!)\n\n# Both produce the same sum\nprint(sum(x * x for x in range(1_000_000)))\n# Works with O(1) memory using generator expression"},
            {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "A generator is like a storyteller reading a book one page at a time. They remember exactly which page they are on (yield pauses and saves state). When you say 'next page please' (next()), they read exactly one more page and pause again. They do not need to photocopy the entire book into memory. A regular function that returns a list is like photocopying every page before handing you the stack. With a 10-million-page book, the storyteller (generator) is far more efficient. When they reach the last page, they say 'The End' (StopIteration). The send() method is like the audience shouting requests to the storyteller.", "codeExample": "# Storyteller analogy\ndef read_book(pages):\n    \"\"\"Generator: reads one page at a time\"\"\"\n    for i, page in enumerate(pages, 1):\n        print(f'[Reading page {i}...]')\n        yield page\n    print('The End!')\n\nbook = ['Once upon a time...', 'The hero traveled far.',\n        'They found the treasure.', 'Happily ever after.']\n\nstoryteller = read_book(book)\nprint(next(storyteller))  # [Reading page 1...] Once upon...\nprint(next(storyteller))  # [Reading page 2...] The hero...\n# Only 2 pages in memory, not all 4"},
        ],
        # ...existing quiz and recommendedVideos for sub-9-2...
    },
    {
        "id": "sub-9-3", "name": "Generator Expressions & Iteration",
        "pdfUrl": "internal", "pdfTitle": "Iterator & Generator Expressions",
        "overview": "Generator expressions provide a concise, memory-efficient syntax to create generators inline using parentheses instead of square brackets: (expr for x in iterable). They produce values lazily, computing each one only when requested. Unlike list comprehensions which build the entire list in memory, generator expressions use O(1) space. They can be used directly in functions like sum(), min(), max(), and any(). Generator expressions are single-pass: once consumed, they cannot be iterated again. The itertools module provides powerful generator-based utilities like chain(), islice(), groupby(), product(), and combinations() for advanced iteration patterns.",
        "explanations": [
            {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "A generator expression looks just like a list comprehension but uses round brackets () instead of square brackets []. For example, (x**2 for x in range(10)) creates a generator that computes squares one at a time. It uses almost no memory, even for millions of values. You can feed them directly into functions like sum(), list(), or any for loop. They are single-pass, meaning once you iterate through them, they are exhausted and cannot be reused. For small data, list comprehensions are fine. For large data or infinite streams, generator expressions are essential to avoid running out of memory.", "codeExample": "# Generator expression vs list comprehension\nsquares_list = [x**2 for x in range(10)]   # list in memory\nsquares_gen  = (x**2 for x in range(10))   # lazy generator\n\nprint(type(squares_list))  # <class 'list'>\nprint(type(squares_gen))   # <class 'generator'>\n\n# Direct use in functions (no extra list needed)\ntotal = sum(x**2 for x in range(1000000))  # O(1) memory\nprint(total)  # 333332833333500000\n\n# Filtering with condition\nevens = (x for x in range(20) if x % 2 == 0)\nprint(list(evens))  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]"},
            {"style": "logical", "title": "Logical", "icon": "🧠", "content": "Generator expressions use the syntax (expr for var in iterable [if condition]). They return a generator object implementing __iter__ and __next__. They are consumed in a single pass: once exhausted, iterating again yields nothing. Nested generator expressions can be chained: g2 = (f(x) for x in g1). The itertools module provides powerful utilities: chain() concatenates iterables, islice() slices lazily, groupby() groups consecutive elements, product() computes Cartesian products, combinations() and permutations() for combinatorics. map() and filter() also return lazy iterators in Python 3. For reusability, define a generator function instead of an expression.", "codeExample": "from itertools import chain, islice, groupby\n\n# chain: concatenate multiple iterables lazily\ncombined = chain(range(3), range(10, 13))\nprint(list(combined))  # [0, 1, 2, 10, 11, 12]\n\n# islice: lazy slicing (no list created)\nfib = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34)\nprint(list(islice(fib, 3, 7)))  # [2, 3, 5, 8]\n\n# Chaining generators\nnums = range(1, 11)\nsquared = (x**2 for x in nums)\nfiltered = (x for x in squared if x > 20)\nprint(list(filtered))  # [25, 36, 49, 64, 81, 100]\n\n# Single-pass proof\ngen = (x for x in range(3))\nprint(list(gen))  # [0, 1, 2]\nprint(list(gen))  # [] (exhausted!)"},
            {"style": "visual", "title": "Visual", "icon": "🎨", "content": "Memory comparison:\n\nList comprehension [x**2 for x in range(1000000)]:\n  Allocates ~8 MB for 1 million integers\n  All values computed and stored immediately\n\nGenerator expression (x**2 for x in range(1000000)):\n  Allocates ~200 bytes (just the generator state)\n  Values computed one at a time on demand\n\nExecution flow of sum(x**2 for x in range(5)):\n  x=0 -> yield 0  -> sum adds 0  (total=0)\n  x=1 -> yield 1  -> sum adds 1  (total=1)\n  x=2 -> yield 4  -> sum adds 4  (total=5)\n  x=3 -> yield 9  -> sum adds 9  (total=14)\n  x=4 -> yield 16 -> sum adds 16 (total=30)\n  Result: 30", "codeExample": "import sys\n\n# Memory comparison\nbig_list = [x for x in range(1_000_000)]\nbig_gen  = (x for x in range(1_000_000))\n\nprint(f'List: {sys.getsizeof(big_list):,} bytes')  # ~8,000,056\nprint(f'Gen:  {sys.getsizeof(big_gen):,} bytes')    # ~200\n\n# Practical use: find first match in huge data\ndef find_first_prime_above(n):\n    \"\"\"Find the first prime number above n\"\"\"\n    candidates = (x for x in range(n+1, n+10000))\n    return next(x for x in candidates\n                if all(x % d != 0 for d in range(2, int(x**0.5)+1)))\n\nprint(find_first_prime_above(1000))  # 1009"},
            {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "A list comprehension is like printing every page of a cookbook and stacking them all on your desk. You have instant access to any recipe, but it takes a lot of paper (memory). A generator expression is like having a chef who knows all the recipes but only cooks the dish you ask for right now. No wasted paper, no wasted food, just the one dish you need at the moment. The itertools module is like a set of kitchen tools: chain() is combining two recipe books, islice() is opening to a specific chapter, and groupby() is sorting recipes by cuisine. The downside: once the chef has cooked through the menu (single-pass), you need to start over with a new generator.", "codeExample": "# Chef analogy - practical file processing\ndef read_large_file(filepath):\n    \"\"\"Generator: reads file line by line (O(1) memory)\"\"\"\n    with open(filepath) as f:\n        for line in f:\n            yield line.strip()\n\n# Process million-line file without loading it all\n# long_lines = (line for line in read_large_file('huge.txt')\n#               if len(line) > 100)\n# for line in long_lines:\n#     process(line)  # one line at a time!\n\n# Equivalent: built-in map/filter are also lazy\nnums = [1, 2, 3, 4, 5]\ndoubled = map(lambda x: x * 2, nums)  # lazy!\nprint(list(doubled))  # [2, 4, 6, 8, 10]"},
        ],
        # ...existing quiz and recommendedVideos for sub-9-3...
    }
]
topic_8_subtopics = [
    {
        "id": "sub-8-1", "name": "ArrayList & LinkedList",
        "pdfUrl": "internal", "pdfTitle": "Java ArrayList & LinkedList",
        "overview": "ArrayList and LinkedList are the two primary List implementations in Java. ArrayList is backed by a dynamic Object[] array, offering O(1) random access via get(index) and amortized O(1) add at the end. LinkedList uses doubly-linked nodes, providing O(1) insertion and removal at both ends but O(n) random access. ArrayList is cache-friendly due to contiguous memory and is the default choice for most use cases. LinkedList shines when you need frequent insertions and deletions at the beginning or middle of the list, or when implementing a queue/deque pattern.",
        "explanations": [
            {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "ArrayList is like a row of numbered lockers: you can instantly access locker number 42 because they are in a line. Adding at the end is fast, but inserting in the middle means shifting all the lockers after it. LinkedList is like a chain where each link knows the next and previous link. Adding or removing at the ends is instant, but finding item number 42 requires walking through 42 links one by one. For most everyday coding, use ArrayList. Only switch to LinkedList if you frequently add and remove elements at the beginning of the list or need a deque-like structure.", "codeExample": "import java.util.ArrayList;\nimport java.util.LinkedList;\n\n// ArrayList: fast random access\nArrayList<String> al = new ArrayList<>();\nal.add(\"Apple\");   // [Apple]\nal.add(\"Banana\");  // [Apple, Banana]\nal.add(\"Cherry\");  // [Apple, Banana, Cherry]\n\nSystem.out.println(al.get(1)); // \"Banana\" - O(1)\nal.remove(0);                   // O(n) shift\n\n// LinkedList: fast add/remove at ends\nLinkedList<String> ll = new LinkedList<>();\nll.addFirst(\"X\");  // [X]\nll.addLast(\"Y\");   // [X, Y]\nll.addFirst(\"W\");  // [W, X, Y]\nSystem.out.println(ll.getFirst()); // \"W\" - O(1)\nSystem.out.println(ll.get(1));     // \"X\" - O(n)"},
            {"style": "logical", "title": "Logical", "icon": "🧠", "content": "ArrayList is internally backed by Object[], with default initial capacity 10. When full, it grows by 50% (newCapacity = oldCapacity + oldCapacity >> 1). get(index) is O(1) via array indexing. add(element) at the end is amortized O(1). add(index, element) and remove(index) at arbitrary positions are O(n) due to System.arraycopy shifts. LinkedList is a doubly-linked list implementing both List and Deque interfaces. addFirst/addLast/removeFirst/removeLast are O(1). get(index) is O(n) requiring node traversal. ArrayList has better cache locality because array elements are stored contiguously in memory, whereas LinkedList nodes may be scattered across the heap.", "codeExample": "import java.util.ArrayList;\nimport java.util.LinkedList;\n\n// ArrayList capacity management\nArrayList<Integer> al = new ArrayList<>(20); // initial cap 20\nfor (int i = 0; i < 15; i++) al.add(i);\n// size=15, internal array length=20 (no resize yet)\n\nal.trimToSize(); // shrink internal array to size\n\n// LinkedList as Deque\nLinkedList<Integer> deque = new LinkedList<>();\ndeque.offerFirst(1); // add to front\ndeque.offerLast(2);  // add to back\ndeque.offerFirst(0); // [0, 1, 2]\n\nint first = deque.pollFirst(); // 0, removes from front\nint last = deque.pollLast();   // 2, removes from back"},
            {"style": "visual", "title": "Visual", "icon": "🎨", "content": "ArrayList memory layout (contiguous array):\n[Apple][Banana][Cherry][  ][  ]\n  0       1       2    (unused capacity)\nget(1) -> direct jump to index 1 -> O(1)\n\nLinkedList memory layout (scattered nodes):\n[W|->][<-|X|->][<-|Y]\nhead         middle        tail\nget(1) -> start at head, follow next pointer -> O(n)\n\nInsert at index 0:\nArrayList: shift ALL elements right -> O(n)\nLinkedList: just update head pointer -> O(1)", "codeExample": "// Performance comparison\nimport java.util.*;\n\nArrayList<Integer> al = new ArrayList<>();\nLinkedList<Integer> ll = new LinkedList<>();\n\n// Adding 100000 elements at the BEGINNING\nlong start = System.nanoTime();\nfor (int i = 0; i < 100000; i++) al.add(0, i); // SLOW\nlong alTime = System.nanoTime() - start;\n\nstart = System.nanoTime();\nfor (int i = 0; i < 100000; i++) ll.addFirst(i); // FAST\nlong llTime = System.nanoTime() - start;\n\nSystem.out.println(\"ArrayList: \" + alTime/1e6 + \"ms\");\nSystem.out.println(\"LinkedList: \" + llTime/1e6 + \"ms\");\n// LinkedList is MUCH faster for front insertions"},
            {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "ArrayList is like numbered lockers in a gym. Want locker 42? Walk right to it instantly. But if you need to insert a new locker between 20 and 21, every locker from 21 onward must be renumbered and shifted down. LinkedList is like a treasure hunt where each clue leads to the next location. To find the 10th clue, you must follow all 9 clues before it. But adding a new clue between any two existing clues is easy: just change what the previous clue points to. Choose lockers (ArrayList) when you need fast lookup. Choose treasure hunt (LinkedList) when you frequently rearrange the order.", "codeExample": "// Choosing the right one\nimport java.util.*;\n\n// Use ArrayList for random access patterns\nList<String> students = new ArrayList<>();\nstudents.add(\"Alice\"); students.add(\"Bob\");\nString second = students.get(1); // instant access\n\n// Use LinkedList for queue/deque patterns\nLinkedList<String> taskQueue = new LinkedList<>();\ntaskQueue.addLast(\"Task A\");  // enqueue\ntaskQueue.addLast(\"Task B\");\nString next = taskQueue.removeFirst(); // dequeue \"Task A\""},
        ],
        # ...existing quiz and recommendedVideos for sub-8-1...
    },
    {
        "id": "sub-8-2", "name": "HashMap & TreeMap",
        "pdfUrl": "internal", "pdfTitle": "Java HashMap & TreeMap Guide",
        "overview": "HashMap and TreeMap are the two primary Map implementations in Java. HashMap stores key-value pairs in a hash table, providing O(1) average-case get, put, and remove operations. It does not maintain any ordering of keys. TreeMap uses a Red-Black tree to keep keys in sorted (natural or custom) order, with O(log n) operations. HashMap is the default choice when you need fast lookups. TreeMap is used when you need sorted keys or range queries through the NavigableMap interface (subMap, headMap, tailMap). LinkedHashMap preserves insertion order while maintaining O(1) performance.",
        "explanations": [
            {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "HashMap is the fastest way to store key-value pairs in Java. Give it a key, and it finds the value almost instantly using hashing. Keys have no particular order. TreeMap is slower but keeps all keys sorted, so you can iterate in alphabetical or numerical order. Use HashMap for maximum speed when order does not matter. Use TreeMap when you need sorted keys, like building a sorted dictionary or finding the smallest and largest keys. LinkedHashMap is a middle ground that maintains the order in which you inserted items while keeping HashMap speed.", "codeExample": "import java.util.HashMap;\nimport java.util.TreeMap;\n\n// HashMap: fast but unordered\nHashMap<String, Integer> hm = new HashMap<>();\nhm.put(\"banana\", 2);\nhm.put(\"apple\", 5);\nhm.put(\"cherry\", 1);\n\nSystem.out.println(hm.get(\"apple\")); // 5 - O(1)\n// Iteration order is NOT guaranteed\n\n// TreeMap: sorted by key\nTreeMap<String, Integer> tm = new TreeMap<>();\ntm.put(\"banana\", 2);\ntm.put(\"apple\", 5);\ntm.put(\"cherry\", 1);\n\nSystem.out.println(tm.firstKey());  // \"apple\"\nSystem.out.println(tm.lastKey());   // \"cherry\"\n// Iteration: apple->5, banana->2, cherry->1"},
            {"style": "logical", "title": "Logical", "icon": "🧠", "content": "HashMap uses an array of buckets. The hash of the key determines the bucket index. Java 8+ converts buckets with 8+ collisions from linked lists to balanced trees (O(log n) worst case instead of O(n)). Default load factor is 0.75; exceeding it triggers rehashing to double the bucket count. TreeMap is a Red-Black tree providing guaranteed O(log n) for get, put, and remove. It implements NavigableMap, enabling subMap(fromKey, toKey), headMap(toKey), and tailMap(fromKey) for range queries. The Comparable interface or a Comparator determines key ordering. containsKey is O(1) for HashMap and O(log n) for TreeMap.", "codeExample": "import java.util.TreeMap;\nimport java.util.NavigableMap;\n\nTreeMap<Integer, String> scores = new TreeMap<>();\nscores.put(85, \"Bob\");\nscores.put(92, \"Alice\");\nscores.put(78, \"Charlie\");\nscores.put(95, \"Diana\");\n\n// Range query: scores between 80 and 93\nNavigableMap<Integer, String> range =\n    scores.subMap(80, true, 93, true);\nSystem.out.println(range); // {85=Bob, 92=Alice}\n\n// Floor and ceiling\nSystem.out.println(scores.floorKey(90));   // 85\nSystem.out.println(scores.ceilingKey(90)); // 92"},
            {"style": "visual", "title": "Visual", "icon": "🎨", "content": "HashMap internal structure:\nBuckets: [0][ ]  [1][ ]  [2][apple->5]  [3][ ]  [4][banana->2, cherry->1]\n           hash(\"apple\")%size = 2\n           hash(\"banana\")%size = 4  (collision with cherry)\n\nTreeMap internal structure (Red-Black tree):\n         [banana:2]\n        /          \\\n  [apple:5]     [cherry:1]\n\nIn-order traversal gives sorted keys: apple, banana, cherry", "codeExample": "import java.util.*;\n\n// HashMap: check for key/value existence\nHashMap<String, Integer> map = new HashMap<>();\nmap.put(\"x\", 10);\nmap.put(\"y\", 20);\n\nSystem.out.println(map.containsKey(\"x\"));    // true\nSystem.out.println(map.containsValue(20));    // true\nSystem.out.println(map.getOrDefault(\"z\", 0)); // 0\n\n// Iterate over entries\nfor (Map.Entry<String, Integer> e : map.entrySet())\n    System.out.println(e.getKey() + \"=\" + e.getValue());"},
            {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "HashMap is like a coat check at a theater. You hand in your coat and get a numbered ticket (hash). When you return, you give the ticket and instantly get your coat back. The coats are not stored in any particular order, just wherever there is space. TreeMap is like an alphabetical filing cabinet. Every folder is placed in the right alphabetical spot. Looking something up takes a bit longer because you navigate through the alphabet, but you can easily say 'show me everything from D to G' (range query). LinkedHashMap is a coat check that remembers the order people arrived.", "codeExample": "import java.util.LinkedHashMap;\n\n// LinkedHashMap: insertion-order preserved\nLinkedHashMap<String, Integer> lhm = new LinkedHashMap<>();\nlhm.put(\"banana\", 2);\nlhm.put(\"apple\", 5);\nlhm.put(\"cherry\", 1);\n\n// Iterates in insertion order:\nfor (var entry : lhm.entrySet())\n    System.out.println(entry);\n// banana=2, apple=5, cherry=1 (insertion order!)"},
        ],
        # ...existing quiz and recommendedVideos for sub-8-2...
    },
    {
        "id": "sub-8-3", "name": "HashSet & TreeSet",
        "pdfUrl": "internal", "pdfTitle": "Java HashSet & TreeSet Guide",
        "overview": "HashSet and TreeSet are the primary Set implementations in Java for storing unique elements. HashSet is backed by a HashMap internally (values are dummy objects), providing O(1) average-case add, remove, and contains operations. It does not maintain any element order. TreeSet uses a Red-Black tree (backed by TreeMap) to keep elements in sorted order with O(log n) operations. For HashSet to work correctly, the stored objects must properly override equals() and hashCode(). TreeSet requires elements to implement Comparable or a Comparator to be provided. LinkedHashSet maintains insertion order with O(1) operations.",
        "explanations": [
            {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "HashSet is a collection that stores only unique elements with no duplicates allowed. Adding an element that already exists is silently ignored. It is extremely fast for checking if something exists (contains), adding, and removing, all in O(1) average time. However, elements have no guaranteed order. TreeSet also stores unique elements but keeps them sorted at all times. This means iterating over a TreeSet always gives elements in ascending order. Use HashSet when you only care about uniqueness and speed. Use TreeSet when you need sorted unique elements.", "codeExample": "import java.util.HashSet;\nimport java.util.TreeSet;\n\n// HashSet: fast, unordered, no duplicates\nHashSet<String> hs = new HashSet<>();\nhs.add(\"Banana\");\nhs.add(\"Apple\");\nhs.add(\"Cherry\");\nhs.add(\"Apple\");  // duplicate ignored!\n\nSystem.out.println(hs.size());          // 3\nSystem.out.println(hs.contains(\"Apple\")); // true\n\n// TreeSet: sorted, no duplicates\nTreeSet<String> ts = new TreeSet<>();\nts.add(\"Banana\"); ts.add(\"Apple\"); ts.add(\"Cherry\");\n\nSystem.out.println(ts.first()); // \"Apple\"\nSystem.out.println(ts.last());  // \"Cherry\"\nfor (String s : ts) System.out.print(s + \" \");\n// Apple Banana Cherry (sorted!)"},
            {"style": "logical", "title": "Logical", "icon": "🧠", "content": "HashSet internally wraps a HashMap where every element is a key mapped to a dummy PRESENT object. add() calls HashMap.put(element, PRESENT), so all HashMap rules apply: proper equals() and hashCode() are essential. If two objects are equal by equals(), they must have the same hashCode(). TreeSet wraps a TreeMap similarly. It implements NavigableSet, providing methods like first(), last(), higher(e), lower(e), subSet(from, to), headSet(to), and tailSet(from). LinkedHashSet extends HashSet with a linked list overlay to maintain insertion order. Set operations like union, intersection, and difference can be done with addAll, retainAll, and removeAll respectively.", "codeExample": "import java.util.*;\n\n// Set operations\nSet<Integer> a = new HashSet<>(Arrays.asList(1, 2, 3, 4));\nSet<Integer> b = new HashSet<>(Arrays.asList(3, 4, 5, 6));\n\n// Union\nSet<Integer> union = new HashSet<>(a);\nunion.addAll(b);  // {1, 2, 3, 4, 5, 6}\n\n// Intersection\nSet<Integer> inter = new HashSet<>(a);\ninter.retainAll(b); // {3, 4}\n\n// Difference\nSet<Integer> diff = new HashSet<>(a);\ndiff.removeAll(b);  // {1, 2}\n\n// TreeSet navigation\nTreeSet<Integer> ts = new TreeSet<>(a);\nSystem.out.println(ts.higher(2));  // 3\nSystem.out.println(ts.lower(3));   // 2"},
            {"style": "visual", "title": "Visual", "icon": "🎨", "content": "HashSet internal (backed by HashMap):\nBuckets: [0][Cherry] [1][ ] [2][Apple] [3][Banana]\ncontains(\"Apple\") -> hash(\"Apple\") -> bucket 2 -> found! O(1)\n\nTreeSet internal (Red-Black tree):\n       [Banana]\n      /        \\\n  [Apple]    [Cherry]\nIteration: Apple -> Banana -> Cherry (in-order = sorted)\n\nadd(\"Apple\") again? Already in tree -> returns false, no change.", "codeExample": "import java.util.TreeSet;\n\nTreeSet<Integer> ts = new TreeSet<>();\nts.add(50); ts.add(20); ts.add(80); ts.add(10); ts.add(60);\n\nSystem.out.println(ts);           // [10, 20, 50, 60, 80]\nSystem.out.println(ts.first());   // 10\nSystem.out.println(ts.last());    // 80\n\n// subSet: elements from 20 (inclusive) to 60 (exclusive)\nSystem.out.println(ts.subSet(20, 60)); // [20, 50]\n\n// headSet: elements less than 50\nSystem.out.println(ts.headSet(50));    // [10, 20]"},
            {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "HashSet is like a VIP guest list at a concert. Each name appears only once, and the bouncer can check if your name is on the list almost instantly by looking up a hash. But the list has no particular order. TreeSet is the same guest list but kept in alphabetical order. Checking if a name is there is slightly slower because the bouncer has to do a binary-search-style lookup, but you can easily answer questions like 'who comes after Dave?' or 'list everyone between C and M.' LinkedHashSet remembers the order in which people signed up.", "codeExample": "import java.util.LinkedHashSet;\n\n// LinkedHashSet: insertion order preserved\nLinkedHashSet<String> guestList = new LinkedHashSet<>();\nguestList.add(\"Charlie\");\nguestList.add(\"Alice\");\nguestList.add(\"Bob\");\nguestList.add(\"Alice\"); // duplicate ignored\n\nfor (String guest : guestList)\n    System.out.print(guest + \" \");\n// Charlie Alice Bob (insertion order!)"},
        ],
        # ...existing quiz and recommendedVideos for sub-8-3...
    },
]
"""
Seed Database Script â€” Populates MongoDB with comprehensive educational data.
Run:  python seed_database.py
"""

import bcrypt, pymongo, sys
from datetime import datetime, timedelta

MONGO_URL = "mongodb://localhost:27017/"
DB_NAME   = "pixel_pirates"

def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# TOPICS (10 topics across Python, Java, JS, C, C++, SQL)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TOPICS = [
    {
        "id": "topic-1",
        "language": "Python",
        "topicName": "Python Loops",
        "difficulty": "Beginner",
        "overview": (
            "Loops are fundamental constructs in Python that allow you to execute a block of code repeatedly. "
            "Python supports two primary loop types: 'for' loops for iterating over sequences and 'while' loops "
            "for repeating until a condition becomes false. Mastering loops is essential for tasks like data processing, "
            "automation, and building algorithms. You'll learn about range(), enumerate(), break, continue, and "
            "nested loop patterns that form the backbone of Python programming."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Start Loop","detail":"Initialize loop variable"},{"id":"p1","type":"process","label":"for i in range(n)","detail":"Iterator picks next item from sequence"},{"id":"d1","type":"decision","label":"More items left?","detail":"Check if iterator is exhausted","yes":"Execute loop body","no":"Exit loop"},{"id":"p2","type":"process","label":"Execute Loop Body","detail":"Run the indented code block"},{"id":"d2","type":"decision","label":"break or continue?","detail":"Check for control keywords","yes":"break -> exit, continue -> skip","no":"Go to next iteration"},{"id":"p3","type":"process","label":"Increment / Next Item","detail":"Move to the next element in the iterable"},{"id":"e1","type":"end","label":"Loop Complete","detail":"All items processed or break was called"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "A for loop says: 'Do this thing for every item in my list.' A while loop says: 'Keep doing this until I say stop.' range(5) gives you numbers 0,1,2,3,4. break exits the loop early, continue skips the current item and moves to the next one."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "A for loop iterates over an iterable object, binding each element to the loop variable per iteration with O(n) time complexity. A while loop evaluates a boolean condition before each iteration. range(start, stop, step) generates an arithmetic progression lazily. Loop control: break terminates, continue advances to next iteration, else clause executes when loop completes without break."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "Think of a for loop as reading every page in a book â€” you go through each one in order. A while loop is like eating chips â€” you keep eating WHILE there are chips in the bag. break is slamming the book shut mid-chapter. continue is skipping a page you've already read."},
        ],
        "quiz": [
            {"id": "q1-1", "question": "What keyword starts a for loop in Python?", "options": ["for", "loop", "repeat", "iterate"], "correctAnswer": 0},
            {"id": "q1-2", "question": "What does range(5) generate?", "options": ["1 to 5", "0 to 5", "0 to 4", "1 to 4"], "correctAnswer": 2},
            {"id": "q1-3", "question": "Which statement skips the current iteration?", "options": ["break", "pass", "continue", "return"], "correctAnswer": 2},
            {"id": "q1-4", "question": "What is the output of: for i in range(3): print(i)?", "options": ["1 2 3", "0 1 2", "0 1 2 3", "1 2"], "correctAnswer": 1},
            {"id": "q1-5", "question": "Which loop is best for iterating over a list?", "options": ["while loop", "do-while loop", "for loop", "repeat loop"], "correctAnswer": 2},
        ],
        "recommendedVideos": [
            {"id": "vid-1", "title": "Python For Loops Tutorial", "language": "Python", "youtubeId": "6iF8Xb7Z3wQ", "thumbnail": "https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg", "duration": "12:30"},
            {"id": "vid-2", "title": "While Loops in Python Explained", "language": "Python", "youtubeId": "HZARImviDxg", "thumbnail": "https://img.youtube.com/vi/HZARImviDxg/mqdefault.jpg", "duration": "8:45"},
        ],
        "subtopics": [
            {
                "id": "sub-1-1", "name": "For Loop",
                "pdfUrl": "internal", "pdfTitle": "For Loop â€“ Complete Guide",
                "overview": "The for loop is one of the most fundamental constructs in Python. It iterates over a sequence such as a list, tuple, string, or range object, executing the loop body once for each item. Unlike C-style for loops that use counters, Python's for loop works directly with iterables, making code cleaner and less error-prone. The range() function generates a sequence of numbers â€” range(5) produces 0, 1, 2, 3, 4. You can also use range(start, stop, step) for more control. The enumerate() function is extremely useful when you need both the index and the value, returning tuples like (0, 'apple'), (1, 'banana'). Nested for loops let you iterate over multi-dimensional data like matrices. For loops also support an else clause that runs when the loop completes without hitting a break statement.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "A for loop goes through items one by one â€” it's the most common way to repeat code in Python. When you write 'for x in [1, 2, 3]', the loop runs 3 times: first x is 1, then x is 2, then x is 3. The range() function generates numbers for you â€” range(5) gives 0, 1, 2, 3, 4 (note: it stops BEFORE 5). You can also use range(2, 8) to get numbers from 2 to 7, or range(0, 10, 2) to count by twos: 0, 2, 4, 6, 8. The enumerate() function is a handy shortcut when you need both the position and the value â€” instead of tracking an index variable yourself, enumerate gives you tuples like (0, 'apple'). You can loop over strings character by character, over dictionary keys, or even over file lines. Nested for loops (a loop inside a loop) are used for working with 2D data like tables or matrices.", "codeExample": "# Basic for loop with range\nfor i in range(5):\n    print(i)  # prints 0, 1, 2, 3, 4\n\n# Looping over a list\nfruits = ['apple', 'banana', 'cherry']\nfor fruit in fruits:\n    print(fruit)\n\n# Using enumerate for index + value\nfor index, fruit in enumerate(fruits):\n    print(f'{index}: {fruit}')\n# Output: 0: apple, 1: banana, 2: cherry\n\n# Nested for loop\nfor i in range(3):\n    for j in range(3):\n        print(f'({i},{j})', end=' ')"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "The for loop in Python works by calling __iter__() on the iterable to obtain an iterator object, then repeatedly calling __next__() on that iterator until a StopIteration exception is raised. This is called the Iterator Protocol. The range(start, stop, step) function creates a lazy arithmetic progression â€” it doesn't store all numbers in memory, but calculates each one on demand. This makes range(1000000) memory-efficient. Time complexity of a for loop is O(n) where n is the number of items in the iterable. The enumerate(iterable, start=0) function wraps each item as an (index, item) tuple without creating a new list in memory. For loops support an else clause that executes when the loop terminates normally (not via break). List comprehensions like [x**2 for x in range(10)] are syntactic sugar for for loops that create lists more concisely.", "codeExample": "# Iterator protocol under the hood\nnums = [10, 20, 30]\niterator = iter(nums)   # calls nums.__iter__()\nprint(next(iterator))   # 10 â€” calls iterator.__next__()\nprint(next(iterator))   # 20\nprint(next(iterator))   # 30\n# next(iterator) â†’ raises StopIteration\n\n# range is memory efficient\nimport sys\nprint(sys.getsizeof(range(1000000)))  # ~48 bytes!\nprint(sys.getsizeof(list(range(1000000))))  # ~8MB\n\n# for-else clause\nfor n in range(2, 10):\n    if n == 5:\n        break\nelse:\n    print('Loop completed without break')"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Step 1: Start â†’ Python calls iter() on the sequence to create an iterator\nStep 2: Check â†’ Call next() on the iterator. Are there more items?\nStep 3: YES â†’ Bind the next item to the loop variable (e.g., i = 0)\nStep 4: Execute the indented loop body (your code runs here)\nStep 5: Go back to Step 2 and get the next item\nStep 6: NO (StopIteration raised) â†’ Exit the loop\nStep 7: If there's an else clause and no break was hit, run the else block\n\nVisualized flow for: for i in range(3): print(i)\nâ†’ i=0, print 0 â†’ i=1, print 1 â†’ i=2, print 2 â†’ StopIteration â†’ done", "codeExample": "# Visual step-by-step execution:\nfor i in range(3):\n    print(f'Step: i = {i}')\n\n# Output:\n# Step: i = 0\n# Step: i = 1\n# Step: i = 2\n\n# Looping over a string\nfor char in 'Python':\n    print(char, end='-')  # P-y-t-h-o-n-"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "A for loop is like a teacher taking attendance â€” they go through the class list name by name, calling each student once. range(5) is the class list with 5 students numbered 0 through 4. The teacher starts at the top, calls the first name, does something (like marking present), then moves to the next name. enumerate() is like the teacher also calling out the seat number: 'Seat 0, Alice! Seat 1, Bob!' A nested for loop is like the teacher going through every class in every grade â€” for each grade, they go through all students in that class. The for-else is like the teacher saying: 'If I get through the whole list without finding the missing student, announce it.'", "codeExample": "# Like a teacher checking each student\nstudents = ['Alice', 'Bob', 'Charlie']\nfor seat, name in enumerate(students):\n    print(f'Seat {seat}: {name} - Present!')\n\n# Seat 0: Alice - Present!\n# Seat 1: Bob - Present!\n# Seat 2: Charlie - Present!"},
                ],
                "quiz": [
                    {"id": "q1-1-1", "question": "What does 'for x in range(3)' produce?", "options": ["x = 1, 2, 3", "x = 0, 1, 2", "x = 0, 1, 2, 3", "x = 1, 2"], "correctAnswer": 1},
                    {"id": "q1-1-2", "question": "What does enumerate() return?", "options": ["Only values", "Only indices", "Tuples of (index, value)", "A dictionary"], "correctAnswer": 2},
                    {"id": "q1-1-3", "question": "Which can a for loop iterate over?", "options": ["Only lists", "Only numbers", "Any iterable (list, string, range, etc.)", "Only range objects"], "correctAnswer": 2},
                ],
                "recommendedVideos": [
                    {"id": "vid-1", "title": "Python For Loops Tutorial", "language": "Python", "youtubeId": "6iF8Xb7Z3wQ", "thumbnail": "https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg", "duration": "12:30"},
                ],
            },
            {
                "id": "sub-1-2", "name": "While Loop",
                "pdfUrl": "internal", "pdfTitle": "While Loop â€“ Complete Guide",
                "overview": "The while loop repeatedly executes a block of code as long as a given condition remains True. It is most useful when the number of iterations isn't known in advance â€” for example, reading user input until they type 'quit', or processing data until a file is empty. The condition is evaluated BEFORE each iteration, so if it starts as False, the body never runs. A common pattern is 'while True' with a break statement inside for input validation loops. Python's while loop also supports an optional else clause that runs when the condition becomes False naturally (not via break). Be careful to always update the condition variable inside the loop body â€” failing to do so creates an infinite loop that can freeze your program. While loops are essential for algorithms like binary search, game loops, and menu-driven programs.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "A while loop keeps running as long as its condition is True â€” it checks the condition before EACH round. Write 'while x < 5' and the loop runs as long as x is less than 5. Inside the loop, make sure to change x (like x += 1) or the loop runs forever! The 'while True' pattern with break inside is perfect for menus or input validation â€” keep asking until valid input is given. If the condition is False from the start, the body never runs at all. Python also allows 'while-else': the else block runs when the condition becomes False naturally, NOT when break exits the loop. Common uses include: counting down, waiting for user input, game loops, and processing queues.", "codeExample": "# Basic counting loop\nx = 0\nwhile x < 5:\n    print(x)  # prints 0, 1, 2, 3, 4\n    x += 1\n\n# Input validation pattern\nwhile True:\n    age = input('Enter your age: ')\n    if age.isdigit() and int(age) > 0:\n        break\n    print('Invalid! Try again.')\n\n# Countdown\nn = 5\nwhile n > 0:\n    print(n)\n    n -= 1\nprint('Liftoff!')"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "The while loop evaluates a boolean expression before each iteration. If True, the body executes and control returns to the condition check. If False, execution continues after the loop. An infinite loop occurs when the condition never becomes False â€” this is intentional in patterns like 'while True: ... break'. The else clause executes ONLY when the condition becomes False naturally, NOT when break exits the loop. Time complexity depends on the loop body and how fast the condition converges to False. While loops can simulate for loops: 'i = 0; while i < n: ...; i += 1' but for loops are preferred for iteration. Common algorithms using while loops: binary search O(log n), two-pointer technique O(n), and Newton's method for finding roots.", "codeExample": "# Binary search using while loop\ndef binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n\n# while-else\nn = 10\nwhile n > 0:\n    if n == 5:\n        break  # else won't run\n    n -= 1\nelse:\n    print('Finished normally')"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Step 1: Evaluate the condition (e.g., x < 5)\nStep 2: If True â†’ Execute the loop body â†’ Modify the variable â†’ Go to Step 1\nStep 3: If False â†’ Skip the loop body entirely â†’ Exit loop\nStep 4: If there's an else clause and no break was hit, run else block\n\nExample trace for x starting at 0:\nCheck: 0 < 3? YES â†’ print 0, x becomes 1\nCheck: 1 < 3? YES â†’ print 1, x becomes 2\nCheck: 2 < 3? YES â†’ print 2, x becomes 3\nCheck: 3 < 3? NO â†’ Exit loop", "codeExample": "# Step-by-step trace\nx = 0\nwhile x < 3:\n    print(f'x = {x}, condition {x} < 3 is True')\n    x += 1\nprint(f'x = {x}, condition {x} < 3 is False. Loop ends.')"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "A while loop is like eating chips from a bag â€” you keep eating WHILE there are chips remaining. Before each chip, you check: are there still chips? If yes, eat one. If no, stop. The condition is 'are there chips left?' and the body is 'eat one chip.' If someone gave you an empty bag, you'd never eat at all (condition is False from the start). An infinite loop is like a bottomless bag of chips â€” you never stop because the condition is always True. The break statement is like deciding 'I'm full' and stopping even though there are chips left.", "codeExample": "# Chips analogy in code\nchips = 5\nwhile chips > 0:\n    print(f'Eating chip! {chips} left')\n    chips -= 1\nprint('Bag is empty!')\n\n# Full before bag is empty (break)\nchips = 10\nfullness = 0\nwhile chips > 0:\n    chips -= 1\n    fullness += 1\n    if fullness >= 3:\n        print(\"I'm full!\")\n        break"},
                ],
                "quiz": [
                    {"id": "q1-2-1", "question": "When does a while loop stop?", "options": ["After a fixed number of iterations", "When the condition becomes False", "When it runs out of memory", "After 100 iterations"], "correctAnswer": 1},
                    {"id": "q1-2-2", "question": "What causes an infinite loop?", "options": ["Using break", "Condition never becomes False", "Using continue", "Too many variables"], "correctAnswer": 1},
                    {"id": "q1-2-3", "question": "What does 'while True: break' do?", "options": ["Runs forever", "Runs once then exits", "Causes an error", "Never runs"], "correctAnswer": 1},
                ],
                "recommendedVideos": [
                    {"id": "vid-2", "title": "While Loops in Python Explained", "language": "Python", "youtubeId": "HZARImviDxg", "thumbnail": "https://img.youtube.com/vi/HZARImviDxg/mqdefault.jpg", "duration": "8:45"},
                ],
            },
            {
                "id": "sub-1-3", "name": "Loop Control (break, continue, pass)",
                "pdfUrl": "internal", "pdfTitle": "Control Flow â€“ break, continue, pass",
                "overview": "Python provides three special statements to control loop execution: break, continue, and pass. The break statement immediately exits the innermost loop â€” useful when you've found what you're searching for and don't need to continue. The continue statement skips the rest of the current iteration and jumps to the next one â€” great for filtering out unwanted items. The pass statement is a null operation that does absolutely nothing â€” it serves as a placeholder where Python syntax requires a statement but you haven't written the code yet. In nested loops, break and continue only affect the innermost loop. Understanding these statements lets you write more efficient loops by avoiding unnecessary iterations and handling edge cases elegantly.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "These three keywords give you fine control over loops. break = STOP the loop completely and move on to the code after it. continue = SKIP this round and jump to the next iteration. pass = do NOTHING â€” it's just a placeholder. Use break when you found what you need and want to stop searching. Use continue to skip items you don't care about (like skipping even numbers). Use pass when you need an empty code block â€” Python requires at least one statement in every block, and pass fills that requirement. Remember: in nested loops, break only exits the INNER loop, not the outer one.", "codeExample": "# break â€” stop when found\nfor name in ['Alice', 'Bob', 'Charlie']:\n    if name == 'Bob':\n        print('Found Bob!')\n        break\n    print(f'Checking {name}...')\n# Output: Checking Alice... Found Bob!\n\n# continue â€” skip unwanted items\nfor i in range(10):\n    if i % 2 == 0:  # skip even numbers\n        continue\n    print(i)  # prints 1, 3, 5, 7, 9\n\n# pass â€” placeholder\nfor i in range(5):\n    pass  # TODO: implement later"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "break terminates the innermost enclosing for or while loop. When break is used, the loop's else clause (if any) is NOT executed. continue jumps to the next iteration â€” in a for loop it fetches the next item, in a while loop it re-evaluates the condition. pass is a null operation (NOP) â€” it exists because Python uses indentation for blocks and sometimes you need a syntactically valid but empty block (like a placeholder class or function). In nested loops, break only exits the innermost loop. To break from multiple nested loops, use a flag variable, encapsulate in a function with return, or use itertools. The performance impact: break can turn O(n) into O(1) in best case (early termination), continue adds negligible overhead.", "codeExample": "# break with else clause\nfor i in range(5):\n    if i == 3:\n        break\nelse:\n    print('This will NOT print because break was used')\n\n# continue in while loop\ni = 0\nwhile i < 10:\n    i += 1\n    if i % 3 == 0:\n        continue  # skip multiples of 3\n    print(i, end=' ')  # 1 2 4 5 7 8 10\n\n# pass as placeholder\nclass MyClass:\n    pass  # will implement later\n\ndef my_function():\n    pass  # will implement later"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "for i in range(10):\n    if i == 3: continue  â†’ skips 3 (jumps back to top)\n    if i == 7: break     â†’ stops at 7 (exits loop)\n    print(i)\n\nOutput: 0, 1, 2, 4, 5, 6\n\nVisualization:\ni=0 â†’ print 0 âœ“\ni=1 â†’ print 1 âœ“\ni=2 â†’ print 2 âœ“\ni=3 â†’ continue (skip!) â†©\ni=4 â†’ print 4 âœ“\ni=5 â†’ print 5 âœ“\ni=6 â†’ print 6 âœ“\ni=7 â†’ break (STOP!) âœ–", "codeExample": "# Combining break and continue\nfor i in range(10):\n    if i == 3:\n        continue  # skip 3\n    if i == 7:\n        break     # stop at 7\n    print(i, end=' ')\n# Output: 0 1 2 4 5 6"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "Imagine reading a book chapter by chapter. break is slamming the book shut mid-chapter â€” you're done reading entirely. continue is looking at a chapter title, deciding 'this one is boring,' and skipping to the next chapter without reading a single page. pass is opening a chapter that has blank pages â€” you don't do anything but you've still 'processed' it. In nested loops, it's like reading multiple books: break only closes the current book, not the whole bookshelf. Use break when searching (found it, no need to keep looking), continue for filtering (skip unwanted items), and pass for drafting (I'll fill this in later).", "codeExample": "# Searching with break (stop when found)\nbooks = ['Math', 'Science', 'History', 'Art']\nfor book in books:\n    if book == 'History':\n        print(f'Found {book}! Stop searching.')\n        break\n    print(f'Not {book}, keep looking...')\n# Not Math... Not Science... Found History!"},
                ],
                "quiz": [
                    {"id": "q1-3-1", "question": "What does 'break' do inside a loop?", "options": ["Skips current iteration", "Exits the loop entirely", "Pauses the loop", "Restarts the loop"], "correctAnswer": 1},
                    {"id": "q1-3-2", "question": "What does 'continue' do?", "options": ["Exits the loop", "Skips to the next iteration", "Stops the program", "Repeats current iteration"], "correctAnswer": 1},
                    {"id": "q1-3-3", "question": "When is 'pass' useful?", "options": ["To exit a loop", "As a placeholder where code is needed", "To skip iterations", "To handle errors"], "correctAnswer": 1},
                ],
                "recommendedVideos": [
                    {"id": "vid-1", "title": "Python For Loops Tutorial", "language": "Python", "youtubeId": "6iF8Xb7Z3wQ", "thumbnail": "https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg", "duration": "12:30"},
                ],
            },
        ],
    },
    {
        "id": "topic-2",
        "language": "Java",
        "topicName": "Java OOP Basics",
        "difficulty": "Intermediate",
        "overview": (
            "Object-Oriented Programming (OOP) is the cornerstone of Java development. It organizes code into "
            "reusable objects that combine data (fields) and behavior (methods). The four pillars â€” Encapsulation, "
            "Inheritance, Polymorphism, and Abstraction â€” enable you to build modular, maintainable, and scalable "
            "applications. Understanding these concepts is crucial for frameworks like Spring Boot and Android development."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Define a Class","detail":"Blueprint with fields and methods"},{"id":"p1","type":"process","label":"Encapsulation","detail":"Hide internal data with private/protected modifiers"},{"id":"p2","type":"process","label":"Create Object (new)","detail":"Instantiate class -> object in memory"},{"id":"d1","type":"decision","label":"Need specialization?","detail":"Does a child class extend the parent?","yes":"Use Inheritance (extends)","no":"Use base class directly"},{"id":"p3","type":"process","label":"Inheritance","detail":"Child class inherits fields & methods from parent"},{"id":"p4","type":"process","label":"Polymorphism","detail":"Same method name -> different behavior per subclass"},{"id":"p5","type":"process","label":"Abstraction","detail":"Hide complexity behind abstract classes & interfaces"},{"id":"e1","type":"end","label":"OOP Object Ready","detail":"Modular, reusable, maintainable code"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "A class is a template, an object is a thing made from that template. Encapsulation = keeping private stuff private. Inheritance = a child class gets everything from its parent. Polymorphism = same method name, different behavior. Abstraction = hiding complexity behind simple interfaces."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "OOP models real-world entities as objects with state (fields) and behavior (methods). Encapsulation enforces access control via private/protected/public modifiers. Inheritance establishes IS-A relationships through 'extends' keyword, promoting code reuse. Polymorphism enables method dispatch based on runtime type (dynamic binding). Abstraction uses abstract classes and interfaces to define contracts."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "OOP is like a restaurant: the Class is the recipe, the Object is the actual dish. Encapsulation is the kitchen â€” customers can't access it directly. Inheritance: a Margherita pizza inherits from the base Pizza recipe. Polymorphism: 'cook()' means different things for pasta vs steak. Abstraction: the menu hides all the kitchen complexity."},
        ],
        "quiz": [
            {"id": "q2-1", "question": "What is encapsulation in Java?", "options": ["Hiding internal data with access modifiers", "Creating multiple objects", "Extending a class", "Overriding methods"], "correctAnswer": 0},
            {"id": "q2-2", "question": "Which keyword is used for inheritance in Java?", "options": ["implements", "inherits", "extends", "super"], "correctAnswer": 2},
            {"id": "q2-3", "question": "What is polymorphism?", "options": ["Multiple inheritance", "Same method acting differently based on object", "Data hiding", "Creating interfaces"], "correctAnswer": 1},
            {"id": "q2-4", "question": "What does the 'new' keyword do?", "options": ["Defines a class", "Creates an object from a class", "Imports a package", "Declares a variable"], "correctAnswer": 1},
            {"id": "q2-5", "question": "Which is NOT a pillar of OOP?", "options": ["Encapsulation", "Compilation", "Inheritance", "Polymorphism"], "correctAnswer": 1},
        ],
        "recommendedVideos": [
            {"id": "vid-3", "title": "Java OOP Concepts Explained", "language": "Java", "youtubeId": "pTB0EiLXUC8", "thumbnail": "https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg", "duration": "18:20"},
        ],
        "subtopics": [
            {
                "id": "sub-2-1", "name": "Encapsulation",
                "pdfUrl": "internal", "pdfTitle": "Encapsulation in OOP",
                "overview": "Encapsulation is one of the four fundamental OOP pillars. It bundles data (fields) and the methods that operate on that data into a single class, while restricting direct access to internal state using access modifiers. In Java, you use private to hide fields, then provide public getter and setter methods for controlled access. This prevents external code from putting objects into invalid states â€” for example, a BankAccount class can validate that deposits are positive before modifying the balance. Encapsulation reduces coupling between classes, making your code easier to maintain and debug. It also allows you to change internal implementation without affecting code that uses the class.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "Encapsulation means hiding your data behind private fields and only allowing access through getter/setter methods. Think of it as putting your valuables in a safe â€” only you have the key (methods) to access them. In Java, you mark fields as 'private' so nobody can change them directly. Then you create public methods like getName() and setName() to control how the data is read and written. This way, you can add validation â€” for example, setAge() can check that the age is between 0 and 150 before allowing it. Without encapsulation, anyone could set age to -5 or 10000, causing bugs. It's one of the most important concepts in Java because every well-designed class uses it.", "codeExample": "public class Student {\n    private String name;   // hidden from outside\n    private int age;       // hidden from outside\n\n    // Getter â€” controlled read\n    public String getName() {\n        return name;\n    }\n\n    // Setter â€” controlled write with validation\n    public void setAge(int age) {\n        if (age > 0 && age < 150) {\n            this.age = age;\n        } else {\n            System.out.println(\"Invalid age!\");\n        }\n    }\n}"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "Encapsulation enforces information hiding via Java's access modifiers: private (accessible only within the class), protected (class + subclasses + same package), default/package-private (same package only), and public (accessible everywhere). Getters and setters provide a controlled interface â€” setters can include validation logic, and getters can return computed values or defensive copies. This maintains class invariants: conditions that must always be true (e.g., balance >= 0). Encapsulation reduces coupling: changes to internal representation don't propagate to dependent code. Java beans convention: private fields + public getters/setters. The 'this' keyword distinguishes instance variables from parameters when they share the same name.", "codeExample": "public class BankAccount {\n    private double balance;  // invariant: balance >= 0\n\n    public double getBalance() {\n        return balance;\n    }\n\n    public void deposit(double amount) {\n        if (amount > 0) {\n            balance += amount;  // validated write\n        }\n    }\n\n    public boolean withdraw(double amount) {\n        if (amount > 0 && amount <= balance) {\n            balance -= amount;\n            return true;  // success\n        }\n        return false;  // insufficient funds\n    }\n}"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "ACCESS MODIFIER VISIBILITY:\n\nprivate    â†’ Only within the same class\ndefault    â†’ Within the same package\nprotected  â†’ Same package + subclasses\npublic     â†’ Everywhere\n\nEncapsulation flow:\n1. Declare fields as private\n2. Create public getters (read access)\n3. Create public setters (write access + validation)\n4. External code uses methods, never fields directly\n5. Internal changes don't break external code", "codeExample": "// Without encapsulation (BAD)\nclass Student {\n    public int age;  // anyone can set age = -5!\n}\n\n// With encapsulation (GOOD)\nclass Student {\n    private int age;\n    public void setAge(int a) {\n        if (a > 0) this.age = a;\n    }\n    public int getAge() { return age; }\n}"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "Encapsulation is like an ATM machine. The money (data) is locked inside the vault (private fields). You can't reach in and grab cash directly. Instead, you use the ATM screen and buttons (public methods) to check your balance (getter) or withdraw money (setter with validation). The ATM validates your PIN and checks you have sufficient funds before giving you money. If the bank changes how they store money internally, you don't care â€” the ATM interface stays the same. This is exactly what encapsulation does: hides the messy internals and exposes a clean, safe interface.", "codeExample": "// ATM analogy in code\npublic class ATM {\n    private double vault;  // hidden money\n\n    public double checkBalance() {\n        return vault;  // safe read\n    }\n\n    public boolean withdraw(double amount) {\n        if (amount > 0 && amount <= vault) {\n            vault -= amount;\n            return true;\n        }\n        return false;  // ATM says: insufficient funds\n    }\n}"},
                ],
                "quiz": [
                    {"id": "q2-1-1", "question": "What is the main purpose of encapsulation?", "options": ["Code reuse", "Hiding internal data and providing controlled access", "Method overriding", "Creating objects"], "correctAnswer": 1},
                    {"id": "q2-1-2", "question": "Which access modifier restricts access to the class only?", "options": ["public", "protected", "private", "default"], "correctAnswer": 2},
                    {"id": "q2-1-3", "question": "What do getters and setters do?", "options": ["Create objects", "Provide controlled access to private fields", "Define constructors", "Handle exceptions"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-3", "title": "Java OOP Concepts Explained", "language": "Java", "youtubeId": "pTB0EiLXUC8", "thumbnail": "https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg", "duration": "18:20"}],
            },
            {
                "id": "sub-2-2", "name": "Inheritance",
                "pdfUrl": "internal", "pdfTitle": "Inheritance in OOP",
                "overview": "Inheritance allows a child class (subclass) to inherit fields and methods from a parent class (superclass) using the 'extends' keyword. This promotes code reuse and establishes IS-A relationships â€” a Dog IS-A Animal. The child class gets all non-private members of the parent and can add its own fields and methods. Java supports single inheritance for classes (one parent only) but allows multiple interface implementation. The super keyword calls the parent's constructor or methods. Method overriding lets the child provide its own version of an inherited method. Inheritance creates a class hierarchy that models real-world relationships naturally.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "Inheritance lets a child class get everything from its parent class. When you write 'class Dog extends Animal', Dog automatically gets all of Animal's fields and methods â€” plus it can add its own. Use super() in the constructor to call the parent's constructor first. If the parent has a method eat(), the Dog also has eat() without rewriting it. The child can also override methods â€” Dog can have its own version of makeSound() that barks instead of making a generic sound. Java only allows ONE parent class (single inheritance), but a class can implement multiple interfaces. This saves you from writing the same code over and over.", "codeExample": "class Animal {\n    String name;\n    \n    Animal(String name) {\n        this.name = name;\n    }\n    \n    void eat() {\n        System.out.println(name + \" is eating\");\n    }\n}\n\nclass Dog extends Animal {\n    String breed;\n    \n    Dog(String name, String breed) {\n        super(name);     // call parent constructor\n        this.breed = breed;\n    }\n    \n    void bark() {\n        System.out.println(name + \" says Woof!\");\n    }\n}\n\n// Dog inherits eat() and adds bark()\nDog d = new Dog(\"Rex\", \"Lab\");\nd.eat();   // inherited: Rex is eating\nd.bark();  // own method: Rex says Woof!"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "Inheritance creates an IS-A relationship â€” the subclass is a specialized version of the superclass. The child inherits all non-private members (fields, methods) from the parent. Java uses single inheritance for classes (only one 'extends') to avoid the Diamond Problem, but supports multiple interface inheritance ('implements'). Method resolution follows the class hierarchy upward: JVM checks the subclass first, then parent, then grandparent, up to Object. The super keyword explicitly accesses parent members. Constructor chaining: the first line of a child constructor must call super() (implicitly or explicitly). Access levels: private members are NOT inherited, but protected and public are.", "codeExample": "class Vehicle {\n    protected int speed;  // accessible by subclasses\n    \n    void accelerate() { speed += 10; }\n}\n\nclass Car extends Vehicle {\n    int numDoors;\n    \n    void turboBoost() {\n        speed += 50;  // can access protected field\n    }\n}\n\nclass ElectricCar extends Car {\n    int batteryLevel = 100;\n    \n    @Override\n    void accelerate() {\n        super.accelerate();  // call parent's version\n        batteryLevel -= 5;   // add own logic\n    }\n}\n// Hierarchy: Vehicle â†’ Car â†’ ElectricCar"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Class Hierarchy:\n\n       Animal (parent/superclass)\n       â”œâ”€â”€ name, eat()\n       â”‚\n   â”Œâ”€â”€â”€â”´â”€â”€â”€â”\n   Dog     Cat (children/subclasses)\n   bark()  purr()\n\nInheritance Rules:\n1. Child gets ALL non-private members of parent\n2. Child can ADD new fields and methods\n3. Child can OVERRIDE parent's methods\n4. super() calls parent constructor (must be first line)\n5. Java: ONE parent class only (single inheritance)", "codeExample": "// Demonstrating the hierarchy\nAnimal a = new Dog(\"Rex\", \"Lab\");\na.eat();     // âœ“ inherited from Animal\n// a.bark();  // âœ— compile error â€” Animal type doesn't know bark()\n\n// But the object IS a Dog, so casting works:\nDog d = (Dog) a;\nd.bark();    // âœ“ now we can call Dog methods"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "Inheritance is like family traits â€” a child inherits eye color, height, and abilities (fields/methods) from parents. But the child can also develop their own unique skills (new methods) and even do things differently than the parents (method overriding). A Margherita pizza inherits from the Pizza base class â€” it gets crust, sauce, and cheese (inherited fields) and adds its own basil topping (new field). Java's single inheritance is like having one biological parent you inherit from. Interfaces are like job certifications â€” you can have many, and they define what you CAN do without dictating HOW.", "codeExample": "// Family analogy\nclass Parent {\n    void cook() { System.out.println(\"Basic cooking\"); }\n}\n\nclass Child extends Parent {\n    @Override\n    void cook() {\n        super.cook();  // learned from parent\n        System.out.println(\"Plus gourmet skills!\");\n    }\n    void dance() { System.out.println(\"Own skill!\"); }\n}"},
                ],
                "quiz": [
                    {"id": "q2-2-1", "question": "Which keyword is used for inheritance in Java?", "options": ["implements", "inherits", "extends", "super"], "correctAnswer": 2},
                    {"id": "q2-2-2", "question": "What does the child class inherit?", "options": ["Only private members", "All non-private members", "Only constructors", "Nothing by default"], "correctAnswer": 1},
                    {"id": "q2-2-3", "question": "Does Java support multiple class inheritance?", "options": ["Yes", "No", "Only with abstract classes", "Only with final classes"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-3", "title": "Java OOP Concepts Explained", "language": "Java", "youtubeId": "pTB0EiLXUC8", "thumbnail": "https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg", "duration": "18:20"}],
            },
            {
                "id": "sub-2-3", "name": "Polymorphism",
                "pdfUrl": "internal", "pdfTitle": "Polymorphism in Computer Science",
                "overview": "Polymorphism means 'many forms' â€” the same method name can behave differently depending on the object calling it. Java supports two types: runtime polymorphism (method overriding) where the child class provides its own version of a parent method, and compile-time polymorphism (method overloading) where the same method name has different parameter lists. Runtime polymorphism is the more powerful concept â€” it enables you to write code that works with the parent type but automatically calls the correct child's method. This is the foundation of frameworks like Spring and design patterns like Strategy and Template Method.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "Polymorphism means one method name, different behaviors depending on the object. A Dog and Cat both have makeSound() but Dog barks and Cat meows â€” same method name, different implementation. Method overriding = child replaces parent's method with its own version. Method overloading = same name but different parameters (like add(int, int) and add(double, double)). The magic: you can use a parent-type variable to hold a child object, and calling a method uses the CHILD's version. This is called dynamic dispatch and it's incredibly powerful for writing flexible code.", "codeExample": "class Animal {\n    void sound() { System.out.println(\"...\"); }\n}\n\nclass Dog extends Animal {\n    @Override\n    void sound() { System.out.println(\"Woof!\"); }\n}\n\nclass Cat extends Animal {\n    @Override\n    void sound() { System.out.println(\"Meow!\"); }\n}\n\n// Polymorphism in action\nAnimal[] pets = { new Dog(), new Cat(), new Dog() };\nfor (Animal pet : pets) {\n    pet.sound();  // Woof! Meow! Woof!\n    // Java automatically calls the right version!\n}"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "Runtime polymorphism uses dynamic method dispatch â€” the JVM determines the actual method to call based on the object's runtime type (not the reference type). This enables programming to interfaces/abstractions. Compile-time polymorphism (overloading) resolves based on method signature (name + parameter types) at compile time. The @Override annotation is not required but catches errors â€” if you misspell the method name, the compiler warns you. Method resolution order: JVM checks the actual object's class first, then walks up the hierarchy. Polymorphism enables the Open/Closed Principle: classes are open for extension but closed for modification.", "codeExample": "// Runtime polymorphism (dynamic dispatch)\nAnimal a = new Dog();  // reference type: Animal, object type: Dog\na.sound();  // calls Dog's sound() â€” decided at RUNTIME\n\n// Compile-time polymorphism (overloading)\nclass Calculator {\n    int add(int a, int b) { return a + b; }\n    double add(double a, double b) { return a + b; }\n    String add(String a, String b) { return a + b; }\n}\n// Compiler decides which add() based on argument types"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Method Override Resolution:\n\nAnimal a = new Dog();\na.sound();  â†’  Which sound() runs?\n\nStep 1: Check the ACTUAL object type â†’ Dog\nStep 2: Does Dog have sound()? â†’ YES â†’ Call Dog.sound()\nStep 3: If NO â†’ Check parent (Animal) â†’ Call Animal.sound()\n\nOverloading Resolution (compile time):\nadd(5, 3)      â†’ matches add(int, int)\nadd(2.5, 1.5)  â†’ matches add(double, double)\nadd(\"Hi\", \"!\") â†’ matches add(String, String)", "codeExample": "// Polymorphism with arrays\nAnimal[] zoo = {\n    new Dog(),\n    new Cat(),\n    new Dog()\n};\n\nfor (Animal a : zoo) {\n    a.sound();  // Each calls its OWN version\n}\n// Output: Woof! Meow! Woof!"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "Polymorphism is like the word 'open' â€” 'open a door' means push/pull, 'open a book' means flip the cover, 'open a conversation' means start talking. Same action name, completely different behaviors depending on the object. In code, makeSound() means different things for a Dog vs Cat vs Bird. Another analogy: a remote control with a 'play' button works for TV (shows video), radio (plays music), and game console (starts game) â€” each device interprets 'play' in its own way. You (the programmer) just press 'play' without knowing the internal details.", "codeExample": "// Remote control analogy\ninterface Playable {\n    void play();\n}\n\nclass TV implements Playable {\n    public void play() { System.out.println(\"Playing video\"); }\n}\n\nclass Radio implements Playable {\n    public void play() { System.out.println(\"Playing music\"); }\n}\n\n// Same button, different behavior\nPlayable device = new TV();\ndevice.play();  // Playing video"},
                ],
                "quiz": [
                    {"id": "q2-3-1", "question": "What is runtime polymorphism?", "options": ["Method overloading", "Method overriding with dynamic dispatch", "Creating multiple objects", "Using interfaces only"], "correctAnswer": 1},
                    {"id": "q2-3-2", "question": "What is method overloading?", "options": ["Same name, different parameters", "Same name, same parameters", "Different name, same parameters", "Changing a parent method"], "correctAnswer": 0},
                    {"id": "q2-3-3", "question": "Which annotation verifies method overriding?", "options": ["@Override", "@Overload", "@Method", "@Inherit"], "correctAnswer": 0},
                ],
                "recommendedVideos": [{"id": "vid-3", "title": "Java OOP Concepts Explained", "language": "Java", "youtubeId": "pTB0EiLXUC8", "thumbnail": "https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg", "duration": "18:20"}],
            },
        ],
    },
    {
        "id": "topic-3",
        "language": "JavaScript",
        "topicName": "JavaScript Async/Await",
        "difficulty": "Intermediate",
        "overview": (
            "Asynchronous programming is at the heart of modern JavaScript. From fetching API data to reading files, "
            "async operations prevent your app from freezing while waiting for results. async/await â€” built on Promises â€” "
            "lets you write asynchronous code that reads like synchronous code. You'll learn about the event loop, "
            "Promises, try/catch error handling, and parallel execution with Promise.all()."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Call async function","detail":"Function returns a Promise immediately"},{"id":"p1","type":"process","label":"Encounter await","detail":"Pause this function, yield to event loop"},{"id":"p2","type":"io","label":"Web API / I/O Operation","detail":"Fetch data, read file, timer, etc."},{"id":"d1","type":"decision","label":"Promise settled?","detail":"Is the async operation complete?","yes":"Resume execution","no":"Event loop runs other tasks"},{"id":"p3","type":"process","label":"Resume after await","detail":"Value is unwrapped from resolved Promise"},{"id":"d2","type":"decision","label":"Error thrown?","detail":"Did the Promise reject?","yes":"Caught by try/catch","no":"Continue normally"},{"id":"e1","type":"end","label":"Return Result","detail":"Async function resolves its own Promise"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "async = this function will do something that takes time. await = wait here until that thing is done, but don't freeze everything else. A Promise is a 'I promise to give you data later.' try/catch handles when things go wrong. Promise.all() waits for multiple things at once."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "async functions return Promises implicitly. The await keyword pauses function execution until the Promise settles, yielding control back to the event loop. Under the hood, await uses microtask queue scheduling. Error handling wraps in try/catch blocks. Promise.all() enables concurrent execution with O(max(t1,t2,...tn)) time instead of sequential O(t1+t2+...+tn)."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "Think of async/await like ordering food delivery: calling the restaurant is the async call, tracking your order is the Promise, and 'await' is checking your door â€” you can do other things while waiting. Promise.all() is ordering from 3 restaurants at once and waiting for all deliveries."},
        ],
        "quiz": [
            {"id": "q3-1", "question": "What does the 'async' keyword do to a function?", "options": ["Makes it return a Promise", "Makes it run faster", "Makes it synchronous", "Prevents errors"], "correctAnswer": 0},
            {"id": "q3-2", "question": "Where can 'await' be used?", "options": ["Any function", "Global scope only", "Inside async functions", "Inside callbacks"], "correctAnswer": 2},
            {"id": "q3-3", "question": "What does Promise.all() do?", "options": ["Runs promises one by one", "Runs promises in parallel and waits for all", "Cancels all promises", "Returns the fastest promise"], "correctAnswer": 1},
            {"id": "q3-4", "question": "How do you handle errors with async/await?", "options": [".catch() method", "try/catch block", "if/else statement", "error callback"], "correctAnswer": 1},
            {"id": "q3-5", "question": "What is the event loop?", "options": ["A loop in your code", "A mechanism that handles async callbacks", "A debugging tool", "A type of Promise"], "correctAnswer": 1},
        ],
        "recommendedVideos": [
            {"id": "vid-4", "title": "JavaScript Async/Await Crash Course", "language": "JavaScript", "youtubeId": "V_Kr9OSfDeU", "thumbnail": "https://img.youtube.com/vi/V_Kr9OSfDeU/mqdefault.jpg", "duration": "22:15"},
            {"id": "vid-5", "title": "Promises vs Async/Await", "language": "JavaScript", "youtubeId": "li7FzDHYZpc", "thumbnail": "https://img.youtube.com/vi/li7FzDHYZpc/mqdefault.jpg", "duration": "14:10"},
        ],
        "subtopics": [
            {
                "id": "sub-3-1", "name": "Promises",
                "pdfUrl": "internal", "pdfTitle": "JavaScript Promises Guide",
                                                "overview": "A Promise represents a value that may be available now, or at some point in the future, or never at all. It is the foundation of modern asynchronous JavaScript, replacing older callback-based patterns that often led to deeply nested 'callback hell.' A Promise exists in one of three states: pending (initial state), fulfilled (the operation completed successfully), or rejected (the operation failed). Promises support chaining via .then(), .catch(), and .finally(), allowing you to build readable pipelines of async operations. Static combinators like Promise.all(), Promise.race(), Promise.allSettled(), and Promise.any() let you coordinate multiple concurrent async tasks efficiently. Understanding Promises is essential before learning async/await, since async/await is syntactic sugar built directly on top of the Promise API.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "A Promise is like ordering food at a counter â€” you get a receipt (the Promise) immediately, even though the food is not ready yet. The receipt starts in a 'pending' state; once the food is prepared it becomes 'fulfilled' (resolved), or the kitchen tells you the dish is unavailable (rejected). You handle these outcomes using .then() for success, .catch() for errors, and .finally() for cleanup that always runs. Promises can be chained: each .then() passes its return value to the next one, forming a neat pipeline. Promise.all() waits until every Promise in an array resolves (or one rejects). Promise.race() resolves or rejects as soon as the first Promise settles. Always attach a .catch() somewhere in the chain, otherwise rejected Promises will cause unhandled-rejection warnings.", "codeExample": "// Creating a Promise\nconst myPromise = new Promise((resolve, reject) => {\n    setTimeout(() => {\n        resolve('Data loaded!');\n    }, 2000);\n});\n\n// Consuming the Promise\nmyPromise\n    .then(data => console.log(data))   // 'Data loaded!'\n    .catch(err => console.error(err))\n    .finally(() => console.log('Done'));\n\n// Promise.all\nconst p1 = fetch('/api/users');\nconst p2 = fetch('/api/posts');\nPromise.all([p1, p2])\n    .then(([users, posts]) => console.log('Both loaded!'));"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "The Promise constructor accepts an executor function that receives two callbacks: resolve(value) and reject(reason). Once created, a Promise is in the pending state; calling resolve transitions it to fulfilled, while calling reject transitions it to rejected â€” both transitions are irreversible. The .then(onFulfilled, onRejected) method registers handlers and itself returns a new Promise, enabling chaining where each .then() receives the return value of the previous handler. The microtask queue ensures that .then() callbacks execute after the current call stack empties but before any macrotasks like setTimeout. Promise.all(iterable) short-circuits on the first rejection, while Promise.allSettled(iterable) waits for every promise regardless of outcome. Promise.race(iterable) settles as soon as the first promise settles, while Promise.any(iterable) resolves with the first fulfillment and only rejects if all promises reject with an AggregateError. Proper error propagation through the chain is critical: an uncaught rejection in any .then() will propagate down until a .catch() intercepts it.", "codeExample": "# Chaining transforms\nconst fetchData = new Promise((resolve, reject) => {\n    const success = true;\n    if (success) resolve({ id: 1, name: 'Alice' });\n    else reject(new Error('Fetch failed'));\n});\n\nfetchData\n    .then(data => data.name)              // 'Alice'\n    .then(name => name.toUpperCase())      // 'ALICE'\n    .then(upper => console.log(upper))     // logs ALICE\n    .catch(err => console.error(err.message));\n\n// Promise.allSettled\nPromise.allSettled([Promise.resolve(1), Promise.reject('err')])\n    .then(results => console.log(results));\n// [{status:'fulfilled',value:1}, {status:'rejected',reason:'err'}]"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Creating a Promise runs the executor function immediately and synchronously. Inside the executor you perform your async work, then call resolve(value) on success or reject(error) on failure. The Promise transitions from pending to either fulfilled or rejected â€” a one-way, irreversible transition. Attaching .then(callback) registers a handler that runs when the Promise fulfills, receiving the resolved value as its argument. .catch(callback) intercepts rejections at any point above it in the chain. .finally(callback) executes regardless of the outcome, making it ideal for spinner dismissal or resource cleanup. Because each .then() and .catch() returns a new Promise, you can build arbitrarily long sequential pipelines of asynchronous operations.", "codeExample": "# Full lifecycle\nconst loadUser = new Promise((resolve, reject) => {\n    console.log('1. Promise created (pending)');\n    setTimeout(() => {\n        console.log('2. Async work complete');\n        resolve({ name: 'Alice', age: 25 });\n    }, 1000);\n});\n\nloadUser\n    .then(user => {\n        console.log('3. Fulfilled:', user.name);\n        return user.age;\n    })\n    .then(age => console.log('4. Age:', age))\n    .catch(err => console.error('Error:', err))\n    .finally(() => console.log('5. Cleanup done'));"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "A Promise is like a restaurant buzzer you receive after placing an order. Initially the buzzer is in 'pending' state â€” your food is being prepared but is not ready yet. When the kitchen finishes your meal the buzzer lights up (fulfilled/resolved) and you go pick up your food (.then()). If the kitchen runs out of ingredients the buzzer flashes red (rejected) and a server tells you what went wrong (.catch()). Whether you get your food or not, you still return the buzzer (.finally()). Promise.all() is like ordering food for your entire table: everyone waits until ALL meals are ready before anyone eats. Promise.race() is like multiple delivery apps racing: you take whichever arrives first. Ignoring a flashing buzzer (unhandled rejection) means problems pile up silently.", "codeExample": "# Buzzer analogy in code\nfunction orderFood(dish) {\n    return new Promise((resolve, reject) => {\n        console.log(`Ordering: ${dish} (buzzer pending)`);\n        setTimeout(() => {\n            if (dish !== 'sold-out') {\n                resolve(`${dish} is ready!`);\n            } else {\n                reject(`${dish} is unavailable`);\n            }\n        }, 1500);\n    });\n}\n\norderFood('Pizza')\n    .then(msg => console.log('Pick up:', msg))\n    .catch(err => console.log('Oops:', err))\n    .finally(() => console.log('Return buzzer'));"},
                ],
                "quiz": [
                    {"id": "q3-1-1", "question": "What are the three states of a Promise?", "options": ["start, middle, end", "pending, fulfilled, rejected", "open, closed, error", "new, running, done"], "correctAnswer": 1},
                    {"id": "q3-1-2", "question": "What method handles a rejected Promise?", "options": [".then()", ".catch()", ".finally()", ".reject()"], "correctAnswer": 1},
                    {"id": "q3-1-3", "question": "What does Promise.all() do?", "options": ["Runs one promise", "Waits for all promises to resolve", "Cancels all promises", "Runs promises sequentially"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-5", "title": "Promises vs Async/Await", "language": "JavaScript", "youtubeId": "li7FzDHYZpc", "thumbnail": "https://img.youtube.com/vi/li7FzDHYZpc/mqdefault.jpg", "duration": "14:10"}],
            },
            {
                "id": "sub-3-2", "name": "Async/Await Syntax",
                "pdfUrl": "internal", "pdfTitle": "Async/Await â€“ Asynchronous Programming",
                                                "overview": "async/await is syntactic sugar built on top of Promises that lets you write asynchronous code that reads like synchronous code. The async keyword marks a function as asynchronous, causing it to implicitly return a Promise regardless of what you explicitly return. The await keyword can only be used inside async functions (or at the top level of ES modules) and pauses execution until the awaited Promise settles. Under the hood, the JavaScript engine uses the microtask queue to schedule the continuation after an await expression. async/await dramatically improves readability compared to raw Promise chains, especially when dealing with sequential async operations. It pairs naturally with try/catch for error handling, making async error flows as intuitive as synchronous ones.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "Putting 'async' before a function means it automatically returns a Promise, even if you just return a plain value. 'await' tells JavaScript to pause at that line until the Promise resolves, then gives you the resolved value. Without await, the Promise would just be an unresolved object you cannot use directly. You can await multiple things in sequence: each await waits for the previous step before continuing, just like synchronous code. If you need parallel execution, combine await with Promise.all() so multiple tasks run at the same time. One major benefit is readability: instead of .then().then().then() chains, each step is a simple line of code.", "codeExample": "// Basic async/await\nasync function getUser() {\n    const response = await fetch('/api/user');\n    const data = await response.json();\n    return data;  // automatically wrapped in Promise\n}\n\n// Calling an async function\ngetUser().then(user => console.log(user));\n\n// Parallel with Promise.all\nasync function loadDashboard() {\n    const [user, posts] = await Promise.all([\n        fetch('/api/user').then(r => r.json()),\n        fetch('/api/posts').then(r => r.json()),\n    ]);\n    console.log(user, posts);\n}"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "An async function wraps its return value in Promise.resolve(), making it thenable. When the engine encounters await expr, it evaluates expr (which should produce a Promise), then suspends the async function's execution frame and schedules its continuation as a microtask for when the Promise settles. This means code after an await only runs once the awaited Promise fulfills or rejects. If the Promise rejects and there is no surrounding try/catch, the async function's returned Promise also rejects. Top-level await (ES2022) allows await outside async functions in module contexts, simplifying initialisation scripts. Performance consideration: sequential awaits serialize execution; for independent operations, use Promise.all() to run them concurrently and reduce total latency.", "codeExample": "// Sequential vs parallel await\nasync function sequential() {\n    const a = await fetchA();  // waits ~1s\n    const b = await fetchB();  // waits ~1s after a\n    return a + b;              // total ~2s\n}\n\nasync function parallel() {\n    const [a, b] = await Promise.all([\n        fetchA(),  // starts immediately\n        fetchB(),  // starts immediately\n    ]);\n    return a + b;  // total ~1s (concurrent)\n}\n\n// async always returns a Promise\nasync function greet() { return 'Hello'; }\ngreet().then(msg => console.log(msg)); // 'Hello'"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Step 1: You mark the function with 'async' â†’ it now returns a Promise.\nStep 2: Inside the function, await <promise> pauses execution.\nStep 3: The engine saves the function's state and returns to the event loop.\nStep 4: When the Promise resolves, the engine restores the function and continues from the line after await.\nStep 5: If the Promise rejects and there is no try/catch, the error propagates as if thrown.\nStep 6: The value you return is wrapped in Promise.resolve() and sent to any .then() caller.\nThis pause-and-resume mechanism is what makes async code look linear while remaining non-blocking.", "codeExample": "# Visualising the pause + resume\nasync function demo() {\n    console.log('A - before await');\n    const val = await new Promise(r =>\n        setTimeout(() => r('done'), 1000)\n    );\n    console.log('B - after await:', val);\n}\n\ndemo();\nconsole.log('C - synchronous code');\n\n// Output order:\n// A - before await\n// C - synchronous code   (event loop continues)\n// B - after await: done   (resumes after 1s)"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "async/await is like ordering coffee through a mobile app at a busy cafe. You tap 'order' (call the async function), then you wait at the counter (await) while other customers keep ordering (event loop handles other tasks). When the barista calls your name, you resume your day with coffee in hand (the resolved value). If the machine breaks (Promise rejects), the barista tells you immediately (error is thrown at the await line). Sequential awaits are like ordering coffee, waiting for it, THEN ordering a muffin and waiting again. Promise.all() is like ordering coffee AND the muffin at the same time so both are prepared in parallel. The 'async' label on the function is like the cafe sign saying 'mobile orders accepted here.'", "codeExample": "# Coffee shop analogy\nasync function morningRoutine() {\n    // Sequential: order one, wait, then next\n    const coffee = await orderCoffee('latte');\n    const muffin = await orderFood('blueberry muffin');\n    console.log(`Got ${coffee} and ${muffin}`);\n\n    // Parallel: order both at once\n    const [tea, scone] = await Promise.all([\n        orderCoffee('green tea'),\n        orderFood('scone'),\n    ]);\n    console.log(`Also got ${tea} and ${scone}`);\n}"},
                ],
                "quiz": [
                    {"id": "q3-2-1", "question": "What does an async function always return?", "options": ["undefined", "A Promise", "null", "The result directly"], "correctAnswer": 1},
                    {"id": "q3-2-2", "question": "Where can await be used?", "options": ["Anywhere", "Only inside async functions", "Only in callbacks", "Only in global scope"], "correctAnswer": 1},
                    {"id": "q3-2-3", "question": "What happens when await encounters a resolved Promise?", "options": ["It throws an error", "It returns the resolved value immediately", "It creates a new Promise", "It skips it"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-4", "title": "JavaScript Async/Await Crash Course", "language": "JavaScript", "youtubeId": "V_Kr9OSfDeU", "thumbnail": "https://img.youtube.com/vi/V_Kr9OSfDeU/mqdefault.jpg", "duration": "22:15"}],
            },
            {
                "id": "sub-3-3", "name": "Error Handling (try/catch)",
                "pdfUrl": "internal", "pdfTitle": "Exception Handling Guide",
                                                "overview": "With async/await, errors are handled using familiar try/catch/finally blocks instead of .catch() chains. When an awaited Promise rejects, its rejection reason is thrown as an exception at the await line, allowing catch to intercept it. This makes error handling in async code nearly identical to synchronous error handling, improving readability and reducing bugs. For parallel operations, Promise.allSettled() lets you capture both fulfilled and rejected results without short-circuiting. Unhandled Promise rejections trigger the 'unhandledrejection' event in browsers and emit warnings in Node.js, so you should always handle errors. Combining try/catch with finally ensures cleanup logic (closing connections, hiding spinners) runs regardless of success or failure.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "Wrap your await calls in a try block; if the Promise rejects, the catch block runs automatically with the error object. This is much cleaner than chaining .catch() handlers on every Promise. The finally block runs no matter what, making it perfect for cleanup tasks like hiding loading spinners. You can catch specific error types by checking error.name or using instanceof inside the catch block. If you forget to add try/catch, an unhandled rejection can crash your Node.js app or show console warnings in the browser. For multiple parallel Promises, use Promise.allSettled() so that one failure does not prevent you from getting the other results.", "codeExample": "// Basic try/catch with async/await\nasync function fetchUser(id) {\n    try {\n        const res = await fetch(`/api/users/${id}`);\n        if (!res.ok) throw new Error(`HTTP ${res.status}`);\n        const user = await res.json();\n        return user;\n    } catch (error) {\n        console.error('Failed to fetch user:', error.message);\n        return null;\n    } finally {\n        console.log('Fetch attempt complete');\n    }\n}"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "When an awaited Promise rejects, the rejection value is thrown as an exception at the await site, entering the nearest enclosing catch block. The try/catch mechanism leverages the same exception-handling infrastructure as synchronous throws, so stack traces are preserved. A catch block in an async function can itself throw or return, propagating the error further or recovering gracefully. Promise.allSettled() returns an array of {status, value/reason} objects, ensuring no short-circuit on rejection. The 'unhandledrejection' event fires globally when a rejected Promise has no handler attached within a microtask turn. In Node.js versions 15+, unhandled rejections terminate the process by default, making proper error handling mandatory. Re-throwing errors from catch blocks is a common pattern: log the error locally then re-throw so callers can also react.", "codeExample": "// Handling multiple async errors\nasync function loadDashboard() {\n    try {\n        const [user, settings] = await Promise.all([\n            fetchUser(),\n            fetchSettings(),\n        ]);\n        render(user, settings);\n    } catch (err) {\n        // Promise.all rejects if ANY promise rejects\n        showError(err.message);\n    }\n}\n\n// allSettled: get all results regardless\nconst results = await Promise.allSettled([task1(), task2()]);\nconst succeeded = results.filter(r => r.status === 'fulfilled');\nconst failed    = results.filter(r => r.status === 'rejected');"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Step 1: Enter the try block and begin executing await statements sequentially.\nStep 2: If an awaited Promise fulfills, its value is returned and execution continues to the next line.\nStep 3: If an awaited Promise rejects, execution jumps immediately to the catch block with the rejection reason.\nStep 4: Inside catch, you can log the error, show a UI message, retry the operation, or re-throw.\nStep 5: The finally block runs after either try completes or catch completes, guaranteed.\nStep 6: If no try/catch wraps the await, the async function's returned Promise rejects, propagating the error to the caller.\nThis structured flow ensures every async error has a clear, predictable path through your code.", "codeExample": "// Error flow visualisation\nasync function riskyOperation() {\n    try {\n        console.log('1. Trying...');\n        const data = await failingAPI();\n        console.log('2. This line is SKIPPED');\n    } catch (err) {\n        console.log('3. Caught:', err.message);\n    } finally {\n        console.log('4. Finally always runs');\n    }\n}\n// Output: 1. Trying... -> 3. Caught: ... -> 4. Finally always runs"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "try/catch is like a safety net under a trapeze artist. You attempt the trick (try the await), and if you slip (the Promise rejects), the net catches you (catch block). Without the net, a fall is catastrophic â€” in code terms, an unhandled rejection can crash the app. The finally block is like the cleanup crew that comes out regardless of whether the trick succeeded or the artist fell. Promise.allSettled() is like a talent show judge watching every act to the end, scoring each one, rather than walking out after the first bad performance. Re-throwing an error from catch is like the safety net catching you, then reporting the fall to the show manager so they can decide whether to continue the show.", "codeExample": "// Safety net analogy\nasync function trapeze() {\n    try {\n        console.log('Attempting the trick...');\n        await riskyFlip();\n        console.log('Trick succeeded!');\n    } catch (err) {\n        console.log('Net caught you:', err.message);\n        // Re-throw to notify the manager\n        throw err;\n    } finally {\n        console.log('Cleanup crew on stage');\n    }\n}\n\n// The caller handles the rethrown error\ntrapeze().catch(e => console.log('Manager notified:', e.message));"},
                ],
                "quiz": [
                    {"id": "q3-3-1", "question": "How do you handle errors with async/await?", "options": [".catch() only", "try/catch block", "if/else", "error callback"], "correctAnswer": 1},
                    {"id": "q3-3-2", "question": "What happens to an unhandled Promise rejection?", "options": ["Nothing", "It silently succeeds", "It can crash the app or trigger a warning", "It retries automatically"], "correctAnswer": 2},
                    {"id": "q3-3-3", "question": "Which method captures results of all promises (resolved or rejected)?", "options": ["Promise.all()", "Promise.race()", "Promise.allSettled()", "Promise.any()"], "correctAnswer": 2},
                ],
                "recommendedVideos": [{"id": "vid-4", "title": "JavaScript Async/Await Crash Course", "language": "JavaScript", "youtubeId": "V_Kr9OSfDeU", "thumbnail": "https://img.youtube.com/vi/V_Kr9OSfDeU/mqdefault.jpg", "duration": "22:15"}],
            },
        ],
    },
    {
        "id": "topic-4",
        "language": "C",
        "topicName": "C Pointers & Memory",
        "difficulty": "Intermediate",
        "overview": (
            "Pointers are one of C's most powerful â€” and most confusing â€” features. A pointer stores the memory "
            "address of another variable, giving you direct access to memory. Understanding pointers is essential for "
            "dynamic memory allocation (malloc/free), arrays, strings, and data structures like linked lists and trees. "
            "You'll learn pointer arithmetic, dereferencing, pointer-to-pointer, and how to avoid common pitfalls "
            "like dangling pointers and memory leaks."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Declare pointer","detail":"int *ptr; -> pointer to an int"},{"id":"p1","type":"process","label":"Get address with &","detail":"ptr = &x; -> ptr holds the memory address of x"},{"id":"p2","type":"process","label":"Dereference with *","detail":"*ptr reads/writes value at that address"},{"id":"d1","type":"decision","label":"Need dynamic memory?","detail":"Is the size known at compile time?","yes":"Use malloc()","no":"Use stack variable"},{"id":"p3","type":"process","label":"malloc(n) -> allocate heap","detail":"Returns void* to n bytes of memory"},{"id":"p4","type":"process","label":"Use the memory","detail":"Read/write via pointer, pointer arithmetic"},{"id":"p5","type":"process","label":"free(ptr)","detail":"Release allocated memory back to OS"},{"id":"e1","type":"end","label":"Memory freed","detail":"Avoid leaks - always free what you malloc"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "A pointer holds an address, not a value. Use & to get an address, * to read what's at that address. int *p = &x means p points to x. *p gives you x's value. malloc gives you new memory, free gives it back. Always free what you malloc, or you leak memory."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "A pointer variable stores a memory address of type T*. The unary & (address-of) operator returns the lvalue address. The dereference operator * accesses the object located at the address stored in the pointer. sizeof(T*) is platform-dependent: 4 bytes on 32-bit architectures and 8 bytes on 64-bit architectures, regardless of T. Pointer assignment (p = &x) copies the address, not the value â€” both p and &x then refer to the same memory location. Dereferencing a NULL or uninitialised pointer invokes undefined behaviour, typically resulting in a segmentation fault. const correctness applies to pointers: 'const int *p' means the value cannot be changed through p, while 'int *const p' means p itself cannot be reassigned.", "codeExample": "int a = 10, b = 20;\nint *p = &a;       // p points to a\nint *q = &b;       // q points to b\n\nprintf(\"%zu\\n\", sizeof(p));  // 8 on 64-bit\n\n*p = *q;            // a is now 20 (value copy)\np  = q;             // p now points to b (address copy)\n\nconst int *cp = &a; // can read *cp, cannot write *cp\nint *const pc = &a; // can write *pc, cannot change pc\n// cp = &b;  OK     // *cp = 5;  ERROR\n// pc = &b;  ERROR  // *pc = 5;  OK"},
            {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
             "content": "A pointer is like your home address written on a business card. The card isn't your house â€” it just tells you where to find it. Giving someone the card (&) lets them visit. Reading what's at the address (*) is arriving at the house. malloc() is building a new house. free() is demolishing it. Forgetting to free is like abandoned buildings taking up space forever."},
        ],
        "quiz": [
            {"id": "q4-1", "question": "What does a pointer store?", "options": ["A value", "A memory address", "A function", "A data type"], "correctAnswer": 1},
            {"id": "q4-2", "question": "What does the '&' operator return?", "options": ["The value of a variable", "The address of a variable", "The size of a variable", "The type of a variable"], "correctAnswer": 1},
            {"id": "q4-3", "question": "What does ptr++ do if ptr is an int*?", "options": ["Adds 1 byte to address", "Adds sizeof(int) to address", "Increments the pointed value", "Causes an error"], "correctAnswer": 1},
            {"id": "q4-4", "question": "What function allocates memory dynamically?", "options": ["alloc()", "new()", "malloc()", "create()"], "correctAnswer": 2},
            {"id": "q4-5", "question": "What causes a memory leak?", "options": ["Using pointers", "Freeing memory twice", "Not freeing allocated memory", "Declaring too many variables"], "correctAnswer": 2},
        ],
        "recommendedVideos": [
            {"id": "vid-6", "title": "C Pointers Explained", "language": "C", "youtubeId": "zuegQmMdy8M", "thumbnail": "https://img.youtube.com/vi/zuegQmMdy8M/mqdefault.jpg", "duration": "15:45"},
        ],
        "subtopics": [
            {
                "id": "sub-4-1", "name": "Pointer Basics (& and *)",
                "pdfUrl": "internal", "pdfTitle": "Pointer Basics in C",
                "overview": "A pointer is a variable whose value is the memory address of another variable, giving you direct access to data stored in memory. In C, you declare a pointer with the * symbol (e.g., int *p) and obtain an address with the & (address-of) operator. Dereferencing a pointer with * lets you read or write the value stored at the address the pointer holds. Pointers are fundamental to C: they enable pass-by-reference, dynamic memory allocation, efficient array traversal, and the construction of data structures like linked lists and trees. The size of a pointer depends on the platform (typically 4 bytes on 32-bit systems and 8 bytes on 64-bit systems), regardless of the type it points to. A NULL pointer explicitly represents 'points to nothing' and should always be checked before dereferencing to avoid segmentation faults.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "A pointer holds a memory address, not a regular value like 42 or 'hello'. You create one with: int *p = &x; which means 'p stores the address of x'. Reading *p gives you the value stored at that address (if x is 42, *p is also 42). Writing *p = 100 changes the value at the address, which also changes x to 100 because they share the same memory location. Think of & as asking 'where do you live?' and * as 'what is at this address?' A NULL pointer means the pointer does not point anywhere yet; always check for NULL before using *p or your program will crash.", "codeExample": "int x = 42;\nint *p = &x;      // p holds the address of x\n\nprintf(\"%d\\n\", *p);   // 42 (dereference)\nprintf(\"%p\\n\", p);    // address like 0x1000\n\n*p = 100;              // changes x to 100\nprintf(\"%d\\n\", x);    // 100\n\nint *q = NULL;         // null pointer\n// *q would cause a segmentation fault!"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "A pointer of type T* stores the address of a variable of type T in memory. The unary & (address-of) operator returns the lvalue address. The unary * (dereference/indirection) operator accesses the object located at the address stored in the pointer. sizeof(T*) is platform-dependent: 4 bytes on 32-bit architectures and 8 bytes on 64-bit architectures, regardless of T. Pointer assignment (p = &x) copies the address, not the value â€” both p and &x then refer to the same memory location. Dereferencing a NULL or uninitialised pointer invokes undefined behaviour, typically resulting in a segmentation fault. const correctness applies to pointers: 'const int *p' means the value cannot be changed through p, while 'int *const p' means p itself cannot be reassigned.", "codeExample": "int a = 10, b = 20;\nint *p = &a;       // p points to a\nint *q = &b;       // q points to b\n\nprintf(\"%zu\\n\", sizeof(p));  // 8 on 64-bit\n\n*p = *q;            // a is now 20 (value copy)\np  = q;             // p now points to b (address copy)\n\nconst int *cp = &a; // can read *cp, cannot write *cp\nint *const pc = &a; // can write *pc, cannot change pc\n// cp = &b;  OK     // *cp = 5;  ERROR\n// pc = &b;  ERROR  // *pc = 5;  OK"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Memory diagram for int x = 42; int *p = &x;\n\nVariable | Address  | Value\n---------|----------|------\n   x     | 0x1000   |  42\n   p     | 0x1008   | 0x1000  (stores x's address)\n\nReading *p follows the arrow from p's value (0x1000) to x's location, yielding 42. Writing *p = 100 goes to address 0x1000 and overwrites the value there, so x becomes 100.", "codeExample": "// Visualising pointer relationships\nint x = 42;\nint *p = &x;\n\nprintf(\"x  value: %d\\n\", x);    // 42\nprintf(\"x  addr : %p\\n\", &x);   // 0x1000\nprintf(\"p  value: %p\\n\", p);     // 0x1000\nprintf(\"p  addr : %p\\n\", &p);    // 0x1008\nprintf(\"*p value: %d\\n\", *p);    // 42"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "A pointer is like a business card with a home address printed on it. The card itself is small and light, but the house it points to can be enormous. The & operator is like looking at a house and writing down its address. The * operator is like reading the address on the card and driving to that house to see what is inside. Copying a pointer (p = q) is like photocopying the business card: now two cards have the same address, so visiting either leads to the same house. A NULL pointer is like a blank business card with no address: if you try to visit, you will get lost (segfault). const pointers are like laminated cards you cannot overwrite.", "codeExample": "// Business card analogy\nint house = 42;            // the house has value 42\nint *card = &house;        // card stores house address\n\n// Read the card and visit\nprintf(\"Visit: %d\\n\", *card);  // 42\n\n// Safe lookup (drawer might not exist)\nprint(cabinet.get('recipes', 'Not filed'))  // 'Not filed'\n\n// Remove a drawer\ncabinet.pop('medical')\nprint(cabinet)  # {'taxes': '2024 return', 'id': 'passport'}"},
                ],
                "quiz": [
                    {"id": "q4-1-1", "question": "What does a pointer store?", "options": ["A value", "A memory address", "A data type", "A function"], "correctAnswer": 1},
                    {"id": "q4-1-2", "question": "What does &x return?", "options": ["Value of x", "Address of x", "Size of x", "Type of x"], "correctAnswer": 1},
                    {"id": "q4-1-3", "question": "What does *p do?", "options": ["Gets address of p", "Multiplies p", "Accesses value at address p points to", "Declares a pointer"], "correctAnswer": 2},
                ],
                "recommendedVideos": [{"id": "vid-6", "title": "C Pointers Explained", "language": "C", "youtubeId": "zuegQmMdy8M", "thumbnail": "https://img.youtube.com/vi/zuegQmMdy8M/mqdefault.jpg", "duration": "15:45"}],
            },
            {
                "id": "sub-4-2", "name": "Dynamic Memory (malloc/free)",
                "pdfUrl": "internal", "pdfTitle": "Dynamic Memory Allocation in C",
                "overview": "Dynamic memory allocation lets you request memory at runtime when the required size is not known at compile time. malloc(n) allocates n contiguous bytes on the heap and returns a void pointer to the start of the block. calloc(count, size) does the same but also initialises all bytes to zero, while realloc(ptr, new_size) resizes an existing allocation. When you are finished with the memory you MUST call free(ptr) to return it to the system; failing to do so creates a memory leak. Double-freeing (calling free on the same pointer twice) causes undefined behaviour and potential crashes. A best practice is to set the pointer to NULL immediately after freeing it, so that any accidental later dereference triggers a clean segfault rather than corrupting memory.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "When you declare int arr[5] the size is fixed at compile time. malloc(n) lets you ask for n bytes of memory while the program is running, so the size can come from user input or a calculation. It returns a pointer to the allocated block (or NULL if the system is out of memory). You use the pointer just like an array: arr[0], arr[1], etc. When you are done, call free(arr) to give the memory back. Forgetting free() is a memory leak: the program keeps eating more and more RAM. After freeing, set the pointer to NULL so you do not accidentally use it again.", "codeExample": "#include <stdlib.h>\n#include <stdio.h>\n\nint n = 5;\nint *arr = (int *)malloc(n * sizeof(int));\nif (arr == NULL) { printf(\"Out of memory!\\n\"); return 1; }\n\nfor (int i = 0; i < n; i++) arr[i] = i * 10;\nfor (int i = 0; i < n; i++) printf(\"%d \", arr[i]);\n// Output: 0 10 20 30 40\n\nfree(arr);\narr = NULL;  // avoid dangling pointer"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "malloc(size_t n) allocates n contiguous bytes from the heap and returns void*; it does NOT initialise the memory. calloc(size_t count, size_t size) allocates count*size bytes AND zeros them, which is safer for arrays of structs. realloc(void *ptr, size_t new_size) resizes a previously allocated block; it may move the block and returns the new address. free(void *ptr) marks the block as available for future allocations â€” the pointer itself is not modified. Double-free or freeing a non-malloc'd pointer causes undefined behaviour because the allocator's internal bookkeeping is corrupted. Memory leaks occur when allocated blocks become unreachable (the pointer is lost or overwritten without freeing first). Tools like Valgrind and AddressSanitizer detect leaks, double-frees, and out-of-bounds heap access at runtime.", "codeExample": "# calloc vs malloc\nint *a = (int *)malloc(5 * sizeof(int));  // uninitialised\nint *b = (int *)calloc(5, sizeof(int));    // all zeros\n\n// realloc to grow the array\na = (int *)realloc(a, 10 * sizeof(int));\nif (a == NULL) { /* handle failure */ }\n\n// Proper cleanup\nfree(a);  a = NULL;\nfree(b);  b = NULL;\n\n// Valgrind usage:\n// gcc -g main.c -o main\n// valgrind --leak-check=full ./main"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Heap memory lifecycle:\n\n1. malloc(20) -> OS reserves 20 bytes on the heap, returns pointer p\n2. p[0]=10, p[1]=20 -> you write data through the pointer\n3. realloc(p, 40) -> block grows (may move), returns new pointer\n4. free(p) -> memory returned to the OS/allocator\n5. p = NULL -> pointer no longer dangles\n\nIf you skip step 4, the 20 bytes are leaked for the lifetime of the process. If you perform step 4 twice, the heap metadata is corrupted and the program may crash unpredictably.", "codeExample": "// Step-by-step lifecycle\nint *p = (int *)malloc(5 * sizeof(int));  // step 1\nprintf(\"Allocated at: %p\\n\", p);\n\np[0] = 10; p[1] = 20;                     // step 2\n\np = (int *)realloc(p, 10 * sizeof(int));   // step 3\nprintf(\"Resized to: %p\\n\", p);\n\nfree(p);                                   // step 4\np = NULL;                                  // step 5"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "malloc() is like renting a storage unit â€” you ask the facility for a certain amount of space and they give you a key (pointer) to access it. You can put whatever you want inside and visit it whenever you need. realloc() is like requesting a bigger or smaller unit; the facility might move your stuff to a new unit and give you a new key. free() is returning the key and ending your rental. A memory leak is like moving out of town without cancelling your rental: the unit sits there locked and wasted. A double-free is like returning the key twice, confusing the front desk so badly they might give your unit to someone else while your stuff is still inside.", "codeExample": "// Storage unit analogy\nint *unit = (int *)malloc(3 * sizeof(int)); // rent 3 slots\nunit[0] = 100;  // store item in slot 0\nunit[1] = 200;  // store item in slot 1\nunit[2] = 300;  // store item in slot 2\n\n// Need more space? Upgrade the unit\nunit = (int *)realloc(unit, 6 * sizeof(int));\n\n// Done? Return the key\nfree(unit);\nunit = NULL;  // forget the old key"},
                ],
                "quiz": [
                    {"id": "q4-2-1", "question": "What does malloc() return?", "options": ["An integer", "A void pointer to allocated memory", "The size of memory", "An error code"], "correctAnswer": 1},
                    {"id": "q4-2-2", "question": "What causes a memory leak?", "options": ["Using free()", "Not freeing allocated memory", "Declaring variables", "Using pointers"], "correctAnswer": 1},
                    {"id": "q4-2-3", "question": "What does free(ptr) do?", "options": ["Deletes the pointer variable", "Releases the allocated memory", "Sets ptr to NULL", "Crashes the program"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-6", "title": "C Pointers Explained", "language": "C", "youtubeId": "zuegQmMdy8M", "thumbnail": "https://img.youtube.com/vi/zuegQmMdy8M/mqdefault.jpg", "duration": "15:45"}],
            },
            {
                "id": "sub-4-3", "name": "Pointer Arithmetic",
                "pdfUrl": "internal", "pdfTitle": "Pointer Arithmetic & Memory",
                "overview": "Pointer arithmetic allows you to navigate through blocks of memory by adding or subtracting integer offsets to pointers. When you add 1 to a pointer of type T*, the address advances by sizeof(T) bytes, not by 1 byte. This is the mechanism that makes array indexing work: arr[i] is defined as *(arr + i), and the compiler automatically scales the offset by the element size. Subtracting two pointers of the same type yields the number of elements between them (ptrdiff_t). Pointer comparisons (<, >, <=, >=, ==) are valid when both pointers point into the same array or one past its end. Understanding pointer arithmetic is essential for writing efficient low-level code, implementing custom memory pools, and debugging memory-related issues.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“",
                     "content": "When you do ptr + 1, the address moves forward by the size of the data type, not by 1 byte. For an int pointer (4 bytes per int), ptr + 1 jumps forward 4 bytes to the next integer. For a char pointer (1 byte per char), ptr + 1 jumps forward just 1 byte. This means you can walk through an array using a pointer: *ptr is the first element, *(ptr+1) is the second, and so on. In fact, arr[i] and *(arr + i) are exactly the same thing in C. You can also subtract two pointers to find how many elements are between them.", "codeExample": "int arr[] = {10, 20, 30, 40, 50};\nint *p = arr;  // points to arr[0]\n\nprintf(\"%d\\n\", *p);       // 10  (arr[0])\nprintf(\"%d\\n\", *(p+1));   // 20  (arr[1])\nprintf(\"%d\\n\", *(p+3));   // 40  (arr[3])\n\n// arr[i] == *(arr + i)\nprintf(\"%d\\n\", arr[2]);   // 30\nprintf(\"%d\\n\", *(arr+2)); // 30  (same thing)\n\n// Pointer subtraction\nint *q = &arr[4];\nprintf(\"%td\\n\", q - p);   // 4 elements apart"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ",
                     "content": "For a pointer of type T*, the expression ptr + n computes the address ptr + n * sizeof(T) at the machine level. This scaling is inserted automatically by the compiler and ensures type-safe traversal of arrays. Subtraction of two pointers of the same type produces a ptrdiff_t value representing the number of elements (not bytes) between them. Pointer comparison operators (<, >, ==) are defined for pointers within the same array object or one element past its end; comparisons between unrelated pointers are undefined behaviour. The equivalence arr[i] == *(arr + i) is a language-level definition in the C standard, not merely an optimisation. Incrementing a void* is not allowed by the standard (since sizeof(void) is undefined), although some compilers permit it as an extension with 1-byte steps. Pointer arithmetic combined with casting allows low-level byte manipulation, which is critical for network protocols and binary file parsing.", "codeExample": "int arr[] = {1, 2, 3, 4, 5};\nint *p = arr;\n\n// Compiler scales: p+2 => address + 2*sizeof(int)\nprintf(\"addr p  : %p\\n\", p);\nprintf(\"addr p+2: %p\\n\", p + 2);\nprintf(\"diff    : %td bytes\\n\",\n       (char*)(p+2) - (char*)p);  // 8 bytes\n\n// ptrdiff_t\nint *end = &arr[5];  // one past last\nptrdiff_t count = end - p;  // 5 elements\nprintf(\"elements: %td\\n\", count);"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨",
                     "content": "Memory layout for int arr[] = {10, 20, 30, 40};\n(assuming sizeof(int) = 4 and arr starts at address 0x100)\n\nAddress:  0x100  0x104  0x108  0x10C\nValue:    [ 10 ] [ 20 ] [ 30 ] [ 40 ]\nIndex:     [0]    [1]    [2]    [3]\n\np = arr      -> p is 0x100, *p is 10\np + 1        -> 0x104 (moved 4 bytes), *(p+1) is 20\np + 3        -> 0x10C (moved 12 bytes), *(p+3) is 40\nThe jump size equals sizeof(int) = 4 bytes per step.", "codeExample": "# Walking through an array with pointer increment\nint arr[] = {10, 20, 30, 40};\nint *p = arr;\n\nfor (int i = 0; i < 4; i++) {\n    printf(\"arr[%d] at %p = %d\\n\", i, p, *p);\n    p++;  // moves sizeof(int) bytes forward\n}"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—",
                     "content": "Pointer arithmetic is like walking through a train where each carriage has a fixed size. Stepping forward by 1 (ptr + 1) moves you to the next carriage, not just one foot forward. The carriage size depends on the data type: int carriages are 4 bytes wide, char carriages are 1 byte, double carriages are 8 bytes. arr[i] is like saying 'go to carriage number i directly,' while *(arr + i) is like 'start at the front and walk i carriages.' Subtracting two pointers tells you how many carriages apart two passengers are sitting. You should only do arithmetic within the same train (same array); jumping to a different train (different memory block) gives unpredictable results.", "codeExample": "# Train carriage analogy\nint train[] = {100, 200, 300, 400, 500};\nint *passenger = train;  // start at carriage 0\n\n// Walk two carriages forward\npassenger += 2;\nprintf(\"Carriage 2: %d\\n\", *passenger);  // 300\n\n// How far apart?\nint *other = &train[4];\nprintf(\"%td carriages apart\\n\", other - passenger);  // 2"},
                ],
                "quiz": [
                    {"id": "q4-3-1", "question": "If p is int* and sizeof(int)=4, what does p+1 do?", "options": ["Adds 1 byte", "Adds 4 bytes to address", "Adds 1 to the value", "Causes an error"], "correctAnswer": 1},
                    {"id": "q4-3-2", "question": "What is arr[2] equivalent to?", "options": ["arr + 2", "*(arr + 2)", "&arr[2]", "arr * 2"], "correctAnswer": 1},
                    {"id": "q4-3-3", "question": "Can you subtract two pointers?", "options": ["No, never", "Yes, it gives the number of elements between them", "Yes, it gives bytes between them", "Only for char pointers"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-6", "title": "C Pointers Explained", "language": "C", "youtubeId": "zuegQmMdy8M", "thumbnail": "https://img.youtube.com/vi/zuegQmMdy8M/mqdefault.jpg", "duration": "15:45"}],
            },
        ],
    },
    {
        "id": "topic-5",
        "language": "Python",
        "topicName": "Python Data Structures",
        "difficulty": "Beginner",
        "overview": (
            "Python offers powerful built-in data structures: lists, tuples, dictionaries, and sets. Each has "
            "unique characteristics â€” lists are ordered and mutable, tuples are ordered and immutable, dicts map "
            "keys to values, and sets store unique elements. Choosing the right data structure dramatically impacts "
            "performance and code clarity. You'll learn creation, manipulation, common methods, comprehensions, "
            "and when to use each type."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Choose a Data Structure","detail":"What kind of collection do you need?"},{"id":"d1","type":"decision","label":"Need key-value pairs?","detail":"Map keys to values?","yes":"Use dict {}","no":"Continue below"},{"id":"d2","type":"decision","label":"Need unique items only?","detail":"No duplicates allowed?","yes":"Use set {}","no":"Continue below"},{"id":"d3","type":"decision","label":"Need to modify later?","detail":"Will you add/remove items?","yes":"Use list []","no":"Use tuple ()"},{"id":"p1","type":"process","label":"list -> ordered, mutable","detail":"[1,2,3] - append, insert, remove, sort"},{"id":"p2","type":"process","label":"tuple -> ordered, immutable","detail":"(1,2,3) - fixed once created, hashable"},{"id":"p3","type":"process","label":"dict -> O(1) lookup by key","detail":"Fast access, no duplicate keys"},{"id":"e1","type":"end","label":"Data Structure Selected","detail":"Choose based on mutability, ordering, and uniqueness"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "List [1,2,3] â€” ordered, changeable, allows duplicates. Tuple (1,2,3) â€” ordered, NOT changeable. Dict {'a':1} â€” key-value pairs, fast lookup. Set {1,2,3} â€” unique items only, no order. Use list for collections, dict for mappings, set for uniqueness, tuple for fixed data."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "Lists implement dynamic arrays with O(1) append and O(n) insert. Tuples are immutable sequences (hashable if elements are hashable). Dicts use hash tables: O(1) average for get/set/delete. Sets use hash tables without values: O(1) membership testing, support union/intersection/difference operations. List comprehensions [x for x in ...] create lists declaratively."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "Data structures are like containers: a list is a train with ordered carriages you can rearrange, a tuple is a sealed package (fixed once packed), a dict is a filing cabinet (labeled drawers for quick access), a set is a cookie cutter collection (each shape unique, order doesn't matter)."},
        ],
        "quiz": [
            {"id": "q5-1", "question": "Which Python data structure is ordered and mutable?", "options": ["Tuple", "Set", "List", "Dict"], "correctAnswer": 2},
            {"id": "q5-2", "question": "What makes a set different from a list?", "options": ["Sets are ordered", "Sets allow duplicates", "Sets contain only unique elements", "Sets are immutable"], "correctAnswer": 2},
            {"id": "q5-3", "question": "How do you access a dict value?", "options": ["dict[index]", "dict.key", "dict[key]", "dict.get_value()"], "correctAnswer": 2},
            {"id": "q5-4", "question": "Which is immutable?", "options": ["List", "Dict", "Set", "Tuple"], "correctAnswer": 3},
            {"id": "q5-5", "question": "What is a list comprehension?", "options": ["A way to understand lists", "A compact syntax to create lists", "A method to sort lists", "A list documentation tool"], "correctAnswer": 1},
        ],
        "recommendedVideos": [
            {"id": "vid-7", "title": "Python Data Structures Full Course", "language": "Python", "youtubeId": "8hly31xKli0", "thumbnail": "https://img.youtube.com/vi/8hly31xKli0/mqdefault.jpg", "duration": "25:00"},
        ],
        "subtopics": [
            {
                "id": "sub-5-1", "name": "Lists",
                "pdfUrl": "internal", "pdfTitle": "Python Lists â€“ Complete Guide",
                "overview": "Lists are Python's most versatile built-in data structure: ordered, mutable sequences that can hold items of any type. You create a list with square brackets ([1, 2, 3]) or the list() constructor, and access elements by zero-based index. Lists support slicing (lst[1:4]), concatenation (+), repetition (*), and in-place mutation through methods like append(), insert(), remove(), and sort(). Under the hood, CPython implements lists as dynamic arrays that automatically resize when capacity is exceeded, giving O(1) amortised append but O(n) insert at arbitrary positions. List comprehensions ([expr for x in iterable if cond]) offer a concise, readable, and often faster way to build new lists from existing iterables. Because lists are mutable and ordered, they are the go-to choice for most collection-oriented tasks in Python.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "A list is like an ordered shopping list: each item has a position starting from 0. You can add items at the end with append(), insert them at a specific position with insert(), and remove them with remove() or pop(). Access any item by its index: my_list[0] is the first item, my_list[-1] is the last. Slicing lets you grab a range: my_list[1:4] gives items at positions 1, 2, and 3. Lists can hold mixed types: [1, 'hello', True, 3.14] is perfectly valid. List comprehensions let you create new lists in one line: [x*2 for x in range(5)] gives [0, 2, 4, 6, 8].", "codeExample": "# Creating and modifying lists\nfruits = ['apple', 'banana', 'cherry']\nfruits.append('date')       # ['apple','banana','cherry','date']\nfruits.insert(1, 'avocado') # insert at index 1\nfruits.remove('banana')     # remove by value\nlast = fruits.pop()         # remove & return last item\n\n# Indexing and slicing\nprint(fruits[0])    # 'apple'\nprint(fruits[-1])   # 'cherry'\nprint(fruits[1:3])  # ['avocado', 'cherry']\n\n# List comprehension\nsquares = [x**2 for x in range(6)]\nprint(squares)  # [0, 1, 4, 9, 16, 25]"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "Python lists are implemented as dynamic arrays (over-allocated contiguous memory blocks) in CPython. Appending is amortised O(1) because the internal array is grown by a factor when full, typically ~1.125x. Indexing (lst[i]) is O(1) direct memory offset. Insertion and deletion at arbitrary positions are O(n) because subsequent elements must be shifted. The 'in' operator performs a linear O(n) scan; for frequent membership tests, use a set instead. List comprehensions compile to faster bytecode than equivalent for-loop-with-append patterns because they avoid repeated method lookups. Nested lists create references, not copies: lst2 = [lst1] means modifying lst1 also affects lst2 unless you use copy.deepcopy().", "codeExample": "import sys\n\n# Dynamic array resizing\nlst = []\nfor i in range(20):\n    lst.append(i)\n    print(f'len={len(lst):2d}  size={sys.getsizeof(lst)} bytes')\n\n# O(1) append vs O(n) insert\nlst.append(99)       # fast: add to end\nlst.insert(0, -1)    # slow: shift everything right\n\n# Shallow vs deep copy\nimport copy\na = [[1, 2], [3, 4]]\nb = copy.deepcopy(a)  # independent copy\na[0][0] = 99\nprint(b[0][0])  # still 1"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "List in memory (conceptual):\n\nIndex:   [  0  ] [  1  ] [  2  ] [  3  ]\nValue:   ['apple','banana','cherry','date']\n\nappend('elderberry') -> adds at index 4 (fast, O(1))\ninsert(1, 'avocado') -> shifts indices 1-4 right (slow, O(n))\npop() -> removes last element (fast, O(1))\npop(0) -> removes first, shifts everything left (slow, O(n))\n\nSlicing creates a NEW list: fruits[1:3] copies indices 1 and 2."},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "A list is like a train with numbered carriages. Each carriage (index) can hold a different type of cargo: numbers, strings, even other trains (nested lists). Appending is like coupling a new carriage at the end, which is quick. Inserting in the middle is like adding a carriage between existing ones: every carriage behind it must shuffle back, which takes more work. Slicing is like detaching a section of carriages to form a brand-new mini-train. A list comprehension is like an automated factory that builds a new train by processing each item on a conveyor belt in one pass.", "codeExample": "# Train analogy\ntrain = ['coal', 'wood', 'steel']  # 3 carriages\n\n# Couple a new carriage at the end (fast)\ntrain.append('gold')\nprint(train)  # ['coal','wood','steel','gold']\n\n# Insert a carriage in the middle (slower)\ntrain.insert(1, 'iron')\nprint(train)  # ['coal','iron','wood','steel','gold']\n\n# Detach a section (slice)\nsection = train[1:3]\nprint(section)  # ['iron', 'wood']"},
                ],
                "quiz": [
                    {"id": "q5-1-1", "question": "Are lists mutable?", "options": ["No", "Yes", "Only sometimes", "Only with numbers"], "correctAnswer": 1},
                    {"id": "q5-1-2", "question": "What does list.append(x) do?", "options": ["Adds x at the beginning", "Adds x at the end", "Replaces the first element", "Sorts the list"], "correctAnswer": 1},
                    {"id": "q5-1-3", "question": "What is the time complexity of list[i]?", "options": ["O(n)", "O(log n)", "O(1)", "O(nÂ²)"], "correctAnswer": 2},
                ],
                "recommendedVideos": [{"id": "vid-7", "title": "Python Data Structures Full Course", "language": "Python", "youtubeId": "8hly31xKli0", "thumbnail": "https://img.youtube.com/vi/8hly31xKli0/mqdefault.jpg", "duration": "25:00"}],
            },
            {
                "id": "sub-5-2", "name": "Dictionaries",
                "pdfUrl": "internal", "pdfTitle": "Python Dictionaries Guide",
                "overview": "Dictionaries are Python's built-in hash-table implementation, mapping unique immutable keys to arbitrary values with O(1) average-case lookup, insertion, and deletion. You create a dict with curly braces ({'key': 'value'}) or the dict() constructor, and access values using bracket notation or the safer .get() method. Since Python 3.7, dictionaries officially maintain insertion order, so iterating over a dict always yields keys in the order they were added. Keys must be hashable (immutable types like str, int, tuple), while values can be any Python object including other dicts or lists. Dict comprehensions ({k: v for k, v in iterable}) provide a concise way to build or transform dictionaries from data. Common patterns include using .setdefault() for initialising missing keys and collections.defaultdict for automatic default values.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "A dictionary maps keys to values, like a real-world dictionary maps words to definitions. Create one with {'name': 'Alice', 'age': '25'}, then access values with dict['name'] (returns 'Alice'). Use .get('key', default) for safe access: it returns the default instead of raising a KeyError if the key is missing. Add or update entries with dict['new_key'] = value. Remove entries with del dict['key'] or dict.pop('key'). Loop over keys with for k in dict, over values with for v in dict.values(), or over both with for k, v in dict.items(). Dict comprehensions let you build dicts in one line: {x: x**2 for x in range(5)}.", "codeExample": "# Creating and using a dictionary\nstudent = {'name': 'Alice', 'grade': 'A', 'age': 20}\n\nprint(student['name'])           # 'Alice'\nprint(student.get('gpa', 'N/A')) # 'N/A' (safe access)\n\nstudent['gpa'] = 3.9             # add new key\ndel student['grade']             # remove key\n\n# Looping\nfor key, val in student.items():\n    print(f'{key}: {val}')\n\n# Dict comprehension\nsquares = {x: x**2 for x in range(6)}\nprint(squares)  # {0:0, 1:1, 2:4, 3:9, 4:16, 5:25}"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "CPython dicts use a compact hash table with open addressing and a perturbation-based probing scheme to resolve collisions. Average-case time complexity is O(1) for get, set, and delete; worst case is O(n) when many collisions occur (extremely rare with a good hash function). Keys must implement __hash__() and __eq__(); built-in immutable types (str, int, float, tuple of immutables) satisfy this. Since Python 3.7, dicts are guaranteed to maintain insertion order as a language specification, not merely an implementation detail. .setdefault(key, default) returns the value if key exists, otherwise inserts key with default and returns it. collections.defaultdict(factory) auto-creates missing keys using the factory function (e.g., list, int, set). Dict comprehension {k: v for k, v in pairs} is O(n) and is syntactic sugar for a loop with assignment.", "codeExample": "from collections import defaultdict\n\n# O(1) operations\nd = {'a': 1, 'b': 2}\nd['c'] = 3           # O(1) insert\nval = d['a']         # O(1) lookup\ndel d['b']           # O(1) delete\n\n# setdefault\nd.setdefault('d', 0) # inserts 'd':0 if missing\n\n# defaultdict\ngroups = defaultdict(list)\nfor word in ['cat', 'car', 'bat', 'bar']:\n    groups[word[0]].append(word)\nprint(dict(groups))  # {'c':['cat','car'], 'b':['bat','bar']}\n\n# Merge dicts (Python 3.9+)\nmerged = {'x': 1} | {'y': 2}  # {'x':1, 'y':2}"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "Hash table structure (simplified):\n\nKey     -> hash() -> bucket index -> Value\n'name'  -> 384732 ->     3        -> 'Alice'\n'age'   -> 291054 ->     7        -> 25\n'grade' -> 573921 ->     1        -> 'A'\n\nWhen you access dict['name'], Python hashes 'name', finds bucket 3, and returns 'Alice' in O(1).\nCollision: if two keys hash to the same bucket, Python probes the next available slot. Iteration follows insertion order thanks to a compact internal array."},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "A dictionary is like a filing cabinet with labelled drawers. Each drawer (key) has a unique label, and inside is whatever you filed (value). Finding a file is instant: you read the label, open the drawer. You cannot have two drawers with the same label (keys are unique). Adding a file means labelling a new drawer and putting the document inside. Removing means pulling the drawer out entirely (del or .pop()). A defaultdict is like a magic cabinet that auto-creates empty drawers whenever you try to open one that does not exist yet.", "codeExample": "# Filing cabinet analogy\ncabinet = {}  # empty cabinet\n\n# File some documents\ncabinet['taxes'] = '2024 return'\ncabinet['medical'] = 'insurance card'\ncabinet['id'] = 'passport'\n\n# Find a document instantly\nprint(cabinet['taxes'])  # '2024 return'\n\n# Safe lookup (drawer might not exist)\nprint(cabinet.get('recipes', 'Not filed'))  # 'Not filed'\n\n# Remove a drawer\ncabinet.pop('medical')\nprint(cabinet)  # {'taxes': '2024 return', 'id': 'passport'}"},
                ],
                "quiz": [
                    {"id": "q5-2-1", "question": "What is the average lookup time for a dictionary?", "options": ["O(n)", "O(log n)", "O(1)", "O(nÂ²)"], "correctAnswer": 2},
                    {"id": "q5-2-2", "question": "Can dictionary keys be duplicated?", "options": ["Yes", "No", "Only strings", "Only numbers"], "correctAnswer": 1},
                    {"id": "q5-2-3", "question": "What does dict.get('key', default) do?", "options": ["Always raises an error", "Returns value or default if key missing", "Deletes the key", "Creates a new dict"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-7", "title": "Python Data Structures Full Course", "language": "Python", "youtubeId": "8hly31xKli0", "thumbnail": "https://img.youtube.com/vi/8hly31xKli0/mqdefault.jpg", "duration": "25:00"}],
            },
            {
                "id": "sub-5-3", "name": "Sets",
                "pdfUrl": "internal", "pdfTitle": "Python Sets â€“ Complete Guide",
                "overview": "Sets are unordered collections of unique, hashable elements, backed by hash tables for O(1) average-case membership testing. You create a set with curly braces ({1, 2, 3}) or the set() constructor; duplicates are automatically discarded. Sets support classical mathematical operations: union (|), intersection (&), difference (-), and symmetric difference (^). Because elements must be hashable, you can store strings, numbers, and tuples in a set, but not lists or dictionaries. frozenset is the immutable variant of set, which CAN be used as a dictionary key or as an element of another set. Common use cases include removing duplicates from a list, fast membership checks, and computing overlaps between collections.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "A set is a bag of unique items with no particular order. If you add the same item twice, the set just keeps one copy: {1, 2, 2, 3} becomes {1, 2, 3}. Checking 'is this item in the set?' is extremely fast, much faster than scanning a list. Union (|) combines two sets: {1,2} | {2,3} gives {1,2,3}. Intersection (&) keeps only shared items: {1,2,3} & {2,3,4} gives {2,3}. Difference (-) removes items found in the other set: {1,2,3} - {2} gives {1,3}. Use set() to convert a list to a set when you need to remove duplicates quickly.", "codeExample": "# Creating sets\ncolors = {'red', 'green', 'blue', 'red'}  # duplicate removed\nprint(colors)  # {'red', 'green', 'blue'}\n\n# Set operations\na = {1, 2, 3, 4}\nb = {3, 4, 5, 6}\nprint(a | b)   # {1,2,3,4,5,6}  union\nprint(a & b)   # {3,4}           intersection\nprint(a - b)   # {1,2}           difference\nprint(a ^ b)   # {1,2,5,6}       symmetric diff\n\n# Remove duplicates from a list\nnums = [1, 3, 3, 7, 7, 7]\nunique = list(set(nums))  # [1, 3, 7]"},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "Sets are implemented as hash tables with keys but no values, giving O(1) average time for add, remove, discard, and membership tests. Elements must implement __hash__() and __eq__(); mutable types like list and dict cannot be set members. Set operations have well-defined complexities: union is O(len(a)+len(b)), intersection is O(min(len(a),len(b))), and difference is O(len(a)). The symmetric difference (a ^ b) is equivalent to (a | b) - (a & b) and returns elements in exactly one of the two sets. frozenset is hashable and immutable, making it suitable as a dict key or a member of another set. Set comprehensions ({expr for x in iterable}) work just like list comprehensions but produce sets. For disjointness checks, use a.isdisjoint(b) which returns True if a and b share no elements.", "codeExample": "# Membership test performance\nbig_list = list(range(1_000_000))\nbig_set  = set(range(1_000_000))\n\nimport time\n# List: O(n) scan\nstart = time.time()\n_ = 999_999 in big_list\nprint(f'List: {time.time()-start:.6f}s')\n\n# Set: O(1) hash lookup\nstart = time.time()\n_ = 999_999 in big_set\nprint(f'Set:  {time.time()-start:.6f}s')\n\n# frozenset as dict key\ncache = {}\nkey = frozenset([1, 2, 3])\ncache[key] = 'result'\nprint(cache[frozenset([3, 2, 1])])  # 'result'"},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "Venn diagram of set operations:\n\n  A = {1, 2, 3, 4}      B = {3, 4, 5, 6}\n  [ 1  2 ( 3  4 ) 5  6 ]\n         overlap\n\n  A | B  = {1,2,3,4,5,6}   (everything)\n  A & B  = {3,4}            (overlap only)\n  A - B  = {1,2}            (A minus overlap)\n  B - A  = {5,6}            (B minus overlap)\n  A ^ B  = {1,2,5,6}        (everything except overlap)\n\nAdding a duplicate has no effect; the set size stays the same."},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "A set is like a guest list for an exclusive party: each name can appear only once and the order people arrive does not matter. Adding a name that is already on the list changes nothing. Checking if someone is invited (membership test) is instant because the bouncer has a lookup table, not a long scroll to read through. Union is merging guest lists from two parties into one combined list. Intersection is finding people invited to BOTH parties. Difference is finding people invited to one party but not the other. A frozenset is like a printed (permanent) guest list that cannot be edited after creation.", "codeExample": "# Guest list analogy\nparty_a = {'Alice', 'Bob', 'Charlie'}\nparty_b = {'Bob', 'Diana', 'Eve'}\n\n# Who is invited to either party?\nall_guests = party_a | party_b\nprint(all_guests)  # all 5 people\n\n# Who is invited to BOTH?\nvip = party_a & party_b\nprint(vip)  # {'Bob'}\n\n# Only at party A?\nexclusive_a = party_a - party_b\nprint(exclusive_a)  # {'Alice', 'Charlie'}"},
                ],
                "quiz": [
                    {"id": "q5-3-1", "question": "What happens when you add a duplicate to a set?", "options": ["Error", "Duplicate added", "Duplicate ignored, returns false", "Replaces existing"], "correctAnswer": 2},
                    {"id": "q5-3-2", "question": "What does a & b return?", "options": ["Union", "Intersection", "Difference", "Symmetric difference"], "correctAnswer": 1},
                    {"id": "q5-3-3", "question": "Are sets ordered?", "options": ["Yes", "No", "Only when sorted", "Depends on size"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-7", "title": "Python Data Structures Full Course", "language": "Python", "youtubeId": "8hly31xKli0", "thumbnail": "https://img.youtube.com/vi/8hly31xKli0/mqdefault.jpg", "duration": "25:00"}],
            },
        ],
    },
    {
        "id": "topic-6",
        "language": "SQL",
        "topicName": "SQL Fundamentals",
        "difficulty": "Beginner",
        "overview": (
            "SQL (Structured Query Language) is the standard language for managing relational databases. It's used "
            "by nearly every application that stores data â€” from web apps to data science pipelines. You'll learn "
            "SELECT, INSERT, UPDATE, DELETE, WHERE clauses, JOIN types (INNER, LEFT, RIGHT, FULL), GROUP BY, "
            "ORDER BY, aggregate functions (COUNT, SUM, AVG), and subqueries. SQL proficiency is essential for "
            "backend development, data analysis, and database administration."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Write SQL Query","detail":"Start building your data request"},{"id":"p1","type":"process","label":"SELECT columns","detail":"Choose which columns to display"},{"id":"p2","type":"process","label":"FROM table","detail":"Specify the source table(s)"},{"id":"d1","type":"decision","label":"Need data from multiple tables?","yes":"Use JOIN","no":"Skip to WHERE"},{"id":"p3","type":"process","label":"WHERE condition","detail":"Filter rows matching your criteria"},{"id":"d2","type":"decision","label":"Need aggregation?","detail":"COUNT, SUM, AVG needed?","yes":"Use GROUP BY","no":"Skip to ORDER BY"},{"id":"p4","type":"process","label":"ORDER BY column","detail":"Sort results ASC or DESC"},{"id":"e1","type":"end","label":"Results Returned","detail":"Filtered, sorted, grouped data"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "SELECT picks columns, FROM picks the table, WHERE filters rows, JOIN combines tables. INNER JOIN = only matching rows. LEFT JOIN = all left + matching right. GROUP BY groups rows for counting/summing. ORDER BY sorts results. INSERT adds rows, UPDATE changes rows, DELETE removes rows."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "SQL operates on relational algebra: SELECT is projection (Ï€), WHERE is selection (Ïƒ), JOIN is the natural join (â‹ˆ). Query execution order: FROM â†’ WHERE â†’ GROUP BY â†’ HAVING â†’ SELECT â†’ ORDER BY â†’ LIMIT. Indexes create B-tree structures for O(log n) lookups instead of O(n) full table scans. Normalization (1NF through 3NF) eliminates data redundancy."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "Think of SQL like a librarian: SELECT is asking for specific book info, WHERE is saying 'only mystery books,' JOIN is cross-referencing the author catalog with the book catalog, GROUP BY is organizing books into genre piles, and ORDER BY is alphabetizing the results."},
        ],
        "quiz": [
            {"id": "q6-1", "question": "Which SQL clause filters rows?", "options": ["SELECT", "FROM", "WHERE", "GROUP BY"], "correctAnswer": 2},
            {"id": "q6-2", "question": "What does INNER JOIN return?", "options": ["All rows from both tables", "Only matching rows", "All rows from the left table", "All rows from the right table"], "correctAnswer": 1},
            {"id": "q6-3", "question": "Which function counts rows?", "options": ["SUM()", "COUNT()", "AVG()", "TOTAL()"], "correctAnswer": 1},
            {"id": "q6-4", "question": "What does ORDER BY do?", "options": ["Groups results", "Filters results", "Sorts results", "Limits results"], "correctAnswer": 2},
            {"id": "q6-5", "question": "Which statement adds new data?", "options": ["UPDATE", "INSERT", "CREATE", "ALTER"], "correctAnswer": 1},
        ],
        "recommendedVideos": [
            {"id": "vid-8", "title": "SQL Tutorial for Beginners", "language": "SQL", "youtubeId": "HXV3zeQKqGY", "thumbnail": "https://img.youtube.com/vi/HXV3zeQKqGY/mqdefault.jpg", "duration": "30:00"},
        ],
        "subtopics": [
            {
                "id": "sub-6-1", "name": "SELECT & WHERE",
                "pdfUrl": "internal", "pdfTitle": "SQL SELECT & WHERE Guide",
                "overview": "SELECT and WHERE form the most fundamental query pattern in SQL, used to retrieve specific data from a database table. SELECT specifies which columns to include in the result set, and you can use * to select all columns or list specific column names. WHERE filters rows based on boolean conditions using operators like =, <>, <, >, >=, <=, LIKE, IN, BETWEEN, and IS NULL. Multiple conditions can be combined with AND, OR, and NOT to build complex filters. In the logical query processing order, FROM is evaluated first, then WHERE filters rows, and finally SELECT projects the requested columns. Adding ORDER BY sorts the results, and LIMIT (or TOP in some databases) restricts the number of rows returned.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "SELECT tells the database which columns you want to see, and FROM tells it which table to look in. WHERE acts as a filter: only rows that match your condition are included in the results. For example, SELECT name, age FROM students WHERE age > 18 returns the name and age of adult students only. You can combine conditions: WHERE age > 18 AND grade = 'A' requires BOTH to be true. LIKE lets you do pattern matching: WHERE name LIKE 'A%' matches names starting with A. IN lets you check against a list: WHERE department IN ('Sales', 'Engineering'). ORDER BY sorts your results, and adding DESC sorts in reverse order."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "SELECT performs projection (â†’ vertical slicing of columns), while WHERE performs selection (â†’ horizontal filtering of rows). The logical query processing order is: FROM (identify source table), WHERE (filter rows), SELECT (project columns), then ORDER BY (sort results). WHERE predicates support comparison (=, <>, <, >), range (BETWEEN), pattern (LIKE with % and _ wildcards), list (IN), and null checks (IS NULL, IS NOT NULL). Compound predicates use AND (both must be true), OR (at least one), and NOT (negation), with AND binding tighter than OR. Use parentheses to control evaluation order when mixing AND and OR: WHERE (a = 1 OR b = 2) AND c = 3. Indexes on filtered columns improve WHERE performance from O(n) full table scan to O(log n) index seek. SELECT DISTINCT eliminates duplicate rows from the result set."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "Step-by-step query execution:\n\nTable: employees (5 rows, 4 columns)\n  id | name   | dept  id | dept_name\n   1 | Alice  |  10    10 | Engineering\n   2 | Bob    |  20    20 | Sales\n   3 | Charlie| NULL   30 | HR\n\nQuery: SELECT name, salary FROM employees WHERE dept = 'Eng' ORDER BY salary DESC;\nStep 1 (FROM): read all 5 rows\nStep 2 (WHERE dept='Eng'): keep rows 1, 3, 5\nStep 3 (SELECT name,salary): drop id, dept columns\nStep 4 (ORDER BY salary DESC): Charlie 95000, Alice 80000, Eve 72000"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "SELECT is like ordering at a restaurant: you pick specific items from the menu (columns from the table). FROM is which restaurant you go to (which table to query). WHERE is like dietary restrictions: 'only vegetarian dishes under $15.' AND means BOTH restrictions must be satisfied; OR means EITHER one is enough. LIKE is like asking the waiter: 'Do you have anything that starts with Ch...?' (pattern match). ORDER BY is asking 'sort by price, cheapest first.' LIMIT is saying 'just show me the top 3 options, I do not need the entire menu.'", "codeExample": "# Restaurant analogy queries\n-- 'Show me name and price of veggie dishes under $15'\nSELECT name, price\nFROM menu\nWHERE category = 'Vegetarian'\n  AND price < 15\nORDER BY price ASC;\n\n-- 'Anything starting with Ch?'\nSELECT name FROM menu\nWHERE name LIKE 'Ch%';\n\n-- 'Top 3 cheapest'\nSELECT name, price FROM menu\nORDER BY price ASC\nLIMIT 3;"},
                ],
                "quiz": [
                    {"id": "q6-1-1", "question": "What does SELECT do?", "options": ["Deletes rows", "Chooses columns to display", "Creates a table", "Inserts data"], "correctAnswer": 1},
                    {"id": "q6-1-2", "question": "What does WHERE do?", "options": ["Sorts results", "Groups results", "Filters rows based on conditions", "Joins tables"], "correctAnswer": 2},
                    {"id": "q6-1-3", "question": "Which is processed first: WHERE or SELECT?", "options": ["SELECT", "WHERE", "They run simultaneously", "Depends on the database"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-8", "title": "SQL Tutorial for Beginners", "language": "SQL", "youtubeId": "HXV3zeQKqGY", "thumbnail": "https://img.youtube.com/vi/HXV3zeQKqGY/mqdefault.jpg", "duration": "30:00"}],
            },
            {
                "id": "sub-6-2", "name": "JOINs",
                "pdfUrl": "internal", "pdfTitle": "SQL JOINs â€“ Complete Guide",
                "overview": "JOINs combine rows from two or more tables based on a related column, enabling you to query normalised relational data. INNER JOIN returns only the rows where the join condition matches in both tables, which is the most common join type. LEFT (OUTER) JOIN returns all rows from the left table and matched rows from the right table; unmatched right columns are filled with NULL. RIGHT (OUTER) JOIN is the mirror image: all rows from the right table plus matching left rows. FULL OUTER JOIN returns all rows from both tables, with NULLs where there is no match on either side. CROSS JOIN produces the Cartesian product of two tables (every combination of rows), and a self-join is a table joined to itself, useful for hierarchical data.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "Imagine two spreadsheets: one lists employees with a dept_id column, the other lists departments with an id column. INNER JOIN combines them so you see each employee next to their department name, but only if the dept_id matches a department id. Employees without a matching department are dropped from the results. LEFT JOIN keeps ALL employees, even those without a department; the department columns show NULL for unmatched rows. RIGHT JOIN keeps ALL departments; employees columns are NULL if a department has no members. FULL OUTER JOIN keeps everything from both tables, with NULLs filling in wherever there is no match."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "INNER JOIN computes the equi-join (or theta-join for non-equality conditions) returning only rows satisfying the ON predicate. LEFT OUTER JOIN is defined as the inner join UNION ALL the unmatched left rows, with NULL-padded right columns. CROSS JOIN produces the Cartesian product: if table A has m rows and B has n rows, the result has m x n rows. A self-join joins a table to itself using aliases, enabling comparisons between rows in the same table (e.g., finding employees and their managers). Join order can affect performance: the query optimiser typically rearranges joins to minimise intermediate result sizes. Indexes on join columns (especially foreign keys) are critical for performance, reducing the join algorithm from nested-loop O(m*n) to hash join O(m+n). ON specifies the join condition, while WHERE filters the joined result; placing conditions incorrectly can change LEFT JOIN semantics."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "employees:          departments:\nid | name   | dept  id | dept_name\n 1 | Alice  |  10    10 | Engineering\n 2 | Bob    |  20    20 | Sales\n 3 | Charlie| NULL   30 | HR\n\nINNER JOIN (e.dept = d.id):\n  Alice  | Engineering\n  Bob    | Sales\n(Charlie dropped, HR dropped)\n\nLEFT JOIN:\n  Alice  | Engineering\n  Bob    | Sales\n  Charlie| NULL         (no matching dept)\n\nFULL OUTER JOIN:\n  Alice  | Engineering\n  Bob    | Sales\n  Charlie| NULL\n  NULL   | HR           (no matching employee)"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "JOINs are like matching puzzle pieces from two different puzzles. INNER JOIN keeps only pieces that fit together: unmatched pieces from both puzzles are discarded. LEFT JOIN keeps all pieces from the first puzzle, even if they have no match; you see gaps (NULLs) where a piece is missing from the second puzzle. FULL OUTER JOIN keeps everything from both puzzles: completed matches plus all unmatched pieces from both sides. CROSS JOIN is like pairing every shirt with every pair of trousers in your wardrobe: every possible combination. A self-join is like a family tree query: you look at the same table of people twice to find parent-child relationships.", "codeExample": "# Puzzle analogy: finding matched and unmatched records\n\n-- Only matched (INNER JOIN)\nSELECT o.order_id, c.name\nFROM orders o\nINNER JOIN customers c ON o.customer_id = c.id;\n\n-- All orders, even those with deleted customers (LEFT JOIN)\nSELECT o.order_id, COALESCE(c.name, 'Unknown') AS customer\nFROM orders o\nLEFT JOIN customers c ON o.customer_id = c.id;\n\n-- Family tree (self-join)\nSELECT child.name, parent.name AS parent_name\nFROM people child\nLEFT JOIN people parent ON child.parent_id = parent.id;"},
                ],
                "quiz": [
                    {"id": "q6-2-1", "question": "What does INNER JOIN return?", "options": ["All rows from both tables", "Only matching rows from both tables", "All rows from the left table", "A Cartesian product"], "correctAnswer": 1},
                    {"id": "q6-2-2", "question": "What happens with LEFT JOIN when there's no match on the right?", "options": ["Row is excluded", "Right columns are NULL", "An error occurs", "Right columns are 0"], "correctAnswer": 1},
                    {"id": "q6-2-3", "question": "What is a self-join?", "options": ["A join with no condition", "A table joined to itself", "A join that returns all rows", "A join between 3 tables"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-8", "title": "SQL Tutorial for Beginners", "language": "SQL", "youtubeId": "HXV3zeQKqGY", "thumbnail": "https://img.youtube.com/vi/HXV3zeQKqGY/mqdefault.jpg", "duration": "30:00"}],
            },
            {
                "id": "sub-6-3", "name": "Aggregate Functions & GROUP BY",
                "pdfUrl": "internal", "pdfTitle": "SQL Aggregate Functions Guide",
                "overview": "Aggregate functions (COUNT, SUM, AVG, MIN, MAX) compute a single result from a set of input rows, collapsing many rows into one summary value. GROUP BY partitions the result set into groups based on one or more column values, and the aggregate function is applied independently to each group. HAVING filters groups after aggregation, similar to how WHERE filters rows before aggregation. The logical processing order is: FROM â†’ WHERE â†’ GROUP BY â†’ HAVING â†’ SELECT â†’ ORDER BY, which is why you cannot use column aliases from SELECT inside WHERE. COUNT(*) counts all rows including NULLs, while COUNT(column) counts only non-NULL values in that column. You can combine aggregate queries with JOINs, subqueries, and window functions to build powerful analytical reports.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "Aggregate functions summarise data: COUNT() counts rows, SUM() adds up numbers, AVG() calculates the average, MIN() finds the smallest, MAX() finds the biggest. Without GROUP BY, the aggregate applies to ALL rows and returns one result. GROUP BY splits the data into groups first, then each aggregate runs per group. For example, SELECT department, COUNT(*) FROM employees GROUP BY department counts employees in EACH department separately. HAVING filters which groups appear in the final result: HAVING COUNT(*) > 5 keeps only departments with more than 5 employees. Remember: WHERE filters individual rows BEFORE grouping, HAVING filters entire groups AFTER aggregation."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "Aggregate functions collapse sets of rows into scalar values and are evaluated during the SELECT phase after GROUP BY has partitioned the data. COUNT(*) counts rows regardless of NULL; COUNT(col) skips NULLs; COUNT(DISTINCT col) counts unique non-NULL values. GROUP BY creates partitions: all rows sharing the same GROUP BY column values form one group. Any column in SELECT that is not inside an aggregate function MUST appear in GROUP BY (SQL standard requirement). HAVING is the post-aggregation filter: it can reference aggregate results like HAVING SUM(amount) > 1000, which WHERE cannot do because WHERE runs before aggregation. Window functions (e.g., SUM() OVER (PARTITION BY ...)) perform aggregation without collapsing rows, adding summary columns alongside detail rows. Query execution order: FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "Aggregation pipeline visualised:\n\nRaw data (employees table, 6 rows):\n  Eng: Alice 80k, Bob 90k, Eve 70k\n  Sales: Charlie 50k, Diana 55k\n  HR: Frank 45k\n\nGROUP BY department (3 groups formed):\n  Eng group   -> COUNT=3, AVG=80k, SUM=240k\n  Sales group -> COUNT=2, AVG=52.5k, SUM=105k\n  HR group    -> COUNT=1, AVG=45k, SUM=45k\n\nHAVING COUNT(*) > 1 (filter groups):\n  Eng group   -> kept (3 > 1)\n  Sales group -> kept (2 > 1)\n  HR group    -> removed (1 is not > 1)"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "GROUP BY is like sorting books into piles by genre at a library. Once you have the piles, aggregate functions are what you do with each pile: COUNT is counting the books per genre, SUM is adding up the total pages, AVG is the average page count, MAX is finding the thickest book. HAVING is like saying 'only show me genres that have more than 10 books'; it filters the piles after they have been formed. WHERE is different: it removes individual books BEFORE they go into piles (e.g., 'only include hardcovers'). The distinction matters: WHERE cannot use aggregate results because the piles have not been formed yet when WHERE runs.", "codeExample": "# Library analogy queries\n\n-- Count books per genre\nSELECT genre, COUNT(*) AS book_count\nFROM books\nGROUP BY genre;\n\n-- Only hardcovers (WHERE = before grouping)\nSELECT genre, COUNT(*) AS book_count\nFROM books\nWHERE format = 'Hardcover'\nGROUP BY genre;\n\n-- Genres with many books (HAVING = after grouping)\nSELECT genre, COUNT(*) AS book_count\nFROM books\nGROUP BY genre\nHAVING COUNT(*) > 10\nORDER BY book_count DESC;"},
                ],
                "quiz": [
                    {"id": "q6-3-1", "question": "What does COUNT(*) do?", "options": ["Counts columns", "Counts all rows", "Counts distinct values", "Counts NULL values only"], "correctAnswer": 1},
                    {"id": "q6-3-2", "question": "What is the difference between WHERE and HAVING?", "options": ["No difference", "WHERE filters rows, HAVING filters groups", "WHERE is faster", "HAVING filters rows, WHERE filters groups"], "correctAnswer": 1},
                    {"id": "q6-3-3", "question": "Is GROUP BY processed before or after WHERE?", "options": ["Before", "After", "At the same time", "Depends on the query"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-8", "title": "SQL Tutorial for Beginners", "language": "SQL", "youtubeId": "HXV3zeQKqGY", "thumbnail": "https://img.youtube.com/vi/HXV3zeQKqGY/mqdefault.jpg", "duration": "30:00"}],
            },
        ],
    },
    {
        "id": "topic-7",
        "language": "C++",
        "topicName": "C++ STL Containers",
        "difficulty": "Advanced",
        "overview": (
            "The Standard Template Library (STL) is C++'s crown jewel â€” a collection of generic, reusable data "
            "structures and algorithms. Containers like vector, map, set, unordered_map, stack, queue, and deque "
            "provide efficient, type-safe storage. Iterators give uniform access patterns across all containers. "
            "Understanding STL is vital for competitive programming, systems development, and writing idiomatic C++."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Choose STL Container","detail":"What access pattern do you need?"},{"id":"d1","type":"decision","label":"Need key-value storage?","yes":"map or unordered_map","no":"Continue below"},{"id":"d2","type":"decision","label":"Need sorted order?","detail":"Ordered iteration required?","yes":"map / set (Red-Black tree)","no":"unordered_map / unordered_set (hash)"},{"id":"d3","type":"decision","label":"LIFO or FIFO?","detail":"Stack or Queue behavior?","yes":"stack (LIFO) or queue (FIFO)","no":"Use vector or deque"},{"id":"p1","type":"process","label":"vector<T>","detail":"Dynamic array  -  O(1) random access, amortized O(1) push_back"},{"id":"p2","type":"process","label":"Iterators","detail":"begin(), end(), ++it  -  uniform traversal for all containers"},{"id":"e1","type":"end","label":"Container Selected","detail":"Match data structure to access pattern"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "vector = resizable array. map = sorted key-value pairs. set = sorted unique values. unordered_map = fast key-value lookup. stack = LIFO. queue = FIFO. Use vector when you need fast access by index, map for sorted lookups, unordered_map for fastest lookups, set for unique sorted items."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "vector: dynamic array, O(1) random access, amortized O(1) push_back. map/set: Red-Black trees, O(log n) operations, sorted order. unordered_map/unordered_set: hash tables, O(1) average operations. stack/queue: adapter containers. deque: double-ended queue, O(1) push/pop at both ends. Iterators abstract container traversal: begin(), end(), ++, *, ->."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "vector is a magic backpack that grows when you add items. map is a dictionary (word â†’ definition). set is a membership list where nobody appears twice. stack is a Pringles can (last chip in, first chip out). queue is a drive-through (first car in, first car served). unordered_map is like a speed-dial phone â€” you know the shortcut, instant connection."},
        ],
        "quiz": [
            {"id": "q7-1", "question": "What is the time complexity of vector::push_back?", "options": ["O(n)", "O(log n)", "Amortized O(1)", "O(nÂ²)"], "correctAnswer": 2},
            {"id": "q7-2", "question": "Which container uses a hash table?", "options": ["map", "set", "unordered_map", "vector"], "correctAnswer": 2},
            {"id": "q7-3", "question": "What data structure does std::map use internally?", "options": ["Hash table", "Array", "Red-Black tree", "Linked list"], "correctAnswer": 2},
            {"id": "q7-4", "question": "Which container follows LIFO order?", "options": ["queue", "vector", "deque", "stack"], "correctAnswer": 3},
            {"id": "q7-5", "question": "What does an iterator do?", "options": ["Sorts elements", "Provides sequential access to container elements", "Allocates memory", "Creates containers"], "correctAnswer": 1},
        ],
        "recommendedVideos": [
            {"id": "vid-9", "title": "C++ STL Tutorial", "language": "C++", "youtubeId": "Wl2gxKOjMTg", "thumbnail": "https://img.youtube.com/vi/Wl2gxKOjMTg/mqdefault.jpg", "duration": "35:00"},
        ],
        "subtopics": [
            {
                "id": "sub-7-1", "name": "vector",
                "pdfUrl": "internal", "pdfTitle": "C++ STL vector Guide",
                "overview": "std::vector is the most commonly used STL container in C++. It is a dynamic array that automatically grows when elements are added beyond its current capacity. Internally, vector allocates a contiguous block of memory and doubles its capacity when full, giving amortized O(1) push_back performance. Random access by index is O(1) because the address is computed as base + index * sizeof(T). The reserve() function pre-allocates memory to avoid costly reallocations, while shrink_to_fit() releases unused capacity. Iterators may become invalid after push_back if reallocation occurs, so be cautious when storing iterators across insertions.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "A vector is like a resizable array and is the most commonly used container in C++. You can use push_back() to add elements at the end, operator[] or at() to access elements by position, and size() to find out how many elements are stored. Unlike plain arrays, vectors grow automatically when you add more items than they can hold. The empty() method checks if there are no elements, and clear() removes everything. You can also use iterators (begin() and end()) with for loops for clean traversal. Behind the scenes, vector stores elements in contiguous memory, making it very cache-friendly and fast for sequential access.", "codeExample": "#include <vector>\n#include <iostream>\nusing namespace std;\n\nvector<int> v = {10, 20, 30};\nv.push_back(40);       // {10, 20, 30, 40}\nv.push_back(50);       // {10, 20, 30, 40, 50}\n\ncout << v[0] << endl;    // 10\ncout << v.size() << endl; // 5\ncout << v.at(2) << endl;  // 30 (bounds-checked)\n\nv.pop_back();            // removes 50\nv.erase(v.begin() + 1); // removes 20 -> {10, 30, 40}\n\nfor (int x : v) cout << x << ' '; // 10 30 40"},
                    {"style": "logical", "title": "Logical", "icon": "🧠", "content": "vector<T> uses contiguous memory with a capacity-doubling strategy. When size() reaches capacity(), a new block (typically 2x larger) is allocated, elements are copied or moved, and the old block is freed. push_back is amortized O(1) due to geometric growth. Random access via operator[] is O(1) since the address is computed as base + index*sizeof(T). Insert and erase at an arbitrary position are O(n) because elements must be shifted. reserve(n) pre-allocates to avoid repeated reallocations. shrink_to_fit() releases unused capacity. Iterators, pointers, and references are invalidated on reallocation. emplace_back constructs elements in-place, avoiding an extra copy.", "codeExample": "#include <vector>\n#include <iostream>\nusing namespace std;\n\nvector<int> v;\nv.reserve(100);  // pre-allocate for 100 elements\ncout << v.size() << endl;     // 0\ncout << v.capacity() << endl; // 100\n\nfor (int i = 0; i < 50; i++) v.push_back(i);\ncout << v.size() << endl;     // 50\ncout << v.capacity() << endl; // 100 (no reallocation)\n\nv.shrink_to_fit();\ncout << v.capacity() << endl; // ~50\n\n// emplace_back constructs in-place\nv.emplace_back(99);"},
                    {"style": "visual", "title": "Visual", "icon": "🎨", "content": "Imagine the memory layout of a vector:\n\nCapacity = 8, Size = 5:\n[10][20][30][40][50][ ][ ][ ]\n  ^                      ^\n begin()              end()\n\npush_back(60) -> Size = 6, Capacity still 8:\n[10][20][30][40][50][60][ ][ ]\n\nAfter push_back fills all 8 -> reallocation doubles capacity to 16:\nOld: [10][20][30][40][50][60][70][80] (full!)\nNew: [10][20][30][40][50][60][70][80][ ][ ][ ][ ][ ][ ][ ][ ]", "codeExample": "#include <vector>\n#include <iostream>\nusing namespace std;\n\nvector<int> v;\nfor (int i = 1; i <= 9; i++) {\n    v.push_back(i * 10);\n    cout << \"size=\" << v.size()\n         << \" cap=\" << v.capacity() << endl;\n}\n// Output shows capacity doubling:\n// size=1 cap=1\n// size=2 cap=2\n// size=3 cap=4\n// size=5 cap=8\n// size=9 cap=16"},
                    {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "A vector is like a magic backpack that expands when you keep adding items. You can instantly grab any item by saying 'give me item number 3' because they are stored in numbered slots. Adding to the end (push_back) is easy, just toss it in. But inserting in the middle means shifting everything after it, like squeezing a book into a full shelf. When the backpack is completely full, the magic kicks in: you get a new backpack twice the size, move everything over, and the old one disappears. That is why reserve() is useful, because you can start with a big enough backpack so you never need to upgrade mid-task.", "codeExample": "// Backpack analogy in code\nvector<string> backpack;\nbackpack.reserve(5);  // start with 5-slot backpack\n\nbackpack.push_back(\"Book\");     // slot 0\nbackpack.push_back(\"Laptop\");   // slot 1\nbackpack.push_back(\"Bottle\");   // slot 2\n\ncout << backpack[1] << endl;     // \"Laptop\" - instant\ncout << backpack.size() << endl; // 3 items in backpack\ncout << backpack.capacity() << endl; // 5 total slots"},
                ],
                "quiz": [
                    {"id": "q7-1-1", "question": "What does push_back's amortized time complexity?", "options": ["O(n)", "O(log n)", "O(1)", "O(nÂ²)"], "correctAnswer": 2},
                    {"id": "q7-1-2", "question": "Does vector use contiguous memory?", "options": ["No", "Yes", "Only for small sizes", "Depends on the type"], "correctAnswer": 1},
                    {"id": "q7-1-3", "question": "What does reserve(n) do?", "options": ["Adds n elements", "Pre-allocates memory for n elements", "Sorts n elements", "Removes n elements"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-9", "title": "C++ STL Tutorial", "language": "C++", "youtubeId": "Wl2gxKOjMTg", "thumbnail": "https://img.youtube.com/vi/Wl2gxKOjMTg/mqdefault.jpg", "duration": "35:00"}],
            },
            {
                "id": "sub-7-2", "name": "map & set",
                "pdfUrl": "internal", "pdfTitle": "C++ STL map & set Guide",
                "overview": "std::map stores sorted key-value pairs using a Red-Black tree, providing O(log n) insert, lookup, and erase. std::set stores sorted unique values with the same O(log n) guarantees. Both containers keep elements in sorted order automatically by the key (or value for set). The unordered variants (unordered_map, unordered_set) use hash tables for O(1) average-case operations but sacrifice ordering. Custom comparators can be provided as a third template parameter. multimap and multiset allow duplicate keys. Range queries are supported through lower_bound() and upper_bound().",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "A map is a sorted dictionary of key-value pairs, like a phone book sorted alphabetically where each name has a phone number. A set is a sorted collection of unique values, like a membership roster with no duplicates. Both use trees internally, so all operations (insert, find, erase) take O(log n) time. Use map when you need to associate keys with values and want them sorted. Use set when you just need a sorted collection of unique items. The bracket operator map[key] both accesses and inserts entries. The find() method returns an iterator to the element or end() if not found.", "codeExample": "#include <map>\n#include <set>\n#include <iostream>\nusing namespace std;\n\nmap<string, int> ages;\nages[\"Alice\"] = 25;\nages[\"Bob\"] = 30;\nages[\"Charlie\"] = 22;\n\n// Iterating gives sorted order by key\nfor (auto& [name, age] : ages)\n    cout << name << \": \" << age << endl;\n// Alice: 25, Bob: 30, Charlie: 22\n\nset<int> s = {5, 3, 1, 4, 2};\nfor (int x : s) cout << x << ' '; // 1 2 3 4 5"},
                    {"style": "logical", "title": "Logical", "icon": "🧠", "content": "map<K,V> and set<K> are implemented as Red-Black trees (self-balancing BSTs). Insert, find, and erase all run in O(log n) time. Iterating over a map or set produces elements in sorted order. A custom comparator can be specified as the third template parameter, for example map<int,string,greater<int>> for reverse ordering. multimap and multiset allow duplicate keys. lower_bound(key) returns an iterator to the first element not less than key, and upper_bound(key) returns the first element greater than key, enabling efficient range queries. The count() method returns 0 or 1 for map/set (or the duplicate count for multi variants).", "codeExample": "#include <map>\n#include <set>\nusing namespace std;\n\n// Custom comparator: reverse order\nmap<int, string, greater<int>> rm;\nrm[1] = \"one\"; rm[3] = \"three\"; rm[2] = \"two\";\n// Iteration: 3->three, 2->two, 1->one\n\n// Range queries\nset<int> s = {10, 20, 30, 40, 50};\nauto lo = s.lower_bound(20); // points to 20\nauto hi = s.upper_bound(40); // points to 50\nfor (auto it = lo; it != hi; ++it)\n    cout << *it << ' '; // 20 30 40\n\n// multiset allows duplicates\nmultiset<int> ms = {1, 2, 2, 3};\ncout << ms.count(2); // 2"},
                    {"style": "visual", "title": "Visual", "icon": "🎨", "content": "Red-Black tree behind std::map:\n\n        [Bob:30]\n       /        \\\n  [Alice:25]  [Charlie:22]\n\nInserting [Dave:28]:\n        [Bob:30]\n       /        \\\n  [Alice:25]  [Charlie:22]\n                    \\\n                  [Dave:28]\n\nTree self-balances to maintain O(log n) height.\nIterating in-order gives: Alice, Bob, Charlie, Dave (sorted!).", "codeExample": "// Visual demo of sorted iteration\n#include <map>\n#include <iostream>\nusing namespace std;\n\nmap<string, int> scores;\nscores[\"Dave\"] = 88;\nscores[\"Alice\"] = 95;\nscores[\"Charlie\"] = 72;\nscores[\"Bob\"] = 81;\n\n// Always prints in alphabetical order:\nfor (auto& [name, score] : scores)\n    cout << name << \": \" << score << endl;\n// Alice: 95\n// Bob: 81\n// Charlie: 72\n// Dave: 88"},
                    {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "A map is like a phone book where names (keys) are sorted alphabetically and each name has exactly one phone number (value). Looking up a name is fast because the book is sorted, you can use binary search. A set is like a membership roster where every member name appears only once, and the list is always kept in alphabetical order. Finding someone means flipping to roughly the middle, checking, and narrowing down. multimap is like a phone book where one person can have multiple numbers. unordered_map is like a hash table, no sorting but instant lookup.", "codeExample": "# Phone book analogy\nmap<string, string> phonebook;\nphonebook[\"Alice\"] = \"555-0101\";\nphonebook[\"Bob\"] = \"555-0202\";\nphonebook[\"Charlie\"] = \"555-0303\";\n\n// Fast lookup\nif (phonebook.find(\"Bob\") != phonebook.end())\n    cout << \"Bob: \" << phonebook[\"Bob\"] << endl;\n\n// Membership roster\nset<string> members = {\"Alice\", \"Charlie\", \"Bob\"};\ncout << members.count(\"Alice\"); // 1 (found)\ncout << members.count(\"Dave\");  // 0 (not found)"},
                ],
                "quiz": [
                    {"id": "q7-2-1", "question": "What is the time complexity of map operations?", "options": ["O(n)", "O(log n)", "O(1)", "O(nÂ²)"], "correctAnswer": 2},
                    {"id": "q7-2-2", "question": "Can dictionary keys be duplicated?", "options": ["Yes", "No", "Only strings", "Only numbers"], "correctAnswer": 1},
                    {"id": "q7-2-3", "question": "What does dict.get('key', default) do?", "options": ["Always raises an error", "Returns value or default if key missing", "Deletes the key", "Creates a new dict"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-9", "title": "C++ STL Tutorial", "language": "C++", "youtubeId": "Wl2gxKOjMTg", "thumbnail": "https://img.youtube.com/vi/Wl2gxKOjMTg/mqdefault.jpg", "duration": "35:00"}],
            },
            {
                "id": "sub-7-3", "name": "stack & queue",
                "pdfUrl": "internal", "pdfTitle": "C++ STL stack & queue Guide",
                "overview": "std::stack provides LIFO (last in, first out) access, while std::queue provides FIFO (first in, first out) access. Both are container adapters built on top of deque by default. Stack supports push(), pop(), and top() operations, all in O(1) time. Queue supports push(), pop(), front(), and back(), also all O(1). The priority_queue adapter uses a max-heap internally, providing O(log n) push and pop based on element priority. You can specify a custom underlying container or a custom comparator for priority_queue to create a min-heap.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "📝", "content": "A stack is a LIFO (last in, first out) container, like a stack of plates where you always take from the top. Use push() to add to the top, pop() to remove from the top, and top() to peek at the top element without removing it. A queue is a FIFO (first in, first out) container, like a line at a store where the first person in line gets served first. Use push() to add to the back, pop() to remove from the front, and front() to peek at the first element. A priority_queue always gives you the largest element first, like an emergency room where the most urgent patient is treated first.", "codeExample": "#include <stack>\n#include <queue>\n#include <iostream>\nusing namespace std;\n\n// Stack: LIFO\nstack<int> s;\ns.push(10); s.push(20); s.push(30);\ncout << s.top() << endl; // 30 (last added)\ns.pop();                  // removes 30\ncout << s.top() << endl; // 20\n\n// Queue: FIFO\nqueue<int> q;\nq.push(10); q.push(20); q.push(30);\ncout << q.front() << endl; // 10 (first added)\nq.pop();                    // removes 10\ncout << q.front() << endl; // 20"},
                    {"style": "logical", "title": "Logical", "icon": "🧠", "content": "stack and queue are container adapters, not full containers themselves. They wrap an underlying container (deque by default) and restrict its interface. stack exposes only push, pop, top, size, and empty, all O(1). queue exposes push, pop, front, back, size, and empty, all O(1). priority_queue uses a max-heap (std::make_heap internally) with O(log n) push and pop. To create a min-heap, use priority_queue<int, vector<int>, greater<int>>. You can specify a different underlying container: stack<int, vector<int>> uses vector instead of deque.", "codeExample": "// Priority queue (max-heap by default)\n#include <queue>\n#include <vector>\n#include <iostream>\nusing namespace std;\n\npriority_queue<int> maxHeap;\nmaxHeap.push(30); maxHeap.push(10); maxHeap.push(20);\ncout << maxHeap.top() << endl; // 30 (largest)\nmaxHeap.pop();\ncout << maxHeap.top() << endl; // 20\n\n// Min-heap\npriority_queue<int, vector<int>, greater<int>> minHeap;\nminHeap.push(30); minHeap.push(10); minHeap.push(20);\ncout << minHeap.top() << endl; // 10 (smallest)"},
                    {"style": "visual", "title": "Visual", "icon": "🎨", "content": "Stack (LIFO):\n  push(1) push(2) push(3):\n  | 3 | <- top\n  | 2 |\n  | 1 |\n  pop() removes 3, top is now 2\n\nQueue (FIFO):\n  push(1) push(2) push(3):\n  front -> [1][2][3] <- back\n  pop() removes 1, front is now 2\n\nPriority Queue (max-heap):\n  push(10) push(30) push(20):\n      30\n     /  \\\n   10    20\n  top() = 30 (always the maximum)", "codeExample": "// Demonstrating stack vs queue behavior\n#include <stack>\n#include <queue>\n#include <iostream>\nusing namespace std;\n\nstack<char> stk;\nstk.push('A'); stk.push('B'); stk.push('C');\nwhile (!stk.empty()) {\n    cout << stk.top(); stk.pop();\n}\n// Output: CBA (reverse order - LIFO)\n\nqueue<char> que;\nque.push('A'); que.push('B'); que.push('C');\nwhile (!que.empty()) {\n    cout << que.front(); que.pop();\n}\n// Output: ABC (same order - FIFO)"},
                    {"style": "analogy", "title": "Analogy", "icon": "🔗", "content": "A stack is like a Pringles can: the last chip you put in is the first chip you take out. You can only access the top. A queue is like a drive-through at a restaurant: the first car that arrives is the first car that gets served. Nobody cuts in line. A priority_queue is like an ER: it does not matter who arrived first, the most urgent patient gets served first. You can customize the 'urgency' with a comparator to decide what counts as highest priority.", "codeExample": "// Real-world: undo stack for text editor\nstack<string> undoStack;\nundoStack.push(\"typed Hello\");\nundoStack.push(\"typed World\");\nundoStack.push(\"deleted o\");\n\n// Undo last action\ncout << \"Undo: \" << undoStack.top() << endl;\nundoStack.pop(); // undoes \"deleted o\"\n\n// Real-world: print queue\nqueue<string> printQueue;\nprintQueue.push(\"report.pdf\");\nprintQueue.push(\"photo.jpg\");\ncout << \"Printing: \" << printQueue.front() << endl;\nprintQueue.pop(); // prints report.pdf first"},
                ],
                "quiz": [
                    {"id": "q7-3-1", "question": "What order does a stack follow?", "options": ["FIFO", "LIFO", "Random", "Sorted"], "correctAnswer": 1},
                    {"id": "q7-3-2", "question": "What does queue::front() return?", "options": ["Last element", "First element", "Middle element", "Random element"], "correctAnswer": 1},
                    {"id": "q7-3-3", "question": "What is the time complexity of stack::push()?", "options": ["O(n)", "O(log n)", "O(1)", "O(nÂ²)"], "correctAnswer": 2},
                ],
                "recommendedVideos": [{"id": "vid-9", "title": "C++ STL Tutorial", "language": "C++", "youtubeId": "Wl2gxKOjMTg", "thumbnail": "https://img.youtube.com/vi/Wl2gxKOjMTg/mqdefault.jpg", "duration": "35:00"}],
            },
        ],
    },
    {
        "id": "topic-8",
        "language": "Java",
        "topicName": "Java Collections Framework",
        "difficulty": "Intermediate",
        "overview": (
            "The Java Collections Framework provides a unified architecture for storing and manipulating groups of "
            "objects. It includes interfaces (List, Set, Map, Queue), implementations (ArrayList, HashSet, HashMap, "
            "LinkedList, TreeMap), and utility classes (Collections, Arrays). Understanding collections is essential "
            "for data handling, algorithm implementation, and passing technical interviews."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Choose Collection Type","detail":"What behavior do you need?"},{"id":"d1","type":"decision","label":"Need key-value pairs?","yes":"Use Map (HashMap / TreeMap)","no":"Continue below"},{"id":"d2","type":"decision","label":"Allow duplicates?","detail":"Can elements repeat?","yes":"Use List interface","no":"Use Set interface"},{"id":"d3","type":"decision","label":"Need fast random access?","detail":"Frequent get(index) calls?","yes":"ArrayList (array-backed)","no":"LinkedList (node-based)"},{"id":"p1","type":"process","label":"HashSet -> O(1) contains","detail":"Unordered, no duplicates, hash table"},{"id":"p2","type":"process","label":"TreeMap -> O(log n) sorted","detail":"Sorted keys, Red-Black tree"},{"id":"e1","type":"end","label":"Collection Selected","detail":"Choose based on ordering, duplicates, and performance"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "ArrayList = resizable array, fast get(index). LinkedList = chain of nodes, fast add/remove. HashSet = unique items, no order. TreeSet = unique items, sorted. HashMap = key-value pairs, fast lookup. TreeMap = key-value pairs, sorted keys. Use ArrayList for most cases, HashMap for lookups, HashSet for uniqueness."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "ArrayList: backed by Object[], O(1) get, amortized O(1) add, O(n) insert. LinkedList: doubly-linked nodes, O(1) add/remove at ends, O(n) random access. HashSet/HashMap: hash table, O(1) average contains/get/put. TreeSet/TreeMap: Red-Black tree, O(log n) operations, NavigableSet/NavigableMap interfaces. PriorityQueue: binary heap, O(log n) offer/poll."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "ArrayList is a numbered locker system â€” instant access by number. LinkedList is a treasure hunt â€” each clue leads to the next. HashSet is a VIP guest list â€” names only, no duplicates. HashMap is a coat check â€” give them your ticket (key), get your coat (value). TreeMap is an alphabetical filing system."},
        ],
        "quiz": [
            {"id": "q8-1", "question": "Which is faster for random access?", "options": ["LinkedList", "ArrayList", "HashSet", "TreeSet"], "correctAnswer": 1},
            {"id": "q8-2", "question": "What does HashMap use internally?", "options": ["Array", "Linked list", "Hash table", "Binary tree"], "correctAnswer": 2},
            {"id": "q8-3", "question": "Which maintains sorted order?", "options": ["HashMap", "HashSet", "ArrayList", "TreeMap"], "correctAnswer": 3},
            {"id": "q8-4", "question": "What is the parent interface of ArrayList?", "options": ["Set", "Map", "List", "Queue"], "correctAnswer": 2},
            {"id": "q8-5", "question": "Which does NOT allow duplicate elements?", "options": ["ArrayList", "LinkedList", "HashSet", "Vector"], "correctAnswer": 2},
        ],
        "recommendedVideos": [
            {"id": "vid-10", "title": "Java Collections Framework Tutorial", "language": "Java", "youtubeId": "s4SfATHPQGo", "thumbnail": "https://img.youtube.com/vi/s4SfATHPQGo/mqdefault.jpg", "duration": "40:15"},
        ],
        "subtopics": [
            {
                "id": "sub-8-1", "name": "ArrayList & LinkedList",
                "pdfUrl": "internal", "pdfTitle": "Java ArrayList & LinkedList",
                "overview": "ArrayList uses a dynamic array for fast random access. LinkedList uses doubly-linked nodes for fast insertion/removal at ends. Choose based on your access pattern.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "ArrayList = fast access by index (like numbered lockers). LinkedList = fast add/remove at ends (like a chain). Use ArrayList for most cases. Use LinkedList only when you frequently add/remove at the beginning."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "ArrayList: backed by Object[], O(1) get, amortized O(1) add, O(n) insert. LinkedList: doubly-linked nodes, O(1) add/remove at ends, O(n) random access. Both implement List interface. ArrayList is cache-friendly due to contiguous memory."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "ArrayList<String> al = new ArrayList<>();\nal.add(\"A\"); al.add(\"B\"); al.add(\"C\");\nal.get(1);  // \"B\" â€” O(1)\n\nLinkedList<String> ll = new LinkedList<>();\nll.addFirst(\"X\");     // O(1)\nll.addLast(\"Y\");      // O(1)\nll.get(0);            // O(n) traversal"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "ArrayList is like a numbered locker system. LinkedList is like a treasure hunt. HashSet is like a VIP guest list. HashMap is like a coat check. TreeSet is like an alphabetical filing system."},
                ],
                "quiz": [
                    {"id": "q8-1-1", "question": "Which is faster for get(index)?", "options": ["LinkedList", "ArrayList", "Both equal", "Depends on size"], "correctAnswer": 1},
                    {"id": "q8-1-2", "question": "What data structure backs ArrayList?", "options": ["Linked list", "Dynamic array", "Hash table", "Tree"], "correctAnswer": 1},
                    {"id": "q8-1-3", "question": "When should you prefer LinkedList?", "options": ["Random access needed", "Frequent add/remove at ends", "Sorted data needed", "Unique elements needed"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-10", "title": "Java Collections Framework Tutorial", "language": "Java", "youtubeId": "s4SfATHPQGo", "thumbnail": "https://img.youtube.com/vi/s4SfATHPQGo/mqdefault.jpg", "duration": "40:15"}],
            },
            {
                "id": "sub-8-2", "name": "HashMap & TreeMap",
                "pdfUrl": "internal", "pdfTitle": "Java HashMap & TreeMap Guide",
                "overview": "HashMap provides O(1) average key-value lookups using a hash table. TreeMap provides O(log n) lookups with keys in sorted order using a Red-Black tree.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "HashMap = fastest lookup (give key, get value instantly). TreeMap = sorted keys (slower but always in order). Use HashMap for speed, TreeMap when you need sorted keys."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "HashMap: hash table with O(1) average get/put/remove. Load factor (0.75 default) triggers rehashing. TreeMap: Red-Black tree, O(log n) operations, implements NavigableMap for range queries (subMap, headMap, tailMap). LinkedHashMap maintains insertion order."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "HashMap<String, Integer> hm = new HashMap<>();\nhm.put(\"cat\", 3); hm.put(\"dog\", 5);\nhm.get(\"cat\");    // 3 â€” O(1)\n\nTreeMap<String, Integer> tm = new TreeMap<>();\ntm.put(\"banana\", 2); tm.put(\"apple\", 1);\ntm.firstKey();    // \"apple\" â€” sorted!"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "HashMap is like a coat check â€” hand over your ticket number (key), get your coat (value) instantly. TreeMap is an alphabetical filing cabinet â€” you can find things and also easily see what comes before/after."},
                ],
                "quiz": [
                    {"id": "q8-2-1", "question": "What is HashMap's average lookup time?", "options": ["O(n)", "O(log n)", "O(1)", "O(nÂ²)"], "correctAnswer": 2},
                    {"id": "q8-2-2", "question": "Which maintains sorted keys?", "options": ["HashMap", "TreeMap", "Both", "Neither"], "correctAnswer": 1},
                    {"id": "q8-2-3", "question": "What tree does TreeMap use?", "options": ["AVL tree", "B-tree", "Red-Black tree", "Binary tree"], "correctAnswer": 2},
                ],
                "recommendedVideos": [{"id": "vid-10", "title": "Java Collections Framework Tutorial", "language": "Java", "youtubeId": "s4SfATHPQGo", "thumbnail": "https://img.youtube.com/vi/s4SfATHPQGo/mqdefault.jpg", "duration": "40:15"}],
            },
            {
                "id": "sub-8-3", "name": "HashSet & TreeSet",
                "pdfUrl": "internal", "pdfTitle": "Java HashSet & TreeSet Guide",
                "overview": "HashSet stores unique elements using a hash table with O(1) operations. TreeSet stores unique elements in sorted order using a Red-Black tree with O(log n) operations.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "HashSet = fast unique collection (no duplicates, no order). TreeSet = sorted unique collection. Use HashSet when you just need uniqueness, TreeSet when you also need sorting."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "HashSet: backed by HashMap (values are dummy objects). O(1) add/contains/remove. TreeSet: backed by TreeMap, O(log n) operations, implements NavigableSet. LinkedHashSet maintains insertion order. equals() and hashCode() must be consistent for HashSet."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "HashSet<String> hs = new HashSet<>();\nhs.add(\"B\"); hs.add(\"A\"); hs.add(\"B\");\nhs.size();     // 2 (duplicate ignored)\nhs.contains(\"A\"); // true â€” O(1)\n\nTreeSet<Integer> ts = new TreeSet<>(Set.of(3,1,2));\n// ts: [1, 2, 3] â€” sorted!"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "HashSet is like a VIP guest list â€” each name appears only once, checked off instantly. TreeSet is the same list but alphabetically sorted, so you can easily find who comes 'before' or 'after' someone."},
                ],
                "quiz": [
                    {"id": "q8-3-1", "question": "What happens when adding a duplicate to HashSet?", "options": ["Error thrown", "Duplicate added", "Duplicate ignored, returns false", "Replaces existing"], "correctAnswer": 2},
                    {"id": "q8-3-2", "question": "What backs a HashSet internally?", "options": ["Array", "LinkedList", "HashMap", "TreeMap"], "correctAnswer": 2},
                    {"id": "q8-3-3", "question": "What is TreeSet's add time complexity?", "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-10", "title": "Java Collections Framework Tutorial", "language": "Java", "youtubeId": "s4SfATHPQGo", "thumbnail": "https://img.youtube.com/vi/s4SfATHPQGo/mqdefault.jpg", "duration": "40:15"}],
            },
        ],
    },
    {
        "id": "topic-9",
        "language": "Python",
        "topicName": "Python Decorators & Generators",
        "difficulty": "Advanced",
        "overview": (
            "Decorators and generators are advanced Python features that make your code more elegant and efficient. "
            "Decorators modify function behavior using the @decorator syntax â€” they're used extensively in Flask, "
            "Django, and testing frameworks. Generators use 'yield' to produce sequences lazily, saving memory when "
            "processing large datasets. Together, they represent Python's functional programming capabilities."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Define a Function","detail":"Regular function with def"},{"id":"d1","type":"decision","label":"Add @decorator?","detail":"Need to wrap with extra behavior?","yes":"Decorator wraps it","no":"Use function directly"},{"id":"p1","type":"process","label":"@decorator applied","detail":"func = decorator(func)  -  returns wrapper"},{"id":"p2","type":"process","label":"Wrapper runs extra logic","detail":"Before/after the original function call"},{"id":"d2","type":"decision","label":"Use yield instead of return?","detail":"Need lazy evaluation?","yes":"Generator function","no":"Normal return"},{"id":"p3","type":"io","label":"yield value","detail":"Pauses execution, saves state, produces one item"},{"id":"p4","type":"process","label":"next() called","detail":"Resumes from where it paused  -  O(1) memory"},{"id":"e1","type":"end","label":"All values yielded","detail":"StopIteration raised when generator is exhausted"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "Decorator = a function that wraps another function to extend its behavior without modifying it. Use @decorator above a function. Generator = a function that uses 'yield' instead of 'return'. Each time you ask for a value (next()), it runs until the next yield, gives the value, and pauses. It remembers where it stopped. Great for huge data that doesn't fit in memory."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "Decorators leverage closures and first-class functions: decorator(func) â†’ wrapper_func. The @syntax is syntactic sugar for func = decorator(func). The decorator receives func, defines a wrapper that calls func with extra logic, and returns the wrapper. functools.wraps preserves the original function's metadata (__name__, __doc__). Generators implement the iterator protocol (__iter__, __next__). yield suspends execution, saving the stack frame. Generator expressions: (expr for var in iterable [if condition]). Memory: generators are O(1) space vs O(n) for lists."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "A decorator is like adding a security badge scanner at a door â€” the room (function) stays the same, but now everyone gets scanned (extra behavior) before entering. A generator is like a storyteller reading one page at a time â€” they remember where they stopped and continue from there, instead of reading the whole book into memory."},
        ],
        "quiz": [
            {"id": "q9-1", "question": "What does @decorator syntax do?", "options": ["Comments the function", "Wraps the function with decorator behavior", "Deletes the function", "Renames the function"], "correctAnswer": 1},
            {"id": "q9-2", "question": "What keyword does a generator use?", "options": ["return", "yield", "generate", "produce"], "correctAnswer": 1},
            {"id": "q9-3", "question": "What is the memory advantage of generators?", "options": ["They use more memory", "They use O(1) space", "They cache results", "They compress data"], "correctAnswer": 1},
            {"id": "q9-4", "question": "What happens when a generator function is called?", "options": ["It runs immediately", "It returns a generator object", "It raises an error", "It creates a list"], "correctAnswer": 1},
            {"id": "q9-5", "question": "Which framework heavily uses decorators?", "options": ["NumPy", "Pandas", "Flask", "Matplotlib"], "correctAnswer": 2},
        ],
        "recommendedVideos": [
            {"id": "vid-11", "title": "Python Decorators Explained", "language": "Python", "youtubeId": "DYzThl2TnWQ", "thumbnail": "https://img.youtube.com/vi/DYzThl2TnWQ/mqdefault.jpg", "duration": "20:00"},
        ],
        "subtopics": [
            {
                "id": "sub-9-1", "name": "Decorators",
                "pdfUrl": "internal", "pdfTitle": "Python Decorators Guide",
                "overview": "A decorator is a function that wraps another function to extend its behavior without modifying it. Python uses the @decorator syntax for clean application.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "A decorator adds extra behavior to a function. @my_decorator above a function wraps it. It's like adding a security scanner at a door â€” the room (function) stays the same, but now everyone gets scanned (extra behavior) before entering. A generator is like a storyteller reading one page at a time â€” they remember where they stopped and continue from there, instead of reading the whole book into memory."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "Decorators leverage closures and first-class functions. @decorator is syntactic sugar for func = decorator(func). The decorator receives func, defines a wrapper that calls func with extra logic, and returns the wrapper. functools.wraps preserves the original function's metadata (__name__, __doc__)."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "def timer(func):\n    def wrapper(*args):\n        start = time.time()\n        result = func(*args)\n        print(f'Took {time.time()-start}s')\n        return result\n    return wrapper\n\n@timer\ndef slow_func():\n    time.sleep(1)\n\nslow_func()  # prints 'Took 1.0s'"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "A decorator is like gift wrapping â€” the present (function) stays the same, but you add wrapping paper (extra behavior). @timer is like putting a stopwatch on any function. @login_required is like adding a bouncer to a VIP room."},
                ],
                "quiz": [
                    {"id": "q9-1-1", "question": "What does @decorator syntax do?", "options": ["Deletes the function", "Wraps the function with extra behavior", "Comments the function", "Renames the function"], "correctAnswer": 1},
                    {"id": "q9-1-2", "question": "What does a decorator return?", "options": ["The original function", "A new wrapper function", "None", "An error"], "correctAnswer": 1},
                    {"id": "q9-1-3", "question": "What does functools.wraps preserve?", "options": ["The wrapper's name", "The original function's metadata", "The return value", "The parameters"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-11", "title": "Python Decorators Explained", "language": "Python", "youtubeId": "DYzThl2TnWQ", "thumbnail": "https://img.youtube.com/vi/DYzThl2TnWQ/mqdefault.jpg", "duration": "20:00"}],
            },
            {
                "id": "sub-9-2", "name": "Generators & yield",
                "pdfUrl": "internal", "pdfTitle": "Python Generators & yield",
                "overview": "Generators are functions that use yield to produce values lazily â€” one at a time â€” instead of returning all values at once. They save memory when processing large datasets.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "A generator uses 'yield' instead of 'return'. Each time you ask for a value (next()), it runs until the next yield, gives the value, and pauses. It remembers where it stopped. Great for huge data that doesn't fit in memory."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "Generators implement the iterator protocol (__iter__, __next__). yield suspends execution, saving the stack frame. O(1) memory vs O(n) for lists. Generator expressions: (expr for var in iterable [if condition]). StopIteration is raised when the generator is exhausted. send() can push values into the generator."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "def count_up(n):\n    i = 0\n    while i < n:\n        yield i\n        i += 1\n\ngen = count_up(3)\nnext(gen)  # 0\nnext(gen)  # 1\nnext(gen)  # 2\nnext(gen)  # StopIteration"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "A generator is like a storyteller reading one page at a time. They remember where they stopped (yield) and continue from there when asked (next()). They don't need to photocopy the whole book into memory â€” just read the page you need."},
                ],
                "quiz": [
                    {"id": "q9-2-1", "question": "What keyword makes a function a generator?", "options": ["return", "yield", "generate", "async"], "correctAnswer": 1},
                    {"id": "q9-2-2", "question": "What is the memory advantage of generators?", "options": ["O(n) space", "O(1) space", "O(nÂ²) space", "No advantage"], "correctAnswer": 1},
                    {"id": "q9-2-3", "question": "What happens when a generator is exhausted?", "options": ["It restarts", "StopIteration is raised", "It returns None", "It loops forever"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-11", "title": "Python Decorators Explained", "language": "Python", "youtubeId": "DYzThl2TnWQ", "thumbnail": "https://img.youtube.com/vi/DYzThl2TnWQ/mqdefault.jpg", "duration": "20:00"}],
            },
            {
                "id": "sub-9-3", "name": "Generator Expressions & Iteration",
                "pdfUrl": "internal", "pdfTitle": "Iterator & Generator Expressions",
                "overview": "Generator expressions provide a concise syntax to create generators inline. Python's iteration protocol (for loops, list(), sum(), etc.) works seamlessly with generators.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "ðŸ“", "content": "Generator expression = list comprehension but with () instead of []. (x**2 for x in range(10)) creates values lazily. You can use them in for loops, sum(), list(), etc. They're memory-efficient for large data."},
                    {"style": "logical", "title": "Logical", "icon": "ðŸ§ ", "content": "Generator expressions: (expr for var in iterable [if condition]). They return a generator object. Consumed once (single-pass iteration). Can chain generators: g2 = (f(x) for x in g1). itertools module provides powerful generator utilities: chain(), islice(), groupby(), product()."},
                    {"style": "visual", "title": "Visual", "icon": "ðŸŽ¨", "content": "# List comprehension â€” stores ALL in memory\nsquares_list = [x**2 for x in range(1000000)]  # ~8MB\n\n# Generator expression â€” computes on demand\nsquares_gen = (x**2 for x in range(1000000))   # ~120 bytes!\n\nsum(x**2 for x in range(10))  # 285 â€” clean syntax"},
                    {"style": "analogy", "title": "Analogy", "icon": "ðŸ”—", "content": "A list comprehension is like printing ALL recipes in a cookbook. A generator expression is like a chef who knows all recipes but only cooks the one you ask for â€” no wasted paper (memory), dishes made on demand."},
                ],
                "quiz": [
                    {"id": "q9-3-1", "question": "What brackets does a generator expression use?", "options": ["[]", "()", "{}", "<>"], "correctAnswer": 1},
                    {"id": "q9-3-2", "question": "Can a generator be iterated more than once?", "options": ["Yes", "No, it's single-pass", "Only with reset()", "Depends on the data"], "correctAnswer": 1},
                    {"id": "q9-3-3", "question": "Which uses less memory: [x for x in range(10**6)] or (x for x in range(10**6))?", "options": ["List comprehension", "Generator expression", "Both use the same", "Depends on values"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-11", "title": "Python Decorators Explained", "language": "Python", "youtubeId": "DYzThl2TnWQ", "thumbnail": "https://img.youtube.com/vi/DYzThl2TnWQ/mqdefault.jpg", "duration": "20:00"}],
            },
        ],
    },
    {
        "id": "topic-10",
        "language": "JavaScript",
        "topicName": "JavaScript DOM Manipulation",
        "difficulty": "Beginner",
        "overview": (
            "The Document Object Model (DOM) is a tree-like representation of your webpage. JavaScript can select, "
            "modify, create, and delete DOM elements to build dynamic, interactive web experiences. You'll learn "
            "document.querySelector, element creation, event listeners, classList manipulation, and how modern "
            "frameworks like React abstract DOM operations through virtual DOM reconciliation."
        ),
        "explanations": [
            {"style": "visual", "title": "Visual Flowchart", "icon": "ðŸŽ¨",
             "content": '[FLOWCHART]{"nodes":[{"id":"s1","type":"start","label":"Browser loads HTML","detail":"HTML parsed into DOM tree"},{"id":"p1","type":"process","label":"document.querySelector()","detail":"Find element by CSS selector"},{"id":"d1","type":"decision","label":"Element found?","detail":"Returns element or null","yes":"Manipulate it","no":"Check selector / timing"},{"id":"p2","type":"process","label":"Modify Element","detail":"textContent, style, classList.add/remove"},{"id":"p3","type":"process","label":"Create New Element","detail":"document.createElement() -> appendChild()"},{"id":"p4","type":"io","label":"addEventListener()","detail":"Listen for click, input, submit, etc."},{"id":"p5","type":"process","label":"Event fires -> callback runs","detail":"Handler modifies DOM in response to user action"},{"id":"e1","type":"end","label":"Dynamic page updated","detail":"DOM reflects new state without page reload"}]}'},
            {"style": "simplified", "title": "Simplified Explanation", "icon": "ðŸ“",
             "content": "DOM = how JavaScript sees your HTML. querySelector finds elements by CSS selector. textContent changes text. style changes appearance. createElement makes new elements. appendChild adds them. addEventListener listens for clicks, inputs, etc. classList.add/remove toggles CSS classes."},
            {"style": "logical", "title": "Logical Explanation", "icon": "ðŸ§ ",
             "content": "The DOM is an in-memory tree of Node objects representing the HTML document. querySelector uses CSS selectors with O(n) traversal. Modifying element properties triggers layout reflows (expensive). Event delegation from parent elements is O(1) vs O(n) individual listeners. DocumentFragment allows batch DOM mutations. MutationObserver provides async change detection."},
            {"style": "analogy", "title": "Analogy Explanation", "icon": "ðŸ”—",
             "content": "The DOM is like a puppet show: the HTML is the script, the DOM is the stage with puppets, and JavaScript is the puppeteer who can move, add, or remove puppets, change their costumes (styles), and make them react to the audience (event listeners)."},
        ],
        "quiz": [
            {"id": "q10-1", "question": "What does querySelector return?", "options": ["All matching elements", "The first matching element", "A string", "An array"], "correctAnswer": 1},
            {"id": "q10-2", "question": "How do you create a new element?", "options": ["new Element()", "document.createElement()", "element.create()", "DOM.new()"], "correctAnswer": 1},
            {"id": "q10-3", "question": "What does addEventListener do?", "options": ["Creates an element", "Modifies styles", "Attaches an event handler", "Removes an element"], "correctAnswer": 2},
            {"id": "q10-4", "question": "How do you add a CSS class?", "options": ["element.class = 'name'", "element.classList.add('name')", "element.style.class('name')", "element.addCSS('name')"], "correctAnswer": 1},
            {"id": "q10-5", "question": "What is the DOM?", "options": ["A programming language", "A CSS framework", "A tree representation of the HTML document", "A database"], "correctAnswer": 2},
        ],
        "recommendedVideos": [
            {"id": "vid-12", "title": "JavaScript DOM Crash Course", "language": "JavaScript", "youtubeId": "0ik6X4DJKCc", "thumbnail": "https://img.youtube.com/vi/0ik6X4DJKCc/mqdefault.jpg", "duration": "28:30"},
        ],
        "subtopics": [
                        {
                "id": "sub-10-1", "name": "Selecting Elements",
                "pdfUrl": "internal", "pdfTitle": "DOM Selecting Elements",
                "overview": "JavaScript provides several methods to find HTML elements in the DOM tree. querySelector() is the most versatile, accepting any CSS selector and returning the first matching element (or null). querySelectorAll() returns a static NodeList of all matches. getElementById() is the fastest method for finding elements by their ID attribute, using an O(1) hash table lookup internally. getElementsByClassName() and getElementsByTagName() return live HTMLCollections that automatically update when the DOM changes. Understanding when to use static vs live collections, and how to convert NodeLists to arrays for array methods, is essential for effective DOM manipulation.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "[NOTE]", "content": "To interact with HTML elements using JavaScript, you first need to select them. querySelector() is the go-to method because it accepts any CSS selector you already know: IDs (#myId), classes (.myClass), tags (div), and complex selectors (div > p.intro). It returns the first matching element or null if nothing matches. querySelectorAll() finds ALL matching elements and returns a NodeList you can loop through with forEach(). getElementById() is fastest when you know the exact ID. Always check if your selection returned null before trying to modify the element, or you will get a TypeError.", "codeExample": "// querySelector: the most flexible selector\nconst header = document.querySelector('#main-header');\nconst firstBtn = document.querySelector('.btn-primary');\nconst firstPara = document.querySelector('article > p');\n\n// querySelectorAll: find ALL matches\nconst allCards = document.querySelectorAll('.card');\nconsole.log(allCards.length);  // number of cards\nallCards.forEach(card => {\n    console.log(card.textContent);\n});\n\n// getElementById: fastest for IDs\nconst nav = document.getElementById('navbar');\n\n// Always check for null!\nconst el = document.querySelector('.maybe-missing');\nif (el) {\n    el.textContent = 'Found it!';\n}"},
                    {"style": "logical", "title": "Logical", "icon": "[LOGIC]", "content": "document.querySelector(selector) performs a depth-first pre-order traversal of the DOM tree, matching against CSS selectors. It returns the first matching Element or null. querySelectorAll() returns a static NodeList (snapshot at call time, does not update). getElementById() uses an internal hash map for O(1) lookup by ID. getElementsByClassName() and getElementsByTagName() return live HTMLCollections that reflect DOM changes in real time. NodeList supports forEach() but not map() or filter() directly; convert with Array.from(nodeList) or [...nodeList] to use array methods. Scoped queries are possible: element.querySelector() searches only within that element's subtree.", "codeExample": "// Static vs live collections\nconst staticList = document.querySelectorAll('li');\nconst liveList = document.getElementsByTagName('li');\n\nconsole.log(staticList.length); // e.g., 5\nconsole.log(liveList.length);   // e.g., 5\n\n// Add a new <li> to the DOM\nconst newLi = document.createElement('li');\ndocument.querySelector('ul').appendChild(newLi);\n\nconsole.log(staticList.length); // still 5 (snapshot)\nconsole.log(liveList.length);   // now 6 (live!)\n\n// Convert NodeList to Array for array methods\nconst items = [...document.querySelectorAll('.item')];\nconst texts = items.map(el => el.textContent);\n\n// Scoped query: search within a specific element\nconst sidebar = document.querySelector('#sidebar');\nconst sideLinks = sidebar.querySelectorAll('a');"},
                    {"style": "visual", "title": "Visual", "icon": "[VISUAL]", "content": "DOM Tree:\n  document\n    |-- html\n         |-- head\n         |-- body\n              |-- div#header\n              |    |-- h1.title\n              |    |-- nav\n              |         |-- a.link\n              |         |-- a.link.active\n              |-- main\n                   |-- p\n                   |-- p.intro\n\nquerySelector('.link')       -> first a.link\nquerySelectorAll('.link')    -> NodeList[a.link, a.link.active]\nquerySelector('.link.active') -> a.link.active\nquerySelector('#header h1')  -> h1.title", "codeExample": "// Practical: highlight all links in a specific section\nconst nav = document.querySelector('nav');\nconst navLinks = nav.querySelectorAll('a');\n\nnavLinks.forEach((link, index) => {\n    console.log(`Link ${index}: ${link.href}`);\n});\n\n// Find elements by data attribute\nconst activeTab = document.querySelector('[data-tab=\"home\"]');\nconst allTabs = document.querySelectorAll('[data-tab]');\n\n// Complex CSS selectors work too\nconst el = document.querySelector(\n    'div.container > ul li:first-child'\n);"},
                    {"style": "analogy", "title": "Analogy", "icon": "[ANALOGY]", "content": "Selecting DOM elements is like using a spotlight on a theater stage. getElementById() is like calling an actor by their unique stage name: instant and precise, there is only one actor with that name. querySelector() is like describing the actor you want: 'the one wearing a red hat in the second row' (CSS selector). The spotlight crew searches the stage and finds the first match. querySelectorAll() tells the spotlight crew to find ALL actors matching your description and line them up. A live collection (getElementsByClassName) is a magic list that updates itself whenever actors join or leave the stage. A static NodeList is a photograph: it shows who was there when you took it.", "codeExample": "// Spotlight analogy: finding actors on stage\n\n// By unique name (ID) - instant\nconst hero = document.getElementById('protagonist');\n\n// By description (CSS selector) - first match\nconst villain = document.querySelector('.character.evil');\n\n// All matching the description\nconst allExtras = document.querySelectorAll('.extra');\nconsole.log(`${allExtras.length} extras on stage`);\n\n// Narrow the search to a specific scene\nconst scene2 = document.querySelector('#scene-2');\nconst scene2Actors = scene2.querySelectorAll('.character');"},
                ],
                "quiz": [
                    {"id": "q10-1-1", "question": "What does querySelector return if no match?", "options": ["undefined", "An empty element", "null", "An error"], "correctAnswer": 2},
                    {"id": "q10-1-2", "question": "What does querySelectorAll return?", "options": ["A single element", "An array", "A NodeList", "A string"], "correctAnswer": 2},
                    {"id": "q10-1-3", "question": "Which selector method is fastest for IDs?", "options": ["querySelector", "querySelectorAll", "getElementById", "getElementsByTagName"], "correctAnswer": 2},
                ],
                "recommendedVideos": [{"id": "vid-12", "title": "JavaScript DOM Crash Course", "language": "JavaScript", "youtubeId": "0ik6X4DJKCc", "thumbnail": "https://img.youtube.com/vi/0ik6X4DJKCc/mqdefault.jpg", "duration": "28:30"}],
            },
            {
                "id": "sub-10-2", "name": "Modifying Elements",
                "pdfUrl": "internal", "pdfTitle": "DOM Modifying Elements",
                "overview": "Once you have selected a DOM element, JavaScript lets you modify its content, styles, attributes, and CSS classes. textContent safely sets plain text (immune to XSS). innerHTML parses and sets HTML markup (use with caution as it can introduce XSS vulnerabilities if used with user input). The style property sets inline CSS styles. classList provides methods like add(), remove(), toggle(), and contains() for managing CSS classes cleanly. setAttribute() and getAttribute() work with any HTML attribute. The dataset property provides convenient access to data-* custom attributes. createElement() and appendChild() let you build and insert new elements into the DOM.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "[NOTE]", "content": "After selecting an element, you can change almost everything about it. textContent changes the text inside an element safely (it will not execute any HTML or scripts). innerHTML can set HTML markup inside an element, but be careful: never put user input directly into innerHTML or it could run malicious scripts (XSS attack). style lets you change CSS properties directly: el.style.backgroundColor = 'blue'. classList is the cleanest way to manage CSS classes: add(), remove(), toggle() a class on or off, and contains() to check if a class exists. createElement() builds new elements, and appendChild() or append() adds them to the page.", "codeExample": "const card = document.querySelector('.card');\n\n// Safe text change\ncard.textContent = 'Hello World!';\n\n// HTML change (be careful with user input!)\ncard.innerHTML = '<strong>Bold text</strong>';\n\n// Style changes\ncard.style.backgroundColor = '#1a1a2e';\ncard.style.padding = '20px';\ncard.style.borderRadius = '12px';\n\n// Class management (preferred over direct style)\ncard.classList.add('active', 'highlighted');\ncard.classList.remove('hidden');\ncard.classList.toggle('dark-mode');\nconsole.log(card.classList.contains('active')); // true\n\n// Create and append new elements\nconst badge = document.createElement('span');\nbadge.textContent = 'NEW';\nbadge.classList.add('badge');\ncard.appendChild(badge);"},
                    {"style": "logical", "title": "Logical", "icon": "[LOGIC]", "content": "textContent sets the text node content without HTML parsing, making it XSS-safe. innerHTML triggers the HTML parser and can execute scripts embedded in the markup, so never use it with unsanitized user input. innerText is similar to textContent but respects CSS visibility (slower due to layout computation). The style property accesses CSSStyleDeclaration for inline styles; camelCase is used (backgroundColor, not background-color). classList is a DOMTokenList supporting add(), remove(), toggle(class, force?), contains(), and replace(oldClass, newClass). setAttribute(name, value) and getAttribute(name) handle any HTML attribute. dataset provides a DOMStringMap for data-* attributes: data-user-id becomes element.dataset.userId.", "codeExample": "const el = document.querySelector('#profile');\n\n// Attributes\nel.setAttribute('role', 'button');\nel.setAttribute('aria-label', 'User profile');\nconsole.log(el.getAttribute('role')); // 'button'\n\n// Data attributes\nel.dataset.userId = '42';     // sets data-user-id=\"42\"\nel.dataset.status = 'active'; // sets data-status=\"active\"\nconsole.log(el.dataset.userId); // '42'\n\n// Building DOM elements programmatically\nconst ul = document.createElement('ul');\nconst fruits = ['Apple', 'Banana', 'Cherry'];\n\nfruits.forEach(fruit => {\n    const li = document.createElement('li');\n    li.textContent = fruit;\n    li.classList.add('fruit-item');\n    ul.appendChild(li);\n});\n\ndocument.querySelector('#list-container').appendChild(ul);"},
                    {"style": "visual", "title": "Visual", "icon": "[VISUAL]", "content": "Before modification:\n<div class=\"card\">\n  <p>Original text</p>\n</div>\n\nAfter el.textContent = 'New text':\n<div class=\"card\">New text</div>\n(all children replaced with text node)\n\nAfter el.innerHTML = '<p>New <b>HTML</b></p>':\n<div class=\"card\"><p>New <b>HTML</b></p></div>\n(HTML parsed and inserted)\n\nAfter el.classList.add('active'):\n<div class=\"card active\">...</div>\n\nAfter el.style.color = 'red':\n<div class=\"card active\" style=\"color: red;\">...</div>", "codeExample": "// Practical: toggle dark mode\nconst toggleBtn = document.querySelector('#theme-toggle');\nconst body = document.body;\n\ntoggleBtn.addEventListener('click', () => {\n    body.classList.toggle('dark-mode');\n    const isDark = body.classList.contains('dark-mode');\n    toggleBtn.textContent = isDark ? 'Light Mode' : 'Dark Mode';\n});\n\n// Practical: build a card dynamically\nfunction createCard(title, description) {\n    const card = document.createElement('div');\n    card.classList.add('card');\n\n    const h3 = document.createElement('h3');\n    h3.textContent = title;  // safe from XSS\n\n    const p = document.createElement('p');\n    p.textContent = description;\n\n    card.appendChild(h3);\n    card.appendChild(p);\n    return card;\n}"},
                    {"style": "analogy", "title": "Analogy", "icon": "[ANALOGY]", "content": "Modifying DOM elements is like customizing a puppet in a puppet show. textContent is changing what the puppet says (its dialogue). innerHTML is rewriting the puppet's entire script, which is powerful but dangerous if the script comes from an untrusted stranger (XSS). style is changing the puppet's costume directly: new hat, new color. classList is like adding or removing accessories: add a cape (classList.add), remove the mask (classList.remove), or toggle the hat on and off (classList.toggle). createElement and appendChild are building a brand new puppet and placing it on the stage next to the others.", "codeExample": "// Puppet customization analogy\nconst puppet = document.querySelector('.puppet');\n\n// Change dialogue (safe)\npuppet.textContent = 'Hello, audience!';\n\n// Change costume\npuppet.style.color = 'gold';\npuppet.style.fontSize = '24px';\n\n// Add accessories\npuppet.classList.add('cape', 'crown');\npuppet.classList.remove('mask');\npuppet.classList.toggle('hat');\n\n// Build a new puppet and add to stage\nconst newPuppet = document.createElement('div');\nnewPuppet.classList.add('puppet', 'villain');\nnewPuppet.textContent = 'I am the villain!';\ndocument.querySelector('#stage').appendChild(newPuppet);"},
                ],
                "quiz": [
                    {"id": "q10-2-1", "question": "Which is safer: textContent or innerHTML?", "options": ["innerHTML", "textContent", "Both are equal", "Neither is safe"], "correctAnswer": 1},
                    {"id": "q10-2-2", "question": "What does classList.toggle() do?", "options": ["Adds a class", "Removes a class", "Adds if absent, removes if present", "Clears all classes"], "correctAnswer": 2},
                    {"id": "q10-2-3", "question": "How do you change an element's background color?", "options": ["el.color = 'red'", "el.style.backgroundColor = 'red'", "el.bg = 'red'", "el.css('bg', 'red')"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-12", "title": "JavaScript DOM Crash Course", "language": "JavaScript", "youtubeId": "0ik6X4DJKCc", "thumbnail": "https://img.youtube.com/vi/0ik6X4DJKCc/mqdefault.jpg", "duration": "28:30"}],
            },
            {
                "id": "sub-10-3", "name": "Event Handling",
                "pdfUrl": "internal", "pdfTitle": "DOM Event Handling Guide",
                "overview": "Event handling is how JavaScript responds to user interactions like clicks, key presses, form submissions, and mouse movements. addEventListener(type, callback) attaches an event handler to an element. Events propagate through three phases: capture (top-down from document to target), target (the element itself), and bubble (bottom-up from target to document). Event delegation leverages bubbling by attaching a single listener to a parent element and using event.target to determine which child was clicked, which is far more efficient than attaching listeners to every child. event.preventDefault() stops the browser's default action (like form submission), and event.stopPropagation() prevents the event from bubbling further up.",
                "explanations": [
                    {"style": "simplified", "title": "Simplified", "icon": "[NOTE]", "content": "addEventListener lets you run a function when something happens to an element, like a click, key press, or form submission. The first argument is the event type ('click', 'input', 'submit', 'keydown'), and the second is your handler function that runs when the event fires. Events bubble up from the clicked element to its parents, which means a click on a button inside a div also triggers click handlers on the div. Event delegation takes advantage of this: instead of adding a click listener to every list item, add one listener to the parent ul and check event.target to see which item was clicked. Use event.preventDefault() to stop default browser behavior like following a link or submitting a form.", "codeExample": "// Basic click handler\nconst btn = document.querySelector('#myButton');\nbtn.addEventListener('click', function(event) {\n    console.log('Button clicked!');\n    console.log('Clicked element:', event.target);\n});\n\n// Form submit with preventDefault\nconst form = document.querySelector('#myForm');\nform.addEventListener('submit', (e) => {\n    e.preventDefault();  // stop page refresh\n    const name = form.querySelector('#name').value;\n    console.log('Form submitted:', name);\n});\n\n// Input event for real-time updates\nconst search = document.querySelector('#search');\nsearch.addEventListener('input', (e) => {\n    console.log('Typing:', e.target.value);\n});"},
                    {"style": "logical", "title": "Logical", "icon": "[LOGIC]", "content": "addEventListener(type, callback, options) attaches event handlers. The options parameter can be a boolean (useCapture) or an object {capture, once, passive}. Event propagation has three phases: capture (document to target), target phase, and bubble (target to document). event.stopPropagation() halts propagation. event.stopImmediatePropagation() also prevents other handlers on the same element. event.preventDefault() cancels the default browser action (navigation, form submit, text selection). Event delegation uses bubbling: attach one O(1) listener on a parent instead of O(n) listeners on children. Use event.target for the actual clicked element and event.currentTarget for the element the listener is on. removeEventListener requires the same function reference to detach.", "codeExample": "// Event delegation: one listener for many items\nconst todoList = document.querySelector('#todo-list');\n\ntodoList.addEventListener('click', (e) => {\n    if (e.target.classList.contains('delete-btn')) {\n        e.target.closest('li').remove();\n    }\n    if (e.target.classList.contains('todo-text')) {\n        e.target.classList.toggle('completed');\n    }\n});\n\n// Capture vs bubble phase\ndocument.querySelector('#outer').addEventListener('click',\n    () => console.log('Outer - capture'), true);\ndocument.querySelector('#inner').addEventListener('click',\n    () => console.log('Inner - bubble'));\n// Click inner: 'Outer - capture' then 'Inner - bubble'\n\n// {once: true} auto-removes after first trigger\nbtn.addEventListener('click', () => {\n    console.log('This only fires once!');\n}, {once: true});"},
                    {"style": "visual", "title": "Visual", "icon": "[VISUAL]", "content": "Event propagation phases:\n\n         document    (1) CAPTURE phase: top-down\n           |              document -> body -> div -> button\n          body\n           |         (2) TARGET phase: the clicked element\n          div              button fires its handlers\n           |\n         button      (3) BUBBLE phase: bottom-up\n       [CLICKED]          button -> div -> body -> document\n\nEvent delegation:\n  <ul id='list'>          <- ONE listener here\n    <li>Item 1</li>       <- click bubbles up to ul\n    <li>Item 2</li>       <- event.target tells us which li\n    <li>Item 3</li>\n  </ul>", "codeExample": "// Dynamic list with event delegation\nconst list = document.querySelector('#item-list');\nconst addBtn = document.querySelector('#add-item');\n\n// One listener handles ALL items (even future ones!)\nlist.addEventListener('click', (e) => {\n    const li = e.target.closest('li');\n    if (!li) return;\n\n    console.log('Clicked:', li.textContent);\n    li.classList.toggle('selected');\n});\n\n// Adding new items - they work automatically!\nlet count = 0;\naddBtn.addEventListener('click', () => {\n    const li = document.createElement('li');\n    li.textContent = `Item ${++count}`;\n    list.appendChild(li);\n    // No need to add a new event listener!\n});"},
                    {"style": "analogy", "title": "Analogy", "icon": "[ANALOGY]", "content": "Event handling is like a doorbell system in an apartment building. addEventListener is installing a doorbell (listener) on a specific door (element). When a visitor presses the doorbell (event occurs), your handler function answers. Event bubbling is like sound traveling: when someone rings Apartment 3A's bell, the sound travels up through the floor (parent elements) to the whole building. Event delegation is like having ONE security guard at the building entrance instead of a guard at every apartment door. The guard checks who the visitor wants to see (event.target) and handles it. This is much more efficient, especially when apartments (child elements) are constantly added or removed.", "codeExample": "// Building security analogy\n\n// BAD: guard at every door (inefficient)\nconst apartments = document.querySelectorAll('.apartment');\napartments.forEach(apt => {\n    apt.addEventListener('click', (e) => {\n        console.log('Visited:', apt.id);\n    });\n}); // O(n) listeners!\n\n// GOOD: one guard at the entrance (event delegation)\nconst building = document.querySelector('#building');\nbuilding.addEventListener('click', (e) => {\n    const apt = e.target.closest('.apartment');\n    if (apt) {\n        console.log('Visited:', apt.id);\n    }\n}); // O(1) listener!\n\n// Works for new apartments added later!\nconst newApt = document.createElement('div');\nnewApt.classList.add('apartment');\nnewApt.id = 'apt-new';\nbuilding.appendChild(newApt);"},
                ],
                "quiz": [
                    {"id": "q10-3-1", "question": "What does addEventListener do?", "options": ["Creates an element", "Attaches an event handler to an element", "Removes an element", "Modifies styles"], "correctAnswer": 1},
                    {"id": "q10-3-2", "question": "What is event delegation?", "options": ["Attaching listeners to every child", "Listening on a parent and checking the target", "Removing all events", "Creating custom events"], "correctAnswer": 1},
                    {"id": "q10-3-3", "question": "What does event.preventDefault() do?", "options": ["Stops event bubbling", "Prevents the default browser action", "Removes the listener", "Creates a new event"], "correctAnswer": 1},
                ],
                "recommendedVideos": [{"id": "vid-12", "title": "JavaScript DOM Crash Course", "language": "JavaScript", "youtubeId": "0ik6X4DJKCc", "thumbnail": "https://img.youtube.com/vi/0ik6X4DJKCc/mqdefault.jpg", "duration": "28:30"}],
            },
        ],
    },
]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# USERS (8 users with realistic progress)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
now = datetime.now()
def ts(days_ago=0): return (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")

USERS = [
    {
        "id": "user-1",
        "name": "Alex Johnson",
        "email": "alex@edutwin.com",
        "password": hash_pw("password123"),
        "completedTopics": ["topic-1", "topic-2", "topic-5", "topic-6", "topic-9", "topic-10"],
        "pendingTopics": ["topic-7"],
        "inProgressTopics": ["topic-3", "topic-4", "topic-8"],
        "videosWatched": [
            {"id": "vid-1", "title": "Python For Loops Tutorial", "language": "Python", "youtubeId": "6iF8Xb7Z3wQ", "thumbnail": "https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg", "duration": "12:30", "watchedAt": ts(2), "timeWatched": "12:30"},
            {"id": "vid-3", "title": "Java OOP Concepts Explained", "language": "Java", "youtubeId": "pTB0EiLXUC8", "thumbnail": "https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg", "duration": "18:20", "watchedAt": ts(5), "timeWatched": "18:20"},
            {"id": "vid-7", "title": "Python Data Structures Full Course", "language": "Python", "youtubeId": "8hly31xKli0", "thumbnail": "https://img.youtube.com/vi/8hly31xKli0/mqdefault.jpg", "duration": "25:00", "watchedAt": ts(8), "timeWatched": "25:00"},
        ],
        "totalScore": 185,
        "rank": 3,
        "preferredStyle": "visual",
        "confusionCount": 0,
        "createdAt": "2026-01-05",
        "quizScores": {"topic-1": 90, "topic-2": 80, "topic-5": 95, "topic-6": 85, "topic-9": 70, "topic-10": 90},
        "streak": 15,
        "totalHours": 42,
        "badges": [
            {"name": "First Quiz", "icon": "ðŸ…", "earned": True},
            {"name": "Week Streak", "icon": "ðŸ”¥", "earned": True},
            {"name": "Perfect Score", "icon": "â­", "earned": True},
            {"name": "Night Owl", "icon": "ðŸ¦‰", "earned": True},
            {"name": "Speed Demon", "icon": "âš¡", "earned": True},
            {"name": "Completionist", "icon": "ðŸ†", "earned": False},
        ],
        "languages": [
            {"name": "Python", "level": 85, "color": "bg-blue-500"},
            {"name": "Java", "level": 60, "color": "bg-orange-500"},
            {"name": "JavaScript", "level": 55, "color": "bg-yellow-500"},
            {"name": "SQL", "level": 70, "color": "bg-emerald-500"},
            {"name": "C", "level": 40, "color": "bg-gray-600"},
        ],
    },
    {
        "id": "user-2",
        "name": "Sarah Johnson",
        "email": "sarah@edutwin.com",
        "password": hash_pw("password456"),
        "completedTopics": ["topic-1", "topic-2", "topic-3", "topic-5", "topic-6", "topic-8", "topic-9", "topic-10"],
        "pendingTopics": [],
        "inProgressTopics": ["topic-4", "topic-7"],
        "videosWatched": [
            {"id": "vid-1", "title": "Python For Loops Tutorial", "language": "Python", "youtubeId": "6iF8Xb7Z3wQ", "thumbnail": "https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg", "duration": "12:30", "watchedAt": ts(1), "timeWatched": "12:30"},
        ],
        "totalScore": 245,
        "rank": 1,
        "preferredStyle": "logical",
        "confusionCount": 0,
        "createdAt": "2026-01-02",
        "quizScores": {"topic-1": 95, "topic-2": 90, "topic-3": 85, "topic-5": 100, "topic-6": 92, "topic-8": 88, "topic-9": 78, "topic-10": 95},
        "streak": 22,
        "totalHours": 68,
        "badges": [
            {"name": "First Quiz", "icon": "ðŸ…", "earned": True},
            {"name": "Week Streak", "icon": "ðŸ”¥", "earned": True},
            {"name": "Perfect Score", "icon": "â­", "earned": True},
            {"name": "Night Owl", "icon": "ðŸ¦‰", "earned": True},
            {"name": "Speed Demon", "icon": "âš¡", "earned": True},
            {"name": "Completionist", "icon": "ðŸ†", "earned": True},
        ],
        "languages": [
            {"name": "Python", "level": 95, "color": "bg-blue-500"},
            {"name": "Java", "level": 80, "color": "bg-orange-500"},
            {"name": "JavaScript", "level": 75, "color": "bg-yellow-500"},
            {"name": "SQL", "level": 85, "color": "bg-emerald-500"},
        ],
    },
    {
        "id": "user-3",
        "name": "Michael Chen",
        "email": "michael@edutwin.com",
        "password": hash_pw("password789"),
        "completedTopics": ["topic-1", "topic-2", "topic-4", "topic-5", "topic-6", "topic-7", "topic-8"],
        "pendingTopics": ["topic-10"],
        "inProgressTopics": ["topic-3", "topic-9"],
        "videosWatched": [],
        "totalScore": 220,
        "rank": 2,
        "preferredStyle": "simplified",
        "confusionCount": 0,
        "createdAt": "2026-01-08",
        "quizScores": {"topic-1": 85, "topic-2": 88, "topic-4": 92, "topic-5": 80, "topic-6": 90, "topic-7": 75, "topic-8": 82},
        "streak": 18,
        "totalHours": 55,
        "badges": [
            {"name": "First Quiz", "icon": "ðŸ…", "earned": True},
            {"name": "Week Streak", "icon": "ðŸ”¥", "earned": True},
            {"name": "Perfect Score", "icon": "â­", "earned": False},
            {"name": "Night Owl", "icon": "ðŸ¦‰", "earned": True},
            {"name": "Speed Demon", "icon": "âš¡", "earned": True},
            {"name": "Completionist", "icon": "ðŸ†", "earned": False},
        ],
        "languages": [
            {"name": "Python", "level": 78, "color": "bg-blue-500"},
            {"name": "Java", "level": 72, "color": "bg-orange-500"},
            {"name": "C", "level": 80, "color": "bg-gray-600"},
            {"name": "C++", "level": 65, "color": "bg-purple-500"},
            {"name": "SQL", "level": 82, "color": "bg-emerald-500"},
        ],
    },
    {
        "id": "user-4",
        "name": "Dharikha",
        "email": "dharikha@edutwin.com",
        "password": hash_pw("password123"),
        "completedTopics": ["topic-1", "topic-2", "topic-5", "topic-6"],
        "pendingTopics": ["topic-7", "topic-8", "topic-9", "topic-10"],
        "inProgressTopics": ["topic-3", "topic-4"],
        "videosWatched": [
            {"id": "vid-1", "title": "Python For Loops Tutorial", "language": "Python", "youtubeId": "6iF8Xb7Z3wQ", "thumbnail": "https://img.youtube.com/vi/6iF8Xb7Z3wQ/mqdefault.jpg", "duration": "12:30", "watchedAt": ts(1), "timeWatched": "12:30"},
            {"id": "vid-3", "title": "Java OOP Concepts Explained", "language": "Java", "youtubeId": "pTB0EiLXUC8", "thumbnail": "https://img.youtube.com/vi/pTB0EiLXUC8/mqdefault.jpg", "duration": "18:20", "watchedAt": ts(3), "timeWatched": "15:00"},
            {"id": "vid-8", "title": "SQL Tutorial for Beginners", "language": "SQL", "youtubeId": "HXV3zeQKqGY", "thumbnail": "https://img.youtube.com/vi/HXV3zeQKqGY/mqdefault.jpg", "duration": "30:00", "watchedAt": ts(5), "timeWatched": "28:00"},
        ],
        "totalScore": 165,
        "rank": 4,
        "preferredStyle": "visual",
        "confusionCount": 0,
        "createdAt": "2026-01-15",
        "quizScores": {"topic-1": 88, "topic-2": 76, "topic-5": 92, "topic-6": 84},
        "streak": 8,
        "totalHours": 34,
        "badges": [
            {"name": "First Quiz", "icon": "ðŸ…", "earned": True},
            {"name": "Week Streak", "icon": "ðŸ”¥", "earned": True},
            {"name": "Perfect Score", "icon": "â­", "earned": False},
            {"name": "Night Owl", "icon": "ðŸ¦‰", "earned": True},
            {"name": "Speed Demon", "icon": "âš¡", "earned": False},
            {"name": "Completionist", "icon": "ðŸ†", "earned": False},
        ],
        "languages": [
            {"name": "Python", "level": 78, "color": "bg-blue-500"},
            {"name": "Java", "level": 55, "color": "bg-orange-500"},
            {"name": "SQL", "level": 70, "color": "bg-emerald-500"},
            {"name": "JavaScript", "level": 25, "color": "bg-yellow-500"},
            {"name": "C", "level": 30, "color": "bg-gray-600"},
        ],
    },
    {
        "id": "user-5",
        "name": "Emily Davis",
        "email": "emily@edutwin.com",
        "password": hash_pw("password123"),
        "completedTopics": ["topic-1", "topic-3", "topic-5", "topic-10"],
        "pendingTopics": ["topic-4", "topic-7", "topic-8", "topic-9"],
        "inProgressTopics": ["topic-2", "topic-6"],
        "videosWatched": [],
        "totalScore": 155,
        "rank": 5,
        "preferredStyle": "analogy",
        "confusionCount": 0,
        "createdAt": "2026-01-20",
        "quizScores": {"topic-1": 82, "topic-3": 78, "topic-5": 88, "topic-10": 90},
        "streak": 5,
        "totalHours": 22,
        "badges": [
            {"name": "First Quiz", "icon": "ðŸ…", "earned": True},
            {"name": "Week Streak", "icon": "ðŸ”¥", "earned": False},
            {"name": "Perfect Score", "icon": "â­", "earned": False},
            {"name": "Night Owl", "icon": "ðŸ¦‰", "earned": False},
            {"name": "Speed Demon", "icon": "âš¡", "earned": True},
            {"name": "Completionist", "icon": "ðŸ†", "earned": False},
        ],
        "languages": [
            {"name": "Python", "level": 70, "color": "bg-blue-500"},
            {"name": "JavaScript", "level": 65, "color": "bg-yellow-500"},
        ],
    },
    {
        "id": "user-6",
        "name": "James Wilson",
        "email": "james@edutwin.com",
        "password": hash_pw("password123"),
        "completedTopics": ["topic-2", "topic-4", "topic-7", "topic-8"],
        "pendingTopics": ["topic-1", "topic-5", "topic-9", "topic-10"],
        "inProgressTopics": ["topic-3", "topic-6"],
        "videosWatched": [],
        "totalScore": 140,
        "rank": 6,
        "preferredStyle": "logical",
        "confusionCount": 0,
        "createdAt": "2026-01-22",
        "quizScores": {"topic-2": 75, "topic-4": 80, "topic-7": 72, "topic-8": 78},
        "streak": 3,
        "totalHours": 18,
        "badges": [
            {"name": "First Quiz", "icon": "ðŸ…", "earned": True},
            {"name": "Week Streak", "icon": "ðŸ”¥", "earned": False},
            {"name": "Perfect Score", "icon": "â­", "earned": False},
            {"name": "Night Owl", "icon": "ðŸ¦‰", "earned": True},
            {"name": "Speed Demon", "icon": "âš¡", "earned": False},
            {"name": "Completionist", "icon": "ðŸ†", "earned": False},
        ],
        "languages": [
            {"name": "Java", "level": 68, "color": "bg-orange-500"},
            {"name": "C", "level": 60, "color": "bg-gray-600"},
            {"name": "C++", "level": 55, "color": "bg-purple-500"},
        ],
    },
    {
        "id": "user-7",
        "name": "Priya Sharma",
        "email": "priya@edutwin.com",
        "password": hash_pw("password123"),
        "completedTopics": ["topic-1", "topic-5", "topic-6"],
        "pendingTopics": ["topic-3", "topic-4", "topic-7", "topic-8", "topic-9", "topic-10"],
        "inProgressTopics": ["topic-2"],
        "videosWatched": [],
        "totalScore": 120,
        "rank": 7,
        "preferredStyle": "visual",
        "confusionCount": 0,
        "createdAt": "2026-02-01",
        "quizScores": {"topic-1": 78, "topic-5": 82, "topic-6": 75},
        "streak": 6,
        "totalHours": 15,
        "badges": [
            {"name": "First Quiz", "icon": "ðŸ…", "earned": True},
            {"name": "Week Streak", "icon": "ðŸ”¥", "earned": True},
            {"name": "Perfect Score", "icon": "â­", "earned": False},
            {"name": "Night Owl", "icon": "ðŸ¦‰", "earned": False},
            {"name": "Speed Demon", "icon": "âš¡", "earned": False},
            {"name": "Completionist", "icon": "ðŸ†", "earned": False},
        ],
        "languages": [
            {"name": "Python", "level": 62, "color": "bg-blue-500"},
            {"name": "SQL", "level": 58, "color": "bg-emerald-500"},
        ],
    },
    {
        "id": "user-8",
        "name": "Daniel Kim",
        "email": "daniel@edutwin.com",
        "password": hash_pw("password123"),
        "completedTopics": ["topic-3", "topic-4", "topic-10"],
        "pendingTopics": ["topic-1", "topic-5", "topic-6", "topic-7", "topic-8", "topic-9"],
        "inProgressTopics": ["topic-2"],
        "videosWatched": [],
        "totalScore": 105,
        "rank": 8,
        "preferredStyle": "simplified",
        "confusionCount": 0,
        "createdAt": "2026-02-05",
        "quizScores": {"topic-3": 72, "topic-4": 68, "topic-10": 80},
        "streak": 2,
        "totalHours": 12,
        "badges": [
            {"name": "First Quiz", "icon": "ðŸ…", "earned": True},
            {"name": "Week Streak", "icon": "ðŸ”¥", "earned": False},
            {"name": "Perfect Score", "icon": "â­", "earned": False},
            {"name": "Night Owl", "icon": "ðŸ¦‰", "earned": False},
            {"name": "Speed Demon", "icon": "âš¡", "earned": False},
            {"name": "Completionist", "icon": "ðŸ†", "earned": False},
        ],
        "languages": [
            {"name": "JavaScript", "level": 58, "color": "bg-yellow-500"},
            {"name": "C", "level": 52, "color": "bg-gray-600"},
        ],
    },
]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# LEADERBOARD  (derived from users, sorted by totalScore)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
LEADERBOARD = sorted(
    [
        {
            "rank": 0,   # will be set after sorting
            "userId": u["id"],
            "name": u["name"],
            "score": u["totalScore"],
            "topicsCompleted": len(u["completedTopics"]),
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={u['name'].split()[0]}",
        }
        for u in USERS
    ],
    key=lambda x: x["score"],
    reverse=True,
)
for i, entry in enumerate(LEADERBOARD):
    entry["rank"] = i + 1

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# SEARCH HISTORY  (for user-4 = Dharikha, and user-1 = Alex)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SEARCH_HISTORY = [
    # Dharikha's searches
    {"userId": "user-4", "query": "Python decorators", "time": "2 hours ago"},
    {"userId": "user-4", "query": "JavaScript async await", "time": "5 hours ago"},
    {"userId": "user-4", "query": "SQL joins explained", "time": "Yesterday"},
    {"userId": "user-4", "query": "C pointer arithmetic", "time": "2 days ago"},
    {"userId": "user-4", "query": "Java collections tutorial", "time": "3 days ago"},
    # Alex's searches
    {"userId": "user-1", "query": "Python generators", "time": "2 hours ago"},
    {"userId": "user-1", "query": "Binary search tree", "time": "5 hours ago"},
    {"userId": "user-1", "query": "SQL joins explained", "time": "Yesterday"},
    {"userId": "user-1", "query": "C++ STL vector", "time": "3 days ago"},
]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# SEED FUNCTION
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def seed():
    print("ðŸŒ± Connecting to MongoDB â€¦")
    client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as e:
        print(f"âŒ Cannot connect to MongoDB: {e}")
        sys.exit(1)

    db = client[DB_NAME]

    # Drop existing collections for a clean start
    for col in ["users", "topics", "leaderboard", "search_history"]:
        db[col].drop()
        print(f"   ðŸ—‘  Dropped '{col}'")

    # Insert topics
    db.topics.insert_many(TOPICS)
    print(f"   âœ… Inserted {len(TOPICS)} topics")

    # Insert users  (use id as _id for easy lookup)
    for u in USERS:
        doc = {**u, "_id": u["id"]}
        db.users.insert_one(doc)
    print(f"   âœ… Inserted {len(USERS)} users")

    # Insert leaderboard
    db.leaderboard.insert_many(LEADERBOARD)
    print(f"   âœ… Inserted {len(LEADERBOARD)} leaderboard entries")

    # Insert search history
    db.search_history.insert_many(SEARCH_HISTORY)
    print(f"   âœ… Inserted {len(SEARCH_HISTORY)} search history entries")

    # Create indexes
    db.users.create_index("email", unique=True)
    db.topics.create_index("id", unique=True)
    db.search_history.create_index("userId")
    db.leaderboard.create_index("rank")
    print("   âœ… Indexes created")

    # Verify
    print("\nðŸ“Š Verification:")
    for col_name in ["users", "topics", "leaderboard", "search_history"]:
        count = db[col_name].count_documents({})
        print(f"   {col_name}: {count} documents")

    print("\nðŸŽ‰ Database seeded successfully!")
    print("\n   Credentials:")
    print("   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”")
    print("   â”‚ Email                      â”‚ Password      â”‚")
    print("   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤")
    print("   â”‚ dharikha@edutwin.com       â”‚ password123   â”‚")
    print("   â”‚ alex@edutwin.com           â”‚ password123   â”‚")
    print("   â”‚ sarah@edutwin.com          â”‚ password456   â”‚")
    print("   â”‚ michael@edutwin.com        â”‚ password789   â”‚")
    print("   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜")

    client.close()

if __name__ == "__main__":
    seed()
