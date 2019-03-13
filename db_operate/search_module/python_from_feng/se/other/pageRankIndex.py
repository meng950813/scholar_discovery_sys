# coding=utf-8
import pickle
import networkx as nx
import matplotlib.pyplot as plt
from search_module.python_from_feng.se.config import root

def makeIndex(code, k):
    '''

    :param code:
    :param k:
    :return:
    '''
    path = root+'/' + code + '/k' + str(k)
    teacherTopic = pickle.load(open(path + '/teacherTopic', 'rb'))  #{author_id： {topic:这个作者的文章对应这个主题的概率之和，.... }，.....}

    G = nx.Graph() #表示有向图
    exp_to_topic = []
    topic_top_exp = []
    num = len(teacherTopic) #教师的数量

    for teacher in teacherTopic: #教师id
        for topic in teacherTopic[teacher]: #教师id对应的主题（多个）
            exp_to_topic.append((teacher, "topic_" + str(topic), teacherTopic[teacher][topic]))
            #三元组： （教师id， “topic_”+主题id， 这个教师的所有文章对应这个主题的概率之和） [(94720, 'topic_0', 2.0434909685), ....]
            topic_top_exp.append(("topic_"+str(topic), teacher, teacherTopic[teacher][topic] * 10 / num))#????????????????????????????
            # 三元组： （“topic_”+主题id，教师id， 这个教师的所有文章对应这个主题的概率之和 除以教师的总数）  [('topic_0', 94720, 0.15719161296153847), .....]
    G.add_weighted_edges_from(exp_to_topic)
    G.add_weighted_edges_from(topic_top_exp)
    print("computer")
    layout = nx.spring_layout(G)
    nx.draw_networkx(G)
    plt.show()
    pr = nx.pagerank(G, alpha=0.85)  #这个0.85 取自吴志成开题报告
    #pr： {94720: 0.003991142769616514,....... , 110589: 0.004503673210235896, 110590: 0.0042132466645341754}

    dmin = min(pr.items(), key=lambda x: x[1])[1] * (num+k)# k 是训练得出的主题数， num是教师的数量？？？
    dmax = max(pr.items(), key=lambda x: x[1])[1] * (num+k)
    nx.draw_networkx(G, pos=layout, node_size=[x * 6000 for x in pr.values()], node_color='m', with_labels=True)

    teacherRank = {}
    print(pr.items())
    for node, pageRankValue in pr.items():
        if type(node) == str:
            continue
        teacherRank[node] = (pageRankValue * (num + k) + 1) / 2
    print(teacherRank)  #{94720: 0.7833711366427725, .....  , 84650: 0.9104579459915477, 110590: 0.7991405131819265}
    print(max([teacherRank[t] for t in teacherRank]))
    print(min([teacherRank[t] for t in teacherRank]))

    pickle.dump(teacherRank, open(path + '/teacherRank', 'wb'))

# if __name__ == '__main__':
#     makeIndex("0835", 12)

def makeSchoolIndex(code, k):
    '''

    :param code:
    :param k:
    :return:
    '''
    path = root + '/' + code + '/k' + str(k)
    print(path)
    schoolTopic = pickle.load(open(path + '/schoolTopic', 'rb'))
    #   学校对应主题的概率  {18432: {0: 1.9729973247979795, 1: 1.4606949981857031,  .....   , 9: 6.504844019316634, 10: 3.1317970868372833, 11: 3.0198792337906832}}
    G = nx.Graph()
    exp_to_topic = []
    topic_top_exp = []
    num = len(schoolTopic)
    for school in schoolTopic:  #学校的id
        for topic in schoolTopic[school]:  #主题的id
            exp_to_topic.append((school, "topic_" + str(topic), schoolTopic[school][topic]))  #三元组 （学校id， “topic_”主题id ，概率）
            '''[(18432, 'topic_0', 1.9729973247979795), (18432, 'topic_1', 1.4606949981857031), ........
            (18431, 'topic_10', 3.1317970868372833), (18431, 'topic_11', 3.0198792337906832)]
            '''
            topic_top_exp.append(("topic_" + str(topic), school, schoolTopic[school][topic] * 10 / num))   #三元组 （学校id， “topic_”主题id ，概率）

    G.add_weighted_edges_from(exp_to_topic)
    G.add_weighted_edges_from(topic_top_exp)
    print("computer")
    layout = nx.spring_layout(G)
    # nx.draw_networkx(G)
    pr = nx.pagerank(G, alpha=0.85)

    dmin = min(pr.items(), key=lambda x: x[1])[1]
    dmax = max(pr.items(), key=lambda x: x[1])[1]
    nx.draw_networkx(G, pos=layout, node_size=[x * 6000 for x in pr.values()], node_color='m', with_labels=True)
    schoolRank = {}
    for node, pageRankValue in pr.items():
        if type(node) == str:
            continue
        schoolRank[node] = (pageRankValue * (num+k)+1) / 2
    print()
    pickle.dump(schoolRank, open(path + '/schoolRank', 'wb'))

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''
这段代码粘贴自duan，作用是创建学院的索引
'''

def makeInstitutionIndex(code, k):

    path = root+'/' + code + '/k' + str(k)
    institutionTopic = pickle.load(open(path + '/institutionTopic', 'rb'))
    G = nx.Graph()
    exp_to_topic = []
    topic_top_exp = []
    num = len(institutionTopic)
    for institution in institutionTopic:
        for topic in institutionTopic[institution]:
            exp_to_topic.append((institution, "topic_" + str(topic), institutionTopic[institution][topic]))
            topic_top_exp.append(("topic_" + str(topic), institution, institutionTopic[institution][topic] * 10 / num))
    G.add_weighted_edges_from(exp_to_topic)
    G.add_weighted_edges_from(topic_top_exp)
    print("computer")
    layout = nx.spring_layout(G)
    nx.draw_networkx(G)
    pr = nx.pagerank(G, alpha=0.85)

    dmin = min(pr.items(), key=lambda x: x[1])[1]
    dmax = max(pr.items(), key=lambda x: x[1])[1]
    nx.draw_networkx(G, pos=layout, node_size=[x * 6000 for x in pr.values()], node_color='m', with_labels=True)
    institutionRank = {}
    for node, pageRankValue in pr.items():
        if type(node) == str:
            continue
        institutionRank[node] =(pageRankValue *(num+k)+1)/2

    pickle.dump(institutionRank, open(path + '/institutionRank', 'wb'))
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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
    # subject = [{"code": '12', "k": 98}]
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
        makeIndex(sub['code'],sub['k'])
        makeSchoolIndex(sub['code'], sub['k'])
        # --------------------
        makeInstitutionIndex(sub['code'], sub['k'])
        # --------------------