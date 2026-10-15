"""LEVEL 11 - Capstone: planning, an end-to-end pipeline and code review tooling."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l11.project_planning",
        level=11,
        order_index=1,
        domain="capstone",
        title_ar="تخطيط المشروع والمسار الحرج",
        title_en="Project planning and the critical path",
        summary_ar="تبعية المهام، أطول مسار، ومحاكاة تأخير قبل أن يحدث.",
        summary_en="Task dependencies, the longest path and simulating delay before it happens.",
        explanation_ar="""المشروع شبكة مهام مرتبطة بتبعيات. السؤال العملي الوحيد المهم:
**ما الذي يؤخّر التسليم فعلاً؟**

المسار الحرج هو أطول سلسلة تبعيات في الشبكة. أي تأخير فيه يؤخّر التسليم
بنفس المقدار؛ وتأخير مهمة خارجه قد لا يؤثّر شيئاً حتى يستنفد "المجال" (slack).

الخوارزمية (على رسم DAG):
1. **الترتيب الطوبولوجي** للتبعيات (Kahn)،
2. **المرور الأمامي**: أقرب بداية لكل مهمة = `max(أقرب نهاية لكل تبعية)`،
3. **المرور الخلفي**: آخر بداية مسموح = `min(آخر بداية للتبعيات اللاحقة) - المدة`،
4. **المجال** = آخر بداية − أقرب بداية. المهام ذات المجال صفر هي الحرجة،
5. أطول مسار = `max(أقرب نهاية)` = أقل زمن للتسليم.

بهذا يمكنك الإجابة بثقة: "هذه المهمة تؤخّرنا يومين، وتلك أسبوعان".""",
        explanation_en="""A project is a network of tasks linked by dependencies. The only practical question that
matters: **what actually delays delivery?**

The critical path is the longest chain of dependencies in the network. Any delay on it delays
delivery by the same amount; a delay off it may change nothing until the slack is exhausted.

The algorithm (over a DAG):
1. **topological order** the dependencies (Kahn),
2. **forward pass**: earliest start of a task = `max(earliest finish of its dependencies)`,
3. **backward pass**: latest allowed start = `min(latest start of successors) - duration`,
4. **slack** = latest start - earliest start. Tasks with zero slack are critical,
5. the longest path is `max(earliest finish)` = the minimum delivery time.

With this you can answer confidently: "this task costs us two days, that one two weeks".""",
        skills=("career.delivery", "ds.graphs"),
        prerequisites=("l6.graphs",),
        example_code="""from collections import deque

TASKS = [
    {"id": "design", "duration": 3, "depends": []},
    {"id": "ingest", "duration": 4, "depends": ["design"]},
    {"id": "features", "duration": 5, "depends": ["ingest"]},
    {"id": "model", "duration": 6, "depends": ["features"]},
    {"id": "report", "duration": 2, "depends": ["ingest"]},
    {"id": "launch", "duration": 1, "depends": ["model", "report"]},
]

by_id = {task["id"]: task for task in TASKS}
successors = {task["id"]: [] for task in TASKS}
indegree = {task["id"]: 0 for task in TASKS}
for task in TASKS:
    for dependency in task["depends"]:
        successors[dependency].append(task["id"])
        indegree[task["id"]] += 1

queue = deque(sorted(task_id for task_id, degree in indegree.items() if degree == 0))
order = []
while queue:
    node = queue.popleft()
    order.append(node)
    for successor in successors[node]:
        indegree[successor] -= 1
        if indegree[successor] == 0:
            queue.append(successor)

earliest_finish = {}
for task_id in order:
    start = max([earliest_finish.get(dep, 0) for dep in by_id[task_id]["depends"]] or [0])
    earliest_finish[task_id] = start + by_id[task_id]["duration"]

latest_finish = {}
project_end = max(earliest_finish.values())
for task_id in reversed(order):
    children = [dep for dep in successors if task_id in by_id[dep]["depends"]]
    latest_finish[task_id] = min([latest_finish.get(child, project_end) for child in children] or [project_end]) 

print("order        :", order)
print("earliest end :", earliest_finish)
print("project end  :", project_end)
print("critical     :", sorted(t for t in order if earliest_finish[t] == project_end or
                               (by_id[t] and project_end - earliest_finish[t] == 0)))
""",
        example_notes_ar="المسار الحرج هنا `design → ingest → features → model → launch` = 19 يوماً.",
        example_notes_en="The critical path here is `design -> ingest -> features -> model -> launch` = 19 days.",
        experiment_code="""TASKS = [
    {"id": "a", "duration": 3, "depends": []},
    {"id": "b", "duration": 4, "depends": ["a"]},
    {"id": "c", "duration": 2, "depends": ["a"]},
    {"id": "d", "duration": 5, "depends": ["b"]},
    {"id": "e", "duration": 1, "depends": ["c"]},
]


def finish(tasks, delays=None):
    delays = delays or {}
    by_id = {task["id"]: task for task in tasks}
    cache = {}

    def compute(task_id):
        if task_id in cache:
            return cache[task_id]
        duration = by_id[task_id]["duration"] + delays.get(task_id, 0)
        cache[task_id] = max([compute(dep) for dep in by_id[task_id]["depends"]] or [0]) + duration
        return cache[task_id]

    return max(compute(task["id"]) for task in tasks)


print("baseline finish:", finish(TASKS))
for task_id in ("a", "b", "c", "d", "e"):
    delayed = finish(TASKS, {task_id: 2})
    print(f"+2 days on {task_id}: finish {delayed}  (slip {delayed - finish(TASKS)})")
""",
        experiment_brief_ar="رتّب المهام حسب مقدار الانزلاق الذي يسببه تأخيرها، وفسّر الترتيب.",
        experiment_brief_en="Rank the tasks by how much slip a delay causes, and explain the ordering.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `build_plan(tasks)` تُعيد قاموساً `{"tasks": {id: task}, "successors": {...}, "order": [...]}`
   بترتيب طوبولوجي (أبجدي عند التساوي لضمان الثبات). ترفع `ValueError("cycle detected")`
   إن وُجدت حلقة.
2. `earliest_finish(plan)` قاموس `{task_id: days}`.
3. `critical_path(plan)` تُعيد `{"path": [...], "duration": int}` لأطول مسار (سلسلة تبعيات).
4. `slack(plan)` قاموس `{task_id: days}` لكل مهمة.""",
            brief_en="""Write:
1. `build_plan(tasks)` returning `{"tasks": {id: task}, "successors": {...}, "order": [...]}` in
   topological order (alphabetical on ties, for determinism). Raise `ValueError("cycle detected")`
   when there is a cycle.
2. `earliest_finish(plan)` - a `{task_id: days}` dict.
3. `critical_path(plan)` returning `{"path": [...], "duration": int}` for the longest dependency chain.
4. `slack(plan)` - a `{task_id: days}` dict for every task.""",
            starter_code="""from collections import deque


def build_plan(tasks):
    pass


def earliest_finish(plan):
    pass


def critical_path(plan):
    pass


def slack(plan):
    pass
""",
            public_tests={"test_public.py": """from main import build_plan, critical_path

TASKS = [
    {"id": "a", "duration": 3, "depends": []},
    {"id": "b", "duration": 4, "depends": ["a"]},
]

def test_critical_path():
    plan = build_plan(TASKS)
    assert critical_path(plan) == {"path": ["a", "b"], "duration": 7}
"""},
            hidden_tests={"test_hidden.py": """import pytest
from main import build_plan, earliest_finish, critical_path, slack

TASKS = [
    {"id": "design", "duration": 3, "depends": []},
    {"id": "ingest", "duration": 4, "depends": ["design"]},
    {"id": "features", "duration": 5, "depends": ["ingest"]},
    {"id": "model", "duration": 6, "depends": ["features"]},
    {"id": "report", "duration": 2, "depends": ["ingest"]},
    {"id": "launch", "duration": 1, "depends": ["model", "report"]},
]

def test_order_is_topological():
    plan = build_plan(TASKS)
    order = plan["order"]
    for task in TASKS:
        for dependency in task["depends"]:
            assert order.index(dependency) < order.index(task["id"])

def test_earliest_finish():
    plan = build_plan(TASKS)
    finish = earliest_finish(plan)
    assert finish["design"] == 3
    assert finish["ingest"] == 7
    assert finish["launch"] == 19

def test_critical_path_is_longest_chain():
    plan = build_plan(TASKS)
    result = critical_path(plan)
    assert result["duration"] == 19
    assert result["path"][0] == "design" and result["path"][-1] == "launch"

def test_slack_of_critical_tasks_is_zero():
    plan = build_plan(TASKS)
    values = slack(plan)
    assert values["design"] == 0
    assert values["model"] == 0
    assert values["launch"] == 0

def test_slack_of_side_task():
    plan = build_plan(TASKS)
    values = slack(plan)
    assert values["report"] > 0

def test_cycle_detected():
    with pytest.raises(ValueError) as info:
        build_plan([
            {"id": "a", "duration": 1, "depends": ["b"]},
            {"id": "b", "duration": 1, "depends": ["a"]},
        ])
    assert "cycle" in str(info.value).lower()

def test_empty_plan():
    plan = build_plan([])
    assert plan["order"] == []
    assert critical_path(plan)["duration"] == 0

def test_single_task():
    plan = build_plan([{"id": "only", "duration": 4, "depends": []}])
    assert critical_path(plan) == {"path": ["only"], "duration": 4}
    assert slack(plan)["only"] == 0
"""},
            reference_solution="""from collections import deque


def build_plan(tasks):
    by_id = {task["id"]: task for task in tasks}
    successors = {task["id"]: [] for task in tasks}
    indegree = {task["id"]: 0 for task in tasks}
    for task in tasks:
        for dependency in task["depends"]:
            if dependency not in by_id:
                raise ValueError(f"unknown dependency: {dependency}")
            successors[dependency].append(task["id"])
            indegree[task["id"]] += 1

    queue = deque(sorted(task_id for task_id, degree in indegree.items() if degree == 0))
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for successor in sorted(successors[node]):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)
    if len(order) != len(tasks):
        raise ValueError("cycle detected")
    return {"tasks": by_id, "successors": successors, "order": order}


def earliest_finish(plan):
    finish = {}
    for task_id in plan["order"]:
        task = plan["tasks"][task_id]
        start = max([finish[dependency] for dependency in task["depends"]] or [0])
        finish[task_id] = start + task["duration"]
    return finish


def critical_path(plan):
    finish = earliest_finish(plan)
    if not finish:
        return {"path": [], "duration": 0}
    end_task = max(plan["order"], key=lambda task_id: (finish[task_id], task_id))
    path = [end_task]
    while plan["tasks"][path[0]]["depends"]:
        candidates = plan["tasks"][path[0]]["depends"]
        best = max(candidates, key=lambda task_id: finish[task_id])
        path.insert(0, best)
    return {"path": path, "duration": finish[end_task]}


def slack(plan):
    finish = earliest_finish(plan)
    if not finish:
        return {}
    project_end = max(finish.values())
    latest_start = {}
    for task_id in reversed(plan["order"]):
        children = [other for other in plan["order"] if task_id in plan["tasks"][other]["depends"]]
        if children:
            latest_finish = min(latest_start[child] for child in children)
        else:
            latest_finish = project_end
        latest_start[task_id] = latest_finish - plan["tasks"][task_id]["duration"]
    return {task_id: latest_start[task_id] - (finish[task_id] - plan["tasks"][task_id]["duration"])
            for task_id in plan["order"]}
""",
            hints=(
                "Sort the ready queue so the order does not depend on dictionary insertion order.",
                "`len(order) != len(tasks)` is the simplest cycle test for Kahn's algorithm.",
                "Slack is `latest start - earliest start`, so compute both passes.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `simulate(plan, delays=None, seed=0)` تحاكي التشغيل:
- `delays` قاموس `{task_id: extra_days}` يزيد مدة المهام (0 للبقية)،
- تُعيد `{"finish": int, "baseline": int, "slip": int, "critical_path": [...], "bottleneck": str|None,
  "per_task": {task_id: {"earliest_finish", "slack"}}}`
- `bottleneck` هي المهمة ذات التأثير الأكبر: لكل مهمة احسب الانزلاق الذي يسببه
  تأخيرها يوماً واحداً، واختر الأكبر (و`None` لخطة فارغة).

ثم `recommend(plan, days_to_save)` تُعيد قائمة مهام يجب ضغطها لتقليل التسليم
بمقدار `days_to_save` (من المهام الحرجة، الأطول أولاً).""",
            brief_en="""Write `simulate(plan, delays=None, seed=0)` simulating the run:
- `delays` is a `{task_id: extra_days}` dict extending durations (0 for the rest),
- return `{"finish": int, "baseline": int, "slip": int, "critical_path": [...], "bottleneck": str|None,
  "per_task": {task_id: {"earliest_finish", "slack"}}}`
- `bottleneck` is the task with the largest effect: for each task compute the slip caused by
  delaying it by one day and pick the largest (`None` for an empty plan).

Then `recommend(plan, days_to_save)` returns the tasks to compress in order to cut delivery by
`days_to_save` days (from the critical tasks, longest first).""",
            independent=True,
            starter_code="""def simulate(plan, delays=None):
    pass


def recommend(plan, days_to_save):
    pass
""",
            public_tests={"test_public.py": """from main import simulate, recommend

PLAN = {
    "tasks": {
        "a": {"id": "a", "duration": 3, "depends": []},
        "b": {"id": "b", "duration": 4, "depends": ["a"]},
    },
    "successors": {"a": ["b"], "b": []},
    "order": ["a", "b"],
}

def test_simulate_baseline():
    report = simulate(PLAN)
    assert report["finish"] == 7
    assert report["slip"] == 0
"""},
            hidden_tests={"test_hidden.py": """from main import simulate, recommend

PLAN = {
    "tasks": {
        "design": {"id": "design", "duration": 3, "depends": []},
        "ingest": {"id": "ingest", "duration": 4, "depends": ["design"]},
        "features": {"id": "features", "duration": 5, "depends": ["ingest"]},
        "model": {"id": "model", "duration": 6, "depends": ["features"]},
        "report": {"id": "report", "duration": 2, "depends": ["ingest"]},
        "launch": {"id": "launch", "duration": 1, "depends": ["model", "report"]},
    },
    "successors": {
        "design": ["ingest"], "ingest": ["features", "report"],
        "features": ["model"], "model": ["launch"], "report": ["launch"], "launch": [],
    },
    "order": ["design", "ingest", "features", "model", "report", "launch"],
}

def test_baseline_and_slip():
    report = simulate(PLAN, {"model": 3})
    assert report["baseline"] == 19
    assert report["finish"] == 22
    assert report["slip"] == 3

def test_delay_off_the_critical_path_can_be_free():
    report = simulate(PLAN, {"report": 1})
    assert report["slip"] == 0

def test_bottleneck_is_on_the_critical_path():
    assert simulate(PLAN)["bottleneck"] in {"design", "ingest", "features", "model", "launch"}

def test_per_task_details():
    report = simulate(PLAN)
    assert set(report["per_task"]["model"]) == {"earliest_finish", "slack"}
    assert report["per_task"]["model"]["slack"] == 0

def test_critical_path_reported():
    assert simulate(PLAN)["critical_path"][-1] == "launch"

def test_empty_plan():
    report = simulate({"tasks": {}, "successors": {}, "order": []})
    assert report["finish"] == 0 and report["bottleneck"] is None

def test_recommend_orders_by_duration():
    tasks = recommend(PLAN, 5)
    assert tasks[0] == "model"      # the longest critical task

def test_recommend_stops_at_target():
    tasks = recommend(PLAN, 4)
    assert tasks == ["model"]

def test_recommend_all_critical():
    tasks = recommend(PLAN, 100)
    assert set(tasks) == {"design", "ingest", "features", "model", "launch"}
"""},
            reference_solution="""def _finish(plan, delays):
    delays = delays or {}
    finish = {}
    for task_id in plan["order"]:
        task = plan["tasks"][task_id]
        start = max([finish[dependency] for dependency in task["depends"]] or [0])
        finish[task_id] = start + task["duration"] + delays.get(task_id, 0)
    return finish


def _critical_path(plan, finish):
    if not finish:
        return []
    end_task = max(plan["order"], key=lambda task_id: (finish[task_id], task_id))
    path = [end_task]
    while plan["tasks"][path[0]]["depends"]:
        best = max(plan["tasks"][path[0]]["depends"], key=lambda task_id: finish[task_id])
        path.insert(0, best)
    return path


def _slack(plan, finish):
    if not finish:
        return {}
    project_end = max(finish.values())
    latest_start = {}
    for task_id in reversed(plan["order"]):
        children = [other for other in plan["order"] if task_id in plan["tasks"][other]["depends"]]
        latest_finish = min([latest_start[child] for child in children] or [project_end])
        latest_start[task_id] = latest_finish - plan["tasks"][task_id]["duration"]
    return {task_id: latest_start[task_id] - (finish[task_id] - plan["tasks"][task_id]["duration"])
            for task_id in plan["order"]}


def simulate(plan, delays=None):
    baseline_finish = _finish(plan, {})
    finish = _finish(plan, delays)
    baseline = max(baseline_finish.values()) if baseline_finish else 0
    current = max(finish.values()) if finish else 0
    path = _critical_path(plan, finish)
    slack = _slack(plan, finish)

    bottleneck = None
    worst = 0
    for task_id in plan["order"]:
        with_delay = _finish(plan, {task_id: 1})
        slip = (max(with_delay.values()) if with_delay else 0) - current
        if slip > worst:
            worst = slip
            bottleneck = task_id

    return {
        "finish": current,
        "baseline": baseline,
        "slip": current - baseline,
        "critical_path": path,
        "bottleneck": bottleneck,
        "per_task": {
            task_id: {"earliest_finish": finish[task_id], "slack": slack.get(task_id, 0)}
            for task_id in plan["order"]
        },
    }


def recommend(plan, days_to_save):
    finish = _finish(plan, {})
    if not finish:
        return []
    critical = [task_id for task_id in plan["order"] if _slack(plan, finish).get(task_id) == 0]
    critical.sort(key=lambda task_id: (-plan["tasks"][task_id]["duration"], task_id))
    chosen = []
    saved = 0
    for task_id in critical:
        if saved >= days_to_save:
            break
        chosen.append(task_id)
        saved += plan["tasks"][task_id]["duration"]
    return chosen
""",
        ),
        transfer_ar="استخدم `simulate` في Project Rescue لتبرير قرارك بأرقام لا بانطباع.",
        transfer_en="Use `simulate` in Project Rescue to justify your decision with numbers, not intuition.",
        references=(
            ("Critical path method on Wikipedia", "https://en.wikipedia.org/wiki/Critical_path_method"),
            ("Kahn's algorithm", "https://en.wikipedia.org/wiki/Topological_sorting"),
        ),
    ),
    CurriculumModule(
        id="l11.capstone_pipeline",
        level=11,
        order_index=2,
        domain="capstone",
        title_ar="مشروع تخرّج: مسار بيانات متكامل",
        title_en="Capstone: an end-to-end data pipeline",
        summary_ar="مشروع متعدد الملفات: استيعاب، ميزات، نموذج، تقييم، وتقرير.",
        summary_en="A multi-file project: ingest, features, model, evaluation and report.",
        explanation_ar="""هذا المشروع يجمع ما تعلّمته. الهيكل:

```
pipeline/
  __init__.py
  ingest.py     - قراءة المصادر والتحقق منها (معطى)
  features.py   - بناء الميزات (ملفك الرئيسي)
  report.py     - تجميع النتائج (معطى)
```

قواعد المشروع الاحترافي:
- **كل مرحلة دالة نقية**: لا قراءة ملفات ولا طباعة داخل المنطق.
- **التحقق عند الحدود**: `ingest.validate` يرفع `ValueError` عند بيانات تالفة.
- **الفصل بين الميزات والنموذج**: هندسة الميزات قرار منفصل عن اختيار النموذج،
  وكلاهما أسهل في الاختبار منفصلين.
- **التقييم بالأرقام**: دقة، و`recall` للصنف المهم، ومصفوفة التباس.
- **تقرير قابل للقراءة**: `report.build` يحول الأرقام إلى نص واضح.

المعيار هنا ليس "يعمل"، بل "يعمل ويمكن لغيرك فهمه وتعديله".""",
        explanation_en="""This project combines everything you have learned. The layout:

```
pipeline/
  __init__.py
  ingest.py     - reads and validates the sources (provided)
  features.py   - builds the features (your entry file)
  report.py     - collects the results (provided)
```

Professional rules:
- **every stage is a pure function**: no file reads, no printing inside the logic;
- **validate at the boundary**: `ingest.validate` raises `ValueError` on corrupt data;
- **separate features from the model**: feature engineering is a different decision from model
  choice, and both are easier to test apart;
- **measure with numbers**: accuracy, recall for the important class and a confusion matrix;
- **readable reporting**: `report.build` turns numbers into clear text.

The standard here is not "it works", but "it works and someone else can understand and change it".""",
        skills=("data.pipelines", "ml.evaluation", "pro.refactoring"),
        prerequisites=("l7.evaluation_cv", "l5.etl_pipeline"),
        example_code="""from collections import Counter

ROWS = [
    {"amount": 120, "country": "SA", "label": 0},
    {"amount": 900, "country": "AE", "label": 1},
    {"amount": 30, "country": "SA", "label": 0},
    {"amount": 1500, "country": "EG", "label": 1},
]


def features(rows):
    return [[row["amount"], 1 if row["country"] == "SA" else 0, len(str(row["amount"]))] for row in rows]


def fit_thresholds(matrix, labels):
    \"\"\"Pick the split point per column with the best information gain (one pass).\"\"\"
    thresholds = []
    for column in range(len(matrix[0])):
        values = sorted({row[column] for row in matrix})
        best, best_gain = None, -1.0
        for value in values:
            left = [labels[i] for i, row in enumerate(matrix) if row[column] <= value]
            right = [labels[i] for i, row in enumerate(matrix) if row[column] > value]
            if not left or not right:
                continue
            majority_left = Counter(left).most_common(1)[0][1]
            majority_right = Counter(right).most_common(1)[0][1]
            gain = (majority_left + majority_right) / len(labels)
            if gain > best_gain:
                best_gain, best = gain, value
        thresholds.append(best)
    return thresholds


matrix = features(ROWS)
labels = [row["label"] for row in ROWS]
print("thresholds:", fit_thresholds(matrix, labels))
print("feature rows:", matrix)
""",
        example_notes_ar="هذا نموذج شجرة قرار بسيط: اختيار أفضل نقطة فصل لكل عمود.",
        example_notes_en="This is a tiny decision tree: the best split point per column.",
        experiment_code="""import random

rng = random.Random(7)
ROWS = []
for index in range(200):
    amount = rng.randint(10, 2000)
    night = 1 if rng.random() < 0.3 else 0
    label = 1 if (amount > 800 and night) or amount > 1500 else 0
    ROWS.append({"amount": amount, "night": night, "label": label})


def split(rows, ratio=0.75):
    shuffled = rows[:]
    rng.shuffle(shuffled)
    cut = int(len(shuffled) * ratio)
    return shuffled[:cut], shuffled[cut:]


train, test = split(ROWS)
print("train:", len(train), "test:", len(test))


def rule(row):
    return 1 if row["amount"] > 800 and row["night"] else (1 if row["amount"] > 1500 else 0)


correct = sum(1 for row in test if rule(row) == row["label"])
print("rule accuracy on test:", round(correct / len(test), 3))
print("positive rate:", round(sum(r["label"] for r in ROWS) / len(ROWS), 3))
""",
        experiment_brief_ar="أضف ميزة ثالثة (`amount` مقسوماً على 100) وشاهد هل تحسّن القاعدة.",
        experiment_brief_en="Add a third feature (amount divided by 100) and see whether the rule improves.",
        task=TaskSpec(
            entry_filename="pipeline/features.py",
            extra_files={
                "pipeline/__init__.py": "",
                "pipeline/ingest.py": '''"""Read and validate the raw transaction rows."""
from __future__ import annotations

REQUIRED = ("amount", "country", "hour", "label")


def validate(rows):
    """Return (clean_rows, report). Raise ValueError when a required column is missing."""
    if not rows:
        return [], {"rows": 0, "dropped": 0, "missing_columns": []}
    available = set(rows[0]) | {key for row in rows for key in row}
    missing = [column for column in REQUIRED if column not in available]
    if missing:
        raise ValueError(f"missing columns: {', '.join(sorted(missing))}")

    clean, dropped = [], 0
    for row in rows:
        record = {column: row.get(column) for column in REQUIRED}
        if record["amount"] is None or record["hour"] is None or record["label"] is None:
            dropped += 1
            continue
        record["amount"] = float(record["amount"])
        record["hour"] = int(record["hour"])
        record["label"] = int(record["label"])
        record["country"] = str(record["country"] or "unknown")
        clean.append(record)
    return clean, {"rows": len(clean), "dropped": dropped, "missing_columns": []}


def load(rows):
    clean, report = validate(rows)
    if not clean:
        raise ValueError("no usable rows")
    return clean, report
''',
                "pipeline/report.py": '''"""Turn evaluation numbers into readable text."""
from __future__ import annotations


def build(metrics, title="Pipeline report"):
    lines = [title, "=" * len(title), ""]
    lines.append(f"rows evaluated : {metrics['rows']}")
    lines.append(f"accuracy       : {metrics['accuracy']:.3f}")
    lines.append(f"precision      : {metrics['precision']:.3f}")
    lines.append(f"recall         : {metrics['recall']:.3f}")
    lines.append(f"f1             : {metrics['f1']:.3f}")
    lines.append("")
    lines.append("confusion matrix:")
    lines.append(f"  true positives : {metrics['tp']}")
    lines.append(f"  false positives: {metrics['fp']}")
    lines.append(f"  true negatives : {metrics['tn']}")
    lines.append(f"  false negatives: {metrics['fn']}")
    return "\\n".join(lines)
''',
            },
            brief_ar="""المشروع في `pipeline/`. الملفان `ingest.py` و`report.py` جاهزان؛
نفّذ `features.py` (ملفك الرئيسي):

1. `build_features(rows)` تُعيد مصفوفة `X` (قائمة قوائم) بالأعمدة:
   `[amount, hour, is_night, amount_per_hour_bucket]`
   حيث `is_night = 1` إذا كانت الساعة خارج `[8, 20]`.
2. `labels_of(rows)` تُعيد قائمة التسميات.
3. `fit_rules(X, y)` تُعلّم قاعدتين بسيطتين بالبحث عن أفضل عتبة على العمود الأول،
   وتُعيد `{"threshold": float, "direction": "above", "baseline": float}` حيث `baseline`
   نسبة الصنف الموجب في التدريب.
4. `predict(model, X)` تُعيد 0/1: `1` إذا كان المبلغ أكبر من العتبة، وإلا `1` إذا
   كان ليلياً والمبلغ أكبر من نصف العتبة، وإلا `0`.""",
            brief_en="""The project lives in `pipeline/`. `ingest.py` and `report.py` are provided; implement
`features.py` (your entry file):

1. `build_features(rows)` returning a matrix `X` (list of lists) with the columns
   `[amount, hour, is_night, amount_per_hour_bucket]`, where `is_night` is 1 when the hour is
   outside `[8, 20]`.
2. `labels_of(rows)` returning the label list.
3. `fit_rules(X, y)` learning two simple rules by searching for the best threshold on the first
   column, returning `{"threshold": float, "direction": "above", "baseline": float}` where
   `baseline` is the positive rate in training.
4. `predict(model, X)` returning 0/1: `1` when the amount exceeds the threshold, otherwise `1`
   when it is night and the amount exceeds half the threshold, otherwise `0`.""",
            starter_code='''"""Feature engineering for the transaction pipeline."""
from __future__ import annotations


def build_features(rows):
    pass


def labels_of(rows):
    pass


def fit_rules(X, y):
    pass


def predict(model, X):
    pass
''',
            public_tests={
                "test_public.py": """from pipeline.features import build_features, labels_of

ROWS = [
    {"amount": 100.0, "country": "SA", "hour": 10, "label": 0},
    {"amount": 900.0, "country": "AE", "hour": 22, "label": 1},
]

def test_features_shape():
    X = build_features(ROWS)
    assert len(X) == 2 and len(X[0]) == 4

def test_labels():
    assert labels_of(ROWS) == [0, 1]
"""},
            hidden_tests={
                "test_hidden.py": """from pipeline.features import build_features, labels_of, fit_rules, predict
from pipeline.ingest import validate
from pipeline.report import build

RAW = [
    {"amount": 50, "country": "SA", "hour": 9, "label": 0},
    {"amount": 900, "country": "AE", "hour": 23, "label": 1},
    {"amount": 1700, "country": "EG", "hour": 15, "label": 1},
    {"amount": 30, "country": "SA", "hour": 2, "label": 0},
    {"amount": 850, "country": "SA", "hour": 3, "label": 1},
    {"amount": 120, "country": "AE", "hour": 11, "label": 0},
    {"amount": 2000, "country": "EG", "hour": 19, "label": 1},
    {"amount": 10, "country": "SA", "hour": 8, "label": 0},
]

def test_is_night_flag():
    X = build_features(RAW)
    assert X[1][2] == 1      # hour 23
    assert X[0][2] == 0      # hour 9

def test_boundary_hours_are_day():
    X = build_features(RAW)
    assert X[7][2] == 0      # hour 8 is inside the day window

def test_amount_bucket_is_positive():
    X = build_features(RAW)
    assert X[0][3] > 0

def test_labels_order():
    assert labels_of(RAW) == [0, 1, 1, 0, 1, 0, 1, 0]

def test_fit_returns_model_shape():
    rows, _ = validate(RAW)
    model = fit_rules(build_features(rows), labels_of(rows))
    assert set(model) == {"threshold", "direction", "baseline"}
    assert model["direction"] == "above"
    assert 0.0 <= model["baseline"] <= 1.0

def test_predict_shape_and_values():
    rows, _ = validate(RAW)
    X = build_features(rows)
    model = fit_rules(X, labels_of(rows))
    predictions = predict(model, X)
    assert len(predictions) == len(rows)
    assert set(predictions).issubset({0, 1})

def test_predict_is_better_than_chance():
    rows, _ = validate(RAW)
    X = build_features(rows)
    y = labels_of(rows)
    model = fit_rules(X, y)
    predictions = predict(model, X)
    accuracy = sum(1 for a, b in zip(predictions, y) if a == b) / len(y)
    assert accuracy >= 0.7

def test_ingest_rejects_bad_schema():
    try:
        validate([{"amount": 1}])
    except ValueError:
        return
    raise AssertionError("expected ValueError for a missing column")

def test_report_contains_metrics():
    text = build({"rows": 2, "accuracy": 0.5, "precision": 0.5, "recall": 1.0,
                  "f1": 0.667, "tp": 1, "fp": 1, "tn": 0, "fn": 0})
    assert "accuracy" in text and "confusion" in text
"""},
            reference_solution='''"""Feature engineering for the transaction pipeline."""
from __future__ import annotations

DAY_START, DAY_END = 8, 20


def build_features(rows):
    matrix = []
    for row in rows:
        amount = float(row["amount"])
        hour = int(row["hour"])
        is_night = 1 if hour < DAY_START or hour > DAY_END else 0
        bucket = amount / max(1, hour // 6 + 1)
        matrix.append([amount, hour, is_night, bucket])
    return matrix


def labels_of(rows):
    return [int(row["label"]) for row in rows]


def fit_rules(X, y):
    positive = sum(1 for value in y if value == 1)
    baseline = positive / len(y) if y else 0.0

    candidates = sorted({row[0] for row in X})
    best_threshold, best_accuracy = (max(candidates) if candidates else 0.0), -1.0
    for threshold in candidates:
        predictions = [1 if row[0] > threshold else 0 for row in X]
        accuracy = sum(1 for a, b in zip(predictions, y) if a == b) / len(y)
        if accuracy > best_accuracy:
            best_accuracy, best_threshold = accuracy, threshold
    return {"threshold": float(best_threshold), "direction": "above", "baseline": baseline}


def predict(model, X):
    threshold = model["threshold"]
    predictions = []
    for row in X:
        amount, is_night = row[0], row[2]
        if amount > threshold:
            predictions.append(1)
        elif is_night and amount > threshold / 2:
            predictions.append(1)
        else:
            predictions.append(0)
    return predictions
''',
            hints=(
                "The night flag is `hour < 8 or hour > 20` - both ends of the window are inclusive.",
                "Search thresholds over the distinct values of the first column only.",
                "Keep `fit_rules` deterministic: iterate over a sorted list of candidates.",
            ),
        ),
        assessment=TaskSpec(
            entry_filename="pipeline/evaluate.py",
            extra_files={
                "pipeline/__init__.py": "",
                "pipeline/ingest.py": '"""Read and validate the raw transaction rows."""\nfrom __future__ import annotations\n\nREQUIRED = ("amount", "country", "hour", "label")\n\n\ndef validate(rows):\n    """Return (clean_rows, report). Raise ValueError when a required column is missing."""\n    if not rows:\n        return [], {"rows": 0, "dropped": 0, "missing_columns": []}\n    available = set(rows[0]) | {key for row in rows for key in row}\n    missing = [column for column in REQUIRED if column not in available]\n    if missing:\n        raise ValueError(f"missing columns: {\', \'.join(sorted(missing))}")\n\n    clean, dropped = [], 0\n    for row in rows:\n        record = {column: row.get(column) for column in REQUIRED}\n        if record["amount"] is None or record["hour"] is None or record["label"] is None:\n            dropped += 1\n            continue\n        record["amount"] = float(record["amount"])\n        record["hour"] = int(record["hour"])\n        record["label"] = int(record["label"])\n        record["country"] = str(record["country"] or "unknown")\n        clean.append(record)\n    return clean, {"rows": len(clean), "dropped": dropped, "missing_columns": []}\n\n\ndef load(rows):\n    clean, report = validate(rows)\n    if not clean:\n        raise ValueError("no usable rows")\n    return clean, report\n',
                "pipeline/report.py": '"""Turn evaluation numbers into readable text."""\nfrom __future__ import annotations\n\n\ndef build(metrics, title="Pipeline report"):\n    lines = [title, "=" * len(title), ""]\n    lines.append(f"rows evaluated : {metrics[\'rows\']}")\n    lines.append(f"accuracy       : {metrics[\'accuracy\']:.3f}")\n    lines.append(f"precision      : {metrics[\'precision\']:.3f}")\n    lines.append(f"recall         : {metrics[\'recall\']:.3f}")\n    lines.append(f"f1             : {metrics[\'f1\']:.3f}")\n    lines.append("")\n    lines.append("confusion matrix:")\n    lines.append(f"  true positives : {metrics[\'tp\']}")\n    lines.append(f"  false positives: {metrics[\'fp\']}")\n    lines.append(f"  true negatives : {metrics[\'tn\']}")\n    lines.append(f"  false negatives: {metrics[\'fn\']}")\n    return "\\\\n".join(lines)\n',
                "pipeline/features.py": '"""Feature engineering for the transaction pipeline."""\nfrom __future__ import annotations\n\nDAY_START, DAY_END = 8, 20\n\n\ndef build_features(rows):\n    matrix = []\n    for row in rows:\n        amount = float(row["amount"])\n        hour = int(row["hour"])\n        is_night = 1 if hour < DAY_START or hour > DAY_END else 0\n        bucket = amount / max(1, hour // 6 + 1)\n        matrix.append([amount, hour, is_night, bucket])\n    return matrix\n\n\ndef labels_of(rows):\n    return [int(row["label"]) for row in rows]\n\n\ndef fit_rules(X, y):\n    positive = sum(1 for value in y if value == 1)\n    baseline = positive / len(y) if y else 0.0\n\n    candidates = sorted({row[0] for row in X})\n    best_threshold, best_accuracy = (max(candidates) if candidates else 0.0), -1.0\n    for threshold in candidates:\n        predictions = [1 if row[0] > threshold else 0 for row in X]\n        accuracy = sum(1 for a, b in zip(predictions, y) if a == b) / len(y)\n        if accuracy > best_accuracy:\n            best_accuracy, best_threshold = accuracy, threshold\n    return {"threshold": float(best_threshold), "direction": "above", "baseline": baseline}\n\n\ndef predict(model, X):\n    threshold = model["threshold"]\n    predictions = []\n    for row in X:\n        amount, is_night = row[0], row[2]\n        if amount > threshold:\n            predictions.append(1)\n        elif is_night and amount > threshold / 2:\n            predictions.append(1)\n        else:\n            predictions.append(0)\n    return predictions\n',
            },
            brief_ar="""أضف وحدة `pipeline/evaluate.py` تُكمل المشروع:
- `confusion(y_true, y_pred)` تُعيد `{"tp", "fp", "tn", "fn"}`،
- `metrics(y_true, y_pred)` تُعيد `{"rows", "accuracy", "precision", "recall", "f1"}`
  بحماية من القسمة على صفر،
- `cross_validated(model_factory, rows, folds=3)` تُدرّب `model_factory()` على كل طية
  (باستخدام `fit_rules` و`predict` من `features.py`) وتُعيد قائمة الدقة،
- `run(rows)` تُعيد `{"metrics": {...}, "report": text}` باستخدام `report.build`.

استيرادك: `from pipeline.features import build_features, labels_of, fit_rules, predict`.""",
            brief_en="""Add a `pipeline/evaluate.py` module completing the project:
- `confusion(y_true, y_pred)` returning `{"tp", "fp", "tn", "fn"}`,
- `metrics(y_true, y_pred)` returning `{"rows", "accuracy", "precision", "recall", "f1"}`,
  guarded against division by zero,
- `cross_validated(model_factory, rows, folds=3)` training `model_factory()` on every fold (using
  `fit_rules` and `predict` from `features.py`) and returning the list of accuracies,
- `run(rows)` returning `{"metrics": {...}, "report": text}` using `report.build`.

Your import: `from pipeline.features import build_features, labels_of, fit_rules, predict`.""",
            independent=True,
            starter_code='''"""Evaluation for the transaction pipeline."""
from __future__ import annotations

from pipeline.features import build_features, fit_rules, labels_of, predict
from pipeline.report import build


def confusion(y_true, y_pred):
    pass


def metrics(y_true, y_pred):
    pass


def cross_validated(model_factory, rows, folds=3):
    pass


def run(rows):
    pass
''',
            public_tests={"test_public.py": """from pipeline.evaluate import confusion

def test_confusion():
    counts = confusion([1, 0, 1], [1, 0, 0])
    assert counts == {"tp": 1, "fp": 0, "tn": 1, "fn": 1}
"""},
            hidden_tests={"test_hidden.py": """from pipeline.evaluate import confusion, metrics, cross_validated, run
from pipeline.features import build_features, fit_rules, labels_of, predict

ROWS = [
    {"amount": 50, "country": "SA", "hour": 9, "label": 0},
    {"amount": 900, "country": "AE", "hour": 23, "label": 1},
    {"amount": 1700, "country": "EG", "hour": 15, "label": 1},
    {"amount": 30, "country": "SA", "hour": 2, "label": 0},
    {"amount": 850, "country": "SA", "hour": 3, "label": 1},
    {"amount": 120, "country": "AE", "hour": 11, "label": 0},
    {"amount": 2000, "country": "EG", "hour": 19, "label": 1},
    {"amount": 10, "country": "SA", "hour": 8, "label": 0},
]

def test_metrics_keys():
    result = metrics([1, 0, 1], [1, 0, 0])
    assert set(result) == {"rows", "accuracy", "precision", "recall", "f1"}
    assert result["rows"] == 3

def test_metrics_perfect():
    result = metrics([1, 0], [1, 0])
    assert result["accuracy"] == 1.0 and result["f1"] == 1.0

def test_metrics_no_positive_predictions():
    result = metrics([1, 0], [0, 0])
    assert result["precision"] == 0.0

def test_metrics_empty():
    result = metrics([], [])
    assert result["rows"] == 0 and result["accuracy"] == 0.0

def test_cross_validated_returns_one_score_per_fold():
    scores = cross_validated(dict, ROWS, folds=2)
    assert len(scores) == 2
    assert all(0.0 <= score <= 1.0 for score in scores)

def test_run_returns_metrics_and_text():
    result = run(ROWS)
    assert set(result) == {"metrics", "report"}
    assert "accuracy" in result["report"]

def test_run_end_to_end():
    result = run(ROWS)
    assert result["metrics"]["rows"] == 8
    assert result["metrics"]["accuracy"] >= 0.7
"""},
            reference_solution='''"""Evaluation for the transaction pipeline."""
from __future__ import annotations

from pipeline.features import build_features, fit_rules, labels_of, predict
from pipeline.report import build


def confusion(y_true, y_pred):
    actual = list(y_true)
    predicted = list(y_pred)
    return {
        "tp": sum(1 for a, b in zip(actual, predicted) if a == 1 and b == 1),
        "fp": sum(1 for a, b in zip(actual, predicted) if a == 0 and b == 1),
        "tn": sum(1 for a, b in zip(actual, predicted) if a == 0 and b == 0),
        "fn": sum(1 for a, b in zip(actual, predicted) if a == 1 and b == 0),
    }


def metrics(y_true, y_pred):
    counts = confusion(y_true, y_pred)
    rows = len(list(y_true))
    precision_denominator = counts["tp"] + counts["fp"]
    recall_denominator = counts["tp"] + counts["fn"]
    precision = counts["tp"] / precision_denominator if precision_denominator else 0.0
    recall = counts["tp"] / recall_denominator if recall_denominator else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "rows": rows,
        "accuracy": ((counts["tp"] + counts["tn"]) / rows) if rows else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def cross_validated(model_factory, rows, folds=3):
    X = build_features(rows)
    y = labels_of(rows)
    scores = []
    total = len(rows)
    folds = max(1, min(int(folds), total))
    for fold in range(folds):
        validation = list(range(fold, total, folds))
        train = [index for index in range(total) if index not in set(validation)]
        model_factory()
        model = fit_rules([X[i] for i in train], [y[i] for i in train])
        predictions = predict(model, [X[i] for i in validation])
        actual = [y[i] for i in validation]
        scores.append(sum(1 for a, b in zip(predictions, actual) if a == b) / len(actual))
    return scores


def run(rows):
    X = build_features(rows)
    y = labels_of(rows)
    model = fit_rules(X, y)
    predictions = predict(model, X)
    result = metrics(y, predictions)
    counts = confusion(y, predictions)
    return {
        "metrics": result,
        "report": build({**result, **counts}),
    }
''',
        ),
        transfer_ar="هذا المشروع هو نواة معرض أعمالك في CareerVerse.",
        transfer_en="This project is the core of your CareerVerse portfolio.",
        references=(
            ("scikit-learn - pipelines and composite estimators", "https://scikit-learn.org/stable/modules/compose.html"),
            ("Google - rules of machine learning", "https://mlsysbook.ai/"),
        ),
    ),
    CurriculumModule(
        id="l11.code_review_ast",
        level=11,
        order_index=3,
        domain="capstone",
        title_ar="مراجعة الكود بأدوات ثابتة",
        title_en="Code review with static analysis",
        summary_ar="تحليل الشيفرة بـ `ast`: اكتشاف أنماط خطرة وقياس الجودة.",
        summary_en="Analysing code with `ast`: detecting risky patterns and measuring quality.",
        explanation_ar="""المراجعة اليدوية لا تتوسّع. `ast` (شجرة التركيب المجردة) يتيح لك تحليل الكود
كبيانات: تمشي على العقد وتبحث عن أنماط.

```python
import ast
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        ...
```

أنماط تستحق الكشف الآلي:
- **`except:` مطلق** (`ast.ExceptHandler` بلا `type`) يبتلع كل شيء،
  حتى `KeyboardInterrupt` و`SystemExit`،
- **وسيط افتراضي قابل للتغيير** (`[]` أو `{}` كقيمة افتراضية) — يُشارك بين النداءات،
- **دوال طويلة جداً** (عدد أسطر يتجاوز حداً) — علامة على مسؤوليات متعددة،
- **استيراد غير مستخدم** — اجمع أسماء `Import`/`ImportFrom` وقارنها بـ `ast.Name`،
- **`assert` في كود إنتاج** — يُزال مع تحسين `-O`،
- **`global`** — يعقّد الاختبار.

حدود الأدوات الثابتة: تكشف الأنماط، ولا تفهم النية. الاكتشاف يتطلب حكماً بشرياً،
لذا اجعل التقرير **مرجّحاً** (issues مع severity) لا حكماً نهائياً.""",
        explanation_en="""Manual review does not scale. `ast` (the abstract syntax tree) lets you analyse code as
data: walk the nodes and look for patterns.

```python
import ast
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        ...
```

Patterns worth detecting automatically:
- **bare `except:`** (`ast.ExceptHandler` with no `type`) swallows everything, including
  `KeyboardInterrupt` and `SystemExit`,
- **mutable default arguments** (`[]` or `{}` as a default) - shared between calls,
- **over-long functions** (line count above a limit) - a sign of many responsibilities,
- **unused imports** - collect `Import`/`ImportFrom` names and compare against `ast.Name`,
- **`assert` in production code** - removed under `-O`,
- **`global`** - complicates testing.

Limits of static tools: they detect patterns, they do not understand intent. Detection needs
human judgement, so make the report **advisory** (issues with severity), not a verdict.""",
        skills=("career.code_review", "career.code_reading"),
        prerequisites=("l4.decorators", "l3.debugging"),
        example_code="""import ast

SOURCE = '''
import os
import sys

def process(items, cache={}):
    total = 0
    for item in items:
        try:
            total += item
        except:
            pass
    return total
'''

tree = ast.parse(SOURCE)

imported = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imported.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        imported.update(alias.asname or alias.name for alias in node.names)

used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
used |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        used.add(node.value.id)

print("imported:", sorted(imported))
print("unused  :", sorted(imported - used))

for node in ast.walk(tree):
    if isinstance(node, ast.ExceptHandler) and node.type is None:
        print(f"bare except at line {node.lineno}")
    if isinstance(node, (ast.List, ast.Dict, ast.Set)) and isinstance(node.parent if hasattr(node, "parent") else None, ast.arguments):
        print("mutable default detected")
    if isinstance(node, ast.FunctionDef):
        span = (node.end_lineno or node.lineno) - node.lineno + 1
        print(f"function {node.name}: {span} lines, {len(node.args.defaults)} defaults")
""",
        example_notes_ar="`ast` لا يحفظ العقدة الأب افتراضياً: استخدم `ast.walk` مع تتبّع السياق بنفسك.",
        example_notes_en="`ast` does not keep parent links by default: use `ast.walk` and track the context yourself.",
        experiment_code="""import ast

SAMPLES = {
    "bare except": "def f():\\n    try:\\n        1/0\\n    except:\\n        pass",
    "mutable default": "def f(items=[]):\\n    return items",
    "long function": "def f():\\n" + "".join(f"    x = {i}\\n" for i in range(40)),
    "unused import": "import json\\ndef f():\\n    return 1",
    "clean": "def add(a, b):\\n    return a + b",
}


def find_mutable_defaults(tree):
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d]
            for default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    found.append(node.name)
    return found


def longest_function(tree):
    best = (None, 0)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            span = (node.end_lineno or node.lineno) - node.lineno + 1
            if span > best[1]:
                best = (node.name, span)
    return best


for label, source in SAMPLES.items():
    tree = ast.parse(source)
    print(f"{label:>16}: mutables={find_mutable_defaults(tree)} longest={longest_function(tree)}")
""",
        experiment_brief_ar="أضف كاشفاً للدوال التي تحتوي أكثر من 3 مستويات تَداخُل (nesting).",
        experiment_brief_en="Add a detector for functions nested more than 3 levels deep.",
        task=TaskSpec(
            brief_ar="""اكتب `analyze_source(source, max_function_lines=30)` تُعيد قائمة قواميس
`{"rule", "message", "line", "severity"}` بالقواعد:
- `bare-except`: `ast.ExceptHandler` بلا `type` (severity `"high"`)،
- `mutable-default`: قيمة افتراضية من نوع list/dict/set (severity `"high"`)،
- `long-function`: دالة تتجاوز `max_function_lines` سطراً (severity `"medium"`)،
- `unused-import`: استيراد لا يُستخدم (severity `"low"`)،
- `global-statement`: استخدام `global` (severity `"medium"`).

رتّب النتيجة حسب رقم السطر.""",
            brief_en="""Write `analyze_source(source, max_function_lines=30)` returning a list of dicts
`{"rule", "message", "line", "severity"}` with the rules:
- `bare-except`: an `ast.ExceptHandler` with no `type` (severity `"high"`),
- `mutable-default`: a list/dict/set default value (severity `"high"`),
- `long-function`: a function longer than `max_function_lines` lines (severity `"medium"`),
- `unused-import`: an import that is never used (severity `"low"`),
- `global-statement`: use of `global` (severity `"medium"`).

Sort the result by line number.""",
            starter_code="""import ast


def analyze_source(source, max_function_lines=30):
    pass
""",
            public_tests={"test_public.py": """from main import analyze_source

def test_detects_bare_except():
    source = "def f():\\n    try:\\n        1/0\\n    except:\\n        pass"
    issues = analyze_source(source)
    assert any(issue["rule"] == "bare-except" for issue in issues)
"""},
            hidden_tests={"test_hidden.py": """from main import analyze_source

def rules(source, **kwargs):
    return {issue["rule"] for issue in analyze_source(source, **kwargs)}

def test_clean_code_has_no_issues():
    assert analyze_source("def add(a, b):\\n    return a + b") == []

def test_mutable_default():
    assert "mutable-default" in rules("def f(items=[]):\\n    return items")

def test_mutable_dict_default():
    assert "mutable-default" in rules("def f(options={}):\\n    return options")

def test_long_function():
    source = "def f():\\n" + "".join(f"    x = {i}\\n" for i in range(40))
    assert "long-function" in rules(source, max_function_lines=30)

def test_short_function_passes():
    source = "def f():\\n" + "".join(f"    x = {i}\\n" for i in range(10))
    assert "long-function" not in rules(source, max_function_lines=30)

def test_unused_import():
    assert "unused-import" in rules("import json\\ndef f():\\n    return 1")

def test_used_import_is_fine():
    assert "unused-import" not in rules("import json\\ndef f():\\n    return json.dumps({})")

def test_global_statement():
    assert "global-statement" in rules("counter = 0\\ndef f():\\n    global counter\\n    counter += 1")

def test_issue_shape():
    issues = analyze_source("def f(items=[]):\\n    return items")
    assert set(issues[0]) == {"rule", "message", "line", "severity"}
    assert issues[0]["line"] == 1

def test_sorted_by_line():
    source = (
        "import json\\n"
        "def f(items=[]):\\n"
        "    total = 0\\n"
        "    try:\\n"
        "        total += 1\\n"
        "    except:\\n"
        "        pass\\n"
        "    return total\\n"
    )
    issues = analyze_source(source)
    assert issues == sorted(issues, key=lambda issue: issue["line"])

def test_severity_values():
    issues = analyze_source("def f(items=[]):\\n    return items")
    assert issues[0]["severity"] in {"high", "medium", "low"}

def test_syntax_error_is_reported():
    issues = analyze_source("def f(:")
    assert any(issue["rule"] == "syntax-error" for issue in issues)
"""},
            reference_solution="""import ast


def _used_names(tree):
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            current = node
            while isinstance(current, ast.Attribute):
                current = current.value
            if isinstance(current, ast.Name):
                used.add(current.id)
    return used


def analyze_source(source, max_function_lines=30):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return [{
            "rule": "syntax-error",
            "message": f"could not parse: {error.msg}",
            "line": error.lineno or 1,
            "severity": "high",
        }]

    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append({
                "rule": "bare-except",
                "message": "a bare except swallows every exception, including KeyboardInterrupt",
                "line": node.lineno,
                "severity": "high",
            })
        if isinstance(node, ast.Global):
            issues.append({
                "rule": "global-statement",
                "message": "global state makes functions harder to test",
                "line": node.lineno,
                "severity": "medium",
            })
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d]
            for default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append({
                        "rule": "mutable-default",
                        "message": f"mutable default argument in {node.name}() is shared between calls",
                        "line": node.lineno,
                        "severity": "high",
                    })
            span = (node.end_lineno or node.lineno) - node.lineno + 1
            if span > int(max_function_lines):
                issues.append({
                    "rule": "long-function",
                    "message": f"{node.name}() spans {span} lines (limit {max_function_lines})",
                    "line": node.lineno,
                    "severity": "medium",
                })

    imported = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported[alias.asname or alias.name.split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported[alias.asname or alias.name] = node.lineno

    used = _used_names(tree)
    for name, line in imported.items():
        if name != "*" and name not in used:
            issues.append({
                "rule": "unused-import",
                "message": f"'{name}' is imported but never used",
                "line": line,
                "severity": "low",
            })

    return sorted(issues, key=lambda issue: issue["line"])
""",
            hints=(
                "Catch `SyntaxError` from `ast.parse` so a broken file is an issue, not a crash.",
                "`node.args.defaults` plus `node.args.kw_defaults` covers all default values.",
                "Unwrap `ast.Attribute` chains to find the base name used by `json.dumps(...)`.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب:
1. `review_files(files, max_function_lines=30)` حيث `files` قاموس `{path: source}`،
   تُعيد `{"files": {path: issues}, "counts": {"high", "medium", "low"}, "score": int, "blocking": bool}`
   - `score` من 100، يُخصم 10 عن كل `high` و4 عن كل `medium` و1 عن كل `low` (لا يقل عن 0)،
   - `blocking = True` إن وُجدت مشكلة `high`.
2. `format_report(report)` نص مقروء: سطر لكل ملف مع قواعده، ثم الملخص.""",
            brief_en="""Write:
1. `review_files(files, max_function_lines=30)` where `files` is a `{path: source}` dict, returning
   `{"files": {path: issues}, "counts": {"high", "medium", "low"}, "score": int, "blocking": bool}`
   - `score` starts at 100 and loses 10 per `high`, 4 per `medium` and 1 per `low` (never below 0),
   - `blocking = True` when any `high` issue exists.
2. `format_report(report)` - readable text: one line per file with its rules, then the summary.""",
            independent=True,
            starter_code="""def review_files(files, max_function_lines=30):
    pass


def format_report(report):
    pass
""",
            public_tests={"test_public.py": """from main import review_files

def test_clean_project_scores_full():
    report = review_files({"a.py": "def add(a, b):\\n    return a + b"})
    assert report["score"] == 100
    assert report["blocking"] is False
"""},
            hidden_tests={"test_hidden.py": """from main import review_files, format_report

FILES = {
    "good.py": "def add(a, b):\\n    return a + b",
    "bad.py": "import json\\ndef f(items=[]):\\n    try:\\n        1/0\\n    except:\\n        pass\\n    return items",
}

def test_files_key_mirrors_input():
    report = review_files(FILES)
    assert set(report["files"]) == {"good.py", "bad.py"}

def test_counts_are_reported():
    report = review_files(FILES)
    assert set(report["counts"]) == {"high", "medium", "low"}
    assert report["counts"]["high"] >= 1

def test_blocking_flag():
    assert review_files(FILES)["blocking"] is True
    assert review_files({"ok.py": "x = 1"})["blocking"] is False

def test_score_penalty():
    report = review_files(FILES)
    expected = 100 - 10 * report["counts"]["high"] - 4 * report["counts"]["medium"] - report["counts"]["low"]
    assert report["score"] == max(0, expected)

def test_score_never_negative():
    source = "def f(a=[], b={}, c=set()):\\n    try:\\n        pass\\n    except:\\n        pass"
    report = review_files({f"m{i}.py": source for i in range(20)})
    assert report["score"] >= 0

def test_empty_project():
    report = review_files({})
    assert report["score"] == 100 and report["blocking"] is False

def test_format_report_mentions_files():
    text = format_report(review_files(FILES))
    assert "good.py" in text and "bad.py" in text

def test_format_report_has_summary():
    text = format_report(review_files(FILES))
    assert "score" in text.lower()
"""},
            reference_solution="""import ast


def _used_names(tree):
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            current = node
            while isinstance(current, ast.Attribute):
                current = current.value
            if isinstance(current, ast.Name):
                used.add(current.id)
    return used


def analyze_source(source, max_function_lines=30):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return [{
            "rule": "syntax-error",
            "message": f"could not parse: {error.msg}",
            "line": error.lineno or 1,
            "severity": "high",
        }]

    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append({
                "rule": "bare-except",
                "message": "a bare except swallows every exception, including KeyboardInterrupt",
                "line": node.lineno,
                "severity": "high",
            })
        if isinstance(node, ast.Global):
            issues.append({
                "rule": "global-statement",
                "message": "global state makes functions harder to test",
                "line": node.lineno,
                "severity": "medium",
            })
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d]
            for default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append({
                        "rule": "mutable-default",
                        "message": f"mutable default argument in {node.name}() is shared between calls",
                        "line": node.lineno,
                        "severity": "high",
                    })
            span = (node.end_lineno or node.lineno) - node.lineno + 1
            if span > int(max_function_lines):
                issues.append({
                    "rule": "long-function",
                    "message": f"{node.name}() spans {span} lines (limit {max_function_lines})",
                    "line": node.lineno,
                    "severity": "medium",
                })

    imported = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported[alias.asname or alias.name.split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported[alias.asname or alias.name] = node.lineno

    used = _used_names(tree)
    for name, line in imported.items():
        if name != "*" and name not in used:
            issues.append({
                "rule": "unused-import",
                "message": f"'{name}' is imported but never used",
                "line": line,
                "severity": "low",
            })

    return sorted(issues, key=lambda issue: issue["line"])


def review_files(files, max_function_lines=30):
    per_file = {}
    counts = {"high": 0, "medium": 0, "low": 0}
    for path, source in files.items():
        issues = analyze_source(source, max_function_lines=max_function_lines)
        per_file[path] = issues
        for issue in issues:
            counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    penalty = 10 * counts["high"] + 4 * counts["medium"] + counts["low"]
    return {
        "files": per_file,
        "counts": counts,
        "score": max(0, 100 - penalty),
        "blocking": counts["high"] > 0,
    }


def format_report(report):
    lines = ["Code review", "=" * 11, ""]
    for path, issues in report["files"].items():
        if issues:
            lines.append(f"{path}")
            for issue in issues:
                lines.append(f"  line {issue['line']:>4}  [{issue['severity']}] {issue['rule']}: {issue['message']}")
        else:
            lines.append(f"{path}: no issues")
    lines.append("")
    lines.append(f"high: {report['counts']['high']}  medium: {report['counts']['medium']}  low: {report['counts']['low']}")
    lines.append(f"score: {report['score']}/100  blocking: {report['blocking']}")
    return "\\n".join(lines)
""",
        ),
        transfer_ar="استخدم `review_files` في Project Rescue لتقييم الكود الموروث بسرعة.",
        transfer_en="Use `review_files` in Project Rescue to assess inherited code quickly.",
        references=(
            ("Python docs - ast", "https://docs.python.org/3/library/ast.html"),
            ("Python docs - ast node visitor", "https://docs.python.org/3/library/ast.html#ast.NodeVisitor"),
        ),
    ),
]
