"""Mission catalogue for the three simulation worlds.

Every mission ships with a *reference solution*: the test suite executes it in
the real sandbox to prove the mission is solvable and that the objectives are
reachable by ordinary Python.  Nothing here is validated by keyword matching.
"""

from __future__ import annotations

from pfn.domain.missions.models import Mission

MISSIONS: list[Mission] = [
    # ------------------------------------------------------------ RoboVerse
    Mission(
        id="robo.first_steps",
        world="roboverse",
        title_ar="الخطوات الأولى",
        title_en="First Steps",
        order_index=1,
        difficulty=1,
        skills=("robo.control_flow", "core.loops"),
        concepts_ar="التكرار والتحكم بالروبوت: كرّر الحركة حتى تصل إلى الهدف.",
        concepts_en="Loops and robot control: repeat a move until the goal is reached.",
        brief_ar=(
            "الروبوت يواجه الشرق في شبكة مفتوحة. الهدف عند (7, 4).\n\n"
            "اكتب `program(robot)` تُحرّك الروبوت إلى نقطة التسليم.\n"
            "استخدم `robot.move()` و`robot.turn_right()` و`robot.deliver()`.\n"
            "المهمة تنجح فقط عندما يصل الروبوت فعلياً إلى الخلية الهدف."
        ),
        brief_en=(
            "The robot faces east on an open grid. The depot is at (7, 4).\n\n"
            "Write `program(robot)` that drives the robot to the delivery cell.\n"
            "Use `robot.move()`, `robot.turn_right()` and `robot.deliver()`.\n"
            "The mission only succeeds when the robot physically reaches the target."
        ),
        config={
            "width": 8,
            "height": 6,
            "robots": [{"name": "r1", "x": 0, "y": 4, "heading": "E", "battery": 100}],
            "depots": [[7, 4]],
            "objectives": [{"type": "reach", "target": [7, 4]}, {"type": "no_crash"}],
            "max_ticks": 60,
        },
        starter_code=(
            "def program(robot):\n"
            "    # TODO: drive the robot to the depot at (7, 4)\n"
            "    pass\n"
        ),
        reference_solution=(
            "def program(robot):\n"
            "    for _ in range(7):\n"
            "        robot.move()\n"
            "    robot.deliver()\n"
        ),
        hints=(
            "`robot.position()` returns (x, y). Compare it with the depot position.",
            "You can loop while the robot has not reached x == 7.",
            "robot.move() returns False when the way is blocked - useful as a loop guard.",
        ),
    ),
    Mission(
        id="robo.avoid_walls",
        world="roboverse",
        title_ar="تجاوز العوائق",
        title_en="Around the Wall",
        order_index=2,
        difficulty=2,
        skills=("robo.sensors", "core.conditions", "core.loops"),
        concepts_ar="المستشعرات والشروط: تحقّق مما أمامك قبل التحرك.",
        concepts_en="Sensors and conditionals: check what is ahead before moving.",
        brief_ar=(
            "جدار من العوائق يقطع الطريق مباشرة. الهدف عند (7, 4) والروبوت عند (0, 4).\n\n"
            "استخدم `robot.front()` (أو `robot.scan()`) لتقرر متى تتحرك ومتى تلتفت.\n"
            "الاصطدام يُنهي المهمة بالفشل."
        ),
        brief_en=(
            "A wall of obstacles blocks the direct route. The depot is at (7, 4), the robot starts at (0, 4).\n\n"
            "Use `robot.front()` (or `robot.scan()`) to decide when to move and when to turn.\n"
            "A crash ends the mission as a failure."
        ),
        config={
            "width": 8,
            "height": 6,
            "robots": [{"name": "r1", "x": 0, "y": 4, "heading": "E", "battery": 120}],
            "obstacles": [[3, 2], [3, 3], [3, 4], [3, 5]],
            "depots": [[7, 4]],
            "objectives": [
                {"type": "reach", "target": [7, 4]},
                {"type": "no_crash"},
                {"type": "ticks", "max": 40},
            ],
            "max_ticks": 80,
            "crash_on_blocked": False,
        },
        starter_code=(
            "def program(robot):\n"
            "    # Tip: robot.front() tells you what is in the next cell\n"
            "    pass\n"
        ),
        reference_solution=(
            "def program(robot):\n"
            "    while robot.y > 1:\n"
            "        while robot.heading != 'N':\n"
            "            robot.turn_right()\n"
            "        robot.move()\n"
            "    while robot.heading != 'E':\n"
            "        robot.turn_left()\n"
            "    while robot.x < 7:\n"
            "        robot.move()\n"
            "    while robot.heading != 'S':\n"
            "        robot.turn_right()\n"
            "    while robot.y < 4:\n"
            "        robot.move()\n"
            "    robot.deliver()\n"
        ),
        hints=(
            "Print robot.map() once to see the grid layout ('#' wall, 'X' obstacle, 'G' depot).",
            "Go around: move north until the wall ends, then east, then back south.",
            "A helper function `face(robot, direction)` keeps the code readable.",
        ),
    ),
    Mission(
        id="robo.patrol",
        world="roboverse",
        title_ar="دورية التحقق",
        title_en="Patrol Route",
        order_index=3,
        difficulty=2,
        skills=("core.loops", "ds.lists", "robo.sensors"),
        concepts_ar="قوائم الإحداثيات والتكرار: زُر كل النقاط المطلوبة.",
        concepts_en="Lists of coordinates and iteration: visit every checkpoint.",
        brief_ar=(
            "يجب أن يمر الروبوت على أربع نقاط تفتيش قبل العودة إلى نقطة التسليم.\n"
            "النقاط: (1,1)، (6,1)، (6,4)، (1,4) ثم التسليم عند (0,0).\n\n"
            "خزّن النقاط في قائمة ومرّ عليها بحلقة."
        ),
        brief_en=(
            "The robot must pass through four checkpoints before returning to the depot.\n"
            "Checkpoints: (1,1), (6,1), (6,4), (1,4), then deliver at (0,0).\n\n"
            "Store the points in a list and iterate over them."
        ),
        config={
            "width": 8,
            "height": 6,
            "robots": [{"name": "r1", "x": 0, "y": 0, "heading": "E", "battery": 200}],
            "depots": [[0, 0]],
            "objectives": [
                {"type": "visit", "targets": [[1, 1], [6, 1], [6, 4], [1, 4]]},
                {"type": "reach", "target": [0, 0]},
                {"type": "no_crash"},
            ],
            "max_ticks": 120,
        },
        starter_code=(
            "CHECKPOINTS = [(1, 1), (6, 1), (6, 4), (1, 4)]\n\n"
            "def program(robot):\n"
            "    # TODO: visit every checkpoint, then return to (0, 0)\n"
            "    pass\n"
        ),
        reference_solution=(
            "CHECKPOINTS = [(1, 1), (6, 1), (6, 4), (1, 4)]\n\n"
            "def face(robot, direction):\n"
            "    while robot.heading != direction:\n"
            "        robot.turn_right()\n\n"
            "def walk_to(robot, tx, ty):\n"
            "    while robot.x != tx:\n"
            "        face(robot, 'E' if tx > robot.x else 'W')\n"
            "        robot.move()\n"
            "    while robot.y != ty:\n"
            "        face(robot, 'S' if ty > robot.y else 'N')\n"
            "        robot.move()\n\n"
            "def program(robot):\n"
            "    for cx, cy in CHECKPOINTS:\n"
            "        walk_to(robot, cx, cy)\n"
            "    walk_to(robot, 0, 0)\n"
            "    robot.deliver()\n"
        ),
        hints=(
            "Write a `walk_to(robot, x, y)` helper: align x first, then y.",
            "Turning until `robot.heading` matches the wanted direction is a small while-loop.",
            "The `visit` objective checks robot.visited, not the final position.",
        ),
    ),
    Mission(
        id="robo.delivery",
        world="roboverse",
        title_ar="التوصيل",
        title_en="Pickup and Delivery",
        order_index=4,
        difficulty=3,
        skills=("robo.sensors", "ds.dicts", "core.functions"),
        concepts_ar="القواميس وحالة الروبوت: التقط الشحنة ثم سلّمها.",
        concepts_en="Dictionaries and robot state: collect the cargo, then deliver it.",
        brief_ar=(
            "توجد شحنة عند (7, 1) ونقطة تسليم عند (0, 5).\n"
            "تحرّك إلى الشحنة (يُلتقط تلقائياً عند المرور)، ثم عد إلى نقطة التسليم واستدعِ `robot.deliver()`.\n"
            "الميزانية: 60 tick فقط."
        ),
        brief_en=(
            "A crate sits at (7, 1) and the depot is at (0, 5).\n"
            "Drive onto the crate (it is collected automatically), then reach the depot and call `robot.deliver()`.\n"
            "Budget: 60 ticks."
        ),
        config={
            "width": 8,
            "height": 6,
            "robots": [{"name": "r1", "x": 0, "y": 0, "heading": "E", "battery": 200}],
            "items": [{"x": 7, "y": 1, "contains": {"crate": 1}}],
            "depots": [[0, 5]],
            "objectives": [
                {"type": "deliver", "quantity": 1},
                {"type": "no_crash"},
                {"type": "ticks", "max": 60},
            ],
            "max_ticks": 100,
        },
        starter_code=(
            "def program(robot):\n"
            "    # 1) reach the crate, 2) reach the depot, 3) deliver\n"
            "    pass\n"
        ),
        reference_solution=(
            "def face(robot, direction):\n"
            "    while robot.heading != direction:\n"
            "        robot.turn_right()\n\n"
            "def walk_to(robot, tx, ty):\n"
            "    while robot.x != tx:\n"
            "        face(robot, 'E' if tx > robot.x else 'W')\n"
            "        robot.move()\n"
            "    while robot.y != ty:\n"
            "        face(robot, 'S' if ty > robot.y else 'N')\n"
            "        robot.move()\n\n"
            "def program(robot):\n"
            "    walk_to(robot, 7, 1)\n"
            "    walk_to(robot, 0, 5)\n"
            "    robot.deliver()\n"
        ),
        hints=(
            "`robot.cargo` is a dict - after driving onto the crate it holds {'crate': 1}.",
            "Delivering only works while standing on a depot cell; check robot.depots().",
            "Count ticks: 7 + 1 + 7 + 4 = 19 moves plus turns, well inside the budget.",
        ),
    ),
    Mission(
        id="robo.maze",
        world="roboverse",
        title_ar="المتاهة والبحث بالعرض",
        title_en="Maze and BFS",
        order_index=5,
        difficulty=4,
        skills=("algo.bfs", "robo.pathfinding", "ds.stacks_queues", "ds.graphs"),
        concepts_ar="البحث بالعرض على شبكة: ابنِ أقصر طريق ثم نفّذه.",
        concepts_en="Breadth-first search on a grid: build the shortest route, then execute it.",
        brief_ar=(
            "متاهة حقيقية: الطريق الوحيد طويل وملتوٍ.\n"
            "اقرأ الخريطة عبر `robot.map()`، نفّذ BFS من موقع الروبوت إلى الهدف، "
            "ثم حوّل المسار إلى حركات.\n\n"
            "تلميح: الخلايا '.' و'G' سالكة، و'#' و'X' مغلقة."
        ),
        brief_en=(
            "A real maze: the only route is long and winding.\n"
            "Read the grid with `robot.map()`, run BFS from the robot to the goal, "
            "then translate the path into moves.\n\n"
            "Hint: '.' and 'G' are walkable, '#' and 'X' are blocked."
        ),
        config={
            "width": 11,
            "height": 7,
            "map": [
                "###########",
                "#.........#",
                "#.#######.#",
                "#.#.....#.#",
                "#.#.###.#.#",
                "#.....#...#",
                "###########",
            ],
            "robots": [{"name": "r1", "x": 1, "y": 1, "heading": "S", "battery": 400}],
            "depots": [[5, 5]],
            "objectives": [
                {"type": "reach", "target": [5, 5]},
                {"type": "no_crash"},
                {"type": "ticks", "max": 70},
            ],
            "max_ticks": 140,
        },
        starter_code=(
            "from collections import deque\n\n"
            "def program(robot):\n"
            "    # 1) read the grid, 2) BFS from the robot to the depot,\n"
            "    # 3) convert the path into moves\n"
            "    pass\n"
        ),
        reference_solution=(
            "from collections import deque\n\n"
            "DELTAS = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}\n"
            "ORDER = ['N', 'E', 'S', 'W']\n\n"
            "def bfs(grid, start, goal):\n"
            "    queue = deque([start])\n"
            "    parent = {start: None}\n"
            "    while queue:\n"
            "        cell = queue.popleft()\n"
            "        if cell == goal:\n"
            "            break\n"
            "        x, y = cell\n"
            "        for dx, dy in DELTAS.values():\n"
            "            nx, ny = x + dx, y + dy\n"
            "            if 0 <= ny < len(grid) and 0 <= nx < len(grid[ny]):\n"
            "                if grid[ny][nx] in '.GoC' and (nx, ny) not in parent:\n"
            "                    parent[(nx, ny)] = cell\n"
            "                    queue.append((nx, ny))\n"
            "    if goal not in parent:\n"
            "        return []\n"
            "    path, node = [], goal\n"
            "    while node is not None:\n"
            "        path.append(node)\n"
            "        node = parent[node]\n"
            "    return list(reversed(path))\n\n"
            "def face(robot, direction):\n"
            "    while robot.heading != direction:\n"
            "        robot.turn_right()\n\n"
            "def program(robot):\n"
            "    grid = robot.map()\n"
            "    goal = robot.depots()[0]\n"
            "    path = bfs(grid, robot.position(), tuple(goal))\n"
            "    for cell in path[1:]:\n"
            "        dx = cell[0] - robot.x\n"
            "        dy = cell[1] - robot.y\n"
            "        wanted = 'E' if dx > 0 else 'W' if dx < 0 else 'S' if dy > 0 else 'N'\n"
            "        face(robot, wanted)\n"
            "        robot.move()\n"
            "    robot.deliver()\n"
        ),
        hints=(
            "BFS needs a queue (collections.deque) and a dict mapping each cell to its predecessor.",
            "Walkable characters are '.', 'G', 'o' and 'C'.",
            "After BFS, walk the path cell by cell: face the right direction, then move().",
        ),
    ),
    Mission(
        id="robo.energy_budget",
        world="roboverse",
        title_ar="ميزانية الطاقة",
        title_en="Energy Budget",
        order_index=6,
        difficulty=4,
        skills=("robo.energy", "algo.complexity", "core.functions"),
        concepts_ar="التحسين تحت القيود: كل حركة تكلف طاقة، فاختر أقصر طريق.",
        concepts_en="Optimisation under constraints: every move costs energy, so pick the shortest route.",
        brief_ar=(
            "البطارية 30 وحدة فقط: كل حركة تكلف 1 وكل التفاتة تكلف 1 أيضاً.\n"
            "الهدف عند (6,0) والروبوت يبدأ عند (0,0) مواجهاً الشرق، والعوائق تحيط بالطريق المباشر.\n"
            "أوصل الشحنة دون نفاد البطارية: `battery` يجب أن يبقى ≥ 5."
        ),
        brief_en=(
            "The battery holds only 30 units: each move costs 1 and each turn costs 1.\n"
            "The depot is at (6,0); the robot starts at (0,0) facing east, with obstacles around the direct route.\n"
            "Deliver without running dry: `battery` must stay >= 5."
        ),
        config={
            "width": 8,
            "height": 5,
            "robots": [{"name": "r1", "x": 0, "y": 0, "heading": "E", "battery": 30}],
            "obstacles": [[2, 0], [5, 1], [1, 2]],
            "items": [{"x": 4, "y": 3, "contains": {"cell": 1}}],
            "depots": [[6, 0]],
            "objectives": [
                {"type": "deliver", "quantity": 1},
                {"type": "battery", "min": 5},
                {"type": "no_crash"},
            ],
            "max_ticks": 60,
            "turn_cost": 1,
            "move_cost": 1,
        },
        starter_code=(
            "def program(robot):\n"
            "    # Every move AND every turn costs one battery unit - plan first.\n"
            "    pass\n"
        ),
        reference_solution=(
            "ORDER = ['N', 'E', 'S', 'W']\n\n"
            "def face(robot, direction):\n"
            "    diff = (ORDER.index(direction) - ORDER.index(robot.heading)) % 4\n"
            "    if diff == 3:  # one turn left is cheaper than three turns right\n"
            "        robot.turn_left()\n"
            "        return\n"
            "    for _ in range(diff):\n"
            "        robot.turn_right()\n\n"
            "def walk_to(robot, tx, ty):\n"
            "    if robot.x != tx:\n"
            "        face(robot, 'E' if tx > robot.x else 'W')\n"
            "        while robot.x != tx:\n"
            "            if not robot.move():\n"
            "                break  # blocked: never spin on a blocked move\n"
            "    if robot.y != ty:\n"
            "        face(robot, 'S' if ty > robot.y else 'N')\n"
            "        while robot.y != ty:\n"
            "            if not robot.move():\n"
            "                break\n\n"
            "def program(robot):\n"
            "    # Waypoints skirt the obstacles at (2,0), (5,1) and (1,2).\n"
            "    for x, y in [(1, 0), (1, 1), (4, 1), (4, 3), (4, 0), (6, 0)]:\n"
            "        walk_to(robot, x, y)\n"
            "    robot.deliver()\n"
        ),
        hints=(
            "Moving in a straight line is cheaper than zig-zagging: align one axis at a time.",
            "Turn twice to go back is 2 battery - avoid unnecessary turns.",
            "Print robot.battery to check your budget as you experiment.",
        ),
    ),
    Mission(
        id="robo.fleet",
        world="roboverse",
        title_ar="أسطول الروبوتات",
        title_en="Robot Fleet",
        order_index=7,
        difficulty=5,
        skills=("robo.coordination", "civ.scheduling", "core.oop_composition"),
        concepts_ar="تعدد الروبوتات وتخصيص المهام: نسّق بين وحدتين لتوصيل شحنتين.",
        concepts_en="Multiple robots and task allocation: coordinate two units to deliver two crates.",
        brief_ar=(
            "روبوتان: r1 عند (0,0) وr2 عند (7,4). شحنتان عند (7,0) و(0,4)، ونقطة التسليم عند (4,2).\n"
            "استقبل `fleet` بدل `robot`: `fleet.robot('r1')` و`fleet.all()`.\n"
            "يجب تسليم شحنتين."
        ),
        brief_en=(
            "Two robots: r1 at (0,0) and r2 at (7,4). Two crates at (7,0) and (0,4), depot at (4,2).\n"
            "Your function receives a `fleet`: use `fleet.robot('r1')` and `fleet.all()`.\n"
            "Two deliveries are required."
        ),
        config={
            "width": 8,
            "height": 5,
            "robots": [
                {"name": "r1", "x": 0, "y": 0, "heading": "E", "battery": 200},
                {"name": "r2", "x": 7, "y": 4, "heading": "W", "battery": 200},
            ],
            "items": [
                {"x": 7, "y": 0, "contains": {"crate": 1}},
                {"x": 0, "y": 4, "contains": {"crate": 1}},
            ],
            "depots": [[4, 2]],
            "objectives": [
                {"type": "deliver", "quantity": 2},
                {"type": "no_crash"},
                {"type": "ticks", "max": 60},
            ],
            "max_ticks": 120,
        },
        starter_code=(
            "def program(fleet):\n"
            "    # fleet.robot('r1'), fleet.robot('r2'), fleet.all()\n"
            "    pass\n"
        ),
        reference_solution=(
            "def face(robot, direction):\n"
            "    while robot.heading != direction:\n"
            "        robot.turn_right()\n\n"
            "def walk_to(robot, tx, ty):\n"
            "    if robot.x != tx:\n"
            "        face(robot, 'E' if tx > robot.x else 'W')\n"
            "        while robot.x != tx:\n"
            "            robot.move()\n"
            "    if robot.y != ty:\n"
            "        face(robot, 'S' if ty > robot.y else 'N')\n"
            "        while robot.y != ty:\n"
            "            robot.move()\n\n"
            "def run_route(robot, crate, depot):\n"
            "    walk_to(robot, crate[0], crate[1])\n"
            "    walk_to(robot, depot[0], depot[1])\n"
            "    robot.deliver()\n\n"
            "def program(fleet):\n"
            "    r1 = fleet.robot('r1')\n"
            "    r2 = fleet.robot('r2')\n"
            "    run_route(r1, (7, 0), (4, 2))\n"
            "    run_route(r2, (0, 4), (4, 2))\n"
        ),
        hints=(
            "Give each robot its nearest crate: that is the greedy allocation.",
            "Write one reusable `run_route(robot, crate, depot)` helper and call it twice.",
            "Both robots must finish: the 'deliver' objective counts total deliveries.",
        ),
    ),
    # ------------------------------------------------------ Automation City
    Mission(
        id="city.first_line",
        world="automation_city",
        title_ar="خط الإنتاج الأول",
        title_en="First Production Line",
        order_index=1,
        difficulty=2,
        skills=("core.loops", "core.functions", "robo.simulation"),
        concepts_ar="الحلقات والدوال: انقل الخام إلى الفرن ثم صدّر المنتج.",
        concepts_en="Loops and functions: carry ore to the smelter, then export the product.",
        brief_ar=(
            "المنجم `mine` مصدر لا نهائي للخام، والفرن `smelter` يحول 2 خام إلى لوح معدني خلال 3 نبضات، "
            "ومنفذ التصدير `export` يستلم المنتجات.\n\n"
            "المطلوب: تسليم لوحين معدنيين (plate) إلى منفذ التصدير خلال 100 نبضة."
        ),
        brief_en=(
            "The `mine` is an infinite ore source, the `smelter` turns 2 ore into 1 plate over 3 ticks, "
            "and the `export` sink accepts finished goods.\n\n"
            "Goal: deliver two plates to the export sink within 100 ticks."
        ),
        config={
            "width": 8,
            "height": 6,
            "machines": [
                {"name": "mine", "x": 0, "y": 0, "output": {"ore": 1}, "duration": 1, "infinite": True},
                {"name": "smelter", "x": 4, "y": 0, "recipe": {"ore": 2}, "output": {"plate": 1}, "duration": 3},
                {"name": "export", "x": 7, "y": 5, "sink": True},
            ],
            "haulers": [{"name": "h1", "x": 1, "y": 0, "capacity": 4, "battery": 400}],
            "objectives": [
                {"type": "produce", "item": "plate", "quantity": 2},
                {"type": "ticks", "max": 100},
            ],
            "max_ticks": 160,
        },
        starter_code=(
            "def program(city):\n"
            "    h = city.hauler('h1')\n"
            "    # TODO: ore -> smelter -> export, twice\n"
            "    pass\n"
        ),
        reference_solution=(
            "def program(city):\n"
            "    h = city.hauler('h1')\n"
            "    for _ in range(2):\n"
            "        h.load('mine', 'ore', 2)\n"
            "        h.move_to(4, 0)\n"
            "        h.unload('smelter')\n"
            "        city.wait(3)\n"
            "        h.load('smelter', 'plate', 1)\n"
            "        h.move_to(7, 5)\n"
            "        h.unload('export')\n"
        ),
        hints=(
            "Machines only progress while time advances: call city.wait(n) or h.wait(n).",
            "h.load returns how much was actually loaded - check it before walking away.",
            "The smelter needs 2 ore and 3 ticks per plate.",
        ),
    ),
    Mission(
        id="city.throughput",
        world="automation_city",
        title_ar="رفع الإنتاجية",
        title_en="Throughput",
        order_index=2,
        difficulty=4,
        skills=("civ.scheduling", "algo.greedy", "core.functions"),
        concepts_ar="الجدولة: تجاوز تنفيذ مهمة واحدة في كل مرة لتقليل زمن الإنجاز.",
        concepts_en="Scheduling: overlap the steps instead of running one batch at a time.",
        brief_ar=(
            "المطلوب 5 ألواح في 120 نبضة كحد أقصى.\n"
            "التنفيذ المتسلسل البسيط يستهلك وقتاً طويلاً: فكّر في تحميل دفعات أكبر "
            "(سعة الناقل 6) وتقليل الرحلات الفارغة."
        ),
        brief_en=(
            "Produce 5 plates within 120 ticks.\n"
            "A naive one-batch-at-a-time loop is too slow: load bigger batches "
            "(the hauler holds 6) and cut empty trips."
        ),
        config={
            "width": 10,
            "height": 6,
            "machines": [
                {"name": "mine", "x": 0, "y": 0, "output": {"ore": 1}, "duration": 1, "infinite": True},
                {"name": "smelter", "x": 5, "y": 0, "recipe": {"ore": 2}, "output": {"plate": 1}, "duration": 3},
                {"name": "export", "x": 9, "y": 5, "sink": True},
            ],
            "haulers": [{"name": "h1", "x": 1, "y": 0, "capacity": 6, "battery": 900}],
            "objectives": [
                {"type": "produce", "item": "plate", "quantity": 5},
                {"type": "ticks", "max": 120},
            ],
            "max_ticks": 200,
        },
        starter_code=(
            "def program(city):\n"
            "    h = city.hauler('h1')\n"
            "    # Produce 5 plates in <= 120 ticks. Batching is the key.\n"
            "    pass\n"
        ),
        reference_solution=(
            "def program(city):\n"
            "    h = city.hauler('h1')\n"
            "    smelter = city.machine('smelter')\n"
            "    delivered = 0\n"
            "    while delivered < 5:\n"
            "        h.move_to(0, 0)\n"
            "        h.load('mine', 'ore', 6)\n"
            "        h.move_to(5, 0)\n"
            "        h.unload('smelter')\n"
            "        city.wait(9)\n"
            "        h.load('smelter', 'plate', 6)\n"
            "        h.move_to(9, 5)\n"
            "        h.unload('export')\n"
            "        delivered = city.storage().get('plate', 0)\n"
        ),
        hints=(
            "Load 6 ore at once: three plates' worth per trip to the smelter.",
            "While you haul plates to export, the smelter keeps working - overlap the work.",
            "Loop until city.storage()['plate'] >= 5 instead of guessing the number of rounds.",
        ),
    ),
    Mission(
        id="city.assembly",
        world="automation_city",
        title_ar="سلسلة التجميع",
        title_en="Assembly Chain",
        order_index=3,
        difficulty=5,
        skills=("ds.dicts", "core.oop_composition", "civ.scheduling"),
        concepts_ar="سلاسل الإنتاج والقواميس: لوحان + برغي = وحدة جاهزة.",
        concepts_en="Production chains and dicts: two plates plus one bolt make a widget.",
        brief_ar=(
            "مرحلتان: الفرن يحوّل 2 خام إلى لوح، والمجمّع `assembler` يحوّل لوحين وبرغياً واحداً إلى وحدة `widget`.\n"
            "المطلوب: وحدتان جاهزتان في منفذ التصدير خلال 180 نبضة."
        ),
        brief_en=(
            "Two stages: the smelter turns 2 ore into a plate, and the `assembler` turns "
            "two plates plus one bolt into a `widget`.\n"
            "Goal: two finished widgets at the export sink within 180 ticks."
        ),
        config={
            "width": 12,
            "height": 8,
            "machines": [
                {"name": "mine", "x": 0, "y": 0, "output": {"ore": 1}, "duration": 1, "infinite": True},
                {"name": "bolts", "x": 0, "y": 7, "output": {"bolt": 1}, "duration": 1, "infinite": True},
                {"name": "smelter", "x": 5, "y": 0, "recipe": {"ore": 2}, "output": {"plate": 1}, "duration": 3},
                {"name": "assembler", "x": 8, "y": 3, "recipe": {"plate": 2, "bolt": 1}, "output": {"widget": 1}, "duration": 4},
                {"name": "export", "x": 11, "y": 7, "sink": True},
            ],
            "haulers": [
                {"name": "h1", "x": 1, "y": 0, "capacity": 6, "battery": 1200},
                {"name": "h2", "x": 1, "y": 7, "capacity": 6, "battery": 1200},
            ],
            "objectives": [
                {"type": "produce", "item": "widget", "quantity": 2},
                {"type": "ticks", "max": 180},
            ],
            "max_ticks": 260,
        },
        starter_code=(
            "def program(city):\n"
            "    # Two haulers: feed the smelter and the assembler, then export.\n"
            "    pass\n"
        ),
        reference_solution=(
            "def program(city):\n"
            "    h1 = city.hauler('h1')\n"
            "    h2 = city.hauler('h2')\n\n"
            "    def wait_for(machine, item, qty, limit=25):\n"
            "        for _ in range(limit):\n"
            "            if machine.output().get(item, 0) >= qty:\n"
            "                return True\n"
            "            city.wait(1)\n"
            "        return False\n\n"
            "    # Stage A: 8 ore -> 4 plates (the smelter only runs while time advances)\n"
            "    for _ in range(2):\n"
            "        h1.move_to(0, 0)\n"
            "        h1.load('mine', 'ore', 4)\n"
            "        h1.move_to(5, 0)\n"
            "        h1.unload('smelter')\n"
            "    wait_for(city.machine('smelter'), 'plate', 4)\n"
            "    # Stage B: plates -> assembler\n"
            "    h1.load('smelter', 'plate', 4)\n"
            "    h1.move_to(8, 3)\n"
            "    h1.unload('assembler')\n"
            "    # Stage C: bolts -> assembler (h2 works on the same timeline)\n"
            "    h2.move_to(0, 7)\n"
            "    h2.load('bolts', 'bolt', 2)\n"
            "    h2.move_to(8, 3)\n"
            "    h2.unload('assembler')\n"
            "    # Stage D: wait for both widgets, then export them\n"
            "    wait_for(city.machine('assembler'), 'widget', 2)\n"
            "    h1.load('assembler', 'widget', 2)\n"
            "    h1.move_to(11, 7)\n"
            "    h1.unload('export')\n"
        ),
        hints=(
            "Split the work: one hauler handles ore/plates, the other bolts.",
            "The assembler waits until it has 2 plates AND 1 bolt in its input buffer.",
            "city.machine('assembler').input() shows what has arrived so far.",
        ),
    ),
    # -------------------------------------------------- Neural Civilization
    Mission(
        id="civ.harvest",
        world="neural_civilization",
        title_ar="الحصاد الأول",
        title_en="First Harvest",
        order_index=1,
        difficulty=3,
        skills=("civ.agents", "core.loops", "civ.simulation"),
        concepts_ar="الكيانات المستقلة: سياسة بسيطة تجعل الوكلاء يجمعون الغذاء.",
        concepts_en="Autonomous agents: a simple policy that makes agents gather food.",
        brief_ar=(
            "عاملان وعقدتا غذاء. اجمع 25 وحدة غذاء خلال 60 نبضة مع بقاء العاملين على قيد الحياة.\n"
            "كل نبضة تستهلك طاقة، وكل خطوة تستهلك نصف وحدة، والغذاء يعيد 25 وحدة طاقة."
        ),
        brief_en=(
            "Two agents and two food nodes. Gather 25 food within 60 ticks while keeping both alive.\n"
            "Each tick costs energy, each step costs half a unit, and one food restores 25 energy."
        ),
        config={
            "width": 10,
            "height": 8,
            "agents": [
                {"name": "a1", "x": 0, "y": 0, "energy": 60},
                {"name": "a2", "x": 9, "y": 7, "energy": 60},
            ],
            "nodes": [
                {"x": 3, "y": 2, "item": "food", "amount": 40, "regen": 1},
                {"x": 7, "y": 6, "item": "food", "amount": 40, "regen": 1},
            ],
            "objectives": [
                {"type": "collect", "item": "food", "quantity": 25},
                {"type": "survive", "min_alive": 2},
                {"type": "ticks", "max": 60},
            ],
            "max_ticks": 60,
        },
        starter_code=(
            "def program(society):\n"
            "    def policy(s):\n"
            "        for agent in s.alive_agents():\n"
            "            pass  # TODO: eat when tired, otherwise gather\n"
            "    society.on_tick(policy)\n"
            "    society.run()\n"
        ),
        reference_solution=(
            "def program(society):\n"
            "    def policy(s):\n"
            "        for agent in s.alive_agents():\n"
            "            if agent.energy < 40 and agent.store().get('food', 0) > 0:\n"
            "                agent.eat(1)\n"
            "                continue\n"
            "            node = s.nearest_node(agent, 'food')\n"
            "            if node is None:\n"
            "                continue\n"
            "            agent.move_to(node.x, node.y)\n"
            "            agent.gather(node)\n"
            "    society.on_tick(policy)\n"
            "    society.run()\n"
        ),
        hints=(
            "Eat only when energy drops and you actually hold food: eating with an empty store does nothing.",
            "s.nearest_node(agent, 'food') is the cheapest allocation heuristic - start with it.",
            "gather() only works when the agent stands on the node: move first, then gather.",
        ),
    ),
    Mission(
        id="civ.fair_share",
        world="neural_civilization",
        title_ar="التوزيع العادل",
        title_en="Fair Share",
        order_index=2,
        difficulty=4,
        skills=("civ.resource_allocation", "civ.cooperation", "sci.statistics"),
        concepts_ar="العدالة في التوزيع: استخدم المشاركة حتى لا يموت أحد العاملين.",
        concepts_en="Fair allocation: share resources so that no agent starves.",
        brief_ar=(
            "أربعة عملاء: اثنان قريبان من الغذاء واثنان بعيدان.\n"
            "اجمع 40 غذاء، أبقِ الثلاثة على الأقل أحياء، وحافظ على معامل جيني ≤ 0.35.\n"
            "المشاركة بين الوكلاء هي المفتاح."
        ),
        brief_en=(
            "Four agents: two start close to the food, two start far away.\n"
            "Gather 40 food, keep at least three alive, and hold the Gini coefficient at or below 0.35.\n"
            "Sharing between agents is the key."
        ),
        config={
            "width": 12,
            "height": 10,
            "agents": [
                {"name": "a1", "x": 1, "y": 1, "energy": 70},
                {"name": "a2", "x": 2, "y": 1, "energy": 70},
                {"name": "a3", "x": 10, "y": 8, "energy": 45},
                {"name": "a4", "x": 11, "y": 8, "energy": 45},
            ],
            "nodes": [
                {"x": 3, "y": 3, "item": "food", "amount": 60, "regen": 2},
                {"x": 8, "y": 6, "item": "food", "amount": 60, "regen": 2},
            ],
            "objectives": [
                {"type": "collect", "item": "food", "quantity": 40},
                {"type": "survive", "min_alive": 3},
                {"type": "fairness", "max_gini": 0.35},
            ],
            "max_ticks": 90,
        },
        starter_code=(
            "def program(society):\n"
            "    # Keep everyone alive AND keep the Gini coefficient low.\n"
            "    def policy(s):\n"
            "        pass\n"
            "    society.on_tick(policy)\n"
            "    society.run()\n"
        ),
        reference_solution=(
            "def program(society):\n"
            "    def policy(s):\n"
            "        agents = s.alive_agents()\n"
            "        # 1) emergency feeding from whoever has a surplus\n"
            "        for needy in agents:\n"
            "            if needy.energy < 35 and needy.store().get('food', 0) == 0:\n"
            "                for donor in agents:\n"
            "                    if donor.name != needy.name and donor.store().get('food', 0) > 1:\n"
            "                        donor.share(needy, 'food', 1)\n"
            "                        break\n"
            "        # 2) eat when low, otherwise gather from the nearest node\n"
            "        for agent in agents:\n"
            "            if agent.energy < 40 and agent.store().get('food', 0) > 0:\n"
            "                agent.eat(1)\n"
            "                continue\n"
            "            node = s.nearest_node(agent, 'food')\n"
            "            if node is not None:\n"
            "                agent.move_to(node.x, node.y)\n"
            "                agent.gather(node)\n"
            "    society.on_tick(policy)\n"
            "    society.run()\n"
        ),
        hints=(
            "Gini measures inequality of *gathered* totals, not of stored food.",
            "A donor should share only its surplus (keep at least 1 for itself).",
            "Send far agents to the far node so they are not permanently starved by distance.",
        ),
    ),
    Mission(
        id="civ.scheduling",
        world="neural_civilization",
        title_ar="الجدولة وتقليل البطالة",
        title_en="Scheduling and Idle Time",
        order_index=3,
        difficulty=5,
        skills=("civ.scheduling", "algo.greedy", "civ.simulation"),
        concepts_ar="الجدولة: خصّص العقد بذكاء لتقليل النبضات الضائعة.",
        concepts_en="Scheduling: assign nodes smartly to cut wasted ticks.",
        brief_ar=(
            "ثلاثة عملاء وأربع عقد غذاء متباعدة.\n"
            "اجمع 60 غذاء في 70 نبضة، وأبقِ الجميع أحياء، ولا تتجاوز 20 نبضة خمول إجمالية.\n"
            "التخصيص الجشع البسيط يهدر الوقت: خصّص لكل عامل عقدة مختلفة."
        ),
        brief_en=(
            "Three agents and four food nodes spread across the map.\n"
            "Gather 60 food in 70 ticks, keep everyone alive, and stay under 20 idle ticks in total.\n"
            "Naive greedy assignment wastes time: give each agent its own node."
        ),
        config={
            "width": 14,
            "height": 10,
            "agents": [
                {"name": "a1", "x": 0, "y": 0, "energy": 120},
                {"name": "a2", "x": 13, "y": 0, "energy": 120},
                {"name": "a3", "x": 6, "y": 9, "energy": 120},
            ],
            "nodes": [
                {"x": 2, "y": 2, "item": "food", "amount": 60, "regen": 3},
                {"x": 11, "y": 2, "item": "food", "amount": 60, "regen": 3},
                {"x": 2, "y": 7, "item": "food", "amount": 60, "regen": 3},
                {"x": 11, "y": 7, "item": "food", "amount": 60, "regen": 3},
            ],
            "objectives": [
                {"type": "collect", "item": "food", "quantity": 60},
                {"type": "survive", "min_alive": 3},
                {"type": "idle", "max": 20},
            ],
            "max_ticks": 70,
        },
        starter_code=(
            "def program(society):\n"
            "    # Assign each agent a fixed node instead of everyone chasing the same one.\n"
            "    def policy(s):\n"
            "        pass\n"
            "    society.on_tick(policy)\n"
            "    society.run()\n"
        ),
        reference_solution=(
            "def program(society):\n"
            "    assignments = {}\n"
            "    def policy(s):\n"
            "        agents = s.alive_agents()\n"
            "        free = [n for n in s.nodes('food')]\n"
            "        # stable assignment: remember each agent's node while it still has food\n"
            "        for agent in agents:\n"
            "            node = assignments.get(agent.name)\n"
            "            if node is None or node.amount <= 0:\n"
            "                candidates = [n for n in free if n not in assignments.values()]\n"
            "                node = candidates[0] if candidates else (free[0] if free else None)\n"
            "                assignments[agent.name] = node\n"
            "            if node is None:\n"
            "                continue\n"
            "            if agent.energy < 40 and agent.store().get('food', 0) > 0:\n"
            "                agent.eat(1)\n"
            "                continue\n"
            "            agent.move_to(node.x, node.y)\n"
            "            agent.gather(node)\n"
            "    society.on_tick(policy)\n"
            "    society.run()\n"
        ),
        hints=(
            "Idle ticks are counted per agent per tick: an agent must act every tick.",
            "A dict of {agent_name: node} gives a stable assignment across ticks.",
            "Each agent gathering from its own node avoids the queue at one node.",
        ),
    ),
    Mission(
        id="civ.scarcity",
        world="neural_civilization",
        title_ar="الندرة والاختيار",
        title_en="Scarcity and Choice",
        order_index=4,
        difficulty=6,
        skills=("civ.resource_allocation", "algo.greedy", "sci.probability"),
        concepts_ar="الندرة: عقد محدودة، اختر من يأكل ومن يجمع.",
        concepts_en="Scarcity: limited nodes, choose who eats and who gathers.",
        brief_ar=(
            "عقدتان صغيرتان فقط وثلاثة عملاء بطاقة منخفضة.\n"
            "اجمع 30 غذاء، وأبقِ عاملين على الأقل أحياء حتى النبضة 60، واستهلك أقل من 12 غذاءً.\n"
            "الاستهلاك الزائد يعني الفشل: وازن بين الجمع والأكل."
        ),
        brief_en=(
            "Only two small nodes and three agents with low energy.\n"
            "Gather 30 food, keep at least two agents alive until tick 60, and eat fewer than 12 food.\n"
            "Over-eating fails the mission: balance gathering against consumption."
        ),
        config={
            "width": 10,
            "height": 8,
            "agents": [
                {"name": "a1", "x": 1, "y": 1, "energy": 45},
                {"name": "a2", "x": 8, "y": 6, "energy": 45},
                {"name": "a3", "x": 5, "y": 4, "energy": 30},
            ],
            "nodes": [
                {"x": 2, "y": 3, "item": "food", "amount": 25, "regen": 1},
                {"x": 7, "y": 5, "item": "food", "amount": 25, "regen": 1},
            ],
            "objectives": [
                {"type": "collect", "item": "food", "quantity": 30},
                {"type": "survive", "min_alive": 2},
                {"type": "consumption", "max_eaten": 12},
                {"type": "ticks", "max": 60},
            ],
            "max_ticks": 60,
        },
        starter_code=(
            "def program(society):\n"
            "    # Eat only just in time - every meal is a point against you.\n"
            "    pass\n"
        ),
        reference_solution=(
            "def program(society):\n"
            "    assignments = {}\n"
            "    def policy(s):\n"
            "        agents = s.alive_agents()\n"
            "        nodes = s.nodes('food')\n"
            "        for index, agent in enumerate(agents):\n"
            "            node = assignments.get(agent.name)\n"
            "            if node is None or node.amount <= 0:\n"
            "                node = nodes[index % len(nodes)] if nodes else None\n"
            "                assignments[agent.name] = node\n"
            "            if node is None:\n"
            "                continue\n"
            "            if agent.energy < 18 and agent.store().get('food', 0) > 0:\n"
            "                agent.eat(1)\n"
            "                continue\n"
            "            agent.move_to(node.x, node.y)\n"
            "            agent.gather(node)\n"
            "    society.on_tick(policy)\n"
            "    society.run()\n"
        ),
        hints=(
            "Eat at the last moment: energy below ~18 is safe, eating at 40 wastes food.",
            "Round-robin assignment (index % len(nodes)) spreads agents over the two nodes.",
            "The 'consumption' objective counts every eat() call, not the energy restored.",
        ),
    ),
]


def by_id(mission_id: str) -> Mission:
    for mission in MISSIONS:
        if mission.id == mission_id:
            return mission
    raise KeyError(f"unknown mission: {mission_id}")
