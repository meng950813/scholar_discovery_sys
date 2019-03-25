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
 * 处理学校商务的关系
 * @param self {id: id, name: name} 个人信息
 * @param json_data 数组
 */
function handle_school_agent_relations(self, json_data) {
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
        let kind = datum['SCHOOL_NAME'] + '-' + datum['COLLEGE_NAME'];
        //不添加重复类别
        let index = kinds.indexOf(kind);
        if (index == -1){
            kinds.push(kind);
            index = kinds.length - 1;
        }
        //尝试添加学院节点
        let collegeIndex = contains(nodes, 'name', kind);
        if (collegeIndex == -1){
            nodes.push({category: index, 'name': kind});
            collegeIndex = nodes.length - 1;
        }
        //尝试添加个人与学院的联系
        let link = {source: 0, target: collegeIndex};
        if (containsLink(links, link) == -1)
            links.push(link);
        //尝试添加学院的人节点
        let agentIndex = contains(nodes, 'name', datum['TEACHER_NAME']);
        if (agentIndex == -1){
            nodes.push({category: index, name: datum['TEACHER_NAME']});
            agentIndex = nodes.length - 1;
        }
        //尝试添加学院和学院中人的联系
        link = {source: collegeIndex, target: agentIndex};
        if (containsLink(links, link) == -1)
            links.push(link);
    }
    let categories = [];
    for (let i = 0; i < kinds.length; i++){
        let kind = kinds[i];
        let color = colors[i % colors.length];

        categories.push({name: kind, color: color});
    }
    let data = {
        "categories": categories,
        "nodes": nodes,
        "links": links,
    };
    return data;
}

function updateAgentRelationList(relation_list, mapping, json_data){
    relation_list.selectAll('tr').remove();

    console.log(json_data);
    for (let index = 0; index < json_data.length; index++){
        let datum = json_data[index];
        let tr = relation_list.append('tr')
            .attr('data-index', datum['ID']);
        tr.selectAll('td')
            .data(mapping)
            .enter()
            .append('td')
            .text(function (_, i) {
                return datum[mapping[i]];
            });
        let td = tr.append('td');
        td.append('button')
            .attr('type', 'button')
            .attr('class', 'btn btn-danger delete-relation')
            .text('删除');
        td.append('button')
            .attr('type', 'button')
            .attr('class', 'btn btn-info modify-relation')
            .text('修改');
    }
}
