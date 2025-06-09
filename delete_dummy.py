# clear_dummy_data.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import *

DATABASE_URI = "postgresql+psycopg2://postgres:millionwhitesu04@localhost:5432/RunCrewProject"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

# 시퀀스 리스트
sequences = [
    '"User_user_id_seq"',
    '"Crew_crew_id_seq"',
    '"Post_post_id_seq"',
    '"Review_review_id_seq"',
    '"UserRunLog_user_log_id_seq"',
    '"CrewRunLog_crew_log_id_seq"',
    '"PostLike_post_like_id_seq"',
    '"SportsEvent_event_id_seq"',
    '"SportsEventLog_event_log_id_seq"'
]

def delete_dummy_data():
    session = Session()
    try:
        print("Deleting existing dummy data...")

        # 참조 순서 고려한 삭제 (자식 → 부모)
        session.query(Review).delete()
        session.query(PostLike).delete()
        session.query(CrewRunLog).delete()
        session.query(UserRunLog).delete()
        session.query(CrewMember).delete()
        session.query(CrewNotice).delete()
        session.query(Post).delete()
        session.query(Crew).delete()
        session.query(User).delete()
        session.commit()
        print("Data deleted successfully.")

        # 시퀀스 초기화
        print("Resetting sequences...")
        for seq in sequences:
            session.execute(text(f'ALTER SEQUENCE {seq} RESTART WITH 1;'))
        session.commit()
        print("Sequences reset.")

    except Exception as e:
        session.rollback()
        print(f"Error while clearing data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    delete_dummy()
