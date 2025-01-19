from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
import json
import datetime
import jwt
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../application_gas_utility/.env')

SECRET_KEY = str(os.getenv('JWT_SECRET_KEY'))

MONGO_URI = str(os.getenv('MONGODB_URI'))
client = MongoClient(MONGO_URI)
db = client['cluster']
users_collection = db["users"]
requests_collection = db["requests"]

def verify_jwt(request):
    token = request.headers.get('Authorization')
    if not token:
        return None, "Missing token"

    try:
        payload = jwt.decode(token.split(' ')[1], SECRET_KEY, algorithms=["HS256"])
        username = payload.get("username")
        user_type = payload.get("user_type")  
        if not username or not user_type:
            return None, "Invalid token"

        return {"username": username, "user_type": user_type}, None  
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


@csrf_exempt
def chnage_status_admin(request, request_id, new_status):
    if request.method=="POST":
        user, error = verify_jwt(request)
        if error:
            return JsonResponse({'error': error}, status=403)
        
        if user["user_type"] !="admin":
            return JsonResponse({'error': 'Unauthorized user type'}, status=403)
        result = requests_collection.update_one({"_id": request_id}, {"$set": {"status": new_status}})

        if result.matched_count > 0:
            return JsonResponse({'message': 'status updated successfully'})
        else:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
    
        
@csrf_exempt
def delete_request_admin(request, request_id):
    if request.method == 'DELETE':
        user, error = verify_jwt(request)
        if error:
            return JsonResponse({'error': error}, status=403)

        if user["user_type"] != "admin":
            return JsonResponse({'error': 'Unauthorized user type'}, status=403)

        result = requests_collection.delete_one({"_id": request_id})
        if result.deleted_count == 0:
            return JsonResponse({'error': 'Request not found or not authorized'}, status=404)

        return JsonResponse({'message': 'Request deleted successfully'})

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

@csrf_exempt
def get_requests_admin(request):
    if request.method == 'GET':
        user, error = verify_jwt(request)
        if error:
            return JsonResponse({'error': error}, status=403)

        if user["user_type"] != "admin":
            return JsonResponse({'error': 'Unauthorized user type'}, status=403)

        user_requests = list(requests_collection.find())
        for req in user_requests:
            req["_id"] = str(req["_id"])

        return JsonResponse({'requests': user_requests}, safe=False)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

@csrf_exempt
def create_request(request):
    if request.method == 'POST':
        user, error = verify_jwt(request)
        if error:
            return JsonResponse({'error': error}, status=403)

        if user["user_type"] != "normal":
            return JsonResponse({'error': 'Unauthorized user type'}, status=403)

        try:
            data = json.loads(request.body)
            request_type = data.get('request_type')
            details = data.get('details')

            new_request = {
                'username': user['username'],
                'request_type': request_type,
                'details': details,
                'status': 'Pending',
                'submitted_at': datetime.datetime.now(),
            }
            result = requests_collection.insert_one(new_request)
            new_request["_id"] = str(result.inserted_id)

            return JsonResponse({'message': 'Request created successfully', 'request': new_request})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

@csrf_exempt
def get_requests(request):
    if request.method == 'GET':
        user, error = verify_jwt(request)
        if error:
            return JsonResponse({'error': error}, status=403)

        if user["user_type"] != "normal":
            return JsonResponse({'error': 'Unauthorized user type'}, status=403)

        user_requests = list(requests_collection.find({"username": user['username']}))
        for req in user_requests:
            req["_id"] = str(req["_id"])

        return JsonResponse({'requests': user_requests}, safe=False)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

@csrf_exempt
def delete_request(request, request_id):
    if request.method == 'DELETE':
        user, error = verify_jwt(request)
        if error:
            return JsonResponse({'error': error}, status=403)

        if user["user_type"] != "normal":
            return JsonResponse({'error': 'Unauthorized user type'}, status=403)

        result = requests_collection.delete_one({"_id": request_id, "username": user['username']})
        if result.deleted_count == 0:
            return JsonResponse({'error': 'Request not found or not authorized'}, status=404)

        return JsonResponse({'message': 'Request deleted successfully'})

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


