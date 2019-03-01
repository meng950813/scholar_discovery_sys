from flask import Flask, render_template, url_for
import os
import os.path

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/official_demo')
def official_demo():
    return render_template('official_demo.html')


@app.route('/graph')
def graph():
    return render_template('graph.html')


@app.route('/user/<int:user_id>')
def user_homepage(user_id):
    return str(user_id)


@app.route('/data/<filename>')
def get_resource(filename):
    real_path = os.path.join(os.getcwd(), 'static', filename)

    fp = open(real_path, 'r', encoding='utf-8')
    content = fp.read()
    fp.close()

    return content


@app.route('/database/<name>')
def get_database(name):
    """
    从数据库中获取院系老师信息，并发送
    :param name: 院系名称
    :return: 院系老师之间的关系，格式为
    {
        'categories': ["杰青", "院士"],
         color:[类别对应的颜色],
         nodes:[id, 名字, 称号(索引), 权值],
         links:[id, id, 合作次数]}
    """
    pass


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)
