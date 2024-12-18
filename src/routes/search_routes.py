from re import search

from flask import Blueprint, request, jsonify
from services.search_services import *


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
    print(owner_id)
    try:
        owner = get_owner_by_id(owner_id)
        if owner:
            return jsonify({"status": "success", "data": owner_id}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@search_blueprint.route('/ownersProperties/<int:owner_id>', methods=['GET'])
def get_all_owners_properties(owner_id):
    try:
        owner = get_properties_by_ownerId(owner_id)
        if owner:
            return jsonify({"status": "success", "data": owner}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@search_blueprint.route('/changePropertyOwner/<int:owner_id>/<int:property_id>', methods=['PUT'])
def change_owner_property(owner_id, property_id):
    try:
        result = update_property_owner(owner_id, property_id)
        if result:
            return jsonify({"status": "success", "data": result}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404
    except Exception as e:
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
