import streamlit as st
import requests
import google.generativeai as genai
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# ------------------ Gemini Setup ------------------
genai.configure(api_key="AIzaSyAYA6dptTU9j52J20itf-c9U5FccrSsH8I")
model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------ API Setup ------------------
API_BASE = "http://172.16.42.61:8502"

# ------------------ Database Setup ------------------
DB_PATH = "clinic_inventory.db"

def init_database():
    """Initialize SQLite database with inventory tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            stock_quantity INTEGER NOT NULL,
            unit TEXT NOT NULL,
            expiry_date DATE NOT NULL,
            reorder_threshold INTEGER DEFAULT 10,
            price REAL NOT NULL,
            type TEXT DEFAULT 'drug',
            barcode TEXT UNIQUE,
            usage_rate REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'nurse',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            action_type TEXT NOT NULL,
            quantity_change INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES inventory (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_sample_data():
    """Add sample inventory data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    sample_items = [
        ("Ibuprofen", "MediCare", 25, "200mg", "2025-12-15", 10, 0.50, "drug", "IBU001"),
        ("Paracetamol", "HealthPlus", 45, "500mg", "2025-11-30", 15, 0.30, "drug", "PAR002"),
        ("Amoxicillin", "PharmaBest", 8, "250mg", "2025-10-20", 5, 1.20, "drug", "AMX003"),
        ("Vitamin C", "NutriWell", 60, "1000mg", "2026-03-10", 20, 0.25, "supplement", "VIT004"),
        ("Insulin", "DiabetCare", 3, "100IU", "2025-09-05", 2, 25.00, "drug", "INS005"),
        ("Bandages", "MediAid", 100, "10cm", "2027-01-01", 50, 0.15, "medical_supply", "BND006"),
        ("Antiseptic", "CleanGuard", 15, "100ml", "2025-08-25", 5, 3.50, "medical_supply", "ANT007"),
        ("Aspirin", "HeartCare", 30, "81mg", "2025-11-10", 10, 0.40, "drug", "ASP008")
    ]
    
    for item in sample_items:
        cursor.execute('''
            INSERT OR IGNORE INTO inventory (name, brand, stock_quantity, unit, expiry_date, reorder_threshold, price, type, barcode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', item)
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(username, password):
    users = load_users()
    users[username] = hash_password(password)
    with open("users.json", "w") as f:
        json.dump(users, f)

def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    with open("users.json", "r") as f:
        return json.load(f)

def check_login(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

def get_inventory():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory ORDER BY name")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in data]

def get_low_stock_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE stock_quantity < reorder_threshold ORDER BY stock_quantity ASC")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def get_expiring_items(days=14):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM inventory WHERE expiry_date <= ? ORDER BY expiry_date ASC", (future_date,))
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def get_restock_plan():
    low_stock = get_low_stock_items()
    restock_plan = []
    for item in low_stock:
        ideal_stock = 50
        to_order = max(0, ideal_stock - item['stock_quantity'])
        restock_plan.append({
            'item': item,
            'to_order': to_order,
            'estimated_cost': to_order * item['price']
        })
    return restock_plan

def get_cheapest_brand(medicine_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE LOWER(name) = LOWER(?) ORDER BY price ASC LIMIT 1", (medicine_name,))
    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(zip(columns, row))
    return None

def generate_inventory_report():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(stock_quantity), AVG(price), SUM(stock_quantity * price) FROM inventory")
    total_items, avg_stock, avg_price, total_value = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE stock_quantity < reorder_threshold")
    low_stock_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE expiry_date <= date('now', '+14 days')")
    expiring_count = cursor.fetchone()[0]
    conn.close()
    return {
        'total_items': total_items,
        'low_stock_count': low_stock_count,
        'expiring_count': expiring_count,
        'total_value': round(total_value or 0, 2),
        'avg_stock': round(avg_stock or 0, 2),
        'avg_price': round(avg_price or 0, 2)
    }

# Initialize
init_database()
add_sample_data()

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# Login/Signup
if not st.session_state.logged_in:
    st.title("🔐 Clinic Inventory Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Log In"):
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect username or password")
    
    with tab2:
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")
        if st.button("Sign Up"):
            if new_user in load_users():
                st.warning("⚠️ Username already exists")
            elif not new_user or not new_pass:
                st.warning("Please fill all fields")
            else:
                save_user(new_user, new_pass)
                st.success("✅ Account created! Please log in.")
else:
    st.sidebar.success(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Add Inventory", "View Inventory", "Smart Assistant", "Dashboard"])

    if page == "Add Inventory":
        st.title("Clinic Inventory System")
        st.subheader("➕ Add a New Item")

        name = st.text_input("Medicine Name")
        brand = st.text_input("Brand")
        quantity = st.number_input("Quantity", min_value=0)
        unit = st.text_input("Unit (e.g., mg, ml)")
        expiry = st.date_input("Expiry Date")
        usage_rate = st.number_input("Usage Rate", min_value=0)
        price = st.number_input("Price (₹)", min_value=0.0)

        if st.button("Add Item"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO inventory (name, brand, stock_quantity, unit, expiry_date, reorder_threshold, price, type, barcode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, brand, quantity, unit, str(expiry), usage_rate, price, "drug", "AUTO"))
            conn.commit()
            conn.close()
            st.success("✅ Item added successfully!")

    elif page == "View Inventory":
        st.title("📋 Inventory List")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY name")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        items = [dict(zip(columns, row)) for row in rows]
        if items:
            df = pd.DataFrame(items)
            st.dataframe(df)
        else:
            st.info("ℹ️ No items in inventory yet.")

    elif page == "Smart Assistant":
        st.title("🤖 Smart Inventory Assistant")
        st.write("Ask anything about the inventory system.")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        query = st.chat_input("Ask a question...")
        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            st.chat_message("user").write(query)

            prompt = f"""
You are a smart assistant for a clinic inventory system. You have access to endpoints:
- /items → all medicines
- /alerts/low-stock → low stock
- /alerts/expiry → soon-to-expire

User's query: {query}
"""
            try:
                gemini_response = model.generate_content(prompt)
                reply = gemini_response.text
                st.chat_message("assistant").write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Gemini error: {e}")

    elif page == "Dashboard":
        st.title("🏥 Terminal Dashboard")

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚠ Low Stock Alerts")
            low_stock = get_low_stock_items()
            if low_stock:
                for item in low_stock:
                    st.write(f"- **{item['name']}** ({item['brand']}): {item['stock_quantity']} units (Threshold: {item['reorder_threshold']})")
            else:
                st.success("✅ No low stock items")

            st.subheader("📦 Restock Advisor")
            restock_plan = get_restock_plan()
            if restock_plan:
                for plan in restock_plan:
                    st.write(f"- **{plan['item']['name']}**: Order {plan['to_order']} units (Estimated cost: ${plan['estimated_cost']:.2f})")
            else:
                st.success("✅ No restocking needed")

        with col2:
            st.subheader("⏰ Expiry Alerts")
            expiring = get_expiring_items()
            if expiring:
                for item in expiring:
                    days_left = (datetime.strptime(item['expiry_date'], '%Y-%m-%d') - datetime.now()).days
                    st.write(f"- **{item['name']}** ({item['brand']}): Expires in {days_left} days on {item['expiry_date']}")
            else:
                st.success("✅ No items expiring soon")

            st.subheader("💰 Price Comparison")
            medicine = st.text_input("Enter medicine name to compare prices")
            if medicine:
                cheapest = get_cheapest_brand(medicine)
                if cheapest:
                    st.write(f"**Cheapest option for {medicine}:**")
                    st.write(f"- Brand: {cheapest['brand']}")
                    st.write(f"- Price: ${cheapest['price']:.2f}")
                    st.write(f"- Stock: {cheapest['stock_quantity']} units")
                else:
                    st.error(f"No data found for medicine '{medicine}'")

        st.subheader("📊 Inventory Health Report")
        report = generate_inventory_report()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Items", report['total_items'])
        col2.metric("Low Stock Items", report['low_stock_count'])
        col3.metric("Expiring Items", report['expiring_count'])
        col4.metric("Total Value", f"${report['total_value']}")
