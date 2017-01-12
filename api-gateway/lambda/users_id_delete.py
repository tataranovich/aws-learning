import psycopg2
from psycopg2.extras import RealDictCursor
from rds_config import conn_uri


def handler(event, context):
    user_id = event['id']
    conn = psycopg2.connect(conn_uri)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("delete from friendship where user_id=%s" % user_id)
    cur.execute("delete from membership where user_id=%s" % user_id)
    cur.execute("delete from users where user_id=%s" % user_id)
    result = {}
    conn.commit()
    conn.close()
    return result
