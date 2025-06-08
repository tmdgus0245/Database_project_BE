class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:millionwhitesu04@localhost:5432/RunCrewProject"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"
