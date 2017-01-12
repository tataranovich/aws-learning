import psycopg2
from psycopg2.extras import RealDictCursor
from rds_config import conn_uri


def handler(event, context):
    user_id = event['id']
    conn = psycopg2.connect(conn_uri)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from users where user_id=%s" % user_id)
    result = cur.fetchall()
    conn.commit()
    conn.close()
    return result
