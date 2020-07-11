from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from trackyr.config import Config
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_colorpicker import colorpicker
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    CSRFProtect(app)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app,db)
    Bootstrap(app)
    colorpicker(app)

    from trackyr.main.routes import main
    from trackyr.sources.routes import sources
    from trackyr.notification_agents.routes import notification_agents
    from trackyr.tasks.routes import tasks
    from trackyr.trackyr_config.routes import trackyr_config
    from trackyr.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(sources)
    app.register_blueprint(notification_agents)
    app.register_blueprint(tasks)
    app.register_blueprint(trackyr_config)
    app.register_blueprint(errors)
    return app