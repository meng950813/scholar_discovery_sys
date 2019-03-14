/*
    获取地图的中心
 */
function getCenter(features) {
    //最小经度和纬度
    let longitudeMin = 100000;
    let latitudeMin = 100000;
    //最大经度和纬度
    let longitudeMax = 0;
    let latitudeMax = 0;
    
    features.forEach(function (e) {
        let a = d3.geoBounds(e);
        if (a[0][0] <longitudeMin)
            longitudeMin = a[0][0];
        if (a[0][1] < latitudeMin)
            latitudeMin = a[0][1];
        if (a[1][0] > longitudeMax)
            longitudeMax = a[1][0];
        if (a[1][1] > latitudeMax)
            latitudeMax = a[1][1];
    });
    let a = (longitudeMax + longitudeMin) / 2;
    let b = (latitudeMax + latitudeMin) / 2;

    return [a, b];
}
/*
    获取地图的缩放比
 */
function getZoomScale(features, width, height) {
    //最小经度和纬度
    let longitudeMin = 100000;
    let latitudeMin = 100000;
    //最大经度和纬度
    let longitudeMax = 0;
    let latitudeMax = 0;

    features.forEach(function (e) {
        let a = d3.geoBounds(e);
        if (a[0][0] <longitudeMin)
            longitudeMin = a[0][0];
        if (a[0][1] < latitudeMin)
            latitudeMin = a[0][1];
        if (a[1][0] > longitudeMax)
            longitudeMax = a[1][0];
        if (a[1][1] > latitudeMax)
            latitudeMax = a[1][1];
    });
    let a = longitudeMax - longitudeMin;
    let b = latitudeMax - latitudeMin;

    return Math.min(width / a, height / b);
}

/**
 * 判断两个矩形是否相交，若是则返回true
 * @param r1 {x1, y1, x2, y2} x1,y1 为左上角 x2,y2为右上角
 * @param r2 {x1, y1, x2, y2}
 * @returns {boolean}
 */
function intersectRect(r1, r2) {
    return !(r1.x2 < r2.x1 ||
        r2.x2 < r1.x1 ||
        r1.y2 < r2.y1 ||
        r2.y2 < r1.y1);
}

/**
 * 显示中国地图的类，依赖于d3.js
 * 需要额外的css #tooltip 其position必须为absolute
 * 地图块保存在id为map的g标签中
 * 面包屑导航栏保存在id为breadcrumb的g标签中
 * 标注保存在id为tag的g标签中
 */
class ChinaMap{
    constructor(svg){
        this.svg = svg;
        let that = this;
        //所有的path都添加到g中，并命名为map
        this.svg.append('g')
            .attr('id', 'map');
        //获取宽度和高度
        this.width = this.svg.attr('width');
        this.height = this.svg.attr('height');
        //添加面包屑导航栏 目前仅三级
        this.svg.append('g')
            .attr('id', 'breadcrumb');
        this.svg.select('#breadcrumb')
            .selectAll('text')
            .data(['中国', '河南', '商丘'])
            .enter()
            .append('text')
            .text(function (data, index) {
                return data;
            })
            .attr('x', 0)
            .attr('y', function (d, i) {
                return i * 30 + 60;
            })
            .attr('style', function (d, i) {
                if (i > 0)
                    return 'display:none';
                else
                    return "cursor: pointer";
            })
            .on('click', function (d, i) {
                that.clickBreadcrumb(i);
            });
        //添加保存标注的点
        this.svg.append('g')
            .attr('id', 'tag');
        //地图颜色 [0,1]映射到['#ffffcc', '#800026']
        this.mapColor = d3.interpolate('#ffffcc', '#800026');
        //投影函数 用于将GeoJson映射到像素
        this.projection = d3.geoMercator()
            .translate([this.width / 2, this.height / 2]);
        //地理路径生成器
        this.path = d3.geoPath()
            .projection(this.projection);
        //当前缩放级别
        this.scaleLevel = 0;
        //默认未显示
        this.visible = false;
        //要加载的文件路径(也是视图函数的路径)
        this.filepath_list = ['mapdata/china.json', 'mapdata/geometryProvince', 'mapdata/geometryCouties'];
        //栈，用于保存文件名和地图名
        this.stack = [{filename: this.filepath_list[0], 'name': '中国'}];
        //保存已经加载过的文件数据，有则不再获取
        this.loadedData = {};
        //机构经纬度 数组
        this.institutions = [];
        //提示框
        this.tooltip = d3.select('body')
            .append('div')
            .attr('id', 'tooltip');
        this.special_cities = ['北京市', '天津市', '上海市', '台湾省', '海南省', '香港特别行政区', '澳门特别行政区'];
    }

    /**
     *  公有函数 显示中国地图
     */
    showChinaMap(){
        this.clickBreadcrumb(0);
    }

    clickTopItem(item){
        if ('selector' in item && 'datum' in item){
            this.clickMap(item.selector, item.datum);
        }
    }

    onUpdateMap(items){
    }

    /**
     * 地图更新时回调该函数，需要外部重写
     * @param items 保存着更新后的数据
     * @param {Number} index 索引 0时redrawMap回调，1则是redrawInstitutions()回调
     */
    updateMapCallback(items, index){
        if (index == 0){
            this.onUpdateMap(items);
        }//尝试提取数据
        else if (index == 1){
            let data = [];

            for (let i = 0;i < items.length; i++){
                data.push({'name': items[i].school});
            }
            this.onUpdateMap(data);
        }
    }

    /**
     * 私有函数 加载地图文件，并尝试显示地图和文本标签
     * @param filename 要加载的地图完整文件名
     * @param name 选中的地图块对应的名字
     */
    loadAndShowMap(filename, name) {
        //存入栈中
        this.stack.push({'filename': filename,'name': name});
        let that = this;
        //加载文件成功回调函数
        function success(jsondata) {
            //若是空数组，则直接退出
            if (jsondata.length == 0) {
                return;
            }
            that.visible = true;
            //重新绘制地图
            that.redrawMap(jsondata);
            //二级后开始显示学校标记
            if (that.scaleLevel > 0)
                that.redrawInstitutions();
            //中国地图删除标记
            else
                that.svg.select('#tag')
                    .selectAll('g')
                    .remove();
            //更新面包屑导航栏
            that.updateBreadCrumb(name, that.scaleLevel);
        }
        //已经加载过数据，则直接回调函数
        if (filename in this.loadedData){
            success(this.loadedData[filename]);
        }
        //加载文件
        else{
            d3.json(filename).then(function (jsondata) {
                that.loadedData[filename] = jsondata;
                success(jsondata);
            });
        }
    }

    /**
     * private 私有函数 用于重绘地图
     * @param jsondata 加载成功所获得的json格式的地图数据
     */
    redrawMap(jsondata){
        let that = this;
        //获取中心点和缩放
        let center = getCenter(jsondata.features);
        let zoomScale = getZoomScale(jsondata.features, that.width, that.height);
        this.svg.select('#map').selectAll('path').remove();
        //设置缩放比和中心点
        that.projection.center(center)
            .scale(zoomScale * 45);
        //生成位置及对应的权值 主要用于显示热力图
        let address_weights = this.handleHotSpotData();
        //用于回调updateMapCallback的数据
        let items = [];
        //生成地图
        that.svg.select('#map')
            .selectAll('path')
            .data(jsondata.features)
            .enter()
            .append('path')
            .each(function (d, i) {
                d.weight = 0;
                if (address_weights.has(d.properties.name)){
                    d.weight = address_weights.get(d.properties.name);
                    items.push({'name': d.properties.name, 'selector': this, 'weight': d.weight, 'datum': d});
                }
            })
            .attr('stroke', '#000')
            .attr('stroke-width', 1)
            .attr('fill', function (d, i) {
                return that.mapColor(d.weight);
            })
            .attr('d', that.path)
            .on('mouseover', function (d, i, nodes) {
                that.mouseover(this, d, i)
            })
            .on('mousemove', function (d, i) {
                that.mousemove(this, d, i);
            })
            .on('click', function (d, i) {
                that.clickMap(this, d);
            })
            .on('mouseout', function (d, i) {
                that.mouseout(this, d);
            });
        //回调更新地图钩子函数
        if (items.length > 0)
            this.updateMapCallback(items, 0);
        else{
            this.updateMapCallback(this.getLimitedInstitutions(), 1);
        }
    }

    /**
     * 处理热点数据并返回
     * @return {d3.map}
     */
    handleHotSpotData(){
        //按当前缩放级别给数据分块
        let address_values = new d3.map();
        if (this.institutions.length == 0)
            return address_values;
        //获取国家、省份
        let names = [];
        this.stack.forEach(function (d) {
            names.push(d.name);
        });
        for (let i = 0; i < this.institutions.length; i++){
            let school = this.institutions[i];
            let ret = true;
            //排除部分数据
            for (let j = 0;j < names.length && j < school.address.length; j++){
                if (names[j] != school.address[j]){
                    ret = false;
                    break;
                }
            }
            if (ret == false || this.stack.length >= school.address.length)
                continue;
            //预先添加键值对
            let address = school.address[this.stack.length];
            if (!address_values.has(address)){
                address_values.set(address, 0);
            }
            let weight = address_values.get(address) + school.weight;
            address_values.set(address, weight);
        }
        //获取最大值，并进行规格化处理
        let maxWeight = d3.max(address_values.values());
        address_values.each(function (value, key, map) {
           address_values.set(key, value / maxWeight);
        });
        return address_values;
    }

    getLimitedInstitutions(){
        //筛选对应的学校
        let schools = [];

        if (this.institutions.length == 0)
            return schools;
        this.svg.select('#tag').selectAll('g').remove();
        //获取国家、省份
        let names = [];
        this.stack.forEach(function (d) {
            names.push(d.name);
        });
        this.institutions.forEach(function (d) {
            let ret = true;
            for (let i = 0; i < names.length; i++){
                if (names[i] != d.address[i]){
                    ret = false;
                    break;
                }
            }
            if (ret)
                schools.push(d);
        });
        return schools;
    }
    /**
     * 处理学院数据并返回
     * @returns {Array} 处理好的数组
     */
    handleInstitutions(){
        let schools = this.getLimitedInstitutions();
        //绘制机构
        if (schools.length <= 0)
            return schools;
        //由经纬度转为绘制的实际坐标
        for (let i = 0; i < schools.length; i++){
            schools[i].position = this.projection([schools[i].longitude, schools[i].latitude]);
        }
        //用作判断矩形碰撞的两个变量
        let r1 = {x1:0, y1:0, x2:0, y2:0};
        let r2 = {x1:0, y1:0, x2:0, y2:0};
        let size = 15;
        let positions = [];
        //八方向向外扩散
        let deltas = [[0, 0], [-size, 0], [-size, -size], [0, -size], [size, -size], [size, 0], [size, size], [0, size], [-size, size]];

        for (let i = 0; i < schools.length; i++){
            let pos1 = [schools[i].position[0], schools[i].position[1]];
            if (i == 0)
                positions.push(pos1);
            //判断是否互斥
            let ret = false;
            for (let j = 0;j < positions.length; j++){
                let pos2 = positions[j];
                [r2.x1, r2.y1, r2.x2, r2.y2] = [pos2[0], pos2[1], pos2[0] + size, pos2[1] + size];
                for (let k = 0;k < deltas.length; k++){
                    //修改值，然后判断
                    let temp_x = deltas[k][0];
                    let temp_y = deltas[k][1];
                    [r1.x1, r1.y1] = [pos1[0] + temp_x, pos1[1] + temp_y];
                    [r1.x2, r1.y2] = [r1.x1 + size, r1.y1 + size];
                    //矩形发生碰撞，则更改位置，并再次判断
                    if (intersectRect(r1, r2)){
                        ret = true;
                    }
                    else
                        break;
                }
                //找到一个合适的值，重写给pos1
                if (ret)
                    [pos1[0], pos1[1]] = [r1.x1, r1.y1];
            }
            positions.push(pos1);
            //位置发生变化，则回写
            if (ret){
                schools[i].position = pos1;
            }
        }
        return schools;
    }

    /**
     * 私有函数 绘制学校所在的位置 不过目前并未添加事件
     */
    redrawInstitutions(){
        //获取学校
        let schools = this.handleInstitutions();
        //回调地图更新函数
        //this.updateMapCallback(schools, 1);
        //使用id为tag的g来保存所有的文字
        let group = this.svg.select('#tag')
            .selectAll('g')
            .data(schools)
            .enter()
            .append('g')
            .attr('transform', function (d, i) {
                return 'translate(' + d.position[0] + ',' + d.position[1] + ')';
            });
        //添加图片
        group.append('path')
            .attr('transform', 'scale(0.5,0.5) translate(-20,-52)')
            .attr('d', 'm16.98001,0.50592c-8.560135,0 -15.5,6.160021 -15.5,13.758243c0,7.600051 15.5,33.241746 15.5,33.241746s15.5,-25.641696 15.5,-33.241746c0,-7.598221 -6.9378,-13.758243 -15.5,-13.758243z')
            .attr('stroke-width', '1')
            .attr('fill', 'red');
        //添加数字
        group.append('text')
            .attr('transform', 'translate(-6,-12)')
            .attr('fill', 'white')
            .text(function (d, i) {
                return (i + 1);
            });
        /*
        group.append('circle')
            .attr('r', 4)
            .attr('fill', 'red');
        */
    }
    /**
     * 私有函数 点击面包屑导航 仅仅用于地图回退
     * @param index 点击的导航栏的索引
     */
    clickBreadcrumb(index) {
        //第一次直接显示。若点击的索引和缩放等级相同，则不进行操作
        if (this.visible && this.scaleLevel == index)
            return;
        //显示地图
        this.scaleLevel = index;
        //获取文件的url和名字
        let realpath = this.stack[this.scaleLevel].filename;
        let name = this.stack[this.scaleLevel].name;
        //维护栈
        for (let j = this.stack.length - 1; j >= index; j--)
            this.stack.pop();
        //加载并显示地图，由于点击的时面包屑导航栏，所以不需要更新导航栏显示
        this.loadAndShowMap(realpath, name);
    }

    /**
     * 以text和index索引来更新对应的面包屑导航栏，并隐藏index后续的导航栏
     * @param text {string} 更新导航栏的显示文本
     * @param index {int} 要更新的导航栏索引
     */
    updateBreadCrumb(text, index){
        //更新文本
        if (text != null) {
            this.svg.select('#breadcrumb')
                .selectAll('text')
                .filter(function (d, i) {
                    return index == i;
                })
                .attr('style', 'cursor:pointer')
                .text(text);
        }
        //TODO:style隐藏不需要的文本控件
        this.svg.select('#breadcrumb')
            .selectAll('text')
            .attr('style', function (d, i) {
                if (i > index)
                    return 'display:none';
                else
                    return "cursor: pointer";
            })
    }
    /**
     * 私有函数点击地图块回调函数
     * @param path 指向了path node
     * @param datum DOM对应的数据
     * @param index 选择集的索引
     */
    clickMap(path, datum){
        //超出缩放等级
        if (this.scaleLevel >= this.filepath_list.length - 1)
            return;
        let id = datum.properties.id;
        let filename = '';
        let that = this;
        this.scaleLevel++;
        //TODO:由于文件名问题，故需要加上00
        if (this.scaleLevel == 2)
            filename = id + '00.json';
        else
            filename = id + '.json';
        //隐藏tooltip
        this.mouseout(path, datum);
        //获取url
        let realpath = this.filepath_list[this.scaleLevel] + '/' + filename;
        //加载并展示地图
        this.loadAndShowMap(realpath, datum.properties.name);
    }

    /**
     * 私有函数 用于生成弹出框显示所需要的html格式数据
     * @param path 选定的path
     * @param datum path所对应的数据
     * @returns {string} html格式数据，交给d3渲染
     */
    static getToolTipHTML(path, datum){
        return "<h4>" + datum.properties.name + "</h4>";
    }
    /**
     * 私有函数 鼠标移到地图块回调函数
     * @param path 指向了path
     * @param datum DOM对应的数据
     * @param index 选择集的索引
     */
    mouseover(path, datum, index){
        //鼠标悬浮时设置地图块的透明度
        d3.select(path)
            .style('opacity', 0.2);
        //渐渐显示tooltip
        this.tooltip.transition()
            .duration(200)
            .style('opacity', 0.9);
        //使用函数toolTip填充数据
        this.tooltip.html(ChinaMap.getToolTipHTML(path, datum))
            .style('left', (d3.event.pageX + 'px'))
            .style('top', (d3.event.pageY - 28 + 'px'));
    }
    /**
     * 私有函数 鼠标移动时的回调函数
     * @param path 指向了path
     * @param datum DOM对应的数据
     * @param index 选择集的索引
     */
    mousemove(path, datum, index){
        this.tooltip.style('left', (d3.event.pageX) + 'px')
            .style('top', (d3.event.pageY - 28) + 'px');
    }
    /**
     * 私有函数 鼠标移出地图块回调函数
     * @param path 指向了path
     * @param datum DOM对应的数据
     */
    mouseout(path, datum){
        d3.select(path)
            //.attr('fill', this.mapColor(datum.weight));
            .style('opacity', 1);
        //动画隐藏提示框
        this.tooltip
            .transition()
            .duration(500)
            .style('opacity', 0);
    }
}
