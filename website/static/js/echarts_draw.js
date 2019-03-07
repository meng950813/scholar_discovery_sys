//是否显示名称
var isShowingName = false;

var myChart = echarts.init(document.getElementById('relation_graph'), 'macarons');
// 添加点击事件
myChart.on('click', {dataType: 'node'}, function (param) {
    
    //TODO:跳转 需要视图函数和id
    var id = param.value[1];
    window.open("/homepage/" + id);
});


// function toggleName() {
//     var btn = $('#toggle_btn');
//     isShowingName = !isShowingName;
//     //隐藏名字
//     var text = isShowingName? '隐藏名字': '显示名字';
//     btn.text(text);
//     //节点上是否显示名字
//     setNameVisibile(myChart, isShowingName);
// }



/*
 * 获取echarts所需要的option
 * graphInfo 包含要绘制的键值对 如nodes color links categories
 * isShowingName 是否显示节点的名字 默认不显示
 * minLineWidth 线的最小宽度 默认为2
 * maxLineWidth 线的最大宽度 默认为12
 * minNodeSize 节点的最小尺寸 默认为20
 * maxNodeSize 节点的最大尺寸 默认为70
 * return 返回设置好的、echarts需要的option
 */
function getOption(graphInfo, isShowingName, minLineWidth, maxLineWidth, minNodeSize, maxNodeSize) {
    //默认值
    isShowingName = arguments[1]? arguments[1]: false;
    minLineWidth = arguments[2]? arguments[2]: 2;
    maxLineWidth = arguments[3]? arguments[3]: 12;

    minNodeSize = arguments[4] ? arguments[4] : 20;
    maxNodeSize = arguments[5] ? arguments[5] : 40;

    graphInfo.nodes.forEach(function (node) {
        node.x = node.y = null;
        node.draggable = true;
    });
    var title = graphInfo['title'];
    var nodes = graphInfo['nodes'];
    //转换成echarts需要的格式
    var links = transformLinksFormat(nodes, graphInfo['links']);
    //links = graphInfo['links'];
    // 确定每条边的宽度
    //获取最大权值
    var maxWeight = 0;
    links.forEach(function (edge) {
        if (maxWeight < edge.weight)
            maxWeight = edge.weight;
    });
    links.forEach(function (edge) {
        edge.lineStyle = {};
        // 等比例缩放行宽度
        edge.lineStyle.width = edge.weight / maxWeight * maxLineWidth;
        edge.lineStyle.width = edge.lineStyle.width > minLineWidth ? edge.lineStyle.width: minLineWidth;
    });
    //确定节点的最小值和最大值
    realNodeMaxSize = 0;
    nodes.forEach(function (node) {
        if (realNodeMaxSize < node.value[0])
            realNodeMaxSize = node.value[0];
    });
    nodes.forEach(function (node) {
        node.value[0] = node.value[0] / realNodeMaxSize * maxNodeSize;
        node.value[0] = node.value[0] > minNodeSize ? node.value[0] : minNodeSize;
        // 确认字体大小
        node.label = {fontSize: Math.log10(node.value[0]) * 12};
    });

    categories = graphInfo['categories'];
    color = graphInfo['color'];
    //设置option样式
    option = {
        title: {
            //text: title,
            x: "right",
            y: "bottom"
        },
        // 弹框
        tooltip: {
            trigger: 'item',
            formatter: function (param) {
                if (param.dataType == 'edge'){
                    //console.log(param);
                    return "合作次数" + param.data.weight + "次";
                }
                //悬浮在节点上时显示的内容,目前仅仅显示名称
                else if (param.dataType == 'node'){
                    return param.name;
                }
                return param.name;
            }
        },
        color: color,
        toolbox: {
            show: false,
            feature: {
                restore: {show: true},
                magicType: {show: true, type: ['force', 'chord']},
                saveAsImage: {show:true}
            }
        },
        legend: {
            x: 'left',
            data: categories.map(function (a) {
                return a.name;
            })
        },
        series: [
            {
                type: 'graph',
                layout: 'force',
                name: title,
                ribbonType: false,
                categories: categories,
                useWorker: false,
                minRadius: 15,
                maxRadius: 25,
                gravity: 1.1,
                scaling: 1.1,
                roam: true,
                nodes: nodes,
                links: links,
                // 鼠标移动到节点上时突出显示节点
                focusNodeAdjacency: true,
                hoverAnimation: true,
                force: {
                    repulsion: 100,
                    gravity: 0.03,
                    edgeLength: 80,
                    layoutAnimation: true
                },
                // 节点大小 可以是数值或者函数
                symbolSize: function (value, params){
                    return value[0];
                },
                label: {
                    show: isShowingName
                },
                nodeStyle: {
                    brushType: 'both',
                    borderColor: 'rgba(255,215,0,0.4)',
                    borderWidth: 1
                },
                lineStyle: {
                    //线的弯度
                    curveness: 0.3
                },
                emphasis: {
                    itemStyle: {
                        borderWidth: 4
                    },
                    label: {
                        show: true
                    },
                    lineStyle: {
                        width: maxLineWidth + 2
                    }
                }
            }
        ]
    };
    return option;
}


/*
    设置是否显示节点名称
    chart 图表
    isShowingName 是否显示节点名称
 */
function setNameVisibile(chart, isShowingName) {
    var option = chart.getOption();
    option.series[0].label.show = isShowingName;
    //重新设置选项
    chart.setOption(option);
}


/*
    转换节点的链接的格式，并设置线的长度
    links_dict = {} links_dict['source'] = [{'target': 'sky', 'weight': 10}]
 */
function transformLinksFormat(nodes, links) {
    for (var index in nodes){
        //获取节点名称
        var node_name = nodes[index].name;
        //找出该节点的所有边 并且确定最大权重和最小权重
        var minWeight = null;
        var maxWeight = 0;
        var temp_links = [];
        for (var j in links){
            var link = links[j];
            var temp_link = null;

            if (link.source == node_name)
                temp_link = link;
            else if (link.target == node_name)
                temp_link = link;

            if (temp_link != null)
            {
                temp_links.push(temp_link);
                //确定最大值
                if (maxWeight < temp_link.weight)
                    maxWeight = temp_link.weight;
                //确定最小值
                if (minWeight == null || minWeight > temp_link.weight)
                    minWeight = temp_link.weight;
            }
        }
        //开始分级
        var step = (maxWeight - minWeight) / 3;
        var levels = [];
        levels[3] = [minWeight, minWeight + step];
        levels[2] = [minWeight + step, minWeight + step * 2];
        levels[1] = [minWeight + step * 2, maxWeight];
        console.log(minWeight, maxWeight, step);
        for (var j in temp_links)
        {
            var temp_link = temp_links[j];
            var weight = temp_link.weight;
            var level = 1;
            var oldLevel = typeof(temp_link.value);

            for (var k = 1; k <= 3; k++){
                if (weight >= levels[k][0] && weight <= levels[k][1]) {
                    level = k;
                    break;
                }
            }
            //和旧的值进行比较
            if (oldLevel == 'undefined' || level > oldLevel)
            {
                temp_link.value = level;
            }
        }
    }
    console.log(links);
    return links;
}
