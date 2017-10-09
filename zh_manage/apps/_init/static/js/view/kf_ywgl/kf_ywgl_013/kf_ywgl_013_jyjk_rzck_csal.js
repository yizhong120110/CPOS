$(document).ready(function() {
    var srys = ($('#srys').val()+'');
    var scys = ($('#scys').val()+'');
    var demoid = $('#demoid').val();
    srys = eval('(' + srys + ')');
    scys = eval('(' + scys + ')');
    $("#demo_iframe")[0].src =  "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_demo_view/csal_demo_view?demoid=" + demoid;
    $('#datagrid_srys').datagrid({
        nowrap : false,
        fit : true,
        height: '78px',
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        data: srys,
        remoteSort: false,
        columns: [[
            { field: 'ysdm', title: '输入要素', width: 21 },
            { field: 'ysz', title: '值', width: 79, editor:{
                type:'text'
            }, styler: function() {
                return 'word-break:break-word;';
            },formatter:function(node){
                return $('<div/>').text(node).html().replace(/&lt;\/br&gt;/g,'</br>');
            } }
        ]]
    });
    
    $('#datagrid_scys').datagrid({
        nowrap : false,
        fit : true,
        height: '78px',
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        data:scys,
        remoteSort: false,
        columns: [[
            { field: 'ysdm', title: '期望输出要素', width: 31 },
            { field: 'ysz', title: '值', width: 79, editor:{type:'text'}, styler: function() {
                return 'word-break:break-word;';
            },formatter:function(node){
                return $('<div/>').text(node).html().replace(/&lt;\/br&gt;/g,'</br>');
            } }
        ]]
    });
    
    //处理demo数据是否隐藏
    //调用来源
    var dyly = getUrlParam('dyly'); 
    if( dyly == 'jyjk' ){
        if( $('#lb_busnessTab').tabs('tabs').length == 4 ){
            $('#lb_busnessTab').tabs('close', 3);
        }
    }
    
    $("#demo_add_tab ul").each(function(){
        //$(this).find('.tabs-title').addClass('test');
    });
    
});

// 获取url中的参数
function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg);  //匹配目标参数
    if (r != null) return unescape(r[2]); return null; //返回参数值
}
