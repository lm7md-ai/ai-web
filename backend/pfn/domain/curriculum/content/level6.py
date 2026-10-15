"""LEVEL 6 - Algorithms and data structures."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l6.complexity",
        level=6,
        order_index=1,
        domain="algorithms",
        title_ar="تحليل التعقيد",
        title_en="Complexity analysis",
        summary_ar="Big-O بالقياس لا بالحفظ: كيف تكتشف عنق الزجاجة فعلياً.",
        summary_en="Big-O by measurement, not memorisation: finding the real bottleneck.",
        explanation_ar="""التعقيد وصفٌ لكيفية **نمو** زمن التنفيذ (أو الذاكرة) مع حجم المدخل، لا رقم ثابت.

الرتب الشائعة من الأفضل للأسوأ:

| الرتبة | مثال واقعي |
|---|---|
| O(1) | قراءة عنصر بقاموس أو فهرس |
| O(log n) | بحث ثنائي في مصفوفة مرتّبة |
| O(n) | مسح قائمة مرة واحدة |
| O(n log n) | ترتيب مقارن جيد (merge sort) |
| O(n²) | مقارنة كل زوج (حلقتان متداخلتان) |
| O(2ⁿ) | تجريب كل المجموعات الفرعية |

قواعد عملية:
- احذف الثوابت والعوامل غير المهيمنة: `3n² + 10n + 5` هي `O(n²)`.
- حلقتان متداخلتان على نفس `n` تعنيان غالباً `O(n²)` — لكن انتبه للحلقات التي تتقلص.
- تكلفة العمليات المدمجة مهمة: `x in list` هو `O(n)` بينما `x in set` هو `O(1)`.
- **قِس قبل أن تُحسّن**: استخدم `time.perf_counter` ونِسب النمو، لا الانطباع.

طريقة النسبة: ضاعف حجم المدخل. إذا تضاعف الزمن تقريباً → `O(n)`. إذا تضاعف أربع مرات → `O(n²)`.
إذا زاد بمقدار ثابت → `O(log n)`.""",
        explanation_en="""Complexity describes how runtime (or memory) **grows** with input size, not a fixed number.

Common orders, best to worst:

| order | real example |
|---|---|
| O(1) | reading a dict entry or an index |
| O(log n) | binary search in a sorted array |
| O(n) | one pass over a list |
| O(n log n) | a good comparison sort (merge sort) |
| O(n^2) | comparing every pair (nested loops) |
| O(2^n) | trying every subset |

Practical rules:
- drop constants and non-dominant terms: `3n^2 + 10n + 5` is `O(n^2)`.
- two nested loops over the same `n` usually mean `O(n^2)` - but watch for shrinking loops.
- the cost of built-in operations matters: `x in list` is `O(n)` while `x in set` is `O(1)`.
- **measure before optimising**: use `time.perf_counter` and growth ratios, not intuition.

The ratio method: double the input. If the time roughly doubles -> `O(n)`. If it quadruples ->
`O(n^2)`. If it grows by a constant amount -> `O(log n)`.""",
        skills=("algo.complexity", "algo.benchmarking", "ds.lists"),
        prerequisites=("l1.lists_tuples", "l1.dicts_sets"),
        example_code="""import random
import time

HITS = 5000


def membership_list(values, targets):
    return sum(1 for target in targets if target in values)


def membership_set(values, targets):
    lookup = set(values)
    return sum(1 for target in targets if target in lookup)


def measure(function, size):
    values = list(range(size))
    random.shuffle(values)
    targets = [random.randrange(size) for _ in range(HITS)]
    start = time.perf_counter()
    function(values, targets)
    return (time.perf_counter() - start) * 1000


print(f"{'n':>8} {'list (ms)':>12} {'set (ms)':>12}")
for size in (1000, 2000, 4000, 8000):
    list_time = measure(membership_list, size)
    set_time = measure(membership_set, size)
    print(f"{size:>8} {list_time:>12.2f} {set_time:>12.2f}")

print("")
print("the list column grows with n, the set column does not: O(n) against O(1).")
""",
        example_notes_ar="شغّل بأحجام أكبر (مثلاً 50000) وشاهد كيف تنهار نسخة القائمة.",
        example_notes_en="Run it with bigger sizes (50000) and watch the list version collapse.",
        experiment_code="""import time


def quadratic(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return total


def linear(n):
    return sum(1 for _ in range(n))


def logarithmic(n):
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps


def measure(function, n):
    start = time.perf_counter()
    function(n)
    return (time.perf_counter() - start) * 1000


print(f"{'n':>8} {'O(n)':>10} {'O(n^2)':>10} {'O(log n)':>10}")
for n in (200, 400, 800, 1600):
    print(f"{n:>8} {measure(linear, n):>10.3f} {measure(quadratic, n):>10.3f} {measure(logarithmic, n):>10.3f}")
""",
        experiment_brief_ar="استنتج رتبة كل دالة من نسبة النمو بين صفين متتاليين، واكتب استنتاجك في تعليق.",
        experiment_brief_en="Derive each function's order from the growth ratio between two consecutive rows and write your conclusion in a comment.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `has_duplicate_quadratic(values)` تتحقق من وجود تكرار بمقارنة كل زوج (O(n²)).
2. `has_duplicate_linear(values)` تفعل ذلك بمجموعة (O(n)).
3. `pair_with_sum(values, target)` تُعيد أول زوج فهارس `(i, j)` مجموعهما `target`
   بخوارزمية O(n) باستخدام قاموس، أو `None`.""",
            brief_en="""Write:
1. `has_duplicate_quadratic(values)` detecting a duplicate by comparing every pair (O(n^2)).
2. `has_duplicate_linear(values)` doing the same with a set (O(n)).
3. `pair_with_sum(values, target)` returning the first index pair `(i, j)` summing to `target`
   with an O(n) algorithm using a dict, or `None`.""",
            starter_code="""def has_duplicate_quadratic(values):
    pass


def has_duplicate_linear(values):
    pass


def pair_with_sum(values, target):
    pass
""",
            public_tests={
                "test_public.py": """from main import has_duplicate_linear

def test_duplicate():
    assert has_duplicate_linear([1, 2, 3, 2]) is True
    assert has_duplicate_linear([1, 2, 3]) is False
"""},
            hidden_tests={
                "test_hidden.py": """import time
from main import has_duplicate_quadratic, has_duplicate_linear, pair_with_sum

def test_quadratic_agrees():
    assert has_duplicate_quadratic([1, 2, 1]) is True
    assert has_duplicate_quadratic([1, 2, 3]) is False

def test_empty_and_single():
    assert has_duplicate_linear([]) is False
    assert has_duplicate_linear([5]) is False

def test_pair_found():
    assert pair_with_sum([2, 7, 11, 15], 9) == (0, 1)

def test_pair_absent():
    assert pair_with_sum([1, 2, 3], 100) is None

def test_pair_no_self_pairing():
    assert pair_with_sum([5], 10) is None

def test_pair_negative_numbers():
    assert pair_with_sum([-3, 4, 3, 90], 0) in {(0, 2), (2, 0)}

def test_quadratic_is_slower():
    values = list(range(1500))
    start = time.perf_counter()
    has_duplicate_quadratic(values)
    slow = time.perf_counter() - start
    start = time.perf_counter()
    has_duplicate_linear(values)
    fast = time.perf_counter() - start
    assert slow > fast
"""},
            reference_solution="""def has_duplicate_quadratic(values):
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] == values[j]:
                return True
    return False


def has_duplicate_linear(values):
    seen = set()
    for value in values:
        if value in seen:
            return True
        seen.add(value)
    return False


def pair_with_sum(values, target):
    positions = {}
    for index, value in enumerate(values):
        complement = target - value
        if complement in positions:
            return (positions[complement], index)
        positions[value] = index
    return None
""",
            hints=(
                "Starting the inner loop at `i + 1` avoids comparing an element with itself.",
                "A set gives O(1) membership, which is what makes the linear version linear.",
                "Store each value's index in a dict as you scan, and look for the complement first.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب أداة قياس: `estimate_order(function, sizes, repeats=3)` حيث `function` تأخذ عدداً صحيحاً
`n` وتُنفّذ عملاً. تُعيد الأداة قاموساً:

```python
{"sizes": [...], "times": [...], "ratios": [...], "guess": "O(1)|O(log n)|O(n)|O(n^2)"}
```

`ratios[i] = times[i+1] / times[i]`. التخمين:
- أقل من 1.4 → `O(log n)`
- بين 1.4 و3 → `O(n)`
- أكبر من 3 → `O(n^2)`

استخدم `time.perf_counter` وأفضل نتيجة من عدة تكرارات.""",
            brief_en="""Write a measurement tool: `estimate_order(function, sizes, repeats=3)` where `function`
takes an integer `n` and does work. Return a dict:

```python
{"sizes": [...], "times": [...], "ratios": [...], "guess": "O(1)|O(log n)|O(n)|O(n^2)"}
```

`ratios[i] = times[i+1] / times[i]`. The guess:
- below 1.4 -> `O(log n)`
- between 1.4 and 3 -> `O(n)`
- above 3 -> `O(n^2)`

Use `time.perf_counter` and keep the best of several repeats.""",
            independent=True,
            starter_code="""import time


def estimate_order(function, sizes, repeats=3):
    pass
""",
            public_tests={"test_public.py": """from main import estimate_order

def work(n):
    return sum(range(n))

def test_linear_is_detected():
    report = estimate_order(work, [1000, 2000, 4000])
    assert report["guess"] == "O(n)"
"""},
            hidden_tests={
                "test_hidden.py": """from main import estimate_order

def linear(n):
    return sum(range(n))

def quadratic(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return total

def constant(n):
    return 42

def test_shapes():
    report = estimate_order(linear, [500, 1000, 2000])
    assert report["sizes"] == [500, 1000, 2000]
    assert len(report["times"]) == 3
    assert len(report["ratios"]) == 2

def test_constant_guess():
    assert estimate_order(constant, [10, 100, 1000])["guess"] in {"O(1)", "O(log n)"}

def test_quadratic_guess():
    assert estimate_order(quadratic, [50, 100, 200])["guess"] == "O(n^2)"

def test_linear_guess():
    assert estimate_order(linear, [5000, 10000, 20000])["guess"] in {"O(n)", "O(log n)"}

def test_positive_times():
    report = estimate_order(linear, [100, 200])
    assert all(t >= 0 for t in report["times"])

def test_single_size():
    report = estimate_order(linear, [1000])
    assert report["ratios"] == []
"""},
            reference_solution="""import time


def _time(function, size, repeats):
    best = float("inf")
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        function(size)
        best = min(best, time.perf_counter() - start)
    return best * 1000


def estimate_order(function, sizes, repeats=3):
    times = [_time(function, size, repeats) for size in sizes]
    ratios = []
    for previous, current in zip(times, times[1:]):
        if previous <= 0:
            ratios.append(1.0)
        else:
            ratios.append(round(current / previous, 3))
    meaningful = [ratio for ratio in ratios if ratio > 0]
    average = sum(meaningful) / len(meaningful) if meaningful else 1.0
    if average < 1.4:
        guess = "O(log n)"
    elif average <= 3.0:
        guess = "O(n)"
    else:
        guess = "O(n^2)"
    return {"sizes": list(sizes), "times": times, "ratios": ratios, "guess": guess}
""",
        ),
        transfer_ar="استخدم `estimate_order` في Algorithm Gladiators قبل إعادة كتابة أي حل.",
        transfer_en="Use `estimate_order` in Algorithm Gladiators before rewriting any solution.",
        references=(
            ("Python wiki - time complexity", "https://wiki.python.org/moin/TimeComplexity"),
            ("Big-O cheat sheet", "https://www.bigocheatsheet.com/"),
        ),
    ),
    CurriculumModule(
        id="l6.sorting_searching",
        level=6,
        order_index=2,
        domain="algorithms",
        title_ar="الترتيب والبحث",
        title_en="Sorting and searching",
        summary_ar="تنفيذ merge وquick sort والبحث الثنائي، ومعرفة متى تستخدم الجاهز.",
        summary_en="Implementing merge and quick sort plus binary search, and knowing when to use the built-ins.",
        explanation_ar="""**Merge sort** يقسّم النصفين، يرتّب كل نصف، ثم يدمج. زمنه `O(n log n)` في كل الحالات
ويحتاج ذاكرة إضافية `O(n)`. مستقر (يحافظ على ترتيب العناصر المتساوية).

**Quick sort** يختار محوراً (pivot)، يفصل الأصغر والأكبر، ثم يرتّب كل جانب. متوسطه
`O(n log n)` لكن أسوأ حالة `O(n²)` (عند اختيار محور سيئ على بيانات مرتّبة). يعمل في
المكان تقريباً ولا يحتاج ذاكرة إضافية كبيرة.

**البحث الثنائي** على مصفوفة مرتّبة يقصّر نطاق البحث إلى النصف في كل خطوة: `O(log n)`.
يحتاج البيانات **مرتّبة** ويفشل بصمت إن لم تكن.

في الإنتاج: استخدم `sorted()` و`list.sort()` (TimSort: `O(n log n)`، مستقر، سريع جداً
على البيانات المرتّبة جزئياً) و`bisect` للبحث الثنائي. اكتب الخوارزميات هنا لتفهمها،
ثم استخدم الجاهز في عملك.""",
        explanation_en="""**Merge sort** splits, sorts each half, then merges. It is `O(n log n)` in every case and
needs `O(n)` extra memory. It is stable (equal elements keep their order).

**Quick sort** picks a pivot, partitions smaller and larger, then sorts each side. Its average
is `O(n log n)` but the worst case is `O(n^2)` (a bad pivot on sorted data). It works mostly
in place and needs little extra memory.

**Binary search** over a sorted array halves the search range every step: `O(log n)`. It
requires **sorted** data and fails silently when the data is not sorted.

In production: use `sorted()` / `list.sort()` (TimSort: `O(n log n)`, stable, very fast on
partially sorted data) and `bisect` for binary search. Write the algorithms here to
understand them, then use the built-ins at work.""",
        skills=("algo.sorting", "algo.searching", "algo.recursion"),
        prerequisites=("l6.complexity",),
        example_code="""import random


def merge_sort(values):
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search(values, target):
    low, high = 0, len(values) - 1
    steps = 0
    while low <= high:
        steps += 1
        middle = (low + high) // 2
        if values[middle] == target:
            return middle, steps
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1, steps


data = [random.randrange(1000) for _ in range(40)]
ordered = merge_sort(data)
print("sorted correctly:", ordered == sorted(data))
print("first ten:", ordered[:10])

target = ordered[17]
index, steps = binary_search(ordered, target)
print(f"found {target} at index {index} in {steps} steps (a linear scan needs {index + 1})")
print("missing value:", binary_search(ordered, -5)[0])
""",
        example_notes_ar="لاحظ أن عدد خطوات البحث الثنائي يقارب log2(n) فقط.",
        example_notes_en="Notice the binary search needs only about log2(n) steps.",
        experiment_code="""import random
import time


def quick_sort(values):
    if len(values) <= 1:
        return list(values)
    pivot = values[len(values) // 2]
    left = [v for v in values if v < pivot]
    middle = [v for v in values if v == pivot]
    right = [v for v in values if v > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def builtin_sort(values):
    return sorted(values)


def measure(function, size):
    data = [random.randrange(size * 10) for _ in range(size)]
    start = time.perf_counter()
    function(data)
    return (time.perf_counter() - start) * 1000


for size in (500, 2000, 8000):
    quick = measure(quick_sort, size)
    builtin = measure(builtin_sort, size)
    print(f"n={size:>6}  quicksort(naive): {quick:7.2f} ms   sorted(): {builtin:7.2f} ms")

print("")
print("the built-in runs in C, so it wins by a wide margin - this is why we reuse it.")
""",
        experiment_brief_ar="أضف نسخة in-place من quick sort وقارن الذاكرة والزمن مع النسخة أعلاه.",
        experiment_brief_en="Add an in-place version of quick sort and compare memory and time with the one above.",
        task=TaskSpec(
            brief_ar="""اكتب في `main.py`:
1. `merge_sort(values)` تُعيد قائمة جديدة مرتّبة (مستقرة).
2. `quick_sort(values)` تُعيد قائمة جديدة مرتّبة، باختيار المحور من منتصف القائمة،
   وتعمل بشكل صحيح مع القيم المتكررة.
3. `binary_search(values, target)` تُعيد فهرس الهدف أو `-1` (تكرارية، بدون استدعاء ذاتي).
4. `count_less_than(values, threshold)` تستخدم `bisect_left` لإرجاع عدد العناصر الأصغر
   من `threshold` في قائمة مرتّبة.""",
            brief_en="""Write in `main.py`:
1. `merge_sort(values)` returning a new sorted list (stable).
2. `quick_sort(values)` returning a new sorted list, pivoting on the middle element and
   handling duplicate values correctly.
3. `binary_search(values, target)` returning the index or `-1` (iterative, no self-calls).
4. `count_less_than(values, threshold)` using `bisect_left` to count elements below
   `threshold` in a sorted list.""",
            starter_code="""from bisect import bisect_left


def merge_sort(values):
    pass


def quick_sort(values):
    pass


def binary_search(values, target):
    pass


def count_less_than(values, threshold):
    pass
""",
            public_tests={"test_public.py": """from main import merge_sort

def test_merge_sort():
    assert merge_sort([3, 1, 2]) == [1, 2, 3]
"""},
            hidden_tests={"test_hidden.py": """from main import merge_sort, quick_sort, binary_search, count_less_than

DATA = [5, 3, 9, 1, 7, 3, 8]

def test_merge_sort_basic():
    assert merge_sort(DATA) == sorted(DATA)

def test_merge_sort_empty_and_single():
    assert merge_sort([]) == []
    assert merge_sort([4]) == [4]

def test_merge_sort_does_not_mutate():
    values = [2, 1]
    merge_sort(values)
    assert values == [2, 1]

def test_quick_sort_basic():
    assert quick_sort(DATA) == sorted(DATA)

def test_quick_sort_duplicates():
    assert quick_sort([2, 2, 1, 2]) == [1, 2, 2, 2]

def test_quick_sort_already_sorted():
    assert quick_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_binary_search_found():
    assert binary_search([1, 3, 5, 7], 5) == 2

def test_binary_search_missing():
    assert binary_search([1, 3, 5, 7], 4) == -1

def test_binary_search_edges():
    assert binary_search([1, 3, 5], 1) == 0
    assert binary_search([1, 3, 5], 5) == 2
    assert binary_search([], 1) == -1

def test_count_less_than():
    assert count_less_than([1, 2, 3, 4], 3) == 2
    assert count_less_than([1, 2, 3], 1) == 0
    assert count_less_than([1, 2, 3], 10) == 3
"""},
            reference_solution="""from bisect import bisect_left


def merge_sort(values):
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(values):
    if len(values) <= 1:
        return list(values)
    pivot = values[len(values) // 2]
    left = [value for value in values if value < pivot]
    middle = [value for value in values if value == pivot]
    right = [value for value in values if value > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def binary_search(values, target):
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def count_less_than(values, threshold):
    return bisect_left(values, threshold)
""",
            hints=(
                "In merge sort, `<=` on the left side is what keeps the sort stable.",
                "Quick sort must collect a `middle` list of elements equal to the pivot.",
                "`bisect_left` already returns the number of elements strictly below the threshold.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب أدوات ترتيب مخصصة:
1. `sort_by_key(records, key, reverse=False)` تُعيد نسخة مرتّبة دون تعديل الأصل
   (`key` إما اسم حقل أو دالة).
2. `top_n(values, n)` تُعيد أكبر `n` قيم مرتّبة تنازلياً بـ `heapq.nlargest`.
3. `rank(values)` تُعيد قائمة الرتب (1 للأكبر) مع التعامل الصحيح مع القيم المتساوية
   (نفس الرتبة للقيم المتساوية، والرتبة التالية تقفز: 1،2،2،4).""",
            brief_en="""Write custom ordering tools:
1. `sort_by_key(records, key, reverse=False)` returning a sorted copy without mutating the input
   (`key` is either a field name or a callable).
2. `top_n(values, n)` returning the `n` largest values, descending, using `heapq.nlargest`.
3. `rank(values)` returning ranks (1 is the largest) handling ties correctly
   (equal values share a rank and the next rank skips: 1, 2, 2, 4).""",
            independent=True,
            starter_code="""import heapq


def sort_by_key(records, key, reverse=False):
    pass


def top_n(values, n):
    pass


def rank(values):
    pass
""",
            public_tests={"test_public.py": """from main import top_n

def test_top_n():
    assert top_n([5, 1, 9, 3], 2) == [9, 5]
"""},
            hidden_tests={"test_hidden.py": """from main import sort_by_key, top_n, rank

RECORDS = [
    {"name": "b", "score": 10},
    {"name": "a", "score": 30},
    {"name": "c", "score": 20},
]

def test_sort_ascending():
    assert [r["name"] for r in sort_by_key(RECORDS, "score")] == ["b", "c", "a"]

def test_sort_descending():
    assert [r["name"] for r in sort_by_key(RECORDS, "score", reverse=True)] == ["a", "c", "b"]

def test_sort_callable_key():
    assert [r["name"] for r in sort_by_key(RECORDS, lambda r: r["name"])] == ["a", "b", "c"]

def test_sort_does_not_mutate():
    snapshot = [dict(r) for r in RECORDS]
    sort_by_key(RECORDS, "score")
    assert RECORDS == snapshot

def test_top_n_smaller_than_input():
    assert top_n([3, 1, 2], 5) == [3, 2, 1]

def test_top_n_zero():
    assert top_n([3, 1], 0) == []

def test_rank_standard_competition():
    assert rank([100, 100, 50, 25]) == [1, 1, 3, 4]

def test_rank_ascending_values():
    assert rank([1, 2, 3]) == [3, 2, 1]

def test_rank_empty():
    assert rank([]) == []
"""},
            reference_solution="""import heapq


def sort_by_key(records, key, reverse=False):
    getter = key if callable(key) and not isinstance(key, str) else (lambda record: record[key])
    return sorted(records, key=getter, reverse=reverse)


def top_n(values, n):
    if n <= 0:
        return []
    return heapq.nlargest(n, values)


def rank(values):
    order = sorted(range(len(values)), key=lambda index: values[index], reverse=True)
    ranks = [0] * len(values)
    position = 0
    while position < len(order):
        value = values[order[position]]
        end = position
        while end < len(order) and values[order[end]] == value:
            end += 1
        shared = position + 1
        for offset in range(position, end):
            ranks[order[offset]] = shared
        position = end
    return ranks
""",
        ),
        transfer_ar="استخدم هذه الأدوات في Algorithm Gladiators لحل تحديات الترتيب والترتيب النسبي.",
        transfer_en="Use these tools in Algorithm Gladiators for sorting and ranking challenges.",
        references=(
            ("Python docs - bisect", "https://docs.python.org/3/library/bisect.html"),
            ("Python docs - heapq", "https://docs.python.org/3/library/heapq.html"),
        ),
    ),
    CurriculumModule(
        id="l6.stacks_queues_trees",
        level=6,
        order_index=3,
        domain="algorithms",
        title_ar="المكدّسات والطوابير والأشجار",
        title_en="Stacks, queues and trees",
        summary_ar="بنى خطية وهرمية: deque، مكدّس، طابور، وشجرة بحث ثنائية.",
        summary_en="Linear and hierarchical structures: deque, stack, queue and a binary search tree.",
        explanation_ar="""**المكدّس (stack)** آخر من يدخل أول من يخرج: `append` و`pop` من نفس الطرف. استخدمه
للتراجع، تتبّع الاستدعاءات، ومطابقة الأقواس.

**الطابور (queue)** أول من يدخل أول من يخرج: `append` من طرف و`popleft` من الآخر.
`collections.deque` يعطي `O(1)` من الطرفين، بينما `list.pop(0)` هو `O(n)` — لا تفعله.

**الشجرة الثنائية للبحث (BST)**: لكل عقدة مفتاح، كل ما في الشجرة اليسرى أصغر وكل ما في
اليمنى أكبر. العمليات `O(h)` حيث `h` ارتفاع الشجرة: `O(log n)` إذا كانت متوازنة،
و`O(n)` في أسوأ حالة (شجرة متدهورة تشبه القائمة).

أنواع المرور (traversal):
- `in-order` (يسار، عقدة، يمين) على BST يُعيد القيم **مرتّبة**،
- `pre-order` (عقدة، يسار، يمين) مفيد لنسخ الشجرة،
- `post-order` (يسار، يمين، عقدة) مفيد للحذف وتقييم التعابير.

للحفاظ على التوازن في الإنتاج استخدم أشجاراً متزنة (AVL/Red-Black) أو ببساطة
اعتمد على `dict`/`set` إن لم تحتج الترتيب.""",
        explanation_en="""**Stack** - last in, first out: `append` and `pop` on the same end. Use it for undo,
call tracking and bracket matching.

**Queue** - first in, first out: `append` on one end, `popleft` on the other.
`collections.deque` gives `O(1)` at both ends, while `list.pop(0)` is `O(n)` - never do that.

**Binary search tree**: every node has a key; everything in the left subtree is smaller and
everything in the right subtree is larger. Operations are `O(h)` where `h` is the height:
`O(log n)` when balanced, `O(n)` in the worst case (a degenerate tree that is just a list).

Traversals:
- `in-order` (left, node, right) on a BST yields values **in sorted order**,
- `pre-order` (node, left, right) is useful for copying a tree,
- `post-order` (left, right, node) is useful for deletion and evaluating expressions.

For balance in production use a self-balancing tree (AVL/Red-Black), or simply rely on
`dict`/`set` when you do not need ordering.""",
        skills=("ds.stacks_queues", "ds.trees"),
        prerequisites=("l6.sorting_searching",),
        example_code="""from collections import deque

stack = []
for char in "(a + [b * {c}])":
    if char in "([{":
        stack.append(char)
    elif char in ")]}":
        if not stack:
            print("unbalanced closing", char)
            break
        opening = stack.pop()
        if "([{".index(opening) != ")]}".index(char):
            print("mismatched:", opening, char)
            break
print("stack balanced:", not stack)

queue = deque(["task-1", "task-2"])
queue.append("task-3")
print("queue order:", [queue.popleft() for _ in range(len(queue))])


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def insert(node, value):
    if node is None:
        return Node(value)
    if value < node.value:
        node.left = insert(node.left, value)
    else:
        node.right = insert(node.right, value)
    return node


def inorder(node):
    if node is None:
        return []
    return inorder(node.left) + [node.value] + inorder(node.right)


root = None
for value in [8, 3, 10, 1, 6, 14]:
    root = insert(root, value)
print("in-order (sorted):", inorder(root))
""",
        example_notes_ar="`inorder` على BST تُعيد القيم مرتّبة — هذه خاصية الشجرة لا الصدفة.",
        example_notes_en="`inorder` on a BST returns sorted values - that is a property of the tree, not luck.",
        experiment_code="""from collections import deque


def bfs_levels(neighbours, start):
    seen = {start}
    queue = deque([(start, 0)])
    levels = {}
    while queue:
        node, depth = queue.popleft()
        levels.setdefault(depth, []).append(node)
        for neighbour in neighbours(node):
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append((neighbour, depth + 1))
    return levels


GRAPH = {
    "home": ["shop", "school"],
    "shop": ["bank"],
    "school": ["bank", "park"],
    "bank": [],
    "park": [],
}

for depth, nodes in sorted(bfs_levels(lambda node: GRAPH[node], "home").items()):
    print(f"depth {depth}: {nodes}")


def depth_first(graph, start):
    stack = [start]
    seen = set()
    order = []
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for neighbour in reversed(graph[node]):
            stack.append(neighbour)
    return order


print("iterative DFS:", depth_first(GRAPH, "home"))
""",
        experiment_brief_ar="عدّل `bfs_levels` لتُعيد أيضاً أقصر مسار (قائمة العقد) إلى كل عقدة.",
        experiment_brief_en="Change `bfs_levels` to also return the shortest path (node list) to every node.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `is_balanced(text)` تتحقق من تطابق `()[]{}` باستخدام مكدّس (ترتيب صحيح ونوع متطابق).
2. `evaluate_rpn(tokens)` تُقيّم تعبيراً بالصيغة البولندية العكسية مثل
   `["2", "1", "+", "3", "*"]` → `9`، وتدعم `+ - * /`.
3. `class MinQueue` طابور يستخدم `deque` ويدعم `enqueue`, `dequeue`, `peek`, `min`،
   ويعيد `None` عند الفراغ بدل رفع استثناء.""",
            brief_en="""Write:
1. `is_balanced(text)` checking that `()[]{}` match, using a stack (right order and right type).
2. `evaluate_rpn(tokens)` evaluating a Reverse Polish Notation expression such as
   `["2", "1", "+", "3", "*"]` -> `9`, supporting `+ - * /`.
3. `class MinQueue` - a queue backed by `deque` supporting `enqueue`, `dequeue`, `peek` and `min`,
   returning `None` when empty instead of raising.""",
            starter_code="""from collections import deque


def is_balanced(text):
    pass


def evaluate_rpn(tokens):
    pass


class MinQueue:
    def __init__(self):
        pass
""",
            public_tests={"test_public.py": """from main import is_balanced

def test_balanced():
    assert is_balanced("(a + [b])") is True
    assert is_balanced("(a + [b)") is False
"""},
            hidden_tests={"test_hidden.py": """from main import is_balanced, evaluate_rpn, MinQueue

def test_nested_balanced():
    assert is_balanced("{[()]}") is True

def test_unclosed():
    assert is_balanced("(((") is False

def test_extra_closing():
    assert is_balanced(")(") is False

def test_empty_is_balanced():
    assert is_balanced("") is True

def test_ignores_other_characters():
    assert is_balanced("def f(x): return [1,2]") is True

def test_rpn_basic():
    assert evaluate_rpn(["2", "1", "+", "3", "*"]) == 9

def test_rpn_division():
    assert evaluate_rpn(["4", "2", "/"]) == 2

def test_rpn_negative():
    assert evaluate_rpn(["3", "5", "-"]) == -2

def test_queue_order():
    queue = MinQueue()
    for value in (3, 1, 2):
        queue.enqueue(value)
    assert queue.peek() == 3
    assert queue.dequeue() == 3
    assert queue.peek() == 1

def test_queue_min():
    queue = MinQueue()
    for value in (5, 2, 7):
        queue.enqueue(value)
    assert queue.min() == 2
    queue.dequeue()
    assert queue.min() == 2

def test_queue_empty():
    queue = MinQueue()
    assert queue.dequeue() is None
    assert queue.min() is None
    assert queue.peek() is None
"""},
            reference_solution="""from collections import deque

PAIRS = {")": "(", "]": "[", "}": "{"}


def is_balanced(text):
    stack = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in PAIRS:
            if not stack or stack.pop() != PAIRS[char]:
                return False
    return not stack


def evaluate_rpn(tokens):
    stack = []
    for token in tokens:
        if token in {"+", "-", "*", "/"}:
            right = stack.pop()
            left = stack.pop()
            if token == "+":
                stack.append(left + right)
            elif token == "-":
                stack.append(left - right)
            elif token == "*":
                stack.append(left * right)
            else:
                stack.append(int(left / right))
        else:
            stack.append(float(token) if "." in str(token) else int(token))
    return stack.pop() if stack else 0


class MinQueue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, value):
        self.items.append(value)

    def dequeue(self):
        return self.items.popleft() if self.items else None

    def peek(self):
        return self.items[0] if self.items else None

    def min(self):
        return min(self.items) if self.items else None

    def __len__(self):
        return len(self.items)
""",
            hints=(
                "Push opening brackets and, on a closing one, pop and compare with the expected match.",
                "In RPN the operator pops the right operand first, then the left.",
                "Guard every `deque` access with an emptiness check to keep `dequeue`/`peek`/`min` safe.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""نفّذ شجرة بحث ثنائية كاملة في صنف `BST`:
- `insert(value)` و`contains(value)`،
- `values()` تُعيد القيم مرتّبة (in-order)،
- `height()` ارتفاع الشجرة (شجرة فارغة = 0، ورقة = 1)،
- `size()` عدد العقد،
- `delete(value)` تحذف القيمة وتُعيد `True` إن وُجدت،
- `min_value()` / `max_value()` (تُعيد `None` للشجرة الفارغة).""",
            brief_en="""Implement a complete binary search tree as a `BST` class:
- `insert(value)` and `contains(value)`,
- `values()` returning the values in sorted order (in-order),
- `height()` - the tree height (empty tree = 0, a leaf = 1),
- `size()` - the number of nodes,
- `delete(value)` removing the value and returning `True` when it existed,
- `min_value()` / `max_value()` (returning `None` for an empty tree).""",
            independent=True,
            starter_code="""class BST:
    def __init__(self):
        pass
""",
            public_tests={"test_public.py": """from main import BST

def test_insert_and_values():
    tree = BST()
    for value in (5, 3, 8):
        tree.insert(value)
    assert tree.values() == [3, 5, 8]
"""},
            hidden_tests={"test_hidden.py": """from main import BST

def build(values=(8, 3, 10, 1, 6, 14, 4)):
    tree = BST()
    for value in values:
        tree.insert(value)
    return tree

def test_contains():
    tree = build()
    assert tree.contains(6) is True
    assert tree.contains(99) is False

def test_size():
    assert build().size() == 7

def test_duplicates_are_ignored():
    tree = BST()
    tree.insert(1)
    tree.insert(1)
    assert tree.size() == 1

def test_height_of_leaf_tree():
    tree = BST()
    tree.insert(1)
    assert tree.height() == 1

def test_height_balanced():
    # 8 -> 3 -> 6 -> 4 is the deepest chain
    assert build().height() == 4

def test_empty_tree():
    tree = BST()
    assert tree.height() == 0
    assert tree.size() == 0
    assert tree.values() == []
    assert tree.min_value() is None
    assert tree.max_value() is None

def test_min_max():
    tree = build()
    assert (tree.min_value(), tree.max_value()) == (1, 14)

def test_delete_leaf():
    tree = build()
    assert tree.delete(1) is True
    assert tree.contains(1) is False
    assert tree.values() == [3, 4, 6, 8, 10, 14]

def test_delete_node_with_one_child():
    tree = BST()
    for value in (5, 3, 1):
        tree.insert(value)
    tree.delete(3)
    assert tree.values() == [1, 5]

def test_delete_node_with_two_children():
    tree = build()
    tree.delete(3)
    assert tree.values() == [1, 4, 6, 8, 10, 14]

def test_delete_missing():
    assert build().delete(42) is False
"""},
            reference_solution="""class _Node:
    __slots__ = ("value", "left", "right")

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        self.root = self._insert(self.root, value)

    def _insert(self, node, value):
        if node is None:
            return _Node(value)
        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        return node

    def contains(self, value):
        node = self.root
        while node is not None:
            if value == node.value:
                return True
            node = node.left if value < node.value else node.right
        return False

    def values(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.value)
        self._inorder(node.right, result)

    def height(self):
        return self._height(self.root)

    def _height(self, node):
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))

    def size(self):
        return self._size(self.root)

    def _size(self, node):
        return 0 if node is None else 1 + self._size(node.left) + self._size(node.right)

    def min_value(self):
        if self.root is None:
            return None
        node = self.root
        while node.left is not None:
            node = node.left
        return node.value

    def max_value(self):
        if self.root is None:
            return None
        node = self.root
        while node.right is not None:
            node = node.right
        return node.value

    def delete(self, value):
        found = self.contains(value)
        if found:
            self.root = self._delete(self.root, value)
        return found

    def _delete(self, node, value):
        if node is None:
            return None
        if value < node.value:
            node.left = self._delete(node.left, value)
        elif value > node.value:
            node.right = self._delete(node.right, value)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.value = successor.value
            node.right = self._delete(node.right, successor.value)
        return node
""",
        ),
        transfer_ar="استخدم الشجرة في Algorithm Gladiators لبناء فهرس ترتيب سريع.",
        transfer_en="Use the tree in Algorithm Gladiators to build a fast ordered index.",
        references=(
            ("Python docs - collections.deque", "https://docs.python.org/3/library/collections.html#deque-objects"),
            ("Binary search tree on Wikipedia", "https://en.wikipedia.org/wiki/Binary_search_tree"),
        ),
    ),
    CurriculumModule(
        id="l6.graphs",
        level=6,
        order_index=4,
        domain="algorithms",
        title_ar="الرسم البياني",
        title_en="Graphs",
        summary_ar="BFS وDFS وأقصر مسار وترتيب طوبولوجي على بيانات حقيقية.",
        summary_en="BFS, DFS, shortest paths and topological ordering on real data.",
        explanation_ar="""الرسم البياني مجموعة عقد وحواف. تمثيلان شائعان:
- **قائمة التجاور** (`dict[node] -> list[node]`) — الأفضل للرسوم المتفرقة (الغالبية)،
- **مصفوفة التجاور** — الأفضل للرسوم الكثيفة والاستعلام السريع عن وجود حافة.

خوارزميتان أساسيتان:
- **BFS** يستكشف طبقة طبقة بطابور → أقصر مسار بالعقد في رسم غير موزون،
- **DFS** يغوص عميقاً بمكدّس أو استدعاء ذاتي → كشف الحلقات والترتيب الطوبولوجي.

امتدادات:
- **Dijkstra** لأقصر مسار بأوزان موجبة (استخدم `heapq`)،
- **Kahn** للترتيب الطوبولوجي بحساب درجات الدخول،
- **Union-Find** للمكوّنات المتصلة بكفاءة.

احذر الحلقات اللانهائية: احتفظ بمجموعة `seen` دائماً.""",
        explanation_en="""A graph is a set of nodes and edges. Two common representations:
- **adjacency list** (`dict[node] -> list[node]`) - best for sparse graphs (the common case),
- **adjacency matrix** - best for dense graphs and fast edge-existence queries.

Two core algorithms:
- **BFS** explores level by level with a queue -> shortest path in hops on an unweighted graph,
- **DFS** dives deep with a stack or recursion -> cycle detection and topological ordering.

Extensions:
- **Dijkstra** for shortest paths with positive weights (use `heapq`),
- **Kahn** for topological ordering by counting in-degrees,
- **Union-Find** for connected components.

Beware infinite loops: always keep a `seen` set.""",
        skills=("ds.graphs", "algo.bfs", "algo.shortest_paths"),
        prerequisites=("l6.stacks_queues_trees",),
        example_code="""from collections import deque


def build_adjacency(edges, directed=False):
    graph = {}
    for source, target in edges:
        graph.setdefault(source, [])
        graph.setdefault(target, [])
        graph[source].append(target)
        if not directed:
            graph[target].append(source)
    return graph


def bfs(graph, start):
    order = []
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return order


def shortest_path(graph, start, goal):
    queue = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        for neighbour in graph.get(node, []):
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(path + [neighbour])
    return None


EDGES = [("home", "shop"), ("home", "school"), ("shop", "bank"), ("school", "bank"), ("bank", "park")]
graph = build_adjacency(EDGES)
print("bfs from home :", bfs(graph, "home"))
print("home -> park  :", shortest_path(graph, "home", "park"))
print("home -> island:", shortest_path(graph, "home", "island"))
""",
        example_notes_ar="`shortest_path` يخزّن المسار كاملاً في الطابور: بسيط لكنه يستهلك ذاكرة مع الرسوم الكبيرة.",
        example_notes_en="`shortest_path` stores the whole path in the queue: simple, but memory-hungry on big graphs.",
        experiment_code="""import heapq


def dijkstra(graph, start):
    distances = {start: 0}
    queue = [(0, start)]
    settled = set()
    while queue:
        distance, node = heapq.heappop(queue)
        if node in settled:
            continue
        settled.add(node)
        for neighbour, weight in graph.get(node, {}).items():
            candidate = distance + weight
            if candidate < distances.get(neighbour, float("inf")):
                distances[neighbour] = candidate
                heapq.heappush(queue, (candidate, neighbour))
    return distances


WEIGHTED = {
    "home": {"shop": 4, "school": 2},
    "shop": {"bank": 5},
    "school": {"bank": 8, "park": 11},
    "bank": {"park": 3},
    "park": {},
}

print("distances from home:", dijkstra(WEIGHTED, "home"))


def has_cycle(graph):
    state = {}

    def visit(node):
        state[node] = "visiting"
        for neighbour in graph.get(node, []):
            if state.get(neighbour) == "visiting":
                return True
            if state.get(neighbour) is None and visit(neighbour):
                return True
        state[node] = "done"
        return False

    return any(visit(node) for node in graph if state.get(node) is None)


print("cycle in a DAG? ", has_cycle({"a": ["b"], "b": ["c"], "c": []}))
print("cycle with a loop?", has_cycle({"a": ["b"], "b": ["c"], "c": ["a"]}))
""",
        experiment_brief_ar="أعد كتابة `has_cycle` بشكل تكراري (بدون استدعاء ذاتي) لتجنّب حد التكرار.",
        experiment_brief_en="Rewrite `has_cycle` iteratively (no recursion) to avoid the recursion limit.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `build_graph(edges, directed=False)` تُعيد قاموس تجاور (كل العقد موجودة كمفاتيح).
2. `bfs_distances(graph, start)` تُعيد قاموساً `{node: distance}` في رسم غير موزون
   (العقدة غير المتصلة لا تظهر في القاموس).
3. `connected_components(graph)` تُعيد قائمة مكوّنات متصلة (قوائم عقد) لرسم غير موجه.
4. `has_path(graph, start, goal)` منطقية تستخدم BFS.""",
            brief_en="""Write:
1. `build_graph(edges, directed=False)` returning an adjacency dict (every node present as a key).
2. `bfs_distances(graph, start)` returning `{node: distance}` on an unweighted graph
   (unreachable nodes are simply absent).
3. `connected_components(graph)` returning a list of connected components (node lists) for
   an undirected graph.
4. `has_path(graph, start, goal)` - a boolean using BFS.""",
            starter_code="""from collections import deque


def build_graph(edges, directed=False):
    pass


def bfs_distances(graph, start):
    pass


def connected_components(graph):
    pass


def has_path(graph, start, goal):
    pass
""",
            public_tests={"test_public.py": """from main import build_graph, has_path

def test_has_path():
    graph = build_graph([("a", "b"), ("b", "c")])
    assert has_path(graph, "a", "c") is True
    assert has_path(graph, "c", "a") is True
"""},
            hidden_tests={"test_hidden.py": """from main import build_graph, bfs_distances, connected_components, has_path

EDGES = [("a", "b"), ("b", "c"), ("d", "e")]

def test_undirected_keys():
    graph = build_graph(EDGES)
    assert set(graph) == {"a", "b", "c", "d", "e"}
    assert "a" in graph["b"]

def test_directed_keys():
    graph = build_graph([("a", "b")], directed=True)
    assert graph == {"a": ["b"], "b": []}

def test_distances():
    graph = build_graph(EDGES)
    distances = bfs_distances(graph, "a")
    assert distances["a"] == 0
    assert distances["c"] == 2
    assert "d" not in distances

def test_components():
    graph = build_graph(EDGES)
    parts = sorted(sorted(part) for part in connected_components(graph))
    assert parts == [["a", "b", "c"], ["d", "e"]]

def test_components_of_empty():
    assert connected_components({}) == []

def test_no_path_between_components():
    graph = build_graph(EDGES)
    assert has_path(graph, "a", "e") is False

def test_path_to_self():
    graph = build_graph(EDGES)
    assert has_path(graph, "a", "a") is True

def test_missing_node():
    graph = build_graph(EDGES)
    assert has_path(graph, "a", "zzz") is False
    assert bfs_distances(graph, "zzz") == {"zzz": 0}
"""},
            reference_solution="""from collections import deque


def build_graph(edges, directed=False):
    graph = {}
    for source, target in edges:
        graph.setdefault(source, [])
        graph.setdefault(target, [])
        graph[source].append(target)
        if not directed:
            graph[target].append(source)
    return graph


def bfs_distances(graph, start):
    if start not in graph:
        return {start: 0}
    distances = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph.get(node, []):
            if neighbour not in distances:
                distances[neighbour] = distances[node] + 1
                queue.append(neighbour)
    return distances


def connected_components(graph):
    seen = set()
    components = []
    for node in graph:
        if node in seen:
            continue
        group = []
        queue = deque([node])
        seen.add(node)
        while queue:
            current = queue.popleft()
            group.append(current)
            for neighbour in graph.get(current, []):
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        components.append(group)
    return components


def has_path(graph, start, goal):
    if start == goal:
        return start in graph
    if start not in graph:
        return False
    return goal in bfs_distances(graph, start)
""",
            hints=(
                "`setdefault` both endpoints so every node exists as a key, even with no edges.",
                "BFS gives hop distances for free: distance[neighbour] = distance[node] + 1.",
                "For components, iterate over all nodes and skip the ones already visited.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب:
1. `dijkstra(graph, start)` لأقصر مسار في رسم موزون موجب، تُعيد `{node: distance}`.
   شكل الرسم: `{node: {neighbour: weight}}`.
2. `shortest_path(graph, start, goal)` تُعيد **المسار** كقائمة عقد (أو `None`)،
   عبر تتبّع `previous` من Dijkstra.
3. `topological_order(graph)` تُعيد ترتيباً طوبولوجياً (خوارزمية Kahn) أو `None` إن وجدت حلقة.""",
            brief_en="""Write:
1. `dijkstra(graph, start)` for shortest paths in a positively weighted graph, returning
   `{node: distance}`. Graph shape: `{node: {neighbour: weight}}`.
2. `shortest_path(graph, start, goal)` returning the **path** as a node list (or `None`), by
   tracking `previous` from Dijkstra.
3. `topological_order(graph)` returning a topological order (Kahn's algorithm) or `None` if a
   cycle exists.""",
            independent=True,
            starter_code="""import heapq


def dijkstra(graph, start):
    pass


def shortest_path(graph, start, goal):
    pass


def topological_order(graph):
    pass
""",
            public_tests={"test_public.py": """from main import dijkstra

def test_dijkstra():
    graph = {"a": {"b": 1}, "b": {"c": 2}, "c": {}}
    assert dijkstra(graph, "a") == {"a": 0, "b": 1, "c": 3}
"""},
            hidden_tests={"test_hidden.py": """from main import dijkstra, shortest_path, topological_order

GRAPH = {
    "home": {"shop": 4, "school": 2},
    "shop": {"bank": 5},
    "school": {"bank": 8, "park": 11},
    "bank": {"park": 3},
    "park": {},
}

def test_distances():
    distances = dijkstra(GRAPH, "home")
    assert distances["park"] == 12     # home -> shop -> bank -> park (4 + 5 + 3)
    assert distances["bank"] == 9      # home -> shop -> bank (4 + 5)

def test_unreachable_absent():
    graph = {"a": {"b": 1}, "b": {}, "island": {}}
    assert "island" not in dijkstra(graph, "a")

def test_path_list():
    assert shortest_path(GRAPH, "home", "park") == ["home", "shop", "bank", "park"]

def test_path_to_self():
    assert shortest_path(GRAPH, "home", "home") == ["home"]

def test_path_missing():
    assert shortest_path(GRAPH, "home", "nowhere") is None

def test_topological_order():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    order = topological_order(graph)
    assert order.index("a") < order.index("d")
    assert order.index("b") < order.index("d")

def test_topological_cycle():
    assert topological_order({"a": ["b"], "b": ["a"]}) is None

def test_topological_empty():
    assert topological_order({}) == []
"""},
            reference_solution="""import heapq
from collections import deque


def dijkstra(graph, start):
    distances = {start: 0}
    queue = [(0, start)]
    settled = set()
    while queue:
        distance, node = heapq.heappop(queue)
        if node in settled:
            continue
        settled.add(node)
        for neighbour, weight in graph.get(node, {}).items():
            candidate = distance + weight
            if candidate < distances.get(neighbour, float("inf")):
                distances[neighbour] = candidate
                heapq.heappush(queue, (candidate, neighbour))
    return distances


def shortest_path(graph, start, goal):
    if start not in graph:
        return None
    previous = {start: None}
    best = {start: 0}
    queue = [(0, start)]
    settled = set()
    while queue:
        distance, node = heapq.heappop(queue)
        if node in settled:
            continue
        settled.add(node)
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = previous[node]
            return path[::-1]
        for neighbour, weight in graph.get(node, {}).items():
            candidate = distance + weight
            if candidate < best.get(neighbour, float("inf")):
                best[neighbour] = candidate
                previous[neighbour] = node
                heapq.heappush(queue, (candidate, neighbour))
    return None


def topological_order(graph):
    nodes = set(graph)
    indegree = {node: 0 for node in nodes}
    for node, neighbours in graph.items():
        for neighbour in neighbours:
            nodes.add(neighbour)
            indegree[neighbour] = indegree.get(neighbour, 0) + 1
    indegree.update({node: indegree.get(node, 0) for node in nodes})
    queue = deque(sorted(node for node in indegree if indegree[node] == 0))
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph.get(node, []):
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)
    return order if len(order) == len(indegree) else None
""",
        ),
        transfer_ar="استخدم Dijkstra في RoboVerse لتخطيط مسار الروبوت.",
        transfer_en="Use Dijkstra in RoboVerse to plan the robot's path.",
        references=(
            ("Python docs - heapq", "https://docs.python.org/3/library/heapq.html"),
            ("Dijkstra's algorithm on Wikipedia", "https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm"),
        ),
    ),
    CurriculumModule(
        id="l6.dynamic_programming",
        level=6,
        order_index=5,
        domain="algorithms",
        title_ar="البرمجة الديناميكية",
        title_en="Dynamic programming",
        summary_ar="تكرار + حفظ نتائج: من العلاقة التكرارية إلى الحل الفعّال.",
        summary_en="Recursion plus memoisation: from the recurrence to the efficient solution.",
        explanation_ar="""البرمجة الديناميكية تنطبق عندما يتوفر شرطان:
1. **بنية جزئية مثالية**: حل المسألة يُبنى من حلول مسائل أصغر،
2. **مسائل فرعية متكررة**: نفس المسألة الفرعية تُحسب مرات عديدة.

طريقتان:
- **من الأعلى للأسفل (memoization)**: اكتب التكرار الطبيعي ثم احفظ النتائج
  (`functools.lru_cache` أو قاموس يدوي).
- **من الأسفل للأعلى (tabulation)**: املأ جدولاً من الحالات الصغيرة إلى الكبيرة.

خطوات الحل:
1. عرّف الحالة بدقة (ما المتغيّرات؟)،
2. اكتب العلاقة التكرارية،
3. حدد الحالات الأساسية،
4. قرر ترتيب الحساب (أو الحفظ)،
5. أعد بناء الحل إن احتجت القرارات لا القيمة فقط.

أمثلة كلاسيكية: فيبوناتشي، تغيير العملات، أطول تتابع مشترك، حقيبة الظهر،
ومسافة التعديل (edit distance).

انتبه: التكرار العميق في بايثون يصطدم بحد 1000 استدعاء — استخدم الجدول أو
`sys.setrecursionlimit` بحذر.""",
        explanation_en="""Dynamic programming applies when two conditions hold:
1. **optimal substructure**: the solution is built from solutions of smaller problems,
2. **overlapping subproblems**: the same subproblem is recomputed many times.

Two styles:
- **top-down (memoisation)**: write the natural recursion, then cache the results
  (`functools.lru_cache` or a manual dict).
- **bottom-up (tabulation)**: fill a table from small states to large ones.

Solution steps:
1. define the state precisely (what varies?),
2. write the recurrence,
3. fix the base cases,
4. choose the evaluation order (or the cache),
5. reconstruct the solution if you need the decisions, not just the value.

Classic examples: Fibonacci, coin change, longest common subsequence, knapsack and edit
distance.

Careful: deep recursion hits Python's 1000-call limit - use a table or raise
`sys.setrecursionlimit` with care.""",
        skills=("algo.dp", "algo.recursion"),
        prerequisites=("l6.graphs",),
        example_code="""import time
from functools import lru_cache


def fib_naive(n):
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)
def fib_memo(n):
    if n < 2:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


def fib_table(n):
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


start = time.perf_counter()
fib_naive(30)
naive_time = time.perf_counter() - start

start = time.perf_counter()
fib_memo(30)
memo_time = time.perf_counter() - start

print(f"naive fib(30): {naive_time * 1000:8.2f} ms")
print(f"memo  fib(30): {memo_time * 1000:8.4f} ms")
print("table fib(60):", fib_table(60))
print("cache hits   :", fib_memo.cache_info().hits)
""",
        example_notes_ar="`lru_cache` يحفظ المفتاح والقيمة: تحتاج وسائط قابلة للتهيئة (hashable).",
        example_notes_en="`lru_cache` keys on the arguments, so they must be hashable.",
        experiment_code="""def coin_change(coins, amount):
    \"\"\"Return the fewest coins needed, or -1 when impossible.\"\"\"
    best = [0] + [float("inf")] * amount
    for coin in coins:
        for value in range(coin, amount + 1):
            if best[value - coin] + 1 < best[value]:
                best[value] = best[value - coin] + 1
    return -1 if best[amount] == float("inf") else best[amount]


def count_ways(coins, amount):
    ways = [1] + [0] * amount
    for coin in coins:
        for value in range(coin, amount + 1):
            ways[value] += ways[value - coin]
    return ways[amount]


print("min coins for 11 with [1, 5, 10]:", coin_change([1, 5, 10], 11))
print("ways to make 10 with [1, 5, 10] :", count_ways([1, 5, 10], 10))
print("impossible amount 3 with [2, 4] :", coin_change([2, 4], 3))

for amount in range(0, 21, 5):
    print(f"  {amount:>2} -> min {coin_change([1, 3, 4], amount)}")
""",
        experiment_brief_ar="غيّر ترتيب الحلقتين في `count_ways` وشاهد كيف تتغيّر النتيجة — وفسّر السبب.",
        experiment_brief_en="Swap the two loops in `count_ways` and watch the result change - then explain why.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `fib(n)` بنهج الجدول (tabulation) تُعيد فيبوناتشي رقم `n` (fib(0)=0, fib(1)=1).
2. `min_coins(coins, amount)` أقل عدد عملات للمبلغ، أو `-1`.
3. `lcs_length(first, second)` طول أطول تتابع مشترك (subsequence).
4. `climb_stairs(n)` عدد طرق صعود سلّم من `n` درجة بخطوة أو خطوتين.""",
            brief_en="""Write:
1. `fib(n)` with the tabulation approach returning Fibonacci number `n` (fib(0)=0, fib(1)=1).
2. `min_coins(coins, amount)` - the fewest coins for the amount, or `-1`.
3. `lcs_length(first, second)` - the length of the longest common subsequence.
4. `climb_stairs(n)` - the number of ways to climb `n` steps using 1 or 2 at a time.""",
            starter_code="""def fib(n):
    pass


def min_coins(coins, amount):
    pass


def lcs_length(first, second):
    pass


def climb_stairs(n):
    pass
""",
            public_tests={"test_public.py": """from main import fib

def test_fib():
    assert fib(0) == 0
    assert fib(10) == 55
"""},
            hidden_tests={"test_hidden.py": """from main import fib, min_coins, lcs_length, climb_stairs

def test_fib_series():
    assert [fib(n) for n in range(8)] == [0, 1, 1, 2, 3, 5, 8, 13]

def test_fib_large():
    assert fib(50) == 12586269025

def test_min_coins_basic():
    assert min_coins([1, 5, 10], 11) == 2

def test_min_coins_impossible():
    assert min_coins([2, 4], 3) == -1

def test_min_coins_zero():
    assert min_coins([1, 2], 0) == 0

def test_min_coins_greedy_trap():
    assert min_coins([1, 3, 4], 6) == 2    # 3 + 3; a greedy take would be 4 + 1 + 1

def test_lcs():
    assert lcs_length("abcde", "ace") == 3
    assert lcs_length("abc", "def") == 0
    assert lcs_length("", "abc") == 0
    assert lcs_length("AGGTAB", "GXTXAYB") == 4

def test_climb_stairs():
    assert climb_stairs(1) == 1
    assert climb_stairs(2) == 2
    assert climb_stairs(4) == 5
    assert climb_stairs(0) == 1
"""},
            reference_solution="""def fib(n):
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


def min_coins(coins, amount):
    best = [0] + [float("inf")] * amount
    for coin in coins:
        for value in range(coin, amount + 1):
            candidate = best[value - coin] + 1
            if candidate < best[value]:
                best[value] = candidate
    return -1 if best[amount] == float("inf") else best[amount]


def lcs_length(first, second):
    table = [[0] * (len(second) + 1) for _ in range(len(first) + 1)]
    for i in range(1, len(first) + 1):
        for j in range(1, len(second) + 1):
            if first[i - 1] == second[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table[len(first)][len(second)]


def climb_stairs(n):
    if n <= 1:
        return 1
    previous, current = 1, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current
""",
            hints=(
                "Rolling two variables keeps Fibonacci at O(1) memory.",
                "Initialise the coin table with infinity and `best[0] = 0`.",
                "For LCS, a 2-D table of size (n+1) x (m+1) removes the need for -1 guards.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب:
1. `edit_distance(first, second)` مسافة التعديل (إدخال/حذف/استبدال) بين نصين.
2. `knapsack(items, capacity)` حيث `items` قائمة `(weight, value)`، تُعيد أعلى قيمة ممكنة
   (حقيبة 0/1: كل عنصر مرة واحدة).
3. `best_time_with_cooldown(prices)` أفضل ربح من البيع والشراء مع يوم راحة إلزامي بين
   كل بيع والشراء التالي (حالة ديناميكية بثلاث حالات).""",
            brief_en="""Write:
1. `edit_distance(first, second)` - the edit distance (insert/delete/substitute) between two strings.
2. `knapsack(items, capacity)` where `items` is a list of `(weight, value)` pairs, returning the
   best achievable value (0/1 knapsack: each item at most once).
3. `best_time_with_cooldown(prices)` - the best profit from buying and selling with a mandatory
   one-day cooldown between a sell and the next buy (a three-state DP).""",
            independent=True,
            starter_code="""def edit_distance(first, second):
    pass


def knapsack(items, capacity):
    pass


def best_time_with_cooldown(prices):
    pass
""",
            public_tests={"test_public.py": """from main import edit_distance

def test_edit_distance():
    assert edit_distance("kitten", "sitting") == 3
"""},
            hidden_tests={"test_hidden.py": """from main import edit_distance, knapsack, best_time_with_cooldown

def test_edit_distance_identical():
    assert edit_distance("same", "same") == 0

def test_edit_distance_empty():
    assert edit_distance("", "abc") == 3
    assert edit_distance("abc", "") == 3

def test_edit_distance_substitution_only():
    assert edit_distance("flaw", "lawn") == 2

def test_knapsack_basic():
    assert knapsack([(2, 3), (3, 4), (4, 5), (5, 6)], 5) == 7

def test_knapsack_zero_capacity():
    assert knapsack([(1, 10)], 0) == 0

def test_knapsack_empty_items():
    assert knapsack([], 10) == 0

def test_knapsack_single_item_fits():
    assert knapsack([(3, 5)], 3) == 5

def test_cooldown_basic():
    assert best_time_with_cooldown([1, 2, 3, 0, 2]) == 3

def test_cooldown_flat():
    assert best_time_with_cooldown([5, 5, 5]) == 0

def test_cooldown_empty():
    assert best_time_with_cooldown([]) == 0

def test_cooldown_two_days():
    assert best_time_with_cooldown([1, 5]) == 4
"""},
            reference_solution="""def edit_distance(first, second):
    rows, columns = len(first) + 1, len(second) + 1
    previous = list(range(columns))
    for i in range(1, rows):
        current = [i] + [0] * (columns - 1)
        for j in range(1, columns):
            cost = 0 if first[i - 1] == second[j - 1] else 1
            current[j] = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
        previous = current
    return previous[-1]


def knapsack(items, capacity):
    best = [0] * (capacity + 1)
    for weight, value in items:
        for remaining in range(capacity, weight - 1, -1):
            candidate = best[remaining - weight] + value
            if candidate > best[remaining]:
                best[remaining] = candidate
    return best[capacity]


def best_time_with_cooldown(prices):
    if len(prices) < 2:
        return 0
    hold = -prices[0]
    sold = 0
    rest = 0
    for price in prices[1:]:
        previous_sold = sold
        sold = hold + price
        hold = max(hold, rest - price)
        rest = max(rest, previous_sold)
    return max(sold, rest)
""",
        ),
        transfer_ar="استخدم مسافة التعديل في Research Reactor لمقارنة صياغات النتائج.",
        transfer_en="Use edit distance in Research Reactor to compare result formulations.",
        references=(
            ("Dynamic programming on Wikipedia", "https://en.wikipedia.org/wiki/Dynamic_programming"),
            ("Python docs - lru_cache", "https://docs.python.org/3/library/functools.html#functools.lru_cache"),
        ),
    ),
]
