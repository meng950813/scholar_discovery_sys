from flask import Flask,render_template
from controllers.api import api_blueprint
from utils import db

app = Flask(__name__)
app.register_blueprint(api_blueprint)

# 需要预先调用，且只调用一次
db.create_engine('db_user', 'pwd', 'db_name')


@app.route('/')
def index():
    return render_template("basic.html")


if __name__ == '__main__':
    app.run(debug=True)
