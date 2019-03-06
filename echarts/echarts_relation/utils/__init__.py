"""
author: xiaoniu
date: 2019-03-05
desc: 实用工具包包含着一些常用的函数
"""


def handleRelations(teachers, relations, academic_titles, total_categories):
    """
    处理老师之间的联系，并生成echarts对应的格式
    :param teachers: 老师信息dict 结构同es_teacher 目前仅仅用到了 NAME、TITLE、ID
    :param relations: 老师关系dict 内部字典结构，其结构同teacher_teacher
    :param academic_titles: 学术头衔列表
    :param total_categories: 总的头衔类别
    :return: echarts4所需要的格式 类型为dict
    """
    # 每个类别所对应的颜色
    color = ["#EE6A50", "#4F94CD", "#DAA520", "#0000FF", "#8FBC8F", "#5D478B", "#528B8B", "#483D8B", "#3A5FCD"]
    # 类别 使用到的类别所对应的索引 主要用于职称到颜色的对应
    categories = {}
    # 用到的职称
    titles = []
    nodes = []
    links = []
    # 学术头衔会覆盖原有的头衔
    for title_row in academic_titles:
        teachers[title_row['TEACHER_ID']]['TITLE'] = title_row['HONOR']
    # 获取老师关系 目前保证为无向图
    for relation in relations:
        teacher2_id = relation['teacher2_id']
        if teacher2_id not in teachers.keys():
            continue
        teacher_id = relation['teacher1_id']
        teacher_name = teachers[teacher_id].get('NAME')
        teacher_title = teachers[teacher_id].get('TITLE')
        # 合作论文次数
        paper_num = relation['paper_num']

        teacher2_name = relation['teacher2_name']
        teacher2_title = teachers[teacher2_id].get('TITLE')
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
            nodes.append(
                {'category': titles.index(teacher_title), 'name': teacher_name, 'value': [paper_num, teacher_id]})
        # 确定其他点
        for node in nodes:
            if node.get('name') == teacher2_name:
                node.get('value')[0] += paper_num
                break
        else:
            nodes.append({'category': titles.index(teacher2_title), 'name': teacher2_name,
                          'value': [paper_num, teacher2_id]})

    # 对类别进行一次排序
    data = {
        'categories': [{'name': title} for title in titles],
        'nodes': nodes,
        'links': links,
        'color': [color[index] for index in categories.values()]
    }
    return data


def db2python(results, key):
    """
    把数据库的list[dict]格式转为dict[id]={}格式，仅仅适用于key唯一的情况
    :param results: 从数据库中查询得到的数据列表 数据项格式为dict
    :param key: 主键 目前仅仅支持int或者str
    :return: 返回转换成功的dict
    """
    d = {}
    for result in results:
        result_id = result[key]
        result.pop(key)
        d[result_id] = result
    return d
