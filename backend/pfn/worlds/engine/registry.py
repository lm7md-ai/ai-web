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

from pfn.worlds.sim import city_sim, neural_sim, robot_sim

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
