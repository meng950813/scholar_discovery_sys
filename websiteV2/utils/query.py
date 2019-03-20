# coding=utf-8
from __future__ import division
import pickle
import time, jieba, math
import jieba.posseg as pseg
import os


class Subject:
    """
    计算教师关于被搜索内容的语言模型得分，LDA评分，pagerank评分，最后得出教师的评分
    """

    def __init__(self, sub, id_name, path):
        '''
        初始化Subject对象
        :param sub:所计算的学科代码及主题数
        :param id_name: 教师信息
        '''
        # ({"code": 学科代码, "k": 主题数}
        self.sub = sub
        # self.id_name 字典
        self.id_name = id_name
        code = self.sub['code']
        k = self.sub['k']
        print("load:" + code)
        self.basepath = path
        self.path = os.path.join(path, 'querydata', code, 'k' + str(k))
        # 词的索引 wordIndex
        self.lmindex = pickle.load(open(os.path.join(self.path, 'wordIndex'),'rb'))
        # word和topic的关系
        self.ldaword = pickle.load(open(os.path.join(self.path, 'wordToTopic'), 'rb'))
        # 教师和topic的关系
        self.ldaexp = pickle.load(open(os.path.join(self.path, 'teacherTopic'), 'rb'))
        # 教师PageRank评分
        self.pagerank = pickle.load(open(os.path.join(self.path, 'teacherRank'), 'rb'))
        self.cal = 0.9

    def cal_lda_one_word(self, word, teacher_id):
        '''
        计算教师关于搜索内容中某词的lda得分
        :param word:搜索内容可能有多个词，依次处理，这里的word是搜索内容中的一个词
        :param teacher_id:用于限制、筛选需要排名的教师，可以为空
        :return:res type:dict 教师id及对上述word的lda得分
        '''
        """计算单个词的专家lda得分"""
        ld = self.ldaword.get(word)
        # sort      {topic_id1:value,...} 筛选出value>1.0e-06 value降序排序
        sort = {}
        # res       {teacher_id1:value,...}
        res = {}
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
            # ldaexp  教师和topic的关系
            for m in self.ldaexp.keys():
                # m是teacher_id
                if j in self.ldaexp[m]:
                    # id为m的老师对某主题的值乘这个主题对这个词的值
                    if m in res:
                        res[m] += self.ldaexp[m][j] * sort[j]
                    else:
                        res[m] = self.ldaexp[m][j] * sort[j]
        return res

    def cal_one_word(self, word, teacher_id):
        '''
        计算教师关于搜索内容中的一个词的语言模型得分
        :param word:搜索内容可能有多个词，依次处理，这里的word是搜索内容中的一个词
        :param teacher_id:用于限制、筛选需要排名的教师，可以为空
        :return:res type:dict 返回教师ID及其对上述word的得分
        '''
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
        return res

    def cal_rank(self, res, lda, cof):
        rank = {}
        exp_list = [r for wd in res.keys() for r in res[wd]]
        exp_list = list(set(exp_list))
        exp_list_lda = [r for wd in lda.keys() for r in lda[wd]]
        exp_list_lda = list(set(exp_list_lda))
        exp_list.extend(exp_list_lda)
        if 'col' in exp_list:
            exp_list.remove('col')
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
                    rank[r] *= 1e-6
            for wd in lda:
                if wd not in res:
                    rank[r] *= lda[wd][r]
                else:
                    rank[r] *= 1e-6
            if self.pagerank.get(r):
                rank[r] *= self.pagerank[r] * self.id_name[r]["total"]
        return rank

    def do_query(self, words, teacher_id):
        '''
        进行搜索操作，并返回搜索结果
        :param words:搜索内容
        :param teacher_id: 用于限制、筛选需要排名的教师
        :return: result 教师id及关于搜索内容的评分，降序排序
        '''
        temp_res = {}
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
        return result


class Query:
    '''
    对输入内容进行搜索，并打印及返回搜索结果
    '''

    def __init__(self, subs, path):
        '''
        初始化Query对象
        :param subs:学科代码及主题数
        '''
        # [{"code": '01', "k": 46}, {"code": '02', "k": 98}]
        self.subs = subs
        # {teacher_id1:{id:xx,name:xxx},...}
        self.id_name = pickle.load(open(os.path.join(path,'querydata','teacherName'), 'rb'))
        self.institution_info = pickle.load(open(os.path.join(path,'querydata','institutionName'), 'rb'))
        self.school_info =pickle.load(open(os.path.join(path,'querydata','SchoolName'), 'rb'))
        # self.Subject {code1:Subject(sub1),sode2:Subject2(sub2)}

        self.Subject = {sub['code']: Subject(sub, self.id_name,path) for sub in self.subs}
        self.stop = []
        stopword = [line.strip() for line in open(os.path.join(path,'querydata','stopwords.txt'), encoding='utf-8').readlines()]
        stopword1 = [line.strip() for line in open(os.path.join(path,'querydata','stop_word_4.txt'), encoding='utf-8').readlines()]
        stopwords = [i.split(':')[0] for i in stopword1]
        self.stop.extend(stopword)
        self.stop.extend(stopwords)
        self.fill = ['vn', 'n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf',
                     'nt', 'nz', 'nl', 'ng']
        jieba.load_userdict(os.path.join(path,'querydata','userdict.txt'))

    def prints(self, result):
        '''
        搜索教师后，打印教师信息
        :param result:进行搜索后返回的信息，包括教师id及对搜索内容的得分，降序排序
        :return:
        '''
        query_result = []
        for code in result:
            size = len(result[code])
            if size == 0:
                continue
            # 教师个数
            print("学科:%s,有关教师个数：%d" % (code, size))
            teacher = result[code]
            for t in teacher:
                # 教师名字：（id:权重)
                # print(self.id_name[t[0]]["NAME"]+":"+str(t))
                query_result.append((self.id_name[t[0]]["NAME"], str(t[1])))
            # print()
        return query_result

    def prints_for_institution(self, result, school=None):
        '''
        将搜索到的老师转化为学院信息，并打印
        :param result:进行搜索后返回的老师信息，包括教师id及对搜索内容的得分，降序排序
        :return:院系的搜索结果，学校名+学院名
        '''
        # 学院信息
        institution_info = {}
        for code in result:
            # 学科代码code下的教师权值信息
            teacher_info_s = result[code]

            for teacher_info in teacher_info_s:
                # 教师id
                teacher_id = teacher_info[0]
                # 学院id
                institution_id = self.id_name[teacher_id]['INSTITUTION_ID']
                # 将老师的权值归入老师对应的学院中，以计算学院信息
                if institution_id in institution_info:
                    institution_info[institution_id] += teacher_info[1]
                else:
                    institution_info[institution_id] = teacher_info[1]
        # 学院按权值从大到小排序
        institution_rank = dict(sorted(institution_info.items(), key=lambda x: x[1], reverse=True))
        # 返回学院的学校名+学院名+学院权值
        query_result = []
        if school != None:
            for institution_id in institution_rank:
                # 学院所属的学校名字
                schoolName = self.institution_info[institution_id]['SCHOOL_NAME']
                # 打印所查学校的院系
                if schoolName == school:
                    query_result.append((schoolName, self.institution_info[institution_id]['NAME'],institution_rank[institution_id]))
        else:
            for institution_id in institution_rank:
                schoolName = self.institution_info[institution_id]['SCHOOL_NAME']
                # print(schoolName + self.institution_info[institution_id]['NAME'] + str(institution_rank[institution_id]))
                query_result.append((schoolName, self.institution_info[institution_id]['NAME'],institution_rank[institution_id]))
        return query_result

    def prints_for_school(self, result, city=None):
        '''
        将搜索到的老师转化为学校信息，打印并返回
        :param result: 搜索得到的结果，每个学科代码下的教师id和评分
        :return:学校的搜索结果，学校名+省+城市名+评分
        '''
        # 学校信息
        school_info = {}
        for code in result:
            # 学科代码code下的教师权值信息
            teacher_info_s = result[code]
            for teacher_info in teacher_info_s:
                # 教师id
                teacher_id = teacher_info[0]
                # 学院id
                school_id = self.id_name[teacher_id]['SCHOOL_ID']
                # 将老师的权值归入老师对应的学院中，以计算学院信息
                if school_id in school_info:
                    school_info[school_id] += teacher_info[1]
                else:
                    school_info[school_id] = teacher_info[1]
        # 学院按权值从大到小排序
        school_rank = dict(sorted(school_info.items(), key=lambda x: x[1], reverse=True))
        # 根据是否有city限制进行操作
        # 返回 学校名+省份+市+得分
        query_result = []
        if city == None:
            for school_id in school_rank:
                school_infomation = self.school_info[school_id]
                query_result.append(
                    {'school_name': school_infomation['NAME'], 'province': school_infomation['PROVINCE'],
                     'city': school_infomation['CITY'], 'score': school_rank[school_id]})
        else:
            for school_id in school_rank:
                city_name = self.school_info[school_id]['CITY']
                if city_name == city:
                    school_infomation = self.school_info[school_id]
                    query_result.append(
                        {'school_name': school_infomation['NAME'], 'province': school_infomation['PROVINCE'],
                         'city': school_infomation['CITY'], 'score': school_rank[school_id]})
        return query_result

    def prints_for_teacher(self, result):
        '''
        根据搜索到的老师信息得到老师所在的学院名，学校名，并打印
        :param result:进行搜索后返回的老师信息，包括老师姓名及老师学院，以老师得分降序排序
        :return:院系的搜索结果，老师+学院名+学校名
        '''

        teacher_info = []
        for code in result:
            # 学科代码code下的教师权值信息
            teacher_info_s = result[code]

            for teacher_info1 in teacher_info_s:
                # 教师id
                teacher_id = teacher_info1[0]
                # 学院id
                institution_id = self.id_name[teacher_id]['INSTITUTION_ID']

                teacher_info.append({'teacher_name': self.id_name[teacher_id]["NAME"],'institution_name': self.institution_info[institution_id]['NAME'],'school_name':self.institution_info[institution_id]['SCHOOL_NAME']})

        return teacher_info



    def do_query(self, text, filer):
        '''

        :param text:输入的搜索文本
        :param filer:过滤器
        :return: 老师id和得分
        '''
        # 将输入内容进行分词
        # text = jieba.cut(text,cut_all=True)
        # texts = ''
        # for word in text:
        #     texts += word+' '
        seg_list = pseg.cut(text)
        words = []
        for word, flag in seg_list:
            if flag in self.fill and word not in self.stop:
                # 是名词且不是停用词，将其纳入搜索列表
                words.append(word)
        if "school" in filer and len(filer["school"]) > 0:
            teacher_id = {t for t in self.id_name if self.id_name[t]['school_id'] in filer['school']}
        else:
            teacher_id = None

        # 筛选符合院系信息的老师
        if "institution" in filer and filer['institution'] != None and len(filer['institution']) > 0:
            teacher_id = {t for t in self.id_name if str(self.id_name[t]['INSTITUTION_ID']) in filer['institution']}
        else:
            teacher_id = None

        if "name" in filer and len(filer["name"]) > 0:
            if teacher_id:
                teacher_id = {t for t in teacher_id if self.id_name[t]['name'].find(filer["name"]) >= 0}
            else:
                teacher_id = {t for t in self.id_name if self.id_name[t]['name'].find(filer["name"]) >= 0}
        result = {}
        # teacher_id dict None
        for sub in self.Subject:
            if "code" in filer and len(filer['code']) > 0 and sub not in filer['code']:
                continue
            else:
                # self.Subject_for_teacher {code1:Subject_for_teacher(sub1),sode2:Subject_for_teacher2(sub2)}
                result[sub] = self.Subject[sub].do_query(words, teacher_id)
        # result {code:[teacher_id:value,].,code:[],...}
        return result

def queryForTeacher(words, institution_id='1526'):
    '''
    搜索教师
    :param words:搜索内容
    :param institution_id: 搜索教师时，该教师被限制的学院ID
    :return: 搜索结果 学院 人
    '''
    filer = {}
    filer['institution'] = institution_id
    result = query.do_query(words, filer)
    result_info = query.prints(result)
    print(result_info)
    return result_info


subject = [
    {"code": '0801', "k": 16},
    {"code": '0802', "k": 10}, {"code": '0803', "k": 10}, {"code": '0804', "k": 12},
    {"code": '0805', "k": 10}, {"code": '0806', "k": 12}, {"code": '0807', "k": 14},
    {"code": '0808', "k": 12}, {"code": '0809', "k": 18}, {"code": '080901', "k": 16}, {"code": '0810', "k": 18},
    {"code": '0811', "k": 12}, {"code": '081101', "k": 28}, {"code": '0812', "k": 10}, {"code": '081202', "k": 12},
    {"code": '0814', "k": 20}, {"code": '0815', "k": 12},
    {"code": '0817', "k": 10}, {"code": '0818', "k": 14},
    {"code": '0822', "k": 10}, {"code": '0823', "k": 10},
    {"code": '0824', "k": 12}, {"code": '0825', "k": 20}, {"code": '0826', "k": 10},
    {"code": '0827', "k": 10}, {"code": '0828', "k": 10},
    {"code": '0830', "k": 18}, {"code": '0831', "k": 10}, {"code": '0832', "k": 12}]


query = Query(subject, path = os.path.join(os.getcwd(),'static'))



def query_all(range, words, limit=None):
    '''
    用于搜索的接口函数
    :param query_range:查询范围
    :param words: 搜索的关键词
    :param limit 搜索限制，如搜索学校时限制是市，搜索学院时，限制是学校，可以为空，为空为全国范围搜索
    :return:result_info 搜索结果，如学校是 学校名，省，城市名，评分的信息
    '''
    query_range = range
    if query_range == '省':
        pass
    if query_range == '市':
        pass
    if query_range == '学校':
        filer = {}
        result = query.do_query(words, filer)
        result_info = query.prints_for_school(result, limit)
        return result_info
    if query_range == '学院':
        filer = {}
        result = query.do_query(words, filer)
        result_info = query.prints_for_institution(result, limit)
        return result_info
    if query_range == '老师':
        filer = {}
        result = query.do_query(words, filer)
        result_info = query.prints_for_teacher(result)
        return result_info
    if query_range == '教师':
        filer = {}
        filer['institution'] = limit
        result = query.do_query(words, filer)
        result_info = query.prints(result)
        return result_info



if __name__ == '__main__':
    print(query_all("老师","计算机"))
