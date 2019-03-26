"""
author: chen, xiaoniu
date: 2019-03-16
desc: login蓝图，主要负责登陆相关的路由函数
"""

from flask import Blueprint, request, redirect, url_for, session, render_template
import functools
from service.userservice import user_service
import json

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


def login_required(func):
    """
    装饰函数，如果需要某函数需要登陆后操作，则可以装饰上此函数
    如@login_required
    """
    @functools.wraps(func)
    def wrapper(*args, **kw):
        # 当前未登陆
        user = session.get('username')
        if user is None:
            return redirect(url_for('user.login'))
        return func(*args, **kw)
    return wrapper


@user_blueprint.route('/dologin', methods=['POST'])
def do_login():
    """
    处理登录事件
    :return:
    """
    name = request.form['username']
    pwd = request.form['password']

    result = user_service.dologin(name, pwd)
    if "error" in result:
        # 请求失败
        return redirect(url_for("user.login", error=1))

    session["username"] = result

    # 登陆成功，重定向显示页
    return redirect(url_for("index"))
    # print(result)
    
    # # 根据用户身份重定向
    # if result["TYPE"] == "1":
    #     return redirect(url_for("agent.govern_personal"))
    # return redirect(url_for("agent.school_personal"))


@user_blueprint.route('/login')
def login():
    # 商务登录
    if "username" in session:
        return redirect("index")

    err = request.args.get("error")
    return render_template("./components/login.html", error=err)


@user_blueprint.route('/manageLogin')
def manager_login():
    # 管理员登录
    return render_template("./components/manageLogin.html")


@user_blueprint.route("/logout")
def logout():
    # 商务注销
    session.pop("username", None)
    return redirect(url_for("user.login"))


@user_blueprint.route("/manageLogout")
def manager_logout():
    # 管理员注销
    return redirect(url_for("user.manager_login"))
