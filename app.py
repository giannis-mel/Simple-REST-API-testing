from flask import Flask, request, jsonify, make_response # Imports the flask library modules
from flask_sqlalchemy import SQLAlchemy
import uuid # for public id, not used for now
from  werkzeug.security import generate_password_hash, check_password_hash
# Imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta
from functools import wraps


app = Flask(__name__) # Single module that grabs all modules executing from this file

app.config['SECRET_KEY'] = 'your secret key'
# Database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Creates SQLALCHEMY object
db = SQLAlchemy(app)

idNum = 1

# Database ORMs
class User(db.Model):
    id = db.Column(db.String(100), primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique = True)
    password = db.Column(db.String(80))
    active = db.Column(db.Boolean, unique=False, default=True)
    passwordChanged = db.Column(db.Boolean, unique=False, default=False)
    role = db.Column(db.String(20))
    createdAt = db.Column(db.String(100))
    createdBy = db.Column(db.String(100), unique = False)
    updatedAt = db.Column(db.String(100), default = "not updated yet")
    updatedBy = db.Column(db.String(100), default = "not updated yet")

## TO DO
"""
# Verify that you receive JSON
def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            request.json
        except BadRequest, e:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        return f(*args, **kw)
    return wrapper
"""
 
# Decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # JWT is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        # Return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # Remove the bearer
            tokens = token.split(" ");
            # Decoding the payload to fetch the stored details
            data = jwt.decode(tokens[1], key='your secret key', algorithms=['HS256'])
            # Useful for debugging
            #print("Data returned: ")
            #print(data)
            # Find current user by his id.
            current_user = User.query.filter_by(id = data['id']).first()
        except:
            return jsonify({'message' : 'Token is invalid !!'}), 401
        # Returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

## ROUTES

# Route for logging user
@app.route('/login', methods=['POST']) # HTTP request methods
def login():
    data = []
    if request.method == 'POST': # Checks if it's a POST request
        
        request_data = request.get_json(force=True, silent=True ) 
        # force and silent attributes are set True to not raise an exception and return None when a non valid JSON is received
        # Request data can be i) a normal JSON ii) None as it is not valid JSON and iii) {} as an empty JSON
        # If it is a {} then I treat it as not valid JSON 
        
        rec_email = None 
        rec_password = None
        
        # Useful for debugging purposes
        #print(request_data)
        
        if request_data:
            if 'email' in request_data :
                rec_email = request_data['email']
            else :
                data = {"error" : {"messages" : ["Invalid username-password combination(No email given)."]}, "status" : 400}
                response = jsonify(data) # Converts your data into JSON format
                response.status_code = 400 # Provides a response status code of 400 which is "Not Acceptable"
                return response # Returns the HTTP response 
            if 'password' in request_data :
                rec_password = request_data['password']
            else :
                data = {"error" : {"messages" : ["Invalid username-password combination(No password given)."]}, "status" : 400}
                response = jsonify(data) # Converts your data into JSON format
                response.status_code = 400 # Provides a response status code of 400 which is "Not Acceptable"
                return response # Returns the HTTP response
        else:
            data = {"error" : {"messages" : ["Invalid username-password combination(No valid JSON)."]}, "status" : 400}
            response = jsonify(data) # Converts your data into JSON format
            response.status_code = 400 # Provides a response status code of 400 which is "Not Acceptable"
            return response # Returns the HTTP response
  
        user = User.query.filter_by(email = rec_email).first()
        
        if user :
            if check_password_hash(user.password, rec_password):
                # Generates the JWT Token
                token = jwt.encode({
                'id': user.id,
                'exp' : datetime.utcnow() + timedelta(minutes = 30)
                }, app.config['SECRET_KEY'])
                
                data = {"data" : {"jwt" : {"accessToken": token}}, "status" : 200}
                response = jsonify(data) # Converts your data into JSON format
                response.status_code = 200 # Provides a response status code of 200 which is "Accepted" 
                return response # Returns the HTTP response
            else :
                data = {"error" : {"messages" : ["Invalid username-password combination(Wrong password)."]}, "status" : 400}
                response = jsonify(data) # Converts your data into JSON format
                response.status_code = 400 # Provides a response status code of 400 which is "Not Acceptable"
                return response # Returns the HTTP response   
        else:
                data = {"error" : {"messages" : ["Invalid username-password combination(Wrong email)."]}, "status" : 400}
                response = jsonify(data) # Converts your data into JSON format
                response.status_code = 400 # Provides a response status code of 400 which is "Not Acceptable"
                return response # Returns the HTTP response   

# Route for creating the database(run this the first time you make a connection to create the db !)
@app.route('/create')
def create():
    db.create_all()
    return 'All tables created'

# Route for updating user with if of the user that needs to be updated in path variable 
# Ex: /api/v1/users/5ca5ddd23bf77546543e2c9f 
@app.route('/api/v1/users/<userId>', methods =['PUT'])
@token_required
def update_with_path_variable(current_user, userId):
    data = []
    output = []
    print(userId)
    if request.method == 'PUT': # Checks if it's a PUT request
        request_data = request.get_json()
        # Check if current user has admin rights
        if current_user.role == "admin":
            # Creates a dictionary
            request_data = request.get_json()
          
            # Gets values from JSON
            new_name, new_email = request_data.get('name'), request_data.get('email')
            new_role = request_data.get('role')
            new_active = request_data.get('active')
            
            # Datetime object containing current date and time
            now = datetime.now()
            
            # Checking for existing user by using userId given in path variable
            user_to_update = User.query.filter_by(id = userId).first()
            print(user_to_update)
            
            if not user_to_update:
                return make_response('No such user can be found.', 400)
            else :
            
                # Check if valid role is given
                if new_role != "reporter" :
                    if new_role != "executor":
                        if new_role != "admin":
                            return make_response('Role can only be reporter, executor or admin.', 403) 
            
                user_to_update.active = new_active
                user_to_update.email = new_email
                user_to_update.role = new_role
                user_to_update.updatedAt = now.strftime("%d/%m/%Y %H:%M:%S")
                user_to_update.updatedBy = current_user.id
                
                db.session.commit()
                
                # Send the response
                output.append({
                    'active' : user_to_update.active,
                    'id': user_to_update.id,
                    'name' : user_to_update.name,
                    'email' : user_to_update.email,
                    'role' : user_to_update.role,
                    'createdAt' : user_to_update.createdAt,
                    'createdBy' : user_to_update.createdBy,
                    'updatedAt' : user_to_update.updatedAt,
                    'updatedBy' : user_to_update.updatedBy
                })
                
                data = {"data" : {"user" : output}, "status" : 200}
                response = jsonify(data) # Converts your data into JSON format
                response.status_code = 200 # Provides a response status code of 200 which is "Accepted" 
                return response # Returns the HTTP response
        else :
            return make_response('Only an admin can update a user.', 400)

 
# Route for updating user with no path variable and just using email from json body
@app.route('/update', methods =['PUT'])
@token_required
def update_with_no_path_variable(current_user):
    data = []
    output = []
    if request.method == 'PUT': # Checks if it's a POST request
        request_data = request.get_json()
        # Check if current user has admin rights
        if current_user.role == "admin":
            # Creates a dictionary
            request_data = request.get_json()
          
            # Gets values from JSON
            new_name, new_email = request_data.get('name'), request_data.get('email')
            new_role = request_data.get('role')
            new_active = request_data.get('active')
            
            # Datetime object containing current date and time
            now = datetime.now()
            
            # Checking for existing user
            user_to_update = User.query.filter_by(email = new_email).first()
            print(user_to_update)
            
            if not user_to_update:
                return make_response('No such user can be found.', 400)
            else :
            
                # Check if valid role is given
                if new_role != "reporter" :
                    if new_role != "executor":
                        if new_role != "admin":
                            return make_response('Role can only be reporter, executor or admin.', 403) 
            
                user_to_update.active = new_active
                user_to_update.email = new_email
                user_to_update.role = new_role
                user_to_update.updatedAt = now.strftime("%d/%m/%Y %H:%M:%S")
                user_to_update.updatedBy = current_user.id
                
                db.session.commit()
                
                # Send the response
                output.append({
                    'active' : user_to_update.active,
                    'id': user_to_update.id,
                    'name' : user_to_update.name,
                    'email' : user_to_update.email,
                    'role' : user_to_update.role,
                    'createdAt' : user_to_update.createdAt,
                    'createdBy' : user_to_update.createdBy,
                    'updatedAt' : user_to_update.updatedAt,
                    'updatedBy' : user_to_update.updatedBy
                })
                
                data = {"data" : {"user" : output}, "status" : 200}
                response = jsonify(data) # Converts your data into JSON format
                response.status_code = 200 # Provides a response status code of 200 which is "Accepted" 
                return response # Returns the HTTP response
        else :
            return make_response('Only an admin can update a user.', 400)
    

# Route for signing up new users
@app.route('/signup', methods =['POST'])
def signup():
    # Creates a dictionary
    request_data = request.get_json()
  
    # Gets values from JSON
    new_name, new_email = request_data.get('name'), request_data.get('email')
    new_password = request_data.get('password')
    new_role = request_data.get('role')
    new_active = request_data.get('active')
    
    # Datetime object containing current date and time
    now = datetime.now()
    
    # Checking for existing user
    user = User.query.filter_by(email = new_email).first()
    
    # Every potential new user can sign up on each own
    global idNum
    
    if not user:
    
        # Check if valid role is given
        if new_role != "reporter" :
            if new_role != "executor":
                if new_role != "admin":
                    return make_response('Your role can only be reporter, executor or admin.', 403) 
    
        # Database ORM object
        user = User(
            id = str(idNum),
            name = new_name,
            email = new_email,
            password = generate_password_hash(new_password),
            active = new_active,
            passwordChanged = False,
            role = new_role,
            createdAt = now.strftime("%d/%m/%Y %H:%M:%S"),
            createdBy = str(idNum),
            updatedAt = "not updated yet",
            updatedBy = "not updated yet"
        )
        # Insert user
        db.session.add(user)
        db.session.commit()
        
        # Increase the id number
        idNum = idNum + 1 
  
        return make_response('Successfully registered.', 200)
    else:
        # Returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)
        
        
# Route for returning list of users
@app.route('/user', methods =['GET'])
@token_required
def get_all_users(current_user):

    # Check if current user has admin rights
    if current_user.role == "admin":
        output = []
        # querying the database for all the entries in it
        users = User.query.all()
        # converting the query objects to list of jsons
        for user in users:
            # appending the user data json
            # to the response list
            output.append({
                'id': user.id,
                'name' : user.name,
                'email' : user.email,
                'active' : user.active,
                'role' : user.role,
                'createdAt' : user.createdAt,
                'createdBy' : user.createdBy,
                'updatedAt' : user.updatedAt,
                'updatedBy' : user.updatedBy
            })
        return jsonify({'users': output})
    else :
        return make_response('Only an admin can see the list of users', 400)
       