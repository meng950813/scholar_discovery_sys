/**
 * author: xiaoniu
 * date: 2019-03-18
 */

//获取地图的中心
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
 * 显示中国地图的类，依赖于d3.js
 * 需要额外的css #tooltip 其position必须为absolute
 * 地图块保存在id为map的g标签中
 * 标注保存在id为tag的g标签中
 */
class ChinaMap2 {
    /**
     * 构造函数
     * @param svg 地图所需要的画布svg，其必须包含width和height两个参数
     * @param scale 缩放比，会影响显示的地图的大小
     */
    constructor(svg, scale){
        this.svg = svg;
        //地图缩放常数
        this.scale = scale == null? 40: scale;
        //获取宽度和高度
        this.width = this.svg.attr('width');
        this.height = this.svg.attr('height');
        //所有的地图都在一个group组中
        this.group = this.svg.append('g');
        //为svg添加缩放功能
        let that = this;
        this.svg.call(d3.zoom()
            .scaleExtent([0.3, 4])
            .on('zoom', function () {
                let transform = d3.event.transform;
                that.group.attr('transform', transform);
            }))
            .on('dblclick.zoom', null);
        //所有的地图都放在id为map的g标签中
        this.group.append('g').attr('id', 'map');
        //所有的地图标记都在id为tag的g标签中
        this.group.append('g').attr('id', 'tag');
        //投影函数 用于将GeoJson映射到像素
        this.projection = d3.geoMercator()
            .translate([this.width / 2, this.height / 2]);
        //地理路径生成器
        this.path = d3.geoPath()
            .projection(this.projection);
        //保存已经加载过的文件数据，有则不再获取
        this.loadedData = {};
        //提示框
        this.tooltip = d3.select('body')
            .append('div')
            .attr('id', 'tooltip');
        //地图颜色 [0,1]映射到['#ffffcc', '#800026']
        this.mapColor = d3.interpolate('#ffffcc', '#800026');
        //获取地图数据的url
        this.api_path = '/api/mapdata/mapping/';
        //异步加载地图数据，用于标记当前地图是否加载成功
        this.isLoadingData = false;
        //暂存标记点数据
        this.tagData = null;
        //暂存热力图数据
        this.hotSpotData = null;
        //暂时存储当前选中的标记
        this.selectedTag = null;
        //暂时存储当前选中索引
        this.selectIndex = null;
    }


    /**
     * 重写函数 标记鼠标移动回调函数
     * @param tag 标记点group，一般外部不进行操作
     * @param datum tag所对应的数据
     * @param index tag所在的索引
     */
    onTagMouseOver(tag, datum, index){
        this.tagMouseOver(tag, datum, index);
    }

    /**
     * 重写函数 鼠标移出标记回调函数
     * @param tag 标记点group，一般外部不进行操作
     * @param datum tag所对应的数据
     * @param index tag所在的索引
     */
    onTagMouseOut(tag, datum, index){
        this.tagMouseOut(tag, datum, index);
    }

    /**
     * 重写函数 鼠标点击标记回调函数
     * @param tag 标记点group，一般外部不进行操作
     * @param datum tag所对应的数据
     * @param index tag所在的索引
     */
    onTagClicking(tag, datum, index){
        let ret = this.tagClicking(tag);
    }

    /**
     * 公有函数 根据范围显示地图
     * @param scope 默认显示中国地图，scope = ['中国', '北京市']则显示北京地图
     */
    show(scope = null){
        //默认显示中国地图
        if (scope == null){
            scope = ['中国'];
        }
        //转换成所需要的键
        let key = scope.join(',');
        //设置当前未加载数据
        this.isLoadingData = false;
        this.selectedTag = null;
        //加载并显示地图
        this.loadAndShowMap(key);
    }

    selectTag(index){
        //地图未加载成功，则延迟设置热力图
        let that = this;
        if (!this.isLoadingData){
            this.selectIndex = index;
            return ;
        }
        let g =this.group.select('#tag').selectAll('g').filter(function (d, i) {
            return i == index;
        });
        if (g != null){
            g.select('path').each(function (d, i) {
                that.onTagClicking(this, d, i);
            });
        }
    }

    /**
     * 公有函数 设置地图上的标记点,会先删除原先的标记点，然后再生成
     * @param tags 标记点数组 每个数据项必须含有longitude和latitude
     */
    setTags(tags){
        //地图未加载成功，则延迟设置热力图
        if (!this.isLoadingData){
            this.tagData = tags;
            return ;
        }
        let that = this;
        //先移除原先的显示
        this.group.select('#tag').selectAll('g').remove();
        //由经纬度转为绘制的实际坐标
        for (let i = 0; i < tags.length; i++){
            tags[i].position = this.projection([tags[i].longitude, tags[i].latitude]);
        }
        //每个标记点都是一个group标签，方便以后显示
        let group = this.group.select('#tag')
            .selectAll('g')
            .data(tags)
            .enter()
            .append('g')
            .attr('transform', function (d) {
                return 'translate(' + d.position[0] + ',' + d.position[1] + ')';
            });
        //添加标记点
        group.append('path')
            .attr('transform', 'scale(0.5,0.5) translate(-20,-52)')
            .attr('d', 'm16.98001,0.50592c-8.560135,0 -15.5,6.160021 -15.5,13.758243c0,7.600051 15.5,33.241746 15.5,33.241746s15.5,-25.641696 15.5,-33.241746c0,-7.598221 -6.9378,-13.758243 -15.5,-13.758243z')
            .attr('stroke-width', '1')
            .attr('fill', function (d) {
                if (d.color != undefined)
                    return d.color;
                return '#FF0000';
            })
            .on('click', function (d, i) {
                that.onTagClicking(this, d, i);
            })
            .on('mouseover', function (d, i) {
                that.onTagMouseOver(this, d, i);
            })
            .on('mouseout', function (d, i) {
                that.onTagMouseOut(this, d, i);
            });
        //TODO:添加文本
    }

    /**
     * 公有函数 设置热力图,只是更新了图块的颜色
     * @param data 字典，如data['北京市'] = {'float': 1} float 范围为[0,1]
     */
    setHotSpotData(data){
        //地图未加载成功，则延迟设置热力图
        if (!this.isLoadingData){
            this.hotSpotData = data;
            return;
        }
        //进行更新
        this.group.select('#map')
            .selectAll('path')
            .each(function (d) {
                d.float = 0;
                if (d.properties.name in data){
                    d.float = data[d.properties.name].float;
                }
            })
            .attr('fill', d => this.mapColor(d.float));
    }

    /**
     * 可重写函数 用于生成弹出框显示所需要的html格式数据
     * @param type 当前点击的类型
     * @param datum path所对应的数据
     * @returns {string} html格式数据，交给d3渲染
     */
    getToolTipHTMLHook(type, datum){
        return "<h4>" + datum.properties.name + "</h4>";
    }

    /**
     * 私有函数 加载地图文件，并尝试显示地图和文本标签
     * @param map_name 要加载的地图完整名 如 中国 中国,江苏
     */
    loadAndShowMap(map_name) {
        let that = this;
        //已经加载过该文件，则直接回调函数
        if (map_name in this.loadedData){
            this.loadDataSuccess(this.loadedData[map_name]);
        }
        //加载文件
        else{
            let url = this.api_path + map_name;
            d3.json(url).then(function (jsondata) {
                that.loadedData[map_name] = jsondata;
                that.loadDataSuccess(jsondata);
            });
        }// end else
    }

    /**
     * 私有函数 加载文件成功回调函数
     * @param json_data 地图数据
     */
    loadDataSuccess(json_data){
        //若是空数组，则直接退出
        if (json_data.length == 0) {
            return;
        }
        //重新绘制地图
        this.redrawMap(json_data);
        this.isLoadingData = true;
        //地图加载完成后，尝试绘制热力图和标记
        if (this.tagData){
            this.setTags(this.tagData);
            this.tagData = null;
        }
        if (this.hotSpotData){
            this.setHotSpotData(this.hotSpotData);
            this.hotSpotData = null;
        }
        //选中标记
        if (this.selectIndex){
            this.selectedTag(this.selectIndex);
            this.selectIndex = null;
        }
    }

    /**
     * 私有函数 用于重绘地图
     * @param jsondata 加载成功所获得的json格式的地图数据
     */
    redrawMap(jsondata){
        let that = this;
        //获取中心点和缩放
        let center = getCenter(jsondata.features);
        let zoomScale = getZoomScale(jsondata.features, this.width, this.height);
        //绘制前先删除原来的所有地图块
        this.group.select('#map').selectAll('path').remove();
        //设置缩放比和中心点
        this.projection.center(center)
            .scale(zoomScale * this.scale);
        //生成地图
        this.group.select('#map')
            .selectAll('path')
            .data(jsondata.features)
            .enter()
            .append('path')
            .attr('stroke', '#000')
            .attr('stroke-width', 1)
            .attr('fill', d => that.mapColor(0))
            .attr('d', this.path)
            .on('mouseover', function (d, i) {
                that.mouseover(this, d, i);
            })
            .on('mousemove', function (d, i) {
                that.mousemove(this, d, i);
            })
            .on('click', function (d) {
            })
            .on('mouseout', function (d) {
                that.mouseout(this, d);
            });
    }

    /**
     * 私有函数 鼠标移到地图块回调函数
     * @param path 指向了path
     * @param datum DOM对应的数据
     * @param index 选择集的索引
     */
    mouseover(path, datum, index){
        //鼠标悬浮时设置地图块的透明度
        d3.select(path).style('opacity', 0.5);
        //显示文本
        let html = this.getToolTipHTMLHook('map', datum);
        setVisibleOfToolTip(this.tooltip, true, html);
    }

    /**
     * 私有函数 鼠标移动时的回调函数
     * @param path 指向了path
     * @param datum DOM对应的数据
     * @param index 选择集的索引
     */
    mousemove(path, datum, index){
        setVisibleOfToolTip(this.tooltip, true);
    }

    /**
     * 私有函数 鼠标移出地图块回调函数
     * @param path 指向了path
     * @param datum DOM对应的数据
     */
    mouseout(path, datum){
        d3.select(path).style('opacity', 1);
        //动画隐藏提示框
        setVisibleOfToolTip(this.tooltip, false);
    }

    /**
     * 鼠标覆盖标记点回调函数，更改了该点的颜色
     * @param tag d3可使用的对象
     * @param datum 标记对应的数据
     * @param index 标记所在的索引
     */
    tagMouseOver(tag, datum, index){
        d3.select(tag).attr('fill', '#2b81ff');
        //显示文本
        let html = this.getToolTipHTMLHook('tag', datum);
        setVisibleOfToolTip(this.tooltip, true, html);
    }

    /**
     * 鼠标移出标记点回调函数，更改了该点的颜色
     * @param tag d3可使用的对象
     * @param datum 标记对应的数据
     * @param index 标记所在的索引
     */
    tagMouseOut(tag, datum, index){
        if (this.selectedTag == tag)
            return ;
        d3.select(tag).attr('fill', '#FF0000');
        setVisibleOfToolTip(this.tooltip, false);
    }

    /**
     * 鼠标点击标记点回调函数，更改了该点的颜色
     * @param tag d3可使用的对象
     * @return {boolean} 切换选中点成功时则返回true，否则返回false
     */
    tagClicking(tag){
        //选中了同一个,不进行操作
        if (this.selectedTag != null && this.selectedTag == tag)
            return false;
        if (this.selectedTag != null)
            d3.select(this.selectedTag).attr('fill', '#FF0000');
        this.selectedTag = tag;
        d3.select(this.selectedTag).attr('fill', '#2b81ff');

        return true;
    }
}
