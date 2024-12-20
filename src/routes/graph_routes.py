from flask import Blueprint, request, jsonify, current_app, send_from_directory
import os
from src.services.graph_services import upload_file, export_to_excel


graph_blueprint = Blueprint('graph_routes', __name__)

@graph_blueprint.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part in the request"}), 400
        
        file = request.files['file']
        distribution = request.form['distribution']

        if distribution != 'user_choice' and distribution != 'uniform':
            return jsonify({"status": "error", "message": "Invalid distribution"}), 400
        
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        upload_file(file, upload_folder, distribution)
        
        return jsonify({"status": "success", "message": "Graph structure created successfully"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@graph_blueprint.route('/download', methods=['GET'])
def export():
    try:
       
        file_path = export_to_excel()
       
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "File not found"}), 404

        return jsonify({"status": "success", "message": f"Graph structure save in {file_path}"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

   

        
        