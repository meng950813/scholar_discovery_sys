"""
author: chen, xiaoniu
date: 2019-03-24
desc: 代理蓝图，主要包含了代理相关的视图函数
"""
from flask import Blueprint, request, session, render_template
import controllers.api as api
from controllers.user import login_required

agent_blueprint = Blueprint('agent', __name__, url_prefix='/agent')


@agent_blueprint.route('/schoolBasic')
def school_basic():
    user = None
    if "username" in session:
        user = session.get("username")
    return render_template("schoolBasic.html", user=user)


@agent_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    keyword = request.form.get("simple-input")
    school_name = '南京大学'

    data = api.get_teachers_by_school(school_name, keyword)
    # 学者个数
    number = data['number']
    # 学院信息
    institutions = data['institutions']
    # 渲染，并传递参数
    return render_template('./components/schoolScholar.html',
                           user=session.get('username'),
                           keyword=keyword,
                           number=number,
                           intstitutions=institutions,
                           school_name=school_name)


@agent_blueprint.route("/governPersonal")
def govern_personal():
    # 转到个人页面
    return render_template("./components/governPersonal.html", user=session.get('username'))


@agent_blueprint.route("/schoolPersonal")
@login_required
def school_personal():
    # 转到个人页面
    return render_template("./components/schoolPersonal.html", user=session.get('username'))
