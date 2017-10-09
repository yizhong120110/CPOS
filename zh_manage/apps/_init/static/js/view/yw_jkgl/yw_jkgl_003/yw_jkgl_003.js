var edtor = null;
//表格查询
function doSearch() {
    // 函数名称
    hsmc = $("#txtSearch_hsmc").textbox('getValue');
    // 中文名称
    zwmc = $("#txtSearch_zwmc").textbox('getValue');
    // 状态
    dxzt = $("#combSearch_dxzt").combobox('getValue');
    // 来源
    dxly = $("#combSearch_dxly").combobox('getValue');
    
    // 根据条件查询管理对象
    $("#dgXydz").datagrid('load',{
        hsmc: hsmc,
        zwmc: zwmc,
        dxzt: dxzt,
        dxly: dxly
    });
}

//新增或编辑
function xydz_add2upd(datagrid_id, index, type,event) {
    if (event){
        event.stopPropagation();
    }
    if (type == 'add') {
        newWindow($('#xydz_add2upd_window'), "新增分析规则", '770', '510');
        $("#warning_hsmc").hide();
        //默认选择第一个tab页
        $("#dzdm_div").tabs({
            selected: 0
        });
        //清空编辑框
        if (edtor.getValue && edtor.getValue() != "") {
            edtor.setValue('')
        }
        // 初始化传入参数
        $("#dg_crcs").datagrid('load',{
            // 随意写一个id，让后台查询不出数据,用着初始化
            xydz_id: 'klqw'
        });
        // 移除禁用状态
        $('#state_link').removeClass("cursor_not_allowed");
        $("#state").get(0).checked = true;
        $('#state').prop("disabled", false);
        $("#txtHsmc").textbox('enable');
        $('#form_window').tabSort();
    } else if (type = 'upd') {
        newWindow($('#xydz_add2upd_window'), "编辑分析规则", '770', '510');
        //默认选择第一个tab页
        $("#dzdm_div").tabs({
            selected: 0
        });
        //赋值
        var row_xx = $('#'+datagrid_id).datagrid('getData').rows[index];
        // id
        $("#hidXydz_id").val(row_xx.id);
        // 获取分析规则的内容
        get_edit(row_xx.id);
        // 根据条件查询传入参数
        $("#dg_crcs").datagrid('load',{
            xydz_id: $("#hidXydz_id").val()
        });
    }
}


/**
 * 获取要编辑的分析规则的内容
 */
function get_edit(id){
    // ajax请求
    $.ajax({
        url:'/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/get_xydz',
        type : 'post',
        data : {
            'id':id
        },
        dataType : 'json',
        success:function(data){
            //执行请求后的方法
            if(data.state == true){
                // 如果查询成功
                // 函数名称
                $("#txtHsmc").textbox('setValue', data.xydz.hsmc);
                // 隐藏的函数名称
                $("#hidHsmc").val(data.xydz.hsmc);
                if(data.flag == true){
                    $("#txtHsmc").textbox('disable');
                    $("#warning_hsmc").show();
                }else{
                    $("#warning_hsmc").hide();
                    $("#txtHsmc").textbox('enable');
                }
                // 中文名称
                $("#txtZwmc").textbox('setValue', data.xydz.zwmc);
                // 规则描述
                $("#txtMs").textbox('setValue', data.xydz.ms);
                // 状态
                $("#state").get(0).checked = data.xydz.zt == '1';
                // 隐藏的状态按钮
                $("#hidXydz_zt").val(data.xydz.zt);
                // 禁用状态
                $('#state_link').addClass("cursor_not_allowed");
                $('#state').prop("disabled", true);
                // 设置分析规则的代码
                edtor.setValue(data.xydz.nr);
                // 内容id
                $("#hidNr_id").val(data.xydz.nr_id);
                $('#form_window').tabSort();
            }else{
                // 如果查询失败
                afterAjax(data, "", "");
            }
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

/**
 *批量删除
 */
function removechecked() {
    // 获取所有选中的监控对象
    var checkedItems = $('#dgXydz').datagrid('getChecked');
    // 校验至少选择一项
    if (!checkSelected("dgXydz")){
        return;
    }
    $.messager.confirm("提示", "删除后，不再在监控配置中展示，您确定要删除吗？", function(flag) {
        if (flag) {
            var rows = $('#dgXydz').datagrid('getSelections');
            //创建存放id的数组
            var idArray = new Array();
            $.each(rows,function(n,row){
                idArray[n] = row.id;
            });
            url = '/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/del_view';
            // 删除监控对象
            ajax_jkdx(url);
        }
    });
}
/**
 * 启用监控
 */
function qyxydz(datagrid_id,able) {
    var comf = "1" == able?"您确定要设为启用吗？":"设置禁用后不再在监控配置选择中展示，您确定要设置为禁用吗？";
    // 校验至少选择一项
    if (!checkSelected("dgXydz")){
        return;
    }
    $.messager.confirm("提示", comf, function(flag) {
        if (flag) {
            url = '/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/able_view';
            // 启用监控对象
            ajax_jkdx(url,able);
        }
    });

}

/**
 * 页面ready方法
 */
$(function() {
    // 函数名称
    $("#txtHsmc").next().children().attr("maxlength","100");
    // 中文名称
    $("#txtZwmc").next().children().attr("maxlength","30");
     // 查询的函数名称
    $("#txtSearch_hsmc").next().children().attr("maxlength","100");
    // 查询的中文名称
    $("#txtSearch_zwmc").next().children().attr("maxlength","30");
    // 规则描述
    $("#txtMs").next().children().attr("maxlength","100");
    // 参数说明
    $("#txtCssm").next().children().attr("maxlength","100");
    $("#dgXydz").datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "post",
        url: "/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/data_view",
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [
            [{
                field: 'id', title: 'id', width: 25,hidden:true
            },{
                field: 'hsmc', title: '规则函数名称', width: '20%'
            }, {
                field: 'zwmc' ,title: '中文名称', width: '15%'
            }, {
                field: 'lymc', title: '来源' ,width: '5%'
            }, {
                field: 'ly', title: '来源名称' ,width: 18,hidden:true
            }, {
                field: 'zt', title: '状态',width: '5%',
                formatter: function(value, rowData, rowIndex) {
                    if (value == '1') {
                        return "启用";
                    }else{
                        return "禁用";
                    }
                }
            }, {
                field: 'ms', title: '规则描述', width: '25%'
            }, {
                field: 'czr' ,title: '操作人', width: '8%'
            }, {
                field: 'czsj', title: '操作时间', width: '12%', align: 'center'
            }, {
                field: 'cz', title: '操作', width: '6%',
                formatter: function(value, rowData, rowIndex) {
                    czStr = '<a href="javascript:;" onclick="javascript:xydz_add2upd(\'dgXydz\',' + rowIndex + ',\'upd\',event);">编辑</a> ';
                    return czStr;
                }
            }]
        ],
        toolbar: [{
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                // 新增
                xydz_add2upd('dgXydz', '', 'add');
            }
        }, '-', {
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 删除
                removechecked();
            }
        }, '-', {
            iconCls: 'icon-ok',
            text: '设为启用',
            handler: function() {
                // 启用
                qyxydz('dgXydz','1');
            }
        }, '-', {
            iconCls: 'icon-cancel',
            text: '设为禁用',
            handler: function() {
                // 禁用
                qyxydz('dgXydz','0');
            }
        }],
        onLoadSuccess: function(data){ // 加载完毕后获取所有的checkbox遍历
            if (data.rows.length > 0) {
                // 循环判断操作来源为铺底的不能选择
                for (var i = 0; i < data.rows.length; i++) {
                    // 根据引用次数让某些行不可选
                    if (data.rows[i].ly == '2') {
                        $("input[type='checkbox']")[i + 1].disabled = true;
                    }
                }
            }
        },
        onClickRow: function(rowIndex, rowData){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgXydz').datagrid('unselectRow', index - 1);
                }
            });
            // 如果可选的都已选中，全选复选框置为勾选状态
            if ($('.datagrid-cell-check input:enabled').length == $('#dgXydz').datagrid('getChecked').length && $('#dgXydz').datagrid('getChecked').length != 0) {
                $('.datagrid-header-check input').get(0).checked = true;
            }
        },
        onCheckAll: function(rows){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgXydz').datagrid('unselectRow', index - 1);
                }
            });
            // 全选复选框置为勾选状态
            $('.datagrid-header-check input').get(0).checked = true;
        }
    });
    // 传入参数grid
    $("#dg_crcs").datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "post",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        url: "/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/crcs_data_view",
        columns: [
            [{
                field: 'id',title: 'id',width: 30,hidden:true
            },{
                field: 'csdm',title: '参数代码',width: '15%'
            }, {
                field: 'cssm',title: '参数说明',width: '31%'
            }, {
                field: 'sfkk',title: '是否可空',width: '10%',
                formatter: function(value, rowData, rowIndex) {
                    if (value == 'True') {
                        return "是";
                    }else{
                        return "否";
                    }
                }
            }, {
                field: 'mrz',title: '默认值',width: '20%'
            }, {
                field: 'cz',title: '操作',width: '10%',
                formatter: function(value, rowData, rowIndex) {
                    var czStr = '';
                    if (rowData) {
                        czStr += '<a href="javascript:;" onclick="javascript:crcsbj(' + rowIndex + ',event);">编辑</a> ';
                    }
                    return czStr;
                }
            }]
        ]
    });
    //渲染添加或修改框中的编辑框
    edtor = CodeMirror.fromTextArea(document.getElementById("tarNodeBox"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent: true,
        matchBrackets: true
    });
    //将tab换为4个空格
    edtor.setOption("extraKeys", {
        Tab: function(cm) {
            var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
            cm.replaceSelection(spaces);
        }
    });
    // 绑定添加管理对象的方法
    $('#lbtnXydz_ok_add').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        window_update_add_func();
    });
    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        doSearch();
    });
    $("#lbtnXydz_cancel").on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $("#warning_hsmc").hide();
        $("#xydz_add2upd_window").window('close');
    });
    // 对象状态的下来列表
    $("#combSearch_dxzt").combobox({
        data: dxzt,
        valueField: 'bm',
        textField: 'mc'
    });
    // 对象来源的下来列表
    $("#combSearch_dxly").combobox({
        data: dxly,
        valueField: 'bm',
        textField: 'mc'
    });
    // 保存参数
    $("#lbtnCrcs_ok_upd").on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        // 添加遮罩
        ajaxLoading();
        // 提交
        $('#crcs_window').find('form').form('submit', {
            url:'/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/crcs_edit_view',
            dataType : 'json',
            method: "post",
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                //执行请求后的方法
                afterAjax(data, 'dg_crcs','crcs_window');
            },
            error : function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });
    // 取消
    $("#lbtnCrcs_cancel").on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $("#crcs_window").window("close");
    });
    // tab顺 
    $('#dxForm').tabSort();
    // 给规则函数窗口添加关闭事件
    $('#xydz_add2upd_window').window({
        onClose:function(){
            $("#warning_hsmc").hide();
        }
    });

});
// 输入框校验
function validate(){
    // 函数名称
    var hsmc = $("#txtHsmc").textbox('getValue');
    // 中文名称
    var zwmc = $("#txtZwmc").textbox('getValue');
    // 规则代码
    var nodeBox = edtor.getValue()
    
    // 函数名称
    if (hsmc=="" || hsmc==null) {
        $.messager.alert('错误','规则函数名称不可为空，请输入','error', function(){
            $("#txtHsmc").next().children().focus();
        });
        return false;
    }
    
    // 中文名称
    if (zwmc=="" || zwmc==null) {
        $.messager.alert('错误','中文名称不可为空，请输入','error', function(){
            $("#txtZwmc").next().children().focus();
        });
        return false;
    }
    // 规则代码
    if (nodeBox=="" || nodeBox==null) {
        $.messager.alert('错误','规则代码不可为空，请输入','error', function(){
            $("#tarNodeBox").focus();
        });
        return false;
    }
}

// 公共函数更新方法
function window_update_add_func(e){
    if(e){
        e.preventDefault();
    }
    // 添加遮罩
    ajaxLoading();
    // 添加监控对象url
    var url = '/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/add_view'
    if( $('#hidXydz_id').val() ){
        url = '/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/edit_view'
    }
    // 添加监控对象
    $('#xydz_add2upd_window').find('form').form('submit', {
        url:url,
        dataType : 'json',
        onSubmit: function(){
            var ret = validate();
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
            data = JSON.parse(data);
            data['msg'] = data['msg'].replace(/\n/gm, '<br/>');
            //执行请求后的方法
            afterAjax(data, 'dgXydz','xydz_add2upd_window');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

/**
 * 启用或者禁用监控对象
 **/
function ajax_jkdx(url,zt){
    // 添加遮罩
    ajaxLoading();
    // 启用或者禁用监控对象
    var rows = $('#dgXydz').datagrid('getSelections');
    //创建存放id的数组
    var idArray = new Array();
    // 获取所有id
    $.each(rows,function(n,row){
        idArray[n] = row.id;
    });
    // ajax请求
    $.ajax({
        url:url,
        type : 'post',
        dataType : 'json',
        data : {
            'ids' : idArray.join(","),
            'zt':zt // 启用或者禁用的状态
        },
        success:function(data){
            // 取消遮罩
            ajaxLoadEnd();
            //执行请求后的方法
            afterAjax(data, 'dgXydz','');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}
/**
 * 传入参数编辑
 **/
function crcsbj(index, event){
    if (event){
        event.stopPropagation();
    }
    newWindow($('#crcs_window'), "编辑传入参数", '370', '250');
    var rowdata = $("#dg_crcs").datagrid("getRows");
    var row = rowdata[index];
    // 获取传入参数的内容
    get_crcs_edit(row['id'])
    $('#crcs_form').tabSort();
    //$("#txtCsdm").textbox('setValue', row['csdm']).textbox("disable");
    //$("#txtSfkk").textbox('setValue', row['sfkk']=='True'?'是':'否').textbox("disable");
    //$("#txtMrz").textbox('setValue', row['mrz']).textbox("disable");
    //$("#txtCssm").textbox('setValue', row['cssm']);
    //$("#hidCrcs_id").val(row['id']);
    //$("#hidCsdm_d").val(row['hsmc']);
}

/**
 * 获取要编辑的传入参数内容
 */
function get_crcs_edit(id){
    // ajax请求
    $.ajax({
        url:'/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/get_crcsxx',
        type : 'post',
        data : {
            'id':id
        },
        dataType : 'json',
        success:function(data){
            //执行请求后的方法
            if(data.state == true){
                // 如果查询成功
                $("#txtCsdm").textbox('setValue', data.csxx.csdm).textbox("disable");
                $("#txtSfkk").textbox('setValue', data.csxx.sfkk=='True'?'是':'否').textbox("disable");
                $("#txtMrz").textbox('setValue', data.csxx.mrz).textbox("disable");
                $("#txtCssm").textbox('setValue', data.csxx.cssm);
                $("#hidCrcs_id").val(data.csxx.id);
                $("#hidCsdm_d").val(data.csxx.csdm);
            }else{
                // 如果查询失败
                afterAjax(data, "", "");
            }
            $('#crcs_form').tabSort();
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
