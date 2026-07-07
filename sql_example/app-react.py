# app.py
import gradio as gr
import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "./taxi.db"


def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            rating REAL DEFAULT 5.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE drivers (
            driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            license_number TEXT UNIQUE NOT NULL,
            rating REAL DEFAULT 5.0,
            total_rides INTEGER DEFAULT 0,
            is_available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE vehicles (
            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER NOT NULL,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            color TEXT NOT NULL,
            plate_number TEXT UNIQUE NOT NULL,
            vehicle_type TEXT NOT NULL,
            capacity INTEGER DEFAULT 4,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE ride_types (
            ride_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            base_fare REAL NOT NULL,
            per_km_rate REAL NOT NULL,
            per_minute_rate REAL NOT NULL,
            minimum_fare REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE locations (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            city TEXT NOT NULL,
            zone TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE rides (
            ride_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            driver_id INTEGER,
            vehicle_id INTEGER,
            ride_type_id INTEGER NOT NULL,
            pickup_location_id INTEGER NOT NULL,
            dropoff_location_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            request_time TIMESTAMP NOT NULL,
            pickup_time TIMESTAMP,
            dropoff_time TIMESTAMP,
            distance_km REAL,
            duration_minutes INTEGER,
            fare_amount REAL,
            tip_amount REAL DEFAULT 0,
            payment_method TEXT,
            rating_by_user INTEGER,
            rating_by_driver INTEGER,
            cancellation_reason TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
            FOREIGN KEY (ride_type_id) REFERENCES ride_types(ride_type_id),
            FOREIGN KEY (pickup_location_id) REFERENCES locations(location_id),
            FOREIGN KEY (dropoff_location_id) REFERENCES locations(location_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ride_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            transaction_id TEXT,
            payment_time TIMESTAMP,
            FOREIGN KEY (ride_id) REFERENCES rides(ride_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE promotions (
            promotion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            discount_type TEXT NOT NULL,
            discount_value REAL NOT NULL,
            max_discount REAL,
            min_ride_amount REAL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            max_uses INTEGER,
            current_uses INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE driver_earnings (
            earning_id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER NOT NULL,
            ride_id INTEGER NOT NULL,
            base_earning REAL NOT NULL,
            tip_amount REAL DEFAULT 0,
            bonus_amount REAL DEFAULT 0,
            commission_rate REAL NOT NULL,
            commission_amount REAL NOT NULL,
            net_earning REAL NOT NULL,
            earning_date DATE NOT NULL,
            is_paid INTEGER DEFAULT 0,
            FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
            FOREIGN KEY (ride_id) REFERENCES rides(ride_id)
        )
    """)
    
    conn.commit()
    
    first_names = ["Ali", "Mohammad", "Reza", "Hossein", "Mehdi", "Amir", "Saeed", "Hamid", "Javad", "Nima",
                   "Sara", "Maryam", "Zahra", "Fatemeh", "Narges", "Leila", "Mina", "Shirin", "Parisa", "Nazanin"]
    last_names = ["Ahmadi", "Hosseini", "Mohammadi", "Rezaei", "Karimi", "Hashemi", "Mousavi", "Jafari", "Moradi", "Alavi"]
    
    users = []
    for i in range(100):
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"{first.lower()}.{last.lower()}{i}@email.com"
        phone = f"09{random.randint(10, 39)}{random.randint(1000000, 9999999)}"
        rating = round(random.uniform(3.5, 5.0), 2)
        created = datetime.now() - timedelta(days=random.randint(1, 365))
        users.append((first, last, email, phone, rating, created, 1))
    
    cursor.executemany("""
        INSERT INTO users (first_name, last_name, email, phone, rating, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, users)
    
    drivers = []
    for i in range(50):
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"driver.{first.lower()}.{last.lower()}{i}@email.com"
        phone = f"09{random.randint(10, 39)}{random.randint(1000000, 9999999)}"
        license_num = f"DL{random.randint(100000, 999999)}"
        rating = round(random.uniform(3.8, 5.0), 2)
        total_rides = random.randint(10, 500)
        created = datetime.now() - timedelta(days=random.randint(30, 730))
        drivers.append((first, last, email, phone, license_num, rating, total_rides, random.randint(0, 1), created, 1))
    
    cursor.executemany("""
        INSERT INTO drivers (first_name, last_name, email, phone, license_number, rating, total_rides, is_available, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, drivers)
    
    makes_models = [
        ("Toyota", "Camry"), ("Toyota", "Corolla"), ("Honda", "Accord"), ("Honda", "Civic"),
        ("Hyundai", "Sonata"), ("Hyundai", "Elantra"), ("Kia", "Optima"), ("Kia", "Cerato"),
        ("Peugeot", "206"), ("Peugeot", "207"), ("Peugeot", "405"), ("Samand", "LX"),
        ("Iran Khodro", "Dena"), ("Iran Khodro", "Runna"), ("MVM", "315"), ("Chery", "Tiggo")
    ]
    colors = ["White", "Black", "Silver", "Gray", "Blue", "Red", "Green", "Brown"]
    vehicle_types = ["Economy", "Comfort", "Premium", "XL"]
    
    vehicles = []
    for driver_id in range(1, 51):
        make, model = random.choice(makes_models)
        year = random.randint(2015, 2024)
        color = random.choice(colors)
        plate = f"{random.randint(10, 99)}{chr(random.randint(65, 90))}{random.randint(100, 999)}-{random.randint(10, 99)}"
        v_type = random.choice(vehicle_types)
        capacity = 4 if v_type != "XL" else 6
        vehicles.append((driver_id, make, model, year, color, plate, v_type, capacity, 1))
    
    cursor.executemany("""
        INSERT INTO vehicles (driver_id, make, model, year, color, plate_number, vehicle_type, capacity, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, vehicles)
    
    ride_types = [
        ("Economy", 5000, 2000, 500, 15000),
        ("Comfort", 8000, 3000, 700, 25000),
        ("Premium", 15000, 5000, 1000, 40000),
        ("XL", 10000, 3500, 800, 30000)
    ]
    
    cursor.executemany("""
        INSERT INTO ride_types (name, base_fare, per_km_rate, per_minute_rate, minimum_fare)
        VALUES (?, ?, ?, ?, ?)
    """, ride_types)
    
    tehran_locations = [
        ("Azadi Square", "Azadi St, Tehran", 35.6997, 51.3380, "Tehran", "West"),
        ("Tajrish Square", "Tajrish, Tehran", 35.8042, 51.4333, "Tehran", "North"),
        ("Vanak Square", "Vanak, Tehran", 35.7575, 51.4100, "Tehran", "North"),
        ("Ferdowsi Square", "Ferdowsi St, Tehran", 35.6892, 51.4200, "Tehran", "Central"),
        ("Enghelab Square", "Enghelab St, Tehran", 35.7012, 51.3890, "Tehran", "Central"),
        ("Imam Khomeini Square", "Imam Khomeini St, Tehran", 35.6833, 51.4167, "Tehran", "Central"),
        ("Valiasr Square", "Valiasr St, Tehran", 35.7150, 51.4050, "Tehran", "Central"),
        ("Tehranpars", "Tehranpars, Tehran", 35.7350, 51.5100, "Tehran", "East"),
        ("Sadeghieh", "Sadeghieh, Tehran", 35.7200, 51.3300, "Tehran", "West"),
        ("Shahr-e Rey", "Shahr-e Rey, Tehran", 35.6000, 51.4300, "Tehran", "South"),
        ("Mehrabad Airport", "Mehrabad, Tehran", 35.6892, 51.3100, "Tehran", "West"),
        ("Imam Khomeini Airport", "IKA, Tehran", 35.4161, 51.1522, "Tehran", "South"),
        ("Milad Tower", "Milad Tower, Tehran", 35.7448, 51.3753, "Tehran", "North"),
        ("Darband", "Darband, Tehran", 35.8200, 51.4200, "Tehran", "North"),
        ("Chitgar Park", "Chitgar, Tehran", 35.7450, 51.2900, "Tehran", "West"),
        ("Tehran Grand Bazaar", "Grand Bazaar, Tehran", 35.6761, 51.4228, "Tehran", "Central"),
        ("Niavaran Palace", "Niavaran, Tehran", 35.8100, 51.4650, "Tehran", "North"),
        ("Tabiat Bridge", "Tabiat Bridge, Tehran", 35.7650, 51.4250, "Tehran", "North"),
        ("Eram Park", "Eram, Tehran", 35.7100, 51.4800, "Tehran", "East"),
        ("Pardis Technology Park", "Pardis, Tehran", 35.7600, 51.7800, "Tehran", "East")
    ]
    
    cursor.executemany("""
        INSERT INTO locations (name, address, latitude, longitude, city, zone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tehran_locations)
    
    statuses = ["completed", "completed", "completed", "completed", "completed", 
                "completed", "completed", "cancelled", "cancelled", "completed"]
    payment_methods = ["cash", "card", "wallet", "card", "wallet"]
    cancellation_reasons = ["Driver cancelled", "User cancelled", "No driver available", "Changed plans"]
    
    rides = []
    for i in range(500):
        user_id = random.randint(1, 100)
        driver_id = random.randint(1, 50)
        vehicle_id = driver_id
        ride_type_id = random.randint(1, 4)
        pickup_loc = random.randint(1, 20)
        dropoff_loc = random.randint(1, 20)
        while dropoff_loc == pickup_loc:
            dropoff_loc = random.randint(1, 20)
        
        status = random.choice(statuses)
        request_time = datetime.now() - timedelta(days=random.randint(1, 180), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        if status == "completed":
            pickup_time = request_time + timedelta(minutes=random.randint(3, 15))
            duration = random.randint(10, 60)
            dropoff_time = pickup_time + timedelta(minutes=duration)
            distance = round(random.uniform(2, 25), 2)
            
            cursor.execute("SELECT base_fare, per_km_rate, per_minute_rate, minimum_fare FROM ride_types WHERE ride_type_id = ?", (ride_type_id,))
            rt = cursor.fetchone()
            fare = max(rt[0] + (distance * rt[1]) + (duration * rt[2]), rt[3])
            fare = round(fare, 0)
            
            tip = round(random.choice([0, 0, 0, fare * 0.1, fare * 0.15, fare * 0.2]), 0)
            payment = random.choice(payment_methods)
            user_rating = random.randint(3, 5) if random.random() > 0.3 else None
            driver_rating = random.randint(3, 5) if random.random() > 0.3 else None
            cancel_reason = None
        else:
            pickup_time = None
            dropoff_time = None
            duration = None
            distance = None
            fare = None
            tip = 0
            payment = None
            user_rating = None
            driver_rating = None
            cancel_reason = random.choice(cancellation_reasons)
            driver_id = None
            vehicle_id = None
        
        rides.append((user_id, driver_id, vehicle_id, ride_type_id, pickup_loc, dropoff_loc,
                     status, request_time, pickup_time, dropoff_time, distance, duration,
                     fare, tip, payment, user_rating, driver_rating, cancel_reason))
    
    cursor.executemany("""
        INSERT INTO rides (user_id, driver_id, vehicle_id, ride_type_id, pickup_location_id, dropoff_location_id,
                          status, request_time, pickup_time, dropoff_time, distance_km, duration_minutes,
                          fare_amount, tip_amount, payment_method, rating_by_user, rating_by_driver, cancellation_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rides)
    
    cursor.execute("SELECT ride_id, user_id, fare_amount, tip_amount, payment_method, dropoff_time FROM rides WHERE status = 'completed'")
    completed_rides = cursor.fetchall()
    
    payments = []
    for ride in completed_rides:
        ride_id, user_id, fare, tip, method, dropoff_time = ride
        total = fare + tip
        tx_id = f"TX{random.randint(100000000, 999999999)}"
        payments.append((ride_id, user_id, total, method, "completed", tx_id, dropoff_time))
    
    cursor.executemany("""
        INSERT INTO payments (ride_id, user_id, amount, payment_method, payment_status, transaction_id, payment_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, payments)
    
    promotions = [
        ("WELCOME50", "50% off first ride", "percentage", 50, 30000, 10000, datetime.now() - timedelta(days=30), datetime.now() + timedelta(days=30), 1000, 150, 1),
        ("SUMMER20", "20% summer discount", "percentage", 20, 20000, 15000, datetime.now() - timedelta(days=60), datetime.now() + timedelta(days=60), 5000, 890, 1),
        ("FLAT5000", "5000 Toman off", "fixed", 5000, None, 20000, datetime.now() - timedelta(days=10), datetime.now() + timedelta(days=20), 2000, 456, 1),
        ("VIP30", "30% VIP discount", "percentage", 30, 50000, 30000, datetime.now() - timedelta(days=5), datetime.now() + timedelta(days=25), 500, 78, 1),
        ("NIGHT15", "15% night ride discount", "percentage", 15, 15000, 10000, datetime.now() - timedelta(days=15), datetime.now() + timedelta(days=45), 3000, 234, 1)
    ]
    
    cursor.executemany("""
        INSERT INTO promotions (code, description, discount_type, discount_value, max_discount, min_ride_amount, start_date, end_date, max_uses, current_uses, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, promotions)
    
    driver_earnings = []
    for ride in completed_rides:
        ride_id, user_id, fare, tip, method, dropoff_time = ride
        cursor.execute("SELECT driver_id FROM rides WHERE ride_id = ?", (ride_id,))
        driver_result = cursor.fetchone()
        if driver_result and driver_result[0]:
            driver_id = driver_result[0]
            commission_rate = 0.20
            base_earning = fare
            commission = round(fare * commission_rate, 0)
            bonus = round(random.choice([0, 0, 0, 1000, 2000, 5000]), 0)
            net = base_earning - commission + tip + bonus
            if isinstance(dropoff_time, datetime):
                earning_date = dropoff_time.date()
            else:
                earning_date = datetime.strptime(str(dropoff_time).split('.')[0], "%Y-%m-%d %H:%M:%S").date()
            is_paid = 1 if random.random() > 0.3 else 0
            driver_earnings.append((driver_id, ride_id, base_earning, tip, bonus, commission_rate, commission, net, earning_date, is_paid))
    
    cursor.executemany("""
        INSERT INTO driver_earnings (driver_id, ride_id, base_earning, tip_amount, bonus_amount, commission_rate, commission_amount, net_earning, earning_date, is_paid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, driver_earnings)
    
    conn.commit()
    conn.close()
    
    return "Database created successfully"


from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import operator
import json
import re


class AgentState(TypedDict):
    """State for the ReACT SQL Agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_question: str
    sql_query: str
    query_result: str
    error_message: str
    attempt_count: int
    max_attempts: int
    execution_history: list  # Track all attempts for debugging
    final_answer: str
    should_continue: bool


class ReACTSQLAgent:
    """
    ReACT (Reasoning and Acting) SQL Agent
    
    This agent follows the ReACT pattern:
    1. THOUGHT: Reason about what SQL query to generate
    2. ACTION: Execute the SQL query
    3. OBSERVATION: Observe the result or error
    4. LOOP: If error, go back to THOUGHT with error context
    """
    
    def __init__(self, api_key: str, db_path: str = "./taxi.db", max_attempts: int = 3):
        self.api_key = api_key
        self.db_path = db_path
        self.max_attempts = max_attempts
        self.llm = None
        self.schema_info = None
        self.graph = None
        self.setup_llm()
        self.load_schema()
        self.build_graph()
    
    def setup_llm(self):
        os.environ["OPENAI_API_KEY"] = self.api_key
        os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
        
        self.llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            temperature=0,
            max_tokens=2000
        )
    
    def load_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema[table_name] = [
                {"name": col[1], "type": col[2], "nullable": not col[3], "pk": col[5]}
                for col in columns
            ]
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            schema[table_name + "_count"] = count
        
        conn.close()
        self.schema_info = schema
    
    def get_schema_description(self):
        desc = "Database Schema:\n\n"
        for key, value in self.schema_info.items():
            if not key.endswith("_count"):
                table_name = key
                count = self.schema_info.get(f"{table_name}_count", 0)
                desc += f"Table: {table_name} ({count} rows)\n"
                desc += "Columns:\n"
                for col in value:
                    pk = " [PK]" if col["pk"] else ""
                    desc += f"  - {col['name']} ({col['type']}){pk}\n"
                desc += "\n"
        return desc
    
    def extract_sql_query(self, text: str) -> str:
        """Extract SQL query from LLM response"""
        text = text.strip()
        
        # Try to find SQL in code blocks first
        code_block_pattern = r'```(?:sqlite)?\s*([\s\S]*?)```'
        matches = re.findall(code_block_pattern, text, re.IGNORECASE)
        if matches:
            return matches[0].strip()
        
        # Look for SQL keywords
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH']
        text_upper = text.upper()
        
        for keyword in sql_keywords:
            if keyword in text_upper:
                start_idx = text_upper.find(keyword)
                sql_part = text[start_idx:]
                
                lines = sql_part.split('\n')
                clean_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('--'):
                        continue
                    if any(stripped.lower().startswith(x) for x in ['this ', 'note:', 'please ', 'the ', 'i ', 'here']):
                        break
                    clean_lines.append(line)
                
                sql_query = '\n'.join(clean_lines).strip()
                
                if sql_query and not sql_query.endswith(';'):
                    sql_query += ';'
                
                return sql_query
        
        return text
    
    def execute_sql(self, query: str) -> tuple[bool, str]:
        """
        Execute SQL query and return (success, result_or_error)
        """
        try:
            query = query.strip()
            if not query:
                return False, "Empty query provided"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith(("SELECT", "WITH")):
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                if len(rows) == 0:
                    conn.close()
                    return True, json.dumps({"message": "No results found", "columns": columns, "rows": []}, ensure_ascii=False)
                
                result = {"columns": columns, "rows": [list(row) for row in rows[:100]]}
                if len(rows) > 100:
                    result["note"] = f"Showing first 100 of {len(rows)} rows"
                
                conn.close()
                return True, json.dumps(result, ensure_ascii=False, default=str)
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                return True, json.dumps({"message": f"Query executed successfully. Rows affected: {affected}"}, ensure_ascii=False)
        
        except sqlite3.Error as e:
            return False, f"SQL Error: {str(e)}"
        except Exception as e:
            return False, f"Execution Error: {str(e)}"
    
    # ==================== ReACT Nodes ====================
    
    def thought_node(self, state: AgentState) -> AgentState:
        """
        THOUGHT: Reason about the query and generate SQL
        This node considers previous errors if any
        """
        user_question = state["user_question"]
        error_message = state.get("error_message", "")
        attempt_count = state.get("attempt_count", 0)
        execution_history = state.get("execution_history", [])
        
        # Build context with error history if this is a retry
        error_context = ""
        if error_message and attempt_count > 0:
            error_context = f"""

⚠️ PREVIOUS ATTEMPT FAILED!
Attempt #{attempt_count} failed with error:
{error_message}

Previous SQL that failed:
{state.get('sql_query', 'N/A')}

Please analyze the error and generate a CORRECTED SQL query.
Common fixes:
- Check column names match the schema exactly
- Verify table names are correct
- Ensure proper JOIN conditions
- Check for syntax errors
- Verify data types in comparisons
"""
        
        system_prompt = f"""You are an expert SQL query generator using ReACT (Reasoning and Acting) pattern.

{self.get_schema_description()}

Relationships:
- rides.user_id -> users.user_id
- rides.driver_id -> drivers.driver_id  
- rides.vehicle_id -> vehicles.vehicle_id
- rides.ride_type_id -> ride_types.ride_type_id
- rides.pickup_location_id -> locations.location_id
- rides.dropoff_location_id -> locations.location_id
- vehicles.driver_id -> drivers.driver_id
- payments.ride_id -> rides.ride_id
- driver_earnings.driver_id -> drivers.driver_id

IMPORTANT RULES:
1. Output ONLY the SQL query - no explanations
2. Must be valid SQLite syntax
3. End with semicolon
4. Use LIMIT 50 for SELECT queries
5. rides.status can be: 'completed' or 'cancelled'
6. payment_method can be: 'cash', 'card', 'wallet'
{error_context}

User Question: {user_question}

Generate the SQL query:"""

        response = self.llm.invoke([HumanMessage(content=system_prompt)])
        raw_response = response.content.strip()
        sql_query = self.extract_sql_query(raw_response)
        
        # Record this attempt
        new_history = execution_history + [{
            "attempt": attempt_count + 1,
            "sql": sql_query,
            "phase": "thought"
        }]
        
        return {
            "messages": state["messages"],
            "user_question": user_question,
            "sql_query": sql_query,
            "query_result": "",
            "error_message": "",
            "attempt_count": attempt_count + 1,
            "max_attempts": state["max_attempts"],
            "execution_history": new_history,
            "final_answer": "",
            "should_continue": True
        }
    
    def action_node(self, state: AgentState) -> AgentState:
        """
        ACTION: Execute the SQL query
        """
        sql_query = state["sql_query"]
        execution_history = state.get("execution_history", [])
        
        success, result = self.execute_sql(sql_query)
        
        # Update history with execution result
        if execution_history:
            execution_history[-1]["execution_result"] = "success" if success else "error"
            execution_history[-1]["result"] = result[:500] if len(result) > 500 else result
        
        if success:
            return {
                "messages": state["messages"],
                "user_question": state["user_question"],
                "sql_query": sql_query,
                "query_result": result,
                "error_message": "",
                "attempt_count": state["attempt_count"],
                "max_attempts": state["max_attempts"],
                "execution_history": execution_history,
                "final_answer": "",
                "should_continue": True
            }
        else:
            return {
                "messages": state["messages"],
                "user_question": state["user_question"],
                "sql_query": sql_query,
                "query_result": "",
                "error_message": result,  # Error message
                "attempt_count": state["attempt_count"],
                "max_attempts": state["max_attempts"],
                "execution_history": execution_history,
                "final_answer": "",
                "should_continue": True
            }
    
    def observation_node(self, state: AgentState) -> AgentState:
        """
        OBSERVATION: Check the result and decide next step
        This is a pass-through node that prepares state for routing
        """
        # Just pass through - routing logic is in should_retry
        return state
    
    def answer_node(self, state: AgentState) -> AgentState:
        """
        Generate final answer from successful query result
        """
        user_question = state["user_question"]
        sql_query = state["sql_query"]
        query_result = state["query_result"]
        execution_history = state.get("execution_history", [])
        attempt_count = state["attempt_count"]
        
        # Add retry information if there were multiple attempts
        retry_info = ""
        if attempt_count > 1:
            retry_info = f"\n\n(Note: Query succeeded after {attempt_count} attempts)"
        
        system_prompt = """You are a helpful assistant. Explain the database query results in Persian (Farsi).
Be clear and format numbers nicely. Monetary values are in Toman.
If the query required multiple attempts to succeed, briefly mention that the system self-corrected."""

        user_prompt = f"""Question: {user_question}

SQL Query: {sql_query}

Query Result: {query_result}

Number of attempts: {attempt_count}

Please provide a clear answer in Persian:"""

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        final_answer = response.content
        if attempt_count > 1:
            final_answer += f"\n\n✅ (سیستم پس از {attempt_count} تلاش به نتیجه رسید)"
        
        return {
            "messages": state["messages"] + [AIMessage(content=final_answer)],
            "user_question": user_question,
            "sql_query": sql_query,
            "query_result": query_result,
            "error_message": "",
            "attempt_count": attempt_count,
            "max_attempts": state["max_attempts"],
            "execution_history": execution_history,
            "final_answer": final_answer,
            "should_continue": False
        }
    
    def error_node(self, state: AgentState) -> AgentState:
        """
        Handle final error when max attempts exceeded
        """
        execution_history = state.get("execution_history", [])
        attempt_count = state["attempt_count"]
        
        # Build error summary
        error_summary = f"متأسفانه پس از {attempt_count} تلاش، سیستم نتوانست کوئری صحیح را تولید کند.\n\n"
        error_summary += "خلاصه تلاش‌ها:\n"
        
        for attempt in execution_history:
            error_summary += f"\n🔄 تلاش {attempt['attempt']}:\n"
            error_summary += f"SQL: {attempt.get('sql', 'N/A')[:100]}...\n"
            error_summary += f"نتیجه: {attempt.get('result', 'N/A')[:200]}\n"
        
        error_summary += f"\n❌ آخرین خطا: {state['error_message']}"
        
        return {
            "messages": state["messages"] + [AIMessage(content=error_summary)],
            "user_question": state["user_question"],
            "sql_query": state["sql_query"],
            "query_result": "",
            "error_message": state["error_message"],
            "attempt_count": attempt_count,
            "max_attempts": state["max_attempts"],
            "execution_history": execution_history,
            "final_answer": error_summary,
            "should_continue": False
        }
    
    # ==================== Routing Logic ====================
    
    def should_retry(self, state: AgentState) -> Literal["retry", "answer", "error"]:
        """
        Decide whether to retry, generate answer, or give up
        """
        error_message = state.get("error_message", "")
        query_result = state.get("query_result", "")
        attempt_count = state.get("attempt_count", 0)
        max_attempts = state.get("max_attempts", 3)
        
        # If we have a successful result, go to answer
        if query_result and not error_message:
            return "answer"
        
        # If we have an error but haven't exceeded max attempts, retry
        if error_message and attempt_count < max_attempts:
            return "retry"
        
        # Max attempts exceeded, go to error
        return "error"
    
    # ==================== Graph Building ====================
    
    def build_graph(self):
        """
        Build the ReACT graph with retry loop
        
        Graph structure:
        
        START -> thought -> action -> observation -> [routing]
                   ^                                    |
                   |                                    v
                   +---- retry <----+          answer -> END
                                    |             |
                                    +-- error ----+
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("thought", self.thought_node)
        workflow.add_node("action", self.action_node)
        workflow.add_node("observation", self.observation_node)
        workflow.add_node("answer", self.answer_node)
        workflow.add_node("error", self.error_node)
        
        # Set entry point
        workflow.set_entry_point("thought")
        
        # Add edges
        workflow.add_edge("thought", "action")
        workflow.add_edge("action", "observation")
        
        # Conditional routing from observation
        workflow.add_conditional_edges(
            "observation",
            self.should_retry,
            {
                "retry": "thought",  # Go back to thought with error context
                "answer": "answer",  # Success - generate answer
                "error": "error"     # Max attempts exceeded
            }
        )
        
        # Terminal edges
        workflow.add_edge("answer", END)
        workflow.add_edge("error", END)
        
        self.graph = workflow.compile()
    
    def query(self, question: str) -> dict:
        """
        Execute a query using the ReACT agent
        """
        initial_state: AgentState = {
            "messages": [HumanMessage(content=question)],
            "user_question": question,
            "sql_query": "",
            "query_result": "",
            "error_message": "",
            "attempt_count": 0,
            "max_attempts": self.max_attempts,
            "execution_history": [],
            "final_answer": "",
            "should_continue": True
        }
        
        result = self.graph.invoke(initial_state)
        
        return {
            "question": question,
            "sql_query": result["sql_query"],
            "query_result": result["query_result"],
            "answer": result["final_answer"],
            "attempts": result["attempt_count"],
            "execution_history": result["execution_history"]
        }


# Global agent instance
agent = None


def initialize_agent(api_key: str, max_retries: int = 3) -> str:
    global agent
    
    if not api_key.strip():
        return "لطفا کلید API را وارد کنید"
    
    if not os.path.exists(DB_PATH):
        create_database()
    
    try:
        agent = ReACTSQLAgent(api_key=api_key, db_path=DB_PATH, max_attempts=max_retries)
        return f"✅ سیستم ReACT با موفقیت راه اندازی شد (حداکثر {max_retries} تلاش برای هر کوئری)"
    except Exception as e:
        return f"❌ خطا در راه اندازی: {str(e)}"


def reset_database() -> str:
    global agent
    agent = None
    
    try:
        create_database()
        return "✅ پایگاه داده با موفقیت بازنشانی شد. لطفا مجددا سیستم را راه اندازی کنید."
    except Exception as e:
        return f"❌ خطا: {str(e)}"


def ask_question(question: str, api_key: str, max_retries: int = 3) -> tuple:
    global agent
    
    if not question.strip():
        return "", "", "", "لطفا یک سوال وارد کنید"
    
    if agent is None:
        init_result = initialize_agent(api_key, max_retries)
        if "خطا" in init_result:
            return "", "", "", init_result
    
    try:
        result = agent.query(question)
        
        # Format execution history for display
        history_text = "📋 تاریخچه اجرا:\n\n"
        for attempt in result.get("execution_history", []):
            status = "✅" if attempt.get("execution_result") == "success" else "❌"
            history_text += f"{status} تلاش {attempt['attempt']}:\n"
            history_text += f"   SQL: {attempt.get('sql', 'N/A')[:100]}...\n"
            if attempt.get("result"):
                history_text += f"   نتیجه: {attempt.get('result', '')[:150]}...\n"
            history_text += "\n"
        
        return result["sql_query"], result["query_result"], history_text, result["answer"]
    except Exception as e:
        return "", "", "", f"❌ خطا: {str(e)}"


def get_sample_questions():
    return """
سوالات نمونه:

📊 آمار کلی:
- تعداد کل سفرها چقدر است؟
- مجموع درآمد سیستم چقدر است؟
- چند سفر لغو شده است؟

👤 کاربران و رانندگان:
- پرکارترین راننده کیست؟
- میانگین امتیاز رانندگان چقدر است؟
- لیست رانندگان با امتیاز بالای 4.5

📍 مکان‌ها:
- محبوب ترین مبدا سفرها کجاست؟
- کدام منطقه بیشترین سفر را داشته؟

💰 مالی:
- درآمد هر راننده چقدر بوده؟
- میانگین انعام چقدر است؟
- میانگین کرایه سفرها چقدر است؟

🚗 خودروها:
- کدام نوع خودرو بیشترین سفر را داشته؟
- میانگین مسافت سفرها چقدر است؟
"""


# ==================== Gradio Interface ====================

with gr.Blocks(
    title="سیستم ReACT پرسش و پاسخ تاکسی",
    theme=gr.themes.Soft(),
    css="""
    .rtl {direction: rtl; text-align: right;}
    .ltr {direction: ltr; text-align: left;}
    .status-box {padding: 10px; border-radius: 5px; margin: 5px 0;}
    """
) as demo:
    
    with gr.Row():
        with gr.Column(scale=1):
            api_key_input = gr.Textbox(
                label="کلید API اوپن روتر",
                placeholder="sk-or-...",
                type="password",
                elem_classes=["rtl"]
            )
            
            max_retries_slider = gr.Slider(
                minimum=1,
                maximum=5,
                value=3,
                step=1,
                label="حداکثر تعداد تلاش مجدد",
                elem_classes=["rtl"]
            )
            
            with gr.Row():
                init_btn = gr.Button("راه اندازی", variant="primary")
                reset_btn = gr.Button("بازنشانی", variant="secondary")
            
            init_status = gr.Textbox(
                label="م",
                lines=2,
                interactive=False,
                elem_classes=["rtl"]
            )
            
            gr.Markdown(get_sample_questions(), elem_classes=["rtl"])
        
        with gr.Column(scale=2):
            question_input = gr.Textbox(
                label="سوال خود را بنویسید",
                placeholder="مثال: تعداد کل سفرها چقدر است؟",
                lines=2,
                elem_classes=["rtl"]
            )
            
            ask_btn = gr.Button("ارسال سوال", variant="primary", size="lg")
            
            with gr.Accordion("کوئری SQL نهایی", open=True):
                sql_output = gr.Code(
                    label="SQL",
                    language="sql",
                    lines=5
                )
            
            with gr.Accordion("تاریخچه اجرا (ReACT Loop)", open=True):
                history_output = gr.Textbox(
                    label="Execution History",
                    lines=8,
                    interactive=False,
                    elem_classes=["ltr"]
                )
            
            with gr.Accordion("نتیجه خام", open=False):
                result_output = gr.Code(
                    label="Result",
                    language="json",
                    lines=10
                )
            
            answer_output = gr.Textbox(
                label="پاسخ",
                lines=12,
                interactive=False,
                elem_classes=["rtl"]
            )
    
    # Event handlers
    init_btn.click(
        fn=initialize_agent, 
        inputs=[api_key_input, max_retries_slider], 
        outputs=[init_status]
    )
    reset_btn.click(
        fn=reset_database, 
        inputs=[], 
        outputs=[init_status]
    )
    ask_btn.click(
        fn=ask_question, 
        inputs=[question_input, api_key_input, max_retries_slider], 
        outputs=[sql_output, result_output, history_output, answer_output]
    )
    question_input.submit(
        fn=ask_question, 
        inputs=[question_input, api_key_input, max_retries_slider], 
        outputs=[sql_output, result_output, history_output, answer_output]
    )


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        create_database()
    demo.launch(server_name="0.0.0.0", server_port=7860)