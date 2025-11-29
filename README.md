# 🟦 Zahra Quotes API  

This is a **tiny FastAPI project built for learning purposes**, but it includes **all the essential features that a real production API requires**, such as:

- 🔐 JWT Authentication  
- 🔏 Authorization  
- ♻️ Idempotency Keys  
- 📝 Structured Logging  
- 🧪 Integration Tests  
- ⚙️ Environment Variables (.env)  
- 🧵 Background Task Processing  
- 🧱 Proper Error Handling and Validation  
- 🚀 CI/CD Pipeline (Continuous Integration / Continuous Delivery or Deployment)

Although the API itself is simple (it only returns jokes and quotes), it demonstrates **every major backend concept** found in real-world APIs — making it an excellent foundation for professional API development and deployment.

---
## 🚀 Live Deployment
This API is **deployed on Render.com**, a cloud hosting platform designed for modern web services.

**Live API URL:**  
👉 https://zahra-quotes-api.onrender.com

**Swagger Docs:**  
👉 https://zahra-quotes-api.onrender.com/docs  

**ReDoc Docs:**  
👉 https://zahra-quotes-api.onrender.com/redoc  


## 🚀 Features

### 🔐 Authentication (JWT)
- Generates secure JWT tokens with:
  - `sub` – user identity  
  - `iat` – issued timestamp  
  - `exp` – token expiration  
- Tokens required for accessing protected routes.

### 🔏 Authorization
Protected endpoints use:

```python
current_user: str = Depends(get_current_user)
```
Requests without valid tokens return 401 Unauthorized.

### ♻️ Idempotency Support

- Requires header:
```python
Idempotency-Key: <unique-id>
```
- Ensures repeated requests return the same stored response.

- Prevents duplicate processing.

- Implements background cleanup of expired keys.

### 📝 Logging Middleware
Logs every request with:

- Client IP

- HTTP method

- Path

- Status code

- Processing duration

- JWT user (sub)

- Idempotency key

Example log:
```
2025-11-26 14:52:13 - INFO - zahra-api - 127.0.0.1 - POST /process - status=200 - user=anonymous_user - idempotency_key=abc123 - 0.024s
```

### 🧪 Integration Tests

Covers:

 - Token generation

 - Missing idempotency key

 - Valid & invalid prompts

 - Duplicate-key idempotency behavior

 - JWT-protection enforcemen