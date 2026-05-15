import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_FILE = "data.json"


# ── Data helpers ────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"expenses": [], "income": 0, "goals": [], "chat_history": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Finance tools ────────────────────────────────────────────────────
def add_expense(description: str, amount: float, category: str, date: str = None):
    data = load_data()
    entry = {
        "id": int(datetime.now().timestamp() * 1000),
        "description": description,
        "amount": round(float(amount), 2),
        "category": category,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
    }
    data["expenses"].append(entry)
    save_data(data)
    return entry


def delete_expense(expense_id: int):
    data = load_data()
    data["expenses"] = [e for e in data["expenses"] if e["id"] != expense_id]
    save_data(data)


def set_income(amount: float):
    data = load_data()
    data["income"] = round(float(amount), 2)
    save_data(data)


def add_goal(name: str, target: float, saved: float = 0):
    data = load_data()
    data["goals"].append({
        "id": int(datetime.now().timestamp() * 1000),
        "name": name,
        "target": round(float(target), 2),
        "saved": round(float(saved), 2),
    })
    save_data(data)


def delete_goal(goal_id: int):
    data = load_data()
    data["goals"] = [g for g in data["goals"] if g["id"] != goal_id]
    save_data(data)


def get_summary() -> str:
    data = load_data()
    expenses = data["expenses"]
    income = data["income"]
    goals = data["goals"]

    if not expenses and not income:
        return "No financial data recorded yet."

    total = sum(e["amount"] for e in expenses)
    by_cat: dict = {}
    for e in expenses:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]

    savings = income - total if income else 0
    save_rate = (savings / income * 100) if income else 0
    health = min(100, max(0, int(40 + save_rate * 0.6 + (5 if goals else 0) + (5 if len(expenses) >= 5 else 0))))

    cat_lines = "\n".join(
        f"  {cat}: ₹{amt:.0f} ({amt / total * 100:.1f}%)"
        for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1])
    ) if total else "  None"

    goal_lines = "\n".join(
        f"  {g['name']}: ₹{g['saved']:.0f}/₹{g['target']:.0f}"
        for g in goals
    ) if goals else "  None"

    return (
        f"Income: ₹{income:.0f}\n"
        f"Total expenses: ₹{total:.0f}\n"
        f"Net savings: ₹{savings:.0f} ({save_rate:.1f}% of income)\n"
        f"Daily avg spend: ₹{total / 30:.0f}\n"
        f"Financial health score: {health}/100\n\n"
        f"Expense breakdown:\n{cat_lines}\n\n"
        f"Savings goals:\n{goal_lines}"
    )


# ── GPT-4o chat ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are FinWise, a smart personal finance AI advisor for Indian users.
Currency: ₹ (Indian Rupees). You have full access to the user's financial data below.

Your capabilities:
- Analyze spending patterns and give category-level advice
- Apply the 50-30-20 rule (50% Needs, 30% Wants, 20% Savings)
- Give a Financial Health Score out of 100
- Suggest where to cut spending and where to invest savings
- Answer questions about budgeting, SIPs, FDs, PPF, NPS, emergency funds

Rules:
- Always use ₹ for currency
- Be warm, friendly, and specific — not generic
- When user mentions an expense, confirm and give a quick insight
- Keep responses concise (under 200 words)
- Use bullet points for lists
- Always end advice with one actionable next step"""


def chat(user_message: str, history: list) -> str:
    summary = get_summary()
    messages = [{"role": "system", "content": SYSTEM_PROMPT + f"\n\nCurrent financial snapshot:\n{summary}"}]

    for turn in history[-10:]:  # keep last 10 turns for context
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["ai"]})

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=600,
        temperature=0.7,
    )
    return response.choices[0].message.content
