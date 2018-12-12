from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, login_required
from flask_admin import Admin
from flask_marshmallow import Marshmallow


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'Muahahahaha'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = '$2a$16$PnnIgfMwkOjGX4SkHqSO'
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'HTTP_AUTHORIZATION'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='estoque', template_mode='bootstrap3')


api = Api(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)


from models import *
from users import *
from resources import *

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


#@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='v@v.c', password='123')
    db.session.commit()


@app.route('/')
@login_required
def home():
    return "<h1>Muahahahaha</h1>"


if __name__ == '__main__':
    app.run(debug=True)


