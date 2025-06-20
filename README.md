# Pharmacy Management System - Clean Version

A clean, modern Flask-based pharmacy management system with PostgreSQL integration.

## 🚀 Features

- **Clean Architecture**: Simplified from complex DDD patterns to maintainable code
- **PostgreSQL Integration**: Optimized for PostgreSQL with proper connection pooling
- **Product Management**: Complete CRUD operations for pharmaceutical products
- **RESTful API**: Clean API endpoints with proper error handling
- **Environment Configuration**: Flexible configuration via environment variables
- **Database Migrations**: Flask-Migrate integration for schema management
- **Docker Support**: Easy deployment with Docker and Docker Compose

## 📋 Requirements

- Python 3.8+ (or Docker)
- PostgreSQL 12+ (or use existing hosted database)
- Docker & Docker Compose (for containerized deployment)
- Redis (optional, for future caching)

## ��️ Installation

### Option 1: Docker (Recommended - Simplest)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd phserver
```

2. **Create environment file:**
```bash
cp env.example .env
# Edit .env with your configuration (database URL, secret keys, etc.)
```

3. **Start with Docker:**
```bash
# Quick start (creates .env if missing)
chmod +x start.sh
./start.sh

# Or manually
docker-compose up --build
```

The application will be available at:
- **Development**: http://localhost:5000
- **Health check**: http://localhost:5000/health

### Option 2: Manual Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd phserver
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/pharmacy_dev

# Server
PORT=5000
HOST=0.0.0.0
```

### 3. Database Setup

#### Option A: Using Migrations (Recommended)
```bash
python manage.py init-db
```

#### Option B: Direct Table Creation
```bash
python manage.py create-tables
```

#### Add Sample Data
```bash
python manage.py seed-data
```

## 🚦 Running the Application

### Development
```bash
python run.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

## 📚 API Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/products/` | Create a new product |
| GET | `/api/v1/products/{id}` | Get product by ID |
| PUT | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Delete product (soft delete) |
| GET | `/api/v1/products/list` | List products with pagination |
| GET | `/api/v1/products/search` | Search products |
| GET | `/api/v1/products/category/{id}` | Get products by category |
| POST | `/api/v1/products/bulk` | Create multiple products |

### Example Requests

#### Create Product
```json
POST /api/v1/products/
{
    "name": "Paracetamol 500mg",
    "description": "Pain relief medication",
    "brand": "Acme Pharma",
    "dosage_form": "Tablet",
    "strength": "500mg",
    "package": "Box of 20"
}
```

#### List Products
```
GET /api/v1/products/list?page=1&per_page=20&search=paracetamol
```

#### Search Products
```
GET /api/v1/products/search?q=paracetamol&page=1&per_page=10
```

## 🗄️ Database Management

### Available Commands

```bash
# Initialize database with migrations
python manage.py init-db

# Create tables directly
python manage.py create-tables

# Drop all tables
python manage.py drop-tables

# Reset database (drop and recreate)
python manage.py reset-db

# Apply migrations
python manage.py upgrade

# Create new migration
python manage.py migrate "Add new column"

# Seed sample data
python manage.py seed-data
```

### Database Schema

#### Products Table
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    category_id UUID,
    dosage_form VARCHAR(50),
    strength VARCHAR(50),
    package VARCHAR(50),
    image_url VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `development` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | Flask secret key | Required |
| `JWT_SECRET_KEY` | JWT secret key | Required |
| `PORT` | Server port | `5000` |
| `HOST` | Server host | `0.0.0.0` |
| `DEFAULT_PAGE_SIZE` | Default pagination size | `20` |
| `MAX_PAGE_SIZE` | Maximum pagination size | `100` |

### Database Configuration

The application supports multiple database configurations:

- **Development**: PostgreSQL with query logging
- **Testing**: SQLite in-memory for fast tests
- **Production**: PostgreSQL with connection pooling

## �� Testing

```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📈 Performance

### PostgreSQL Optimizations

- Connection pooling with configurable pool size
- Pre-ping for connection health checks
- Proper indexing on frequently queried columns
- Query optimization with SQLAlchemy ORM

### Caching (Future)

- Redis integration ready for session storage
- Query result caching capability
- API response caching

## 🔒 Security

- JWT token authentication ready
- Password hashing with bcrypt
- CORS configuration
- SQL injection prevention via ORM
- Input validation and sanitization

## 📁 Project Structure

```
phserver/
├── app/
│   ├── __init__.py                 # App factory
│   ├── config.py                   # Configuration classes
│   ├── dataBase.py                 # Database setup
│   ├── extensions.py               # Flask extensions
│   ├── services/
│   │   └── product_service/
│   │       ├── service.py          # Clean product service
│   │       ├── infrastructure/
│   │       │   └── persistence/
│   │       │       └── models/
│   │       │           └── product_model.py  # Product model
│   │       └── domain/
│   │           └── enums/
│   │               └── product_status.py
│   └── apis/
│       └── product/
│           └── routes.py           # Clean API routes
├── run.py                          # Application entry point
├── manage.py                       # Database management
├── requirements.txt                # Dependencies
├── environment.example             # Environment template
└── README.md                       # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check your `DATABASE_URL` in `.env`
   - Ensure PostgreSQL is running
   - Verify credentials and database exists

2. **Migration Issues**
   - Run `python manage.py reset-db` for fresh start
   - Check migration files in `migrations/` folder

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path and virtual environment

### Logs

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

## 🔮 Roadmap

- [ ] Authentication & Authorization system
- [ ] Inventory management integration
- [ ] Order management system
- [ ] Category management
- [ ] Invoice generation
- [ ] Reporting & Analytics
- [ ] API documentation with Swagger
- [ ] Docker containerization
- [ ] CI/CD pipeline 