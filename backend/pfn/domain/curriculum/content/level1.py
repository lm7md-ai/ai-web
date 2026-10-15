"""LEVEL 1 - Python foundations (verified: examples execute, references pass tests)."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l1.variables_types",
        level=1,
        order_index=1,
        domain="python_core",
        title_ar="المتغيرات والأنواع",
        title_en="Variables and types",
        summary_ar="الأسماء تشير إلى كائنات؛ الأنواع تحدد ما يمكن فعله بها.",
        summary_en="Names point at objects; types decide what you can do with them.",
        explanation_ar="""المتغير في بايثون **اسم مرتبط بكائن**. `x = 5` لا يضع 5 داخل صندوق اسمه x،
بل يجعل الاسم x يشير إلى كائن العدد 5.

الأنواع الأساسية: `int` و`float` و`str` و`bool` و`NoneType`.
اعرف نوع أي قيمة بـ `type(value)`، وحوّل بين الأنواع بـ `int()` و`float()` و`str()` و`bool()`.

نقاط مهمة:
- القسمة `/` تُنتج دائماً `float`، أما `//` فتُنتج قسمة صحيحة، و`%` هو الباقي.
- `bool` هو نوع فرعي من `int`: `True + True == 2`.
- القيم "الفارغة" تُعتبر خاطئة: `0`, `0.0`, `""`, `[]`, `{}`, `None`.
- السلاسل النصية غير قابلة للتغيير: كل عملية تُنتج سلسلة جديدة.

التنسيق الحديث: استخدم f-strings مثل `f"{name} has {count} items"`.
""",
        explanation_en="""A Python variable is a **name bound to an object**. `x = 5` does not put 5
inside a box called x; it makes the name x refer to the integer object 5.

Core types: `int`, `float`, `str`, `bool`, `NoneType`. Inspect any value with
`type(value)` and convert with `int()`, `float()`, `str()`, `bool()`.

Points that matter:
- `/` always produces a `float`; `//` is floor division; `%` is the remainder.
- `bool` is a subclass of `int`: `True + True == 2`.
- "Empty" values are falsy: `0`, `0.0`, `""`, `[]`, `{}`, `None`.
- Strings are immutable: every operation returns a new string.

For formatting, prefer f-strings: `f"{name} has {count} items"`.""",
        skills=("core.variables", "core.operators", "core.strings"),
        prerequisites=("recovery.syntax",),
        example_code="""name = "Aisha"
age = 21
height = 1.68
is_student = True

print(type(name), type(age), type(height), type(is_student))
print(f"{name} is {age} years old and {height} m tall")

total = 17
people = 5
print("division:", total / people)
print("floor    :", total // people)
print("remainder:", total % people)
print("bool math:", True + True)

value = ""
print("empty string is falsy:", bool(value))
print("zero is falsy:", bool(0), "| one is truthy:", bool(1))
""",
        example_notes_ar="غيّر القيم وشاهد كيف يتغير النوع. جرّب `age / 0` لتقرأ رسالة الخطأ.",
        example_notes_en="Change the values and watch the types. Try `age / 0` and read the error message.",
        experiment_code="""# Predict each result before running this file.
a = 7
b = 2
print(a / b, a // b, a % b, divmod(a, b))

text = "python"
print(text.upper(), text[::-1], text * 2, len(text))

print(int("42") + 1)
print(float("3.5") * 2)
print(bool("False"))   # surprising? every non-empty string is True
""",
        experiment_brief_ar="تنبأ بكل سطر قبل التشغيل. ثم عدّل آخر سطر لاستخدام مقارنة صحيحة بدل bool('False').",
        experiment_brief_en="Predict every line before running. Then fix the last line to use a real comparison instead of bool('False').",
        task=TaskSpec(
            brief_ar="""اكتب `describe(value)` تُعيد سلسلة نصية تصف القيمة بالشكل:
`"int:5"` أو `"str:hello"` أو `"bool:True"` أو `"none"` إذا كانت القيمة `None`.

ثم اكتب `safe_divide(a, b)` تُعيد ناتج القسمة كعدد عشري، أو `None` عندما يكون `b` صفراً.""",
            brief_en="""Write `describe(value)` returning a string describing the value as
`"int:5"`, `"str:hello"`, `"bool:True"`, or `"none"` when the value is `None`.

Then write `safe_divide(a, b)` returning the division result as a float, or `None` when `b` is zero.""",
            starter_code="""def describe(value):
    # TODO: "int:5", "str:hello", "bool:True", "none"
    pass


def safe_divide(a, b):
    # TODO: float division, or None when b == 0
    pass
""",
            public_tests={
                "test_public.py": """from main import describe, safe_divide

def test_describe_int():
    assert describe(5) == "int:5"

def test_safe_divide():
    assert safe_divide(10, 4) == 2.5
"""},
            hidden_tests={
                "test_hidden.py": """from main import describe, safe_divide

def test_describe_types():
    assert describe("hello") == "str:hello"
    assert describe(3.5) == "float:3.5"
    assert describe(None) == "none"

def test_describe_bool_before_int():
    # bool is a subclass of int, so it must be checked first
    assert describe(True) == "bool:True"
    assert describe(False) == "bool:False"

def test_safe_divide_zero():
    assert safe_divide(1, 0) is None
    assert safe_divide(0, 0) is None

def test_safe_divide_negative():
    assert safe_divide(-9, 3) == -3.0
    assert safe_divide(1, 3) > 0.33
"""},
            reference_solution="""def describe(value):
    if value is None:
        return "none"
    if isinstance(value, bool):
        return f"bool:{value}"
    if isinstance(value, int):
        return f"int:{value}"
    if isinstance(value, float):
        return f"float:{value}"
    if isinstance(value, str):
        return f"str:{value}"
    return f"{type(value).__name__}:{value}"


def safe_divide(a, b):
    if b == 0:
        return None
    return a / b
""",
            hints=(
                "Check `bool` before `int`: `isinstance(True, int)` is True in Python.",
                "Check `value is None` first - None is not a str, int or float.",
                "Return `None` (not 0) when the divisor is zero, so callers can tell them apart.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `parse_number(text)` التي:
- تُعيد عدداً صحيحاً إذا كان النص يمثّل عدداً صحيحاً (مثل `"42"` → `42`)،
- تُعيد عدداً عشرياً إذا كان النص يحتوي نقطة (مثل `"3.14"` → `3.14`)،
- تُعيد `None` إذا لم يكن النص رقماً (مثل `"abc"` أو `""`).
لا تستخدم `try/except` هنا: استخدم فحصاً صريحاً.""",
            brief_en="""Write `parse_number(text)` which:
- returns an int when the text is a whole number (`"42"` -> `42`),
- returns a float when the text contains a dot (`"3.14"` -> `3.14`),
- returns `None` when the text is not numeric (`"abc"` or `""`).
Do not use try/except here: check explicitly.""",
            independent=True,
            starter_code="""def parse_number(text):
    # TODO: int, float or None - without try/except
    pass
""",
            public_tests={"test_public.py": """from main import parse_number

def test_int():
    assert parse_number("42") == 42
    assert type(parse_number("42")) is int
"""},
            hidden_tests={"test_hidden.py": """from main import parse_number

def test_float():
    value = parse_number("3.14")
    assert value == 3.14
    assert isinstance(value, float)

def test_invalid():
    assert parse_number("abc") is None
    assert parse_number("") is None
    assert parse_number("12abc") is None

def test_negative_and_signs():
    assert parse_number("-7") == -7
    assert parse_number("-2.5") == -2.5

def test_no_exception_on_weird_input():
    assert parse_number(".") is None
    assert parse_number("1.2.3") is None
"""},
            reference_solution="""def parse_number(text):
    if not isinstance(text, str) or not text:
        return None
    body = text[1:] if text[0] in "+-" else text
    if not body or not body.replace(".", "", 1).isdigit():
        return None
    return float(text) if "." in body else int(text)
""",
        ),
        transfer_ar="استخدم نفس الفحص في Data Empire عند قراءة أسعار من ملف CSV قد يحتوي قيماً ناقصة.",
        transfer_en="Reuse the same checking when reading prices from a CSV that may contain missing values in Data Empire.",
        references=(
            ("Python tutorial - numbers and strings", "https://docs.python.org/3/tutorial/introduction.html"),
            ("Python docs - truth value testing", "https://docs.python.org/3/library/stdtypes.html#truth-value-testing"),
        ),
    ),
    CurriculumModule(
        id="l1.control_flow",
        level=1,
        order_index=2,
        domain="python_core",
        title_ar="الشروط والحلقات",
        title_en="Conditionals and loops",
        summary_ar="اتخاذ القرار والتكرار: الأدوات التي تجعل البرنامج يعمل alone.",
        summary_en="Decisions and repetition: the tools that make a program do work.",
        explanation_ar="""الشرط `if/elif/else` ينفّذ أول فرع يتحقق شرطه فقط.
استخدم تعبيراً شرطياً مضغوطاً للقيم البسيطة: `label = "adult" if age >= 18 else "child"`.

حلقة `for` تمرّر كل عنصر من متتالية: `for item in items:`.
حلقة `while` تستمر طالما الشرط صحيحاً — **احذر من الحلقات اللانهائية**: تأكد أن الشرط سيتغير.

أدوات التحكم:
- `break`: يخرج من الحلقة.
- `continue`: يتخطى بقية الجسم ويبدأ الدورة التالية.
- `else` بعد الحلقة: يُنفَّذ فقط إذا انتهت الحلقة دون `break`.

دوال التكرار المفيدة: `range(n)` و`enumerate(items)` (تعطي الفهرس والقيمة)
و`zip(a, b)` (تمشي على متتاليتين معاً).""",
        explanation_en="""`if/elif/else` runs the first branch whose condition is true, and only that one.
For simple values use the conditional expression:
`label = "adult" if age >= 18 else "child"`.

A `for` loop iterates over a sequence: `for item in items:`.
A `while` loop continues while its condition holds - **watch out for infinite
loops**: make sure something inside the body changes the condition.

Control tools:
- `break` leaves the loop.
- `continue` skips the rest of the body and starts the next round.
- `else` after a loop runs only if the loop finished without `break`.

Useful iteration helpers: `range(n)`, `enumerate(items)` (index and value) and
`zip(a, b)` (walk two sequences together).""",
        skills=("core.conditions", "core.loops", "core.operators"),
        prerequisites=("l1.variables_types",),
        example_code="""temperatures = [21, 35, 18, 40, 29]

for index, value in enumerate(temperatures):
    status = "hot" if value >= 30 else "mild" if value >= 20 else "cold"
    print(index, value, status)

print("--- while with a guard ---")
queue = list(temperatures)
checked = 0
while queue:
    current = queue.pop()
    checked += 1
    if current > 38:
        print("alarm at", current)
        break
else:
    print("no alarm")
print("checked:", checked)
""",
        example_notes_ar="لاحظ أن `else` الخاصة بالحلقة لم تُنفَّذ لأن `break` حدث. أزل الشرط وشاهد الفرق.",
        example_notes_en="The loop's `else` did not run because `break` fired. Remove the condition and watch the difference.",
        experiment_code="""names = ["sara", "omar", "layla"]
scores = [88, 92, 75]

for name, score in zip(names, scores):
    grade = "A" if score >= 90 else "B" if score >= 80 else "C"
    print(f"{name:5s} {score} {grade}")

# Count how many attempts a loop needs - and always keep a safety limit.
attempts = 0
value = 1
while value < 1000 and attempts < 50:
    value *= 2
    attempts += 1
print("reached", value, "in", attempts, "steps")
""",
        experiment_brief_ar="أزل الشرط `attempts < 50` وفكّر ماذا يحدث. ثم عدّل الكود ليحسب المعدل باستخدام حلقة for عادية.",
        experiment_brief_en="Remove the `attempts < 50` guard and think about what happens. Then compute the average with a plain for loop.",
        task=TaskSpec(
            brief_ar="""اكتب `classify_temps(values)` تُعيد قائمة سلاسل: `"hot"` إذا كانت القيمة ≥ 30،
و`"mild"` إذا كانت ≥ 20، و`"cold"` خلاف ذلك.

ثم اكتب `first_alarm(values, limit)` تُعيد **فهرس** أول قيمة تتجاوز `limit`،
أو `-1` إذا لم توجد. استخدم حلقة واحدة فقط.""",
            brief_en="""Write `classify_temps(values)` returning a list of strings: `"hot"` when the value
is >= 30, `"mild"` when it is >= 20, and `"cold"` otherwise.

Then write `first_alarm(values, limit)` returning the **index** of the first value above
`limit`, or `-1` when there is none. Use a single loop.""",
            starter_code="""def classify_temps(values):
    # TODO: "hot" >= 30, "mild" >= 20, else "cold"
    pass


def first_alarm(values, limit):
    # TODO: index of the first value > limit, else -1
    pass
""",
            public_tests={
                "test_public.py": """from main import classify_temps, first_alarm

def test_classify():
    assert classify_temps([10, 25, 35]) == ["cold", "mild", "hot"]

def test_first_alarm():
    assert first_alarm([10, 40, 50], 30) == 1
"""},
            hidden_tests={
                "test_hidden.py": """from main import classify_temps, first_alarm

def test_boundaries():
    assert classify_temps([19, 20, 29, 30]) == ["cold", "mild", "mild", "hot"]

def test_empty():
    assert classify_temps([]) == []
    assert first_alarm([], 5) == -1

def test_no_alarm():
    assert first_alarm([1, 2, 3], 100) == -1

def test_strictly_greater():
    assert first_alarm([30, 31], 30) == 1

def test_negative_values():
    assert classify_temps([-5]) == ["cold"]
    assert first_alarm([-5, -1], -3) == 1
"""},
            reference_solution="""def classify_temps(values):
    result = []
    for value in values:
        if value >= 30:
            result.append("hot")
        elif value >= 20:
            result.append("mild")
        else:
            result.append("cold")
    return result


def first_alarm(values, limit):
    for index, value in enumerate(values):
        if value > limit:
            return index
    return -1
""",
            hints=(
                "`enumerate(values)` gives you the index without a counter variable.",
                "The task says strictly greater than the limit - equal values do not trigger the alarm.",
                "Return -1 after the loop, not inside it.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `running_max(values)` تُعيد قائمة فيها أكبر قيمة **حتى كل موضع**.
مثال: `[3, 1, 5, 2]` → `[3, 3, 5, 5]`.

ثم اكتب `longest_streak(values, threshold)` تُعيد طول أطول سلسلة متصلة من القيم
الأكبر من أو تساوي `threshold`.""",
            brief_en="""Write `running_max(values)` returning a list with the largest value **up to each
position**. Example: `[3, 1, 5, 2]` -> `[3, 3, 5, 5]`.

Then write `longest_streak(values, threshold)` returning the length of the longest
consecutive run of values greater than or equal to `threshold`.""",
            independent=True,
            starter_code="""def running_max(values):
    pass


def longest_streak(values, threshold):
    pass
""",
            public_tests={"test_public.py": """from main import running_max

def test_running_max():
    assert running_max([3, 1, 5, 2]) == [3, 3, 5, 5]
"""},
            hidden_tests={"test_hidden.py": """from main import running_max, longest_streak

def test_running_max_descending():
    assert running_max([5, 4, 3]) == [5, 5, 5]

def test_running_max_empty():
    assert running_max([]) == []

def test_streak_basic():
    assert longest_streak([1, 5, 6, 1, 7], 5) == 2
    assert longest_streak([1, 1, 1], 5) == 0

def test_streak_at_the_end():
    assert longest_streak([0, 5, 5, 5], 5) == 3

def test_streak_all():
    assert longest_streak([9, 9], 1) == 2
    assert longest_streak([], 1) == 0
"""},
            reference_solution="""def running_max(values):
    result = []
    best = None
    for value in values:
        best = value if best is None or value > best else best
        result.append(best)
    return result


def longest_streak(values, threshold):
    best = current = 0
    for value in values:
        if value >= threshold:
            current += 1
            if current > best:
                best = current
        else:
            current = 0
    return best
""",
        ),
        transfer_ar="طبّق `first_alarm` على RoboVerse: أوقف الروبوت عند أول خلية عائق أمامه.",
        transfer_en="Apply `first_alarm` in RoboVerse: stop the robot at the first obstacle cell ahead.",
        references=(
            ("Python tutorial - control flow", "https://docs.python.org/3/tutorial/controlflow.html"),
            ("Python docs - enumerate/zip", "https://docs.python.org/3/library/functions.html"),
        ),
    ),
    CurriculumModule(
        id="l1.functions",
        level=1,
        order_index=3,
        domain="python_core",
        title_ar="الدوال",
        title_en="Functions",
        summary_ar="تسمية خطوات قابلة لإعادة الاستخدام، مع وسائط واضحة وقيمة مُعادة واحدة.",
        summary_en="Naming reusable steps, with clear parameters and one return value.",
        explanation_ar="""الدالة تحزم سلوكاً وتعطيه اسماً. عناصرها:

- **المعاملات**: موضعية، أو بالاسم (`f(a, b=2)`)، أو `*args` و`**kwargs`.
- **القيمة الافتراضية**: تُحسب مرة واحدة عند التعريف — لذلك لا تستخدم قائمة أو قاموساً كقيمة افتراضية.
- **الإرجاع**: `return` يُنهئ الدالة؛ بدون قيمة تُعيد `None`. لإرجاع أكثر من شيء أرجع `tuple`.
- **التوثيق**: اكتب docstring قصيراً يشرح المدخلات والمخرجات.

قاعدة عملية: الدالة الجيدة تفعل شيئاً واحداً، ولا تطبع داخلها إن كانت ستُستخدم في حسابات —
اترك الطباعة للمتصل.""",
        explanation_en="""A function packages behaviour under a name. Its parts:

- **Parameters**: positional, keyword (`f(a, b=2)`), or `*args` / `**kwargs`.
- **Defaults**: evaluated once at definition time - never use a list or dict as a default.
- **Return**: `return` ends the function; with no value it returns `None`. To hand
  back several results, return a tuple.
- **Documentation**: write a short docstring describing inputs and outputs.

Practical rule: a good function does one thing, and it does not print if it will
be used inside calculations - leave printing to the caller.""",
        skills=("core.functions", "core.scope"),
        prerequisites=("l1.control_flow",),
        example_code="""def total_with_tax(price, tax_rate=0.15, *, discount=0.0):
    \"\"\"Return the price including tax, after an optional discount.\"\"\"
    base = max(0.0, price) * (1 - discount)
    return round(base * (1 + tax_rate), 2)


def min_max(values):
    \"\"\"Return both extremes as a tuple.\"\"\"
    if not values:
        return None, None
    return min(values), max(values)


print(total_with_tax(100))
print(total_with_tax(100, discount=0.2))
low, high = min_max([4, 1, 9])
print("range:", low, high)
""",
        example_notes_ar="الوسيط بعد `*` يجب تمريره بالاسم. جرّب `total_with_tax(100, 0.2)` ولاحظ الخطأ.",
        example_notes_en="Arguments after `*` must be passed by name. Try `total_with_tax(100, 0.2)` and read the error.",
        experiment_code="""def stats(*numbers, **options):
    if not numbers:
        return {}
    result = {"count": len(numbers), "mean": sum(numbers) / len(numbers)}
    if options.get("include_extremes"):
        result["min"] = min(numbers)
        result["max"] = max(numbers)
    return result

print(stats(1, 2, 3))
print(stats(1, 2, 3, include_extremes=True))
print(stats())
""",
        experiment_brief_ar="أضف خياراً باسم `median` يحسب الوسيط باستخدام sorted، وجرّبه على قوائم فردية وزوجية.",
        experiment_brief_en="Add a `median` option that computes the median with sorted(), and try it on odd and even lists.",
        task=TaskSpec(
            brief_ar="""اكتب `apply_discount(prices, percent, minimum=0.0)` تُعيد **قائمة جديدة** بأسعار مخفّضة،
بحيث لا يقل أي سعر عن `minimum`. ثم اكتب `invoice_total(items)` حيث `items` قائمة
قواميس بالشكل `{"price": .., "quantity": ..}`، وتُعيد الإجمالي مضروباً في 1.15 (ضريبة)
مقرّباً لمنزلتين. الحقل الناقص `price` يُحسب صفراً، والحقل الناقص `quantity` يُحسب واحداً.""",
            brief_en="""Write `apply_discount(prices, percent, minimum=0.0)` returning a **new list** of
discounted prices, never letting a price fall below `minimum`. Then write
`invoice_total(items)` where `items` is a list of dicts shaped
`{"price": .., "quantity": ..}`, returning the total times 1.15 (tax) rounded to two decimals.
A missing `price` counts as zero and a missing `quantity` counts as one.""",
            starter_code="""def apply_discount(prices, percent, minimum=0.0):
    # TODO: new list, discounted, floored at minimum
    pass


def invoice_total(items):
    # TODO: sum(price * quantity) * 1.15, rounded to 2 decimals
    pass
""",
            public_tests={
                "test_public.py": """from main import apply_discount, invoice_total

def test_apply_discount():
    assert apply_discount([100, 50], 10) == [90.0, 45.0]

def test_invoice_total():
    assert invoice_total([{"price": 10, "quantity": 2}]) == 23.0
"""},
            hidden_tests={
                "test_hidden.py": """from main import apply_discount, invoice_total

def test_original_not_mutated():
    prices = [100, 50]
    apply_discount(prices, 10)
    assert prices == [100, 50]

def test_minimum_floor():
    assert apply_discount([5, 100], 50, minimum=10) == [10.0, 50.0]

def test_zero_percent():
    assert apply_discount([1, 2], 0) == [1.0, 2.0]

def test_invoice_missing_fields():
    assert invoice_total([{"price": 10}, {"quantity": 2}]) == 11.5

def test_invoice_empty():
    assert invoice_total([]) == 0.0
"""},
            reference_solution="""def apply_discount(prices, percent, minimum=0.0):
    result = []
    for price in prices:
        discounted = price * (1 - percent / 100)
        result.append(max(minimum, round(discounted, 2)))
    return result


def invoice_total(items):
    subtotal = 0.0
    for item in items:
        subtotal += item.get("price", 0) * item.get("quantity", 1)
    return round(subtotal * 1.15, 2)
""",
            hints=(
                "Build a new list; do not modify `prices` in place.",
                "`max(minimum, value)` applies the floor in one step.",
                "Use `.get(" ", 0)` for optional fields so missing keys do not raise.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `make_counter(start=0)` تُعيد دالة `counter()` تُعيد رقماً متزايداً في كل استدعاء
(تبدأ من `start`). استخدم الإغلاق (closure) لحفظ الحالة.

ثم اكتب `once(func)` تُعيد دالة تنفّذ `func` مرة واحدة فقط وتُعيد نفس النتيجة بعد ذلك.""",
            brief_en="""Write `make_counter(start=0)` returning a `counter()` function that yields an
increasing number on every call (starting at `start`). Use a closure to hold the state.

Then write `once(func)` returning a wrapper that runs `func` only the first time and
replays the same result afterwards.""",
            independent=True,
            starter_code="""def make_counter(start=0):
    # TODO: return a callable that increments
    pass


def once(func):
    # TODO: return a wrapper that caches the first result
    pass
""",
            public_tests={"test_public.py": """from main import make_counter

def test_counter():
    counter = make_counter()
    assert [counter(), counter(), counter()] == [1, 2, 3]
"""},
            hidden_tests={"test_hidden.py": """from main import make_counter, once

def test_counter_start():
    counter = make_counter(10)
    assert counter() == 11
    assert counter() == 12

def test_counters_are_independent():
    a, b = make_counter(), make_counter()
    a()
    assert b() == 1

def test_once_caches():
    calls = []

    def expensive():
        calls.append(1)
        return 42

    wrapped = once(expensive)
    assert wrapped() == 42
    assert wrapped() == 42
    assert len(calls) == 1

def test_once_passes_arguments():
    @once
    def double(x):
        return x * 2

    assert double(3) == 6
"""},
            reference_solution="""def make_counter(start=0):
    count = start

    def counter():
        nonlocal count
        count += 1
        return count

    return counter


def once(func):
    cache = {}

    def wrapper(*args, **kwargs):
        if "value" not in cache:
            cache["value"] = func(*args, **kwargs)
        return cache["value"]

    return wrapper
""",
        ),
        transfer_ar="استخدم `once` في Data Empire لتحميل ملف البيانات مرة واحدة فقط داخل الجلسة.",
        transfer_en="Use `once` in Data Empire to load a data file a single time per session.",
        references=(
            ("Python tutorial - defining functions", "https://docs.python.org/3/tutorial/controlflow.html#defining-functions"),
            ("PEP 8 - naming and layout", "https://peps.python.org/pep-0008/"),
        ),
    ),
    CurriculumModule(
        id="l1.lists_tuples",
        level=1,
        order_index=4,
        domain="data_structures",
        title_ar="القوائم والصفوف",
        title_en="Lists and tuples",
        summary_ar="متتاليات مرتبة: متى تستخدم قائمة قابلة للتغيير ومتى تستخدم صفاً ثابتاً.",
        summary_en="Ordered sequences: when to use a mutable list and when an immutable tuple.",
        explanation_ar="""القائمة `list` متتالية **قابلة للتغيير**: `append` و`extend` و`insert` و`pop` و`remove` و`sort`.

الصف `tuple` متتالية **ثابتة**: مناسب للسجلات والإحداثيات ومفاتيح القواميس،
وللبيانات التي لا يجب أن تتغير بالخطأ.

عمليات مهمة:
- التقطيع `items[1:4]` و`items[::-1]` (عكس) — يُنتج كائناً جديداً.
- `items.copy()` أو `items[:]` لنسخة سطحية.
- `sorted(items, key=...)` تُعيد قائمة جديدة، أما `items.sort()` فترتّب في المكان.
- `enumerate` و`zip` للتكرار.

تكلفة العمليات: الفهرسة والوصول للنهاية `O(1)`، أما البحث `x in list` والإدراج في
البداية فـ `O(n)`. إذا كنت تبحث كثيراً استخدم `set` أو `dict`.""",
        explanation_en="""A `list` is a **mutable** sequence: `append`, `extend`, `insert`, `pop`, `remove`,
`sort`.

A `tuple` is **immutable**: ideal for records, coordinates and dictionary keys, and
for data that must not change by accident.

Important operations:
- Slicing `items[1:4]` and `items[::-1]` (reverse) - both build new objects.
- `items.copy()` or `items[:]` for a shallow copy.
- `sorted(items, key=...)` returns a new list; `items.sort()` sorts in place.
- `enumerate` and `zip` for iteration.

Cost: indexing and appending are `O(1)`; searching with `x in list` and inserting at
the front are `O(n)`. If you search a lot, reach for a `set` or `dict`.""",
        skills=("ds.lists", "ds.tuples", "core.mutability"),
        prerequisites=("l1.functions",),
        example_code="""items = [5, 2, 9, 1]
items.append(7)
items.sort()
print("sorted in place:", items)

print("slice:", items[1:4], "reversed:", items[::-1])
print("sorted copy:", sorted([5, 2, 9], reverse=True))

coordinates = [(0, 0), (3, 4), (1, 1)]
for x, y in coordinates:          # tuple unpacking
    print(f"distance from origin: {(x * x + y * y) ** 0.5:.2f}")

first, *middle, last = items      # extended unpacking
print("first:", first, "middle:", middle, "last:", last)
""",
        example_notes_ar="الصفوف تُفكَّغ تلقائياً في `for x, y in`. جرّب تقطيعاً بخطوة 2: `items[::2]`.",
        example_notes_en="Tuples unpack automatically in `for x, y in`. Try a step of two: `items[::2]`.",
        experiment_code="""import time

def time_membership(container, target, repeats=20000):
    start = time.perf_counter()
    for _ in range(repeats):
        _ = target in container
    return (time.perf_counter() - start) * 1000

big_list = list(range(20000))
big_set = set(big_list)

print("list search ms:", round(time_membership(big_list, 19999), 2))
print("set  search ms:", round(time_membership(big_set, 19999), 2))
""",
        experiment_brief_ar="شغّل القياس عدة مرات. لماذا البحث في المجموعة أسرع بكثير؟ اكتب استنتاجك في تعليق.",
        experiment_brief_en="Run the measurement several times. Why is the set search so much faster? Write your conclusion in a comment.",
        task=TaskSpec(
            brief_ar="""اكتب `move_zeroes(values)` تُعيد قائمة جديدة تنقل كل الأصفار إلى النهاية مع الحفاظ على
ترتيب بقية العناصر: `[0, 1, 0, 3, 12]` → `[1, 3, 12, 0, 0]`.

ثم اكتب `merge_sorted(a, b)` تدمج قائمتين مرتبتين في قائمة مرتبة واحدة (بأسلوب الدمج).""",
            brief_en="""Write `move_zeroes(values)` returning a new list that pushes every zero to the end
while preserving the order of the rest: `[0, 1, 0, 3, 12]` -> `[1, 3, 12, 0, 0]`.

Then write `merge_sorted(a, b)` merging two sorted lists into one sorted list (merge style).""",
            starter_code="""def move_zeroes(values):
    # TODO: new list, zeroes at the end, order preserved
    pass


def merge_sorted(a, b):
    # TODO: merge two sorted lists
    pass
""",
            public_tests={
                "test_public.py": """from main import move_zeroes, merge_sorted

def test_move_zeroes():
    assert move_zeroes([0, 1, 0, 3, 12]) == [1, 3, 12, 0, 0]

def test_merge():
    assert merge_sorted([1, 3], [2, 4]) == [1, 2, 3, 4]
"""},
            hidden_tests={
                "test_hidden.py": """from main import move_zeroes, merge_sorted

def test_input_not_mutated():
    values = [0, 1]
    move_zeroes(values)
    assert values == [0, 1]

def test_all_zeroes_and_empty():
    assert move_zeroes([0, 0]) == [0, 0]
    assert move_zeroes([]) == []
    assert move_zeroes([1, 2]) == [1, 2]

def test_merge_uneven():
    assert merge_sorted([1], [2, 3, 4]) == [1, 2, 3, 4]
    assert merge_sorted([5, 6], [1]) == [1, 5, 6]

def test_merge_duplicates_and_empty():
    assert merge_sorted([1, 1], [1]) == [1, 1, 1]
    assert merge_sorted([], [1, 2]) == [1, 2]
    assert merge_sorted([1, 2], []) == [1, 2]
"""},
            reference_solution="""def move_zeroes(values):
    non_zero = [value for value in values if value != 0]
    return non_zero + [0] * (len(values) - len(non_zero))


def merge_sorted(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result
""",
            hints=(
                "Collect non-zero items, then append the right number of zeroes.",
                "For the merge, keep two indices and compare the current heads.",
                "`result.extend(a[i:])` adds the leftovers in one step.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `chunk(values, size)` تُعيد قائمة من القوائم (دفعات) بحجم `size`،
آخر دفعة قد تكون أقصر. ارفع `ValueError` إذا كان `size` ≤ 0.

ثم اكتب `running_sum(values)` تُعيد قائمة المجاميع التراكمية.""",
            brief_en="""Write `chunk(values, size)` returning a list of batches of length `size`; the last
batch may be shorter. Raise `ValueError` when `size` <= 0.

Then write `running_sum(values)` returning the cumulative sums.""",
            independent=True,
            starter_code="""def chunk(values, size):
    pass


def running_sum(values):
    pass
""",
            public_tests={"test_public.py": """from main import chunk

def test_chunk():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
"""},
            hidden_tests={"test_hidden.py": """from main import chunk, running_sum
import pytest

def test_chunk_exact():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

def test_chunk_bad_size():
    with pytest.raises(ValueError):
        chunk([1], 0)
    with pytest.raises(ValueError):
        chunk([1], -3)

def test_chunk_empty():
    assert chunk([], 3) == []

def test_running_sum():
    assert running_sum([1, 2, 3]) == [1, 3, 6]
    assert running_sum([]) == []
    assert running_sum([-1, 1]) == [-1, 0]
"""},
            reference_solution="""def chunk(values, size):
    if size <= 0:
        raise ValueError("size must be positive")
    return [list(values[i:i + size]) for i in range(0, len(values), size)]


def running_sum(values):
    total = 0
    result = []
    for value in values:
        total += value
        result.append(total)
    return result
""",
        ),
        transfer_ar="استخدم `merge_sorted` في Algorithm Gladiators كخطوة أساسية في ترتيب الدمج.",
        transfer_en="Reuse `merge_sorted` in Algorithm Gladiators as the core step of merge sort.",
        references=(
            ("Python docs - list methods", "https://docs.python.org/3/tutorial/datastructures.html"),
            ("Python wiki - time complexity", "https://wiki.python.org/moin/TimeComplexity"),
        ),
    ),
    CurriculumModule(
        id="l1.dicts_sets",
        level=1,
        order_index=5,
        domain="data_structures",
        title_ar="القواميس والمجموعات",
        title_en="Dictionaries and sets",
        summary_ar="خرائط سريعة البحث وقيم فريدة: أساس معالجة البيانات.",
        summary_en="Fast lookups and unique values: the foundation of data work.",
        explanation_ar="""القاموس `dict` خريطة من مفاتيح قابلة للتجزئة إلى قيم. البحث فيه سريع (متوسط O(1)).

أدوات أساسية:
- `d.get(key, default)` لتجنب `KeyError`.
- `d.setdefault(key, [])` لبناء قوائم مجمّعة.
- `collections.Counter` للعدّ، و`defaultdict` للتجميع.
- المرور: `for key, value in d.items()`.

المجموعة `set` تحتفظ بقيم فريدة غير مرتبة وتدعم `|` (اتحاد) و`&` (تقاطع) و`-` (فرق).

المفاتيح يجب أن تكون قابلة للتجزئة: `str` و`int` و`tuple` (من عناصر ثابتة) تعمل،
أما `list` و`dict` فلا تعمل.""",
        explanation_en="""A `dict` maps hashable keys to values, with O(1) average lookup.

Essentials:
- `d.get(key, default)` to avoid `KeyError`.
- `d.setdefault(key, [])` to build grouped lists.
- `collections.Counter` for counting and `defaultdict` for grouping.
- Iterate with `for key, value in d.items()`.

A `set` holds unique, unordered values and supports `|` (union), `&` (intersection)
and `-` (difference).

Keys must be hashable: `str`, `int` and `tuple` (of immutable items) work, while
`list` and `dict` do not.""",
        skills=("ds.dicts", "ds.sets", "stdlib.collections"),
        prerequisites=("l1.lists_tuples",),
        example_code="""from collections import Counter, defaultdict

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counts = Counter(words)
print("counts:", counts)
print("most common:", counts.most_common(2))

grouped = defaultdict(list)
for word in words:
    grouped[word[0]].append(word)
print("grouped:", dict(grouped))

inventory = {"apple": 10, "banana": 3}
order = {"apple": 4, "cherry": 2}
for item, qty in order.items():
    available = inventory.get(item, 0)
    print(f"{item}: need {qty}, have {available}")

print("missing items:", set(order) - set(inventory))
""",
        example_notes_ar="`Counter` هو قاموس متخصص: تستطيع جمعه وطرحه مع عدّاد آخر.",
        example_notes_en="`Counter` is a specialised dict: you can add and subtract counters.",
        experiment_code="""from collections import Counter

text = "the quick brown fox jumps over the lazy dog the fox"
tokens = text.split()

frequency = Counter(tokens)
print("unique words:", len(frequency))
print("top 3:", frequency.most_common(3))

# Build a simple inverted index: word -> sorted positions
index = {}
for position, token in enumerate(tokens):
    index.setdefault(token, []).append(position)
print("fox appears at:", index["fox"])
print("words appearing once:", [w for w, p in index.items() if len(p) == 1])
""",
        experiment_brief_ar="وسّع الفهرس ليحسب أيضاً عدد الجمل (استخدم النقطة فاصلاً) وأضف بحثاً يعيد كل المواضع لكلمة.",
        experiment_brief_en="Extend the index to also count sentences (split on the full stop) and add a lookup returning every position of a word.",
        task=TaskSpec(
            brief_ar="""اكتب `word_frequencies(text)` تُعيد قاموساً يربط الكلمة (بحروف صغيرة، بدون علامات ترقيم)
عدد مرات ظهورها.

ثم اكتب `unique_sorted(values)` تُعيد قائمة مرتبة من القيم الفريدة فقط.
رتّب أولاً حسب اسم النوع ثم حسب القيمة، حتى لا يفشل الترتيب عند اختلاط الأنواع.""",
            brief_en="""Write `word_frequencies(text)` returning a dict mapping each word (lowercase,
punctuation stripped) to how often it appears.

Then write `unique_sorted(values)` returning a sorted list of the unique values only.
Sort by type name first and then by value, so mixed types never raise a TypeError.""",
            starter_code="""def word_frequencies(text):
    # TODO: lowercase, strip punctuation, count
    pass


def unique_sorted(values):
    # TODO: sorted unique values
    pass
""",
            public_tests={
                "test_public.py": """from main import word_frequencies, unique_sorted

def test_word_frequencies():
    assert word_frequencies("Hi hi there") == {"hi": 2, "there": 1}

def test_unique_sorted():
    assert unique_sorted([3, 1, 3, 2]) == [1, 2, 3]
"""},
            hidden_tests={
                "test_hidden.py": """from main import word_frequencies, unique_sorted

def test_punctuation_stripped():
    result = word_frequencies("Hello, hello! world.")
    assert result == {"hello": 2, "world": 1}

def test_empty_text():
    assert word_frequencies("") == {}
    assert word_frequencies("   ") == {}

def test_numbers_and_hyphens():
    result = word_frequencies("data-2024 data")
    assert "data" in result
    assert result["data"] == 1

def test_unique_with_strings():
    assert unique_sorted(["b", "a", "b"]) == ["a", "b"]
    assert unique_sorted([]) == []

def test_unique_mixed_fails_gracefully():
    assert unique_sorted([2, "2"]) == [2, "2"] or unique_sorted([2, "2"]) == ["2", 2]
"""},
            reference_solution="""import string

_TRANSLATION = str.maketrans("", "", string.punctuation)


def word_frequencies(text):
    counts = {}
    for raw in text.split():
        word = raw.strip().lower().translate(_TRANSLATION)
        if not word:
            continue
        counts[word] = counts.get(word, 0) + 1
    return counts


def unique_sorted(values):
    return sorted(set(values), key=lambda value: (type(value).__name__, value))
""",
            hints=(
                "`str.maketrans('', '', string.punctuation)` plus `.translate()` strips punctuation in one call.",
                "Lowercase before counting, otherwise 'Hi' and 'hi' are different keys.",
                "`sorted(set(values), key=lambda v: (type(v).__name__, v))` never raises on mixed types.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `invert_index(documents)` حيث `documents` قاموس يربط اسم المستند بنصه،
فتُعيد قاموساً يربط الكلمة بقائمة أسماء المستندات التي تحتويها (مرتبة أبجدياً).

ثم اكتب `search(index, query)` تُعيد قائمة المستندات التي تحتوي **كل** كلمات الاستعلام.""",
            brief_en="""Write `invert_index(documents)` where `documents` maps a document name to its text,
returning a dict mapping each word to the alphabetically sorted list of documents containing it.

Then write `search(index, query)` returning the documents containing **all** query words.""",
            independent=True,
            starter_code="""def invert_index(documents):
    pass


def search(index, query):
    pass
""",
            public_tests={"test_public.py": """from main import invert_index, search

def test_index():
    index = invert_index({"a": "hello world", "b": "hello"})
    assert index["hello"] == ["a", "b"]
"""},
            hidden_tests={"test_hidden.py": """from main import invert_index, search

def test_index_sorted():
    index = invert_index({"b": "x", "a": "x"})
    assert index["x"] == ["a", "b"]

def test_search_all_words():
    index = invert_index({"a": "hello world", "b": "hello", "c": "world"})
    assert search(index, "hello world") == ["a"]

def test_search_unknown_word():
    index = invert_index({"a": "hello"})
    assert search(index, "hello missing") == []

def test_empty_inputs():
    assert invert_index({}) == {}
    assert search({}, "anything") == []
    assert search({"x": ["a"]}, "") == ["a"]
"""},
            reference_solution="""import string

_TRANSLATION = str.maketrans("", "", string.punctuation)


def _tokens(text):
    return [
        token.translate(_TRANSLATION).lower()
        for token in text.split()
        if token.translate(_TRANSLATION)
    ]


def invert_index(documents):
    index = {}
    for name, text in documents.items():
        for token in set(_tokens(text)):
            index.setdefault(token, []).append(name)
    for token in index:
        index[token].sort()
    return index


def search(index, query):
    words = [word.lower() for word in query.split() if word]
    if not words:
        return sorted({name for names in index.values() for name in names})
    found = None
    for word in words:
        current = set(index.get(word, []))
        found = current if found is None else found & current
    return sorted(found or [])
""",
        ),
        transfer_ar="ابنِ فهرساً مشابهاً في Agent Planet لاسترجاع الوثائق (RAG) قبل إجابة النموذج.",
        transfer_en="Build a similar index in Agent Planet for document retrieval (RAG) before answering.",
        references=(
            ("Python docs - dict", "https://docs.python.org/3/library/stdtypes.html#typesmapping"),
            ("Python docs - collections", "https://docs.python.org/3/library/collections.html"),
        ),
    ),
    CurriculumModule(
        id="l1.files_exceptions",
        level=1,
        order_index=6,
        domain="python_core",
        title_ar="الملفات والاستثناءات",
        title_en="Files and exceptions",
        summary_ar="قراءة وكتابة ملفات بأمان، والتعامل مع الأخطاء دون إخفائها.",
        summary_en="Reading and writing files safely, and handling errors without hiding them.",
        explanation_ar="""استخدم `with open(path, encoding="utf-8")` دائماً: يغلق الملف تلقائياً حتى لو حدث خطأ.

الاستثناءات:
- `try / except / else / finally`: عالج الحالة المتوقعة فقط، ولا تستخدم `except:` مجرداً.
- اربط الاستثناءات: `raise ValueError("...") from exc` للحفاظ على السبب.
- اكتب رسائل خطأ تقول **ماذا** حدث و**أين**.

الأخطاء الشائعة:
- نسيان `encoding` (يختلف حسب النظام).
- كتابة مسارات بشرطات مائلة خاصة بنظام واحد — استخدم `pathlib`.
- ابتلاع الخطأ بـ `except Exception: pass` — هذا يخفي الأخطاء الحقيقية.""",
        explanation_en="""Always use `with open(path, encoding="utf-8")`: it closes the file even when an
exception is raised.

Exceptions:
- `try / except / else / finally`: handle only what you expect, and never a bare `except:`.
- Chain exceptions with `raise ValueError("...") from exc` to preserve the cause.
- Write error messages that say **what** happened and **where**.

Common mistakes:
- forgetting `encoding` (it depends on the platform otherwise);
- hard-coding platform-specific path separators - use `pathlib` instead;
- swallowing errors with `except Exception: pass`, which hides real bugs.""",
        skills=("core.files", "core.exceptions", "stdlib.pathlib"),
        prerequisites=("l1.dicts_sets",),
        example_code="""from pathlib import Path
import json
import tempfile

workdir = Path(tempfile.mkdtemp())
data_file = workdir / "scores.json"

scores = {"sara": 88, "omar": 92}
with data_file.open("w", encoding="utf-8") as handle:
    json.dump(scores, handle, ensure_ascii=False)

with data_file.open("r", encoding="utf-8") as handle:
    loaded = json.load(handle)
print("round trip:", loaded, loaded == scores)

try:
    missing = (workdir / "nope.json").open()
except FileNotFoundError as exc:
    print("handled:", type(exc).__name__, exc.filename)

print("exists:", data_file.exists(), "| size:", data_file.stat().st_size)
""",
        example_notes_ar="`pathlib` يجعل المسارات محمولة بين Windows وLinux وmacOS.",
        example_notes_en="`pathlib` keeps paths portable across Windows, Linux and macOS.",
        experiment_code="""from pathlib import Path
import tempfile, csv

workdir = Path(tempfile.mkdtemp())
csv_path = workdir / "sales.csv"

rows = [
    {"city": "Jeddah", "amount": "120"},
    {"city": "Riyadh", "amount": "80"},
]
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["city", "amount"])
    writer.writeheader()
    writer.writerows(rows)

# Now read it back and compute the total - including a deliberate type bug.
with csv_path.open("r", encoding="utf-8") as handle:
    data = list(csv.DictReader(handle))
print("rows:", data)
print("total:", sum(int(row["amount"]) for row in data))
""",
        experiment_brief_ar="أضف صفاً بقيمة amount فارغة وشاهد الخطأ. ثم عالجه بحيث تُعامل القيمة الفارغة كصفر.",
        experiment_brief_en="Add a row with an empty amount and watch the error. Then handle it so an empty value counts as zero.",
        task=TaskSpec(
            brief_ar="""اكتب `read_numbers(path)` التي تقرأ ملفاً نصياً سطراً بسطر وتُعيد قائمة أعداد صحيحة،
متجاهلة الأسطر الفارغة والأسطر التي تبدأ بـ `#`.

اكتب أيضاً `write_report(path, rows)` التي تكتب كل سطر من `rows` في ملف UTF-8،
وتُعيد عدد الأسطر المكتوبة. ارفع `OSError` للمتصل إذا تعذّرت الكتابة (لا تبتلع الخطأ).""",
            brief_en="""Write `read_numbers(path)` reading a text file line by line and returning a list of
integers, skipping blank lines and lines starting with `#`.

Also write `write_report(path, rows)` writing each item of `rows` on its own line in a
UTF-8 file and returning the number of lines written. Let `OSError` reach the caller
instead of swallowing it.""",
            starter_code="""from pathlib import Path


def read_numbers(path):
    # TODO: integers, skip blanks and comments
    pass


def write_report(path, rows):
    # TODO: write lines in UTF-8, return the count
    pass
""",
            public_tests={
                "test_public.py": """from main import read_numbers, write_report
from pathlib import Path

def test_read_numbers(tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("1\\n# comment\\n\\n22\\n", encoding="utf-8")
    assert read_numbers(path) == [1, 22]

def test_write_report(tmp_path):
    path = tmp_path / "out.txt"
    assert write_report(path, ["a", "b"]) == 2
    assert path.read_text(encoding="utf-8") == "a\\nb\\n"
"""},
            hidden_tests={
                "test_hidden.py": """from main import read_numbers, write_report
import pytest

def test_negative_and_whitespace(tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("  -5  \\n\\n#x\\n7\\n", encoding="utf-8")
    assert read_numbers(path) == [-5, 7]

def test_missing_file_raises(tmp_path):
    with pytest.raises((FileNotFoundError, OSError)):
        read_numbers(tmp_path / "missing.txt")

def test_invalid_line_is_skipped(tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("1\\nabc\\n2\\n", encoding="utf-8")
    assert read_numbers(path) == [1, 2]

def test_write_empty_creates_file(tmp_path):
    path = tmp_path / "out.txt"
    assert write_report(path, []) == 0
    assert path.exists()

def test_write_overwrites(tmp_path):
    path = tmp_path / "out.txt"
    write_report(path, ["old"])
    write_report(path, ["new"])
    assert path.read_text(encoding="utf-8") == "new\\n"
"""},
            reference_solution="""from pathlib import Path


def read_numbers(path):
    numbers = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            try:
                numbers.append(int(text))
            except ValueError:
                continue
    return numbers


def write_report(path, rows):
    count = 0
    with Path(path).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(f"{row}\\n")
            count += 1
    return count
""",
            hints=(
                "Always open files with an explicit `encoding='utf-8'`.",
                "Strip each line before testing for blanks and comments.",
                "Do not catch OSError in `write_report` - let the caller decide.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `merge_reports(paths, output)` التي تقرأ عدة ملفات أعداد، تدمج محتوياتها،
تزيل التكرارات، ترتّب الناتج، وتكتبه في `output` سطراً لكل رقم. تُعيد عدد الأرقام المكتوبة.

تعامل مع الملفات المفقودة بتجاهلها مع تسجيلها في قائمة تُعيدها الدالة كقيمة ثانية.""",
            brief_en="""Write `merge_reports(paths, output)` reading several number files, merging their
contents, removing duplicates, sorting the result and writing one number per line to
`output`. It returns the count written.

Skip missing files but return their paths as a second value.""",
            independent=True,
            starter_code="""from pathlib import Path


def merge_reports(paths, output):
    # TODO: (count_written, missing_paths)
    pass
""",
            public_tests={"test_public.py": """from main import merge_reports

def test_merge(tmp_path):
    a = tmp_path / "a.txt"; a.write_text("3\\n1\\n", encoding="utf-8")
    b = tmp_path / "b.txt"; b.write_text("2\\n1\\n", encoding="utf-8")
    out = tmp_path / "out.txt"
    count, missing = merge_reports([a, b], out)
    assert count == 3
    assert out.read_text(encoding="utf-8") == "1\\n2\\n3\\n"
    assert missing == []
"""},
            hidden_tests={"test_hidden.py": """from main import merge_reports
from pathlib import Path

def test_missing_files_reported(tmp_path):
    real = tmp_path / "a.txt"; real.write_text("5\\n", encoding="utf-8")
    ghost = tmp_path / "ghost.txt"
    out = tmp_path / "out.txt"
    count, missing = merge_reports([real, ghost], out)
    assert count == 1
    assert [str(ghost)] == [str(p) for p in missing]

def test_comments_and_duplicates(tmp_path):
    a = tmp_path / "a.txt"; a.write_text("#note\\n4\\n4\\n", encoding="utf-8")
    out = tmp_path / "out.txt"
    count, _ = merge_reports([a], out)
    assert count == 1

def test_no_files(tmp_path):
    out = tmp_path / "out.txt"
    count, missing = merge_reports([], out)
    assert count == 0
    assert missing == []
    assert out.exists()
"""},
            reference_solution="""from pathlib import Path


def merge_reports(paths, output):
    numbers = set()
    missing = []
    for path in paths:
        candidate = Path(path)
        try:
            with candidate.open("r", encoding="utf-8") as handle:
                for line in handle:
                    text = line.strip()
                    if not text or text.startswith("#"):
                        continue
                    try:
                        numbers.add(int(text))
                    except ValueError:
                        continue
        except OSError:
            missing.append(candidate)
    ordered = sorted(numbers)
    with Path(output).open("w", encoding="utf-8") as handle:
        for number in ordered:
            handle.write(f"{number}\\n")
    return len(ordered), missing
""",
        ),
        transfer_ar="استخدم نفس النمط في Data Empire لاستيراد ملفات CSV اليومية وتنظيفها.",
        transfer_en="Reuse the same pattern in Data Empire to import and clean daily CSV files.",
        references=(
            ("Python tutorial - reading and writing files", "https://docs.python.org/3/tutorial/inputoutput.html"),
            ("Python docs - pathlib", "https://docs.python.org/3/library/pathlib.html"),
        ),
    ),
]
