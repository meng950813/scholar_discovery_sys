"""
author: xiaoniu
date: 2019-03-14
desc: 实用工具包包含着一些常用的函数
"""
import utils.wordcloud


def db2python(results, key):
    """
    把数据库的list[dict]格式转为dict[id]={}格式，仅仅适用于key唯一的情况
    :param results: 从数据库中查询得到的数据列表 数据项格式为dict
    :param key: 主键 目前仅仅支持int或者str
    :return: 返回转换后的dict
    """
    d = {}
    for result in results:
        result_id = result[key]
        result.pop(key)
        d[result_id] = result
    return d
