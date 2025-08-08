# 📦 Unified Advanced Inventory Management System

Welcome to the **Unified Advanced Inventory Management System**, a powerful and intelligent clinic inventory solution built using **Streamlit**, **FastAPI**, **SQLite**, and **Gemini AI**. This system simplifies product tracking, batch handling, supplier management, purchase orders, analytics, and more — all in a sleek and interactive dashboard.

---

## ✨ Features

### 🏥 Clinic-Focused Modules
- **📦 Product Management**: Add, view, and categorize medicines and medical supplies.
- **📋 Batch Tracking**: Track expiry dates, costs, and quantities per batch.
- **🏢 Supplier Management**: Manage supplier details, contacts, and credit limits.
- **📜 Purchase Orders**: Create detailed POs with pricing, quantities, and supplier links.
- **📊 Analytics**: Real-time insights into inventory value, low stock, and expiring batches.
- **🚨 Alerts**: Automated alerts for low stock and upcoming expiries.
- **🤖 AI Assistant**: Ask inventory-related questions via a smart chatbot powered by **Gemini**.

### 🧠 Intelligence Built In
- 🔁 **Reorder Quantity Suggestions**: Based on past buying patterns.
- 📅 **Expiry Monitoring**: Identify soon-to-expire batches automatically.
- 💬 **Chat Assistant**: Natural language assistant trained on system logic.

---

## 🖥️ Tech Stack

| Layer            | Technology               |
|------------------|---------------------------|
| 💻 Frontend       | [Streamlit](https://streamlit.io) |
| ⚙️ Backend        | [FastAPI](https://fastapi.tiangolo.com/) |
| 🧠 AI Assistant   | [Gemini 1.5 Flash](https://deepmind.google/technologies/gemini/) |
| 🗃️ Database       | SQLite                   |
| 📈 Charts         | Plotly                   |
| 🔐 Auth           | SHA-256 + Local Storage  |

---

## 🚀 Getting Started

### ✅ Prerequisites

Make sure you have:
- Python 3.10+
- Internet access for AI
- Streamlit installed

### 📦 Setup

```bash
git clone https://github.com/Abhinav_freelancer/unified-inventory-app.git
cd unified-inventory-app

# Setup virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\activate  # On Windows

