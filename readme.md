# 💳 Credit Scoring and Loan Eligibility System

<div align="center">

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

*A comprehensive Django REST API for customer registration, credit scoring, and intelligent loan management*

</div>

---

## 🌟 Overview

This project provides a robust Django REST API system for managing customer credit profiles and loan applications. Built with modern best practices, it features automated credit scoring, dynamic interest rate calculations, and comprehensive loan management capabilities. The entire system is containerized using Docker with PostgreSQL as the database backend.

## ✨ Key Features

- 🔐 **Customer Registration** - Seamless customer onboarding with automatic credit limit calculation
- 📊 **Smart Credit Scoring** - Intelligent credit evaluation based on payment history and financial behavior
- 🏦 **Loan Eligibility Assessment** - Real-time loan approval decisions with customizable criteria
- 💰 **Dynamic Interest Rates** - Automatic interest rate adjustments based on credit scores
- 📈 **Comprehensive Loan Management** - Full lifecycle loan tracking and management
- 📋 **Detailed Reporting** - Customer and loan analytics with complete transaction history
- 🐳 **Fully Dockerized** - One-command deployment with Docker Compose

## 🏗️ Architecture

### Database Models

#### Customer Model
```python
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_income = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(default=0)
```

#### Loan Model
```python
class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_payment = models.FloatField()
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
```

## 🚀 Quick Start

### Prerequisites

- 🐳 **Docker** (v20.0 or higher)
- 🐙 **Docker Compose** (v2.0 or higher)
- 🔧 **Git**

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/credit-loan-system.git
   cd credit-loan-system
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   POSTGRES_DB=credit_db
   POSTGRES_USER=shreyashgautam
   POSTGRES_PASSWORD=shreyash#123
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   ```

3. **Build and Run**
   ```bash
   docker-compose up --build
   ```

4. **Initialize Database**
   ```bash
   docker exec -it credit-web-1 python manage.py migrate
   ```

5. **Access the API**
   - API Base URL: `http://localhost:8000/api/`
   - Admin Panel: `http://localhost:8000/admin/`

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Endpoints Overview

| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/register` | POST | Register new customer | ✅ |
| `/check-eligibility` | POST | Check loan eligibility | ✅ |
| `/create-loan` | POST | Create new loan | ✅ |
| `/view-loan/<loan_id>` | GET | Get specific loan | ✅ |
| `/view-loans/<customer_id>` | GET | Get customer loans | ✅ |

---

### 1. 🆕 Register Customer

**Endpoint:** `POST /api/register`

**Request Body:**
```json
{
  "first_name": "Shreyash",
  "last_name": "Gautam",
  "age": 24,
  "phone_number": "9876543210",
  "monthly_income": 100000
}
```

**Success Response (201):**
```json
{
  "customer_id": 1,
  "first_name": "Shreyash",
  "last_name": "Gautam",
  "age": 24,
  "phone_number": "9876543210",
  "monthly_income": 100000,
  "approved_limit": 500000,
  "current_debt": 0
}
```

**Error Response (400):**
```json
{
  "error": "Phone number already exists"
}
```

---

### 2. 🔍 Check Loan Eligibility

**Endpoint:** `POST /api/check-eligibility`

**Request Body:**
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 12,
  "tenure": 12
}
```

**Success Response - Approved (200):**
```json
{
  "customer_id": 1,
  "loan_approved": true,
  "approved_amount": 200000,
  "tenure": 12,
  "interest_rate": 12.0,
  "monthly_installment": 17774.4
}
```

**Success Response - Rejected (200):**
```json
{
  "customer_id": 1,
  "loan_approved": false,
  "message": "Loan amount exceeds approved limit or customer's credit behavior is poor."
}
```

---

### 3. 🏦 Create Loan

**Endpoint:** `POST /api/create-loan`

**Request Body:**
```json
{
  "customer_id": 1,
  "loan_amount": 150000,
  "interest_rate": 10.5,
  "tenure": 24,
  "emis_paid_on_time": 12,
  "start_date": "2024-01-01"
}
```

**Success Response (201):**
```json
{
  "loan_id": 101,
  "customer_id": 1,
  "loan_amount": 150000,
  "tenure": 24,
  "interest_rate": 10.5,
  "monthly_payment": 6954.23,
  "emis_paid_on_time": 12,
  "start_date": "2024-01-01",
  "end_date": "2026-01-01"
}
```

---

### 4. 📄 View Single Loan

**Endpoint:** `GET /api/view-loan/<loan_id>`

**Example:** `GET /api/view-loan/101`

**Success Response (200):**
```json
{
  "loan_id": 101,
  "customer_id": 1,
  "loan_amount": 150000,
  "tenure": 24,
  "interest_rate": 10.5,
  "monthly_payment": 6954.23,
  "emis_paid_on_time": 12,
  "start_date": "2024-01-01",
  "end_date": "2026-01-01"
}
```

---

### 5. 📊 View Customer Loans

**Endpoint:** `GET /api/view-loans/<customer_id>`

**Example:** `GET /api/view-loans/1`

**Success Response (200):**
```json
[
  {
    "loan_id": 101,
    "customer_id": 1,
    "loan_amount": 150000,
    "tenure": 24,
    "interest_rate": 10.5,
    "monthly_payment": 6954.23,
    "emis_paid_on_time": 12,
    "start_date": "2024-01-01",
    "end_date": "2026-01-01"
  },
  {
    "loan_id": 102,
    "customer_id": 1,
    "loan_amount": 200000,
    "tenure": 36,
    "interest_rate": 11.0,
    "monthly_payment": 6550.0,
    "emis_paid_on_time": 36,
    "start_date": "2023-01-01",
    "end_date": "2026-01-01"
  }
]
```

## 🧪 Testing the API

### Using cURL

**Register a Customer:**
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "phone_number": "1234567890",
    "monthly_income": 75000
  }'
```

**Check Eligibility:**
```bash
curl -X POST http://localhost:8000/api/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 12,
    "tenure": 12
  }'
```

### Using Postman

1. Import the API collection
2. Set base URL to `http://localhost:8000/api`
3. Test each endpoint with the provided request examples

## 📁 Project Structure

```
credit-loan-system/
├── 📂 api/
│   ├── 📄 models.py          # Database models
│   ├── 📄 views.py           # API views and logic
│   ├── 📄 urls.py            # URL routing
│   ├── 📄 utils.py           # Utility functions
│   └── 📄 serializers.py     # DRF serializers
├── 📂 credit/
│   ├── 📄 settings.py        # Django settings
│   ├── 📄 urls.py            # Main URL config
│   └── 📄 wsgi.py            # WSGI application
├── 📄 manage.py              # Django management
├── 📄 Dockerfile             # Docker configuration
├── 📄 docker-compose.yml     # Docker Compose setup
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env                   # Environment variables
└── 📄 README.md              # Project documentation
```

## 📦 Dependencies

```txt
Django>=5.2
djangorestframework
psycopg2-binary
python-decouple
django-cors-headers
```

## 🛠️ Development

### Local Development Setup

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```


4. **Run Development Server:**
   ```bash
   python manage.py runserver
   ```

## 🚢 Deployment

### Docker Production Deployment

1. **Build Production Image:**
   ```bash
   docker build -t credit-system:latest .
   ```

2. **Deploy with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | ` ` |
| `POSTGRES_USER` | Database user | ` ` |
| `POSTGRES_PASSWORD` | Database password | ` ` |
| `POSTGRES_HOST` | Database host | ` ` |
| `POSTGRES_PORT` | Database port | ` ` |


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Shreyash Gautam**
- GitHub: [@shreyashgautam](https://github.com/shreyashgautam)
- LinkedIn: [Shreyash Gautam](https://linkedin.com/in/shreyash-gautam)

---

<div align="center">

**Built with ❤️ using Django & Docker**

*If you found this project helpful, please give it a ⭐*

</div>