"""
author: xiaoniu
date: 2019-03-18
desc: 主要用在TeacherService类中，简单封装了和数据库的交互的SQL语句
"""
from dao.teacherdao import teacher_dao
import json
import time


class TeacherService:

    def __init__(self):
        self.teacher_info_mapping = {
            'ID': 'id', 'NAME': 'name', 'FIELDS': 'fields', 'EMAIL': 'email', 'EDUEXP': 'eduexp',
            'SCHOOL_ID': 'school_id', 'INSTITUTION_ID': 'institution_id'
        }

    @staticmethod
    def get_relations_by_ids(id_list):
        """
        获取老师id对应的所有有联系的老师id
        :param id_list: 老师id数组 或单个id
        :return: array
        """
        if isinstance(id_list, int):
            id_list = [id_list]
        results = teacher_dao.get_relations_by_ids(id_list)
        return results

    def get_teachers_by_ids(self, id_list, keys=None):
        """
        根据老师id数组获取所有的老师
        :param id_list: 老师id所组成的数组
        :param keys: 要获得的键值数组 如['ID', 'NAME'] 为空则获取所有的键值对
        :return: 查询成功的结果数组
        """
        results = teacher_dao.get_teachers_by_ids(id_list, keys=keys)
        # 转换成键值对的形式
        teachers = {}
        for result in results:
            teacher_id = result['ID']
            teachers[teacher_id] = self.normalization_teacher(result)
        return teachers

    def get_teacher_info_by_id(self, teacher_id):
        keys = ['ID', 'NAME', 'TITLE', 'EMAIL', 'FIELDS', 'ACADEMICIAN', 'OUTYOUTH', 'CHANGJIANG', 'BIRTHYEAR', 'EDUEXP']
        result = teacher_dao.get_teachers_by_ids([teacher_id], keys=keys)[0]
        info = self.normalization_teacher(result, False)
        return info

    def get_academic_titles_by_ids(self, id_list):
        """
        根据老师id数组获取存在的头衔
        :param id_list: 老师id所组成的数组
        :return:返回存在的老师头衔数组
        """
        results = teacher_dao.get_academic_titles_by_ids(id_list)
        return results

    def get_total_academic_titles(self):
        """
        获取所有的学术头衔
        :return: 学术头衔数组
        """
        results = teacher_dao.get_total_academic_titles()
        total_titles = [result['HONOR'] for result in results]

        return total_titles

    def get_papers_by_id(self, teacher_id):
        """
        获取老师的所有论文数组
        :param teacher_id: 老师id
        :return: 论文信息数组
        """
        keys = ['name', 'org', 'year', 'cited_num', 'author', 'paper_md5']
        results = teacher_dao.get_papers_by_id(teacher_id, keys=keys)
        return results

    def get_paper_partners_by_md5(self, md5_list):
        """
        根据md5数组获取与之有合作的所有的合伙人信息
        :param md5_list: md5数组，它是论文标题的对应
        :return: 有过合作的合伙人
        """
        keys = ['ID', 'NAME', 'TITLE', 'SCHOOL_ID', 'INSTITUTION_ID', 'ACADEMICIAN', 'OUTYOUTH', 'CHANGJIANG']
        results = teacher_dao.get_paper_partners_by_md5(md5_list, keys)
        # 转换成键值对的形式
        teachers = []
        for result in results:
            teacher = self.normalization_teacher(result)
            teachers.append(teacher)
        return teachers

    def normalization_teacher(self, teacher, isFieldList=True):
        """
        对老师的信息进行标准化，如把出生日期转为年龄
        :param teacher: 老师的信息字典
        :param isFieldList: 老师关键字是否只有值
        :return: 转换好的老师信息，和参数teacher相同
        """
        info = {}
        honor_keys = ['ACADEMICIAN', 'OUTYOUTH', 'CHANGJIANG']
        for key, value in teacher.items():
            trans_key = self.teacher_info_mapping.get(key, None)
            # 转换领域
            if key == 'FIELDS':
                if value is not None:
                    fields = value.replace("\'", "\"")
                    if isFieldList:
                        info[trans_key] = tuple(json.loads(fields).keys())
                    else:
                        info[trans_key] = fields
                else:
                    info[trans_key] = []
            elif key == 'TITLE':
                info['title'] = value if (value is not None and len(value) > 0) else '未知'
            elif key == 'BIRTHYEAR' and value is not None:
                info['yearsold'] = time.localtime(time.time()).tm_year - int(teacher['BIRTHYEAR'])
            elif key in honor_keys:
                info[key] = 0 if value is None else value
            elif trans_key is not None:
                info[trans_key] = teacher[key]
            else:
                info[key] = teacher[key]

        return info


teacher_service = TeacherService()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)
    # 获取该老师的所有联系
    # self_relations = teacher_service.get_relations_by_ids(150896)
    # print(self_relations)
    # # 获取teacher2_id的所有id
    # teacher_ids = [relation['teacher2_id'] for relation in self_relations]
    # # 获取所有老师相关信息
    # teacher_list = teacher_service.get_teachers_by_ids(teacher_ids)
    # print(teacher_list)

    # print(teacher_service.get_total_academic_titles())
    # id_arr = [159822, 159729, 159835, 159805, 159742, 159842, 159739, 159808, 159737, 159828, 99181, 99236, 99318, 99329, 99304, 99234, 99252, 99259]
    # print(teacher_service.get_teacher_info_by_id(73932))
    # print(teacher_service.get_papers_by_id(100874))
    # 测试论文
    print(teacher_service.get_paper_partners_by_md5(['7cfad1665f03661b9e6af69e24dfe412', '614cbcd6779f55e3000a73bc033c0626', 'ddab1c5f56972c1ed030a1edad4665e8', 'cd0e73b2471361f2101eaf26bf0d32ed', '87b4edeea2db031ed4f4f0128bfeee8c', 'c621196f1636f518963266975c0f51fa', '87db0220e223e48fd8e414d2c9ac4c99', 'ff843bafd49652352094458b90c3f571', 'f54d536326f68810d82c4c88c9abeb69', '7300d2a2a86d558a45719e8ab878ffff', 'ebb0362d5f4f90f80b66a5867c6e43e6', 'f75fa90e27a75adc4f55bac88ca18930', '6f480ed8ceb0347154e70eb23e5791d6', '06a16c85559e9b7d906c75cfc442ddd9', '68ec189dee4dcb708d49a7788b99552f', 'a7880df016ea793a9f0c884ccd3afe52', '6ad61b2350636e3ae1da6fdd7028c41c', '5186cb7a2e865d59ea0952ca9f545a39', '77796de7ec22583d9f90a9ddb66238fe', '6716c2de17c278d6a510a8d2d037610c', '95fb00074f96b5eabb7a196f71cc27f1', 'e25a5d030895ff0b917814a7fa8d7cef', '1e3b712b88f2a192c0ace70df634454c', 'ec009e2272b6ecb076e38ffe3e5490ae']))
