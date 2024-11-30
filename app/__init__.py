from flask import Flask , request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect

def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

db = SQLAlchemy()


def create_app():

    app = Flask(__name__)
        


    app.config.from_object('config')
    db.init_app(app)


    csrf = CSRFProtect(app)

    babel = Babel(app, locale_selector=get_locale)
    admin = Admin(app,template_mode='bootstrap4')


    
    migrate = Migrate(app,db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User, Trip, Destination, trip_destination

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Trip, db.session))
    admin.add_view(ModelView(Destination, db.session))


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #ive done this to improve modularity and make it so i can seperate my functions so its not too crodded
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,  url_prefix='/auth')

    from .views import views as views_blueprint
    app.register_blueprint(views_blueprint)

    from .functions import functions as functions_blueprint
    app.register_blueprint(functions_blueprint)

    

    return app

