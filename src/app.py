from flask import Flask, request, jsonify
import geopandas as gpd
from shapely.geometry import MultiPolygon
from shapely.wkt import loads

app = Flask(__name__)

def read_gpkg(input_file, layer):
    try:
        gdf = gpd.read_file(input_file, layer=layer)
        return gdf
    except Exception as e:
        print(f"Erro ao ler o ficheiro: {e}")
        return None

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = f"uploads/{file.filename}"
        file.save(file_path)
        layer = request.form.get('layer', 'default_layer')  # You can specify the layer name in the form data
        gdf = read_gpkg(file_path, layer)
        if gdf is not None:
            return gdf.to_json()
        else:
            return jsonify({"error": "Failed to read the GPKG file"}), 500

if __name__ == '__main__':
    app.run(debug=True)