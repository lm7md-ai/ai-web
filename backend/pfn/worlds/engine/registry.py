"""Registry of simulation worlds and the contract they all share.

Every world module lives in ``pfn.worlds.sim`` and is *standard-library only*,
because it is copied verbatim into the execution sandbox and imported there.
Each module must expose::

    build(config) -> (api, state)
    result(api, state) -> dict
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pfn.worlds.sim import (
    agent_sim,
    algo_sim,
    career_sim,
    city_sim,
    crisis_sim,
    data_sim,
    galaxy_sim,
    library_sim,
    neural_sim,
    olympics_sim,
    research_sim,
    rescue_sim,
    robot_sim,
    sci_sim,
)

SIM_DIR = Path(robot_sim.__file__).parent


@dataclass(frozen=True, slots=True)
class WorldSpec:
    id: str
    module_name: str
    source_path: Path
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    entrypoint: str
    api_docs: tuple[tuple[str, str], ...]
    missions: tuple[str, ...] = ()

    def source(self) -> str:
        return self.source_path.read_text(encoding="utf-8")

    def title(self, locale: str = "en") -> str:
        return self.title_ar if locale == "ar" else self.title_en

    def description(self, locale: str = "en") -> str:
        return self.description_ar if locale == "ar" else self.description_en


WORLDS: dict[str, WorldSpec] = {
    "roboverse": WorldSpec(
        id="roboverse",
        module_name="robot_sim",
        source_path=SIM_DIR / "robot_sim.py",
        title_ar="روبوفيرس",
        title_en="RoboVerse",
        description_ar="مختبر روبوتات على شبكة: حركة، مستشعرات، طاقة وتخطيط مسار.",
        description_en="A grid robotics lab: motion, sensors, energy and pathfinding.",
        entrypoint="program(robot)",
        api_docs=(
            ("move(steps=1)", "Move forward; returns False when blocked by a wall or obstacle."),
            ("turn_left() / turn_right()", "Rotate 90 degrees."),
            ("front(distance=1)", "Cell type ahead: '.', '#', 'X', 'G', 'C'."),
            ("scan(max_distance=None)", "Free cells ahead before the next obstacle."),
            ("position() / x / y / heading", "Where the robot is and which way it faces."),
            ("battery / cargo / tick", "Remaining energy, carried items, current tick."),
            ("map()", "The grid as strings: '.' empty, '#' wall, 'X' obstacle, 'o' item, 'G' depot."),
            ("items() / depots()", "Undelivered items and delivery points."),
            ("deliver()", "Drop the whole cargo at the current depot cell."),
            ("say(message)", "Record a message event for the replay."),
        ),
    ),
    "automation_city": WorldSpec(
        id="automation_city",
        module_name="city_sim",
        source_path=SIM_DIR / "city_sim.py",
        title_ar="مدينة الأتمتة",
        title_en="Automation City",
        description_ar="مصنع يحرّكه كود بايثون: آلات، ناقلات، موارد وخطوط إنتاج.",
        description_en="A factory driven by Python: machines, haulers, resources and production lines.",
        entrypoint="program(city)",
        api_docs=(
            ("hauler(name)", "Get a hauler: move_to(x,y), load(machine,item,qty), unload(machine)."),
            ("machine(name)", "Inspect status, progress, input(), output(), produced()."),
            ("wait(n)", "Advance the simulation by n ticks (machines only work while time runs)."),
            ("storage()", "Everything delivered to sinks so far."),
            ("tick", "Current tick (read-only counter)."),
            ("map()", "Factory floor: 'M' machine, 'S' sink, 'H' hauler."),
            ("say(message)", "Record a message event."),
        ),
    ),
    "neural_civilization": WorldSpec(
        id="neural_civilization",
        module_name="neural_sim",
        source_path=SIM_DIR / "neural_sim.py",
        title_ar="الحضارة العصبية",
        title_en="Neural Civilization",
        description_ar="مجتمع من الكيانات المستقلة: موارد، مشاركة، جدولة وعدالة التوزيع.",
        description_en="A society of autonomous agents: resources, sharing, scheduling and fairness.",
        entrypoint="program(society)",
        api_docs=(
            ("on_tick(handler)", "Register a policy function called once per tick."),
            ("run(ticks=None)", "Advance the society until the tick budget is spent."),
            ("agents() / agent(name)", "Agent handles: move_to, gather, share, eat, deposit."),
            ("nodes(item=None)", "Resource nodes with amount > 0."),
            ("nearest_node(agent, item)", "Closest non-empty node (cheap greedy allocation)."),
            ("treasury()", "Everything gathered by the whole society."),
            ("tick", "Current tick."),
        ),
    ),
    "algorithm_gladiators": WorldSpec(
        id="algorithm_gladiators",
        module_name="algo_sim",
        source_path=SIM_DIR / "algo_sim.py",
        title_ar="مصارعو الخوارزميات",
        title_en="Algorithm Gladiators",
        description_ar="ساحة ترتيب وبحث بميزانية مقارنات: كل مقارنة تُحصى وتكلف.",
        description_en="A sorting and search arena with a comparison budget: every comparison counts.",
        entrypoint="program(arena)",
        api_docs=(
            ("size() / get(i) / snapshot()", "Read the array. Reading is free."),
            ("compare(i, j)", "Return -1/0/1 for cells i and j. This is the counted operation."),
            ("swap(i, j)", "Exchange two cells (counted)."),
            ("write(i, value)", "Overwrite a cell (counted)."),
            ("is_sorted() / inversions()", "Check the current order."),
            ("tick(n)", "Spend n ticks of the step budget."),
        ),
    ),
    "data_empire": WorldSpec(
        id="data_empire",
        module_name="data_sim",
        source_path=SIM_DIR / "data_sim.py",
        title_ar="إمبراطورية البيانات",
        title_en="Data Empire",
        description_ar="تدفّق سجلات حقيقي: صفِّ، حوّل، واجمع — والمخرجات تُحسب فعلياً.",
        description_en="A real record stream: filter, transform and aggregate - the outputs are computed.",
        entrypoint="program(pipeline)",
        api_docs=(
            ("source() / head(n) / size()", "Inspect the raw records."),
            ("set_transform(fn)", "Register a record -> record function."),
            ("set_filter(fn)", "Register a predicate; false rows are dropped."),
            ("run(limit=None)", "Push every row through filter -> transform."),
            ("sum(field) / count() / groups(field)", "Aggregate what you emitted."),
        ),
    ),
    "stem_cosmos": WorldSpec(
        id="stem_cosmos",
        module_name="sci_sim",
        source_path=SIM_DIR / "sci_sim.py",
        title_ar="كون العلوم",
        title_en="STEM Cosmos",
        description_ar="مختبر فيزياء حتمي: دفع، جاذبية، وقود ومدار.",
        description_en="A deterministic physics lab: thrust, gravity, fuel and orbit.",
        entrypoint="program(lab)",
        api_docs=(
            ("thrust(ax, ay)", "Spend fuel to accelerate this step."),
            ("step(n)", "Advance the integrator by n steps of dt."),
            ("position() / velocity() / altitude() / speed()", "Current state."),
            ("fuel_left() / steps()", "Remaining delta-v and elapsed steps."),
            ("orbital()", "True when high, fast and with near-zero vertical speed."),
        ),
    ),
    "agent_planet": WorldSpec(
        id="agent_planet",
        module_name="agent_sim",
        source_path=SIM_DIR / "agent_sim.py",
        title_ar="كوكب الوكلاء",
        title_en="Agent Planet",
        description_ar="بيئة وكيل يستدعي الأدوات: كل استدعاء يكلّف رصيداً وخطوة.",
        description_en="A tool-calling agent environment: every call spends credits and a step.",
        entrypoint="program(agent)",
        api_docs=(
            ("goal() / done() / tasks_left()", "Read the current task and progress."),
            ("think()", "One reasoning step (costs a tick)."),
            ("search(term) / lookup(key)", "Query the knowledge base."),
            ("calculate(expression)", "Evaluate an arithmetic expression from a safe character set."),
            ("fetch(key) / translate(text)", "Read notes and apply the glossary."),
            ("answer(value)", "Submit an answer; the world grades it and moves on."),
        ),
    ),
    "project_rescue": WorldSpec(
        id="project_rescue",
        module_name="rescue_sim",
        source_path=SIM_DIR / "rescue_sim.py",
        title_ar="إنقاذ المشاريع",
        title_en="Project Rescue",
        description_ar="قاعدة كود مكسورة: اقرأ المصدر، سجّل الإصلاح، واجتز الفحوص.",
        description_en="A broken codebase: read the source, register a fix and pass the checks.",
        entrypoint="program(repo)",
        api_docs=(
            ("names() / source(name) / bug_hint(name)", "Inspect the broken code as text."),
            ("checks(name)", "The arguments and expected values the fix must satisfy."),
            ("fix(name, fn)", "Register your working replacement."),
            ("run(name, *args)", "Call a registered fix."),
            ("verify()", "Run every check against your fixes."),
        ),
    ),
    "careerverse": WorldSpec(
        id="careerverse",
        module_name="career_sim",
        source_path=SIM_DIR / "career_sim.py",
        title_ar="عالم المهنة",
        title_en="CareerVerse",
        description_ar="تخطيط سباق تطويري: ترتيب المهام، الاعتماديات، المراجعة والجودة.",
        description_en="Sprint planning: task order, dependencies, review time and quality.",
        entrypoint="program(sprint)",
        api_docs=(
            ("task_ids() / task(id) / dependencies(id)", "Inspect the backlog."),
            ("plan(order)", "Choose the order in which tasks are built."),
            ("set_review_ratio(r)", "Share of capacity spent on review (0.0 - 0.6)."),
            ("ask_for_help(task_id)", "Costs a day, clears a blocker."),
            ("run()", "Simulate the sprint day by day."),
        ),
    ),
    "crisis_simulator": WorldSpec(
        id="crisis_simulator",
        module_name="crisis_sim",
        source_path=SIM_DIR / "crisis_sim.py",
        title_ar="محاكي الأزمات",
        title_en="Crisis Simulator",
        description_ar="الاستجابة للحوادث: أعطال، زمن الاستجابة، ميزانية وخسارة بيانات.",
        description_en="Incident response: outages, MTTR, budget and data loss.",
        entrypoint="program(ops)",
        api_docs=(
            ("alerts() / health(name) / names()", "See what is broken and where."),
            ("investigate(name)", "Free but reveals the root cause."),
            ("act(name, action, **kw)", "restart, scale, rollback, patch or noop."),
            ("wait(n)", "Advance the clock; unresolved incidents keep burning uptime."),
            ("money_left()", "Remaining incident budget."),
        ),
    ),
    "research_reactor": WorldSpec(
        id="research_reactor",
        module_name="research_sim",
        source_path=SIM_DIR / "research_sim.py",
        title_ar="مفاعل البحث",
        title_en="Research Reactor",
        description_ar="صمّم اختبار A/B: حجم العينة، الإحصاء، والقرار — مع إعادة حساب مستقلة.",
        description_en="Design an A/B test: sample size, the statistic, and the decision - independently recomputed.",
        entrypoint="program(lab)",
        api_docs=(
            ("sample(arm, count)", "Draw observations for 'A' or 'B'."),
            ("mean(values) / welch_p(a, b)", "Helpers you may use or replace with your own."),
            ("report(decision, effect, p_value, n_per_arm=None)", "Submit your conclusion."),
            ("truth()", "Only after the run: the hidden parameters."),
        ),
    ),
    "model_olympics": WorldSpec(
        id="model_olympics",
        module_name="olympics_sim",
        source_path=SIM_DIR / "olympics_sim.py",
        title_ar="أولمبياد النماذج",
        title_en="Model Olympics",
        description_ar="درّب مصنّفاً بلغة بايثون الصرفة وقارنه بخطوط أساس حقيقية.",
        description_en="Train a classifier in pure Python and compare it with honest baselines.",
        entrypoint="program(arena)",
        api_docs=(
            ("train_set()", "Labeled rows: (features, 0|1)."),
            ("test_features()", "The held-out feature rows you must predict."),
            ("submit(predictions)", "Submit 0/1 predictions."),
            ("peek_baseline() / score()", "Majority-class baseline and your live metrics."),
            ("tick(n)", "Declare compute work; the budget is wall-clock seconds."),
        ),
    ),
    "library_nexus": WorldSpec(
        id="library_nexus",
        module_name="library_sim",
        source_path=SIM_DIR / "library_sim.py",
        title_ar="مكتبة المعرفة",
        title_en="Library Nexus",
        description_ar="ابنِ محرك بحث صغيراً، وتحقّق منه بخصائص حقيقية على مجموعة مستندات.",
        description_en="Build a tiny search engine and validate it with real properties over a corpus.",
        entrypoint="program(shelf)",
        api_docs=(
            ("corpus() / doc(id) / size()", "The document collection."),
            ("implement('tokenize'|'build_index'|'search', fn)", "Register your components."),
            ("validate()", "Run the property-based checks."),
            ("query_terms()", "The queries your search will be judged on."),
        ),
    ),
    "knowledge_galaxy": WorldSpec(
        id="knowledge_galaxy",
        module_name="galaxy_sim",
        source_path=SIM_DIR / "galaxy_sim.py",
        title_ar="مجرة المعرفة",
        title_en="Knowledge Galaxy",
        description_ar="جدول مراجعاتك: منحنى نسيان حقيقي وميزانية مراجعات يومية.",
        description_en="Schedule your reviews: a real forgetting curve and a daily review budget.",
        entrypoint="program(galaxy)",
        api_docs=(
            ("candidates()", "Every node with its retention and difficulty."),
            ("retention(id) / weakest(n) / forgotten()", "Who is slipping away."),
            ("review(id)", "Review one node (limited by the daily budget)."),
            ("sleep(days=1)", "Advance the clock; retention decays."),
            ("daily_budget() / reviews_left()", "How many reviews today allows."),
        ),
    ),
}

def get_world(world_id: str) -> WorldSpec:
    if world_id not in WORLDS:
        raise KeyError(f"unknown world {world_id!r}; available: {sorted(WORLDS)}")
    return WORLDS[world_id]


def sandbox_files(world_id: str, config: dict) -> tuple[dict[str, str], dict]:
    """Return the files and job fragment needed to run a world in the sandbox."""
    spec = get_world(world_id)
    return {"pfnworld.py": spec.source()}, {"module": "pfnworld", "config": config}


def world_summary(locale: str = "en") -> list[dict]:
    out = []
    for spec in WORLDS.values():
        out.append(
            {
                "id": spec.id,
                "title": spec.title(locale),
                "title_ar": spec.title_ar,
                "title_en": spec.title_en,
                "description": spec.description(locale),
                "description_ar": spec.description_ar,
                "description_en": spec.description_en,
                "entrypoint": spec.entrypoint,
                "api_docs": [
                    {"signature": sig, "description": desc} for sig, desc in spec.api_docs
                ],
            }
        )
    return out
