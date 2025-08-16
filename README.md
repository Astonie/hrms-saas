# HRMS-SAAS: Enterprise Multi-Tenant Human Resources Management System

## 🏗️ Architecture Overview

This is a comprehensive, enterprise-grade HRMS built with modern technologies and best practices for multi-tenant SaaS applications.

### Multi-Tenant Strategy: Schema-Based Isolation

We've chosen **schema-based multi-tenancy** for maximum security and data isolation:

- **Complete Data Isolation**: Each tenant operates in their own PostgreSQL schema
- **Security**: Zero risk of cross-tenant data leakage
- **Scalability**: Tenant-specific optimizations and indexes
- **Compliance**: Ideal for regulatory requirements (GDPR, SOX, HIPAA)
- **Performance**: Dedicated resources per tenant

### Tech Stack

- **Backend**: FastAPI (Python 3.10+) with async SQLAlchemy
- **Database**: PostgreSQL with schema-based multi-tenancy
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Authentication**: JWT + OAuth2 + RBAC
- **Deployment**: Docker + Docker Compose
- **Testing**: pytest + React Testing Library
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Development Setup

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd HRMS-SAAS
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Services**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

5. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the Application**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## 🏛️ Project Structure

```
HRMS-SAAS/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities
│   └── tests/              # Frontend tests
├── docker-compose.yml       # Development services
└── docs/                    # Documentation
```

## 🔐 Multi-Tenant Architecture

### Tenant Management

- **Tenant Creation**: Admin creates tenants with unique subdomains/domains
- **Schema Isolation**: Each tenant gets dedicated PostgreSQL schema
- **User Management**: Tenant-specific users with role-based access
- **Data Segregation**: Complete separation of HR data, documents, and configurations

### Authentication Flow

1. User authenticates with tenant identifier
2. System validates tenant and user credentials
3. JWT token includes tenant context
4. All subsequent requests are scoped to the tenant's schema

## 📊 Core HR Features

- **Employee Management**: CRUD operations, departments, job titles
- **Leave Management**: Request/approval workflow, calendar integration
- **Payroll**: Salary management, deductions, history
- **Performance**: Evaluations, feedback, goal tracking
- **Recruitment**: Job posts, applications, interview scheduling
- **Attendance**: Time tracking, biometric integration
- **Documents**: Contract management, file uploads

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deployment

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Staging
```bash
docker-compose -f docker-compose.staging.yml up -d
```

## 📈 Monitoring & Logging

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Endpoint monitoring for all services
- **Metrics**: Prometheus metrics for performance tracking
- **Error Tracking**: Sentry integration for production monitoring

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth with refresh
- **RBAC**: Role-based access control per tenant
- **Data Encryption**: At-rest and in-transit encryption
- **Audit Logging**: Complete audit trail for compliance
- **Rate Limiting**: API protection against abuse
- **CORS**: Configurable cross-origin policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the [documentation](docs/)
- Review the [API documentation](http://localhost:8000/docs)
