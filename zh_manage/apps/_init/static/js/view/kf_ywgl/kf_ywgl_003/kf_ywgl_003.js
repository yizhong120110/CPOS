$(document).ready(function() {
    
    // form tab排序
    $("#divJbxx form").tabSort();
    
    // 渲染表格
    $('#dgJycs').datagrid({
        title: '交易参数设置',
        nowrap : false,
        fit : true,
        height: '150px',
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_003/kf_ywgl_003_view/data_view?jyid=" + $("#hidJyid").val(),
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        frozenColumns: [[
            { field: 'select_box', checkbox: true }
        ]],
        columns: [[
            { field: 'csdm', title: '参数代码', width: '20%' },
            { field: 'value', title: '参数值', width: '20%' },
            { field: 'csms', title: '参数描述', width: '30%' },
            { field: 'zt', title: '状态', width: '13%', formatter: function(value,rowData,rowIndex) {
                return value=="1" ? "启用" : "禁用";
            } },
            { field: 'cz', title: '操作', width: '13%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="showHide(\'update\',\'dgJycs\','+rowIndex+');">编辑</a>';
            } }
        ]],
        toolbar : [
            {
                iconCls : 'icon-add',
                text : '增加',
                handler : function() {
                    // 增加
                    showHide('add');
                }
            },
            {
                iconCls : 'icon-remove',
                text : '删除',
                handler : function() {
                    // 调用删除方法
                    removechecked();
                }
            }
        ]
    });
    
    // 最大值限制
    $("#txtCsdm").next().children().attr("maxlength","32");
    $("#txtCsz").next().children().attr("maxlength","1000");
    $("#txtCsms").next().children().attr("maxlength","150");
    
    /*
    *新增页面按钮事件
    */
    $("#lbtnJycsSubmit").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 交易ID
        var jyid = $("#hidJyid").val();
        // 交易码
        var jym = $("#hidJym").val();
        // 参数状态
        var cszt = $("#nfsCszt").get(0).checked ? "1" : "0";
        // 平台
        var pt = $("#hidPt").val() == undefined ? "kf" : $("#hidPt").val();
        // 出错提示
        var msg = "新增失败，请稍后再试";
        if ($("#txtCsid").val()=="") {
            // 新增
            url = "/oa/kf_ywgl/kf_ywgl_003/kf_ywgl_003_view/data_add_view";
        } else {
            // 修改
            url = "/oa/kf_ywgl/kf_ywgl_003/kf_ywgl_003_view/data_edit_view",
            msg = "修改失败，请稍后再试";
        }
        // 提交表单
        $('#divJycsWindow').find('form').form('submit', {
            url: url,
            queryParams: {'jyid':jyid, 'jym': jym, 'cszt': cszt, 'pt': pt},
            onSubmit: function(){
                var csbm = $("#txtCsdm").textbox("getValue");
                var csz = $("#txtCsz").textbox("getValue");
                var csms = $("#txtCsms").textbox("getValue");
                if (csbm=="") {
                    $.messager.alert('错误','参数代码不可为空，请输入','error', function(){
                        $("#txtCsdm").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!checkBm(csbm, '参数代码', 'txtCsdm')) {
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (csz=="") {
                    $.messager.alert('错误','参数值不可为空，请输入','error', function(){
                        $("#txtCsz").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                return true;
            },
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, "dgJycs", "divJycsWindow");
            },
            error: function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });
    
    $("#lbtnJycsCancel").click(function(e){
        e.preventDefault();
        $('#divJycsWindow').window('close');
    });
    
    // 最大值限制
    $("#txtJym").next().children().attr("maxlength","20");
    $("#txtJymc").next().children().attr("maxlength","30");
    $("#txtJyms").next().children().attr("maxlength","120");
    $("#txtTimeout").next().children().attr("maxlength","5");
    $("#txtZdfqpz").next().children().attr("maxlength","100");
    
    $("#lbtnJbxxSubmit").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        var id = $("#hidJyid").val();
        var zt = $("#nfsJyzt").get(0).checked ? '1' : '0';
        var jymc = '';
        var jym = '';
        $('#divJbxx').find('form').form('submit', {
            url: '/oa/kf_ywgl/kf_ywgl_003/kf_ywgl_003_view/jbxx_edit_view',
            queryParams: {'id': id, 'zt': zt}, 
            onSubmit: function(){
                jym = $("#txtJym").textbox("getValue");
                jymc = $("#txtJymc").textbox("getValue");
                var timeout = $("#txtTimeout").numberbox("getValue");
                var zdfqpz = $("#txtZdfqpz").textbox("getValue");
                if (jymc=="") {
                    $.messager.alert('错误','交易名称不可为空，请输入','error', function(){
                        $("#txtJymc").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!checkMc(jymc, '交易名称', 'txtJymc')) {
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (jym=="") {
                    $.messager.alert('错误','交易码不可为空，请输入','error', function(){
                        $("#txtJym").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!checkBm(jym, '交易码', 'txtJym')) {
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (timeout=="") {
                    $.messager.alert('错误','交易超时时间不可为空，请输入','error', function(){
                        $("#txtTimeout").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!/^[0-9]*$/.test(timeout)) {
                    $.messager.alert('错误','交易超时时间只可为数字，请重新输入','error', function(){
                        $("#txtTimeout").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                return true;
            },
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, "", "");
                $('#hidJym').val(jym);
                // 更新tab名称
                var parentDocument = window.parent.parent.document;
                top.$(parentDocument).find("#pnlMain ul.tabs .tabs-selected span.tabs-title").text(jymc + '_交易详情');
                // 自动发起配置说明
                data = $.parseJSON( data );
                $("#txtZdfqpzsm").textbox('setValue', data.zdfqpzsm);
                // 更新成功，更新隐藏域值
                if( data.state == true ){
                    $("#hidYzt").val( zt );
                    var zdfqpz = $("#txtZdfqpz").textbox("getValue");
                    $("#hidYzdfqpz").val( zdfqpz );
                }
            }
        });
    });
    
    $("#txtCsdm").next().children().on('keydown', function(e){
        var that = this;
        var value = this.value;
        // 按键的keycode
        var keycode = e.which;
        // shift键是否按住
        var isshift = e.shiftKey;
        if(keycode == 229) {
            $(that).blur();
            setTimeout(function() {
                $(that).focus()
            }, 10)
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    });

    $("#txtCsdm").next().children().on('keypress', function(e){
        var that = this;
        var value = this.value;
        // 按键的keycode
        var keycode = e.which;
        // shift键是否按住
        var isshift = e.shiftKey;
        if ((keycode >= 65 && keycode <= 90)
            || keycode == 8
            || keycode == 46
            // || keycode == 36
            || (keycode >= 48 && keycode <= 57)
            || (keycode == 95)) {
        } else {
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    });
    
    // 翻译
    $("#lbtnFy").click(function(e){
        e.preventDefault();
        zdfqpzFy( 'txtZdfqpz','txtZdfqpzsm' );
    })

});

/**
*新增or编辑交易参数弹出框
*/
function showHide(handle,id,index) {
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    if(handle=='add'){
        $("#nfsCszt").get(0).checked = true;
        newWindow($("#divJycsWindow"),'新增交易参数',450,320);
        // 新增时参数代码控件可编辑
        $("#txtCsdm").textbox('enable');
        // 清空参数ID
        $("#txtCsid").val('');
    }
    else if(handle=='update'){
        var d = $('#'+id).datagrid('getData').rows[index];
        $("#nfsCszt").get(0).checked = (d.zt=="1");
        newWindow($("#divJycsWindow"),'编辑交易参数',450,320);
        $("#txtCsid").val(d.id);
        $("#txtCsdm").textbox('setValue', d.csdm);
        // 编辑时参数代码控件不可编辑
        $("#txtCsdm").textbox('disable');
        $("#txtCsz").textbox('setValue', d.value);
        $("#txtCsms").textbox('setValue', d.csms);
    }
    // form tab排序
    $("#divJycsWindow").children('form').tabSort();
    $('#txtCsdm').textbox('textbox').attr('placeholder', '仅能输入大写字母数字下划线');
};

/**
*批量删除交易参数
*/
function removechecked(){
    if(!checkSelected("dgJycs")) {
        return;
    }
    $.messager.confirm('提示', '所选参数将被删除且不可恢复，您确定要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 当前选中的记录
            var checkedItems = $('#dgJycs').datagrid('getChecked');
            var ids = new Array();
            $(checkedItems).each(function(index, item){
                ids.push(item["id"]);
            });
            // 平台
            var pt = $("#hidPt").val() == undefined ? "kf" : $("#hidPt").val();
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_ywgl/kf_ywgl_003/kf_ywgl_003_view/data_del_view",
                data: {"ids":ids.join(","), "jym":$("#hidJym").val(), "pt": pt},
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, "dgJycs", "");
                },
                error: function(){
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    });
}
