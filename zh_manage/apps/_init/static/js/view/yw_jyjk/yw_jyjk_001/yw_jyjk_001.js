/**
* 交易监控列表
*/
$(document).ready(function() {
    // 渲染表格
    // 平台
    var pt = $("#hidPt").val();
    // 默认交易日期
    var jyrq = $("#dateSeaJyrq").datebox("getValue");
    // 系统系统
    var xtlx = $("#hidXtlx").val();
    var dbjyslHid = false;
    if( xtlx == 'sc' ){
        dbjyslHid = true;
    }
    // 表格初始化后台url
    var url = "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/data_view";
    // 表格初始化:
    // 不支持多选，没有复选框，无操作区域
    datagrid = $('#dgJyjk').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize : 50,
        fitColumns : true,
        method: "post",
        singleSelect : true,
        url: url,
        queryParams: {
            pt: pt,
            jyrq: jyrq
        },
        remoteSort: false,
        columns: [[
            { field: 'lsh', title: '流水号', width: '5%' },
            { field: 'jyrqsj', title: '交易时间', width: '8%', align:'center', formatter: function(value,rowData,rowIndex) {
                return rowData.jyrq + ' ' + rowData.jysj;
            }},
            { field: 'jgdm', title: '机构码', width: '6%'},
            { field: 'ywbm', title: '业务编码', width: '6%'},
            { field: 'ywmc', title: '业务名称', width: '17%'},
            { field: 'jymc', title: '交易名称', width: '13%', formatter: function(value,rowData,rowIndex) {
                if( rowData.czbz == '1' ){
                    value = '冲正交易(' + value + ' 原流水号:' + rowData.ylsh + ')'
                }
                return '<a href="javascript:" onclick = "rzck(\'dgJyjk\',\''+rowIndex+'\');">' + value +'</a> ';
            }},
            { field: 'jym', title: '交易码', width: '8%'},
            { field: 'khzh', title: '卡号/账号', width: '8%'},
            { field: 'shzh', title: '第三方账号', width: '8%'},
            { field: 'fse', title: '发生额', width: '10%', halign: 'center', align:'right',formatter: function(value,row,index){ 
                return accounting.formatNumber(value,2);
            }},
            { field: 'jysl', title: '有效性校验流水', width: '8%', halign: 'center', align:'right', formatter: function(value,rowData,rowIndex) {
                if( value > 0 ){
                    return '<a href="javascript:" onclick = "yxxjylsCk(\''+rowData.lsh+'\',\''+ rowData.jymc + '\',\''+ rowData.jyrq + '\');">' + value +'</a> ';
                }else{
                    return value;
                }
            }},
            { field: 'dbjysl', title: '挡板校验流水', width: '7%', halign: 'center', align:'right', hidden: dbjyslHid, formatter: function(value,rowData,rowIndex) {
                if( value > 0 ){
                    return '<a href="javascript:" onclick = "dbjylsCk(\''+rowData.lsh+'\',\''+ rowData.jymc + '\',\''+ rowData.jyrq + '\');">' + value +'</a> ';
                }else{
                    return value;
                }
            }},
            { field: 'gyh', title: '柜员号', width: '6%'},
            { field: 'ztmc', title: '交易状态', width: '6%', formatter: function(value,rowData,rowIndex) {
                // 状态默认显示红色
                var color_xx = 'red';
                // 当交易执行成功时，显示绿色
                if( rowData.zt == '01' )
                    color_xx = 'green';
                // 当交易异常时，显示警告图标
                if( rowData.zt == '88' )
                    return '<span style="color:red;float:left;">' + value + '</span><div style = "float:left;" class = "icon-warning-left">&nbsp;&nbsp;&nbsp;&nbsp;</div>';
                else
                    return '<span style = "color:'+ color_xx +'">' + value +'</span> ';
            }},
            { field: 'xyxx', title: '响应内容', width: '15%', formatter: function(value,rowData,rowIndex) {
                return rowData.xym + ':' + rowData.xynr;
            }},
            { field: 'jyrq', title: '交易日期', hidden: true },
            { field: 'jyid', title: '交易id', hidden: true }
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
    // 交易名称
    var seaJymc = $("#txtSeaJymc").textbox("getValue");
    // 交易码
    var seaJym = $("#txtSeaJym").textbox("getValue");
    // 流水状态
    var seaLszt = $("#selSeaLszt").combobox("getValue");
    // 机构码
    var seaJgdm = $("#txtSeaJgdm").textbox("getValue");
    // 流水号
    var seaLsh = $("#txtSeaLsh").textbox("getValue");
    // 卡号/账号
    var seaKhzh = $("#txtSeaKhzh").textbox("getValue");
    // 第三方账号
    var seaShzh = $("#txtSeaShzh").textbox("getValue");
    // 柜员号
    var seaGyh = $("#txtSeaGyh").textbox("getValue");
    // 业务编码
    var seaYwbm = $("#selSeaYwbm").combobox("getValue");
    // 根据条件查询管理对象
    $("#dgJyjk").datagrid('load',{
        pt: pt,
        jyrq: seaJyrq,
        jymc: seaJymc,
        jym: seaJym,
        lszt: seaLszt,
        jgdm:seaJgdm,
        lsh: seaLsh,
        khzh:seaKhzh,
        shzh:seaShzh,
        gyh:seaGyh,
        ywbm:seaYwbm
    });
}

/**
* 交易日志查看
* dbId: 数据表格id
* rowIndex：行号
*/
function rzck( dbId, rowIndex ){
    // 获取行信息
    var rowxx = $('#'+dbId).datagrid('getData').rows[rowIndex];
    // 定义url
    // 交易日期、流水号、交易码、流程类型（交易）、流程层级（交易码）、交易名称
    var cs_str = 'jyid=' + rowxx.jyid + '&jyrq=' + rowxx.jyrq + '&lsh=' + rowxx.lsh+ '&jym=' + rowxx.jym + "&lclx=lc&lccj=&jymc=" + rowxx.jymc;
    // 追加窗口
    var obj_win = '<div id="divRzckWindow'+ rowxx.jyid +'" class="easyui-window" style="display:none" data-options="closed:true,collapsible:false,minimizable:false,maximizable:false"> <iframe id="rzckFrame' + rowxx.jyid +'" name="rzckFrame" scrolling="auto"  frameborder="0"  src="##" style="width:100%;height:99.9%;"></iframe></div>'
    $('body').append(obj_win);
    // 最终url
    url = '/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/rzck_view?' + cs_str;
    $('#rzckFrame').attr('src', url );
    newWindow($("#divRzckWindow"),'交易[' + rowxx.jymc + ']日志查看',1030,520);
}

/**
* 有效性校验流水查看
* lsh: 流水号
* jymc：交易名称
*/
function yxxjylsCk( lsh, jymc, jyrq ){
    newWindow($("#divYxxjylsCkWindow"),'交易[' + jymc + ']-接口有效性校验流水查看',920,401);
    // 反馈信息初始化页面
    $('#dgYxxjylsCk').datagrid({
        nowrap : true,
        fitColumns : true,
        method: "post",
        pageSize: 50,
        fit : true,
        pageNumber : 1,
        rownumbers : true,
        pagination: true,
        singleSelect:true,
        url: '/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/yxxjyls_ck_view',
        queryParams: {
            jyrq: jyrq,
            lsh: lsh
        },
        columns: [[
            { field: 'zddm',title: '字段代码',width: 30 },
            { field: 'cd_dfjymc',title: '接口名称',width: 40 },
            { field: 'zdmc',title: '字段名称',width: 40},
            { field: 'jymc',title: '校验名称',width: 40},
            { field: 'jyms',title: '校验描述',width: 50},
            { field: 'jyrq',title: '校验日期时间', align:'center',width: 50},
            { field: 'jyjg',title: '校验结果', width: 30, formatter: function(value,rowData,rowIndex) {
                if( value == '1' )
                    return '成功';
                else
                    return '失败';
            } },
            { field: 'jyjgsm',title: '校验结果说明', align:'center',width: 50},
            { field: 'cd_txbm',title: 'C端通讯编码', align:'center',width: 50}
        ]]
    });
}

/**
* 挡板校验流水查看
* lsh: 流水号
* jymc：交易名称
*/
function dbjylsCk( lsh, jymc, jyrq ){
    // 打开窗口
    newWindow($("#divDbjylsCkWindow"),'交易[' + jymc + ']-挡板校验流水查看',920,401);
    // 反馈信息初始化页面
    $('#dgDbjylsCk').datagrid({
        nowrap : true,
        fitColumns : true,
        method: "post",
        pageSize: 50,
        fit : true,
        pageNumber : 1,
        rownumbers : true,
        pagination: true,
        singleSelect:true,
        url: '/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/dbjyls_ck_view',
        queryParams: {
            jyrq: jyrq,
            lsh: lsh
        },
        columns: [[
            { field: 'ysmc',title: '要素名称',width: 40 },
            { field: 'ysz',title: '要素值',width: 40 },
            { field: 'lx',title: '类型',width: 40, formatter: function(value,rowData,rowIndex) {
                if( value == '1' )
                    return '要素';
                else
                    return '返回值';
            } },
            { field: 'dblx',title: '挡板类型',width: 40, formatter: function(value,rowData,rowIndex) {
                if( value == '1' )
                    return '挡板定义';
                else
                    return '测试案例执行步骤';
            } },
            { field: 'cd_txbm',title: 'C端通讯编码',width: 40},
            { field: 'cd_dfjymc',title: 'C端对方交易名称',width: 50}
        ]]
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
