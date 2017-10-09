/**
* 交易监控列表
*/
$(document).ready(function() {
    // 渲染表格
    // 平台
    var pt = $("#hidPt").val();
    // 默认交易日期
    var jyrq = $("#dateSeaJyrq").datebox("getValue");
    // 表格初始化后台url
    var url = "/oa/yw_jyczjk/yw_jyczjk_001/yw_jyczjk_001_view/data_view";
    // 表格初始化:
    // 不支持多选，没有复选框，无操作区域
    datagrid = $('#dgJyczjk').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : false,
        method: "post",
        singleSelect : true,
        url: url,
        queryParams: {
            pt: pt,
            jyrq: jyrq
        },
        remoteSort: false,
        columns: [[
            { field: 'ylsh', title: '交易流水号', width: '7%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:" onclick = "select_log(\''+rowData.ylsh+'\',\''+ rowData.jymc + '\',\''+ rowData.jyrq + '\');">' + value +'</a> ';
            } },
            { field: 'czlsh', title: '冲正流水号', width: '7%' , formatter: function(value,rowData,rowIndex) {
                if( value != null ){
                    return '<a href="javascript:" onclick = "select_log(\''+rowData.czlsh+'\',\'冲正交易['+ rowData.jymc + ']\',\''+ rowData.jyrq + '\');">' + value +'</a> ';
                }else{
                    return '';
                }
            } },
            { field: 'jyrqsj', title: '交易时间', width: '10%', align:'center', formatter: function(value,rowData,rowIndex) {
                return rowData.jyrq + ' ' + rowData.jysj;
            }},
            { field: 'jymc', title: '交易名称', width: '21%'},
            { field: 'jym', title: '交易编码', width: '8%'},
            { field: 'cs', title: '冲正次数', width: '7%'},
            { field: 'czwz', title: '冲正位置', width: '7%', halign: 'center', align:'right', formatter: function(value,rowData,rowIndex) {
                if( value > 0 ){
                    return '<a href="javascript:" onclick = "czbzLst(\''+rowData.ylsh+'\',\''+ rowData.jymc + '\',\''+ rowData.jyrq + '\');">&nbsp;' + value +'&nbsp;</a> ';
                }else{
                    return value;
                }
            }},
            { field: 'ylsztmc', title: '原交易状态', width: '10%' },
            { field: 'ztmc', title: '冲正流水状态', width: '10%' },
            { field: 'jysl', title: '操作', width: '11%', halign: 'center', align:'center', formatter: function(value,rowData,rowIndex) {
                if( rowData.zt =='9' && ['10', '88', '98'].indexOf(rowData.ylszt) != -1 && rowData.jyrq == jyrq.replace(/-/g,'') ){
                    return '<a href="javascript:" onclick = "sgcz(\''+rowData.ylsh+'\',\''+ rowData.jymc + '\',\''+ rowData.jyrq + '\',\''+ rowData.czlsh + '\');">手工冲正</a> ';
                }else{
                    return '';
                }
            }}
        ]],
        onLoadSuccess: function(data) {
            if (data.rows.length > 0) {
                //Utils.mergeCellsByFieldSingle("dgJyjk", "shipCargoNo,shipCargoSeqNo,clientNam,format,ieId,agentNam,cargoNam,cargoMark,materialNam,madeCom,billNum,billWgt,piecesWgt");  
            } else {  
                scrollShow($("#dgJyjk"));
            }
        }
    });
    
    // 状态默认选择“请选择”
    $("#selSeaJyzt").combobox('select', '');
    // 交易名称
    $("#txtSeaJymc").next().children().attr("maxlength","30");
    // 交易码
    $("#txtSeaJym").next().children().attr("maxlength","20");
    // 主页面 form tab排序
    $("#fmSearch").tabSort();
});
/**
* 条件查询
* event：时间对象
*/
function doSearch(event){
    // 取消默认提交事件
    if( event != '' && event != 'undefined' ){
        event.preventDefault();
    }
    // 平台
    var pt = $("#hidPt").val();
    // 交易日期
    var seaJyrq = $("#dateSeaJyrq").datebox("getValue");
    var ret = checkNull2( seaJyrq, '交易日期', 'dateSeaJyrq' );
    if( ret == false ){
        return false;
    }
    // 原流水号
    var ylsh =  $("#txtYlsh").numberbox("getValue");
    // 冲正流水号
    var czlsh =  $("#txtCzlsh").numberbox("getValue");
    // 冲正流水状态
    var seaLszt = $("#selSeaLszt").textbox("getValue");
    // 交易名称
    var seaJymc = $("#txtSeaJymc").textbox("getValue");
    // 交易码
    var seaJym = $("#txtSeaJym").textbox("getValue");
    
    // 根据条件查询管理对象
    $("#dgJyczjk").datagrid('load',{
        pt: pt,
        jyrq: seaJyrq,
        ylsh: ylsh,
        czlsh: czlsh,
        czlshzt: seaLszt,
        jymc: seaJymc,
        jym: seaJym
    });
}

/*
* 查看流程全部日志
*/
function select_log( lsh, jymc, jyrq ){
    // 请求信息：流水号、交易或子流程名称、交易日期
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jyczjk/yw_jyczjk_001/yw_jyczjk_001_view/select_log_view",
        data: {'jyrq': jyrq, 'lsh': lsh},
        success: function(data){
            var title = "[" + jymc +"]日志查看";
            // 打开窗口
            newWindow($("#winRznr"),title, 800, 400);
            // 反馈信息初始化页面
            data = $.parseJSON(data);
            // 获取数据成功
            if( data.state == true ){
                $("#preLcrznr").html( $('<div/>').text(data.rznr).html() );
            }else{
                afterAjax(data, "", "");
            }
        },
        error : function(){
            errorAjax();
        }
    });
}

/**
* 冲正步骤查看
* ylsh: 流水号
* jyrq：交易日期
* jymc：交易名称
*/
function czbzLst( ylsh, jymc, jyrq ){
    newWindow($("#divCzbzWindow"),'[' + jymc + ']-冲正子流程步骤查看',770,301);
    // 反馈信息初始化页面
    $('#dgCzbz').datagrid({
        nowrap : false,
        fitColumns : false,
        method: "post",
        pageSize: 50,
        fit : true,
        pageNumber : 1,
        rownumbers : true,
        pagination: false,
        singleSelect:true,
        url: '/oa/yw_jyczjk/yw_jyczjk_001/yw_jyczjk_001_view/czjyrz_ck_view',
        queryParams: {
            jyrq: jyrq,
            lsh: ylsh
        },
        columns: [[
            { field: 'xh',title: '序号',width: '8%' },
            { field: 'htzlcmc',title: '回退子流程',width: '25%' },
            { field: 'htxx',title: '回退信息',width: '63%' }
        ]]
    });
}

/**
* 手工冲正
* ylsh: 流水号
* jyrq：交易日期
* jymc：交易名称
*/
function sgcz( ylsh, jymc, jyrq, czlsh ){
    // 请求信息：流水号、交易或子流程名称、交易日期
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jyczjk/yw_jyczjk_001/yw_jyczjk_001_view/sgcz_view",
        data: {'jyrq': jyrq, 'lsh': ylsh, 'czlsh': czlsh},
        success: function(data){
            // 反馈信息初始化页面
            data = $.parseJSON(data);
            // 获取数据成功
            afterAjax(data, "dgJyczjk", "");
        },
        error : function(){
            errorAjax();
        }
    });
}



// 每分钟调用一次
function countSecond( ){
    // 查询函数
    doSearch('');
　  setTimeout("countSecond()", 60000);
}
// 初始化调用每分钟调用一次函数
setTimeout("countSecond()", 60000);

/**
* 当没有数据时，数据表格也显示滚动条
*/
function scrollShow(datagrid) {  
    datagrid.prev(".datagrid-view2").children(".datagrid-body").html("<div style='width:" + datagrid.prev(".datagrid-view2").find(".datagrid-header-row").width() + "px;border:solid 0px;height:1px;'></div>");  
}  
