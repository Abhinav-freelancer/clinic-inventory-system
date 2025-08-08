📦 Unified Advanced Inventory Management System
A powerful, intuitive, and intelligent inventory management system tailored for clinics and healthcare environments, built with Streamlit and FastAPI. This application consolidates product, batch, supplier, purchase order, and analytics management into a single, easy-to-use interface — with an integrated AI assistant to guide your decisions.

🚀 Features
🔐 User Authentication
Secure login/signup system with password hashing.

Session-based authentication to manage users safely.

🏠 Dashboard
Displays key inventory metrics:

📦 Total Inventory Value

📈 Number of Products

⚠️ Low Stock Alerts

⏰ Expiring Stock Summary

📦 Product Management
Add and manage all types of medical or inventory items.

Track:

SKU, Barcode

Name, Description

Category/Subcategory

Unit Price, Cost Price

Reorder Level, Max Stock Level

Supplier Association

📦 Batch Management
Associate stock with batches to track:

Batch Number

Quantity Received & Remaining

Expiry & Manufacturing Date

Cost per Unit

Storage Location

✅ AI-powered reorder quantity suggestions based on historical patterns.

Expiry tracking ensures proactive replacement.

📋 Purchase Orders
Create detailed purchase orders with:

Supplier linkage

Multiple line items

Quantity and unit cost

Auto-generated PO numbers

Track all POs with status, dates, and delivery records.

🏢 Supplier Management
Maintain a complete database of your vendors:

Contact details, Tax ID

Payment terms, Lead time

Credit limits

Add, view, and manage supplier info seamlessly.

📊 Analytics
View core metrics via charts or raw JSON:

Inventory valuation

Expiry analysis

Reorder forecasting

Low stock visibility

🚨 Alert System
Monitors your stock and:

Generates alerts for low inventory

Warns of items expiring soon

Easy toggle to clear all alerts.

🤖 Smart AI Assistant (Gemini-Powered)
Natural language assistant powered by Google Gemini.

Ask questions like:

“What items are low on stock?”

“Which items are about to expire?”

“How many gloves should I order?”

Integrates with internal APIs to provide actionable insights.

⚙️ Settings & Utilities
Full DB backup and download

Reset tools:

Clear alerts

Delete all test data

Wipe the database entirely

Safe and admin-oriented features for full control.

🛠️ Tech Stack
Frontend: Streamlit

Backend: SQLite

AI Integration: Google Gemini via google-generativeai

Data Handling: pandas, plotly

Language: Python 3.11+

Authentication: JSON file-based with SHA256 hashing

🔧 Getting Started
bash
Copy
Edit
# Clone the repo
git clone https://github.com/your-repo/unified-inventory.git
cd unified-inventory

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run unified_inventory_app.py
⚠️ Make sure to set your Gemini API key in the script:

python
Copy
Edit
genai.configure(api_key="YOUR_API_KEY")
📂 Project Structure
pgsql
Copy
Edit
📁 unified_inventory_app.py
📁 unified_inventory.db
📁 users.json
📁 README.md
🧠 Future Scope
Multi-user role-based access

Inventory export to Excel/PDF

REST API for external integrations

Dashboard charts and trends

Notification emails for alerts
