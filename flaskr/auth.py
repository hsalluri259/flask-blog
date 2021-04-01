"""Create a blueprint."""
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# associates the /register url with register view function. When Flask receives a request to /auth/register, 
# it will call the register view and use the return value as the response.
@bp.route('register', methods=('GET', 'POST'))
def register():
    # If the user submitted the form, request.method will be 'POST'. In this case, start validating the input.
    if request.method == 'POST':
        # request.form is a special type of dict mapping submitted form keys and values. 
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # validate if username is not empty
        if not username:
            error = 'Username is required!'
        # validate if password is not empty
        elif not password:
            error = 'Password is required!'
        # validate if username is not already registered
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        
        # When no error then insert the new user data into database. For security, passwords should never be
        # stored in the database directly. Instead, generate_password_hash() is used to securely hash the password,
        # and that hash is stored. commit db, and redirect url to login.
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            # Redirect to the login page after storing user. url_gor() generates the url for the login view
            # based on its name. This is preferable to writing URL directly as it allows you to change to URL later 
            # without changing all code that links to it. redirect() generates a redirect response to the generated URL. 
            return redirect(url_for('auth.login'))

        # if validation fails, the error is shown to user. flash() stores messages that can be retrieved when rendering the template.
        flash(error)
    # When the user initially navigates to auth/register, or there was a validation error, an HTML page with the registration form should be shown. 
    # render_template() will render a template containing the HTML
    return render_template('auth/register.html')


# This view follows the same pattern as the register view above.
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':    
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # The user is queried first to later use.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        #check_password_hash() hashes the submitted password in the same way as the stored hash and securely compares them. 
        # If they match, the password is valid.
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'
        
        if error is None:
            # session is a dict that stores data across requests. When validation succeeds, the user’s id is stored in a new session. 
            # The data is stored in a cookie that is sent to the browser, and the browser then sends it back with subsequent requests. 
            # Flask securely signs the data so that it can’t be tampered with.
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
        
    return render_template('auth/login.html')

# bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested.
@bp.before_app_request
def load_logged_in_user():
    """load_logged_in_user checks if a user id is stored in the session and gets that user’s data from the database,
        storing it on g.user, which lasts for the length of the request. 
        If there is no user id, or if the id doesn’t exist, g.user will be None.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# To log out, you need to remove the user id from the session. 
# Then load_logged_in_user won’t load a user on subsequent requests.
@bp.route('/logout')
def logout():
    """Logout when user clicks on logout button."""
    session.clear()

    return redirect(url_for('index'))

# Require Authentication in Other Views
# Creating, editing, and deleting blog posts will require a user to be logged in. 
# A decorator can be used to check this for each view it’s applied to.
# This decorator returns a new view function that wraps the original view it’s applied to.
# The new function checks if a user is loaded and redirects to the login page otherwise. If a user is loaded the original view is called and continues normally. You’ll use this decorator when writing the blog views.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view