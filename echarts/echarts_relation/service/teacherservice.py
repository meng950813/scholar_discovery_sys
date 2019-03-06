"""
TeacherService
author: xiaoniu
date: 2019-03-05
desc: 内部调用了TeacgerDao的函数，并提供了python下易用的函数
"""
from dao.teacherdao import teacher_dao


class TeacherService:

    def getRelationById(self, teacher_id):
        """
        根据老师的id获取与此老师有关的所有联系
        :param teacher_id: 老师id
        :return: 与该id有联系的所有id的dict，值为dict结构，具体结构见teacher_teacher表
        """
        results = teacher_dao.getRelationsById(teacher_id)
        return results

    def getRelationsByIds(self, teacher_id_list):
        """
        从teacher_teacher表中获取在ids列表内的所有关系列表
        :param teacher_id_list: 老师id列表 list
        :return: 符合ids内的所有关系dict，键为teacher1_id，值为字典dict结构，其余键名见teacher_teacher表
        """
        string = ','.join([str(id) for id in teacher_id_list])
        params = '(' + string + ')'

        results = teacher_dao.getRelationsByIds(params)
        return results

    def getTeachersByIds(self, teacher_id_list):
        """
        获取ids列表中的所有老师信息
        :param teacher_id_list: 老师的id组成的数组 list
        :return: 相关的所有老师信息数组 老师结构键为ID,值为字典dict结构，详细见es_teacher表
        """
        string = ','.join([str(id) for id in teacher_id_list])
        params = '(' + string + ')'

        results = teacher_dao.getTeachersByIds(params)
        # 转换成键值对的形式
        teachers = {}
        for result in results:
            teacher_id = result['ID']
            result.pop('ID')
            # 设置title
            result['TITLE'] = result['TITLE'] if (result['TITLE'] is not None and len(result['TITLE']) > 0) else '未知'
            teachers[teacher_id] = result
        return teachers

    def getAcademicTitlesByIds(self, teacher_id_list):
        """
        根据老师id列表中的id获取存在的学术头衔列表，
        考虑到有的老师会有多个头衔，因此未进行转换
        :param teacher_id_list: 老师id数组 list
        :return: 学术头衔数组,,内部数据项为字典dict结构，详细见es_honor表
        """
        string = ','.join([str(id) for id in teacher_id_list])
        param = '(' + string + ')'

        return teacher_dao.getAcademicTitlesByIds(param)

    def getCategoriesOfAcademicTitles(self):
        """
        从数据库中获取学术头衔类别并返回
        :return: 返回学术头衔数组
        """
        results = teacher_dao.getCategoriesOfAcademicTitles()
        # 把结果转化为数组
        academic_titles = [result['HONOR'] for result in results]
        return academic_titles


teacher_service = TeacherService()


if __name__ == '__main__':
    import utils.db as db
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine('root', '9527', 'training')

    print(teacher_service.getRelationById(150896))
    print(teacher_service.getRelationsByIds([150896, 85311]))
    print(teacher_service.getTeachersByIds([150896]))
    print(teacher_service.getAcademicTitlesByIds([134862]))
    print(teacher_service.getCategoriesOfAcademicTitles())
