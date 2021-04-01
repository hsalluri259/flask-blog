# flask-blog
# Before starting, follow this page to install flask in a virtual environment. 
https://flask.palletsprojects.com/en/1.1.x/installation/#install-activate-env

# set the following environment variables before running app. 
$ export FLASK_ENV=development  
$ export FLASK_APP=flaskr

# To run the flask app
$ python -m flask run  
(OR)  
$ flask run  

# To Run the init-db command:
$ flask init-db  
Initialized the database.

# Install the Project
Use pip to install your project in the virtual environment.
$ pip install -e . 

This tells pip to find setup.py in the current directory and install it in editable or development mode. Editable mode means that as you make changes to your local code, you’ll only need to re-install if you change the metadata about the project, such as its dependencies.

You can observe that the project is now installed with pip list.