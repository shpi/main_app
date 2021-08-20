# -*- coding: utf-8 -*-

from flask import Flask, session, request, redirect, url_for, render_template, make_response
from os import urandom
from html import escape

app = Flask(
    'HTTPServer',
    template_folder='modules/HTTPServer/templates',
    static_folder='modules/HTTPServer/static',
)

app.config.update(
    {
        'SECRET_KEY': b'kjgnbd_kbghk_4;r',  # urandom(16),
        'DEBUG': True,
        # 'SESSION_COOKIE_PATH': '/tmp/sessions/',
        "TESTING": True,
        'SESSION_REFRESH_EACH_REQUEST': True,
        "SESSION_COOKIE_SECURE": True,
    }
)

# su as -c exit


@app.route('/')
def index():
    session.permanent = True
    if 'username' in session:
        return f'Logged in as {session["username"]}:{session}'
    return 'You are not logged in ' + escape(str(request.cookies))


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = ''
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        if user == password == "pi":
            print("correct")
            session['username'] = user
            resp = make_response(redirect(url_for('index')))
            return resp
    return render_template('login.html', hostname="shpione", user=user)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/testpage')
def testpage():
    return 'Logged in only content'
