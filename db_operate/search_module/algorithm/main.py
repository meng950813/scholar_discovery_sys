import os,re,time
import pickle
import jieba
import jieba.posseg as pseg

from search_module.algorithm.lda import LdaTest
from search_module.algorithm.base import dbs
from search_module.algorithm.uploadToWeb import upload
from sklearn.feature_extraction.text import TfidfVectorizer

def loadData(version, code, core=False):
    '''
    将某一学科的教师的id和对应的学科代码 以及这些教师id对应的论文信息存到文件中
    :param version:学科名字
    :param code:学科代码
    :param core:
    :return:
    '''
    print("加载数据")
    try:
        dic = pickle.load(open('data/dic', 'rb'))
    except:
        dic={}
    dic[version] = code
    pickle.dump(dic, open('data/dic', 'wb'))
    # sql = 'SELECT id FROM `teacher_dis_code` where discipline_code=%s' #取属于某一学科的教师id
    sql = 'SELECT teacher_id FROM `teacher_discipline` where discipline_id = %s' #取属于某一学科的教师id

    if not core:  #是否是核心期刊
        # papersql = "select id,`name`,abstract,keyword from paper2 where  author_id=%s and checkOrg=1"
        papersql = "select id, `name`, abstract, keyword from paper where  author_id=%s and checkOrg=1"
    else:
        # papersql="select id,`name`,abstract,keyword from paper2 where core_journal=1 and author_id=%s and checkOrg=1"
        papersql="select id,`name`,abstract,keyword from paper where core_journal=1 and author_id=%s and checkOrg=1"
    # engsql = "select cn from englist_title where id=%s"
    teacher = dbs.getDics(sql, (code,))  #code学科代码
    try:
        os.makedirs("data/"+version)
    except:
        pass
    file = open("data/" + version + "/" + code+".txt", 'w', encoding='utf8')
    num1, num2, num3 = 0, 0, 0
    for t in teacher:
        id = t["teacher_id"]
        papers = dbs.getDics(papersql, (id,)) #id作者的id
        num1 += len(papers)
        paper = []
        keyWord = []
        for p in papers:
            pid = p["id"]
            temp = {"id": pid, "paper": p["name"] + ',' + p['abstract'], "keyWord":p["keyword"].split(',')}
            #将作者的id， 论文的名字， 论文的摘要， 论文的关键词写入文件， 文件名是学科的名字
            file.write(str(temp) + '\n')

    file.close()
    print("paper:", num1)
    print("eng:", num2)
    print("teacher:", num3)

    return num1


def fenci(version, code):
    '''
    将存在code.txt文件中的某学科对应的论文信息提取出来，进行分词,
    在这个过程中，要将位于停用词词表中的词剔除掉，剔除后将词数据写入到code_fenci.txt中
    并记录剔除后的词在最终的词典中出现的个数，存放在code_dic_temp.txt中
    :param version: 学科名字
    :param code:学科代码
    :return:
    '''
    print("分词")
    stopwords = [line.strip() for line in open('stopwords.txt', encoding='utf-8').readlines()]
    fill = ['vn', 'n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf',
            'nt', 'nz', 'nl', 'ng']
    # fill = ['n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf',
    #         'nt', 'nz', 'nl', 'ng']
    jieba.load_userdict('userdict.txt')
    file = open("data/" + version+'/' + code + ".txt", 'r', encoding='utf8') #读取某学科下的论文信息：作者的id， 论文的名字， 论文的摘要， 论文的关键词写入文件， 文件名是学科的名字
    file2 = open("data/" + version+'/' + code + "_fenci.txt", 'w', encoding='utf8') #分词后要写入的文件
    dic = {}
    for line in file.readlines():
        item = eval(line)
        seg_list = pseg.cut(item["paper"]) #paper 名字
        words = []
        for word, flag in seg_list:
            if flag in fill and word not in stopwords:
                words.append(word)
        for w in words:
            if w not in dic:
                dic[w] = 0
            dic[w] += 1  #总的词典，记录每个词在所有文中出现的次数
        words.extend(item['keyWord'])
        temp = {"id": item["id"], "fenci": " ".join(words)} #教师id，  分词后的论文信息
        file2.write(str(temp)+"\n")

    file2.close()
    c1 = sorted(dic.items(), key=lambda x: x[1], reverse=True)

    file3 = open("data/"+version+'/' + code + "_dic_temp.txt", 'w', encoding='utf8')  #？？？
    for d in c1:
        file3.write(str(d[0])+":"+str(d[1])+"\n")
    file3.close()


def deleteStopWord(version, code):
    '''
    使用stop_word_4.txt 来对上面的code_fenci.txt进行再一次停用词的去除，并将重新去除的后的词写入到code_fenci_stopword.txt中
    :param version: 学科名字
    :param code: 学科代码
    :return:
    '''
    print("删除停用词")
    file2 = open("data/" + version + '/' + code + "_fenci.txt", 'r', encoding='utf8') #分词后的文件
    file3 = open("data/" + version + '/' + code + "_fenci_stopword.txt", 'w', encoding='utf8')
    stopword1 = [line.strip() for line in open('stop/stop_word_4.txt', encoding='utf-8').readlines()]
    stopwords = [i.split(':')[0] for i in stopword1]
    dic = {}
    for line in file2.readlines():
        item = eval(line)
        words = item["fenci"].split(" ") #每篇论文分词后的词表
        newWords = [] #去除停用词后的新词表
        for w in words:
            if w not in stopwords:
                newWords.append(w)
        temp = {"id": item["id"], "fenci": " ".join(newWords)}
        file3.write(str(temp) + "\n")
        for w in newWords:
            if w not in dic:
                dic[w] = 0
            dic[w] += 1
    file4 = open("data/" + version + '/' + code + "_dic_stopword.txt", 'w', encoding='utf8')
    c1 = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    for d in c1:
        file4.write(str(d[0]) + ":" + str(d[1]) + "\n")
    file4.close()
    file3.close()

def replaceAll(doubleWords, words):
    '''

    :param doubleWords:
    :param words:
    :return:
    '''
    for w in doubleWords:
        replaceOne(w, words)

def replaceOne(doubleWord, words, start):
    '''

    :param doubleWord:近义词表中的某一个相邻词
    :param words:去除停用词后的文档词表
    :param start:
    :return:
    '''
    ws = doubleWord.split(" ") #重新组成相邻词的列表 [前一个词，  后一个词]
    try:
        index = words[start:].index(ws[0]) + start #找到前一个词在文档词表中的位置
    except:
        index = -1 #没有的话返回-1
    if index >= 0:
        if index+1 < len(words) and words[index + 1] == ws[1]: #如果找到的索引之后的一个词与近义词表中的后一个词相同，则用 ws[0]+ws[1] 替换
            del words[index]
            del words[index]
            words.insert(index, ws[0]+ws[1])
        replaceOne(doubleWord, words, index+1)

def findDouble(version, code):
    '''
    没用到
    :param version:
    :param code:
    :return:
    '''
    file3 = open("data/" + version + '/' + code + "_fenci_stopword.txt", 'r', encoding='utf8')
    double_word = {}
    for line in file3.readlines():
        item = eval(line)

        word = item["fenci"].split(' ')
        for i in range(len(word)-1):
            if word[i] == word[i+1]: #相邻词相等
                continue
            w = word[i]+"__"+word[i+1] #相邻词不等
            if w not in double_word:
                double_word[w] = 0  #将不等的相邻词相连

            double_word[w] += 1 #并计算这些相邻词的在文章词列表中重复的次数，加入到字典中

    file4 = open("data/" + version + '/' + code + "_dic_doubleWord.txt", 'w', encoding='utf8')
    c1 = sorted(double_word.items(), key=lambda x: x[1], reverse=True) # 按照字典的value倒序排序
    for d in c1:
        if d[1] < 5:
            break
        file4.write(str(d[0]) + ":" + str(d[1]) + "\n") #将重复数大于5的写入到文件中
    file4.close()

def countDouble(version, code):
    '''
    没用到
    :param version:
    :param code:
    :return:
    '''
    file = open("data/" + version + '/' + code + ".txt", 'r', encoding='utf8')
    file4 = open("data/" + version + '/' + code + "_dic_doubleWord.txt", 'r', encoding='utf8') #相邻词表
    file5 = open("data/" + version + '/' + code + "_dic_doubleWord_pass.txt", 'w', encoding='utf8')
    all_pass = "".join([line for line in file.readlines()]) #使用最初始的，未分词时的文档对应的的文件
    for line in file4.readlines():
        words = line.split(":")[0].split("__")
        p1 = words[0] + r"[\u4e00-\u9fa5]{0,5}" + words[1]  # 相邻词分开，并找出相邻词之间存在中文，且存在的字数在[0, 5]之间
        try:
            pattern1 = re.compile(p1)
            word = pattern1.findall(all_pass) #找出所有满足上述模式的所有词
            if len(word) > 10:
                file5.write("__".join(words) + ":" + ",".join(word) + "\n") #将符合条件的长词对应的 相邻词写入到文件中
        except:
            print(line)

    file5.close()

def mergeDouble(version, code):
    '''

    :param version:
    :param code:
    :return:
    '''
    double = []
    try:
        file = open("Synonym/" + code + "_doubleWord.txt", 'r', encoding="utf8") #近义词表
        for line in file.readlines(): #将近义词表中的内容组成这样的字符串  word[0]+" "+word[1]  写入到列表
            word = line.split(":")[0].split("__")
            double.append(word[0]+" "+word[1])
    except:
        print("为定义分词错误词典")
    file2 = open("data/" + version + '/' + code + "_fenci_stopword.txt", 'r', encoding='utf8') #{'id': 353392, 'fenci': '柴达木盆地 北 生物气 田际 气层  气面 中央 部位 级别 气层 气层 潜力 气层 分布状况 优化调整 部署方案 产能评价 单砂体 层次分析法 柴达木盆地'}
    file3 = open("data/" + version + '/' + code + "_fenci_double_merge.txt", 'w', encoding='utf8') #{'id': 353392, 'fenci': '柴达木盆地 北 生物 气层 部位 气面 中央 部位 级别 气层 气层 潜力 气层 分布状况 优化调整 部署方案 产能评价 单砂体 层次分析法 柴达木盆地'}

    dic = {}

    for line in file2.readlines(): #去除停用词后的文档词表：{'fenci': '柴达木盆地 北 生物气 田 砂体 分类评价 柴达木盆地 北 气田 砂泥 薄互层 滩坝相 高孔 细粒 储层特征 气层 评价目标 内涵 孔隙度 渗透率 含气饱和度 有效厚度 泥质 体积分数 地质参数 厘清调整 部署方案 产能评价 单砂体 层次分析法 柴达木盆地', 'id': 353392}
        item = eval(line)
        words = item["fenci"].split(" ") #word:[柴达木盆地 北 生物气 田 砂体 分类评价 柴达木盆地 北 气田 砂泥 薄互层 滩坝相 高孔 细粒 储层特征 气层 评价目标 内涵 ]
        for d in double: #double：[word[0]+" "+word[1], ....]
            replaceOne(d, words, 0)
        temp = {"id": item["id"], "fenci": " ".join(words)}
        for w in words:
            if w not in dic:
                dic[w] = 0
            dic[w] += 1
        file3.write(str(temp) + "\n")
    file3.close()
    file4 = open("data/" + version + '/' + code + "_dic_double_merge.txt", 'w', encoding='utf8')
    c1 = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    for d in c1:
        file4.write(str(d[0]) + ":" + str(d[1]) + "\n")
    file4.close()

def findSynonym(version, code):
    '''
    找到同义词
    :param version:
    :param code:
    :return:
    '''
    file2 = open("data/" + version + '/' + code + "_fenci_double_merge.txt", 'r', encoding='utf8')  #{'fenci': '柴达木盆地 北 生物气 田 砂体 分类评价 柴达木盆地   气层 分布状况 优化调整 部署方案 产能评价 单砂体 层次分析法 柴达木盆地', 'id': 353392}
    id = []
    paper = []
    for line in file2.readlines():
        item = eval(line)
        id.append(item['id'])
        paper.append(item["fenci"])
    vec = TfidfVectorizer(ngram_range=(1, 2),min_df=5, max_df=0.9)
    temp = vec.fit_transform(paper)
    word = vec.get_feature_names() #获取词袋模型中的所有词语
    tfidf_dic = word
    doubleWord = []
    for k in tfidf_dic:
        ws = k.split(" ")
        if len(ws) == 2 and ws[0] != ws[1] :
            doubleWord.append(k)
    print("二元数量:"+str(len(doubleWord)))
    file5 = open("data/" + version + '/' + code + "_synonymWord.txt", 'w', encoding='utf8')
    for line in doubleWord:
        words = line.split(" ")
        if words[0].find(words[1]) >= 0:
            file5.write(words[0] + ":" + words[1] + "\n")
        elif words[1].find(words[0]) >= 0:
            file5.write(words[1] + ":" + words[0] + "\n")
    file5.close()

def mergeSynonym(version, code):
    synonym = {}
    try:
        file = open("Synonym/" + code + "_synonymWord.txt", 'r', encoding="utf8")

        for line in file.readlines():
            word=line.strip().split(":")
            synonym[word[0]] = word[1]
    except:
        print("请建立同义词典")
    file2 = open("data/" + version + '/' + code + "_fenci_double_merge.txt", 'r', encoding='utf8')
    file3 = open("data/" + version + '/' + code + "_fenci_synonym_merge.txt", 'w', encoding='utf8')
    dic = {}

    for line in file2.readlines():
        item=eval(line)
        words=item["fenci"].split(" ")
        # if i<17064:
        #     continue
        for i in range(len(words)):
            if words[i] in synonym:
                words[i] = synonym[words[i]]
        temp = {"id": item["id"], "fenci": " ".join(words)}
        for w in words:
            if w not in dic:
                dic[w] = 0
            dic[w] += 1
        file3.write(str(temp) + "\n")
    file3.close()
    file4 = open("data/" + version + '/' + code + "_dic_synonym_merge.txt", 'w', encoding='utf8')
    c1 = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    for d in c1:
        file4.write(str(d[0]) + ":" + str(d[1]) + "\n")
    file4.close()

def computerTfIdf(version,code):
    print(" 计算 tfidf ")
    file2 = open("data/" + version + '/' + code + "_fenci_synonym_merge.txt", 'r', encoding='utf8') #取合并同义词后的词典
    #{'fenci': '柴达木盆地 北 生物气 田 砂体 分类评价 柴达木盆地 北 气田 砂泥 薄互层 滩坝相 高孔 细粒 储层特征 气层 评价目标 内涵 孔隙度 渗透率 含气饱和度 有效厚度 泥质 体积分数 地质参数 厘清 层次结构模型 单砂体 基本单元 生产压差 无阻流量 层次分析法 现场 生产实际 气层 气层 分布特征 气井产能 气层 含气 储层条件 原始地层压力 气层 气层 高产 级别 气层 气层 气层 气层 级别 高产 级别 气层 部位 气面 中央 部位 级别 气层 气层 潜力 气层 分布状况 优化调整 部署方案 产能评价 单砂体 层次分析法 柴达木盆地', 'id': 353392}
    id = []
    paper = []
    for line in file2.readlines():
        item = eval(line)
        id.append(item['id'])
        paper.append(item["fenci"])
    vec = TfidfVectorizer(ngram_range=(1, 1), min_df=5, max_df=0.6)
    '''
     TfidfVectorizer可以把原始文本转化为tf-idf的特征矩阵，从而为后续的文本相似度计算，主题模型(如LSI)，文本搜索排序等一系列应用奠定基础。
    ngram_range: tuple(min_n, max_n)
    要提取的n-gram的n-values的下限和上限范围，在min_n <= n <= max_n区间的n的全部值
    '''
    temp = vec.fit_transform(paper)

    word = vec.get_feature_names() #获取词袋模型中的所有词语  Array mapping from feature integer indices to feature name
    tfidf_dic = word
    file3 = open("data/" + version + '/' + code + "_fenci_tdidf.txt", 'w', encoding='utf8')
    dic = {}
    for index, p in enumerate(paper):
        words = p.split(" ")
        p_temp = []
        for w in words:
            if w in tfidf_dic: #将在词典同时又在词袋中的所有词取出，写到文件 _fenci_tdidf 中
                p_temp.append(w)
        temp = {"id": id[index], "fenci": " ".join(p_temp)}
        file3.write(str(temp) + "\n")
        for w in p_temp:
            if w not in dic:
                dic[w] = 0
            dic[w] += 1
    file4 = open("data/" + version + '/' + code + "_dic_tdidf.txt", 'w', encoding='utf8')
    c1 = sorted(dic.items(), key=lambda x: x[1], reverse=True)

    for d in c1:
        file4.write(str(d[0]) + ":" + str(d[1]) + "\n")
    file4.close()
    file3.close()

def merge(version, code):

    print("去重")
    file3 = open("data/" + version + '/' + code + "_fenci_tdidf.txt", 'r', encoding='utf8') #{'fenci': '全厂断电 安全壳 研究 安全壳 安全壳 事故 堆芯 碎片 安全壳 全厂断电', 'id': 198216}
    file5 = open("data/" + version + '/' + code + "_fenci_merge.txt", 'w', encoding='utf8') #{'fenci': '内涵 现场 分布特征 部位 中央 潜力', 'id': 353392}
    dic={}
    for line in file3.readlines():
        item = eval(line)
        word=item["fenci"].split(' ')
        new_word=[]
        for w in word:
            if w not in new_word:
                new_word.append(w)
        temp = {"id": item["id"], "fenci": " ".join(new_word)}
        file5.write(str(temp) + "\n")
        for w in new_word:
            if w not in dic:
                dic[w] = 0
            dic[w] += 1
    file5.close()
    file4 = open("data/" + version + '/' + code + "_dic_merge.txt", 'w', encoding='utf8')
    c1 = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    for d in c1:
        file4.write(str(d[0]) + ":" + str(d[1]) + "\n")
    file4.close()

def check(version,code):
    file2 = open("data/" + version + '/' + code + "_fenci.txt", 'r', encoding='utf8')
    word="图像"
    num=0
    for line in file2.readlines():
        item = eval(line)
        words = []
        words.extend(item['fenci'].split(' '))
        if word in words:
            num+=1
    print(num)

class Param:
    def __init__(self):
        print("-----")
        # sql = "SELECT b.name,a.discipline_code from (SELECT discipline_code FROM `teacher_dis_code`  GROUP BY discipline_code) a LEFT JOIN discipline_new b on a.discipline_code=b.code "
        sql = "SELECT b.NAME, a.discipline_id from (SELECT discipline_id FROM `teacher_discipline`  GROUP BY discipline_id) a LEFT JOIN es_discipline b on a.discipline_id=b.CODE "
        discipline = dbs.getDics(sql)  #[{'name':**学科，"discipline_code": **学科代码} ,  {},  {} ,  ]
        print(discipline)
        # 是否是核心期刊
        core = [False]
        # 是否去重
        file = ["tdidf"] #????
        self.used={}
        self.dic=[]
        # print(discipline)
        for d in discipline:
            # print(d)
            if d['discipline_id'][0:2] == "08":
                for c in core:
                    for f in file:
                        version = d["NAME"] #学科名字
                        # if c:
                        #     version += "-core-stopword4"
                        # else:
                        #     version += "-all-stopword4"
                        # version += "-"+f+"-5-0.6-" + d["discipline_code"]
                        version += "-" + d["discipline_id"] #学科名字-学科代码
                        self.dic.append([c, f, d["discipline_id"], version])
        print(self.dic)

    def getParam(self):
        for t in self.dic:
            if str(t) in self.used:
                continue
            else:
                self.used[str(t)] = 1
                return t
        # return None, None, None, None
        return False



if __name__=="__main__":
    P = Param()
    # P = [([False], "tdidf", "0805", "材料科学与工程-0805"),
    #      ([False], "tdidf", "0811", "控制科学与工程-0811"),
    #      ([False], "tdidf", "0835", "软件工程-0835"),
    #      ([False], "tdidf", "0810", "信息与通信工程-0810"),
    #      ([False], "tdidf", "0812", "计算机科学与技术-0812"), ]
    # P = [([False], "tdidf", "0805", "材料科学与工程-0805"),
    #      ([False], "tdidf", "0811", "控制科学与工程-0811"),
    #      ([False], "tdidf", "0835", "软件工程-0835"),
    #      ([False], "tdidf", "0810", "信息与通信工程-0810"),
    #       ]
    # upload()

    # print(P)
    while P.getParam() is not False:
            try:
                core, file, code, version = P.getParam()  # 是否是核心期刊， [tfidf]， 学科代码， 学科名字
                # print(P.getParam())
            except:
                print("error   ", P.getParam())
                break
            if code is not None:
                time1 = time.time()
                print("version:"+version)
                print("code:" + code)
                num=loadData(version, code, core)
                if num < 100:
                    print("code:"+str(code)+" num:"+str(num))
                    continue
                fenci(version, code)
                deleteStopWord(version, code)
                findDouble(version, code) #
                countDouble(version, code) #
                mergeDouble(version, code)
                findSynonym(version, code) #
                mergeSynonym(version, code)
                computerTfIdf(version, code)
                merge(version, code) #
                lda = LdaTest(version, code, file)
                topic=[i for i in range(10, 30, 2)]
                for t in topic:
                    lda.train(t)
                    # break
                    # upload()
                    # continue

                time2 = time.time()
                print('总的模型训练用时：', time2 - time1)
                # upload()
                with open("record.txt", 'w') as f:
                    f.write(version + "   is done\n")
            else:
                break

    upload()
    # check(version, code)

