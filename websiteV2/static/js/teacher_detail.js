/**
 * 用于判断数组中是否包含键为key，值为value的dict，若有则返回索引，没有则返回-1
 * @param array 数组，数组中包含着是字典
 * @param key 键名
 * @param value 值
 * @return {int} 索引，若不存在则返回-1
 */
function contains(array, key, value){
    for (let i = 0; i < array.length; i++){
        let data = array[i];
        if (data[key] == value)
            return i;
    }
    return -1;
}
/**
 * 联系数组中是否包含对应的联系，
 * @param links 联系数组
 * @param link 联系 {source:0, target: 1}
 * @return {number} 若有，则返回对应的索引；否则返回-1
 */
function containslink(links, link) {
    for (let i = 0; i < links.length; i++){
        let l = links[i];
        if (l.source == link.source && l.target == link.target){
            return i;
        }
    }
    return -1;
}
/**
 * 处理老师和和做人的关系
 * @param self {id: id, name: name} 个人信息
 * @param json_data 数组
 */
function handle_partner_relations(self, json_data) {
    //每个类别所对应的颜色
    let colors = ["#ee6a50", "#4f94cd", "#daa520", "#0000ff", "#8fbc8f", "#5d478b", "#528b8b", "#483d8b", "#3a5fcd"];
    //种类
    let kinds = [self.name];
    let nodes = [];
    let links = [];
    //添加个人节点
    nodes.push({category: 0, name: self.name, "id": self.id});

    for (let i = 0; i < json_data.length; i++){
        let datum = json_data[i];
        //不添加个人信息
        if (datum['name'] == self.name)
            continue;
        //设置职称
        let academician = datum['academician'];
        let outyouth = datum['outyouth'];
        let changjiang = datum['changjiang'];
        if (academician)
            kind = '院士';
        else if (changjiang)
            kind = '长江学者';
        else if (outyouth)
            kind = '杰出青年';
        else
            kind = datum['title'];
        //不添加重复类别
        let index = kinds.indexOf(kind);
        if (index == -1){
            kinds.push(kind);
            index = kinds.length - 1;
        }
        //尝试添加节点
        let nodeindex = contains(nodes, 'name', datum['name']);
        //不存在对应的点，则添加
        if (nodeindex == -1){
            nodes.push({
                category: index,
                'name': datum['name'],
                'id': datum['id'],
                'school_id': datum['school_id'],
                'college_id': datum['institution_id']
            });
            nodeindex = nodes.length - 1;
        }
        //尝试添加联系
        let link = {source: 0, target: nodeindex, width: 1};
        let linkindex = containslink(links, link);
        //不存在，则添加
        if (linkindex == -1){
            links.push(link);
        }else{
            links[linkindex].width += 1;
        }
    }
    let categories = [];
    for (let i = 0; i < kinds.length; i++){
        let kind = kinds[i];
        let color = colors[i % colors.length];

        categories.push({name: kind, color: color});
    }
    return {
        "categories": categories,
        "nodes": nodes,
        "links": links,
    };
}

function post(url, parameters) {
    //创建form表单
    let temp_form = document.createElement('form');
    temp_form.action = url;
    //打开一个新的页面
    temp_form.target = '_blank';
    temp_form.method = 'post';
    temp_form.style.display = 'none';
    //添加参数
    for (let item in parameters){
        let opt = document.createElement('textarea');
        opt.name = item;
        opt.value = parameters[item];

        temp_form.appendChild(opt);
    }
    document.body.appendChild(temp_form);
    //提交数据
    temp_form.submit();
}

/**
 * 钩子函数 点击节点后的动作
 * @param node 节点
 * @param datum 节点对应的数据
 */
function clickNodeHook(node, datum){
    //点击的为本主页的老师，不进行跳转
    if (datum.id == TEACHER_ID)
        return;
    //尝试跳转
    console.log(datum);
    let params = {'school_id': datum['school_id'], 'college_id': datum['college_id']};
    let url = '/detail/' + datum.id;
    console.log(params);
    console.log(url);
    //发送表单
    post(url, params);
}

//main
let words = [];
//转换成词云需要的格式
for (let key in FIELDS){
    let value = FIELDS[key];
    words.push({text: key, size: value * 100 * 6});
}
let wordCloud = new WordCloud(d3.select('#word-cloud'));
wordCloud.setData(words);
//关系图
let self = {'id': TEACHER_ID, 'name': TEACHER_NAME};

//设置关系图
let relationGraph = new RelationGraph(d3.select('#relation-net'));
let handled_data = handle_partner_relations(self, PARTNERS);
relationGraph.clickNodeHook = clickNodeHook;
relationGraph.setData(handled_data);

//论文和发表年的一个区域图
let paper_data = handle_papers(PAPERS);
let paperChart = new AreaChart(d3.select('#paper-chart'));
paperChart.setData(paper_data["paper_numbers"]);

let citedChart = new AreaChart(d3.select('#cited-chart'));
citedChart.setData(paper_data["cited_numbers"]);
/*
 * {name: ,value} 数组
 */
function handle_papers(papers) {
    let paper_numbers = [];
    let cited_numbers = [];
    for (let i in papers){
        let paper = papers[i];
        let year = parseInt(paper.year);
        if (isNaN(year))
            continue;
        let cited_num = paper.cited_num;
        let ret = false;
        let j = 0;
        for (j = 0; j < paper_numbers.length; j++)
            if (year < paper_numbers[j].name)
                break;
            else if (year == paper_numbers[j].name){
                ret = true;
                break;
            }
        //该年的论文数量+1
        if (ret){
            paper_numbers[j].value += 1;
            cited_numbers[j].value += cited_num;
        }else{
            paper_numbers.splice(j, 0, {"name": year, "value": 1});
            cited_numbers.splice(j, 0, {"name": year, "value": cited_num});
        }
    }//end for
    console.log(cited_numbers);
    return {
        "paper_numbers": paper_numbers,
        "cited_numbers": cited_numbers
    };
}
