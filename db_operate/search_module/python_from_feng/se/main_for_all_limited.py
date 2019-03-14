# coding=utf-8
from __future__ import division
from search_module.python_from_feng.se.config import root
import pickle
import time,jieba,math
import jieba.posseg as pseg

class Subject_for_teacher:
    #subs = [{"code": '0828', "k": 36}, {"code": '0829', "k": 14}]
    #self.subs = subs
    #self.Subject_for_teacher = {sub['code']: Subject_for_teacher(sub, self.id_name) for sub in self.subs}
    #self.Subject_for_teacher = {0828:Subject_for_teacher({"code": '0828', "k": 36},self.id_name),0829:Subject_for_teacher({"code": '0829', "k": 14}}
    def __init__(self,sub,id_name):
        #({"code": '0828', "k": 36},self.id_name)
        self.sub=sub
        #self.id_name 字典
        self.id_name=id_name
        code=self.sub['code']
        k=self.sub['k']
        print("load:"+code)
        self.path= root+'/' + code + '/k' + str(k)
        #词的索引 wordIndex   {word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数, col_fre: word[w] / length}, word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数}}
        self.lmindex =  pickle.load(open(self.path+'/wordIndex', 'rb'))
        #word和topic的关系 wordToTopic  word2topic {'催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0,}
        self.ldaword = pickle.load(open(self.path+'/wordToTopic', 'rb'))
        #教师和topic的关系 {teacher1: {topic1: p1, topic2: p2}, ...}
        self.ldaexp = pickle.load(open(self.path+'/teacherTopic', 'rb'))
        #教师PageRank评分 {teacher_id:value,...}
        self.pagerank = pickle.load(open(self.path+'/teacherRank', 'rb'))

        self.cal = 0.9

    def cal_lda_one_word(self,word,teacher_id):
        '''
        没有用
        :param word:
        :param teacher_id:
        :return:
        '''
        """计算单个词的专家lda得分"""
        # self.ldaword         wordToTopi {'催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0, }
        ld = self.ldaword.get(word)
        #sort      {topic_id1:value,...} 筛选出value>1.0e-06 value降序排序
        sort = {}
        #res       {teacher_id1:value,...}
        res = {}
        #ld     '催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0, }
        if ld != None:
            if teacher_id is not None:
                ld = {k: ld[k] for k in ld if k in teacher_id}
            #对字典中的项，进行值升序排序，然后逆序，返回一个列表 [(topic_id1:value),(topic_id2:value),(topic_id3:value),...]
            sortld = sorted(ld.items(),key=lambda item:item[1],reverse=True)
            a = [r for r in sortld if r[1]>1.0e-06]
            for i in a :
                sort[i[0]] = i[1]

        for j in sort.keys():
            #j是 topic_id
            #ldaexp        教师和topic的关系{teacher1: {topic1: p1, topic2: p2}, ...}
            for m in self.ldaexp.keys():
                #m是teacher_id
                if j in self.ldaexp[m]:
                    #id为m的老师对某主题的值乘这个主题对这个词的值
                    res[m] = self.ldaexp[m][j]*sort[j]

        return res

    def cal_one_word(self,word,teacher_id):
        '''
        :param word:一个被搜索的词
        :param teacher_id:
        :return:
        '''
        """计算单个词的专家语言模型得分"""

        # lm = wordIndex   {word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数, col_fre: word[w] / length}, word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数}}
        lm = self.lmindex.get(word)  #type dict
        res = {}
        # 引入平滑系数
        #lm可能为空，因为这是一个学科的倒排索引表，可能没这个单词
        if lm != None:
            #lm    {teacher_id1: word1出现的次数 / 总词数，teacher_id2: word1出现的次数 / 总词数, col_fre: word[w] / length}
            if teacher_id is not None:
                lm = {k: lm[k] for k in lm if k in teacher_id or k=="col_fre"}
            for l in lm.keys():
                #l teacher_id
                if l != 'col_fre':
                    res[l] = self.cal*lm[l]+(1-self.cal)*lm['col_fre']
            res['col'] = lm['col_fre']
        #res =  {'teacher_id':value,...,col:lm['col_fre']}
        return res

    def cal_rank(self,res,lda,cof):
        '''

        :param res: {word1:{'teacher_id':value,...,col:lm['col_fre'],...}
        :param lda: {word1:{teacher_id1:value,...},...}
        :param cof: cof = math.pow(10e-6, len(words) - max(len(temp_res), len(temp_lda)))
        :return:
        '''
        """计算专家排序"""
        rank = {}
        #wd是res的key,代表词，res[wd]还是字典，代表词对应的老师及其对该词的值，r是res[wd]中的key,代表老师id
        #exp_list [teacher_id1,teacher_id2,...]
        exp_list = [r for wd in res.keys() for r in res[wd]]
        exp_list = set(exp_list)
        if 'col' in exp_list:
            #教师名单，所以去掉cof
            exp_list.remove('col')
        #rank   {'teacher_id1':cof,teacher_id2:cof}
        #r teacher_id
        for r in exp_list:
            rank[r] = cof
            #wd word
            for wd in res.keys():
                if len(res[wd]) != 0:
                    #如果res[wd]中有r这个teacher_id,那么给这个
                     if res[wd].get(r):
                        rank[r] *= res[wd][r]
                     else:
                        rank[r] *= res[wd]['col']

                if wd in lda and lda[wd].get(r):
                    adjust = lda[wd][r]
                    rank[r] *= adjust
                else:
                    rank[r] *= 10e-6
            for wd in lda:
                if wd not in res:
                    rank[r]*=lda[wd][r]
            if self.pagerank.get(r):
                rank[r] *= self.pagerank[r]*self.id_name[r]["total"]
        return rank

    def do_query(self,words,teacher_id):
        #words为搜索的关键字集合的列表，teacher_id默认为空
        #temp_res  {word1:{'teacher_id':value,...,col:lm['col_fre']},word2:{'teacher_id':value,...,col:lm['col_fre']},...}
        temp_res = {}
        # res       {word1:{teacher_id1:value,...},...}
        temp_lda = {}

        for word in words :
            temp_res[word] = self.cal_one_word(word,teacher_id)

            temp_lda[word] = self.cal_lda_one_word(word,teacher_id)
        for word in words:
            if word in temp_res and not temp_res[word]:
            #Python 字典 pop() 方法删除字典给定键 key 及对应的值，返回值为被删除的值。key 值必须给出。 否则，返回 default 值。
                temp_res.pop(word)
            if word in temp_lda and not temp_lda[word]:
                temp_lda.pop(word)
        if not temp_res and not temp_lda:
            return []
        #返回xy（x的y次方） 的值。
        cof = math.pow(10e-6, len(words) - max(len(temp_res), len(temp_lda)))
        level = math.pow(10e-6, len(words)+1)
        rank = self.cal_rank(temp_res,temp_lda,cof)
        sortrk = sorted(rank.items(), key=lambda item: item[1], reverse=True)
        result = [(r[0],r[1]) for r in sortrk if r[1]>level]
        #result [(teacher_id,'权值'),(),..]
        return result
class Query_for_teacher:
    def __init__(self,subs):
        # [{"code": '01', "k": 46}, {"code": '02', "k": 98}]
        self.subs=subs
        #{teacher_id1:{id:xx,name:xxx},...}
        self.id_name = pickle.load(open(root + '/teacherName', 'rb'))
        #self.Subject_for_teacher {code1:Subject_for_teacher(sub1),sode2:Subject_for_teacher2(sub2)}
        self.Subject_for_teacher={sub['code']:Subject_for_teacher(sub,self.id_name) for sub in self.subs}
        self.stop=[]
        stopword = [line.strip() for line in open('fenci/stopwords.txt', encoding='utf-8').readlines()]
        stopword1 = [line.strip() for line in open('fenci/stop_word_4.txt', encoding='utf-8').readlines()]
        stopwords = [i.split(':')[0] for i in stopword1]
        self.stop.extend(stopword)
        self.stop.extend(stopwords)
        self.fill = ['vn', 'n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf',
                'nt', 'nz', 'nl', 'ng']
        jieba.load_userdict('fenci/userdict.txt')

    def prints(self,result):
        # {'0828': [(23711, 0.031088879496921837), (23721, 0.003430221466157156), (143479, 0.00010151384288551602)],
        #  '0829': [],
        #  '0830': [(126955, 0.0007021102104810927), (68129, 0.00013266169457311943), (22286, 0.00011640344697493587),
        #           (5818, 1.821814740424121e-05)]}
        for code in result:
            size=len(result[code])
            if size==0:
                continue
            #教师个数
            print("学科:%s,有关教师个数：%d" %(code,size))
            teacher=result[code]
            for t in teacher:
                #教师名字：（id:权重)
                print(self.id_name[t[0]]["NAME"]+":"+str(t))
            print()

    def do_query(self,text,filer):
        #将输入内容进行分词

        texts = jieba.cut(text, cut_all=False)
        print("texts   :  ", texts)
        texts = " ".join(texts)
        seg_list = pseg.cut(texts)
        words = []
        for word, flag in seg_list:
            if flag in self.fill and word not in self.stop:
                #是名词且不是停用词，将其纳入搜索列表
                words.append(word)
        print(words)
        if "school" in filer and len(filer["school"])>0:
            teacher_id={t for t in self.id_name if self.id_name[t]['school_id'] in filer['school']}
        else:
            teacher_id=None

        #筛选符合院系信息的老师
        if "institution" in filer and len(filer['institution'])>0:
            teacher_id = {t for t in self.id_name if str(self.id_name[t]['INSTITUTION_ID']) in filer['institution']}
        else:
            teacher_id=None

        if "name" in filer and len(filer["name"])>0:
            if teacher_id:
                teacher_id={t for t in teacher_id if self.id_name[t]['name'].find(filer["name"])>=0}
            else:
                teacher_id = {t for t in self.id_name if self.id_name[t]['name'].find(filer["name"])>=0}
        result={}
        #teacher_id dict None
        for sub in self.Subject_for_teacher:
            if "code" in filer and len(filer['code'])>0 and sub not in filer['code']:
                continue
            else:
                # self.Subject_for_teacher {code1:Subject_for_teacher(sub1),sode2:Subject_for_teacher2(sub2)}
                result[sub]=self.Subject_for_teacher[sub].do_query(words,teacher_id)
        #result {code:[teacher_id:value,].,code:[],...}
        return result
class Subject_for_institution:
    #subs = [{"code": '0828', "k": 36}, {"code": '0829', "k": 14}]
    #self.subs = subs
    #self.Subject_for_institution = {sub['code']: Subject_for_institution(sub, self.id_name) for sub in self.subs}
    #self.Subject_for_institution = {0828:Subject_for_institution({"code": '0828', "k": 36},self.id_name),0829:Subject_for_institution({"code": '0829', "k": 14}}
    def __init__(self,sub,id_name):
        #({"code": '0828', "k": 36},self.id_name)
        self.sub=sub
        #self.id_name 字典
        self.id_name=id_name
        code=self.sub['code']
        k=self.sub['k']
        print("load:"+code)
        self.path= root+'/' + code + '/k' + str(k)
        #词的索引 wordIndex   {word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数, col_fre: word[w] / length}, word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数}}
        self.lmindex =  pickle.load(open(self.path+'/i_wordIndex', 'rb'))
        #word和topic的关系 wordToTopic  word2topic {'催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0,}
        self.ldaword = pickle.load(open(self.path+'/wordToTopic', 'rb'))
        #教师和topic的关系 {teacher1: {topic1: p1, topic2: p2}, ...}
        self.ldaexp = pickle.load(open(self.path+'/institutionTopic', 'rb'))
        #教师PageRank评分 {teacher_id:value,...}
        self.pagerank = pickle.load(open(self.path+'/institutionRank', 'rb'))

        self.cal = 0.9

    def cal_lda_one_word(self,word,teacher_id):
        '''
        没有用
        :param word:
        :param teacher_id:
        :return:
        '''
        """计算单个词的专家lda得分"""
        # self.ldaword         wordToTopi {'催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0, }
        ld = self.ldaword.get(word)
        #sort      {topic_id1:value,...} 筛选出value>1.0e-06 value降序排序
        sort = {}
        #res       {teacher_id1:value,...}
        res = {}
        #ld     '催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0, }
        if ld != None:
            if teacher_id is not None:
                ld = {k: ld[k] for k in ld if k in teacher_id}
            #对字典中的项，进行值升序排序，然后逆序，返回一个列表 [(topic_id1:value),(topic_id2:value),(topic_id3:value),...]
            sortld = sorted(ld.items(),key=lambda item:item[1],reverse=True)
            a = [r for r in sortld if r[1]>1.0e-06]
            for i in a :
                sort[i[0]] = i[1]

        for j in sort.keys():
            #j是 topic_id
            #ldaexp        教师和topic的关系{teacher1: {topic1: p1, topic2: p2}, ...}
            for m in self.ldaexp.keys():
                #m是teacher_id
                if j in self.ldaexp[m]:
                    #id为m的老师对某主题的值乘这个主题对这个词的值
                    res[m] = self.ldaexp[m][j]*sort[j]

        return res

    def cal_one_word(self,word,teacher_id):
        '''
        :param word:一个被搜索的词
        :param teacher_id:
        :return:
        '''
        """计算单个词的专家语言模型得分"""

        # lm = wordIndex   {word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数, col_fre: word[w] / length}, word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数}}
        lm = self.lmindex.get(word)  #type dict
        res = {}
        # 引入平滑系数
        #lm可能为空，因为这是一个学科的倒排索引表，可能没这个单词
        if lm != None:
            #lm    {teacher_id1: word1出现的次数 / 总词数，teacher_id2: word1出现的次数 / 总词数, col_fre: word[w] / length}
            if teacher_id is not None:
                lm = {k: lm[k] for k in lm if k in teacher_id or k=="col_fre"}
            for l in lm.keys():
                #l teacher_id
                if l != 'col_fre':
                    res[l] = self.cal*lm[l]+(1-self.cal)*lm['col_fre']
            res['col'] = lm['col_fre']
        #res =  {'teacher_id':value,...,col:lm['col_fre']}
        return res

    def cal_rank(self,res,lda,cof):
        '''

        :param res: {word1:{'teacher_id':value,...,col:lm['col_fre'],...}
        :param lda: {word1:{teacher_id1:value,...},...}
        :param cof: cof = math.pow(10e-6, len(words) - max(len(temp_res), len(temp_lda)))
        :return:
        '''
        """计算专家排序"""
        rank = {}
        #wd是res的key,代表词，res[wd]还是字典，代表词对应的老师及其对该词的值，r是res[wd]中的key,代表老师id
        #exp_list [teacher_id1,teacher_id2,...]
        exp_list = [r for wd in res.keys() for r in res[wd]]
        exp_list = set(exp_list)
        if 'col' in exp_list:
            #教师名单，所以去掉cof
            exp_list.remove('col')
        #rank   {'teacher_id1':cof,teacher_id2:cof}
        #r teacher_id
        for r in exp_list:
            rank[r] = cof
            #wd word
            for wd in res.keys():
                if len(res[wd]) != 0:
                    #如果res[wd]中有r这个teacher_id,那么给这个
                     if res[wd].get(r):
                        rank[r] *= res[wd][r]
                     else:
                        rank[r] *= res[wd]['col']

                if wd in lda and lda[wd].get(r):
                    adjust = lda[wd][r]
                    rank[r] *= adjust
                else:
                    rank[r] *= 10e-6
            for wd in lda:
                if wd not in res:
                    rank[r]*=lda[wd][r]
            if self.pagerank.get(r):
                rank[r] *= self.pagerank[r]*self.id_name[r]["total"]
        return rank

    def do_query(self,words,teacher_id):
        #words为搜索的关键字集合的列表，teacher_id默认为空
        #temp_res  {word1:{'teacher_id':value,...,col:lm['col_fre']},word2:{'teacher_id':value,...,col:lm['col_fre']},...}
        temp_res = {}
        # res       {word1:{teacher_id1:value,...},...}
        temp_lda = {}

        for word in words :
            temp_res[word] = self.cal_one_word(word,teacher_id)

            temp_lda[word] = self.cal_lda_one_word(word,teacher_id)
        for word in words:
            if word in temp_res and not temp_res[word]:
            #Python 字典 pop() 方法删除字典给定键 key 及对应的值，返回值为被删除的值。key 值必须给出。 否则，返回 default 值。
                temp_res.pop(word)
            if word in temp_lda and not temp_lda[word]:
                temp_lda.pop(word)
        if not temp_res and not temp_lda:
            return []
        #返回xy（x的y次方） 的值。
        cof = math.pow(10e-6, len(words) - max(len(temp_res), len(temp_lda)))
        level = math.pow(10e-6, len(words)+1)
        rank = self.cal_rank(temp_res,temp_lda,cof)
        sortrk = sorted(rank.items(), key=lambda item: item[1], reverse=True)
        result = [(r[0],r[1]) for r in sortrk if r[1]>level]
        #result [(teacher_id,'权值'),(),..]
        return result
class Query_for_institution:
    def __init__(self,subs):
        # [{"code": '01', "k": 46}, {"code": '02', "k": 98}]
        self.subs=subs
        #{teacher_id1:{id:xx,name:xxx},...}
        self.id_name = pickle.load(open(root + '/InstitutionName', 'rb'))
        #self.Subject_for_institution {code1:Subject_for_institution(sub1),sode2:Subject_for_institution2(sub2)}
        self.Subject_for_institution={sub['code']:Subject_for_institution(sub,self.id_name) for sub in self.subs}
        self.stop=[]
        stopword = [line.strip() for line in open('fenci/stopwords.txt', encoding='utf-8').readlines()]
        stopword1 = [line.strip() for line in open('fenci/stop_word_4.txt', encoding='utf-8').readlines()]
        stopwords = [i.split(':')[0] for i in stopword1]
        self.stop.extend(stopword)
        self.stop.extend(stopwords)
        self.fill = ['vn', 'n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf',
                'nt', 'nz', 'nl', 'ng']
        jieba.load_userdict('fenci/userdict.txt')

    def prints(self,result):
        # {'0828': [(23711, 0.031088879496921837), (23721, 0.003430221466157156), (143479, 0.00010151384288551602)],
        #  '0829': [],
        #  '0830': [(126955, 0.0007021102104810927), (68129, 0.00013266169457311943), (22286, 0.00011640344697493587),
        #           (5818, 1.821814740424121e-05)]}
        for code in result:
            size=len(result[code])
            if size==0:
                continue
            #教师个数
            print("学科:%s,有关学院个数：%d" %(code,size))
            teacher=result[code]
            print(code)
            for t in teacher:
                #教师名字：（id:权重)
                print(self.id_name[t[0]]["SCHOOL_NAME"]+self.id_name[t[0]]["NAME"]+":"+str(t))
            print()

    def do_query(self,text,filer):
        #将输入内容进行分词
        seg_list = pseg.cut(text)
        words = []
        for word, flag in seg_list:
            if flag in self.fill and word not in self.stop:
                #是名词且不是停用词，将其纳入搜索列表
                words.append(word)
        print(words)
        if "school" in filer and len(filer["school"])>0:
            teacher_id={t for t in self.id_name if self.id_name[t]['SCHOOL_NAME'] in filer['school']}
        else:
            teacher_id=None
        if "name" in filer and len(filer["name"])>0:
            if teacher_id:
                teacher_id={t for t in teacher_id if self.id_name[t]['name'].find(filer["name"])>=0}
            else:
                teacher_id = {t for t in self.id_name if self.id_name[t]['name'].find(filer["name"])>=0}
        result={}
        #teacher_id dict None
        for sub in self.Subject_for_institution:
            if "code" in filer and len(filer['code'])>0 and sub not in filer['code']:
                continue
            else:
                # self.Subject_for_institution {code1:Subject_for_institution(sub1),sode2:Subject_for_institution2(sub2)}
                result[sub]=self.Subject_for_institution[sub].do_query(words,teacher_id)
        #result {code:[teacher_id:value,].,code:[],...}
        return result
class Subject_for_school():

    # subs = [{"code": '0828', "k": 36}, {"code": '0829', "k": 14}]
    # self.subs = subs
    # self.Subject_for_school = {sub['code']: Subject_for_school(sub, self.id_name) for sub in self.subs}
    # self.Subject_for_school = {0828:Subject_for_school({"code": '0828', "k": 36},self.id_name),0829:Subject_for_school({"code": '0829', "k": 14}}
    def __init__(self, sub, id_name):
        # ({"code": '0828', "k": 36},self.id_name)
        self.sub = sub
        # self.id_name 字典
        self.id_name = id_name
        code = self.sub['code']
        k = self.sub['k']
        print("load:" + code)
        self.path = root + '/' + code + '/k' + str(k)
        # 词的索引 wordIndex   {word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数, col_fre: word[w] / length}, word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数}}
        self.lmindex = pickle.load(open(self.path + '/s_wordIndex', 'rb'))
        # word和topic的关系 wordToTopic  word2topic {'催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0,}
        self.ldaword = pickle.load(open(self.path + '/wordToTopic', 'rb'))
        # 教师和topic的关系 {teacher1: {topic1: p1, topic2: p2}, ...}
        self.ldaexp = pickle.load(open(self.path + '/schoolTopic', 'rb'))
        # 教师PageRank评分 {teacher_id:value,...}
        self.pagerank = pickle.load(open(self.path + '/schoolRank', 'rb'))

        self.cal = 0.9

    def cal_lda_one_word(self, word, teacher_id):
        '''
        没有用
        :param word:
        :param teacher_id:
        :return:
        '''
        """计算单个词的专家lda得分"""
        # self.ldaword         wordToTopi {'催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0, }
        ld = self.ldaword.get(word)
        # sort      {topic_id1:value,...} 筛选出value>1.0e-06 value降序排序
        sort = {}
        # res       {teacher_id1:value,...}
        res = {}
        # ld     '催化剂': {0: 0.104, 1: 0.0, 2: 0.0, 3: 0.0, }
        if ld != None:
            if teacher_id is not None:
                ld = {k: ld[k] for k in ld if k in teacher_id}
            # 对字典中的项，进行值升序排序，然后逆序，返回一个列表 [(topic_id1:value),(topic_id2:value),(topic_id3:value),...]
            sortld = sorted(ld.items(), key=lambda item: item[1], reverse=True)
            a = [r for r in sortld if r[1] > 1.0e-06]
            for i in a:
                sort[i[0]] = i[1]

        for j in sort.keys():
            # j是 topic_id
            # ldaexp        教师和topic的关系{teacher1: {topic1: p1, topic2: p2}, ...}
            for m in self.ldaexp.keys():
                # m是teacher_id
                if j in self.ldaexp[m]:
                    # id为m的老师对某主题的值乘这个主题对这个词的值
                    res[m] = self.ldaexp[m][j] * sort[j]

        return res

    def cal_one_word(self, word, teacher_id):
        '''
        :param word:一个被搜索的词
        :param teacher_id:
        :return:
        '''
        """计算单个词的专家语言模型得分"""

        # lm = wordIndex   {word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数, col_fre: word[w] / length}, word1: {teacher_id1: word1出现的次数 / 总词数，teacher_id1: word1出现的次数 / 总词数}}
        lm = self.lmindex.get(word)  # type dict
        res = {}
        # 引入平滑系数
        # lm可能为空，因为这是一个学科的倒排索引表，可能没这个单词
        if lm != None:
            # lm    {teacher_id1: word1出现的次数 / 总词数，teacher_id2: word1出现的次数 / 总词数, col_fre: word[w] / length}
            if teacher_id is not None:
                lm = {k: lm[k] for k in lm if k in teacher_id or k == "col_fre"}
            for l in lm.keys():
                # l teacher_id
                if l != 'col_fre':
                    res[l] = self.cal * lm[l] + (1 - self.cal) * lm['col_fre']
            res['col'] = lm['col_fre']
        # res =  {'teacher_id':value,...,col:lm['col_fre']}
        return res

    def cal_rank(self, res, lda, cof):
        '''

        :param res: {word1:{'teacher_id':value,...,col:lm['col_fre'],...}
        :param lda: {word1:{teacher_id1:value,...},...}
        :param cof: cof = math.pow(10e-6, len(words) - max(len(temp_res), len(temp_lda)))
        :return:
        '''
        """计算专家排序"""
        rank = {}
        # wd是res的key,代表词，res[wd]还是字典，代表词对应的老师及其对该词的值，r是res[wd]中的key,代表老师id
        # exp_list [teacher_id1,teacher_id2,...]
        exp_list = [r for wd in res.keys() for r in res[wd]]
        exp_list = set(exp_list)
        if 'col' in exp_list:
            # 教师名单，所以去掉cof
            exp_list.remove('col')
        # rank   {'teacher_id1':cof,teacher_id2:cof}
        # r teacher_id
        for r in exp_list:
            rank[r] = cof
            # wd word
            for wd in res.keys():
                if len(res[wd]) != 0:
                    # 如果res[wd]中有r这个teacher_id,那么给这个
                    if res[wd].get(r):
                        rank[r] *= res[wd][r]
                    else:
                        rank[r] *= res[wd]['col']

                if wd in lda and lda[wd].get(r):
                    adjust = lda[wd][r]
                    rank[r] *= adjust
                else:
                    rank[r] *= 10e-6
            for wd in lda:
                if wd not in res:
                    rank[r] *= lda[wd][r]
            if self.pagerank.get(r) and r in self.id_name and self.id_name[r]['total'] is not None:
                print(rank[r])
                print("pagerank    ", self.pagerank[r])
                print("id_name[r]  ", self.id_name[r])
                print("total   ", self.id_name[r]["total"])
                rank[r] *= self.pagerank[r] * self.id_name[r]["total"]
        return rank

    def do_query(self, words, teacher_id):
        # words为搜索的关键字集合的列表，teacher_id默认为空
        # temp_res  {word1:{'teacher_id':value,...,col:lm['col_fre']},word2:{'teacher_id':value,...,col:lm['col_fre']},...}
        temp_res = {}
        # res       {word1:{teacher_id1:value,...},...}
        temp_lda = {}

        for word in words:
            temp_res[word] = self.cal_one_word(word, teacher_id)

            temp_lda[word] = self.cal_lda_one_word(word, teacher_id)
        for word in words:
            if word in temp_res and not temp_res[word]:
                # Python 字典 pop() 方法删除字典给定键 key 及对应的值，返回值为被删除的值。key 值必须给出。 否则，返回 default 值。
                temp_res.pop(word)
            if word in temp_lda and not temp_lda[word]:
                temp_lda.pop(word)
        if not temp_res and not temp_lda:
            return []
        # 返回xy（x的y次方） 的值。
        cof = math.pow(10e-6, len(words) - max(len(temp_res), len(temp_lda)))
        level = math.pow(10e-6, len(words) + 1)
        rank = self.cal_rank(temp_res, temp_lda, cof)
        sortrk = sorted(rank.items(), key=lambda item: item[1], reverse=True)
        result = [(r[0], r[1]) for r in sortrk if r[1] > level]
        # result [(teacher_id,'权值'),(),..]
        return result
class Query_for_school():
    def __init__(self, subs):
        # [{"code": '01', "k": 46}, {"code": '02', "k": 98}]
        self.subs = subs
        # {teacher_id1:{id:xx,name:xxx},...}
        self.id_name = pickle.load(open(root + '/SchoolName', 'rb'))
        # self.Subject_for_school {code1:Subject_for_school(sub1),sode2:Subject_for_school2(sub2)}
        self.Subject_for_school = {sub['code']: Subject_for_school(sub, self.id_name) for sub in self.subs}
        self.stop = []
        stopword = [line.strip() for line in open('fenci/stopwords.txt', encoding='utf-8').readlines()]
        stopword1 = [line.strip() for line in open('fenci/stop_word_4.txt', encoding='utf-8').readlines()]
        stopwords = [i.split(':')[0] for i in stopword1]
        self.stop.extend(stopword)
        self.stop.extend(stopwords)
        self.fill = ['vn', 'n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf',
                     'nt', 'nz', 'nl', 'ng']
        jieba.load_userdict('fenci/userdict.txt')

    def prints(self, result):
        # {'0828': [(23711, 0.031088879496921837), (23721, 0.003430221466157156), (143479, 0.00010151384288551602)],
        #  '0829': [],
        #  '0830': [(126955, 0.0007021102104810927), (68129, 0.00013266169457311943), (22286, 0.00011640344697493587),
        #           (5818, 1.821814740424121e-05)]}
        for code in result:
            size = len(result[code])
            if size == 0:
                continue
            # 教师个数
            print("学科:%s,有关学校个数：%d" % (code, size))
            teacher = result[code]
            print(code)
            for t in teacher:
                # 教师名字：（id:权重)
                print(self.id_name[t[0]]["NAME"] + ":" + str(t))
            print()

    def prints_for_city(self, result, province):
        # {'0828': [(23711, 0.031088879496921837), (23721, 0.003430221466157156), (143479, 0.00010151384288551602)],
        #  '0829': [],
        #  '0830': [(126955, 0.0007021102104810927), (68129, 0.00013266169457311943), (22286, 0.00011640344697493587),
        #           (5818, 1.821814740424121e-05)]}
        city_info = {}
        #SchoolAddress {school_id: (procince_id, city_id), }
        schoolAddress = pickle.load(open(root + '/schooladdress', 'rb'))
        for code in result:
            size = len(result[code])
            if size == 0:
                continue
            # 教师个数
            print("学科:%s,有关城市个数：%d" % (code, size))
            #[(23711, 0.031088879496921837), (23721, 0.003430221466157156), (143479, 0.00010151384288551602)]
            school_info = result[code]
            print(code)
            print(school_info)
            for t in school_info:
                #print(self.id_name[t[0]]["NAME"] + ":" + str(t))
                school_id = t[0]
                if school_id in schoolAddress:
                    city_id = schoolAddress[school_id][1]
                    schoolAddress[school_id][1]
                else:
                    continue
                if city_id in city_info:
                    city_info[city_id] += t[1]
                else:
                    city_info[city_id] = t[1]
            city_rank = dict(sorted(city_info.items(), key=lambda x: x[1], reverse=True))
            print("city rank ", city_rank)
            for city in city_rank:
                if city in provinceCity[province]:
                    print(city+' '+str(city_rank[city]))
            print()

    def prints_for_province(self, result):
        # {'0828': [(23711, 0.031088879496921837), (23721, 0.003430221466157156), (143479, 0.00010151384288551602)],
        #  '0829': [],
        #  '0830': [(126955, 0.0007021102104810927), (68129, 0.00013266169457311943), (22286, 0.00011640344697493587),
        #           (5818, 1.821814740424121e-05)]}
        province_info = {}
        #SchoolAddress {school_id: (procince_id, city_id), }
        schoolAddress =  pickle.load(open(root + '/schooladdress', 'rb'))
        for code in result:
            size = len(result[code])
            if size == 0:
                continue
            # 教师个数
            print("学科:%s,有关省的个数：%d" % (code, size))
            #[(23711, 0.031088879496921837), (23721, 0.003430221466157156), (143479, 0.00010151384288551602)]
            school_info = result[code]
            print(code)
            for t in school_info:
                # 学校名字：（id:权重)
                #print(self.id_name[t[0]]["NAME"] + ":" + str(t))
                school_id = t[0]
                # print("schoolAddress   ", schoolAddress[school_id])
                if school_id in schoolAddress:
                    province_id = schoolAddress[school_id][0]
                else:
                    continue
                if province_id in province_info:
                    province_info[province_id] += t[1]
                else:
                    province_info[province_id]=t[1]
            province_rank =dict(sorted(province_info.items(),key = lambda x:x[1],reverse=True))
            for province in province_rank:
                print(province+' '+str(province_rank[province]))
            print()


    def do_query(self, text, filer):
        # 将输入内容进行分词
        seg_list = pseg.cut(text)
        words = []
        for word, flag in seg_list:
            if flag in self.fill and word not in self.stop:
                # 是名词且不是停用词，将其纳入搜索列表
                words.append(word)
        print(words)
        if "city" in filer and len(filer["city"]) > 0:
            print('true')
            teacher_id = {t for t in self.id_name if self.id_name[t]['CITY'] in filer['city'] }
        else:
            teacher_id = None

        # if "school" in filer and len(filer["school"]) > 0:
        #     teacher_id = {t for t in self.id_name if self.id_name[t]['school_id'] in filer['school']}
        # else:
        #     teacher_id = None
        # if "name" in filer and len(filer["name"]) > 0:
        #     if teacher_id:
        #         teacher_id = {t for t in teacher_id if self.id_name[t]['name'].find(filer["name"]) >= 0}
        #     else:
        #         teacher_id = {t for t in self.id_name if self.id_name[t]['name'].find(filer["name"]) >= 0}
        result = {}
        # teacher_id dict None
        for sub in self.Subject_for_school:
            if "code" in filer and len(filer['code']) > 0 and sub not in filer['code']:
                continue
            else:
                # self.Subject_for_school {code1:Subject_for_school(sub1),sode2:Subject_for_school2(sub2)}
                result[sub] = self.Subject_for_school[sub].do_query(words, teacher_id)
        # result {code:[teacher_id:value,].,code:[],...}
        return result

def queryForProvince(filer):
    t = input("请输入要搜索的内容")
    # t = "计算机"
    start = time.time()
    r = query_for_school.do_query(t, filer)
    query_for_school.prints_for_province(r)
    end = time.time()
    # print (end - start)
def queryForCity(filer,province='北京'):
    t = input("请输入要搜索的内容")
    start = time.time()
    r = query_for_school.do_query(t, filer)
    query_for_school.prints_for_city(r,province)
    end = time.time()
    # print (end - start)

def queryForSchool(filer,city = '北京市'):
    t = input("请输入要搜索的内容")
    start = time.time()
    # filer['city'] = city
    r = query_for_school.do_query(t, filer)
    query_for_school.prints(r)
    end = time.time()
    # print (end - start)

def queryForInstitution(filer,school = '中国人民大学'):
    t = input("请输入要搜索的内容")
    start = time.time()
    # filer['school'] = school
    r = query_for_institution.do_query(t, filer)
    query_for_institution.prints(r)
    end = time.time()
    # print (end - star


def queryForTeacher(filer,institution_id = '1526'):
    t = input("请输入要搜索的内容")
    start = time.time()
    # filer['institution']=institution_id
    r = query_for_teacher.do_query(t, filer)
    query_for_teacher.prints(r)
    end = time.time()
    # print (end - start)

if __name__ == '__main__':

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
        {"code": '0826', "k": 10},
        {"code": '0824', "k": 12},
        {"code": '0808', "k": 12},
        {"code": '0822', "k": 12},
        {"code": '0814', "k": 10},
        {"code": '0804', "k": 12},
    ]
    #用于查询老师的对象
    query_for_teacher = Query_for_teacher(subject)
    #用于查询学院的对象
    query_for_institution = Query_for_institution(subject)
    #用于查询学校的对象
    query_for_school = Query_for_school(subject)
    #省和市的关系信息
    provinceCity = pickle.load(open(root + '\provinceCity', 'rb'))

    while True:
        #查询范围
        query_range = input('输入要查询的范围（省、市、学校、学院、教师）')
        # query_range = "省"
        #filer = {}
        if query_range == '省':
            filer = {}
            queryForProvince(filer)
        if query_range == '市':
            filer = {}
            queryForCity(filer,)
        if query_range == '学校':
            filer = {}
            queryForSchool(filer,)
        if query_range == '学院':
            filer = {}
            queryForInstitution(filer,)
        if query_range == '教师':
            filer ={}
            queryForTeacher(filer)




