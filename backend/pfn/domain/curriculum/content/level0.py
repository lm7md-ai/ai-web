"""LEVEL 0 - Recovery and diagnosis.

These modules are *investigation* scenarios, not lectures: the learner reads
broken behaviour, forms a hypothesis, runs real code and repairs it.  They are
also used by the Knowledge Recovery engine as diagnostic probes.
"""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l0.investigate_mutation",
        level=0,
        order_index=1,
        domain="python_core",
        title_ar="التحقيق في تعديل غير متوقع",
        title_en="Investigating an unexpected mutation",
        summary_ar="لماذا تغيّرت القائمة الثانية عندما عدّلنا الأولى؟",
        summary_en="Why did the second list change when we edited the first one?",
        explanation_ar="""في بايثون، المتغيرات أسماء تشير إلى كائنات، وليست صناديق تحتوي قيماً.

عند كتابة `b = a` فأنت لا تنسخ القائمة، بل تُنشئ اسماً جديداً يشير إلى **نفس** الكائن.
لذلك أي تعديل عبر `a` يظهر فوراً عبر `b`، لأن الاثنين ينظران إلى شيء واحد.

للنسخ الحقيقي استخدم `list(a)` أو `a.copy()` أو `a[:]` (نسخة سطحية)،
أو `copy.deepcopy(a)` إذا كانت القائمة تحتوي كائنات قابلة للتغيير بداخلها.

لاحظ الفرق بين:
- `a.append(x)`: تعديل الكائن نفسه (يظهر في `b`).
- `a = a + [x]`: إنشاء كائن جديد وإعادة ربط الاسم (لا يظهر في `b`).

يمكنك التحقق من الهوية بـ `a is b`، ومن المساواة بـ `a == b`.""",
        explanation_en="""In Python, variables are *names bound to objects*, not boxes holding values.

Writing `b = a` does not copy the list: it creates a second name pointing at the
**same** object. Any mutation performed through `a` is therefore visible through
`b`, because both names look at one thing.

To copy for real, use `list(a)`, `a.copy()` or `a[:]` (a shallow copy), or
`copy.deepcopy(a)` when the list contains other mutable objects.

Note the difference between:
- `a.append(x)` - mutates the object in place (visible through `b`);
- `a = a + [x]` - builds a new object and rebinds the name (not visible through `b`).

Check identity with `a is b` and equality with `a == b`.""",
        skills=("core.mutability", "core.aliasing", "recovery.lists"),
        prerequisites=("recovery.syntax",),
        example_code="""a = [1, 2, 3]
b = a              # same object, two names
c = list(a)        # a real (shallow) copy

a.append(4)

print("a     :", a)
print("b     :", b)
print("c     :", c)
print("b is a:", b is a)
print("c is a:", c is a)
print("c == a:", c == a)

a = a + [5]        # rebinding: b keeps pointing at the original list
print("after rebinding -> a:", a, "b:", b)
""",
        example_notes_ar="شغّل المثال وقارن `b is a` مع `c is a`. جرّب تبديل `append` بـ `+=` ولاحظ الفرق.",
        example_notes_en="Run it and compare `b is a` with `c is a`. Try replacing `append` with `+=` and watch the difference.",
        experiment_code="""# Experiment: how many distinct objects are involved?
matrix = [[0] * 3] * 3      # a classic trap
matrix[0][0] = 99
print(matrix)

# Fix it, then predict the output before running again.
fixed = [[0] * 3 for _ in range(3)]
fixed[0][0] = 99
print(fixed)
""",
        experiment_brief_ar="فسّر لماذا ظهر 99 في ثلاثة صفوف، ثم أصلح الإنشاء باستخدام تعبير اختصار. تنبأ بالنتيجة قبل التنفيذ.",
        experiment_brief_en="Explain why 99 appeared in three rows, then fix the construction with a comprehension. Predict the output before running it.",
        task=TaskSpec(
            brief_ar="""اكتب الدالة `snapshot(values)` التي تُعيد نسخة مستقلة عن القائمة، ثم الدالة
`add_unique(values, item)` التي تُضيف العنصر فقط إذا لم يكن موجوداً، وتُعيد **قائمة جديدة**
دون تعديل القائمة الأصلية.

المتطلبات:
- `add_unique` لا تُعدّل القائمة المُمرَّرة.
- القائمة المُعادة من `snapshot` لا تتأثر بتعديل الأصلية لاحقاً.""",
            brief_en="""Write `snapshot(values)` returning an independent copy of the list, and
`add_unique(values, item)` which appends the item only if it is absent and returns a
**new** list without mutating the argument.

Requirements:
- `add_unique` must not modify the list passed in.
- The list returned by `snapshot` must not change when the original is mutated later.""",
            starter_code="""def snapshot(values):
    # TODO: return an independent copy of values
    pass


def add_unique(values, item):
    # TODO: return a NEW list with item appended if missing, without mutating values
    pass
""",
            public_tests={
                "test_public.py": """from main import snapshot, add_unique

def test_snapshot_is_independent():
    original = [1, 2, 3]
    copy = snapshot(original)
    original.append(4)
    assert copy == [1, 2, 3]

def test_add_unique_appends():
    assert add_unique([1, 2], 3) == [1, 2, 3]

def test_add_unique_skips_duplicates():
    assert add_unique([1, 2], 2) == [1, 2]
"""},
            hidden_tests={
                "test_hidden.py": """from main import snapshot, add_unique

def test_original_untouched():
    original = [1, 2]
    result = add_unique(original, 5)
    assert original == [1, 2], "the input list must not be mutated"
    assert result == [1, 2, 5]

def test_results_are_new_objects():
    original = [1]
    assert add_unique(original, 2) is not original
    assert snapshot(original) is not original
    assert snapshot(original) == original

def test_works_with_empty_and_strings():
    assert add_unique([], "a") == ["a"]
    assert add_unique(["a"], "a") == ["a"]
    assert snapshot([]) == []
"""},
            reference_solution="""def snapshot(values):
    return list(values)


def add_unique(values, item):
    if item in values:
        return list(values)
    return list(values) + [item]
""",
            hints=(
                "`list(values)` builds a new list with the same elements.",
                "Returning `values` unchanged when the item exists still has to be a copy - the caller may mutate it.",
                "Avoid `values.append(...)` here: the task forbids mutating the argument.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `deep_snapshot(board)` تُعيد نسخة عميقة من مصفوفة ثنائية الأبعاد (قائمة قوائم)،
بحيث لا يؤثر تعديل أي صف في النسخة على الأصل ولا العكس.

هذا تقييم مستقل: أكمله دون مساعدة، ثم راجع تقرير الاختبارات.""",
            brief_en="""Write `deep_snapshot(board)` returning a deep copy of a 2-D list, so that
changing any row of the copy never affects the original (and vice versa).

This is an independent assessment: finish it without help, then review the test report.""",
            independent=True,
            starter_code="""def deep_snapshot(board):
    # TODO: return a deep copy of a list of lists
    pass
""",
            public_tests={
                "test_public.py": """from main import deep_snapshot

def test_copy_equals_original():
    board = [[1, 2], [3, 4]]
    assert deep_snapshot(board) == board
"""},
            hidden_tests={
                "test_hidden.py": """from main import deep_snapshot

def test_rows_are_independent():
    board = [[1, 2], [3, 4]]
    copy = deep_snapshot(board)
    copy[0][0] = 99
    assert board == [[1, 2], [3, 4]], "mutating the copy must not touch the original"

def test_original_mutation_does_not_leak():
    board = [[0], [0]]
    copy = deep_snapshot(board)
    board[0][0] = 7
    assert copy == [[0], [0]]

def test_nested_three_levels():
    data = [[[1]], [[2]]]
    copy = deep_snapshot(data)
    copy[0][0][0] = 42
    assert data == [[[1]], [[2]]]
"""},
            reference_solution="""import copy


def deep_snapshot(board):
    return copy.deepcopy(board)
""",
        ),
        transfer_ar="""انقل المفهوم إلى سياق جديد: ملف JSON يُقرأ ثم يُعدّل بالخطأ.
اكتب `load_config(data)` تُعيد قاموساً مستقلاً عن القاموس المُمرَّر، بحيث لا تتسرّب التعديلات بين النسخ.""",
        transfer_en="""Transfer the idea to a new context: a JSON config that is read and then mutated by accident.
Write `load_config(data)` returning a dictionary independent from the one passed in, so edits never leak between copies.""",
        transfer_task=TaskSpec(
            brief_ar="اكتب `load_config(data)` تُعيد نسخة مستقلة من قاموس قد يحتوي قوائم بداخله.",
            brief_en="Write `load_config(data)` returning an independent copy of a dict that may contain nested lists.",
            starter_code="""def load_config(data):
    # TODO: return an independent copy, including nested lists
    pass
""",
            public_tests={"test_public.py": """from main import load_config

def test_values_preserved():
    assert load_config({"a": [1, 2]}) == {"a": [1, 2]}
"""},
            hidden_tests={"test_hidden.py": """from main import load_config

def test_nested_list_independent():
    data = {"a": [1, 2], "b": 3}
    copy = load_config(data)
    copy["a"].append(9)
    assert data == {"a": [1, 2], "b": 3}

def test_top_level_independent():
    data = {"a": 1}
    copy = load_config(data)
    copy["b"] = 2
    assert data == {"a": 1}
"""},
            reference_solution="""def load_config(data):
    return {key: list(value) if isinstance(value, list) else value for key, value in data.items()}
""",
        ),
        references=(
            ("Python docs - copy module", "https://docs.python.org/3/library/copy.html"),
            ("Ned Batchelder - Names and Values", "https://nedbatchelder.com/text/names1.html"),
        ),
    ),
    CurriculumModule(
        id="l0.repair_function",
        level=0,
        order_index=2,
        domain="python_core",
        title_ar="إصلاح دالة معطوبة",
        title_en="Repairing a broken function",
        summary_ar="الدالة تعمل أحياناً وتفشل أحياناً: اقرأ السلوك، شخّص السبب، وأصلحه.",
        summary_en="A function that works sometimes and fails other times: read the behaviour, diagnose it, fix it.",
        explanation_ar="""أخطاء التشغيل تُقرأ من الأسفل إلى الأعلى: آخر سطر في رسالة الخطأ هو المكان الذي توقف عنده التنفيذ.

أكثر الأسباب شيوعاً في دوال "تعمل أحياناً":
1. **القيمة الافتراضية القابلة للتغيير**: `def f(items=[])` — القائمة تُنشأ مرة واحدة عند تعريف الدالة وتُشارك بين كل الاستدعاءات.
2. **نوع المدخل غير المتوقع**: الدالة تفترض رقماً لكنها تستقبل نصاً.
3. **حالة حدية**: قائمة فارغة، قسمة على صفر، أو فهرس خارج النطاق.

الإصلاح النموذجي للقيمة الافتراضية:
`def f(items=None): items = [] if items is None else list(items)`.

قبل الإصلاح، اكتب اختباراً يُعيد إنتاج الخطأ — هذا ما يمنع عودته.""",
        explanation_en="""Runtime errors are read bottom-up: the last line of the traceback is where
execution actually stopped.

The usual reasons a function "works sometimes":
1. **A mutable default argument**: `def f(items=[])` builds the list once, at
   definition time, and every call shares it.
2. **An unexpected input type**: the function assumes a number but receives a string.
3. **An edge case**: an empty list, a division by zero, or an out-of-range index.

The standard fix for the mutable default is:
`def f(items=None): items = [] if items is None else list(items)`.

Before fixing anything, write a test that reproduces the bug - that is what stops
it from coming back.""",
        skills=("core.functions", "recovery.debugging", "core.exceptions_basic"),
        prerequisites=("recovery.syntax",),
        example_code="""# Broken: the default list is shared by every call.
def broken_log(message, entries=[]):
    entries.append(message)
    return entries

print(broken_log("first"))
print(broken_log("second"))     # <- surprising: two entries

# Fixed: build a fresh list on every call.
def fixed_log(message, entries=None):
    entries = [] if entries is None else list(entries)
    entries.append(message)
    return entries

print(fixed_log("first"))
print(fixed_log("second"))
""",
        example_notes_ar="لاحظ أن `broken_log` تُراكم العناصر بين الاستدعاءات. هذا هو الخطأ الكلاسيكي للقيم الافتراضية القابلة للتغيير.",
        example_notes_en="Notice that `broken_log` accumulates entries across calls - the classic mutable-default bug.",
        experiment_code="""def classify(score, thresholds=[50, 75, 90]):
    labels = ["fail", "pass", "good", "excellent"]
    level = 0
    for threshold in thresholds:
        if score >= threshold:
            level += 1
    return labels[level]

print(classify(30), classify(60), classify(80), classify(95))
try:
    print(classify("eighty"))
except TypeError as exc:
    print("TypeError:", exc)
""",
        experiment_brief_ar="شغّل الدالة على قيم مختلفة including قيمة من نوع خاطئ. أضف تحققاً من النوع يرفع `TypeError` برسالة واضحة.",
        experiment_brief_en="Run the function on several values including the wrong type. Add a type check that raises `TypeError` with a clear message.",
        task=TaskSpec(
            brief_ar="""الدالة التالية تُحسب متوسط درجات الطلاب لكنها معطوبة:

```python
def average(scores, drop_lowest=False):
    values = scores
    if drop_lowest:
        values.sort()
        values = values[1:]
    return sum(values) / len(values)
```

المطلوب:
1. لا تُعدّل القائمة المُمرَّرة (الدالة الحالية تُرتّبها في مكانها!).
2. أرجع `0.0` عندما تكون القائمة فارغة بدل رفع `ZeroDivisionError`.
3. ارفع `TypeError` برسالة واضحة إذا كان `scores` ليس قائمة من الأرقام.""",
            brief_en="""The function below averages student scores but it is broken:

```python
def average(scores, drop_lowest=False):
    values = scores
    if drop_lowest:
        values.sort()
        values = values[1:]
    return sum(values) / len(values)
```

Fix it so that:
1. It never mutates the list passed in (the current version sorts it in place!).
2. It returns `0.0` for an empty list instead of raising `ZeroDivisionError`.
3. It raises `TypeError` with a clear message when `scores` is not a list of numbers.""",
            starter_code="""def average(scores, drop_lowest=False):
    # TODO: fix the three defects described in the brief
    values = scores
    if drop_lowest:
        values.sort()
        values = values[1:]
    return sum(values) / len(values)
""",
            public_tests={
                "test_public.py": """from main import average

def test_simple_average():
    assert average([2, 4, 6]) == 4.0

def test_drop_lowest():
    assert average([1, 5, 5], drop_lowest=True) == 5.0
"""},
            hidden_tests={
                "test_hidden.py": """from main import average
import pytest

def test_input_not_mutated():
    scores = [5, 1, 3]
    average(scores, drop_lowest=True)
    assert scores == [5, 1, 3], "the caller's list must not be reordered"

def test_empty_list():
    assert average([]) == 0.0
    assert average([], drop_lowest=True) == 0.0

def test_bad_type():
    with pytest.raises(TypeError):
        average("not a list")
    with pytest.raises(TypeError):
        average([1, "two", 3])

def test_single_value():
    assert average([7]) == 7.0
    assert average([7], drop_lowest=True) == 0.0
"""},
            reference_solution="""def average(scores, drop_lowest=False):
    if not isinstance(scores, list) or any(
        isinstance(item, bool) or not isinstance(item, (int, float)) for item in scores
    ):
        raise TypeError("scores must be a list of numbers")
    if not scores:
        return 0.0
    values = sorted(scores) if drop_lowest else list(scores)
    if drop_lowest:
        values = values[1:]
        if not values:
            return 0.0
    return sum(values) / len(values)
""",
            hints=(
                "`sorted(scores)` returns a new list; `scores.sort()` mutates in place.",
                "Booleans are ints in Python - decide whether you want to reject them.",
                "Handle the empty case before dividing, not after.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `normalise(values)` تُعيد قائمة جديدة بقيم محوّلة إلى نطاق 0..1 باستخدام
`(v - min) / (max - min)`، مع:
- رفع `ValueError("empty input")` عند قائمة فارغة،
- إرجاع قائمة من الأصفار عندما تكون كل القيم متساوية (لتجنب القسمة على صفر)،
- عدم تعديل المدخل.""",
            brief_en="""Write `normalise(values)` returning a new list scaled to 0..1 using
`(v - min) / (max - min)`, with:
- `ValueError("empty input")` for an empty list,
- a list of zeros when every value is identical (avoid dividing by zero),
- no mutation of the input.""",
            independent=True,
            starter_code="""def normalise(values):
    # TODO: scale to 0..1, handle empty input and the constant case
    pass
""",
            public_tests={"test_public.py": """from main import normalise

def test_basic():
    assert normalise([0, 5, 10]) == [0.0, 0.5, 1.0]
"""},
            hidden_tests={"test_hidden.py": """from main import normalise
import pytest

def test_empty():
    with pytest.raises(ValueError):
        normalise([])

def test_constant_values():
    assert normalise([3, 3, 3]) == [0.0, 0.0, 0.0]

def test_no_mutation():
    values = [1, 2, 3]
    normalise(values)
    assert values == [1, 2, 3]

def test_negative_range():
    result = normalise([-10, 0, 10])
    assert result[0] == 0.0 and abs(result[-1] - 1.0) < 1e-9
"""},
            reference_solution="""def normalise(values):
    if not values:
        raise ValueError("empty input")
    lowest, highest = min(values), max(values)
    span = highest - lowest
    if span == 0:
        return [0.0 for _ in values]
    return [(value - lowest) / span for value in values]
""",
        ),
        transfer_ar="انقل مهارة قراءة الأخطاء: في RoboVerse اصطدم الروبوت بجدار. اقرأ الحدث، حدد النبضة التي حدث فيها الاصطدام، وصحّح المنطق.",
        transfer_en="Transfer the debugging skill: in RoboVerse a robot crashed into a wall. Read the events, find the tick of the crash and correct the logic.",
        references=(
            ("Python docs - default argument values", "https://docs.python.org/3/reference/compound_stmts.html#function-definitions"),
            ("Python docs - errors and exceptions", "https://docs.python.org/3/tutorial/errors.html"),
        ),
    ),
    CurriculumModule(
        id="l0.process_records",
        level=0,
        order_index=3,
        domain="python_core",
        title_ar="معالجة سجلات حقيقية",
        title_en="Processing real records",
        summary_ar="قائمة من القواميس: تجميع، فلترة، وتلخيص بدون مكتبات.",
        summary_en="A list of dictionaries: group, filter and summarise without libraries.",
        explanation_ar="""البيانات الحقيقية غالباً ما تأتي كقائمة من القواميس (سجلات). المهارات الأساسية:

- **الفلترة**: `[r for r in rows if r["status"] == "ok"]`.
- **التجميع**: قاموس يربط المفتاح بقائمة، باستخدام `dict.setdefault(key, []).append(value)`
  أو `collections.defaultdict(list)`.
- **التلخيص**: `sum(...)`, `len(...)`, `max(..., key=...)`.
- **المفاتيح الناقصة**: استخدم `row.get("field", default)` بدل `row["field"]` عندما لا تكون متأكداً.

احذر من الخلط بين الحقل المفقود والقيمة الصفرية: `row.get("qty")` يُعيد `None` إذا كان المفتاح غائباً،
و`0` إذا كانت القيمة صفراً. استخدم `row.get("qty", 0)` عند الحاجة إلى افتراض رقمي.""",
        explanation_en="""Real data usually arrives as a list of dictionaries (records). Core moves:

- **Filtering**: `[r for r in rows if r["status"] == "ok"]`.
- **Grouping**: a dict mapping a key to a list, using
  `dict.setdefault(key, []).append(value)` or `collections.defaultdict(list)`.
- **Summarising**: `sum(...)`, `len(...)`, `max(..., key=...)`.
- **Missing keys**: prefer `row.get("field", default)` over `row["field"]` when a
  field is optional.

Be careful not to confuse a missing field with a zero value: `row.get("qty")`
returns `None` when the key is absent and `0` when the value is zero. Use
`row.get("qty", 0)` when you need a numeric default.""",
        skills=("ds.dicts", "core.loops", "stdlib.collections"),
        prerequisites=("recovery.lists",),
        example_code="""from collections import defaultdict

orders = [
    {"city": "Jeddah", "amount": 120, "status": "paid"},
    {"city": "Riyadh", "amount": 80, "status": "pending"},
    {"city": "Jeddah", "amount": 45, "status": "paid"},
    {"city": "Riyadh", "amount": 200},
]

by_city = defaultdict(int)
for order in orders:
    by_city[order["city"]] += order.get("amount", 0)
print("totals:", dict(by_city))

paid = [o for o in orders if o.get("status") == "paid"]
print("paid orders:", len(paid))
print("largest:", max(orders, key=lambda o: o.get("amount", 0)))
""",
        example_notes_ar='لاحظ أن السجل الأخير لا يحتوي مفتاح status: استخدام o.get("status") أنقذنا من KeyError.',
        example_notes_en="The last record has no `status` key: `o.get('status')` saved us from a `KeyError`.",
        experiment_code="""rows = [
    {"sku": "A1", "qty": 3, "price": 10},
    {"sku": "A2", "qty": 1, "price": 25},
    {"sku": "A1", "qty": 2, "price": 10},
]

# Predict the output, then run it.
revenue = {}
for row in rows:
    revenue[row["sku"]] = revenue.get(row["sku"], 0) + row["qty"] * row["price"]
print(revenue)
print("total:", sum(revenue.values()))
""",
        experiment_brief_ar="تنبأ بمخرجات `revenue` قبل التشغيل، ثم عدّل الكود ليحسب أيضاً إجمالي الكميات لكل منتج.",
        experiment_brief_en="Predict the output before running, then extend the code to also compute total quantity per product.",
        task=TaskSpec(
            brief_ar="""اكتب `summarise(orders)` تُعيد قاموساً فيه:
- `"count"`: عدد السجلات،
- `"revenue"`: مجموع `amount` للطلبات التي حالتها `"paid"` فقط،
- `"by_city"`: قاموس يربط المدينة بإجمالي مبلغها (لكل الطلبات)،
- `"top_city"`: المدينة صاحبة أعلى إجمالي (أو `None` إذا كانت القائمة فارغة).

تجاهل الحقول الناقصة بأمان ولا تُعدّل القائمة المُمرَّرة.""",
            brief_en="""Write `summarise(orders)` returning a dict with:
- `"count"`: number of records,
- `"revenue"`: total `amount` of orders whose status is `"paid"` only,
- `"by_city"`: a dict mapping city to its total amount (all orders),
- `"top_city"`: the city with the highest total (or `None` for an empty list).

Handle missing fields safely and do not mutate the input list.""",
            starter_code="""def summarise(orders):
    # TODO: count, revenue (paid only), by_city totals, top_city
    pass
""",
            public_tests={
                "test_public.py": """from main import summarise

def test_basic():
    result = summarise([
        {"city": "Jeddah", "amount": 100, "status": "paid"},
        {"city": "Riyadh", "amount": 50, "status": "pending"},
    ])
    assert result["count"] == 2
    assert result["revenue"] == 100
    assert result["by_city"] == {"Jeddah": 100, "Riyadh": 50}
    assert result["top_city"] == "Jeddah"
"""},
            hidden_tests={
                "test_hidden.py": """from main import summarise

def test_empty():
    result = summarise([])
    assert result["count"] == 0
    assert result["revenue"] == 0
    assert result["by_city"] == {}
    assert result["top_city"] is None

def test_missing_fields():
    result = summarise([{"city": "Dammam"}, {"amount": 10, "status": "paid"}])
    assert result["revenue"] == 10
    assert result["by_city"]["Dammam"] == 0

def test_input_not_mutated():
    orders = [{"city": "Jeddah", "amount": 5, "status": "paid"}]
    summarise(orders)
    assert orders == [{"city": "Jeddah", "amount": 5, "status": "paid"}]

def test_tie_breaks_deterministically():
    result = summarise([
        {"city": "A", "amount": 1}, {"city": "B", "amount": 1}
    ])
    assert result["top_city"] in ("A", "B")
"""},
            reference_solution="""def summarise(orders):
    by_city = {}
    revenue = 0
    for order in orders:
        amount = order.get("amount", 0)
        city = order.get("city")
        if city is not None:
            by_city[city] = by_city.get(city, 0) + amount
        if order.get("status") == "paid":
            revenue += amount
    top_city = max(by_city, key=by_city.get) if by_city else None
    return {
        "count": len(orders),
        "revenue": revenue,
        "by_city": by_city,
        "top_city": top_city,
    }
""",
            hints=(
                "Build `by_city` first, then `top_city` is just max(by_city, key=by_city.get).",
                "Guard `max()` against an empty dict - it raises ValueError otherwise.",
                "Only add to revenue when status == 'paid'.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `group_by(rows, key)` تُعيد قاموساً يربط كل قيمة للمفتاح بقائمة السجلات المطابقة،
ثم `top_n(rows, key, value_key, n)` تُعيد أعلى `n` مفاتيح حسب مجموع `value_key`.
تعامل مع السجلات التي تفتقد المفتاح بتجاهلها.""",
            brief_en="""Write `group_by(rows, key)` returning a dict mapping each key value to the matching
records, then `top_n(rows, key, value_key, n)` returning the top `n` keys by the sum of
`value_key`. Skip records that lack the key.""",
            independent=True,
            starter_code="""def group_by(rows, key):
    pass


def top_n(rows, key, value_key, n):
    pass
""",
            public_tests={"test_public.py": """from main import group_by, top_n

def test_group_by():
    rows = [{"k": "a"}, {"k": "b"}, {"k": "a"}]
    assert group_by(rows, "k") == {"a": [{"k": "a"}, {"k": "a"}], "b": [{"k": "b"}]}
"""},
            hidden_tests={"test_hidden.py": """from main import group_by, top_n

def test_missing_key_skipped():
    rows = [{"k": "a"}, {"other": 1}]
    assert group_by(rows, "k") == {"a": [{"k": "a"}]}

def test_top_n_sums_values():
    rows = [
        {"team": "x", "points": 3},
        {"team": "y", "points": 10},
        {"team": "x", "points": 4},
    ]
    assert top_n(rows, "team", "points", 1) == ["y"]
    assert set(top_n(rows, "team", "points", 2)) == {"x", "y"}

def test_top_n_larger_than_groups():
    rows = [{"team": "x", "points": 1}]
    assert top_n(rows, "team", "points", 5) == ["x"]

def test_empty_rows():
    assert group_by([], "k") == {}
    assert top_n([], "team", "points", 3) == []
"""},
            reference_solution="""def group_by(rows, key):
    groups = {}
    for row in rows:
        if key in row:
            groups.setdefault(row[key], []).append(row)
    return groups


def top_n(rows, key, value_key, n):
    totals = {}
    for row in rows:
        if key in row and value_key in row:
            totals[row[key]] = totals.get(row[key], 0) + row[value_key]
    ordered = sorted(totals.items(), key=lambda item: (-item[1], str(item[0])))
    return [name for name, _ in ordered[:n]]
""",
        ),
        transfer_ar="استخدم نفس النمط في Data Empire: جمّع المعاملات حسب المنتج ثم احسب الطلب الأسبوعي.",
        transfer_en="Reuse the same pattern in Data Empire: group transactions by product and compute weekly demand.",
        references=(
            ("Python docs - collections", "https://docs.python.org/3/library/collections.html"),
            ("Python docs - dict", "https://docs.python.org/3/library/stdtypes.html#dict"),
        ),
    ),
    CurriculumModule(
        id="l0.read_multifile",
        level=0,
        order_index=4,
        domain="python_core",
        title_ar="قراءة وتعديل تطبيق متعدد الملفات",
        title_en="Reading and modifying a small multi-file app",
        summary_ar="مشروع من ثلاثة ملفات: افهم العلاقة بينها ثم أضف ميزة دون كسر الاختبارات.",
        summary_en="A three-file project: understand how the parts fit, then add a feature without breaking tests.",
        explanation_ar="""المشاريع الحقيقية مقسّمة إلى وحدات. قبل تعديل أي شيء:

1. اقرأ نقطة الدخول (`main.py`) لتعرف ترتيب التنفيذ.
2. تتبّع الاستيرادات لمعرفة من يستخدم ماذا.
3. ابحث عن الاختبارات: إنها العقد الذي يصف السلوك المطلوب.
4. غيّر شيئاً واحداً في كل مرة، ثم شغّل الاختبارات.

قواعد الاستيراد المهمة:
- `import module` ثم `module.func()` — الأفضل لتجنب الالتباس.
- `from module import func` — أقصر، لكنه قد يخفي مصدر الاسم.
- الاستيراد النسبي `from . import x` يعمل فقط داخل الحزم.

ملف `__init__.py` (حتى لو كان فارغاً) يجعل المجلد حزمة قابلة للاستيراد.""",
        explanation_en="""Real projects are split into modules. Before changing anything:

1. Read the entry point (`main.py`) to learn the order of execution.
2. Follow the imports to see who uses what.
3. Find the tests: they are the contract describing required behaviour.
4. Change one thing at a time, then run the tests.

Import rules worth remembering:
- `import module` then `module.func()` - clearest, avoids name clashes.
- `from module import func` - shorter, but hides where a name came from.
- Relative imports (`from . import x`) only work inside packages.

An `__init__.py` file (even an empty one) turns a folder into an importable package.""",
        skills=("core.modules", "core.packages", "career.code_reading"),
        prerequisites=("recovery.functions",),
        example_code="""# --- project layout used in the task -------------------------------
# main.py        -> entry point, wires everything together
# pricing.py     -> pure calculation, no printing
# catalogue.py   -> data access

# pricing.py
DISCOUNTS = {"student": 0.2, "staff": 0.1}


def final_price(price, category=None):
    discount = DISCOUNTS.get(category, 0.0)
    return round(price * (1 - discount), 2)


# main.py
# from pricing import final_price
print(final_price(100, "student"))
print(final_price(100))
""",
        example_notes_ar="لاحظ أن منطق الحساب في ملف مستقل عن الطباعة — هذا يجعله قابلاً للاختبار.",
        example_notes_en="Notice that the calculation lives apart from the printing - that is what makes it testable.",
        experiment_code="""# Create two modules in the workbench and import one from the other.
# inventory.py
ITEMS = {"widget": 12, "bolt": 300}

# stock.py
# from inventory import ITEMS

def available(name, reserved=0):
    return max(0, ITEMS.get(name, 0) - reserved)

ITEMS = {"widget": 12, "bolt": 300}
print(available("widget", 5), available("missing"))
""",
        experiment_brief_ar="انقل `available` إلى ملف مستقل واستوردها. أضف اختباراً يتحقق من سلوك الصنف غير الموجود.",
        experiment_brief_en="Move `available` into its own file and import it. Add a test covering the missing-item case.",
        task=TaskSpec(
            brief_ar="""المشروع مكوّن من ملفين:

**`pricing.py`**
```python
DISCOUNTS = {"student": 0.2, "staff": 0.1}

def final_price(price, category=None):
    discount = DISCOUNTS.get(category, 0.0)
    return round(price * (1 - discount), 2)
```

**`main.py`** يستورد `final_price` ويطبعه.

المطلوب: أضف إلى `pricing.py` دالة `bulk_price(price, quantity, category=None)` بحيث:
- خصم 5% للكميات من 10 إلى 49،
- خصم 10% للكميات 50 فأكثر،
- يُطبَّق خصم الفئة بعد خصم الكمية،
- النتيجة مقرّبة لمنزلتين عشريتين، وغير سالبة.""",
            brief_en="""The project has two files:

**`pricing.py`**
```python
DISCOUNTS = {"student": 0.2, "staff": 0.1}

def final_price(price, category=None):
    discount = DISCOUNTS.get(category, 0.0)
    return round(price * (1 - discount), 2)
```

**`main.py`** imports `final_price` and prints it.

Add `bulk_price(price, quantity, category=None)` to `pricing.py`:
- 5% off for quantities from 10 to 49,
- 10% off for 50 or more,
- the category discount is applied after the bulk discount,
- the result is rounded to two decimals and never negative.""",
            starter_code="""DISCOUNTS = {"student": 0.2, "staff": 0.1}


def final_price(price, category=None):
    discount = DISCOUNTS.get(category, 0.0)
    return round(price * (1 - discount), 2)


def bulk_price(price, quantity, category=None):
    # TODO: quantity discount first, then category discount
    pass
""",
            entry_filename="pricing.py",
            public_tests={
                "test_public.py": """from pricing import final_price, bulk_price

def test_final_price_unchanged():
    assert final_price(100, "student") == 80.0

def test_bulk_small_quantity():
    assert bulk_price(10, 3) == 10.0
"""},
            hidden_tests={
                "test_hidden.py": """from pricing import bulk_price

def test_bulk_tiers():
    assert bulk_price(100, 10) == 95.0
    assert bulk_price(100, 49) == 95.0
    assert bulk_price(100, 50) == 90.0

def test_category_applied_after_bulk():
    # 100 -> 90 (bulk) -> 72 (20% student)
    assert bulk_price(100, 50, "student") == 72.0

def test_rounding_and_negatives():
    assert bulk_price(0, 100) == 0.0
    assert bulk_price(-5, 100) == 0.0
    assert round(bulk_price(9.99, 10), 2) == 9.49

def test_unknown_category():
    assert bulk_price(100, 10, "vip") == 95.0
"""},
            reference_solution="""DISCOUNTS = {"student": 0.2, "staff": 0.1}


def final_price(price, category=None):
    discount = DISCOUNTS.get(category, 0.0)
    return round(price * (1 - discount), 2)


def bulk_price(price, quantity, category=None):
    base = max(0.0, float(price))
    if quantity >= 50:
        base *= 0.90
    elif quantity >= 10:
        base *= 0.95
    discount = DISCOUNTS.get(category, 0.0)
    return round(base * (1 - discount), 2)
""",
            hints=(
                "Apply the bulk discount to the base price first, then the category discount to the result.",
                "Clamp negative prices to zero before discounting.",
                "Keep `final_price` unchanged: the existing tests are your contract.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""في نفس المشروع، أضف وحدة `reports.py` فيها دالة `revenue_by_category(lines)` حيث
`lines` قائمة قواميس بالشكل `{"price": .., "quantity": .., "category": ..}`.
تُعيد الدالة قاموساً يربط الفئة (أو `"none"` عند غيابها) بإجمالي الإيراد بعد خصم الكمية.
استورد `bulk_price` من `pricing` بدل تكرار المنطق.""",
            brief_en="""In the same project, add a `reports.py` module with `revenue_by_category(lines)` where
`lines` is a list of dicts shaped `{"price": .., "quantity": .., "category": ..}`.
It returns a dict mapping each category (or `"none"` when missing) to total revenue after
the bulk discount. Import `bulk_price` from `pricing` instead of duplicating the logic.""",
            independent=True,
            starter_code="""# reports.py
from pricing import bulk_price


def revenue_by_category(lines):
    # TODO: aggregate revenue per category using bulk_price
    pass
""",
            entry_filename="reports.py",
            extra_files={
                "pricing.py": """DISCOUNTS = {"student": 0.2, "staff": 0.1}


def final_price(price, category=None):
    discount = DISCOUNTS.get(category, 0.0)
    return round(price * (1 - discount), 2)


def bulk_price(price, quantity, category=None):
    base = max(0.0, float(price))
    if quantity >= 50:
        base *= 0.90
    elif quantity >= 10:
        base *= 0.95
    discount = DISCOUNTS.get(category, 0.0)
    return round(base * (1 - discount), 2)
"""},
            public_tests={"test_public.py": """from reports import revenue_by_category

def test_basic():
    lines = [{"price": 100, "quantity": 50, "category": "staff"}]
    assert revenue_by_category(lines) == {"staff": 81.0}
"""},
            hidden_tests={"test_hidden.py": """from reports import revenue_by_category

def test_missing_category():
    lines = [{"price": 100, "quantity": 50}]
    assert revenue_by_category(lines) == {"none": 90.0}

def test_aggregation():
    lines = [
        {"price": 10, "quantity": 1, "category": "a"},
        {"price": 10, "quantity": 1, "category": "a"},
    ]
    assert revenue_by_category(lines) == {"a": 20.0}

def test_empty():
    assert revenue_by_category([]) == {}

def test_no_duplicated_logic():
    import inspect, pricing, reports
    source = inspect.getsource(reports)
    assert "bulk_price" in source, "reuse the existing pricing logic"
    assert pricing.bulk_price(100, 50) == 90.0
"""},
            reference_solution="""from pricing import bulk_price


def revenue_by_category(lines):
    totals = {}
    for line in lines:
        category = line.get("category") or "none"
        value = bulk_price(
            line.get("price", 0),
            line.get("quantity", 0),
            None if category == "none" else category,
        )
        totals[category] = round(totals.get(category, 0.0) + value, 2)
    return totals
""",
        ),
        transfer_ar="طبّق نفس المهارة على Project Rescue: اقرأ مستودعاً غير مألوف وحدّد مكان المنطق قبل التعديل.",
        transfer_en="Apply the same skill in Project Rescue: read an unfamiliar repository and locate the logic before editing.",
        references=(
            ("Python docs - modules", "https://docs.python.org/3/tutorial/modules.html"),
            ("Python docs - packages", "https://docs.python.org/3/tutorial/modules.html#packages"),
        ),
    ),
]
