import psycopg
from decouple import config
import json

DATABASE_URL = config('DATABASE_URL')

#add to db
conn = psycopg.connect(DATABASE_URL)

with conn.cursor() as cur:
    #cur.execute("DROP TABLE Posts;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Posts (
            PostID INT PRIMARY KEY, 
            message STRING NOT NULL, 
            name STRING NOT NULL,
            reply_to INT REFERENCES Posts(PostID) ON DELETE SET NULL
        );
    """)
    conn.commit()
    
    # cur.execute("SELECT MAX(PostID) FROM Posts;")
    # res = cur.fetchall()
    # conn.commit()
    # print(res)
    
    # post_num = res[0][0]
    # if(post_num is None):
    #     post_num = 0
    # else:
    #     post_num = post_num+1

    # cur.execute(f"INSERT INTO Posts ( PostID, message, name, reply_to) VALUES ( {post_num}, 'Heloo sadasd ', 'sadads', NULL ); ")
    # conn.commit()
    
    cur.execute("SELECT MAX(PostID) FROM Posts;")
    res = cur.fetchall()
    print(res)
    conn.commit()
    
    # cur.execute("SELECT * FROM Posts;")
    # res = cur.fetchall()
    # conn.commit()
    # print(res)
    
    # cur.execute("""
        
    #     INSERT INTO Posts (message, name, reply_to) VALUES ( 'Heloo sadasd ', 'sadads', NULL ) RETURNING PostID;
                
    #             """)
    
    # res = cur.fetchall()
    # conn.commit()
    # print(res[0][0])
    
    # cur.execute("""SELECT * FROM Posts WHERE PostID BETWEEN x AND y""")
    
    # cur.execute("SELECT * FROM Posts;")
    # res = cur.fetchall()
    
    # cur.execute("INSERT INTO Posts (message, name, reply_to) VALUES ('Test1', 'Guy', NULL) RETURNING PostID;")
    
    # conn.commit()
    # print(res)
    
    cur.execute("DELETE FROM Posts WHERE PostID='7'")
    conn.commit()
