from flask import Flask,render_template,Blueprint,send_from_directory
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials

app = Flask(__name__)
CORS(app)

firebase_admin.initialize_app()

from api import user_info
todo = Blueprint('todo', __name__,
                    template_folder='todo/dist/todo')
app.register_blueprint(todo)
app.register_blueprint(user_info,url_prefix='/api')

@app.route('/assets/<path:filename>')
def custom_static_for_assets(filename):
    return send_from_directory('todo/dist/todo/assets', filename)


@app.route('/<path:filename>')
def custom_static(filename):
    return send_from_directory('todo/dist/todo/', filename)

@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8000,debug=True)

