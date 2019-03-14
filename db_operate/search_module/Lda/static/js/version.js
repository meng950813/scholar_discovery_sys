/**
 *  author   ：feng
 *  time     ：2018/5/30
 *  function : 搜索
 */

 /**
 阻止回车的时候表单提交
 */
function ClearSubmit(e) {
    if (e.keyCode == 13) {
        return false;
    }
}
/*
    vue框架
*/
var index;
$(function() {
index= new Vue({
  el : '#app',

  data : function() {
    return {
        version:'',
        k:'',
        url:'',
        topic:'',
        topic_paper:'',
        topic_num:'',
    }
   },
    methods: {
    open:function(event){
        target=$(event.target);
        this.k=target.text();
        this.url="/static/"+this.version+'/'+this.k;
    },
     load:function(){
          params={version:this.version,k:this.k,topic:this.topic}
          var data= {
                data: JSON.stringify(params),
           };
           self=this;
          url="/lodaData"
          $.ajax({
            url:url,
            type:'POST',
            data:data,
            dataType: 'json',
            success:function(data){
                re=data.obj;
                self.topic_paper=re["topic_paper"];
                self.topic_num=re["topic_num"];
            },
            error:function (res) {
            }
        });
     },

    },
     created:function() {
        this.version=$("#version").text();
     },
  });

});