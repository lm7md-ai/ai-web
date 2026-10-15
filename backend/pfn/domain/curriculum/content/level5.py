"""LEVEL 5 - Data engineering: numpy, pandas, cleaning and ETL pipelines."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l5.numpy_foundations",
        level=5,
        order_index=1,
        domain="data_engineering",
        title_ar="أساسيات NumPy",
        title_en="NumPy foundations",
        summary_ar="المصفوفات مقابل القوائم، التوجيه (vectorization)، البث (broadcasting)، والأقنعة المنطقية.",
        summary_en="Arrays vs lists, vectorization, broadcasting and boolean masks.",
        explanation_ar="""`ndarray` كتلة ذاكرة واحدة متصلة من قيم **متجانسة النوع**، عكس قائمة بايثون
التي تخزّن مؤشرات لكائنات متفرقة. هذا يعني:

- عمليات رياضية تُطبَّق على كل عنصر دفعة واحدة (vectorization) بدون حلقة `for`،
- ذاكرة أقل وسرعة أكبر بكثير،
- شكل (`shape`) ونوع (`dtype`) ثابتان.

**البث (broadcasting)** يسمح بعمليات بين أشكال مختلفة:
- `(3, 4) + (4,)` → يُبث الصف على كل الصفوف،
- `(3, 1) + (1, 4)` → النتيجة `(3, 4)`،
- القاعدة: الأبعاد تُقارن من اليمين، وكل بُعد يجب أن يكون متساوياً أو `1` أو غائباً.

**الأقنعة المنطقية** بديل الفلترة: `values[values > 0]` تُعيد نسخة (fancy indexing)،
بينما `values[values > 0] = 0` تعدّل في المكان.

انتبه: `arr[1:3]` **عرض** (view) على نفس الذاكرة، وليس نسخة. عدّله وستتغيّر المصفوفة الأم.""",
        explanation_en="""An `ndarray` is one contiguous block of memory holding values of a **single type**,
unlike a Python list, which stores pointers to scattered objects. That means:

- arithmetic applies to every element at once (vectorization) without a `for` loop,
- far less memory and much more speed,
- a fixed `shape` and `dtype`.

**Broadcasting** lets arrays of different shapes interact:
- `(3, 4) + (4,)` broadcasts the row across every row,
- `(3, 1) + (1, 4)` yields `(3, 4)`,
- the rule: dimensions are compared from the right, and each must be equal, `1`, or missing.

**Boolean masks** replace filtering: `values[values > 0]` returns a copy (fancy indexing),
while `values[values > 0] = 0` writes in place.

Careful: `arr[1:3]` is a **view** onto the same memory, not a copy - mutating it changes the parent.""",
        skills=("data.numpy", "data.numpy_advanced", "sci.linalg"),
        prerequisites=("l1.lists_tuples", "l4.data_model"),
        example_code="""import time

import numpy as np

size = 200_000
values = list(range(size))
array = np.arange(size, dtype=np.int64)

start = time.perf_counter()
squares = [v * v for v in values]
python_time = time.perf_counter() - start

start = time.perf_counter()
np_squares = array * array
numpy_time = time.perf_counter() - start

print(f"python list: {python_time * 1000:6.2f} ms")
print(f"numpy array: {numpy_time * 1000:6.2f} ms")
print(f"speedup    : {python_time / numpy_time:6.1f}x")
print("same result:", squares[-1] == np_squares[-1])

matrix = np.arange(12).reshape(3, 4)
print(matrix)
print("row means  :", matrix.mean(axis=1))
print("col means  :", matrix.mean(axis=0))
print("broadcast  :", (matrix + np.array([100, 200, 300, 400])).tolist())
print("mask       :", matrix[matrix % 5 == 0].tolist())

view = matrix[1:3]
view[0, 0] = -1
print("view mutated the parent:", matrix[1, 0] == -1)
""",
        example_notes_ar="غيّر `size` إلى 1000 وشاهد كيف يختفي فرق السرعة — التوجيه يفيد مع البيانات الكبيرة.",
        example_notes_en="Change `size` to 1000 and watch the speed gap shrink - vectorization pays off on big data.",
        experiment_code="""import numpy as np

rng = np.random.default_rng(7)

samples = rng.normal(loc=50, scale=12, size=(1000, 3))
print("shape:", samples.shape, "dtype:", samples.dtype)
print("mean per column:", np.round(samples.mean(axis=0), 2))
print("std  per column:", np.round(samples.std(axis=0), 2))

z = (samples - samples.mean(axis=0)) / samples.std(axis=0)
print("z-score frame: mean ~", round(float(z.mean()), 4), " std ~", round(float(z.std()), 4))
print("share above 2 sigma:", round(float((np.abs(z) > 2).mean()), 4))

A = np.array([[3.0, 1.0], [1.0, 2.0]])
b = np.array([9.0, 8.0])
print("solve Ax=b ->", np.round(np.linalg.solve(A, b), 3))
print("determinant:", round(float(np.linalg.det(A)), 3))

try:
    np.array([1, 2, 3]) + np.array([1, 2])
except ValueError as exc:
    print("broadcasting error:", exc)
""",
        experiment_brief_ar="غيّر seed المولّد إلى 42 وأعد التشغيل: ما الذي تغيّر وما الذي لم يتغيّر؟",
        experiment_brief_en="Change the generator seed to 42 and rerun: what changed and what stayed the same?",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `column_stats(matrix)` تُعيد قاموساً لكل عموم بمفتاح رقم العمود وقيمته
   `{"mean", "std", "min", "max"}` (استخدم `axis=0`).
2. `normalize_rows(matrix)` تُعيد نسخة جديدة كل صف فيها مجموعه `1.0`
   (تجنّب القسمة على صفر: اعتبر الصف الصفري توزيعاً متساوياً).
3. `top_k(values, k)` تُعيد فهارس أكبر `k` قيم مرتّبة تنازلياً (استخدم `np.argsort`).""",
            brief_en="""Write:
1. `column_stats(matrix)` returning, per column index, a dict with
   `{"mean", "std", "min", "max"}` (use `axis=0`).
2. `normalize_rows(matrix)` returning a new copy where every row sums to `1.0`
   (avoid dividing by zero: treat a zero row as a uniform distribution).
3. `top_k(values, k)` returning the indices of the `k` largest values, largest first
   (use `np.argsort`).""",
            starter_code="""import numpy as np


def column_stats(matrix):
    # TODO
    pass


def normalize_rows(matrix):
    # TODO
    pass


def top_k(values, k):
    # TODO
    pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import column_stats

def test_column_stats():
    matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
    stats = column_stats(matrix)
    assert stats[0]["mean"] == 2.0
    assert stats[1]["max"] == 4.0
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import column_stats, normalize_rows, top_k

def test_column_stats_keys():
    stats = column_stats(np.array([[1.0, 10.0], [3.0, 20.0], [5.0, 30.0]]))
    assert set(stats[0]) == {"mean", "std", "min", "max"}
    assert stats[0]["min"] == 1.0 and stats[0]["max"] == 5.0
    assert abs(stats[1]["mean"] - 20.0) < 1e-9

def test_normalize_rows():
    matrix = np.array([[1.0, 3.0], [0.0, 0.0], [2.0, 2.0]])
    result = normalize_rows(matrix)
    assert np.allclose(result.sum(axis=1), 1.0)
    assert np.allclose(result[0], [0.25, 0.75])
    assert np.allclose(result[1], [0.5, 0.5])

def test_normalize_does_not_mutate():
    matrix = np.array([[1.0, 1.0]])
    normalize_rows(matrix)
    assert np.allclose(matrix, [[1.0, 1.0]])

def test_top_k_order():
    values = np.array([5, 1, 9, 3])
    assert list(top_k(values, 2)) == [2, 0]

def test_top_k_larger_than_array():
    values = np.array([1, 2])
    assert sorted(top_k(values, 5).tolist()) == [0, 1]

def test_2d_matrix_stats_shape():
    rng = np.random.default_rng(0)
    matrix = rng.normal(size=(10, 4))
    assert len(column_stats(matrix)) == 4
"""},
            reference_solution="""import numpy as np


def column_stats(matrix):
    data = np.asarray(matrix, dtype=float)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    return {
        index: {
            "mean": float(data[:, index].mean()),
            "std": float(data[:, index].std()),
            "min": float(data[:, index].min()),
            "max": float(data[:, index].max()),
        }
        for index in range(data.shape[1])
    }


def normalize_rows(matrix):
    data = np.asarray(matrix, dtype=float).copy()
    if data.ndim == 1:
        data = data.reshape(1, -1)
    totals = data.sum(axis=1)
    if data.shape[1]:
        empty = totals == 0
        data[empty] = 1.0 / data.shape[1]
        totals[empty] = 1.0
    return data / totals.reshape(-1, 1)


def top_k(values, k):
    data = np.asarray(values).ravel()
    limit = min(int(k), data.size)
    order = np.argsort(-data)
    return order[:limit]
""",
            hints=(
                "`np.asarray(..., dtype=float)` makes the functions safe for lists too.",
                "`np.where(totals == 0, 1.0, totals)` replaces zero divisors with a neutral value.",
                "`np.argsort(-data)` sorts descending without reversing the array.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `describe(values)` يُعيد إحصاءات وصفية لمصفوفة أرقام:

```python
{
  "count": int, "mean": float, "median": float, "std": float,
  "min": float, "max": float, "p25": float, "p75": float, "iqr": float
}
```

ثم اكتب `detect_outliers(values, k=1.5)` تُعيد فهارس القيم الخارجة عن
`[p25 - k*iqr, p75 + k*iqr]`، و`winsorize(values)` التي تستبدل القيم الخارجة
بحدود النطاق ( clip ) دون تعديل المصفوفة الأصلية.""",
            brief_en="""Write `describe(values)` returning descriptive statistics for a numeric array:

```python
{
  "count": int, "mean": float, "median": float, "std": float,
  "min": float, "max": float, "p25": float, "p75": float, "iqr": float
}
```

Then write `detect_outliers(values, k=1.5)` returning the indices of values outside
`[p25 - k*iqr, p75 + k*iqr]`, and `winsorize(values)` which clips those values to the
bounds without mutating the input array.""",
            independent=True,
            starter_code="""import numpy as np


def describe(values):
    pass


def detect_outliers(values, k=1.5):
    pass


def winsorize(values):
    pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import describe

def test_describe_keys():
    stats = describe(np.array([1.0, 2.0, 3.0, 4.0]))
    assert set(stats) == {"count", "mean", "median", "std", "min", "max", "p25", "p75", "iqr"}
    assert stats["mean"] == 2.5
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import describe, detect_outliers, winsorize

def test_describe_values():
    stats = describe(np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
    assert stats["count"] == 5
    assert stats["median"] == 3.0
    assert stats["min"] == 1.0 and stats["max"] == 5.0

def test_iqr_consistency():
    stats = describe(np.array([2.0, 4.0, 6.0, 8.0]))
    assert abs(stats["iqr"] - (stats["p75"] - stats["p25"])) < 1e-9

def test_no_outliers_in_tight_data():
    values = np.array([10.0, 11.0, 12.0, 13.0])
    assert len(detect_outliers(values)) == 0

def test_detects_single_spike():
    values = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 100.0])
    assert 7 in detect_outliers(values).tolist()

def test_winsorize_clips_and_copies():
    values = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 100.0])
    clipped = winsorize(values)
    assert clipped.max() < 100.0
    assert values.max() == 100.0

def test_winsorize_keeps_normal_values():
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    assert np.allclose(winsorize(values), values)

def test_empty_input_is_safe():
    stats = describe(np.array([]))
    assert stats["count"] == 0
"""},
            reference_solution="""import numpy as np


def describe(values):
    data = np.asarray(values, dtype=float).ravel()
    if data.size == 0:
        return {"count": 0, "mean": 0.0, "median": 0.0, "std": 0.0,
                "min": 0.0, "max": 0.0, "p25": 0.0, "p75": 0.0, "iqr": 0.0}
    p25, p75 = np.percentile(data, [25, 75])
    return {
        "count": int(data.size),
        "mean": float(data.mean()),
        "median": float(np.median(data)),
        "std": float(data.std()),
        "min": float(data.min()),
        "max": float(data.max()),
        "p25": float(p25),
        "p75": float(p75),
        "iqr": float(p75 - p25),
    }


def detect_outliers(values, k=1.5):
    data = np.asarray(values, dtype=float).ravel()
    if data.size == 0:
        return np.array([], dtype=int)
    p25, p75 = np.percentile(data, [25, 75])
    iqr = p75 - p25
    low, high = p25 - k * iqr, p75 + k * iqr
    return np.flatnonzero((data < low) | (data > high))


def winsorize(values):
    data = np.asarray(values, dtype=float)
    if data.size == 0:
        return data.copy()
    p25, p75 = np.percentile(data, [25, 75])
    iqr = p75 - p25
    low, high = p25 - 1.5 * iqr, p75 + 1.5 * iqr
    return np.clip(data, low, high)
""",
        ),
        transfer_ar="استخدم `describe` في Data Empire قبل أي قرار بناءً على توزيع البيانات.",
        transfer_en="Use `describe` in Data Empire before any decision based on a data distribution.",
        references=(
            ("NumPy quickstart", "https://numpy.org/doc/stable/user/quickstart.html"),
            ("NumPy broadcasting", "https://numpy.org/doc/stable/user/basics.broadcasting.html"),
        ),
    ),
    CurriculumModule(
        id="l5.pandas_core",
        level=5,
        order_index=2,
        domain="data_engineering",
        title_ar="جوهر pandas",
        title_en="pandas core",
        summary_ar="DataFrame والفهرسة وgroupby والدمج والتعامل مع القيم المفقودة.",
        summary_en="DataFrame, indexing, groupby, joins and missing values.",
        explanation_ar="""`DataFrame` جدول بأعمدة مسماة وفهرس. أهم ما يجب تثبيته مبكراً:

- **`loc` بالتسمية و`iloc` بالموضع** — الخلط بينهما أشهر مصدر للأخطاء.
- **الاختيار المنطقي**: `df[df["age"] > 30]` يمرّر قناعاً، و`&`/`|` تحتاج أقواساً.
- **`groupby`**: قسّم → طبّق → اجمع. `df.groupby("city")["sales"].agg(["sum", "mean"])`.
- **الدمج**: `merge` لأعمدة مشتركة (مثل SQL JOIN) و`concat` للتجميع الرأسي/الأفقي.
- **القيم المفقودة**: `isna()`, `dropna()`, `fillna()`. NaN لا يساوي نفسه،
  فاستخدم `pd.isna` لا `== None`.
- **النسخ مقابل العرض**: `df[df.a > 1]["b"] = 5` (chained assignment) قد لا يفعل شيئاً؛
  استخدم `df.loc[mask, "b"] = 5`.

انتبه لأخطاء شائعة: تعديل DataFrame أثناء التكرار عليه، واستخدام `apply` حيث تكفي
عملية موجّهة (أبطأ بكثير).""",
        explanation_en="""A `DataFrame` is a table with named columns and an index. Nail these early:

- **`loc` is by label, `iloc` is by position** - mixing them up is the classic bug.
- **Boolean selection**: `df[df["age"] > 30]` passes a mask, and `&`/`|` need parentheses.
- **`groupby`**: split -> apply -> combine. `df.groupby("city")["sales"].agg(["sum", "mean"])`.
- **Combining**: `merge` on shared columns (like a SQL JOIN) and `concat` for stacking.
- **Missing values**: `isna()`, `dropna()`, `fillna()`. NaN is not equal to itself, so use
  `pd.isna`, never `== None`.
- **Copy vs view**: `df[df.a > 1]["b"] = 5` (chained assignment) may do nothing; write
  `df.loc[mask, "b"] = 5` instead.

Watch for classic mistakes: mutating a frame while iterating over it, and reaching for
`apply` where a vectorised operation would do (much slower).""",
        skills=("data.pandas", "data.joins"),
        prerequisites=("l5.numpy_foundations",),
        example_code="""import pandas as pd

orders = pd.DataFrame(
    {
        "city": ["Jeddah", "Riyadh", "Jeddah", "Riyadh", "Dammam"],
        "amount": [120.0, 80.0, 200.0, None, 50.0],
        "items": [2, 1, 3, 1, 1],
    }
)

print(orders)
print("\\ndtypes:\\n", orders.dtypes)
print("\\nmissing per column:\\n", orders.isna().sum())

print("\\nloc/iloc:")
print("row 1 by position:\\n", orders.iloc[1])
print("cities of the first two rows:", orders.loc[:1, "city"].tolist())

print("\\ngroupby:")
summary = orders.groupby("city")["amount"].agg(["count", "sum", "mean"]).round(2)
print(summary)

print("\\nfilter + assign:")
big = orders[orders["amount"].fillna(0) > 70]
print(big[["city", "amount"]])

customers = pd.DataFrame({"city": ["Jeddah", "Riyadh", "Dammam"], "region": ["west", "central", "east"]})
print("\\nmerge:")
print(orders.merge(customers, on="city", how="left").head(3))
""",
        example_notes_ar="لاحظ أن `count` في groupby يتجاهل NaN بينما `size` لا يتجاهله.",
        example_notes_en="Note that `count` in groupby skips NaN while `size` does not.",
        experiment_code="""import numpy as np
import pandas as pd

rng = np.random.default_rng(3)
frame = pd.DataFrame(
    {
        "team": rng.choice(["alpha", "beta", "gamma"], size=300),
        "score": rng.normal(70, 12, size=300).round(1),
        "minutes": rng.integers(5, 60, size=300),
    }
)
frame.loc[rng.choice(frame.index, size=15, replace=False), "score"] = np.nan

print("rows:", len(frame))
print(frame.groupby("team")["score"].agg(["count", "mean", "std"]).round(2))

frame["score"] = frame["score"].fillna(frame.groupby("team")["score"].transform("mean"))
print("\\nafter filling by team mean, missing:", int(frame["score"].isna().sum()))

frame["band"] = pd.cut(frame["score"], bins=[0, 60, 75, 100], labels=["low", "mid", "high"])
print("\\nbands:\\n", frame["band"].value_counts())
print("\\ncrosstab:\\n", pd.crosstab(frame["team"], frame["band"]))

pivot = frame.pivot_table(index="team", columns="band", values="minutes", aggfunc="mean")
print("\\npivot:\\n", pivot.round(1))
""",
        experiment_brief_ar="أضف عمود `efficiency = score / minutes` ثم ابحث عن أفضل فريق به.",
        experiment_brief_en="Add an `efficiency = score / minutes` column and find the best team by it.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `safe_load(records)` تُبني DataFrame من قائمة قواميس مع أعمدة `["user", "event", "value"]`
   وتُعيد `(frame, report)` حيث `report` قاموس يصف القيم المفقودة وعدد الصفوف المكرّرة.
2. `top_users(frame, n=3)` تُعيد DataFrame بأعلى `n` مستخدمين حسب مجموع `value`.
3. `add_share(frame)` تُضيف عمود `share` = نسبة كل صف من مجموع `value` الإجمالي.""",
            brief_en="""Write:
1. `safe_load(records)` building a DataFrame from a list of dicts with columns
   `["user", "event", "value"]` and returning `(frame, report)` where `report` describes
   missing values and duplicate-row counts.
2. `top_users(frame, n=3)` returning a DataFrame of the top `n` users by total `value`.
3. `add_share(frame)` adding a `share` column: each row's fraction of the total `value`.""",
            starter_code="""import pandas as pd


def safe_load(records):
    pass


def top_users(frame, n=3):
    pass


def add_share(frame):
    pass
""",
            public_tests={"test_public.py": """from main import safe_load

def test_safe_load():
    frame, report = safe_load([
        {"user": "a", "event": "click", "value": 2.0},
        {"user": "b", "event": "click", "value": 3.0},
    ])
    assert list(frame.columns) == ["user", "event", "value"]
    assert report["rows"] == 2
"""},
            hidden_tests={"test_hidden.py": """import pandas as pd
from main import safe_load, top_users, add_share

RECORDS = [
    {"user": "a", "event": "click", "value": 5.0},
    {"user": "a", "event": "view", "value": 3.0},
    {"user": "b", "event": "click", "value": 7.0},
    {"user": "c", "event": "view", "value": None},
]

def test_report_missing():
    frame, report = safe_load(RECORDS)
    assert report["missing_value"] == 1

def test_report_duplicates():
    frame, report = safe_load(RECORDS + [dict(RECORDS[0])])
    assert report["duplicate_rows"] == 1

def test_top_users():
    frame, _ = safe_load(RECORDS)
    result = top_users(frame, n=2)
    assert result.index.tolist() == ["a", "b"] or result["user"].tolist()[:1] == ["a"]

def test_top_users_totals():
    frame, _ = safe_load(RECORDS)
    result = top_users(frame, n=1)
    assert float(result.iloc[0]["value"]) == 8.0

def test_add_share():
    frame, _ = safe_load(RECORDS)
    with_share = add_share(frame)
    assert abs(with_share["share"].sum() - 1.0) < 1e-9

def test_add_share_does_not_mutate():
    frame, _ = safe_load(RECORDS)
    add_share(frame)
    assert "share" not in frame.columns

def test_missing_input_columns():
    frame, report = safe_load([{"user": "a"}])
    assert list(frame.columns) == ["user", "event", "value"]
    assert report["rows"] == 1
"""},
            reference_solution="""import pandas as pd

COLUMNS = ["user", "event", "value"]


def safe_load(records):
    frame = pd.DataFrame(list(records))
    for column in COLUMNS:
        if column not in frame.columns:
            frame[column] = None
    frame = frame[COLUMNS]
    report = {
        "rows": int(len(frame)),
        "missing_value": int(frame["value"].isna().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
    }
    return frame, report


def top_users(frame, n=3):
    totals = frame.groupby("user", dropna=False)["value"].sum().sort_values(ascending=False)
    return totals.head(n).reset_index()


def add_share(frame):
    result = frame.copy()
    total = result["value"].sum()
    if total == 0 or pd.isna(total):
        result["share"] = 0.0
    else:
        result["share"] = result["value"].fillna(0.0) / total
    return result
""",
            hints=(
                "Reindex with the expected column list so missing columns become NaN instead of KeyError.",
                "`frame.duplicated().sum()` counts fully duplicated rows.",
                "Copy before adding a column when the caller does not expect mutation.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""لديك جدولان: `orders(order_id, user_id, amount)` و`users(user_id, city, signed_up)`.
اكتب:
1. `join_orders(orders, users)` دمج يسار (left join) مع الإبلاغ عن الطلبات بلا مستخدم
   عبر حقل `report["orphan_orders"]`.
2. `city_revenue(frame)` تُعيد DataFrame مرتّباً تنازلياً فيه `city, revenue, orders, avg_order`.
3. `monthly_trend(frame, date_column="signed_up")` تُعيد سلسلة زمنية شهرية لعدد الطلبات
   (استخدم `pd.Grouper` أو `dt.to_period`).""",
            brief_en="""You have two tables: `orders(order_id, user_id, amount)` and
`users(user_id, city, signed_up)`. Write:
1. `join_orders(orders, users)` - a left join reporting orders without a user through
   `report["orphan_orders"]`.
2. `city_revenue(frame)` - a DataFrame sorted descending with `city, revenue, orders, avg_order`.
3. `monthly_trend(frame, date_column="signed_up")` - a monthly time series of order counts
   (use `pd.Grouper` or `dt.to_period`).""",
            independent=True,
            starter_code="""import pandas as pd


def join_orders(orders, users):
    pass


def city_revenue(frame):
    pass


def monthly_trend(frame, date_column="signed_up"):
    pass
""",
            public_tests={"test_public.py": """import pandas as pd
from main import join_orders

def test_join():
    orders = pd.DataFrame({"order_id": [1, 2], "user_id": [10, 99], "amount": [5.0, 7.0]})
    users = pd.DataFrame({"user_id": [10], "city": ["Jeddah"]})
    joined, report = join_orders(orders, users)
    assert len(joined) == 2
    assert report["orphan_orders"] == 1
"""},
            hidden_tests={"test_hidden.py": """import pandas as pd
from main import join_orders, city_revenue, monthly_trend

ORDERS = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4, 5],
        "user_id": [10, 11, 10, 12, 99],
        "amount": [100.0, 50.0, 25.0, 10.0, 5.0],
    }
)
USERS = pd.DataFrame(
    {
        "user_id": [10, 11, 12],
        "city": ["Jeddah", "Riyadh", "Jeddah"],
        "signed_up": pd.to_datetime(["2024-01-05", "2024-01-20", "2024-02-02"]),
    }
)

def test_join_keeps_all_orders():
    joined, _ = join_orders(ORDERS, USERS)
    assert len(joined) == 5

def test_city_for_unknown_user():
    joined, _ = join_orders(ORDERS, USERS)
    row = joined[joined["order_id"] == 5].iloc[0]
    assert pd.isna(row["city"])

def test_city_revenue_sorted():
    joined, _ = join_orders(ORDERS, USERS)
    revenue = city_revenue(joined)
    assert revenue["city"].tolist()[0] == "Jeddah"
    assert float(revenue.iloc[0]["revenue"]) == 135.0

def test_city_revenue_columns():
    joined, _ = join_orders(ORDERS, USERS)
    assert list(city_revenue(joined).columns) == ["city", "revenue", "orders", "avg_order"]

def test_city_revenue_avg():
    joined, _ = join_orders(ORDERS, USERS)
    row = city_revenue(joined).iloc[0]
    assert abs(row["avg_order"] - row["revenue"] / row["orders"]) < 1e-9

def test_monthly_trend_counts():
    joined, _ = join_orders(ORDERS, USERS)
    trend = monthly_trend(joined)
    assert len(trend) >= 2
    assert int(trend.sum()) == 4
"""},
            reference_solution="""import pandas as pd


def join_orders(orders, users):
    joined = orders.merge(users, on="user_id", how="left", validate="many_to_one")
    report = {"orphan_orders": int(joined["user_id"].isna().sum() + joined["city"].isna().sum()
                                   if "city" in joined else 0)}
    if "city" in joined.columns:
        report["orphan_orders"] = int(joined["city"].isna().sum())
    return joined, report


def city_revenue(frame):
    known = frame.dropna(subset=["city"])
    grouped = known.groupby("city")["amount"].agg(["sum", "count"]).reset_index()
    grouped.columns = ["city", "revenue", "orders"]
    grouped["avg_order"] = grouped["revenue"] / grouped["orders"]
    return grouped.sort_values("revenue", ascending=False).reset_index(drop=True)


def monthly_trend(frame, date_column="signed_up"):
    data = frame.dropna(subset=[date_column]).copy()
    period = pd.to_datetime(data[date_column]).dt.to_period("M")
    return data.groupby(period).size().sort_index()
""",
        ),
        transfer_ar="استخدم نفس النمط في Data Empire لبناء لوحة إيرادات المدن.",
        transfer_en="Reuse the same pattern in Data Empire to build a city revenue board.",
        references=(
            ("pandas user guide", "https://pandas.pydata.org/docs/user_guide/index.html"),
            ("pandas groupby", "https://pandas.pydata.org/docs/user_guide/groupby.html"),
        ),
    ),
    CurriculumModule(
        id="l5.data_cleaning",
        level=5,
        order_index=3,
        domain="data_engineering",
        title_ar="تنظيف البيانات",
        title_en="Data cleaning",
        summary_ar="بيانات حقيقية فوضوية: أسماء أعمدة، أنواع، تكرارات، قيم شاذة، ونصوص.",
        summary_en="Messy real data: column names, types, duplicates, outliers and text.",
        explanation_ar="""أغلب وقت العمل الحقيقي يُصرف في التنظيف لا في النمذجة. قائمة تحقق عملية:

1. **أسماء الأعمدة**: وحّدها (صغيرة، شرطات سفلية، بلا مسافات) قبل أي شيء.
2. **الأنواع**: حوّل الأرقام المكتوبة كنصوص بـ `pd.to_numeric(errors="coerce")`،
   والتواريخ بـ `pd.to_datetime(errors="coerce")` — معامل `errors` يحافظ على التدفق.
3. **التكرارات**: حدّد مفتاحاً منطقياً (`subset=["email"]`) لا كل الصف.
4. **القيم المفقودة**: اسأل لماذا فُقدت. أحياناً الملء بصفر يدمّر المعنى؛
   أحياناً المتوسط أو القيمة السابقة (forward fill) هو الصحيح.
5. **القيم الشاذة**: لا تحذفها تلقائياً. افحصها: قد تكون خطأ إدخال أو أهم صف في الجدول.
6. **النصوص**: قصّ المسافات، ووحّد الحالة عند المقارنة.
7. **سجّل كل خطوة**: دالة تنظيف جيدة تُعيد تقريراً بما غيّرته.""",
        explanation_en="""Most real work goes into cleaning, not modelling. A practical checklist:

1. **Column names**: normalise them (lower case, underscores, no spaces) first.
2. **Types**: coerce numeric-looking text with `pd.to_numeric(errors="coerce")` and dates with
   `pd.to_datetime(errors="coerce")` - the `errors` argument keeps the pipeline flowing.
3. **Duplicates**: define a logical key (`subset=["email"]`), not the whole row.
4. **Missing values**: ask why they are missing. Filling with zero can destroy meaning;
   sometimes the mean or a forward fill is right.
5. **Outliers**: never drop them automatically. Inspect them - they may be a typo or the most
   important row in the table.
6. **Text**: strip whitespace and normalise case before comparing.
7. **Log every step**: a good cleaning function returns a report of what it changed.""",
        skills=("data.cleaning", "data.pandas", "pro.typing"),
        prerequisites=("l5.pandas_core",),
        example_code="""import pandas as pd

raw = pd.DataFrame(
    {
        " Full Name ": ["  Aisha  ", "Omar", "AISHA", None, "Layla"],
        "Age": ["28", "31", "28", "not given", "45"],
        "signup-date": ["2024-01-02", "2024-01-03", "2024-01-02", "", "2024-03-01"],
        "email": ["a@x.com", "o@x.com", "a@x.com", "g@x.com", "l@x.com"],
    }
)

print("raw:\\n", raw)
print("\\nraw dtypes:\\n", raw.dtypes)

frame = raw.copy()
frame.columns = [column.strip().lower().replace(" ", "_").replace("-", "_") for column in frame.columns]
print("\\nnormalised columns:", list(frame.columns))

frame["age"] = pd.to_numeric(frame["age"], errors="coerce")
frame["signup_date"] = pd.to_datetime(frame["signup_date"], errors="coerce")
frame["full_name"] = frame["full_name"].astype("string").str.strip().str.title()
frame["email"] = frame["email"].astype("string").str.strip().str.lower()

print("\\ncleaned:\\n", frame)
print("\\nmissing:\\n", frame.isna().sum())
print("duplicate emails:", int(frame["email"].duplicated().sum()))
""",
        example_notes_ar="`astype(\"string\")` يحافظ على القيم المفقودة كـ `<NA>` بخلاف `astype(str)` الذي يحوّلها إلى نص `None`.",
        example_notes_en="`astype(\"string\")` keeps missing values as `<NA>`, unlike `astype(str)` which turns them into the text `None`.",
        experiment_code="""import numpy as np
import pandas as pd

rng = np.random.default_rng(11)
frame = pd.DataFrame(
    {
        "sensor": ["s1", "s2", "s1", "s2", "s1", "s2", "s1", "s2"],
        "reading": [20.1, 19.8, 20.5, 999.9, 20.2, -50.0, 20.4, 20.0],
    }
)

print("raw:\\n", frame)
print("\\nraw mean:", round(float(frame['reading'].mean()), 2), "  <- destroyed by outliers")

def flag_outliers(group):
    median = group["reading"].median()
    deviation = (group["reading"] - median).abs()
    scale = deviation.median() or 1.0
    return deviation > 6 * scale

frame["suspect"] = frame.groupby("sensor", group_keys=False).apply(flag_outliers)
print("\\nsuspect rows:\\n", frame[frame["suspect"]])

frame["reading_clean"] = frame["reading"].where(~frame["suspect"])
frame["reading_clean"] = frame.groupby("sensor")["reading_clean"].transform(
    lambda series: series.fillna(series.median())
)
print("\\nclean mean:", round(float(frame['reading_clean'].mean()), 2))
print(frame)
""",
        experiment_brief_ar="طبّق نفس المنطق على مجموعة بياناتك في Data Empire وفسّر سبب اختيار الوسيط (median).",
        experiment_brief_en="Apply the same logic to your dataset in Data Empire and explain why the median was chosen.",
        task=TaskSpec(
            brief_ar="""اكتب `clean_dataframe(frame)` يقوم بـ:
- توحيد أسماء الأعمدة (صغيرة، شرطات سفلية، مسافات مُقلّمة)،
- تحويل الأعمدة التي تبدو رقمية إلى أرقام (`errors="coerce"`)،
- قصّ المسافات من كل الأعمدة النصية،
- حذف الصفوف المكرّرة بالكامل،
ويُعيد `(clean_frame, report)` حيث `report` قاموس فيه:
`{"columns_renamed", "numeric_columns", "rows_dropped", "missing_before", "missing_after"}`.""",
            brief_en="""Write `clean_dataframe(frame)` which:
- normalises column names (lower case, underscores, trimmed),
- coerces columns that look numeric into numbers (`errors="coerce"`),
- strips whitespace from every text column,
- drops fully duplicated rows,
and returns `(clean_frame, report)` where `report` has:
`{"columns_renamed", "numeric_columns", "rows_dropped", "missing_before", "missing_after"}`.""",
            starter_code="""import pandas as pd


def clean_dataframe(frame):
    pass
""",
            public_tests={"test_public.py": """import pandas as pd
from main import clean_dataframe

def test_names_normalised():
    frame = pd.DataFrame({"Full Name": [" a "], "Age": ["30"]})
    clean, report = clean_dataframe(frame)
    assert list(clean.columns) == ["full_name", "age"]
    assert report["columns_renamed"] == 2
"""},
            hidden_tests={"test_hidden.py": """import pandas as pd
from main import clean_dataframe

FRAME = pd.DataFrame(
    {
        "  City  ": [" Jeddah ", "Riyadh", "Jeddah", None],
        "Sales": ["100", "bad", "100", "50"],
        "Units": [1, 2, 1, 3],
    }
)

def test_coerced_numeric():
    clean, report = clean_dataframe(FRAME)
    assert "sales" in report["numeric_columns"]
    assert pd.api.types.is_numeric_dtype(clean["sales"])

def test_bad_value_becomes_nan():
    clean, _ = clean_dataframe(FRAME)
    assert pd.isna(clean.loc[1, "sales"])

def test_strip_text():
    clean, _ = clean_dataframe(FRAME)
    assert clean.loc[0, "city"] == "Jeddah"

def test_duplicates_dropped():
    clean, report = clean_dataframe(FRAME)
    assert report["rows_dropped"] == 1
    assert len(clean) == 3

def test_missing_counts():
    clean, report = clean_dataframe(FRAME)
    assert report["missing_before"] == 1
    assert report["missing_after"] == 2

def test_original_untouched():
    clean_dataframe(FRAME)
    assert list(FRAME.columns) == ["  City  ", "Sales", "Units"]

def test_empty_frame():
    clean, report = clean_dataframe(pd.DataFrame())
    assert len(clean) == 0
    assert report["rows_dropped"] == 0
"""},
            reference_solution="""import pandas as pd


def _normalise(name):
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def clean_dataframe(frame):
    renamed = {}
    missing_before = int(frame.isna().sum().sum())
    for column in frame.columns:
        new_name = _normalise(column)
        if new_name != column:
            renamed[column] = new_name
    clean = frame.rename(columns=renamed)

    numeric_columns = []
    for column in clean.columns:
        series = clean[column]
        if pd.api.types.is_numeric_dtype(series):
            numeric_columns.append(column)
            continue
        if series.dtype == object or pd.api.types.is_string_dtype(series):
            coerced = pd.to_numeric(series, errors="coerce")
            original_na = series.isna().sum()
            new_na = coerced.isna().sum()
            tolerance = max(1, len(clean) // 2)
            if new_na <= original_na + tolerance:
                clean[column] = coerced
                numeric_columns.append(column)
            else:
                clean[column] = series.astype("string").str.strip()

    rows_before = len(clean)
    clean = clean.drop_duplicates().reset_index(drop=True)

    report = {
        "columns_renamed": len(renamed),
        "numeric_columns": numeric_columns,
        "rows_dropped": int(rows_before - len(clean)),
        "missing_before": missing_before,
        "missing_after": int(clean.isna().sum().sum()),
    }
    return clean, report
""",
            hints=(
                "Rename first, then coerce types: the report refers to the new column names.",
                "Compare NaN counts before and after coercion to detect a failed conversion.",
                "`drop_duplicates()` returns a new frame, so capture the result.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب دالة `validate_dataset(frame, schema)` حيث `schema` قاموس
`{"column": {"type": "number"|"text"|"date", "required": bool, "min": .., "max": ..}}`.

تُعيد `(is_valid, errors)` حيث `errors` قائمة نصوص وصفية (اسم العمود + المشكلة).
تحقّق من: الأعمدة الناقصة، القيم المفقودة في الأعمدة المطلوبة، النوع، وحدود القيم.""",
            brief_en="""Write `validate_dataset(frame, schema)` where `schema` is a dict of
`{"column": {"type": "number"|"text"|"date", "required": bool, "min": .., "max": ..}}`.

Return `(is_valid, errors)` where `errors` is a list of readable strings (column name plus
the problem). Check for: missing columns, missing values in required columns, type mismatch
and value bounds.""",
            independent=True,
            starter_code="""import pandas as pd


def validate_dataset(frame, schema):
    pass
""",
            public_tests={"test_public.py": """import pandas as pd
from main import validate_dataset

def test_valid():
    frame = pd.DataFrame({"age": [30], "name": ["a"]})
    ok, errors = validate_dataset(frame, {"age": {"type": "number"}, "name": {"type": "text"}})
    assert ok is True
    assert errors == []
"""},
            hidden_tests={"test_hidden.py": """import pandas as pd
from main import validate_dataset

SCHEMA = {
    "age": {"type": "number", "required": True, "min": 0, "max": 120},
    "name": {"type": "text", "required": True},
    "joined": {"type": "date", "required": False},
}

def test_missing_column():
    ok, errors = validate_dataset(pd.DataFrame({"age": [1]}), SCHEMA)
    assert ok is False
    assert any("name" in e for e in errors)

def test_required_missing_value():
    frame = pd.DataFrame({"age": [30], "name": [None]})
    ok, errors = validate_dataset(frame, SCHEMA)
    assert ok is False
    assert any("name" in e for e in errors)

def test_out_of_bounds():
    frame = pd.DataFrame({"age": [150], "name": ["a"]})
    ok, errors = validate_dataset(frame, SCHEMA)
    assert ok is False
    assert any("age" in e for e in errors)

def test_below_minimum():
    frame = pd.DataFrame({"age": [-5], "name": ["a"]})
    ok, errors = validate_dataset(frame, SCHEMA)
    assert ok is False

def test_wrong_type():
    frame = pd.DataFrame({"age": ["old"], "name": ["a"]})
    ok, errors = validate_dataset(frame, SCHEMA)
    assert ok is False

def test_optional_column_absent_is_fine():
    frame = pd.DataFrame({"age": [30], "name": ["a"]})
    ok, errors = validate_dataset(frame, SCHEMA)
    assert ok is True

def test_valid_date_column():
    frame = pd.DataFrame({
        "age": [30],
        "name": ["a"],
        "joined": pd.to_datetime(["2024-01-01"]),
    })
    ok, errors = validate_dataset(frame, SCHEMA)
    assert ok is True
"""},
            reference_solution="""import pandas as pd


def validate_dataset(frame, schema):
    errors = []

    for column, rules in schema.items():
        if column not in frame.columns:
            if rules.get("required", False):
                errors.append(f"{column}: column is missing")
            continue

        series = frame[column]
        required = rules.get("required", False)
        missing = series.isna().sum()
        if required and missing:
            errors.append(f"{column}: {int(missing)} missing value(s) in a required column")

        expected = rules.get("type")
        present = series.dropna()
        if present.empty:
            continue

        if expected == "number":
            numeric = pd.to_numeric(present, errors="coerce")
            if numeric.isna().any():
                errors.append(f"{column}: not numeric")
                continue
            minimum = rules.get("min")
            maximum = rules.get("max")
            if minimum is not None and (numeric < minimum).any():
                errors.append(f"{column}: value below {minimum}")
            if maximum is not None and (numeric > maximum).any():
                errors.append(f"{column}: value above {maximum}")
        elif expected == "date":
            converted = pd.to_datetime(present, errors="coerce")
            if converted.isna().any():
                errors.append(f"{column}: not a valid date")
        elif expected == "text":
            if not all(isinstance(value, str) for value in present):
                errors.append(f"{column}: not text")

    return (not errors), errors
""",
        ),
        transfer_ar="استخدم `validate_dataset` كبوابة لأي ملف يدخل Data Empire.",
        transfer_en="Use `validate_dataset` as the gate for any file entering Data Empire.",
        references=(
            ("pandas - working with text data", "https://pandas.pydata.org/docs/user_guide/text.html"),
            ("pandas - missing data", "https://pandas.pydata.org/docs/user_guide/missing_data.html"),
        ),
    ),
    CurriculumModule(
        id="l5.etl_pipeline",
        level=5,
        order_index=4,
        domain="data_engineering",
        title_ar="مسار ETL متعدد الملفات",
        title_en="Multi-file ETL pipeline",
        summary_ar="استخراج وتحويل وتحميل: مشروع حقيقي بملفات متعددة واختبارات.",
        summary_en="Extract, transform, load: a real multi-file project with tests.",
        explanation_ar="""مسار ETL الجيد **قابل للاختبار**: كل مرحلة دالة نقية تأخذ بيانات وتُعيد بيانات،
بدون قراءة ملفات أو طباعة في المنتصف.

هندسة مقترحة:

```
pipeline/
  extract.py    - قراءة المصادر وإرجاع DataFrame خام
  transform.py  - تنظيف وإثراء: DataFrame -> DataFrame
  load.py       - كتابة النتائج وإرجاع تقرير
  report.py     - تجميع المقاييس في قاموس
```

قواعد:
- المراحل لا تعتمد على حالة عامة (global state)؛ مرّر كل شيء كوسيط.
- احتفظ بالبيانات الخام: التحويل يجب أن يكون قابلاً للتراجع (re-runnable).
- سجّل مقاييس بعد كل تشغيل (عدد الصفوف الداخل/الخارج، الصفوف المرفوضة).
- اكتب اختبارات لـ `transform` خصوصاً: هي قلب المنطق وأسهل ما يُختبر.""",
        explanation_en="""A good ETL pipeline is **testable**: every stage is a pure function taking data and
returning data, with no file reads or printing in the middle.

A suggested layout:

```
pipeline/
  extract.py    - reads sources, returns a raw DataFrame
  transform.py  - cleans and enriches: DataFrame -> DataFrame
  load.py       - writes results, returns a report
  report.py     - collects metrics into a dict
```

Rules:
- stages must not depend on global state; pass everything as arguments;
- keep the raw data: a transformation must be re-runnable;
- log metrics after every run (rows in/out, rows rejected);
- test `transform` above all: it is where the logic lives and the easiest to test.""",
        skills=("data.pipelines", "data.pandas", "pro.refactoring"),
        prerequisites=("l5.data_cleaning",),
        example_code="""import pandas as pd


def extract(rows):
    return pd.DataFrame(rows)


def transform(frame):
    frame = frame.copy()
    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce")
    frame = frame.dropna(subset=["amount"])
    frame["tax"] = (frame["amount"] * 0.15).round(2)
    frame["total"] = (frame["amount"] + frame["tax"]).round(2)
    return frame.reset_index(drop=True)


def load(frame):
    return {"rows": len(frame), "revenue": float(frame["amount"].sum())}


raw = extract([
    {"id": 1, "amount": "100"},
    {"id": 2, "amount": "bad"},
    {"id": 3, "amount": "50"},
])
print("raw rows     :", len(raw))
cleaned = transform(raw)
print("cleaned rows :", len(cleaned))
print(cleaned)
print("report       :", load(cleaned))
""",
        example_notes_ar="لاحظ أن `transform` تستقبل وتُعيد DataFrame فقط — لا ملفات ولا طباعة، وهذا ما يجعلها قابلة للاختبار.",
        example_notes_en="Note that `transform` only takes and returns a DataFrame - no files, no printing. That is what makes it testable.",
        experiment_code="""import pandas as pd

SOURCES = {
    "2024-01": pd.DataFrame({"city": ["Jeddah", "Riyadh"], "amount": [10.0, 20.0]}),
    "2024-02": pd.DataFrame({"city": ["Jeddah", "Dammam"], "amount": [30.0, 5.0]}),
}


def concat_with_key(sources):
    frames = [frame.assign(period=period) for period, frame in sources.items()]
    return pd.concat(frames, ignore_index=True)


combined = concat_with_key(SOURCES)
print(combined)
print("\\npivot by period and city:\\n", combined.pivot_table(
    index="period", columns="city", values="amount", aggfunc="sum", fill_value=0
))

running = combined.sort_values("period").groupby("city")["amount"].cumsum()
print("\\ncumulative per city:\\n", running.tolist())
""",
        experiment_brief_ar="أضف مرحلة ترفض المدن التي يقل مجموع مبيعاتها عن حد معين، مع الإبلاغ عن المرفوض.",
        experiment_brief_en="Add a stage that rejects cities below a sales threshold, reporting what was rejected.",
        task=TaskSpec(
            entry_filename="pipeline/transform.py",
            extra_files={
                "pipeline/__init__.py": "",
                "pipeline/extract.py": '''"""Read raw records into a DataFrame."""
from __future__ import annotations

import pandas as pd

COLUMNS = ["id", "city", "amount", "date"]


def extract(rows):
    """Return a DataFrame with the columns id, city, amount, date."""
    frame = pd.DataFrame(list(rows))
    for column in COLUMNS:
        if column not in frame.columns:
            frame[column] = None
    return frame[COLUMNS]
''',
                "pipeline/load.py": '''"""Write results and build a run report."""
from __future__ import annotations


def load(frame):
    """Return a metrics dict describing the loaded frame."""
    return {
        "rows": int(len(frame)),
        "revenue": float(frame["amount"].sum()) if len(frame) else 0.0,
        "big_orders": int(frame["is_big"].sum()) if "is_big" in frame else 0,
        "cities": int(frame["city"].nunique(dropna=True)) if "city" in frame else 0,
    }
''',
            },
            brief_ar="""المشروع في `pipeline/`. الملفان `extract.py` و`load.py` مكتوبان وجاهزان؛
مهمتك هي قلب المسار: `transform.py`.

- `extract.py` (جاهز): `extract(rows)` يُعيد DataFrame بأعمدة
  `["id", "city", "amount", "date"]`.
- `transform.py` (ملفك الرئيسي): نفّذ `transform(frame)` التي
  1. تحوّل `amount` إلى رقم،
  2. تحوّل `date` إلى تاريخ،
  3. تحذف الصفوف التي لا يمكن تحديد مبلغها،
  4. تُضيف عمود `is_big` للصفوف التي يتجاوز مبلغها `1000`,
  5. تُعيد الإطار مرتّباً تنازلياً حسب `amount` ومُعاد تعيين فهرسه.
- `load.py` (جاهز): `load(frame)` يُعيد `{"rows", "revenue", "big_orders", "cities"}`.""",
            brief_en="""The project lives in `pipeline/`. `extract.py` and `load.py` are written for you;
your job is the heart of the pipeline: `transform.py`.

- `extract.py` (provided): `extract(rows)` returning a DataFrame with columns
  `["id", "city", "amount", "date"]`.
- `transform.py` (your entry file): implement `transform(frame)` which
  1. coerces `amount` to numeric,
  2. coerces `date` to datetime,
  3. drops rows whose amount cannot be determined,
  4. adds an `is_big` column for rows above `1000`,
  5. returns the frame sorted descending by `amount` with a reset index.
- `load.py` (provided): `load(frame)` returning `{"rows", "revenue", "big_orders", "cities"}`.""",
            starter_code='''"""Clean and enrich the extracted orders."""
from __future__ import annotations

import pandas as pd


def transform(frame):
    # TODO
    return frame
''',
            public_tests={
                "test_public.py": """import pandas as pd
from pipeline.transform import transform

def test_transform_drops_bad_amounts():
    frame = pd.DataFrame({"id": [1, 2], "city": ["a", "b"], "amount": ["10", "x"]})
    assert len(transform(frame)) == 1
"""},
            hidden_tests={
                "test_hidden.py": """import pandas as pd
from pipeline.transform import transform
from pipeline.extract import extract
from pipeline.load import load

def make_frame():
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "city": ["Jeddah", "Riyadh", "Jeddah", "Dammam"],
            "amount": ["100", "2000", "bad", "50"],
            "date": ["2024-01-01", "2024-02-01", "2024-03-01", ""],
        }
    )

def test_sorted_descending():
    result = transform(make_frame())
    assert result["amount"].tolist() == [2000.0, 100.0, 50.0]

def test_is_big_flag():
    result = transform(make_frame())
    assert bool(result.iloc[0]["is_big"]) is True
    assert bool(result.iloc[-1]["is_big"]) is False

def test_date_parsed():
    result = transform(make_frame())
    assert result["date"].notna().sum() == 2

def test_index_reset():
    result = transform(make_frame())
    assert result.index.tolist() == [0, 1, 2]

def test_original_not_mutated():
    frame = make_frame()
    transform(frame)
    assert len(frame) == 4

def test_extract_columns():
    frame = extract([{"id": 1}])
    assert list(frame.columns) == ["id", "city", "amount", "date"]

def test_load_metrics():
    result = transform(make_frame())
    metrics = load(result)
    assert set(metrics) == {"rows", "revenue", "big_orders", "cities"}
    assert metrics["rows"] == 3
    assert metrics["revenue"] == 2150.0
    assert metrics["big_orders"] == 1
    assert metrics["cities"] == 3
"""},
            reference_solution='''"""Clean and enrich the extracted orders."""
from __future__ import annotations

import pandas as pd

COLUMNS = ["id", "city", "amount", "date"]


def transform(frame):
    result = frame.copy()
    for column in COLUMNS:
        if column not in result.columns:
            result[column] = None
    result["amount"] = pd.to_numeric(result["amount"], errors="coerce")
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result.dropna(subset=["amount"])
    result["is_big"] = result["amount"] > 1000
    result = result.sort_values("amount", ascending=False)
    return result.reset_index(drop=True)
''',
            hints=(
                "`pd.to_datetime(..., errors=\"coerce\")` turns an empty string into NaT, not an exception.",
                "Reset the index after sorting so positional access keeps working.",
                "Copy the frame before mutating: the caller may still need the raw data.",
            ),
        ),
        assessment=TaskSpec(
            entry_filename="pipeline/quality.py",
            brief_ar="""أضف وحدة `quality.py` إلى المشروع تحتوي:

- `profile(frame)` تُعيد قاموساً لكل عمود: `{"dtype", "missing", "unique", "sample"}`.
- `compare_runs(before, after)` تُعيد `{"rows_before", "rows_after", "rows_removed",
  "revenue_before", "revenue_after"}` لمقارنة نتيجتي تشغيل.
- `assert_quality(frame, max_missing_ratio=0.1)` ترفع `ValueError` إذا تجاوزت نسبة القيم
  المفقودة في أي عمود الحد المسموح.""",
            brief_en="""Add a `quality.py` module to the project containing:

- `profile(frame)` returning, per column, `{"dtype", "missing", "unique", "sample"}`.
- `compare_runs(before, after)` returning `{"rows_before", "rows_after", "rows_removed",
  "revenue_before", "revenue_after"}` to compare two runs.
- `assert_quality(frame, max_missing_ratio=0.1)` raising `ValueError` when any column's
  missing ratio exceeds the allowed limit.""",
            independent=True,
            starter_code='''"""Data quality gates for the pipeline."""
from __future__ import annotations

import pandas as pd


def profile(frame):
    pass


def compare_runs(before, after):
    pass


def assert_quality(frame, max_missing_ratio=0.1):
    pass
''',
            public_tests={"test_public.py": """import pandas as pd
from pipeline.quality import profile

def test_profile_keys():
    frame = pd.DataFrame({"a": [1, 2, 2]})
    assert set(profile(frame)["a"]) == {"dtype", "missing", "unique", "sample"}
"""},
            hidden_tests={"test_hidden.py": """import pandas as pd
import pytest
from pipeline.quality import profile, compare_runs, assert_quality

def test_profile_counts():
    frame = pd.DataFrame({"a": [1, 2, 2, None]})
    info = profile(frame)["a"]
    assert info["missing"] == 1
    assert info["unique"] == 2

def test_profile_sample_present():
    frame = pd.DataFrame({"a": [7]})
    assert profile(frame)["a"]["sample"] is not None

def test_compare_runs():
    before = pd.DataFrame({"id": [1, 2, 3], "amount": [10.0, 10.0, 10.0]})
    after = pd.DataFrame({"id": [1, 2], "amount": [10.0, 5.0]})
    report = compare_runs(before, after)
    assert report == {
        "rows_before": 3,
        "rows_after": 2,
        "rows_removed": 1,
        "revenue_before": 30.0,
        "revenue_after": 15.0,
    }

def test_assert_quality_passes():
    frame = pd.DataFrame({"a": [1, 2, 3, 4, 5, 6, 7, 8, 9]})
    assert assert_quality(frame) is True

def test_assert_quality_raises():
    frame = pd.DataFrame({"a": [1, None]})
    with pytest.raises(ValueError):
        assert_quality(frame)

def test_assert_quality_custom_limit():
    frame = pd.DataFrame({"a": [1, None]})
    assert assert_quality(frame, max_missing_ratio=0.6) is True

def test_empty_frame():
    assert profile(pd.DataFrame()) == {}
"""},
            reference_solution='''"""Data quality gates for the pipeline."""
from __future__ import annotations

import pandas as pd


def profile(frame):
    report = {}
    for column in frame.columns:
        series = frame[column]
        report[column] = {
            "dtype": str(series.dtype),
            "missing": int(series.isna().sum()),
            "unique": int(series.nunique(dropna=True)),
            "sample": None if series.dropna().empty else series.dropna().iloc[0],
        }
    return report


def compare_runs(before, after):
    revenue_before = float(pd.to_numeric(before["amount"], errors="coerce").fillna(0).sum()) if len(before) else 0.0
    revenue_after = float(pd.to_numeric(after["amount"], errors="coerce").fillna(0).sum()) if len(after) else 0.0
    return {
        "rows_before": int(len(before)),
        "rows_after": int(len(after)),
        "rows_removed": int(len(before) - len(after)),
        "revenue_before": revenue_before,
        "revenue_after": revenue_after,
    }


def assert_quality(frame, max_missing_ratio=0.1):
    if len(frame) == 0:
        return True
    for column in frame.columns:
        ratio = frame[column].isna().mean()
        if ratio > max_missing_ratio:
            raise ValueError(f"column {column} is {ratio:.0%} missing (limit {max_missing_ratio:.0%})")
    return True
''',
        ),
        transfer_ar="استخدم نفس الهيكل في Data Empire لبناء مسار بيانات ليلي مع بوابة جودة.",
        transfer_en="Reuse the same structure in Data Empire to build a nightly data pipeline with a quality gate.",
        references=(
            ("pandas - reshaping and pivot tables", "https://pandas.pydata.org/docs/user_guide/reshaping.html"),
            ("The Pragmatic Programmer on pipelines", "https://en.wikipedia.org/wiki/Extract,_transform,_load"),
        ),
    ),
]
