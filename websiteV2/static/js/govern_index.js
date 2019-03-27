/**
 * 自执行函数，用于设置 图表 的宽高度
 */
(function(){
    
    // 设置 大学实力图 的宽度
    $("#school-chart").attr("width", $(".relation-container").width())
    
    let map_width = $(".map-container").width();
    // 设置 地图 的宽高
    $("#map").attr("width" , map_width).attr("height" , $(".relation-container").height());

    // 设置 关系图 的宽高
    $("#relation-chart").attr("width", map_width).attr("height" , $(".relation-person").height())

    // 设置 对比图 宽高
    $("#school-compare").attr("width" , $(".container").width() - 150 ).attr("height",$(".outer").height() - 180);
})();





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
    console.log(ret,tag,datum,index);
    if (ret){
        let cityName = datum['city'];
        let schools = datum['schools'];
        
        showSchoolInfo(cityName,schools);
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


/**
 * 获取高校信息，加入全局变量
 * @param {array} schools [{school_name: "南京大学",...},....] 
 */
function getSchoolsInfo(schools) { 
    let school_name_arr = [];
    for(let i in schools){
        school_name_arr.push(schools[i]['school_name']);
    }

    //异步回调获得数据
    $.ajax({
        url: 'api/school/scholar_number',
        data: {school_names: school_name_arr},
        dataType: 'json',
        type: 'POST',
    }).done(function (data) {
        // 保存学校间的对比数据(一维数组) & 学校名(一维数组)
        let school_compare_data = [], school_name_list = [];

        // 遍历全部学校， 将学校信息按 school_keys 顺序化
        for(let school_name in data){
            
            let school = data[school_name];
            // 数据暂存数组
            let temp_data_set = [];


            //映射，获取每一列对应的值
            for (let i in scholar_keys){
                temp_data_set.push(school[scholar_keys[i]]);

                // 保存需要对比的参数(重点实验室，重点学科，院士数)
                if(i < 3){
                    school_compare_data.push(school[scholar_keys[i]]);
                }
            }
            // 将学校的数据保存到全局变量
            SCHOOLS_INFO[school_name] = temp_data_set;
            // 保存学校名
            school_name_list.push(school_name);
        }
        
        // 绘制对比图
        drawSchoolCompareChart(school_name_list,school_compare_data);
    });

}


/**
 * 展示某一地区的学校信息
 * @param {string} city 城市名
 * @param {array} schools 学校名 [{name:'xxxx'},...]
 */
function showSchoolInfo(city,schools){
    
    if(schools.length < 1){
        console.log("schools.length < 1");
        return false;
    }
    // 设置城市名
    $("#city-name").text(city);

    // 保存生成的 tag html文件
    let school_btn_list = "";

    // 设置学校 tag
    for(let i in schools){
        let school_name = schools[i].name;
        if( i == 0){
            school_btn_list += `<a class="btn btn-default active" data-name="${school_name}">${school_name}</a>`
        }else{
            school_btn_list += `<a class="btn btn-default" data-name="${school_name}">${school_name}</a>`
        }
    }
    
    $("#school-list").html(school_btn_list);

    drawSchoolChart(schools[0].name);
}

/**
 * 展示某一学校的信息的图表
 * @param {string} school_name 学校名
 */
function drawSchoolChart(school_name){
    if(! school_name in SCHOOLS_INFO){
        // console.log("");
        showAlert("错误的高校名" , ALERT_TYPE.error);
        return false;
    }
    // 设置学校名
    $("#school-name").text(school_name);
    
    // console.log(school_name);

    // console.log(SCHOOLS_INFO[school_name]);
    // 展示学校实力图
    verticalGraph.setData(SCHOOLS_INFO[school_name]);
}


/**
 * 绘制学校关系对比图
 * @param {array} school_name_list 学校名列表
 * @param {array} school_data 学校间数据
 */
function drawSchoolCompareChart(school_name_list,school_data){
    let svg = d3.select("#school-compare");
    
    console.log(school_name_list);

    compareGraph = new HorizontalBarGraph(svg,school_name_list);
    
    // 配置数据及样式
    let json_data = {dataset : school_data, categories : categories};

    console.log(json_data);
    // 填充数据，绘图
    compareGraph.setData(json_data);
}


//main
let mapSvg = d3.select('#map');
let chinaMap = new ChinaMap2(mapSvg, 40);

// 全局变量，用于保存学校数据
let SCHOOLS_INFO = [];

//默认显示中国地图
chinaMap.show();

//设置tag点击回调函数
chinaMap.onTagClicking = onTagClicking;
chinaMap.getToolTipHTMLHook = getToolTip;


////////////////////////////////////
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

    getSchoolsInfo(data);

});
/////////////////////////////////////


//竖柱状图
let verticalSvg = d3.select('#school-chart');
let xTexts = [ "重点实验室", "重点学科","院士","长江学者","杰出青年" ];
var scholar_keys = ['key_laboratory', 'key_subject', 'academician', 'changjiang', 'outstanding'];

let categories = [
    {name: '重点实验室', color: '#5d89a7'},
    {name: '重点学科', color: '#a8c9ff'},
    {name: '院士', color: '#7fbdc4'},
];

// 绘制学校实力图 下标
let verticalGraph = new VerticalBarGraph(verticalSvg, xTexts);
// 绘制学校对比图的对象
let compareGraph = undefined;


// 添加 btn 点击事件
$("#school-list").on("click", function(e){
    e.preventDefault();
    $target = $(e.target);

    // 若点击 btn 元素 且 其中无 active 类 --> 未被选中
    if($target.hasClass("btn") && !$target.hasClass("active")){
        $target.addClass("active").siblings(".active").removeClass("active");
        // 显示学校实力图
        drawSchoolChart($target.attr("data-name"));
    }
})
