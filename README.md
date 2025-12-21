# MISoft - Manufacturing & Accounting Software

A comprehensive web-based ERP system for manufacturing and accounting operations, built with Django REST Framework and React.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.14+** installed
- **Node.js 22+** and npm installed
- **PostgreSQL 18** running on `localhost:5432`
- **Git** for version control

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd MISoft
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv_new

# Activate virtual environment (Windows)
.\venv_new\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create database (if not exists)
python create_database.py

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Environment Configuration

#### Backend `.env` (already configured)

The backend `.env` file is located at `backend/.env`. For new team members, copy `backend/.env.example` to `backend/.env` and update with your credentials.

#### Frontend `.env` (already configured)

The frontend `.env` file is located at `frontend/.env`. For new team members, copy `frontend/.env.example` to `frontend/.env`.

> [!IMPORTANT]
> Never commit `.env` files to Git. They are excluded via `.gitignore`.

---

## 🎯 Running the Application

### Option 1: Using the Startup Script (Recommended)

```bash
# From the project root directory
.\start.ps1
```

This will:
- ✅ Check PostgreSQL service status
- ✅ Start Django backend server (http://localhost:8000)
- ✅ Start Vite frontend server (http://localhost:5173)
- ✅ Open both in separate terminal windows

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
.\venv_new\Scripts\Activate.ps1
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Access Points

- **Frontend Application:** http://localhost:5173
- **Backend API:** http://localhost:8000/api
- **Django Admin:** http://localhost:8000/admin

---

## 📁 Project Structure

```
MISoft/
├── backend/
│   ├── accounting/          # Accounting module (vouchers, accounts, etc.)
│   ├── accounts/            # User authentication & management
│   ├── config/              # Django settings & configuration
│   ├── manufacturing/       # Manufacturing operations
│   ├── partners/            # Customer & supplier management
│   ├── products/            # Product catalog
│   ├── .env                 # Environment variables (DO NOT COMMIT)
│   ├── .env.example         # Template for environment setup
│   ├── .gitignore           # Git ignore rules
│   ├── requirements.txt     # Python dependencies
│   ├── manage.py            # Django management script
│   ├── create_database.py   # Database creation utility
│   └── verify_vouchers_api.py  # API testing script
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   │   └── api.js       # Axios configuration
│   │   ├── App.jsx          # Main application component
│   │   └── main.jsx         # Application entry point
│   ├── .env                 # Frontend environment variables
│   ├── .env.example         # Template for frontend setup
│   ├── .gitignore           # Git ignore rules
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
│
├── start.ps1                # Application launcher script
└── README.md                # This file
```

---

## 🔐 Security Features

### ✅ Environment Variables
- All sensitive credentials stored in `.env` files
- `.env` files excluded from Git via `.gitignore`
- `.env.example` templates provided for team setup

### ✅ Code Hardening
- No hardcoded URLs or credentials
- Environment-based configuration throughout
- Parameterized database queries for security

### ✅ Authentication
- JWT-based authentication with token refresh
- Token blacklisting on logout
- Secure password validation

---

## 🛠️ API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - User registration
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/user/` - Get current user

### Accounting
- `GET/POST /api/accounting/vouchers-v2/` - Voucher management
- `POST /api/accounting/vouchers-v2/{id}/post/` - Post voucher
- `GET /api/accounting/accounts-v2/hierarchy/` - Account hierarchy

### Partners
- `GET/POST /api/partners/customers/` - Customer management
- `GET/POST /api/partners/suppliers/` - Supplier management

### Products
- `GET/POST /api/products/` - Product catalog

### Manufacturing
- `GET/POST /api/manufacturing/work-orders/` - Work order management

> [!NOTE]
> All API endpoints require Bearer token authentication except login and register.

---

## 🧪 Testing

### Backend API Testing

Use the provided test script:

```bash
cd backend
.\venv_new\Scripts\Activate.ps1
python verify_vouchers_api.py
```

---

## 🔧 Development Workflow

### Making Changes

1. **Backend Changes:**
   - Activate virtual environment: `.\venv_new\Scripts\Activate.ps1`
   - Make your changes
   - Create migrations if models changed: `python manage.py makemigrations`
   - Apply migrations: `python manage.py migrate`

2. **Frontend Changes:**
   - Make your changes in `src/`
   - Vite will hot-reload automatically

### Adding New Dependencies

**Backend:**
```bash
pip install package-name
pip freeze > requirements.txt
```

**Frontend:**
```bash
npm install package-name
```

---

## 🐛 Troubleshooting

### PostgreSQL Not Running

```bash
# Check service status
Get-Service -Name "*postgres*"

# Start service if stopped
Start-Service postgresql-x64-18
```

### Port Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Virtual Environment Issues

```bash
# Delete old venv and create new one
Remove-Item -Recurse -Force venv_new
python -m venv venv_new
.\venv_new\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in backend `.env`
- [ ] Generate new `SECRET_KEY` for production
- [ ] Update `ALLOWED_HOSTS` with production domain
- [ ] Update `CORS_ALLOWED_ORIGINS` with production frontend URL
- [ ] Use strong database password
- [ ] Set up SSL/TLS certificates
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure production web server (Gunicorn, Nginx)
- [ ] Rotate API keys if repository was public

---

## 👥 Team Setup

For new team members:

1. Clone the repository
2. Copy `.env.example` to `.env` in both `backend/` and `frontend/`
3. Update `.env` files with your local configuration
4. Follow the installation steps above
5. Run `.\start.ps1` to launch the application

---

## 📝 License

© 2025 MI Industries. All rights reserved.

---

## ✨ Features

### Current Features
- ✅ User authentication & authorization
- ✅ Chart of accounts management
- ✅ Voucher creation and posting
- ✅ Customer & supplier management
- ✅ Product catalog
- ✅ Manufacturing work orders
- ✅ Responsive UI with glassmorphism design
- ✅ JWT-based API security
- ✅ Environment-based configuration

### Upcoming Features
- 🔄 Advanced analytics dashboard
- 🔄 Bulk import functionality
- 🔄 Report generation
- 🔄 Multi-currency support
- 🔄 Inventory management
- 🔄 Production planning

---

**Built with ❤️ using Django, React, and PostgreSQL**
