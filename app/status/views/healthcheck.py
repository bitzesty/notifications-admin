from flask import current_app, jsonify, request
from app.status import status

@status.route('/_status', methods=['GET'])
def show_status():
    return jsonify(status="ok"), 200