class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:millionwhitesu04@localhost:5432/RunCrewProject"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"

# 예시 (MySQL 로컬 서버 사용 시)
# username: root, password: password123, database: parking_app
# SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:password123@localhost:3306/parking_app"