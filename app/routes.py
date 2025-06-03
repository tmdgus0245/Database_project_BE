from flask import Blueprint, jsonify, request
from . import db
from .models import *

bp = Blueprint('routes', __name__)

######################################
# 1️⃣ 크루 탐색 및 가입
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
                "duration_min": log.duartion_min,
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
        date = data.get('date')

        # 필수 값 검증
        if not title or not distance_km or not duration_min or not avg_pace:
            return jsonify({"error": "Missing required fields"}), 400

        # 새로운 런닝 기록 생성
        new_log = CrewRunLog(
            crew_id=crew_id,
            title=title,
            date=date,  # 오늘 날짜로 등록
            distance_km=distance_km,
            duartion_min=duration_min,
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



@bp.route('/api/crews_make', methods=['POST'])
def create_crew():
    data = request.get_json()
    return jsonify({"message": "크루 생성"}), 201

@bp.route('/api/crews/<int:crew_id>/join', methods=['POST'])
def join_crew(crew_id):
    data = request.get_json()
    return jsonify({"message": f"크루 {crew_id} 가입"}), 200

@bp.route('/api/crews/<int:crew_id>/leave', methods=['POST'])
def leave_crew(crew_id):
    data = request.get_json()
    return jsonify({"message": f"크루 {crew_id} 탈퇴"}), 200

######################################
# 2️⃣ 러닝 코스 추천
######################################

@bp.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify({"message": "러닝 코스 추천 리스트"}), 200

@bp.route('/api/courses', methods=['POST'])
def post_course():
    data = request.get_json()
    return jsonify({"message": "러닝 코스 추천 작성"}), 201

######################################
# 3️⃣ 이만큼 달렸어요 (개인 기록 자랑)
######################################

@bp.route('/api/brag-posts', methods=['GET'])
def get_brag_posts():
    return jsonify({"message": "개인 기록 자랑 리스트"}), 200

@bp.route('/api/brag-posts', methods=['POST'])
def post_brag():
    data = request.get_json()
    return jsonify({"message": "개인 기록 자랑 작성"}), 201

@bp.route('/api/brag-posts/<int:post_id>', methods=['DELETE'])
def delete_brag(post_id):
    return jsonify({"message": f"개인 기록 자랑 {post_id} 삭제"}), 200

######################################
# 4️⃣ 크루 관리
######################################

@bp.route('/api/crews/<int:crew_id>/runs', methods=['GET'])
def get_crew_runs(crew_id):
    return jsonify({"message": f"크루 {crew_id} 러닝 기록 조회"}), 200

@bp.route('/api/crews/<int:crew_id>/schedule', methods=['POST'])
def post_crew_schedule(crew_id):
    data = request.get_json()
    return jsonify({"message": f"크루 {crew_id} 일정 등록"}), 201

@bp.route('/api/crews/<int:crew_id>/schedule', methods=['GET'])
def get_crew_schedule(crew_id):
    return jsonify({"message": f"크루 {crew_id} 일정 조회"}), 200

######################################
# 5️⃣ 체육 행사 정보
######################################

@bp.route('/api/events', methods=['GET'])
def get_events():
    return jsonify({"message": "체육 행사 리스트"}), 200

@bp.route('/api/events/<int:event_id>', methods=['GET'])
def get_event_detail(event_id):
    return jsonify({"message": f"체육 행사 {event_id} 상세 정보"}), 200

@bp.route('/api/events/<int:event_id>/join', methods=['POST'])
def join_event(event_id):
    data = request.get_json()
    return jsonify({"message": f"체육 행사 {event_id} 참가 신청"}), 201

@bp.route('/api/events/<int:event_id>/participants', methods=['GET'])
def get_event_participants(event_id):
    return jsonify({"message": f"체육 행사 {event_id} 참가자 목록"}), 200

######################################
# 6️⃣ 러닝 기록 관리
######################################

@bp.route('/api/users/<int:user_id>/runs', methods=['GET'])
def get_user_runs(user_id):
    return jsonify({"message": f"유저 {user_id} 러닝 기록 조회"}), 200

@bp.route('/api/users/<int:user_id>/runs', methods=['POST'])
def post_user_run(user_id):
    data = request.get_json()
    return jsonify({"message": f"유저 {user_id} 러닝 기록 추가"}), 201

@bp.route('/api/users/<int:user_id>/runs/<int:run_id>', methods=['DELETE'])
def delete_user_run(user_id, run_id):
    return jsonify({"message": f"유저 {user_id} 러닝 기록 {run_id} 삭제"}), 200
