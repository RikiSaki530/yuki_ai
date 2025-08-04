# app/routes/__init__.py

from flask import Blueprint

# 各Blueprintを読み込む
from .main import main_bp
from .survey import survey_bp
from .result import result_bp

def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(result_bp)
