$(document).ready(function() {
    
    // 渲染表格
    // 准备数据
    var url = "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/data_view?nrlx=" + $("#nrlx").val() + '&ss_idlb=' + $("#ss_idlb").val();
    // 内容类型
    var nrlx = $("#nrlx").val();
    // 通讯名称是否显示
    var txmc_type = true;
    var width_arr = [ '28%', '13%', '18%', '26%', '13%' ];
    if( nrlx == 'tx' ){
        txmc_type = false;
        width_arr = [ '25%', '10%', '15%', '23%', '10%' ];
    }
    // 交易名称是否显示
    var jymc_type = true;
    if( nrlx == 'jy' ){
        jymc_type = false;
        width_arr = [ '25%', '10%', '15%', '23%', '10%' ];
    }
    
    //初始化
    $('#dgDrls').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : false,
        singleSelect: true,
        method: "get",
        remoteSort: false,
        url: url,
        columns: [[
            { field: 'id', title: 'ID',  hidden:true },
            { field: 'txmc', title: '通讯名称',  hidden:txmc_type, width: '15%' },
            { field: 'jymc', title: '交易名称',  hidden:jymc_type, width: '15%' },
            { field: 'czms', title: '导入描述', width: width_arr[0] },
            { field: 'czr', title: '导入人编码', hidden: true },
            { field: 'wjm', title: '文件名' , width: '17%'},
            { field: 'czr_mc', title: '导入人', width: width_arr[1] },
            { field: 'czsj', title: '导入时间', width: width_arr[2], align: 'center' },
            { field: 'bz', title: '备注', width: width_arr[3] },
            { field: 'sfht', title: '操作', width: width_arr[4], formatter: function(value,row,index){
                //可以回退
                var ret_str = '<a href="javascript:;" onclick="javascript:drlsUpd(\''+row.id+'\')">编辑</a>';
                if( value == 'TRUE'){
                    ret_str += ' <a href="javascript:;" onclick="javascript:drlsHt(\''+row.id+'\')">回退</a>';
                }
                return ret_str
            } }
        ]]
    });
    
    // 最大值限制（编辑）
    $("#txtCzms").next().children().attr("maxlength","50");
    $("#txtBz").next().children().attr("maxlength","150");
    // 初始化按钮点击事件(编辑)
    $("#lbtnDrlsSubmit").click(function(e){
        e.preventDefault();
        // 编辑提交
        drlsUpdSub();
    });
    // 取消按钮(编辑)
    $("#lbtnDrlsCancel").click(function (e){
        e.preventDefault();
        $("#divDrlsWindow").window('close');
    });
    
    // 最大值限制（回退）
    $("#txtHtms").next().children().attr("maxlength","50");
    $("#txtHtBz").next().children().attr("maxlength","150");
    $("#txtFhrmm").next().children().attr("maxlength","20");
    // 初始化按钮点击事件( 回退 )
    $("#lbtnHtDrlsSubmit").click(function(e){
        e.preventDefault();
        // 回退提交
        drlsHtSub();
    });
    // 取消按钮( 回退 )
    $("#lbtnHtDrlsCancel").click(function (e){
        e.preventDefault();
        $("#divHtDrlsWindow").window('close');
    });
    
});

//导入历史编辑初始化页面
function drlsUpd( drlsid ){
    var event = event || window.event;
    event.stopPropagation();
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/data_edit_sel_view",
        data: { "drlsid": drlsid },
        success: function(data){
            if( data.state == true ){
                newWindow($("#divDrlsWindow"),'编辑导入历史',500,220);
                $("#hidDrlsid").val( drlsid );
                $("#txtCzms").textbox('setValue',data.czms);
                $('#txtBz').textbox('setValue',data.bz);
                // 重新初始化tabindex
                $('#updForm').tabSort();
            }else{
                //$.messager.alert('提示', data.msg, 'error');
                afterAjax(data, "", "");
            }
        },
        error : function(){
            $.messager.alert('提示', '请求异常，请刷新页面后重试！', 'error');
        }
    });
}

//导入历史编辑提交
function drlsUpdSub(){
    // 添加遮罩
    ajaxLoading();
    // 提交表单
    $('#divDrlsWindow').find('form').form('submit', {
        url: '/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/data_edit_view',
        onSubmit: function(){
            // 校验导入描述
            var czms = $("#txtCzms").textbox("getValue");
            var ret = checkNull( czms, '导入描述', 'txtCzms' );
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
            afterAjax(data, "dgDrls", "divDrlsWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            $.messager.alert('提示','编辑导入历史请求出现异常，请稍后重试','error');
        }
    });
}

//回退页面初始化
function drlsHt( drlsid ){
    var event = event || window.event;
    event.stopPropagation();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/drht_sel_view",
        success: function(data){
            data = $.parseJSON(data);
            if( data.state == true ){
                newWindow($("#divHtDrlsWindow"),'回退确认',500,260);
                $("#hidHtDrlsid").val( drlsid );
                // 复核人
                $('#selFhr').combobox({
                    editable:false,
                    data:data.fhr_lst,
                    valueField:'hydm',
                    textField:'xm'
                });
                //默认选择第一个
                if( data.fhr_lst.length > 0 ){
                    $("#selFhr").combobox('select', $("#selFhr").combobox("getData")[0].hydm);
                }
                // 重新初始化tabindex
                $('#htForm').tabSort();
            }else{
                //$.messager.alert('提示', data.msg, 'error');
                afterAjax(data, "", "");
            }
        },
        error : function(){
            $.messager.alert('提示', '请求异常，请刷新页面后重试！', 'error');
        }
    });

}

//回退提交后台
function drlsHtSub(){
    // 添加遮罩
    ajaxLoading();
    // 提交表单
    var nrlx = $("#nrlx").val();
    $('#divHtDrlsWindow').find('form').form('submit', {
        url: '/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/drht_view',
        queryParams: { "nrlx": nrlx },
        onSubmit: function(){
            // 校验回退描述
            var czms = $("#txtHtms").textbox("getValue");
            var ret = checkNull( czms, '导入描述', 'txtHtms' );
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            } else {
                // 校验复核人
                var fhr = $("#selFhr").textbox("getValue");
                ret = checkNull( fhr, '复核人', 'selFhr' );
            }
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            } else {
               // 校验复核人密码
                var fhrmm = $("#txtFhrmm").textbox("getValue");
                ret = checkNull( fhrmm, '复核人密码', 'txtFhrmm' ); 
            }
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            }
            return ret;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgDrls", "divHtDrlsWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            $.messager.alert('提示','编辑导入历史请求出现异常，请稍后重试','error');
        }
    });
}
