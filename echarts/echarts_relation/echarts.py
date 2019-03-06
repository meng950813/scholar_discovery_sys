from flask import Flask, render_template, redirect, url_for
import os, os.path, json, logging
from dao import db
from controllers.api import api_blueprint

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
# 初始化数据库
db.create_engine('root', '9527', 'training')
# 导入蓝图
app.register_blueprint(api_blueprint)


@app.route('/')
def index():
    return redirect(url_for('graph'))


@app.route('/graph')
def graph():
    return render_template('graph.html')


@app.route('/user/<int:user_id>')
def user_homepage(user_id):
    return render_template('person.html', user_id=user_id)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)