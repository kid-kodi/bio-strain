# app/__init__.py

# third-party imports
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads

import flask_excel as excel
from elasticsearch import Elasticsearch
from flask_babel import Babel, lazy_gettext as _l
# from redis import Redis
# import rq

# local imports
from config import Config

db = SQLAlchemy()
login = LoginManager()
babel = Babel()
images = UploadSet('images', IMAGES)


def create_app(config_name=Config):
    app = Flask(__name__)
    app.config.from_object(config_name)

    Bootstrap(app)
    db.init_app(app)
    login.init_app(app)
    login.login_message = "You must be logged in to access this page."
    login.login_view = "auth.login"
    migrate = Migrate(app, db)
    excel.init_excel(app)
    configure_uploads(app, images)
    babel.init_app(app)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.task_queue = rq.Queue('bio-strain-tasks', connection=app.redis)

    from .category import bp as category_bp
    app.register_blueprint(category_bp)

    from .customer import bp as customer_bp
    app.register_blueprint(customer_bp)

    from app.origin import bp as origin_bp
    app.register_blueprint(origin_bp)

    from .role import role as role_bp
    app.register_blueprint(role_bp)

    from app.strain import bp as strain_bp
    app.register_blueprint(strain_bp)

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .user import user as user_bp
    app.register_blueprint(user_bp)

    from .frame import bp as frame_bp
    app.register_blueprint(frame_bp)

    from app.strain_type import bp as strain_type_bp
    app.register_blueprint(strain_type_bp)

    from app.sample_type import bp as sample_type_bp
    app.register_blueprint(sample_type_bp)

    from app.phenotype import bp as phenotype_bp
    app.register_blueprint(phenotype_bp)

    from app.room import bp as room_bp
    app.register_blueprint(room_bp)

    from app.equipment_type import bp as equipment_type_bp
    app.register_blueprint(equipment_type_bp)

    from app.equipment import bp as equipment_bp
    app.register_blueprint(equipment_bp)

    from app.rack import bp as rack_bp
    app.register_blueprint(rack_bp)

    from app.box_type import bp as box_type_bp
    app.register_blueprint(box_type_bp)

    from app.box import bp as box_bp
    app.register_blueprint(box_bp)

    from app.basket import bp as basket_bp
    app.register_blueprint(basket_bp)

    from app.store import bp as store_bp
    app.register_blueprint(store_bp)

    from app.order import bp as order_bp
    app.register_blueprint(order_bp)

    return app


from app import models
