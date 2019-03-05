"""
TeacherService
author: xiaoniu
date: 2019-03-05
desc: 内部调用了TeacgerDao的函数，并提供了python下易用的函数
"""
from dao.teacherdao import teacher_dao


class TeacherService:

    def getRelationById(self, id):
        """
        根据老师的id获取与此老师有关的所有联系
        :param id: 老师id
        :return: 与该id有联系的所有id的数组，联系为dict结构，具体结构见teacher_teacher表
        """
        return teacher_dao.getRelationsById(id)

    def getRelationsByIds(self, ids):
        """
        从teacher_teacher表中获取在ids列表内的所有关系列表
        :param ids: 老师id列表 list
        :return: 符合ids内的所有关系数组，内部为字典dict结构，键名见teacher_teacher表
        """
        string = ','.join([str(id) for id in ids])
        params = '(' + string + ')'

        return teacher_dao.getRelationsByIds(params)

    def getTeachersByIds(self, ids):
        """
        获取ids列表中的所有老师信息
        :param ids: 老师的id组成的数组 list
        :return: 相关的所有老师信息数组 老师结构为字典dict结构，键名见es_teacher表
        """
        string = ','.join([str(id) for id in ids])
        params = '(' + string + ')'

        return teacher_dao.getTeachersByIds(params)

    def getAcademicTitlesByIds(self, ids):
        """
        根据老师id列表中的id获取存在的学术头衔列表
        :param ids: 老师id数组 list
        :return: 学术头衔数组,内部数据项为字典dict结构，键名见es_honor表
        """
        string = ','.join([str(id) for id in ids])
        param = '(' + string + ')'

        return teacher_dao.getAcademicTitlesByIds(param)


teacher_service = TeacherService()


if __name__ == '__main__':
    import dao.db as db
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine('root', '9527', 'training')

    print(teacher_service.getRelationById(150896))
    print(teacher_service.getRelationsByIds([150896, 85311]))
