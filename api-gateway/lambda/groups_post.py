import psycopg2
from psycopg2.extras import RealDictCursor
from rds_config import conn_uri


def handler(event, context):
    group_name = event['group_name']
    conn = psycopg2.connect(conn_uri)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("insert into groups (group_name) values ('%s')" % group_name)
    result = {}
    conn.commit()
    conn.close()
    return result
