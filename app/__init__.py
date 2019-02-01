import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from elasticsearch import Elasticsearch
# from redis import Redis
# import rq
from config import Config
import flask_excel as excel
from flask_uploads import UploadSet, IMAGES, configure_uploads

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()
documents = UploadSet('documents')


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    excel.init_excel(app)
    configure_uploads(app, documents)
    babel.init_app(app)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

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

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

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

    from app.expedition import bp as expedition_bp
    app.register_blueprint(expedition_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1.0')

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='BioBank Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/bio-strain.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('BioBank startup')

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models
