"""The reference library: short, runnable, bilingual explanations.

Every entry carries one or more *executable* snippets. The library is not a
documentation dump: the point is that the learner can run each snippet and
see the real output.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class LibraryEntry:
    id: str
    domain: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    body_ar: str
    body_en: str
    examples: tuple[tuple[str, str], ...] = ()
    skills: tuple[str, ...] = field(default=())

    def title(self, locale: str = "en") -> str:
        return self.title_ar if locale == "ar" else self.title_en

    def summary(self, locale: str = "en") -> str:
        return self.summary_ar if locale == "ar" else self.summary_en

    def body(self, locale: str = "en") -> str:
        return self.body_ar if locale == "ar" else self.body_en

    def to_dict(self, locale: str = "en") -> dict:
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title(locale),
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "summary": self.summary(locale),
            "summary_ar": self.summary_ar,
            "summary_en": self.summary_en,
            "body": self.body(locale),
            "body_ar": self.body_ar,
            "body_en": self.body_en,
            "examples": [{"label": label, "code": code} for label, code in self.examples],
            "example_count": len(self.examples),
            "skills": list(self.skills),
        }


ENTRIES: tuple[LibraryEntry, ...] = (
    LibraryEntry(
        id="lib.list_patterns",
        domain="core",
        title_ar="أنماط القوائم",
        title_en="List patterns",
        summary_ar="العمليات اليومية على القوائم مع تكلفة كل منها.",
        summary_en="Everyday list operations and what each one costs.",
        body_ar="""`list` مصفوفة ديناميكية: الفهرسة `O(1)`، والإضافة من الطرف `O(1)` وسطياً،
والبحث `O(n)`، والإدراج في المنتصف `O(n)`.

- استخدم `deque` إذا أردت الإضافة/الحذف من الطرفين بكفاءة.
- استخدم `set` للبحث عن العضوية.
- التقطيع `items[:]` ينسخ القائمة (سطحياً).
- `sort()` ترتّب في المكان و`sorted()` تُعيد نسخة.""",
        body_en="""A `list` is a dynamic array: indexing is `O(1)`, appending is amortised `O(1)`,
membership is `O(n)` and inserting in the middle is `O(n)`.

- use `deque` when you need fast operations at both ends;
- use `set` for membership tests;
- slicing `items[:]` copies the list (shallowly);
- `sort()` sorts in place while `sorted()` returns a copy.""",
        examples=(
            (
                "slicing and copying",
                "items = [1, 2, 3, 4, 5]\nprint(items[1:4], items[::-1])\nshallow = items[:]\nshallow[0] = 99\nprint(items[0], shallow[0])\n",
            ),
            (
                "sorting with keys",
                "words = [\"date\", \"fig\", \"apple\"]\nprint(sorted(words, key=len))\nprint(sorted(words, key=lambda w: (len(w), w)))\n",
            ),
            (
                "membership cost",
                "import time\n\nvalues = list(range(200_000))\nlookup = set(values)\n\ndef measure(test):\n    start = time.perf_counter()\n    test()\n    return round((time.perf_counter() - start) * 1000, 3)\n\nprint(\"list:\", measure(lambda: 199_999 in values), \"ms\")\nprint(\"set :\", measure(lambda: 199_999 in lookup), \"ms\")\n",
            ),
        ),
        skills=("core.variables", "core.loops"),
    ),
    LibraryEntry(
        id="lib.dict_patterns",
        domain="core",
        title_ar="أنماط القواميس",
        title_en="Dict patterns",
        summary_ar="القاموس كأداة فهرسة وعدّ وتجميع.",
        summary_en="The dict as an index, a counter and a grouping tool.",
        body_ar="""`dict` جدول تجزئة: البحث والإدراج `O(1)` وسطياً.

أنماط تستحق الحفظ:
- `dict.get(key, default)` لتجنّب `KeyError`،
- `collections.defaultdict` للتجميع،
- `collections.Counter` للعدّ،
- `setdefault` لإضافة مفتاح بقيمة ابتدائية،
- `d1 | d2` (بايثون 3.9+) لدمج قاموسين.""",
        body_en="""A `dict` is a hash table: lookup and insertion are amortised `O(1)`.

Patterns worth memorising:
- `dict.get(key, default)` to avoid `KeyError`,
- `collections.defaultdict` for grouping,
- `collections.Counter` for counting,
- `setdefault` to insert a key with an initial value,
- `d1 | d2` (Python 3.9+) to merge two dicts.""",
        examples=(
            (
                "grouping",
                "from collections import defaultdict\n\nrows = [(\"a\", 1), (\"b\", 2), (\"a\", 3)]\ngroups = defaultdict(list)\nfor key, value in rows:\n    groups[key].append(value)\nprint(dict(groups))\n",
            ),
            (
                "counting",
                "from collections import Counter\n\nprint(Counter(\"mississippi\").most_common(2))\nprint(Counter([\"a\", \"b\", \"a\"]) + Counter([\"b\"]))\n",
            ),
            (
                "merging and defaults",
                "base = {\"a\": 1}\noverrides = {\"b\": 2}\nprint(base | overrides)\nprint(base.get(\"missing\", \"fallback\"))\n",
            ),
        ),
        skills=("core.variables", "core.loops"),
    ),
    LibraryEntry(
        id="lib.itertools_recipes",
        domain="stdlib",
        title_ar="أدوات التكرار",
        title_en="Iteration tools",
        summary_ar="`itertools` و`enumerate` و`zip` لكتابة حلقات أنظف.",
        summary_en="`itertools`, `enumerate` and `zip` for cleaner loops.",
        body_ar="""أغلب الحلقات اليدوية لها مكافئ جاهز وأسرع:

- `enumerate(items)` للفهرس والقيمة،
- `zip(a, b)` للمرور على تسلسلين معاً،
- `itertools.groupby` للتجميع (يتطلب بيانات مرتّبة)،
- `itertools.accumulate` للمجاميع التراكمية،
- `itertools.product` للتوليفات،
- `any()` / `all()` للشروط.""",
        body_en="""Most hand-written loops have a faster built-in equivalent:

- `enumerate(items)` for index and value,
- `zip(a, b)` to walk two sequences together,
- `itertools.groupby` for grouping (requires sorted data),
- `itertools.accumulate` for running totals,
- `itertools.product` for combinations,
- `any()` / `all()` for conditions.""",
        examples=(
            (
                "enumerate and zip",
                "names = [\"a\", \"b\"]\nscores = [10, 20]\nfor index, name in enumerate(names, start=1):\n    print(index, name)\nprint(list(zip(names, scores)))\n",
            ),
            (
                "groupby needs sorting",
                "from itertools import groupby\n\nrows = sorted([\"apple\", \"avocado\", \"banana\"], key=lambda w: w[0])\nfor letter, words in groupby(rows, key=lambda w: w[0]):\n    print(letter, list(words))\n",
            ),
            (
                "accumulate and product",
                "from itertools import accumulate, product\n\nprint(list(accumulate([1, 2, 3])))\nprint(list(product([0, 1], repeat=2)))\n",
            ),
        ),
        skills=("stdlib.itertools", "core.loops"),
    ),
    LibraryEntry(
        id="lib.pathlib_files",
        domain="stdlib",
        title_ar="الملفات والمسارات",
        title_en="Files and paths",
        summary_ar="`pathlib` بدلاً من تجميع النصوص يدوياً.",
        summary_en="`pathlib` instead of gluing strings together.",
        body_ar="""`pathlib.Path` يعامل المسار ككائن: يقرأ ويكتب ويبحث بأنماط، ويعمل على كل
الأنظمة. استخدمه دائماً بدل `os.path.join` مع نصوص.

- `Path.read_text(encoding="utf-8")` و`write_text(...)`،
- `Path.glob("**/*.py")` للبحث،
- عوامل `/` لبناء المسارات،
- `with path.open() as handle:` لضمان الإغلاق.""",
        body_en="""`pathlib.Path` treats a path as an object: it reads, writes and globs, and works on every
platform. Use it instead of string concatenation with `os.path.join`.

- `Path.read_text(encoding="utf-8")` and `write_text(...)`,
- `Path.glob("**/*.py")` to search,
- the `/` operator to build paths,
- `with path.open() as handle:` to guarantee the file is closed.""",
        examples=(
            (
                "reading and writing",
                "import tempfile\nfrom pathlib import Path\n\nroot = Path(tempfile.mkdtemp())\nfile = root / \"notes.txt\"\nfile.write_text(\"hello\\n\", encoding=\"utf-8\")\nprint(file.read_text(encoding=\"utf-8\").strip())\nprint(sorted(p.name for p in root.glob(\"*\")))\n",
            ),
            (
                "walking a tree",
                "import tempfile\nfrom pathlib import Path\n\nroot = Path(tempfile.mkdtemp())\n(root / \"pkg\").mkdir()\n(root / \"pkg\" / \"mod.py\").write_text(\"x = 1\\n\", encoding=\"utf-8\")\nprint(sorted(str(p.relative_to(root)) for p in root.glob(\"**/*.py\")))\n",
            ),
        ),
        skills=("stdlib.pathlib", "core.files"),
    ),
    LibraryEntry(
        id="lib.testing_patterns",
        domain="pro",
        title_ar="أنماط الاختبار",
        title_en="Testing patterns",
        summary_ar="اختبارات صغيرة وسريعة ومستقلة.",
        summary_en="Small, fast and independent tests.",
        body_ar="""الاختبار الجيد: سريع، مستقل، وواضح السبب عند فشله.

- Arrange / Act / Assert: جهّز، نفّذ، تحقّق.
- استخدم `pytest.raises` للاستثناءات، و`capsys` للمخرجات، و`tmp_path` للملفات.
- لا تجعل الاختبارات تعتمد على بعضها.
- اذكر الحدود: القيم الفارغة، والسالبة، والمتكررة.""",
        body_en="""A good test is fast, independent and obvious about why it failed.

- Arrange / Act / Assert: set up, run, verify.
- use `pytest.raises` for exceptions, `capsys` for output and `tmp_path` for files;
- never make tests depend on each other;
- cover the boundaries: empty, negative and duplicate values.""",
        examples=(
            (
                "boundaries and exceptions",
                "import pytest\n\n\ndef parse(value):\n    if not value:\n        raise ValueError(\"empty\")\n    return int(value)\n\n\ndef test_parses():\n    assert parse(\"12\") == 12\n\n\ndef test_rejects_empty():\n    with pytest.raises(ValueError):\n        parse(\"\")\n",
            ),
            (
                "capsys and tmp_path",
                "def test_output(capsys):\n    print(\"hello\")\n    assert \"hello\" in capsys.readouterr().out\n\n\ndef test_files(tmp_path):\n    target = tmp_path / \"a.txt\"\n    target.write_text(\"data\", encoding=\"utf-8\")\n    assert target.read_text(encoding=\"utf-8\") == \"data\"\n",
            ),
        ),
        skills=("stdlib.unittest_pytest", "pro.testing"),
    ),
    LibraryEntry(
        id="lib.debugging_recipes",
        domain="pro",
        title_ar="وصفات تنقيح الأخطاء",
        title_en="Debugging recipes",
        summary_ar="من التتبّع إلى الاختبار المصغّر (regression test).",
        summary_en="From the traceback to a minimal regression test.",
        body_ar="""خطوات منهجية:
1. اقرأ التتبّع من الأسفل: آخر سطر هو السبب المباشر.
2. أعد إنتاج الخطأ بأصغر مدخل ممكن.
3. اطبع الحالة عند النقطة المشبوهة، أو استخدم `breakpoint()`.
4. اكتب اختباراً يفشل الآن — سيصبح دليلك على الإصلاح.
5. أصلح السبب لا العَرَض.""",
        body_en="""A systematic path:
1. read the traceback from the bottom: the last line is the immediate cause;
2. reproduce the failure with the smallest possible input;
3. print the state at the suspicious point, or drop into `breakpoint()`;
4. write a test that fails now - it becomes your proof of the fix;
5. fix the cause, not the symptom.""",
        examples=(
            (
                "inspecting state",
                "def buggy(values):\n    total = 0\n    for value in values:\n        total += 1          # BUG: adds the counter, not the value\n    return total\n\n\ndef fixed(values):\n    return sum(values)\n\n\nprint(\"buggy:\", buggy([1, 2, 3]))\nprint(\"fixed:\", fixed([1, 2, 3]))\n",
            ),
            (
                "tracebacks",
                "try:\n    {}[\"missing\"]\nexcept KeyError as error:\n    print(\"caught:\", type(error).__name__, error)\n    import traceback\n    print(\"\".join(traceback.format_exc()).strip().splitlines()[-1])\n",
            ),
        ),
        skills=("pro.debugging", "core.exceptions"),
    ),
    LibraryEntry(
        id="lib.performance_checklist",
        domain="pro",
        title_ar="قائمة تحسين الأداء",
        title_en="Performance checklist",
        summary_ar="قِس، بدّل الرتبة، استخدم المكتبات الموجّهة.",
        summary_en="Measure, change the order of growth, then reach for vectorisation.",
        body_ar="""1. قِس أولاً بـ `time.perf_counter` و`cProfile`.
2. بدّل الخوارزمية قبل تحسين التفاصيل: `O(n²)` → `O(n log n)` يتفوّق على أي تلميع.
3. استخدم البنى الصحيحة: `set` للبحث، `deque` للطوابير، `heapq` للأولويات.
4. للبيانات الرقمية الكبيرة: numpy.
5. احفظ النتائج المتكررة بـ `functools.lru_cache`.""",
        body_en="""1. measure first with `time.perf_counter` and `cProfile`;
2. change the algorithm before polishing details: `O(n^2)` -> `O(n log n)` beats any micro-tuning;
3. pick the right structure: `set` for lookup, `deque` for queues, `heapq` for priorities;
4. for large numeric data: numpy;
5. cache repeated results with `functools.lru_cache`.""",
        examples=(
            (
                "caching",
                "import time\nfrom functools import lru_cache\n\n\n@lru_cache(maxsize=None)\ndef fib(n):\n    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\n\nstart = time.perf_counter()\nfib(300)\nprint(\"cached fib(300) in\", round((time.perf_counter() - start) * 1000, 3), \"ms\")\n",
            ),
            (
                "vectorisation",
                "import time\n\nimport numpy as np\n\nvalues = list(range(2_000_000))\narray = np.arange(2_000_000)\n\nstart = time.perf_counter()\nsum(v * v for v in values)\nloop_time = time.perf_counter() - start\n\nstart = time.perf_counter()\n(array * array).sum()\nnumpy_time = time.perf_counter() - start\n\nprint(\"loop :\", round(loop_time * 1000, 2), \"ms\")\nprint(\"numpy:\", round(numpy_time * 1000, 2), \"ms\")\n",
            ),
        ),
        skills=("pro.performance", "adv.optimization"),
    ),
    LibraryEntry(
        id="lib.typing_hints",
        domain="pro",
        title_ar="التلميحات النوعية",
        title_en="Type hints",
        summary_ar="أنواع تخدم القارئ والأدوات معاً.",
        summary_en="Types that serve both the reader and the tooling.",
        body_ar="""التلميحات لا تغيّر سلوك التشغيل، لكنها تجعل العقد صريحاً.

- ابدأ بتلميح الدوال العامة: `def f(x: int) -> str`.
- استخدم `Optional[str]` أو `str | None` (3.10+) للقيم الاختيارية.
- اجمع الأنواع في `TypeAlias` عند تكرارها.
- شغّل `mypy` أو `pyright` في التكامل المستقل.""",
        body_en="""Hints do not change runtime behaviour, but they make the contract explicit.

- start with public functions: `def f(x: int) -> str`;
- use `Optional[str]` or `str | None` (3.10+) for optional values;
- collect repeated shapes into a `TypeAlias`;
- run `mypy` or `pyright` in CI.""",
        examples=(
            (
                "hints and unions",
                "from __future__ import annotations\n\n\ndef parse(value: str) -> int | None:\n    try:\n        return int(value)\n    except ValueError:\n        return None\n\n\nprint(parse(\"42\"), parse(\"x\"))\n",
            ),
            (
                "generic containers",
                "from __future__ import annotations\n\n\ndef tally(values: list[str]) -> dict[str, int]:\n    counts: dict[str, int] = {}\n    for value in values:\n        counts[value] = counts.get(value, 0) + 1\n    return counts\n\n\nprint(tally([\"a\", \"b\", \"a\"]))\n",
            ),
        ),
        skills=("pro.typing", "pro.typing_advanced"),
    ),
    LibraryEntry(
        id="lib.virtual_environments",
        domain="pro",
        title_ar="البيئات الافتراضية",
        title_en="Virtual environments",
        summary_ar="عزل التبعيات عن نظام التشغيل.",
        summary_en="Keeping dependencies away from the system Python.",
        body_ar="""لكل مشروع بيئته:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pip freeze > requirements.txt
```

- لا تثبّت الحزم عالمياً.
- أضف `.venv/` إلى `.gitignore`.
- ثبّت الإصدارات في ملف لتكرار البيئة."""
        ,
        body_en="""Every project gets its own environment:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pip freeze > requirements.txt
```

- never install packages globally;
- add `.venv/` to `.gitignore`;
- pin versions in a file so the environment can be rebuilt.""",
        examples=(
            (
                "inspecting the interpreter",
                "import sys\n\nprint(sys.executable)\nprint(sys.version.split()[0])\n",
            ),
            (
                "listing installed packages",
                "import importlib.metadata as md\n\nnames = sorted(d.metadata[\"Name\"] for d in md.distributions() if d.metadata[\"Name\"])\nprint(\"installed:\", len(names))\nprint(\"first five:\", names[:5])\n",
            ),
        ),
        skills=("pro.venv", "pro.packaging"),
    ),
    LibraryEntry(
        id="lib.logging_basics",
        domain="pro",
        title_ar="أساسيات التسجيل",
        title_en="Logging basics",
        summary_ar="سجلات منظّمة بدل `print` في كل مكان.",
        summary_en="Structured logs instead of `print` everywhere.",
        body_ar="""`logging` يعطيك مستويات ووجهات وتهيئة مركزية:

- `DEBUG` أثناء التطوير، `INFO` للتشغيل الطبيعي، `WARNING` و`ERROR` للمشاكل.
- هيّئ المسجّل مرة واحدة في نقطة الدخول.
- لا تسجّل أسراراً أو بيانات شخصية.""",
        body_en="""`logging` gives you levels, destinations and central configuration:

- `DEBUG` while developing, `INFO` for normal operation, `WARNING` and `ERROR` for problems;
- configure the logger once, at the entry point;
- never log secrets or personal data.""",
        examples=(
            (
                "levels and formatting",
                "import logging\n\nlogging.basicConfig(level=logging.INFO, format=\"%(levelname)s %(message)s\")\nlog = logging.getLogger(\"demo\")\nlog.info(\"started\")\nlog.warning(\"disk is %d%% full\", 91)\n",
            ),
            (
                "capturing records",
                "import logging\n\nlog = logging.getLogger(\"capture\")\nrecords = []\n\n\nclass Collector(logging.Handler):\n    def emit(self, record):\n        records.append(record.getMessage())\n\n\nlog.addHandler(Collector())\nlog.setLevel(logging.INFO)\nlog.info(\"hello\")\nprint(records)\n",
            ),
        ),
        skills=("pro.logging", "stdlib.logging_lib"),
    ),
    LibraryEntry(
        id="lib.numpy_idioms",
        domain="data",
        title_ar="تعبيرات NumPy المعتادة",
        title_en="NumPy idioms",
        summary_ar="أقنعة، بث، ومحاور.",
        summary_en="Masks, broadcasting and axes.",
        body_ar="""- الأقنعة: `values[values > 0]` نسخة، و`values[values > 0] = 0` تعديل في المكان.
- البث: الأبعاد تُقارن من اليمين؛ `1` أو الغائب يُمدّد.
- المحاور: `axis=0` على الأعمدة، `axis=1` على الصفوف.
- `np.where` بديل موجّه لـ `if` داخل الحلقة.""",
        body_en="""- masks: `values[values > 0]` copies, `values[values > 0] = 0` writes in place;
- broadcasting: dimensions are compared from the right; `1` or a missing axis is stretched;
- axes: `axis=0` runs over rows (columns), `axis=1` over columns (rows);
- `np.where` is the vectorised replacement for an `if` inside a loop.""",
        examples=(
            (
                "masks and where",
                "import numpy as np\n\nvalues = np.array([-1, 2, -3, 4])\nprint(values[values > 0])\nprint(np.where(values < 0, 0, values))\n",
            ),
            (
                "axes",
                "import numpy as np\n\nmatrix = np.arange(6).reshape(2, 3)\nprint(\"matrix:\\n\", matrix)\nprint(\"mean per column:\", matrix.mean(axis=0))\nprint(\"mean per row   :\", matrix.mean(axis=1))\n",
            ),
        ),
        skills=("data.numpy", "data.numpy_advanced"),
    ),
)

_BY_ID = {entry.id: entry for entry in ENTRIES}


def get_entry(entry_id: str) -> LibraryEntry:
    if entry_id not in _BY_ID:
        raise KeyError(f"unknown library entry: {entry_id}")
    return _BY_ID[entry_id]


def all_entries() -> list[LibraryEntry]:
    return list(ENTRIES)


def validate_library() -> list[str]:
    problems = []
    seen = set()
    for entry in ENTRIES:
        if entry.id in seen:
            problems.append(f"duplicate library id: {entry.id}")
        seen.add(entry.id)
        if not entry.examples:
            problems.append(f"{entry.id}: no executable examples")
        for label, code in entry.examples:
            if not label.strip() or not code.strip():
                problems.append(f"{entry.id}: empty example")
    return problems
