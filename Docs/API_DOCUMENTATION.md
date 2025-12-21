# MISoft API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication Endpoints

### 1. Register New User
**POST** `/api/auth/register/`

**Request Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepassword123",
  "role": "worker",
  "phone_number": "1234567890",
  "first_name": "Test",
  "last_name": "User"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "role": "worker",
    "phone_number": "1234567890",
    "first_name": "Test",
    "last_name": "User"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 2. Login
**POST** `/api/auth/login/`

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@misoft.com",
    "role": "admin",
    "phone_number": null,
    "first_name": "",
    "last_name": "",
    "is_staff": true
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 3. Get Current User Info
**GET** `/api/auth/user/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@misoft.com",
  "role": "admin",
  "phone_number": null,
  "first_name": "",
  "last_name": "",
  "is_staff": true
}
```

---

### 4. Refresh Token
**POST** `/api/auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 5. Logout
**POST** `/api/auth/logout/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

---

## Testing with cURL

### Register:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123","role":"worker"}'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Get User Info:
```bash
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Error Responses

### 400 Bad Request
```json
{
  "username": ["This field is required."],
  "password": ["This field is required."]
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Authentication credentials were not provided."
}
```
