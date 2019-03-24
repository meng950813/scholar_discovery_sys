from flask import Flask,render_template,redirect,url_for,request,session
import logging
import controllers.api as api
from controllers.api import api_blueprint
from controllers.user import user_blueprint
from service.userservice import user_service
from controllers.api_agent import agent_blueprint
from utils import db
from config import DB_CONFIG
from config import SESSION_KEY


app = Flask(__name__)
app.register_blueprint(api_blueprint)
app.register_blueprint(user_blueprint)
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


@app.route('/map')
def map():
    """测试地图v2的路由函数"""
    return render_template('map2.html')


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
    school_name = '南京大学'

    data = api.get_teachers_by_school(school_name, keyword)
    # 学者个数
    number = 0
    #学院信息
    institutions = data['institutions']
    for name,values in institutions.items():
        if len(values["teachers"]) > 3:
            number = number + 3
        else:
            number = number + len(values["teachers"])
    # print(institutions)
    # 遍历
    # for name, values in institutions.items():
    #     print(name)
    #     for teacher in values['teachers']:
    #
    #         print( type(teacher['TITLE']))
    #         print(teacher['YEAROLD'] if 'YEAROLD' in teacher else '年龄未知')
    #         print(teacher['ACADEMICIAN'] if teacher['ACADEMICIAN'] == 1 else "不是院士")
    #         print(teacher['OUTYOUTH'] if teacher['OUTYOUTH'] == 1 else "不是杰出青年")
    #         print(teacher['CHANGJIANG'] if teacher['CHANGJIANG'] == 1 else "不是长江学者")
    #         print(teacher['FIELDS'] if teacher['FIELDS'] is not None else '领域未知')
    #     print(values['info'])
    # 渲染，并传递参数
    return render_template('./components/schoolScholar.html' , user=session.get('username'),keyword=keyword,number=number,intstitutions = institutions)


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

    user = None
    if "username" in session:
        user = session.get("username")
    else:
        return redirect(url_for("login"))

    # user_service.
    # 转到个人页面
    return render_template("./components/schoolPersonal.html" , user = session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)
