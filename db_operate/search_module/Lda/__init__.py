
#  author   ：feng
#  time     ：2018/1/25
#  function : 应用初始化

#       注册蓝图
import  os
import pickle
from flask import Flask,redirect,json,request


app = Flask(__name__)
@app.route('/')
@app.route('/index')
@app.route('/index.html')

def index():
    return redirect('/static/allVersion.html')
@app.route('/lodaData',methods=['GET','POST'])
def lodaData():
    '''
    加载数据，
    :return:
    '''
    params=['version','k',"topic"]
    search_params={}
    t=request.form.get('data')
    data = json.loads(t)
    for p in params:
        if p in data.keys():
            search_params[p]=data[p]
        else :
            search_params[p]=None
    dic = pickle.load(open('algorithm/data/dic', 'rb'))
    version=search_params["version"]
    name=dic[version]
    file_paper=open("algorithm/data/"+version+"/"+name+".txt",'r',encoding='utf8')
    k=search_params["k"].replace(".html", '')
    file_topic = open("algorithm/data/"+version+"/"+k+"/"+name+"_teacher_topic.txt",'r',encoding='utf8')
    topic_num={}
    topic_paper=[]
    paper=[]
    for p in file_paper.readlines():
        paper.append(eval(p))
    for index,line in enumerate(file_topic.readlines()):
        item=eval(line)
        for i in item:
            if i[1]>=0.2 and i[0]==int(search_params['topic']):
                topic_paper.append({"paper":paper[index],"value":i[1]})
            if i[0] not in topic_num:
                topic_num[i[0]]=0
            topic_num[i[0]]+=1
    ajax={}
    ajax['success']=True
    ajax['msg']=''
    ajax['obj'] ={"topic_paper":topic_paper,"topic_num":topic_num}
    s=json.jsonify(ajax)
    return s
app.config['SECRET_KEY'] = os.urandom(24)
app.jinja_env.auto_reload = True



