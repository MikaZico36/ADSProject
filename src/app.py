from flask import Flask
from routes.graph_routes import graph_blueprint
from routes.search_routes import search_blueprint

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data_files/input_files'
app.register_blueprint(graph_blueprint)
app.register_blueprint(search_blueprint)
    
if __name__ == '__main__':
    app.run(debug=True)