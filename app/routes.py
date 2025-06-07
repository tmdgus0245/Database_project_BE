from flask import Blueprint, jsonify, request
from . import db
from .models import *
import requests
from datetime import datetime

bp = Blueprint('routes', __name__)

SECRET_KEY = "0uBbt1XG1OmknhgQnJDfxV9ocGXVtEIafDg0BGqpMYYBQRDpzqdT0S+WnQJqCJNaV4Xt1BSCMQJaXl6GTZFRAA=="
URL = "https://api.odcloud.kr/api/15138980/v1/uddi:eedc77c5-a56b-4e77-9c1d-9396fa9cc1d3"
FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/marathon365-4aecd/databases/(default)/documents/events_1740110415044"

######################################
# 크루 관련 엔드포인트
######################################

#크루 탐색 : 크루 목록 조회
@bp.route('/api/crews_search', methods=['GET'])
def get_crews():
    try:
        # 모든 크루 가져오기
        crews = Crew.query.all()
        
        # 결과를 JSON 형식으로 구성
        result = [
            {
                "crew_leader": crew.created_by,
                "crew_id": crew.crew_id,
                "name": crew.name,
                "region": crew.region
            }
            for crew in crews
        ]
        
        return jsonify(result), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루별 페이지
@bp.route('/api/crews/<int:crew_id>', methods=['GET'])
def get_crew_detail(crew_id):
    try:
        # 크루 가져오기
        crew = Crew.query.get(crew_id)
        if not crew:
            return jsonify({"error": "Crew not found"}), 404

        leader = User.query.get(crew.created_by)
        leader_nickname = leader.nickname if leader else "Unknown"

        # 리뷰들 가져오기
        reviews = Review.query.filter_by(crew_id=crew_id).all()
        review_list = [
            {
                "review_id": review.review_id,
                "user_id": review.user_id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for review in reviews
        ]

        result = {
            "crew_id": crew.crew_id,
            "leader": leader_nickname,
            "name": crew.name,
            "region": crew.region,
            "description": crew.description,
            "reviews": review_list
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#크루원 조회
@bp.route('/api/crews/<int:crew_id>/crew_member', methods=['GET'])
def get_crew_member(crew_id):
    try:
        # 해당 크루의 멤버들 조회
        crew_members = CrewMember.query.filter_by(crew_id=crew_id).all()
        
        result = [
            {
                "user_id": member.user_id,
                "nickname": member.user.nickname,
                "join_date": member.join_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            for member in crew_members
        ]

        return jsonify(result), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 런닝기록 조회
@bp.route('/api/crews/<int:crew_id>/crew_run_log', methods=['GET'])
def get_crew_run_log(crew_id):
    try:
        # 해당 크루의 런닝 기록들 가져오기
        run_logs = CrewRunLog.query.filter_by(crew_id=crew_id).all()

        result = [
            {
                "log_id": log.crew_log_id,
                "title": log.title,
                "date": log.date.strftime('%Y-%m-%d'),
                "distance_km": log.distance_km,
                "duration_min": log.duration_min,
                "avg_pace": log.avg_pace,
                "photo_url": log.photo_url,
                "notes": log.notes,
                "created_by": log.created_by
            }
            for log in run_logs
        ]

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 런닝기록 등록
@bp.route('/api/crews/<int:crew_id>/crew_run_log', methods=['POST'])
def post_crew_run_log(crew_id):
    data = request.get_json()
    user_id = data.get('user_id')  # 요청한 사용자 ID

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        # 해당 크루 정보 가져오기
        crew = Crew.query.get(crew_id)
        if not crew:
            return jsonify({"error": "Crew not found"}), 404

        # 권한 체크: 요청한 user_id가 이 크루의 created_by인지 확인
        if crew.created_by != user_id:
            return jsonify({"error": "Permission denied. Only crew leader can register run logs."}), 403

        # 필요한 필드들 가져오기
        title = data.get('title')
        distance_km = data.get('distance_km')
        duration_min = data.get('duration_min')
        avg_pace = data.get('avg_pace')
        photo_url = data.get('photo_url')
        notes = data.get('notes')
        date_str = data.get('date')
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            date = datetime.now().date()

        # 필수 값 검증
        if not title or not distance_km or not duration_min or not avg_pace:
            return jsonify({"error": "Missing required fields"}), 400

        # 새로운 런닝 기록 생성
        new_log = CrewRunLog(
            crew_id=crew_id,
            title=title,
            date=date,  # 오늘 날짜로 등록
            distance_km=distance_km,
            duration_min=duration_min,
            avg_pace=avg_pace,
            photo_url=photo_url,
            notes=notes,
            created_by=user_id,
            created_at=datetime.now()
        )

        db.session.add(new_log)
        db.session.commit()

        return jsonify({"message": "Crew run log created successfully", "log_id": new_log.crew_log_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


#크루 공지사항 조회
@bp.route('/api/crews/<int:crew_id>/crew_notice', methods=['GET'])
def get_crew_notice(crew_id):
    try:
        # 해당 크루의 공지사항들 가져오기
        notices = CrewNotice.query.filter_by(crew_id=crew_id).order_by(CrewNotice.created_at.desc()).all()

        result = [
            {
                "notice_id": notice.notice_id,
                "title": notice.title,
                "content": notice.content,
                "created_at": notice.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for notice in notices
        ]

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 공지사항 게시
@bp.route('/api/crews/<int:crew_id>/crew_notice', methods=['POST'])
def post_crew_notice(crew_id):
    data = request.get_json()
    user_id = data.get('user_id')  # 작성자 ID
    title = data.get('title')
    content = data.get('content')

    # 필수 값 검증
    if not user_id or not title or not content:
        return jsonify({"error": "user_id, title, content are required"}), 400

    try:
        # 해당 크루 가져오기
        crew = Crew.query.get(crew_id)
        if not crew:
            return jsonify({"error": "Crew not found"}), 404

        # 권한 체크: 작성자가 크루장인지 확인
        if crew.created_by != user_id:
            return jsonify({"error": "Permission denied. Only the crew leader can post notices."}), 403

        # 공지사항 생성
        new_notice = CrewNotice(
            crew_id=crew_id,
            title=title,
            content=content,
            created_at=datetime.now()
        )

        db.session.add(new_notice)
        db.session.commit()

        return jsonify({"message": "Crew notice posted successfully", "notice_id": new_notice.notice_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 생성
@bp.route('/api/crews_make', methods=['POST'])
def create_crew():
    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    region = data.get('region')
    created_by = data.get('created_by')

    # 필수값 체크
    if not name or not created_by:
        return jsonify({"error": "name and created_by are required"}), 400

    try:
        new_crew = Crew(
            name=name,
            description=description,
            region=region,
            created_by=created_by
        )
        db.session.add(new_crew)
        db.session.commit()

        crew_leader = CrewMember(
            crew_id=new_crew.crew_id,
            user_id=created_by,
            join_date=datetime.now()
        )
        db.session.add(crew_leader)
        db.session.commit()

        return jsonify({
            "message": "크루 생성 완료",
            "crew_id": new_crew.crew_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 가입
@bp.route('/api/crews/<int:crew_id>/join', methods=['POST'])
def join_crew(crew_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        # 크루 존재 여부 확인
        crew = Crew.query.get(crew_id)
        if not crew:
            return jsonify({"error": "Crew not found"}), 404

        # 이미 가입되어 있는지 확인
        existing_member = CrewMember.query.filter_by(crew_id=crew_id, user_id=user_id).first()
        if existing_member:
            return jsonify({"error": "User already joined this crew"}), 400

        # 가입 처리
        new_member = CrewMember(
            crew_id=crew_id,
            user_id=user_id,
            join_date=datetime.now()
        )
        db.session.add(new_member)
        db.session.commit()

        return jsonify({"message": f"Crew {crew_id} joined successfully", "user_id": user_id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 탈퇴
@bp.route('/api/crews/<int:crew_id>/leave', methods=['POST'])
def leave_crew(crew_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        crew_member = CrewMember.query.filter_by(crew_id=crew_id, user_id=user_id).first()
        if not crew_member:
            return jsonify({"error": "User is not a member of this crew"}), 404

        db.session.delete(crew_member)
        db.session.commit()

        return jsonify({"message": f"User {user_id} has left crew {crew_id}"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 리뷰 등록
@bp.route('/api/crews/<int:crew_id>/reviews', methods=['POST'])
def post_crew_review(crew_id):
    data = request.get_json()
    user_id = data.get('user_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not user_id or not rating:
        return jsonify({"error": "user_id와 rating은 필수입니다."}), 400

    try:
        review = Review(
            user_id=user_id,
            crew_id=crew_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()

        return jsonify({"message": f"크루 {crew_id}에 리뷰 등록 완료", "review_id": review.review_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 리뷰 삭제
@bp.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_crew_review(review_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id가 필요합니다."}), 400

    try:
        review = Review.query.get(review_id)
        if not review:
            return jsonify({"error": "리뷰를 찾을 수 없습니다."}), 404

        # 작성자 본인인지 확인
        if review.user_id != user_id:
            return jsonify({"error": "리뷰 작성자만 삭제할 수 있습니다."}), 403

        db.session.delete(review)
        db.session.commit()

        return jsonify({"message": f"리뷰 {review_id} 삭제 완료"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#크루 리뷰 조회
@bp.route('/api/crews/<int:crew_id>/reviews', methods=['GET'])
def get_crew_reviews(crew_id):
    try:
        # 해당 크루의 모든 리뷰 가져오기
        reviews = Review.query.filter_by(crew_id=crew_id).all()

        result = [
            {
                "review_id": review.review_id,
                "user_id": review.user_id,
                "nickname": review.user.nickname,  # User 모델에 nickname 관계가 있다고 가정
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for review in reviews
        ]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

######################################
# 게시글 관련 엔드포인트
######################################

#게시글 하나 상세 조회
@bp.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    try:
        post = Post.query.filter_by(post_id=post_id).first()
        if not post:
            return jsonify({"error": "Post not found"}), 404

        # 쿼리 파라미터로 유저 ID 받기
        user_id = request.args.get('user_id', type=int)

        liked = False
        if user_id:
            existing_like = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()
            liked = existing_like is not None

        result = {
            "post_id": post.post_id,
            "title": post.title,
            "content": post.content,
            "image_url": post.image_url,
            "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "like_count": post.like_count,
            "liked": liked
        }

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#러닝 코스 추천 게시글 목록 조회
@bp.route('/api/posts/course', methods=['GET'])
def get_courses():
    try:
        # PostTypeEnum.코스추천인 글들만 가져오기
        course_posts = Post.query.filter_by(type=PostTypeEnum.코스추천).all()

        result = []
        for post in course_posts:
            result.append({
                "post_id": post.post_id,
                "title": post.title,
                "author_nickname": post.user.nickname if post.user else "Unknown",
                "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "like_count": post.like_count
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#러닝 코스 추천 게시글 게시
@bp.route('/api/posts/course', methods=['POST'])
def post_course():
    data = request.get_json()

    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')
    image_url = data.get('image_url')

    # 필수값 체크
    if not user_id or not title or not content:
        return jsonify({"error": "user_id, title, content는 필수입니다."}), 400

    try:
        new_post = Post(
            user_id=user_id,
            type=PostTypeEnum.코스추천,
            title=title,
            content=content,
            image_url=image_url
        )

        db.session.add(new_post)
        db.session.commit()

        return jsonify({
            "message": "러닝 코스 추천 작성 완료",
            "post_id": new_post.post_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#러닝 코스 추천 게시글 삭제
@bp.route('/api/posts/course/<int:post_id>', methods=['DELETE'])
def delete_course(post_id):
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"error": "해당 게시글이 존재하지 않습니다."}), 404

        if post.user_id != user_id:
            return jsonify({"error": "작성자만 삭제할 수 있습니다."}), 403

        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": f"러닝 코스 추천 {post_id} 삭제 완료"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#자랑 게시글 목록 조회
@bp.route('/api/posts/brag', methods=['GET'])
def get_brag_posts():
    try:
        # PostTypeEnum.코스추천인 글들만 가져오기
        course_posts = Post.query.filter_by(type=PostTypeEnum.인증글).all()


        result = []
        for post in course_posts:
            result.append({
                "post_id": post.post_id,
                "title": post.title,
                "author_id": post.user.nickname if post.user else "Unknown",
                "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "like_count": post.like_count
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#자랑 게시글 게시
@bp.route('/api/posts/brag', methods=['POST'])
def post_brag():
    data = request.get_json()

    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')
    image_url = data.get('image_url')

    # 필수값 체크
    if not user_id or not title or not content:
        return jsonify({"error": "user_id, title, content는 필수입니다."}), 400

    try:
        new_post = Post(
            user_id=user_id,
            type=PostTypeEnum.인증글,
            title=title,
            content=content,
            image_url=image_url
        )

        db.session.add(new_post)
        db.session.commit()

        return jsonify({
            "message": "이만큼 달렸어요 작성완료",
            "post_id": new_post.post_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500    

#자랑 게시글 삭제
@bp.route('/api/posts/brag/<int:post_id>', methods=['DELETE'])
def delete_brag(post_id):
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"error": "해당 게시글이 존재하지 않습니다."}), 404

        if post.user_id != user_id:
            return jsonify({"error": "작성자만 삭제할 수 있습니다."}), 403

        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": f"이만큼 달렸어요 {post_id} 삭제 완료"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#게시글 좋아요
@bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
def post_like(post_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # 중복 좋아요 방지
    existing_like = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing_like:
        return jsonify({"message": "Already liked"}), 200

    try:
        new_like = PostLike(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()

        return jsonify({"message": "Post liked"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#게시글 좋아요 취소
@bp.route('/api/posts/<int:post_id>/like', methods=['DELETE'])
def post_unlike(post_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        like = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()
        if not like:
            return jsonify({"message": "Like not found"}), 404

        db.session.delete(like)
        db.session.commit()

        return jsonify({"message": "Post like removed"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#좋아요 수 조회
@bp.route('/api/posts/<int:post_id>/like', methods=['GET'])
def get_post_like(post_id):
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404

        return jsonify({
            "post_id": post_id,
            "like_count": post.like_count
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

######################################
# 체육 행사 관련 엔드포인트
######################################

#체옥 행사 목록 조회
@bp.route('/api/events', methods=['GET'])
def get_events():
    try:
        saved_events = []

        # 1. 공공데이터 API 요청
        odcloud_params = {
            "page": 1,
            "perPage": 50,
            "serviceKey": SECRET_KEY
        }

        odcloud_response = requests.get(URL, params=odcloud_params)
        odcloud_response.raise_for_status()
        odcloud_rows = odcloud_response.json().get("data", [])

        # 기존 SportsEvent 데이터 삭제
        SportsEvent.query.delete()
        db.session.commit()

        # 2. 공공데이터 파싱 및 저장
        for row in odcloud_rows:
            title = row.get("대회명")
            host = row.get("주최")
            location = row.get("대회장소")
            date_str = row.get("대회일시")

            if not all([title, host, location, date_str]):
                continue

            try:
                date = datetime.strptime(date_str.split("~")[0].strip(), "%Y-%m-%d")
            except:
                date = None

            event = SportsEvent(
                title=title,
                host=host,
                location=location,
                region=location,
                date=date,
                apply_url=None,
                description=None
            )
            db.session.add(event)
            saved_events.append({
                "title": title,
                "host": host,
                "location": location,
                "region": location,
                "date": date.strftime('%Y-%m-%d') if date else None,
                "apply_url": None,
                "source": "odcloud"
            })

        # 3. Firebase 요청
        firebase_response = requests.get(FIREBASE_URL)
        firebase_response.raise_for_status()
        firebase_docs = firebase_response.json().get("documents", [])

        # 4. Firebase 데이터 파싱 및 저장
        for doc in firebase_docs:
            fields = doc.get("fields", {})

            title = fields.get("event_name", {}).get("stringValue")
            host = fields.get("host", {}).get("stringValue")
            location = fields.get("location", {}).get("stringValue")
            region = fields.get("region", {}).get("stringValue")
            date_str = fields.get("event_datetime", {}).get("stringValue")
            apply_url = fields.get("website", {}).get("stringValue")

            try:
                date = datetime.strptime(date_str.split(" ")[0], "%Y-%m-%d") if date_str else None
            except:
                date = None

            if not all([title, host, location]):
                continue

            event = SportsEvent(
                title=title,
                host=host,
                location=location,
                region=region or location,
                date=date,
                apply_url=apply_url,
                description=None
            )
            db.session.add(event)
            saved_events.append({
                "title": title,
                "host": host,
                "location": location,
                "region": region or location,
                "date": date.strftime('%Y-%m-%d') if date else None,
                "apply_url": apply_url,
                "source": "firebase"
            })

        db.session.commit()

        return jsonify({
            "message": f"{len(saved_events)}개 행사 저장 완료 (공공데이터 + Firebase)",
            "data": saved_events
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

######################################
# 유저 관련 엔드포인트
######################################

#유저 정보 조회
@bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # 유저가 작성한 게시글
        user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
        post_list = [
            {
                "post_id": post.post_id,
                "title": post.title,
                "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for post in user_posts
        ]

        # 유저가 좋아요 누른 게시글
        liked_posts = (
            db.session.query(Post)
            .join(PostLike, Post.post_id == PostLike.post_id)
            .filter(PostLike.user_id == user_id)
            .order_by(Post.created_at.desc())
            .all()
        )
        liked_list = [
            {
                "post_id": post.post_id,
                "title": post.title,
                "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for post in liked_posts
        ]

        #유저가 가입한 크루
        joined_crews = (
            db.session.query(Crew)
            .join(CrewMember, Crew.crew_id == CrewMember.crew_id)
            .filter(CrewMember.user_id == user_id)
            .order_by(Crew.name.asc())
            .all()
        )
        crew_list = [
            {
                "crew_id": crew.crew_id,
                "name": crew.name,
                "region": crew.region
            }
            for crew in joined_crews
        ]

        return jsonify({
            "user_id": user.user_id,
            "nickname": user.nickname,
            "region": user.region,
            "posts": post_list,
            "liked_posts": liked_list,
            "joined_crew": crew_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#유저 정보 수정
@bp.route('/api/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    data = request.get_json()

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        nickname = data.get('nickname')
        region = data.get('region')

        # 수정할 게 하나도 없으면 early return
        if not nickname and not region:
            return jsonify({"message": "수정할 필드가 없습니다."}), 400

        # 필드별 수정
        if nickname:
            user.nickname = nickname
        if region:
            user.region = region

        db.session.commit()
        return jsonify({"message": f"User {user_id} 정보 수정 완료"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


#유저 행사 러닝 기록 조회
@bp.route('/api/users/<int:user_id>/events_run_log', methods=['GET'])
def get_user_event_run_log(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "유저를 찾을 수 없습니다."}), 404

        logs = SportsEventLog.query.filter_by(user_id=user_id).join(SportsEvent).all()

        log_list = []
        for log in logs:
            log_list.append({
                "event_title": log.event.title,
                "event_date": log.event.date.strftime('%Y-%m-%d') if log.event.date else None,
                "distance_km": log.distance_km,
                "duration_min": log.duration_min,
                "logged_at": log.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({"user_id": user_id, "event_logs": log_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#유저 행사 러닝 기록 등록
@bp.route('/api/users/<int:user_id>/events_run_log', methods=['POST'])
def post_user_event_run_log(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "유저를 찾을 수 없습니다."}), 404

        data = request.get_json()
        event_id = data.get("event_id")
        distance_km = data.get("distance_km")
        duration_min = data.get("duration_min")
        joined_at_str = data.get("joined_at")

        if not all([event_id, distance_km, duration_min, joined_at_str]):
            return jsonify({"error": "모든 필드(event_id, distance_km, duration_min, joined_at)는 필수입니다."}), 400

        event = SportsEvent.query.get(event_id)
        if not event:
            return jsonify({"error": "해당 ID의 스포츠 행사를 찾을 수 없습니다."}), 404

        try:
            joined_at = datetime.strptime(joined_at_str, "%Y-%m-%d").date()
        except:
            return jsonify({"error": "joined_at은 YYYY-MM-DD 형식이어야 합니다."}), 400

        new_log = SportsEventLog(
            user_id=user_id,
            event_id=event_id,
            distance_km=distance_km,
            duration_min=duration_min,
            joined_at=joined_at
        )

        db.session.add(new_log)
        db.session.commit()

        return jsonify({
            "message": "러닝 기록이 등록되었습니다.",
            "log": {
                "event_title": event.title,
                "distance_km": distance_km,
                "duration_min": duration_min,
                "joined_at": joined_at.strftime('%Y-%m-%d')
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#유저 러닝 기록 조회
@bp.route('/api/users/<int:user_id>/user_run_log', methods=['GET'])
def get_user_runs(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        logs = UserRunLog.query.filter_by(user_id=user_id).order_by(UserRunLog.date.desc()).all()
        
        result = [
            {
                "log_id": log.user_log_id,
                "date": log.date.strftime('%Y-%m-%d'),
                "distance_km": log.distance_km,
                "duration_min": log.duration_min,
                "pace": log.pace
            }
            for log in logs
        ]

        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#유저 러닝 기록 추가
@bp.route('/api/users/<int:user_id>/user_run_log', methods=['POST'])
def post_user_run(user_id):
    data = request.get_json()
    
    try:
        # 필수 항목 확인
        date = data.get('date')
        distance_km = data.get('distance_km')
        duration_min = data.get('duration_min')
        pace = data.get('pace')

        if not all([date, distance_km, duration_min, pace]):
            return jsonify({"error": "All fields are required"}), 400

        new_log = UserRunLog(
            user_id=user_id,
            date=date,
            distance_km=distance_km,
            duration_min=duration_min,
            pace=pace
        )

        db.session.add(new_log)
        db.session.commit()

        return jsonify({"message": f"유저 {user_id} 러닝 기록 추가 완료", "log_id": new_log.user_log_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#유저 러닝 기록 삭제
@bp.route('/api/users/<int:user_id>/user_run_log/<int:user_log_id>', methods=['DELETE'])
def delete_user_run(user_id, run_id):   
    try:
        log = UserRunLog.query.filter_by(user_id=user_id, user_log_id=user_log_id).first()
        if not log:
            return jsonify({"error": "User run log not found"}), 404

        db.session.delete(log)
        db.session.commit()

        return jsonify({"message": f"유저 {user_id} 러닝 기록 {user_log_id} 삭제 완료"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

