import json
from flask import Flask, render_template, url_for, jsonify
import os.path

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


@app.route('/show_d3')
def index():
    return render_template('basic.html')


@app.route('/')
def echarts():
    return render_template('echarts_test.html')


@app.route('/mapdata/<path:filename>')
def get_data(filename):
    print(basedir)
    path = os.path.join(basedir, 'static', 'mapdata')
    
    print(os.path.join(path, filename))
    
    # 读取文件，若没有文件则返回空
    try:
        with open(os.path.join(path, filename), 'r', encoding='utf-8') as fp:
            map_data = json.load(fp)
    except FileNotFoundError:
        map_data = "[]"
    data = [{"name": datum['properties']['name'], "value": 0} for datum in map_data['features']]
    return jsonify({
        "geoJson": map_data,
        "data": data
    })


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run()
