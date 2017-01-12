import psycopg2
from psycopg2.extras import RealDictCursor
from rds_config import conn_uri


def handler(event, context):
    first_name = event['first_name']
    last_name = event['last_name']
    conn = psycopg2.connect(conn_uri)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("insert into users (first_name, last_name) values ('%s', '%s')" % (first_name, last_name))
    result = {}
    conn.commit()
    conn.close()
    return result
