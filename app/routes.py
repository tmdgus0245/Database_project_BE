from flask import Blueprint, request, jsonify
from .service import get_sports_events

bp = Blueprint('routes', __name__)

@bp.route('/events', methods=['GET'])
def sports_events():
    page = request.args.get('page', default=1, type=int)
    try:
        data = get_sports_events(page)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
