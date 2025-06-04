import enum
from . import db
from datetime import datetime
from sqlalchemy import Enum

# ENUM 타입 정의
class PostTypeEnum(enum.Enum):
    인증글 = '인증글'
    코스추천 = '코스추천'

# 사용자
class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(30), nullable=False)
    region = db.Column(db.String(50), nullable=False)

# 크루
class Crew(db.Model):
    __tablename__ = 'Crew'
    crew_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    region = db.Column(db.String(50))
    created_by = db.Column(db.Integer, db.ForeignKey('User.user_id'))

# 리뷰
class Review(db.Model):
    __tablename__ = 'Review'
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    crew_id = db.Column(db.Integer, db.ForeignKey('Crew.crew_id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

# 크루 멤버
class CrewMember(db.Model):
    __tablename__ = 'CrewMember'
    crew_id = db.Column(db.Integer, db.ForeignKey('Crew.crew_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), primary_key=True)
    join_date = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='crew_memberships')
    crew = db.relationship('Crew', backref='memberships')

# 게시글
class Post(db.Model):
    __tablename__ = 'Post'
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    type = db.Column(db.Enum(PostTypeEnum), nullable=False)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    image_url = db.Column(db.Text)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# 사용자 러닝 기록
class UserRunLog(db.Model):
    __tablename__ = 'UserRunLog'
    user_log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    date = db.Column(db.Date)
    distance_km = db.Column(db.Float)
    duration_min = db.Column(db.Integer)
    pace = db.Column(db.Float)

# 크루 러닝 기록
class CrewRunLog(db.Model):
    __tablename__ = 'CrewRunLog'
    crew_log_id = db.Column(db.Integer, primary_key=True)
    crew_id = db.Column(db.Integer, db.ForeignKey('Crew.crew_id'))
    date = db.Column(db.Date)
    title = db.Column(db.String(100))
    distance_km = db.Column(db.Float)
    duartion_min = db.Column(db.Integer)
    avg_pace = db.Column(db.Float)
    photo_url = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

#크루 공지사항
class CrewNotice(db.Model):
    __tablename__ = 'CrewNotice'
    notice_id = db.Column(db.Integer, primary_key=True)
    crew_id = db.Column(db.Integer, db.ForeignKey('Crew.crew_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    crew = db.relationship('Crew', backref=db.backref('notices', lazy=True))

# 체육 행사
class SportsEvent(db.Model):
    __tablename__ = 'SportsEvent'
    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    host = db.Column(db.String(100))
    location = db.Column(db.String(100))
    date = db.Column(db.Date)
    apply_url = db.Column(db.Text)
    description = db.Column(db.Text)
    region = db.Column(db.String(50))

# 체육 행사 참여 기록
class SportsEventLog(db.Model):
    __tablename__ = 'SportsEventLog'
    event_log_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('SportsEvent.event_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    joined_at = db.Column(db.DateTime, server_default=db.func.now())
    feedback = db.Column(db.Text)
    ranking = db.Column(db.Integer)

# 게시글 좋아요
class PostLike(db.Model):
    __tablename__ = 'PostLike'
    post_like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('Post.post_id'))
    liked_at = db.Column(db.DateTime, server_default=db.func.now())
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
