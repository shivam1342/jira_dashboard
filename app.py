from flask import Flask, redirect, url_for
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.manager_routes import manager_bp
from routes.developer_routes import developer_bp
from routes.admin_routes import admin_bp
from routes.visitor_routes import visitor_bp
from flask import session
from models import db
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from routes.common_routes import common_bp
from flask_mailman import Mail

from dotenv import load_dotenv
import os
# Load .env
load_dotenv()


app = Flask(__name__)
app.secret_key = 'azrdfhb'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = 'zerdragneel400@gmail.com',
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
)

mail = Mail(app)


db.init_app(app)
migrate = Migrate(app, db)


# with app.app_context():
#     db.create_all()



app.register_blueprint(common_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(manager_bp)
app.register_blueprint(developer_bp, url_prefix='/developer')
app.register_blueprint(admin_bp)
app.register_blueprint(visitor_bp)



@app.route('/')
def index():
    return redirect(url_for('auth.login_page')) 

if __name__ == "__main__":
    app.run(debug=True)
