from flask import Blueprint, request, jsonify
from services.trades_services import *

trades_blueprint = Blueprint('trade_routes', __name__)

@trades_blueprint.route('/<int:property1_id>/<int:property2_id>', methods=['PUT'])
def trade_properties(property1_id, property2_id):
    try:
        result = trade_owners_properties(property1_id, property2_id)
        if result:
            return jsonify({"status": "success", "data": result}), 200
        else:
            return jsonify({"status": "error", "message": "Trade properties not possible"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@trades_blueprint.route('/sugestion/<int:owner1_id>/<int:owner2_id>', methods=['GET'])
def get_suggestion_trade_properties(owner1_id, owner2_id):
    try:
        result = suggestion_properties_trades(owner1_id, owner2_id)

        if result:
            return jsonify({"status": "success", "data": result}), 200
        else:
            return jsonify({"status": "error", "message": "Trade properties not possible"}), 404
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

@trades_blueprint.route('/sugestions/allUsers', methods=['GET'])
def get_all_possible_properties_trades():
    try:
        result = get_suggestions_for_all_owner()
        if result:
            return jsonify({"status": "success", "data": result}), 200
        else:
            return jsonify({"status": "error", "message": "Trade properties not possible"}), 404
    except Exception as e:
        print(f"Exception occurred: {str(e)}")