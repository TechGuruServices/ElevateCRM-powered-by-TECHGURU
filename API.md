# ElevateCRM API Documentation

Complete API reference for the ElevateCRM backend services.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://yourdomain.com`

## Authentication

All API endpoints (except public endpoints) require authentication using JSON Web Tokens (JWT).

### Authentication Flow

1. **Register/Login** to obtain access and refresh tokens
2. **Include access token** in the `Authorization` header: `Bearer <access_token>`
3. **Refresh tokens** when access token expires

### Token Endpoints

#### POST /api/v1/auth/register

Register a new user and company.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe",
  "company_name": "ACME Corp",
  "company_size": "small",
  "industry": "technology"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "company_id": "uuid"
  }
}
```

#### POST /api/v1/auth/login

Authenticate existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "company_id": "uuid"
  }
}
```

#### POST /api/v1/auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/logout

Invalidate current session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## Customer Management API

### GET /api/v1/customers

Retrieve customers with pagination and filtering.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 20): Items per page
- `search` (string): Search by name or email
- `status` (string): Filter by status (active, inactive)
- `sort` (string): Sort field (name, email, created_at)
- `order` (string): Sort order (asc, desc)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "John Smith",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "company": "ACME Corp",
      "status": "active",
      "rating": 4.5,
      "total_orders": 12,
      "total_value": 45000.00,
      "last_contact": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8,
  "has_next": true,
  "has_prev": false
}
```

### POST /api/v1/customers

Create a new customer.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1-555-0124",
  "company": "Tech Solutions Inc",
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "country": "USA"
  },
  "tags": ["vip", "enterprise"],
  "notes": "High-value customer"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1-555-0124",
  "company": "Tech Solutions Inc",
  "status": "active",
  "rating": null,
  "total_orders": 0,
  "total_value": 0.00,
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "country": "USA"
  },
  "tags": ["vip", "enterprise"],
  "notes": "High-value customer",
  "created_at": "2024-01-16T10:30:00Z",
  "updated_at": "2024-01-16T10:30:00Z"
}
```

### GET /api/v1/customers/{customer_id}

Retrieve a specific customer.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "uuid",
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "company": "ACME Corp",
  "status": "active",
  "rating": 4.5,
  "total_orders": 12,
  "total_value": 45000.00,
  "address": {
    "street": "456 Oak Ave",
    "city": "Los Angeles",
    "state": "CA",
    "zip": "90210",
    "country": "USA"
  },
  "tags": ["premium"],
  "notes": "Long-term customer",
  "last_contact": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### PUT /api/v1/customers/{customer_id}

Update an existing customer.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Smith Jr.",
  "phone": "+1-555-0125",
  "status": "active",
  "rating": 5.0,
  "notes": "Upgraded to premium service"
}
```

### DELETE /api/v1/customers/{customer_id}

Delete a customer (soft delete).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Customer deleted successfully"
}
```

## Inventory Management API

### GET /api/v1/products

Retrieve products with pagination and filtering.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 20): Items per page
- `search` (string): Search by name or SKU
- `category` (string): Filter by category
- `status` (string): Filter by status (active, inactive, discontinued)
- `low_stock` (boolean): Filter products with low stock
- `sort` (string): Sort field (name, sku, price, stock)
- `order` (string): Sort order (asc, desc)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Wireless Headphones",
      "sku": "WH-001",
      "description": "Premium wireless headphones with noise cancellation",
      "category": "Electronics",
      "price": 299.99,
      "cost": 150.00,
      "stock_quantity": 45,
      "reorder_level": 10,
      "status": "active",
      "images": [
        "https://example.com/images/wh-001-1.jpg"
      ],
      "attributes": {
        "color": "Black",
        "weight": "250g",
        "battery_life": "30 hours"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 250,
  "page": 1,
  "pages": 13,
  "has_next": true,
  "has_prev": false
}
```

### POST /api/v1/products

Create a new product.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Smart Watch",
  "sku": "SW-001",
  "description": "Advanced fitness tracking smartwatch",
  "category": "Electronics",
  "price": 399.99,
  "cost": 200.00,
  "stock_quantity": 25,
  "reorder_level": 5,
  "attributes": {
    "color": "Silver",
    "display": "OLED",
    "battery_life": "7 days"
  }
}
```

### GET /api/v1/products/{product_id}

Retrieve a specific product.

### PUT /api/v1/products/{product_id}

Update an existing product.

### DELETE /api/v1/products/{product_id}

Delete a product (soft delete).

### POST /api/v1/products/{product_id}/stock

Adjust product stock levels.

**Request Body:**
```json
{
  "adjustment": 10,
  "type": "restock",
  "reason": "Received new shipment",
  "cost_per_unit": 150.00
}
```

## Order Management API

### GET /api/v1/orders

Retrieve orders with pagination and filtering.

**Query Parameters:**
- `page`, `limit`: Pagination
- `status`: Filter by order status
- `customer_id`: Filter by customer
- `date_from`, `date_to`: Date range filter

### POST /api/v1/orders

Create a new order.

**Request Body:**
```json
{
  "customer_id": "uuid",
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2,
      "unit_price": 299.99
    }
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "country": "USA"
  },
  "notes": "Rush order"
}
```

### GET /api/v1/orders/{order_id}

Retrieve a specific order.

### PUT /api/v1/orders/{order_id}/status

Update order status.

**Request Body:**
```json
{
  "status": "shipped",
  "tracking_number": "1Z999AA1234567890",
  "notes": "Shipped via UPS"
}
```

## Analytics API

### GET /api/v1/analytics/dashboard

Get dashboard analytics.

**Response:**
```json
{
  "overview": {
    "total_customers": 1250,
    "total_orders": 3450,
    "total_revenue": 125000.00,
    "inventory_value": 85000.00
  },
  "recent_activity": [
    {
      "type": "order",
      "description": "New order #ORD-001 from John Smith",
      "timestamp": "2024-01-16T10:30:00Z"
    }
  ],
  "top_products": [
    {
      "product_id": "uuid",
      "name": "Wireless Headphones",
      "sales_count": 45,
      "revenue": 13499.55
    }
  ],
  "sales_trend": [
    {
      "date": "2024-01-01",
      "sales": 2500.00,
      "orders": 8
    }
  ]
}
```

### GET /api/v1/analytics/sales

Get sales analytics with date range.

**Query Parameters:**
- `period`: today, week, month, quarter, year, custom
- `date_from`, `date_to`: For custom period

### GET /api/v1/analytics/inventory

Get inventory analytics.

**Response:**
```json
{
  "low_stock_products": [
    {
      "product_id": "uuid",
      "name": "Smart Watch",
      "current_stock": 3,
      "reorder_level": 5
    }
  ],
  "top_selling_products": [...],
  "inventory_value_by_category": [
    {
      "category": "Electronics",
      "value": 45000.00,
      "percentage": 52.9
    }
  ]
}
```

## Integration API

### Webhooks

ElevateCRM can send webhooks for various events.

#### Webhook Events

- `customer.created`
- `customer.updated` 
- `order.created`
- `order.status_changed`
- `product.stock_low`

#### Webhook Payload Format

```json
{
  "event": "order.created",
  "timestamp": "2024-01-16T10:30:00Z",
  "data": {
    "order": {
      "id": "uuid",
      "customer_id": "uuid",
      "total": 599.98,
      "status": "pending"
    }
  }
}
```

### External Integrations

#### POST /api/v1/integrations/shopify/sync

Sync with Shopify store.

#### POST /api/v1/integrations/quickbooks/export

Export data to QuickBooks.

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Rate Limited
- `500`: Internal Server Error

## Rate Limiting

API requests are rate limited:

- **Authentication endpoints**: 5 requests per 5 minutes per IP
- **General API**: 100 requests per hour per user
- **Bulk operations**: 10 requests per minute per user

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642348800
```

## SDKs and Libraries

### JavaScript/TypeScript SDK

```bash
npm install elevatecrm-js
```

```javascript
import { ElevateCRM } from 'elevatecrm-js';

const client = new ElevateCRM({
  apiUrl: 'https://yourdomain.com',
  accessToken: 'your-access-token'
});

// Get customers
const customers = await client.customers.list({
  page: 1,
  limit: 10
});

// Create order
const order = await client.orders.create({
  customer_id: 'uuid',
  items: [
    { product_id: 'uuid', quantity: 2, unit_price: 99.99 }
  ]
});
```

### Python SDK

```bash
pip install elevatecrm-python
```

```python
from elevatecrm import ElevateCRM

client = ElevateCRM(
    api_url='https://yourdomain.com',
    access_token='your-access-token'
)

# Get products
products = client.products.list(page=1, limit=10)

# Update inventory
client.products.adjust_stock(
    product_id='uuid',
    adjustment=10,
    type='restock'
)
```

## Testing

### Test Environment

- **Base URL**: `https://sandbox.elevatecrm.com`
- **Test credentials**: Available in developer dashboard

### Postman Collection

Import our Postman collection for easy API testing:

```bash
curl -o elevatecrm-postman.json https://api.elevatecrm.com/postman/collection
```

### API Testing Examples

```bash
# Test authentication
curl -X POST https://yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test protected endpoint
curl -X GET https://yourdomain.com/api/v1/customers \
  -H "Authorization: Bearer your-access-token"
```

## Support

- **Documentation**: [https://docs.elevatecrm.com](https://docs.elevatecrm.com)
- **API Status**: [https://status.elevatecrm.com](https://status.elevatecrm.com)
- **Support**: [support@elevatecrm.com](mailto:support@elevatecrm.com)
- **Developer Forum**: [https://community.elevatecrm.com](https://community.elevatecrm.com)