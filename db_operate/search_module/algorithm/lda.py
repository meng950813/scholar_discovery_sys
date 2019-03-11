
import time, os
import gensim
import pyLDAvis.gensim
from gensim import corpora
class LdaTest:

    def __init__(self, version, name, file="merge"):
        self.version = "data/"+version
        self.file = file  #  file = ["tdidf"]
        try:
            os.makedirs(self.version)
        except:
            pass
        try:
            os.makedirs(self.version + "/view")
        except:
            pass
        self.name = name #name : code

    def strToMap(self, s):
        dic={}
        list=s.split(' + ')
        for l in list:
            v = l.split('*')
            key = v[1][1:-1]
            dic[key] = float(v[0])
        return dic

    def train(self, k, iterations=6000):
        print( self.version, "  ", self.name, "   ", self.file)
        file = open(self.version+'/' + self.name + "_fenci_" + self.file + ".txt", 'r', encoding='utf8')
        DocWord = []
        for line in file.readlines():
            item = eval(line) # 将字符串对象转换为能够具体的对象
            words = item["fenci"].split(" ")
            DocWord.append(words)
        file.close()
        dictionary = corpora.Dictionary(DocWord) #建立词典
        corpus = [dictionary.doc2bow(text) for text in DocWord] #建立每个词出现的频率
        num_topics = k
        file2 = open(self.version + '/' + self.name + "_dic_" + self.file + ".txt", 'r', encoding='utf8')
        num_words = int(len(file2.readlines())/3) #？？？ dic_tfidf.txt中词的数量 / 3  num_words是被用于确定每个主题的词数而计算的
        iterations = iterations
        # print('name:'+self.name+'总数为%d，即将分为主题数%d个，关键字%d个......' % (len(corpus),num_topics,num_words))
        time1 = time.time()
        ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, iterations=iterations)
        result = ldamodel.print_topics(num_topics=num_topics, num_words=num_words) #Get the most significant topics (alias for `show_topics()` method)
        time2 = time.time()
        print('模型训练用时：', time2 - time1)
        try:
            os.makedirs(self.version+"/k" + str(num_topics) + "/")
        except:
            pass
        vis = pyLDAvis.gensim.prepare(ldamodel, corpus, dictionary)
        index = open(self.version + "/k" + str(num_topics) + "/" + self.name + "_index.txt", 'w', encoding='utf8')

        print("vis[6]:   ", vis[6])
        index.write(str(vis[6])+'\n')
        index.close()

        pyLDAvis.save_html(vis, self.version+'/view/k'+str(num_topics)+'.html') #将vis中的内容生成为HTML的可视化文件
        # pyLDAvis.save_json(vis, self.version+'/view/k'+str(num_topics)+'.json')
        # print("vis  :", vis)
        # pyLDAvis.show(vis, open_browser=False)
        file1 = open(self.version+"/k"+str(num_topics)+"/" + self.name + "_topic.txt", 'w', encoding='utf8') # 将主题对应的词分布写进文件 code_topic.txt
        for r in result:
            d = self.strToMap(r[1])
            print("r[1]:  d[] ", str(r[0])+":"+str(d)+'\n')
            file1.write(str(r[0])+":"+str(d)+'\n')
        file1.close()

        file2 = open(self.version+"/k"+str(num_topics)+"/" + self.name + "_teacher_topic.txt", 'w', encoding='utf8')
        doc_lda = ldamodel[corpus]
        print("doc_lda:  ", doc_lda)
        for n in range(len(doc_lda)):
            Topic = doc_lda[n]
            print("学科代码为", self.version, "的主题数为", k, "时的数据训练完成")
            c1 = sorted(Topic, key=lambda x: x[1], reverse=True)
            file2.write(str(c1)+'\n') #将教师（文章）对应的主题分布写入到文件
        file2.close()
