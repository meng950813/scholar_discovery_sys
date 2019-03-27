"""
SchoolService
author: xiaoniu
date: 2019-03-14
desc: 内部调用了SchoolDao的函数，并提供了python下易用的函数
"""
from dao.schooldao import school_dao
import utils


class SchoolService:

    def __init__(self):
        self.NUMBER_KEYS = ['NKD_NUM', 'SKL_NUM', 'ACADEMICIAN_NUM']

    def get_position_by_names(self, school_names):
        """
        根据学校名获取到学校名对应的经纬度，并返回
        :param school_names: 学校名数组
        :return: schools['name'] = {'longitude': 100, 'latitude': 100}
        """
        if school_names is None or len(school_names) == 0:
            return None
        results = school_dao.get_position_by_names(school_names)
        schools = {}
        for result in results:
            name = result['NAME']
            position = result['POSITION']
            # 切割出经纬度
            arr = position.split(',')
            schools[name] = {'longitude': float(arr[0]), 'latitude': float(arr[1])}

        return schools

    def get_teachers_by_school(self, school_id, institution_id=None):
        """
        获取学校id或者(学校id,学院id)下的所有老师
        :param school_id: 学校的id
        :param institution_id: 该学校对应的学院的id
        :return:list[dict] 字典的格式详见es_teacher
        """
        results = school_dao.get_teachers_by_school(school_id, institution_id)
        # 转换成以id为键名，值为一个dict的数据项
        teachers = {}
        for result in results:
            teacher_id = result['ID']
            result.pop('ID')
            # 设置title
            result['TITLE'] = result['TITLE'] if (result['TITLE'] is not None and len(result['TITLE']) > 0) else '未知'
            teachers[teacher_id] = result
        return teachers

    def get_institutions_by_ids(self, school_id, institution_ids, keys=None):
        """
        给定学校id，和学院id数组来获取所有的学院信息
        :param school_id: 学校id
        :param institution_ids: 学校id下的学院id数组
        :param keys: 需要的键 至少包含键ID
        :return:以学院id为键，其余信息为值的字典
        """
        results = school_dao.get_institutions_by_ids(school_id, institution_ids, keys=keys)
        data = {}
        key = 'ID'
        # 转换成字典，键为ID
        for result in results:
            result_id = result[key]
            result.pop(key)
            self.normalization_institution(result)
            data[result_id] = result

        return data

    def get_total_scholars_by_schools(self, school_names):
        """
        获取学校的所有学者，以及种类
        :param school_names: 学校名称
        :return:
        """
        #                      重点学科   重点实验室  院士                长江学者    杰出青年
        keys = ['SCHOOL_NAME', 'NKD_NUM', 'SKL_NUM', 'ACADEMICIAN_NUM', 'CJSP_NUM', 'OUTSTANDING_NUM']
        trans_keys = ['key_subject', 'key_laboratory', 'academician', 'changjiang', 'outstanding']
        results = school_dao.get_total_colleges_by_names(school_names, keys)
        results = results if results is not None else []
        # 聚合，并设置成字典
        schools = {}
        for result in results:
            # 获取学校
            school_name = result['SCHOOL_NAME']
            if school_name not in schools:
                schools[school_name] = {}
            school = schools[school_name]
            # 设置数目
            for i in range(1, len(keys)):
                key = keys[i]
                trans_key = trans_keys[i - 1]
                number = result[key] if result[key] is not None else 0
                # 添加键
                if trans_key not in school:
                    school[trans_key] = 0
                school[trans_key] += number

        return schools

    def normalization_institution(self, institution):
        """
        对学院的信息进行标准化，如把出生日期转为年龄
        :param institution: 学院的信息字典
        :return: 转换好的学院信息，和参数institution相同
        """
        for key, value in institution.items():
            if key in self.NUMBER_KEYS:
                institution[key] = 0 if value is None else value
        return institution


school_service = SchoolService()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)

    # print(school_service.get_position_by_names(['清华大学', '北京大学']))
    # print(school_service.get_teachers_by_school(17134))
    # print(school_service.get_teachers_by_school(17134, 557))

    # institutions = school_service.get_institutions_by_ids(17134, [547, 548])
    # for _, institution in institutions.items():
    #     print(institution)
    print(school_dao.get_total_colleges_by_names(['东南大学', '清华大学']))
    print(school_service.get_total_scholars_by_schools(['东南大学', '清华大学']))
