# Food Delivery API

A FastAPI-based backend API for a food delivery application with Firebase authentication and Firestore database.

## Features

- User Authentication with Firebase
- Role-based Access Control (Admin/User)
- Restaurant Management
- Menu Management
- Order Processing
- Real-time Updates

## Prerequisites

- Python 3.8+
- Firebase Account
- Firebase Service Account Key
- Google Cloud Project

## Setup

1. **Clone the repository**
   git clone https://github.com/AkashSahlot/OrderDeliveryApp.git

2. **Create and activate virtual environment**
   python -m venv .venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
  
3. **Install dependencies**
   pip install -r requirements.txt
  
4. **Firebase Configuration**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Generate a service account key (JSON file)
   - Place the service account key in `app/service-account.json`
   - Update `app/core/firebase.py` with your project ID

5. **Environment Variables**
Create a `.env` file in the root directory:
FIREBASE_PROJECT_ID=your-project-id

## Project Structure
```plaintext
app/
├── api/
│   ├── firebase_authentication.py
│   ├── restaurant.py
│   ├── user.py
│   └── home.py
├── core/
│   └── firebase.py
├── dto/
│   ├── restaurant.py
│   └── user.py
├── middleware/
│   ├── auth_middleware.py
│   ├── admin_logging.py
│   └── error_middleware.py
├── service-account.json
└── main.py
```


## Running the Application
uvicorn app.main:app --reload

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication Flow

1. **Register a new user**
2. **Login**
3.  **Use the token for authenticated requests**
   
## Admin Operations

### Restaurant Management

1. **Create Restaurant** (Admin only)
2. **Update Restaurant** (Admin only)
3. **Delete Restaurant** (Admin only)
## User Operations

1. **View Restaurants**
2. **View Menu Items**
## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
