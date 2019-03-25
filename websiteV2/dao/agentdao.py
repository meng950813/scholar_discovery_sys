"""
author: xiaoniu
date: 2019-03-18
desc: 主要用在SchoolAgentService类中，简单封装了和数据库的交互的SQL语句
学校商务DAO
"""
import utils.db as db


class SchoolAgentDao:

    def get_relations_by_id(self, uid , isSchoolAgent = False):
        """
        获取id数组对应的所有有联系的人
        :param uid: 商务的id
        :param isSchoolAgent: 是否是学校商务操作
        :return: 所有和该商务有联系的数组
        """

        sql = 'select * from sys_net_of_school_agent where U_ID = ? and STATUS = 1'
        # 企商操作
        if not isSchoolAgent:
            sql = 'select * from sys_net_of_business_agent where U_ID = ? and STATUS = 1'

        results = db.select(sql, uid)

        return results

    def append_relation(self, info_dict , isSchoolAgent = False):
        """
        创建新的关系学校商务与高校老师的关系
        :param info_dict : 字典类型参数: 
        :param isSchoolAgent : 是否是学校商务操作
        :return: 插入的id / None
        """

        """ 需要插入的关键字包括：
            ID,U_ID,TEACHER_ID,TEACHER_NAME,COLLEGE_ID,COLLEGE_NAME,SCHOOL_ID,SCHOOL_NAME,REMARK,CREATION_TIME,LINK,STATUS
        """
        keys = ','.join(info_dict.keys())
        values = ','.join(['?'] * len(info_dict))

        string = 'insert into sys_net_of_school_agent ({keys}) values({values})'

        # 企商操作,更换数据库
        if not isSchoolAgent:
            string = 'insert into sys_net_of_business_agent ({keys}) values({values})'

        sql = string.format(keys=keys, values=values)

        return db.insert(sql, tuple(info_dict.values()))

    def update_relation(self, relation_id, info_dict , isSchoolAgent = False):
        """
        更新已经存在的联系
        :param relation_id: 联系的id
        :param info_dict: 要更新的数据，为字典，键表示数据库名；值为要更新的值
        :param isSchoolAgent: 是否是学校商务操作
        :return: 影响的行数
        """
        values = ['%s=?' % key for key in info_dict.keys()]
        params = ','.join(values)
        
        string = 'update sys_net_of_school_agent set {params} where ID = ?'
        
        # 企商操作,更换数据库
        if not isSchoolAgent:
            string = 'update sys_net_of_business_agent set {params} where ID = ?'

        sql = string.format(params=params)

        # 将字典转为列表, 目的是 保证将 relation_id 放于最后
        data = list(info_dict.values())
        # 添加 relation_id 于列表最后
        data.append(relation_id)

        return db.update(sql, *data)


school_agent_dao = SchoolAgentDao()

if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)

    # 查询语句
    # print(school_agent_dao.get_relations_by_id(100000))

    # 测试更新语句函数
    row_count = school_agent_dao.update_relation(15, {'TEACHER_ID': 100})
    print(row_count)
