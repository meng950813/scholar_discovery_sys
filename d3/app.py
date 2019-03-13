from flask import Flask, render_template, url_for
import os.path

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('map.html')


@app.route('/mapdata/<path:filename>')
def get_data(filename):
    path = os.path.join(os.getcwd(), 'static', 'mapdata')
    print(os.path.join(path, filename))
    # 读取文件，若没有文件则返回空
    try:
        with open(os.path.join(path, filename), 'r', encoding='utf-8') as fp:
            data = fp.read()
    except FileNotFoundError:
        data = "[]"
    return data


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run()
