#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, redirect, session

app = Flask(__name__, static_url_path='')

app.config.from_object(__name__)


@app.route('/download_file/', methods=['GET', 'POST'])
def download_file():
    file_path = 'zompigame.zip'
    return app.send_static_file(file_path)


if __name__ == '__main__':
    from blue import blueprint
    app.register_blueprint(blueprint)
    app.secret_key = '2\xd6%\xdf\xabGNOf\x99\x161\xfc\x81\x16P!\xef\xd8oJ^j&'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
