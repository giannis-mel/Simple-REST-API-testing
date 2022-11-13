# Simple REST API testing
This is a simple project for getting familiar with testing tools such as Postman.

First, I created a local REST API using __Flask__. This is the API that will be tested.  For the automated tests I’ll be using __Postman__. The steps I took to create the localhost API, set up the libraries and run tests are:

* Install Flask and all packages needed instructed in https://www.geeksforgeeks.org/using-jwt-for-user-authentication-in-flask/ .
* Create a file named app.py for Flask.
* Write code in app.py.
* Run the terminal command _> flask run_ to run the server.
* Open Postman and create a collection, environment and requests.
* Run the requests and check the responses.

You can also use Newman to run the automated tests in terminal:

* Install the prerequisites Node.js and npm.
* Install Newman.
* To run the automated test with Newman run the command _> newman run (Postman collection)_ where Postman collection is the exported project.
