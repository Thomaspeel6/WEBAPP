


from .forms import LoginForm, SignupForm
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

auth = Blueprint('auth', __name__)


#checking whether cookies are accepted
@auth.route('/accept-cookies', methods=['POST'])
def accept_cookies():
    session['cookies_accepted'] = True
    return jsonify({'message': 'Cookies accepted!'}), 200


#login form, allows user to login with email or username
@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    signup_form = SignupForm()  # Ensure this form is also passed so the singup form can be rednered 

    if login_form.validate_on_submit():
        email_or_username = login_form.email_or_username.data
        password = login_form.password.data
        remember = login_form.remember.data

        #  user by email or username
        user = User.query.filter(
            or_(
                User.email == email_or_username,
                User.username == email_or_username
            )
        ).first()

        #veryinge the user credentials
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return render_template('welcome.html', signup_form=signup_form, login_form=login_form, show_login=True)

        #login user and set session
        login_user(user, remember=remember)


        #cookies so they dont have to contasnlty login when hte pages changes
        session['user_id'] = user.id
        session['user_username'] = user.username
        session['user_email'] = user.email
        session['logged_in'] = True


        return redirect(url_for('views.homepage'))

    # Return for non-valid form submission
    return render_template('welcome.html', signup_form=signup_form, login_form=login_form, show_login=True)

#signup form 
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    login_form = LoginForm()  #ensuring both forms are created fo same reason above 
    signup_form = SignupForm()

    if signup_form.validate_on_submit():
        username = signup_form.username.data
        email = signup_form.email.data
        name = signup_form.name.data
        password = signup_form.password.data

        #checking if extint username o email as theya re uniqure fields
        existing_user = User.query.filter(
            or_(
                User.email == email,
                User.username == username
            )
        ).first()
        
        #client side feedback
        if existing_user:
            if existing_user.email == email:
                flash('Email address already exists')
            elif existing_user.username == username:
                flash('Username already exists')
            return render_template('welcome.html', signup_form=signup_form, login_form=login_form, show_signup=True)

            
        #create the new user  new user
        new_user = User(
            username=username,
            email=email,
            name=name,
            password=generate_password_hash(password, method='pbkdf2:sha256') #hashing passwoerd for security
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Successfully signed up')
        return redirect(url_for('views.welcome'))  #redirecting to login after successful signup
    
    return render_template('welcome.html', login_form=login_form, signup_form=signup_form, show_signup=True)


@auth.route('/logout')
def logout():
    session.clear()  #clearing all session cookies
    logout_user()    #loggin out the user from the falsk and returning them back to the welocme page 
    return redirect(url_for('views.welcome'))