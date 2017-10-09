var edtor = undefined
$(document).ready(function() {
    // 渲染表格
    $('#dgDypzlb').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_018/kf_ywgl_018_view/data_view?ywid="+$("#hidYwid").val(),
        remoteSort: false,
        frozenColumns: [[
            { field: 'ck', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: '编号', width: 85,hidden:true },
            { field: 'mblx', title: '模板类型', width: 80 },
            { field: 'mbmc', title: '模板名称', width: 90 },
            { field: 'mbms', title: '模板描述', width: 200 },
            { field: 'czr', title: '操作人', width: 50 },
            { field: 'czsj', title: '操作时间', width: 70, align: "center" },
            { field: 'operation', title: '操作', width: 70, formatter: function(value,row,rowIndex) {
                return '<a href="javascript:;" onclick="javascript:dy_edit(\''+row.id+'\');">编辑</a>';
            } }
        ]],
        toolbar : [ {
            iconCls : 'icon-add',
            text : '新增',
            handler : function() {
                // 增加
                dy_add();
            }
        }, {
            iconCls : 'icon-remove',
            text : '删除',
            handler : function() {
                if(!checkSelected("dgDypzlb")) {
                    return;
                }
                $.messager.confirm("确认", '所选的打印配置删除后将不可恢复，您确定要删除吗？', function (r) {
                    if (r) {
                        // 调用删除方法
                        removechecked();
                    }
                });
            }
        },{
            iconCls : 'icon-up',
            text : '导出打印配置代码',
            handler : function() {
                //导出打印配置代码
                var ywid = $("#hidYwid").val()
                var to_path = 'window.location.href="/oa/kf_ywgl/kf_ywgl_018/kf_ywgl_018_view/index_view?ywid=' + ywid + '"'
                dm_down( 'dgDypzlb', 'dypz', ywid, to_path );
            }
        }
        ]
    });
    
    // 新增/编辑打印配置中的取消按钮
    $('#lbtnDypzCancel').click(function(e){
        e.preventDefault();
        windowCancelFun();
    });
    
    // 最大值限制
    $("#txtMbmc").next().children().attr("maxlength","30");
    $("#txtMbms").next().children().attr("maxlength","25");
    
    // 绑定更新按钮的事件
    $('#lbtnDypzOkAddUpdate').click(function(e){
        e.preventDefault();
        var txtDyid = $('#txtDyid').val();
        if( txtDyid ){
            window_update_func();
        }else{
            window_add_func();
        }
    });
    
});

/**
 * 关闭bean_window中的关闭按钮
 */
function windowCancelFun() {
    $('#divDypzWindow').window('close');
};

/**
*批量删除
*/
function removechecked(){
    // 添加遮罩
    ajaxLoading();
    var checkedItems = $('#dgDypzlb').datagrid('getChecked');
    var ids = new Array();
    $(checkedItems).each(function(index, item){
        ids.push(item["id"]);
    });
    var dymss = new Array();
    $(checkedItems).each(function(index, item){
        dymss.push(item["mbmc"]+':'+item["mbms"]);
    });
    var ywid = $("#hidYwid").val();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_ywgl/kf_ywgl_018/kf_ywgl_018_view/data_del_view",
        data: {"ids":ids.join(","), 'dymss':dymss.join(","), 'ywid':ywid},
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgDypzlb", "");
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

//新增打印配置页面初始化
function dy_add(id) {
    // 向后台查询新增页面需要的参数
    var ywid = $("#hidYwid").val();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_ywgl/kf_ywgl_018/kf_ywgl_018_view/data_add_sel_view",
        data: {"ywid":ywid},
        success: function(data){
            data = $.parseJSON(data);
            if( data.state == true ){
                showHide('add');
                var mblx_bjlx_dic = data.mblx_bjlx_dic
                $("#txtSsyw").textbox('setValue', data.ywmc);
                $('#txtMblx').combobox({
                    editable:false,
                    data:data.mblx_lst,
                    valueField:'bm',
                    textField:'mc',
                    onSelect: function(rec){
                        var hsnr = edtor.getValue();
                        reloadCodeMirror( eval('mblx_bjlx_dic.' + rec.bm), hsnr );
                    }
                });
                
                //初始化模板内容编辑器
                reloadCodeMirror( 'xml', '' );
                // 重新初始化tabindex
                $('#dyform').tabSort();
            }else{
                afterAjax(data,'','')
            }
        },
        error : function(){
            errorAjax();
        }
    });
}

//新增提交
function window_add_func(){
    // 添加遮罩
    ajaxLoading();
    // 出错提示
    var msg = "新增失败，请稍后再试";
    url = "/oa/kf_ywgl/kf_ywgl_018/kf_ywgl_018_view/data_add_view";
    var ywid = $("#hidYwid").val();
    // 提交表单
    var hsnr = edtor.getValue();
    $('#divDypzWindow').find('form').form('submit', {
        url: url,
        queryParams:{'ywid':ywid,'hsnr':hsnr},
        onSubmit: function(){
            var mbmc = $("#txtMbmc").textbox("getValue");
            var mbms = $("#txtMbms").textbox("getValue");
            if (mbmc=="") {
                $.messager.alert('错误','模板名称不可为空，请输入','error', function(){
                    $("#txtMbmc").next().children().focus();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            // 校验模板名称格式
            if( checkBm( mbmc, '模板名称', 'txtMbmc' ) != true ){
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            var mblx = $("#txtMblx").textbox("getValue");
            if (mblx=="") {
                $.messager.alert('错误','模板类型不可为空，请选择','error', function(){
                    $("#txtMblx").next().children().focus();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            if (mbms=="") {
                $.messager.alert('错误','模板描述不可为空，请输入','error', function(){
                    $("#txtMbms").next().children().focus();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            // 校验模板描述格式
            if( checkMc( mbms, '模板描述', 'txtMbms' ) != true ){
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            return true;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgDypzlb", "divDypzWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

//编辑页面初始化
function dy_edit(id) {
    var event = event || window.event;
    event.stopPropagation();
    // 向后台查询打印信息和blob表信息
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_ywgl/kf_ywgl_018/kf_ywgl_018_view/data_edit_sel_view",
        data: {"id":id},
        success: function(data){
            data = $.parseJSON(data);
            if( data.state == true ){
                showHide('update');
                var mblx_bjlx_dic = data.mblx_bjlx_dic
                $("#txtSsyw").textbox('setValue', data.ywmc);
                $("#mbmc_edit").text(data.mbmc);
                $('#txtMblx').combobox({
                    editable:false,
                    data:data.mblx_lst,
                    valueField:'bm',
                    textField:'mc',
                    onSelect: function(rec){
                        var hsnr = edtor.getValue();
                        reloadCodeMirror( eval('mblx_bjlx_dic.' + rec.bm), hsnr );
                    }
                }); 
                $("#txtMbms").textbox('setValue', data.mbms);
                $("#txtBlobid").val(data.blobid);
                $("#txtDyid").val(data.dyid);
                //初始化模板内容编辑器
                reloadCodeMirror( data.bjlx, data.nr );
                
                // 重新初始化tabindex
                $('#dyform').tabSort();
            }else{
                afterAjax(data,'','')
            }
        },
        error : function(){
            errorAjax();
        }
    });
}

// 修改页面“保存“函数
function window_update_func(){
    // 添加遮罩
    ajaxLoading();
    var ywid = $("#hidYwid").val();
    var hsnr = edtor.getValue();
    $('#divDypzWindow').find('form').form('submit', {
        url:'/oa/kf_ywgl/kf_ywgl_018/kf_ywgl_018_view/data_edit_view',
        queryParams:{'hsnr':hsnr,'ywid':ywid},
        dataType : 'html',
        onSubmit: function(){
            var mblx = $("#txtMblx").textbox("getValue");
            if (mblx=="") {
                $.messager.alert('错误','模板类型不可为空，请选择','error', function(){
                    $("#txtMblx").next().children().focus();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            var mbms = $("#txtMbms").textbox("getValue");
            if (mbms=="") {
                $.messager.alert('错误','模板描述不可为空，请输入','error', function(){
                    $("#txtMbms").next().children().focus();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            // 校验模板描述格式
            if( checkMc( mbms, '模板描述', 'txtMbms' ) != true ){
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            return true;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgDypzlb", "divDypzWindow");
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/*
open新增或编辑页面
*/
function showHide(handle) {
    
    // 增加窗体
    if(handle=='add'){
        $("#mbmc_add").show();
        $("#mbmc_edit").hide();
        // 增加窗体
        newWindow($("#divDypzWindow"),'新增打印配置',750,420);
    } else if( handle=='update' ){
        $("#mbmc_add").hide();
        $("#mbmc_edit").show();
        // 增加窗体
        newWindow($("#divDypzWindow"),'编辑打印配置',750,420);
    }
};

//重新初始化代码编辑器的样式
function reloadCodeMirror( codeType, codeValue ){
    //重新初始化编码框样式
    $('.CodeMirror').remove();
    edtor = CodeMirror.fromTextArea(document.getElementById("txtNr"), {
        mode: {
            name: codeType,
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent:true,
        matchBrackets: true,
        autofocus: false
    });
    edtor.setValue(codeValue);
    
}
