# FastAPI Firebase Backend

A **FastAPI** backend with **JWT authentication** and Firebase integration for managing users with two roles: **Superadmin** and **Admin**. This backend provides an interface for Firebase Authentication and Firestore user management.

## Features
- JWT authentication with role-based access (**Superadmin, Admin**)
- Firebase SDK for user authentication & Firestore management
- CRUD operations for user accounts
- Approve, hold, or delete user accounts (Superadmin only)
- Generate password reset links
- FastAPI with automatic OpenAPI documentation

## Directory Structure
```
backend/
│── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py        # Authentication & JWT
│   │   │   ├── users.py       # User management (List, Add, Edit, Delete)
│   │   │   ├── admin.py       # Superadmin/Admin operations
│   │   │   ├── dependencies.py# Dependency Injection (RBAC)
│   ├── core/
│   │   ├── config.py         # App settings & environment variables
│   │   ├── security.py       # JWT handling & Role-Based Access Control
│   │   ├── firebase.py       # Firebase SDK integration
│   ├── models/               # Pydantic Models (Schemas)
│   │   ├── user.py           # User data models
│   ├── services/             # Business Logic & External Services
│   │   ├── auth_service.py   # Firebase authentication logic
│   │   ├── user_service.py   # User management logic
│   ├── main.py               # App entry point
│── tests/                    # Unit & Integration Tests
│── .env                      # Environment variables (Firebase keys, secrets)
│── requirements.txt          # Python dependencies
│── Dockerfile                # Containerization setup
│── README.md                 # Project Documentation
```

## Setup Instructions
### 1. Clone the repository
```sh
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### 2. Create a virtual environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Set up Firebase credentials
- Generate a Firebase Admin SDK JSON key from Firebase Console.
- Place the JSON file in the project root.
- Create a `.env` file and add:
```sh
FIREBASE_CREDENTIALS=firebase-adminsdk.json
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Run the FastAPI server
```sh
uvicorn app.main:app --reload
```

### 6. Access API Documentation
FastAPI provides interactive API documentation:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc UI: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | User login (JWT) |
| `/users/` | GET | List all users from Firebase |
| `/users/` | POST | Add a new user |
| `/users/{user_id}` | PUT | Edit an existing user |
| `/users/{user_id}/reset-password` | POST | Generate password reset link |
| `/admin/approve/{user_id}` | PUT | Approve a new user |
| `/admin/hold/{user_id}` | PUT | Put a user account on hold |
| `/admin/delete/{user_id}` | DELETE | Delete a user (Superadmin only) |

---
**Author:** Varad Joshi  
**GitHub:** [Varad-13](https://github.com/Varad-13)

