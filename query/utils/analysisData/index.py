from  utils.base import dbs
from  utils.config import root
import pickle
def getTeacherWord(code,k):
    '''
    TeacherWord {teacher_id1:{word1:num1,word2:num2},teacher_id2:{word1:num1,...},...}
    :param code:学科代码
    :param k: 主题数
    :return:
    '''
    sql="SELECT name FROM `discipline_new` where code=%s"
    result = dbs.getDics(sql,(code,))
    #result :[{'name': '农业工程'}]
    #name是code对应的学科名字
    name=result[0]['name']
    path=root+'/' + name + '-' + code
    #file对应的是计算tfidf后的文件
    file= open(path+ "/"+code+"_fenci_tdidf.txt", 'r', encoding="utf8")
    #paper是paper-teacher的对应关系
    paper = pickle.load(open(root+'/paperTeacher', 'rb'))
    list=file.readlines()
    teacherWord={}
    for line in list:
        #temp 字典 {id:paperid,fenci:paper中的关键词}
        temp=eval(line)
        paper_id=temp['id']
        # 70511 论文有30万篇，能找到作者的只有70000篇，所以很多对应不上，而学长代码是在一张表中，必然对应的上，所以要修改代码,判断该paper能否找到作者。
        if paper_id in paper:
            teacher_id=paper[paper_id]["author_id"]
            if teacher_id not in teacherWord:
                teacherWord[teacher_id]={}
            words=temp['fenci'].split(' ')
            for w in words:
                if w in teacherWord[teacher_id]:
                    teacherWord[teacher_id][w]+=1
                else:
                    teacherWord[teacher_id][w]= 1

    pickle.dump(teacherWord, open(root+'/'+ code+'/k'+str(k)+'/teacherWord', 'wb'))

def computer(code,k):
    '''
    wordIndex {word1:{teacher_id1:word1出现的次数/总词数，teacher_id1:word1出现的次数/总词数,col_fre:word[w]/length},word1:{teacher_id1:word1出现的次数/总词数，teacher_id1:word1出现的次数/总词数}}
    :param code:
    :param k:
    :return:
    '''
    teacherWord=pickle.load(open(root+'/'+ code+'/k'+str(k)+'/teacherWord', 'rb'))
    word={}
    wordIndex={}
    length=0
    #teacherWord          {teacher_id1: {word1: num1, word2: num2}, teacher_id2: {word1: num1, ...}, ...}
    for teacher_id in teacherWord:
        #teacher是上述teacher_id所对应的词的字典
        teacher = teacherWord[teacher_id]
        #siz是上述teacher_id所对应的词个数
        size=len(teacher)
        #w是词
        for w in teacher:
            if w not in wordIndex:
                wordIndex[w]={}
                word[w]=0
            #word统计每个单词出现的总次数
            word[w]+=teacher[w]
            #length统计总的单词个数
            length+=teacher[w]
            #wordIndex {word1:{teacher_id1:word1出现的次数/总词数，teacher_id1:word1出现的次数/总词数},word1:{teacher_id1:word1出现的次数/总词数，teacher_id1:word1出现的次数/总词数}}
            wordIndex[w][teacher_id] = teacher[w]/size
    for w in word:

        #col_fre 单词出现次数/总次数
        wordIndex[w]["col_fre"]=word[w]/length
    pickle.dump(wordIndex, open(root+'/'+ code+'/k'+str(k)+'/wordIndex', 'wb'))
def getSchoolWord(code, k):
    #schoolWord {school_id1:{word1:word1出现的次数，word2：word2出现的次数,...},school_id2:{word1:word1出现的次数，word2：word2出现的次数,...}}
    sql = "SELECT name FROM `discipline_new` where code=%s"
    #teacher - school{teacher_id1: school1, teacher_id2: school2}
    teacherSchool=pickle.load(open(root+'/teacherSchool', 'rb'))
    result = dbs.getDics(sql, (code,))
    #name学科名字
    name = result[0]['name']
    path = root+'/' + name + '-' + code
    #file对应的是计算tfidf后的文件
    file = open(path + "/" + code + "_fenci_tdidf.txt", 'r', encoding="utf8")
    #paper paper和teacher的对应关系
    paper = pickle.load(open(root+'/paperTeacher', 'rb'))
    list = file.readlines()
    schoolWord = {}
    for line in list:
        #temp 字典 {id:paperid,fenci:paper中的关键词}
        temp = eval(line)
        paper_id = temp['id']
        if paper_id in paper:
            teacher_id = paper[paper_id]["author_id"]
            school_id=teacherSchool[teacher_id]
            if school_id not in schoolWord :
                schoolWord[school_id] = {}
            words = temp['fenci'].split(' ')
            for w in words:
                if w in schoolWord [school_id]:
                    schoolWord[school_id][w] += 1
                else:
                    schoolWord[school_id][w] = 1

    pickle.dump(schoolWord, open(root+'/' + code + '/k' + str(k) + '/schoolWord', 'wb'))
def computerSchool(code,k):
    '''
    {word1:{school_id1:word1在这个学校数据中出现总次数/这个school_id对应的词个数,school_id2:word1在这个学校数据中出现总次数/这个school_id对应的词个数,col_fre:word[w]/length},...}
    :param code:
    :param k:
    :return:
    '''
    schoolWord=pickle.load(open(root+'/'+ code+'/k'+str(k)+'/schoolWord', 'rb'))
    word={}
    wordIndex={}
    length=0
    # schoolWord {school_id1:{word1:word1出现的次数，word2：word2出现的次数,...},school_id2:{word1:word1出现的次数，word2：word2出现的次数,...}}
    for school_id in schoolWord:
        school = schoolWord[school_id]
        #这个school_id对应的词个数
        size=len(school)
        for w in school:
            if w not in wordIndex:
                wordIndex[w]={}
                word[w]=0
            #word统计每个词出现的次数
            word[w]+=school[w]
            #length统计所有词出现的总次数
            length+=school[w]
            #wordIndex {word1:{school_id:word1在这个学校数据中出现总次数/这个school_id对应的词个数,col_fre:word[w]/length}}
            wordIndex[w][school_id]=school[w]/size
    for w in word:
        wordIndex[w]["col_fre"]=word[w]/length
    pickle.dump(wordIndex, open(root+'/'+ code+'/k'+str(k)+'/s_wordIndex', 'wb'))
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
        #计算teacher所写的关键字出现次数
        getTeacherWord(sub['code'],sub['k'])
        #计算每个单词，在某个老师的词中出现的次数，及这个词出现的次数/词出现的总次数
        computer(sub['code'],sub['k'])
        getSchoolWord(sub['code'],sub['k'])
        computerSchool(sub['code'], sub['k'])
        pass