from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from trackyr.config import Config
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app,db)

    from trackyr.main.routes import main
    from trackyr.sources.routes import sources
    from trackyr.notification_agents.routes import notification_agents
    from trackyr.tasks.routes import tasks
    from trackyr.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(sources)
    app.register_blueprint(notification_agents)
    app.register_blueprint(tasks)
    app.register_blueprint(errors)

    return app