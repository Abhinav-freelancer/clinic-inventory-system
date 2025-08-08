"""
Unified Advanced Inventory Management System
Combines all features from multiple files into one comprehensive application
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
import hashlib
import threading
import time
from datetime import datetime, timedelta
import uuid
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple
import numpy as np

# Database configuration
DB_PATH = "unified_inventory.db"

class UnifiedInventoryManager:
    """Complete inventory management system with all features integrated"""
    
    def __init__(self):
        self.init_database()
        self.notification_queue = []
        self.analytics_cache = {}
    
    def init_database(self):
        """Initialize all database tables"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                subcategory TEXT,
                unit_price REAL,
                cost_price REAL,
                reorder_level INTEGER,
                reorder_quantity INTEGER,
                max_stock_level INTEGER,
                supplier_id INTEGER,
                barcode TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inventory batches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                batch_number TEXT UNIQUE NOT NULL,
                quantity_received INTEGER,
                quantity_remaining INTEGER,
                expiry_date DATE,
                manufacturing_date DATE,
                cost_per_unit REAL,
                supplier_id INTEGER,
                received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT
            )
        ''')
        
        # Purchase orders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number TEXT UNIQUE NOT NULL,
                supplier_id INTEGER,
                order_date DATE,
                expected_delivery DATE,
                actual_delivery DATE,
                status TEXT DEFAULT 'pending',
                total_amount REAL,
                notes TEXT,
                priority TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Purchase order items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_id INTEGER,
                product_id INTEGER,
                quantity_ordered INTEGER,
                quantity_received INTEGER,
                unit_price REAL,
                total_price REAL,
                notes TEXT
            )
        ''')
        
        # Suppliers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                payment_terms TEXT,
                lead_time_days INTEGER,
                credit_limit REAL,
                tax_id TEXT
            )
        ''')
        
        # Inventory movements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                batch_id INTEGER,
                movement_type TEXT,
                quantity INTEGER,
                reference_type TEXT,
                reference_id TEXT,
                movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                user_id TEXT
            )
        ''')
        
        # Alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                product_id INTEGER,
                batch_id INTEGER,
                message TEXT,
                severity TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User Management
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                      (username, self.hash_password(password)))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'role': user[3]
            }
        return None
    
    def create_user(self, username: str, password: str, role: str = 'user') -> bool:
        """Create new user"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (username, self.hash_password(password), role))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    # Product Management
    def add_product(self, sku: str, name: str, description: str = "", 
                   category: str = "", unit_price: float = 0.0, 
                   cost_price: float = 0.0, reorder_level: int = 0,
                   reorder_quantity: int = 0, max_stock_level: int = 0,
                   supplier_id: int = None, barcode: str = None) -> int:
        """Add new product"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO products (sku, name, description, category, unit_price,
                                    cost_price, reorder_level, reorder_quantity,
                                    max_stock_level, supplier_id, barcode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (sku, name, description, category, unit_price, cost_price,
                  reorder_level, reorder_quantity, max_stock_level, supplier_id, barcode))
            
            product_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return product_id
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"Product with SKU {sku} already exists")
    
    def get_products(self) -> pd.DataFrame:
        """Get all products"""
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        return df
    
    # Batch Management
    def add_batch(self, product_id: int, batch_number: str, quantity_received: int,
                  expiry_date: str = None, cost_per_unit: float = 0.0,
                  location: str = "") -> int:
        """Add new inventory batch"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO inventory_batches (product_id, batch_number, quantity_received,
                                           quantity_remaining, expiry_date, cost_per_unit, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_id, batch_number, quantity_received, quantity_received,
                  expiry_date, cost_per_unit, location))
            
            batch_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return batch_id
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"Batch {batch_number} already exists")
    
    # Purchase Order Management
    def create_purchase_order(self, supplier_id: int, items: List[Dict]) -> str:
        """Create new purchase order"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        po_number = f"PO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Calculate total
        total_amount = sum(item['quantity'] * item['unit_price'] for item in items)
        
        cursor.execute('''
            INSERT INTO purchase_orders (po_number, supplier_id, order_date, total_amount)
            VALUES (?, ?, ?, ?)
        ''', (po_number, supplier_id, datetime.now().strftime('%Y-%m-%d'), total_amount))
        
        po_id = cursor.lastrowid
        
        # Add items
        for item in items:
            cursor.execute('''
                INSERT INTO purchase_order_items (po_id, product_id, quantity_ordered,
                                              unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (po_id, item['product_id'], item['quantity'],
                  item['unit_price'], item['quantity'] * item['unit_price']))
        
        conn.commit()
        conn.close()
        return po_number
    
    # Analytics
    def get_analytics(self) -> Dict:
        """Get comprehensive analytics"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Inventory value
        cursor.execute('''
            SELECT SUM(quantity_remaining * cost_per_unit)
            FROM inventory_batches
            WHERE status = 'active'
        ''')
        total_value = cursor.fetchone()[0] or 0
        
        # Product count
        cursor.execute('SELECT COUNT(*) FROM products')
        product_count = cursor.fetchone()[0]
        
        # Low stock items
        cursor.execute('''
            SELECT COUNT(*) FROM (
                SELECT p.id, SUM(ib.quantity_remaining) as stock
                FROM products p
                JOIN inventory_batches ib ON p.id = ib.product_id
                WHERE ib.status = 'active'
                GROUP BY p.id
                HAVING stock <= p.reorder_level
            )
        ''')
        low_stock = cursor.fetchone()[0]
        
        # Expiring items
        cursor.execute('''
            SELECT COUNT(*) FROM inventory_batches
            WHERE expiry_date <= date('now', '+30 days')
            AND status = 'active'
            AND quantity_remaining > 0
        ''')
        expiring = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_value': round(total_value, 2),
            'product_count': product_count,
            'low_stock': low_stock,
            'expiring': expiring
        }
    
    # Alerts
    def check_alerts(self):
        """Check and create alerts"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Low stock alerts
        cursor.execute('''
            SELECT p.id, p.name, p.reorder_level, SUM(ib.quantity_remaining)
            FROM products p
            JOIN inventory_batches ib ON p.id = ib.product_id
            WHERE ib.status = 'active'
            GROUP BY p.id
            HAVING SUM(ib.quantity_remaining) <= p.reorder_level
        ''')
        
        for row in cursor.fetchall():
            product_id, name, reorder_level, current = row
            self.create_alert(
                'LOW_STOCK',
                product_id=product_id,
                message=f"{name} is low on stock ({current} remaining, reorder at {reorder_level})"
            )
        
        conn.close()
    
    def create_alert(self, alert_type: str, product_id: int = None, message: str = ""):
        """Create new alert"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (alert_type, product_id, message, severity)
            VALUES (?, ?, ?, ?)
        ''', (alert_type, product_id, message, 'medium'))
        
        conn.commit()
        conn.close()

# Initialize manager
inventory_system = UnifiedInventoryManager()

# Streamlit App
class StreamlitApp:
    def __init__(self):
        self.manager = inventory_system
    
    def run(self):
        st.set_page_config(
            page_title="Unified Inventory Management System",
            page_icon="📦",
            layout="wide"
        )
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Go to",
            [
                "🏠 Dashboard",
                "📦 Products",
                "📦 Batches",
                "📋 Purchase Orders",
                "🏢 Suppliers",
                "📊 Analytics",
                "🚨 Alerts",
                "⚙️ Settings"
            ]
        )
        
        if page == "🏠 Dashboard":
            self.render_dashboard()
        elif page == "📦 Products":
            self.render_products()
        elif page == "📦 Batches":
            self.render_batches()
        elif page == "📋 Purchase Orders":
            self.render_purchase_orders()
        elif page == "📊 Analytics":
            self.render_analytics()
        elif page == "🚨 Alerts":
            self.render_alerts()
        elif page == "⚙️ Settings":
            self.render_settings()
        elif page == "🏢 Suppliers":
            self.render_suppliers()

    
    def render_dashboard(self):
        st.title("🏠 Dashboard")
        
        analytics = self.manager.get_analytics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Value", f"${analytics['total_value']:,}")
        with col2:
            st.metric("Products", analytics['product_count'])
        with col3:
            st.metric("Low Stock", analytics['low_stock'])
        with col4:
            st.metric("Expiring", analytics['expiring'])
    
    def render_products(self):
        st.title("📦 Product Management")
        
        tab1, tab2 = st.tabs(["View Products", "Add Product"])
        
        with tab1:
            products = self.manager.get_products()
            st.dataframe(products)
        
        with tab2:
            with st.form("add_product"):
                sku = st.text_input("SKU")
                name = st.text_input("Name")
                description = st.text_area("Description")
                category = st.text_input("Category")
                unit_price = st.number_input("Unit Price", min_value=0.0)
                cost_price = st.number_input("Cost Price", min_value=0.0)
                reorder_level = st.number_input("Reorder Level", min_value=0)
                
                if st.form_submit_button("Add Product"):
                    try:
                        product_id = self.manager.add_product(
                            sku, name, description, category, unit_price, cost_price, reorder_level
                        )
                        st.success(f"Product added with ID: {product_id}")
                    except Exception as e:
                        st.error(str(e))
    
    def render_batches(self):
        st.title("📦 Batch Management")
        
        products = self.manager.get_products()
        
        if products.empty:
            st.warning("No products found. Please add products first.")
            return
            
        # Add batch form
        with st.form("add_batch"):
            product_names = products['name'].tolist()
            selected_product = st.selectbox("Product", product_names)
            
            # Safely get product ID
            product_row = products[products['name'] == selected_product]
            if not product_row.empty:
                product_id = int(product_row['id'].iloc[0])
            else:
                st.error("Product not found")
                return
            
            batch_number = st.text_input("Batch Number")
            quantity = st.number_input("Quantity", min_value=1)
            cost_per_unit = st.number_input("Cost per Unit", min_value=0.0)
            
            if st.form_submit_button("Add Batch"):
                try:
                    batch_id = self.manager.add_batch(product_id, batch_number, quantity, cost_per_unit=cost_per_unit)
                    st.success(f"Batch added with ID: {batch_id}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    
    def render_purchase_orders(self):
        st.title("📋 Purchase Orders")

        st.subheader("➕ Create New Purchase Order")

    # Load products and suppliers
        products_df = self.manager.get_products()
        conn = sqlite3.connect(DB_PATH)
        suppliers_df = pd.read_sql_query("SELECT id, name FROM suppliers", conn)
        conn.close()

        if products_df.empty or suppliers_df.empty:
            st.warning("⚠️ You need both suppliers and products to create a purchase order.")
            return

        supplier_names = suppliers_df['name'].tolist()
        selected_supplier = st.selectbox("Select Supplier", supplier_names)

        selected_supplier_id = int(suppliers_df[suppliers_df['name'] == selected_supplier]['id'].iloc[0])

        st.markdown("#### 🧾 Order Items")
        order_items = []
        with st.form("purchase_order_form"):
            num_items = st.number_input("Number of different products", min_value=1, max_value=10, step=1)

            for i in range(num_items):
                st.markdown(f"**Item {i+1}**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    prod_name = st.selectbox(f"Product {i+1}", products_df['name'].tolist(), key=f"product_{i}")
                with col2:
                    quantity = st.number_input(f"Quantity {i+1}", min_value=1, key=f"qty_{i}")
                with col3:
                    unit_price = st.number_input(f"Unit Price {i+1}", min_value=0.01, key=f"price_{i}")

                prod_id = int(products_df[products_df['name'] == prod_name]['id'].iloc[0])
                order_items.append({
                    "product_id": prod_id,
                    "quantity": quantity,
                    "unit_price": unit_price
                })

            submitted = st.form_submit_button("Create Purchase Order")
            if submitted:
                po_number = self.manager.create_purchase_order(selected_supplier_id, order_items)
                st.success(f"✅ Purchase Order `{po_number}` created successfully!")

        st.divider()

        st.subheader("📜 Existing Purchase Orders")
        conn = sqlite3.connect(DB_PATH)
        po_df = pd.read_sql_query('''
            SELECT po.id, po.po_number, s.name as supplier, po.order_date, po.status, po.total_amount
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            ORDER BY po.created_at DESC
        ''', conn)
        conn.close()

        if not po_df.empty:
            st.dataframe(po_df)
        else:
            st.info("No purchase orders found.")

    
    def render_analytics(self):
        st.title("📊 Analytics")
        
        analytics = self.manager.get_analytics()
        
        st.write("### Key Metrics")
        st.json(analytics)
    
    def render_alerts(self):
        st.title("🚨 Alerts")
        
        self.manager.check_alerts()
        st.success("Alerts checked")
    
    def render_settings(self):
        st.title("⚙️ Settings")
        st.write("Administrative settings and database tools")

        st.markdown("### 🔄 Reset & Maintenance Tools")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🧹 Clear All Alerts"):
                conn = sqlite3.connect(DB_PATH)
                conn.execute("DELETE FROM alerts")
                conn.commit()
                conn.close()
                st.success("✅ All alerts cleared.")

            if st.button("🧪 Delete All Test Data"):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                tables = [
                    "products", "inventory_batches", "purchase_orders",
                    "purchase_order_items", "suppliers", "alerts"
                ]
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                conn.commit()
                conn.close()
                st.success("✅ Test data deleted.")

        with col2:
            with open(DB_PATH, "rb") as f:
                st.download_button("⬇️ Download Backup (DB File)", f, file_name="unified_inventory.db")

            if st.button("🗑️ Delete Entire Database"):
                import os
                try:
                    os.remove(DB_PATH)
                    st.warning("⚠️ Database deleted. Please restart the app to reinitialize the schema.")
                except FileNotFoundError:
                    st.error("Database file not found.")
                except Exception as e:
                    st.error(f"Error deleting database: {e}")

    
    def render_suppliers(self):
        st.title("🏢 Supplier Management")

        tab1, tab2 = st.tabs(["📋 View Suppliers", "➕ Add Supplier"])

    # === View All Suppliers ===
        with tab1:
            conn = sqlite3.connect(DB_PATH)
            suppliers_df = pd.read_sql_query("SELECT * FROM suppliers", conn)
            conn.close()

            if not suppliers_df.empty:
                st.dataframe(suppliers_df)
            else:
                st.info("No suppliers found. Use the tab above to add one.")

    # === Add New Supplier ===
        with tab2:
            with st.form("add_supplier_form"):
                name = st.text_input("Supplier Name")
                contact_person = st.text_input("Contact Person")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                address = st.text_area("Address")
                city = st.text_input("City")
                state = st.text_input("State")
                zip_code = st.text_input("ZIP Code")
                country = st.text_input("Country")
                payment_terms = st.text_input("Payment Terms (e.g., Net 30)")
                lead_time_days = st.number_input("Lead Time (days)", min_value=0)
                credit_limit = st.number_input("Credit Limit", min_value=0.0)
                tax_id = st.text_input("Tax ID")

                if st.form_submit_button("Add Supplier"):
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO suppliers (
                                name, contact_person, email, phone, address,
                                city, state, zip_code, country, payment_terms,
                                lead_time_days, credit_limit, tax_id
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            name, contact_person, email, phone, address,
                            city, state, zip_code, country, payment_terms,
                            lead_time_days, credit_limit, tax_id
                        ))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Supplier '{name}' added successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add supplier: {e}")


# Main execution
if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
