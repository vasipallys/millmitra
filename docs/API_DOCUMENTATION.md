# Rice Mill AI - API Documentation

Complete API reference for the Rice Mill AI system.

## 🔗 Base URLs

- **Development**: `http://localhost:5000/api`
- **Production**: `https://your-domain.com/api`
- **AI Services**: `http://localhost:8000`

## 🔐 Authentication

All API endpoints (except public ones) require JWT authentication.

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@ricemill.com",
    "roles": ["super_admin"]
  }
}
```

### Using JWT Token
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 📋 API Endpoints

### 👥 User Management

#### Get All Users
```http
GET /api/users
Authorization: Bearer {token}
```

#### Create User
```http
POST /api/users
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "full_name": "New User",
  "password": "securepassword",
  "roles": ["operator"]
}
```

### 🌾 Farmer Management

#### Get All Farmers
```http
GET /api/farmers
Authorization: Bearer {token}
```

#### Create Farmer
```http
POST /api/farmers
Authorization: Bearer {token}
Content-Type: application/json

{
  "farmer_code": "F001",
  "name": "John Farmer",
  "phone": "+91-9876543210",
  "address": "Village, District, State",
  "land_area": 5.5,
  "crops": ["rice", "wheat"]
}
```

### 📦 Inventory Management

#### Get Inventory Items
```http
GET /api/inventory/items
Authorization: Bearer {token}
```

#### Create Inventory Item
```http
POST /api/inventory/items
Authorization: Bearer {token}
Content-Type: application/json

{
  "item_code": "RICE001",
  "name": "Basmati Rice",
  "category": "finished_goods",
  "unit": "kg",
  "current_stock": 1000,
  "warehouse_id": 1
}
```

### 🏭 Production Management

#### Get Production Batches
```http
GET /api/production/batches
Authorization: Bearer {token}
```

#### Create Production Batch
```http
POST /api/production/batches
Authorization: Bearer {token}
Content-Type: application/json

{
  "batch_number": "B001",
  "raw_material_id": 1,
  "quantity": 1000,
  "target_product": "polished_rice",
  "expected_yield": 0.85
}
```

### 💰 Sales Management

#### Get Sales Orders
```http
GET /api/sales/orders
Authorization: Bearer {token}
```

#### Create Sales Order
```http
POST /api/sales/orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 1,
  "order_date": "2024-01-15",
  "items": [
    {
      "product_id": 1,
      "quantity": 100,
      "unit_price": 50.00
    }
  ]
}
```

## 🤖 AI Services API

### Production Optimization
```http
POST /ai/production/optimize
Content-Type: application/json

{
  "batch_data": {
    "raw_material": "paddy",
    "quantity": 1000,
    "moisture_content": 14.2
  }
}
```

### Quality Assessment
```http
POST /ai/quality/assess
Content-Type: multipart/form-data

image: [rice_sample.jpg]
batch_id: 123
```

### Voice Processing
```http
POST /ai/voice/process
Content-Type: multipart/form-data

audio: [voice_command.wav]
context: production
```

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}
```

## 🔍 Query Parameters

### Filtering
```http
GET /api/inventory/items?category=raw_materials&warehouse_id=1
```

### Sorting
```http
GET /api/sales/orders?sort=order_date&order=desc
```

### Pagination
```http
GET /api/farmers?page=2&per_page=50
```

### Date Ranges
```http
GET /api/production/batches?start_date=2024-01-01&end_date=2024-01-31
```

## 📝 Complete API Reference

For detailed API documentation with interactive examples, visit:
- **Swagger UI**: http://localhost:5000/api/docs
- **ReDoc**: http://localhost:5000/api/redoc