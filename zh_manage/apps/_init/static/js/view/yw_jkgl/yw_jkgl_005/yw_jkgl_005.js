/**
 * 页面ready方法
 */
// 标识是否对基本信息进行校验是否发生改变了。
jiaoyan = true;
// form中原本的数据
old_form_data = {};
$(function() {
    // 采集配置名称最大值长度限制
    $("#txtCjmc").next().children().attr("maxlength","20");
    // 自动发起配置最大值长度限制
    $("#txtZdfqjyZdfqpz").next().children().attr("maxlength","100");
    // 采集配置描述最大值长度限制
    $("#txtCjms").next().children().attr("maxlength","100");
    // 禁用自动发起配置说明
    $("#txtZdfqjyZdfqpzsm").textbox("disable");
    $('#tt').tabs({    
        border:false,    
        onSelect:function(title,index){
            // 如果用户选择了适用对象，必须校验基本信息有没有发生变化。
            if(index == 1 && jiaoyan == true){
                var data = checkXXChange();
                if (data['state'] == false){
                    $('#tt').tabs('unselect',index);
                    $('#tt').tabs('select',0);
                    $("#"+data['input_id']).next().children().focus();
                }
            }
        }    
    });  
    
    $("#dgSjcj").datagrid({
        nowrap : true,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/data_view",
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [
            [
             { field: 'id', title: 'id', hidden: true },
             {field: 'lbmc', title: '采集类型', width: 10 },
             {field: 'zbmc', title: '采集指标', width: 20 },
             {field: 'mc', title: '采集名称',width: 25}, 
             {field: 'zdfqpzsm',title: '采集频率',width: 20}, 
             {field: 'sfkbf',title: '是否可并发',width: 10,
                formatter: function(value, rowData, rowIndex) {
                    if (value == '1') {
                        return "是";
                    }else if(value == '0'){
                        return "否";
                    }
                }}, 
             {field: 'czr',title: '操作人',width: 10}, 
             {field: 'czsj',title: '操作时间',width: 15,align: 'center'}, 
             {field: 'cz',title: '操作',width: 10,
                formatter: function(value, rowData, rowIndex) {
                    var czStr = '';
                    if (rowData) {
                        czStr += '<a href="javascript:;" onclick="javascript:jkdx_add2upd(\'dgSjcj\',' + rowIndex + ',\'upd\',event);">编辑</a> ';
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
                jkdx_add2upd('dgSjcj', '', 'add');
            }
        }, '-', {
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 删除
                removechecked();
            }
        }]
    });
    // 传入参数grid
    $("#dgCs").datagrid({
        striped: true,
        fitColumns: true,
        singleSelect: true,
        rownumbers: true,
        pagination: false,
        nowrap: false,
        columns: [
            [{
                field: 'cs_id',
                title: '参数代码',
                width: 30,
                hidden:true
            },{
                field: 'csdm',
                title: '参数代码',
                width: 30
            }, {
                field: 'cssm',
                title: '参数说明',
                width: 30
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 30,
                formatter: function(value, rowData, rowIndex) {
                    if (value == 'True') {
                        return "是";
                    }else if(value == 'False'){
                        return "否";
                    }
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 30
            }, {
                field: 'csz',
                title: '参数值',
                width: 30,
                formatter: function(value, rowData, rowIndex) {
                    if( value == null )
                        value = '';
                    return '<input type="text" autocomplete="off" id="txtCsz_'+ rowData.id +'" name="csz_'+ rowData.id +'" value = "'+ value +'" class="textbox-text" style="width:80px" />';
                }
            }]
        ],
        onLoadSuccess:  function(){
            // 限定值的长度(100)
            var rows = $("#dgCs").datagrid("getRows");
            for(var i=0;i<rows.length;i++){
                var crcsid = rows[i].id
                $("#txtCsz_" + crcsid).attr("maxlength","100");
            }
        }
    });
    // 适用对象
    $("#dgSydx").datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        pagination: true,
        fitColumns: false,
        method: "post",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        pageSize: 50,
        onLoadSuccess:function(data){
        },
        queryParams:{
            'cjpzid':$("#hidCjid").val(),
            'zbid':$('#combCjzb').combobox('getValue')
        },
        url: "/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/sydx_view",
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [],
        toolbar: [{
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                sydx_add('dgSydx', '', 'add');
            }
        }, '-', {
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                removechecked2('dgSydx');
            }
        }, '-', {
            iconCls: 'icon-edit',
            text: '编辑',
            handler: function() {
                sydx_add('dgSydx', '', 'edit');
            }
        }, '-', {
            iconCls: 'icon-ok',
            text: '设为启用',
            handler: function() {
                // 启用
                qyjk('dgSydx','1');
            }
        }, '-', {
            iconCls: 'icon-cancel',
            text: '设为禁用',
            handler: function() {
                // 禁用
                qyjk('dgSydx','0');
            }
        }]
    });
    
    // 绑定添加管理对象的方法
    $('#lbtnSjcj_ok_add').on('click', function(e) {
        e.preventDefault();
        window_update_add_func();
    });
     // 绑定添加适用对象的方法
    $('#lbtnSydx_ok_add').on('click', function(e) {
        e.preventDefault();
        window_update_add_sydx();
    });
    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });
    $("#lbtnSjcj_cancel").on('click', function(e) {
        e.preventDefault();
        $("#sjcj_add2upd_window").window('close');
    });
    // 绑定适用对象添加窗口的取消按钮事件
    $("#lbtnSydx_cancel").on('click', function(e) {
        e.preventDefault();
        $("#sydx_add_window").window('close');
    });
    // 对象类型的下拉列表
    $("#combSearch_cjlx").combobox({
        data: cjlb,
        valueField: 'lbbm',
        textField: 'lbmc',
    });
    // 是否可并发
    $("#combSearch_sfbf").combobox({
        data: sfbf,
        valueField: 'bm',
        textField: 'mc'
    });
    // 对象状态的下来列表
    $("#combSearch_lx").combobox({
        data: [{'bm':'','mc':'请选择'},{'bm':'1','mc':'发起频率'},{'bm':'2','mc':'计划任务'}],
        valueField: 'bm',
        textField: 'mc'
    });
    // 绑定类型点击的事件
    $("input[name=sjcj_cjlx]").on('click', function(e) {
        var value = this.value;
        // 如果是发起频率
        if (value == "1") {
            $("#txtZdfqjyZdfqpz").textbox("disable");
            $("#combSfbf").textbox("disable");
            $("#txtFqpl").textbox("enable");
            $("#combSfbf").combobox('setValue','');
        } else if (value == "2") {
            // 如果是计划任务
            $("#txtZdfqjyZdfqpz").textbox("enable");
            $("#combSfbf").textbox("enable");
            $("#combSfbf").combobox('select', $("#combSfbf").combobox('getData')[0].bm);
            $("#txtFqpl").textbox("disable");
        }
        // 将计划任务清空
        $("#txtZdfqjyZdfqpz").textbox("setValue","");
        // 将自动发起配置清空
        $("#txtFqpl").textbox("setValue","");
        // 将自动发起配置说明清空
        $("#txtZdfqjyZdfqpzsm").textbox("setValue","");
        // tab顺
        $('#sjcj_add2upd_window').find('form').tabSort();
    });
    // 翻译操作
    $("#lbtnFy").click(function(e){
        e.preventDefault();
        // 获取类型的值
        var sjcj_cjlx = $('input[name="sjcj_cjlx"]:checked').val();
        // 若类型为发起频率
        if (sjcj_cjlx=='1'){
            //每X秒发起一次
            var fqpl = $('#txtFqpl').numberspinner('getValue');
            $('#txtZdfqjyZdfqpzsm').textbox('setValue','每'+fqpl+'秒发起一次');
        }else{
            // 自动发起配置翻译
            zdfqpzFy( 'txtZdfqjyZdfqpz','txtZdfqjyZdfqpzsm' );
        }
        
    });
    // tab顺 
    $('#dxForm').tabSort();
});

//新增或编辑
function jkdx_add2upd(datagrid_id, index, type,event) {
    if (event){
        event.stopPropagation();
    }
    // 默认选中第一个tab
    $('#tt').tabs('select', 0); 
    if (type == 'add') {
        jiaoyan = false;
        // 创建新增窗口
        newWindow($('#sjcj_add2upd_window'), "新增采集配置", '800', '360');
        // 获取下拉框数据
        getComb(false);
        // 启用采集类型
        $("#combCjlx").combobox("enable");
        // 启用采集指标
        $("#combCjzb").combobox("enable");
        // 默认选中发起频率
        $('input[name=sjcj_cjlx][value=1]').prop('checked', true);
        $("#txtZdfqjyZdfqpz").textbox("disable");
        $("#combSfbf").textbox("disable");
        $("#txtFqpl").textbox("enable");
        $('#tt').tabs('disableTab', 1); 
        load_datagrid_sydx();
    } else if (type = 'upd') {
        jiaoyan = true;
        newWindow($('#sjcj_add2upd_window'), "编辑采集配置", '800', '360');
        // 获取下拉框数据
        getComb();
        //赋值
        var row_xx = $('#'+datagrid_id).datagrid('getData').rows[index];
        $("#hidCjid").val(row_xx.id);
        // 获取编辑对象的属性
        get_edit(row_xx.id);
        $("#combCjlx").combobox("disable");
        $("#combCjzb").combobox("disable");
        $('#sjcj_add2upd_window').find('form').tabSort();
        $('#tt').tabs('enableTab', 1); 
    }
    
    var pager = $('#dgSydx').datagrid('getPager');
    $(pager[0]).pagination({
        onRefresh:function(pageNumber, pageSize){
            load_datagrid_sydx();
        }
    });
}

/**
 * 获取要编辑的内容的属性
 */
function get_edit(id){
    // ajax请求
    $.ajax({
        url:'/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/get_cjpz_update_view',
        type : 'post',
        data : {
            'id':id
        },
        dataType : 'json',
        success:function(data){
            //执行请求后的方法
            if(data.state == true){
                // 如果查询成功
                $("#hidCjid").val(data.cjpz.id);
                $("#hidCjlb_hid").val(data.cjpz.sslbbm);
                $("#hidCjzb_hid").val(data.cjpz.zbid);
                // 名称
                $("#txtCjmc").textbox('setValue', data.cjpz.mc);
                // 描述
                $("#txtCjms").textbox('setValue', data.cjpz.ms);
                // 采集类别
                $("#combCjlx").combobox('setValue', data.cjpz.sslbbm);
                // 采集指标
                $("#combCjzb").combobox('setValue', data.cjpz.zbmc);
                // 类型
                $('input[name=sjcj_cjlx][value='+data.cjpz.lx+']').prop('checked', true);
                // 是否可并发
                $("#combSfbf").combobox('setValue', data.cjpz.sfkbf);
                // 如果是发起频率
                if (data.cjpz.lx == '1'){
                    $("#txtFqpl").textbox('setValue', data.cjpz.zdfqpz);
                    // 禁用自动发起配置
                    $("#txtZdfqjyZdfqpz").textbox("disable");
                    // 禁用是否并发
                    $("#combSfbf").textbox("disable");
                    // 禁用发起频率
                    $("#txtFqpl").textbox("enable");
                }else{
                    // 如果是计划任务
                    $("#txtZdfqjyZdfqpz").textbox('setValue', data.cjpz.zdfqpz);
                    // 起用自动发起配置
                    $("#txtZdfqjyZdfqpz").textbox("enable");
                    // 起用是否并发
                    $("#combSfbf").textbox("enable");
                    // 起用发起频率
                    $("#txtFqpl").textbox("disable");
                }
                // 自动发起配置说明
                $("#txtZdfqjyZdfqpzsm").textbox('setValue', data.cjpz.zdfqpzsm);
                //加载适用对象表格 
                load_datagrid_sydx();
                // 将数据放到公共变量中
                old_form_data = data.cjpz;
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
//加载使用对象表格
function load_datagrid_sydx() {
    $.ajax({
        url:'/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/sydx_view',
        type : 'post',
        data : { 'cjpzid':$("#hidCjid").val(),'zbid':$('#hidCjzb_hid').val() },
        dataType : 'json',
        success:function(data){
            var array =[];
            var columns = [];
            data = data.csz;
            $(data).each(function(){
                array.push({field:'',title:'',width:''});
            });
            columns.push(array);
            $(data).each(function(index,el){
                columns[0][index]['field']= el.csdm;
                columns[0][index]['title']= el.cssm;
                // 15个像素一个字，动态的判断field的宽度
                if (el.cssm.length > 10){
                    columns[0][index]['width'] = 15 * el.cssm.length;
                }else{
                    columns[0][index]['width'] = 150;
                }
            });
            $("#dgSydx").datagrid({'columns':columns});
            var pager = $('#dgSydx').datagrid('getPager');
            $(pager[0]).pagination({
                onRefresh:function(pageNumber, pageSize){
                    load_datagrid_sydx();
                }
            });
            $('#sjcj_add2upd_window').find('form').tabSort();
            
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
    $("#dgSydx").datagrid('load',{ 'cjpzid':$("#hidCjid").val(),'zbid':$('#combCjzb').combobox('getValue') })
}
//新增或编辑
function sydx_add(datagrid_id, index, type) {
    if (type == 'add') {
        newWindow($('#sydx_add_window'), "新增适用对象", '700', '400');
        //加载适用对象表格 
        load_datagrid_cs('add',[],'');
        // 禁用对象名称指定主机
        $("#combZdzj").combobox({ disabled: false });
        $("#combDxmc").combobox({ disabled: false });
        
    }else{
        // 获取所有选中的适用对象
        var checkedItems = $('#dgSydx').datagrid('getChecked');
        // 校验至少选择一项
        if (!checkSelected("dgSydx")){
            return;
        }
        if (checkedItems.length > 1){
            $.messager.alert('警告', '只能选择一项', 'info');
            return;
        }
        newWindow($('#sydx_add_window'), "编辑适用对象", '700', '400');
        // 获取要编辑的适用对象的id
        var sydxid = checkedItems[0]['id'];
        // 适用对象id
        $('#hid_sydxid').val(sydxid);
        //加载适用对象表格 
        load_datagrid_cs('edit',sydxid,checkedItems[0]['dxzt']);
        
        // 禁用对象名称指定主机
        $("#combZdzj").combobox({ disabled: true });
        $("#combDxmc").combobox({ disabled: true });
    }
}
//加载使用传入参数
function load_datagrid_cs(type,sydxid,sydx_state) {
    // ajax获取使用对象信息 
    // ajax请求
    $.ajax({
        url:'/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/get_dxmc_zdzj_view',
        type : 'post',
        data : {
            'zbid':$("#hidCjzb_hid").val(),
            'sslbbm':$("#hidCjlb_hid").val(),
            'cjpzid':$("#hidCjid").val(),
            'type':type,
            'sydxid':sydxid
        },
        dataType : 'json',
        success:function(data){
            var zdzj_data = data.zdzj;
            //执行请求后的方法
            if(data.state == true){
                // 指定主机下拉框
                $("#combZdzj").combobox({
                    data: data.zdzj,
                    valueField: 'ip',
                    textField: 'mc'
                });
                // 对象名称下拉框
                $("#combDxmc").combobox({
                    data: data.dxmc,
                    valueField: 'id',
                    textField: 'dxmc',
                    onSelect:function(record){
                        var c_l = $('#combCjlx').combobox('getValue');
                        if (c_l == 'Computer(zjip,dxcjpzid)'){
                            //将制定主机的值换为  对象名称对应的ip的主机
                            $.each(zdzj_data,function(index,value){
                                if (value['ip'] == record['dxbm']){
                                    // 设定主机下拉框的值
                                    $("#combZdzj").combobox('loadData',[value]);
                                    // 指定主机默认选择第一个
                                    if($("#combZdzj").combobox("getData").length > 0){
                                        $("#combZdzj").combobox("select", $("#combZdzj").combobox("getData")[0].ip)
                                    }
                                    return false;
                                }
                            });
                        }
                    }
                });
                if ($("#combDxmc").combobox("getData").length > 0){
                    // 对象名称默认选择第一个
                    $("#combDxmc").combobox("select", $("#combDxmc").combobox("getData")[0].id)
                }
                if ($("#combZdzj").combobox("getData").length > 0){
                    // 指定主机默认选择第一个
                    $("#combZdzj").combobox("select", $("#combZdzj").combobox("getData")[0].ip)
                }
                
                // 传入参数grid
                $('#dgCs').datagrid('loadData', data.crcs); 
                $("#sy_state").get(0).checked = true;
                $('#sydx_add_window').find('form').tabSort();
                if (type=='edit'){
                    // 禁用状态
                    $('#state_link').addClass("cursor_not_allowed");
                    $("#sy_state").get(0).checked = sydx_state == '启用';
                    $('#sy_state').prop("disabled", true);
                }else{
                    $("#sy_state").get(0).checked = true;
                    $('#sy_state').prop("checked", true).prop("disabled", false);
                    // 移除禁用状态
                    $('#state_link').removeClass("cursor_not_allowed");
                }
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
function removechecked2(id) {
    var checkedItems = $('#' + id).datagrid('getChecked');
    // 校验至少选择一项
    if (!checkSelected(id)){
        return;
    }
    $.messager.confirm("提示", "适用对象删除后将不可恢复，您确定要删除吗？", function(flag) {
        if (flag) {
            url = '/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/del_sydx_view';
            ajax_sydx(url,id);
        }
    });
}
/**
 * 删除适用对象
 **/
function ajax_sydx(url,id){
    // 添加遮罩
    ajaxLoading();
    // 启用或者禁用采集配置
    var rows = $('#' + id).datagrid('getSelections');
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
            'cjpzid' : $("#hidCjid").val(),
            'cjpzmc': $("#txtCjmc").textbox('getValue')
        },
        success:function(data){
            // 取消遮罩
            ajaxLoadEnd();
            //执行请求后的方法
            afterAjax(data, id,'');
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
 *批量删除
 */
function removechecked() {
    // 获取所有选中的采集配置
    var checkedItems = $('#dgSjcj').datagrid('getChecked');
    // 校验至少选择一项
    if (!checkSelected("dgSjcj")){
        return;
    }
    $.messager.confirm("提示", "删除后，不再进行数据采集，您确定要删除吗？", function(flag) {
        if (flag) {
            url = '/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/del_cjpz_view';
            // 删除采集配置
            ajax_sydx(url,'dgSjcj');
        }
    });
}

/**
 * 启用,禁用适用对象
 */
function qyjk(datagrid_id,able) {
    var comf = '';
    if (able == '0'){
        comf = '设为禁用后，将不再进行数据采集，您确定要设为禁用吗？';
    }else{
        comf = '您确定要设为启用吗？';
    }
    // 获取所有选中的采集配置
    var checkedItems = $('#'+datagrid_id).datagrid('getChecked');
    // 校验至少选择一项
    if (!checkSelected(datagrid_id)){
        return;
    }
    $.messager.confirm("提示", comf, function(flag) {
        if (flag) {
            url = '/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/able_sydx_view';
            // 启用适用对象
            ajax_sydx_able(datagrid_id,url,able);
        }
    })
}

/**
 * 启用或者禁用采集配置
 **/
function ajax_sydx_able(datagrid_id,url,zt){
    // 添加遮罩
    ajaxLoading();
    // 启用或者禁用采集配置
    var rows = $('#'+datagrid_id).datagrid('getSelections');
    //创建存放对象id的数组
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
            afterAjax(data, datagrid_id,'');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

// 公共函数--更新方法
function window_update_add_func(e){

    var sfkbf = $("#combSfbf").combobox("getValue");
    jiaoyan = true;
    if(e){
        e.preventDefault();
    }
    // 添加遮罩
    ajaxLoading();
    // 添加采集配置url
    var url = '/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/add_view';
    if( $('#hidCjid').val() ){
        url = '/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/edit_view';
    }
    // 添加采集配置
    $('#sjcj_add2upd_window').find('form').form('submit', {
        url:url,
        dataType : 'json',
        type : 'post',
        queryParams : { "sfbf": sfkbf },
        onSubmit: function(){
            // 校验输入值的合法性
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
            data = $.parseJSON(data);
            if(data.state){
                // 设置采集配置的id
                $("#hidCjid").val(data.other.id);
                // 设置采集类型id
                $("#hidCjlb_hid").val(data.other.cjlb);
                // 设置采集配置id
                $("#hidCjzb_hid").val(data.other.cjzb);
                // 将发起配置说明赋值到输入框
                $("#txtZdfqjyZdfqpzsm").textbox('setValue',data.other.c_sm);
                // 将使用对象解除禁用
                $('#tt').tabs('enableTab', 1); 
                
                // 将提交的数据放到公共变量中
                old_form_data = getOldData();
            }
            if($('#hidCjid').val()){
                $("#combCjlx").combobox("disable");
                $("#combCjzb").combobox("disable");
            }
            //执行请求后的方法
            afterAjax(data, 'dgSjcj','');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

// 输入框校验
function validate(){
    // 采集配置名称
    var cjmc = $("#txtCjmc").textbox('getValue');
    // 采集配置类别
    var cjlx = $("#combCjlx").combobox('getValue');
    // 采集指标
    var cjzb = $("#combCjzb").combobox('getValue');
    var sjcj_cjlx = $('input[name="sjcj_cjlx"]:checked').val();
    // 采集配置名称
    if (cjmc=="" || cjmc==null) {
        $.messager.alert('错误','采集配置名称不可为空，请输入','error', function(){
            $("#txtCjmc").next().children().focus();
        });
        return false;
    }
    
    // 采集类别
    if (cjlx=="" || cjlx==null) {
        $.messager.alert('错误','采集类别不可为空，请选择','error', function(){
            $("#combCjlx").next().children().focus();
        });
        return false;
    }
    
    // 采集指标
    if (cjzb=="" || cjzb==null) {
        $.messager.alert('错误','采集指标不可为空，请选择','error', function(){
            $("#combCjzb").next().children().focus();
        });
        return false;
    }
    // 若类型为发起频率
    if (sjcj_cjlx=='1'){
        // 发起频率
        var fqpl = $("#txtFqpl").numberspinner('getValue');
        if (fqpl=="" || fqpl==null) {
            $.messager.alert('错误','发起频率不可为空，请输入','error', function(){
                $("#txtFqpl").next().children().focus();
            });
            return false;
        }
    }else{
        // 发起频率
        var zdfqjyZdfqpz = $("#txtZdfqjyZdfqpz").textbox('getValue');
        if (zdfqjyZdfqpz=="" || zdfqjyZdfqpz==null) {
            $.messager.alert('错误','crontab配置不可为空，请输入','error', function(){
                $("#txtZdfqjyZdfqpz").next().children().focus();
            });
            return false;
        }
    }
}
// 公共函数--添加适用对象
function window_update_add_sydx(e){
    if(e){
        e.preventDefault();
    }
    // 添加遮罩
    ajaxLoading();
    var crcs_json = $("#dgCs").datagrid('getData').rows;
    // 获取参数值输入框的内容
    var csz = [];
    $("input[id^='txtCsz_']").each(function(){
        csz.push($(this).val());
    });
    // 给传入参数添加参数值
    $.each(crcs_json,function(index,value){
        value['csz'] = csz[index];
    });
    // 适用对象id
    var sydxid = $('#hid_sydxid').val();
    var url = '';
    // 添加,编辑采集配置url
    if(sydxid == '' || sydxid == null){
        url = '/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/add_sydx_view';
    }else{
        url = '/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/edit_sydx_view';
    }
    $("#hidCrcs").val(JSON.stringify(crcs_json));
    $('#hid_cjid').val($('#hidCjid').val());
    $('#sydx_add_window').find('form').form('submit', {
        url:url,
        dataType : 'json',
        type : 'post',
        queryParams:{'state':$("#sy_state").get(0).checked,'hid_zdzjip':$("#combZdzj").combobox('getValue'),'hid_dxmc':$("#combDxmc").combobox('getValue')},
        onSubmit: function(){
            // 校验输入值的合法性
            var ret = validate_sydx();
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
            afterAjax(data, 'dgSydx','sydx_add_window');
            load_datagrid_sydx();
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
// 适用对象输入框校验
function validate_sydx(){
    // 对象名称
    var dxmc = $("#combDxmc").combobox('getValue');
    // 指定主机
    var zdzj = $("#combZdzj").combobox('getValue');
    // 采集配置名称
    if (dxmc=="" || dxmc==null) {
        $.messager.alert('错误','对象名称不可为空，请选择','error', function(){
            $("#combDxmc").next().children().focus();
        });
        return false;
    }
    // 指定主机
    if (zdzj=="" || zdzj==null) {
        $.messager.alert('错误','指定主机不可为空，请选择','error', function(){
            $("#combZdzj").next().children().focus();
        });
        return false;
    }
    // 标识有未输入的参数
    var s = true;
    // 未输入的参数代码
    var v = '';
    // 未输入的参数代码对应的参数值的输入框id
    var v_id = '';
    var rows = $("#dgCs").datagrid('getData').rows;
    $.each(rows, function(index, row){
        if(row.sfkk == false || row.sfkk == 'False'){
            if(row.csz == '' || row.csz == null){
                s = false;
                v = row.csdm;
                v_id = 'txtCsz_'+ row.id;
                return false;
            }
        }
    })
    if (!s){
        $.messager.alert('错误','参数代码['+v+']不可为空，请输入','error', function() {
            // 焦点
            $("#"+v_id).focus();
        });
    }
    return s;
}
//表格查询
function doSearch() {
    // 采集类型
    var cjlb = $("#combSearch_cjlx").combobox('getValue');
    // 采集指标
    var cjzb = $("#txtSearch_cjzb").textbox('getValue');
    // 采集名称
    var cjmc = $("#txtSearch_cjmc").textbox('getValue');
    // 是否可并发
    var sfbf = $("#combSearch_sfbf").combobox('getValue');
    // 状态
    var lx = $("#combSearch_lx").combobox('getValue');
    
    // 根据条件查询管理对象
    $("#dgSjcj").datagrid('load',{
        cjlb: cjlb,
        cjzb: cjzb,
        cjmc: cjmc,
        sfbf: sfbf,
        lx:lx
    });
}
/**
 * 获取新增，编辑框的下拉框数据
 **/
function getComb(edit){
    // 采集指标
    $("#combCjzb").combobox({
        data: cjzb,
        method:'get',
        valueField: 'id',
        textField: 'zbmc',
        onLoadSuccess: function(data){
            if( data != null && data != "" && edit == false){
                // 默认选择第一项
                $("#combCjzb").combobox('select', data[0].id);
            }
        }
    });
    $("#combCjzb").combobox('select', cjzb[0].id);
    // 采集对象类别
    $("#combCjlx").combobox({
        data: cjlb,
        method:'post',
        valueField: 'lbbm',
        textField: 'lbmc',
        onSelect: function(record){
            if(record.lbbm == ''){
                $("#combCjzb").combobox('loadData',[{'bm':'','mc':'请选择'}]);
            }else{
                $("#combCjzb").combobox('loadData',lb_zb[record.lbbm]);
            }
        }
    });
    // 默认选择第一项
    $("#combCjlx").combobox('select', cjlb[0].lbbm);
    // 是否并发
    $("#combSfbf").combobox({
        url: '/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/get_sfbf_view',
        method:'post',
        valueField: 'bm',
        textField: 'mc'
    });
}

// 格式化form表单数据
function serializeFormData(){
    // 类型
    var sjcj_cjlx = $('input[name="sjcj_cjlx"]:checked').val();
    // 发起频率
    var fqpl = $("#txtFqpl").numberspinner('getValue');
    // crontab配置
    var zdfqjyZdfqpz = $("#txtZdfqjyZdfqpz").textbox('getValue');
    // 是否可并发
    sfbf = $("#combSfbf").combobox('getValue');
    var c = {'sjcj_cjlx':sjcj_cjlx, 'fqpl':fqpl,'zdfqjyzdfqpz':zdfqjyZdfqpz,'sfbf':sfbf};
    return c;
}

// 对比基本信息有没有发生变化
function checkXXChange(){
    var data = {'state':true,'input_id':''};
    new_form_data = serializeFormData();
    // 如果类型发生改变
    if (new_form_data['sjcj_cjlx'] != old_form_data['lx']){
        return alertMsg('sjcj_cjlx','类型');
    }else{
        // 如果是发起频率
        if(new_form_data['sjcj_cjlx'] == '1'){
            //判断发起频率有没有改变
            if(new_form_data['fqpl'] != old_form_data['zdfqpz']){
                return alertMsg('fqpl','发起频率');
            }
        }else{
            // 如果是计划任务
            new_form_data['zdfqjyzdfqpz'] = new_form_data['zdfqjyzdfqpz'].replace(/\+/g,' ');
            // crontab配置校验
            if(new_form_data['zdfqjyzdfqpz'] != old_form_data['zdfqpz']){
                return alertMsg('zdfqjyzdfqpz','crontab配置');
            }
            new_form_data['sfkbf'] = new_form_data['sfkbf'] == null ? '':new_form_data['sfkbf']
            // 是否可并发
            if(new_form_data['sfbf'] != old_form_data['sfkbf']){
                return alertMsg('sfbf','是否可并发');
            }
        }
    }
    return data;
}

function alertMsg(input_id,input_name){
    var data = {'state':false,'input_id':input_id};
    $.messager.alert('警告', '基本信息的【'+input_name+'】被修改，请先进行保存！', 'warning');
    return data;
}

function getOldData(){
    var form_data = serializeFormData();
    old_form_data['lx'] = form_data['sjcj_cjlx'];
    if(old_form_data['lx']=='2'){
        old_form_data['zdfqpz'] = form_data['zdfqjyzdfqpz'].replace(/\+/g,' ');
        old_form_data['sfkbf'] = form_data['sfbf'];
    }else{
        old_form_data['zdfqpz'] = form_data['fqpl'];
    }
    return old_form_data;
}
