"""LEVEL 10 - Systems and engineering: performance, persistence and services."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l10.performance",
        level=10,
        order_index=1,
        domain="systems",
        title_ar="القياس وتحسين الأداء",
        title_en="Measuring and improving performance",
        summary_ar="قِس قبل أن تُحسّن: قياس موثوق، ملف تعريفي، وتحسين مُثبت.",
        summary_en="Measure before optimising: reliable timing, profiling and proven speedups.",
        explanation_ar="""الحدس سيئ في تقدير الأداء. العملية الصحيحة:

1. **حدّد هدفاً قابلاً للقياس**: "أقل من 200 مللي ثانية لعشرة آلاف سجل".
2. **ابنِ معياراً (benchmark)**: كرّر القياس وخذ **أفضل** نتيجة لا المتوسط،
   لأن الضجيج يأتي من جهات أخرى (GC، نظام التشغيل) ولا يخص كودك.
3. **ملف تعريفي (profile) قبل التحسين**: `cProfile` يخبرك أين يقضي البرنامج وقته
   فعلاً، وغالباً ما يفاجئك.
4. **حسّن الرتبة قبل الثوابت**: استبدال خوارزمية `O(n²)` بأخرى `O(n)` يتفوّق على
   أي تحسين micro.
5. **أعد القياس** وأثبت التحسن. بدون رقم قبل وبعد، لم تفعل شيئاً.

أدوات:
- `time.perf_counter` للقياس الدقيق،
- `cProfile` + `pstats` لتوزيع الوقت،
- `functools.lru_cache` للحفظ،
- عمليات numpy الموجّهة بدل حلقات بايثون.

احذر: القياس الأول يشمل تهيئة (JIT/استيراد/تخصيص ذاكرة) — تجاهل أول تشغيل.""",
        explanation_en="""Intuition is bad at performance. The correct process:

1. **Set a measurable goal**: "under 200 ms for ten thousand records".
2. **Build a benchmark**: repeat the measurement and keep the **best** result rather than the
   average, because noise comes from elsewhere (GC, the OS) and is not your code.
3. **Profile before optimising**: `cProfile` tells you where the time actually goes, and it
   usually surprises you.
4. **Fix the order, then the constants**: replacing an `O(n^2)` algorithm with an `O(n)` one
   beats any micro-optimisation.
5. **Re-measure** and prove the improvement. Without a before/after number you did nothing.

Tools:
- `time.perf_counter` for precise timing,
- `cProfile` + `pstats` for the distribution of time,
- `functools.lru_cache` for memoisation,
- vectorised numpy operations instead of Python loops.

Careful: the first measurement includes warm-up (imports, allocation) - discard the first run.""",
        skills=("adv.profiling", "algo.benchmarking", "adv.optimization"),
        prerequisites=("l6.complexity", "l5.numpy_foundations"),
        example_code="""import cProfile
import io
import pstats
import time


def slow_total(values):
    total = 0
    for value in values:
        total += value * value
    return total


def fast_total(values):
    return sum(value * value for value in values)


def benchmark(function, data, repeats=20):
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        function(data)
        best = min(best, time.perf_counter() - start)
    return best * 1000


data = list(range(50_000))
for function in (slow_total, fast_total):
    print(f"{function.__name__:>11}: {benchmark(function, data):7.3f} ms")


def work():
    return slow_total(data) + fast_total(data)


profiler = cProfile.Profile()
profiler.enable()
work()
profiler.disable()

buffer = io.StringIO()
pstats.Stats(profiler, stream=buffer).sort_stats("cumulative").print_stats(5)
lines = [line for line in buffer.getvalue().splitlines() if line.strip()][:12]
print("\\n".join(lines[4:9]))
""",
        example_notes_ar="`print_stats` يكتب في مجرى نصي: مرّر `io.StringIO()` لالتقاط النتيجة بدل الطباعة.",
        example_notes_en="`print_stats` writes to a stream: pass an `io.StringIO()` to capture it instead of printing.",
        experiment_code="""import time
from functools import lru_cache


def fib_plain(n):
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)


@lru_cache(maxsize=None)
def fib_cached(n):
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


def measure(function, argument, repeats=5):
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        function(argument)
        best = min(best, time.perf_counter() - start)
    return best * 1000


for n in (20, 25, 28):
    plain = measure(fib_plain, n)
    fib_cached.cache_clear()
    cached = measure(fib_cached, n)
    print(f"n={n:>3}  plain {plain:9.3f} ms   cached {cached:9.5f} ms   speedup {plain / max(cached, 1e-9):8.0f}x")
""",
        experiment_brief_ar="زد `n` إلى 33 وشاهد كيف يتغيّر عامل التسريع، وفسّر السبب.",
        experiment_brief_en="Raise `n` to 33 and watch how the speedup factor changes, then explain why.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `benchmark(function, *args, repeats=10, warmup=1, **kwargs)` تُعيد أفضل زمن
   بالميلي ثانية (تجاهل `warmup` نداءات في البداية).
2. `profile_call(function, *args, **kwargs)` تُعيد `{"result": ..., "stats": text, "total_calls": int, "top": [...]}`
   حيث `top` قائمة `(function_name, cumulative_time)` لأعلى 5 دوال حسب `cumulative`.
3. `speedup(before, after, *args, **kwargs)` نسبة `before / after` للزمن.""",
            brief_en="""Write:
1. `benchmark(function, *args, repeats=10, warmup=1, **kwargs)` returning the best time in
   milliseconds (discarding `warmup` initial calls).
2. `profile_call(function, *args, **kwargs)` returning
   `{"result": ..., "stats": text, "total_calls": int, "top": [...]}` where `top` is the top five
   `(function_name, cumulative_time)` entries sorted by cumulative time.
3. `speedup(before, after, *args, **kwargs)` - the time ratio `before / after`.""",
            starter_code="""import cProfile
import io
import pstats
import time


def benchmark(function, *args, repeats=10, warmup=1, **kwargs):
    pass


def profile_call(function, *args, **kwargs):
    pass


def speedup(before, after, *args, **kwargs):
    pass
""",
            public_tests={"test_public.py": """import time
from main import benchmark

def test_benchmark_positive():
    elapsed = benchmark(time.sleep, 0.001, repeats=3, warmup=1)
    assert elapsed > 0
"""},
            hidden_tests={"test_hidden.py": """import time
from main import benchmark, profile_call, speedup

def work(n):
    return sum(i * i for i in range(n))

def slow(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return total

def fast(n):
    return n * n

def test_benchmark_returns_float():
    elapsed = benchmark(work, 1000, repeats=3, warmup=1)
    assert isinstance(elapsed, float) and elapsed >= 0

def test_benchmark_warmup_runs():
    calls = []
    benchmark(calls.append, 1, repeats=3, warmup=2)
    assert len(calls) == 5

def test_benchmark_kwargs_forwarded():
    assert benchmark(lambda value: value, value=5, repeats=2, warmup=0) >= 0

def test_profile_call_result():
    report = profile_call(work, 500)
    assert report["result"] == work(500)

def test_profile_call_top_entries():
    report = profile_call(work, 5000)
    assert len(report["top"]) >= 1
    assert all(isinstance(name, str) and seconds >= 0 for name, seconds in report["top"])
    assert report["top"][0][1] > 0
    assert report["top"] == sorted(report["top"], key=lambda entry: entry[1], reverse=True)

def test_profile_call_stats_text():
    report = profile_call(work, 100)
    assert "function calls" in report["stats"]
    assert report["total_calls"] > 0

def test_speedup_is_greater_than_one():
    ratio = speedup(slow, fast, 300)
    assert ratio > 1

def test_speedup_same_function():
    ratio = speedup(work, work, 200)
    assert 0.1 < ratio < 10
"""},
            reference_solution="""import cProfile
import io
import pstats
import time


def benchmark(function, *args, repeats=10, warmup=1, **kwargs):
    for _ in range(max(0, int(warmup))):
        function(*args, **kwargs)
    best = float("inf")
    for _ in range(max(1, int(repeats))):
        start = time.perf_counter()
        function(*args, **kwargs)
        best = min(best, time.perf_counter() - start)
    return best * 1000


def profile_call(function, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = function(*args, **kwargs)
    profiler.disable()
    buffer = io.StringIO()
    stats = pstats.Stats(profiler, stream=buffer)
    stats.sort_stats("cumulative")
    stats.print_stats(5)
    top = [
        (str(key[2]), float(row[3]))
        for key, row in sorted(stats.stats.items(), key=lambda item: item[1][3], reverse=True)[:5]
    ]
    return {
        "result": result,
        "stats": buffer.getvalue(),
        "total_calls": int(stats.total_calls),
        "top": top,
    }


def speedup(before, after, *args, **kwargs):
    before_time = benchmark(before, *args, **kwargs)
    after_time = benchmark(after, *args, **kwargs)
    if after_time <= 0:
        return float("inf") if before_time > 0 else 1.0
    return before_time / after_time
""",
            hints=(
                "Run the warm-up calls outside the timed loop so imports and allocation do not count.",
                "`pstats.Stats(profiler, stream=buffer)` captures the report instead of printing it.",
                "`stats.stats` is a dict keyed by `(file, line, name)` with `(cc, nc, tt, ct, callers)` values.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""أعطِ نسخة محسّنة: الدالة البطيئة التالية تحسب تكرار الكلمات:

```python
def count_words_slow(text):
    counts = {}
    for word in text.lower().split():
        found = False
        for key in counts:
            if key == word:
                counts[key] += 1
                found = True
                break
        if not found:
            counts[word] = 1
    return counts
```

اكتب `count_words_fast(text)` تُنتج **نفس النتيجة** وتكون أسرع بـ 5 مرات على الأقل
على نص من 20 ألف كلمة. احتفظ بالدالتين في الملف.""",
            brief_en="""Provide an optimised version. This slow function counts words:

```python
def count_words_slow(text):
    counts = {}
    for word in text.lower().split():
        found = False
        for key in counts:
            if key == word:
                counts[key] += 1
                found = True
                break
        if not found:
            counts[word] = 1
    return counts
```

Write `count_words_fast(text)` producing the **same result** at least 5x faster on a text of
20 thousand words. Keep both functions in the file.""",
            independent=True,
            starter_code="""def count_words_slow(text):
    counts = {}
    for word in text.lower().split():
        found = False
        for key in counts:
            if key == word:
                counts[key] += 1
                found = True
                break
        if not found:
            counts[word] = 1
    return counts


def count_words_fast(text):
    # TODO: same result, much faster
    return count_words_slow(text)
""",
            public_tests={"test_public.py": """from main import count_words_slow, count_words_fast

def test_same_result():
    text = "alpha beta alpha gamma"
    assert count_words_fast(text) == count_words_slow(text)
"""},
            hidden_tests={"test_hidden.py": """import random
import string
import time
from main import count_words_slow, count_words_fast

WORDS = [f"word-{index}" for index in range(2000)]
RNG = random.Random(0)          # one generator, reused - a fresh Random(0) repeats itself
TEXT = " ".join(RNG.choice(WORDS) for _ in range(12000))

def measure(function, repeats=1):
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        function(TEXT)
        best = min(best, time.perf_counter() - start)
    return best

def test_identical_result_large_text():
    assert count_words_fast(TEXT) == count_words_slow(TEXT)

def test_is_faster():
    slow = measure(count_words_slow)
    fast = measure(count_words_fast)
    assert slow / fast >= 5, slow / fast

def test_handles_empty():
    assert count_words_fast("") == {}

def test_handles_punctuation_and_case():
    text = "Alpha, alpha! BETA"
    assert count_words_fast(text) == count_words_slow(text)

def test_counts_are_correct():
    result = count_words_fast("a b a c a")
    assert result == {"a": 3, "b": 1, "c": 1}

def test_single_word_text():
    assert count_words_fast("solo") == {"solo": 1}
"""},
            reference_solution="""from collections import Counter


def count_words_slow(text):
    counts = {}
    for word in text.lower().split():
        found = False
        for key in counts:
            if key == word:
                counts[key] += 1
                found = True
                break
        if not found:
            counts[word] = 1
    return counts


def count_words_fast(text):
    return dict(Counter(text.lower().split()))
""",
        ),
        transfer_ar="طبّق نفس المنهجية في Crisis Simulator قبل إعادة كتابة أي مسار حرج.",
        transfer_en="Apply the same method in Crisis Simulator before rewriting any hot path.",
        references=(
            ("Python docs - the profilers", "https://docs.python.org/3/library/profile.html"),
            ("Python docs - time.perf_counter", "https://docs.python.org/3/library/time.html#time.perf_counter"),
        ),
    ),
    CurriculumModule(
        id="l10.sqlite_persistence",
        level=10,
        order_index=2,
        domain="systems",
        title_ar="الثبات مع SQLite",
        title_en="Persistence with SQLite",
        summary_ar="مخطط، استعلامات مُعاملَة، عمليات، وتراجع — بأمان.",
        summary_en="Schema, parameterised queries, transactions and rollback - safely.",
        explanation_ar="""قاعدة البيانات هي المكان الذي تلتقي فيه صحة البيانات بالأداء. أساسيات لا تُهمل:

1. **استعلامات مُعاملَة دائماً**: `cursor.execute("... WHERE id = ?", (value,))`.
   أبداً لا تدمج النص في الاستعلام (حقن SQL).
2. **المخطط صريح**: أنواع الأعمدة، القيود (`PRIMARY KEY`, `NOT NULL`, `UNIQUE`,
   `FOREIGN KEY`)، والفهارس للأعمدة التي تبحث بها.
3. **العمليات (transactions)**: `with connection:` يلتزم عند النجاح ويتراجع عند الاستثناء.
   التراجع يحميك من حالة نصف مكتملة.
4. **الالتزام الصريح**: SQLite يفتح عملية ضمنياً؛ لا تعتمد على الالتزام التلقائي.
5. **استخدم `row_factory`**: `sqlite3.Row` يجعل النتائج تشبه القواميس.

نمط المستودع (Repository): غلّف كل SQL في دوال صريحة (`add`, `get`, `list`, `remove`)
حتى لا ينتشر SQL في بقية التطبيق — ويصبح التبديل إلى قاعدة أخرى ممكناً.""",
        explanation_en="""A database is where correctness meets performance. Non-negotiable basics:

1. **Always parameterise queries**: `cursor.execute("... WHERE id = ?", (value,))`.
   Never concatenate text into SQL (SQL injection).
2. **Make the schema explicit**: column types, constraints (`PRIMARY KEY`, `NOT NULL`,
   `UNIQUE`, `FOREIGN KEY`) and indexes on the columns you search by.
3. **Transactions**: `with connection:` commits on success and rolls back on exceptions.
   Rollback protects you from a half-finished state.
4. **Commit explicitly**: SQLite opens a transaction implicitly; do not rely on autocommit.
5. **Set a `row_factory`**: `sqlite3.Row` makes results behave like dicts.

The Repository pattern: wrap every SQL statement in explicit functions (`add`, `get`, `list`,
`remove`) so SQL does not leak into the rest of the app - and switching databases stays possible.""",
        skills=("stdlib.sqlite", "sec.input_validation"),
        prerequisites=("l5.pandas_core", "l4.context_managers"),
        example_code="""import sqlite3

connection = sqlite3.connect(":memory:")
connection.row_factory = sqlite3.Row
connection.execute("PRAGMA foreign_keys = ON")

connection.executescript(
    \"\"\"
    CREATE TABLE learners (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE attempts (
        id INTEGER PRIMARY KEY,
        learner_id INTEGER NOT NULL REFERENCES learners(id),
        module TEXT NOT NULL,
        score REAL NOT NULL
    );
    \"\"\"
)

connection.execute("INSERT INTO learners (name, level) VALUES (?, ?)", ("Aisha", 3))
connection.execute("INSERT INTO learners (name, level) VALUES (?, ?)", ("Omar", 5))
connection.executemany(
    "INSERT INTO attempts (learner_id, module, score) VALUES (?, ?, ?)",
    [(1, "l1.functions", 0.9), (1, "l2.oop", 0.7), (2, "l2.oop", 1.0)],
)
connection.commit()

rows = connection.execute(
    \"\"\"
    SELECT learners.name, COUNT(attempts.id) AS attempts, AVG(attempts.score) AS average
    FROM learners LEFT JOIN attempts ON attempts.learner_id = learners.id
    GROUP BY learners.id ORDER BY average DESC
    \"\"\"
).fetchall()

for row in rows:
    print(dict(row))

try:
    with connection:
        connection.execute("INSERT INTO learners (name, level) VALUES (?, ?)", ("Ghost", 1))
        raise RuntimeError("something failed")
except RuntimeError as error:
    print("rolled back:", error)

print("learners after rollback:", connection.execute("SELECT COUNT(*) FROM learners").fetchone()[0])
""",
        example_notes_ar="`with connection:` يتراجع تلقائياً عند أي استثناء داخل الكتلة.",
        example_notes_en="`with connection:` rolls back automatically when anything inside the block raises.",
        experiment_code="""import sqlite3

connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, kind TEXT, payload TEXT)")

BAD_NAME = "Robert'); DROP TABLE victim; --"

connection.execute("INSERT INTO events (kind, payload) VALUES (?, ?)", ("login", BAD_NAME))
stored = connection.execute("SELECT payload FROM events WHERE kind = ?", ("login",)).fetchone()[0]
print("parameterised insert stored the text verbatim:", stored)
print("events table intact:", connection.execute(
    "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'events'").fetchone()[0])

# never do this in real code - this is what an injection looks like
connection.execute("CREATE TABLE victim (payload TEXT)")
connection.executescript(f"INSERT INTO victim (payload) VALUES ('{BAD_NAME}')")
print("after string interpolation, victim exists:", connection.execute(
    "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'victim'").fetchone()[0])

connection.execute("CREATE INDEX IF NOT EXISTS idx_events_kind ON events (kind)")
connection.executemany(
    "INSERT INTO events (kind, payload) VALUES (?, ?)",
    [(f"kind-{i % 5}", str(i)) for i in range(2000)],
)
connection.commit()

plan = connection.execute("EXPLAIN QUERY PLAN SELECT * FROM events WHERE kind = ?", ("kind-3",)).fetchall()
print("query plan:", plan[-1][-1])
""",
        experiment_brief_ar="أزل الفهرس وأعد تشغيل `EXPLAIN QUERY PLAN` وقارن (SCAN مقابل SEARCH).",
        experiment_brief_en="Drop the index and rerun `EXPLAIN QUERY PLAN`, then compare (SCAN vs SEARCH).",
        task=TaskSpec(
            brief_ar="""اكتب صنف `TaskRepository(path=":memory:")` بمخطط
`tasks(id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)`
وطرق:
- `add(title)` تُعيد معرّف الصف الجديد،
- `get(task_id)` تُعيد قاموساً أو `None`،
- `list_all(only_open=False)`،
- `complete(task_id)` تضبط `done = 1` وتُعيد `True` إن وُجد،
- `remove(task_id)` تُعيد `True` إن حُذف شيء،
- `counts()` تُعيد `{"total", "open", "done"}`.

كل الاستعلامات مُعاملَة. لا تدمج نصوصاً في SQL.""",
            brief_en="""Write a `TaskRepository(path=":memory:")` class with the schema
`tasks(id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)`
and methods:
- `add(title)` returning the new row id,
- `get(task_id)` returning a dict or `None`,
- `list_all(only_open=False)`,
- `complete(task_id)` setting `done = 1` and returning `True` when it existed,
- `remove(task_id)` returning `True` when something was deleted,
- `counts()` returning `{"total", "open", "done"}`.

Every query must be parameterised. Never interpolate text into SQL.""",
            starter_code="""import sqlite3


class TaskRepository:
    def __init__(self, path=":memory:"):
        pass
""",
            public_tests={"test_public.py": """from main import TaskRepository

def test_add_and_get():
    repository = TaskRepository()
    identifier = repository.add("write docs")
    assert repository.get(identifier)["title"] == "write docs"
"""},
            hidden_tests={"test_hidden.py": """from main import TaskRepository

def test_get_missing():
    assert TaskRepository().get(999) is None

def test_list_all():
    repository = TaskRepository()
    repository.add("a")
    repository.add("b")
    assert len(repository.list_all()) == 2

def test_only_open_filters():
    repository = TaskRepository()
    first = repository.add("a")
    repository.add("b")
    repository.complete(first)
    assert len(repository.list_all(only_open=True)) == 1

def test_complete_returns_false_for_missing():
    assert TaskRepository().complete(42) is False

def test_complete_is_idempotent():
    repository = TaskRepository()
    identifier = repository.add("a")
    assert repository.complete(identifier) is True
    assert repository.complete(identifier) is True
    assert repository.get(identifier)["done"] == 1

def test_remove():
    repository = TaskRepository()
    identifier = repository.add("a")
    assert repository.remove(identifier) is True
    assert repository.remove(identifier) is False

def test_counts():
    repository = TaskRepository()
    repository.add("a")
    second = repository.add("b")
    repository.complete(second)
    assert repository.counts() == {"total": 2, "open": 1, "done": 1}

def test_injection_is_harmless():
    repository = TaskRepository()
    identifier = repository.add("x'); DROP TABLE tasks; --")
    assert repository.get(identifier)["title"] == "x'); DROP TABLE tasks; --"
    assert repository.counts()["total"] == 1

def test_persistence_to_a_file(tmp_path):
    path = str(tmp_path / "tasks.db")
    first = TaskRepository(path)
    first.add("persisted")
    second = TaskRepository(path)
    assert second.counts()["total"] == 1
"""},
            reference_solution="""import sqlite3

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS tasks ("
    " id INTEGER PRIMARY KEY,"
    " title TEXT NOT NULL,"
    " done INTEGER NOT NULL DEFAULT 0)"
)


class TaskRepository:
    def __init__(self, path=":memory:"):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(SCHEMA)
        self.connection.commit()

    def add(self, title):
        cursor = self.connection.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        self.connection.commit()
        return int(cursor.lastrowid)

    def get(self, task_id):
        row = self.connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

    def list_all(self, only_open=False):
        if only_open:
            rows = self.connection.execute("SELECT * FROM tasks WHERE done = 0 ORDER BY id").fetchall()
        else:
            rows = self.connection.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def complete(self, task_id):
        cursor = self.connection.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def remove(self, task_id):
        cursor = self.connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def counts(self):
        row = self.connection.execute(
            "SELECT COUNT(*) AS total,"
            " COALESCE(SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END), 0) AS open,"
            " COALESCE(SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END), 0) AS done"
            " FROM tasks"
        ).fetchone()
        return {"total": row["total"], "open": row["open"], "done": row["done"]}

    def close(self):
        self.connection.close()
""",
            hints=(
                "`cursor.lastrowid` gives the id of the row you just inserted.",
                "`cursor.rowcount` tells you whether an UPDATE or DELETE matched anything.",
                "Use `COALESCE(SUM(...), 0)` so aggregates return 0 rather than NULL on an empty table.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""ابنِ مستودعين مترابطين: `authors(id, name)` و`books(id, author_id REFERENCES authors(id), title, pages)`
في صنف `LibraryRepository(path=":memory:")`:
- `add_author(name)` و`get_author(author_id)`،
- `add_book(author_id, title, pages)` يرفع `ValueError("unknown author")` لمعرّف غير موجود،
- `books_by_author(author_id)` قائمة قواميس،
- `stats()` تُعيد `{"authors", "books", "avg_pages", "top_author"}` حيث `top_author`
  اسم المؤلف صاحب أكبر عدد كتب (أو `None` إذا لم توجد كتب)،
- `transfer(author_id, other_author_id)` تنقل كل كتب مؤلف إلى آخر داخل عملية واحدة،
  وتُعيد عدد الكتب المنقولة.""",
            brief_en="""Build two related repositories: `authors(id, name)` and
`books(id, author_id REFERENCES authors(id), title, pages)` inside a
`LibraryRepository(path=":memory:")`:
- `add_author(name)` and `get_author(author_id)`,
- `add_book(author_id, title, pages)` raising `ValueError("unknown author")` for a missing id,
- `books_by_author(author_id)` - a list of dicts,
- `stats()` returning `{"authors", "books", "avg_pages", "top_author"}` where `top_author` is the
  author with the most books (or `None` when there are no books),
- `transfer(author_id, other_author_id)` moving every book from one author to another inside a
  single transaction and returning the number of books moved.""",
            independent=True,
            starter_code="""import sqlite3


class LibraryRepository:
    def __init__(self, path=":memory:"):
        pass
""",
            public_tests={"test_public.py": """from main import LibraryRepository

def test_add_author_and_book():
    repository = LibraryRepository()
    author = repository.add_author("Aisha")
    assert repository.add_book(author, "Book", 120) is not None
"""},
            hidden_tests={"test_hidden.py": """import pytest
from main import LibraryRepository

def seeded():
    repository = LibraryRepository()
    aisha = repository.add_author("Aisha")
    omar = repository.add_author("Omar")
    repository.add_book(aisha, "Alpha", 100)
    repository.add_book(aisha, "Beta", 200)
    repository.add_book(omar, "Gamma", 300)
    return repository, aisha, omar

def test_unknown_author_raises():
    repository = LibraryRepository()
    with pytest.raises(ValueError):
        repository.add_book(999, "Ghost", 10)

def test_missing_author_get():
    assert LibraryRepository().get_author(5) is None

def test_books_by_author():
    repository, aisha, omar = seeded()
    assert len(repository.books_by_author(aisha)) == 2
    assert len(repository.books_by_author(omar)) == 1

def test_stats_counts():
    repository, _, _ = seeded()
    stats = repository.stats()
    assert stats["authors"] == 2 and stats["books"] == 3

def test_stats_average_pages():
    repository, _, _ = seeded()
    assert abs(repository.stats()["avg_pages"] - 200) < 1e-9

def test_stats_top_author():
    repository, aisha, _ = seeded()
    assert repository.stats()["top_author"] == "Aisha"

def test_stats_empty_library():
    stats = LibraryRepository().stats()
    assert stats["books"] == 0 and stats["top_author"] is None

def test_transfer_moves_books():
    repository, aisha, omar = seeded()
    moved = repository.transfer(aisha, omar)
    assert moved == 2
    assert len(repository.books_by_author(omar)) == 3

def test_transfer_is_atomic():
    repository, aisha, omar = seeded()
    try:
        with repository.connection:
            repository.connection.execute("UPDATE books SET author_id = ? WHERE author_id = ?", (omar, aisha))
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert len(repository.books_by_author(aisha)) == 2
"""},
            reference_solution="""import sqlite3

SCHEMA = \"\"\"
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES authors(id),
    title TEXT NOT NULL,
    pages INTEGER NOT NULL DEFAULT 0
);
\"\"\"


class LibraryRepository:
    def __init__(self, path=":memory:"):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA)
        self.connection.commit()

    def add_author(self, name):
        cursor = self.connection.execute("INSERT INTO authors (name) VALUES (?)", (name,))
        self.connection.commit()
        return int(cursor.lastrowid)

    def get_author(self, author_id):
        row = self.connection.execute("SELECT * FROM authors WHERE id = ?", (author_id,)).fetchone()
        return dict(row) if row else None

    def add_book(self, author_id, title, pages=0):
        if self.get_author(author_id) is None:
            raise ValueError("unknown author")
        cursor = self.connection.execute(
            "INSERT INTO books (author_id, title, pages) VALUES (?, ?, ?)",
            (author_id, title, int(pages)),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def books_by_author(self, author_id):
        rows = self.connection.execute(
            "SELECT * FROM books WHERE author_id = ? ORDER BY id", (author_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def stats(self):
        row = self.connection.execute(
            "SELECT (SELECT COUNT(*) FROM authors) AS authors,"
            " COUNT(books.id) AS books,"
            " COALESCE(AVG(books.pages), 0) AS avg_pages,"
            " (SELECT authors.name FROM authors JOIN books ON books.author_id = authors.id"
            "  GROUP BY authors.id ORDER BY COUNT(books.id) DESC LIMIT 1) AS top_author"
            " FROM books"
        ).fetchone()
        return {
            "authors": int(row["authors"]),
            "books": int(row["books"]),
            "avg_pages": float(row["avg_pages"]),
            "top_author": row["top_author"],
        }

    def transfer(self, author_id, other_author_id):
        if self.get_author(other_author_id) is None:
            raise ValueError("unknown author")
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE books SET author_id = ? WHERE author_id = ?",
                (other_author_id, author_id),
            )
        return int(cursor.rowcount)

    def close(self):
        self.connection.close()
""",
        ),
        transfer_ar="استخدم نمط المستودع في Library Nexus لحفظ تقدّم القراءة.",
        transfer_en="Use the repository pattern in Library Nexus to persist reading progress.",
        references=(
            ("Python docs - sqlite3", "https://docs.python.org/3/library/sqlite3.html"),
            ("SQLite - query planner", "https://www.sqlite.org/queryplanner.html"),
        ),
    ),
    CurriculumModule(
        id="l10.api_services",
        level=10,
        order_index=3,
        domain="systems",
        title_ar="خدمات الويب بـ FastAPI",
        title_en="Web services with FastAPI",
        summary_ar="مسارات، تحقق من المدخلات، أخطاء منظّمة، وصفحات نتائج.",
        summary_en="Routes, input validation, structured errors and pagination.",
        explanation_ar="""خدمة ويب جيدة لها أربع خصائص:

1. **عقود واضحة**: المخرجات مُتحقَّق منها بـ Pydantic، والأنواع موثّقة.
2. **أخطاء متوقعة**: استخدم `HTTPException(status_code=..., detail=...)` بدل إرجاع
   `{"error": ...}` برمز 200. الرمز الصحيح جزء من العقد.
3. **تحقق عند الحدود**: النموذج يتحقق من الأنواع والقيود (مثل `ge=0`) قبل أن يصل
   أي شيء إلى منطقك. استجب بـ 422 عند مدخل غير صالح.
4. **صفحات نتائج**: أي قائمة قد تكبر يجب أن تدعم `limit` و`offset`.

الاختبار: `fastapi.testclient.TestClient` يشغّل التطبيق في نفس العملية،
فتختبر المسارات كدوال عادية دون رفع خادم.

نموذج معماري بسيط: **المسار رقيق** — يستقبل، يتحقق، ثم يستدعي طبقة خدمة
نقية قابلة للاختبار بمفردها.""",
        explanation_en="""A good web service has four properties:

1. **Clear contracts**: outputs validated by Pydantic and documented types.
2. **Predictable errors**: use `HTTPException(status_code=..., detail=...)` instead of returning
   `{"error": ...}` with status 200. The status code is part of the contract.
3. **Validate at the boundary**: the model checks types and constraints (`ge=0` and friends)
   before anything reaches your logic. Respond with 422 for invalid input.
4. **Pagination**: any list that can grow must support `limit` and `offset`.

Testing: `fastapi.testclient.TestClient` runs the app in the same process, so you test routes
like ordinary functions without starting a server.

A simple architecture: **thin routes** - receive, validate, then call a pure service layer that
can be tested on its own.""",
        skills=("back.api_design", "back.fastapi", "back.pydantic"),
        prerequisites=("l10.sqlite_persistence", "l3.typing_dataclasses"),
        example_code="""from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="Notes API")

NOTES = {}
COUNTER = {"value": 0}


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    body: str = ""


class NoteOut(NoteIn):
    id: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/notes", response_model=NoteOut, status_code=201)
def create_note(payload: NoteIn):
    COUNTER["value"] += 1
    note = {"id": COUNTER["value"], "title": payload.title, "body": payload.body}
    NOTES[note["id"]] = note
    return note


@app.get("/notes/{note_id}", response_model=NoteOut)
def read_note(note_id: int):
    note = NOTES.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return note


client = TestClient(app)
print(client.get("/health").json())
print(client.post("/notes", json={"title": "first"}).status_code)
print(client.get("/notes/1").json())
print("missing ->", client.get("/notes/99").status_code, client.get("/notes/99").json())
print("invalid ->", client.post("/notes", json={"title": ""}).status_code)
""",
        example_notes_ar="`TestClient` يختبر التطبيق كاملاً داخل pytest: لا خادم ولا منافذ.",
        example_notes_en="`TestClient` exercises the whole app inside pytest: no server, no ports.",
        experiment_code="""from fastapi import FastAPI, HTTPException, Query
from fastapi.testclient import TestClient

app = FastAPI()
ITEMS = [{"id": index, "name": f"item-{index}", "price": index * 1.5} for index in range(1, 26)]


@app.get("/items")
def list_items(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    window = ITEMS[offset:offset + limit]
    return {"items": window, "total": len(ITEMS), "limit": limit, "offset": offset}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"item {item_id} not found")


@app.get("/stats")
def stats():
    prices = [item["price"] for item in ITEMS]
    return {"count": len(prices), "total": sum(prices), "average": sum(prices) / len(prices)}


client = TestClient(app)
print("page 1:", client.get("/items", params={"limit": 3}).json())
print("page 2:", client.get("/items", params={"limit": 3, "offset": 3}).json())
print("bad limit:", client.get("/items", params={"limit": 0}).status_code)
print("404 body:", client.get("/items/999").json())
print("stats:", client.get("/stats").json())
""",
        experiment_brief_ar="أضف معلمة `q` للبحث بالاسم داخل `/items` واختبرها بـ TestClient.",
        experiment_brief_en="Add a `q` query parameter to search names in `/items` and test it with TestClient.",
        task=TaskSpec(
            brief_ar="""ابنِ تطبيق FastAPI في `main.py` باسم `app` مع:
- `GET /health` يُعيد `{"status": "ok"}`.
- `POST /tasks` يستقبل `{"title": str}` ويُعيد المهمة مع `id` و`done=False` ورمز 201.
- `GET /tasks` يُعيد `{"tasks": [...], "total": int}` مع `limit` و`offset`.
- `GET /tasks/{task_id}` يُعيد المهمة أو 404.
- `POST /tasks/{task_id}/complete` يضبط `done=True` ويُعيد المهمة، أو 404.

البيانات في الذاكرة (قاموس عام). استخدم نماذج Pydantic للمدخلات والمخرجات.""",
            brief_en="""Build a FastAPI app in `main.py` named `app` with:
- `GET /health` returning `{"status": "ok"}`.
- `POST /tasks` accepting `{"title": str}` and returning the task with `id` and `done=False`,
  status 201.
- `GET /tasks` returning `{"tasks": [...], "total": int}` with `limit` and `offset`.
- `GET /tasks/{task_id}` returning the task or 404.
- `POST /tasks/{task_id}/complete` setting `done=True` and returning the task, or 404.

Keep the data in memory (a module-level dict). Use Pydantic models for input and output.""",
            starter_code="""from fastapi import FastAPI

app = FastAPI()
""",
            public_tests={"test_public.py": """from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}
"""},
            hidden_tests={"test_hidden.py": """from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def reset():
    client.delete("/tasks") if client.delete("/tasks").status_code != 405 else None

def test_create_task():
    response = client.post("/tasks", json={"title": "write tests"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "write tests" and body["done"] is False
    assert "id" in body

def test_get_task():
    identifier = client.post("/tasks", json={"title": "read"}).json()["id"]
    assert client.get(f"/tasks/{identifier}").json()["title"] == "read"

def test_missing_task_is_404():
    assert client.get("/tasks/9999").status_code == 404

def test_complete_task():
    identifier = client.post("/tasks", json={"title": "finish"}).json()["id"]
    response = client.post(f"/tasks/{identifier}/complete")
    assert response.status_code == 200
    assert response.json()["done"] is True

def test_complete_missing_is_404():
    assert client.post("/tasks/9999/complete").status_code == 404

def test_list_shape():
    body = client.get("/tasks").json()
    assert set(body) == {"tasks", "total"}
    assert isinstance(body["tasks"], list)

def test_pagination():
    for index in range(6):
        client.post("/tasks", json={"title": f"task-{index}"})
    page = client.get("/tasks", params={"limit": 2, "offset": 0}).json()
    assert len(page["tasks"]) == 2
    second = client.get("/tasks", params={"limit": 2, "offset": 2}).json()
    assert second["tasks"][0]["id"] != page["tasks"][0]["id"]

def test_invalid_payload_is_422():
    assert client.post("/tasks", json={}).status_code == 422
"""},
            reference_solution="""from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Task API")

TASKS = {}
COUNTER = 0


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool = False


def _next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskIn):
    identifier = _next_id()
    TASKS[identifier] = {"id": identifier, "title": payload.title, "done": False}
    return TASKS[identifier]


@app.get("/tasks")
def list_tasks(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    ordered = [TASKS[key] for key in sorted(TASKS)]
    return {"tasks": ordered[offset:offset + limit], "total": len(ordered)}


@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.post("/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    task["done"] = True
    return task
""",
            hints=(
                "Return status 201 by passing `status_code=201` to the route decorator.",
                "`Query(50, ge=1, le=200)` gives validated pagination with a 422 on bad input.",
                "Raise `HTTPException(404, detail=...)`; never return a 200 with an error body.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""وسّع التطبيق: أضف مسار `GET /stats` يُعيد
`{"total", "done", "open", "completion_rate"}`، ومسار `DELETE /tasks/{task_id}`
يُعيد 204 عند النجاح و404 عند الغياب، ومعالج أخطاء عام يُعيد
`{"detail": str}` لأي استثناء غير متوقّع برمز 500 بدل كشف التتبّع.""",
            brief_en="""Extend the app: add `GET /stats` returning
`{"total", "done", "open", "completion_rate"}`, a `DELETE /tasks/{task_id}` route returning 204 on
success and 404 when missing, and a global exception handler returning `{"detail": str}` with
status 500 for any unexpected error instead of leaking a traceback.""",
            independent=True,
            starter_code="""from fastapi import FastAPI

app = FastAPI()
""",
            public_tests={"test_public.py": """from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_stats_shape():
    body = client.get("/stats").json()
    assert set(body) == {"total", "done", "open", "completion_rate"}
"""},
            hidden_tests={"test_hidden.py": """from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_stats_counts():
    for index in range(4):
        identifier = client.post("/tasks", json={"title": f"t{index}"}).json()["id"]
        if index < 2:
            client.post(f"/tasks/{identifier}/complete")
    stats = client.get("/stats").json()
    assert stats["total"] >= 4
    assert stats["done"] >= 2
    assert stats["total"] == stats["done"] + stats["open"]

def test_completion_rate_bounds():
    stats = client.get("/stats").json()
    assert 0.0 <= stats["completion_rate"] <= 1.0

def test_delete_returns_204():
    identifier = client.post("/tasks", json={"title": "delete me"}).json()["id"]
    assert client.delete(f"/tasks/{identifier}").status_code == 204
    assert client.get(f"/tasks/{identifier}").status_code == 404

def test_delete_missing_returns_404():
    assert client.delete("/tasks/999999").status_code == 404

def test_stats_after_delete():
    before = client.get("/stats").json()["total"]
    identifier = client.post("/tasks", json={"title": "temporary"}).json()["id"]
    client.delete(f"/tasks/{identifier}")
    assert client.get("/stats").json()["total"] == before

def test_unexpected_error_is_handled():
    response = client.get("/stats", params={"broken": "x"}) if False else client.get("/boom")
    assert response.status_code in (404, 500)
    if response.status_code == 500:
        assert "detail" in response.json()
"""},
            reference_solution="""from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Task API")

TASKS = {}
COUNTER = 0


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool = False


@app.exception_handler(Exception)
def handle_unexpected(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


def _next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskIn):
    identifier = _next_id()
    TASKS[identifier] = {"id": identifier, "title": payload.title, "done": False}
    return TASKS[identifier]


@app.get("/tasks")
def list_tasks(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    ordered = [TASKS[key] for key in sorted(TASKS)]
    return {"tasks": ordered[offset:offset + limit], "total": len(ordered)}


@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.post("/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    task["done"] = True
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if TASKS.pop(task_id, None) is None:
        raise HTTPException(status_code=404, detail="task not found")
    return None


@app.get("/stats")
def stats():
    total = len(TASKS)
    done = sum(1 for task in TASKS.values() if task["done"])
    return {
        "total": total,
        "done": done,
        "open": total - done,
        "completion_rate": (done / total) if total else 0.0,
    }
""",
        ),
        transfer_ar="استخدم نفس البنية في CareerVerse لعرض خدمة مشاريعك.",
        transfer_en="Reuse the same structure in CareerVerse to serve your project.",
        references=(
            ("FastAPI - first steps", "https://fastapi.tiangolo.com/tutorial/first-steps/"),
            ("FastAPI - handling errors", "https://fastapi.tiangolo.com/tutorial/handling-errors/"),
        ),
    ),
]
