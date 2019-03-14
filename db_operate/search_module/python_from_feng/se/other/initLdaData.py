import pickle, os

from search_module.python_from_feng.se.base import dbs
# from ..base import dbs
from search_module.python_from_feng.se.config import root
# from ..config import root
def getTeacherName():
    '''
    获取教师的信息以及教师的评分total
    :return:
    '''
    # sql = "SELECT a.*,b.total from teacher a join teacher_rank b on a.id=b.teacher_id"
    sql = "SELECT * from es_teacher"
    result = dbs.getDics(sql)
    dic={}
    # print(result)
    for r in result:
        # print(r['id'], "   ", r)
        dic[r['ID']] = r #将教师的信息组成一个大字典，id为键， 教师的信息以及评分为值
    pickle.dump(dic, open(root+'/teacherName', 'wb')) #序列化对象，将对象object保存到文件中


def getPaperAndTecher():
    '''
    获取论文id，作者的id，以及作者的名字
    :return:
    '''

    # sql = "SELECT a.id,a.author_id,b.`name` FROM `paper2` a JOIN teacher b on a.author_id=b.id" #一篇论文到底属于哪个作者，对应哪个作者的id？？？
    # sql = "SELECT a.id,a.author_id,b.`name` FROM `paper_clean1` a JOIN teacher b on a.author_id=b.id" #一篇论文到底属于哪个作者，对应哪个作者的id？？？
    # sql = "SELECT a.id,a.author_id,b.`name` FROM paper a, teacher JOIN teacher b on a.author_id=b.id" #一篇论文到底属于哪个作者，对应哪个作者的id？？？
    sql = "SELECT a.paper_id, b.id, b.NAME from teacher_paper a, es_teacher b where a.teacher_id = b.id" #一篇论文到底属于哪个作者，对应哪个作者的id？？？

    paper = {}
    teacher = {}
    result = dbs.getDics(sql)
    for r in result:
        print(r)
        paper[r["paper_id"]]={"id": r["id"], "name": r["NAME"]} #将论文以及其相关的作者信息组成字典，论文的id为键，值为一个新的字典  {paper_id:{ "author_id" : ***, author_name:  **}}
        if r["id"] in teacher:
            teacher[r["id"]].append(r["paper_id"]) #将论文的作者id与论文的id组成字典，字典的键是作者id，值是论文id组成的字典，一作者可能有多篇论文与之对应
        else:
            teacher[r["id"]] = [r["paper_id"]]
    pickle.dump(paper, open(root+'/paperTeacher', 'wb'))
    pickle.dump(teacher, open(root+'/teacherPaper', 'wb')) #将这两个对象写入到文件中



def getTeacherAndSchool():
    '''
    从教师表中获取教师id以及对应的学校id
    :return:
    '''
    sql = "SELECT a.ID, a.SCHOOL_ID from teacher a"
    result = dbs.getDics(sql)
    teacher = {}
    school = {}
    for r in result:
        if r["SCHOOL_ID"] in school:
            school[r["SCHOOL_ID"]].append(r["ID"]) #获取学校id对应的教师（多个）
        else:
            school[r["SCHOOL_ID"]] = [r["ID"]]
        teacher[r["ID"]] = r["SCHOOL_ID"]   #获取教师id对应的学校id
    print(root + '/teacherSchool')
    pickle.dump(teacher, open(root+'/teacherSchool', 'wb'))
    pickle.dump(school, open(root+'/schoolTeacher', 'wb'))



def getWordPaper(code, k):
    '''

    :param code:学科代码
    :param k: 这个学科下所分的主题数
    :return:
    '''
    # sql = "SELECT name FROM `discipline_new` where code=%s"
    sql = "SELECT NAME FROM `es_discipline` where code=%s"% code
    print(sql)
    # result = dbs.getDics(sql, (code, ))
    result = dbs.getDics(sql)
    print(result)
    name = result[0]['NAME'] #根据学科的代码从数据库中得到学科名称
    p = root + '/' + name + '-' + code + '/k' + str(k)
    file = open(p+'/'+code+"_topic.txt", 'r', encoding="utf8")
    list = file.readlines()
    wordToTopic = {}
    topicToWord = {}
    for topic_id, line in enumerate(list):
        index = line.find(":")  #topic_id, line  --》0:{'': 0.0, '管道':  0.0, '能量色散': 0.002, '信噪比': 0.001, '有效剂量': 0.0, '平均场理论': 0.0, '生物样品': 0.0, '多层膜': 0.002, '法测定': 0.0}
        words = eval(line[index+1:]) #topic_id 对应的词分布词典
        print("words", words)
        topicToWord[topic_id] = words
        for w in words:
            if w in wordToTopic:
                wordToTopic[w][topic_id] = words[w] #wordToTopic 是一个字典，其中的值又是一个字典，表示某个词在某个主题下的概率
            else:
                wordToTopic[w] = {}
                wordToTopic[w][topic_id] = words[w]
    path = root+'/'+code+'/k'+str(k)
    if not os.path.exists(path):
        os.makedirs(path)
    print(path)
    pickle.dump(topicToWord, open(path+'/topicToWord', 'wb'))
    pickle.dump(wordToTopic, open(path+'/wordToTopic', 'wb'))
# if __name__ == '__main__':
    # getTeacherName()
    # getPaperAndTecher()
    # getTeacherAndSchool()
    # getWordPaper("0835", 12)
def getPaperTopic(code, k):
    # sql = "SELECT name FROM `discipline_new` where code=%s"
    sql = "SELECT name FROM `es_discipline` where code=%s" % code
    # result = dbs.getDics(sql, (code,))
    result = dbs.getDics(sql)
    print(result)
    name = result[0]['name']
    p = root+'/' + name + '-' + code + '/k' + str(k)
    file = open(p+'/'+code+"_teacher_topic.txt", 'r', encoding="utf8")
    paperId = open(root+'/' + name + '-' + code + "/"+code+"_fenci_tdidf.txt", 'r', encoding="utf8")
    ids=[]
    for line in paperId.readlines():
        item = eval(line)  #{'fenci': '非均匀 海森堡 量子纠缠 研究 各向异性 海森堡 量子纠缠 粒子 解析式 数值模拟 粒子 外磁场 耦合系数 温度 量子纠缠 差距 温度 外磁场 非均匀 量子纠缠', 'id': 2201032}
        # print(item)
        ids.append(item['id']) #文章的id列表
    paperToic={}

    for paper_index, line in enumerate(file.readlines()):
        temp = eval(line) #[(1, 0.5016497), (5, 0.20031413), (11, 0.18356259), (6, 0.080942236)] 某篇文章的主题分布
        print(paper_index)
        print(temp)
        paperToic[ids[paper_index]] = {} #paper_index
        for t in temp: #t: (1, 0.5016497)
            paperToic[ids[paper_index]][t[0]] = t[1]
    print(paperToic)  #{819200: {1: 0.916655}, 4227074: {1: 0.92359316}, 4571140: {10: 0.9601378},
    path = root + '/' + code + '/k' + str(k)
    # path = root+'\\' + code + '\\k' + str(k)
    pickle.dump(paperToic, open(path + '/paperToic', 'wb'))
# if __name__ == '__main__':
#     getPaperTopic("0835", 12)

def teacherTopic(code, k):
    '''

    :param code:
    :param k:
    :return:
    '''
    path = root+'/' + code + '/k' + str(k)
    paperToic = pickle.load(open(path + '/paperToic', 'rb'))  # {819200: {1: 0.916655}, 4227074: {1: 0.92359316}, 4571140: {10: 0.9601378},...}
    paper = pickle.load(open(root+'/paperTeacher', 'rb')) #{921922: {'author_id': 137804, 'name': '于运花'}, ...}
    teacherTopic = {}
    paperNum = {}
    print(paper)
    # print(paper)
    for p in paperToic: # p是paperTopic中的键，也是论文的id
        # print(p)
        # print(paper[p])
        if paper.__contains__(p):
            author_id = paper[p]["id"]
        else:
            continue
        if author_id not in teacherTopic:
            teacherTopic[author_id] = {} # teacherTopic  {author_id： {  }，.....}
            paperNum[author_id] = 0
        paperNum[author_id] += 1 #{ author_id : 这个id所对应的论文的数量}
        p_topic = paperToic[p] #{1: 0.916655， 3： 0.003， .....}

        for topic in p_topic: #topic 是主题号
            if topic in teacherTopic[author_id]:  # teacherTopic  {author_id： {topic:*** }，.....} 如果某一个作者下面已经有了这一个主题号，将这个主题号所对应的值与原来的相加， 对应的值是这篇文章对应这个主题的概率
                teacherTopic[author_id][topic] += p_topic[topic]
            else:                                 # 如果没有这样的一个主题号，将主题号所对应的值加入到字典
                teacherTopic[author_id][topic] = p_topic[topic]
    for t in teacherTopic:  #{author_id： {topic: 这个作者的文章对应这个主题的概率之和 }，.....}
        for topic in teacherTopic[t]:
            teacherTopic[t][topic] = teacherTopic[t][topic] / ((paperNum[t] - 1) / 10 + 1) #？？？ 为什么要除以这个作者的论文数？？？
    path = root+'/' + code + '/k' + str(k)
    pickle.dump(teacherTopic, open(path+'/teacherTopic', 'wb'))

# if __name__ == '__main__':
#     teacherTopic("0835", 12)

def getTopicTeacher(code, k):
    '''
    获取某一主题对应的教师id（多个），以及对应的概率
    :param code:
    :param k:
    :return:
    '''
    path = root+'/' + code + '/k' + str(k)
    teacherTopic = pickle.load(open(path+'/teacherTopic', 'rb'))  #{author_id： {topic:这个作者的文章对应这个主题的概率之和 }，.....}
    topicTeacher={}
    for teacher_id in teacherTopic:
        teacher = teacherTopic[teacher_id]  #{4: 0.58063, 6: 0.36727637}
        # print(teacher)
        for topic_id in teacher:
            if topic_id not in topicTeacher:
                topicTeacher[topic_id] = {}
            topicTeacher[topic_id][teacher_id] = teacher[topic_id]  #{主题id：{教师id ： 教师id对应该主题的概率 ，.....},.......}
    # {0: {94720: 2.0434909685, 94721: 0.5083823455555556, 49143: 1.1169900987254902,  147722: 0.6978899, 44049: 0.9739477859259258,
    # print(topicTeacher)
    pickle.dump(topicTeacher, open(path + '/topicTeacher', 'wb'))

# if __name__ == '__main__':
#     getTopicTeacher("0835", 12)


def getTeacherTeacher(code, k):

    path = root+'/' + code + '/k' + str(k)
    topicTeacher = pickle.load(open(path + '/topicTeacher', 'rb')) #{主题id：{教师id ： 教师id对应该主题的概率 ，.....},.......}

    TeacherTeacher = {}
    for topic_id in topicTeacher:
        teacher = topicTeacher[topic_id] #该主题下对应的所有教师及其概率
        for t in teacher: # t：  教师的id
            if t not in TeacherTeacher:
                TeacherTeacher[t] = {}  #TeacherTeacher ： {教师1的id： {教师2的id： 他们之间的关系度  } }
            for o in teacher: # o ： 教师的id
                if o != t:
                    if o not in TeacherTeacher[t]:
                        TeacherTeacher[t][o] = 0 # 对教师t 和教师o 之间的值 初始化为 0
                    TeacherTeacher[t][o] += teacher[t] * teacher[o] # 针对不同的主题 对教师t 和教师o 之间的值进行叠加， 如果说某一主题下出现了两个在别的主题中出现的教师，那么其之间的关系度将增加
    pickle.dump(TeacherTeacher, open(path + '/TeacherTeacher', 'wb'))

# if __name__ == '__main__':
#     getTeacherTeacher("0835", 12)

def getSchoolTopic(code, k):
    path = root+'/' + code + '/k' + str(k)
    teacherTopic = pickle.load(open(path+'/teacherTopic', 'rb'))  ##{author_id： {topic:这个作者的文章对应这个主题的概率之和，.... }，.....}
    teacher = pickle.load(open(root+'/teacherSchool', 'rb'))  # {teacher_id: school_id, ..... }
    schoolTopic = {}
    teacherNum = {}  #{ 学校的id： 该学校对应的教师数量 }
    for t in teacherTopic: # t 教师的id
        if t in teacher:
            s = teacher[t] # s 学校的id
        else:
            continue
        if s == 0:
            continue
        topic = teacherTopic[t] #该教师对应的主题的词典{主题1： 概率， 主题2 ：概率， ....}
        if s not in schoolTopic:
            schoolTopic[s] = {}
            teacherNum[s] = 0
        teacherNum[s] += 1
        for to in topic:  #to 主题
            if to in schoolTopic[s]:
                schoolTopic[s][to] += topic[to]  #某一学校的主题，其对应的概率值为该学校所有拥有该主题的老师的概率之和
            else:
                schoolTopic[s][to] = topic[to]
    for t in schoolTopic: #t 学校的id  {学校的id ： {主题一： 概率值，主题二： 概率值， ....}, .....}
        for topic in schoolTopic[t]:
            schoolTopic[t][topic] = schoolTopic[t][topic]/((teacherNum[t]-1)/10+1) #这可能是要归一化
    pickle.dump(schoolTopic, open(path+'/schoolTopic', 'wb'))

# if __name__ == '__main__':
#     getSchoolTopic("0835", 12)

def getTopicSchool(code, k):
    path = root+'/' + code + '/k' + str(k)
    schoolTopic = pickle.load(open(path + '/schoolTopic', 'rb'))  #{学校的id ： {主题一： 概率值，主题二： 概率值， ....}, .....}
    topicSchool = {}
    for school_id in schoolTopic:
        school = schoolTopic[school_id]
        for topic_id in school:  #school 是学校对应的主题  {主题一： 概率值，主题二： 概率值， ....}
            if topic_id not in topicSchool:
                topicSchool[topic_id] = {}
            topicSchool[topic_id][school_id] = school[topic_id] #{主题号： {学校的id： 对应的主题的概率值 }，.....}
    pickle.dump(topicSchool, open(path + '/topicSchool', 'wb'))

# if __name__ == '__main__':
#     getTopicSchool("0835", 12)

def getSchoolSchool(code, k):
    path = root+'/' + code + '/k' + str(k)
    topicSchool = pickle.load(open(path + '/topicSchool', 'rb'))  # {主题号： {学校的id： 对应的主题的概率值 }，.....}
    SchoolSchool = {}
    for topic_id in topicSchool:
        school = topicSchool[topic_id]  #{学校的id： 对应的主题的概率值 }
        for t in school:
            if t not in SchoolSchool:
                SchoolSchool[t] = {}
            for o in school:
                if o != t:
                    if o not in SchoolSchool[t]:
                        SchoolSchool[t][o] = 0
                        SchoolSchool[t][o] += school[t] * school[o]
    pickle.dump(SchoolSchool, open(path + '/SchoolSchool', 'wb'))











# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''
这段代码粘贴自duan，作用是初始化学院的lda数据
'''
def getInstitutionName():
    print('getInstitutionName..')
    print('得到院系信息')
    sql = "SELECT a.*,b.total from es_institution a join institution_rank b on a.ID=b.institution_id"
    result = dbs.getDics(sql)
    dic = {}
    for r in result:
     #r:   # {'id': 149104, 'name': '潘正华', 'position': None, 'title': None, 'school': '江南大学', 'institution': '理学院',
        #  'theme': None, 'eduexp': None, 'email': None, 'pic': None,
        #  'homepage': 'http://cksp.eol.cn/tutor_detail.php?id=11396', 'school_id': 17397, 'age': 0, 'field_id': None,
        #  'total': 0.75}
        dic[r['ID']]=r
    pickle.dump(dic, open(root+'/InstitutionName', 'wb'))


def getTeacherAndInstitution():
    '''
    获得老师和学院的关系
    1.school-teacher {institution_id1:[teacher_id1,teacher_id2,...],institution_id2:{teacher_id3....}}
    2.teacher-school {teacher_id1:institution1,teacher_id2:institution2}
    :return:
    '''
    print('getTeacherAndInstitution')
    sql = "SELECT a.ID,a.INSTITUTION_ID from es_teacher a"
    result = dbs.getDics(sql)
    teacher={}
    institution={}
    for r in result:
        if r["INSTITUTION_ID"] in institution:
            institution[r["INSTITUTION_ID"]].append(r["ID"])
        else:
            institution[r["INSTITUTION_ID"]]=[r["ID"]]
        teacher[r["ID"]]=r["INSTITUTION_ID"]
    pickle.dump(teacher, open(root+'/teacherInstitution', 'wb'))
    pickle.dump(institution, open(root+'/institutionTeacher', 'wb'))

def getInstitutionTopic(code,k):
    '''
    InstitutionTopic {institution_id1:{topic1:p1,topic2:p2,...},institution_id2:{topic1:p1,...}}
    :param code:
    :param k:
    :return:
    '''
    print('getSchoolTopic..')
    path = root+'/' + code + '/k' + str(k)
    #{teacher1: {topic1: p1, topic2: p2}, ...}
    teacherTopic=pickle.load(open(path+'/teacherTopic', 'rb'))
    #{teacher_id1: school1, teacher_id2: school2}
    teacher=pickle.load(open(root+'/teacherInstitution', 'rb'))
    institutionTopic={}
    institutionNum={}

    #t代表teacher_id
    for t in teacherTopic:
        #s是t所在的institution_id
        s=teacher[t]
        if s==0:
            continue
        #teacherTopic {teacher1: {topic1: p1, topic2: p2}, ...}
        #topic是字典 {topic1: p1, topic2: p2}
        topic=teacherTopic[t]
        #将school_id设置为key
        #teacherNum是字典，{school_id1:teachernum1,...}
        if s not in institutionTopic:
            institutionTopic[s]={}
            institutionNum[s]=0
        institutionNum[s] +=1
        #to是topic_id
        for to in topic:
            if to in institutionTopic[s]:
                institutionTopic[s][to]+=topic[to]
            else:
                institutionTopic[s][to]= topic[to]
    for t in institutionTopic:
        for topic in institutionTopic[t]:
            institutionTopic[t][topic]=institutionTopic[t][topic]/((institutionNum[t]-1)/10+1)
    pickle.dump(institutionTopic, open(path+'/institutionTopic', 'wb'))



# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''
这段代码粘贴自duan，作用是获取学校地址和名字
'''
def getSchoolAddress():
    '''
    SchoolAddress {school_id:(procince_id,city_id),}
    :return:
    '''
    school_address = {}
    print('getSchoolAddress..')
    sql = "select ID,PROVINCE,CITY from es_school where LEVEL = '985'"
    results = dbs.getDics(sql)
    for result in results:
        school_address[result['ID']] = (result['PROVINCE'],result['CITY'])
    print(school_address)
    pickle.dump(school_address, open(root + '/schooladdress', 'wb'))


def getSchoolName():
    '''
    把学校信息和权值写入一个文件，格式是{id1(即teacher表中id):{教师信息+权重}，id2:{信息},...}
    {149104:{'id': 149104, 'name': '潘正华', 'position': None, 'title': None, 'school': '江南大学', 'institution': '理学院',
        #  'theme': None, 'eduexp': None, 'email': None, 'pic': None,
        #  'homepage': 'http://cksp.eol.cn/tutor_detail.php?id=11396', 'school_id': 17397, 'age': 0, 'field_id': None,
        #  'total': 0.75}
    :return:
    '''
    #total是字段名
    print('getSchoolName..')
    print('得到学校信息')
    sql = "SELECT a.*,b.total from es_school a join school_rank b on a.ID=b.school_id"
    result=dbs.getDics(sql)
    dic={}
    for r in result:
     #r:   # {'id': 149104, 'name': '潘正华', 'position': None, 'title': None, 'school': '江南大学', 'institution': '理学院',
        #  'theme': None, 'eduexp': None, 'email': None, 'pic': None,
        #  'homepage': 'http://cksp.eol.cn/tutor_detail.php?id=11396', 'school_id': 17397, 'age': 0, 'field_id': None,
        #  'total': 0.75}
        dic[r['ID']]=r
    pickle.dump(dic, open(root+'/SchoolName', 'wb'))

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# if __name__ == '__main__':
#     getSchoolSchool("0835", 12)
if __name__ == '__main__':
    getTeacherName()
    getPaperAndTecher()
    getTeacherAndSchool()
#     subject = [{"code": '01', "k": 46},{"code": '02', "k": 98},{"code": '03', "k": 98},
#                {"code": '04', "k": 88},{"code": '05', "k": 98},{"code": '06', "k": 28},
#                {"code": '07', "k": 54}, {"code": '0701', "k": 64}, {"code": '0702', "k": 30},
#                {"code": '0703', "k": 52}, {"code": '0705', "k": 16}, {"code": '0706', "k": 12},
#                {"code": '0707', "k": 14}, {"code": '0709', "k": 98}, {"code": '0710', "k": 98},
#                {"code": '0712', "k": 10}, {"code": '08', "k":50}, {"code": '0801', "k": 26},
#                {"code": '0802', "k": 98}, {"code": '0803', "k": 14}, {"code": '0804', "k":12},
#                {"code": '0805', "k": 98}, {"code": '0806', "k":12}, {"code": '0807', "k": 38},
#                {"code": '0808', "k": 98}, {"code": '0809', "k": 52}, {"code": '0810', "k": 98},
#                {"code": '0811', "k": 22}, {"code": '0812', "k": 72}, {"code": '0813', "k": 30},
#                {"code": '0814', "k": 68}, {"code": '0815', "k":14}, {"code": '0816', "k": 14},
#                {"code": '0817', "k":98}, {"code": '0818', "k": 14}, {"code": '0819', "k": 18},
#                {"code": '0820', "k": 18}, {"code": '0821', "k": 18}, {"code": '0823', "k": 24},
#                {"code": '0824', "k": 14}, {"code": '0825', "k": 26}, {"code": '0826', "k": 10},
#                {"code": '0827', "k": 12}, {"code": '0828', "k": 36}, {"code": '0829', "k": 14},
#                {"code": '0830', "k": 82}, {"code": '0831', "k": 16}, {"code": '0832', "k": 28},
#                {"code": '09', "k": 74}, {"code": '10', "k": 98},{"code": '11', "k": 14},]
    subject = [
        {"code": '0810', "k": 10},
        {"code": '0811', "k": 10},
        {"code": '0812', "k": 10},
        {"code": '0805', "k": 10},
        {"code": '0835', "k": 10},
        {"code": '0827', "k": 14},
        {"code": '0832', "k": 10},
        {"code": '081101', "k": 12},
        {"code": '0833', "k": 10},
        {"code": '0835', "k": 10},
        {"code": '0828', "k": 16},
        {"code": '0831', "k": 12},
        {"code": '081202', "k": 12},
        {"code": '0834', "k": 16},
        {"code": '0837', "k": 14},
        {"code": '081101', "k": 12},
        {"code": '080901', "k": 12},
    ]
    for sub in subject:
        print(sub)
        getWordPaper(sub['code'], sub['k'])
        getPaperTopic(sub['code'], sub['k'])
        teacherTopic(sub['code'], sub['k'])
        getTopicTeacher(sub['code'], sub['k'])
        getTeacherTeacher(sub['code'], sub['k'])
        getSchoolTopic(sub['code'], sub['k'])
        getTopicSchool(sub['code'], sub['k'])
        getSchoolSchool(sub['code'], sub['k'])
        # -------------------------------------------------
        getInstitutionName()
        getTeacherAndInstitution()
        getInstitutionTopic(sub['code'], sub['k'])


        getSchoolAddress()
        getSchoolName()
        # -------------------------------------------------
