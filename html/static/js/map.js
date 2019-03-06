// 百度地图API功能
	var map = new BMap.Map("map",{minZoom:6,maxZoom:19});
    map.centerAndZoom(new BMap.Point(120.63,31.86713), 6);

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
	var points =[
    ];
	var adds = [
        "北京市海淀区颐和园路5号(北京大学)",　　
    "北京市海淀区清华大学(清华大学)",
　　"北京市海淀区中关村大街59号(中国人民大学)",
　　"北京市海淀区学院路37号(北京航空航天大学)",
　　"北京海淀区中关村南大街5号(北京理工大学)",
　　"北京市新街口外大街19号(北京师范大学)",
　　"海淀区中关村南大街27号(中央民族大学)",
    "北京市海淀区清华东路17号(中国农业大学)",
　　"上海市杨浦区邯郸路220号(复旦大学)",
　　"上海市东川路800号(上海交通大学)",
　　"上海市四平路1239号	(同济大学)",
　　"上海市普陀区中山北路3663号(华东师范大学)",
　　"天津市卫津路94号(南开大学)",
　　"天津市南开区卫津路92号(天津大学)",
　　"重庆市沙坪坝区沙正街174号(重庆大学)",
　　"浙江省杭州市西湖区余杭塘路866号(浙江大学)",
　　"南京鼓楼区汉口路22号(南京大学)",
　　"南京市东南大学路2号(东南大学)",
　　"福建省厦门市思明区思明南路422号(厦门大学)",
    "广东省广州市天河区五山路381号(华南理工大学)",
　　"安徽省合肥市金寨路96号(中国科学技术大学)",
　　"西安市友谊西路127号(西北工业大学)",
    "咸阳市杨陵区西北农林科大(西北农林科技大学)",
　　"成都市高新区（西区）西源大道2006号(电子科技大学)",
　　"成都市一环路南一段24号(四川大学)",
　　"中国山东省济南市山大南路27号(山东大学)",
　　"青岛市崂山区松岭路238号(中国海洋大学)",
　　"辽宁省沈阳市和平区文化路三巷11号(东北大学)",
    "辽宁省大连市甘井子区凌工路2号(大连理工大学)",
　　"哈尔滨市南岗区西大直街92号(哈尔滨工业大学)",
　　"广州市新港西路135号(中山大学)",
　　"湖北省武汉市武昌区八一路299号(武汉大学)",
　　"湖北省武汉市洪山区珞喻路1037号(华中科技大学)",
　　"湖南省长沙市麓山南路932号(中南大学)",
　　"湖南省长沙市岳麓区麓山南路麓山门(湖南大学)",
　　"湖南省长沙市开福区德雅路(国防科技大学)",
　　"吉林省长春市前进大街2699号(吉林大学)",
　　"兰州市天水南路222号(兰州大学)"
	];
	addToPoint(adds);
	var collegeadds = [
        "北京市海淀区双清路30号清华大学内(清华大学,建筑学院),116.335979,40.010127",
        "北京市双清路30号清华大学(经济管理学院),116.337825,40.00508",
        "北京市海淀区清华大学-何善衡楼内(土木水利学院),116.337058,40.009361",
        "北京市海淀区双清路30号清华大学(公共管理学院),116.337975,40.004456",
        "双清路30号清华大学(马克思主义学院),116.327709,40.011861"
    ];
    if(!isSupportCanvas()){
    	alert('热力图目前只支持有canvas支持的浏览器,您所使用的浏览器不能使用热力图功能~')
    }
        heatmapOverlay = new BMapLib.HeatmapOverlay({"radius":20});
        map.addOverlay(heatmapOverlay);
        heatmapOverlay.setDataSet({data:points,max:100});
        heatmapOverlay.show();

    //浏览器定位函数
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

	//显示热力图，监听下拉框变换函数
    function openHeatmap(){
        map.clearOverlays();
        //{"radius":20,"opacity":0, "gradient":{'0.1': 'blue','0.2': 'red','0.3': 'white','0.4':'yellow','0.5':'green'}}
        heatmapOverlay = new BMapLib.HeatmapOverlay({"radius":20});
        map.addOverlay(heatmapOverlay);
        heatmapOverlay.setDataSet({data:points,max:200});
        heatmapOverlay.show();
        position();
        map.centerAndZoom(new BMap.Point(120.63,31.86713), 6);
    }

    //关闭热力图
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
                  var index1 = adds[i].indexOf("(");
                  var string1 = adds[i].substring(0,index1+1);
                  var string2 = adds[i].substring(index+1,adds[i].length+1);
                  console.log(string2);
                  // var string3 = string1 + i +":" + string2;
                  // console.log(string3);
                 geocodeSearch(adds[i]);
              }
          }
          if(map.getZoom()>14){
              delPoint();

              for(var i=0;i<collegeadds.length;i++){
                collegegeocodeSearch(collegeadds[i]);
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

 //将地址转换为经纬度
    function addToPoint(add)
    {
        for(var j=0;j<add.length;j++) {
            myGeo.getPoint(add[j], function (point) {
                points.push({"lng":point.lng,"lat":point.lat,"count":j*5});
            })
        }
    }

    //增加标签
	function bdGEO(){
        var adda = adds[index];
        geocodeSearch(adda);
        index++;
    }


    //增加学校标签
	function geocodeSearch(add){
        //显示标签速度
        if(index < adds.length){
		    setTimeout(window.bdGEO,0);
        }
		myGeo.getPoint(add, function(point){
            console.log(add,point)

			if (point) {

                // point = uniquePoint(point);

				var address = new BMap.Point(point.lng, point.lat);

			    if(add.substring(add.length-3,add.length-1) == "大学") {
                    var index = add.indexOf("(");
                    add = add.substring(index + 1, add.length - 1);
                }
				var label = new BMap.Label(add,{offset:new BMap.Size(20,-10)});
				addMarker(address,label);
			}
		},)
	}

    //增加学院标签
	function collegegeocodeSearch(add){
        //显示标签速度
        if(index < collegeadds.length){
		    setTimeout(window.bdGEO,0);
        }
        //双清路30号清华大学(马克思主义学院),116.327709,40.011861
        var index1 = add.indexOf(")");
        var index2 = add.lastIndexOf(",");
        var lng = add.substring(index1+2,index2);
        var lat = add.substring(index2+1,add.length);
        var point = new BMap.Point(lng,lat);
        add = add.substring(0,index1+1);
        var label = new BMap.Label(add,{offset:new BMap.Size(20,-10)});
        label.addEventListener("mousedown",attribute);
        addMarker(point,label);
	}

	//添加地图标签
	function addMarker(point,label){
		var marker = new BMap.Marker(point);
		//marker.addEventListener("mousedown",attribute);
		map.addOverlay(marker);
		//标签跳动
		//marker.setAnimation(BMAP_ANIMATION_BOUNCE);

		marker.setLabel(label);
	}



	//删除地图所有覆盖物
	function delPoint() {
        var allOverlay = map.getOverlays();

		for (var i = 0; i < allOverlay.length; i++)
		    {
		        map.removeOverlay(allOverlay[i]);
            }
    }



    //学院信息展示
    function attribute(e){
	    //  var styleElement = document.getElementById('ly');
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
