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


from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import operator
import json
import re


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sql_query: str
    query_result: str
    final_answer: str


class MCPSQLAgent:
    def __init__(self, api_key: str, db_path: str = "./taxi.db"):
        self.api_key = api_key
        self.db_path = db_path
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
        text = text.strip()
        
        code_block_pattern = r'```(?:sqlite)?\s*([\s\S]*?)```'
        matches = re.findall(code_block_pattern, text, re.IGNORECASE)
        if matches:
            return matches[0].strip()
        
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
    
    def execute_sql_direct(self, query: str) -> str:
        try:
            query = query.strip()
            if not query:
                return json.dumps({"error": "Empty query"}, ensure_ascii=False)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith(("SELECT", "WITH")):
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                if len(rows) == 0:
                    conn.close()
                    return json.dumps({"message": "No results found", "columns": columns, "rows": []}, ensure_ascii=False)
                
                result = {"columns": columns, "rows": [list(row) for row in rows[:100]]}
                if len(rows) > 100:
                    result["note"] = f"Showing first 100 of {len(rows)} rows"
                
                conn.close()
                return json.dumps(result, ensure_ascii=False, default=str)
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                return json.dumps({"message": f"Query executed successfully. Rows affected: {affected}"}, ensure_ascii=False)
        
        except sqlite3.Error as e:
            return json.dumps({"error": f"SQL Error: {str(e)}", "query": query}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error: {str(e)}", "query": query}, ensure_ascii=False)
    
    def generate_sql(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        user_question = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_question = msg.content
                break
        
        system_prompt = f"""You are an SQL query generator. Your ONLY job is to output a valid SQLite query.

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

CRITICAL RULES:
1. Output ONLY the SQL query
2. NO explanations, NO text before or after
3. Must be valid SQLite syntax
4. End with semicolon
5. Use LIMIT 50 for SELECT queries
6. rides.status can be: 'completed' or 'cancelled'
7. payment_method can be: 'cash', 'card', 'wallet'

Question: {user_question}"""

        response = self.llm.invoke([HumanMessage(content=system_prompt)])
        raw_response = response.content.strip()
        sql_query = self.extract_sql_query(raw_response)
        
        return {
            "messages": state["messages"],
            "sql_query": sql_query,
            "query_result": "",
            "final_answer": ""
        }
    
    def execute_query(self, state: AgentState) -> AgentState:
        sql_query = state["sql_query"]
        result = self.execute_sql_direct(sql_query)
        
        return {
            "messages": state["messages"],
            "sql_query": sql_query,
            "query_result": result,
            "final_answer": ""
        }
    
    def generate_answer(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        sql_query = state["sql_query"]
        query_result = state["query_result"]
        
        user_question = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_question = msg.content
                break
        
        system_prompt = """You are a helpful assistant. Explain the database query results in Persian (Farsi).
Be clear and format numbers nicely. Monetary values are in Toman."""

        user_prompt = f"""Question: {user_question}

SQL: {sql_query}

Result: {query_result}

Answer in Persian:"""

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        return {
            "messages": state["messages"] + [AIMessage(content=response.content)],
            "sql_query": sql_query,
            "query_result": query_result,
            "final_answer": response.content
        }
    
    def build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("generate_sql", self.generate_sql)
        workflow.add_node("execute_query", self.execute_query)
        workflow.add_node("generate_answer", self.generate_answer)
        
        workflow.set_entry_point("generate_sql")
        workflow.add_edge("generate_sql", "execute_query")
        workflow.add_edge("execute_query", "generate_answer")
        workflow.add_edge("generate_answer", END)
        
        self.graph = workflow.compile()
    
    def query(self, question: str) -> dict:
        initial_state = {
            "messages": [HumanMessage(content=question)],
            "sql_query": "",
            "query_result": "",
            "final_answer": ""
        }
        
        result = self.graph.invoke(initial_state)
        
        return {
            "question": question,
            "sql_query": result["sql_query"],
            "query_result": result["query_result"],
            "answer": result["final_answer"]
        }


agent = None


def initialize_agent(api_key: str) -> str:
    global agent
    
    if not api_key.strip():
        return "لطفا کلید API را وارد کنید"
    
    if not os.path.exists(DB_PATH):
        create_database()
    
    try:
        agent = MCPSQLAgent(api_key=api_key, db_path=DB_PATH)
        return "سیستم با موفقیت راه اندازی شد"
    except Exception as e:
        return f"خطا در راه اندازی: {str(e)}"


def reset_database() -> str:
    global agent
    agent = None
    
    try:
        create_database()
        return "پایگاه داده با موفقیت بازنشانی شد. لطفا مجددا سیستم را راه اندازی کنید."
    except Exception as e:
        return f"خطا: {str(e)}"


def ask_question(question: str, api_key: str) -> tuple:
    global agent
    
    if not question.strip():
        return "", "", "لطفا یک سوال وارد کنید"
    
    if agent is None:
        init_result = initialize_agent(api_key)
        if "خطا" in init_result:
            return "", "", init_result
    
    try:
        result = agent.query(question)
        return result["sql_query"], result["query_result"], result["answer"]
    except Exception as e:
        return "", "", f"خطا: {str(e)}"


def get_sample_questions():
    return """
سوالات نمونه:

- تعداد کل سفرها چقدر است؟
- مجموع درآمد سیستم چقدر است؟
- پرکارترین راننده کیست؟
- محبوب ترین مبدا سفرها کجاست؟
- میانگین امتیاز رانندگان چقدر است؟
- چند سفر لغو شده است؟
- میانگین مسافت سفرها چقدر است؟
- کدام نوع خودرو بیشترین سفر را داشته؟
- درآمد هر راننده چقدر بوده؟
- چند مشتری فعال داریم؟
- میانگین انعام چقدر است؟
- لیست رانندگان با امتیاز بالای 4.5
"""


with gr.Blocks(
    title="سیستم پرسش و پاسخ تاکسی",
    theme=gr.themes.Soft(),
    css="""
    .rtl {direction: rtl; text-align: right;}
    .ltr {direction: ltr; text-align: left;}
    """
) as demo:
    gr.Markdown(
        """
        # سیستم پرسش و پاسخ هوشمند پایگاه داده تاکسی
        ## با استفاده از LangGraph
        """,
        elem_classes=["rtl"]
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            api_key_input = gr.Textbox(
                label="کلید API اوپن روتر",
                placeholder="sk-or-...",
                type="password",
                elem_classes=["rtl"]
            )
            
            with gr.Row():
                init_btn = gr.Button("راه اندازی", variant="primary")
                reset_btn = gr.Button("بازنشانی", variant="secondary")
            
            init_status = gr.Textbox(
                label="وضعیت",
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
            
            with gr.Accordion("کوئری SQL", open=True):
                sql_output = gr.Code(
                    label="SQL",
                    language="sql",
                    lines=5
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
    
    init_btn.click(fn=initialize_agent, inputs=[api_key_input], outputs=[init_status])
    reset_btn.click(fn=reset_database, inputs=[], outputs=[init_status])
    ask_btn.click(fn=ask_question, inputs=[question_input, api_key_input], outputs=[sql_output, result_output, answer_output])
    question_input.submit(fn=ask_question, inputs=[question_input, api_key_input], outputs=[sql_output, result_output, answer_output])


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        create_database()
    demo.launch(server_name="0.0.0.0", server_port=7860)