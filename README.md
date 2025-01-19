# Django Project - Request Management System

This project is a request management system that allows users to create, delete, and view requests. It supports two types of users: normal users and admin users. Admin users have additional privileges to manage requests and change their status.

## Features

- **User Authentication**: Secure login and signup with JWT token-based authentication.
- **Request Management**: 
  - Normal users can create, view, and delete their requests.
  - Admin users can view all requests, delete them, and change their statuses.
- **Real-Time Communication**: WebSocket support for customer support interactions.
- **MongoDB Database**: Utilizes MongoDB for storing user and request data.

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/Dhruv-Bajaj-code/application_gas_utility.git

2. Navigate to the project directory:
  
   ```bash
   cd application_gas_utility

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt

4. Set up your environment variables in a .env file. Example:

   ```bash
   JWT_SECRET_KEY=your-secret-key
   MONGODB_URI=your-mongodb-uri
   JWT_EXPIRATION=your-jwt-expiration-time

5. Run the development server:

   ```bash
   uvicorn application_gas_utility.asgi:application --reload

## API Endpoints

**User Endpoints**

   ```bash
   POST /signup/: Create a new user.
   POST /login/: User login, returns a JWT token.
    bash```

**Request Endpoints**

   ```bash
   POST /create_request/: Create a new request.
   GET /get_requests/: Get all requests for the logged-in user.
   DELETE /delete_request/: Delete a specific request.

## Admin Endpoints

   ```bash
   POST /admin/change_status/: Change the status of a request.
   DELETE /admin/delete_request/: Delete any request by its ID.
   GET /admin/get_requests/: Get all requests in the system.

## WebSocket Endpoints

   ```bash
   ws/chat/: A WebSocket connection for real-time chat between users and support staff.


#Contributing
Feel free to fork the repository and submit pull requests. Ensure that your contributions follow the coding standards of the project.
