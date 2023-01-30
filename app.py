from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import traceback

from waitress import serve
import imageMaker.pil_autowrap as pilwrap
import logging
from decouple import config
from instagrapi import Client
import psycopg
import os

DATABASE_URL = config('DATABASE_URL')
INSTA_USER = config('INSTA_USER')
INSTA_PWD = config('INSTA_PWD')
PORT = config('PORT')

logging.basicConfig(level=logging.INFO)
L = logging.getLogger(__name__)
logging.getLogger('instagrapi').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)

# Login to DB
conn = psycopg.connect(DATABASE_URL)
with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Posts (
            PostID INT PRIMARY KEY, 
            message STRING NOT NULL, 
            name STRING NOT NULL,
            reply_to INT REFERENCES Posts(PostID) ON DELETE SET NULL
        );
    """)
    conn.commit()


# Login to Instagram
cl = Client()
cl.login(INSTA_USER, INSTA_PWD)

@app.route('/', methods=["GET"])
def main():
    return render_template("index.html")


@app.route('/', methods=["POST"])
@limiter.limit("2/hour")
def post():
    content = request.get_json(silent=True)
    
    if("message" not in content or content["message"] == ""):
        return {"ret": False, "error":"nomsg"}
    elif(len(content["message"]) > 800):
        return {"ret": False, "error":"msgtoolong"}
    
    if("name" not in content or content["name"] == ""):
        name = "Anon"
    elif(len(content["name"]) > 50):
        return {"ret": False, "error":"nametoolong"}
    else:
        name = content["name"]
        
    #add to DB
    L.debug("Adding to DB..")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(PostID) FROM Posts;")
            res = cur.fetchall()

        
            post_num = res[0][0]
            if(post_num is None):
                post_num = 0
            else:
                post_num = post_num+1

            cur.execute("INSERT INTO Posts (PostID, message, name, reply_to) VALUES ( %s, %s, %s, NULL);", (post_num, content['message'], name))
            conn.commit()

    except:
        conn.rollback()
        L.info(f"Failed to add to db {traceback.format_exc()}")
        return {"ret": False, "error":"dbwrite"}
    
    L.debug("Added to DB, Making image..")
    
    #Make the image
    post_str=f"post#{post_num:05d}"
    try:
        pilwrap.make_text_image(content["message"], name, post_str, (55, 118, 173), post_str)
    except Exception as e:
        L.info("Failed make image", e)
        return {"ret": False, "error":"makeimage"}
    
    L.debug("Image made, posting image..")
    
    #post the image
    i=2
    while(i!=0):
        try:
            cl.photo_upload(f"./temp/{post_str}.jpg", f"#utmconfess{post_num:05d}")
            break
        except:
            i-=1
            if(i==0):
                L.info(f"Failed to post image {traceback.format_exc()}")
                os.remove(f"./temp/{post_str}.jpg")
                
                try:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM Posts WHERE PostID=%s;", (post_num,))
                        conn.commit()
                except:
                    conn.rollback()
                    
                return {"ret": False, "error":"uploadfail"}
            else:
                L.info(f"Retrying post again...")
            
    
    #delete the img from temp
    os.remove(f"./temp/{post_str}.jpg")
    
    return {"ret": True, "post_num": post_num}

@app.route('/recents', methods=["GET"])
def recents():
    startid = int(request.args.get('startid'))
    
    if(startid is None):
        return {"ret": False, "error":"nostartid"}
    
    try:
        with conn.cursor() as cur:
            if(startid < 0):
                cur.execute("SELECT MAX(PostID) FROM Posts;")
                res = cur.fetchall()
       
                max_id = res[0][0]
                if(max_id is None):
                    return {"ret": True}
            else:
                max_id = startid
                
            min_id = max( (max_id - 4) , 0)
            
            cur.execute("SELECT PostID,message,name FROM Posts WHERE PostID BETWEEN %s AND %s;", (min_id, max_id))
            res = cur.fetchall()
            conn.commit()
            
    except Exception as e:
        conn.rollback()
        L.info(f"Failed to get from db {traceback.format_exc()}")
        return {"ret": False, "error":"dbfail"}
    
    return {"ret": True, "data": res}

if __name__ == "__main__":
    
    serve(app, host='0.0.0.0', port=PORT, threads=8)
    #app.run(host='0.0.0.0', port=80)