import pickle,os
from  utils.base import dbs
from  utils.config import root
def getTeacherName():
    '''
    把教师信息和权值写入一个文件，格式是{id1(即teacher表中id):{教师信息+权重}，id2:{信息},...}
    {149104:{'id': 149104, 'name': '潘正华', 'position': None, 'title': None, 'school': '江南大学', 'institution': '理学院',
        #  'theme': None, 'eduexp': None, 'email': None, 'pic': None,
        #  'homepage': 'http://cksp.eol.cn/tutor_detail.php?id=11396', 'school_id': 17397, 'age': 0, 'field_id': None,
        #  'total': 0.75}
    :return:
    '''
    #total是字段名
    print('getTeacherName..')
    sql = "SELECT a.*,b.total from es_teacher a join teacher_rank b on a.ID=b.teacher_id"
    result=dbs.getDics(sql)
    dic={}
    for r in result:
     #r:   # {'id': 149104, 'name': '潘正华', 'position': None, 'title': None, 'school': '江南大学', 'institution': '理学院',
        #  'theme': None, 'eduexp': None, 'email': None, 'pic': None,
        #  'homepage': 'http://cksp.eol.cn/tutor_detail.php?id=11396', 'school_id': 17397, 'age': 0, 'field_id': None,
        #  'total': 0.75}
        dic[r['ID']]=r
    pickle.dump(dic, open(root+'/teacherName', 'wb'))


def getInstitutionName():
    '''
    写入院系信息，{institution_id: {'ID':, 'SCHOOL_ID':, 'SCHOOL_NAME':, 'NAME':}, ...}
    :return:
    '''
    print('getInstitutionName..')
    print('得到院系信息')
    sql = "SELECT a.*,b.total from es_institution a join institution_rank b on a.ID=b.institution_id"
    result=dbs.getDics(sql)
    dic={}
    for r in result:
        dic[r['ID']]=r
    pickle.dump(dic, open(root+'/InstitutionName', 'wb'))

def getPaperAndTecher():
    '''
    paperTeacher {paper_id:{"author_id":r["author_id"],"name":r["name"]}}
    paperTeacher文件：字典，文章id为key,value是教师信息
    teacherpaper {author_id:[]}
    teacherpaper文件：字典，老师id为值，value是文章信息
    :return:
    '''
    #获得论文id,论文author_id 作者name a是论文 b是老师名字

    print('paper-teacher and teacher-paper..')
    sql = "SELECT a.paper_id,a.teacher_id,b.`name` FROM `teacher_paper` a ,es_teacher b where a.teacher_id=b.ID"
    paper={}
    teacher={}
    result=dbs.getDics(sql)


    for r in result:
        paper[r["paper_id"]]={"author_id":r["teacher_id"],"name":r["name"]}

        #以老师名字为key,论文名字为value
        if r["teacher_id"] in teacher:
            teacher[r["teacher_id"]].append(r["paper_id"])
        else:
            teacher[r["teacher_id"]]=[r["paper_id"]]
    pickle.dump(paper,open(root+'/paperTeacher', 'wb'))
    pickle.dump(teacher,open(root+'/teacherPaper', 'wb'))


def getTeacherAndSchool():
    '''
    1.school-teacher {school_id1:[teacher_id1,teacher_id2,...],school_id2:{teacher_id3....}}
    2.teacher-school {teacher_id1:school1,teacher_id2:school2}
    :return:
    '''
    print('getTeacherAndSchool')
    sql = "SELECT a.ID,a.SCHOOL_ID from es_teacher a"
    result = dbs.getDics(sql)
    teacher={}
    school={}
    for r in result:
        if r["SCHOOL_ID"] in school:
            school[r["SCHOOL_ID"]].append(r["ID"])
        else:
            school[r["SCHOOL_ID"]]=[r["ID"]]
        teacher[r["ID"]]=r["SCHOOL_ID"]
    pickle.dump(teacher, open(root+'/teacherSchool', 'wb'))
    pickle.dump(school, open(root+'/schoolTeacher', 'wb'))
def getWordPaper(code,k):
    '''
    读入某个学科某个主题数下的topic2word,输出word2topic和topic2word
    word2topic {'催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0,}
    word2topic {word1:{topic1:p1,topic2:p2},word2:{}}
    topicToWord  {topic1:{word1:p1,word2:p2},topic2:{word1:p1,word2:p2}}
    :param code:学科代码
    :param k: 主题数
    :return:
    '''
    print('getWordPaper..')
    sql="SELECT name FROM `discipline_new` where code=%s"
    result = dbs.getDics(sql,(code,))
    name=result[0]['name']
    # p = data/学科名-学科代码/k0828
    p=root+'/'+name+'-'+code+'/k'+str(k)
    #file:
    # 0: {'无人机': 0.046, '直升机': 0.027, '纤维素': 0.024,
    # 1: {'电机': 0.061, '控制器': 0.031, '控制策略
    file = open(p+'/'+code+"_topic.txt", 'r', encoding="utf8")
    #读取主题及其关键词
    list = file.readlines()
    # 词2主题 每个词，如果这个词在某个主题下出现，就将它的概率记录下来
    # {'催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0,}
    wordToTopic={}
    #与读入的文件结构一样
    topicToWord = {}

    for topic_id,line in enumerate(list):
        #这里的:用来分隔主题号和关键词字典
        index=line.find(":")
        #将关键词字典转化为字典，words{'催化剂': 0.104, '神经网络': 0.063,}
        words=eval(line[index+1:])
        topicToWord[topic_id]=words
        #words是字典，这样遍历，w指代字典中的key
        for w in words:
            if w in wordToTopic:
                wordToTopic[w][topic_id]=words[w]
            else:
                wordToTopic[w]={}
                wordToTopic[w][topic_id] = words[w]
    path=root+'/'+code+'/k'+str(k)
    if not os.path.exists(path):
        os.makedirs(path)
    pickle.dump(topicToWord, open(path+'/topicToWord', 'wb'))
    pickle.dump(wordToTopic, open(path+'/wordToTopic', 'wb'))

def getPaperTopic(code,k):
    '''
    给teacher_topic.txt 加上文章id
    {paper_id1:{topic1:p1,topic2:p2},paper_id2:{},paper_id2:{topic2:p2}}
    格式 {243084: {13: 0.92521083}, 242970: {25: 0.92443347, 15: 0.04058274}}
    :param code:
    :param k:
    :return:
    '''
    print('getPaperTopic')
    sql="SELECT name FROM `discipline_new` where code=%s"
    result = dbs.getDics(sql,(code,))
    name=result[0]['name']
    p = root+'/' + name + '-' + code + '/k' + str(k)
    #p: G:\w_project\data/农业工程-0828/k36
    #file 读取文章主题文件
    file = open(p+'/'+code+"_teacher_topic.txt", 'r', encoding="utf8")
    # paperId 计算tfidf后的文件
    paperId = open(root+'/' + name + '-' + code + "/"+code+"_fenci_tdidf.txt", 'r', encoding="utf8")
    #ids里面是各个文档id
    ids=[]
    for line in paperId.readlines():
        item=eval(line)
        ids.append(item['id'])
    #每个文章对应的主题及id
    # {243084: {13: 0.92521083}, 242970: {25: 0.92443347, 15: 0.04058274},
    paperToic={}

    for paper_index, line in enumerate(file.readlines()):
        # line:[(5, 0.75776845), (7, 0.17293692), (11, 0.04333982)]
        temp = eval(line)
        #ids[paper_index] 是文章id
        paperToic[ids[paper_index]] = {}
        for t in temp:
            #paperToic[ids[paper_index]] 是个字典 t[0] 是key t[1]是value
            paperToic[ids[paper_index]][t[0]] = t[1]
    path = root+'/'+ code + '/k' + str(k)
    pickle.dump(paperToic, open(path+'/paperToic', 'wb'))

def teacherTopic(code,k):
    '''
    知道paper与Topic的关系，paper与teacher ,可以得到teacher与topic的关系
    {teacher1:{topic1:p1,topic2:p2},...}
    :param code:
    :param k:
    :return:
    '''
    print('teacherTopic..')
    path = root+'/' + code + '/k' + str(k)
    #{243084: {13: 0.92521083}, 242970: {25: 0.92443347, 15: 0.04058274},
    paperToic=pickle.load( open(path + '/paperToic', 'rb'))
    #paper[r["id"]] = {"author_id": r["author_id"], "name": r["name"]}
    paper=pickle.load(open(root+'/paperTeacher', 'rb'))
    teacherTopic={}
    paperNum={}


    for p in paperToic:
        # 70511 论文有30万篇，能找到作者的只有70000篇，所以很多对应不上，而学长代码是在一张表中，必然对应的上，所以要修改代码,判断该paper能否找到作者。
        #得到教师id
        if p in paper:
            author_id=paper[p]["author_id"]

            if author_id not in teacherTopic:
                teacherTopic[author_id]={}
                #论文数目？
                paperNum[author_id]=0
            paperNum[author_id]+=1
            p_topic=paperToic[p]
            for topic in p_topic:
                if topic in teacherTopic[author_id]:
                    teacherTopic[author_id][topic]+=p_topic[topic]
                else:
                    teacherTopic[author_id][topic]= p_topic[topic]
    for t in teacherTopic:
        for topic in teacherTopic[t]:
            #对teacherTopic（每个老师每个主题下的概率进行处理）进行处理
            teacherTopic[t][topic]=teacherTopic[t][topic]/((paperNum[t]-1)/10+1)
    path = root+'/' + code + '/k' + str(k)
    pickle.dump(teacherTopic, open(path+'/teacherTopic', 'wb'))

def getTopicTeacher(code,k):
    '''
    {topic1:{teacher1:p1,teacher2:p2},topic2 }
    :param code:
    :param k:
    :return:
    '''
    print('getTopicTeacher')
    path = root+'/'+ code + '/k' + str(k)
    teacherTopic=pickle.load(open(path+'/teacherTopic', 'rb'))
    topicTeacher={}
    #teachertopic {teacher1: {topic1: p1, topic2: p2}, ...}
    for teacher_id in teacherTopic:
        teacher=teacherTopic[teacher_id]
        for topic_id in teacher:
            if topic_id not in topicTeacher:
                topicTeacher[topic_id]={}
            topicTeacher[topic_id][teacher_id]=teacher[topic_id]
    pickle.dump(topicTeacher, open(path +'/topicTeacher', 'wb'))

def getTeacherTeacher(code,k):
    print('getTeacherTeacher')
    path = root+'/' + code + '/k' + str(k)
    #{topic1: {teacher1: p1, teacher2: p2}, topic2}
    topicTeacher=pickle.load(open(path + '/topicTeacher', 'rb'))
    TeacherTeacher={}
    for topic_id in topicTeacher:
        teacher=topicTeacher[topic_id]
        for t in teacher:
            if t not in TeacherTeacher:
                TeacherTeacher[t]={}
            for o in teacher:
                if o!=t:
                    if o not in TeacherTeacher[t]:
                        TeacherTeacher[t][o]=0
                    TeacherTeacher[t][o]+=teacher[t]*teacher[o]
    #{teacher1:{teacher2:p(teacher1)*p(teacher2),teacher3:p1*p3},teacher2:{}}
    pickle.dump(TeacherTeacher, open(path+'/TeacherTeacher', 'wb'))

def getSchoolTopic(code,k):
    '''
    SchoolTopic {school_id1:{topic1:p1,topic2:p2,...},school_id2:{topic1:p1,...}}
    :param code:
    :param k:
    :return:
    '''
    print('getSchoolTopic..')
    path = root+'/' + code + '/k' + str(k)
    #{teacher1: {topic1: p1, topic2: p2}, ...}
    teacherTopic=pickle.load(open(path+'/teacherTopic', 'rb'))
    #{teacher_id1: school1, teacher_id2: school2}
    teacher=pickle.load(open(root+'/teacherSchool', 'rb'))
    schoolTopic={}
    teacherNum={}

    #t代表teacher_id
    for t in teacherTopic:
        #s是t所在的school_id
        s=teacher[t]
        if s==0:
            continue
        #teacherTopic {teacher1: {topic1: p1, topic2: p2}, ...}
        #topic是字典 {topic1: p1, topic2: p2}
        topic=teacherTopic[t]
        #将school_id设置为key
        #teacherNum是字典，{school_id1:teachernum1,...}
        if s not in schoolTopic:
            schoolTopic[s]={}
            teacherNum[s]=0
        teacherNum[s] +=1
        #to是topic_id
        for to in topic:
            if to in schoolTopic[s]:
                schoolTopic[s][to]+=topic[to]
            else:
                schoolTopic[s][to]= topic[to]
    for t in schoolTopic:
        for topic in schoolTopic[t]:
            schoolTopic[t][topic]=schoolTopic[t][topic]/((teacherNum[t]-1)/10+1)
    pickle.dump(schoolTopic, open(path+'/schoolTopic', 'wb'))

def getTopicSchool(code, k):
    '''
    TopicSchool    {topic_id1:{school_id1:p1,school_id2:p2},topic_id2:{school_id1:p1}}
    :param code:
    :param k:
    :return:
    '''
    print('getTopicSchool..')
    path = root+'/' + code + '/k' + str(k)
    #{school_id1: {topic1: p1, topic2: p2, ...}, school_id2: {topic1: p1, ...}}
    schoolTopic = pickle.load(open(path + '/schoolTopic', 'rb'))
    topicSchool = {}
    for school_id in schoolTopic:
        #school是学校对应的主题关系 {topic1: p1, topic2: p2, ...}
        school = schoolTopic[school_id]
        for topic_id in school:
            if topic_id not in topicSchool:
                topicSchool[topic_id] = {}
            topicSchool[topic_id][school_id] = school[topic_id]
    pickle.dump(topicSchool, open(path + '/topicSchool', 'wb'))

def getSchoolSchool(code, k):
    '''
    SchoolSchool {school1:{school2:p12,school3:p12}}
    :param code:
    :param k:
    :return:
    '''
    print('getSchoolSchool..')
    path = root+'/' + code + '/k' + str(k)
    #{topic_id1: {school_id1: p1, school_id2: p2}, topic_id2: {school_id1: p1}}
    topicSchool = pickle.load(open(path + '/topicSchool', 'rb'))
    SchoolSchool = {}
    for topic_id in topicSchool:
        #school是每个主题对应的学校信息
        school = topicSchool[topic_id]
        #t是school_id
        for t in school:
            if t not in SchoolSchool:
                SchoolSchool[t] = {}
            #o是school_id
            for o in school:
                if o != t:
                    if o not in SchoolSchool[t]:
                        SchoolSchool[t][o] = 0
                    SchoolSchool[t][o] += school[t] * school[o]
    pickle.dump(SchoolSchool, open(path + '/SchoolSchool', 'wb'))

if __name__ == '__main__':
    getTeacherName()
    getPaperAndTecher()
    getTeacherAndSchool()
    # subject = [{"code": '01', "k": 46},{"code": '02', "k": 98},{"code": '03', "k": 98},
    #            {"code": '04', "k": 88},{"code": '05', "k": 98},{"code": '06', "k": 28},
    #            {"code": '07', "k": 54}, {"code": '0701', "k": 64}, {"code": '0702', "k": 30},
    #            {"code": '0703', "k": 52}, {"code": '0705', "k": 16}, {"code": '0706', "k": 12},
    #            {"code": '0707', "k": 14}, {"code": '0709', "k": 98}, {"code": '0710', "k": 98},
    #            {"code": '0712', "k": 10}, {"code": '08', "k":50}, {"code": '0801', "k": 26},
    #            {"code": '0802', "k": 98}, {"code": '0803', "k": 14}, {"code": '0804', "k":12},
    #            {"code": '0805', "k": 98}, {"code": '0806', "k":12}, {"code": '0807', "k": 38},
    #            {"code": '0808', "k": 98}, {"code": '0809', "k": 52}, {"code": '0810', "k": 98},
    #            {"code": '0811', "k": 22}, {"code": '0812', "k": 72}, {"code": '0813', "k": 30},
    #            {"code": '0814', "k": 68}, {"code": '0815', "k":14}, {"code": '0816', "k": 14},
    #            {"code": '0817', "k":98}, {"code": '0818', "k": 14}, {"code": '0819', "k": 18},
    #            {"code": '0820', "k": 18}, {"code": '0821', "k": 18}, {"code": '0823', "k": 24},
    #            {"code": '0824', "k": 14}, {"code": '0825', "k": 26}, {"code": '0826', "k": 10},
    #            {"code": '0827', "k": 12}, {"code": '0828', "k": 36}, {"code": '0829', "k": 14},
    #            {"code": '0830', "k": 82}, {"code": '0831', "k": 16}, {"code": '0832', "k": 28},
    #            {"code": '09', "k": 74}, {"code": '10', "k": 98},{"code": '11', "k": 14},
    #            {"code": '12', "k": 98}]
    subject = [
                {"code": '0801', "k": 16},
               {"code": '0802', "k": 10}, {"code": '0803', "k": 10}, {"code": '0804', "k":12},
               {"code": '0805', "k": 10}, {"code": '0806', "k":12}, {"code": '0807', "k": 14},
               {"code": '0808', "k": 12}, {"code": '0809', "k": 18},{"code": '080901', "k": 16}, {"code": '0810', "k": 18},
               {"code": '0811', "k": 12},{"code": '081101', "k": 28}, {"code": '0812', "k": 10}, {"code": '081202', "k": 12},
               {"code": '0814', "k": 20}, {"code": '0815', "k":12},
               {"code": '0817', "k":10}, {"code": '0818', "k": 14},
               {"code": '0822', "k": 10}, {"code": '0823', "k": 10},
               {"code": '0824', "k": 12}, {"code": '0825', "k": 20}, {"code": '0826', "k": 10},
               {"code": '0827', "k": 10}, {"code": '0828', "k": 10},
               {"code": '0830', "k": 18}, {"code": '0831', "k": 10}, {"code": '0832', "k": 12}]

    for sub in subject:
        print(sub)
        #词与主题 1
        getWordPaper(sub['code'],sub['k'])
        #词与主题，主题与词 1
        getPaperTopic(sub['code'],sub['k'])
        #获取老师与论文的信息 1
        getPaperAndTecher()
        #获取老师与主题的关系 1
        teacherTopic(sub['code'],sub['k'])
        #获得主题与老师的关系 1
        getTopicTeacher(sub['code'],sub['k'])
        #获得老师与老师的关系,以topic来计算 1
        getTeacherTeacher(sub['code'],sub['k'])
        #获得老师和学校的关系 1
        getTeacherAndSchool()
        #获得学校和主题的关系 1
        getSchoolTopic(sub['code'],sub['k'])
        #获得主题和学校的关系1
        getTopicSchool(sub['code'],sub['k'])
        #获得学校和学校的关系1
        getSchoolSchool(sub['code'],sub['k'])
        pass
