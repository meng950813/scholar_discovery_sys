from flask import Flask,render_template,redirect,url_for,request,session
import logging
from controllers.api import api_blueprint
from controllers.user import user_blueprint
from utils import db
from config import DB_CONFIG
from config import SESSION_KEY


app = Flask(__name__)
app.register_blueprint(api_blueprint)
app.register_blueprint(user_blueprint)
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
def index():
    user = None
    if "username" in session:
        user = session.get("username")
        if user["TYPE"] == "1":
            return render_template("index.html",user = user)
        else:
            return render_template("schoolBasic.html",user = user)
    return render_template("index.html")


@app.route('/index')
def index_2():
    user = None
    if "username" in session:
        user = session.get("username")
    return render_template("index.html", user = user)

@app.route('/schoolBasic')
def schoolBasic():
    user = None
    if "username" in session:
        user = session.get("username")
    return render_template("schoolBasic.html", user = user)

@app.route('/relation')
def relation():
    """测试关系图使用的路由函数"""
    return render_template('relation.html')


@app.route('/word_cloud')
def word_cloud():
    """测试词云的路由函数"""
    return render_template('wordcloud.html')


@app.route('/login/')
def login():
    # 商务登录
    if "username" in session:
        return redirect("index")

    err = request.args.get("error")
    return render_template("./components/login.html",error = err)


@app.route('/manageLogin')
def manageLogin():
    # 管理员登录
    return render_template("./components/manageLogin.html")



@app.route('/search',methods=['GET','POST'])
def search():
    keyword = request.form.get("simple-input")
    return render_template('./components/schoolScholar.html' , user = session.get('username'))


@app.route("/logout/")
def logout():
    # 商务注销
    session.pop("username",None)

    return redirect(url_for("login"))


@app.route("/manageLogout/")
def manageLogout():
    # 管理员注销
    return redirect(url_for("manageLogin"))


@app.route("/governPersonal/")
def governPersonal():
    # 转到个人页面
    return render_template("./components/governPersonal.html" , user = session.get('username'))


@app.route("/schoolPersonal/")

def schoolPersonal():
    # 转到个人页面
    return render_template("./components/schoolPersonal.html" , user = session.get('username'))



if __name__ == '__main__':
    app.run(debug=True)
