$(document).ready(function() {
    // 渲染表格
    $('#dgTxgl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize : 50,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_txrzck/yw_txrzck_001/yw_txrzck_001_view/data_view",
        remoteSort: false,
        columns: [[
            { field: 'bm', title: '通讯编码', width: 31 },
            { field: 'mc', title: '通讯名称', width: 33 },
            { field: 'fwfx', title: '服务方向id', width: 5, hidden:true },
            { field: 'fwfxmc', title: '服务方向', width: 12, formatter: function(value,rowData,rowIndex) {
                //服务方向 1（客户端） 2（服务端）
                fwfxmc = '客户端'
                if ( rowData.fwfx == '2' )
                    fwfxmc = '服务端'
                return fwfxmc;
            } },
            { field: 'txlx', title: '通讯类型', width: 23 },
            { field: 'txwjmc', title: '通讯对象', width: 25 },
            { field: 'operation', title: '操作', width: 23, formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="selTxRz(event, \''+ rowData.txwjmc +'\', \''+ rowData.mc +'\')">查看日志</a>&nbsp;&nbsp;';
            } }
        ]],
    });
    
    //查看日志
    $("#lbtnCkrz").click(function(e){
        e.preventDefault();
        // 查看日志
        selectRz();
    })
    // 导出日志
    $("#lbtnDcrz").click(function(e) {
        // 剔除原有的右击事件
        e.preventDefault();
        // 导出日志
        dcrz();
    })
    
    // 最大值限制
    $("#txtKssj").next().children().attr("maxlength","6");
    // 最大值限制
    $("#txtJssj").next().children().attr("maxlength","6");
});

/**
* 通讯日志查看弹出框初始化
*/
function selTxRz(event, txwjmc, mc){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    
    mc = '通讯[' + mc + ']日志查看' 
    // 增加窗体
    newWindow($("#divTxglWindow"),mc,555,175);
    $("#txtMc").val(mc);
    $("#txtTxwjmc").textbox("setValue",txwjmc);
    // form tab排序
    $("#divTxglWindow").children('form').tabSort();
    $('#txtKssj').textbox('textbox').attr('placeholder', 'hhmmss');
    $('#txtJssj').textbox('textbox').attr('placeholder', 'hhmmss');
};
/**
* 日志查看
*/
function selectRz(){
    // 添加遮罩
    ajaxLoading();
    // 提交表单
    $('#divTxglWindow').find('form').form('submit', {
        url: '/oa/yw_txrzck/yw_txrzck_001/yw_txrzck_001_view/data_rzck_view',
        onSubmit: function(){
            // 获取校验元素值
            var ret = checkXx();
            // 反馈校验结果
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
            }
            return ret;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            // 反馈信息初始化页面
            data = $.parseJSON(data);
            // 增加窗体
            mc = $("#txtMc").val(); 
            if( data.rz == 'error'){
                $.messager.alert('错误', '查询数据超长，请缩短查询范围', 'error');
            }      
            if( data.state == true ){
                newWindow($("#winRznr"),mc,820,420);
                $("#preLcrznr").html( $('<div/>').text(data.rz).html() );
            }
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
    
}

/*
* 导出日志
*/
function dcrz(){
    // 添加遮罩
    ajaxLoading();
    var jyrq = $("#dateSeaJyrq").textbox("getValue");
    var kssj = $("#txtKssj").numberbox("getValue");
    var jssj = $("#txtJssj").numberbox("getValue");
    var txwjmc = $("#txtTxwjmc").textbox("getValue");
    // 获取校验元素值
    var ret = checkXx();
    // 反馈校验结果
    if( ret == false ){
        // 取消遮罩
        ajaxLoadEnd();
        return false
    }
    // 文档请求url
    downUrl = "/oa/yw_txrzck/yw_txrzck_001/yw_txrzck_001_view/data_rzdc_view?jyrq=" + jyrq + "&kssj=" + kssj + "&jssj=" + jssj + "&txwjmc=" + txwjmc;
    // jquery down
    $.fileDownload(downUrl)
        .done(function () {
            console.log('File download a success!');
            // 取消遮罩
            ajaxLoadEnd();
        })
        .fail(function () {
            $.messager.alert('错误', '导出失败', 'error');
            console.log('File download failed!');
            // 取消遮罩
            ajaxLoadEnd();
        });
}

/**
* 查看提交前台校验
*/
function checkXx(){
    var jyrq = $("#dateSeaJyrq").textbox("getValue");
    var kssj = $("#txtKssj").numberbox("getValue");
    var jssj = $("#txtJssj").numberbox("getValue");
    
    // 交易日期
    ret = checkNull( jyrq, '交易日期', 'dateSeaJyrq' );
    if( ret ){
        ret = checkDate10( jyrq, '交易日期', 'dateSeaJyrq' );
    }
    // 开始时间
    if( ret ){
        ret = checkNull( kssj, '开始时间', 'txtKssj' );
    }
    if( ret ){
        ret = checkInt( kssj, '开始时间', 'txtKssj' );
    }  
    if( ret ){
        ret = checkTime( kssj, '开始时间', 'txtKssj' );
    }    
    // 结束时间
    if( ret ) {
        ret = checkInt( jssj, '结束时间', 'txtJssj' );
    }
    if( ret ){
        if (jssj != ''){
            ret = checkTime( jssj, '结束时间', 'txtJssj' );
        }
    }    
    return ret;
}

/**
* 校验时间格式
*/
function checkTime(eleVal, labelMc, eleId) {
    h = eleVal.substr(0, 2);
    if (!/^([0-2][0-9])([0-5][0-9])([0-5][0-9])$/.test(eleVal)) {
        $.messager.alert('错误', labelMc + '格式不符，正确格式为[hhmmss]', 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    
    if (h >= 24) {
        $.messager.alert('错误', labelMc + '范围错误，请重新输入', 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    return true;
}
