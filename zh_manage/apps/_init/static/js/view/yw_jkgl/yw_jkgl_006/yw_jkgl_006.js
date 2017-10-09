/**
* 监控配置列表
*/
$(document).ready(function() {
    // 渲染表格
    // 平台
    var pt = $("#hidPt").val();
    // 表格初始化后台url
    var url = "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/data_view";
    // 表格初始化:
    // 不支持多选，没有复选框，无操作区域
    datagrid = $('#dgJkpz').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "post",
        singleSelect : false,
        url: url,
        queryParams: {
            pt: pt
        },
        remoteSort: false,
        frozenColumns: [[
            { field: 'select_box', checkbox: true }
        ]],
        columns: [[
            // 名称 分析规则函数名称 分析规则 发起频率 预警级别 是否可并发 状态 操作人 操作时间 操作 
            // e.id, e.mc, e.gzmc, e.hsmc, e.zt, e.fqpl, e.sfkbf, e.yjjb, e.czr , e.czsj
            { field: 'id', title: 'ID', hidden: true },
            { field: 'mc', title: '名称', width: '18%'},
            { field: 'hsmc', title: '分析规则函数名称', width: '18%'},
            { field: 'gzmc', title: '分析规则', width: '10%'},
            { field: 'fqpl', title: '发起频率', width: '10%'},
            { field: 'yjjbmc', title: '预警级别', width: '6%'},
            { field: 'sfkbfmc', title: '是否可并发', width: '6%'},
            { field: 'ztmc', title: '状态', width: '6%'},
            { field: 'czr', title: '操作人', width: '6%'},
            { field: 'czsj', title: '操作时间', width: '10%',align: 'center'},
            { field: 'cz', title: '操作', width: '6%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:" onclick = "jkpz_add2upd(\'winJkpzAdd2Edit\',\'编辑监控配置\',\'dgJkpz\',\''+rowData.id+'\');">编辑</a> ';
            }}
            ]],
        toolbar: [{
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                jkpz_add2upd('winJkpzAdd2Edit','新增监控配置','dgJkpz', '', 'add');
            }
        }, '-', {
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 调用删除方法
                removechecked('dgJkpz');
            }
        }, '-', {
            iconCls: 'icon-ok',
            text: '设为启用',
            handler: function() {
                qyjy_jkpz('dgJkpz','1','启用后将进行数据监控，您确认要设为启用吗？');
            }
        }, '-', {
            iconCls: 'icon-cancel',
            text: '设为禁用',
            handler: function() {
                qyjy_jkpz('dgJkpz','0','禁用后不再进行数据监控，您确认要设为禁用吗？');
            }
        }]
    });
    // 查询区域初始化
    // 名称
    $("#txtSeaMc").next().children().attr("maxlength","20");
    // 分析规则默认选择“请选择”
    $("#selSeaGzid").combobox('select', '');
    // 预警级别默认选择“请选择”
    $("#selSeaYjjb").combobox('select', '');
    // 是否可并发默认选择“请选择”
    $("#selSeaSfkbf").combobox('select', '');
    // 交易状态默认选择“请选择”
    $("#selSeaZt").combobox('select', '');
    // 主页面 form tab排序
    $("#fmSearch").tabSort();
    
    // 监控配置新增或编辑翻译
    $("#lbtnFy").click(function(e){
        e.preventDefault();
        zdfqpzFy( 'txtJkpzZdfqpz','txtJkpzZdfqpzsm', 'crontab配置' );
    })
    // 监控配置新增或编辑页面元素限定长度
    // 名称
    $("#txtJkpzMc").next().children().attr("maxlength","20");
    // crontab配置
    $("#txtJkpzZdfqpz").next().children().attr("maxlength","100");
    // 描述
    $("#txtJkpzMs").next().children().attr("maxlength","100");
    // 监控配置新增或编辑按钮事件
    // 保存
    $("#lbtnJkpzSubmit").click(function(e){
        e.preventDefault();
        jkpz_add2upd_sub();
    });
    // 取消
    $("#lbtnJkpzCancel").click(function(e){
        e.preventDefault();
        $('#winJkpzAdd2Edit').window('close');
    });
    
    // 监控配置编辑 编辑规则参数
    // 保存
    $("#lbtnGzcsSubmit").click(function(e){
        e.preventDefault();
        update_fxgz_cs_sub();
    });
    // 取消
    $("#lbtnGzcsCancel").click(function(e){
        e.preventDefault();
        $('#winGzcsAdd2Edit').window('close');
    });
    //选项卡间进行切换
    $("#tbsJkpz").tabs({
        onSelect: function(title, index){
            if( index == 1 ){
                //自动发起交易列表
                xydz_pageInit();
            }
        }
    });
    
    // 响应动作操作初始化
    // 保存按钮初始化
    $("#lbtnXydzSubmit").click(function(e){
        e.preventDefault();
        xydz_add2upd_sub();
    });
    // 取消按钮初始化
    $("#lbtnXydzCancel").click(function(e){
        e.preventDefault();
        $('#winXydzAdd2Edit').window('close');
    });
    // 发起方式下拉框选择变化对应事件
    $('#selXydzFqfs').combobox({
        onSelect: function(rec){
            var fqfs = rec.value;
            if( fqfs == '3' ){
                // 计划时间可用
                $('#selXydzJhsj').timespinner('enable');
            }else{
                // 计划时间不可用
                $('#selXydzJhsj').timespinner('setValue', '');
                $('#selXydzJhsj').timespinner('disable');
            }
        }
    });
});
/**
* 条件查询
* event：时间对象
*/
function doSearch(event){
    // 取消默认提交事件
    if( event != '' && event != 'undefined' ){
        event.preventDefault();
    }
    // 平台
    var pt = $("#hidPt").val();
    // 名称
    var seaMc = $("#txtSeaMc").textbox("getValue");
    // 分析规则
    var seaGzid = $("#selSeaGzid").textbox("getValue");
    // 预警级别
    var seaYjjb = $("#selSeaYjjb").textbox("getValue");
    // 是否可并发
    var seaSfkbf = $("#selSeaSfkbf").textbox("getValue");
    // 状态
    var seaZt = $("#selSeaZt").textbox("getValue");
    
    // 根据条件查询管理对象
    $("#dgJkpz").datagrid('load',{
        pt: pt,
        mc: seaMc,
        gzid: seaGzid,
        yjjb: seaYjjb,
        sfkbf: seaSfkbf,
        zt: seaZt
    });
}

/**
* 函数名称：监控配置新增或编辑页面初始化
* 函数参数：
    winid: 打开窗口id
    wintit: 打开窗口标题
    dgId：数据表格id
    jkpzid：编辑监控配置id
    czType：操作类型：add，update
*/
function jkpz_add2upd( winid, wintit, dgId, jkpzid, handle ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 平台
    var pt = $("#hidPt").val();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/jkpz_add2upd_sel_view",
        data: { 'pt': pt, 'jkpzid': jkpzid },
        success: function(data){
            // 打开窗口
            newWindow( $( "#" + winid ),wintit,850,360 );
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                pageInit( handle, data )
                // 重新初始化tabindex
                $('#fmJkpzAdd2Upd').tabSort();
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
* 初始化监控配置新增、编辑页面
*/
function pageInit( handle, data ){
     // 执行主机
    $('#selZxzj').combobox({
        editable:false,
        data:data.zxzj_lst,
        valueField:'id',
        textField:'zwmc'
    });
    // 分析规则
    $('#selJkpzFxgz').combobox({
        editable:false,
        data:data.fxgz_lst,
        valueField:'id',
        textField:'zwmc'
    });
    // 预警级别
    $('#selJkpzYjjb').combobox({
        editable:false,
        data:data.yjjb_lst,
        valueField:'value',
        textField:'text'
    });
    // 是否可并发
    $('#selJkpzSfkbf').combobox({
        editable:false,
        data:data.sfbf_lst,
        valueField:'value',
        textField:'text'
    });
    // 新增
    if( handle == 'add' ){
        //默认选择第一个(请选择)
        if( data.zxzj_lst.length > 0 ){
            $("#selZxzj").combobox('select','');
        }        //默认选择第一个(请选择)
        if( data.fxgz_lst.length > 0 ){
            $("#selJkpzFxgz").combobox('select', '');
        }
        //默认选择第一个(预警级别)
        if( data.yjjb_lst.length > 0 ){
            $("#selJkpzYjjb").combobox('select', $("#selJkpzYjjb").combobox("getData")[0].value);
        }
        //默认选择第一个(是否可并发:默认值：1-是)
        if( data.sfbf_lst.length > 0 ){
            $("#selJkpzSfkbf").combobox('select', '1');
        }
        // 状态
        $("#nfsJkpzZt").get(0).checked = (false);
        // 禁用状态
        $('#nfsJkpzZt_link').removeClass("cursor_not_allowed");
        $('#nfsJkpzZt').prop("disabled", false);
        // 编辑分析规则参数连接(不可用)
        $("#aBjgzcs").css("color","#ccc");
        $("#aBjgzcs").removeAttr("onclick");
        // 响应动作不可用
        $("#tbsJkpz").tabs('disableTab', 1);
        // 监控配置id(清空)
        $("#hidJkpzid").val('');
    }else{
        // 编辑
        pageInit_upda( data );
    }
    // 响应动作管理
    $('#tbsJkpz').tabs('select', 0);
}
/**
* 初始化监控配置新增、编辑页面:初始化编辑信息
*/
function pageInit_upda( data ){
    // 编辑
    // 编辑对象
    var d = data.jkpz_dic;
    // 名称
    $("#txtJkpzMc").textbox('setValue', d.mc);
    // 分析规则
    $("#selJkpzFxgz").combobox('select', d.gzid);
    $("#hidYjkpzFxgz").val( d.gzid );
    // 执行主机
    $("#selZxzj").combobox('select', d.zxzj);
    // 预警级别
    $("#selJkpzYjjb").combobox('select', d.yjjb);
    // crontab配置
    $("#txtJkpzZdfqpz").textbox('setValue', d.zdfqpz);
    // 是否可并发
    $("#selJkpzSfkbf").combobox('select', d.sfkbf);
    // crontab说明
    $("#txtJkpzZdfqpzsm").textbox('setValue', d.zdfqpzsm);
    // 状态
    $("#nfsJkpzZt").get(0).checked = (d.zt=='1');
    // 禁用状态
    $('#nfsJkpzZt_link').addClass("cursor_not_allowed");
    $('#nfsJkpzZt').prop("disabled", true);
    // 描述
    $("#txtJkpzMs").textbox('setValue', d.ms);
    // 编辑分析规则参数连接(不可用)
    $("#aBjgzcs").css("color","#00C");
    $("#aBjgzcs").attr("onclick","update_fxgz_cs();");
    // 响应动作可用
    $("#tbsJkpz").tabs('enableTab', 1);
    // 监控配置id(赋值编辑id)
    $("#hidJkpzid").val(d.id);
}
/**
*监控配置新增或编辑提交
*/
function jkpz_add2upd_sub(){
    // 添加遮罩
    ajaxLoading();
    // 监控配置id
    var jkpzid = $("#hidJkpzid").val();
    // 监控配置状态
    var zt = $("#nfsJkpzZt").get(0).checked ? '1' : '0';
    // 分析规则名称
    var gzmc = $("#selJkpzFxgz").combobox("getText");
    // 执行主机
    var zxzj = $("#selZxzj").combobox("getValue");
    // 预警级别名称
    var yjjbmc = $("#selJkpzYjjb").combobox("getText");
    // 是否可并发
    var sfkbfmc = $("#selJkpzSfkbf").combobox("getText");
    var url = '/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/jkpz_add_view';
    if( jkpzid != '' ){
        url = '/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/jkpz_upd_view';
    }
    // form表单提交
    $('#fmJkpzAdd2Upd').form('submit', {
        url: url,
        queryParams: { 'jkpzid': jkpzid, 'zt': zt, 'gzmc': gzmc, 'yjjbmc': yjjbmc, 'sfkbfmc': sfkbfmc,'zxzj':zxzj },
        onSubmit: function(){
            // 校验前台信息是否满足提交条件
            var ret = jkpz_add2upd_sub_check();
            // 反馈校验结果
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
            }
            return ret;
        },
        success: function(data){
            // 处理成功后，弹出后台反馈信息，无需重新加载数据表格， 无需关闭窗口
            afterAjax(data, "dgJkpz", "");
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                pageInit_upda( data )
            }
            // 取消遮罩
            ajaxLoadEnd();
        },
        error: function(data){
            // 异常提示
            errorAjax();
            // 取消遮罩
            ajaxLoadEnd();
        }
    });
}
/**
* 新增或编辑提交前校验前台信息
*/
function jkpz_add2upd_sub_check(){
    // 名称
    var mc = $("#txtJkpzMc").textbox("getValue");
    // 分析规则
    var gzid = $("#selJkpzFxgz").combobox("getValue");
    // 预警级别
    var yjjb = $("#selJkpzYjjb").combobox("getValue");
    // crontab配置
    var zdfqpz = $("#txtJkpzZdfqpz").textbox("getValue");
    // 是否可并发
    var sfkbf = $("#selJkpzSfkbf").combobox("getValue");
    // 判断各个值是否为空，为空则不允许提交
    var ret = checkNull( mc, '名称', 'txtJkpzMc' );
    if( ret == true ){
        ret = checkNull2(gzid, '分析规则', 'selJkpzFxgz');
    }
    if( ret == true ){
        ret = checkNull2(yjjb, '预警级别', 'selJkpzYjjb');
    }
    if( ret == true ){
        ret = checkNull(zdfqpz, 'crontab配置', 'txtJkpzZdfqpz');
    }
    if( ret == true ){
        ret = checkNull2(sfkbf, '是否可并发', 'selJkpzSfkbf');
    }
    return ret;
}
/**
* 编辑分析规则对应的参数值
*/
function update_fxgz_cs( ){
    // 编辑监控配置id
    var jkpzid = $("#hidJkpzid").val();
    // 编辑监控配置id为空时，不允许编辑参数
    if( jkpzid == '' ){
        $.messager.alert('错误', '请先保存，再编辑规则参数', 'error');
        return false;
    }
    // 原分析规则
    var ygzid = $("#hidYjkpzFxgz").val();
    // 现在分析规则
    var gzid = $("#selJkpzFxgz").combobox("getValue");
    if( ygzid != gzid ){
        $.messager.alert('错误', '分析规则已修改，请先保存后再编辑规则参数', 'error');
        return false;
    }
    // 打开编辑页面
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/jkpz_gzcs_sel_view",
        data: { 'jkpzid': jkpzid, 'gzid': gzid },
        success: function(data){
            // 打开窗口
            newWindow( $( "#winGzcsAdd2Edit" ),'编辑规则参数',750,450 );
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                pageInitGzcs( data );
                // 隐藏域 监控配置id
                $("#hidGzcsJkpzid").val( jkpzid );
                // 隐藏域 规则id
                $("#hidGzcsGzid").val( gzid );
                // 重新初始化tabindex
                $('#fmGzcsAdd2Edit').tabSort();
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
* 初始化规则参数编辑页面
*/
function pageInitGzcs( data ){
    // 规则名称
    $("#txtGzcsGzmc").textbox('setValue', data.gzmc);
    // 规则描述
    $("#txtGzcsGzms").textbox('setValue', data.gzms);
    // 原参数值集合字符串
    $("#hidYcsxxStr").val( data.ycsxx_str );
    // 传入参数
    $('#dgGzcsCs').datagrid({
            nowrap : false,
            fit : false,
            height: 150,
            rownumbers : true,
            singleSelect: true,
            fitColumns : true,
            method: "post",
            remoteSort: false,
            scrollbarSize: 15,
            singleSelect : true,
            data: data.gzcs_lst,
            columns: [[
                { field: 'id', title: 'Id', hidden:true},
                { field: 'csdybid', title: 'csdybid', hidden:true},
                { field: 'csdm', title: '参数代码', width: 30},
                {field: 'cssm',title: '参数说明',width: 30},
                {field: 'sfkk',title: '是否可空',width: 22,formatter: function(value, rowData, rowIndex) {
                    if( value == 'True' ){
                        return '是';
                    }else{
                        return '否';
                    }
                }},
                {field: 'mrz',title: '默认值',width: 30},
                {field: 'csz',title: '参数值',width: 65,formatter: function(value, rowData, rowIndex) {
                    if( value == null )
                        value = '';
                    return '<input type="text" autocomplete="off" id="txtCsz_'+ rowData.id +'" name="csz_'+ rowData.id +'" value = "'+ value +'" class="textbox-text" style="width:150px" />';
                }}
        ]],
        onLoadSuccess:  function(){
            // 限定值的长度(100)
            var rows = $("#dgGzcsCs").datagrid("getRows");
            for(var i=0;i<rows.length;i++){
                var crcsid = rows[i].id
                $("#txtCsz_" + crcsid).attr("maxlength","100");
            }
        }
    });
}
/**
* 分析规则参数编辑提交
*/
function update_fxgz_cs_sub(){
    // 添加遮罩
    ajaxLoading();
    // 传入参数
    var crcs_arr = new Array();
    var rows = $("#dgGzcsCs").datagrid("getRows");
    for(var i=0;i<rows.length;i++){
        var id = rows[i].id;
        var csdybid = rows[i].csdybid;
        var csdm = rows[i].csdm;
        var cssm = rows[i].cssm;
        var sfkk = rows[i].sfkk;
        var csz = $("#txtCsz_" + id).val();
        if( sfkk == 'False' && csz == '' ){
            // 取消遮罩
            ajaxLoadEnd();
            // 参数代码[xxxx]不可为空，请录入参数值
            $.messager.alert('错误', '参数代码[' + csdm + ']不可为空，请录入参数值', 'error', function() {
                // 焦点定位
                $("#txtCsz_" + id).focus();
            });
            return false;
        }else{
            // 传入参数id~参数对应表~参数代码~参数说明~参数值
            crcs_arr.push( id + '~' + csdybid + '~' + csdm + '~'+cssm + '~' + csz );
        }
    }
    // 传入信息
    var crcs_str = crcs_arr.join("&");
    // 提交表单
    var url = '/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/jkpz_gzcs_add2edit_view'
    $('#fmGzcsAdd2Edit').form('submit', {
        url: url,
        queryParams: {'crcs_str': crcs_str},
        onSubmit: function(){
            return true;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, '', 'winGzcsAdd2Edit');
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}
/**
*批量删除
*/
function removechecked( dgid ){
    if(!checkSelected(dgid)) {
        return;
    }
    $.messager.confirm('确认', '删除后，不再进行数据分析，您确定要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 当前选中的记录
            var checkedItems = $('#' + dgid).datagrid('getChecked');
            var ids = new Array();
            $(checkedItems).each(function(index, item){
                ids.push( item['id'] );
            });
            // 发起删除请求
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/jkpz_del_view",
                data: { "ids": ids.join(",") },
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, dgid, "");
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
* 启用或禁用监控分析配置
* dgid: 操作数据库表格id
* qyjy_type: 启用禁用标识：'1': 启用， '0': 禁用
*/

function qyjy_jkpz( dgid, qyjy_type, msg ){
    if(!checkSelected(dgid)) {
        return;
    }
    $.messager.confirm('确认', msg, function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 当前选中的记录
            var checkedItems = $('#' + dgid).datagrid('getChecked');
            var ids = new Array();
            $(checkedItems).each(function(index, item){
                ids.push( item['id'] );
            });
            // 发起删除请求
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/jkpz_qyjy_view",
                data: { "ids": ids.join(","), 'qyjy_type': qyjy_type },
                success: function(data){
                    afterAjax(data, dgid, "");
                    // 取消遮罩
                    ajaxLoadEnd();
                },
                error: function(){
                    errorAjax();
                    // 取消遮罩
                    ajaxLoadEnd();
                }
            });
        }
    });
}
/**
* 初始化响应动作数据表格
*/
function xydz_pageInit(){
    // 监控配置id
    var jkpzid = $("#hidJkpzid").val();
    var url = '/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/data_xydz_view'
    // 初始化数据库表格
    $('#dgXydz').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : false,
        pageSize: 50,
        fitColumns : true,
        method: "post",
        singleSelect : false,
        url: url,
        queryParams: {
            jkpzid: jkpzid
        },
        remoteSort: false,
        frozenColumns: [[
            { field: 'select_box', checkbox: true }
        ]],
        columns: [[
            // 分析结果触发,动作函数名称,动作名称,发起方式,动作执行时间,动作参数,动作执行主机,操作
            //  a.id, a.dzid, a.fxjgcf, b.zwmc, b.hsmc, d.mc as fqfs, a.jhsj
            { field: 'id', title: 'ID', hidden: true },
            { field: 'hsmc', title: '动作函数名称', width: '11%'},
            { field: 'zwmc', title: '动作名称', width: '12%'},
            { field: 'fqfs', title: '发起方式', width: '12%'},
            { field: 'jhsj', title: '动作执行时间', width: '10%', align: 'center'},
            { field: 'fxjgcfmc', title: '分析结果触发', width: '11%'},
            { field: 'dzcs', title: '动作参数', width: '8%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:" onclick = "xydz_dzcs_ck(\'winXydzCsck\',\'动作参数查看\',\''+rowData.id+'\',\''+rowData.dzid+'\');">查看</a> ';
            }},
            { field: 'dzzxzj', title: '动作执行主机', width: '24%'},
            { field: 'cz', title: '操作', width: '6%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:" onclick = "xydz_add2upd(\'winXydzAdd2Edit\',\'编辑响应动作\',\'dgXydz\',\''+rowData.id+'\', \'update\');">编辑</a> ';
            }}
            ]],
        toolbar: [{
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                xydz_add2upd('winXydzAdd2Edit','新增响应动作','dgXydz', '', 'add');
            }
        }, '-', {
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 调用删除方法
                removechecked_xydz('dgXydz');
            }
        }]
    });
}
/**
* 函数名称：响应动作新增或编辑页面初始化
* 函数参数：
    winid: 打开窗口id
    wintit: 打开窗口标题
    dgId：数据表格id
    jkpzid：编辑监控配置id
    czType：操作类型：add，update
*/
function xydz_add2upd( winid, wintit, dgId, xydzid, handle ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 平台
    var pt = $("#hidPt").val();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/xydz_add2upd_sel_view",
        data: { 'pt': pt, 'xydzid': xydzid },
        success: function(data){
            // 打开窗口
            newWindow( $( "#" + winid ),wintit,850,360 );
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                xydz_add2upd_pageInit( handle, data )
                // 重新初始化tabindex
                $('#fmXydzAdd2Upd').tabSort();
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
* 初始化响应动作新增、编辑页面
*/
function xydz_add2upd_pageInit( handle, data ){
    // 响应动作
    $('#selXydzXydz').combobox({
        editable:false,
        data:data.xydz_lst,
        valueField:'id',
        textField:'zwmc',
        onSelect: function(rec){
        }
    });
    // 分析结果触发
    $('#selXydzFxjgcf').combobox({
        editable:false,
        data:data.fxjgcf_lst,
        valueField:'value',
        textField:'text'
    });
    // 发起方式
    $('#selXydzFqfs').combobox({
        editable:false,
        data:data.fqfs_lst,
        valueField:'value',
        textField:'text'
    });
    // 动作执行主机
    $('#selXydzDzzxzj').combobox({
        editable:false,
        data:data.dzzxzj_lst,
        valueField:'ip',
        textField:'mc'
    });
    // 传入参数
    $('#dgXydzCs').datagrid({
        nowrap : false,
        fit : false,
        height: 150,
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "post",
        remoteSort: false,
        scrollbarSize: 15,
        singleSelect : true,
        data: data.xydzcs_lst,
        url: '',
        columns: [[
            { field: 'id', title: 'Id', hidden:true},
            { field: 'csdybid', title: 'csdybid', hidden:true},
            { field: 'csdm', title: '参数代码', width: 30},
            {field: 'cssm',title: '参数说明',width: 30},
            {field: 'sfkk',title: '是否可空',width: 22,formatter: function(value, rowData, rowIndex) {
                if( value == 'True' ){
                    return '是';
                }else{
                    return '否';
                }
            }},
            {field: 'mrz',title: '默认值',width: 30},
            {field: 'csz',title: '参数值',width: 65,formatter: function(value, rowData, rowIndex) {
                if( value == null )
                    value = '';
                return '<input type="text" autocomplete="off" id="txtXydzCsz_'+ rowData.id +'" name="xydzCsz_'+ rowData.id +'" value = "'+ value +'" class="textbox-text" style="width:150px" />';
            }}
        ]],
        onLoadSuccess:  function(){
            // 限定值的长度(100)
            var rows = $("#dgXydzCs").datagrid("getRows");
            for(var i=0;i<rows.length;i++){
                var crcsid = rows[i].id
                $("#txtXydzCsz_" + crcsid).attr("maxlength","100");
            }
        }
    });
    
    // 新增
    if( handle == 'add' ){
        //默认选择第一个(请选择)
        if( data.xydz_lst.length > 0 ){
            $("#selXydzXydz").combobox('select', '');
        }
        //默认True(分析结果触发)
        if( data.fxjgcf_lst.length > 0 ){
            $("#selXydzFxjgcf").combobox('select', 'True');
        }
        //默认自动发起(发起方式)
        if( data.fqfs_lst.length > 0 ){
            $("#selXydzFqfs").combobox('select', '1');
        }
        //默认选择第一个（动作执行主机）
        if( data.dzzxzj_lst.length > 0 ){
            $("#selXydzDzzxzj").combobox('select', '');
        }
        // 响应动作id(清空)
        $("#hidXydzid").val('');
        // 响应动作变化，修改输入参数值
        $('#selXydzXydz').combobox({
            onSelect: function(rec){
                // 动作id
                var dzid = rec.id;
                // 输入参数初始化
                xydz_crcs_init( dzid );
            }
        });
    }else{
        // 编辑
        // 编辑对象
        var d = data.xydz_dic;
        // 响应动作
        $("#selXydzXydz").combobox('select', d.dzid);
        // 响应动作不可用
        $("#selXydzXydz").combobox('disable');
        // 分析结果触发
        $("#selXydzFxjgcf").combobox('select', d.fxjgcf);
        // 发起方式
        $("#selXydzFqfs").combobox('select', d.fqfs);
        // 计算时间
        $('#selXydzJhsj').timespinner('setValue', d.jhsj);
        // 当发起方式为计划发起，则计划时间可用；
        if( d.fqfs == '3' ){
            $('#selXydzJhsj').timespinner('enable');
        }
        // 动作执行主机
        $('#selXydzDzzxzj').combobox('setValues', d.zxzj_lst);
        $('#hidZxzjstr').val( d.zxzj_str );
        $('#hidZxzjmcstr').val( d.zxzjmc_str );
        // 原响应动作
        $("#hidXydzYcsxxStr").val( data.ycsxx_str );
        // 响应动作id(清空)
        $("#hidXydzid").val(d.id);
    }
}
/**
*响应动作新增或编辑提交
*/
function xydz_add2upd_sub(){
    // 添加遮罩
    ajaxLoading();
    // 响应动作所属监控分析id
    var ssjkfxid = $("#hidJkpzid").val();
    // 编辑应动作id
    var xydzid = $("#hidXydzid").val();
    // 响应动作名称
    var dzmc = $("#selXydzXydz").combobox("getText");
    // 分析结果触发名称
    var fxjgcfmc = $("#selXydzFxjgcf").combobox("getText");
    // 发起方式名称
    var fqfsmc = $("#selXydzFqfs").combobox("getText");
    // 动作执行主机
    var dzzxzj = $("#selXydzDzzxzj").combobox("getValues");
    var dzzxzjmc = $("#selXydzDzzxzj").combobox("getText");
    // 执行url
    var url = '/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/xydz_add_view';
    if( xydzid != '' ){
        url = '/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/xydz_upd_view';
    }
    // 传入参数
    var crcs_arr = new Array();
    var rows = $("#dgXydzCs").datagrid("getRows");
    for(var i=0;i<rows.length;i++){
        var id = rows[i].id;
        var csdybid = rows[i].csdybid;
        var csdm = rows[i].csdm;
        var cssm = rows[i].cssm;
        var sfkk = rows[i].sfkk;
        var csz = $("#txtXydzCsz_" + id).val();
        if( sfkk == 'False' && csz == '' ){
            // 取消遮罩
            ajaxLoadEnd();
            // 参数代码[xxxx]不可为空，请录入参数值
            $.messager.alert('错误', '参数代码[' + csdm + ']不可为空，请录入参数值', 'error', function() {
                // 焦点定位
                $("#txtXydzCsz_" + id).focus();
            });
            return false;
        }else{
            // 传入参数id~参数对应表~参数代码~参数说明~参数值
            crcs_arr.push( id + '~' + csdybid + '~' + csdm + '~'+cssm + '~' + csz );
        }
    }
    // 传入信息
    var crcs_str = crcs_arr.join("&");
    // form表单提交
    $('#fmXydzAdd2Upd').form('submit', {
        url: url,
        queryParams: { 'ssjkfxid': ssjkfxid, 'xydzid': xydzid, 'dzmc': dzmc, 'fxjgcfmc': fxjgcfmc, 'fqfsmc': fqfsmc, 'dzzxzjmc': dzzxzjmc, 'dzzxzj': dzzxzj, 'crcs_str': crcs_str },
        onSubmit: function(){
            // 校验前台信息是否满足提交条件
            var ret = xydz_add2upd_sub_check();
            // 反馈校验结果
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
            }
            return ret;
        },
        success: function(data){
            // 处理成功后，弹出后台反馈信息，无需重新加载数据表格， 无需关闭窗口，
            afterAjax(data, "dgXydz", "winXydzAdd2Edit");
            // 取消遮罩
            ajaxLoadEnd();
        },
        error: function(data){
            // 异常提示
            errorAjax();
            // 取消遮罩
            ajaxLoadEnd();
        }
    });
}
/**
* 新增或编辑提交前校验前台信息
*/
function xydz_add2upd_sub_check(){
    // 响应动作
    var xydz = $("#selXydzXydz").combobox("getValue");
    // 分析结果触发
    var fxjgcf = $("#selXydzFxjgcf").combobox("getValue");
    // 发起方式
    var fqfs = $("#selXydzFqfs").textbox("getValue");
    // 动作执行主机
    var dzzxzj = $("#selXydzDzzxzj").combobox("getValues");
    // 判断各个值是否为空，为空则不允许提交
    var ret = checkNull2( xydz, '响应动作', 'selXydzXydz' );
    if( ret == true ){
        ret = checkNull2(fxjgcf, '分析结果触发', 'selXydzFxjgcf');
    }
    if( ret == true ){
        ret = checkNull2(fqfs,'发起方式', 'selXydzFqfs');
    }
    if( ret == true ){
        ret = checkNull2(dzzxzj, '动作执行主机', 'selXydzDzzxzj');
    }
    // 校验计划时间
    if( ret == true ){
        // 发起方式为3：计划发起，则计划时间不可为空
        // 计划时间
        var jhsj = $('#selXydzJhsj').timespinner('getValue');
        if( fqfs == '3'){
            ret = checkNull(jhsj, '计划时间', 'selXydzJhsj');
        }
    }
    return ret;
}
/**
* 响应动作新增或编辑 根据响应动作切换，切换传入参数
*/
function xydz_crcs_init( xydz ){
    var xydzid = $('#hidXydzid').val();
    // 根据条件查询管理对象
    $('#dgXydzCs').datagrid({
        url: '/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/xydz_crcs_init_view'
    })
    $("#dgXydzCs").datagrid('load',{
        dzid: xydz,
        xydzid: xydzid
    });
}
/**
*批量删除(响应动作)
*/
function removechecked_xydz( dgid ){
    if(!checkSelected(dgid)) {
        return;
    }
    $.messager.confirm('确认', '删除后，分析结果不再触发该响应动作，您确认要删除该响应动作吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 当前选中的记录
            var checkedItems = $('#' + dgid).datagrid('getChecked');
            var ids = new Array();
            $(checkedItems).each(function(index, item){
                ids.push( item['id'] );
            });
            // 发起删除请求
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/xydz_del_view",
                data: { "ids": ids.join(",") },
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, dgid, "");
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
* 查看相应动作对应动态参数
* 传入参数：
    wintit: 打开窗口标题名称
    xydzid: 响应动作id
    dzid：动作id
*/
function xydz_dzcs_ck( winid, wintit, xydzid, dzid ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 获取数据
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/xydz_csck_sel_view",
        data: { 'xydzid': xydzid, 'dzid': dzid },
        success: function(data){
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 打开窗口
                newWindow( $( "#" + winid ), wintit, 850, 360 );
                // 初始化页面元素
                xydz_crcs_pageInit( data )
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
* 初始化传入参数列表
*/
function xydz_crcs_pageInit( data ){
    // 传入参数
    $('#dgXydzCsck').datagrid({
        nowrap : false,
        fit : false,
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "post",
        remoteSort: false,
        scrollbarSize: 15,
        singleSelect : true,
        data: data.xydzcs_lst,
        url: '',
        columns: [[
            { field: 'id', title: 'Id', hidden:true},
            { field: 'csdybid', title: 'csdybid', hidden:true},
            { field: 'csdm', title: '参数代码', width: 30},
            {field: 'cssm',title: '参数说明',width: 30},
            {field: 'sfkk',title: '是否可空',width: 22,formatter: function(value, rowData, rowIndex) {
                if( value == 'True' ){
                    return '是';
                }else{
                    return '否';
                }
            }},
            {field: 'mrz',title: '默认值',width: 30},
            {field: 'csz',title: '参数值',width: 65}
        ]]
    });
}
