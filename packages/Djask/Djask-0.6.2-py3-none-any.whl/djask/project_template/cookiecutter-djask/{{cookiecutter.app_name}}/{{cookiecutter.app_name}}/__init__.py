{%- set name= cookiecutter.app_name -%}
import os
from importlib import import_module
from pathlib import Path
from djask import Djask
from .settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")
    app = Djask("{{ name }}", config=config[config_name])
    register_blueprints(app)
    return app


def register_blueprints(app: Djask):
    # you can change these lines of codes to manually import your blueprints
    os.chdir("{{ name }}")
    for child in Path('.').iterdir():
        if child.is_dir() and (child / "__init__.py").is_file():
            module = import_module(f".{child}.views", "{{ name }}")
            app.register_blueprint(
                getattr(module, f"{child}_bp")
            )
