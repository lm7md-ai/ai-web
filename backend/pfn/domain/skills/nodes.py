"""The shared Python skill graph.

Every world, curriculum module, mission, library page and professional task
references these nodes, so progression stays unified across the platform
instead of fragmenting per experience.

Each row is::

    (id, domain, level, title_ar, title_en, description_ar, description_en,
     prerequisites, related)
"""

from __future__ import annotations

from dataclasses import dataclass, field

# domain constants -----------------------------------------------------------
CORE = "python_core"
DS = "data_structures"
ALGO = "algorithms"
PRO = "professional"
ADV = "advanced_python"
DATA = "data_science"
SCI = "scientific_computing"
BACK = "backend"
ML = "machine_learning"
DL = "deep_learning"
AIE = "ai_engineering"
ROBO = "robotics"
RSCH = "research"
CAREER = "career_engineering"

_ROWS: list[tuple] = [
    # ---------------- Level 0 : recovery & diagnosis ------------------------
    ("recovery.syntax", CORE, 0, "قراءة كود بايثون", "Reading Python code",
     "قراءة وتتبع كود بايثون بسيط وفهم ترتيب التنفيذ.",
     "Read and trace simple Python code and predict execution order.", [], ["core.variables"]),
    ("recovery.functions", CORE, 0, "استدعاء الدوال", "Calling functions",
     "استدعاء دوال جاهزة وتمرير الوسائط وقراءة القيم المُعادة.",
     "Call existing functions, pass arguments and read return values.", [], ["core.functions"]),
    ("recovery.lists", CORE, 0, "التعامل مع القوائم", "Working with lists",
     "إنشاء القوائم والفهرسة والتعديل وتجنب أخطاء النسخ.",
     "Create, index, mutate lists and avoid copy pitfalls.", [], ["ds.lists"]),
    ("recovery.dicts", CORE, 0, "التعامل مع القواميس", "Working with dicts",
     "قراءة وكتابة القواميس والتعامل مع المفاتيح الناقصة.",
     "Read, write dicts and handle missing keys.", [], ["ds.dicts"]),
    ("recovery.loops", CORE, 0, "الحلقات التكرارية", "Loops",
     "استخدام for و while للتكرار على البيانات وجمع النتائج.",
     "Use for and while loops to iterate and accumulate results.", [], ["core.loops"]),
    ("recovery.debugging", CORE, 0, "تصحيح الأخطاء", "Debugging",
     "قراءة رسائل الخطأ وتحديد مكان الخلل وإصلاحه.",
     "Read tracebacks, locate defects and fix them.", ["recovery.syntax"], ["pro.debugging"]),

    # ---------------- Level 1 : foundations ---------------------------------
    ("core.variables", CORE, 1, "المتغيرات والأنواع", "Variables and types",
     "ربط الأسماء بالكائنات وفهم الأنواع الأساسية والتحويل بينها.",
     "Bind names to objects, understand core types and conversions.", [], ["core.operators"]),
    ("core.operators", CORE, 1, "العوامل", "Operators",
     "العوامل الحسابية والمقارنة والمنطقية وأولوياتها.",
     "Arithmetic, comparison and boolean operators plus precedence.", ["core.variables"], ["core.conditions"]),
    ("core.strings", CORE, 1, "النصوص", "Strings",
     "عمليات النصوص، التنسيق، التقطيع والترميز.",
     "String operations, formatting, slicing and encoding.", ["core.variables"], ["stdlib.re"]),
    ("core.conditions", CORE, 1, "الشروط", "Conditionals",
     "التفرع باستخدام if/elif/else والتعبيرات الشرطية.",
     "Branching with if/elif/else and conditional expressions.", ["core.operators"], ["core.loops"]),
    ("core.loops", CORE, 1, "الحلقات", "Loops",
     "for/while، break/continue/else والتكرار على النطاقات.",
     "for/while, break/continue/else and iterating ranges.", ["core.conditions"], ["ds.lists"]),
    ("core.functions", CORE, 1, "الدوال", "Functions",
     "تعريف الدوال، الوسائط، القيم الافتراضية وإرجاع القيم.",
     "Defining functions, parameters, defaults and returns.", ["core.conditions"], ["core.scope"]),
    ("core.io", CORE, 1, "الإدخال والإخراج", "Input and output",
     "الطباعة، قراءة المدخلات وتهيئة المخرجات.",
     "Printing, reading input and formatting output.", ["core.strings"], ["core.files"]),
    ("core.comments_style", CORE, 1, "أسلوب الكود", "Code style",
     "تسمية واضحة، تعليقات مفيدة وتنسيق متسق.",
     "Clear naming, useful comments and consistent formatting.", [], ["pro.refactoring"]),
    ("core.exceptions_basic", CORE, 1, "الأخطاء والاستثناءات", "Errors and exceptions",
     "التمييز بين أخطاء الصياغة والاستثناءات والتقاطها.",
     "Distinguish syntax errors from exceptions and handle them.", ["core.functions"], ["core.exceptions"]),
    ("core.files_basic", CORE, 1, "الملفات", "Files",
     "قراءة وكتابة الملفات النصية بأمان.",
     "Read and write text files safely.", ["core.io"], ["stdlib.pathlib"]),

    # ---------------- data structures ---------------------------------------
    ("ds.lists", DS, 1, "القوائم", "Lists",
     "القوائم كمتتاليات قابلة للتغيير، والتعقيد الزمني لعملياتها.",
     "Lists as mutable sequences and the cost of their operations.", ["core.loops"], ["ds.tuples"]),
    ("ds.tuples", DS, 1, "الصفوف", "Tuples",
     "الصفوف كسجلات ثابتة وتفريغ القيم.",
     "Tuples as immutable records and unpacking.", ["ds.lists"], ["ds.dicts"]),
    ("ds.dicts", DS, 1, "القواميس", "Dictionaries",
     "القواميس كخرائط hashable، get/setdefault والمرور عليها.",
     "Dicts as hash maps, get/setdefault and iteration.", ["ds.lists"], ["ds.sets"]),
    ("ds.sets", DS, 2, "المجموعات", "Sets",
     "المجموعات وعمليات الاتحاد والتقاطع وإزالة التكرار.",
     "Sets, union/intersection and de-duplication.", ["ds.dicts"], ["algo.hashing"]),
    ("ds.stacks_queues", DS, 2, "المكدسات والطوابير", "Stacks and queues",
     "بناء LIFO و FIFO وتطبيقاتها العملية.",
     "Build LIFO/FIFO structures and apply them.", ["ds.lists"], ["stdlib.deque", "algo.bfs"]),
    ("ds.linked_lists", DS, 2, "القوائم المترابطة", "Linked lists",
     "العقد والمؤشرات ومقارنة الأداء مع القوائم.",
     "Nodes, pointers and performance versus Python lists.", ["ds.lists"], ["algo.complexity"]),
    ("ds.trees", DS, 3, "الأشجار", "Trees",
     "أشجار البحث الثنائية والاجتياز والارتفاع.",
     "Binary search trees, traversal and height.", ["ds.linked_lists"], ["algo.backtracking"]),
    ("ds.heaps", DS, 3, "الكومات", "Heaps",
     "كومة ثنائية، الأولويات وتطبيقاتها.",
     "Binary heaps, priority queues and their uses.", ["ds.trees"], ["algo.dijkstra"]),
    ("ds.graphs", DS, 3, "الرسوم البيانية", "Graphs",
     "تمثيل الرسوم بالقواميس وقوائم الجيران.",
     "Represent graphs with dicts and adjacency lists.", ["ds.dicts"], ["algo.bfs"]),
    ("ds.hash_tables", DS, 3, "جداول التقطيع", "Hash tables",
     "التجزئة، التصادمات ولماذا القواميس سريعة.",
     "Hashing, collisions and why dicts are fast.", ["ds.dicts"], ["algo.hashing"]),
    ("ds.trie", DS, 4, "شجرة البادئات", "Tries",
     "بنية البادئات للبحث في النصوص.",
     "Prefix trees for text search and autocomplete.", ["ds.trees"], ["algo.dp"]),

    # ---------------- Level 2 : core mastery --------------------------------
    ("core.scope", CORE, 2, "النطاقات", "Scopes",
     "LEGB، global و nonlocal وأثرها على المتغيرات.",
     "LEGB rule, global/nonlocal and their effect on names.", ["core.functions"], ["adv.closures"]),
    ("core.mutability", CORE, 2, "القابلية للتغيير", "Mutability",
     "الكائنات القابلة وغير القابلة للتغيير وأثرها على النسخ.",
     "Mutable vs immutable objects and copy semantics.", ["ds.lists"], ["core.aliasing"]),
    ("core.aliasing", CORE, 2, "المشاركة بالمرجع", "Aliasing",
     "مشاركة الكائنات بين الأسماء وآثار التعديل المشترك.",
     "Shared references and the effect of shared mutation.", ["core.mutability"], ["adv.memory"]),
    ("core.args_kwargs", CORE, 2, "*args و **kwargs", "*args and **kwargs",
     "تمرير عدد متغير من الوسائط وتفريغها.",
     "Variable argument passing and unpacking.", ["core.functions"], ["adv.decorators"]),
    ("core.comprehensions", CORE, 2, "تعبيرات الاختصار", "Comprehensions",
     "قوائم/قواميس/مجموعات بالاختصار وتعبيرات المولدات.",
     "List/dict/set comprehensions and generator expressions.", ["ds.lists", "core.loops"], ["core.generators"]),
    ("core.iterators", CORE, 2, "المكررات", "Iterators",
     "بروتوكول المكرر، iter/next والتكرار الكسول.",
     "The iterator protocol, iter/next and lazy iteration.", ["core.functions"], ["core.generators"]),
    ("core.generators", CORE, 2, "المولدات", "Generators",
     "yield، الحالة المحفوظة وبناء خطوط أنابيب كسولة.",
     "yield, suspended state and lazy pipelines.", ["core.iterators"], ["stdlib.itertools"]),
    ("core.modules", CORE, 2, "الوحدات", "Modules",
     "الاستيراد، __name__ وتنظيم الكود في ملفات.",
     "Imports, __name__ and organising code into files.", ["core.files_basic"], ["core.packages"]),
    ("core.packages", CORE, 2, "الحزم", "Packages",
     "حزم متعددة الملفات، __init__ والاستيراد النسبي.",
     "Multi-file packages, __init__ and relative imports.", ["core.modules"], ["pro.pyproject"]),
    ("core.exceptions", CORE, 2, "الاستثناءات", "Exceptions",
     "try/except/else/finally، رفع استثناءات مخصصة وسلاسل الأخطاء.",
     "try/except/else/finally, custom exceptions and chaining.", ["core.exceptions_basic"], ["pro.logging"]),
    ("core.oop_basic", CORE, 2, "الكائنات (مقدمة)", "OOP basics",
     "الأصناف، الكائنات، الخصائص والطرق.",
     "Classes, instances, attributes and methods.", ["core.functions"], ["core.oop_composition"]),
    ("core.oop_composition", CORE, 2, "التركيب", "Composition",
     "تركيب الكائنات بدل الوراثة العميقة وتصميم الواجهات.",
     "Compose objects instead of deep inheritance hierarchies.", ["core.oop_basic"], ["arch.dependency_injection"]),
    ("core.inheritance", CORE, 2, "الوراثة", "Inheritance",
     "الوراثة، super، وتجاوز الطرق ومخاطرها.",
     "Inheritance, super(), method overriding and their risks.", ["core.oop_basic"], ["adv.abc"]),
    ("core.recursion_basic", CORE, 2, "الاستدعاء الذاتي", "Recursion",
     "الحالة الأساسية والخطوة العودية وحدود العمق.",
     "Base case, recursive step and recursion limits.", ["core.functions"], ["algo.recursion"]),
    ("core.files", CORE, 2, "الملفات والمسارات", "Files and paths",
     "مسارات محمولة، ترميز، وملفات سياقية.",
     "Portable paths, encodings and context managers.", ["core.files_basic"], ["stdlib.pathlib"]),
    ("core.json_basic", CORE, 2, "JSON", "JSON",
     "تحويل بين JSON وكائنات بايثون وحفظ الحالة.",
     "Serialize between JSON and Python objects; persist state.", ["core.files", "ds.dicts"], ["back.pydantic"]),

    # ---------------- algorithms --------------------------------------------
    ("algo.complexity", ALGO, 2, "تحليل التعقيد", "Complexity analysis",
     "Big-O عملياً وقياس الزمن الفعلي وتفسيره.",
     "Practical Big-O plus measuring and interpreting real timings.", ["core.loops"], ["algo.searching"]),
    ("algo.searching", ALGO, 2, "البحث", "Searching",
     "البحث الخطي والثنائي ومتى يصلح كل منهما.",
     "Linear and binary search and when each applies.", ["algo.complexity", "ds.lists"], ["algo.sorting"]),
    ("algo.sorting", ALGO, 2, "الترتيب", "Sorting",
     "فرز الفقاعات/الدمج/السريع ومقارنة فعليّة بالزمن.",
     "Bubble/merge/quick sort with real timing comparisons.", ["algo.searching"], ["algo.hashing"]),
    ("algo.hashing", ALGO, 3, "التجزئة", "Hashing",
     "دوال التجزئة، التصادمات وحلولها.",
     "Hash functions, collisions and resolution strategies.", ["algo.sorting"], ["ds.hash_tables"]),
    ("algo.recursion", ALGO, 3, "الاستدعاء الذاتي المتقدم", "Advanced recursion",
     "تتبع العودية، المكدس وتحويلها لتكرار.",
     "Tracing recursion, the call stack and converting to iteration.", ["core.recursion_basic"], ["algo.backtracking"]),
    ("algo.backtracking", ALGO, 3, "التراجع", "Backtracking",
     "بحث مع تراجع: المتاهات، N-Queens والتقليم.",
     "Backtracking search: mazes, N-Queens and pruning.", ["algo.recursion"], ["algo.dp"]),
    ("algo.dp", ALGO, 4, "البرمجة الديناميكية", "Dynamic programming",
     "التراكب، الحفظ والجدولة، وتحليل الذاكرة.",
     "Overlapping subproblems, memoisation and tabulation.", ["algo.recursion"], ["algo.greedy"]),
    ("algo.greedy", ALGO, 4, "الخوارزميات الجشعة", "Greedy algorithms",
     "الاختيار الجشع ومتى يفشل مقابل البرمجة الديناميكية.",
     "Greedy choice and when it fails versus DP.", ["algo.sorting"], ["algo.shortest_paths"]),
    ("algo.bfs", ALGO, 3, "البحث بالعرض", "BFS",
     "البحث بالعرض، أقصر مسار في رسم غير موزون.",
     "Breadth-first search and shortest paths in unweighted graphs.", ["ds.graphs", "ds.stacks_queues"], ["algo.dfs"]),
    ("algo.dfs", ALGO, 3, "البحث بالعمق", "DFS",
     "البحث بالعمق، اكتشاف الدوران والترتيب الطوبولوجي.",
     "Depth-first search, cycle detection and topological order.", ["ds.graphs"], ["algo.shortest_paths"]),
    ("algo.dijkstra", ALGO, 4, "خوارزمية ديكسترا", "Dijkstra",
     "أقصر مسار بالأوزان الموجبة مع كومة الأولويات.",
     "Shortest paths with non-negative weights using a heap.", ["algo.bfs", "ds.heaps"], ["robo.pathfinding"]),
    ("algo.shortest_paths", ALGO, 4, "أقصر المسارات", "Shortest paths",
     "مقارنة BFS/Dijkstra/Bellman-Ford من حيث الافتراضات.",
     "Compare BFS/Dijkstra/Bellman-Ford assumptions and costs.", ["algo.dijkstra"], ["robo.pathfinding"]),
    ("algo.benchmarking", ALGO, 4, "القياس والتقييم", "Benchmarking",
     "قياسات قابلة للتكرار، وتجنب الاستنتاجات الخاطئة.",
     "Repeatable measurement and avoiding misleading conclusions.", ["algo.complexity"], ["adv.profiling"]),

    # ---------------- standard library --------------------------------------
    ("stdlib.itertools", CORE, 3, "itertools", "itertools",
     "أدوات التكرار الفعّالة لبناء خطوط أنابيب.",
     "Efficient iterator building blocks and pipelines.", ["core.generators"], ["stdlib.functools"]),
    ("stdlib.functools", CORE, 3, "functools", "functools",
     "lru_cache، reduce و partial لتحسين الكود.",
     "lru_cache, reduce and partial for cleaner code.", ["core.functions"], ["adv.decorators"]),
    ("stdlib.collections", CORE, 2, "collections", "collections",
     "Counter، defaultdict، deque و namedtuple.",
     "Counter, defaultdict, deque and namedtuple.", ["ds.dicts"], ["stdlib.dataclasses"]),
    ("stdlib.dataclasses", CORE, 3, "dataclasses", "Dataclasses",
     "أصناف بيانات موجزة مع التحقق والترتيب.",
     "Concise data classes with validation and ordering.", ["core.oop_basic"], ["pro.typing"]),
    ("stdlib.re", CORE, 3, "التعبيرات النمطية", "Regular expressions",
     "مطابقة الأنماط، المجموعات والمطابقة الجشعة.",
     "Pattern matching, groups and greedy matching.", ["core.strings"], ["data.cleaning"]),
    ("stdlib.pathlib", CORE, 2, "pathlib", "pathlib",
     "مسارات كائنية محمولة بين الأنظمة.",
     "Object-oriented, cross-platform paths.", ["core.files"], ["pro.packaging"]),
    ("stdlib.datetime", CORE, 2, "التاريخ والوقت", "datetime",
     "التعامل مع الأوقات، الفترات والمناطق الزمنية.",
     "Dates, durations and timezone-aware handling.", ["core.variables"], ["data.timeseries"]),
    ("stdlib.random", CORE, 2, "العشوائية", "random",
     "توليد عشوائي قابل للتكرار بالبذور.",
     "Reproducible randomness with seeds.", ["core.variables"], ["sci.probability"]),
    ("stdlib.json_lib", CORE, 2, "وحدة json", "json module",
     "خيارات json.dumps/loads والتعامل مع الأنواع غير المدعومة.",
     "json.dumps/loads options and unsupported types.", ["core.json_basic"], ["back.pydantic"]),
    ("stdlib.subprocess_env", CORE, 3, "تشغيل العمليات", "Subprocesses",
     "تشغيل أوامر خارجية بأمان والتقاط مخرجاتها.",
     "Run external commands safely and capture output.", ["stdlib.pathlib"], ["pro.cicd"]),
    ("stdlib.sqlite", CORE, 3, "sqlite3", "sqlite3",
     "قاعدة بيانات مضمّنة، معاملات وحقن SQL.",
     "Embedded database, transactions and SQL injection.", ["core.files"], ["back.sqlalchemy"]),
    ("stdlib.deque", CORE, 2, "deque", "deque",
     "طوابير مزدوجة فعّالة من الطرفين.",
     "Efficient double-ended queues.", ["ds.stacks_queues"], ["algo.bfs"]),
    ("stdlib.heapq", CORE, 3, "heapq", "heapq",
     "كومات الأولوية باستخدام heapq.",
     "Priority queues with heapq.", ["ds.heaps"], ["algo.dijkstra"]),
    ("stdlib.math_stats", CORE, 2, "math و statistics", "math and statistics",
     "دوال رياضية وإحصائية من المكتبة القياسية.",
     "Math and statistics helpers from the standard library.", ["core.operators"], ["sci.probability"]),
    ("stdlib.argparse", CORE, 3, "argparse", "argparse",
     "واجهات سطر أوامر احترافية.",
     "Professional command-line interfaces.", ["core.functions"], ["pro.packaging"]),
    ("stdlib.logging_lib", CORE, 3, "logging", "Logging module",
     "تسجيل الأحداث بمستويات ومعالجات.",
     "Level-based event logging with handlers.", ["core.exceptions"], ["pro.logging"]),
    ("stdlib.unittest_pytest", CORE, 3, "pytest", "pytest",
     "كتابة اختبارات، التجهيزات والبارامترات.",
     "Writing tests, fixtures and parametrisation.", ["core.functions"], ["pro.testing"]),

    # ---------------- Level 3 : professional ---------------------------------
    ("pro.venv", PRO, 3, "البيئات الافتراضية", "Virtual environments",
     "عزل التبعيات لكل مشروع وتكرار البيئة.",
     "Per-project dependency isolation and reproducibility.", ["core.packages"], ["pro.packaging"]),
    ("pro.packaging", PRO, 3, "إدارة الحزم", "Package management",
     "pyproject.toml، التبعيات والإصدارات.",
     "pyproject.toml, dependencies and versioning.", ["pro.venv"], ["pro.pyproject"]),
    ("pro.pyproject", PRO, 3, "pyproject.toml", "pyproject.toml",
     "بيانات المشروع، نقاط الدخول وإعدادات الأدوات.",
     "Project metadata, entry points and tool config.", ["pro.packaging"], ["pro.build_backend"]),
    ("pro.build_backend", PRO, 4, "بناء الحزم", "Build backends",
     "بناء حزمة قابلة للتوزيع والتثبيت المحلي.",
     "Build a distributable package and install it locally.", ["pro.pyproject"], ["pro.cicd"]),
    ("pro.git_basics", PRO, 3, "Git", "Git basics",
     "الت commits، الفروع والسجل لفهم تاريخ المشروع.",
     "Commits, branches and history to understand a project timeline.", ["core.files"], ["pro.git_workflow"]),
    ("pro.git_workflow", PRO, 3, "سير العمل مع Git", "Git workflows",
     "الفروع، الدمج، وحل التعارضات.",
     "Branching, merging and resolving conflicts.", ["pro.git_basics"], ["career.code_review"]),
    ("pro.typing", PRO, 3, "التنميط", "Type hints",
     "تلميحات الأنواع، Generic والـ Protocols.",
     "Type hints, generics and protocols.", ["core.functions"], ["pro.typing_advanced"]),
    ("pro.typing_advanced", PRO, 4, "تنميط متقدم", "Advanced typing",
     "TypeVar، overload و TypeGuard لتصميم مكتبات آمنة.",
     "TypeVar, overload and TypeGuard for safe library design.", ["pro.typing"], ["adv.protocols"]),
    ("pro.testing", PRO, 3, "الاختبارات", "Testing",
     "اختبارات الوحدات والتكامل والتغطية.",
     "Unit and integration tests plus coverage.", ["stdlib.unittest_pytest"], ["pro.mocking"]),
    ("pro.mocking", PRO, 3, "المحاكاة", "Mocking",
     "monkeypatch وعزل الاعتماديات الخارجية.",
     "monkeypatch and isolating external dependencies.", ["pro.testing"], ["pro.property_testing"]),
    ("pro.property_testing", PRO, 4, "الاختبارات الخاصية", "Property-based testing",
     "اختبار الخصائص العامة بمدخلات مولّدة.",
     "Test invariants over generated inputs.", ["pro.testing"], ["rsch.reproducibility"]),
    ("pro.logging", PRO, 3, "التسجيل", "Logging",
     "تسجيل منظّم يدعم التشخيص في الإنتاج.",
     "Structured logging that supports production diagnosis.", ["core.exceptions"], ["back.observability"]),
    ("pro.config", PRO, 3, "الإعدادات", "Configuration",
     "إعدادات من البيئة والملفات دون أسرار في الكود.",
     "Environment/file configuration without secrets in code.", ["core.files"], ["sec.secrets"]),
    ("pro.docs", PRO, 3, "التوثيق", "Documentation",
     "docstrings و README يشرح قرار التصميم.",
     "Docstrings and a README explaining design decisions.", ["core.packages"], ["career.communication"]),
    ("pro.refactoring", PRO, 3, "إعادة التصميم", "Refactoring",
     "تحسين البنية دون تغيير السلوك، باختبارات حارسة.",
     "Improve structure without changing behaviour, guarded by tests.", ["core.comments_style", "pro.testing"], ["career.maintenance"]),
    ("pro.debugging", PRO, 3, "تصحيح متقدم", "Advanced debugging",
     "نقاط التوقف، التفتيش وتتبع الحالة.",
     "Breakpoints, inspection and state tracing.", ["recovery.debugging"], ["adv.pdb_trace"]),
    ("pro.cicd", PRO, 4, "CI/CD", "CI/CD",
     "أتمتة الفحص والاختبار قبل الدمج.",
     "Automate linting and testing before merge.", ["pro.testing", "pro.git_workflow"], ["career.delivery"]),
    ("pro.performance", PRO, 4, "الأداء", "Performance",
     "تحديد عنق الزجاجة بالقياس لا بالتخمين.",
     "Find bottlenecks by measurement, not guesswork.", ["algo.complexity"], ["adv.profiling"]),

    # ---------------- Level 4 : advanced python ------------------------------
    ("adv.closures", ADV, 4, "الإغلاقات", "Closures",
     "دوال تحمل بيئتها وحالات الاستخدام الحقيقية.",
     "Functions that capture their environment and real use cases.", ["core.scope"], ["adv.decorators"]),
    ("adv.decorators", ADV, 4, "المزخرفات", "Decorators",
     "كتابة مزخرفات مع الحفاظ على البيانات الوصفية.",
     "Write decorators that preserve metadata.", ["adv.closures", "core.args_kwargs"], ["adv.descriptors"]),
    ("adv.descriptors", ADV, 5, "الواصفات", "Descriptors",
     "بروتوكول الواصف وكيف تعمل property.",
     "The descriptor protocol and how property works.", ["adv.decorators"], ["adv.metaclasses"]),
    ("adv.metaclasses", ADV, 5, "الأصناف الوصفية", "Metaclasses",
     "type، __new__ ومتى تكون الأصناف الوصفية مبالغاً.",
     "type, __new__ and when metaclasses are overkill.", ["adv.descriptors"], ["adv.data_model"]),
    ("adv.data_model", ADV, 4, "نموذج بيانات بايثون", "Python data model",
     "البروتوكولات الخاصة وبناء كائنات تتصرف كالأنواع المدمجة.",
     "Dunder protocols and objects that behave like builtins.", ["core.oop_basic"], ["adv.context_managers"]),
    ("adv.context_managers", ADV, 4, "مديرات السياق", "Context managers",
     "with، __enter__/__exit__ و contextlib.",
     "with, __enter__/__exit__ and contextlib.", ["core.files"], ["adv.asyncio"]),
    ("adv.abc", ADV, 4, "الأصناف المجردة", "Abstract base classes",
     "تحديد العقود بالأصناف المجردة والبروتوكولات.",
     "Specify contracts with ABCs and protocols.", ["core.inheritance"], ["adv.protocols"]),
    ("adv.protocols", ADV, 4, "البروتوكولات", "Protocols",
     "التنميط الهيكلي للتصميم المرن.",
     "Structural typing for flexible design.", ["adv.abc", "pro.typing"], ["arch.dependency_injection"]),
    ("adv.memory", ADV, 5, "إدارة الذاكرة", "Memory management",
     "العدّ بالمراجع، التجميع الدوري وقياس الاستهلاك.",
     "Reference counting, cyclic GC and measuring usage.", ["core.aliasing"], ["adv.optimization"]),
    ("adv.bytecode", ADV, 5, "فحص البايت كود", "Bytecode inspection",
     "قراءة dis لفهم ما ينفّذه المفسّر فعلاً.",
     "Read dis output to see what the interpreter really runs.", ["adv.data_model"], ["adv.cpython"]),
    ("adv.cpython", ADV, 5, "مفاهيم CPython", "CPython internals",
     "GIL، الكائنات الصغيرة المسبقة وسلوك التنفيذ.",
     "GIL, small-object caching and execution behaviour.", ["adv.bytecode"], ["adv.concurrency"]),
    ("adv.asyncio", ADV, 5, "asyncio", "asyncio",
     "المهام، event loop وتجنب حجب الحلقة.",
     "Tasks, the event loop and avoiding blocking calls.", ["core.generators"], ["adv.concurrency"]),
    ("adv.threading", ADV, 5, "الخيوط", "Threading",
     "الخيوط، التزامن ومخاطر الحالة المشتركة.",
     "Threads, synchronisation and shared-state hazards.", ["adv.cpython"], ["adv.multiprocessing"]),
    ("adv.multiprocessing", ADV, 5, "تعدد المعالجات", "Multiprocessing",
     "تجاوز GIL بالعمليات ومقايضاتها.",
     "Bypassing the GIL with processes and its trade-offs.", ["adv.threading"], ["adv.concurrency"]),
    ("adv.concurrency", ADV, 5, "التزامن", "Concurrency",
     "اختيار النموذج الصحيح: خيوط، عمليات أم async.",
     "Choosing threads, processes or async correctly.", ["adv.asyncio"], ["back.architecture"]),
    ("adv.profiling", ADV, 5, "التنميط", "Profiling",
     "cProfile و line_profiler لقراءة أرقام حقيقية.",
     "cProfile and line-level timing on real numbers.", ["pro.performance"], ["adv.optimization"]),
    ("adv.optimization", ADV, 5, "التحسين", "Optimization",
     "تحسين مدفوع بالقياس مع حفظ الصحة.",
     "Measurement-driven optimisation without breaking correctness.", ["adv.profiling"], ["pro.performance"]),
    ("adv.pdb_trace", ADV, 4, "التتبع", "Tracing and pdb",
     "sys.settrace والمصحح لقراءة التنفيذ خطوة بخطوة.",
     "sys.settrace and pdb to read execution step by step.", ["pro.debugging"], ["adv.bytecode"]),

    # ---------------- architecture ------------------------------------------
    ("arch.dependency_injection", PRO, 4, "حقن الاعتماديات", "Dependency injection",
     "فصل البناء عن الاستخدام لقابلية الاختبار.",
     "Separate construction from use for testability.", ["core.oop_composition"], ["back.architecture"]),
    ("back.architecture", BACK, 4, "معمارية التطبيقات", "Application architecture",
     "طبقات، حدود وحدود الوحدات في تطبيق حقيقي.",
     "Layers, boundaries and module limits in a real app.", ["arch.dependency_injection"], ["career.maintenance"]),

    # ---------------- Level 5 : data & scientific computing ------------------
    ("data.numpy", DATA, 5, "NumPy", "NumPy",
     "المصفوفات، البثّ والعمليات المتجهة.",
     "Arrays, broadcasting and vectorised operations.", ["core.comprehensions"], ["data.numpy_advanced"]),
    ("data.numpy_advanced", DATA, 5, "NumPy متقدم", "Advanced NumPy",
     "الفهرسة المتقدمة، المحاور وإدارة الذاكرة.",
     "Advanced indexing, axes and memory layout.", ["data.numpy"], ["dl.tensors"]),
    ("data.pandas", DATA, 5, "Pandas", "Pandas",
     "DataFrame، الفهرسة والتجميع والانضمام.",
     "DataFrame, indexing, groupby and joins.", ["data.numpy"], ["data.cleaning"]),
    ("data.polars", DATA, 5, "Polars", "Polars",
     "إطارات بيانات عمودية وتعبيرات كسولة.",
     "Columnar frames and lazy expressions.", ["data.pandas"], ["data.pipelines"]),
    ("data.cleaning", DATA, 5, "تنظيف البيانات", "Data cleaning",
     "القيم المفقودة، الأنواع والتكرارات.",
     "Missing values, dtypes and duplicates.", ["data.pandas"], ["data.eda"]),
    ("data.eda", DATA, 5, "التحليل الاستكشافي", "Exploratory analysis",
     "إحصاءات وصفية وتلخيصات قبل النمذجة.",
     "Descriptive statistics and summaries before modelling.", ["data.cleaning"], ["sci.statistics"]),
    ("data.joins", DATA, 5, "الانضمام", "Joins and merges",
     "أنواع الانضمام ومضاعفة الصفوف.",
     "Join types and accidental row multiplication.", ["data.pandas"], ["data.pipelines"]),
    ("data.timeseries", DATA, 5, "السلاسل الزمنية", "Time series",
     "إعادة العينة، النوافذ والمؤشرات المتأخرة.",
     "Resampling, windows and lagging indicators.", ["stdlib.datetime", "data.pandas"], ["data.forecasting"]),
    ("data.forecasting", DATA, 6, "التنبؤ", "Forecasting",
     "خطوط أساس بسيطة وتقييم صادق للتنبؤ.",
     "Simple baselines and honest forecast evaluation.", ["data.timeseries"], ["ml.regression"]),
    ("data.pipelines", DATA, 6, "خطوط البيانات", "Data pipelines",
     "خطوات قابلة لإعادة التشغيل والتحقق.",
     "Restartable, verifiable transformation steps.", ["data.polars"], ["career.data_engineering"]),
    ("data.viz", DATA, 5, "التصور البياني", "Data visualization",
     "اختيار الرسم المناسب للسؤال المطروح.",
     "Choosing the right chart for the question.", ["data.eda"], ["sci.plotting"]),
    ("data.sql_analytics", DATA, 5, "تحليلات SQL", "SQL analytics",
     "تجميعات SQL ونوافذ للتحليل.",
     "SQL aggregation and window functions for analysis.", ["stdlib.sqlite"], ["back.sqlalchemy"]),

    # ---------------- scientific computing -----------------------------------
    ("sci.linalg", SCI, 5, "الجبر الخطي", "Linear algebra",
     "المتجهات، المصفوفات، القيم الذاتية والتحليلات.",
     "Vectors, matrices, eigenvalues and decompositions.", ["data.numpy"], ["dl.tensors"]),
    ("sci.calculus", SCI, 5, "التفاضل والتكامل", "Calculus",
     "المشتقات والتكاملات رمزياً وعددياً.",
     "Derivatives and integrals symbolically and numerically.", ["data.numpy"], ["ml.optimization_math"]),
    ("sci.probability", SCI, 5, "الاحتمالات", "Probability",
     "التوزيعات، التوقع والتباين والمحاكاة.",
     "Distributions, expectation, variance and simulation.", ["stdlib.random"], ["sci.statistics"]),
    ("sci.statistics", SCI, 5, "الإحصاء", "Statistics",
     "فترات الثقة، الاختبارات وتفسير النتائج.",
     "Confidence intervals, tests and interpretation.", ["sci.probability"], ["rsch.stats_comparison"]),
    ("sci.optimization_math", SCI, 6, "التحسين العددي", "Numerical optimization",
     "الانحدار التدريجي وطرق نيوتن وحدودها.",
     "Gradient descent, Newton methods and their limits.", ["sci.calculus"], ["ml.optimization_math"]),
    ("sci.simulation", SCI, 6, "المحاكاة العلمية", "Scientific simulation",
     "محاكاة أنظمة فيزيائية والتحقق من الثبات.",
     "Simulate physical systems and verify invariants.", ["sci.linalg"], ["robo.simulation"]),
    ("sci.plotting", SCI, 5, "الرسم العلمي", "Scientific plotting",
     "رسوم دقيقة مع محاور وunits واضحة.",
     "Accurate plots with labelled axes and units.", ["data.viz"], ["rsch.figures"]),

    # ---------------- Level 6 : backend --------------------------------------
    ("back.fastapi", BACK, 6, "FastAPI", "FastAPI",
     "مسارات، نماذج طلب/استجابة وحقن الاعتماديات.",
     "Routes, request/response models and dependencies.", ["pro.typing"], ["back.pydantic"]),
    ("back.pydantic", BACK, 6, "Pydantic", "Pydantic",
     "التحقق، التحليل والمحولات للبيانات الداخلة.",
     "Validation, parsing and serialisation at the boundary.", ["pro.typing"], ["back.api_design"]),
    ("back.sqlalchemy", BACK, 6, "SQLAlchemy", "SQLAlchemy",
     "نماذج، جلسات واستعلامات ORM.",
     "Models, sessions and ORM queries.", ["stdlib.sqlite"], ["back.migrations"]),
    ("back.migrations", BACK, 6, "ترحيلات قاعدة البيانات", "Database migrations",
     "تغيير المخطط بأمان وبشكل قابل للتراجع.",
     "Change schemas safely and reversibly.", ["back.sqlalchemy"], ["career.delivery"]),
    ("back.api_design", BACK, 6, "تصميم الـ API", "API design",
     "موارد، رموز حالة وأخطاء واضحة.",
     "Resources, status codes and clear errors.", ["back.fastapi"], ["back.auth_concepts"]),
    ("back.auth_concepts", BACK, 6, "المصادقة", "Authentication concepts",
     "تجزئة كلمات المرور، الرموز ومخاطر الجلسات.",
     "Password hashing, tokens and session risks.", ["back.api_design"], ["sec.threat_model"]),
    ("back.testing", BACK, 6, "اختبار الخدمات", "Testing services",
     "عملاء اختبار، قواعد بيانات مؤقتة وبيانات تجريبية.",
     "Test clients, temporary databases and fixtures.", ["pro.testing"], ["career.delivery"]),
    ("back.observability", BACK, 6, "المراقبة", "Observability",
     "مقاييس، سجلات وتتبع يكشف الأعطال.",
     "Metrics, logs and traces that reveal failures.", ["pro.logging"], ["career.incident_response"]),
    ("back.async_services", BACK, 6, "خدمات غير متزامنة", "Async services",
     "مسارات async ومهام خلفية دون حجب.",
     "Async endpoints and background tasks without blocking.", ["adv.asyncio", "back.fastapi"], ["adv.concurrency"]),

    # ---------------- Level 7 : machine learning -----------------------------
    ("ml.workflow", ML, 7, "سير عمل تعلم الآلة", "ML workflow",
     "من السؤال إلى التقييم دون تسريب بيانات.",
     "From question to evaluation without leakage.", ["data.eda"], ["ml.regression"]),
    ("ml.regression", ML, 7, "الانحدار", "Regression",
     "نماذج خطية ومقاييس الخطأ المناسبة.",
     "Linear models and appropriate error metrics.", ["ml.workflow"], ["ml.classification"]),
    ("ml.classification", ML, 7, "التصنيف", "Classification",
     "دقة/استرجاع/F1 ومنحنيات ROC.",
     "Precision/recall/F1 and ROC curves.", ["ml.regression"], ["ml.model_selection"]),
    ("ml.clustering", ML, 7, "التجميع", "Clustering",
     "k-means والتحقق من معنى العناقيد.",
     "k-means and checking whether clusters mean anything.", ["ml.workflow"], ["ml.feature_engineering"]),
    ("ml.feature_engineering", ML, 7, "هندسة الخصائص", "Feature engineering",
     "تحويلات، ترميز وتوسيع مدروس.",
     "Transforms, encoding and deliberate scaling.", ["data.cleaning"], ["ml.pipelines"]),
    ("ml.pipelines", ML, 7, "خطوط sklearn", "sklearn pipelines",
     "ربط الخطوات ومنع التسريب بينها.",
     "Chain steps and prevent leakage between them.", ["ml.feature_engineering"], ["ml.model_selection"]),
    ("ml.model_selection", ML, 7, "اختيار النموذج", "Model selection",
     "تحقق متقاطع وضبط معاملات نزيه.",
     "Cross-validation and honest hyper-parameter tuning.", ["ml.pipelines"], ["ml.evaluation"]),
    ("ml.evaluation", ML, 7, "التقييم", "Evaluation",
     "مقاييس، خطوط أساس وفترات ثقة.",
     "Metrics, baselines and confidence intervals.", ["ml.model_selection"], ["olympics.benchmarking"]),
    ("ml.leakage", ML, 7, "تسريب البيانات", "Data leakage",
     "اكتشاف التسريب وتصميم تقسيم سليم.",
     "Detect leakage and design sound splits.", ["ml.model_selection"], ["rsch.reproducibility"]),
    ("ml.optimization_math", ML, 7, "رياضيات التحسين", "Optimisation maths",
     "دوال الخسارة والانحدار التدريجي.",
     "Loss functions and gradient descent.", ["sci.optimization_math"], ["dl.autograd"]),

    # ---------------- Level 8 : deep learning --------------------------------
    ("dl.tensors", DL, 8, "الموترات", "Tensors",
     "موترات NumPy/PyTorch والأشكال والمحاور.",
     "NumPy/PyTorch tensors, shapes and axes.", ["data.numpy_advanced"], ["dl.autograd"]),
    ("dl.autograd", DL, 8, "الاشتقاق التلقائي", "Autograd",
     "بناء رسم حسابي وحساب التدرجات.",
     "Build a computation graph and backpropagate.", ["dl.tensors"], ["dl.nn"]),
    ("dl.nn", DL, 8, "الشبكات العصبية", "Neural networks",
     "طبقات، دوال تنشيط وتهيئة الأوزان.",
     "Layers, activations and weight initialisation.", ["dl.autograd"], ["dl.training"]),
    ("dl.training", DL, 8, "تدريب الشبكات", "Training loops",
     "دفعات، عهود، معدل تعلم وتشخيص التدريب.",
     "Batches, epochs, learning rate and diagnosis.", ["dl.nn"], ["dl.cnn"]),
    ("dl.cnn", DL, 8, "الشبكات الالتفافية", "CNNs",
     "الالتفاف، التجميع والرؤية الحاسوبية.",
     "Convolution, pooling and computer vision.", ["dl.training"], ["dl.nlp"]),
    ("dl.nlp", DL, 8, "معالجة اللغة", "NLP",
     "الترميز، التضمينات والنماذج المتسلسلة.",
     "Tokenisation, embeddings and sequence models.", ["dl.training"], ["dl.transformers"]),
    ("dl.transformers", DL, 9, "المحوّلات", "Transformers",
     "الانتباه، الترميز الموضعي والنماذج الجاهزة.",
     "Attention, positional encoding and pretrained models.", ["dl.nlp"], ["aie.embeddings"]),
    ("dl.inference", DL, 8, "الاستنتاج", "Inference",
     "تحسين زمن الاستجابة وقياس الاستهلاك.",
     "Serving efficiently and measuring latency/resources.", ["dl.training"], ["olympics.benchmarking"]),

    # ---------------- Level 9 : AI engineering -------------------------------
    ("aie.embeddings", AIE, 9, "التضمينات", "Embeddings",
     "تمثيل المتجهات وتشابه الجيب تمام.",
     "Vector representations and cosine similarity.", ["data.numpy"], ["aie.retrieval"]),
    ("aie.retrieval", AIE, 9, "الاسترجاع", "Retrieval",
     "فهرسة، بحث وتقييم جودة الاسترجاع.",
     "Indexing, search and evaluating retrieval quality.", ["aie.embeddings"], ["aie.rag"]),
    ("aie.rag", AIE, 9, "التوليد المعزز بالاسترجاع", "RAG",
     "بناء خط RAG وتقييم الإجابات والأدلة.",
     "Build a RAG pipeline and evaluate answers and evidence.", ["aie.retrieval"], ["agents.tool_calling"]),
    ("aie.llm_integration", AIE, 9, "تكامل النماذج اللغوية", "LLM integration",
     "استدعاء آمن، إعادة المحاولة والتحكم بالتكلفة.",
     "Safe calls, retries and cost control.", ["back.api_design"], ["agents.orchestration"]),
    ("aie.local_models", AIE, 9, "النماذج المحلية", "Local models",
     "تشغيل نماذج محلياً ومقايضات الخصوصية.",
     "Running models locally and privacy trade-offs.", ["aie.llm_integration"], ["olympics.benchmarking"]),
    ("aie.evaluation", AIE, 9, "تقييم النماذج اللغوية", "LLM evaluation",
     "مهام قياسية ومقاييس قابلة للتكرار.",
     "Standard tasks and repeatable metrics.", ["ml.evaluation"], ["olympics.benchmarking"]),
    ("aie.safety", AIE, 9, "أمان الأنظمة الذكية", "AI system safety",
     "حدود الأدوات، موافقة بشرية وتسجيل القرارات.",
     "Tool limits, human approval and decision logging.", ["sec.threat_model"], ["agents.permissions"]),

    # ---------------- agents --------------------------------------------------
    ("agents.tool_calling", AIE, 9, "استدعاء الأدوات", "Tool calling",
     "مخططات الأدوات وتحليل المخرجات المهيكلة.",
     "Tool schemas and parsing structured output.", ["aie.llm_integration", "core.json_basic"], ["agents.orchestration"]),
    ("agents.state", AIE, 9, "إدارة الحالة", "Agent state",
     "حالة دائمة، ذاكرة واستئناف بعد الفشل.",
     "Persistent state, memory and resuming after failure.", ["core.json_basic"], ["agents.orchestration"]),
    ("agents.planning", AIE, 9, "التخطيط", "Planning",
     "خطط متعددة الخطوات وتقييم البدائل.",
     "Multi-step plans and evaluating alternatives.", ["agents.tool_calling"], ["agents.orchestration"]),
    ("agents.orchestration", AIE, 9, "تنسيق سير العمل", "Workflow orchestration",
     "تنسيق خطوات مع إعادة المحاولة والمصادقة.",
     "Coordinate steps with retries and validation.", ["agents.state", "agents.planning"], ["agents.evaluation"]),
    ("agents.permissions", AIE, 9, "صلاحيات الأدوات", "Tool permissions",
     "أدنى صلاحية، موافقة بشرية وسجل تدقيق.",
     "Least privilege, human approval and an audit log.", ["aie.safety"], ["agents.evaluation"]),
    ("agents.multiagent", AIE, 10, "الوكلاء المتعددون", "Multi-agent systems",
     "بروتوكولات تواصل وتخصيص مهام.",
     "Communication protocols and task allocation.", ["agents.orchestration"], ["civ.cooperation"]),
    ("agents.evaluation", AIE, 9, "تقييم الوكلاء", "Agent evaluation",
     "معدل النجاح، التكلفة وتحليل الفشل.",
     "Success rate, cost and failure analysis.", ["agents.orchestration"], ["olympics.benchmarking"]),
    ("agents.observability", AIE, 9, "مراقبة الوكلاء", "Agent observability",
     "تتبع القرارات وأثر الأدوات.",
     "Trace decisions and tool effects.", ["agents.permissions"], ["back.observability"]),

    # ---------------- robotics / simulation -----------------------------------
    ("robo.control_flow", ROBO, 1, "التحكم بالروبوت", "Robot control flow",
     "برمجة حركة روبوت بشروط وحلقات.",
     "Program robot motion with conditions and loops.", ["core.loops"], ["robo.sensors"]),
    ("robo.sensors", ROBO, 2, "المستشعرات", "Sensors",
     "قراءة المستشعرات وبناء سلوك متفاعل.",
     "Read sensors and build reactive behaviour.", ["robo.control_flow"], ["robo.pathfinding"]),
    ("robo.pathfinding", ROBO, 4, "تخطيط المسار", "Pathfinding",
     "BFS/A* على شبكة وتجنب العوائق.",
     "BFS/A* on a grid with obstacle avoidance.", ["algo.bfs", "robo.sensors"], ["robo.coordination"]),
    ("robo.energy", ROBO, 3, "إدارة الطاقة", "Energy management",
     "ميزانية طاقة وقرارات تحت القيود.",
     "Energy budgets and decisions under constraints.", ["robo.sensors"], ["robo.coordination"]),
    ("robo.coordination", ROBO, 5, "تنسيق متعدد", "Multi-robot coordination",
     "تخصيص مهام وتجنب الاصطدام.",
     "Task allocation and collision avoidance.", ["robo.pathfinding", "robo.energy"], ["civ.scheduling"]),
    ("robo.rl", ROBO, 6, "تعلم معزز للروبوتات", "Robotics RL",
     "سياسات مكتسبة: المكافأة والاستكشاف.",
     "Learned policies: reward and exploration.", ["robo.pathfinding"], ["civ.rl"]),
    ("robo.simulation", ROBO, 3, "محاكاة الروبوتات", "Robot simulation",
     "نموذج حالة، خطوة زمنية وأحداث.",
     "State model, time step and event recording.", ["robo.control_flow"], ["civ.simulation"]),

    # ---------------- neural civilization -------------------------------------
    ("civ.agents", ROBO, 5, "الكيانات المستقلة", "Autonomous agents",
     "كيانات ذات حالة وسياسة خاصة.",
     "Stateful entities with their own policies.", ["robo.sensors"], ["civ.resource_allocation"]),
    ("civ.resource_allocation", ROBO, 5, "تخصيص الموارد", "Resource allocation",
     "استراتيجيات تخصيص عادلة وفعّالة.",
     "Fair and efficient allocation strategies.", ["civ.agents"], ["civ.scheduling"]),
    ("civ.scheduling", ROBO, 5, "الجدولة", "Scheduling",
     "جدولة مهام وقياس زمن الإنجاز.",
     "Schedule tasks and measure completion time.", ["civ.resource_allocation"], ["algo.greedy"]),
    ("civ.cooperation", ROBO, 6, "التعاون", "Cooperation",
     "بروتوكولات تعاون وقياس المنفعة الجماعية.",
     "Cooperation protocols and collective utility.", ["civ.resource_allocation"], ["agents.multiagent"]),
    ("civ.simulation", ROBO, 5, "محاكاة المجتمع", "Society simulation",
     "محاكاة حتمية قابلة للتكرار بالبذور.",
     "Deterministic, seed-reproducible simulation.", ["civ.agents"], ["rsch.reproducibility"]),
    ("civ.rl", ROBO, 7, "تعلم معزز متعدد", "Multi-agent RL",
     "مكافآت، استكشاف وتقارب السياسات.",
     "Rewards, exploration and policy convergence.", ["civ.cooperation"], ["dl.training"]),

    # ---------------- research ------------------------------------------------
    ("rsch.experiment_design", RSCH, 8, "تصميم التجارب", "Experiment design",
     "فرضية، متغيرات وضوابط واضحة.",
     "Hypothesis, variables and explicit controls.", ["sci.statistics"], ["rsch.stats_comparison"]),
    ("rsch.stats_comparison", RSCH, 8, "مقارنة إحصائية", "Statistical comparison",
     "مقارنة نماذج بفواصل ثقة واختبارات.",
     "Compare models with intervals and tests.", ["rsch.experiment_design"], ["rsch.reproducibility"]),
    ("rsch.reproducibility", RSCH, 8, "قابلية التكرار", "Reproducibility",
     "بذور، بيئة وتوثيق يسمح بإعادة النتائج.",
     "Seeds, environment and docs that allow re-running.", ["pro.config"], ["rsch.reporting"]),
    ("rsch.reporting", RSCH, 8, "كتابة التقرير", "Research reporting",
     "تمييز النتائج المُبلّغة عن المُعادة إنتاجها.",
     "Separate reported results from reproduced ones.", ["rsch.stats_comparison"], ["career.communication"]),
    ("rsch.figures", RSCH, 8, "الأشكال العلمية", "Research figures",
     "أشكال صادقة مع وحدات وهوامش خطأ.",
     "Honest figures with units and error bars.", ["sci.plotting"], ["rsch.reporting"]),
    ("olympics.benchmarking", RSCH, 8, "قياس الأداء", "Benchmarking",
     "مهام قياسية، تكرارات ومقارنة عادلة.",
     "Standard tasks, repeats and fair comparison.", ["ml.evaluation"], ["rsch.stats_comparison"]),

    # ---------------- security -------------------------------------------------
    ("sec.threat_model", PRO, 4, "نموذج التهديد", "Threat modelling",
     "تحديد الأصول، المهاجمين والحدود.",
     "Identify assets, attackers and boundaries.", ["pro.config"], ["sec.sandboxing"]),
    ("sec.secrets", PRO, 4, "إدارة الأسرار", "Secrets handling",
     "إبقاء الأسرار خارج الكود والمستودع.",
     "Keep secrets out of code and repositories.", ["pro.config"], ["back.auth_concepts"]),
    ("sec.sandboxing", PRO, 5, "العزل", "Sandboxing",
     "حدود الموارد عند تنفيذ كود غير موثوق.",
     "Resource limits when running untrusted code.", ["sec.threat_model", "stdlib.subprocess_env"], ["sec.input_validation"]),
    ("sec.input_validation", PRO, 4, "التحقق من المدخلات", "Input validation",
     "التحقق عند الحدود ومنع الحقن.",
     "Validate at boundaries and prevent injection.", ["back.pydantic"], ["back.auth_concepts"]),

    # ---------------- career engineering ----------------------------------------
    ("career.code_reading", CAREER, 6, "قراءة الكود", "Reading code",
     "فهم مستودع غير مألوف بسرعة ومنهجية.",
     "Understand an unfamiliar repository systematically.", ["core.packages"], ["career.code_review"]),
    ("career.code_review", CAREER, 6, "مراجعة الكود", "Code review",
     "مراجعة بناءة تركّز على المخاطر والوضوح.",
     "Constructive review focused on risk and clarity.", ["career.code_reading", "pro.git_workflow"], ["career.maintenance"]),
    ("career.maintenance", CAREER, 7, "صيانة المشاريع", "Maintenance",
     "إصلاح، تحديث تبعيات وحماية من الانحدار.",
     "Fixing, upgrading dependencies and preventing regressions.", ["career.code_review"], ["career.delivery"]),
    ("career.delivery", CAREER, 7, "التسليم", "Delivery",
     "تغيير صغير، اختبارات ووصف واضح للتغيير.",
     "Small change, tests and a clear change description.", ["career.maintenance"], ["career.communication"]),
    ("career.communication", CAREER, 6, "التواصل التقني", "Technical communication",
     "شرح المشكلة والحل والقيود بلغة دقيقة.",
     "Explain the problem, solution and limits precisely.", ["pro.docs"], ["rsch.reporting"]),
    ("career.incident_response", CAREER, 7, "الاستجابة للحوادث", "Incident response",
     "إعادة إنتاج العطل، تشخيصه وتثبيت الإصلاح.",
     "Reproduce, diagnose and lock the fix with a test.", ["career.maintenance", "back.observability"], ["career.delivery"]),
    ("career.data_engineering", CAREER, 7, "هندسة البيانات", "Data engineering",
     "خطوط بيانات موثوقة وقابلة للمراقبة.",
     "Reliable, observable data pipelines.", ["data.pipelines"], ["career.delivery"]),
]


@dataclass(frozen=True, slots=True)
class SkillNode:
    id: str
    domain: str
    level: int
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    prerequisites: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    evidence_required: int = 2

    def title(self, locale: str = "en") -> str:
        return self.title_ar if locale == "ar" else self.title_en

    def description(self, locale: str = "en") -> str:
        return self.description_ar if locale == "ar" else self.description_en

    def to_dict(self, locale: str = "en") -> dict:
        return {
            "id": self.id,
            "domain": self.domain,
            "level": self.level,
            "title": self.title(locale),
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "description": self.description(locale),
            "description_ar": self.description_ar,
            "description_en": self.description_en,
            "prerequisites": list(self.prerequisites),
            "related": list(self.related),
            "evidence_required": self.evidence_required,
        }


def _build() -> dict[str, SkillNode]:
    nodes: dict[str, SkillNode] = {}
    for row in _ROWS:
        (sid, domain, level, t_ar, t_en, d_ar, d_en, prereqs, related) = row
        nodes[sid] = SkillNode(
            id=sid,
            domain=domain,
            level=level,
            title_ar=t_ar,
            title_en=t_en,
            description_ar=d_ar,
            description_en=d_en,
            prerequisites=tuple(prereqs),
            related=tuple(related),
        )
    return nodes


NODES: dict[str, SkillNode] = _build()


def validate_graph() -> list[str]:
    """Return a list of structural problems (empty list means the graph is sound)."""
    problems: list[str] = []
    for node in NODES.values():
        for prereq in node.prerequisites:
            if prereq not in NODES:
                problems.append(f"{node.id}: unknown prerequisite {prereq}")
        for rel in node.related:
            if rel not in NODES:
                problems.append(f"{node.id}: unknown related skill {rel}")
        if node.id in node.prerequisites:
            problems.append(f"{node.id}: prerequisite cycle on itself")
    # cycle detection
    color: dict[str, int] = {nid: 0 for nid in NODES}

    def visit(nid: str, stack: list[str]) -> None:
        color[nid] = 1
        for prereq in NODES[nid].prerequisites:
            if prereq not in NODES:
                continue
            if color[prereq] == 0:
                visit(prereq, stack + [prereq])
            elif color[prereq] == 1:
                problems.append("cycle: " + " -> ".join(stack + [prereq]))
        color[nid] = 2

    for nid in NODES:
        if color[nid] == 0:
            visit(nid, [nid])
    return problems


def domains() -> list[str]:
    return sorted({node.domain for node in NODES.values()})


def by_domain(domain: str) -> list[SkillNode]:
    return sorted(
        (n for n in NODES.values() if n.domain == domain), key=lambda n: (n.level, n.id)
    )


def by_level(level: int) -> list[SkillNode]:
    return [n for n in NODES.values() if n.level == level]


def closure(skill_ids: list[str]) -> set[str]:
    """All prerequisites (transitively) required by the given skills."""
    out: set[str] = set()
    stack = list(skill_ids)
    while stack:
        current = stack.pop()
        if current in out or current not in NODES:
            continue
        out.add(current)
        stack.extend(NODES[current].prerequisites)
    return out
