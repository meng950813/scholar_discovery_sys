"""
author: xiaoniu
date: 2019-03-05
desc: 实用工具包包含着一些常用的函数
"""

def handleRelations(teachers, relations, academic_titles):
    """
    处理老师之间的联系，并生成echarts对应的格式
    :param teachers: 老师信息数组 结构同es_teacher 目前仅仅用到了 NAME、TITLE、ID
    :param relations: 老师关系数组 内部字典结构，其结构同teacher_teacher
    :return: echarts4所需要的格式 类型为dict
    """
    # 每个类别所对应的颜色
    color = ["#EE6A50", "#4F94CD", "#DAA520", "#0000FF", "#FF0000"]
    # 类别
    categories = ['未知']
    nodes = []
    links = []
    # 预处理
    teacher_ids = {}
    for teacher in teachers:
        teacher_ids[teacher['ID']] = {
            'name': teacher['NAME'],
            'title': teacher['TITLE'] if (teacher['TITLE'] is not None and len(teacher['TITLE']) > 0) else '未知'
        }
    # 学术头衔
    for title_row in academic_titles:
        teacher_ids[title_row['TEACHER_ID']]['title'] = title_row['HONOR']
    # 获取老师关系 目前保证为无向图
    for relation in relations:
        teacher2_id = relation['teacher2_id']
        if teacher2_id not in teacher_ids.keys():
            continue
        teacher_id = relation['teacher1_id']
        teacher_name = teacher_ids[teacher_id].get('name')
        teacher_title = teacher_ids[teacher_id].get('title')
        # 合作论文次数
        paper_num = relation['paper_num']

        teacher2_name = relation['teacher2_name']
        teacher2_title = teacher_ids[teacher2_id].get('title')
        # 不添加自己到自己的边
        if teacher_id == teacher2_id:
            continue
        # 添加类别
        if teacher_title not in categories:
            categories.append(teacher_title)
        if teacher2_title not in categories:
            categories.append(teacher2_title)
        # 确定为无向边
        link = {'source': teacher2_name, 'target': teacher_name, 'weight': paper_num}
        if link not in links:
            links.append({'source': teacher_name, 'target': teacher2_name, 'weight': paper_num})
        # 确定顶点
        for node in nodes:
            if node.get('name') == teacher_name:
                node.get('value')[0] += paper_num
                break
        else:
            nodes.append({'category': categories.index(teacher_title), 'name': teacher_name, 'value':[ paper_num, teacher_id]})
        # 确定其他点
        for node in nodes:
            if node.get('name') == teacher2_name:
                node.get('value')[0] += paper_num
                break
        else:
            nodes.append({'category': categories.index(teacher2_title), 'name': teacher2_name, 'value': [paper_num, teacher2_id]})

    return {
        'categories': [{'name': x} for x in categories],
        'nodes': nodes,
        'links': links,
        'color': color[:len(categories)]
    }
