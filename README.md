# FinWise AI — Personal Finance Agent
Built with FastAPI + GPT-4o + Vanilla HTML/CSS/JS

## Project structure
```
finwise-agent/
├── main.py          ← FastAPI backend (all API routes)
├── agent.py         ← GPT-4o brain + financial tools
├── static/
│   └── index.html   ← Full frontend (dashboard, charts, chat)
├── data.json        ← Auto-created, stores your expenses
├── .env             ← Your secret API key (create this)
├── .env.example     ← Template for .env
└── requirements.txt ← Python dependencies
```

## Setup steps

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your OpenAI API key
Create a file called `.env` in the project folder:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### 3. Run the server
```bash
python main.py
```

### 4. Open in browser
Go to: http://localhost:8000

## API endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /api/dashboard | All financial data |
| POST | /api/expenses  | Add an expense |
| DELETE | /api/expenses/{id} | Delete an expense |
| POST | /api/income    | Set monthly income |
| POST | /api/goals     | Add savings goal |
| DELETE | /api/goals/{id} | Delete a goal |
| POST | /api/chat      | Chat with GPT-4o |

## Features
- Expense tracking with categories
- 50-30-20 budget rule calculator
- Pie chart + bar chart (Chart.js)
- Financial health score (0-100)
- GPT-4o powered AI advisor
- Savings goals tracker
- Full reports with annual projections
- Next month prediction (linear regression)
- Persistent data storage (JSON file)
