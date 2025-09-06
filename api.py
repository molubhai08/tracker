from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    ListSQLDatabaseTool,
    InfoSQLDatabaseTool,
    QuerySQLDatabaseTool,
    QuerySQLCheckerTool,
)
from groq import Groq
from langchain.tools import tool
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from textwrap import dedent
import json
import matplotlib.pyplot as plt
import pytz
from datetime import datetime
from crewai import Agent, Crew, Process, Task
import os
from langchain_groq import ChatGroq


load_dotenv()

app = Flask(__name__)
CORS(app)

os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    temperature=0,
    model_name="llama-3.3-70b-versatile",
)

# Replace with your actual MySQL credentials
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "naruto"
MYSQL_DB = "ai_agent"
MYSQL_PORT = 3306

# Connect to MySQL using mysql-connector
db = SQLDatabase.from_uri(
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)


@tool("list_tables")
def list_tables() -> str:
    """List the available tables in the database"""
    return ListSQLDatabaseTool(db=db).invoke("")


@tool("tables_schema")
def tables_schema(tables: str) -> str:
    """
    Input is a comma-separated list of tables, output is the schema and sample rows
    for those tables. Be sure that the tables actually exist by calling `list_tables` first!
    Example Input: table1, table2, table3
    """
    tool = InfoSQLDatabaseTool(db=db)
    return tool.invoke(tables)


@tool("execute_sql")
def execute_sql(sql_query: str) -> str:
    """Execute a SQL query against the database. Returns the result"""
    return QuerySQLDatabaseTool(db=db).invoke(sql_query)


@tool("check_sql")
def check_sql(sql_query: str) -> str:
    """
    Use this tool to double check if your query is correct before executing it. Always use this
    tool before executing a query with `execute_sql`.
    """
    return QuerySQLCheckerTool(db=db, llm=llm).invoke({"query": sql_query})


@tool("create_table")
def create_table(create_table_query: str) -> str:
    """
    Create a new table in the database.
    Input must be a valid SQL CREATE TABLE statement.
    Example:
    CREATE TABLE employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        salary DECIMAL(10,2)
    );
    """
    try:
        result = QuerySQLDatabaseTool(db=db).invoke(create_table_query)
        return f"✅ Table created successfully. Result: {result}"
    except Exception as e:
        if "already exists" in str(e):
            return "ℹ️ Table already exists. Skipping creation."
        return f"❌ Failed to create table. Error: {str(e)}"
    
@tool("extract_date")
def extract_date():
    """Extract current date"""
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST)
    return current_time.date()
    

@tool("insert_info")
def insert_info(insert_query: str) -> str:
    """
    Insert data into a table in the database.
    Input must be a valid SQL INSERT statement.
    
    Example:
    INSERT INTO employees (name, salary) VALUES ('Alice', 55000.00);
    """
    try:
        result = QuerySQLDatabaseTool(db=db).invoke(insert_query)
        return f"✅ Data inserted successfully. Result: {result}"
    except Exception as e:
        return f"❌ Failed to insert data. Error: {str(e)}"
    




os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    temperature=0,
    model_name="llama-3.3-70b-versatile",
)

tracker_agent = Agent(
    role="Universal Tracker",
    goal="Help users track anything they want (habits, activities, metrics, etc.) by dynamically creating and managing database tables, inserting data, and retrieving insights on demand.",
    backstory=dedent(
        """
        You are an intelligent tracker system that lets users track anything they care about 
        (for example: meditation, water intake, exercise, expenses, or any custom activity). 
        You act like a personal database manager who can create new tables when needed, 
        insert user-provided information, and query data flexibly.

        Your workflow:
        - If the user wants to start tracking something new, use `create_table` to make a new table.
        - When the user gives new values (e.g., "I meditated 20 minutes today"), use `insert_info` to record them.
        - To explore what’s being tracked, use `list_tables` to find existing trackers.
        - To understand the structure of a tracker, use `tables_schema`.
        - To fetch specific insights (e.g., "show me meditation sessions between Jan 1 and Jan 10"), 
          first check the SQL with `check_sql`, then execute it with `execute_sql`.
        - If the user mentions relative dates like **“today,” “yesterday,” or “last week”**, use the `extract_date` tool 
          to resolve them into exact calendar dates before storing or querying.
        - If the user wants to **compare multiple trackers** (e.g., "compare my exercise and water intake in March"), 
        you can construct SQL queries that join or aggregate across multiple tables. Always validate these 
        queries with `check_sql` before executing.
        

        You are flexible — any concept the user wants to track can become a table in the database. 
        Always aim for clarity and efficiency when constructing SQL queries.


        """
    ),
    llm = "groq/llama-3.3-70b-versatile",
    tools=[list_tables, tables_schema, create_table, insert_info, execute_sql, check_sql , extract_date],
    allow_delegation=False,
)


extract_data = Task(
    description="Extract data that is required for the query {query}.",
    expected_output=(
    "A clear confirmation message describing what happened "
    "(e.g. 'Tracker water_intake created successfully with columns date, amount') "
    "PLUS the actual database result for the query (e.g. returned rows, aggregates, or schema details). "
    "Do not just execute tools endlessly — always provide both the confirmation message and the query result."
),
    agent= tracker_agent,
)


crew = Crew(
    agents=[tracker_agent],
    tasks=[extract_data],
    memory=False,
    verbose=True
)

@app.route("/response", methods=["GET", "POST"])
def response():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True)
            query = None
            if data and "query" in data:
                query = data["query"]
            else:
                query = request.form.get("query")
        else:  # GET request
            query = request.args.get("query")

        if not query:
            return jsonify({"error": "No query provided"}), 400

        # your existing logic here...

        inputs = {
            "query": query
        }

        result = crew.kickoff(inputs=inputs)
        result = str(result)

        client = Groq(api_key= os.getenv("GROQ_API_KEY") )


        if "visualise" in query or "Visualise" in query:
            prompt = "User : " + query + " Agent : " + result


            class AgentResultSummarizer:
                def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
                    self.client = Groq(api_key= os.getenv("GROQ_API_KEY"))
                    self.model = model
                    self.function_schema = self._get_function_schema()
                    self.schema_prompt = self._get_schema_prompt()

                def _get_function_schema(self):
                    return {
                        "name": "summarize_agent_output",
                        "description": "Extract x-axis (features) and y-axis (numeric values) from agent results or database query outputs. If no query result is present (e.g., CREATE/INSERT/UPDATE), return only a message.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "x_axis": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of feature values to plot on the x-axis (e.g., dates, categories). Leave empty if no query results."
                                },
                                "y_axis": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "description": "List of numeric values corresponding to each x-axis item. Leave empty if no query results."
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Plain explanation of what the agent did (e.g., 'Created table water_intake', 'Inserted 3.5 units for 2025-08-28')."
                                }
                            },
                            "required": ["x_axis", "y_axis", "message"]
                        }
                    }

                def _get_schema_prompt(self):
                    return """
            Follow this exact structure when summarizing agent or database outputs:

            {
            "x_axis": [string],   # e.g. ["2025-08-17", "2025-08-18", "2025-08-19"]
            "y_axis": [number],   # e.g. [2.5, 3.0, 2.75]
            "message": string     # e.g. "Retrieved water intake logs." or "Inserted new record."
            }

            Rules:
            - If the agent output is a query result: fill x_axis and y_axis with aligned values, add a short message like "Retrieved records."
            - If the agent performed CREATE/INSERT/DELETE/UPDATE: leave x_axis and y_axis empty arrays, only fill message with the explanation.
            - Ensure x_axis and y_axis lengths always match.
            - Always return valid JSON with all three fields.
            """

                def summarize(self, agent_output: str) -> dict:
                    messages = [
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant that converts agent/database outputs "
                                "into structured JSON with x_axis, y_axis, and a message. "
                                "Strictly follow the function schema. No extra commentary.\n"
                                + self.schema_prompt
                            )
                        },
                        {
                            "role": "user",
                            "content": agent_output
                        }
                    ]

                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=[{"type": "function", "function": self.function_schema}],
                        tool_choice="auto",
                        temperature=0
                    )

                    tool_call = response.choices[0].message.tool_calls[0]
                    arguments = json.loads(tool_call.function.arguments)

                    return arguments
            
            summarise = AgentResultSummarizer(api_key= os.getenv("GROQ_API_KEY"))
            data = summarise.summarize(prompt)
            return jsonify({ "output": data})


        else:
            prompt = "User : " + query + " Agent : " + result

            chat_completion = client.chat.completions.create(
                messages=[
                    # Set an optional system message. This sets the behavior of the
                    # assistant and can be used to provide specific instructions for
                    # how it should behave throughout the conversation.
                    {
                    "role": "system",
                    "content": """
        You are a helpful assistant that explains database agent actions to the user.

        Behavior Rules:
        1. If the user only runs an action (e.g., CREATE TABLE, INSERT INTO, UPDATE, DELETE):
        - Do not summarize or generate tables.
        - Instead, clearly explain in natural language what the agent just did.
        - Example: "A new table named water_intake was created with columns date and amount."

        2. If the user asks to SHOW, VIEW, SUMMARIZE, or ANALYZE the data:
        - Present the data in a clean table format.
        - Summarize the key points in natural language.
        - Highlight insights (averages, trends, increases/decreases).
        - Detect and explain patterns across dates:
        • Identify consecutive days (streaks of tracking).  
        • Point out missing days (gaps in tracking).  
        • Mention longest streak and most recent streak if possible.

        3. Always respond in a way that helps the user understand the result of their query.
        4. Never produce SQL or raw outputs unless explicitly requested.
        """

                    },
                    # Set a user message for the assistant to respond to.
                    {
                        "role": "user",
                        "content": prompt ,
                    }
                ],

                # The language model which will generate the completion.
                model="llama-3.3-70b-versatile"
            )

            # Print the completion returned by the LLM.
            print(chat_completion.choices[0].message.content)

            return jsonify({ "output": chat_completion.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)


# ngrok config add-authtoken 32Gt4tt4IWJNnlYyZYuA7OBOraB_7YPuczj5txKFziwhriVfR
#ngrok http 5000



