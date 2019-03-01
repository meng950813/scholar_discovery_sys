// �ٶȵ�ͼAPI����
	var map = new BMap.Map("map");
    map.centerAndZoom(new BMap.Point(120.63,31.86713), 6);
	var geolocation = new BMap.Geolocation();
	var user_location
	position();
    function position() {
        if(user_location){
            console.log("user_location:" ,user_location)
            var label = new BMap.Label("����λ��",{offset:new BMap.Size(20,-10)});
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
			var label = new BMap.Label("����λ��",{offset:new BMap.Size(20,-10)});
			addMarker(user_location,label);
		}
	},{enableHighAccuracy: true})
    }
    //���ù���
	//map.enableScrollWheelZoom(true);
    //����˫��
    map.disableDoubleClickZoom();
	/*�Զ����ͼ��ʽhttp://lbsyun.baidu.com/customv2/index.html
	var styleJson = []
	map.setMapStyle({styleJson:styleJson});*/

    var points =[
        {"lng":116.314214,"lat":39.996322,"count":50444}
    ];

    if(!isSupportCanvas()){
    	alert('����ͼĿǰֻ֧����canvas֧�ֵ������,����ʹ�õ����������ʹ������ͼ����~')
    }
    heatmapOverlay = new BMapLib.HeatmapOverlay({"radius":20});
	map.addOverlay(heatmapOverlay);
	heatmapOverlay.setDataSet({data:points,max:100});
	console.log("heatmapOverlay: ",heatmapOverlay)
    heatmapOverlay.show();

	//�Ƿ���ʾ����ͼ
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
	//�ж�������Ƿ�֧��canvas
    function isSupportCanvas(){
        var elem = document.createElement('canvas');
        return !!(elem.getContext && elem.getContext('2d'));
    }


    //��굥���Ŵ�
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
	//�һ���С
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
        "�����к������ú�԰·5��(������ѧ)",
        "�����к������廪��ѧ(�廪��ѧ)",
        "�����к������йش���59��"
	];
	var collegeadds = [
        "���׻�����ѧԷ5��¥",
        "�����к������ú�԰·5�ű�����ѧ(δ��������)",
        "������ѧ����¥"
    ];

	function bdGEO(){
        var adda = adds[index];
        geocodeSearch(adda);
        index++;
    }


	function geocodeSearch(add){
        //��ʾ��ǩ�ٶ�
        if(index < adds.length){
		    setTimeout(window.bdGEO,0);
        }

		myGeo.getPoint(add, function(point){
			if (point) {
			    //�������Ϣ
				//document.getElementById("result").innerHTML +=  index + "��" + add + ":" + point.lng + "," + point.lat + "</br>";
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

	//��ӵ�ͼ��ǩ
	function addMarker(point,label){
		var marker = new BMap.Marker(point);
		//marker.addEventListener("click",attribute);
		map.addOverlay(marker);
		//��ǩ����
		//marker.setAnimation(BMAP_ANIMATION_BOUNCE);
		marker.setLabel(label);
	}

	//��ǩ����¼�

	
	//ɾ����ͼ���б�ǩ
	function delPoint() {
        var allOverlay = map.getOverlays();
        console.log("delPoint: ",allOverlay)
		for (var i = 0; i < allOverlay.length; i++)
		    {
		        map.removeOverlay(allOverlay[i]);
            }
    }