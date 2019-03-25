"""
author: xiaoniu
date: 2019-03-22
desc: 内部调用了SchoolDao
"""
import utils
import datetime
from dao.agentdao import school_agent_dao


class SchoolAgentService:

    def __init__(self):
        """
        初始化用于转换 前端-数据库 间 键名
        """
        self.school_agent_map = {
            "id" : "ID",                    "ID" : "id",
            "user_id" : "U_ID",                 "U_ID" : "user_id",
            "level_one" : "SCHOOL_NAME",    "SCHOOL_NAME" : "level_one",
            "level_two" : "COLLEGE_NAME",   "COLLEGE_NAME" : "level_two",
            "contract_name" : "TEACHER_NAME","TEACHER_NAME" : "contract_name",
            "remark" : "REMARK",            "REMARK" : "remark",
            "link_method" : "LINK",         "LINK" : "link_method",
            "create_time" : "CREATION_TIME","CREATION_TIME" : "create_time"
        }

        self.business_agent_map = {
            "id" : "ID",                    "ID" : "id",
            "user_id" : "U_ID",              "U_ID" : "user_id",
            "level_one" : "COMPANY_NAME",    "COMPANY_NAME" : "level_one",
            "level_two" : "DEPART_NAME",     "DEPART_NAME" : "level_two",
            "contract_name" : "CONTACT_NAME","CONTACT_NAME" : "contract_name",
            "remark" : "REMARK",            "REMARK" : "remark",
            "link_method" : "LINK",         "LINK" : "link_method",
            "create_time" : "CREATION_TIME","CREATION_TIME" : "create_time"
        }


    def get_relations_by_id(self, uid , isSchool = False):
        """
        获取id数组对应的所有有联系的人
        :param uid: 商务的id
        :param isSchool : 是否为学校商务
        :return: 已经按照学校名和学院名聚合的字典
        """
        results = school_agent_dao.get_relations_by_id(uid , isSchool)

        results_list = []
        # 按照学校和学院进行分类
        for result in results:
            result['CREATION_TIME'] = result['CREATION_TIME'].strftime('%Y/%m/%d')

            # 转化 键名
            results_list.append(self.change_key_of_agent(result,isSchool))

        return results_list

    def append_relation(self, info_data , isSchool = False):
        """
        格式化传入的参数
        :param info_data : 从前端获取的数据，字典类型，需要转化成如下格式
        :param isSchool : 是否为学校商务
        :return :
                {
                    "success" : True/False,
                    "id" : 123
                }
        """
        # info_dict = {
        #     "U_ID": info_data["user_id"],
        #     # "TEACHER_ID": None,
        #     "TEACHER_NAME": info_data["contract_name"],
        #     # "COLLEGE_ID": None,
        #     "COLLEGE_NAME": info_data["level_two"],
        #     # "SCHOOL_ID": None,
        #     "SCHOOL_NAME": info_data['level_one'],
        #     "REMARK": info_data['remark'],
        #     "LINK": info_data["link_method"],
        #     "CREATION_TIME": info_data["create_time"]
        # }

        info_dict = self.change_key_of_agent(info_data, isSchool)
        info_dict["U_ID"] = info_data["user_id"]
        
        new_line_id = school_agent_dao.append_relation(info_dict , isSchool)

        # 执行成功，返回新记录 id
        if new_line_id:
            return {"success": True,"id": new_line_id}
        return {"success": False}

    def delete_relation(self, relation_id, isSchool = False):
        """
        根据该条关系的id“删除”该条联系，逻辑上删除
        :param relation_id: 该条联系对应的id
        :return: 操作成功则返回true,否则返回false
        """
        info_dict = {'STATUS': 0}
        row_count = school_agent_dao.update_relation(relation_id, info_dict , isSchool)

        return row_count == 1

    def update_relation(self, relation_id, info_data ,isSchool = False):
        """
        更新relation_id 对应的关系的值
        :param relation_id: 该条关系对应的id
        :param info_data: { dict} 内容格式如下:
        {
            "level_one" : xx, 
            "level_two" : xx, 
            "contract_name" : xx, 
            "remark" : xx, 
            "link_method" : xx, 
            "create_time" : xx, 
        }
        :param isSchool: 判断该条信息是否为学校代理
        :return: 操作成功则返回True,否则返回False
        """

        # info_dict = {
        #     "TEACHER_NAME": info_data["contract_name"],
        #     "COLLEGE_NAME": info_data["level_two"],
        #     "SCHOOL_NAME": info_data['level_one'],
        #     "REMARK": info_data['remark'],
        #     "LINK": info_data["link_method"],
        #     "CREATION_TIME": info_data["create_time"]
        # }
       
        info_dict = self.change_key_of_agent(info_data , isSchool)

        if not info_dict:
            print("map转换失败")
            return False

        # 调用函数,更新数据
        row_count = school_agent_dao.update_relation(relation_id, info_dict, isSchool)

        return row_count == 1

    def change_key_of_agent(self,data_dict , isSchool = False):
        """
        用于商务发送数据的 前端->数据库 / 数据库->前端 字段名的转换
        :param data_dict: 需要转换的字典数据
        :param isSchool: 是否为学校商务
        :return: (dict) 新的键值对
        """
        new_dict = {}
        
        # 判断使用哪个mapping
        if isSchool:
            mapping = self.school_agent_map
        else:
            mapping = self.business_agent_map

        # 遍历键名
        for key in data_dict:

            # 若该键名不在 mapping 中, 跳过该键
            if not key in mapping:
                print("参数有误,无法转换")
                # return False
                continue

            # 重置字典键名
            new_dict[mapping[key]] = data_dict[key]
        
        # 返回新字典
        return new_dict

   

school_agent_service = SchoolAgentService()


if __name__ == '__main__':
    import utils.db as db
    from config import DB_CONFIG
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # 需要预先调用，且只调用一次
    db.create_engine(**DB_CONFIG)

    # print(school_agent_service.get_relations_by_id(100000))
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
