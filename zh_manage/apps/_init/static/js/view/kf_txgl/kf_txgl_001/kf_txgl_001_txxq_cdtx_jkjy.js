var upd_jdysid = ''
$(document).ready(function() {
    
    // form tab排序
    $("#divQyjy").children('form').tabSort();
    
    // 初始化状态
    $("#nfsZt").get(0).checked = (zt=="1");
    
    // 渲染表格( 包含字段 )
    datagrid = $('#dgBhzd').datagrid({
        nowrap : false,
        fit : true,
        height: '150px',
        rownumbers : true,
        pagination : false,
        fitColumns : true,
        method: "get",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        url: '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_jkjy_qyjy_sel_data_view?cdtxid=' + cdtxid,
        columns: [[
            { field: 'id', title: '要素ID', hidden: true },
            { field: 'bm', title: '字段代码', width: '12%' },
            { field: 'ysmc', title: '字段名称', width: '20%' },
            { field: 'jkjy', title: '是否有效性校验', width: '20%', formatter: function(value,rowData,rowIndex) {
                return value=="1" ? "是" : "否"; 
            } },
            { field: 'ssgzmc', title: '校验规则', width: '13%' },
            { field: 'zjcs', title: '追加参数', width: '20%' },
            { field: 'cz', title: '操作', width: '10%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="showHide(\'dgBhzd\',\''+rowData.id+'\',\'divJdysWindow\',\'接口配置\');">配置</a>';
            } }
        ]]
    });
    
    // 进程并发数
    
    // 最大值限制
    $("#txtCsdm").next().children().attr("maxlength","32");
    $("#txtCsz").next().children().attr("maxlength","50");
    $("#txtCsms").next().children().attr("maxlength","150");
    
    //按钮初始化
    //保存
    $("#lbtnJkjySave").click(function(e){
        e.preventDefault();
        editSub();
    })
    //取消
    $("#lbtnJkjyCancel").click(function(e){
        e.preventDefault();
        parent.$("#divJkjyWindow").window('close');
    })
    //保存
    $("#lbtnJdysSubmit").click(function(e){
        e.preventDefault();
        saveSub();
    })
    //取消
    $("#lbtnJdysCancel").click(function(e){
        e.preventDefault();
        $("#divJdysWindow").window('close');
    })
});

/**
* 接口校验状态修改启用状态
*/
function editSub(){
    // 添加遮罩
    ajaxLoading();
    // 状态
    var zt = $( "#nfsZt" ).get(0).checked ? "1" : "0";
    // 提交表单
    $('#divQyjy').find('form').form('submit', {
        url: '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_jkjy_qyjy_view',
        queryParams: {'cdtxid': cdtxid, 'jkqyzt': zt},
        onSubmit: function(){
            // 获取校验元素值
            var ret = checkXx( zt );
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
            afterAjax(data, "", "");
            parent.$('#dgCdtx').datagrid('reload');
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            $.messager.alert('警告','状态编辑请求出现异常，请稍后重试','warning');
        }
    });
}

/**
* 编辑接口启用状态提交前台校验
*/
function checkXx( zt ){
    
    // 修改状态由“禁用”变为“启用”后的前台校验信息, 接口状态有为是的存在
    if( zt == '1' ){
        var rows = $("#dgBhzd").datagrid("getRows");
        var state = false;
        for(var i=0;i<rows.length;i++){
            var jkjy = rows[i].jkjy;
            if( jkjy == '1' ){
                state = true;
                break;
            }
        }
        if( state == false ){
            $.messager.alert('警告','没有接口需要校验，请先配置，再启用！','error');
            return false;
        }
    }
    return true;
}

/**
* 编辑节点要素弹窗
* jdysid：节点要素id
* winid：open窗口的win
* wintit：open窗口的title
*/
function showHide( dgid, jdysid, winid, wintit ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    upd_jdysid = jdysid;
    // 向后台请求信息
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_jkjy_qyjy_jdys_sel_view",
        data: {'jdysid': jdysid},
        success: function(data){
            // 打开窗口
            newWindow($( "#" + winid ),wintit,500,350);
            // 反馈信息
            data = $.parseJSON(data);
            if( data.state == true ){
                // 初始化页面元素
                pageInit( data );
                // 重新初始化tabindex
                $('#txcsform').tabSort();
            }else{
                afterAjax(data, '', '');
            }
            
            // form tab排序
            $("#divJdysWindow").children('form').tabSort();
        },
        error: function(){
            errorAjax();
        }
    });
}

/**
* 页面初始化
*/
function pageInit( data ){
    // 编辑对象信息
    $("#spZddm").text( data.zddm );
    var zdmc = data.zdmc
    if ( zdmc == null ){
        zdmc = ''
    }
    $("#spZdmc").text( zdmc );
    if( data.sfjkjy != null && data.sfjkjy != '' ){
        $("#selJkjy").combobox('select', data.sfjkjy);
    }else{
        $("#selJkjy").combobox('select', '0');
    }
    $('#selJygzmc').combobox({
        editable:false,
        data:data.jygz_lst,
        valueField:'value',
        textField:'value',
        onSelect: function (r) {
            if( r ){
                $( '#txtHsms' ).textbox('setValue', r.ms);
            }
        }
    });
    //默认选择
    if( $("#selJygzmc").combobox("getData").length > 0 ){
        if( data.jygzmc ){
            $("#selJygzmc").combobox('select', data.jygzmc);
        }else{
            $("#selJygzmc").combobox('select', '请选择');
        }
    }
    $("#txtZjcs").textbox('setValue', data.zjcs);
    $("#txtHsms").textbox('disable');
}

/**
* 信息提交
*/
function saveSub( ){
    // 添加遮罩
    ajaxLoading();
    // 修改
    url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_jkjy_qyjy_jdys_view",
    // 提交表单
    $('#divJdysWindow').find('form').form('submit', {
        url: url,
        queryParams: {'jdysid': upd_jdysid},
        onSubmit: function(){
            // 校验页面信息是否符合要求
            var ret = subCheck();
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
            afterAjax(data, '', '');
            $('#dgBhzd').datagrid('reload');
            $("#divJdysWindow").window('close');
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/**
* 要素页面编辑前校验 todo
*/
function subCheck(){
    // 是否接口有效性校验
    var sfjkjy = $("#selJkjy").combobox("getValue");
    var jygzmc = $("#selJygzmc").combobox("getValue");
    if( sfjkjy == '1' && jygzmc == '请选择' ){
        $.messager.alert( '错误', '是否有效性校验为“是”时，校验规则不可为空，请选择', 'error' );
        return false;
    }
    var zjzs = $("#txtZjcs").textbox("getValue");
    if( zjzs != '' ){
        var ret = check_dic( zjzs );
        if( ret == false ){
            $.messager.alert( '错误', '参数录入不合法，请以{key:value}形式录入', 'error' );
            return false;
        }
    }
    return true;
}

/**
* 交易字符串是否是字典
*/
function check_dic( str ){
    str = str.replace(/\'/g, '"');
    var obj = null;
    try {
        obj = JSON.parse(str);
    } catch(e) {
        obj = null;
    }
    if( $.type( obj ) == "object" ){
        return true;
    }else{
        return false;
    }
}
