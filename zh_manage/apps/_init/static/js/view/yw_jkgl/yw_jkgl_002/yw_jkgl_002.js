/**
 * 页面ready方法
 */
$(function() {
    // 对象编码最大值限制
    $("#txtJkdx_dxbm").next().children().attr("maxlength","30");
    // 对象名称最大值限制
    $("#txtJkdx_dxmc").next().children().attr("maxlength","20");
    // 对象描述最大值限制
    $("#txtJkdx_dxms").next().children().attr("maxlength","100");
    $("#dgJkdx").datagrid({
        nowrap : true,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_jkgl/yw_jkgl_002/yw_jkgl_002_view/data_view",
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [
            [
             { field: 'id', title: 'id', hidden: true },
             {field: 'dxlx', title: '对象类型', width: 10 },
             {field: 'lxbm', title: 'lxbm', width: 25, hidden: true },
             {field: 'dxbm', title: '对象编码',width: 20}, 
             {field: 'dxmc',title: '对象名称',width: 25}, 
             {field: 'dxms',title: '对象描述',width: 25}, 
             {field: 'dxzt',title: '对象状态',width: 10,
                formatter: function(value, rowData, rowIndex) {
                    if (value == '1') {
                        return "启用";
                    }else{
                        return "禁用";
                    }
                }}, 
             {field: 'czr',title: '操作人',width: 10}, 
             {field: 'czsj',title: '操作时间',width: 15,align: 'center'}, 
             {field: 'cz',title: '操作',width: 10,
                formatter: function(value, rowData, rowIndex) {
                    var czStr = '';
                    if (rowData) {
                        czStr += '<a href="javascript:;" onclick="javascript:jkdx_add2upd(\'dgJkdx\',' + rowIndex + ',\'upd\',event);">编辑</a> ';
                    }
                    return czStr;
                }
            }]
        ],
        toolbar: [{
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                // 新增
                jkdx_add2upd('dgJkdx', '', 'add');
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
                qyjk('dgJkdx','1');
            }
        }, '-', {
            iconCls: 'icon-cancel',
            text: '设为禁用',
            handler: function() {
                // 禁用
                qyjk('dgJkdx','0');
            }
        }]
    });
    // 绑定添加管理对象的方法
    $('#lbtnJkdx_ok_add').on('click', function(e) {
        e.preventDefault();
        window_update_add_func();
    });
    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });
    $("#lbtnJkdx_cancel").on('click', function(e) {
        e.preventDefault();
        $("#jkdx_add2upd_window").window('close');
    });
    // 对象类型的下拉列表
    $("#combSearch_dxlx").combobox({
        data: dxlx,
        valueField: 'lbbm',
        textField: 'lbmc',
    });
    // 对象状态的下来列表
    $("#combSearch_dxzt").combobox({
        data: dxzt,
        valueField: 'bm',
        textField: 'mc'
    });
    // tab顺 
    $('#dxForm').tabSort();
});

//新增或编辑
function jkdx_add2upd(datagrid_id, index, type,event) {
    if (event){
        event.stopPropagation();
    }
    if (type == 'add') {
        // 创建新增窗口
        newWindow($('#jkdx_add2upd_window'), "新增监控对象", '360', '350');
        // 获取对象类型
        get_dxlx();
        // 启用对象编码
        $('#txtJkdx_dxbm').textbox("enable");
        $('#dxzt').prop("checked", true).prop("disabled", false);
        // 移除禁用状态
        $('#state_link').removeClass("cursor_not_allowed");
        
    } else if (type = 'upd') {
        newWindow($('#jkdx_add2upd_window'), "编辑监控对象", '360', '350');
        $('#txtJkdx_dxbm').textbox("disable");
        // 获取对象类型
        get_dxlx();
        //赋值
        var row_xx = $('#'+datagrid_id).datagrid('getData').rows[index];
        $("#hidJkdx_id").val(row_xx.id);
        // 获取编辑对象的属性
        get_edit(row_xx.id);
    }
}
/**
 * 获取对象类型
 */
function get_dxlx(){
    get_zjlx();
    // ajax请求
    $.ajax({
        url:'/oa/yw_jkgl/yw_jkgl_002/yw_jkgl_002_view/get_dxlx_view',
        type : 'post',
        dataType : 'json',
        async: false,
        success:function(data){
            //执行请求后的方法
            if(data.state == true){
                // 如果查询成功
                // 添加，编辑页面的对象类型的下拉列表
                $("#combJkdx_dxlx").combobox({
                    data: data.list,
                    valueField: 'lbbm',
                    textField: 'lbmc',
                    onSelect: function(rec){
                        // 若对象类型为主机，则展示主机类型下拉框
                        if(rec.lbbm == "Computer(zjip,dxcjpzid)"){
                            $("#zjlx_tr").css('display','');
                        }else{
                            $("#zjlx_tr").css('display','none');
                        }
                        $('#jkdx_add2upd_window').find('form').tabSort();
                    }
                });
                $("#combJkdx_dxlx").combobox('select',data.list[0].lbbm);
                $('#jkdx_add2upd_window').find('form').tabSort();
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
  * 获取主机类型
  **/
function get_zjlx(){
    
    // 查询主机类型下拉列表
    $.ajax({
        type: 'POST',
        dataType: 'text',
        async: false,
        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/server_add_sel_view",
        data: {},
        success: function(data){
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 主机类型
                $('#selZjlx').combobox({
                    editable:false,
                    data:data.zjxx_lst,
                    valueField:'value',
                    textField:'text'
                });
                $('#jkdx_add2upd_window').find('form').tabSort();
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
 * 获取要编辑的内容的属性
 */
function get_edit(id){
    // ajax请求
    $.ajax({
        url:'/oa/yw_jkgl/yw_jkgl_002/yw_jkgl_002_view/get_edit_view',
        type : 'post',
        data : {
            'id':id
        },
        dataType : 'json',
        success:function(data){
            //执行请求后的方法
            if(data.state == true){
                // 如果查询成功
                $("#combJkdx_dxlx").combobox('select', data.jkdx.sslbbm);
                $("#hid_jkdx_dxlx").val(data.jkdx.sslbbm);
                $('#combJkdx_dxlx').combobox("disable");
                $("#selZjlx").combobox('select', data.jkdx.zjlx);
                $('#selZjlx').combobox("disable");
                $("#txtJkdx_dxbm").textbox('setValue', data.jkdx.dxbm);
                $("#hidJkdx_dxbm").val(data.jkdx.dxbm);
                $("#txtJkdx_dxmc").textbox('setValue', data.jkdx.dxmc);
                $("#hidJkdx_dxmc_old").val(data.jkdx.dxmc);
                $("#txtJkdx_dxms").textbox('setValue', data.jkdx.dxms);
                // 禁用状态
                $('#state_link').addClass("cursor_not_allowed");
                $("#dxzt").get(0).checked = data.jkdx.zt == '1';
                $('#dxzt').prop("disabled", true);
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
    var checkedItems = $('#dgJkdx').datagrid('getChecked');
    // 校验至少选择一项
    if (!checkSelected("dgJkdx")){
        return;
    }
    $.messager.confirm("提示", "删除对象后不可恢复，你确定要删除吗？", function(flag) {
        if (flag) {
            url = '/oa/yw_jkgl/yw_jkgl_002/yw_jkgl_002_view/del_view';
            // 删除监控对象
            ajax_jkdx(url);
        }
    });
}

/**
 * 启用,禁用监控
 */
function qyjk(datagrid_id,able) {
    var comf = "1" == able?"启用":"禁用";
    // 获取所有选中的监控对象
    var checkedItems = $('#dgJkdx').datagrid('getChecked');
    // 校验至少选择一项
    if (!checkSelected("dgJkdx")){
        return;
    }
    if("1" == able){
        msg = "您确定要设为启用吗？";
    }else{
        msg = "设置禁用后不再进行监控，您确定要设置为禁用吗？";
    }
    $.messager.confirm("提示", msg, function(flag) {
        if (flag) {
            url = '/oa/yw_jkgl/yw_jkgl_002/yw_jkgl_002_view/able_view';
            // 启用监控对象
            ajax_jkdx(url,able);
        }
    })
}
/**
 * 启用或者禁用监控对象
 **/
function ajax_jkdx(url,zt){
    // 添加遮罩
    ajaxLoading();
    // 启用或者禁用监控对象
    var rows = $('#dgJkdx').datagrid('getSelections');
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
            afterAjax(data, 'dgJkdx','');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

// 公共函数更新方法
function window_update_add_func(e){
    if(e){
        e.preventDefault();
    }
    var jkdx_zjlx = $("#selZjlx").combobox('getValue');
    // 添加遮罩
    ajaxLoading();
    // 添加监控对象url
    var url = '/oa/yw_jkgl/yw_jkgl_002/yw_jkgl_002_view/add_view'
    if( $('#hidJkdx_id').val() ){
        url = '/oa/yw_jkgl/yw_jkgl_002/yw_jkgl_002_view/edit_view'
    }
    // 添加监控对象
    $('#jkdx_add2upd_window').find('form').form('submit', {
        url:url,
        dataType : 'json',
        queryParams : { "jkdx_zjlx": jkdx_zjlx },
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
            //执行请求后的方法
            afterAjax(data, 'dgJkdx','jkdx_add2upd_window');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
//表格查询
function doSearch() {
    // 对象类型
    var dxlx = $("#combSearch_dxlx").combobox('getValue');
    // 编码
    var dxbm = $("#txtSearch_dxbm").textbox('getValue');
    // 对象名称
    var dxmc = $("#txtSearch_dxmc").textbox('getValue');
    // 对象状态
    var dxzt = $("#combSearch_dxzt").combobox('getValue');
    
    // 根据条件查询管理对象
    $("#dgJkdx").datagrid('load',{
        dxlx: dxlx,
        dxbm: dxbm,
        dxmc: dxmc,
        dxzt: dxzt
    });

}
// 输入框校验
function validate(){
    // 监控对象，对象类型
    var jkdx_dxlx = $("#combJkdx_dxlx").combobox('getValue');
    // 监控对象，对象编码
    var jkdx_dxbm = $("#txtJkdx_dxbm").textbox('getValue');
    // 监控对象，对象名称
    var jkdx_dxmc = $("#txtJkdx_dxmc").textbox('getValue');
    // 监控对象类型
    if (jkdx_dxlx=="" || jkdx_dxlx==null) {
        $.messager.alert('错误','对象类型不可为空，请选择','error', function(){
            $("#combJkdx_dxlx").next().children().focus();
        });
        return false;
    }

    // 当监控类型为主机时
    if ( jkdx_dxlx == "Computer(zjip,dxcjpzid)" ) {
        // 监控对象，主机类型
        var jkdx_zjlx = $("#selZjlx").combobox('getValue');
        if(jkdx_zjlx=="" || jkdx_zjlx==null){
            $.messager.alert('错误','主机类型不可为空，请选择','error', function(){
                $("#selZjlx").next().children().focus();
            });
            return false;
        }
        
    }
    
    // 监控对象编码为空时校验
    if (jkdx_dxbm=="" || jkdx_dxbm==null) {
        $.messager.alert('错误','对象编码不可为空，请输入','error', function(){
            $("#txtJkdx_dxbm").next().children().focus();
        });
        return false;
    }

    // 当监控类型为主机时
    if ( jkdx_dxlx == "Computer(zjip,dxcjpzid)" ) {
        // 当监控对象编码非空时校验
        if(!checkBm2(jkdx_dxbm,"对象编码","txtJkdx_dxbm")) {
            return false;
        }
    }

    // 函数内容
    if (jkdx_dxmc=="" || jkdx_dxmc==null) {
        $.messager.alert('错误','对象名称不可为空，请输入','error', function(){
            $("#txtJkdx_dxmc").next().children().focus();
        });
        return false;
    }
    
    return true;
}
