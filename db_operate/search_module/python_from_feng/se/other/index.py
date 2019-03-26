from search_module.python_from_feng.se.base import dbs
from search_module.python_from_feng.se.config import root
import pickle


def getTeacherWord(code, k):
    # sql="SELECT name FROM `discipline_new` where code=%s"
    sql = "SELECT name FROM `es_discipline` where code=%s" % code
    # result = dbs.getDics(sql,(code,))
    result = dbs.getDics(sql)
    name = result[0]['name'] #学科名
    path = root+'/' + name + '-' + code
    file = open(path + "/" + code+"_fenci_tdidf.txt", 'r', encoding="utf8") #读取该学科下的论文分词后的文件
    paper = pickle.load(open(root+'/paperTeacher', 'rb')) #读取论文教师文件  {932810: {'name': '张浩', 'author_id': 47478}, ....}
    list = file.readlines()  #["{'fenci': '内涵 现场 分布特征 部位 中央 部位 潜力', 'id': 353392}\n", "{'fenci': '教材中', 'id': 530129}\n",
    # print(list)
    # print(paper)
    teacherWord = {}
    for line in list:
        temp = eval(line)  #{"fenci": 分的词, "id": 论文的id}
        paper_id = temp['id']
        if paper_id in paper:
            teacher_id = paper[paper_id]["id"] #通过论文的id获取教师的id
        else:
            continue
        if teacher_id not in teacherWord:
            teacherWord[teacher_id] = {}
        words = temp['fenci'].split(' ') #将该论文的词组成列表
        for w in words:
            if w in teacherWord[teacher_id]:
                teacherWord[teacher_id][w] += 1 #将这个教师写的所有的论文分词后搞到字典中，并记录次出现的次数
            else:
                teacherWord[teacher_id][w] = 1  #{94720: {'工程应用': 1, '图像增强': 2, '嵌入式': 2, '取值范围': 2, '人体': 4, '自定义': 1, ...}n
    # print(teacherWord)
    pickle.dump(teacherWord, open(root+'/' + code+'/k'+str(k)+'/teacherWord', 'wb'))


# if __name__ == '__main__':
#     getTeacherWord("0835", 12)

def computer(code, k):
    teacherWord = pickle.load(open(root+'/'+ code+'/k'+str(k)+'/teacherWord', 'rb'))  # {教师id： {词1：出现的频率，词2： 出现的频率}, ....}
    word = {}
    wordIndex = {}
    length = 0
    for teacher_id in teacherWord:
        teacher = teacherWord[teacher_id] #该教师论文中的所有词（属于该教师的词典）
        size = len(teacher) # 教师词典长度
        for w in teacher:
            if w not in wordIndex:
                wordIndex[w] = {}
                word[w] = 0
            word[w] += teacher[w] #该词在所有教师论文中出现的次数
            length += teacher[w] #该学科下所有论文中的总词数
            wordIndex[w][teacher_id] = teacher[w]/size #某个词在教师的词典中出现的概率

    for w in word:
        wordIndex[w]["col_fre"] = word[w]/length # 词索引 col_fre  : 这个词在总词典中出现的概率
    # print(wordIndex)
    print("所有论文中出现的总词数：  ", length)
    pickle.dump(wordIndex, open(root+'/' + code+'/k' + str(k) + '/wordIndex', 'wb'))

# if __name__ == '__main__':
#     computer("0835", 12)


def getSchoolWord(code, k):
    '''
    统计该学校的词表
    :param code:
    :param k:
    :return:
    '''
    # sql = "SELECT name FROM `discipline_new` where code=%s"
    sql = "SELECT name FROM `es_discipline` where code=%s" % code
    teacherSchool = pickle.load(open(root+'/teacherSchool', 'rb'))
    # result = dbs.getDics(sql, (code,))
    result = dbs.getDics(sql)
    name = result[0]['name']  #学科名
    path = root+'/' + name + '-' + code
    file = open(path + "/" + code + "_fenci_tdidf.txt", 'r', encoding="utf8")
    paper = pickle.load(open(root + '/paperTeacher', 'rb'))  #{943985: {'name': '许乔瑜', 'author_id': 78419}}
    list = file.readlines()  #["{'fenci': '内涵 现场 分布特征 部位 中央 部位 潜力', 'id': 353392}\n", "{'fenci': '教材中', 'id': 530129}\n",.....]
    # print(paper)
    # print(list)
    schoolWord = {}
    for line in list:
        temp = eval(line) #{'fenci': '内涵 现场 分布特征 部位 中央 部位 潜力', 'id': 353392}
        paper_id = temp['id']
        if paper_id in paper:
            teacher_id = paper[paper_id]["id"]
        else:
            continue

        if teacher_id in teacherSchool:
            school_id = teacherSchool[teacher_id]
        else:
            continue
        if school_id not in schoolWord:
            schoolWord[school_id] = {}
        words = temp['fenci'].split(' ')
        for w in words:
            if w in schoolWord[school_id]:
                schoolWord[school_id][w] += 1
            else:
                schoolWord[school_id][w] = 1  #{0: {'': 3, '扫描电镜': 1, '分布特征': 1, '内涵': 1, '模型计算': 1, '系统分析': 1,}, school_id: {} ,...}
    # print(schoolWord)
    pickle.dump(schoolWord, open(root+'/' + code + '/k' + str(k) + '/schoolWord', 'wb'))

# if __name__ == '__main__':
#     getSchoolWord("0835", 12)

def computerSchool(code, k):
    '''

    :param code:
    :param k:
    :return:
    '''
    schoolWord = pickle.load(open(root+'/' + code+'/k'+str(k) + '/schoolWord', 'rb'))
    word = {}
    wordIndex = {}
    length = 0
    for school_id in schoolWord:
        school = schoolWord[school_id] #某一学校对应的词表
        size = len(school) #学校对应的词表长度（重复词算一个）
        for w in school:
            if w not in wordIndex:
                wordIndex[w] = {}
                word[w] = 0
            word[w] += school[w]
            length += school[w]  #学校对应论文中的所有词
            wordIndex[w][school_id] = school[w] / size # 该词出现的次数除以学校词表的长度
    for w in word:
        wordIndex[w]["col_fre"] = word[w] / length #该词出现的次数 除以该校所有论文的总词数
    # print(wordIndex)
    pickle.dump(wordIndex, open(root+'/' + code+'/k'+str(k)+'/s_wordIndex', 'wb'))
# if __name__ == '__main__':
#     computerSchool("0835", 12)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''
这段代码粘贴自duan，作用是创建学院的索引
'''
def getInstitutionWord(code, k):
    #institutionWord {institution_id1:{word1:word1出现的次数，word2：word2出现的次数,...},institution_id2:{word1:word1出现的次数，word2：word2出现的次数,...}}
    sql = "SELECT name FROM `es_discipline` where code=%s"
    #teacher - institution{teacher_id1: institution1, teacher_id2: institution2}
    teacherInstitutionWord=pickle.load(open(root + '/teacherInstitution', 'rb'))
    result = dbs.getDics(sql, (code,))
    #name学科名字
    name = result[0]['name']
    path = root+'/' + name + '-' + code
    #file对应的是计算tfidf后的文件
    file = open(path + "/" + code + "_fenci_tdidf.txt", 'r', encoding="utf8")
    #paper paper和teacher的对应关系
    paper = pickle.load(open(root+'/paperTeacher', 'rb'))
    list = file.readlines()
    institutionWord = {}
    for line in list:
        #temp 字典 {id:paperid,fenci:paper中的关键词}
        temp = eval(line)
        paper_id = temp['id']
        if paper_id in paper:
            print(paper[paper_id])
            teacher_id = paper[paper_id]["id"]
            institution_id=teacherInstitutionWord[teacher_id]
            if institution_id not in institutionWord :
                institutionWord[institution_id] = {}
            words = temp['fenci'].split(' ')
            for w in words:
                if w in institutionWord [institution_id]:
                    institutionWord[institution_id][w] += 1
                else:
                    institutionWord[institution_id][w] = 1

    pickle.dump(institutionWord, open(root+'/' + code + '/k' + str(k) + '/institutionWord', 'wb'))
def computerInstitution(code,k):
    '''
    {word1:{institution_id1:word1在这个学校数据中出现总次数/这个institution_id对应的词个数,institution_id2:word1在这个学校数据中出现总次数/这个institution_id对应的词个数,col_fre:word[w]/length},...}
    :param code:
    :param k:
    :return:
    '''
    institutionWord=pickle.load(open(root+'/'+ code+'/k'+str(k)+'/institutionWord', 'rb'))
    word={}
    wordIndex={}
    length=0
    # institutionWord {institution_id1:{word1:word1出现的次数，word2：word2出现的次数,...},institution_id2:{word1:word1出现的次数，word2：word2出现的次数,...}}
    for institution_id in institutionWord:
        institution = institutionWord[institution_id]
        #这个institution_id对应的词个数
        size=len(institution)
        for w in institution:
            if w not in wordIndex:
                wordIndex[w]={}
                word[w]=0
            #word统计每个词出现的次数
            word[w]+=institution[w]
            #length统计所有词出现的总次数
            length+=institution[w]
            #wordIndex {word1:{institution_id:word1在这个学校数据中出现总次数/这个institution_id对应的词个数,col_fre:word[w]/length}}
            wordIndex[w][institution_id]=institution[w]/size
    for w in word:
        wordIndex[w]["col_fre"]=word[w]/length
    pickle.dump(wordIndex, open(root+'/'+ code+'/k'+str(k)+'/i_wordIndex', 'wb'))






# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------









if __name__ == '__main__':
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
        getTeacherWord(sub['code'], sub['k'])
        computer(sub['code'], sub['k'])
        getSchoolWord(sub['code'], sub['k'])
        computerSchool(sub['code'], sub['k'])


        # ---------------------------------
        getInstitutionWord(sub['code'], sub['k'])
        computerInstitution(sub['code'], sub['k'])
        # ---------------------------------
