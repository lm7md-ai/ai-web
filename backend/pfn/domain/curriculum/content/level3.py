"""LEVEL 3 - Professional Python: environments, typing, testing, debugging."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l3.environments",
        level=3,
        order_index=1,
        domain="professional",
        title_ar="البيئات وإدارة الحزم",
        title_en="Environments and packaging",
        summary_ar="عزل التبعيات، تثبيتها، ووصف المشروع في pyproject.toml.",
        summary_en="Isolating dependencies, pinning them, and describing the project in pyproject.toml.",
        explanation_ar="""البيئة الافتراضية مجلد يحتوي نسخة من المفسّر وحزمه، بحيث لا تتعارض مشاريعك.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

اكتشف برمجياً ما إذا كنت داخل بيئة افتراضية:
`sys.prefix != sys.base_prefix`.

`pyproject.toml` هو文件 الوصف الحديث للمشروع (PEP 621): اسم، إصدار، تبعيات، وإعدادات الأدوات.
اعرف إصدار حزمة مثبّتة بـ `importlib.metadata.version("numpy")`.

قواعد النضج المهني:
- ثبّت الإصدارات في ملف قفل (`requirements.txt` محدّد أو `uv.lock`).
- لا تضع أسراراً في المستودع.
- سجّل الحد الأدنى من إصدار بايثون (`requires-python`).""",
        explanation_en="""A virtual environment is a folder holding its own interpreter and packages, so your
projects never fight over dependencies.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

Detect programmatically whether you are inside one:
`sys.prefix != sys.base_prefix`.

`pyproject.toml` is the modern project description (PEP 621): name, version, dependencies
and tool configuration. Query an installed version with
`importlib.metadata.version("numpy")`.

Professional habits:
- pin versions in a lock file (a pinned `requirements.txt` or `uv.lock`);
- never commit secrets;
- declare the minimum Python version (`requires-python`).""",
        skills=("pro.venv", "pro.packaging", "pro.pyproject"),
        prerequisites=("l2.modules_packages",),
        example_code="""import sys
import importlib.metadata as metadata

print("executable :", sys.executable)
print("in a venv  :", sys.prefix != sys.base_prefix)
print("python     :", sys.version.split()[0])

for package in ("numpy", "pandas", "fastapi", "definitely-not-installed"):
    try:
        print(f"{package:26s}", metadata.version(package))
    except metadata.PackageNotFoundError:
        print(f"{package:26s} not installed")
""",
        example_notes_ar="`importlib.metadata` يقرأ البيانات من الحزم المثبّتة فعلياً — لا يقترح شيئاً.",
        example_notes_en="`importlib.metadata` reads what is really installed - it never guesses.",
        experiment_code="""import tomllib

sample = '''
[project]
name = "warehouse"
version = "0.3.1"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.7",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = ["pytest", "ruff"]

[tool.ruff]
line-length = 110
'''

data = tomllib.loads(sample)
project = data["project"]
print("name:", project["name"], "| version:", project["version"])
print("dependencies:", project["dependencies"])
print("dev extras:", project.get("optional-dependencies", {}).get("dev"))
print("ruff line length:", data["tool"]["ruff"]["line-length"])
""",
        experiment_brief_ar="أضف قسماً `[project.scripts]` واقرأه. ثم اكتب دالة تُعيد أسماء كل التبعيات بدون قيود الإصدار.",
        experiment_brief_en="Add a `[project.scripts]` section and read it. Then write a function returning dependency names without version constraints.",
        task=TaskSpec(
            brief_ar="""اكتب `read_project(text)` التي تحلّل نص `pyproject.toml` باستخدام `tomllib` وتُعيد قاموساً:

- `"name"`: اسم المشروع (أو `"unknown"` إن غاب)،
- `"version"`: الإصدار (أو `"0.0.0"` إن غاب)،
- `"requires_python"`: القيد (أو `None`)،
- `"dependencies"`: قائمة أسماء الحزم **بدون** قيود الإصدار،
- `"extras"`: قاموس يربط اسم المجموعة الاختيارية بقائمة أسماء حزمها.""",
            brief_en="""Write `read_project(text)` parsing a `pyproject.toml` document with `tomllib` and returning:

- `"name"`: the project name (or `"unknown"` when absent),
- `"version"`: the version (or `"0.0.0"`),
- `"requires_python"`: the constraint (or `None`),
- `"dependencies"`: package names **without** version constraints,
- `"extras"`: a dict mapping each optional group to its package names.""",
            starter_code="""import tomllib


def read_project(text):
    # TODO: parse and normalise
    pass
""",
            public_tests={
                "test_public.py": """from main import read_project

SAMPLE = '''
[project]
name = "warehouse"
version = "0.3.1"
dependencies = ["pydantic>=2.7", "sqlalchemy>=2.0"]
'''

def test_basic():
    result = read_project(SAMPLE)
    assert result["name"] == "warehouse"
    assert result["version"] == "0.3.1"
    assert result["dependencies"] == ["pydantic", "sqlalchemy"]
"""},
            hidden_tests={
                "test_hidden.py": """from main import read_project

def test_defaults_when_missing():
    result = read_project("[tool.ruff]\\nline-length = 100\\n")
    assert result["name"] == "unknown"
    assert result["version"] == "0.0.0"
    assert result["dependencies"] == []
    assert result["requires_python"] is None

def test_requires_python_and_extras():
    sample = '''
[project]
name = "x"
version = "1.0"
requires-python = ">=3.11"
dependencies = ["numpy==1.26.0"]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff"]
docs = ["mkdocs"]
'''
    result = read_project(sample)
    assert result["requires_python"] == ">=3.11"
    assert result["dependencies"] == ["numpy"]
    assert result["extras"]["dev"] == ["pytest", "ruff"]
    assert result["extras"]["docs"] == ["mkdocs"]

def test_constraints_stripped():
    result = read_project('[project]\\nname="a"\\nversion="1"\\ndependencies=["pkg >= 1.0,<2", "other"]\\n')
    assert result["dependencies"] == ["pkg", "other"]

def test_invalid_toml_raises():
    import tomllib, pytest
    with pytest.raises(tomllib.TOMLDecodeError):
        read_project("this is not toml = = =")
"""},
            reference_solution="""import tomllib


def _strip_constraint(spec):
    for separator in ("=", "<", ">", "!", "~", " ", "["):
        if separator in spec:
            spec = spec.split(separator)[0]
    return spec.strip()


def read_project(text):
    data = tomllib.loads(text)
    project = data.get("project", {})
    dependencies = [_strip_constraint(item) for item in project.get("dependencies", [])]
    extras = {
        group: [_strip_constraint(item) for item in packages]
        for group, packages in project.get("optional-dependencies", {}).items()
    }
    return {
        "name": project.get("name", "unknown"),
        "version": str(project.get("version", "0.0.0")),
        "requires_python": project.get("requires-python"),
        "dependencies": dependencies,
        "extras": extras,
    }
""",
            hints=(
                "`tomllib.loads` raises `TOMLDecodeError` for invalid input - let it propagate.",
                "Strip everything from the first constraint character: `>=`, `<`, `==`, `~=`, `!=`.",
                "Optional groups live under `project.optional-dependencies`, not `project`.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `audit_dependencies(dependencies)` حيث `dependencies` قائمة سلاسل مثل
`["numpy>=1.26", "pandas", "numpy<2"]`. تُعيد تقريراً:

- `"unpinned"`: الحزم دون قيد إصدار،
- `"duplicates"`: الحزم المكرّرة،
- `"conflicts"`: الحزم ذات القيود المتعارضة (نفس الحزمة مع قيد `>` أو `<` مختلف)،
- `"clean"`: `True` عندما لا توجد أي مشكلة.""",
            brief_en="""Write `audit_dependencies(dependencies)` where `dependencies` is a list of strings such as
`["numpy>=1.26", "pandas", "numpy<2"]`, returning a report with:

- `"unpinned"`: packages with no version constraint,
- `"duplicates"`: packages listed more than once,
- `"conflicts"`: packages whose constraints cannot all hold,
- `"clean"`: `True` when there is no problem at all.""",
            independent=True,
            starter_code="""def audit_dependencies(dependencies):
    # TODO: unpinned, duplicates, conflicts, clean
    pass
""",
            public_tests={"test_public.py": """from main import audit_dependencies

def test_unpinned():
    report = audit_dependencies(["pandas"])
    assert report["unpinned"] == ["pandas"]
    assert report["clean"] is False
"""},
            hidden_tests={"test_hidden.py": """from main import audit_dependencies

def test_clean_project():
    report = audit_dependencies(["numpy>=1.26", "pandas==2.1"])
    assert report["clean"] is True
    assert report["unpinned"] == []
    assert report["duplicates"] == []
    assert report["conflicts"] == []

def test_duplicates_detected():
    report = audit_dependencies(["numpy>=1.26", "numpy"])
    assert report["duplicates"] == ["numpy"]

def test_conflict_detected():
    report = audit_dependencies(["numpy>=2.0", "numpy<1.26"])
    assert "numpy" in report["conflicts"]

def test_empty():
    report = audit_dependencies([])
    assert report["clean"] is True

def test_ordering_stable():
    report = audit_dependencies(["b", "a"])
    assert report["unpinned"] == ["b", "a"]
"""},
            reference_solution="""import re
from collections import defaultdict

_PATTERN = re.compile(r"^([A-Za-z0-9._-]+)\\s*(.*)$")


def audit_dependencies(dependencies):
    constraints = defaultdict(list)
    order = []
    unpinned = []
    seen = defaultdict(int)
    for spec in dependencies:
        match = _PATTERN.match(spec.strip())
        if not match:
            continue
        name, constraint = match.group(1), match.group(2).strip()
        seen[name] += 1
        if name not in constraints:
            order.append(name)
        if constraint:
            constraints[name].append(constraint)
        else:
            unpinned.append(name)

    duplicates = [name for name in order if seen[name] > 1]

    conflicts = []
    for name, specs in constraints.items():
        upper = [s for s in specs if s.startswith("<")]
        lower = [s for s in specs if s.startswith(">")]
        if upper and lower:
            highest_lower = max(float(s.lstrip("><=~!").split(",")[0]) for s in lower)
            lowest_upper = min(float(s.lstrip("><=~!").split(",")[0]) for s in upper)
            if highest_lower >= lowest_upper:
                conflicts.append(name)

    return {
        "unpinned": unpinned,
        "duplicates": duplicates,
        "conflicts": sorted(conflicts),
        "clean": not unpinned and not duplicates and not conflicts,
    }
""",
        ),
        transfer_ar="استخدم `audit_dependencies` في Project Rescue لفحص تبعيات مستودع مستورد.",
        transfer_en="Use `audit_dependencies` in Project Rescue to inspect the dependencies of an imported repository.",
        references=(
            ("Python docs - venv", "https://docs.python.org/3/library/venv.html"),
            ("Packaging - pyproject.toml guide", "https://packaging.python.org/en/latest/guides/writing-pyproject-toml/"),
            ("PEP 621 - project metadata", "https://peps.python.org/pep-0621/"),
        ),
    ),
    CurriculumModule(
        id="l3.typing_dataclasses",
        level=3,
        order_index=2,
        domain="professional",
        title_ar="التنميط و dataclasses",
        title_en="Type hints and dataclasses",
        summary_ar="تلميحات أنواع تجعل الأخطاء مرئية قبل التشغيل، وأصناف بيانات موجزة.",
        summary_en="Type hints that surface bugs before runtime, and concise data classes.",
        explanation_ar="""تلميحات الأنواع لا تُغيّر سلوك التشغيل، لكنها تجعل النية واضحة وتسمح لأدوات
مثل Pyright وmypy بكشف الأخطاء قبل التنفيذ.

الأساسيات:
- `def greet(name: str) -> str:` و`values: list[int]` و`mapping: dict[str, float]`.
- `X | None` بدل `Optional[X]` في بايثون الحديثة.
- `TypeVar` و`Generic` للدوال والحاويات العامة.
- `typing.Protocol` للتنميط الهيكلي (التحقق من وجود methods لا من الوراثة).

`dataclass` تولّد `__init__` و`__repr__` و`__eq__`:
- `field(default_factory=list)` للقيم القابلة للتغيير،
- `frozen=True` لكائنات غير قابلة للتغيير،
- `__post_init__` للتحقق من القيم.""",
        explanation_en="""Type hints do not change runtime behaviour, but they make intent explicit and let tools
such as Pyright or mypy catch bugs before execution.

Basics:
- `def greet(name: str) -> str:`, `values: list[int]`, `mapping: dict[str, float]`.
- Prefer `X | None` over `Optional[X]` on modern Python.
- `TypeVar` and `Generic` for generic functions and containers.
- `typing.Protocol` for structural typing (checking methods exist rather than inheritance).

`dataclass` generates `__init__`, `__repr__` and `__eq__`:
- `field(default_factory=list)` for mutable defaults,
- `frozen=True` for immutable records,
- `__post_init__` for validation.""",
        skills=("pro.typing", "stdlib.dataclasses", "adv.protocols"),
        prerequisites=("l2.oop",),
        example_code="""from dataclasses import dataclass, field
from typing import Protocol, TypeVar

T = TypeVar("T")


class Priced(Protocol):
    def price(self) -> float: ...


@dataclass(slots=True)
class OrderLine:
    sku: str
    quantity: int
    unit_price: float
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

    @property
    def total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


def first(items: list[T]) -> T | None:
    return items[0] if items else None


def total_price(lines: list[Priced]) -> float:
    return round(sum(line.price() for line in lines), 2)


line = OrderLine("A1", 3, 9.99)
print(line, "| total:", line.total)
print(first([1, 2, 3]), first([]))
""",
        example_notes_ar="`Protocol` يسمح بتمرير أي كائن لديه `price()` دون وراثة من صنف معيّن.",
        example_notes_en="`Protocol` lets you pass any object with a `price()` method, without inheriting from a base class.",
        experiment_code="""from dataclasses import dataclass, field, asdict
from typing import TypeVar, Generic

T = TypeVar("T")


@dataclass(slots=True)
class Stack(Generic[T]):
    items: list[T] = field(default_factory=list)

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        if not self.items:
            raise IndexError("pop from an empty stack")
        return self.items.pop()

    def __len__(self) -> int:
        return len(self.items)


stack: Stack[int] = Stack()
stack.push(1)
stack.push(2)
print(asdict(stack), stack.pop(), len(stack))
print(Stack[int].__annotations__ if hasattr(Stack[int], "__annotations__") else "generic alias")
""",
        experiment_brief_ar="أضف طريقة `peek()` و`is_empty()` مع تنميط كامل، ثم اكتب اختباراً لحالة المكدس الفارغ.",
        experiment_brief_en="Add typed `peek()` and `is_empty()` methods, then write a test for the empty-stack case.",
        task=TaskSpec(
            brief_ar="""اكتب `Student` كـ dataclass:
- حقول: `name: str` و`grades: list[float]` (بـ `default_factory`)،
- `__post_init__` يرفع `ValueError` إذا كان الاسم فارغاً أو إذا وجدت درجة خارج 0..100،
- خاصية `average` تُعيد المعدل أو `0.0` لقائمة فارغة،
- خاصية `passed` تُعيد `True` إذا كان المعدل ≥ 60.

ثم اكتب `top_students(students, count=3)` تُعيد أسماء أعلى `count` طلاب حسب المعدل.""",
            brief_en="""Write `Student` as a dataclass:
- fields: `name: str` and `grades: list[float]` (with `default_factory`),
- `__post_init__` raises `ValueError` for an empty name or a grade outside 0..100,
- an `average` property returning the mean or `0.0` for an empty list,
- a `passed` property that is `True` when the average is at least 60.

Then write `top_students(students, count=3)` returning the names of the top `count` students by average.""",
            starter_code="""from dataclasses import dataclass, field


@dataclass
class Student:
    name: str
    grades: list[float] = field(default_factory=list)

    def __post_init__(self):
        pass

    @property
    def average(self) -> float:
        pass

    @property
    def passed(self) -> bool:
        pass


def top_students(students, count=3):
    pass
""",
            public_tests={
                "test_public.py": """from main import Student, top_students

def test_average():
    assert Student("a", [50, 100]).average == 75.0

def test_top():
    students = [Student("a", [50]), Student("b", [90])]
    assert top_students(students, 1) == ["b"]
"""},
            hidden_tests={
                "test_hidden.py": """from main import Student, top_students
import pytest

def test_empty_grades():
    assert Student("a").average == 0.0
    assert Student("a").passed is False

def test_validation_name():
    with pytest.raises(ValueError):
        Student("")
    with pytest.raises(ValueError):
        Student("   ")

def test_validation_grade_range():
    with pytest.raises(ValueError):
        Student("a", [101])
    with pytest.raises(ValueError):
        Student("a", [-1])

def test_passed_boundary():
    assert Student("a", [60]).passed is True
    assert Student("a", [59.9]).passed is False

def test_top_handles_short_lists():
    students = [Student("a", [10])]
    assert top_students(students, 5) == ["a"]
    assert top_students([], 3) == []

def test_top_does_not_mutate():
    students = [Student("a", [10]), Student("b", [90])]
    top_students(students, 1)
    assert [s.name for s in students] == ["a", "b"]
"""},
            reference_solution="""from dataclasses import dataclass, field


@dataclass
class Student:
    name: str
    grades: list[float] = field(default_factory=list)

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name must not be empty")
        for grade in self.grades:
            if not 0.0 <= grade <= 100.0:
                raise ValueError(f"grade out of range: {grade}")

    @property
    def average(self) -> float:
        return sum(self.grades) / len(self.grades) if self.grades else 0.0

    @property
    def passed(self) -> bool:
        return self.average >= 60


def top_students(students, count=3):
    ordered = sorted(students, key=lambda student: (-student.average, student.name))
    return [student.name for student in ordered[:count]]
""",
            hints=(
                "Validate in `__post_init__` - that is exactly what it is for.",
                "Sort by `(-average, name)` so ties are resolved deterministically.",
                "Never mutate the list you were given; `sorted()` already returns a copy.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب حاوية عامة `Result(Generic[T])` تمثّل نتيجة operation إما ناجحة أو فاشلة:
- `Result.ok(value)` و`Result.fail(error)`،
- خاصية `is_ok` وخاصيتا `value` و`error`،
- طريقة `unwrap()` تُعيد القيمة أو ترفع الخطأ المخزّن،
- طريقة `map(func)` تُعيد `Result` جديداً بتطبيق `func` على القيمة الناجحة.

ثم اكتب `parse_int(text) -> Result[int]` تستخدمها.""",
            brief_en="""Write a generic `Result(Generic[T])` container representing success or failure:
- `Result.ok(value)` and `Result.fail(error)`,
- properties `is_ok`, `value` and `error`,
- `unwrap()` returning the value or raising the stored error,
- `map(func)` returning a new `Result` with `func` applied to a successful value.

Then write `parse_int(text) -> Result[int]` built on it.""",
            independent=True,
            starter_code="""from dataclasses import dataclass
from typing import Generic, TypeVar, Callable

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class Result(Generic[T]):
    pass


def parse_int(text):
    pass
""",
            public_tests={"test_public.py": """from main import Result, parse_int

def test_ok():
    assert Result.ok(5).value == 5
    assert Result.ok(5).is_ok is True

def test_parse_int():
    assert parse_int("42").value == 42
    assert parse_int("x").is_ok is False
"""},
            hidden_tests={"test_hidden.py": """from main import Result, parse_int

def test_fail_and_error():
    failure = Result.fail("boom")
    assert failure.is_ok is False
    assert failure.value is None
    assert failure.error == "boom"

def test_unwrap_raises():
    import pytest
    assert Result.ok(3).unwrap() == 3
    with pytest.raises(RuntimeError):
        Result.fail(RuntimeError("bad")).unwrap()

def test_map_on_success_and_failure():
    assert Result.ok(2).map(lambda v: v * 3).value == 6
    mapped = Result.fail("e").map(lambda v: v * 3)
    assert mapped.is_ok is False
    assert mapped.error == "e"

def test_parse_int_edges():
    assert parse_int(" -7 ").value == -7
    assert parse_int("").is_ok is False
    assert parse_int("3.5").is_ok is False
"""},
            reference_solution="""from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class Result(Generic[T]):
    value: T | None = None
    error: BaseException | str | None = None

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(value=value, error=None)

    @classmethod
    def fail(cls, error) -> "Result[T]":
        return cls(value=None, error=error)

    @property
    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> T:
        if self.error is not None:
            raise self.error if isinstance(self.error, BaseException) else RuntimeError(str(self.error))
        return self.value

    def map(self, func: Callable[[T], U]) -> "Result[U]":
        if self.error is not None:
            return Result.fail(self.error)
        return Result.ok(func(self.value))


def parse_int(text):
    try:
        return Result.ok(int(str(text).strip()))
    except (TypeError, ValueError) as exc:
        return Result.fail(str(exc))
""",
        ),
        transfer_ar="استخدم النمط في Agent Planet لتمرير نتائج الأدوات دون استثناءات متناثرة.",
        transfer_en="Use the pattern in Agent Planet to pass tool results around without scattered exceptions.",
        references=(
            ("Python docs - typing", "https://docs.python.org/3/library/typing.html"),
            ("Python docs - dataclasses", "https://docs.python.org/3/library/dataclasses.html"),
        ),
    ),
    CurriculumModule(
        id="l3.testing",
        level=3,
        order_index=3,
        domain="professional",
        title_ar="الاختبارات الآلية",
        title_en="Automated testing",
        summary_ar="اكتب اختبارات تكشف الأخطاء فعلاً، لا اختبارات تمرّر الكود الحالي.",
        summary_en="Write tests that actually catch bugs, not tests that merely pass.",
        explanation_ar="""الاختبار الجيد يعبّر عن **عقد**: "مهما تغيّر التنفيذ، هذا السلوك يجب أن يبقى".

خصائص الاختبار المفيد:
- **حالة واحدة لكل اختبار** مع اسم يصف السلوك.
- **حدود واضحة**: القيم الفارغة، الحدود الدنيا والعليا، والمدخلات الخاطئة.
- **لا يعتمد على ترتيب التشغيل** ولا على بيانات خارجية.
- يفشل لسبب **واحد** يمكن فهمه من الرسالة.

في pytest:
- التجهيزات `@pytest.fixture` لتحضير البيانات،
- `@pytest.mark.parametrize` لتشغيل نفس الاختبار على مدخلات متعددة،
- `pytest.raises` للتحقق من الأخطاء،
- `tmp_path` للملفات المؤقتة.

الاختبار الذي لا يفشل عند كسر الكود ليس اختباراً.""",
        explanation_en="""A good test expresses a **contract**: "however the implementation changes, this
behaviour must hold".

What makes a test useful:
- **one case per test**, named after the behaviour;
- **explicit boundaries**: empty values, lower/upper limits, invalid inputs;
- no dependence on execution order or external data;
- it fails for **one** reason you can read from the message.

In pytest:
- `@pytest.fixture` prepares data,
- `@pytest.mark.parametrize` runs one test over many inputs,
- `pytest.raises` asserts failures,
- `tmp_path` gives you a temporary directory.

A test that does not fail when the code breaks is not a test.""",
        skills=("pro.testing", "stdlib.unittest_pytest", "pro.mocking"),
        prerequisites=("l3.typing_dataclasses",),
        example_code="""import pytest


def discount(price, percent):
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


@pytest.fixture
def cart():
    return {"items": [{"price": 100, "qty": 2}, {"price": 50, "qty": 1}]}


@pytest.mark.parametrize(
    "price, percent, expected",
    [
        (100, 0, 100.0),
        (100, 10, 90.0),
        (50, 100, 0.0),
        (99.99, 15, 84.99),
    ],
)
def test_discount_values(price, percent, expected):
    assert discount(price, percent) == expected


def test_invalid_percent_raises():
    with pytest.raises(ValueError):
        discount(100, 150)


def test_cart_total(cart):
    assert sum(item["price"] * item["qty"] for item in cart["items"]) == 250


# Run this file with: python -m pytest test_pricing.py
""",
        example_notes_ar="شغّل الملف بـ `python -m pytest`. غيّر الدالة عمداً وتأكد أن الاختبارات تفشل.",
        example_notes_en="Run it with `python -m pytest`. Break the function on purpose and confirm the tests fail.",
        experiment_code="""import pytest


def normalise(values):
    if not values:
        return []
    lowest, highest = min(values), max(values)
    span = highest - lowest
    if span == 0:
        return [0.0 for _ in values]
    return [(value - lowest) / span for value in values]


@pytest.mark.parametrize(
    "values, expected",
    [
        ([0, 5, 10], [0.0, 0.5, 1.0]),
        ([5, 5, 5], [0.0, 0.0, 0.0]),
        ([], []),
        ([-10, 0, 10], [0.0, 0.5, 1.0]),
    ],
)
def test_normalise(values, expected):
    result = normalise(values)
    assert len(result) == len(expected)
    for actual, want in zip(result, expected):
        assert actual == pytest.approx(want)
""",
        experiment_brief_ar="أضف حالة اختبار تكشف خطأً في معالجة القيم السالبة، ثم أصلح الدالة إن لزم.",
        experiment_brief_en="Add a test case that exposes a bug in handling negatives, then fix the function if needed.",
        task=TaskSpec(
            brief_ar="""وحدة `cart` معطوبة. اكتب اختبارات تكشف أعطالها ثم أصلحها.

المهمة على مرحلتين:
1. اكتب ملف `test_cart.py` فيه اختبارات (دوال `test_*` تستقبل وسيطاً واحداً هو وحدة cart)
   تغطي: إضافة صنف، حساب الإجمالي، تطبيق الخصم، وحالة المخزون غير الكافي.
2. أصلح `cart.py` بحيث تمرّ اختباراتك.

**الاتفاقية**: كل دالة اختبار تستقبل الوحدة كوسيط، مثلاً:

```python
def test_total_empty(cart):
    c = cart.ShoppingCart()
    assert c.total() == 0
```

سيشغّل النظام اختباراتك على نسخة صحيحة (يجب أن تنجح كلها) وعلى نسخة معطوبة
(يجب أن يفشل واحد منها على الأقل).""",
            brief_en="""The `cart` module is broken. Write tests that expose its bugs, then fix it.

Two steps:
1. Write `test_cart.py` containing tests (functions named `test_*` that take one argument:
   the cart module) covering: adding an item, the total, applying a discount, and
   insufficient stock.
2. Fix `cart.py` so your tests pass.

**Convention**: every test function receives the module, for example:

```python
def test_total_empty(cart):
    c = cart.ShoppingCart()
    assert c.total() == 0
```

The grader runs your tests against a correct implementation (all must pass) and against a
broken one (at least one must fail).""",
            starter_code="""import cart


def test_total_empty(cart):
    instance = cart.ShoppingCart()
    assert instance.total() == 0


def test_add_item(cart):
    # TODO: add an item and assert the total
    pass


def test_discount(cart):
    # TODO: apply a discount and assert the total
    pass


def test_insufficient_stock(cart):
    # TODO: assert that ordering more than the stock raises an error
    pass
""",
            entry_filename="test_cart.py",
            extra_files={
                "cart.py": """class OutOfStock(Exception):
    pass


class ShoppingCart:
    def __init__(self):
        self.items = {}

    def add(self, sku, unit_price, quantity=1):
        self.items[sku] = {
            "unit_price": unit_price,
            "quantity": self.items.get(sku, {}).get("quantity", 0) + quantity,
        }

    def total(self):
        return sum(item["unit_price"] * item["quantity"] for item in self.items.values())

    def apply_discount(self, percent):
        factor = 1 - percent / 100
        for item in self.items.values():
            item["unit_price"] = round(item["unit_price"] * factor, 2)

    def order(self, sku, quantity, stock):
        available = stock.get(sku, 0)
        if available < quantity:
            raise OutOfStock(f"only {available} of {sku} available")
        return {"sku": sku, "quantity": quantity}
""",
                "cart_broken.py": """class OutOfStock(Exception):
    pass


class ShoppingCart:
    def __init__(self):
        self.items = {}

    def add(self, sku, unit_price, quantity=1):
        self.items[sku] = {
            "unit_price": unit_price,
            "quantity": self.items.get(sku, {}).get("quantity", 0) + quantity,
        }

    def total(self):
        # BUG: ignores the quantity
        return sum(item["unit_price"] for item in self.items.values())

    def apply_discount(self, percent):
        # BUG: ignores the percentage
        return None

    def order(self, sku, quantity, stock):
        # BUG: never validates the stock
        return {"sku": sku, "quantity": quantity}
""",
            },
            public_tests={
                "test_public.py": """import importlib
import pathlib
import sys

ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _run(module_name):
    module = importlib.import_module(module_name)
    learner = importlib.import_module("test_cart")
    results = {}
    for name in sorted(dir(learner)):
        if not name.startswith("test_"):
            continue
        function = getattr(learner, name)
        try:
            function(module)
            results[name] = "passed"
        except AssertionError:
            results[name] = "failed"
        except Exception as exc:  # noqa: BLE001
            results[name] = f"error:{type(exc).__name__}"
    return results


def test_learner_tests_exist():
    learner = importlib.import_module("test_cart")
    names = [name for name in dir(learner) if name.startswith("test_")]
    assert len(names) >= 4, "write at least four tests"
"""},
            hidden_tests={
                "test_hidden.py": """import importlib
import pathlib
import sys

ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _run(module_name):
    module = importlib.import_module(module_name)
    learner = importlib.import_module("test_cart")
    results = {}
    for name in sorted(dir(learner)):
        if not name.startswith("test_"):
            continue
        function = getattr(learner, name)
        try:
            function(module)
            results[name] = "passed"
        except AssertionError:
            results[name] = "failed"
        except Exception as exc:  # noqa: BLE001
            results[name] = f"error:{type(exc).__name__}"
    return results


def test_all_tests_pass_on_the_fixed_module():
    results = _run("cart")
    failures = {name: state for name, state in results.items() if state != "passed"}
    assert not failures, f"your tests fail on the correct implementation: {failures}"
    assert len(results) >= 4


def test_at_least_one_test_catches_the_broken_module():
    results = _run("cart_broken")
    caught = [name for name, state in results.items() if state != "passed"]
    assert caught, "your tests pass on the broken implementation too - they are too weak"
"""},
            reference_solution="""import cart


def test_total_empty(cart):
    assert cart.ShoppingCart().total() == 0


def test_add_item(cart):
    instance = cart.ShoppingCart()
    instance.add("A1", 10.0, 2)
    instance.add("A1", 10.0, 3)
    assert instance.total() == 50.0


def test_discount(cart):
    instance = cart.ShoppingCart()
    instance.add("A1", 100.0)
    instance.apply_discount(10)
    assert instance.total() == 90.0


def test_insufficient_stock(cart):
    instance = cart.ShoppingCart()
    try:
        instance.order("A1", 5, {"A1": 2})
    except cart.OutOfStock:
        return
    raise AssertionError("ordering more than the stock must raise OutOfStock")
""",
            hints=(
                "A test that only checks `total() == 0` will pass on the broken module - assert real numbers.",
                "Use `pytest.raises`-style try/except for the stock case; the module raises `OutOfStock`.",
                "Cover the discount calculation: the broken version ignores the percentage.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""وحدة `ledger` تسجل عمليات مالية. اكتب اختبارات شاملة في `test_ledger.py`
(بنفس الاتفاقية: دوال `test_*` تستقبل الوحدة) تغطي على الأقل:
الرصيد الابتدائي، الإيداع، السحب الناجح، السحب الذي يتجاوز الرصيد،
وتحويلاً بين حسابين.""",
            brief_en="""A `ledger` module records financial operations. Write thorough tests in
`test_ledger.py` (same convention: `test_*` functions taking the module) covering at least:
the opening balance, a deposit, a successful withdrawal, a withdrawal beyond the balance,
and a transfer between two accounts.""",
            independent=True,
            starter_code="""import ledger


def test_opening_balance(ledger):
    pass


def test_deposit(ledger):
    pass


def test_withdrawal(ledger):
    pass


def test_overdraft(ledger):
    pass


def test_transfer(ledger):
    pass
""",
            entry_filename="test_ledger.py",
            extra_files={
                "ledger.py": '''class InsufficientFunds(Exception):
    pass


class Account:
    def __init__(self, owner, balance=0.0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise InsufficientFunds(f"balance {self.balance}, requested {amount}")
        self.balance -= amount
        self.history.append(("withdraw", amount))


def transfer(source, target, amount):
    source.withdraw(amount)
    target.deposit(amount)
''',
                "ledger_broken.py": '''class InsufficientFunds(Exception):
    pass


class Account:
    def __init__(self, owner, balance=0.0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        self.balance += amount          # BUG: no validation
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        self.balance -= amount          # BUG: allows overdraft
        self.history.append(("withdraw", amount))


def transfer(source, target, amount):
    source.withdraw(amount)
    target.deposit(amount * 0.9)        # BUG: loses 10 percent
''',
            },
            public_tests={
                "test_public.py": """import importlib, pathlib, sys

ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_tests_exist():
    learner = importlib.import_module("test_ledger")
    names = [n for n in dir(learner) if n.startswith("test_")]
    assert len(names) >= 5
"""},
            hidden_tests={
                "test_hidden.py": """import importlib, pathlib, sys

ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _run(module_name):
    module = importlib.import_module(module_name)
    learner = importlib.import_module("test_ledger")
    results = {}
    for name in sorted(dir(learner)):
        if not name.startswith("test_"):
            continue
        try:
            getattr(learner, name)(module)
            results[name] = "passed"
        except AssertionError:
            results[name] = "failed"
        except Exception as exc:  # noqa: BLE001
            results[name] = f"error:{type(exc).__name__}"
    return results


def test_passes_on_correct_module():
    results = _run("ledger")
    failures = {n: s for n, s in results.items() if s != "passed"}
    assert not failures, failures


def test_catches_broken_module():
    results = _run("ledger_broken")
    assert [n for n, s in results.items() if s != "passed"], "tests are too weak"
"""},
            reference_solution="""import ledger


def test_opening_balance(ledger):
    account = ledger.Account("sara", 100.0)
    assert account.balance == 100.0
    assert account.history == []


def test_deposit(ledger):
    account = ledger.Account("sara")
    account.deposit(50.0)
    assert account.balance == 50.0
    assert account.history == [("deposit", 50.0)]


def test_withdrawal(ledger):
    account = ledger.Account("sara", 100.0)
    account.withdraw(40.0)
    assert account.balance == 60.0


def test_overdraft(ledger):
    account = ledger.Account("sara", 10.0)
    try:
        account.withdraw(50.0)
    except ledger.InsufficientFunds:
        assert account.balance == 10.0
        return
    raise AssertionError("overdraft must raise InsufficientFunds")


def test_transfer(ledger):
    source = ledger.Account("a", 100.0)
    target = ledger.Account("b", 20.0)
    ledger.transfer(source, target, 30.0)
    assert (source.balance, target.balance) == (70.0, 50.0)
""",
        ),
        transfer_ar="طبّق نفس المنهج في CareerVerse: اكتب اختبار انحدار لكل عطل تُصلحه.",
        transfer_en="Apply the same method in CareerVerse: write a regression test for every incident you fix.",
        references=(
            ("pytest docs - fixtures", "https://docs.pytest.org/en/stable/explanation/fixtures.html"),
            ("pytest docs - parametrize", "https://docs.pytest.org/en/stable/parametrize.html"),
        ),
    ),
    CurriculumModule(
        id="l3.debugging",
        level=3,
        order_index=4,
        domain="professional",
        title_ar="التصحيح وإعادة التصميم",
        title_en="Debugging and refactoring",
        summary_ar="من العَرَض إلى السبب: إعادة إنتاج، عزل، إصلاح، واختبار يمنع العودة.",
        summary_en="From symptom to cause: reproduce, isolate, fix, then lock it with a test.",
        explanation_ar="""منهج تصحيح منظّم:

1. **أعد إنتاج العطل** بأصغر مثال ممكن (repro).
2. **اقرأ التتبع من الأسفل**: آخر إطار في كودك هو نقطة التوقف.
3. **كوّن فرضية واختبرها**: اطبع القيم، استخدم `breakpoint()`، أو بسّط المدخلات.
4. **أصلح السبب لا العَرَض**.
5. **اكتب اختبار انحدار** يفشل قبل الإصلاح وينجح بعده.

إعادة التصميم (refactoring) تغيّر البنية دون تغيير السلوك. قاعدتها الذهبية:
**لا تُعيد التصميم دون اختبارات حارسة**. خطوات صغيرة، تشغيل الاختبارات بعد كل خطوة.

استخدم `logging` بدل `print` في الكود الذي سيعيش طويلاً: مستويات، ووقت، وسياق.""",
        explanation_en="""A systematic debugging method:

1. **Reproduce** the failure with the smallest possible example.
2. **Read the traceback bottom-up**: the last frame inside your code is where it stopped.
3. **Form and test a hypothesis**: print values, use `breakpoint()`, or shrink the input.
4. **Fix the cause**, not the symptom.
5. **Write a regression test** that fails before the fix and passes after it.

Refactoring changes structure without changing behaviour. Its golden rule:
**never refactor without tests protecting you**. Take small steps and run the suite after each.

Use `logging` rather than `print` in code that will live: levels, timestamps and context.""",
        skills=("pro.debugging", "pro.refactoring", "pro.logging"),
        prerequisites=("l3.testing",),
        example_code="""import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s :: %(message)s")
log = logging.getLogger("billing")


def safe_mean(values):
    if not values:
        log.warning("safe_mean called with no values; returning 0.0")
        return 0.0
    try:
        return sum(values) / len(values)
    except TypeError as exc:
        log.error("non-numeric value in %r: %s", values, exc)
        raise


print(safe_mean([1, 2, 3]))
print(safe_mean([]))
try:
    safe_mean([1, "two"])
except TypeError:
    print("re-raised with context")

# breakpoint()  <- uncomment to drop into pdb and inspect the frame
""",
        example_notes_ar="فعّل `breakpoint()` داخل دالة وافحص المتغيرات بـ `p variable` ثم `c` للمتابعة.",
        example_notes_en="Enable `breakpoint()` inside a function, inspect with `p variable`, then continue with `c`.",
        experiment_code="""def buggy_median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle]


print(buggy_median([1, 2, 3]))       # 2   correct
print(buggy_median([1, 2, 3, 4]))   # 3   wrong: the median is 2.5

# Reproduce -> hypothesis (even length needs the average of two middles) -> fix.
def fixed_median(values):
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


print(fixed_median([1, 2, 3, 4]), fixed_median([1, 2, 3]))
""",
        experiment_brief_ar="اكتب اختباراً يفشل على `buggy_median` وينجح على `fixed_median` (اختبار انحدار حقيقي).",
        experiment_brief_en="Write a test that fails on `buggy_median` and passes on `fixed_median` (a real regression test).",
        task=TaskSpec(
            brief_ar="""وحدة `statsx` تحتوي ثلاثة أعطاب مخفية. أعد إنتاجها باختبارات، ثم أصلحها:

1. `moving_average(values, window)` تُعيد متوسطات متحركة خاطئة عند نهاية القائمة.
2. `clamp(value, low, high)` لا يعمل عندما يكون `low > high`.
3. `top_n(values, n)` يفشل عندما يكون `n` أكبر من طول القائمة.

المطلوب: أصلح الوحدة بحيث:
- `moving_average([1,2,3,4], 2)` → `[1.5, 2.5, 3.5]`،
- `clamp(5, 10, 1)` تُعيد `5` (تجاهل القيد غير المنطقي) وترفع `ValueError` فقط إذا كان `low == high` وحاولت التقييد،
- `top_n([1,2], 5)` تُعيد `[2, 1]` مرتبة تنازلياً.""",
            brief_en="""The `statsx` module hides three bugs. Reproduce them with tests, then fix them:

1. `moving_average(values, window)` returns wrong values at the end of the list.
2. `clamp(value, low, high)` misbehaves when `low > high`.
3. `top_n(values, n)` fails when `n` exceeds the list length.

Fix the module so that:
- `moving_average([1,2,3,4], 2)` -> `[1.5, 2.5, 3.5]`,
- `clamp(5, 10, 1)` returns `5` (ignore the nonsensical range) and raises `ValueError` only when `low == high`,
- `top_n([1,2], 5)` returns `[2, 1]` sorted descending.""",
            starter_code="""def moving_average(values, window):
    result = []
    for index in range(len(values)):
        chunk = values[index:index + window]
        result.append(sum(chunk) / len(chunk))
    return result


def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value


def top_n(values, n):
    return sorted(values, reverse=True)[:n]
""",
            public_tests={
                "test_public.py": """from main import moving_average

def test_moving_average():
    assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]
"""},
            hidden_tests={
                "test_hidden.py": """from main import moving_average, clamp, top_n
import pytest

def test_moving_average_window_one():
    assert moving_average([1, 2, 3], 1) == [1.0, 2.0, 3.0]

def test_moving_average_window_equals_length():
    assert moving_average([1, 2, 3], 3) == [2.0]

def test_moving_average_bad_window():
    with pytest.raises(ValueError):
        moving_average([1, 2], 0)

def test_clamp_normal():
    assert clamp(5, 1, 10) == 5
    assert clamp(-5, 1, 10) == 1
    assert clamp(50, 1, 10) == 10

def test_clamp_reversed_bounds():
    assert clamp(5, 10, 1) == 5

def test_clamp_equal_bounds():
    with pytest.raises(ValueError):
        clamp(5, 3, 3)

def test_top_n_larger_than_list():
    assert top_n([1, 2], 5) == [2, 1]
    assert top_n([], 3) == []

def test_top_n_zero_and_negative():
    assert top_n([1, 2], 0) == []
    assert top_n([1, 2], -1) == []
"""},
            reference_solution="""def moving_average(values, window):
    if window <= 0:
        raise ValueError("window must be positive")
    result = []
    for index in range(len(values) - window + 1):
        chunk = values[index:index + window]
        result.append(sum(chunk) / len(chunk))
    return result


def clamp(value, low, high):
    if low > high:
        return value
    if low == high:
        raise ValueError(f"empty range: low == high == {low}")
    if value < low:
        return low
    if value > high:
        return high
    return value


def top_n(values, n):
    if n <= 0:
        return []
    return sorted(values, reverse=True)[:n]
""",
            hints=(
                "The moving average should stop at `len(values) - window + 1`, not at the end of the list.",
                "Decide explicitly what a reversed range means: ignoring the bounds is one defensible choice.",
                "Slicing with a negative `n` silently drops items - guard it.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""أعد تصميم `report.py` دون تغيير سلوكه:
- استخرج ثوابت السطور والأعمدة إلى الأعلى،
- استبدل الفهارس الرقمية بأسماء واضحة،
- اجعل `build_report(rows)` تُعيد النص بدل طباعته،
- أضف سجلات (`logging`) عند تخطّي صف غير صالح بدل التجاهل الصامت.""",
            brief_en="""Refactor `report.py` without changing its behaviour:
- lift the magic numbers into named constants,
- replace numeric indices with clear names,
- make `build_report(rows)` return the text instead of printing it,
- log (with `logging`) whenever an invalid row is skipped instead of ignoring it silently.""",
            independent=True,
            starter_code="""def build_report(rows):
    out = ""
    for r in rows:
        if len(r) < 3:
            continue
        out += r[0] + "," + str(r[1]) + "," + str(round(r[1] * r[2], 2)) + "\\n"
    out += "TOTAL," + str(len(rows)) + "," + str(round(sum(r[1] * r[2] for r in rows if len(r) >= 3), 2)) + "\\n"
    print(out)
    return None
""",
            public_tests={"test_public.py": """from main import build_report

def test_returns_text():
    text = build_report([["A1", 2, 5.0]])
    assert isinstance(text, str)
    assert "A1,2,10.0" in text
    assert "TOTAL,1,10.0" in text
"""},
            hidden_tests={"test_hidden.py": """from main import build_report

def test_skips_short_rows():
    text = build_report([["A1", 2, 5.0], ["bad"]])
    assert "bad" not in text
    assert "TOTAL,1,10.0" in text

def test_empty_rows():
    text = build_report([])
    assert "TOTAL,0,0.0" in text

def test_does_not_print(capsys):
    build_report([["A1", 1, 1.0]])
    assert capsys.readouterr().out == ""

def test_rounding_and_multiple_rows():
    text = build_report([["A", 3, 1.007], ["B", 1, 2.0]])
    lines = text.strip().splitlines()
    assert lines[0].split(",")[2] == "3.02"
    assert lines[-1].startswith("TOTAL,2,")
"""},
            reference_solution="""import logging

logger = logging.getLogger(__name__)

SKU, QUANTITY, UNIT_PRICE = 0, 1, 2
MIN_FIELDS = 3
HEADER_ROWS = "rows"


def _row_value(row):
    return row[QUANTITY] * row[UNIT_PRICE]


def build_report(rows):
    lines = []
    total = 0.0
    valid = 0
    for row in rows:
        if len(row) < MIN_FIELDS:
            logger.warning("skipping malformed row: %r", row)
            continue
        value = round(_row_value(row), 2)
        total += value
        valid += 1
        lines.append(f"{row[SKU]},{row[QUANTITY]},{value}")
    lines.append(f"TOTAL,{valid},{round(total, 2)}")
    return "\\n".join(lines) + "\\n"
""",
        ),
        transfer_ar="استخدم المنهج في Engineering Crisis Simulator: أعد إنتاج العطل قبل لمس الكود.",
        transfer_en="Use the method in the Engineering Crisis Simulator: reproduce the incident before touching code.",
        references=(
            ("Python docs - logging", "https://docs.python.org/3/library/logging.html"),
            ("Python docs - pdb", "https://docs.python.org/3/library/pdb.html"),
            ("Refactoring - Martin Fowler", "https://refactoring.com/"),
        ),
    ),
]
