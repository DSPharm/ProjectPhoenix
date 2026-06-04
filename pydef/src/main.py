from fastapi import FastAPI
from pydantic import BaseModel
import random
import openai
import os

app = FastAPI(title="DevOffice AI Simulator")

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    "money": 10000,
    "log": []
}

# -----------------------------
# AI PROMPT
# -----------------------------

def build_prompt(dev: Programmer):
    return f"""
You are an AI programmer in a 2006-style software company simulator.

Name: {dev.name}
Skill: {dev.skill}/10
Personality: {dev.personality}
Stress: {dev.stress}/100
Energy: {dev.energy}/100

Game context:
- Project progress: {world['project_progress']}%
- Total bugs: {world['bugs']}

Choose ONE action:
1. code
2. debug
3. talk
4. rest

Return ONLY JSON:
{{
  "action": "...",
  "message": "...",
  "quality": 1-10,
  "bug_risk": 1-10
}}
"""

# -----------------------------
# CALL AI
# -----------------------------

def call_ai(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        text = res.choices[0].message.content
        return eval(text)  # MVP only (in prod use json.loads)
    except Exception as e:
        return {
            "action": "rest",
            "message": "AI error fallback",
            "quality": 1,
            "bug_risk": 1
        }

# -----------------------------
# GAME LOGIC
# -----------------------------

def apply_action(dev: Programmer, decision):
    action = decision["action"]
    quality = decision["quality"]
    bug_risk = decision["bug_risk"]

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
        prompt = build_prompt(dev)
        decision = call_ai(prompt)
        apply_action(dev, decision)

        logs.append({
            "name": dev.name,
            "action": decision["action"],
            "message": decision["message"],
            "stress": dev.stress,
            "bugs": world["bugs"]
        })

    world["log"] = logs

# -----------------------------
# API
# -----------------------------

class TickResponse(BaseModel):
    day: int
    progress: float
    bugs: int
    log: list

@app.post("/tick", response_model=TickResponse)
def tick():
    game_tick()
    return {
        "day": world["day"],
        "progress": round(world["project_progress"], 2),
        "bugs": world["bugs"],
        "log": world["log"]
    }

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
