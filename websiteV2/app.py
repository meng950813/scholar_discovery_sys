from flask import Flask, render_template, session
import logging
from controllers.api import api_blueprint
from controllers.user import user_blueprint
from controllers.api_agent import api_agent_blueprint
from controllers.agent import agent_blueprint
from utils import db
from config import DB_CONFIG
from config import SESSION_KEY

app = Flask(__name__)
app.register_blueprint(api_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(api_agent_blueprint)
app.register_blueprint(agent_blueprint)
# 打印logging输出
logging.basicConfig(level=logging.DEBUG)

# 需要预先调用，且只调用一次
db.create_engine(**DB_CONFIG)

app.secret_key = SESSION_KEY
"""
# TODO 使用 redis 进行 session 共享
app.config['SESSION_TYPE'] = 'redis'  # session类型为redis
app.config['SESSION_PERMANENT'] = False  # 如果设置为True，则关闭浏览器session就失效。
app.config['SESSION_USE_SIGNER'] = False  # 是否对发送到浏览器上session的cookie值进行加密
app.config['SESSION_KEY_PREFIX'] = 'session:'  # 保存到session中的值的前缀
app.config['SESSION_REDIS'] = redis.Redis(host='127.0.0.1', port='6379', password='123123')
# 用于连接redis的配置

from flask_session import Session
Session(app)

"""


@app.route('/')
@app.route('/index')
def index():
    # 若无，为 None
    user = session.get("username")

    if user:
        if user["TYPE"] == "1":
            return render_template("index.html", user=user)
        else:
            return render_template("schoolBasic.html", user=user)
    return render_template("index.html")


@app.route('/relation')
def relation():
    """测试关系图使用的路由函数"""
    return render_template('relation.html')


@app.route('/school')
def school():
    """测试学校使用的路由函数"""
    return render_template('school.html')


@app.route('/map')
def map():
    """测试地图v2的路由函数"""
    return render_template('map2.html')


@app.route('/detail')
def detail():
    """测试详情页的路由函数"""
    return render_template('detail.html')
@app.route('/bar')
def bar():
    """测试柱状图的路由函数"""
    return render_template('bar.html')


if __name__ == '__main__':
    app.run(debug=True)
