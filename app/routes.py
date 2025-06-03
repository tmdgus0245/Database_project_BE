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
                "name": crew.name,
                "region": crew.region,
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
    return jsonify({"message": f"크루 {crew_id} 상세 정보"}), 200

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

# #크루 런닝기록
# @bp.route('/api/crews/<int:crew_id>/crew_run_log', methods=['GET'])
# def get_crew_run_log(crew_id):

# #크루 공지사항
# @bp.route('/api/crews/<int:crew_id>/crew_notice', methods=['GET'])
# def get_crew_notice(crew_id):



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
