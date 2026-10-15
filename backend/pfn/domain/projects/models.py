"""Project templates: starter scaffolds for the multi-file workbench."""

from __future__ import annotations

from dataclasses import dataclass, field

TEMPLATES: dict[str, dict[str, str]] = {
    "blank": {
        "main.py": '"""Your programme starts here."""\n\n\ndef main():\n    print("hello from Python Forge Nexus")\n\n\nif __name__ == "__main__":\n    main()\n',
        "tests/test_main.py": "from main import main\n\n\ndef test_main_runs(capsys):\n    main()\n    assert \"hello\" in capsys.readouterr().out\n",
    },
    "pipeline": {
        "pipeline/__init__.py": "",
        "pipeline/extract.py": '"""Read raw records."""\nfrom __future__ import annotations\n\nimport pandas as pd\n\n\ndef extract(rows):\n    return pd.DataFrame(list(rows))\n',
        "pipeline/transform.py": '"""Clean and enrich."""\nfrom __future__ import annotations\n\n\ndef transform(frame):\n    result = frame.copy()\n    return result\n',
        "pipeline/load.py": '"""Write results and report."""\nfrom __future__ import annotations\n\n\ndef load(frame):\n    return {"rows": int(len(frame))}\n',
        "tests/test_pipeline.py": "from pipeline.extract import extract\nfrom pipeline.transform import transform\nfrom pipeline.load import load\n\n\ndef test_round_trip():\n    frame = transform(extract([{\"a\": 1}]))\n    assert load(frame)[\"rows\"] == 1\n",
    },
    "agent": {
        "agent.py": '"""A tool-calling agent loop."""\nfrom __future__ import annotations\n\nimport json\n\nTOOLS = {"echo": lambda text: text}\n\n\ndef run_agent(model, goal, max_steps=8):\n    steps = []\n    for _ in range(max_steps):\n        action = json.loads(model(steps))\n        if action[\"action\"] == \"final\":\n            return {\"answer\": action[\"answer\"], \"steps\": steps}\n        try:\n            result = TOOLS[action[\"action\"]](**(action.get(\"args\") or {}))\n        except Exception as error:  # noqa: BLE001 - tool failures are observations\n            steps.append({\"action\": action, \"error\": str(error)})\n            continue\n        steps.append({\"action\": action, \"observation\": result})\n    return {\"answer\": None, \"steps\": steps}\n',
        "tools.py": '"""Tools exposed to the agent."""\nfrom __future__ import annotations\n\n\ndef add(a, b):\n    return a + b\n\n\ndef lookup(key, table):\n    return table.get(key)\n',
        "tests/test_agent.py": "import json\n\nfrom agent import run_agent\n\n\ndef test_final_action_stops_the_loop():\n    report = run_agent(lambda steps: json.dumps({\"action\": \"final\", \"answer\": \"ok\"}), \"anything\")\n    assert report[\"answer\"] == \"ok\"\n",
    },
    "api": {
        "main.py": '"""A small FastAPI service."""\nfrom __future__ import annotations\n\nfrom fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel, Field\n\napp = FastAPI(title="Playground API")\n\nITEMS: dict[int, dict] = {}\nCOUNTER = 0\n\n\nclass ItemIn(BaseModel):\n    name: str = Field(min_length=1, max_length=80)\n\n\nclass ItemOut(ItemIn):\n    id: int\n\n\n@app.get("/health")\ndef health():\n    return {"status": "ok"}\n\n\n@app.post("/items", response_model=ItemOut, status_code=201)\ndef create_item(payload: ItemIn):\n    global COUNTER\n    COUNTER += 1\n    ITEMS[COUNTER] = {\"id\": COUNTER, \"name\": payload.name}\n    return ITEMS[COUNTER]\n\n\n@app.get("/items/{item_id}", response_model=ItemOut)\ndef read_item(item_id: int):\n    item = ITEMS.get(item_id)\n    if item is None:\n        raise HTTPException(status_code=404, detail=\"item not found\")\n    return item\n',
        "tests/test_api.py": "from fastapi.testclient import TestClient\n\nfrom main import app\n\nclient = TestClient(app)\n\n\ndef test_health():\n    assert client.get(\"/health\").json() == {\"status\": \"ok\"}\n",
    },
    "analysis": {
        "analysis.py": '"""A reproducible data analysis."""\nfrom __future__ import annotations\n\nimport numpy as np\nimport pandas as pd\n\n\ndef describe(frame):\n    numeric = frame.select_dtypes(include=\"number\")\n    return {\"rows\": int(len(frame)), \"means\": numeric.mean().to_dict()}\n\n\ndef load(rows):\n    return pd.DataFrame(rows)\n',
        "tests/test_analysis.py": "from analysis import describe, load\n\n\ndef test_describe():\n    frame = load([{\"a\": 1}, {\"a\": 3}])\n    assert describe(frame)[\"means\"][\"a\"] == 2\n",
    },
}

TEMPLATE_NOTES = {
    "blank": {"en": "A single module plus one test.", "ar": "وحدة واحدة واختبار واحد."},
    "pipeline": {"en": "A three-stage ETL package with tests.", "ar": "حزمة ETL من ثلاث مراحل مع اختبارات."},
    "agent": {"en": "A tool-calling agent loop with a tool module.", "ar": "حلقة وكيل تستدعي الأدوات مع وحدة أدوات."},
    "api": {"en": "A FastAPI service tested with TestClient.", "ar": "خدمة FastAPI مُختبرة بـ TestClient."},
    "analysis": {"en": "A reproducible pandas/numpy analysis.", "ar": "تحليل قابل للتكرار بـ pandas و numpy."},
}


@dataclass(slots=True)
class ProjectRecord:
    id: str
    learner_id: str
    slug: str
    title: str
    template: str
    description: str
    current_version: int
    created_at: str
    updated_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "slug": self.slug,
            "title": self.title,
            "template": self.template,
            "description": self.description,
            "current_version": self.current_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
