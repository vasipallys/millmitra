# Rice Mill Management System

A comprehensive, AI-powered Enterprise Resource Planning (ERP) system designed specifically for rice mill operations, featuring intelligent automation, predictive analytics, and complete business management capabilities.

## 🌾 Overview

The Rice Mill Management System is a modern, scalable ERP solution that integrates artificial intelligence throughout the rice milling process - from farmer procurement to final product delivery. The system provides real-time insights, automated quality control, predictive maintenance, and intelligent decision-making capabilities.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │  AI Services    │
│  React + Vite   │◄──►│  Flask + SQLAlchemy │◄──►│ FastAPI + ML    │
│  Material-UI    │    │  JWT Auth       │    │  LangChain      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Database      │              │
         └──────────────►│  PostgreSQL     │◄─────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │     Redis       │
                        │  Cache + Session│
                        └─────────────────┘
```

### Technology Stack

- **Frontend**: React 18 + Vite 5 + Material-UI 5
- **Backend**: Python Flask 3.0.3 + SQLAlchemy
- **AI Services**: FastAPI + Google Gemini + LangChain
- **Database**: PostgreSQL (primary), MySQL (supported)
- **Caching/Session**: Redis
- **Authentication**: JWT + Role-based Access Control
- **Deployment**: Docker, Docker Compose

## 📋 Core Modules

### 1. 👥 User Management & Authentication
- **JWT-based authentication** with role-based access control
- **Multi-role system**: Super Admin, Admin, Manager, Operator, Viewer
- **Permission management** with granular access control
- **User activity tracking** and audit logs
- **Password policies** and security features

**Key Features:**
- Secure login/logout with token refresh
- Role-based dashboard customization
- User profile management
- Activity monitoring

### 2. 🌾 Farmer Management
- **Farmer registration** and profile management
- **Contract management** with terms and conditions
- **Procurement tracking** from farm to mill
- **Payment processing** with multiple methods
- **AI-powered farmer scoring** and risk assessment

**Key Features:**
- Digital contracts with e-signatures
- Automated payment calculations
- Farmer performance analytics
- Procurement scheduling optimization
- Quality-based pricing algorithms

### 3. 📦 Inventory Management
- **Real-time stock tracking** across multiple warehouses
- **Automated stock movements** with barcode/QR scanning
- **Batch tracking** from raw material to finished goods
- **AI-powered demand forecasting** and reorder optimization
- **Expiry management** and quality degradation tracking

**Key Features:**
- Multi-warehouse inventory control
- Automated low-stock alerts
- FIFO/LIFO inventory valuation
- Predictive analytics for demand planning
- Integration with production planning

### 4. 🏭 Production Management
- **Batch production tracking** with real-time monitoring
- **Quality control** at each production stage
- **Equipment monitoring** and predictive maintenance
- **AI-optimized production scheduling** and resource allocation
- **Yield optimization** and waste reduction

**Key Features:**
- Real-time production dashboards
- Quality checkpoints and testing
- Equipment efficiency monitoring
- Production cost analysis
- Automated reporting and alerts

### 5. 💰 Sales Management
- **Customer relationship management** (CRM)
- **Order processing** and fulfillment tracking
- **Dynamic pricing** based on market conditions
- **AI-powered sales forecasting** and trend analysis
- **Customer segmentation** and targeted marketing

**Key Features:**
- Multi-channel sales support
- Automated invoicing and billing
- Customer credit management
- Sales performance analytics
- Market price intelligence

### 6. 💳 Finance Management
- **Comprehensive accounting** with double-entry bookkeeping
- **Automated invoice generation** and payment tracking
- **Financial reporting** and analytics
- **AI-powered financial forecasting** and risk assessment
- **Tax compliance** and regulatory reporting

**Key Features:**
- Real-time financial dashboards
- Automated reconciliation
- Cash flow management
- Profitability analysis
- Regulatory compliance reporting

### 7. 🔗 Supply Chain Management
- **Supplier management** and evaluation
- **Purchase order automation** and tracking
- **Vendor performance monitoring** and scoring
- **AI-optimized procurement** planning and sourcing
- **Supply chain risk assessment** and mitigation

**Key Features:**
- Automated purchase workflows
- Supplier performance analytics
- Cost optimization algorithms
- Supply chain visibility
- Risk management tools

### 8. 🚛 Logistics & Transportation
- **Fleet management** and vehicle tracking
- **Route optimization** using AI algorithms
- **Shipment tracking** and delivery management
- **Driver performance monitoring** and safety tracking
- **Fuel optimization** and cost reduction

**Key Features:**
- Real-time GPS tracking
- Automated route planning
- Delivery confirmation system
- Fleet maintenance scheduling
- Cost per delivery analytics

### 9. ⚖️ Compliance & Regulatory
- **Regulatory framework management** and tracking
- **Automated compliance assessments** and reporting
- **Document management** with version control
- **AI-powered risk assessment** and mitigation
- **Audit trail** and evidence management

**Key Features:**
- Compliance dashboard and alerts
- Automated regulatory reporting
- Document lifecycle management
- Risk scoring and mitigation
- Audit preparation tools

### 10. 🔬 Quality Management
- **Multi-stage quality testing** and inspection
- **AI-powered quality assessment** using computer vision
- **Quality standards compliance** and certification
- **Defect tracking** and root cause analysis
- **Continuous improvement** programs

**Key Features:**
- Automated quality testing
- Visual inspection using AI
- Quality trend analysis
- Corrective action tracking
- Certification management

## 🤖 AI-Powered Features

### Intelligent Analytics
- **Predictive maintenance** for equipment
- **Demand forecasting** for inventory planning
- **Quality prediction** using historical data
- **Financial forecasting** and risk assessment
- **Market price prediction** and optimization

### Computer Vision
- **Grain quality assessment** using image analysis
- **Defect detection** in production
- **Inventory counting** automation
- **Safety monitoring** in production areas

### Natural Language Processing
- **Voice commands** for mill operations
- **Automated report generation** in natural language
- **Document analysis** and information extraction
- **Chatbot support** for common queries

### Machine Learning Models
- **Customer segmentation** and behavior analysis
- **Fraud detection** in transactions
- **Optimal pricing** strategies
- **Production optimization** algorithms

## 🔄 Business Process Flows

### Login Process
1. User accesses login page
2. Enters credentials (username/email and password)
3. System validates credentials against database
4. If valid, generates JWT token
5. Token stored in Redis session
6. User redirected to role-based dashboard

### Procurement Process
1. Farmer registration and profile creation
2. Contract negotiation and digital signing
3. Procurement scheduling
4. Quality assessment at collection
5. Payment processing
6. Inventory update

### Production Process
1. Raw material allocation
2. Batch creation
3. Production scheduling
4. Real-time monitoring
5. Quality checkpoints
6. Finished goods inventory update

### Sales Process
1. Customer order placement
2. Order validation and confirmation
3. Inventory allocation
4. Production scheduling (if needed)
5. Shipment and delivery
6. Invoice generation and payment

## 🚀 Setup and Installation

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 13+**
- **Redis 7+**
- **Docker & Docker Compose** (recommended for development)

### Quick Start with Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd millmitra
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Initialize the database**
```bash
docker-compose exec backend python migrate_db.py
```

5. **Access the application**
- Frontend: http://localhost:3000 (if 3000 is busy, Vite uses the next free port and prints the URL)
- Backend API: http://localhost:5000
- AI Services: http://localhost:8000

### Manual Setup

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Confirm the venv is this repo (`millmitra\\backend\\venv`), not another clone such as `ricemill\\backend\\venv`.

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

Core mill ERP does not need TensorFlow. Optional ML extras: `pip install -r requirements-ml.txt`.

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your local database and Redis configuration
```

4. **Initialize database**
```bash
python migrate_db.py
```
==================================================
🔄 Starting database migration...
🗑️  Dropping existing tables...
🏗️  Creating tables with updated schema...
👤 Creating default admin user...
✅ Default users created successfully!
   - admin@ricemill.com / admin123
   - operator@ricemill.com / operator123
   - manager@ricemill.com / manager123
✅ Database migration completed successfully!
📍 Database location: rice_mill_erp.db
5. **Start the backend server**
```bash
python app.py
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment**
```bash
cp .env.example .env.local
# Edit with your API endpoints
```

3. **Start development server**
```bash
npm run dev
```

#### AI Services Setup

1. **Install dependencies**
```bash
cd ai-services
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Add your Google AI API key and other configurations
```

3. **Start AI services**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## ⚙️ Configuration

### Environment Variables

#### Core Configuration
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/rice_mill_erp

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Flask Environment
FLASK_ENV=development  # or production
FLASK_DEBUG=True       # False for production
```

#### AI Configuration
```bash
# Google AI
GOOGLE_AI_API_KEY=your-google-ai-api-key

# AI Services
AI_SERVICES_URL=http://localhost:8000
```

### Database Setup

#### PostgreSQL Setup
```sql
CREATE DATABASE rice_mill_erp;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE rice_mill_erp TO postgres;
```

### Redis Configuration
```bash
# Redis configuration for caching and session storage
redis-server --port 6379 --daemonize yes
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token

### User Management
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user details
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Farmer Management
- `GET /api/farmers` - List farmers
- `POST /api/farmers` - Create farmer
- `GET /api/farmers/{id}` - Get farmer details
- `PUT /api/farmers/{id}` - Update farmer

### Inventory Management
- `GET /api/inventory` - List inventory items
- `POST /api/inventory` - Add inventory item
- `GET /api/inventory/{id}` - Get inventory item
- `PUT /api/inventory/{id}` - Update inventory item

### Production Management
- `GET /api/production/batches` - List production batches
- `POST /api/production/batches` - Create production batch
- `GET /api/production/batches/{id}` - Get batch details

### Sales Management
- `GET /api/sales/orders` - List sales orders
- `POST /api/sales/orders` - Create sales order
- `GET /api/sales/orders/{id}` - Get order details

## 🔧 Development

### Project Structure
```
millmitra/
├── backend/                 # Flask backend API
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── ai/                 # AI integration services
│   ├── migrations/         # Database migrations
│   ├── config.py           # Configuration
│   ├── app.py              # Main application
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
├── ai-services/            # FastAPI AI microservices
│   ├── core/               # Core AI orchestration
│   ├── models/             # ML models
│   ├── voice/              # Voice processing
│   ├── vision/             # Computer vision
│   ├── analytics/          # Predictive analytics
│   └── main.py             # FastAPI application
├── docs/                   # Documentation
├── tests/                  # Test files
├── docker-compose.yml      # Docker services
└── README.md              # This file
```

### Testing

#### Backend Tests
```bash
cd backend
python -m pytest tests/ -v --cov=.
```

#### Frontend Tests
```bash
cd frontend
npm test
```

#### AI Services Tests
```bash
cd ai-services
python -m pytest tests/ -v
```

## 🚀 Deployment

### Production Deployment with Docker

1. **Update environment for production**
```bash
cp .env.example .env.production
# Configure production values
```

2. **Build and deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Run database migrations**
```bash
docker-compose exec backend python migrate_db.py
```

### Environment-Specific Configuration

For production deployment, ensure the following environment variables are set:

```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-key
DATABASE_URL=your-production-database-url
REDIS_URL=your-production-redis-url
```

## 🔒 Security

### Authentication & Authorization
- **JWT-based authentication** with refresh tokens
- **Role-based access control** (RBAC)
- **API rate limiting** and throttling
- **CORS configuration** for cross-origin requests

### Data Security
- **Encryption at rest** for sensitive data
- **HTTPS/TLS** for data in transit
- **Input validation** and sanitization
- **SQL injection** prevention

## 📈 Business Requirements Document (BRD)

### Business Objectives
1. **Operational Efficiency**: Streamline rice mill operations from procurement to sales
2. **Quality Control**: Implement comprehensive quality management throughout the production process
3. **Financial Transparency**: Provide real-time financial insights and reporting
4. **Supply Chain Optimization**: Enhance procurement and distribution processes
5. **Regulatory Compliance**: Ensure adherence to food safety and quality standards

### Functional Requirements

#### Core Business Functions
1. **Farmer Relationship Management**
   - Farmer registration and profile management
   - Contract negotiation and digital signing
   - Procurement scheduling and tracking
   - Payment processing and reporting

2. **Inventory Management**
   - Real-time stock tracking
   - Batch and lot tracking
   - Automated reorder alerts
   - FIFO/LIFO inventory valuation

3. **Production Management**
   - Batch production tracking
   - Quality control checkpoints
   - Equipment monitoring
   - Yield optimization

4. **Sales and Distribution**
   - Customer relationship management
   - Order processing and fulfillment
   - Dynamic pricing
   - Delivery tracking

5. **Financial Management**
   - Accounting and bookkeeping
   - Invoicing and payment tracking
   - Financial reporting
   - Tax compliance

#### AI-Enhanced Capabilities
1. **Predictive Analytics**
   - Demand forecasting
   - Equipment maintenance prediction
   - Quality trend analysis
   - Financial risk assessment

2. **Automation**
   - Automated quality testing
   - Inventory counting
   - Report generation
   - Procurement optimization

### Non-Functional Requirements

#### Performance
- System response time: < 2 seconds for 95% of requests
- Support for 1000+ concurrent users
- 99.9% uptime SLA

#### Security
- Role-based access control
- Data encryption (AES-256)
- Secure authentication (JWT)
- Regular security audits

#### Scalability
- Horizontal scaling support
- Database optimization for large datasets
- Cloud deployment compatibility

#### Usability
- Intuitive user interface
- Mobile-responsive design
- Multi-language support
- Accessibility compliance

### Success Metrics
1. **Operational Efficiency**: 20% reduction in processing time
2. **Quality Improvement**: 15% reduction in quality issues
3. **Cost Savings**: 10% reduction in operational costs
4. **User Satisfaction**: 90%+ user satisfaction rating
5. **Compliance**: 100% regulatory compliance

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow **PEP 8** for Python code
- Use **ESLint** and **Prettier** for JavaScript
- Write **comprehensive tests** for new features
- Update **documentation** for API changes
- Follow **semantic versioning** for releases

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue on the GitHub repository or contact the development team.

### Documentation
- **API Documentation**: http://localhost:5000/api/docs
- **User Manual**: [docs/user-manual.md](docs/user-manual.md)
- **Developer Guide**: [docs/developer-guide.md](docs/developer-guide.md)

