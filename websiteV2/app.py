from flask import Flask,render_template,redirect,url_for,request
from controllers.api import api_blueprint
from utils import db
from config import DB_CONFIG

app = Flask(__name__)
app.register_blueprint(api_blueprint)

# 需要预先调用，且只调用一次
db.create_engine(DB_CONFIG['user'], DB_CONFIG['pwd'], DB_CONFIG['db_name'])


@app.route('/')
def index():
    return render_template("basic.html")


@app.route('/relation')
def relation():
    return render_template('relation.html')


@app.route('/login/')
def login():
    #商务登录
    return render_template("./components/login.html")


@app.route('/manageLogin')
def manageLogin():
    #管理员登录
    return render_template("./components/manageLogin.html")


@app.route('/search')
def search():
    return render_template('./components/schoolScholar.html')



@app.route("/logout/")
def logout():
    #商务注销
    return redirect(url_for("login"))


@app.route("/manageLogout/")
def manageLogout():
    # 管理员注销
    return redirect(url_for("manageLogin"))

@app.route("/governPersonal/")
def governPersonal():
    #转到个人页面
    return render_template("./components/governPersonal.html")

@app.route("/schoolPersonal/")
def schoolPersonal():
    #转到个人页面
    return render_template("./components/schoolPersonal.html")



if __name__ == '__main__':
    app.run(debug=True)