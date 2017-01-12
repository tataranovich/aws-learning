import psycopg2
from psycopg2.extras import RealDictCursor
from rds_config import conn_uri


def handler(event, context):
    group_id = event['id']
    conn = psycopg2.connect(conn_uri)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select users.user_id, users.first_name, users.last_name from users, membership where membership.group_id=%s and membership.user_id=users.user_id;" % group_id)
    result = cur.fetchall()
    conn.commit()
    conn.close()
    return result
