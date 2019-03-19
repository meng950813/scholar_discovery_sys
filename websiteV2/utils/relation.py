"""
author: xiaoniu
date: 2019-03-19
desc: 用于处理关系图的部分函数
"""


def handle_relations(teachers, relations, academic_titles, total_categories):
    """
    处理老师之间的联系，并生成echarts对应的格式
    :param teachers: 老师信息dict 结构同es_teacher 目前仅仅用到了 NAME、TITLE、ID
    :param relations: 老师关系dict 内部字典结构，其结构同teacher_teacher
    :param academic_titles: 学术头衔列表
    :param total_categories: 总的头衔类别
    :return: relation.js所需要的格式 类型为dict
    """
    # 每个类别所对应的颜色
    color = ["#EE6A50", "#4F94CD", "#DAA520", "#0000FF", "#8FBC8F", "#5D478B", "#528B8B", "#483D8B", "#3A5FCD"]
    # 类别 使用到的类别所对应的索引 主要用于职称到颜色的对应
    categories = {}
    # 用到的职称
    titles = []
    nodes = []
    links = []
    # 老师id和索引对应表
    id_index_map = {}
    # 学术头衔会覆盖原有的头衔
    for title_row in academic_titles:
        teachers[title_row['TEACHER_ID']]['TITLE'] = title_row['HONOR']
    # 获取老师关系 并保证为无向图
    for relation in relations:
        teacher2_id = relation['teacher2_id']
        if teacher2_id not in teachers.keys():
            continue
        teacher_id = relation['teacher1_id']
        teacher_name = teachers[teacher_id].get('NAME')
        teacher_title = teachers[teacher_id].get('TITLE')
        teacher2_name = relation['teacher2_name']
        teacher2_title = teachers[teacher2_id].get('TITLE')
        # 合作论文次数
        paper_num = relation['paper_num']
        # 不添加自己到自己的边
        if teacher_id == teacher2_id:
            continue
        # 设置类别
        for title in set([teacher_title, teacher2_title]):
            if title not in categories:
                # 如果该头衔不在总头衔中，默认为第一个
                if title not in total_categories:
                    categories[title] = 0
                    titles.append(total_categories[0])
                else:
                    categories[title] = total_categories.index(title)
                    titles.append(title)
        # 尝试添加节点
        temp_list = [{'title': teacher_title, 'name': teacher_name, 'id': teacher_id},
                     {'title': teacher2_title, 'name': teacher2_name, 'id': teacher2_id}]
        for data in temp_list:
            for node in nodes:
                if node['id'] == data['id']:
                    node['radius'] += paper_num
                    break
            else:
                nodes.append({'category': titles.index(data['title']), 'name': data['name'],
                              'radius': paper_num, 'id': data['id']})
                id_index_map[data['id']] = len(nodes) - 1
        # 确定为无向边，添加边
        link = {'source': id_index_map[teacher2_id], 'target': id_index_map[teacher_id], 'width': paper_num}
        if link not in links:
            links.append({'source': id_index_map[teacher_id], 'target': id_index_map[teacher2_id], 'width': paper_num})
    # 整合数据并返回
    data = {
        'categories': [{'name': title, 'color': color[categories[title]]} for title in titles],
        'nodes': nodes,
        'links': links,
    }
    return data
