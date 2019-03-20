"""
author: xiaoniu
date: 2019-03-18
desc: 获取老师对应的关键字,用于生成词云
"""
import os
import pickle


base_path = None

# 确定资源路径
if __name__ == '__main__':
    base_path = os.path.join(os.getcwd(), '..', 'static', 'querydata')
else:
    base_path = os.path.join(os.getcwd(), 'static', 'querydata')

teacher_words = pickle.load(open(os.path.join(base_path, 'teacherWordForWordCloud'), 'rb'))
teacher_info = pickle.load(open(os.path.join(base_path, 'teacherName'), 'rb'))


def get_keywords_of_id(teacher_id):
    """
    根据老师id获取对应的关键字
    :param teacher_id: 老师的id
    :return: 返回该老师对应递减的关键字和对应的权值，若不存在该老师对应的关键字则返回None
    """
    keywords = None
    try:
        keywords = teacher_words[teacher_id]
    except KeyError as e:
        print(e)

    return keywords


if __name__ == '__main__':
    for teacherId in teacher_words:
        # 打印ID为teacherId的教师的名字
        print(teacher_info[teacherId], teacherId)
        # 打印ID为teacherId的教师对应的词及其得分，词按得分降序排列
        print(teacher_words[teacherId])
        print()
