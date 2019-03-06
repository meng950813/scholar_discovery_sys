/**
created by chen
2019/3/3

利用ajax获取数据并填充数据的js文件

本 js 文件依赖jquery文件	
*/


// 全局变量，用于保存闭包后的地址信息
var addressInfo = packageAddress();

/**
 * 发送搜索请求，并将返回的数据填充到页面
 * 
 * 其中返回的json数据格式：
 * 
 * 	{
 * 		"school":[
 * 			{
 * 				"name":'清华大学',
 * 				"address":"北京市海淀区双清路30号"
 * 			},
 * 			...
 * 		],
 * 
 * 		college:[
 * 			{
 * 				'school': '清华大学',
 * 				'institution': '材料学院', 
 * 				'address': '北京市海淀区双清路30号清华园清华大学',
 * 				'position' : "123.123456,123.123456"
 * 			},
 * 			...
 * 		]
 * 	}
 * 
 * @param {string  } search_key : 发送的搜索内容，string类型
 */
function search(search_key,serach_id){

	$.ajax({
		// url: `/api/institution/address?keyword=${search_key}&keyword_id=${serach_id}`,
		url: `/api/institution/address`,
		type: "post",
		data: {"keyword":search_key,"keyword_id":serach_id},
		success: function (response) {
			console.log(response);
			
			formatAddress(response);
			
			adds = addressInfo.getSchoolAdd();
			collegeadds = addressInfo.getCollegeAdd();
		}
	});

}


/**
 * 将搜索返回的学校及地址信息格式化为 如下格式：
 * 
 * 	school_add = ["学校地址(学校名)",....]
 *  college_add = ["学院地址(学校名,学院名),坐标",....]
 * 
 * @param {json} adds_info 返回的数据，格式参考 search 函数
 * 
 * rerun array(school_add,college_add)
 */
function formatAddress(adds_info){
	// 分别保存学校地址信息 及学院地址信息
	var school_add = [] , college_add = [];

	// 解析学校数据
	for(var i in adds_info.school){
		console.log(i);
		var oneSchool = adds_info.school[i];
		
		// 此处信任后端数据 ==> 学校名唯一 ==> 不再判断，直接添加
		school_add.push(`${oneSchool.address}(${oneSchool.name})`);
	}

	for(var i in adds_info.college){
		var oneCollege = adds_info.college[i];
		
		college_add.push(`${oneCollege.address}(${oneCollege.school},${oneCollege.institution});${oneCollege.position}`);
	}
	
	console.log(school_add,college_add);
	// 设置新地址
	addressInfo.setAddress(school_add, college_add);

}




/**
 * 使用闭包封装 地址 数组
 */
function packageAddress() { 
	var school_address = [];
	var college_address = []
	
	return {
		setAddress : function (schoolAddress_info,collegeAddress_info) { 
			school_address = schoolAddress_info;
			college_address = collegeAddress_info;
		},
		
		getSchoolAdd : function () { 
			return school_address;
		},
		
		getCollegeAdd : function () {
			return college_address;
		}
		
	}
}



/**
 * 以下是单元测试区域：
 */

var egdata = {
	"school":[
		{
			"name":'清华大学',
			"address":"北京市海淀区双清路30号"
		},
		{
			"name":'北京大学',
			"address":"北京市海淀区颐和园路5号"
		},
		{
			"name":'中国人民大学',
			"address":"北京市海淀区中关村大街59号"
		},
		{
			"name":'北京理工大学',
			"address":"北京海淀区中关村南大街5号"
		},
		{
			"name":'北京航空航天大学',
			"address":"北京市海淀区学院路37号"
		}
	],

	"college":[
		{
			'school': '清华大学',
			'institution': '公共管理学院', 
			'address': '北京市海淀区双清路30号清华大学',
			'position' : "116.337975,40.004456"
		},
		{
			'school': '清华大学',
			'institution': '马克思主义学院', 
			'address': '双清路30号清华大学',
			'position' : "116.327709,40.011861"
		},
		{
			'school': '清华大学',
			'institution': '机械工程学院', 
			'address': '双清路30号清华大学医学科学楼',
			'position' : "116.324311,40.01068"
		},
		{
			'school': '清华大学',
			'institution': '核能与新能源技术研究院', 
			'address': '北京市海淀区清华大学-何善衡楼内',
			'position' : "116.337058,40.009361"
		},
		{
			'school': '清华大学',
			'institution': '材料学院', 
			'address': '北京市海淀区双清路30号清华园清华大学',
			'position' : "116.330553,40.008631"
		},
	]
}

formatAddress(egdata);

SCHOOL_ADDRESS = addressInfo.getSchoolAdd();
COLLEGE_ADDRESS = addressInfo.getCollegeAdd();
addToPoint(SCHOOL_ADDRESS);