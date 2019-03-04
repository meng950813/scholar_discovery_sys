// 百度地图API功能
	var map = new BMap.Map("map",{minZoom:6,maxZoom:19});
    map.centerAndZoom(new BMap.Point(120.63,31.86713), 6);
    //启用滚轮
	//map.enableScrollWheelZoom(true);
    //禁用双击
    map.disableDoubleClickZoom();
	var geolocation = new BMap.Geolocation();
	var user_location;
	position();
	var points =[
        {"lng":116.314214,"lat":39.996322,"count":50444}
    ];
    if(!isSupportCanvas()){
    	alert('热力图目前只支持有canvas支持的浏览器,您所使用的浏览器不能使用热力图功能~')
    }
    heatmapOverlay = new BMapLib.HeatmapOverlay({"radius":20});
	map.addOverlay(heatmapOverlay);
	heatmapOverlay.setDataSet({data:points,max:100});
    heatmapOverlay.show();

    function position() {
        if(user_location){
            var label = new BMap.Label("您的位置",{offset:new BMap.Size(20,-10)});
            //label.addEventListener("mousedown",attribute);
			addMarker(user_location,label);
			return;
        }
        geolocation.getCurrentPosition(function(r){
		if(this.getStatus() == BMAP_STATUS_SUCCESS){
			//var mk = new BMap.Marker(r.point);
			//var centerPoint = new BMap.Point(r.point.lng, r.point.lat);
            //map.panTo(centerPoint);
			user_location = new BMap.Point(r.point.lng, r.point.lat);
			var label = new BMap.Label("您的位置",{offset:new BMap.Size(20,-10)});
			//label.addEventListener("mousedown",attribute);
			//mk.addEventListener("mousedown",attribute);
			addMarker(user_location,label);
		}
	},{enableHighAccuracy: true})
    }

	/*自定义地图样式http://lbsyun.baidu.com/customv2/index.html
	var styleJson = []
	map.setMapStyle({styleJson:styleJson});*/

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
        "北京市海淀区中关村大街59号(中国人民大学)"
	];
	var collegeadds = [
        "李兆基人文学苑5号楼(北京大学,历史学院)",
        "北京市海淀区颐和园路5号北京大学(北京大学,人文学院)",
        "北京大学及重楼(北京大学,艺术学院)"
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
				var address = new BMap.Point(point.lng, point.lat);
			    if(add.substring(add.length-3,add.length-1) == "大学") {
                    var index = add.indexOf("(");
                    add = add.substring(index + 1, add.length - 1);
                }
				var label = new BMap.Label(add,{offset:new BMap.Size(20,-10)});
			    if(add.substring(add.length-3,add.length-1) == "学院") {
                    label.addEventListener("mousedown", attribute);
                }
				addMarker(address,label);
			}
		},)
	}

	//添加地图标签
	function addMarker(point,label){
		var marker = new BMap.Marker(point);
		//marker.addEventListener("mousedown",attribute);
		map.addOverlay(marker);
		//标签跳动
		//marker.setAnimation(BMAP_ANIMATION_BOUNCE);
        console.log(label);
		marker.setLabel(label);
	}



	//删除地图所有标签
	function delPoint() {
        var allOverlay = map.getOverlays();
        console.log("delPoint: ",allOverlay)
		for (var i = 0; i < allOverlay.length; i++)
		    {
		        map.removeOverlay(allOverlay[i]);
            }
    }

    function attribute(e){
	     var styleElement = document.getElementById('ly');
	     var address = e.target.content;
	     $("#myModal").modal();

        $("#show_info .page-header").html("<h2>机械工程学院 <small>清华大学</small></h2>");


        $("#show_info .lead").html(`
            <p>清华大学机械工程学科建设始于1932年，机械工程学科在国际上享有盛誉，连续多年在QS世界大学排名的机械学科中位列全球前20。</p>
            <p>清华大学机械工程学院拥有一支杰出的人才队伍，其中包括院士13名、千人（含青千）28名、长江学者（含青年长江）23名、杰青/优青21名、万人计划人才2名。</p>
            <p>学院现有多个国家和部委级科研和教学平台，包括5个国家重点实验室：电力系统及发电设备控制和仿真国家重点实验室、水沙科学与水利水电工程国家重点实验室、精密测试技术及仪器国家重点实验室（清华分室）、摩擦学国家重点实验室、汽车安全与节能国家重点实验室。
            </p><p>清华大学机械工程学科建设始于1932年，机械工程学科在国际上享有盛誉，连续多年在QS世界大学排名的机械学科中位列全球前20。</p>
            <p>清华大学机械工程学院拥有一支杰出的人才队伍，其中包括院士13名、千人（含青千）28名、长江学者（含青年长江）23名、杰青/优青21名、万人计划人才2名。</p>
            <p>学院现有多个国家和部委级科研和教学平台，包括5个国家重点实验室：电力系统及发电设备控制和仿真国家重点实验室、水沙科学与水利水电工程国家重点实验室、精密测试技术及仪器国家重点实验室（清华分室）、摩擦学国家重点实验室、汽车安全与节能国家重点实验室。</p>
        `);


    }
