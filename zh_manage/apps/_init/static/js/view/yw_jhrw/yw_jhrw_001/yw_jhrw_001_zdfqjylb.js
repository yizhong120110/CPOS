/**
* 自动发起交易列表
*/
$(document).ready(function() {
    // 渲染表格
    // 平台
    var pt = $("#hidPt").val();
    // 表格初始化后台url
    var url = "/oa/yw_jhrw/yw_jhrw_001/yw_jhrw_001_view/zdfqjylb_data_view";
    // 表格初始化:
    // 不支持多选，没有复选框，无操作区域
    datagrid = $('#dgZdfqjy').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "post",
        singleSelect : true,
        url: url,
        queryParams: {
            pt: pt
        },
        remoteSort: false,
        columns: [[
            { field: 'jyid', title: 'ID', hidden: true },
            { field: 'ywmc', title: '业务名称', width: '21%'},
            { field: 'jym', title: '交易码', width: '15%'},
            { field: 'jymc', title: '交易名称', width: '21%'},
            { field: 'zdfqpz', title: '交易自动发起配置', width: '21%'},
            { field: 'jyzt', title: '交易状态', width: '10%'},
            { field: 'cz', title: '操作', width: '10%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:" onclick = "showHide(\'update\',\'dgZdfqjy\',\''+rowData.jyid+'\',\'winZdfqjyUpd\',\'编辑自动发起交易\');">编辑</a> ';
            } }
        ]]
    });
    // 状态默认选择“请选择”
    $("#selSeaJyzt").combobox('select', '');
    // 主页面 form tab排序
    $("#fmSearch").tabSort();
    // 业务名称
    $("#txtSeaYwmc").next().children().attr("maxlength","100");
    // 交易码
    $("#txtSeaJym").next().children().attr("maxlength","20");
    // 交易名称
    $("#txtSeaJymc").next().children().attr("maxlength","30");
    // 限制自动化配置长度
    $("#txtZdfqjyZdfqpz").next().children().attr("maxlength","100");
    // 翻译操作
    $("#lbtnFy").click(function(e){
        e.preventDefault();
        // 自动发起配置翻译
        zdfqpzFy( 'txtZdfqjyZdfqpz','txtZdfqjyZdfqpzsm' );
    });
    // 给保存按钮定义onclick事件
    $("#lbtnZdfqjySubmit").click(function(e){
        // 取消默认提交事件
        e.preventDefault();
        // 保存提交
        saveSub( 'dgZdfqjy', 'winZdfqjyUpd' );
    });
    // 给取消按钮定义onclick事件
    $("#lbtnZdfqjyCancel").click(function(e){
        // 取消默认提交事件
        e.preventDefault();
        // 关闭编辑窗口
        $("#winZdfqjyUpd").window('close');
    });
});
/**
* 条件查询
* event：时间对象
*/
function doSearch(event){
    // 取消默认提交事件
    event.preventDefault();
    // 平台
    var pt = $("#hidPt").val();
    // 业务名称
    var seaYwmc = $("#txtSeaYwmc").textbox("getValue");
    // 交易码
    var seaJym = $("#txtSeaJym").textbox("getValue");
    // 交易名称
    var seaJymc = $("#txtSeaJymc").textbox("getValue");
    // 交易状态
    var seaJyzt = $("#selSeaJyzt").textbox("getValue");
    // 根据条件查询管理对象
    $("#dgZdfqjy").datagrid('load',{
        pt: pt,
        ywmc: seaYwmc,
        jym: seaJym,
        jymc: seaJymc,
        jyzt: seaJyzt
    });
}
/**
* 编辑自动发起交易
* handle: 操作类型
* dgid：数据表格id
* updid：编辑信息id
* winid：open窗口的win
* wintit：open窗口的title
*/
function showHide( handle, dgid, updid, winid, wintit ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 平台
    var pt = $("#hidPt").val();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jhrw/yw_jhrw_001/yw_jhrw_001_view/zdfqjylb_edit_sel_view",
        data: { 'pt': pt, 'jyid': updid },
        success: function(data){
            // 打开窗口
            newWindow( $( "#" + winid ),wintit,450,340 );
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                pageInit( handle, data )
                // 重新初始化tabindex
                $('#fmZdfqjyUpd').tabSort();
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 请求异常，给用户提示
            errorAjax();
        }
    });
}
/**
*初始化编辑自动发起交易
*/
function pageInit( handle, data ){
    // 编辑对象信息
    var d = data.jyjbxx_dic;
    // 业务名称
    $("#txtZdfqjyYwmc").textbox('setValue', d.ywmc);
    // 业务名称不可编辑
    $('#txtZdfqjyYwmc').textbox('disable');
    // 交易码
    $("#txtZdfqjyJym").textbox('setValue', d.jym);
    $('#txtZdfqjyJym').textbox('disable');
    // 交易名称
    $("#txtZdfqjyJymc").textbox('setValue', d.jymc);
    $('#txtZdfqjyJymc').textbox('disable');
    // crontab配置
    $("#txtZdfqjyZdfqpz").textbox('setValue', d.zdfqpz);
    // crontab配置说明
    $("#txtZdfqjyZdfqpzsm").textbox('setValue', d.zdfqpzsm);
    $("#txtZdfqjyZdfqpzsm").textbox('disable');
    // 状态
    $("#nfsJyzt").get(0).checked = (d.zt=="1");
    // 编辑交易id
    $("#hidJyid").val(d.id);
    // 原内容
    var ynr = "业务名称：" + d.ywmc + "，交易码：" + d.jym + "，交易名称：" + d.jymc +"，crontab配置：" + d.zdfqpz + "，状态：" + d.zt;
    // 原内容赋值
    $("#hidYnr").val( ynr );
    // 原自动发起配置
    $("#hidYzdfqpz").val( d.zdfqpz );
    // 原内容赋值
    $("#hidYzt").val( d.zt );
}
/**
*编辑提交
*/
function saveSub( dgid, winid ){
    // 添加遮罩
    ajaxLoading();
    // 首先判断交易自动发起配置是否为空
    var zdfqpz = $("#txtZdfqjyZdfqpz").textbox("getValue");
    var ret = checkNull( zdfqpz, '自动发起配置', 'txtZdfqjyZdfqpz' );
    // 翻译成功，进行提交操作
    if( ret == true ){
        // 平台
        var pt = $("#hidPt").val();
        // 业务名称
        var ywmc = $( "#txtZdfqjyYwmc" ).val();
        // 交易码
        var jym = $("#txtZdfqjyJym").textbox("getValue");
        // 交易名称
        var jymc = $("#txtZdfqjyJymc").textbox("getValue");
        // 交易状态
        var jyzt = $( "#nfsJyzt" ).get(0).checked ? "1" : "0";
        // 访问url
        url = "/oa/yw_jhrw/yw_jhrw_001/yw_jhrw_001_view/zdfqjylb_edit_view";
        // 提交表单
        $('#' + winid).find('form').form('submit', {
            url: url,
            queryParams: {'pt': pt, 'ywmc': ywmc,'jym': jym,'jymc': jymc, 'jyzt': jyzt },
            onSubmit: function(){
                // 不需要校验信息，直接提交请求
                return true;
            },
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                // 根据反馈结果给用户提示和刷新页面
                afterAjax(data, dgid, winid);
            },
            error: function () {
                // 取消遮罩
                ajaxLoadEnd();
                // 请求异常，给用户提示
                errorAjax();
            }
        });
    }else{
        // 取消遮罩
        ajaxLoadEnd();
    };
}
