from flask import Flask, render_template, redirect, url_for
import logging
from utils import db
from controllers.api import api_blueprint

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
# 初始化数据库
db.create_engine('root', '111111', 'eds_base', '47.106.83.33')
# 导入蓝图
app.register_blueprint(api_blueprint)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/homepage/<int:teacher_id>')
def user_homepage(teacher_id):
    return render_template('detail.html', user_id=teacher_id)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)
