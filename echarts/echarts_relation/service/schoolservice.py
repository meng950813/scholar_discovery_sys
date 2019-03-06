"""
SchoolService
author: xiaoniu
date: 2019-03-05
desc: 内部调用了SchoolDao的函数，并提供了python下易用的函数
"""
from dao.schooldao import school_dao


class SchoolService:
    def getTeachers(self, *params):
        """
        根据学校名或学校名和学院名获取符合条件的所有老师
        :param params: str或str, str，前者是获取该学校的所有老师；后者是获取该学校对应学院的所有老师
        :return:符合条件的所有老师数组，老师的结构为dict,其键名见es_teacher
        """
        school_id, institution_id = school_dao.getIdByName(*params)

        if institution_id is None:
            return school_dao.getTeachers(school_id)
        else:
            return school_dao.getTeachers(school_id, institution_id)


school_service = SchoolService()


if __name__ == '__main__':
    import dao.db as db
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine('root', '9527', 'training')

    print(school_service.getTeachers('东南大学', '计算机科学与工程学院'))
    print(school_service.getTeachers('东南大学'))
