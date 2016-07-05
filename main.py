#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, redirect, flash, render_template, url_for
from flask import g, jsonify, render_template, request, abort, make_response, session
from flask_socketio import SocketIO, send, emit
from form import ConnForm, SignUpForm
import rethinkdb as rdb
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from threading import Thread
import json
import multiprocessing


app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)
socketio = SocketIO(app)
app.config.update(dict(DEBUG=True,
                       RDB_HOST='localhost',
                       RDB_PORT=28015,
                       DB_NAME='test'))

global thread
thread = None


# ----------------Gestion DB------------------


@app.before_request
def before_request():
    try:
        # g.rdb_conn = rdb.connect(host=RDB_HOST, port=RDB_PORT, db=DB_NAME, auth_key=DB_KEY)
        g.rdb_conn = rdb.connect(host=app.config['RDB_HOST'],
                                 port=app.config['RDB_PORT'],
                                 db=app.config['DB_NAME'])
    except RqlDriverError:
        abort(503, "No database connection could be established.")


@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass


def messages_select():
    return rdb.db(app.config['DB_NAME']).table("chat").order_by(index=rdb.asc('number')).run(g.rdb_conn)


def channels_select():
    return rdb.db(app.config['DB_NAME']).table('Channels').run(g.rdb_conn)


def delete():
    select_all = list(rdb.db(app.config['DB_NAME']).table("chat").run(g.rdb_conn))
    for val in select_all:
        rdb.db(app.config['DB_NAME']).table("chat").get(val['id']).delete().run(g.rdb_conn)


def insert(pseudo, message, channel, number):
    rdb.db(app.config['DB_NAME']).table("chat").insert({"pseudo": pseudo,
                                                        "message": message,
                                                        "channel": channel,
                                                        "number": number}).run(g.rdb_conn)


# ----------------Thread-----------------


def send_changes():
    conn = rdb.connect(host=app.config['RDB_HOST'],
                       port=app.config['RDB_PORT'],
                       db=app.config['DB_NAME'])
    feed = rdb.db(app.config['DB_NAME']).table("chat").changes().run(conn)
    for change in feed:
        socketio.emit('new_change', change['new_val'])


# ----------------Gestion Url-----------------


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ConnForm(request.form)
    if request.method == "POST":
        if request.form['submit'] == 'sign up':
            return redirect(url_for('register'), code=301)
        elif form.validate():
            pseudo = form.pseudo.data
            password = form.password.data
            result = list(rdb.db(app.config['DB_NAME']).table('compte').filter({"pseudo": pseudo,
                                                                                "password": password}).run(g.rdb_conn))
            if len(result) != 0:
                session['user_name'] = pseudo
                rdb.db(app.config['DB_NAME']).table('connected').insert({"pseudo": pseudo}).run(g.rdb_conn)
                socketio.emit('new_user', [])
                return redirect(url_for('chat'), code=301)
            else:
                flash('Essaye encore !')
    return render_template('corps_index.html', titre="Accueil", form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = SignUpForm(request.form)
    if request.method == "POST" and form.validate():
        pseudo = form.pseudo.data
        password = form.password.data
        mail = form.mail.data
        if len(list(rdb.db(app.config['DB_NAME']).table('compte').filter({"pseudo": pseudo}).run(g.rdb_conn))) != 0:
            flash("Pseudo déjà utilisé !")
        elif len(list(rdb.db(app.config['DB_NAME']).table('compte').filter({"mail": mail}).run(g.rdb_conn))) != 0:
            flash("Mail déjà utilisé !")
        else:
            rdb.db(app.config['DB_NAME']).table('compte').insert({"pseudo": pseudo,
                                                                  "password": password,
                                                                  "mail": mail}).run(g.rdb_conn)
            flash("Compte crée")
            return redirect(url_for('index'), code=301)
    return render_template('corps_signup.html', titre="Sign Up", form=form)


@app.route('/chat/', methods=['GET', 'POST'])
def chat():
    old_messages = messages_select()
    all_channels = channels_select()
    connected_users = rdb.db(app.config['DB_NAME']).table('connected').run(g.rdb_conn)
    return render_template('corps_chat.html',
                           titre="Chat",
                           old_messages=old_messages,
                           connected=connected_users,
                           all_channels=all_channels,
                           actual_channel="General")


@app.route('/send_to_db/', methods=['POST'])
def send():
    data = json.loads(request.data)
    if data.get('message'):
        insert(session['user_name'],
               data.get('message'),
               data.get('channel'),
               len(list(messages_select())))
        return make_response('success!', 201)
    return make_response('invalid chat', 401)


@app.route('/channel_change/', methods=['POST'])
def channel_change():
    old_messages = list(messages_select())
    messages_to_send = []
    for message in old_messages:
        messages_to_send.append(message)
    socketio.emit('channel_change', messages_to_send)
    return make_response('success!', 201)


@app.route('/new_user_list/', methods=['POST'])
def new_user_list():
    result = list(rdb.db(app.config['DB_NAME']).table('connected').run(g.rdb_conn))
    all_user = []
    for user in result:
        all_user.append(user['pseudo'])
    socketio.emit('connected_list', all_user)
    return make_response('success!', 201)


@app.route('/disconnect/', methods=['POST'])
def disconnect():
    rdb.db(app.config['DB_NAME']).table('connected').filter({'pseudo': session['user_name']}).delete().run(g.rdb_conn)
    socketio.emit('user_disconnect', [])
    return make_response('success!', 201)


if __name__ == '__main__':
    app.secret_key = '2\xd6%\xdf\xabGNOf\x99\x161\xfc\x81\x16P!\xef\xd8oJ^j&'
    if thread is None:
        thread = Thread(target=send_changes)
        thread.start()
    socketio.run(app)

# source venv/bin/activate
