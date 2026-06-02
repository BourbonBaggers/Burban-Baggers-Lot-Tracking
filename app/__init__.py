from pathlib import Path

from flask import Flask

from app.config import Config
from app.extensions import db
from app.routes import main


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    app.register_blueprint(main)

    return app
