from db_operate.dbhelper import DBhelper
'''
2019.2.27
该代码用于建立数据库project2中teacher表和paper表之间的联系
by zs

'''
def get_school_info():
    '''
    从es_school表中获取学校的 id， name 组成{id， name}形式的列表并返回
    :return:
    '''
    school_info = DBhelper.execute("select id, NAME from es_school ")
    school_dict = {}
    for i in school_info:
        school_dict[i[0]] = i[1]
    # print(school_dict)
    return school_dict

def get_institution_info():
    '''
    从es_institution表中获取学院的id， name，组成{id， name}的形式返回
    :return:
    '''
    institution_info = DBhelper.execute("select ID, `NAME` from es_institution")

    institution_dict = {}
    for i in institution_info:
        institution_dict[i[0]] = i[1]
    # print(institution_dict)
    return institution_dict


def get_teacher_info(school_dict, institution_dict):
    '''
    接受参数来获取学校与学院各自id和name的对应关系，
    并从es_teacher表中获取教师的name，school_id, institution_id ,id，组成{(name, school_name, institution_name) : teacher_id}并返回
    :param school_dict: {id，name}
    :param institution_dict: {id, name}
    :return: { name: [(school_name, institution_name, teacher_id), (name,sc..., ins...)...], ...}
    '''

    teacher_info = DBhelper.execute("SELECT name, school_id, institution_id, id from es_teacher")
    teacher_dict = {}
    for i in teacher_info:
        # print(i)
        name = i[0]
        school_id = i[1]
        institution_id = i[2]
        teacher_id = i[3]

        school_name = school_dict[school_id]
        # print(institution_id)
        if institution_dict.__contains__(institution_id):
            institution_name = institution_dict[institution_id]
        else:
            institution_name = ""
        if teacher_dict.__contains__(name):
            teacher_dict[name].append((school_name, institution_name, teacher_id))
        else:
            teacher_dict[name] = [(school_name, institution_name, teacher_id)]
        print(teacher_dict[name])

    return teacher_dict

def get_teacher_info2():
    '''
    调用get_teacher_info(school_dict, institution_dict)获取teacher_dict
    :return:
    '''
    school_dict = get_school_info()
    institution_dict = get_institution_info()
    return get_teacher_info(school_dict, institution_dict)


def parse_school_name(str):
    '''

    :param str:解析传过来的学校的名字，“**大学***学院” --->  "**大学"
    :return:["**大学", ..]
    '''
    if str == "":
        return []
    if str[-1] == "学" and str[-2] == "大":
        return [str]
    for i in range(len(str)-1):
        if str[i] == "大" and str[i+1] == "学":
            return [str[0: i+2],str[i+2:]]
    return [str]


def parse_institution_name(str):
    '''

    :param str:
    :return:
    '''
    if len(str) == 0:
        return ""
    if str[-2] == "学" and str[-1] == "院":
        return str[0: len(str)-2]
    elif str[-2] == "中" and str[-1] == "心":
        return str[0: len(str) - 2]
    elif str[-1] == "系":
        return str[0: len(str)-1]
    else:
        return str

import json
def get_paper_author(teacher_dict):
    '''
    用于获取论文的id，以及author 的信息，
    解析author的信息，并与teacher_dict中的name，school，institution对照，看是否为同一个人，如果是，则将其加入到新表当中
    :param teacher_dict:
    :return:
    '''
    author_info = DBhelper.execute("SELECT id, author from paper")
    author_dict = {}
    count = 0
    res = ""
    for t in author_info:
        paper_id = t[0] #
        author_str = t[1] #
        author_list = json.loads(author_str) #
        # print(author_list)
        for d in author_list:  #[  {"name":***, "org":"***"},  {}  ]
            name = d["name"] #论文中的作者名字
            school_info = d["org"] #论文中的学校学院名字
            school_institution = parse_school_name(school_info)
            if teacher_dict.__contains__(name):
                same_name_teacher_list = teacher_dict[name]
            else:
                continue
            for t in same_name_teacher_list:
                teacher_school = t[0]
                teacher_institution = parse_institution_name(t[1])
                count += 1
                if len(school_institution) == 2:
                    if teacher_school == school_institution[0] and teacher_institution in school_institution[1]:
                        teacher_id = t[2]
                        # print(teacher_id)
                        res += "(" + str(teacher_id) + "," + str(paper_id)+"),"
                        # continue
                elif len(school_institution) == 1:
                    if teacher_school == school_institution[0]:
                        teacher_id = t[2]
                        res += "(" + str(teacher_id) + "," + str(paper_id) + "),"
                        # print(teacher_id)
                if count >= 5000:
                    count = 0
                    res = res[0:len(res)-1]
                    sql = "insert into teacher_paper(teacher_id, paper_id) values" + res
                    DBhelper.execute(sql)
                    print(sql)
                    res = ""
    res = res[0:len(res) - 1]
    sql = "insert into teacher_paper(teacher_id, paper_id) values" + res
    DBhelper.execute(sql)

                # print(teacher_id)
    print("---", count)
    # print(type(author_info))
    # print(len(author_info))
    # print(type(author_info[1][0]))
if __name__ == '__main__':
    teacher_dict = get_teacher_info2()
    get_paper_author(teacher_dict)