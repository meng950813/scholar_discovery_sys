/**
 * created by chen
 * 2019/3/10
 * 
 *  */

// 弹出窗类型
const ALERT_TYPE = {
    "info" : "info",
    "error" : "error",
    "warning" : "warning",
    "success" : "success",
};


/////////////////////// start of login model //////////////////////////////
$("#submit").on("click",checkLoginForm);

function checkLoginForm(){   
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

    if(checkUsername(name)){
        $.ajax({
            "type" : "post",
            "url" : "/user/dologin",
            "data" : {"username" : name , "password" : password},
            success : function (data) { 
                /**
                 * 若登陆成功，后端重定向到新页面 
                 * 
                 * ==> 若有返回值，则表示请求失败
                 * 此时： data = {'error':True,"msg":"请输入正确的账户或密码"}
                 *  */ 
                console.log(data)
                // data = JSON.parse(data);
                showAlert(data.msg , ALERT_TYPE.error);
            },
            error : function (param) { 
                console.log(param);
                showAlert("请求失败",ALERT_TYPE.error);
            }
        })
    }
}

/**
 * 利用正则表达式判断用户输入是否为 手机号/ 邮箱 / 6-8位 user_id 
 * @param {*} username 用户输入
 * @return true(符合规则) / false(不符合规则)
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

/////////////////////// end of login model //////////////////////////////



//判断校商首页搜索框是否为空
function checkForm1() {

    let keyword = $("#simple-input").val();
    console.log(keyword);
    if(keyword == ""){
        return false;
    }
}




/////////////////////// start of relation operation model //////////////////////////////

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

    
    // 有 记录id , 修改
    if($("#modify-relation-id").val()){
        
        info['id'] = parseInt($("#modify-relation-id").val());
        
        console.log("#modify-relation-id",info);
        $.ajax({
            "url" : "/api/agent/relation",
            "type" : "PUT",
            "dataType" : "json",
            "data" : info,
            success : function(data) { 
                if(data.success){
                    // 隐藏模态框
                    toggleModal("addContractModal" , true);

                    // 显示结果
                    showAlert("操作成功" , ALERT_TYPE.success);
                    
                    // 清空模态框中输入内容
                    clearRelationModal();

                    // 填充新内容到列表中
                    creatAndUpdateRecord(info,$(`#relation_list tr[data-index=${info.id}]`));
                }
                else{
                    showAlert("操作失败，请稍后再试",ALERT_TYPE.error);
                }
            },
            error : function() { 
                showAlert("操作失败，请稍后再试",ALERT_TYPE.error);
            }
        });
    }
    // 创建新记录
    else{
        $.ajax({
            "type" : "post",
            "url" : '/api/agent/relation',
            "dataType" : "json",
            "data" : info,
            success : function (data) { 
                console.log("success , data = " , data);
                if(data.success){
                    // 隐藏模态框
                    toggleModal("addContractModal" , true);
                    
                    // 显示结果
                    showAlert("操作成功",ALERT_TYPE.success);
                    
                    // 清空模态框中输入内容
                    clearRelationModal();
    
                    info['id'] = data.id;
                    // 在关系表格中添加一条数据 & 重新生成关系网络
                    creatAndUpdateRecord(info);
                }
                else{
                    showAlert("操作失败，请稍后再试",ALERT_TYPE.error);
                }
            },
            error : function(){
                showAlert("操作失败，请稍后再试",ALERT_TYPE.error);
            }
        });
    }
});

/**
 * 添加联系列表操作的监听函数
 */
$("#relation_list").on("click",function(e){
    // 获取响应对象 ==> button > td>tr
    let $target = $(e.target);

    // 点击 修改 按钮
    if($target.hasClass("modify-relation")){
        
        // 向模态框中填充数据
        fillModifyDataToModal($target.parent().parent());

        // 显示模态窗
        toggleModal("addContractModal");
    }
    // 点击 删除 按钮
    else if($target.hasClass("delete-relation")){
        // 设置记录id
        $("#relation-id").val($target.parent().parent().attr("data-index"));
        // 显示模态窗
        toggleModal("delRelationModal");
    }
})


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
 * 获取关系表中的数据,结构化为相应格式,填充到 模态框中
 * @param {jquery对象} $tr 需要修改的记录 的 tr 元素
 */
function fillModifyDataToModal($tr){

    // 设置记录id
    $("#modify-relation-id").val($tr.attr("data-index"));
        
    let tds = $tr.children();
    
    $("#name_level_one").val(tds[0].textContent);
    $("#name_level_two").val(tds[1].textContent);
    $("#contract_name").val(tds[2].textContent);
    $("#link_method").val(tds[3].textContent);
    $("#remark").val(tds[4].textContent);
}

/**
 * 清空模态框中内容
 */
function clearRelationModal(){

    $("#contract_name").val("");
    $("#link_method").val("");
    $("#remark").val("");
    $("#modify-relation-id").val("");
}



/**
 * 在联系列表里插入 / 修改 一条新的联系记录
 * @param {*} info 用于填充的数据
 * @param {*} $update_target 修改的目标元素 ==> 将修改后的内容插入其中
 */
function creatAndUpdateRecord(info, $update_target = undefined){
    let relaton_item_obj  = {
        "ID" : info.id,
        "SCHOOL_NAME" : info.level_one,
        "COLLEGE_NAME" : info.level_two,
        "TEACHER_NAME" : info.contract_name
    };

    // 若关系表不为空
    if(GRAPH_DATA){
        // 若本次操作为修改,则需要覆盖修改内容
        if($update_target){
            for(let index = 0 ; index < GRAPH_DATA.length ; index++){
                if(GRAPH_DATA[index].ID == info.id){
                    GRAPH_DATA.splice(index,1,relaton_item_obj);
                    break;
                }
            }
        }
        // 否则直接添加新节点
        else{
            GRAPH_DATA.push(relaton_item_obj);
        }
    }
    // 创建
    else{
        GRAPH_DATA = [relaton_item_obj];
    }

    reloadRelationGraph();

    let tr_start = `<tr data-index="${info.id}">`, tr_end = "</tr>";

    let content = `
        <td>${info.level_one}</td>
        <td>${info.level_two}</td>
        <td>${info.contract_name}</td>
        <td>${info.link_method}</td>
        <td>${info.remark}</td>
        <td>${info.create_time}</td>
        <td>
            <button type="button" class="btn btn-danger delete-relation">删除</button>
            <button type="button" class="btn btn-info modify-relation">修改</button>
        </td>`;


    // 若目标tr不为空,即为修改元素,
    if($update_target){
        $update_target.html(content);
    }

    // $update_target 为空则将新数据 插入到第一行
    else{
        $("#relation_list tr:first").before(tr_start + content + tr_end);
    }
    
}



/**
 * 设置删除联系按钮的点击事件
 */
$("#deleteRelationBtn").on("click",function(){ 
    // 获取记录id
    let relatioin_id = $("#relation-id").val();

    console.log("relatioin_id , ", relatioin_id);

    // id 有效
    if(relatioin_id){
        $.ajax({
            "url" : "/api/agent/relation",
            "type" : "DELETE",
            "data" : {"relation_id" : relatioin_id},
            "dataType" : "json",
            success : function (data) {
                console.log(data,typeof(data),data.success);
                // 返回 {success ：true / false}
                // 隐藏模态框
                toggleModal("delRelationModal",true);
                if(data.success){
                    // console.log("success");
                    showAlert("删除成功",ALERT_TYPE.success);
                    
                    //  隐藏被删除的记录
                    $(`#relation_list tr[data-index=${relatioin_id}]`).hide();

                    // 删除节点，重绘关系网
                    deleteRelationNode(relatioin_id);
                }
                else{
                    showAlert("删除失败", ALERT_TYPE.error);
                }
            }
        })
    }
});


/**
 * 从GRAPH_DATA 中删除节点数据
 * @param {number} id 需要删除的 节点的 ID
 */
function deleteRelationNode(id){
    if(!GRAPH_DATA){
        console.log("节点列表为空，错误操作");
        return false;
    }

    // 确定被删元素的下标
    for(var index = 0 ; index < GRAPH_DATA.length; index++){
        
        if(GRAPH_DATA[index].ID == id){
            // 删除元素
            GRAPH_DATA.splice(index,1);

            // 重绘关系图
            reloadRelationGraph();
        }
    }


}


/**
 * 重绘关系图
 */
function reloadRelationGraph(){
    // self 为全局变量，保存当前用户信息
    // GRAPH_DATA 为全局变量，保存关系信息
    let handled_data = handle_school_agent_relations(self, GRAPH_DATA);
    relationGraph.setData(handled_data);
}

/////////////////////// end of relation operation model //////////////////////////////



/////////////////////// start of public model //////////////////////////////
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
 * 显示 / 隐藏 模态窗
 * @param {string} mod_id 
 */

 /**
  * 显示 / 隐藏 模态窗
  * @param {string} mod_id 需要操作的模态窗id
  * @param {bool} hide 是否隐藏 模态框
  */
function toggleModal(mod_id , hide = false){
    let modal = document.getElementById(mod_id);
    
    // 若找不到对应模态窗
    if(!modal){
        console.log("id 有误，找不到对应模态窗");
        return;
    }

    // 隐藏模态框
    if(hide){
        $(modal).modal("hide");
    }
    // 显示模态窗
    else{
        $(modal).modal();
    }

}


/**
 * 对Date的扩展，将 Date 转化为指定格式的String
 * 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符， 
 * 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字) 
 * 例子： 
 *  (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423 
 *  (new Date()).Format("yyyy-MM-dd hh:mm:ss") ==> 2006-07-02 08:09:04
 *  (new Date()).Format("yyyy-M-d h:m:s")      ==> 2006-7-2 8:9:4
 *  (new Date()).Format("yyyy-MM-dd ")      ==> 2006-7-2
 * 
 */
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

/////////////////////// end of public model //////////////////////////////