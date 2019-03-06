from flask import Flask, render_template, url_for
import os, os.path, json, logging
import db

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
# 初始化数据库
db.create_engine('root', '9527', 'training')


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
    """
    sql_id = """SELECT es_teacher.ID,es_teacher.NAME,es_teacher.TITLE from es_teacher 
        where es_teacher.SCHOOL_ID = ? and es_teacher.INSTITUTION_ID = ?"""
    sql_relation = "select * from teacher_teacher WHERE teacher1_id in (%s)"
    # 保存数据
    categories = ['未知']
    nodes = []
    links = []
    color = ["#EE6A50", "#4F94CD", "#DAA520", "#00FF00", "#0000FF"]
    # 保存该院系所有老师的id
    teacher_ids = {}

    teachers = db.select(sql_id, 19024, 1341)
    for teacher in teachers:
        teacher_ids[teacher['ID']] = {
            'name': teacher['NAME'],
            'title': teacher['TITLE'] if (teacher['TITLE'] is not None and len(teacher['TITLE']) > 0) else '未知'
        }

    # TODO:目前应该存在数据库查询问题
    relations = db.select(sql_relation % ','.join(len(teacher_ids) * ['?']), *teacher_ids.keys())
    # 获取老师关系
    for relation in relations:
        if relation['teacher2_id'] not in teacher_ids.keys():
            continue
        teacher_id = relation['teacher1_id']
        teacher_name = teacher_ids[teacher_id].get('name')
        teacher_title = teacher_ids[teacher_id].get('title')
        # 不添加自己的线条
        if teacher_id == relation['teacher2_id']:
            continue
        # 添加类别
        if teacher_title not in categories:
            categories.append(teacher_title)

        # 确定为无向边
        link = {'source': relation['teacher2_name'], 'target': teacher_name, 'weight': relation['paper_num']}

        if link not in links:
            links.append({'source': teacher_name, 'target': relation['teacher2_name'], 'weight': relation['paper_num']})
        # 确定顶点
        for node in nodes:
            if node.get('name') == teacher_name:
                node.get('value')[0] += 1
                break
        else:
            nodes.append({'category': categories.index(teacher_title), 'name': teacher_name, 'value': [1, teacher_id]})


    return json.dumps({
        'categories': [{'name': x} for x in categories],
        'color': color[:len(categories)],
        'nodes': nodes,
        'links': links})


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)
