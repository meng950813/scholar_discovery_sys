from flask import Flask, render_template, url_for
import os
import os.path

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/graph')
def graph():
    return render_template('graph.html')


@app.route('/data/<filename>')
def get_resource(filename):
    #real_path = url_for('static', filename=filename)
    real_path = os.path.join(os.getcwd(), 'static', filename)

    fp = open(real_path, 'r', encoding='utf-8')
    content = fp.read()
    fp.close()

    return content


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)
