import psycopg
from decouple import config
import json

DATABASE_URL = config('DATABASE_URL')

#add to db
conn = psycopg.connect(DATABASE_URL)

with conn.cursor() as cur:

    post_id = int(input("Enter post num: "))

    cur.execute("DELETE FROM Posts WHERE PostID=%s", (post_id,))
    conn.commit()
