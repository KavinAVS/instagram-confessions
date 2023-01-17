from flask import Flask, render_template, request
from waitress import serve
import logging
from decouple import config

DATABASE_URL = config('DATABASE_URL')
INSTA_USER = config('INSTA_USER')
INSTA_PWD = config('INSTA_PWD')

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)
app = Flask(__name__)

@app.route('/', methods=["GET"])
def main():
    return render_template("index.html")

@app.route('/', methods=["POST"])
def post():
    content = request.get_json(silent=True)
    print(content)
    return {"ret": True}

if __name__ == "__main__":
    #serve(app, host='0.0.0.0', port=80, threads=8)
    app.run(host='0.0.0.0', port=80)