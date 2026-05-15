"""
FinWise AI — FastAPI Backend
Run with: uvicorn main:app --reload
Or:       python main.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from agent import (
    load_data, save_data,
    add_expense, delete_expense,
    set_income, add_goal, delete_goal,
    chat, get_summary,
)

app = FastAPI(title="FinWise AI", version="1.0.0")

# Serve static frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Serve frontend ─────────────────────────────────────────────────────────────
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


# ── Dashboard data ─────────────────────────────────────────────────────────────
@app.get("/api/dashboard")
def get_dashboard():
    data      = load_data()
    expenses  = data["expenses"]
    income    = data["income"]
    goals     = data["goals"]

    total      = sum(e["amount"] for e in expenses)
    savings    = income - total if income else 0
    save_rate  = (savings / income * 100) if income else 0
    health     = min(100, max(0, int(
        40
        + save_rate * 0.6
        + (5 if goals else 0)
        + (5 if len(expenses) >= 5 else 0)
    )))
    daily_avg  = total / 30

    by_cat: dict = {}
    for e in expenses:
        by_cat[e["category"]] = round(by_cat.get(e["category"], 0) + e["amount"], 2)

    # monthly trend (last 6 months)
    from collections import defaultdict
    monthly: dict = defaultdict(float)
    for e in expenses:
        month = e["date"][:7] if e.get("date") else "unknown"
        monthly[month] += e["amount"]
    monthly_trend = [
        {"month": k, "amount": round(v, 2)}
        for k, v in sorted(monthly.items())[-6:]
    ]

    return {
        "income":         income,
        "total_expenses": round(total, 2),
        "net_savings":    round(savings, 2),
        "save_rate":      round(save_rate, 1),
        "daily_avg":      round(daily_avg, 2),
        "health_score":   health,
        "by_category":    by_cat,
        "monthly_trend":  monthly_trend,
        "expenses":       sorted(expenses, key=lambda x: x["date"], reverse=True),
        "goals":          goals,
        "budget_50_30_20": {
            "needs":   round(income * 0.5, 2),
            "wants":   round(income * 0.3, 2),
            "savings": round(income * 0.2, 2),
        } if income else None,
    }


# ── Expenses ───────────────────────────────────────────────────────────────────
class ExpenseIn(BaseModel):
    description: str
    amount: float
    category: str
    date: Optional[str] = None


@app.post("/api/expenses")
def create_expense(body: ExpenseIn):
    if not body.description or body.amount <= 0:
        raise HTTPException(400, "Invalid description or amount")
    entry = add_expense(body.description, body.amount, body.category, body.date)
    return {"success": True, "expense": entry}


@app.delete("/api/expenses/{expense_id}")
def remove_expense(expense_id: int):
    delete_expense(expense_id)
    return {"success": True}


# ── Income ─────────────────────────────────────────────────────────────────────
class IncomeIn(BaseModel):
    amount: float


@app.post("/api/income")
def update_income(body: IncomeIn):
    if body.amount < 0:
        raise HTTPException(400, "Income cannot be negative")
    set_income(body.amount)
    return {"success": True, "income": body.amount}


# ── Goals ──────────────────────────────────────────────────────────────────────
class GoalIn(BaseModel):
    name: str
    target: float
    saved: Optional[float] = 0


@app.post("/api/goals")
def create_goal(body: GoalIn):
    entry = add_goal(body.name, body.target, body.saved)
    return {"success": True, "goal": entry}


@app.delete("/api/goals/{goal_id}")
def remove_goal(goal_id: int):
    delete_goal(goal_id)
    return {"success": True}


# ── AI Chat ────────────────────────────────────────────────────────────────────
class ChatIn(BaseModel):
    message: str
    history: Optional[list] = []


@app.post("/api/chat")
def ai_chat(body: ChatIn):
    if not body.message.strip():
        raise HTTPException(400, "Message cannot be empty")
    try:
        reply = chat(body.message, body.history or [])
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(500, f"AI error: {str(e)}")


# ── Summary (debug/dev) ────────────────────────────────────────────────────────
@app.get("/api/summary")
def api_summary():
    return {"summary": get_summary()}


# ── Run directly ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)