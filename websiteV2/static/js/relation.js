/**
 * author: xiaoniu
 * date: 2019-03-18
 * desc: 显示关系图的类，依赖于d3.js
 * 需要额外的css #tooltip 其position必须为absolute

 let categories = [
 {name: '长江学者（青年学者）', color: '#EE6A50'},
 {name: '长江学者（特聘教师）', color: '#4F94CD'},
 {name: '杰出青年', color: '#DAA520'},
 ];

 let nodes = [
 {category: 0, name: '桂林'},
 {category: 1, name: '广州'},
 {category: 2, name: '厦门'},
 {category: 1, name: '杭州'},
 {category: 0, name: '上海'},
 {category: 1, name: '青岛'},
 {category: 0, name: '天津'}
 ];
 let edges = [
 {source: 0, target: 1},
 {source: 0, target: 2},
 {source: 0, target: 3},
 {source: 1, target: 4},
 {source: 1, target: 5},
 {source: 1, target: 6},
 ];
 let json_data = {
        'nodes': nodes,
        'links': edges,
        "categories": categories,
    };
 注：每个节点可以有不同的大小，其键名为radius，默认为10
    每个联系可以有不同的宽度，其键名为width，默认为2 选中时为5
 */

/**
 * 拷贝对象
 * @param obj 要拷贝的对象
 * @param elimination 过滤的键
 * @return 拷贝的对象
 */
function copy(obj, elimination = null) {
    let result = {};
    elimination = elimination == null? []: elimination;
    for (let key in obj){
        //是否拷贝对象
        if (typeof obj[key] === 'object'){
            continue;
        }
        else if (elimination.indexOf(key) == -1)
            result[key] = obj[key];
    }
    return result;
}

class RelationGraph{
    /**
     * 构造函数 绘制的节点和线都会在此svg下
     * @param svg 带有宽高的svg控件
     */
    constructor(svg){
        this.svg = svg;
        //获取控件的宽和高
        this.width = this.svg.attr('width');
        this.height = this.svg.attr('height');
        let that = this;
        //参与缩放的标签都在此g标签中
        this.group = this.svg.append('g')
            .attr('cursor', 'pointer');
        //为svg添加缩放事件
        this.svg.call(d3.zoom()
            .scaleExtent([0.3, 4])
            .on('zoom', function () {
                that.group.attr('transform', d3.event.transform);
            }))
            .on('dblclick.zoom', null);
        //线group,在this.group下
        this.links_group = null;
        //节点group，在this.group节点下
        this.nodes_group = null;
        //文本group，在this.group节点下
        this.labels_group = null;
        //类别group，与this.group同级
        this.categories_group = null;
        //创建力导向
        this.simulation = d3.forceSimulation();
        //保存数据
        this.nodes = null;
        this.links = null;
        this.categories = null;
        //暂存数据
        this.nodes_map = {};
        this.links_map = [];
        //提示框
        this.tooltip = d3.select('body').append('div').attr('id', 'tooltip');
    }

    /**
     * 公有函数 设置数据
     * @param json_data
     */
    setData(json_data){
        //获取数据
        this.nodes = json_data.nodes;
        this.links = json_data.links;
        this.categories = json_data.categories;
        //清除数据
        this.nodes_map = {};
        this.links_map = [];
        let that = this;
        //标准化节点大小
        this.normalizeNodes();
        //标准化联系宽度
        this.normalizeLinks();
        //绑定力导向图对应的数据
        this.simulation.nodes(this.nodes)
            .force('link', d3.forceLink(this.links).distance(this.getDistanceHook))
            .force('charge', d3.forceManyBody().strength(-100))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2));
        //绑定tick回调函数
        this.simulation.on('tick', function () {
            that.tickCallback(arguments);
        });
        //生成类别
        //根据类别和颜色生成
        this.updateCategories();
        //添加链接group和节点group
        //添加节点、连线和文本标签
        this.updateLinks();
        this.updateNodes();
        this.updateLabels();
        //力导向图重新模拟
        this.simulation.alpha(1).restart();
    }

    /**
     * 钩子函数 返回联系的长度
     * @param datum 该联系对应的数据
     * @param index 该联系所在的索引
     * @returns {number}
     */
    getDistanceHook(datum, index){
        return datum.level * 60;
    }

    /**
     * 钩子函数 返回强调的联系宽度
     * @param datum 联系对应的数据项
     * @returns {number} 联系的宽度
     */
    getEmphasisLinkWidthHook(datum){
        return 12;
    }

    /**
     * 钩子函数 点击节点后的动作
     * @param node 节点
     * @param datum 节点对应的数据
     */
    clickNodeHook(node, datum){
        console.log(datum);
    }

    /**
     * 钩子函数 鼠标移动到node或者link上显示的内容
     * @param {string} type node/link
     * @param datum 节点/联系对应的数据项
     * @returns {string} 要生成的html字符串
     */
    getToolTipHook(type, datum){
        let html = null;
        if (type == 'node'){
            html = "<p>" + datum.name + '</p>';
        }
        else if (type == 'link'){
            html = '<p>' + datum.source.name + '-' + datum.target.name + '</p>';
        }
        return html;
    }

    /**
     * 私有函数 会在this.svg中生成一个g来保存所有的类别
     */
    updateCategories(){
        if (this.categories_group == null){
            this.categories_group = this.svg.append('g').attr('id', 'categories');
        }
        let that = this;
        //先移除原先的类别
        this.categories_group.selectAll('g').remove();

        let group = this.categories_group.selectAll('g')
            .data(this.categories)
            .enter()
            .append('g')
            .attr('cursor', 'pointer');
        //添加
        let width = 0;
        let fontWidth = 15;
        //矩形宽度
        let rectWidth = 30;
        //添加矩形
        group.append('rect')
            .attr('x', function (d, i) {
                d.status = true;
                if (i > 0)
                    width += that.categories[i - 1].name.length * fontWidth;
                return i * rectWidth + width;
            })
            .attr('y', 20)
            .attr('fill', d => d.color)
            .attr('width', rectWidth)
            .attr('height', 15)
            .attr('rx', 5)
            .attr('ry', 5);
        //添加文本
        width = 0;
        group.append('text')
            .attr('x', function (d, i) {
                if (i > 0)
                    width += that.categories[i - 1].name.length * fontWidth;
                return (i + 1) * rectWidth + width;
            })
            .attr('y', 32)
            .text(d => d.name)
            .attr('fill', (d) => d.color);
        //添加可点击函数
        group.on('click', function (datum, index) {
            that.clickCategoryCallback(datum, index);
        });
    }

    /**
     * 私有函数 根据this.nodes添加节点this.nodes_group中
     */
    updateNodes(){
        if (this.nodes_group == null){
            this.nodes_group = this.group.append('g').attr('id', 'nodes');
        }
        let circles = this.nodes_group.selectAll('circle');
        //更新已有的节点
        let update = circles.data(this.nodes);
        updateNodes(update, this);
        //设置新增的节点
        let enter = update.enter().append('circle');
        updateNodes(enter, this);
        //删除不需要的节点
        update.exit().remove();

        function updateNodes(nodes, that) {
            //添加节点，并使得节点可拖拽
                nodes.each(function (d) {
                    //设置节点的默认半径
                    if (d.radius == undefined)
                        d.radius = 10;
                })
                .attr('r', d => d.radius)
                .attr('fill', d => that.categories[d.category].color)
                .call(that.dragNodesCallback(that.simulation))
                .on('mouseover', function (d) {
                    that.mouseOver2Node(d);
                })
                .on('mousemove', function () {
                    that.setVisibleOfToolTip(true);
                })
                .on('mouseout', function () {
                    that.mouseOut();
                })
                .on('click', function (d) {
                    that.clickNodeHook(this, d);
                });
        }//end function
    }

    /**
     * 私有函数 this.links添加连线到this.links_group
     */
    updateLinks(){
        if (this.links_group == null){
            this.links_group = this.group.append('g').attr('id', 'lines');
        }
        let links =this.links_group.selectAll('path');
        //绑定数据后，不同类型，不同操作
        let update = links.data(this.links);
        let enter = update.enter().append('path');
        updateLinks(update, this);
        updateLinks(enter, this);
        //移除不需要的联系
        update.exit().remove();
        function updateLinks(links, that) {
            //添加连线
                links.attr('fill', 'none')
                .style('stroke', '#ccc')
                .each(function (d) {
                    //设置线的默认宽度
                    if (d.width == undefined)
                        d.width = 2;
                })
                .style('stroke-width', d => d.width)
                .on('mouseover', function (d) {
                    that.mouseOver2Link(d);
                })
                .on('mousemove', function () {
                    that.setVisibleOfToolTip(true);
                })
                .on('mouseout', function () {
                    that.mouseOut();
                });
        }//end function
    }

    /**
     * 更新节点对应的标签，会先更新标签，如果需要的话会添加标签。多余的则会删除
     */
    updateLabels(){
        if (this.labels_group == null){
            this.labels_group = this.group.append('g').attr('id', 'labels');
        }
        let that = this;
        let texts =this.labels_group.selectAll('text');
        //绑定数据后，不同类型，不同操作
        let update = texts.data(this.nodes);
        updateLabels(update, this);
        let enter = update.enter().append('text');
        updateLabels(enter, this);
        //移除不需要的文本
        update.exit().remove();

        function updateLabels(labels, that) {
        let fontSize = 15;
        labels.attr('fill', 'white')
                .attr('display', 'none')
                .attr('dx', d => -d.name.length * fontSize / 2)
                .attr('dy', fontSize / 4)
                .attr('font-size', fontSize)
                .attr('stroke-width', 0.5)
                .attr('stroke', d => that.categories[d.category].color)
                .text(d => d.name)
                .call(that.dragNodesCallback(that.simulation))
                .on('mouseover', function (d) {
                    that.mouseOver2Node(d);
                })
                .on('mousemove', function () {
                    that.setVisibleOfToolTip(true);
                })
                .on('mouseout', function () {
                    that.mouseOut();
                })
                .on('click', function (d) {
                    that.clickNodeHook(this, d);
                });
        }
    }

    /**
     * 设置this.nodes_group中的circle标签的透明度
     * @param opacity 透明度
     * @param filter 过滤器，为空则完全不过滤
     */
    setOpacityOfNodes(opacity, filter = null){
        let nodes = null;

        if (filter == null)
            nodes = this.nodes_group.selectAll('circle');
        else
            nodes = this.nodes_group.selectAll('circle').filter(filter);

        nodes.attr('opacity', opacity);
    }

    /**
     * 设置this.links_group中的line标签的透明度
     * @param opacity 透明度
     * @param filter 过滤器，为空则完全不过滤
     */
    setOpacityOfLinks(opacity, filter = null){
        //隐藏连线
        let links = null;

        if (filter == null)
            links = this.links_group.selectAll('path');
        else
            links = this.links_group.selectAll('path').filter(filter);

        links.attr('opacity', opacity);
    }

    /**
     * 设置this.links_group中的line标签的宽度
     * @param width 线的宽度 可以是数值或者函数
     * @param filter 过滤器，为空则完全不过滤
     */
    setWidthOfLinks(width, filter = null){
        //隐藏连线
        let links = null;

        if (filter == null)
            links = this.links_group.selectAll('path');
        else
            links = this.links_group.selectAll('path').filter(filter);

        links.style('stroke-width', width);
    }

    /**
     * 设置this.labels_group中的text标签是否显示
     * @param visible 是否隐藏
     * @param filter 过滤器，为空则完全不过滤
     */
    setVisibleOfLabels(visible, filter = null){
        //隐藏标签
        let labels = null;
        let display = visible? 'inline': 'none';

        if (filter == null)
            labels = this.labels_group.selectAll('text');
        else
            labels = this.labels_group.selectAll('text').filter(filter);

        labels.style('display', display);
    }

    /**
     * 私有函数 按照类别category和this.nodes_map和this.links_map来添加节点和联系
     * @param {Number} category 类别，为该节点在this.nodes的索引
     */
    addNodesAndLinks(category){
        //添加节点
        this.nodes = this.nodes.concat(this.nodes_map[category]);
        this.nodes_map[category] = [];
        let elimination = ['target_name'];
        //添加线
        for (let i = 0; i < this.nodes.length; i++){
            let node1 = this.nodes[i];
            let links = this.links_map[node1.name];
            if (links == undefined)
                continue;
            let len = links.length;
            for (let j = 0;j >= 0 && j < len; j++){
                for (let k = 0; k < this.nodes.length; k++){
                    let node2 = this.nodes[k];
                    if (j >= 0 && j < len && links[j].target_name == node2.name){
                        let obj = copy(links[j], elimination);
                        obj['source'] = i;
                        obj['target'] = k;
                        this.links.push(obj);
                        //移除一个
                        links.splice(j, 1);
                        j--;
                        len--;
                    }
                }
            }
        }
        //添加节点和联系
        this.updateNodes();
        this.updateLinks();
        this.updateLabels();
    }

    /**
     * 私有函数 移除类别下的所有节点和联系，并放入this.nodes_map和this.links_map之中
     * @param {Number} category 类别，为该节点在this.nodes的索引
     */
    removeNodesAndLinks(category){
        let that = this;
        //清除线
        let count = 0;
        let elimination = ['index'];
        let lines = this.links_group.selectAll('path')
            .filter(function (d, i) {
                if (d.source.category == category || d.target.category == category){
                    let link = that.links.splice(i - count, 1)[0];
                    let source_name = link.source.name;
                    let target_name = link.target.name;

                    if (!(source_name in that.links_map))
                        that.links_map[source_name] = [];
                    let obj = copy(link, elimination);
                    obj['target_name'] = target_name;
                    that.links_map[source_name].push(obj);
                    count++;
                    return true;
                }
                return false;
            });
        lines.remove();
        count = 0;
        //清除circles
        elimination = ['index', 'vx', 'vy', 'x', 'y'];
        let circles = this.nodes_group.selectAll('circle')
            .filter(function (d, i) {
                if (d.category == category){
                    let node = that.nodes.splice(i - count, 1)[0];
                    if (!(category in that.nodes_map)){
                        that.nodes_map[category] = [];
                    }
                    let obj = copy(node, elimination);
                    that.nodes_map[category].push(obj);
                    count++;
                    return true;
                }
                return false;
            });
        circles.remove();
    }

    /**
     * 点击类别回调函数,会添加/移除该类别下的所有节点和联系
     * @param datum 绑定的数据
     * @param index 对应的索引
     */
    clickCategoryCallback(datum, index){
        let g = this.categories_group.selectAll('g')
            .filter(function (d, i) {
                return index == i;
            });
        let color = null;
        //设置颜色为灰色
        if (datum.status){
            datum.status = false;
            color = '#ABABAB';
        }
        else{
            datum.status = true;
            color = datum.color;
        }
        //设置矩形和文本颜色
        g.select('rect').attr('fill', color);
        g.select('text').attr('fill', color);
        //按照类别index来添加/移除节点和连线
        if (datum.status)
            this.addNodesAndLinks(index);
        else
            this.removeNodesAndLinks(index);
        //力导向图重新模拟
        this.simulation.nodes(this.nodes);
        this.simulation.force('link', d3.forceLink(this.links).distance(this.getDistanceHook));
        this.simulation.alpha(1).restart();
    }

    /**
     * 节点拖拽回调函数
     * @param force
     * @returns {*}
     */
    dragNodesCallback(force){
        function drag_started(d, index) {
            if (!d3.event.active)
                force.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }
        function drag_ended(d) {
            if (!d3.event.active)
                force.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        return d3.drag()
            .on('start', drag_started)
            .on('drag', dragged)
            .on('end', drag_ended);
    }

    /**
     * 力导向图tick回调函数 会更新节点和联系的坐标
     */
    tickCallback(){
        //更新连线坐标
        let that = this;
        this.links_group.selectAll('path')
            .attr('d', function (d) {
                let dx = d.target.x - d.source.x;
                let dy = d.target.y - d.source.y;
                let dr = Math.sqrt(dx * dx + dy * dy);

                return 'M' + d.source.x + ',' + d.source.y
                + 'A' + dr + ',' + dr + ' 0 0,1' + d.target.x + ',' + d.target.y;
            });
        //更新节点坐标
        this.nodes_group.selectAll('circle')
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        //更新文本坐标
        this.labels_group.selectAll('text')
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    }

    /**
     * 设置动画显示/隐藏提示面板
     * @param {boolean} visible 显示/隐藏 为true时会更新提示面板位置，为false会隐藏面板
     * @param  html 只有visible为true时才会更新面板显示
     */
    setVisibleOfToolTip(visible, html = null){
        let duration = null;
        let opacity = null;
        //渐渐显示tooltip
        if (visible){
            this.tooltip.style('left', (d3.event.pageX) + 'px')
                .style('top', (d3.event.pageY - 28) + 'px');
            //设置文本
            if (html != null){
                this.tooltip.html(html);
                duration = 200;
                opacity = 0.8;
            }
        }
        //动画隐藏提示框
        else{
            duration = 500;
            opacity = 0;
        }
        if (duration != null && opacity != null){
            this.tooltip
                .transition()
                .duration(duration)
                .style('opacity', opacity);
        }
    }

    /**
     * 私有函数 移动到节点上的回调函数，其他节点和联系会变略微透明
     * @param datum 该节点对应的数据
     */
    mouseOver2Node(datum){
        //显示提示文本
        let html = this.getToolTipHook('node', datum);
        this.setVisibleOfToolTip(true, html);
        //暂存节点的id
        let temp_nodes = new Set();
        //获取与该节点相连的所有的连线
        for (let i = 0; i < this.links.length; i++){
            let link = this.links[i];
            if (link.source.name == datum.name || link.target.name == datum.name){
                temp_nodes.add(link.source.name);
                temp_nodes.add(link.target.name);
            }
        }
        let node_name = datum.name;
        //隐藏其他节点
        this.setOpacityOfNodes(0.2, d => !temp_nodes.has(d.name));
        //隐藏其他连线
        this.setOpacityOfLinks(0.2, function (d) {
            return d.source.name != node_name && d.target.name != node_name;
        });
        //加宽连线
        this.setWidthOfLinks(this.getEmphasisLinkWidthHook, function (d) {
            return d.source.name == node_name || d.target.name == node_name;
        });
        //显示文本
        this.setVisibleOfLabels(true, d => temp_nodes.has(d.name));
    }

    /**
     * 鼠标移出节点回调函数
     */
    mouseOut(){
        //动画隐藏提示框
        this.setVisibleOfToolTip(false);
        //显示节点和连线
        this.setOpacityOfNodes(1);
        this.setOpacityOfLinks(1);
        //TODO:恢复线宽
        this.setWidthOfLinks(function (d) {
            return d.width;
        });
        this.setVisibleOfLabels(false);
    }

    mouseOver2Link(datum){
        //显示关系
        let html = this.getToolTipHook('link', datum);
        this.setVisibleOfToolTip(true, html);
        //其他节点半透明
        this.setOpacityOfNodes(0.2, function (d) {
            return d.name != datum.source.name && d.name != datum.target.name;
        });
        //其他联系半透明
        this.setOpacityOfLinks(0.2, d => d != datum);
        //加宽连线
        this.setWidthOfLinks(this.getEmphasisLinkWidthHook, d => d == datum);
        //显示有联系的节点的文本
        this.setVisibleOfLabels(true, function (d) {
            return d.name == datum.source.name || d.name == datum.target.name;
        })
    }

    /**
     * 标准化节点
     * @param minNodeRadius 最小的节点
     * @param maxNodeRadius 最大的节点
     */
    normalizeNodes(minNodeRadius = 10, maxNodeRadius = 30){
        //获取节点的最大值
        let realNodeMaxSize = 0;
        for (let i = 0; i < this.nodes.length; i++){
            let node = this.nodes[i];
            if (realNodeMaxSize < node.radius)
                realNodeMaxSize = node.radius;
        }
        for (let i = 0; i < this.nodes.length; i++){
            let node = this.nodes[i];
            node.radius = node.radius / realNodeMaxSize * maxNodeRadius;
            node.radius = node.radius > minNodeRadius? node.radius: minNodeRadius;
        }
    }

    /**
     * 标准化联系宽度
     * @param minLineWidth 最小宽度
     * @param maxLineWidth 最大宽度
     */
    normalizeLinks(minLineWidth = 2, maxLineWidth = 8){
        this.transformLinksFormat();
        //获取最大宽度
        let maxWidth = 0;
        for (let i = 0; i < this.links.length; i++){
            let link = this.links[i];
            if (maxWidth < link.width)
                maxWidth = link.width;
        }
        //设置宽度
        for (let i = 0; i < this.links.length; i++){
            let link = this.links[i];

            link.width = link.width / maxWidth * maxLineWidth;
            link.width = link.width > minLineWidth? link.width: minLineWidth;
        }
    }
    /*
        转换节点的链接的格式，并设置线的长度
        links_dict = {} links_dict['source'] = [{'target': 'sky', 'weight': 10}]
     */
    transformLinksFormat() {
        for (let index = 0; index < this.nodes.length; index++){
            //找出该节点的所有边 并且确定最大权重和最小权重
            let minWidth = null;
            let maxWidth = 0;
            let temp_links = [];
            for (let j = 0;j < this.links.length; j++){
                let link = this.links[j];
                let temp_link = null;

                if (link.source == index)
                    temp_link = link;
                else if (link.target == index)
                    temp_link = link;

                if (temp_link != null)
                {
                    temp_links.push(temp_link);
                    //确定最大值
                    if (maxWidth < temp_link.width)
                        maxWidth = temp_link.width;
                    //确定最小值
                    if (minWidth == null || minWidth > temp_link.width)
                        minWidth = temp_link.width;
                }
            }
            //开始分级
            var step = (maxWidth - minWidth) / 3;
            var levels = [];
            levels[3] = [minWidth, minWidth + step];
            levels[2] = [minWidth + step, minWidth + step * 2];
            levels[1] = [minWidth + step * 2, maxWidth];
            for (let j in temp_links)
            {
                var temp_link = temp_links[j];
                var weight = temp_link.width;
                var level = 1;
                var oldLevel = typeof(temp_link.level);

                for (let k = 1; k <= 3; k++){
                    if (weight >= levels[k][0] && weight <= levels[k][1]) {
                        level = k;
                        break;
                    }
                }
                //和旧的值进行比较
                if (oldLevel == 'undefined' || level > oldLevel)
                {
                    temp_link.level = level;
                }
            }
        }
    }
}