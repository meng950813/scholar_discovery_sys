from flask import Flask,render_template
from controllers.api import api_blueprint
from utils import db

app = Flask(__name__)
app.register_blueprint(api_blueprint)
# 需要预先调用，且只调用一次
db.create_engine('root', '9527', 'training')


@app.route('/')
def index():
    return render_template("map.html")


if __name__ == '__main__':
    app.run(debug=True)
