from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import jwt
from dotenv import load_dotenv
import datetime
import os

load_dotenv(dotenv_path='../application_gas_utility/.env')

# MongoDB setup
MONGO_URI = str(os.getenv('MONGODB_URI'))
client = MongoClient(MONGO_URI)
db = client['cluster']
users_collection = db['users']

# JWT secret key and settings
SECRET_KEY = str(os.getenv('JWT_SECRET_KEY'))
JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION'))


def generate_jwt(username, user_type):
    """
    Generate a JWT token with the username and user_type.
    """
    payload = {
        "username": username,
        "user_type": user_type,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        print("body: ",request.body)

        
        username = request.GET.get('username')
        password = request.GET.get('password')
        user_type = 'normal'  # Default user type
        
        # Check if username already exists
        if users_collection.find_one({'username': username}):
            return JsonResponse({'error': 'Username already exists'}, status=400)

        # Create user document
        user_data = {
            'username': username,
            'password': make_password(password),  # Hash the password
            'user_type': user_type,
        }

        # Save to MongoDB
        users_collection.insert_one(user_data)

        return JsonResponse({'message': 'User created successfully'}, status=201)
        

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            username = request.GET.get('username')
            password = request.GET.get('password')

            # Find user by username
            user_data = users_collection.find_one({'username': username})
            if user_data and check_password(password, user_data['password']):
                # Generate JWT token
                token = generate_jwt(user_data['username'], user_data['user_type'])

                # Set token as a cookie
                response = JsonResponse({
                    'message': 'Login successful',
                    'username': user_data['username'],
                    'user_type': user_data['user_type'],
                }, status=200)
                response.set_cookie(
                    key='token',
                    value=token,
                    httponly=True,  # Prevent JavaScript access
                    secure=True,  # Use secure cookies in production
                    samesite='Strict',  # Prevent cross-site request forgery
                )

                return response
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
