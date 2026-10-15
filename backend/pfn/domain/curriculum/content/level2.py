"""LEVEL 2 - Core Python mastery."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l2.comprehensions",
        level=2,
        order_index=1,
        domain="python_core",
        title_ar="تعبيرات الاختصار",
        title_en="Comprehensions",
        summary_ar="بناء متتاليات وقواميس موجزة ومقروءة بدل حلقات مطوّلة.",
        summary_en="Building sequences and mappings concisely instead of with long loops.",
        explanation_ar="""تعبير الاختصار يبني متتالية جديدة من متتالية أخرى في سطر واحد مقروء:

```python
squares = [x * x for x in range(10)]
evens = [x for x in values if x % 2 == 0]
index = {word: len(word) for word in words}
unique = {name.lower() for name in names}
```

الصيغة العامة: `[تعبير for عنصر في متتالية if شرط]`.

قواعد عملية:
- إذا صار التعبير معقداً (أكثر من شرطين أو حلقة متداخلة) فالحلقة العادية أوضح.
- استخدم تعبير مولّد `(x for x in ...)` عندما تستهلك النتيجة مرة واحدة: لا يبني قائمة في الذاكرة.
- لا تستخدم الاختصار من أجل **آثار جانبية** (مثل `print`): استخدم حلقة for في هذه الحالة.

تعبير المولّد يُستهلك مرة واحدة ثم ينفد — خزّنه في قائمة إن احتجته مرتين.""",
        explanation_en="""A comprehension builds a new sequence from another in one readable line:

```python
squares = [x * x for x in range(10)]
evens = [x for x in values if x % 2 == 0]
index = {word: len(word) for word in words}
unique = {name.lower() for name in names}
```

The general shape is `[expression for item in sequence if condition]`.

Practical rules:
- When the expression gets complicated (more than two conditions, or nested loops), a plain loop is clearer.
- Use a generator expression `(x for x in ...)` when you consume the result once: it never builds a list in memory.
- Never use a comprehension for **side effects** (printing, appending elsewhere); use a `for` loop.

A generator expression is consumed once and then exhausted - materialise it into a list if you need it twice.""",
        skills=("core.comprehensions", "core.generators", "ds.dicts"),
        prerequisites=("l1.lists_tuples", "l1.dicts_sets"),
        example_code="""numbers = range(12)

squares = [n * n for n in numbers]
even_squares = [n * n for n in numbers if n % 2 == 0]
lengths = {word: len(word) for word in ["data", "ai", "nexus"]}
unique_first = {word[0] for word in ["apple", "avocado", "banana"]}

matrix = [[1, 2], [3, 4], [5, 6]]
flattened = [cell for row in matrix for cell in row]

total = sum(n * n for n in numbers)   # generator: nothing stored

print(squares)
print(even_squares)
print(lengths, sorted(unique_first))
print(flattened, total)
""",
        example_notes_ar="لاحظ ترتيب الحلقات في الاختصار المتداخل: من الخارج إلى الداخل كما في الحلقات العادية.",
        example_notes_en="Watch the loop order in the nested comprehension: outer to inner, exactly like nested for loops.",
        experiment_code="""import sys

values = list(range(100000))

list_version = [v * 2 for v in values]
gen_version = (v * 2 for v in values)

print("list bytes:", sys.getsizeof(list_version))
print("generator bytes:", sys.getsizeof(gen_version))

# A generator can only be consumed once:
total = sum(gen_version)
again = sum(gen_version)
print("first pass:", total, "| second pass:", again)
""",
        experiment_brief_ar="لماذا كانت الحصة الثانية صفراً؟ اكتب تعليقاً يشرح متى تختار المولّد ومتى تختار القائمة.",
        experiment_brief_en="Why was the second pass zero? Write a comment explaining when to pick a generator and when a list.",
        task=TaskSpec(
            brief_ar="""اكتب `square_dict(values)` تُعيد قاموساً يربط كل رقم بمربّعه، متجاهلة القيم السالبة.

ثم اكتب `transpose(matrix)` تُعيد مصفوفة مقلوبة (الصفوف تصبح أعمدة) باستخدام تعبير اختصار
متداخل واحد. مثال: `[[1, 2], [3, 4]]` → `[[1, 3], [2, 4]]`.""",
            brief_en="""Write `square_dict(values)` returning a dict mapping each number to its square, skipping
negative values.

Then write `transpose(matrix)` returning the transposed matrix (rows become columns) using a
single nested comprehension. Example: `[[1, 2], [3, 4]]` -> `[[1, 3], [2, 4]]`.""",
            starter_code="""def square_dict(values):
    # TODO: {value: value ** 2} for non-negative values
    pass


def transpose(matrix):
    # TODO: nested comprehension
    pass
""",
            public_tests={
                "test_public.py": """from main import square_dict, transpose

def test_square_dict():
    assert square_dict([1, 2, 3]) == {1: 1, 2: 4, 3: 9}

def test_transpose():
    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]
"""},
            hidden_tests={
                "test_hidden.py": """from main import square_dict, transpose

def test_negatives_skipped():
    assert square_dict([-3, 0, 4]) == {0: 0, 4: 16}

def test_empty():
    assert square_dict([]) == {}

def test_transpose_rectangular():
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]

def test_transpose_empty_and_single():
    assert transpose([]) == []
    assert transpose([[1, 2]]) == [[1], [2]]

def test_transpose_round_trip():
    matrix = [[1, 2, 3], [4, 5, 6]]
    assert transpose(transpose(matrix)) == matrix
"""},
            reference_solution="""def square_dict(values):
    return {value: value ** 2 for value in values if value >= 0}


def transpose(matrix):
    if not matrix:
        return []
    return [[row[column] for row in matrix] for column in range(len(matrix[0]))]
""",
            hints=(
                "The comprehension condition goes at the end: `for value in values if value >= 0`.",
                "For transpose, the outer comprehension walks columns and the inner one walks rows.",
                "Guard the empty matrix so `len(matrix[0])` is never evaluated on nothing.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `group_lengths(words)` تُعيد قاموساً يربط طول الكلمة بقائمة كلماتها (مرتبة أبجدياً).

ثم اكتب `lazy_squares(limit)` تُعيد **مولّداً** (استخدم `yield`) ينتج المربّعات من 0 حتى `limit`,
وتحقق أن استهلاكه مرتين غير ممكن دون إعادة إنشائه.""",
            brief_en="""Write `group_lengths(words)` returning a dict mapping word length to its words (sorted
alphabetically).

Then write `lazy_squares(limit)` returning a **generator** (use `yield`) producing squares from
0 up to `limit`.""",
            independent=True,
            starter_code="""def group_lengths(words):
    pass


def lazy_squares(limit):
    pass
""",
            public_tests={"test_public.py": """from main import group_lengths, lazy_squares

def test_group_lengths():
    assert group_lengths(["b", "a", "cc"]) == {1: ["a", "b"], 2: ["cc"]}

def test_lazy_squares():
    assert list(lazy_squares(3)) == [0, 1, 4, 9]
"""},
            hidden_tests={"test_hidden.py": """from main import group_lengths, lazy_squares
import types

def test_group_lengths_empty():
    assert group_lengths([]) == {}

def test_group_sorted():
    result = group_lengths(["z", "a", "m"])
    assert result[1] == ["a", "m", "z"]

def test_is_generator():
    gen = lazy_squares(3)
    assert isinstance(gen, types.GeneratorType)

def test_generator_is_lazy_and_exhausts():
    gen = lazy_squares(2)
    assert next(gen) == 0
    assert list(gen) == [1, 4]
    assert list(gen) == []

def test_zero_limit():
    assert list(lazy_squares(0)) == [0]
"""},
            reference_solution="""def group_lengths(words):
    groups = {}
    for word in words:
        groups.setdefault(len(word), []).append(word)
    return {length: sorted(items) for length, items in groups.items()}


def lazy_squares(limit):
    for value in range(limit + 1):
        yield value * value
""",
        ),
        transfer_ar="استخدم المولّدات في Data Empire لمعالجة ملف ضخم سطراً بسطر دون تحميله كاملاً.",
        transfer_en="Use generators in Data Empire to process a large file line by line without loading it all.",
        references=(
            ("Python tutorial - list comprehensions", "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions"),
            ("Python howto - functional programming", "https://docs.python.org/3/howto/functional.html"),
        ),
    ),
    CurriculumModule(
        id="l2.iterators_generators",
        level=2,
        order_index=2,
        domain="python_core",
        title_ar="المكررات والمولدات",
        title_en="Iterators and generators",
        summary_ar="بروتوكول التكرار، `yield`، وبناء خطوط أنابيب كسولة.",
        summary_en="The iterator protocol, `yield`, and lazy pipelines.",
        explanation_ar="""كل حلقة `for` في بايثون تعمل عبر **بروتوكول المكرر**:

1. `iter(obj)` يستدعي `obj.__iter__()` ويُعيد مكرّراً.
2. `next(iterator)` يستدعي `__next__()` ويُعيد العنصر التالي.
3. عندما تنفد العناصر يرفع المكرّر `StopIteration` فتنتهي الحلقة.

المولّد دالة تحتوي `yield`: عند استدعائها لا تنفّذ شيئاً بل تُعيد مكرّراً،
ويتوقف تنفيذها عند كل `yield` حتى الطلب التالي. هذا يجعلها مناسبة للبيانات الكبيرة
والسلاسل اللانهائية.

أدوات من `itertools`: `islice` و`chain` و`takewhile` و`accumulate` و`groupby`.
استخدم `yield from` لتفويض التكرار إلى مولّد آخر.""",
        explanation_en="""Every `for` loop in Python runs on the **iterator protocol**:

1. `iter(obj)` calls `obj.__iter__()` and returns an iterator.
2. `next(iterator)` calls `__next__()` and yields the next item.
3. When items run out the iterator raises `StopIteration`, ending the loop.

A generator is a function containing `yield`: calling it runs nothing and returns an
iterator; execution suspends at each `yield` until the next request. That makes
generators ideal for large data and infinite streams.

Useful `itertools` tools: `islice`, `chain`, `takewhile`, `accumulate`, `groupby`.
Use `yield from` to delegate iteration to another generator.""",
        skills=("core.iterators", "core.generators", "stdlib.itertools"),
        prerequisites=("l2.comprehensions",),
        example_code="""from itertools import islice, accumulate, count

class Countdown:
    \"\"\"A hand-written iterator: __iter__ + __next__.\"\"\"

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


print(list(Countdown(4)))

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

print(list(islice(fibonacci(), 8)))
print(list(accumulate([1, 2, 3, 4])))          # running totals
print(list(islice(count(10, 5), 4)))           # infinite arithmetic sequence
""",
        example_notes_ar="`fibonacci()` مولّد لا نهائي: `islice` هو ما يحدّد عدد العناصر المستهلكة.",
        example_notes_en="`fibonacci()` is an infinite generator; `islice` decides how many items to consume.",
        experiment_code="""def read_events(events):
    \"\"\"A lazy pipeline: filter -> transform -> take.\"\"\"
    for event in events:
        if event.get("type") == "error":
            yield {"message": event.get("message", "").upper(), "code": event.get("code", 0)}


def take(iterator, n):
    for index, value in enumerate(iterator):
        if index >= n:
            return
        yield value


events = [
    {"type": "info", "message": "started"},
    {"type": "error", "message": "disk full", "code": 507},
    {"type": "error", "message": "timeout", "code": 504},
]
print(list(take(read_events(events), 5)))
""",
        experiment_brief_ar="وسّع خط الأنابيب: أضف مرحلة تحسب عدد الأخطاء ومرحلة تجمّع الرسائل في قائمة.",
        experiment_brief_en="Extend the pipeline: add a stage counting errors and a stage collecting the messages.",
        task=TaskSpec(
            brief_ar="""اكتب `evens_up_to(limit)` كمولّد ينتج الأعداد الزوجية من 0 إلى `limit` ضمناً.

ثم اكتب `windowed(values, size)` كمولّد ينتج قوائم متتالية بطول `size`:
`windowed([1,2,3,4], 2)` → `[1,2]`, `[2,3]`, `[3,4]`. إذا كان `size` أكبر من طول القائمة
فلا ينتج شيئاً.""",
            brief_en="""Write `evens_up_to(limit)` as a generator yielding even numbers from 0 up to and including
`limit`.

Then write `windowed(values, size)` as a generator yielding consecutive slices of length
`size`: `windowed([1,2,3,4], 2)` -> `[1,2]`, `[2,3]`, `[3,4]`. Yield nothing when `size`
exceeds the length.""",
            starter_code="""def evens_up_to(limit):
    # TODO: generator of even numbers
    pass


def windowed(values, size):
    # TODO: generator of sliding windows
    pass
""",
            public_tests={
                "test_public.py": """from main import evens_up_to, windowed

def test_evens():
    assert list(evens_up_to(6)) == [0, 2, 4, 6]

def test_windowed():
    assert list(windowed([1, 2, 3], 2)) == [[1, 2], [2, 3]]
"""},
            hidden_tests={
                "test_hidden.py": """from main import evens_up_to, windowed
import types

def test_generators_not_lists():
    assert isinstance(evens_up_to(4), types.GeneratorType)
    assert isinstance(windowed([1, 2], 1), types.GeneratorType)

def test_evens_edge():
    assert list(evens_up_to(1)) == [0]
    assert list(evens_up_to(0)) == [0]

def test_windowed_size_one_and_all():
    assert list(windowed([1, 2], 1)) == [[1], [2]]
    assert list(windowed([1, 2], 2)) == [[1, 2]]

def test_windowed_too_big():
    assert list(windowed([1, 2], 5)) == []
    assert list(windowed([], 1)) == []

def test_windowed_lazy():
    gen = windowed([1, 2, 3], 2)
    assert next(gen) == [1, 2]
    assert next(gen) == [2, 3]
    try:
        next(gen)
    except StopIteration:
        pass
    else:
        raise AssertionError("generator should stop")
"""},
            reference_solution="""def evens_up_to(limit):
    for value in range(0, limit + 1, 2):
        yield value


def windowed(values, size):
    if size <= 0 or size > len(values):
        return
    for index in range(len(values) - size + 1):
        yield list(values[index:index + size])
""",
            hints=(
                "Use `range(0, limit + 1, 2)` and yield each value.",
                "The number of windows is `len(values) - size + 1`.",
                "A bare `return` inside a generator stops it immediately (no items).",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب صنف `Ring` يُمثّل حلقة ثابتة السعة قابلة للتكرار:
- `Ring(capacity)` ينشئ حلقة فارغة،
- `push(item)` يضيف عنصراً، وعند الامتلاء يُزال الأقدم،
- `__iter__` يمرّر العناصر من الأقدم إلى الأحدث،
- `__len__` يُعيد عدد العناصر الحالية.""",
            brief_en="""Write a `Ring` class representing a fixed-capacity ring buffer that is iterable:
- `Ring(capacity)` creates an empty buffer,
- `push(item)` adds an item, discarding the oldest when full,
- `__iter__` walks items from oldest to newest,
- `__len__` returns the current number of items.""",
            independent=True,
            starter_code="""class Ring:
    def __init__(self, capacity):
        pass

    def push(self, item):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass
""",
            public_tests={"test_public.py": """from main import Ring

def test_basic():
    ring = Ring(3)
    ring.push(1); ring.push(2)
    assert list(ring) == [1, 2]
    assert len(ring) == 2
"""},
            hidden_tests={"test_hidden.py": """from main import Ring

def test_overflow_discards_oldest():
    ring = Ring(2)
    for value in (1, 2, 3):
        ring.push(value)
    assert list(ring) == [2, 3]

def test_reusable_iterator():
    ring = Ring(2)
    ring.push(1)
    assert list(ring) == [1]
    assert list(ring) == [1]      # iterating twice must work

def test_empty():
    ring = Ring(3)
    assert list(ring) == []
    assert len(ring) == 0

def test_capacity_one():
    ring = Ring(1)
    ring.push("a"); ring.push("b")
    assert list(ring) == ["b"]
"""},
            reference_solution="""from collections import deque


class Ring:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._items = deque(maxlen=capacity)

    def push(self, item):
        self._items.append(item)

    def __iter__(self):
        return iter(list(self._items))

    def __len__(self):
        return len(self._items)
""",
        ),
        transfer_ar="استخدم نافذة منزلقة في Reality Twin لتحليل متوسط سبعة أيام.",
        transfer_en="Use a sliding window in Reality Twin to analyse a seven-day moving average.",
        references=(
            ("Python docs - iterator types", "https://docs.python.org/3/library/stdtypes.html#iterator-types"),
            ("Python docs - itertools", "https://docs.python.org/3/library/itertools.html"),
        ),
    ),
    CurriculumModule(
        id="l2.scope_closures",
        level=2,
        order_index=3,
        domain="python_core",
        title_ar="النطاقات والإغلاقات",
        title_en="Scopes and closures",
        summary_ar="قاعدة LEGB و`nonlocal` وكيف تحمل الدالة بيئتها معها.",
        summary_en="The LEGB rule, `nonlocal`, and how a function carries its environment.",
        explanation_ar="""عند الإشارة إلى اسم يبحث بايثون بالترتيب: **L**ocal ثم **E**nclosing ثم **G**lobal ثم **B**uiltins (قاعدة LEGB).

- المتغير المعرّف داخل دالة محلي ما لم تُعلنه `global` أو `nonlocal`.
- القراءة من النطاق الخارجي تعمل؛ **التعديل** يحتاج `nonlocal` (للنطاق المغلِّف) أو `global`.
- **الإغلاق** (closure): دالة داخلية تتذكر متغيرات النطاق المغلِّف بعد انتهاء الدالة الخارجية.

فخ مشهور في الحلقات: الإغلاقات تلتقط **المتغير** لا القيمة،
لذا لحظة الاستدعاء تُقرأ القيمة الأخيرة. الحل: مرّر القيمة كوسيط افتراضي
`lambda x=value: ...` أو استخدم `functools.partial`.""",
        explanation_en="""When resolving a name, Python searches: **L**ocal, **E**nclosing, **G**lobal,
**B**uiltins (the LEGB rule).

- A variable assigned inside a function is local unless declared `global` or `nonlocal`.
- Reading from an outer scope works; **rebinding** needs `nonlocal` (enclosing scope) or `global`.
- A **closure** is an inner function that remembers the enclosing scope's variables after
  the outer function has returned.

A famous loop trap: closures capture the **variable**, not the value, so by the time
they are called they all see the final value. Fix it by binding the value as a default
argument (`lambda x=value: ...`) or with `functools.partial`.""",
        skills=("core.scope", "adv.closures", "core.functions"),
        prerequisites=("l1.functions",),
        example_code="""def make_multiplier(factor):
    def multiply(value):
        return value * factor      # 'factor' lives in the enclosing scope
    return multiply

times_three = make_multiplier(3)
print(times_three(7), times_three.__closure__ is not None)

def counter():
    count = 0
    def increment():
        nonlocal count             # needed because we rebind, not just read
        count += 1
        return count
    return increment

tick = counter()
print(tick(), tick(), tick())

# The classic loop trap and its fix:
functions = [lambda x=value: x * 2 for value in range(3)]
print([f() for f in functions])
""",
        example_notes_ar="بدون `nonlocal` سيرفع الكود `UnboundLocalError`. جرّب حذف السطر وشاهد الخطأ.",
        example_notes_en="Without `nonlocal` the code raises `UnboundLocalError`. Delete the line and read the error.",
        experiment_code="""def build(format_string):
    def formatter(**values):
        return format_string.format(**values)
    return formatter

title = build("[{level}] {message}")
print(title(level="INFO", message="started"))
print(title(level="ERROR", message="disk full"))

# Inspect what the closure captured:
print(title.__closure__[0].cell_contents)
""",
        experiment_brief_ar="اكتب `make_adder(n)` و`make_adder_curried` وأضف طباعة لـ `__closure__` لتفهم ما يُحفظ.",
        experiment_brief_en="Write `make_adder(n)` and a curried variant, and print `__closure__` to see what is captured.",
        task=TaskSpec(
            brief_ar="""اكتب `make_accumulator(start=0)` تُعيد دالة تجمع ما تُمرَّر إليه وترجع المجموع الحالي.

ثم اكتب `make_rate_limiter(max_calls)` تُعيد دالة `allow()` تُعيد `True` لأول `max_calls`
استدعاءً ثم `False` بعد ذلك.""",
            brief_en="""Write `make_accumulator(start=0)` returning a function that adds whatever it receives and
returns the running total.

Then write `make_rate_limiter(max_calls)` returning an `allow()` function that returns `True`
for the first `max_calls` calls and `False` afterwards.""",
            starter_code="""def make_accumulator(start=0):
    # TODO: closure holding a running total
    pass


def make_rate_limiter(max_calls):
    # TODO: closure holding a call counter
    pass
""",
            public_tests={
                "test_public.py": """from main import make_accumulator, make_rate_limiter

def test_accumulator():
    add = make_accumulator()
    assert [add(1), add(2), add(3)] == [1, 3, 6]

def test_rate_limiter():
    allow = make_rate_limiter(2)
    assert [allow(), allow(), allow()] == [True, True, False]
"""},
            hidden_tests={
                "test_hidden.py": """from main import make_accumulator, make_rate_limiter

def test_accumulator_start():
    add = make_accumulator(10)
    assert add(5) == 15

def test_accumulators_independent():
    a, b = make_accumulator(), make_accumulator()
    a(5)
    assert b(1) == 1

def test_accumulator_negative():
    add = make_accumulator()
    add(3)
    assert add(-5) == -2

def test_limiter_zero_and_reuse():
    allow = make_rate_limiter(0)
    assert allow() is False
    allow2 = make_rate_limiter(1)
    assert allow2() is True
    assert allow2() is False
"""},
            reference_solution="""def make_accumulator(start=0):
    total = start

    def add(value=0):
        nonlocal total
        total += value
        return total

    return add


def make_rate_limiter(max_calls):
    used = 0

    def allow():
        nonlocal used
        if used >= max_calls:
            return False
        used += 1
        return True

    return allow
""",
            hints=(
                "`nonlocal` is required because you rebind the captured variable.",
                "Each call to the factory creates a fresh, independent closure.",
                "Return real booleans, not truthy values.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `memoize(func)` تُعيد دالة تحفظ نتائج `func` في قاموس داخلي،
بحيث لا تُحسب النتيجة نفسها مرتين للوسائط نفسها.
يجب أن تعمل مع وسائط موضعية ووسائط بالاسم، وأن تحفظ `functools.wraps` اسم الدالة.""",
            brief_en="""Write `memoize(func)` returning a wrapper caching results in an internal dict so the same
arguments are never computed twice. It must support positional and keyword arguments and
preserve the function name with `functools.wraps`.""",
            independent=True,
            starter_code="""def memoize(func):
    # TODO: cache results, keep func.__name__ visible
    pass
""",
            public_tests={"test_public.py": """from main import memoize

def test_caches():
    calls = []

    @memoize
    def double(x):
        calls.append(x)
        return x * 2

    assert double(3) == 6
    assert double(3) == 6
    assert len(calls) == 1
"""},
            hidden_tests={"test_hidden.py": """from main import memoize

def test_name_preserved():
    @memoize
    def greet(name):
        return "hi " + name

    assert greet.__name__ == "greet"

def test_keyword_arguments():
    calls = []

    @memoize
    def power(base, exponent=2):
        calls.append(1)
        return base ** exponent

    assert power(2) == 4
    assert power(2, exponent=2) == 4
    assert len(calls) == 1
    assert power(2, exponent=3) == 8
    assert len(calls) == 2

def test_distinct_arguments():
    @memoize
    def identity(x):
        return x

    assert identity(1) == 1
    assert identity(2) == 2
"""},
            reference_solution="""import inspect
from functools import wraps


def memoize(func):
    cache = {}
    signature = inspect.signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        key = tuple(sorted(bound.arguments.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper
""",
        ),
        transfer_ar="استخدم `memoize` في Algorithm Gladiators لحفظ نتائج البرمجة الديناميكية.",
        transfer_en="Use `memoize` in Algorithm Gladiators to cache dynamic-programming results.",
        references=(
            ("Python tutorial - scopes and namespaces", "https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces"),
            ("Python FAQ - closures in loops", "https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result"),
        ),
    ),
    CurriculumModule(
        id="l2.modules_packages",
        level=2,
        order_index=4,
        domain="python_core",
        title_ar="الوحدات والحزم",
        title_en="Modules and packages",
        summary_ar="تنظيم الكود في ملفات وحزم قابلة للاستيراد والاختبار.",
        summary_en="Organising code into importable, testable files and packages.",
        explanation_ar="""الوحدة ملف `.py`، والحزمة مجلد يحتوي `__init__.py`.

- `import package.module` ثم الاستخدام باسم كامل — الوضوح أولاً.
- `if __name__ == "__main__":` يجعل الملف قابلاً للتشغيل المباشر والاستيراد معاً.
- الاستيراد النسبي `from .sibling import thing` يعمل فقط داخل الحزمة.
- تجنّب **الاستيراد الدائري**: إذا احتاج A من B والعكس، انقل الجزء المشترك إلى وحدة ثالثة.
- `sys.path` هو ما يبحث فيه المفسّر؛ مشاكل الاستيراد غالباً سببها تشغيل الملف من مجلد آخر.

تخطيط مشروع صغير واضح:
```
project/
  pyproject.toml
  src/warehouse/__init__.py
  src/warehouse/models.py
  tests/test_models.py
```""",
        explanation_en="""A module is a `.py` file; a package is a folder containing `__init__.py`.

- `import package.module` and use the fully qualified name - clarity first.
- `if __name__ == "__main__":` lets a file be both run directly and imported.
- Relative imports (`from .sibling import thing`) only work inside a package.
- Avoid **circular imports**: if A needs B and B needs A, move the shared part into a third module.
- `sys.path` is what the interpreter searches; most import problems come from running a file
  from a different directory.

A clean small-project layout:
```
project/
  pyproject.toml
  src/warehouse/__init__.py
  src/warehouse/models.py
  tests/test_models.py
```""",
        skills=("core.modules", "core.packages", "pro.pyproject"),
        prerequisites=("l1.functions",),
        example_code="""# warehouse/__init__.py  -> from .models import Item
# warehouse/models.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Item:
    sku: str
    quantity: int

    def value(self, price):
        return self.quantity * price


def total_value(items, prices):
    return sum(item.value(prices.get(item.sku, 0.0)) for item in items)


if __name__ == "__main__":
    stock = [Item("A1", 3), Item("B2", 2)]
    print(total_value(stock, {"A1": 10.0, "B2": 5.5}))
""",
        example_notes_ar="شغّل الملف مباشرة ثم استورد `total_value` من مكان آخر: السلوك نفسه دون تكرار.",
        example_notes_en="Run this file directly, then import `total_value` elsewhere: same behaviour, no duplication.",
        experiment_code="""import sys, importlib, tempfile, pathlib

workdir = pathlib.Path(tempfile.mkdtemp())
package = workdir / "warehouse"
package.mkdir()
(package / "__init__.py").write_text("from .models import Item\\n", encoding="utf-8")
(package / "models.py").write_text(
    "class Item:\\n"
    "    def __init__(self, sku, quantity):\\n"
    "        self.sku = sku\\n"
    "        self.quantity = quantity\\n",
    encoding="utf-8",
)

sys.path.insert(0, str(workdir))
module = importlib.import_module("warehouse")
print("imported:", module.Item("A1", 4).sku)
print("module file:", module.__file__)
""",
        experiment_brief_ar="أضف وحدة `pricing.py` داخل الحزمة واستوردها من `__init__.py`، ثم تحقق من ترتيب الاستيراد.",
        experiment_brief_en="Add a `pricing.py` module inside the package, import it from `__init__.py`, then check the import order.",
        task=TaskSpec(
            brief_ar="""أنت تعمل داخل حزمة `warehouse` مكوّنة من ملفين:

**`warehouse/models.py`**
```python
class Item:
    def __init__(self, sku, quantity, unit_price=0.0):
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price
```

**`warehouse/reports.py`** (الملف المطلوب إنجازه)

المطلوب في `reports.py`:
- `line_total(item)` تُعيد `item.quantity * item.unit_price`،
- `stock_value(items)` تُعيد مجموع قيم كل العناصر،
- `low_stock(items, threshold=5)` تُعيد قائمة رموز (`sku`) للعناصر التي كميتها أقل من `threshold`،
- استيراد `Item` بصيغة نسبية (`from .models import Item`) لاستخدامه في تعليمات الأنواع.""",
            brief_en="""You are working inside a `warehouse` package with two files:

**`warehouse/models.py`**
```python
class Item:
    def __init__(self, sku, quantity, unit_price=0.0):
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price
```

**`warehouse/reports.py`** (the file you must write)

Inside `reports.py` provide:
- `line_total(item)` returning `item.quantity * item.unit_price`,
- `stock_value(items)` returning the sum over all items,
- `low_stock(items, threshold=5)` returning the `sku` list of items below `threshold`,
- import `Item` relatively (`from .models import Item`) and use it in type hints.""",
            starter_code="""from .models import Item


def line_total(item):
    # TODO
    pass


def stock_value(items):
    # TODO
    pass


def low_stock(items, threshold=5):
    # TODO
    pass
""",
            entry_filename="warehouse/reports.py",
            extra_files={
                "warehouse/__init__.py": """from .models import Item
from .reports import line_total, low_stock, stock_value

__all__ = ["Item", "line_total", "low_stock", "stock_value"]
""",
                "warehouse/models.py": """class Item:
    def __init__(self, sku, quantity, unit_price=0.0):
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price
""",
            },
            public_tests={
                "test_public.py": """from warehouse import Item, line_total, stock_value, low_stock

def test_line_total():
    assert line_total(Item("A1", 3, 10.0)) == 30.0

def test_low_stock():
    items = [Item("A1", 2), Item("B2", 9)]
    assert low_stock(items) == ["A1"]
"""},
            hidden_tests={
                "test_hidden.py": """from warehouse import Item, line_total, stock_value, low_stock
from warehouse.reports import line_total as direct_import

def test_stock_value():
    items = [Item("A1", 2, 5.0), Item("B2", 1, 10.0)]
    assert stock_value(items) == 20.0

def test_empty_and_defaults():
    assert stock_value([]) == 0
    assert line_total(Item("X", 0)) == 0.0

def test_low_stock_threshold():
    items = [Item("A", 4), Item("B", 5), Item("C", 6)]
    assert low_stock(items, threshold=5) == ["A"]
    assert low_stock(items, threshold=10) == ["A", "B", "C"]

def test_relative_import_used():
    assert direct_import is line_total
"""},
            reference_solution="""from .models import Item


def line_total(item: Item) -> float:
    return item.quantity * item.unit_price


def stock_value(items) -> float:
    return sum(line_total(item) for item in items)


def low_stock(items, threshold: int = 5):
    return [item.sku for item in items if item.quantity < threshold]
""",
            hints=(
                "Relative imports (`from .models import Item`) only work when tests import the package, not the file.",
                "Sum with a generator expression to avoid building an intermediate list.",
                "Return sku strings from `low_stock`, not Item objects.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""أضف وحدة `warehouse/cli.py` فيها `format_report(items)` تُعيد نصاً متعدد الأسطر:
سطر لكل عنصر بالشكل `sku  quantity  total` ثم سطر إجمالي يبدأ بـ `TOTAL`.
يجب أن تعيد الدالة نصاً (لا تطبعه)، وأن تعمل مع قائمة فارغة.""",
            brief_en="""Add a `warehouse/cli.py` module with `format_report(items)` returning a multi-line string:
one line per item shaped `sku  quantity  total`, followed by a `TOTAL` line.
The function must return the text instead of printing it, and must work for an empty list.""",
            independent=True,
            starter_code="""def format_report(items):
    # TODO: return a multi-line report string
    pass
""",
            entry_filename="warehouse/cli.py",
            extra_files={
                "warehouse/__init__.py": """from .models import Item
from .reports import line_total, low_stock, stock_value
from .cli import format_report

__all__ = ["Item", "line_total", "low_stock", "stock_value", "format_report"]
""",
                "warehouse/models.py": """class Item:
    def __init__(self, sku, quantity, unit_price=0.0):
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price
""",
                "warehouse/reports.py": """from .models import Item


def line_total(item: Item) -> float:
    return item.quantity * item.unit_price


def stock_value(items) -> float:
    return sum(line_total(item) for item in items)


def low_stock(items, threshold: int = 5):
    return [item.sku for item in items if item.quantity < threshold]
""",
            },
            public_tests={"test_public.py": """from warehouse import Item, format_report

def test_report_contains_totals():
    text = format_report([Item("A1", 2, 5.0)])
    assert "A1" in text and "TOTAL" in text
"""},
            hidden_tests={"test_hidden.py": """from warehouse import Item, format_report

def test_line_shape():
    text = format_report([Item("A1", 2, 5.0)])
    lines = text.strip().splitlines()
    assert lines[0].split() == ["A1", "2", "10.0"]

def test_total_line():
    text = format_report([Item("A1", 2, 5.0), Item("B2", 1, 3.0)])
    last = text.strip().splitlines()[-1]
    assert last.startswith("TOTAL")
    assert "13.0" in last

def test_empty_report():
    text = format_report([])
    assert "TOTAL" in text
    assert "0" in text

def test_returns_string_not_prints(capsys):
    text = format_report([Item("A1", 1, 1.0)])
    captured = capsys.readouterr()
    assert captured.out == "", "format_report must return the text, not print it"
    assert isinstance(text, str)
"""},
            reference_solution="""def format_report(items):
    lines = []
    total = 0.0
    for item in items:
        value = item.quantity * item.unit_price
        total += value
        lines.append(f"{item.sku}  {item.quantity}  {value}")
    lines.append(f"TOTAL  {len(items)}  {total}")
    return "\\n".join(lines) + "\\n"
""",
        ),
        transfer_ar="طبّق نفس البنية في My Projects عند تحويل سكربت واحد إلى حزمة متعددة الملفات.",
        transfer_en="Apply the same structure in My Projects when turning a single script into a multi-file package.",
        references=(
            ("Python tutorial - modules", "https://docs.python.org/3/tutorial/modules.html"),
            ("Python docs - import system", "https://docs.python.org/3/reference/import.html"),
        ),
    ),
    CurriculumModule(
        id="l2.oop",
        level=2,
        order_index=5,
        domain="python_core",
        title_ar="البرمجة الكائنية",
        title_en="Object-oriented programming",
        summary_ar="الأصناف والتركيب: نمذجة البيانات مع السلوك الذي يخصّها.",
        summary_en="Classes and composition: modelling data together with the behaviour that belongs to it.",
        explanation_ar="""الصنف يجمع **الحالة** (الخصائص) مع **السلوك** (الطرق).

- `__init__` يهيئ الكائن، و`self` هو الكائن نفسه.
- `__repr__` يُعيد تمثيلاً للمطوّر (مفيد جداً في التصحيح)، و`__str__` للمستخدم.
- `__eq__` يحدد معنى المساواة.
- الخصائص الخاصة تبدأ بـ `_` اصطلاحاً، وبـ `__` لتغيير الاسم (name mangling).

**فضّل التركيب على الوراثة**: بدل `class Truck(Vehicle)` أعطِ الكائن مكوّنات
(`self.engine = Engine()`). الوراثة مناسبة عندما يكون هناك "is-a" حقيقي وواجهة مشتركة.

`@dataclass` تولّد `__init__` و`__repr__` و`__eq__` تلقائياً: استخدمها لعناصر البيانات.""",
        explanation_en="""A class bundles **state** (attributes) with **behaviour** (methods).

- `__init__` initialises the object; `self` is the object itself.
- `__repr__` returns a developer-facing representation (invaluable when debugging) and `__str__` a user-facing one.
- `__eq__` defines what equality means.
- A single leading `_` marks an attribute as internal by convention; a double `__` triggers name mangling.

**Prefer composition over inheritance**: instead of `class Truck(Vehicle)`, give the object
components (`self.engine = Engine()`). Inheritance fits when there is a real "is-a"
relationship and a shared interface.

`@dataclass` generates `__init__`, `__repr__` and `__eq__` for you: use it for data holders.""",
        skills=("core.oop_basic", "core.oop_composition", "stdlib.dataclasses"),
        prerequisites=("l2.modules_packages",),
        example_code="""from dataclasses import dataclass, field


@dataclass(slots=True)
class Sensor:
    name: str
    readings: list[float] = field(default_factory=list)

    def record(self, value):
        self.readings.append(value)

    @property
    def average(self):
        return sum(self.readings) / len(self.readings) if self.readings else 0.0


class Robot:
    def __init__(self, name, sensor):
        self.name = name
        self.sensor = sensor          # composition, not inheritance

    def sample(self, value):
        self.sensor.record(value)

    def __repr__(self):
        return f"Robot(name={self.name!r}, average={self.sensor.average:.2f})"


bot = Robot("r1", Sensor("lidar"))
for value in (1.0, 2.0, 6.0):
    bot.sample(value)
print(bot, "| average:", bot.sensor.average)
""",
        example_notes_ar="`field(default_factory=list)` ضروري: لا تضع `[]` كقيمة افتراضية في dataclass.",
        example_notes_en="`field(default_factory=list)` is required: never use `[]` as a dataclass default.",
        experiment_code="""from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "SAR"

    def __add__(self, other):
        if other.currency != self.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)


wallet = Money(10) + Money(5)
print(wallet, wallet == Money(15))
try:
    Money(10, "USD") + Money(10, "SAR")
except ValueError as exc:
    print("ValueError:", exc)
""",
        experiment_brief_ar="شغّل الكود واقرأ الخطأ. ثم أضف `__mul__` للضرب في عدد، واجعل التقريب لمنزلتين.",
        experiment_brief_en="Run it and read the error. Then add `__mul__` for multiplying by a number and round to two decimals.",
        task=TaskSpec(
            brief_ar="""اكتب صنف `Battery` بخصائص `capacity` و`level`:
- `drain(amount)` يخفض المستوى بمقدار `amount` ويرفع `ValueError` إذا صار سالباً،
- `charge(amount)` يرفع المستوى دون تجاوز `capacity`،
- `percentage` خاصية (property) تُعيد النسبة المئوية،
- `__repr__` يُعيد نصاً واضحاً.

ثم اكتب صنف `Device` يستخدم `Battery` بالتركيب: `Device(name, battery)` مع طريقة `use(minutes)`
تستهلك `minutes * 0.5` من البطارية.""",
            brief_en="""Write a `Battery` class with `capacity` and `level`:
- `drain(amount)` lowers the level and raises `ValueError` if it would go negative,
- `charge(amount)` raises the level without exceeding `capacity`,
- `percentage` is a property returning the percentage,
- `__repr__` returns clear text.

Then write a `Device` class that *composes* a battery: `Device(name, battery)` with a
`use(minutes)` method consuming `minutes * 0.5`.""",
            starter_code="""class Battery:
    def __init__(self, capacity, level=None):
        pass

    def drain(self, amount):
        pass

    def charge(self, amount):
        pass

    @property
    def percentage(self):
        pass

    def __repr__(self):
        pass


class Device:
    def __init__(self, name, battery):
        pass

    def use(self, minutes):
        pass
""",
            public_tests={
                "test_public.py": """from main import Battery, Device

def test_battery_drain():
    battery = Battery(100)
    battery.drain(40)
    assert battery.level == 60

def test_device_consumes():
    battery = Battery(10)
    device = Device("phone", battery)
    device.use(4)
    assert battery.level == 8.0
"""},
            hidden_tests={
                "test_hidden.py": """from main import Battery, Device
import pytest

def test_default_level_is_full():
    assert Battery(50).level == 50

def test_drain_below_zero_raises():
    battery = Battery(10)
    with pytest.raises(ValueError):
        battery.drain(11)
    assert battery.level == 10, "a failed drain must not change the level"

def test_charge_is_capped():
    battery = Battery(10, level=8)
    battery.charge(5)
    assert battery.level == 10

def test_percentage():
    assert Battery(200, level=50).percentage == 25.0
    assert Battery(0).percentage == 0

def test_repr_is_informative():
    text = repr(Battery(10, level=5))
    assert "5" in text and "10" in text

def test_device_stops_when_empty():
    battery = Battery(1)
    device = Device("toy", battery)
    device.use(2)
    with pytest.raises(ValueError):
        device.use(2)
"""},
            reference_solution="""class Battery:
    def __init__(self, capacity, level=None):
        self.capacity = capacity
        self.level = capacity if level is None else level

    def drain(self, amount):
        if amount > self.level:
            raise ValueError(f"not enough charge: need {amount}, have {self.level}")
        self.level -= amount

    def charge(self, amount):
        self.level = min(self.capacity, self.level + amount)

    @property
    def percentage(self):
        return (self.level / self.capacity * 100) if self.capacity else 0.0

    def __repr__(self):
        return f"Battery(level={self.level}, capacity={self.capacity})"


class Device:
    drain_per_minute = 0.5

    def __init__(self, name, battery):
        self.name = name
        self.battery = battery

    def use(self, minutes):
        self.battery.drain(minutes * self.drain_per_minute)
""",
            hints=(
                "Validate before mutating: a failed drain must leave the level untouched.",
                "`level = capacity if level is None else level` gives a sensible default.",
                "`Device` should hold a Battery instance (composition) and delegate to it.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب صنف `Inventory` يستخدم قاموساً داخلياً:
- `add(sku, quantity=1)` يزيد الكمية،
- `remove(sku, quantity=1)` ينقصها ويرفع `KeyError` إذا لم يكفِ المخزون،
- `value(prices)` تُعيد القيمة الإجمالية،
- `__len__` و`__contains__` و`__iter__` (يمرّر على الرموز)،
- `__repr__` يصف عدد الأصناف.""",
            brief_en="""Write an `Inventory` class backed by an internal dict:
- `add(sku, quantity=1)` increases the quantity,
- `remove(sku, quantity=1)` decreases it and raises `KeyError` when stock is insufficient,
- `value(prices)` returns the total value,
- `__len__`, `__contains__` and `__iter__` (over skus),
- `__repr__` describing how many skus it holds.""",
            independent=True,
            starter_code="""class Inventory:
    def __init__(self):
        pass
""",
            public_tests={"test_public.py": """from main import Inventory

def test_add_and_len():
    inv = Inventory()
    inv.add("A1", 3)
    assert len(inv) == 1
    assert "A1" in inv
"""},
            hidden_tests={"test_hidden.py": """from main import Inventory
import pytest

def test_remove_and_zero_removes_entry():
    inv = Inventory()
    inv.add("A1", 2)
    inv.remove("A1", 2)
    assert len(inv) == 0
    assert "A1" not in inv

def test_remove_insufficient():
    inv = Inventory()
    inv.add("A1", 1)
    with pytest.raises(KeyError):
        inv.remove("A1", 5)
    assert inv._items["A1"] == 1

def test_value_with_prices():
    inv = Inventory()
    inv.add("A1", 2)
    inv.add("B2", 1)
    assert inv.value({"A1": 10.0, "B2": 5.0}) == 25.0

def test_iteration_and_repr():
    inv = Inventory()
    inv.add("A1"); inv.add("B2")
    assert sorted(inv) == ["A1", "B2"]
    assert "2" in repr(inv)
"""},
            reference_solution="""class Inventory:
    def __init__(self):
        self._items = {}

    def add(self, sku, quantity=1):
        self._items[sku] = self._items.get(sku, 0) + quantity

    def remove(self, sku, quantity=1):
        have = self._items.get(sku, 0)
        if have < quantity:
            raise KeyError(f"insufficient stock for {sku}: {have} < {quantity}")
        remaining = have - quantity
        if remaining:
            self._items[sku] = remaining
        else:
            del self._items[sku]

    def value(self, prices):
        return sum(qty * prices.get(sku, 0.0) for sku, qty in self._items.items())

    def __len__(self):
        return len(self._items)

    def __contains__(self, sku):
        return sku in self._items

    def __iter__(self):
        return iter(self._items)

    def __repr__(self):
        return f"Inventory(skus={len(self._items)}, units={sum(self._items.values())})"
""",
        ),
        transfer_ar="استخدم نفس الصنف في Automation City لتمثيل مستودع المصنع.",
        transfer_en="Reuse the same class in Automation City to represent the factory warehouse.",
        references=(
            ("Python tutorial - classes", "https://docs.python.org/3/tutorial/classes.html"),
            ("Python docs - dataclasses", "https://docs.python.org/3/library/dataclasses.html"),
        ),
    ),
]
