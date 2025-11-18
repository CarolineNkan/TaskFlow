from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # allow frontend to communicate with backend

@app.route("/")
def home():
    return {"message": "TaskFlow backend running"}

if __name__ == "__main__":
    app.run(debug=True)
