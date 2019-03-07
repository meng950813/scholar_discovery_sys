// 百度地图API功能
var map = new BMap.Map("map", { minZoom: 6, maxZoom: 19 });
map.centerAndZoom(new BMap.Point(120.63, 31.86713), 6);

map.addEventListener("click", showInfo);
map.addEventListener("rightclick", showInfo1);

//启用滚轮,默认关闭
//map.enableScrollWheelZoom(true);
//禁用双击
map.disableDoubleClickZoom();
//获取浏览器定位
var geolocation = new BMap.Geolocation();
var user_location;
var index = 0;
//根据地址获取经纬度
var myGeo = new BMap.Geocoder();
position();


// 全局变量，用于保存热点学校位置。
var HOT_SCHOOL_POINTS = [];
// 全局变量，保存学校地址
var SCHOOL_ADDRESS = [];
// 全局变量，保存学院地址
var COLLEGE_ADDRESS = [];


addToPoint(SCHOOL_ADDRESS);


if (!isSupportCanvas()) {
    alert('热力图目前只支持有canvas支持的浏览器,您所使用的浏览器不能使用热力图功能~')
}
heatmapOverlay = new BMapLib.HeatmapOverlay({ "radius": 20 });
map.addOverlay(heatmapOverlay);
heatmapOverlay.setDataSet({ data: HOT_SCHOOL_POINTS, max: 100 });
heatmapOverlay.show();


//浏览器定位函数
function position() {
    if (user_location) {
        var label = new BMap.Label("您的位置", { offset: new BMap.Size(20, -10) });
        //label.addEventListener("mousedown",attribute);
        addMarker(user_location, label);
        return;
    }
    geolocation.getCurrentPosition(function (r) {
        if (this.getStatus() == BMAP_STATUS_SUCCESS) {
            //var mk = new BMap.Marker(r.point);
            //var centerPoint = new BMap.Point(r.point.lng, r.point.lat);
            //map.panTo(centerPoint);
            user_location = new BMap.Point(r.point.lng, r.point.lat);
            var label = new BMap.Label("您的位置", { offset: new BMap.Size(20, -10) });
            //label.addEventListener("mousedown",attribute);
            //mk.addEventListener("mousedown",attribute);
            addMarker(user_location, label);
        }
    }, { enableHighAccuracy: true })
}

/*自定义地图样式http://lbsyun.baidu.com/customv2/index.html
var styleJson = []
map.setMapStyle({styleJson:styleJson});*/

//显示热力图，监听下拉框变换函数
function openHeatmap() {
    map.clearOverlays();
    //{"radius":20,"opacity":0, "gradient":{'0.1': 'blue','0.2': 'red','0.3': 'white','0.4':'yellow','0.5':'green'}}
    heatmapOverlay = new BMapLib.HeatmapOverlay({ "radius": 20 });
    map.addOverlay(heatmapOverlay);
    heatmapOverlay.setDataSet({ data: HOT_SCHOOL_POINTS, max: 200 });
    heatmapOverlay.show();
    position();
    map.centerAndZoom(new BMap.Point(120.63, 31.86713), 6);
}

//关闭热力图
function closeHeatmap() {
    heatmapOverlay.hide();
}

closeHeatmap();


//判断浏览区是否支持canvas
function isSupportCanvas() {
    var elem = document.createElement('canvas');
    return !!(elem.getContext && elem.getContext('2d'));
}

//鼠标单击放大
function showInfo(e) {
    map.setCenter(new BMap.Point(e.point.lng, e.point.lat));
    map.setZoom(map.getZoom() + 2);
    
    // 判读当前缩放等级，一定程度时取消热力图，显示学校名
    if (map.getZoom() > 11 && map.getZoom() < 15) {
        // 关闭热力图
        closeHeatmap();
        // 定位学校
        for (var i = 0; i < SCHOOL_ADDRESS.length; i++) {
            var index1 = SCHOOL_ADDRESS[i].lastIndexOf("(");
            var string1 = SCHOOL_ADDRESS[i].substring(0, index1 + 1);
            var string2 = SCHOOL_ADDRESS[i].substring(index1 + 1, SCHOOL_ADDRESS[i].length + 1);
            var no = i + 1;
            var string3 = string1 + no + ":" + string2;
            geocodeSearch(string3);
        }
    }
    // 判断缩放等级，显示学院
    if (map.getZoom() > 14) {
        
        // console.log(COLLEGE_ADDRESS);
        
        delPoint();

        for (var i = 0; i < COLLEGE_ADDRESS.length; i++) {
            var order = i + 1;
            collegegeocodeSearch(order , COLLEGE_ADDRESS[i]);
        }
    }
}

//右击缩小
function showInfo1(e) {
    map.setCenter(new BMap.Point(e.point.lng, e.point.lat));
    map.setZoom(map.getZoom() - 2);
    if (map.getZoom() > 11 && map.getZoom() < 15) {
        delPoint();
        for (var i = 0; i < SCHOOL_ADDRESS.length; i++) {
            var no = i + 1;
            geocodeSearch(no + "：" + SCHOOL_ADDRESS[i]);
        }
    }
    if (map.getZoom() < 11) {
        delPoint();
        heatmapOverlay = new BMapLib.HeatmapOverlay({ "radius": 30 });
        map.addOverlay(heatmapOverlay);
        heatmapOverlay.setDataSet({ data: HOT_SCHOOL_POINTS, max: 100 });
        heatmapOverlay.show();
        position();
    }
}


/**
 * 将地址信息转换为经纬度
 * @param {array} adds 学校地址
 */
function addToPoint(adds) {
    for (var j = 0; j < adds.length; j++) {
        myGeo.getPoint(adds[j], function (point) {
            // TODO  set 'count' should be more meaningful
            HOT_SCHOOL_POINTS.push({ "lng": point.lng, "lat": point.lat, "count": j * 500000 });
        })
    }
}



//增加学校标签
function geocodeSearch(add) {
    myGeo.getPoint(add, function (point) {
        // console.log(add, point)

        if (point) {

            var address = new BMap.Point(point.lng, point.lat);
            var index = add.indexOf("(");
            add = add.substring(index + 1, add.length - 1);
            var label = new BMap.Label(add, { offset: new BMap.Size(20, -10) });
            label.addEventListener("mousedown",schooleattribute);
            addMarker(address, label);
        }
    })
}

/**
 * 增加学院定位及标签
 * @param {number} order 序号
 * @param {string} add 地址，格式如下 ： 双清路30号清华大学(马克思主义学院);116.327709,40.011861
 */
function collegegeocodeSearch(order,add) {

    // 结果：["双清路30号清华大学(马克思主义学院)","116.327709,40.011861"]
    var part = add.split(";");
   
    // 结果：["116.327709","40.011861"]
    var point_arr = part[1].split(",");

    var point = new BMap.Point(point_arr[0], point_arr[1]);
    
    var label_name = order + " : " + part[0];

    var label = new BMap.Label(label_name, { offset: new BMap.Size(20, -10) });

    label.addEventListener("mousedown", attribute);
    addMarker(point, label);
}

//添加地图标签
function addMarker(point, label) {
    var marker = new BMap.Marker(point);
    //添加标签响应函数
    //marker.addEventListener("mousedown",attribute);
    map.addOverlay(marker);
    //标签跳动
    //marker.setAnimation(BMAP_ANIMATION_BOUNCE);

    marker.setLabel(label);
}



//删除地图所有覆盖物
function delPoint() {
    var allOverlay = map.getOverlays();

    for (var i = 0; i < allOverlay.length; i++) {
        map.removeOverlay(allOverlay[i]);
    }
}



//学院信息展示
function attribute(e) {
    // 双清路30号(清华大学,马克思主义学院)
    var address = e.target.content;
    
    // ["清华大学","马克思主义学院"]
    var add_arr = address.substring(address.indexOf("(") + 1).split(")")[0].split(',');

    // 发送获取学院简介的ajax请求
    getCollegeInfo(add_arr[0],add_arr[1]);    


}

//点击学校标签使学校地址居中放大
function schooleattribute(e){
    //获取学校地址坐标
    var address = e.target.content.split("：")[1];
    var fulladdress;
    for(var i=0; i< SCHOOL_ADDRESS.length; i++){
        if(SCHOOL_ADDRESS[i].indexOf(address) > 0){
            fulladdress = SCHOOL_ADDRESS[i];
        }
    }
    lng = fulladdress.split(",")[0];
    lat = fulladdress.substring(fulladdress.indexOf(",")+1,fulladdress.indexOf(";"));
    console.log(lng, lat);

    //设置地图中心点
    map.setCenter(new BMap.Point(lng, lat));

    map.setZoom(map.getZoom() + 2);

    // 判读当前缩放等级，一定程度时取消热力图，显示学校名
    if (map.getZoom() > 11 && map.getZoom() < 15) {
        // 关闭热力图
        closeHeatmap();
        // 定位学校
        for (var i = 0; i < SCHOOL_ADDRESS.length; i++) {
            var no = i + 1;
            geocodeSearch(no + "：" + SCHOOL_ADDRESS[i]);
        }
    }
    // 判断缩放等级，显示学院
    if (map.getZoom() > 14) {
        // console.log(COLLEGE_ADDRESS);
        delPoint();
        for (var i = 0; i < COLLEGE_ADDRESS.length; i++) {
            var order = i + 1;
            collegegeocodeSearch(order , COLLEGE_ADDRESS[i]);
        }
    }

}