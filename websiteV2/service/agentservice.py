"""
author: xiaoniu
date: 2019-03-22
desc: 内部调用了SchoolDao
"""
import utils
import datetime
from dao.agentdao import school_agent_dao


class SchoolAgentService:

    def get_relations_by_id(self, uid):
        """
        获取id数组对应的所有有联系的人
        :param uid: 商务的id
        :return: 已经按照学校名和学院名聚合的字典
        """
        results = school_agent_dao.get_relations_by_id(uid)
        # 按照学校和学院进行分类
        for result in results:
            result['CREATION_TIME'] = result['CREATION_TIME'].strftime('%Y/%m/%d')
        return results

    def append_relation(self, info_data):
        """
        格式化传入的参数
        :param info_data : 从前端获取的数据，字典类型，需要转化成如下格式
        :return :
                {
                    "success" : True/False,
                    "id" : 123
                }
        """
        info_dict = {
            "U_ID": info_data["user_id"],
            "TEACHER_ID": None,
            "TEACHER_NAME": info_data["contract_name"],
            "COLLEGE_ID": None,
            "COLLEGE_NAME": info_data["level_two"],
            "SCHOOL_ID": None,
            "SCHOOL_NAME": info_data['level_one'],
            "REMARK": info_data['remark'],
            "LINK": info_data["link_method"],
            "CREATION_TIME": info_data["create_time"]
        }

        new_line_id = school_agent_dao.append_relation(info_dict)
        # 执行成功，返回新记录 id
        if new_line_id:
            return {"success": True,"id": new_line_id}
        return {"success": False}

    def delete_relation(self, relation_id):
        """
        根据该条关系的id“删除”该条联系，逻辑上删除
        :param relation_id: 该条联系对应的id
        :return: 操作成功则返回true,否则返回false
        """
        info_dict = {'STATUS': 0}
        row_count = school_agent_dao.update_relation(relation_id, info_dict)

        return row_count == 1

    def update_relation(self, relation_id, info_data):
        """
        更新relation_id 对应的关系的值
        :param relation_id: 该条关系对应的id
        :param info_data:{ dict}
        :return: 操作成功则返回True,否则返回False
        """

        info_dict = {
            "TEACHER_NAME": info_data["contract_name"],
            "COLLEGE_NAME": info_data["level_two"],
            "SCHOOL_NAME": info_data['level_one'],
            "REMARK": info_data['remark'],
            "LINK": info_data["link_method"],
            "CREATION_TIME": info_data["create_time"]
        }

        row_count = school_agent_dao.update_relation(relation_id, info_dict)
        return row_count == 1


school_agent_service = SchoolAgentService()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)

    print(school_agent_service.get_relations_by_id(100000))
    # 插入语句测试
    # info_dict = {
    #     "user_id" : 100000,
    #     "teacher_id" : 73994,
    #     "contract_name" : "谢光辉",
    #     "college_id" : 1341,
    #     "level_two" : "农学院",
    #     "school_id" : 19024,
    #     "level_one" : "中国农业大学",
    #     "remark" : "备注-  33",
    #     "link_method" : "123@123.com",
    #     "create_time" : "2019-03-04 14:21:23"
    # }
    # print(school_agent_service.append_relation(info_dict))

    # 删除语句测试
    print('删除成功' if school_agent_service.delete_relation(15) else '删除失败')
