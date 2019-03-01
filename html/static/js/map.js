// 百度地图API功能
	var map = new BMap.Map("map");
    map.centerAndZoom(new BMap.Point(120.63,31.86713), 6);
	var geolocation = new BMap.Geolocation();
	var user_location
	position();
    function position() {
        if(user_location){
            console.log("user_location:" ,user_location)
            var label = new BMap.Label("您的位置",{offset:new BMap.Size(20,-10)});
			addMarker(user_location,label);
			return;
        }
        geolocation.getCurrentPosition(function(r){
            console.log("getCurrentPosition")
		if(this.getStatus() == BMAP_STATUS_SUCCESS){
			//var mk = new BMap.Marker(r.point);
			//var centerPoint = new BMap.Point(r.point.lng, r.point.lat);
            //map.panTo(centerPoint);
			user_location = new BMap.Point(r.point.lng, r.point.lat);
			var label = new BMap.Label("您的位置",{offset:new BMap.Size(20,-10)});
			addMarker(user_location,label);
		}
	},{enableHighAccuracy: true})
    }
    //启用滚轮
	//map.enableScrollWheelZoom(true);
    //禁用双击
    map.disableDoubleClickZoom();
	/*自定义地图样式http://lbsyun.baidu.com/customv2/index.html
	var styleJson = []
	map.setMapStyle({styleJson:styleJson});*/

    var points =[
        {"lng":116.314214,"lat":39.996322,"count":50444}
    ];

    if(!isSupportCanvas()){
    	alert('热力图目前只支持有canvas支持的浏览器,您所使用的浏览器不能使用热力图功能~')
    }
    heatmapOverlay = new BMapLib.HeatmapOverlay({"radius":20});
	map.addOverlay(heatmapOverlay);
	heatmapOverlay.setDataSet({data:points,max:100});
	console.log("heatmapOverlay: ",heatmapOverlay)
    heatmapOverlay.show();

	//是否显示热力图
    function openHeatmap(){
        map.clearOverlays();
        heatmapOverlay = new BMapLib.HeatmapOverlay({"radius":20});
        map.addOverlay(heatmapOverlay);
        heatmapOverlay.setDataSet({data:points,max:100});
        heatmapOverlay.show();
        position();
        map.centerAndZoom(new BMap.Point(120.63,31.86713), 6);
        //console.log(map.getOverlays());
    }
	function closeHeatmap(){
        heatmapOverlay.hide();
    }
	closeHeatmap();
	//判断浏览区是否支持canvas
    function isSupportCanvas(){
        var elem = document.createElement('canvas');
        return !!(elem.getContext && elem.getContext('2d'));
    }


    //鼠标单击放大
    function showInfo(e){
          map.setCenter(new BMap.Point(e.point.lng, e.point.lat));
          map.setZoom(map.getZoom() + 2);
          if(map.getZoom()>11&&map.getZoom()<15){
              closeHeatmap();
              for(var i=0;i<adds.length;i++){
                geocodeSearch(adds[i]);
              }
          }
          if(map.getZoom()>14){
              delPoint();
              for(var i=0;i<collegeadds.length;i++){
                geocodeSearch(collegeadds[i]);
              }
          }
	}
	//右击缩小
	function showInfo1(e){
          map.setCenter(new BMap.Point(e.point.lng, e.point.lat));
          map.setZoom(map.getZoom() - 3);
          if(map.getZoom() >10 && map.getZoom() < 17){
              delPoint();
              for(var i=0;i<adds.length;i++){
                geocodeSearch(adds[i]);
              }
          }
          if(map.getZoom() < 10 ){
              delPoint();
              heatmapOverlay = new BMapLib.HeatmapOverlay({"radius":20});
                map.addOverlay(heatmapOverlay);
                heatmapOverlay.setDataSet({data:points,max:100});
                heatmapOverlay.show();
                position();
          }

	}
	map.addEventListener("click", showInfo);
    map.addEventListener("rightclick", showInfo1);
    var index = 0;
    var myGeo = new BMap.Geocoder();
	var adds = [
        "北京市海淀区颐和园路5号(北京大学)",
        "北京市海淀区清华大学(清华大学)",
        "北京市海淀区中关村大街59号"
	];
	var collegeadds = [
        "李兆基人文学苑5号楼",
        "北京市海淀区颐和园路5号北京大学(未名湖北侧)",
        "北京大学及重楼"
    ];

	function bdGEO(){
        var adda = adds[index];
        geocodeSearch(adda);
        index++;
    }


	function geocodeSearch(add){
        //显示标签速度
        if(index < adds.length){
		    setTimeout(window.bdGEO,0);
        }

		myGeo.getPoint(add, function(point){
			if (point) {
			    //输出点信息
				//document.getElementById("result").innerHTML +=  index + "、" + add + ":" + point.lng + "," + point.lat + "</br>";
				var address = new BMap.Point(point.lng, point.lat);
				var label = new BMap.Label(add,{offset:new BMap.Size(20,-10)});
				addMarker(address,label);
			}
		},)
	}

    function  attribute(e) {
		map.centerAndZoom(new BMap.Point(e.point.lng, e.point.lat), 18);
		map.setZoom(map.getZoom() + 2);
    }

	//添加地图标签
	function addMarker(point,label){
		var marker = new BMap.Marker(point);
		//marker.addEventListener("click",attribute);
		map.addOverlay(marker);
		//标签跳动
		//marker.setAnimation(BMAP_ANIMATION_BOUNCE);
		marker.setLabel(label);
	}

	//标签点击事件

	
	//删除地图所有标签
	function delPoint() {
        var allOverlay = map.getOverlays();
        console.log("delPoint: ",allOverlay)
		for (var i = 0; i < allOverlay.length; i++)
		    {
		        map.removeOverlay(allOverlay[i]);
            }
    }