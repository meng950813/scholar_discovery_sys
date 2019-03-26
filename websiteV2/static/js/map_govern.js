/**
 * 根据学校数据，整理出ChinaMap02所需要的热力图和标记的数据
 * @param json_data 学校的数据数组 目前仅用到了学校的address 经纬度和学校名称
 * @return ChinaMap2所需要的热力图数据和标记数据
 */
function handle_school_data(json_data) {
    let provinces = {};
    let cities = {};
    let tags = [];
    let maxWeight = 0;

    for (let i = 0; i < json_data.length; i++){
        let datum = json_data[i];
        //省市
        let province = datum['province'];
        let city = datum['city'];
        let weight = datum['score'];
        //添加省份
        if (!(province in provinces)){
            provinces[province] = {float: weight};
        }
        else
            provinces[province].float += weight;
        if (provinces[province].float > maxWeight)
            maxWeight = provinces[province].float;
        //市
        if (!(city in cities))
            cities[city] = [];
        cities[city].push(datum);
    }//end for
    //归一化热力图
    let levels = [1.0, 0.6, 0.4, 0.2];
    for (let i in provinces){
        let datum = provinces[i];
        let weight = datum.float / maxWeight;

        for (let j = 0; j < levels.length; j++){
            if (j == levels.length - 1 || (weight<= levels[j] && weight >= levels[j + 1])){
                datum['float'] = levels[j];
                break;
            }
        }
    }//end for
    //获得标记
    console.log(cities);
    for (let name in cities){
        let schools = cities[name];
        //TODO: 暂时只获取学校的位置
        let tag = {"city": name, latitude:schools[0].latitude, longitude: schools[0].longitude, schools: []};
        for (let i = 0; i < schools.length; i++){
            let school = schools[i];
            tag['schools'].push({name: school['school_name']});
        }
        tags.push(tag);
    }
    return {
        'hot_data': provinces,
        'tag_data': tags,
    }
}

/**
 * 点击某个tag后的回调函数
 * @param tag
 * @param datum tag对应的数据
 * @param index tag的索引
 */
function onTagClicking(tag, datum, index){
    //标记点点击回调函数
    let ret = chinaMap.tagClicking(tag, datum, index);
    if (ret){
        let cityName = datum['city'];
        let schools = datum['schools'];
        //TODO:在此处进行操作
        console.log(cityName, schools);
    }
}
/**
 * 鼠标移动到map或者tag上显示的内容
 * @param {string} type map/tag
 * @param datum 节点/联系对应的数据项
 * @returns {string} 要生成的html字符串
 */
function getToolTip(type, datum){
    let html = null;
    if (type == 'map'){
        html = "<p>" + datum.properties.name + '</p>';
    }
    else if (type == 'tag'){
        html = '<p>' + datum['city'] + '</p>';
    }
    return html;
}


//main
let mapSvg = d3.select('#map');
let chinaMap = new ChinaMap2(mapSvg, 40);
//默认显示中国地图
chinaMap.show();
//设置tag点击回调函数
chinaMap.onTagClicking = onTagClicking;
chinaMap.getToolTipHTMLHook = getToolTip;
//异步回调获得数据
$.ajax({
    url: 'api/school/addressV2',
    data: {'keyword': '计算机', maximum: 5},
    dataType: 'json',
    type: 'POST',
}).done(function (data) {
    console.log(data);
    let handled_data = handle_school_data(data);
    let hot_data = handled_data['hot_data'];
    let tag_data = handled_data['tag_data'];
    //tag_data.push({longitude: 120.986014, latitude: 31.386424, color: '#2b81ff'});
    chinaMap.setHotSpotData(hot_data);
    chinaMap.setTags(tag_data);
    if(data == null){
        console.log('未发现匹配的高校');
    }
});
