# backend/app.py

import os
from flask import Flask
from .config import config as config_map
from .extensions import db

def create_app():
    app = Flask(__name__)

    env = os.environ.get("CDB_ENV", "dev")
    app.config.from_object(config_map.get(env, config_map["dev"]))

    db.init_app(app)

    with app.app_context():
        from .routes_public import public
        from .routes_admin import admin
        from .routes_auth import auth      # 🔥 NEW

        app.register_blueprint(public)
        app.register_blueprint(admin)
        app.register_blueprint(auth)       # 🔥 NEW

        @app.cli.command("init-db")
        def init_db():
            from .models import Campaign, Target, Event
            db.create_all()
            print("Database initialized.")

    return app

app = create_app()
