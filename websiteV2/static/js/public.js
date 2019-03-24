// 弹出窗类型
const ALERT_TYPE = {
    "info" : "info",
    "error" : "error",
    "warning" : "warning",
    "success" : "success",
};

$("#submit").on("click",checkForm);


function checkForm(){   
    let name = $("#username").val();
    let password = $("#password").val();


    if( name == ""){
        showAlert("用户名不能为空!",ALERT_TYPE.warning);
        return false;
    }

    if(password == ""){
        showAlert("密码不能为空!",ALERT_TYPE.warning);
        return false;
    }

    // if(checkUsername(name)){
    //     $.ajax({
    //         "type" : "post",
    //         "url" : "/user/dologin",
    //         "data" : {"username" : name , "password" : password},
    //         success : function (data) { 
    //             /**
    //              * 若登陆成功，后端重定向到新页面 
    //              * 
    //              * ==> 若有返回值，则表示请求失败
    //              * 此时： data = {'error':True,"msg":"请输入正确的账户或密码"}
    //              *  */ 
    //             console.log(data)
    //             // data = JSON.parse(data);
    //             showAlert(data.msg , ALERT_TYPE.error);
    //         },
    //         error : function (param) { 
    //             console.log(param);
    //             showAlert("请求失败",ALERT_TYPE.error);
    //         }
    //     })
    // }
    

    return checkUsername(name);
    // return true;
}

//判断校商首页搜索框是否为空
function checkForm1() {

    let keyword = $("#simple-input").val();
    console.log(keyword);
    if(keyword == ""){
        return false;
    }
}

/**
 * 利用正则表达式判断用户输入是否为 手机号/ 邮箱 / 6-8位 user_id 
 * @param {*} username 
 */
function checkUsername(username){
    // 正则表达式
    let phone = /^\d{11}$/;
    let mail = /^[\d\w_]+@[\d\w]+\.com$/;
    let id = /^\d{6,8}$/;

    if( phone.test(username) || mail.test(username) || id.test(username)){
        return true;
    }

    showAlert("用户名格式不正确！", ALERT_TYPE.error);

    return false;
}


/**
 * 显示弹出窗，并设置延时关闭
 * @param {*} msg 显示弹出内容
 * @param {*} TYPE 弹出窗类型 ：源于 ALERT_TYPE info,error,warning,success
 */
function showAlert(msg, TYPE){
    
    if(!(TYPE in ALERT_TYPE)){
        console.log("参数有误");
        return;
    }

    $(".alert-container .alert").removeClass().addClass(`alert alert-${TYPE}`).html(msg);

    $(".alert-container").addClass("show-opacity");

    // 设置 2.5s 后关闭弹出窗
    setTimeout(hideAlert,2500);
}

/**
 * 隐藏弹出窗
 */
function hideAlert(){
    $(".alert-container").removeClass("show-opacity");
}


/**
 * 自执行函数，用于确定是否需要显示后端传回的登陆错误信息
 */
(function hasMsg(){
    if(document.getElementById("error-msg")){
        showAlert("请输入正确的账户或密码", ALERT_TYPE.error);
    }
})();


/**
 * 显示模态窗
 * @param {string} mod_id 模态窗id
 */
function showModal(mod_id){
    let modal = document.getElementById(mod_id);
    
    // 若找不到对应模态窗
    if(!modal){
        console.log("id 有误，找不到对应模态窗");
        return;
    }

    // 显示模态窗
    $(modal).modal();

}



/**
 * 添加联系人的模态框提交响应事件
 */
$("#submit-connect").on("click",function(e){
    e.preventDefault();

    // 不能为空的元素的 jQuery 列表
    let not_empty_target_JQ_list = [$("#name_level_one"),$("#name_level_two"), $("#contract_name"),$("#link_method")];

    let info = {
        // "level_one" : $("#name_level_one").val(),
        "level_one" : not_empty_target_JQ_list[0].val(),
        // "level_two" : $("#name_level_two").val(),
        "level_two" : not_empty_target_JQ_list[1].val(),
        // "contract_name" : $("#contract_name").val(),
        "contract_name" : not_empty_target_JQ_list[2].val(),
        // "link_method" : $("#link_method").val(),
        "link_method" : not_empty_target_JQ_list[3].val(),
        "remark" : $("#remark").val(),
        "create_time" : (new Date()).Format("yyyy-MM-dd hh:mm:ss")

    };
    // TODO checkout is there any empty
    if (checkRelationFormEmpty(not_empty_target_JQ_list) ){
        console.log("checkRelationFormEmpty is true");
        return false;
    }

    // $.ajax({
    //     "type" : "post",
    //     "url" :  "/user/createRelationship",
    //     "dataType" : "json",
    //     "data" : info,
    //     success : function (data) { 
    //         console.log("success , data = " , data)
    //         if(data.success){
    //             $("#addContractModal").modal("hide");
                
    //             showAlert("操作成功",ALERT_TYPE.success);
                
    //             clearModal()

    //             info.id = data.id;
    //             creatNewRecord(info);
    //         }
    //         else{
    //             showAlert("操作失败，请稍后再试",ALERT_TYPE.error);
    //         }
    //     }
    // });
});


/**
 * 检查提交内容是否为空
 * @param {array} target_list 需要判断元素的 jquery 样式
 * @return true(has empty) / false(not empty)
 */
function checkRelationFormEmpty(target_list) {
    for(let i in target_list){
        let $target = target_list[i];
        if(!$target.val()){
            console.log("this is $tagert.val : ",$target.attr("id"),$target.val())
            $target.parent().parent().addClass("has-error");
            return true;
        }
        else{
            $target.parent().parent().removeClass("has-error");
        }
    };
    
    return false;
}


/**
 * 清空模态框中的内容
 */
function clearModal(){
    // $("#name_level_one").val("");
    // $("#name_level_two").val("");
    $("#contract_name").val("");
    $("#link_method").val("");
    $("#remark").val("");
}


/**
 * 在联系列表里添加一条新的联系记录
 * @param {object} info 用于填充的数据
 */
function creatNewRecord(info){
    let html = `<tr>
        <td>${info.level_one}</td>
        <td>${info.level_two}</td>
        <td>${info.contract_name}</td>
        <td>${info.link_method}</td>
        <td>${info.remark}</td>
        <td>${info.create_time}</td>
        <td>
            <button type="button" class="btn btn-danger" data ="${info.id}">删除</button>
            <button type="button" class="btn btn-info" data ="${info.id}">修改</button>
        </td>
    </tr>`;

    // 插入到第一行
    $("#contract_list tr:first").before(html);
}



// 对Date的扩展，将 Date 转化为指定格式的String
// 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符， 
// 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字) 
// 例子： 
// (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423 
// (new Date()).Format("yyyy-MM-dd hh:mm:ss") ==> 2006-07-02 08:09:04
// (new Date()).Format("yyyy-M-d h:m:s")      ==> 2006-7-2 8:9:4
// (new Date()).Format("yyyy-MM-dd ")      ==> 2006-7-2
Date.prototype.Format = function (fmt) { 
    let option = {
        "M+": this.getMonth() + 1, //月份 
        "d+": this.getDate(), //日 
        "h+": this.getHours(), //小时 
        "m+": this.getMinutes(), //分 
        "s+": this.getSeconds(), //秒 
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度 
        "S": this.getMilliseconds() //毫秒 
    };

    // 将 y 替换为 具体年份
    if (/(y+)/.test(fmt)){
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    }


    for (var k in option){
        if (new RegExp("(" + k + ")").test(fmt)){
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (option[k]) : (("00" + option[k]).substr(("" + option[k]).length)));
        }
    }
    return fmt;
}



function testInsert() {
    var testData = {
        "level_one" : `$("#name_level_one").val()`,
        "level_two" : `$("#name_level_two").val()`,
        "contract_name" :` $("#contract_name").val()`,
        "link_method" : `$("#link_method").val()`,
        "remark" :` $("#remark").val()`,
        "create_time" : "2019/3/4"
    }
    console.log("in testInsert : ", testData)
    creatNewRecord(testData);
}
