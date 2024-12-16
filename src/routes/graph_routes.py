from flask import Blueprint, request, jsonify, render_template, current_app
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import os
from wtforms.validators import InputRequired
from src.services.graph_services import save_file

graph_blueprint = Blueprint('graph_routes', __name__)
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

#FUNÇÃO PRECISA DE SER ALTERADA 
@graph_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), current_app.config['UPLOAD_FOLDER'])
        file_path = save_file(file, upload_folder)
        
        if isinstance(file_path, tuple): 
            return file_path
         
        return render_template('popup.html', message="File has been uploaded.")
    return render_template('read_files.html', form=form)