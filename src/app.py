from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import geopandas as gpd
from shapely.geometry import MultiPolygon
from shapely.wkt import loads

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'data_files/input_files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/upload', methods=['GET','POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        
        # Verificar se o ficheiro tem a extensão .gpkg
        if not filename.lower().endswith('.gpkg'):
            return "Invalid file type. Only .gpkg files are allowed.", 400
        
        upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
          
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)  # Then save the file
        return "File has been uploaded."
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)