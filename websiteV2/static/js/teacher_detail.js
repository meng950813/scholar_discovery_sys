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
function containsLink(links, link) {
    for (let i = 0; i < links.length; i++){
        let L = links[i];
        if (L.source == link.source && L.target == link.target){
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
    let colors = ["#EE6A50", "#4F94CD", "#DAA520", "#0000FF", "#8FBC8F", "#5D478B", "#528B8B", "#483D8B", "#3A5FCD"];
    //种类
    let kinds = [self.name];
    let nodes = [];
    let links = [];
    //添加个人节点
    nodes.push({category: 0, name: self.name});

    for (let i = 0; i < json_data.length; i++){
        let datum = json_data[i];
        //不添加个人信息
        if (datum['name'] == self.name)
            continue;
        //设置职称
        let academician = datum['ACADEMICIAN'];
        let outyouth = datum['OUTYOUTH'];
        let changjiang = datum['CHANGJIANG'];
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
        let nodeIndex = contains(nodes, 'name', datum['name']);
        //不存在对应的点，则添加
        if (nodeIndex == -1){
            nodes.push({category: index, 'name': datum['name']});
            nodeIndex = nodes.length - 1;
        }
        //尝试添加联系
        let link = {source: 0, target: nodeIndex, width: 1};
        let linkIndex = containsLink(links, link);
        //不存在，则添加
        if (linkIndex == -1){
            links.push(link);
        }else{
            links[linkIndex].width += 1;
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
relationGraph.setData(handled_data);
