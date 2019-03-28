"""
author: xiaoniu
date: 2019-03-24
desc: 主要用在TeacherService类中，简单封装了和数据库的交互的SQL语句
"""
import utils.db as db


class TeacherDao:
    def get_relations_by_ids(self, id_list):
        """
        获取老师id对应的所有有联系的老师id
        :param id_list: 老师id数组
        :return: 所有和该老师有联系的数组
        """
        string = 'select * from teacher_teacher where teacher1_id in (%s)'
        sql = string % (','.join(['?' for id in id_list]))
        results = db.select(sql, *id_list)

        return results

    def get_teachers_by_ids(self, id_list, keys=None):
        """
        根据老师id数组获取所有的老师
        :param id_list: 老师id所组成的数组
        :param keys: 要获得的键值数组 如['ID', 'NAME'] 为空则获取所有的键值对
        :return: 查询成功的结果数组
        """
        string = "select %s from es_teacher where ID in (%s)" %\
                 (','.join(keys) if keys is not None else '*', '%s')
        # 设置占位符
        sql = string % (','.join(['?' for id in id_list]))

        results = db.select(sql, *id_list)
        return results

    def get_academic_titles_by_ids(self, id_list):
        """
        根据老师id数组获取存在的头衔
        :param id_list: 老师id所组成的数组
        :return:返回存在的老师头衔数组
        """
        string = "select * from es_honor where TYPE='学术头衔' and TEACHER_ID IN (%s)"
        sql = string % (','.join(['?' for id in id_list]))

        results = db.select(sql, *id_list)
        return results

    def get_total_academic_titles(self):
        """
        获取所有的学术头衔
        :return: 学术头衔数组
        """
        sql = "select HONOR from es_honor where TYPE ='学术头衔' group by HONOR"
        results = db.select(sql)

        return results

    def get_papers_by_id(self, teacher_id, keys=None):
        """
        根据老师id获取他的所有论文
        :param teacher_id: 老师的id
        :param keys:
        :return:
        """
        sql = "select %s from eds_paper_clean where author_id=?" % \
                 (','.join(keys) if keys is not None else '*')
        results = db.select(sql, teacher_id)
        return results

    def get_paper_partners_by_md5(self, md5_list, keys=None):
        """
        根据md5数组获取与之有合作的所有的合伙人信息
        :param md5_list: md5数组，它是论文标题的对应
        :param keys: 要获取的键值对
        :return: 有过合作的合伙人
        """
        # 从es_teacher表中获取老师的具体信息
        string1 = 'select %s from es_teacher where ID in (%s)' % (','.join(keys) if keys is not None else '*', '%s')
        # 从eds_paper_clean表中获取论文信息
        string2 = 'select author_id from eds_paper_clean where paper_md5 in (%s)'  % (','.join(['?' for _ in md5_list]))
        sql = string1 % string2

        results = db.select(sql, *md5_list)
        return results


teacher_dao = TeacherDao()


if __name__ == '__main__':
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)
    # # 获取该老师的所有关系
    # self_relations = teacher_dao.get_relations_by_ids([150896])
    # print(self_relations)
    # # 获取teacher2_id的所有id
    # teacher_ids = [relation['teacher2_id'] for relation in self_relations]
    # # 获取老师相关信息
    # teacher_list = teacher_dao.get_teachers_by_ids(teacher_ids)
    # # teacher_list = teacher_dao.get_teachers_by_ids(teacher_ids, ['ID', 'NAME'])
    # print('老师信息')
    # print(teacher_list)
    # # 获取老师对应的存在的学术头衔
    # academic_titles = teacher_dao.get_academic_titles_by_ids(teacher_ids)
    # print(academic_titles)
    # # 获取所有学术头衔
    # total_categories = teacher_dao.get_total_academic_titles()
    # print(total_categories)

    # print(teacher_dao.get_papers_by_id(100874))

    print(teacher_dao.get_paper_partners_by_md5(['7cfad1665f03661b9e6af69e24dfe412', '614cbcd6779f55e3000a73bc033c0626', 'ddab1c5f56972c1ed030a1edad4665e8', 'cd0e73b2471361f2101eaf26bf0d32ed', '87b4edeea2db031ed4f4f0128bfeee8c', 'c621196f1636f518963266975c0f51fa', '87db0220e223e48fd8e414d2c9ac4c99', 'ff843bafd49652352094458b90c3f571', 'f54d536326f68810d82c4c88c9abeb69', '7300d2a2a86d558a45719e8ab878ffff', 'ebb0362d5f4f90f80b66a5867c6e43e6', 'f75fa90e27a75adc4f55bac88ca18930', '6f480ed8ceb0347154e70eb23e5791d6', '06a16c85559e9b7d906c75cfc442ddd9', '68ec189dee4dcb708d49a7788b99552f', 'a7880df016ea793a9f0c884ccd3afe52', '6ad61b2350636e3ae1da6fdd7028c41c', '5186cb7a2e865d59ea0952ca9f545a39', '77796de7ec22583d9f90a9ddb66238fe', '6716c2de17c278d6a510a8d2d037610c', '95fb00074f96b5eabb7a196f71cc27f1', 'e25a5d030895ff0b917814a7fa8d7cef', '1e3b712b88f2a192c0ace70df634454c', 'ec009e2272b6ecb076e38ffe3e5490ae']))

