// 弹出窗类型
const ALERT_TYPE = {
    "info" : "info",
    "error" : "error",
    "warning" : "warning",
    "success" : "success",
} 

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


/**
 * 利用正则表达式判断用户输入是否为 手机号/ 邮箱 / 6-8位 user_id 
 * @param {*} username 
 */
function checkUsername(username){
    // 正则表达式
    let phone = /^\d{11}$/;
    let mail = /^[\d\w_]+@[\d\w]+\.com$/;
    let id = /^\d{6,8}$/

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

    // 设置 2s 后关闭弹出窗
    setTimeout(hideAlert,2500);
}

/**
 * 隐藏弹出窗
 */
function hideAlert(){
    $(".alert-container").removeClass("show-opacity");
}

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
    $(mod_id).modal();

}

/**
 * 自执行函数，用于确定是否需要显示后端传回的登陆错误信息
 */
(function hasMsg(){
    if(document.getElementById("error-msg")){
        showAlert("请输入正确的账户或密码", ALERT_TYPE.error);
    }
})()
