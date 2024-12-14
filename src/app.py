from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from functions import save_file, get_owner_by_id, get_owners, get_owner_by_name


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'data_files/input_files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

#FUNÇÃO PRECISA DE SER ALTERADA 
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
        file_path = save_file(file, upload_folder)
        
        if isinstance(file_path, tuple): 
            return file_path
         
        return render_template('popup.html', message="File has been uploaded.")
    return render_template('read_files.html', form=form)

@app.route('/owners', methods=['GET'])
def get_all_owners():
    try:
        owners = get_owners()
        return jsonify({"status": "success", "data": owners}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/owners/<int:owner_id>', methods=['GET'])
def fetch_owner_by_id(owner_id):
    try:
        owner = get_owner_by_id(owner_id)
        if owner:
            return jsonify({"status": "success", "data": owner}), 200
        else:
            return jsonify({"status": "error", "message": "Owner not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/owners/search', methods=['GET'])
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
    


if __name__ == '__main__':
    app.run(debug=True)