"""RoboVerse grid world - a self-contained, dependency-free simulation module.

This file is copied verbatim into the execution sandbox and imported by the
worker, so it must only use the Python standard library.  Everything the
learner sees (robot motion, collisions, battery drain, collected items) is
computed here and nothing is pre-baked: the learner's Python code is the only
source of behaviour.

Learner contract::

    def program(robot):
        while not robot.at_goal():
            if robot.front() == "wall":
                robot.turn_right()
            else:
                robot.move()
"""

from __future__ import annotations

import json
import random
from typing import Any, Callable

DIRS = ["N", "E", "S", "W"]
_DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


class CrashError(Exception):
    """Raised when the robot performs an illegal move and the world forbids it."""


class OutOfEnergyError(Exception):
    """Raised when the robot runs out of battery."""


class StepLimitError(Exception):
    """Raised when the mission's tick budget is exhausted."""


class Cell:
    EMPTY = "."
    WALL = "#"
    OBSTACLE = "X"
    CHARGER = "C"
    GOAL = "G"


class Event:
    """A recorded, replayable simulation event."""

    __slots__ = ("tick", "type", "payload", "robot")

    def __init__(self, tick: int, type_: str, payload: dict | None = None, robot: str = "") -> None:
        self.tick = tick
        self.type = type_
        self.payload = payload or {}
        self.robot = robot

    def to_dict(self) -> dict:
        return {"tick": self.tick, "type": self.type, "robot": self.robot, **self.payload}


class Robot:
    """Runtime state of one robot."""

    def __init__(self, name: str, x: int, y: int, heading: str = "N", battery: int = 100) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.heading = heading
        self.battery = battery
        self.cargo: dict[str, int] = {}
        self.visited: set[tuple[int, int]] = {(x, y)}
        self.alive = True
        self.crashed = False
        self.actions = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "heading": self.heading,
            "battery": self.battery,
            "cargo": dict(self.cargo),
            "visited": sorted(self.visited),
            "alive": self.alive,
            "crashed": self.crashed,
            "actions": self.actions,
        }


class World:
    """Grid world state and the transition rules that govern it."""

    def __init__(self, config: dict) -> None:
        cfg = dict(config or {})
        self.width = int(cfg.get("width", 10))
        self.height = int(cfg.get("height", 10))
        self.max_ticks = int(cfg.get("max_ticks", 200))
        self.move_cost = int(cfg.get("move_cost", 1))
        self.turn_cost = int(cfg.get("turn_cost", 0))
        self.crash_on_blocked = bool(cfg.get("crash_on_blocked", False))
        self.tick = 0
        self.events: list[Event] = []
        self.rng = random.Random(cfg.get("seed", 7))
        self.grid = self._build_grid(cfg)
        self.items: dict[tuple[int, int], dict[str, int]] = {}
        for item in cfg.get("items", []):
            self.items[(int(item["x"]), int(item["y"]))] = dict(item.get("contains", {"part": 1}))
        self.depots = [tuple(d) for d in cfg.get("depots", [])]  # type: ignore[misc]
        for depot in self.depots:
            self.grid[depot[1]][depot[0]] = Cell.GOAL
        self.robots: dict[str, Robot] = {}
        for spec in cfg.get("robots", [{"name": "r1", "x": 0, "y": 0}]):
            self.robots[spec.get("name", "r1")] = Robot(
                spec.get("name", "r1"),
                int(spec.get("x", 0)),
                int(spec.get("y", 0)),
                str(spec.get("heading", "N")),
                int(spec.get("battery", cfg.get("battery", 100))),
            )
        self.objectives = cfg.get("objectives", [])
        self.finished = False
        self.stop_reason: str | None = None

    # ------------------------------------------------------------- grid
    def _build_grid(self, cfg: dict) -> list[list[str]]:
        rows = cfg.get("map")
        if rows:
            grid = [list(row) for row in rows]
            self.height = len(grid)
            self.width = max(len(row) for row in grid)
            for row in grid:
                while len(row) < self.width:
                    row.append(Cell.WALL)
            return grid
        grid = [[Cell.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        for obstacle in cfg.get("obstacles", []):
            x, y = int(obstacle[0]), int(obstacle[1])
            if self.in_bounds(x, y):
                grid[y][x] = Cell.OBSTACLE
        return grid

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def cell_at(self, x: int, y: int) -> str:
        if not self.in_bounds(x, y):
            return Cell.WALL
        return self.grid[y][x]

    def log(self, type_: str, robot: str = "", **payload) -> None:
        self.events.append(Event(self.tick, type_, payload, robot))

    # ------------------------------------------------------------ clocks
    def spend(self, robot: Robot, cost: int) -> None:
        robot.actions += 1
        robot.battery -= cost
        if robot.battery <= 0:
            robot.battery = 0
            robot.alive = False
            self.log("out_of_energy", robot.name, x=robot.x, y=robot.y)
            raise OutOfEnergyError(f"{robot.name} ran out of battery after {self.tick} ticks")

    def advance(self, robot: Robot, cost: int) -> None:
        """Consume one simulation tick for the given robot."""
        self.spend(robot, cost)
        self.tick += 1
        if self.tick > self.max_ticks:
            self.finished = True
            self.stop_reason = "tick_limit"
            self.log("tick_limit", robot.name, tick=self.tick)
            raise StepLimitError(f"mission stopped after {self.max_ticks} ticks")

    # ---------------------------------------------------------- movement
    def move(self, robot: Robot, steps: int = 1) -> bool:
        for _ in range(int(steps)):
            dx, dy = _DELTA[robot.heading]
            nx, ny = robot.x + dx, robot.y + dy
            target = self.cell_at(nx, ny)
            if target in (Cell.WALL, Cell.OBSTACLE):
                self.log("blocked", robot.name, x=nx, y=ny, cell=target)
                if self.crash_on_blocked:
                    robot.crashed = True
                    robot.alive = False
                    self.log("crash", robot.name, x=nx, y=ny)
                    raise CrashError(
                        f"{robot.name} crashed into {target} at ({nx}, {ny}) while facing {robot.heading}"
                    )
                self.advance(robot, self.move_cost)
                return False
            robot.x, robot.y = nx, ny
            robot.visited.add((nx, ny))
            self.log("move", robot.name, x=nx, y=ny, heading=robot.heading, battery=robot.battery)
            self.advance(robot, self.move_cost)
            self._auto_pickup(robot)
        return True

    def turn(self, robot: Robot, direction: int) -> None:
        index = (DIRS.index(robot.heading) + direction) % 4
        robot.heading = DIRS[index]
        self.log("turn", robot.name, heading=robot.heading)
        self.advance(robot, self.turn_cost)

    def _auto_pickup(self, robot: Robot) -> None:
        pos = (robot.x, robot.y)
        if pos in self.items and self.items[pos]:
            for item, qty in list(self.items[pos].items()):
                robot.cargo[item] = robot.cargo.get(item, 0) + qty
                self.log("pickup", robot.name, item=item, qty=qty, x=pos[0], y=pos[1])
            self.items[pos] = {}

    def deposit(self, robot: Robot) -> int:
        pos = (robot.x, robot.y)
        if pos not in self.depots:
            return 0
        delivered = 0
        for item, qty in list(robot.cargo.items()):
            if qty:
                delivered += qty
                self.log("deliver", robot.name, item=item, qty=qty, x=pos[0], y=pos[1])
                robot.cargo[item] = 0
        return delivered

    # ----------------------------------------------------------- sensors
    def look(self, robot: Robot, distance: int = 1) -> str:
        dx, dy = _DELTA[robot.heading]
        return self.cell_at(robot.x + dx * distance, robot.y + dy * distance)

    def ray(self, robot: Robot, max_distance: int | None = None) -> int:
        limit = max_distance or max(self.width, self.height)
        dx, dy = _DELTA[robot.heading]
        for step in range(1, limit + 1):
            x, y = robot.x + dx * step, robot.y + dy * step
            cell = self.cell_at(x, y)
            if cell in (Cell.WALL, Cell.OBSTACLE):
                return step - 1
        return limit


class RobotAPI:
    """The object handed to the learner's ``program(...)`` function."""

    def __init__(self, world: World, robot: Robot) -> None:
        self._world = world
        self._robot = robot

    # motion ------------------------------------------------------------
    def move(self, steps: int = 1) -> bool:
        return self._world.move(self._robot, steps)

    def turn_left(self) -> None:
        self._world.turn(self._robot, -1)

    def turn_right(self) -> None:
        self._world.turn(self._robot, 1)

    def wait(self) -> None:
        self._world.log("wait", self._robot.name)
        self._world.advance(self._robot, 0)

    # sensing -----------------------------------------------------------
    def front(self, distance: int = 1) -> str:
        return self._world.look(self._robot, distance)

    def scan(self, max_distance: int | None = None) -> int:
        """Distance to the nearest obstacle or wall ahead (cells)."""
        return self._world.ray(self._robot, max_distance)

    def position(self) -> tuple[int, int]:
        return (self._robot.x, self._robot.y)

    @property
    def x(self) -> int:
        return self._robot.x

    @property
    def y(self) -> int:
        return self._robot.y

    @property
    def heading(self) -> str:
        return self._robot.heading

    @property
    def battery(self) -> int:
        return self._robot.battery

    @property
    def cargo(self) -> dict[str, int]:
        return dict(self._robot.cargo)

    @property
    def tick(self) -> int:
        return self._world.tick

    def map(self) -> list[str]:
        """The full grid as strings ('.' empty, '#' wall, 'X' obstacle, 'G' goal, 'C' charger)."""
        rows = []
        for y, row in enumerate(self._world.grid):
            cells = []
            for x, cell in enumerate(row):
                if (x, y) in self._world.items and self._world.items[(x, y)]:
                    cells.append("o")
                else:
                    cells.append(cell)
            rows.append("".join(cells))
        return rows

    def items(self) -> list[dict]:
        return [
            {"x": x, "y": y, "contains": contents}
            for (x, y), contents in self._world.items.items()
            if contents
        ]

    def depots(self) -> list[tuple[int, int]]:
        return list(self._world.depots)

    def deliver(self) -> int:
        return self._world.deposit(self._robot)

    def say(self, message: str) -> None:
        self._world.log("say", self._robot.name, message=str(message)[:120])

    def at_goal(self) -> bool:
        return (self._robot.x, self._robot.y) in self._world.depots


class FleetAPI:
    """Multi-robot controller used when a mission configures several robots."""

    def __init__(self, world: World) -> None:
        self._world = world
        self.robots = {name: RobotAPI(world, bot) for name, bot in world.robots.items()}

    def robot(self, name: str) -> RobotAPI:
        if name not in self.robots:
            raise KeyError(f"unknown robot {name!r}; available: {sorted(self.robots)}")
        return self.robots[name]

    def all(self) -> list[RobotAPI]:
        return list(self.robots.values())

    @property
    def tick(self) -> int:
        return self._world.tick

    def map(self) -> list[str]:
        return next(iter(self.robots.values())).map() if self.robots else []

    def say(self, message: str) -> None:
        self._world.log("say", "fleet", message=str(message)[:120])


def build(config: dict) -> tuple[Any, World]:
    """Sandbox entry point: build the world and the API object."""
    world = World(config)
    if len(world.robots) == 1:
        only = next(iter(world.robots.values()))
        api: Any = RobotAPI(world, only)
    else:
        api = FleetAPI(world)
    world.log("start", "", tick=0, robots=len(world.robots))
    return api, world


def evaluate_objectives(world: World) -> tuple[list[dict], float]:
    """Check the mission objectives against the final world state."""
    results: list[dict] = []
    for objective in world.objectives:
        kind = objective.get("type", "visit")
        if kind == "visit":
            targets = {tuple(t) for t in objective.get("targets", [])}
            visited_any = set()
            for bot in world.robots.values():
                visited_any |= bot.visited
            missing = sorted(targets - visited_any)
            ok = not missing
            results.append(
                {
                    "type": kind,
                    "ok": ok,
                    "missing": missing,
                    "detail": f"{len(targets) - len(missing)}/{len(targets)} targets visited",
                }
            )
        elif kind == "reach":
            target = tuple(objective.get("target", (0, 0)))
            robots_ok = [b.name for b in world.robots.values() if (b.x, b.y) == target]
            ok = bool(robots_ok) and all(
                (b.x, b.y) == target for b in world.robots.values()
            ) if objective.get("all", True) else bool(robots_ok)
            results.append({"type": kind, "ok": ok, "detail": f"robots at target: {robots_ok}"})
        elif kind == "deliver":
            needed = int(objective.get("quantity", 1))
            delivered = sum(1 for e in world.events if e.type == "deliver")
            ok = delivered >= needed
            results.append({"type": kind, "ok": ok, "detail": f"delivered {delivered}/{needed}"})
        elif kind == "collect":
            needed = dict(objective.get("items", {}))
            held: dict[str, int] = {}
            for bot in world.robots.values():
                for item, qty in bot.cargo.items():
                    held[item] = held.get(item, 0) + qty
            ok = all(held.get(item, 0) >= qty for item, qty in needed.items())
            results.append({"type": kind, "ok": ok, "detail": f"cargo {held} need {needed}"})
        elif kind == "ticks":
            limit = int(objective.get("max", world.max_ticks))
            ok = world.tick <= limit
            results.append({"type": kind, "ok": ok, "detail": f"used {world.tick}/{limit} ticks"})
        elif kind == "battery":
            minimum = int(objective.get("min", 0))
            ok = all(bot.battery >= minimum for bot in world.robots.values())
            results.append(
                {
                    "type": kind,
                    "ok": ok,
                    "detail": ", ".join(f"{b.name}={b.battery}" for b in world.robots.values()),
                }
            )
        elif kind == "no_crash":
            ok = not any(bot.crashed for bot in world.robots.values())
            results.append({"type": kind, "ok": ok, "detail": "no crash" if ok else "a robot crashed"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})

    passed = sum(1 for r in results if r["ok"])
    score = round(passed / len(results), 3) if results else 0.0
    return results, score


def result(api: Any, world: World) -> dict:
    """Sandbox exit point: serialise the outcome and the recorded events."""
    objectives, score = evaluate_objectives(world)
    ok = all(o["ok"] for o in objectives) and not any(bot.crashed for bot in world.robots.values())
    return {
        "world": "roboverse",
        "ok": ok,
        "score": score,
        "tick": world.tick,
        "stop_reason": world.stop_reason or ("completed" if ok else "objectives_unmet"),
        "robots": {name: bot.to_dict() for name, bot in world.robots.items()},
        "objectives": objectives,
        "events": [event.to_dict() for event in world.events][-2000:],
        "grid": ["".join(row) for row in world.grid],
        "stats": {
            "moves": sum(1 for e in world.events if e.type == "move"),
            "turns": sum(1 for e in world.events if e.type == "turn"),
            "blocked": sum(1 for e in world.events if e.type == "blocked"),
            "deliveries": sum(1 for e in world.events if e.type == "deliver"),
            "battery_left": sum(bot.battery for bot in world.robots.values()),
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    demo = {
        "width": 6,
        "height": 5,
        "robots": [{"name": "r1", "x": 0, "y": 0, "heading": "E", "battery": 60}],
        "obstacles": [[2, 0], [2, 1]],
        "depots": [[5, 4]],
        "objectives": [{"type": "reach", "target": [5, 4]}, {"type": "no_crash"}],
        "max_ticks": 80,
    }
    api, world = build(demo)
    try:
        for _ in range(4):
            api.move()
        api.turn_right()
        api.move()
        for _ in range(3):
            api.turn_left()
            api.move()
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:1200])
