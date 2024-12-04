from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from functions import save_file


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'data_files/input_files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/list_files', methods=['GET'])
def list_files():
    upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
    files = os.listdir(upload_folder)
    return render_template('list_files.html', files=files)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
        file_path = save_file(file, upload_folder)
        
        if isinstance(file_path, tuple):  # Verifica se houve erro no save_file
            return file_path
         
        return render_template('popup.html', message="File has been uploaded.")
    return render_template('read_files.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)