
/**
 * 自执行函数，用于设置 #map-d3-container 的高度
 */
(function(){
  var map_height = document.body.clientHeight - 230;

 // 宽高取整
  map_height = parseInt(map_height / 100) * 100;
  map_width = parseInt($("#map-d3-container").width() / 100) *100;

  $("#map-d3-container").height(map_height);
  $("#map-d3-container svg").attr('height',map_height);
  $("#map-d3-container svg").attr('width',map_width);

  console.log($("#map-d3-container svg"));

})();

/**
 * 添加各种响应事件
 */
$(document).ready(function(){

  // 绑定输入框中的 onchange 事件
  $("#simple-input").on("input",onKeywordChange);

   // 绑定输入框中的 onkeydown 事件
   $("#simple-input").on("keydown",onKeyDown);
  
  // 绑定 热点词的 点击事件
  $("#hot-key-list").on("click",search_hot_word);

  // 绑定 联想提示框中 内容的点击事件
  $("#hide-tip").on("click",search_hot_word);


  // 绑定搜索按钮的点击事件
  $("#search-btn").on("click",go_search);


});




// 保存一些标志性变量
var FLAG_VARIABLE = {
  /**
   * 记录每次需要异步获取联想关键字的 setTimeout 函数 
   * 
   * 作用在于可以减少快速输入搜索内容时的 异步请求次数
   */      
  recode_setTimeout : undefined,

  // 保存上次搜索的内容，减少重复搜索
  lastKey : undefined

}


/**
 * 监听 搜索框中 输入内容 的变化
 * @param {*} e javascript 类型，响应事件的受体 --> input
 */
function onKeywordChange(e){

  // 获取搜索框中的内容
  let keyword = $(e.target).val();

  // 若 keyword 为空 
  if(!keyword ){
    // 隐藏联想框
    hideAssociativeWordsArea();
    return;
  }

  // 否则
  // 清空上一个尚未响应的函数
  clearTimeout(FLAG_VARIABLE.recode_setTimeout);
  
  // 设置输入时间间隔为 0.6s 
  FLAG_VARIABLE.recode_setTimeout = setTimeout(getAssociativeWordsByAjax.bind(this),600)
  
}

/**
 * 响应键盘事件 ： 包括 确认 + 删除
 * @param {} event 
 */
function onKeyDown(event){
  let e = event || window.event;
  
  /**响应回车键 且 keyword 不为空，执行搜索任务 */
  if(e.keyCode == 13 && $("#simple-input").val()){
    go_search()
  }
  /**若键入 删除 / 回退 键， 且内容清空，隐藏联想框 */ 
  else if((e.keyCode === 8 || e.keyCode === 46) && !$("#simple-input").val()){
    hideAssociativeWordsArea()
  }
}



/**
 * 通过 ajax 获取搜索框中的联想词
 */
function getAssociativeWordsByAjax (){
  console.log("getAssociativeWordsByAjax")
  // TODO： ajax 获取数据
  
  toggleAssociativeWordsArea();

  // 测试数据
  var associative_words_list = ['社交网络','深度学习','医疗健康','人工智能'];
}




/**
 * 点击搜索热点词 / 联想词
 * @param {*} event ： 点击事件的受体
 */
function search_hot_word(event){
    
  // 获取响应内容
  let key = event.target.innerText;

  // 设置搜索框中的内容
  $("#simple-input").val(key);
  

  go_search()
}
    
    
/**
 * 发送搜索请求
 * return： 
 */
function go_search(){

  
  // 关闭联想提示框
  hideAssociativeWordsArea();

  let keyword = $("#simple-input").val();

  // 若 keyword 为空
  if(!keyword || keyword == FLAG_VARIABLE.lastKey){
    return;
  }

  FLAG_VARIABLE.lastKey = keyword;

  //异步回调获得数据
  $.ajax({
    url: 'api/school/address',
    data: {'keyword': keyword},
    dataType: 'json',
    type: 'POST',
  }).done(function (data) {

    console.log(data);
    
    chinaMap.setData(data);
    chinaMap.showChinaMap();

    if(data == null){
      $("#top_list").html("<h3>无搜索结果</h3>");
    }
  });

  // 标识搜索开始，显示地图
  showMapArea();
    
}


/**
 * 显示 隐藏提示框区域
 */
function toggleAssociativeWordsArea(){
  $("#hide-tip").removeClass("display_none");
}

/**
 *  提示框区域
 */
function hideAssociativeWordsArea() {
  $("#hide-tip").addClass("display_none");
}

/**
 * 显示地图区域
 */
function showMapArea(){
  $("#search-container").addClass("searched");
  $("#map-d3-container").removeClass("display_none");
}



// ------------ajax请求处理返回结果函数-----------------//

/**
 * 处理并渲染返回的联想词数据
 * @param {json} data {{"keyword":'xxx',"key_id":123},....}
 */
function renderAssociativeWords(data){
  let html = ``;
  for(item in data){
    html += `<li data='${item['key_id']}'>${item['keyword']}</li>`;
  }
  
  console.log(html);
  
  // 若 html 为空 ==> ajax 请求返回值为空
  if(!html){
    html = "<h2>暂无数据！<h2>"
  }
  
  $("#hide-tip").html(html);
}



/* *******调用地图部分******* */
//中国地图
let chinaMap = new ChinaMap(d3.select('body').select('svg'));


// //异步回调获得数据
// $.ajax({
//     url: 'api/school/address',
//     data: {'keyword': '计算机'},
//     dataType: 'json',
//     type: 'POST',
// }).done(function (data) {
//     chinaMap.setData(data);
//     chinaMap.showChinaMap();
// });


chinaMap.onUpdateMap = onUpdateMap;
chinaMap.onUpdateBreadCrumb = onUpdateBreadCrumb;
//获得数据项 DOM
let topList = d3.select('#top_list');
let breadCrumb = d3.select('#breadcrumb');
/**
 * 更新地图时会回调该函数，主要用于刷新topList列表的值和回调函数
 * @param items 是一个数组 每一个数据项至少会有一个键为name的名字，有的会有selector 和 weight
 */
function onUpdateMap(items) {
    let update = topList.selectAll('li')
        .data(items)
        .text(function (d, i) {
            return d.name;
        });
    update.enter()
        .append('li')
        .text(function (d, i) {
            return d.name;
        })
        .on('click', function (item) {
            //点击函数使用了chinaMap提供的函数
            let ret = chinaMap.clickMapBlockByItem(item);
        });

    update.exit()
        .remove();
}
/**
 * 以texts来更新对应的面包屑导航栏
 * @param texts {Array} 更新导航栏的显示文本
 */
function onUpdateBreadCrumb(texts){
    console.log(texts);
    let update = breadCrumb.selectAll('li')
        .data(texts)
        .text(function (d) {
            return d;
        });
        update.enter()
        .append('li')
        .text(function (data) {
            return data;
        })
        .attr('style', function (d, i) {
                return "cursor: pointer";
        })
        .on('click', function (d, i) {
            //点击函数使用了chinaMap提供的函数
            chinaMap.clickBreadcrumb(i);
        });
    //删除不必要的数据项
    update.exit()
        .remove();
}
