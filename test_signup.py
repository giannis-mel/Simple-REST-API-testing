import requests
import pytest
from app import app # Flask instance of the API
from app import User
from  werkzeug.security import generate_password_hash, check_password_hash

url = 'http://127.0.0.1:5000' # The root url of the flask app

# Test user signup
def test_user_signup():

    myBody = {
    "name": "Chandler Bing",
    "email": "admin@ekmechanes.com",
    "password": "Password!!!!!",
    "active" : True ,
    "role" : "admin"
    }
    
    # Request
    response = requests.post(url+'/signup', json = myBody)
    
    # Expected results
    assert response.status_code == 200
    
    # Checking for the user in db TODO
    # signed_user = User.query.filter_by(email = 'admin@ekmechanes.com').first()
    # assert signed_user != None
 
# Test user signup for the 2nd time
def test_user_signup_again():

    myBody = {
    "name": "Chandler Bing",
    "email": "admin@ekmechanes.com",
    "password": "Password!!!!!",
    "active" : True ,
    "role" : "admin"
    }
    
    # Request
    response = requests.post(url+'/signup', json = myBody)
    
    # Expected results
    assert response.status_code == 202

# Test trying to sign up a user with a forbidden role
def test_user_signup_forbidden_role():

    myBody = {
    "name": "Monica Geller",
    "email": "monica@ekmechanes.com",
    "password": "monica",
    "active" : False,
    "role" : "cook"
    }   
    
    # Request
    response = requests.post(url+'/signup', json = myBody)
    
    # Expected results
    assert response.status_code == 403