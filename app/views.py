from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

def create_views(db):
    pass

#크루별 최근 1개월 러닝 집계
#사용자별 주간 활동 랭킹
#크루별 좋아요 많은 게시글
#전체 크루 인기 순위
