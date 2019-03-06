"""
SchoolService
author: xiaoniu
date: 2019-03-05
desc: 内部调用了SchoolDao的函数，并提供了python下易用的函数
"""
from dao.schooldao import school_dao


class SchoolService:
    def getTeachersBySchool(self, school_name, institution_name=None):
        """
        根据学校名或学校名和学院名获取符合条件的所有老师
        :param school_name: 学校名
        :param institution_name: 学校下的学院名
        :return:符合条件的所有老师数组，老师的结构为dict,其键名见es_teacher
        """
        school_id, institution_id = school_dao.getSchoolIdByName(school_name, institution_name)

        results = None
        if institution_id is None:
            results = school_dao.getTeachers(school_id)
        else:
            results = school_dao.getTeachers(school_id, institution_id)
        # 转换成以id为键名，值为一个dict的数据项
        teachers = {}
        for result in results:
            teacher_id = result['ID']
            result.pop('ID')
            # 设置title
            result['TITLE'] = result['TITLE'] if (result['TITLE'] is not None and len(result['TITLE']) > 0) else '未知'
            teachers[teacher_id] = result
        return teachers

    def getSchoolsByKeyword(self, keyword):
        """
        根据关键字匹配学校和对应的学院，并返回
        :param keyword: 关键字
        :return: 学校数组和学院数组
        """
        results = school_dao.getSchoolsByKeyword(keyword)
        # 转换
        schools = []
        colleges = []
        for result in results:
            school_name = result['SCHOOL_NAME']
            address = result['INSTITUTION_ADDRESS']

            # 加入学院
            colleges.append({'school': school_name, 'institution': result['NAME'], 'address': address, 'position': result['POSITION']})
            # 加入学校和对应的地址
            for school in schools:
                if school['name'] == school_name:
                    break
            else:
                schools.append({'name': school_name, 'address': address})

        return schools, colleges



school_service = SchoolService()


if __name__ == '__main__':
    import utils.db as db
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine('root', '9527', 'training')

    print(school_service.getTeachersBySchool('东南大学', '计算机科学与工程学院'))
