import psycopg2
from psycopg2.extras import RealDictCursor
from rds_config import conn_uri


def handler(event, context):
    group_id = event['id']
    group_name = event['group_name']
    conn = psycopg2.connect(conn_uri)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("update groups set group_name='%s' where group_id=%s" % (group_name, group_id))
    result = {}
    conn.commit()
    conn.close()
    return result
