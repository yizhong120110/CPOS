$(document).ready(function() {
    
    // form tab排序
    $("#node_edit_layout").children('form').tabSort();
    
    var editor = CodeMirror.fromTextArea(document.getElementById("tarJdnr"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent:true,
        matchBrackets: true
    });
    //将tab换为4个空格
    editor.setOption("extraKeys", {
        Tab: function(cm) {
            var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
            cm.replaceSelection(spaces);
        }
    });
    
    $("#tbsNodeEdit").tabs({
        onSelect: function(title, index){
            var id = "";
            if (index == 1) {
                // 保存代码后输入要素会新增或减少，使重新加载dgSrysData
                dgSrysData = null;
                id = "dgSrys";
                $("#lb").val("1");
            } else if (index == 2) {
                // 保存代码后输出要素会新增或减少，使重新加载dgScysData
                dgScysData = null;
                id = "dgScys";
                $("#lb").val("2");
            } else if (index == 3) {
                id = "dgFhz";
                $("#lb").val("3");
            } else if (index == 4) {
                //id = "dgYycs";
                $('#frmYycs')[0].contentWindow.$("#datagrid_jdyycs").datagrid('reload');
            }
            if (id != "") {
                $('#'+id).datagrid("reload", {
                    lb: $("#lb").val(),
                    nodeid: $("#nodeid").val()
                });
            }
        }
    });
    
    
    // 最大值限制
    $("#txtJdbm").next().children().attr("maxlength","50");
    $("#txtJdmc").next().children().attr("maxlength","50");
    
    $('#lbtnJdSave').click(function(e){
        // 添加遮罩
        ajaxLoading();
        e.preventDefault();
        var jdbm = $("#txtJdbm").textbox("getValue");
        var jdmc = $("#txtJdmc").textbox("getValue");
        var jdnr = editor.getValue();
        if (jdbm=="") {
            $.messager.alert('错误','节点编码不可为空，请输入','error', function(){
                $("#txtJdbm").next().children().focus();
            });
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        if (!checkBm(jdbm, '节点编码', 'txtJdbm')) {
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        if (jdmc=="") {
            $.messager.alert('错误','节点名称不可为空，请输入','error', function(){
                $("#txtJdmc").next().children().focus();
            });
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        if (!checkMc(jdmc, '节点名称', 'txtJdmc')) {
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        if (jdnr=="") {
            $.messager.alert('错误','代码不可为空，请输入','error', function(){
                editor.focus();
            });
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_edit_submit_view",
            // nodeid为空时，后台进行新增
            data: {"nodeid":$("#nodeid").val(), "jdlx":$("#jdlx").val(), "jdbm":jdbm, "jdmc":jdmc, "jdnr":jdnr},
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                if (data.state) {
                    $("#nodeid").val(data.nodeid);
                    var bjid = $("#bjid").val();
                    if (bjid) {
                        $(parent.document).find("#"+bjid).attr("data-saved", "1");
                        $(parent.document).find("#"+bjid).attr("data-wym", data.wym);
                        $(parent.document).find("#"+bjid).attr("data-wym_bbk", data.wym_bbk);
                        $(parent.document).find("#"+bjid).attr("data-nodeid", data.nodeid);
                        $(parent.document).find("#"+bjid).find("span").text(jdmc);
                    }
                    // 更新连接线颜色
                    if (parent.refreshNodeConnColor) {
                        parent.refreshNodeConnColor(data.nodeid);
                    }
                    $.messager.alert('提示', data.msg, 'info', function(){
                        if(parent.$("#dgJdgl") != undefined && parent.$("#dgJdgl") != 'undefined'){
                            parent.$("#dgJdgl").datagrid("reload");
                        }
                        // 通讯管理新增打解包配置重新加载
                        if(parent.initDbJb != undefined && parent.initDbJb != 'undefined'){
                            parent.initDbJb();
                        }
                    });
                } else {
                    $.messager.alert('警告', '<pre id="msgPre">'+data.msg+'</pre>', 'warning');
                    // 根据提示信息的长度来确定当前提示框的高度
                    if ( data.msg.length >=0 && data.msg.length <= 20 ) {
                        $('#msgPre').css({'height': '15px'});
                    } else if ( data.msg.length >=20 && data.msg.length <= 40 ){
                        $('#msgPre').css({'height': '30px'});
                    } else if ( data.msg.length >=40 && data.msg.length <= 60 ){
                        $('#msgPre').css({'height': '45px'});
                    } else if ( data.msg.length >=60 && data.msg.length <= 80 ){
                        $('#msgPre').css({'height': '60px'});
                    } else {
                        $('#msgPre').css({'height': '75px'});
                    };
                    $('#msgPre').css({'overflow': 'auto', 'margin-bottom': '0'}).parent().css('width', '285px');
                    var msgWin = $('#msgPre').parents('.messager-window');
                    msgWin.css({'width': '350px', 'left': ($(window).width()-400)*0.5});
                    msgWin.find('.window-header').css('width', '');
                    msgWin.find('.messager-body').css('width', '');
                    // 去掉因返回提示信息过长而出现的白块区域
                    msgWin.siblings('.window-shadow').css({'height':'0px'});
                }
            },
            error: function(){
                errorAjax();
            }
        });
    });
    
    var columns = [[
        { field: 'id', hidden: true },
        { field: 'bm', title: '要素编码', width: 17 },
        { field: 'ysmc', title: '要素名称', width: 20 },
        { field: 'gslbmc', title: '归属类别', width: 15 },
        { field: 'ly', title: '来源', width: 11 },
        //{ field: 'mrz', title: '默认值', width: 15 },
        { field: 'cz', title: '操作', width: 8, formatter: function(value,rowData,rowIndex) {
            return '<a href="javascript:editYs(\'dgSrys\','+rowIndex+');">编辑</a>';
        } }
    ]];
    // 如果节点类型为通讯打包节点，则展示是否接口校验、校验规则名称、追加参数列
    if ($("#jdlx").val() == '5') {
        columns[0].splice(3, 0, { field: 'jkjy', title: '是否接口校验', width: 16, formatter: function(value,rowData,rowIndex) {
            return value == '1' ? '是' : '否';
        } });
        columns[0].splice(4, 0, { field: 'ssgzmc', title: '校验规则名称', width: 16 });
        columns[0].splice(5, 0, { field: 'zjcs', title: '追加参数列表', width: 16 });
    }
    var dgSrysData = null;
    var $checkbox_sr = null;
    $('#dgSrys').datagrid({
        nowrap : false,
        fit : true,
        border: false,
        height: '300px',
        rownumbers : true,
        singleSelect: false,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_ys_view",
        queryParams: {
            lb: '1',
            nodeid: $("#nodeid").val(),
            jdlx: $("#jdlx").val()
        },
        remoteSort: false,
        frozenColumns: [[
            { field: 'select_box', checkbox: true, width: '2%' }
        ]],
        columns: columns,
        toolbar : "#tb",
        onLoadSuccess: function(data){
            if (dgSrysData == null) {
                dgSrysData = data;
                filterData('dgSrys', $('#selSryslb').combobox('getText'), $('#selSrysly').combobox('getText'));
            }
            $checkbox_sr = $('#dgSrys').datagrid('getPanel').find("input[type='checkbox']");
            // 加载完毕后获取所有的checkbox遍历
            if (data.rows.length > 0) {
                // 循环判断操作为新增的不能选择
                for (var i = 0; i < data.rows.length; i++) {
                    // 根据来源让某些行不可选
                    if (data.rows[i].ly == '自动') {
                        $checkbox_sr[i + 1].disabled = true;
                    }
                }
            }
        },
        onClickRow: function(rowIndex, rowData){
            // 获取所有的checkbox遍历
            $checkbox_sr.each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgSrys').datagrid('unselectRow', index - 1);
                }
            });
            // 如果可选的都已选中，全选复选框置为勾选状态
            if ($('#dgSrys').datagrid('getPanel').find('.datagrid-cell-check input:enabled').length == $('#dgSrys').datagrid('getChecked').length && $('#dgSrys').datagrid('getChecked').length != 0) {
                $('#dgSrys').datagrid('getPanel').find('.datagrid-header-check input').get(0).checked = true;
            }
        },
        onCheckAll: function(rows){
            // 获取所有的checkbox遍历
            $checkbox_sr.each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgSrys').datagrid('unselectRow', index - 1);
                }
            });
            // 全选复选框置为勾选状态
            $('#dgSrys').datagrid('getPanel').find('.datagrid-header-check input').get(0).checked = true;
        }
    });
    
    var dgScysData = null;
    var $checkbox_sc = null;
    $('#dgScys').datagrid({
        nowrap : false,
        fit : true,
        border: false,
        height: '300px',
        rownumbers : true,
        singleSelect: false,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_ys_view",
        queryParams: {
            lb: '2',
            nodeid: $("#nodeid").val()
        },
        remoteSort: false,
        frozenColumns: [[
            { field: 'select_box', checkbox: true }
        ]],
        columns: [[
            { field: 'id', hidden: true },
            { field: 'bm', title: '要素编码', width: 17 },
            { field: 'ysmc', title: '要素名称', width: 20 },
            { field: 'gslbmc', title: '归属类别', width: 15 },
            { field: 'ly', title: '来源', width: 11 },
            //{ field: 'mrz', title: '默认值', width: 15 },
            { field: 'cz', title: '操作', width: 8, formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:editYs(\'dgScys\','+rowIndex+');">编辑</a>';
            } }
        ]],
        toolbar : "#tb_sc",
        onLoadSuccess: function(data){
            if (dgScysData == null) {
                dgScysData = data;
                filterData('dgScys', $('#selScyslb').combobox('getText'), $('#selScysly').combobox('getText'));
            }
            $checkbox_sc = $('#dgScys').datagrid('getPanel').find("input[type='checkbox']");
            // 加载完毕后获取所有的checkbox遍历
            if (data.rows.length > 0) {
                // 循环判断操作为新增的不能选择
                for (var i = 0; i < data.rows.length; i++) {
                    // 根据来源让某些行不可选
                    if (data.rows[i].ly == '自动') {
                        $checkbox_sc[i + 1].disabled = true;
                    }
                }
            }
        },
        onClickRow: function(rowIndex, rowData){
            // 获取所有的checkbox遍历
            $checkbox_sc.each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgScys').datagrid('unselectRow', index - 1);
                }
            });
            // 如果可选的都已选中，全选复选框置为勾选状态
            if ($('#dgScys').datagrid('getPanel').find('.datagrid-cell-check input:enabled').length == $('#dgScys').datagrid('getChecked').length && $('#dgScys').datagrid('getChecked').length != 0) {
                $('#dgScys').datagrid('getPanel').find('.datagrid-header-check input').get(0).checked = true;
            }
        },
        onCheckAll: function(rows){
            // 获取所有的checkbox遍历
            $checkbox_sc.each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgScys').datagrid('unselectRow', index - 1);
                }
            });
            // 全选复选框置为勾选状态
            $('#dgScys').datagrid('getPanel').find('.datagrid-header-check input').get(0).checked = true;
        }
    });
    
    $('#dgFhz').datagrid({
        nowrap : false,
        fit : false,
        border: false,
        height: '300px',
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_ys_view",
        queryParams: {
            lb: '3',
            nodeid: $("#nodeid").val()
        },
        remoteSort: false,
        columns: [[
            { field: 'id', hidden: true },
            { field: 'bm', title: '返回值', width: 35 },
            { field: 'ysmc', title: '备注', width: 57 },
            { field: 'cz', title: '操作', width: 8, formatter: function(value, rowData, rowIndex) {
                return '<a href="javascript:;" onclick="editFhz(event, \'dgFhz\', '+rowIndex+');return false;">编辑</a>';
            } }
        ]]
    });
    
    $(".lbtnAddys").click(function(){
        $("#txtLyTr").hide();
        if ($("#lb").val() == 1) {
            newWindow($("#winAddYs"), "新增输入要素", 410, 190);
        } else {
            newWindow($("#winAddYs"), "新增输出要素", 410, 190);
        }
        $('#txtYsbm').textbox('enable');
//        $("#selYsGslb").combobox("select", $("#selYsGslb").combobox('getData')[0].id);
        $("#cz").val("add");
        // form tab排序
        $("#winAddYs").children('form').tabSort();
        $('#txtYsbm').textbox('textbox').attr('placeholder', '仅能输入大写字母数字下划线');
    });
    
    // 获取光标位置
    function getCursortPosition (ctrl) {
        var CaretPos = 0;
        if (document.selection) {
            // IE Support
            ctrl.focus ();
            var Sel = document.selection.createRange ();
            Sel.moveStart ('character', -ctrl.value.length);
            CaretPos = Sel.text.length;
        } else if (ctrl.selectionStart || ctrl.selectionStart == '0') {
            // Firefox support
            CaretPos = ctrl.selectionStart;
        }
        return CaretPos;
    }
    // 设置光标位置
    function setCaretPosition(ctrl, pos){
        if(ctrl.setSelectionRange) {
            ctrl.focus();
            ctrl.setSelectionRange(pos,pos);
        } else if (ctrl.createTextRange) {
            var range = ctrl.createTextRange();
            range.collapse(true);
            range.moveEnd('character', pos);
            range.moveStart('character', pos);
            range.select();
        }
    }

    // 最大值限制、编码转为大写
    // $("#txtYsbm").next().children().attr("maxlength","50").on('keyup', function(e){
    //     // console.log($(this).val())
    //     var range = getCursortPosition(this);
    //     $("#txtYsbm").textbox('setValue', $(this).val().toUpperCase());
    //     setCaretPosition(this, range);
    // });

    $("#txtYsbm").next().children().attr("maxlength","50").on('keydown', function(e){
        var that = this;
        var value = this.value;
        // 按键的keycode
        var keycode = e.which;
        // shift键是否按住
        var isshift = e.shiftKey;
        // console.log(keycode, isshift)
        if(keycode == 229) {
            $(that).blur();
            setTimeout(function() {
                $(that).focus()
            }, 10)
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    });

    $("#txtYsbm").next().children().attr("maxlength","50").on('keypress', function(e){
        var that = this;
        var value = this.value;
        // 按键的keycode
        var keycode = e.which;
        // shift键是否按住
        var isshift = e.shiftKey;
        console.log(keycode, isshift)
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



    $("#txtYsmc").next().children().attr("maxlength","25");
    //$("#txtYsmrz").next().children().attr("maxlength","166");
    
    $("#lbtnYsSubmit").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 提交表单
        var id = $("#lb").val()=="1" ? "dgSrys" : "dgScys";
        var url = $("#cz").val()=="add" ? "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_ys_add_view" : "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_ys_edit_view";
        $('#winAddYs').find('form').form('submit', {
            url: url,
            queryParams: {'nodeid':$("#nodeid").val(), 'bjid':$("#bjid").val(), 'lb':$("#lb").val(), 'ysbm':$('#txtYsbm').textbox('getValue')},
            onSubmit: function(){
                var ysbm = $("#txtYsbm").textbox("getValue");
                var ysmc = $("#txtYsmc").textbox("getValue");
//                var lb = $("#selYsGslb").combobox("getValue");
                if (ysbm=="") {
                    $.messager.alert('错误', '要素编码不可为空，请输入', 'error', function(){
                        $("#txtYsbm").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!checkBm(ysbm, '要素编码', 'txtYsbm')) {
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (ysmc=="") {
                    $.messager.alert('错误', '要素名称不可为空，请输入', 'error', function(){
                        $("#txtYsmc").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
//                if (lb=="") {
//                    $.messager.alert('错误', '归属类别不可为空，请选择', 'error', function(){
//                        $("#selYsGslb").next().children().focus();
//                    });
//                    return false;
//                }
                return true;
            },
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, "", "winAddYs");
                data = $.parseJSON(data);
                if (data.state) {
                    if (!$("#nodeid").val() && data.nodeid) {
                        $("#nodeid").val(data.nodeid);
                    }
                    if ($("#bjid").val()) {
                        $(parent.document).find("#"+$("#bjid").val()).attr("data-nodeid", data.nodeid);
                    }
                    if (id == 'dgSrys') {
                        dgSrysData = null;
                    } else if (id == 'dgScys') {
                        dgScysData = null;
                    }
                    $("#"+id).datagrid("reload",{
                        lb: $("#lb").val(),
                        nodeid: $("#nodeid").val()
                    });
                    // 更新节点唯一码
                    if (parent.refreshJdWym) {
                        parent.refreshJdWym();
                    }
                }
            },
            error: function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });
    
    $("#lbtnYsCancel").click(function(e){
        e.preventDefault();
        $('#winAddYs').window('close');
    });
    
    // 最大值限制
    $("#txtFhzbz").next().children().attr("maxlength","25");
    
    $("#lbtnSubmitFhzbz").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        $('#winEditFhz').find('form').form('submit', {
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_fhz_update_view",
            onSubmit: function(){
                return true;
            },
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, "dgFhz", "winEditFhz");
            },
            error: function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });
    
    $("#lbtnCancelFhzbz").click(function(e){
        e.preventDefault();
        $('#winEditFhz').window('close');
    });
    
    $("#btnSrysDel").click(function(){
        if(!checkSelected("dgSrys")) {
            return;
        }
        $.messager.confirm("确认", '要素删除后将不可恢复，您确认要删除吗？', function (r) {
            if (r) {
                // 调用删除方法
                removechecked('dgSrys');
            }
        });
    });
    $("#add_sc_btn").click(function(){
        append_sc();
    });
    $("#btnScysDel").click(function(){
        if(!checkSelected("dgScys")) {
            return;
        }
        $.messager.confirm("确认", '要素删除后将不可恢复，您确认要删除吗？', function (r) {
            if (r) {
                // 调用删除方法
                removechecked('dgScys');
            }
        });
    });
    
    /**
    *批量删除
    */
    function removechecked(id){
        // 添加遮罩
        ajaxLoading();
        var checkedItems = $('#'+id).datagrid('getChecked');
        var ids = new Array();
        $(checkedItems).each(function(index, item){
            ids.push(item["id"]);
        });
        $.ajax({
            type: 'POST',
            dataType: 'text',
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_ys_del_view",
            data: {"ids":ids.join(",")},
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, id, "");
            },
            error: function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    }
    
    $("#lbtnJdClose").click(function(e){
        e.preventDefault();
        parent.$("#winNodeEdit").window('close');
    });
    
    $('#selSryslb').combobox({
        editable: false,
        width: '180px',
        valueField: 'id',
        textField: 'text',
        multiple: true,
        panelHeight: 'auto',
        onSelect: function(record) {
            filterData('dgSrys', $('#selSryslb').combobox('getText'), $('#selSrysly').combobox('getText'));
        },
        onUnselect: function(record) {
            filterData('dgSrys', $('#selSryslb').combobox('getText'), $('#selSrysly').combobox('getText'));
        },
        onLoadSuccess: function() {
            // 全选
            var data = [];
            $.each($('#selSryslb').combobox('getData'), function(){
                data.push(this.id);
            });
            $("#selSryslb").combobox("setValues", data);
        }
    });
    
    $('#selSrysly').combobox({
        editable: false,
        width: '150px',
        valueField: 'id',
        textField: 'text',
        multiple: true,
        panelHeight: 'auto',
        onSelect: function(record) {
            filterData('dgSrys', $('#selSryslb').combobox('getText'), $('#selSrysly').combobox('getText'));
        },
        onUnselect: function(record) {
            filterData('dgSrys', $('#selSryslb').combobox('getText'), $('#selSrysly').combobox('getText'));
        },
        onLoadSuccess: function() {
            // 全选
            var data = [];
            $.each($('#selSrysly').combobox('getData'), function(){
                data.push(this.id);
            });
            $("#selSrysly").combobox("setValues", data);
        }
    });
    
    $('#selScyslb').combobox({
        editable: false,
        width: '180px',
        valueField: 'id',
        textField: 'text',
        multiple: true,
        panelHeight: 'auto',
        onSelect: function(record) {
            filterData('dgScys', $('#selScyslb').combobox('getText'), $('#selScysly').combobox('getText'));
        },
        onUnselect: function(record) {
            filterData('dgScys', $('#selScyslb').combobox('getText'), $('#selScysly').combobox('getText'));
        },
        onLoadSuccess: function() {
            // 全选
            var data = [];
            $.each($('#selScyslb').combobox('getData'), function(){
                data.push(this.id);
            });
            $("#selScyslb").combobox("setValues", data);
        }
    });
    
    $('#selScysly').combobox({
        editable: false,
        width: '150px',
        valueField: 'id',
        textField: 'text',
        multiple: true,
        panelHeight: 'auto',
        onSelect: function(record) {
            filterData('dgScys', $('#selScyslb').combobox('getText'), $('#selScysly').combobox('getText'));
        },
        onUnselect: function(record) {
            filterData('dgScys', $('#selScyslb').combobox('getText'), $('#selScysly').combobox('getText'));
        },
        onLoadSuccess: function() {
            // 全选
            var data = [];
            $.each($('#selScysly').combobox('getData'), function(){
                data.push(this.id);
            });
            $("#selScysly").combobox("setValues", data);
        }
    });
    
    function filterData(id, valueLb, valueLy) {
        valueLbArr = valueLb.split(',');
        valueLyArr = valueLy.split(',');
        var rows = [];
        var data = id == 'dgSrys' ? dgSrysData.rows : dgScysData.rows;
        $.each(data, function(){
            if (valueLbArr.indexOf(this['gslbmc']) >= 0 && valueLyArr.indexOf(this['ly']) >= 0) {
                rows.push(this);
            }
        });
        $('#'+id).datagrid('loadData', rows);
    }
    
});

function editYs(id, index) {
    $("#txtLyTr").show();
    if ($("#lb").val() == 1) {
        newWindow($("#winAddYs"), "编辑输入要素", 410, 220);
    } else {
        newWindow($("#winAddYs"), "编辑输出要素", 410, 220);
    }
    var d = $('#'+id).datagrid('getData').rows[index];
    $("#txtYsbm").textbox('setValue', d.bm);
    if (d.ly=="自动") {
        $("#txtYsbm").textbox('disable');
    } else {
        $("#txtYsbm").textbox('enable');
    }
    $("#txtYsmc").textbox('setValue', d.ysmc);
//    $("#selYsGslb").combobox('select', d.gslb);
    //$("#txtYsmrz").textbox('setValue', d.mrz);
    $("#txtLy").text(d.ly=="自动" ? "自动识别" : "手工添加");
    $("#txtYsid").val(d.id);
    $("#cz").val("update");
}

function editFhz(event, id, index) {
    event.stopPropagation();
    newWindow($("#winEditFhz"), '编辑返回值', 350, 190);
    var d = $('#'+id).datagrid('getData').rows[index];
    $("#txtFhz").textbox('setValue', d.bm);
    $("#txtFhzbz").textbox('setValue', d.ysmc);
    $("#txtFhzid").val(d.id);
    // form tab排序
    $("#winEditFhz").children('form').tabSort();
}
