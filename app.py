from flask import Flask, render_template, request
from waitress import serve
import imageMaker.pil_autowrap as pilwrap
import logging
from decouple import config
import psycopg2

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
    
    if("message" not in content or content["message"] == ""):
        return {"ret": False}
    
    if("name" not in content or content["name"] == ""):
        name = "Anon"
    else:
        name = content["name"]
        
    post_num="post#0000"
    
    #add to db
    conn = psycopg2.connect(DATABASE_URL, sslrootcert="./ca.crt")

    with conn.cursor() as cur:
        cur.execute("SELECT now()")
        res = cur.fetchall()
        conn.commit()
        print(res)
    
    pilwrap.make_text_image(content["message"], name, post_num, (100,100,0,255), post_num)
    
    #post the image
    
    #delete the img from temp
    
    return {"ret": True}

if __name__ == "__main__":
    #serve(app, host='0.0.0.0', port=80, threads=8)
    app.run(host='0.0.0.0', port=80)