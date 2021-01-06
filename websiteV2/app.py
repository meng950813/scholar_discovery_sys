from flask import Flask, render_template, session, request
import logging
import json
from controllers.api import api_blueprint
from controllers.user import user_blueprint
from controllers.api_agent import api_agent_blueprint
from controllers.agent import agent_blueprint
from utils import db
from config import DB_CONFIG
from service.teacherservice import teacher_service
from service.schoolservice import school_service
from controllers.user import login_required
import controllers.api

app = Flask(__name__)
app.register_blueprint(api_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(api_agent_blueprint)
app.register_blueprint(agent_blueprint)
# 打印logging输出
logging.basicConfig(level=logging.DEBUG)

# 需要预先调用，且只调用一次
db.create_engine(**DB_CONFIG)

app.secret_key = "secret key"
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
            return render_template("business_search.html", user=user)
        else:
            return render_template("schoolBasic.html", user=user)
    return render_template("business_search.html")


@app.route('/school', methods=['GET', 'POST'])
@login_required
def school():
    """没有登录点击搜索跳转到登录界面"""
    user = session.get("username")
    keyword = None
    """测试学校使用的路由函数"""
    if request.method == 'GET':
        keyword = request.args.get('key')
    elif request.method == 'POST':
        keyword = request.form.get('key')
    # 根据关键字获取对应的学校
    schools = controllers.api.get_school_address_by_keywords(keyword, 5)
    return render_template('school.html', schools=schools, keyword=keyword,user=user)


@app.route('/detail/<int:teacher_id>', methods=['GET', 'POST'])
def detail(teacher_id):
    user = session.get("username")
    """测试详情页的路由函数"""
    if request.method == 'GET':
        school_name = request.args.get('school_name')
        college_name = request.args.get('college_name')
    elif request.method == 'POST':
        # 查表获取学校和学院名称
        school_id = request.form.get('school_id', type=int)
        college_id = request.form.get('college_id', type=int)
        info = school_service.get_institution_name(school_id, college_id)
        school_name = info['school']
        college_name = info['college_name']
    # 获取老师的信息
    info = teacher_service.get_teacher_info_by_id(teacher_id)
    # 获取论文
    papers = teacher_service.get_papers_by_id(teacher_id)
    # 获取论文的md5
    paper_md5_list = []
    for paper in papers:
        authors = json.loads(paper.pop('author'))
        paper['partners'] = [author['name'] for author in authors]
        paper_md5_list.append(paper['paper_md5'])
    # 查询数据库
    partners = teacher_service.get_paper_partners_by_md5(paper_md5_list)
    return render_template('detail.html',
                           school_name=school_name,
                           college_name=college_name,
                           info=info,
                           papers=papers,
                           user=user,
                           partners=partners)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run("0.0.0.0", debug=True)
