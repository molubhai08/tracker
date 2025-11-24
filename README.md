

# **📌 Universal Tracker AI — Flask + CrewAI + Groq + MySQL**

This project is an **AI-powered universal tracking system** where users can track anything (habits, activities, daily logs, expenses, productivity, workouts, etc.) using natural language.

The system uses:

* **Flask** (Backend API)
* **CrewAI** intelligent agent
* **Groq LLaMA 3.3 70B** for reasoning
* **MySQL database** for dynamic table creation and data storage
* **LangChain SQL tools** for safe SQL execution
* **Automatic visualization** using matplotlib when requested

---

# 🚀 **Features**

### ✅ Track ANYTHING using plain English

Example:

* *“Start tracking my meditation with minutes and date”*
* *“I drank 2.5 liters today, save it”*
* *“Show me last week’s meditation stats”*

### ✅ Dynamic Table Creation

The agent creates tables automatically using SQL.

### ✅ Automatic Date Handling

Understands words like **today, yesterday, last week** using the `extract_date` tool.

### ✅ Visualization on Demand

If the user says "visualise", it:

* Extracts X-axis & Y-axis using LLM function calling
* Returns structured JSON to the frontend for plotting

### ✅ MySQL-supported Tracking

Uses `mysql+mysqlconnector`.

### ✅ Safe SQL Execution

Every SQL query is:
✔ Checked → `check_sql`
✔ Executed → `execute_sql`

### ✅ Clear natural-language explanations

The model explains results simply and clearly.

---

# 📦 **Project Structure**

```
├── app.py                 # Main Flask backend
├── .env                   # Environment variables
├── requirements.txt
└── README.md
```

---

# 🔧 **Installation & Setup**

## **1️⃣ Clone the repo**

```bash
git clone https://github.com/molubhai08/tracker.git
cd tracker
```

---

## **2️⃣ Install dependencies**

Create a venv (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

Install required packages:

```bash
pip install -r requirements.txt
```

---

## **3️⃣ Setup environment variables**

Create a `.env` file:

```
GROQ_API_KEY=your_groq_api_key
```

---

## **4️⃣ Setup MySQL database**

Open MySQL and create DB:

```sql
CREATE DATABASE ai_agent;
```

Update credentials inside `app.py`:

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "yourpassword"
MYSQL_DB = "ai_agent"
MYSQL_PORT = 3306
```

---

## **5️⃣ Run the Flask Server**

```bash
python app.py
```

Server starts at:

```
http://127.0.0.1:5000
```

---

# 🌐 **6️⃣ Expose API using Ngrok (optional)**

Login:

```bash
ngrok config add-authtoken <your_token>
```

Expose Flask server:

```bash
ngrok http 5000
```

Your public API URL appears like:

```
https://df42-103-11-233-101.ngrok-free.app
```

---

# 🧠 **Agent Logic Explained**

Your CrewAI agent (`tracker_agent`) can:

### ⭐ Create new trackers

Example input:
**"Start tracking water intake with date and amount"**

### ⭐ Insert data

**"Log that today I drank 2.5 liters"**

### ⭐ Retrieve & analyze data

**"Show my water intake this month"**

### ⭐ Visualize charts

**"Visualise my water intake trend"**

When the user requests visualization →
✔ The agent result is passed to summarization model
✔ Extracts `x_axis`, `y_axis`, `message`
✔ Returned as JSON for frontend plotting

---

# 🧪 **API Usage**

## **POST /response**

Send natural language:

### **📌 Example**

```json
{
  "query": "I meditated 20 minutes today"
}
```

### **📌 Example Response**

```json
{
  "output": "A new entry was added for meditation: 20 minutes on 2025-11-24."
}
```

---

### **Visualization Query**

```json
{
  "query": "Visualise my meditation minutes this week"
}
```

Output format:

```json
{
  "output": {
    "x_axis": ["2025-11-21", "2025-11-22", "2025-11-23"],
    "y_axis": [10, 20, 15],
    "message": "Retrieved meditation records."
  }
}
```

You can directly plot these values on frontend.

---

# 📎 **Included SQL Tools**

| Tool Name         | Purpose                   |
| ----------------- | ------------------------- |
| `list_tables()`   | List all trackers         |
| `tables_schema()` | Show table structure      |
| `create_table()`  | Create new tracker table  |
| `insert_info()`   | Insert new entry          |
| `execute_sql()`   | Run SQL queries           |
| `check_sql()`     | Validate SQL              |
| `extract_date()`  | Convert "today/yesterday" |

---

# 📘 **How the Visualization System Works**

1. User asks:
   **"Visualise my water intake last week."**

2. Agent runs SQL → gets data

3. A second LLM step extracts:
   ✔ x_axis
   ✔ y_axis
   ✔ message

4. Returned as JSON

5. Frontend renders a chart
   (matplotlib example included in backend)

---

# 🎯 **Future Improvements**

* User authentication
* Multi-user DB separation
* Scheduled reminders
* Mobile-friendly UI
* Auto-trend detection

---
