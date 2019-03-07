from db_operate.db_operate.dbhelper import DBhelper

'''
2019.2.28
本代码用于建立teacher_teacher表，此表的属性有（teacher1_id， paper_num， teacher2_id, teacher2_name）
表示教师1和教师2之间的合作次数。
by zhangshuo
'''

def find_paper_teacher():
    '''
    在表teacher_paper中找到所有的teacher_id和paper_id，组成{paper_id:[teacher1_id, teacher2_id,....], .....}
    :return: {paper_id:[teacher1_id, teacher2_id,....], .....}
    '''
    data = DBhelper.execute("select paper_id, teacher_id from teacher_paper")
    paper_teacher_dict = {}
    for t in data:
        paper_id = t[0]
        teacher_id = t[1]

        if paper_teacher_dict.__contains__(paper_id):
            paper_teacher_dict[paper_id].append(teacher_id)
        else:
            paper_teacher_dict[paper_id] = [teacher_id]
    # print(paper_teacher_dict)
    return paper_teacher_dict



def find_corporate_num(paper_teacher_dict):
    '''
    找出作者之间的论文合著次数
    :param paper_teacher_dict: {paper_id:[teacher1_id, teacher2_id,....], .....}
    :return: {(teacher1_id, teacher2_id): num}
    '''

    teacher_rela_dict = {}
    count = 0
    for paper_id in paper_teacher_dict.keys():
        teacher_id_list = paper_teacher_dict[paper_id]
        if len(teacher_id_list) == 1:
            continue
        for i in range(len(teacher_id_list)-1):
            for j in range(i+1, len(teacher_id_list)):
                t1= teacher_id_list[i]
                t2 = teacher_id_list[j]


                if teacher_rela_dict.__contains__((t1, t2)):
                    teacher_rela_dict[(t1, t2)] += 1
                else:
                    teacher_rela_dict[(t1, t2)] = 1
                if teacher_rela_dict.__contains__((t2, t1)):
                    teacher_rela_dict[(t2, t1)] += 1
                else:
                    teacher_rela_dict[(t2, t1)] = 1

    # print(teacher_rela_dict)
    return teacher_rela_dict

def find_teacher_name():
    '''
    从es_teacher中获取到teacher的id和name的对应关系
    :return:
    '''
    data = DBhelper.execute("select ID, NAME from es_teacher")
    teacher_id_name = {}
    for t in data:
        id = t[0]
        name = t[1]
        teacher_id_name[id] = name
    print(teacher_id_name)
    return teacher_id_name
def insert_from_teacher_rela_dict(teacher_rela_dict, teacher_id_name):
    '''
    将教师对之间的合作关系以及合作的次数插入到数据库
    :param teacher_rela_dict: {(teacher1_id, teacher2_id): num}
    :param teacher_id_name:
    :return: None
    '''
    count = 0
    res = ""
    for t in teacher_rela_dict.keys():
        t1 = t[0]
        t2 = t[1]
        count += 1
        name2 = teacher_id_name[t2]
        paper_num = teacher_rela_dict[t]
        res += "(" + str(t1) + "," + str(paper_num) + "," + str(t2) + ", \"" + name2 + "\"),"
        if count >= 1000:
            count = 0
            res = res[0: len(res)-1]
            insert_into_form(res)
            res = ""
    res = res[0: len(res) - 1]
    insert_into_form(res)

def insert_into_form(res):

    sql = "insert into teacher_teacher(teacher1_id, paper_num, teacher2_id, teacher2_name) values"
    sql += res
    print(sql)
    DBhelper.execute(sql)

if __name__ == '__main__':
    paper_teacher_dict = find_paper_teacher()
    teacher_rela_dict = find_corporate_num(paper_teacher_dict)
    teacher_id_name = find_teacher_name()
    insert_from_teacher_rela_dict(teacher_rela_dict, teacher_id_name)