from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
import os
import json
import re
import openai

app = FastAPI(title="DevOffice AI Simulator")

# -----------------------------
# OPENAI SETUP
# -----------------------------
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise Exception("OPENAI_API_KEY is missing on server!")

client = openai.OpenAI(api_key=api_key)

# -----------------------------
# GAME STATE
# -----------------------------

class Programmer:
    def __init__(self, name, skill, personality):
        self.name = name
        self.skill = skill
        self.personality = personality
        self.stress = random.randint(0, 30)
        self.energy = 100
        self.bugs = 0
        self.last_action = ""

team = [
    Programmer("Alex", 7, "calm but perfectionist"),
    Programmer("Mihai", 5, "fast but messy"),
    Programmer("Vlad", 9, "arrogant genius")
]

world = {
    "day": 0,
    "project_progress": 0,
    "bugs": 0,
    "log": []
}

# -----------------------------
# AI PROMPT
# -----------------------------

def build_prompt(dev: Programmer):
    return f"""
You are a programmer in a 2006-style office simulation game.

Name: {dev.name}
Skill: {dev.skill}/10
Personality: {dev.personality}
Stress: {dev.stress}/100
Energy: {dev.energy}/100

Choose ONE action:
- code
- debug
- talk
- rest

Return ONLY valid JSON:
{{
  "action": "code|debug|talk|rest",
  "message": "short message",
  "quality": 1-10,
  "bug_risk": 1-10
}}
"""

# -----------------------------
# AI CALL (SAFE)
# -----------------------------

def call_ai(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON. No markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        text = res.choices[0].message.content.strip()

        # SAFE JSON extraction
        import json
        import re

        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No JSON found")

        return json.loads(match.group())

    except Exception as e:
        print("AI ERROR:", e)
        return {
            "action": "rest",
            "message": "fallback mode",
            "quality": 1,
            "bug_risk": 1
        }

# -----------------------------
# GAME LOGIC
# -----------------------------

def apply_action(dev: Programmer, decision):
    action = decision.get("action", "rest")
    quality = decision.get("quality", 1)
    bug_risk = decision.get("bug_risk", 1)

    dev.last_action = action

    if action == "code":
        world["project_progress"] += quality * 0.5

        if bug_risk > 6:
            world["bugs"] += 1
            dev.bugs += 1
            dev.stress += 10

    elif action == "debug":
        world["bugs"] = max(0, world["bugs"] - quality * 0.3)
        dev.stress -= 5

    elif action == "talk":
        dev.stress += random.randint(-5, 5)

    elif action == "rest":
        dev.energy = min(100, dev.energy + 20)
        dev.stress -= 10

    dev.stress = max(0, min(100, dev.stress))
    dev.energy = max(0, min(100, dev.energy))

# -----------------------------
# GAME LOOP
# -----------------------------

def game_tick():
    world["day"] += 1
    logs = []

    for dev in team:
        decision = call_ai(build_prompt(dev))
        apply_action(dev, decision)

        logs.append({
            "name": dev.name,
            "action": decision["action"],
            "message": decision["message"],
            "stress": dev.stress
        })

    world["log"] = logs

# -----------------------------
# API
# -----------------------------

@app.get("/tick")
def tick():
    try:
        game_tick()
        return {
            "day": world["day"],
            "progress": round(world["project_progress"], 2),
            "bugs": world["bugs"],
            "log": world["log"]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/state")
def state():
    return {
        "world": world,
        "team": [
            {
                "name": d.name,
                "skill": d.skill,
                "stress": d.stress,
                "energy": d.energy,
                "bugs": d.bugs,
                "last_action": d.last_action
            }
            for d in team
        ]
    }

# -----------------------------
# UI (GAME FRONTEND)
# -----------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>DevOffice AI</title>
    <style>
        body { font-family: Arial; background:#111; color:#0f0; }
        .container { padding:20px; }
        .npc { border:1px solid #0f0; padding:10px; margin:10px; }
        button { padding:10px; background:#0f0; border:none; cursor:pointer; }
        pre { background:#000; padding:10px; }
    </style>
</head>
<body>
<img src="https://www.mamp.one/wp-content/uploads/2024/09/image-resources2.jpg" width="300" />
<div class="container">

<h1>💻 DevOffice AI Simulator</h1>

<button onclick="tick()">▶ Next Tick</button>

<h2>📊 World</h2>
<pre id="world"></pre>

<h2>👨‍💻 NPCs</h2>
<div id="npcs"></div>

</div>

<script>
async function tick() {
    const res = await fetch('/tick');
    const data = await res.json();

    document.getElementById('world').innerText =
        JSON.stringify(data, null, 2);

    let html = "";
    data.log.forEach(npc => {
        html += `
        <div class="npc">
            <b>${npc.name}</b><br>
            Action: ${npc.action}<br>
            Message: ${npc.message}<br>
            Stress: ${npc.stress}
        </div>`;
    });

    document.getElementById('npcs').innerHTML = html;
}
</script>

</body>
</html>
"""