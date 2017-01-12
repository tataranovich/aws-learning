import psycopg2
from psycopg2.extras import RealDictCursor
from rds_config import conn_uri


def handler(event, context):
    group_id = event['id']
    conn = psycopg2.connect(conn_uri)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("delete from membership where group_id=%s" % group_id)
    cur.execute("delete from groups where group_id=%s" % group_id)
    result = {}
    conn.commit()
    conn.close()
    return result
