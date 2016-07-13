import rethinkdb as rdb
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from flask import abort

RDB_HOST = 'localhost'
RDB_PORT = 28015
DB_NAME = 'zompigame'
TABLE_NAME = 'rating'
DB_KEY = 'ZompKey69'
MAIL_TABLE_NAME = 'mail'


# ----------------Gestion DB------------------

# g.rdb_conn = rdb.connect(host=RDB_HOST, port=RDB_PORT, db=DB_NAME, auth_key=DB_KEY)


def select():
    try:
        rdb_conn = rdb.connect(host=RDB_HOST, port=RDB_PORT, db=DB_NAME)
        result = rdb.db(DB_NAME).table(TABLE_NAME).order_by(index=rdb.desc('point')).limit(10).run(rdb_conn)
        rdb_conn.close()
        return result
    except RqlDriverError:
        abort(503, "No database connection could be established.")


def insert(nom, email, sujet, message):
    try:
        rdb_conn = rdb.connect(host=RDB_HOST, port=RDB_PORT, db=DB_NAME)
        rdb.db(DB_NAME).table(MAIL_TABLE_NAME).insert([{'name': nom,
                                                        'email': email,
                                                        'sujet': sujet,
                                                        'message': message}]).run(rdb_conn)
        rdb_conn.close()
    except RqlDriverError:
        abort(503, "No database connection could be established.")
