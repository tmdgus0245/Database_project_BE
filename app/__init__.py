from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.trigger import register_triggers  # 트리거 등록 함수
from app.views import create_views  # 뷰 생성 함수 가져오기

db = SQLAlchemy()  # Flask-SQLAlchemy 초기화

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)  # 앱과 db 객체를 연결

    # CORS 설정
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    with app.app_context():
        from .routes import bp
        from . import models
        print("Creating all tables...")

        # 테이블 생성
        db.create_all()
        print("Table created!")

        # # 트리거 등록
        # register_triggers(db)

        # # 뷰 생성
        # create_views(db)

        # 블루프린트 등록
        app.register_blueprint(bp)

    return app