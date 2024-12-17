from re import search

from flask import Blueprint, request, jsonify

from src.services.search_services import *

search_blueprint = Blueprint('search_routes', __name__)


@search_blueprint.route('/owners', methods=['GET'])
def get_all_owners():
    try:
        owners = get_owners()
        return jsonify({"status": "success", "data": owners}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@search_blueprint.route('/owners/<int:owner_id>', methods=['GET'])
def fetch_owner_by_id(owner_id):
    try:
        owner = get_owner_by_id(owner_id)
        if owner:
            return jsonify({"status": "success", "data": owner_id}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@search_blueprint.route('/totalArea/<int:owner_id>', methods=['GET'])
def get_total_area(owner_id):
    try:
        total_area = get_total_area_by_owner(owner_id)

        if total_area is not None:
            return jsonify({"status": "success", "data": {"total_area": total_area}}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@search_blueprint.route('/meanArea/<int:owner_id>', methods=['GET'])
def get_mean_area(owner_id):
    try:
        mean_area = get_mean_area_by_owner(owner_id)

        if mean_area is not None:
            return jsonify({"status": "success", "data": {"total_area": mean_area}}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@search_blueprint.route('/owners/search', methods=['GET'])
def fetch_owner_by_name():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"status": "error", "message": "Name parameter is required"}), 400
        
        owner = get_owner_by_name(name)
        if owner:
            return jsonify({"status": "success", "data": owner}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


