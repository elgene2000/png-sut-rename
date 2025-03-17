from flask import Flask
from routes.sut import sut
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

app.register_blueprint(sut, url_prefix="/api/sut")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)