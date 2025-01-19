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
   git clone https://github.com/your-repository.git
```
