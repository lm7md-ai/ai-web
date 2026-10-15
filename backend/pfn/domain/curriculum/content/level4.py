"""LEVEL 4 - Advanced Python: decorators, context managers, data model, concurrency."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l4.decorators",
        level=4,
        order_index=1,
        domain="advanced_python",
        title_ar="المزخرفات (Decorators)",
        title_en="Decorators",
        summary_ar="تعديل سلوك الدوال دون تغييرها: قياس، تحقق، وإعادة محاولة.",
        summary_en="Changing function behaviour without editing it: timing, validation, retries.",
        explanation_ar="""المزخرف دالة تستقبل دالة وتُعيد دالة. هذه هي الفكرة كاملة:

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

الصياغة `@decorator` فوق تعريف دالة هي سكر نحوي لـ `func = decorator(func)`.

قواعد أساسية:
- استخدم `functools.wraps` دائماً: يحفظ `__name__` و`__doc__` والبيانات الوصفية.
- `*args, **kwargs` تجعل المزخرف يعمل مع أي دالة.
- المزخرفات **تُنفَّذ عند الاستيراد**، لا عند الاستدعاء.
- المزخرف ذو المعاملات يحتاج ثلاث طبقات: `def retry(times):` → `def decorator(func):` → `def wrapper(...)`.

استخدمات واقعية: قياس الزمن، التسجيل، التحقق من المدخلات، التخزين المؤقت، وإعادة المحاولة.""",
        explanation_en="""A decorator is a function that takes a function and returns a function. That is the
whole idea:

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

Writing `@decorator` above a definition is sugar for `func = decorator(func)`.

Ground rules:
- always use `functools.wraps`: it preserves `__name__`, `__doc__` and metadata;
- `*args, **kwargs` makes the decorator work with any function;
- decorators run at **import time**, not at call time;
- a decorator that takes arguments needs three levels: `def retry(times):` ->
  `def decorator(func):` -> `def wrapper(...)`.

Real uses: timing, logging, input validation, caching and retries.""",
        skills=("adv.decorators", "adv.closures", "core.functions"),
        prerequisites=("l2.scope_closures",),
        example_code="""import time
from functools import wraps


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            print(f"{func.__name__} took {elapsed:.2f} ms")
    return wrapper


def retry(times, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
            return None
        return wrapper
    return decorator


@timed
def slow_sum(values):
    time.sleep(0.01)
    return sum(values)


attempts = {"count": 0}


@retry(3)
def flaky():
    attempts["count"] += 1
    if attempts["count"] < 3:
        raise ConnectionError("temporary failure")
    return "ok"


print(slow_sum(range(100)))
print(flaky(), "after", attempts["count"], "calls")
""",
        example_notes_ar="لاحظ أن `timed` يستخدم `finally` لقياس الزمن حتى عند حدوث خطأ.",
        example_notes_en="`timed` uses `finally` so the duration is measured even when the call fails.",
        experiment_code="""from functools import wraps

REGISTRY = {}


def register(name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        REGISTRY[name] = wrapper
        return wrapper
    return decorator


@register("double")
def double(x):
    return x * 2


@register("square")
def square(x):
    return x * x


print(REGISTRY["double"](4), REGISTRY["square"](4))
print("registered:", sorted(REGISTRY))
""",
        experiment_brief_ar="أضف مزخرفاً `validate_types` يتحقق من الأنواع باستخدام `__annotations__` ويرفع TypeError.",
        experiment_brief_en="Add a `validate_types` decorator that checks annotations and raises TypeError on mismatch.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `once(func)`: مزخرف ينفّذ الدالة مرة واحدة فقط ويُعيد نفس النتيجة بعدها.
2. `limit_calls(max_calls)`: مزخرف بمعامل يسمح بأول `max_calls` استدعاءً ويرفع
   `RuntimeError("call limit reached")` بعدها.
3. `logged(func)`: مزخرف يطبع `اسم_الدالة(وسائط) -> نتيجة` عند كل استدعاء.

استخدم `functools.wraps` في الثلاثة.""",
            brief_en="""Write:
1. `once(func)`: runs the function only the first time and replays the result afterwards.
2. `limit_calls(max_calls)`: a decorator factory allowing the first `max_calls` calls and
   raising `RuntimeError("call limit reached")` afterwards.
3. `logged(func)`: prints `name(args) -> result` on every call.

Use `functools.wraps` in all three.""",
            starter_code="""from functools import wraps


def once(func):
    # TODO
    pass


def limit_calls(max_calls):
    # TODO
    pass


def logged(func):
    # TODO
    pass
""",
            public_tests={
                "test_public.py": """from main import once

def test_once():
    calls = []

    @once
    def expensive():
        calls.append(1)
        return 7

    assert expensive() == 7
    assert expensive() == 7
    assert len(calls) == 1
"""},
            hidden_tests={
                "test_hidden.py": """from main import once, limit_calls, logged
import pytest

def test_once_keeps_name():
    @once
    def greet():
        return "hi"

    assert greet.__name__ == "greet"

def test_limit_calls_allows_first():
    @limit_calls(2)
    def value(x):
        return x

    assert value(1) == 1
    assert value(2) == 2

def test_limit_calls_raises_after():
    @limit_calls(1)
    def value(x):
        return x

    value(1)
    with pytest.raises(RuntimeError):
        value(2)

def test_limit_zero():
    @limit_calls(0)
    def value():
        return 1

    with pytest.raises(RuntimeError):
        value()

def test_logged_prints(capsys):
    @logged
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    out = capsys.readouterr().out
    assert "add" in out and "3" in out

def test_logged_passes_kwargs():
    @logged
    def greet(name="world"):
        return "hi " + name

    assert greet(name="sara") == "hi sara"
"""},
            reference_solution="""from functools import wraps


def once(func):
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "value" not in cache:
            cache["value"] = func(*args, **kwargs)
        return cache["value"]

    return wrapper


def limit_calls(max_calls):
    def decorator(func):
        used = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal used
            if used >= max_calls:
                raise RuntimeError("call limit reached")
            used += 1
            return func(*args, **kwargs)

        return wrapper

    return decorator


def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__}{args} -> {result}")
        return result

    return wrapper
""",
            hints=(
                "`nonlocal` lets the wrapper mutate the counter captured from the enclosing scope.",
                "Store the cached value in a dict so a legitimate `None` result is not recomputed.",
                "Log after calling, so you can print the real result.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب مزخرفاً `validate` يقبل وظيفة تحقق ويعيد `TypeError` واضحاً عند الفشل:

```python
@validate(lambda x: x > 0)
def sqrt_positive(x):
    return x ** 0.5
```

يجب أن:
- يفحص الوسائط الموضعية الأولى والوسائط بالاسم،
- يرفع `TypeError` برسالة تحتوي اسم الدالة،
- يحافظ على `__name__` و`__doc__`.""",
            brief_en="""Write a `validate` decorator factory taking a predicate and raising a clear `TypeError`
when it fails:

```python
@validate(lambda x: x > 0)
def sqrt_positive(x):
    return x ** 0.5
```

It must:
- check the first positional argument and keyword arguments,
- raise `TypeError` with the function name in the message,
- preserve `__name__` and `__doc__`.""",
            independent=True,
            starter_code="""from functools import wraps


def validate(predicate):
    # TODO
    pass
""",
            public_tests={"test_public.py": """from main import validate
import pytest

@validate(lambda x: x > 0)
def positive_root(x):
    \"\"\"Return the square root of a positive number.\"\"\"
    return x ** 0.5

def test_accepts_valid():
    assert positive_root(9) == 3.0

def test_rejects_invalid():
    with pytest.raises(TypeError):
        positive_root(-1)
"""},
            hidden_tests={"test_hidden.py": """from main import validate
import pytest

@validate(lambda value: isinstance(value, str) and value)
def shout(text):
    return text.upper()

def test_metadata_preserved():
    assert shout.__name__ == "shout"

def test_error_message_mentions_function():
    try:
        shout("")
    except TypeError as exc:
        assert "shout" in str(exc)
    else:
        raise AssertionError("expected TypeError")

def test_keyword_argument_checked():
    with pytest.raises(TypeError):
        shout(text="")

def test_valid_keyword():
    assert shout(text="hi") == "HI"

def test_other_arguments_pass_through():
    @validate(lambda a: a > 0)
    def multiply(a, b):
        return a * b

    assert multiply(2, 3) == 6
"""},
            reference_solution="""from functools import wraps


def validate(predicate):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            candidate = None
            found = False
            if args:
                candidate, found = args[0], True
            elif kwargs:
                first = next(iter(kwargs))
                candidate, found = kwargs[first], True
            if found and not predicate(candidate):
                raise TypeError(f"{func.__name__} rejected the argument {candidate!r}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
""",
        ),
        transfer_ar="استخدم المزخرفات في Agent Planet لتسجيل كل استدعاء أداة وقياس زمنه.",
        transfer_en="Use decorators in Agent Planet to log every tool call and measure its latency.",
        references=(
            ("Python docs - functools", "https://docs.python.org/3/library/functools.html"),
            ("Real Python - primer on decorators", "https://realpython.com/primer-on-python-decorators/"),
        ),
    ),
    CurriculumModule(
        id="l4.context_managers",
        level=4,
        order_index=2,
        domain="advanced_python",
        title_ar="مديرات السياق",
        title_en="Context managers",
        summary_ar="`with` يضمن التنظيف: ملفات، أقفال، قياس زمن، وتراجع عن تغييرات.",
        summary_en="`with` guarantees cleanup: files, locks, timing, and rolling back changes.",
        explanation_ar="""مدير السياق يضمن تنفيذ كود **التهيئة** و**التنظيف** حتى عند حدوث استثناء.

طريقتان لكتابته:

```python
# 1) class based
class Managed:
    def __enter__(self): ...
    def __exit__(self, exc_type, exc, tb): ...   # return True to swallow the exception

# 2) generator based (contextlib)
from contextlib import contextmanager

@contextmanager
def managed():
    setup()
    try:
        yield resource
    finally:
        teardown()
```

إذا أعاد `__exit__` قيمة حقيقية يُبتلع الاستثناء — افعل ذلك فقط إن كنت تقصد.
`contextlib.suppress` و`ExitStack` و`nullcontext` أدوات جاهزة تستحق المعرفة.""",
        explanation_en="""A context manager guarantees **setup** and **cleanup**, even when an exception is raised.

Two ways to write one:

```python
# 1) class based
class Managed:
    def __enter__(self): ...
    def __exit__(self, exc_type, exc, tb): ...   # return True to swallow the exception

# 2) generator based (contextlib)
from contextlib import contextmanager

@contextmanager
def managed():
    setup()
    try:
        yield resource
    finally:
        teardown()
```

If `__exit__` returns a truthy value the exception is swallowed - only do that when you
mean it. `contextlib.suppress`, `ExitStack` and `nullcontext` are worth knowing.""",
        skills=("adv.context_managers", "core.exceptions", "pro.logging"),
        prerequisites=("l4.decorators",),
        example_code="""import time
from contextlib import contextmanager


@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {(time.perf_counter() - start) * 1000:.2f} ms")


class temporary_value:
    \"\"\"Change an attribute, then put the old value back.\"\"\"

    def __init__(self, obj, name, value):
        self.obj, self.name, self.value = obj, name, value

    def __enter__(self):
        self.previous = getattr(self.obj, self.name)
        setattr(self.obj, self.name, self.value)
        return self.obj

    def __exit__(self, exc_type, exc, tb):
        setattr(self.obj, self.name, self.previous)
        return False


class Settings:
    level = 1


config = Settings()
with timer("work"), temporary_value(config, "level", 99):
    print("level inside:", config.level)
print("level after :", config.level)
""",
        example_notes_ar="`__exit__` أرجع `False` حتى لا تُخفي الأخطاء. غيّره إلى True وشاهد ما يحدث.",
        example_notes_en="`__exit__` returns `False` so errors stay visible. Change it to True and watch what happens.",
        experiment_code="""from contextlib import contextmanager, suppress
import os


@contextmanager
def working_directory(path):
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(previous)


print("before:", os.getcwd())
with working_directory("/tmp"):
    print("inside:", os.getcwd())
print("after :", os.getcwd())

with suppress(ZeroDivisionError):
    1 / 0
print("the ZeroDivisionError was suppressed on purpose")
""",
        experiment_brief_ar="اكتب مدير سياق يلتقط الاستثناءات ويسجلها ثم يعيد رفعها (re-raise) مع سياق إضافي.",
        experiment_brief_en="Write a context manager that catches exceptions, logs them and re-raises with extra context.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `timer()` مدير سياق (بـ `@contextmanager`) يُنتج قاموساً `{"ms": ..}` يملأه عند الخروج.
2. `collect_errors()` مدير سياق يُنتج قائمة، ويضيف إليها أي استثناء يحدث داخل السياق
   ثم **يمنع** انتشاره (يُبتلع).
3. `transaction(store)` مدير سياق يعمل على قاموس: ينسخه عند الدخول، ويعيد النسخة الأصلية
   إذا حدث استثناء، ويُبقي التغييرات إذا نجح.""",
            brief_en="""Write:
1. `timer()` - a context manager (with `@contextmanager`) yielding a dict `{"ms": ..}` that it
   fills on exit.
2. `collect_errors()` - yielding a list, appending any exception raised inside the block and
   **suppressing** it.
3. `transaction(store)` - operating on a dict: snapshot on entry, restore the snapshot if an
   exception escapes, keep the changes otherwise.""",
            starter_code="""from contextlib import contextmanager


@contextmanager
def timer():
    # TODO: yield {"ms": 0.0} and fill it on exit
    pass


@contextmanager
def collect_errors():
    # TODO: yield a list, collect and suppress exceptions
    pass


@contextmanager
def transaction(store):
    # TODO: snapshot / restore on failure
    pass
""",
            public_tests={
                "test_public.py": """from main import timer

def test_timer():
    with timer() as stats:
        total = sum(range(1000))
    assert stats["ms"] >= 0.0
"""},
            hidden_tests={
                "test_hidden.py": """from main import timer, collect_errors, transaction

def test_timer_measures():
    with timer() as stats:
        for _ in range(20000):
            pass
    assert isinstance(stats["ms"], float)

def test_collect_errors_suppresses():
    with collect_errors() as errors:
        raise ValueError("boom")
    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)

def test_collect_errors_empty():
    with collect_errors() as errors:
        pass
    assert errors == []

def test_transaction_commits():
    store = {"a": 1}
    with transaction(store) as working:
        working["a"] = 2
    assert store["a"] == 2

def test_transaction_rolls_back():
    store = {"a": 1}
    try:
        with transaction(store) as working:
            working["a"] = 99
            raise RuntimeError("failure")
    except RuntimeError:
        pass
    assert store["a"] == 1

def test_transaction_nested_keys():
    store = {"a": {"b": 1}}
    with transaction(store) as working:
        working["a"]["b"] = 5
    assert store["a"]["b"] == 5
"""},
            reference_solution="""import copy
import time
from contextlib import contextmanager


@contextmanager
def timer():
    stats = {"ms": 0.0}
    start = time.perf_counter()
    try:
        yield stats
    finally:
        stats["ms"] = (time.perf_counter() - start) * 1000


@contextmanager
def collect_errors():
    errors = []
    try:
        yield errors
    except Exception as exc:  # noqa: BLE001 - collecting is the point here
        errors.append(exc)


@contextmanager
def transaction(store):
    snapshot = copy.deepcopy(store)
    try:
        yield store
    except Exception:
        store.clear()
        store.update(snapshot)
        raise
""",
            hints=(
                "A `finally` block runs even when the body raises - put the elapsed time there.",
                "Catching `Exception` and not re-raising is how `collect_errors` suppresses.",
                "For rollback, snapshot before yielding and restore in `except`, then re-raise.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب صنف `Resource` يحاكي مورداً خارجياً (اتصال/ملف):
- `open()` و`close()` مع حالة `is_open`،
- `__enter__` يفتح ويعيد الكائن،
- `__exit__` يغلق دائماً،
- `write(data)` يرفع `RuntimeError("resource is closed")` إن كان مغلقاً،
- عدّاد صنفي `Resource.opened_now` يتتبع عدد الموارد المفتوحة حالياً.""",
            brief_en="""Write a `Resource` class simulating an external resource (a connection or file):
- `open()` and `close()` with an `is_open` state,
- `__enter__` opens and returns the object,
- `__exit__` always closes,
- `write(data)` raises `RuntimeError("resource is closed")` when closed,
- a class-level counter `Resource.opened_now` tracking how many resources are open.""",
            independent=True,
            starter_code="""class Resource:
    opened_now = 0

    def __init__(self, name):
        pass
""",
            public_tests={"test_public.py": """from main import Resource

def test_opens_and_closes():
    with Resource("db") as resource:
        assert resource.is_open is True
    assert resource.is_open is False
"""},
            hidden_tests={"test_hidden.py": """from main import Resource
import pytest

def test_write_when_closed():
    resource = Resource("db")
    with pytest.raises(RuntimeError):
        resource.write("data")

def test_write_when_open():
    with Resource("db") as resource:
        assert resource.write("data") == "data"

def test_counter_increases_and_decreases():
    before = Resource.opened_now
    with Resource("a"):
        assert Resource.opened_now == before + 1
    assert Resource.opened_now == before

def test_cloSES_even_on_exception():
    before = Resource.opened_now
    with pytest.raises(ValueError):
        with Resource("b"):
            raise ValueError("boom")
    assert Resource.opened_now == before

def test_double_open_is_safe():
    resource = Resource("c")
    resource.open()
    resource.open()
    assert Resource.opened_now == 1
    resource.close()
"""},
            reference_solution="""class Resource:
    opened_now = 0

    def __init__(self, name):
        self.name = name
        self.is_open = False

    def open(self):
        if not self.is_open:
            self.is_open = True
            Resource.opened_now += 1

    def close(self):
        if self.is_open:
            self.is_open = False
            Resource.opened_now -= 1

    def write(self, data):
        if not self.is_open:
            raise RuntimeError("resource is closed")
        return data

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
""",
        ),
        transfer_ar="استخدم `transaction` في Project Rescue لتجربة تغيير على بيانات يمكن التراجع عنه.",
        transfer_en="Use `transaction` in Project Rescue to try a reversible change on data.",
        references=(
            ("Python docs - contextlib", "https://docs.python.org/3/library/contextlib.html"),
            ("Python docs - with statement", "https://docs.python.org/3/reference/compound_stmts.html#the-with-statement"),
        ),
    ),
    CurriculumModule(
        id="l4.data_model",
        level=4,
        order_index=3,
        domain="advanced_python",
        title_ar="نموذج بيانات بايثون",
        title_en="The Python data model",
        summary_ar="اجعل كائناتك تتصرف كالأنواع المدمجة عبر البروتوكولات الخاصة.",
        summary_en="Make your objects behave like built-ins through the dunder protocols.",
        explanation_ar="""نموذج بيانات بايثون مجموعة **بروتوكولات**: إذا نفّذ كائنك الطرق المناسبة
يعمل مع أدوات اللغة مباشرة.

أهمها:
- `__len__` → `len(obj)`، و`__bool__` → القيمة الحقيقية،
- `__iter__` / `__next__` → التكرار،
- `__getitem__` → الفهرسة والتقطيع،
- `__eq__` و`__hash__` → المقارنة واستخدامه مفتاح قاموس (إن كان ثابتاً)،
- `__repr__` و`__str__` → التمثيل،
- `__add__`, `__mul__`, `__lt__` → العوامل،
- `__enter__` / `__exit__` → `with`.

**الواصفات (descriptors)** هي الآلية التي تعمل بها `property` وطرق الأصناف:
كائن يعرّف `__get__` (و`__set__` للتحكم في الكتابة) ويُستخدم كخاصية صنف.
هذا يسمح بالتحقق من القيم وإعادة استخدامه عبر أصناف كثيرة.""",
        explanation_en="""The Python data model is a set of **protocols**: implement the right methods and your
object works with the language itself.

The important ones:
- `__len__` -> `len(obj)`, and `__bool__` -> truthiness,
- `__iter__` / `__next__` -> iteration,
- `__getitem__` -> indexing and slicing,
- `__eq__` and `__hash__` -> comparison and use as a dict key (when immutable),
- `__repr__` and `__str__` -> representation,
- `__add__`, `__mul__`, `__lt__` -> operators,
- `__enter__` / `__exit__` -> `with`.

**Descriptors** are the mechanism behind `property` and methods: an object defining
`__get__` (and `__set__` to control assignment) used as a class attribute. They let you
validate values once and reuse that logic across many classes.""",
        skills=("adv.data_model", "adv.descriptors", "core.oop_basic"),
        prerequisites=("l2.oop",),
        example_code="""import math


class Vector:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __eq__(self, other):
        return isinstance(other, Vector) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


v = Vector(3, 4)
print(v + Vector(1, 2), v * 2, abs(v), list(v), v == Vector(3, 4))
print({v: "origin-ish"})
""",
        example_notes_ar="`__slots__` يمنع إنشاء `__dict__` لكل كائن: ذاكرة أقل ووصول أسرع.",
        example_notes_en="`__slots__` avoids a per-object `__dict__`: less memory and faster attribute access.",
        experiment_code="""class Range:
    \"\"\"Reusable validation descriptor.\"\"\"

    def __init__(self, low, high):
        self.low, self.high = low, high

    def __set_name__(self, owner, name):
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        if not self.low <= value <= self.high:
            raise ValueError(f"{value} outside [{self.low}, {self.high}]")
        setattr(obj, self.private, value)


class Sensor:
    temperature = Range(-50, 150)
    humidity = Range(0, 100)

    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity


probe = Sensor(25, 40)
print(probe.temperature, probe.humidity)
try:
    probe.humidity = 150
except ValueError as exc:
    print("ValueError:", exc)
""",
        experiment_brief_ar="أضف واصفاً `NonEmpty` للنصوص يمنع السلاسل الفارغة، واستخدمه في صنف `User`.",
        experiment_brief_en="Add a `NonEmpty` descriptor for strings that rejects empty values, and use it in a `User` class.",
        task=TaskSpec(
            brief_ar="""اكتب صنف `Matrix` يمثّل مصفوفة ثنائية الأبعاد بقائمة من القوائم:
- `__getitem__` يدعم الفهرسة `m[0][1]` والتقطيع `m[0]`،
- `__setitem__` للتعديل،
- `__eq__` للمقارنة،
- `__iter__` يمرّر على الصفوف،
- `__len__` عدد الصفوف، وخاصية `shape` تُعيد `(صفوف، أعمدة)`،
- `__repr__` واضح.""",
            brief_en="""Write a `Matrix` class wrapping a list of lists:
- `__getitem__` supports `m[0][1]` and slicing `m[0]`,
- `__setitem__` for assignment,
- `__eq__` for comparison,
- `__iter__` over rows,
- `__len__` is the row count and a `shape` property returns `(rows, cols)`,
- a clear `__repr__`.""",
            starter_code="""class Matrix:
    def __init__(self, rows):
        pass
""",
            public_tests={"test_public.py": """from main import Matrix

def test_indexing():
    m = Matrix([[1, 2], [3, 4]])
    assert m[0][1] == 2
    assert m.shape == (2, 2)
"""},
            hidden_tests={"test_hidden.py": """from main import Matrix

def test_setitem():
    m = Matrix([[1, 2], [3, 4]])
    m[1][0] = 9
    assert m[1][0] == 9

def test_iteration_and_len():
    m = Matrix([[1, 2], [3, 4], [5, 6]])
    assert len(m) == 3
    assert [row for row in m] == [[1, 2], [3, 4], [5, 6]]

def test_equality_and_inequality():
    assert Matrix([[1]]) == Matrix([[1]])
    assert Matrix([[1]]) != Matrix([[2]])
    assert Matrix([[1]]) != [[1]]

def test_shape_rectangular():
    assert Matrix([[1, 2, 3]]).shape == (1, 3)

def test_bool_empty():
    assert bool(Matrix([])) is False
    assert bool(Matrix([[0]])) is True

def test_repr_shows_dimensions():
    text = repr(Matrix([[1, 2], [3, 4]]))
    assert "2" in text
"""},
            reference_solution="""class Matrix:
    def __init__(self, rows):
        self.rows = [list(row) for row in rows]

    @property
    def shape(self):
        if not self.rows:
            return (0, 0)
        return (len(self.rows), len(self.rows[0]))

    def __getitem__(self, index):
        return self.rows[index]

    def __setitem__(self, index, value):
        self.rows[index] = value

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def __bool__(self):
        return bool(self.rows)

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        return self.rows == other.rows

    def __repr__(self):
        rows, columns = self.shape
        return f"Matrix({rows}x{columns})"
""",
            hints=(
                "Copy the rows in `__init__` so the caller cannot mutate your data by accident.",
                "Returning `NotImplemented` from `__eq__` lets Python fall back to identity comparison.",
                "`shape` must handle the empty matrix without indexing row zero.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب واصفاً `Bounded(low, high)` يتحقق من القيم عند الإسناد، واصفاً `Typed(expected_type)`
يتحقق من النوع، ثم صنف `RobotConfig` يستخدمهما:

```python
class RobotConfig:
    speed = Bounded(0, 10)
    name = Typed(str)
```

يجب رفع `ValueError` للقيم خارج النطاق و`TypeError` للنوع الخاطئ، مع رسالة واضحة.""",
            brief_en="""Write a `Bounded(low, high)` descriptor validating values on assignment and a
`Typed(expected_type)` descriptor checking types, then a `RobotConfig` class using them:

```python
class RobotConfig:
    speed = Bounded(0, 10)
    name = Typed(str)
```

Raise `ValueError` for out-of-range values and `TypeError` for the wrong type, with clear messages.""",
            independent=True,
            starter_code="""class Bounded:
    def __init__(self, low, high):
        pass


class Typed:
    def __init__(self, expected_type):
        pass


class RobotConfig:
    speed = Bounded(0, 10)
    name = Typed(str)
""",
            public_tests={"test_public.py": """from main import RobotConfig

def test_valid():
    config = RobotConfig()
    config.speed = 5
    config.name = "r1"
    assert (config.speed, config.name) == (5, "r1")
"""},
            hidden_tests={"test_hidden.py": """from main import Bounded, Typed, RobotConfig
import pytest

def test_bounded_rejects_high():
    config = RobotConfig()
    with pytest.raises(ValueError):
        config.speed = 11

def test_bounded_rejects_low():
    config = RobotConfig()
    with pytest.raises(ValueError):
        config.speed = -1

def test_typed_rejects_type():
    config = RobotConfig()
    with pytest.raises(TypeError):
        config.name = 42

def test_descriptors_are_reusable():
    class Other:
        level = Bounded(0, 3)

    other = Other()
    other.level = 2
    assert other.level == 2
    with pytest.raises(ValueError):
        other.level = 9

def test_instances_are_independent():
    a, b = RobotConfig(), RobotConfig()
    a.speed = 1
    b.speed = 7
    assert (a.speed, b.speed) == (1, 7)

def test_access_on_class_returns_descriptor():
    assert isinstance(RobotConfig.speed, Bounded)
"""},
            reference_solution="""class Bounded:
    def __init__(self, low, high):
        self.low, self.high = low, high

    def __set_name__(self, owner, name):
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private, None)

    def __set__(self, obj, value):
        if not self.low <= value <= self.high:
            raise ValueError(f"{value} is outside [{self.low}, {self.high}]")
        setattr(obj, self.private, value)


class Typed:
    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __set_name__(self, owner, name):
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private, None)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"expected {self.expected_type.__name__}, got {type(value).__name__}")
        setattr(obj, self.private, value)


class RobotConfig:
    speed = Bounded(0, 10)
    name = Typed(str)
""",
        ),
        transfer_ar="استخدم الواصفات في CareerVerse للتحقق من إعدادات الخدمة عند الإقلاع.",
        transfer_en="Use descriptors in CareerVerse to validate service configuration at startup.",
        references=(
            ("Python docs - data model", "https://docs.python.org/3/reference/datamodel.html"),
            ("Python howto - descriptors", "https://docs.python.org/3/howto/descriptor.html"),
        ),
    ),
    CurriculumModule(
        id="l4.concurrency",
        level=4,
        order_index=4,
        domain="advanced_python",
        title_ar="التزامن: خيوط أم async",
        title_en="Concurrency: threads or async",
        summary_ar="اختيار النموذج الصحيح بناءً على نوع العمل، وقياس الفرق فعلياً.",
        summary_en="Choosing the right model for the workload, and measuring the difference.",
        explanation_ar="""قاعدة التصفية الأولى:

- عمل مرتبط بـ **CPU** (حساب، تحليل أرقام): استخدم **عمليات** (`multiprocessing`) لأن
  الـ GIL يمنع تشغيل بايت كود بايثون على أكثر من خيط في نفس اللحظة.
- عمل مرتبط بـ **I/O** (شبكة، ملفات، sleep): استخدم **خيوط** أو **asyncio**.

`asyncio` يتفوق عندما يكون هناك عدد كبير من العمليات المنتظرة: حلقة حدث واحدة
تشغل مهاماً (`coroutines`) تتخلى عن التحكم عند `await`.

أخطاء شائعة:
- استدعاء دالة حاجبة (مثل `time.sleep` أو `requests.get`) داخل `async def` — يوقف الحلقة كلها.
- مشاركة حالة قابلة للتغيير بين خيوط دون قفل (`threading.Lock`).
- افتراض أن async أسرع دائماً: التزامن يقلل **زمن الانتظار** لا زمن الحساب.""",
        explanation_en="""The first filter is simple:

- **CPU-bound** work (computation, number crunching): use **processes**
  (`multiprocessing`), because the GIL stops Python bytecode from running on more than
  one thread at a time.
- **I/O-bound** work (network, files, sleeps): use **threads** or **asyncio**.

`asyncio` shines when there are many waiting operations: one event loop drives coroutines
that yield control at every `await`.

Common mistakes:
- calling a blocking function (`time.sleep`, `requests.get`) inside `async def` - it stalls the whole loop;
- sharing mutable state between threads without a `threading.Lock`;
- assuming async is always faster: concurrency cuts **waiting time**, not compute time.""",
        skills=("adv.concurrency", "adv.asyncio", "adv.threading"),
        prerequisites=("l4.context_managers",),
        example_code="""import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


def blocking_task(seconds):
    time.sleep(seconds)
    return f"slept {seconds}s"


def measure_threads(tasks):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
        results = list(pool.map(blocking_task, tasks))
    return results, time.perf_counter() - start


async def async_task(seconds):
    await asyncio.sleep(seconds)
    return f"slept {seconds}s"


async def measure_async(tasks):
    start = time.perf_counter()
    results = await asyncio.gather(*(async_task(t) for t in tasks))
    return results, time.perf_counter() - start


def measure_sequential(tasks):
    start = time.perf_counter()
    results = [blocking_task(t) for t in tasks]
    return results, time.perf_counter() - start


TASKS = [0.05, 0.05, 0.05, 0.05]
for label, result in [
    ("sequential", measure_sequential(TASKS)[1]),
    ("threads", measure_threads(TASKS)[1]),
    ("asyncio", asyncio.run(measure_async(TASKS))[1]),
]:
    print(f"{label:11s}: {result * 1000:6.1f} ms")
""",
        example_notes_ar="العمل هنا انتظار (sleep) لذلك الخيوط وasyncio يتفوقان على التنفيذ المتسلسل.",
        example_notes_en="The work here is waiting, so threads and asyncio beat the sequential run.",
        experiment_code="""import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def cpu_task(n):
    return sum(i * i for i in range(n))


NUMBERS = [400000] * 4

start = time.perf_counter()
sequential = [cpu_task(n) for n in NUMBERS]
print(f"sequential : {(time.perf_counter() - start) * 1000:.1f} ms")

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(cpu_task, NUMBERS))
print(f"4 threads  : {(time.perf_counter() - start) * 1000:.1f} ms  (GIL limited)")

start = time.perf_counter()
with ProcessPoolExecutor(max_workers=4) as pool:
    list(pool.map(cpu_task, NUMBERS))
print(f"4 processes: {(time.perf_counter() - start) * 1000:.1f} ms")
""",
        experiment_brief_ar="شغّل عدة مرات وسجّل الأرقام. اكتب استنتاجاً: متى تختار العمليات ومتى تختار الخيوط؟",
        experiment_brief_en="Run it several times and note the numbers. Conclude: when would you pick processes and when threads?",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `run_with_timeout(func, args=(), timeout=1.0, default=None)` تشغّل الدالة في خيط،
   وتُعيد `default` إذا تجاوزت `timeout` ثانية.
2. `gather_results(jobs)` حيث `jobs` قاموس `{"name": callable}`، فتُشغّلها كلها في
   `ThreadPoolExecutor` وتُعيد قاموس النتائج بنفس المفاتيح.""",
            brief_en="""Write:
1. `run_with_timeout(func, args=(), timeout=1.0, default=None)` running the function in a thread
   and returning `default` when it exceeds `timeout` seconds.
2. `gather_results(jobs)` where `jobs` is a `{"name": callable}` dict, running them all in a
   `ThreadPoolExecutor` and returning a dict of results with the same keys.""",
            starter_code="""from concurrent.futures import ThreadPoolExecutor


def run_with_timeout(func, args=(), timeout=1.0, default=None):
    # TODO
    pass


def gather_results(jobs):
    # TODO
    pass
""",
            public_tests={
                "test_public.py": """from main import gather_results

def test_gather():
    results = gather_results({"a": lambda: 1, "b": lambda: 2})
    assert results == {"a": 1, "b": 2}
"""},
            hidden_tests={
                "test_hidden.py": """from main import run_with_timeout, gather_results
import time

def test_fast_call_returns_value():
    assert run_with_timeout(lambda x: x * 2, args=(21,), timeout=2.0) == 42

def test_slow_call_returns_default():
    def slow():
        time.sleep(3)
        return "never"

    assert run_with_timeout(slow, timeout=0.1, default="timeout") == "timeout"

def test_args_and_kwargs_free():
    assert run_with_timeout(sum, args=([1, 2, 3],), timeout=2.0) == 6

def test_gather_empty():
    assert gather_results({}) == {}

def test_gather_preserves_keys_and_errors():
    def failing():
        raise ValueError("x")

    results = gather_results({"ok": lambda: 5})
    assert results == {"ok": 5}
    try:
        gather_results({"bad": failing})
    except ValueError:
        pass
    else:
        raise AssertionError("exceptions should propagate")
"""},
            reference_solution="""from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout


def run_with_timeout(func, args=(), timeout=1.0, default=None):
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(func, *args)
        try:
            return future.result(timeout=timeout)
        except FutureTimeout:
            future.cancel()
            return default


def gather_results(jobs):
    results = {}
    with ThreadPoolExecutor(max_workers=max(1, len(jobs))) as pool:
        futures = {name: pool.submit(job) for name, job in jobs.items()}
        for name, future in futures.items():
            results[name] = future.result()
    return results
""",
            hints=(
                "`future.result(timeout=...)` raises `concurrent.futures.TimeoutError`, not the built-in one.",
                "A thread cannot be killed mid-run: cancelling only works before it starts.",
                "Submit all jobs first, then collect - otherwise you serialise them.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب برنامجاً غير متزامن:
1. `async def fetch(name, delay)` تنتظر `delay` ثانية ثم تُعيد `{"name": name, "ok": True}`.
2. `async def fetch_all(jobs)` تُشغّل كل المهام معاً بـ `asyncio.gather` وتُعيد القائمة.
3. `async def with_deadline(coro, timeout, default=None)` تُلغي المهمة عند تجاوز المهلة
   وتُعيد `default` (استخدم `asyncio.wait_for` و`asyncio.TimeoutError`)."""
            ,
            brief_en="""Write an asynchronous programme:
1. `async def fetch(name, delay)` waits `delay` seconds then returns `{"name": name, "ok": True}`.
2. `async def fetch_all(jobs)` runs every task together with `asyncio.gather` and returns the list.
3. `async def with_deadline(coro, timeout, default=None)` cancels the task when the deadline
   passes and returns `default` (use `asyncio.wait_for` and `asyncio.TimeoutError`).""",
            independent=True,
            starter_code="""import asyncio


async def fetch(name, delay):
    pass


async def fetch_all(jobs):
    pass


async def with_deadline(coro, timeout, default=None):
    pass
""",
            public_tests={"test_public.py": """import asyncio
from main import fetch_all

def test_fetch_all():
    jobs = [("a", 0.01), ("b", 0.01)]
    results = asyncio.run(fetch_all(jobs))
    assert [r["name"] for r in results] == ["a", "b"]
"""},
            hidden_tests={"test_hidden.py": """import asyncio, time
from main import fetch, fetch_all, with_deadline

def test_fetch_payload():
    assert asyncio.run(fetch("a", 0.01)) == {"name": "a", "ok": True}

def test_concurrent_not_sequential():
    jobs = [("a", 0.2), ("b", 0.2), ("c", 0.2)]
    start = time.perf_counter()
    asyncio.run(fetch_all(jobs))
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5, f"tasks did not run concurrently ({elapsed:.2f}s)"

def test_deadline_returns_default():
    async def slow():
        await asyncio.sleep(2)
        return "late"

    result = asyncio.run(with_deadline(slow(), 0.1, default="timeout"))
    assert result == "timeout"

def test_deadline_keeps_fast_results():
    assert asyncio.run(with_deadline(fetch("x", 0.01), 1.0, default=None)) == {"name": "x", "ok": True}

def test_fetch_all_empty():
    assert asyncio.run(fetch_all([])) == []
"""},
            reference_solution="""import asyncio


async def fetch(name, delay):
    await asyncio.sleep(delay)
    return {"name": name, "ok": True}


async def fetch_all(jobs):
    tasks = [fetch(name, delay) for name, delay in jobs]
    return list(await asyncio.gather(*tasks))


async def with_deadline(coro, timeout, default=None):
    try:
        return await asyncio.wait_for(coro, timeout)
    except (asyncio.TimeoutError, TimeoutError):
        return default
""",
        ),
        transfer_ar="استخدم async في Agent Planet لتنفيذ عدة أدوات خارجية بالتوازي.",
        transfer_en="Use async in Agent Planet to call several external tools in parallel.",
        references=(
            ("Python docs - asyncio", "https://docs.python.org/3/library/asyncio.html"),
            ("Python docs - concurrent.futures", "https://docs.python.org/3/library/concurrent.futures.html"),
        ),
    ),
]
