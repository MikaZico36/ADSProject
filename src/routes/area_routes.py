from re import search

from flask import Blueprint, request, jsonify
from services.area_services import *


area_blueprint = Blueprint('area_routes', __name__)

@area_blueprint.route('/totalArea/<int:owner_id>', methods=['GET'])
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


@area_blueprint.route('/meanArea/<int:owner_id>', methods=['GET'])
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
    

@area_blueprint.route('/owners/<int:owner_id>/subareas', methods=['GET'])
def fetch_area_adject_properties_by_owner(owner_id):
    try:
        owner = get_area_adject_properties_by_owner(owner_id)
        if owner:
            return jsonify({"status": "success", "data": owner}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@area_blueprint.route('/subAreas', methods=['GET'])
def get_subarea():
    try:
        data = request.get_json()
        print(data)
        properties_ids = data.get("property_ids", [])

        if not properties_ids or not isinstance(properties_ids, list):
            return jsonify({"error": "Invalid or missing 'property_ids' parameter. Provide a list of IDs."}), 400

        total_area = get_selected_subarea(properties_ids)
        print(total_area)
        return jsonify({"total_area": total_area})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


