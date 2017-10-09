$(document).ready(function() {
    
    // form tab排序
    $("#divJbxx form").tabSort();
    
    // 渲染表格
    datagrid = $('#dgYwcs').datagrid({
        title: '业务参数设置',
        nowrap : false,
        fit : true,
        height: '150px',
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        method: "get",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        frozenColumns: [[
            { field: 'select_box', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: '参数ID', hidden: true },
            { field: 'csdm', title: '参数代码', width: '20%' },
            { field: 'value', title: '参数值', width: '20%' },
            { field: 'csms', title: '参数描述', width: '30%' },
            { field: 'zt', title: '状态', width: '13%', formatter: function(value,rowData,rowIndex) {
                return value=="1" ? "启用" : "禁用"; 
            } },
            { field: 'cz', title: '操作', width: '13%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="showHide(\'update\',\'dgYwcs\','+rowIndex+');">编辑</a>';
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
            }, {
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
    
    $("#lbtnYwcsSubmit").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 业务ID
        var ywid = $("#hidYwid").val();
        // 参数状态
        var cszt = $("#nfsCszt").get(0).checked ? "1" : "0";
        // 平台
        var pt = $("#hidPt").val() == undefined ? "kf" : $("#hidPt").val();
        // 出错提示
        var msg = "新增失败，请稍后再试";
        if ($("#hidCsid").val()=="") {
            // 新增
            url = "/oa/kf_ywgl/kf_ywgl_002/kf_ywgl_002_view/data_add_view";
        } else {
            // 修改
            url = "/oa/kf_ywgl/kf_ywgl_002/kf_ywgl_002_view/data_edit_view",
            msg = "修改失败，请稍后再试";
        }
        // 提交表单
        $('#divYwcsWindow').find('form').form('submit', {
            url: url,
            queryParams: {'ywid':ywid, 'cszt':cszt, 'pt': pt},
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
                afterAjax(data, "dgYwcs", "divYwcsWindow");
            },
            error: function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });
    
    // 最大值限制
    $("#txtYwbm").next().children().attr("maxlength","10");
    $("#txtYwmc").next().children().attr("maxlength","50");
    $("#txtYwms").next().children().attr("maxlength","150");
    
    $("#lbtnJbxxSubmit").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        var ywmc = '';
        $('#divJbxx').find('form').form('submit', {
            url:'/oa/kf_ywgl/kf_ywgl_002/kf_ywgl_002_view/jbxx_edit_view',
            onSubmit: function(){
                var ywbm = $("#txtYwbm").textbox("getValue");
                ywmc = $("#txtYwmc").textbox("getValue");
                if (ywmc=="") {
                    $.messager.alert('错误','业务名称不可为空，请输入','error', function(){
                        $("#txtYwmc").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!checkMc(ywmc, '业务名称', 'txtYwmc')) {
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (ywbm=="") {
                    $.messager.alert('错误','业务简称不可为空，请输入','error', function(){
                        $("#txtYwbm").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!checkBm(ywbm, '业务简称', 'txtYwbm')) {
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
                // 更新tab名称
                var parentDocument = window.parent.parent.document;
                top.$(parentDocument).find("#pnlMain ul.tabs .tabs-selected span.tabs-title").text(ywmc + '_业务详情');
            }
        });
    });
    
    /*
    *新增或编辑页面按钮事件
    */
    $("#lbtnYwcsCancel").click(function(e){
        e.preventDefault();
        $('#divYwcsWindow').window('close');
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
    
});

/**
*批量删除
*/
function removechecked(){
    if(!checkSelected("dgYwcs")) {
        return;
    }
    $.messager.confirm('提示', '所选参数将被删除且不可恢复，您确定要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 当前选中的记录
            var checkedItems = $('#dgYwcs').datagrid('getChecked');
            var ids = new Array();
            $(checkedItems).each(function(index, item){
                ids.push(item["id"]);
            });
            // 平台
            var pt = $("#hidPt").val() == undefined ? "kf" : $("#hidPt").val();
            // 业务ID
            var ywid = $("#hidYwid").val();
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_ywgl/kf_ywgl_002/kf_ywgl_002_view/data_del_view",
                data: {"ids": ids.join(","),"pt":pt,"ywid":ywid},
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, "dgYwcs", "");
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

/**
*新增or编辑业务参数弹窗
*/
function showHide(handle,id,index) {
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    if(handle=='add'){
        $("#nfsCszt").get(0).checked = true;
        newWindow($("#divYwcsWindow"),'新增业务参数',450,320);
        // 新增时参数代码控件可编辑
        $("#txtCsdm").textbox('enable');
        // 清空参数ID
        $("#hidCsid").val('');
    }
    else if(handle=='update'){
        var d = $('#'+id).datagrid('getData').rows[index];
        $("#nfsCszt").get(0).checked = (d.zt=="1");
        newWindow($("#divYwcsWindow"),'编辑业务参数',450,320);
        $("#hidCsid").val(d.id);
        $("#txtCsdm").textbox('setValue', d.csdm);
        // 编辑时参数代码控件不可编辑
        $("#txtCsdm").textbox('disable');
        $("#txtCsz").textbox('setValue', d.value);
        $("#txtCsms").textbox('setValue', d.csms);
    }
    // form tab排序
    $("#divYwcsWindow").children('form').tabSort();
    $('#txtCsdm').textbox('textbox').attr('placeholder', '仅能输入大写字母数字下划线');
}
