import random
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import *
from datetime import datetime, timedelta
from sqlalchemy import text

# app = create_app()
# app.app_context().push()

# MySQL DB 연결 설정
DATABASE_URI = "postgresql+psycopg2://postgres:millionwhitesu04@localhost:5432/RunCrewProject"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

# Faker 인스턴스 생성
fake = Faker('ko_KR')

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

seoul_dongs = {
    '종로구': ['청운동', '신교동', '궁정동', '효자동', '창성동', '통의동', '통인동', '누상동', '누하동', '옥인동'],
    '중구': ['소공동', '회현동', '명동', '충무로1가', '을지로1가', '을지로2가', '남대문로5가', '예장동', '필동', '장충동1가'],
    '용산구': ['후암동', '용산동2가', '남영동', '동자동', '서계동', '청파동1가', '원효로1가', '효창동', '용문동', '문배동'],
    '성동구': ['왕십리도선동', '마장동', '홍익동', '사근동', '행당동', '응봉동', '금호1가동', '옥수동', '성수1가1동', '성수2가1동'],
    '광진구': ['중곡1동', '중곡2동', '중곡3동', '중곡4동', '능동', '구의1동', '구의2동', '구의3동', '광장동', '자양1동'],
    '동대문구': ['용신동', '제기동', '전농1동', '답십리1동', '답십리2동', '장안1동', '장안2동', '청량리동', '회기동', '휘경1동'],
    '중랑구': ['면목본동', '면목2동', '면목3·8동', '면목4동', '면목5동', '면목7동', '상봉1동', '상봉2동', '중화1동', '중화2동'],
    '성북구': ['성북동', '삼선동', '동선동', '돈암1동', '돈암2동', '안암동', '보문동', '정릉1동', '정릉2동', '정릉3동'],
    '강북구': ['삼양동', '미아동', '송중동', '송천동', '삼각산동', '번1동', '번2동', '번3동', '수유1동', '수유2동'],
    '도봉구': ['쌍문1동', '쌍문2동', '쌍문3동', '쌍문4동', '방학1동', '방학2동', '방학3동', '창1동', '창2동', '창3동'],
    '노원구': ['월계1동', '월계2동', '월계3동', '공릉1동', '공릉2동', '하계1동', '하계2동', '중계본동', '중계1동', '중계2·3동'],
    '은평구': ['녹번동', '불광1동', '불광2동', '갈현1동', '갈현2동', '구산동', '대조동', '응암1동', '응암2동', '응암3동'],
    '서대문구': ['충현동', '천연동', '북아현동', '신촌동', '연희동', '홍제1동', '홍제2동', '홍제3동', '홍은1동', '홍은2동'],
    '마포구': ['아현동', '공덕동', '도화동', '용강동', '대흥동', '염리동', '신수동', '서강동', '합정동', '망원1동'],
    '양천구': ['목1동', '목2동', '목3동', '목4동', '목5동', '신월1동', '신월2동', '신월3동', '신월4동', '신월5동'],
    '강서구': ['염창동', '등촌1동', '등촌2동', '등촌3동', '화곡본동', '화곡1동', '화곡2동', '화곡3동', '화곡4동', '화곡6동'],
    '구로구': ['신도림동', '구로1동', '구로2동', '구로3동', '구로4동', '구로5동', '가리봉동', '고척1동', '고척2동', '개봉1동'],
    '금천구': ['가산동', '독산1동', '독산2동', '독산3동', '독산4동', '시흥1동', '시흥2동', '시흥3동', '시흥4동', '시흥5동'],
    '영등포구': ['여의동', '당산1동', '당산2동', '도림동', '문래동', '양평1동', '양평2동', '신길1동', '신길3동', '신길4동'],
    '동작구': ['노량진1동', '노량진2동', '상도1동', '상도2동', '상도3동', '상도4동', '흑석동', '사당1동', '사당2동', '사당3동'],
    '관악구': ['보라매동', '청림동', '성현동', '행운동', '낙성대동', '청룡동', '은천동', '중앙동', '인헌동', '남현동'],
    '서초구': ['서초1동', '서초2동', '서초3동', '서초4동', '잠원동', '반포본동', '반포1동', '반포2동', '반포3동', '반포4동'],
    '강남구': ['신사동', '논현1동', '논현2동', '압구정동', '청담동', '삼성1동', '삼성2동', '대치1동', '대치2동', '역삼1동'],
    '송파구': ['풍납1동', '풍납2동', '거여1동', '거여2동', '마천1동', '마천2동', '방이1동', '방이2동', '오륜동', '오금동'],
    '강동구': ['강일동', '상일1동', '상일2동', '명일1동', '명일2동', '고덕1동', '고덕2동', '암사1동', '암사2동', '암사3동']
}

def main():
    # SQLAlchemy 세션 생성
    session = Session()
    
    print("Deleting existing data...")

    # 1. 리뷰 먼저 삭제 (Crew 참조)
    session.query(Review).delete()

    # 2. 크루 관련 로그 삭제
    session.query(CrewRunLog).delete()
    session.query(CrewMember).delete()
    session.query(CrewNotice).delete()  
    session.query(Crew).delete()

    # 3. 사용자 관련 로그, 포스트, 좋아요 삭제
    session.query(PostLike).delete()
    session.query(Post).delete()
    session.query(UserRunLog).delete()

    # 4. 사용자 삭제
    session.query(User).delete()
    session.commit()
    print("Old data deleted.")


    # 시퀀스 리셋
    for seq in sequences:
        session.execute(text(f'ALTER SEQUENCE {seq} RESTART WITH 1;'))
    session.commit()
    print("User ID sequence reset.")

    try:

        #user 더미데이터 생성
        users = []
        for i in range(1, 51):
            gu = random.choice(list(seoul_dongs.keys()))    
            dong = random.choice(seoul_dongs[gu])
            region = f"{gu} {dong}"
            user = User(
                nickname=fake.name(),
                region=region,
            )
            users.append(user)
            session.add(user)
        session.commit()
        users = session.query(User).all()
        print("User inserted")

        #crew 더미데이터 생성
        crews = []
        for _ in range(10):
            gu = random.choice(list(seoul_dongs.keys()))
            dong = random.choice(seoul_dongs[gu])
            region = f"{gu} {dong}"

            crew = Crew(
                name=fake.word(),
                description=fake.text(),
                region=region,
                created_by=random.choice(users).user_id
            )
            crews.append(crew)
            session.add(crew)
        session.commit()
        crews = session.query(Crew).all()
        print("Crews inserted")

        #CrewRunLog 더미데이터 생성
        for crew in crews:
            for _ in range(random.randint(1, 3)):
                run_log = CrewRunLog(
                    crew_id=crew.crew_id,
                    date=fake.date_this_year(),
                    title=fake.word(),
                    distance_km=round(random.uniform(5, 20), 2),
                    duration_min=random.randint(30, 150),
                    avg_pace=round(random.uniform(5, 7), 2),
                    photo_url=fake.image_url(),
                    notes=fake.sentence(),
                    created_by=random.choice(users).user_id
                )
                session.add(run_log)
        session.commit()
        print("CrewRunLogs inserted")    

        #UserRunLog 더미데이터 생성
        for user in users:
            for _ in range(random.randint(1, 5)):
                run_log = UserRunLog(
                    user_id=user.user_id,
                    date=fake.date_this_year(),
                    distance_km=round(random.uniform(3, 15), 2),
                    duration_min=random.randint(20, 120),
                    pace=round(random.uniform(5, 8), 2)
                )
                session.add(run_log)
        session.commit()
        print("UserRunLogs inserted")

        #Post 더미데이터 생성
        for user in users:
            for _ in range(random.randint(1, 3)):
                post = Post(
                    user_id=user.user_id,
                    type=random.choice([PostTypeEnum.인증글, PostTypeEnum.코스추천]),
                    title=fake.sentence(),
                    content=fake.text(),
                    image_url=fake.image_url()
                )
                session.add(post)
        session.commit()
        print("Posts inserted")

        #Crew 더미데이터 생성
        for crew in crews:
            crew_leader_member = CrewMember(
                crew_id=crew.crew_id,
                user_id=crew.created_by,
                join_date=fake.date_this_year()
            )
            session.add(crew_leader_member)

            possible_members = [u for u in users if u.user_id != crew.created_by]
            members_in_crew = random.sample(possible_members, random.randint(5, 10))
            for user in members_in_crew:
                crew_member = CrewMember(
                    crew_id=crew.crew_id,
                    user_id=user.user_id,
                    join_date=fake.date_this_year()
                )
                session.add(crew_member)

        session.commit()
        print("CrewMembers inserted")

        #PostLike 더미데이터 생성
        posts = session.query(Post).all()
        for post in posts:
            like_users = random.sample(users, random.randint(0, 10))
            for user in like_users:
                if not session.query(PostLike).filter_by(post_id=post.post_id, user_id=user.user_id).first():
                    like = PostLike(
                        post_id=post.post_id,
                        user_id=user.user_id
                    )
                    session.add(like)

        session.commit()
        print("PostLikes inserted")

        #Review 더미데이터 생성
        created_pairs = set()

        for _ in range(200):  
            user = random.choice(users)
            crew = random.choice(crews)
            pair = (user.user_id, crew.crew_id)

            if pair in created_pairs:
                continue  

            created_pairs.add(pair)

            review = Review(
                user_id=user.user_id,
                crew_id=crew.crew_id,
                rating=random.randint(1, 5),
                comment=fake.sentence()
            )
            session.add(review)

        session.commit()
        print("Reviews inserted")

        # 커밋
        session.commit()
        print("Dummy data inserted successfully")

    except Exception as e:
        # 오류 발생 시 롤백
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        # 세션 닫기
        session.close()

if __name__ == "__main__":
    main()