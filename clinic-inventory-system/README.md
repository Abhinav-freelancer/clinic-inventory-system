# Clinic Inventory Management System

A comprehensive backend system for managing medical supplies inventory in clinics and hospitals.

## 🎯 Features

- **User Management**: Role-based access control (Admin, Staff)
- **Inventory Management**: Track medical supplies with real-time stock updates
- **Usage Tracking**: Record item usage with detailed logs
- **Alerts & Notifications**: Low stock and expiry date warnings
- **Reports & Analytics**: Usage reports and restocking suggestions
- **Barcode Support**: Simulate barcode scanning for inventory management
- **RESTful API**: Well-documented endpoints with Swagger UI

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **ORM**: SQLAlchemy
- **Documentation**: Swagger/OpenAPI

## 📁 Project Structure

```
clinic-inventory-system/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── items.py
│   │       │   ├── usage.py
│   │       │   ├── alerts.py
│   │       │   └── reports.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── item.py
│   │   └── usage_record.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── item.py
│   │   └── usage_record.py
│   └── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd clinic-inventory-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Create database**
```bash
# Create PostgreSQL database named 'clinic_inventory'
createdb clinic_inventory
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 API Documentation

Once the application is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Authentication

The system uses JWT tokens for authentication. Users can register and login to receive access tokens.

### User Roles
- **Admin**: Full access to all features
- **Staff**: Limited access based on permissions

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info

### Items (Inventory)
- `GET /api/v1/items` - List all items
- `POST /api/v1/items` - Create new item
- `GET /api/v1/items/{id}` - Get item details
- `PUT /api/v1/items/{id}` - Update item
- `DELETE /api/v1/items/{id}` - Delete item
- `GET /api/v1/items/low-stock` - Get low stock items
- `GET /api/v1/items/expiring-soon` - Get expiring items

### Usage Tracking
- `POST /api/v1/usage` - Record item usage
- `GET /api/v1/usage` - List usage records
- `GET /api/v1/usage/item/{item_id}` - Get usage for specific item

### Alerts
- `GET /api/v1/alerts` - Get all alerts
- `GET /api/v1/alerts/low-stock` - Get low stock alerts
- `GET /api/v1/alerts/expiry` - Get expiry alerts

### Reports
- `GET /api/v1/reports/usage` - Get usage reports
- `GET /api/v1/reports/stock` - Get stock reports
- `GET /api/v1/reports/suggestions` - Get restocking suggestions

## 🧪 Testing

Run tests with pytest:
```bash
pytest
```

## 🚀 Deployment

### Using Docker (Optional)
```bash
docker-compose up --build
```

### Using Render/Vercel
1. Push code to GitHub
2. Connect repository to Render/Vercel
3. Set environment variables
4. Deploy

## 📊 Sample Data

You can use the following sample data to test the system:

### Users
```json
{
  "username": "admin",
  "email": "admin@clinic.com",
  "password": "admin123",
  "role": "admin"
}
```

### Items
```json
{
  "name": "Paracetamol 500mg",
  "type": "drug",
  "stock_quantity": 100,
  "unit": "tablets",
  "expiry_date": "2024-12-31",
  "reorder_threshold": 20,
  "barcode": "DRUG-001"
}
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiry time
- `SMTP_*`: Email configuration (optional)
- `TWILIO_*`: SMS configuration (optional)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, email support@clinic-inventory.com or create an issue in the repository.
