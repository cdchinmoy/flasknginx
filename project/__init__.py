from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate, MigrateCommand

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'thisissecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345678@database-1.ci8mswb2d1o2.ap-south-1.rds.amazonaws.com:5432/mydb"
    
    db.init_app(app)
    migrate.init_app(app, db)

    from project.routes.user import user_bp
    app.register_blueprint(user_bp, url_prefix="/user")

    from project.routes.seller import seller_bp
    app.register_blueprint(seller_bp, url_prefix="/seller")

    ### swagger specific ###
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "CMDs-Python-Flask-REST-API"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    ### end swagger specific ###

    return app
