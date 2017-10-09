$(document).ready(function() {
    
    // 渲染表格
    var cdtxid = $('#hidCdtxid').val();
    var url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_data_view?cdtxid=" + cdtxid;
    datagrid = $('#dgYydb').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        singleSelect: true,
        url: url,
        remoteSort: false,
        columns: [[
            { field: 'id', title: 'ID', hidden: true },
            { field: 'xz', title: '选择', width: '5%', formatter: function(value, rowData, rowIndex){
                return '<input type="radio" name="selectRadio" id="selectRadio' + rowIndex + '" value="' + rowData.id + '|1" />';
                }
            },
            { field: 'jc', title: '简称', width: '13%'},
            { field: 'mc', title: '挡板名称', width: '20%'},
            { field: 'czr', title: '操作人', width: '12%'},
            { field: 'czsj', title: '操作时间', width: '13%', align: 'center'},
            { field: 'ms', title: '描述', width: '26%'},
            { field: 'cz', title: '操作', width: '9%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="showHide(\'update\',\'dgYydb\',\''+rowData.id+'\',\'divYydbWindow\',\'编辑挡板\');">编辑</a> <a href="javascript:removeYydb(\'dgYydb\','+rowIndex+');">删除</a>';
            } }
        ]],
        toolbar : [
            {
                iconCls : 'icon-add',
                text : '新增',
                handler : function() {
                    // 新增
                    showHide( 'add','dgYydb','', 'divYydbWindow', '新增挡板' )
                }
            }
        ],
        onLoadSuccess: function(data) {
            // 默认选择行
            var dbssid = $( "#hidDbssid" ).val();
            var rows = data.rows;
            for(var i = 0, len = rows.length; i < len; i++) {
                if (rows[i].id == dbssid.split('|')[0]) {
                    $('#dgYydb').datagrid("selectRow", i);
                }
            }
        },
        onSelect: function( rowIndex, rowData ){
            $( "#hidDbssid" ).val(rowData.id + '|1');
            checkRadio( 'selectRadio' );
        }
    });
    
    // 最大值限制
    $("#txtJc").next().children().attr("maxlength","50");
    $("#txtMc").next().children().attr("maxlength","50");
    $("#txtMs").next().children().attr("maxlength","100");
    
    // 初始化按钮(保存)
    $("#dbglWindowOkAdd").click(function(e){
        e.preventDefault();
        // 保存提交
        saveSub( 'dgYydb', 'divYydbWindow' );
    })
    
    // 初始化按钮（取消）
    $("#dbglWindowCancel").click(function(e){
        e.preventDefault();
        $("#divYydbWindow").window('close');
    })
    
    // 确定选择挡板
    $("#window_see_log").click(function(){
        //确定选择挡板
        selectDb();
    });
    
    // 渲染表格( 已有测试案例 )
    var zlcdyid = $('#hidZlcdyid').val();
    var url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_testdb_data_view?zlcdyid=" + zlcdyid;
    $('#dgYycsal').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        singleSelect: true,
        url: url,
        remoteSort: false,
        columns: [[
            { field: 'id', title: 'ID', hidden: true },
            { field: 'xz', title: '选择', width: '4%', formatter: function(value, rowData, rowIndex){
                return '<input type="radio" name="selectRadio" id="selectRadioT' + rowIndex + '" value="' + rowData.id + '|2" />';
                }
            },
            { field: 'csalmc', title: '测试案例名称', width: '14%' },
            { field: 'bzmc', title: '步骤名称', width: '13%' },
            { field: 'ywmc', title: '业务名称', width: '20%' },
            { field: 'jymc', title: '交易名称', width: '20%' },
            { field: 'ms', title: '描述', width: '10%' },
            { field: 'fhz', title: '返回值', hidden: true },
            { field: 'cktgxx', title: '查看跳过信息', width: '9%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:seeTgxx(\'divTestTgWindow\','+rowIndex+');">查看</a>';
            } }
        ]],
        onLoadSuccess: function(data) {
            // 默认选择行
            var dbssid = $( "#hidDbssid" ).val();
            var rows = data.rows;
            for(var i = 0, len = rows.length; i < len; i++) {
                if (rows[i].id == dbssid.split('|')[0]) {
                    $('#dgYycsal').datagrid("selectRow", i);
                }
            }
        },
        onSelect: function( rowIndex, rowData ){
            $( "#hidDbssid" ).val(rowData.id + '|2');
            checkRadio( 'selectRadio' );
        }
    });
    
    // 初始化已有测试案例查看跳过信息按钮（取消）
    $("#tgWindowCancel").click(function(e){
        e.preventDefault();
        $("#divTestTgWindow").window('close');
    })
});

/**
* 新增or编辑挡板弹窗
* handle: 操作类型
* dgid：数据表格id
* updid：编辑信息id
* winid：open窗口的win
* wintit：open窗口的title
*/
function showHide( handle, dgid, updid, winid, wintit ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 向后台请求信息
    var cdtxid = $("#hidCdtxid").val();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_add2edit_sel_view",
        data: { 'cdtxid': cdtxid, 'dbid': updid },
        success: function(data){
            // 打开窗口
            newWindow($( "#" + winid ),wintit,520,420);
            // 反馈信息
            data = $.parseJSON( data );
            if( data.state == true ){
                // 初始化页面元素
                pageInit( handle, data )
                // 重新初始化tabindex
                $('#dbglform').tabSort();
            }else{
                afterAjax(data, '', '');
            }
        },
        error: function(){
            errorAjax();
        }
    });
}

/**
*新增or编辑挡板弹窗口初始化
*/
function pageInit( handle, data ){
    //初始化输出要素
    $('#dgScys').datagrid({
            nowrap : false,
            fit : false,
            rownumbers : true,
            singleSelect: true,
            fitColumns : true,
            method: "get",
            remoteSort: false,
            scrollbarSize: 15,
            singleSelect : true,
            data: data.scys_lst,
            columns: [[
                { field: 'id', title: 'ID', hidden: true },
                { field: 'ysmc', title: '定义输出要素', width: 28 },
                { field: 'ysz', title: '值', width: 67,formatter: function(value,rowData,rowIndex) {
                    if( value == null ){
                        value = ''
                    }
                    return '<input type="text" autocomplete="off" id="txtYsz_'+ rowData.ysmc +'" name="ysz_'+ rowData.ysmc +'" value = "'+ value +'" class="easyui-textbox" style="width:150px" />';
                } }
            ]]
    });
    //限定值的长度(250)
    var rows = $("#dgScys").datagrid("getRows");
    for(var i=0;i<rows.length;i++){
        var ysmc = rows[i].ysmc
        $("#txtYsz_" + ysmc).attr("maxlength","250");
    }
    // 根据类型不同做不同处理
    if(handle=='add'){
        // 简称
        $("#txtJc").textbox('enable');
        // 返回值默认选中第一个值
        if( $("#selFhz").combobox("getData").length > 0 ){
            $("#selFhz").combobox('select', $("#selFhz").combobox("getData")[0].value);
        }
        // 清空dbid
        $("#hidDbid").val('');
    }
    else if(handle=='update'){
        // 编辑对象信息
        var d = data.yydb_dic;
        // 简称
        $("#txtJc").textbox('setValue', d.jc);
        $("#txtJc").textbox('disable');
        // 挡板名称
        $("#txtMc").textbox('setValue', d.mc);
        // 挡板描述
        $("#txtMs").textbox('setValue', d.ms);
        // 返回值
        if( $("#selFhz").combobox("getData").length > 0 ){
            $("#selFhz").combobox('select', d.fhz);
        }
        // 赋值dbid
        $("#hidDbid").val(d.id);
    }
}

/**
*新增or编辑保存提交
*/
function saveSub( dgid, winid ){
    // 添加遮罩
    ajaxLoading();
    // C端通讯ID
    var cdtxid = $( "#hidCdtxid" ).val();
    // 出错提示(默认新增)
    var msg = "新增失败，请稍后再试";
    var url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_add_view";
    if ( $("#hidDbid").val() != "" ){
        // 修改
        url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_edit_view",
        msg = "修改失败，请稍后再试";
    }
    
    // 获取要素信息集合
    var scys = {};
    var rows = $("#dgScys").datagrid("getRows");
    for(var i=0;i<rows.length;i++){
        var id = rows[i].id;
        var ysmc = rows[i].ysmc;
        var ysz = $("#txtYsz_" + ysmc).val();
        
        scys[id+'|'+ysmc] = ysz;
    };
    
    // 提交表单
    $('#' + winid).find('form').form('submit', {
        url: url,
        queryParams: {'cdtxid': cdtxid, 'ysxx_str': JSON.stringify(scys)},
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
            afterAjax(data, dgid, winid);
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/**
*编辑页面提交前校验
*/
function subCheck(){
    // 编辑C端通讯
    var dbid = $("#hidDbid").val();
    // 返回参数默认true
    var ret = true;
    // 编辑和新增都需要校验的信息
    var jc = $("#txtJc").textbox("getValue");
    var mc = $("#txtMc").textbox("getValue");
    var fhz = $("#selFhz").textbox("getValue");
    //简称
    if( ret ){
        ret = checkNull( jc, '简称', 'txtJc' );
    }
    // 校验简称格式
    if( ret ){
        ret = checkBm( jc, '简称', 'txtJc' )
    }
    // 挡板名称
    if( ret ){
        ret = checkNull( mc, '挡板名称', 'txtMc' );
    }
    //挡板名称格式
    if( ret ){
        ret = checkMc( mc, '挡板名称', 'txtMc' );
    }
    // 返回值
    if( ret ){
        ret = checkNull( fhz, '返回值', 'selFhz' );
    }
    
    return ret
}

/**
*批量删除
*/
function removeYydb( dgid, rowIndex ){
    
    $.messager.confirm('确认', '挡板删除后数据将无法恢复，您确认要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 获取删除信息
            var d = $('#'+dgid).datagrid('getData').rows[rowIndex];
            var dbid = d.id;
            var jc = d.jc;
            var mc = d.mc;
            // 发起删除
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_del_view",
                data: { "dbid": dbid, 'jc': jc, 'mc': mc },
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax( data, dgid, "" );
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
*确定选择为挡板
*/
function selectDb(){
    var xz = getRadioValue( 'selectRadio' );
    if( xz == false ){
        $.messager.alert('错误', '请先选择挡板信息，再提交', 'error');
        return false;
    }
    $.messager.confirm('确认', '是否确认选择此挡板？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            var cdtxid = $( "#hidCdtxid" ).val();
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_sel_view",
                data: { "dbid": xz, 'cdtxid': cdtxid },
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    // 转化为json数据
                    if(typeof data == 'string'){
                        data = $.parseJSON(data);
                    }
                    // 成功关闭页面，刷新主页面
                    if( data.state == true ){
                        $( "#hidDbssid" ).val(xz);
                        $.messager.alert('提示', data.msg.replace("\n","<br/>"), 'info', function(){
                            parent.$("#divDbglWindow").window('close');
                            parent.$('#dgCdtx').datagrid('reload');
                        });
                    }else{
                        // 失败提示错误信息
                        afterAjax( data, '', "" );
                        
                    }
                },
                error: function(){
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    })
}

/**
*获取选中的值
*/
function getRadioValue(name){
    var radioes = document.getElementsByName(name);
    for(var i=0;i<radioes.length;i++){
        if(radioes[i].checked){
            return radioes[i].value;
        }
    }
    return false;
}

/**
*选择某个值
*/
function checkRadio( name ){
    var dbssid = $( "#hidDbssid" ).val();
    var oRadio = document.getElementsByName(name);
    //循环
    for(var i=0;i<oRadio.length;i++) {
        //比较值
        if(oRadio[i].value==dbssid){
            //修改选中状态
            oRadio[i].checked=true;
            //停止循环
            break;
        }
    }
}

/**
*查看已有测试案例跳过输出信息
*/
function seeTgxx( winid, rowIndex ){
    // 选择行信息
    var d = $('#dgYycsal').datagrid('getData').rows[rowIndex];
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_testdb_query_view",
        data: { 'fhz': d.fhz, 'jdcsalzxbzid': d.id },
        success: function(data){
            // 打开窗口
            newWindow($( "#" + winid ),'跳过输出信息',520,340);
            // 反馈信息
            data = $.parseJSON( data );
            if( data.state == true ){
                // 初始化页面元素
                pageInit2( data )
                // 重新初始化tabindex
                $('#tgform').tabSort();
            }else{
                afterAjax(data, '', '');
            }
        },
        error: function(){
            errorAjax();
        }
    });
}

/**
*初始化测试案例跳过信息查看页面初始化
*/
function pageInit2( data ){
    //初始化输出要素
    $('#dgTgScys').datagrid({
            nowrap : false,
            fit : false,
            rownumbers : true,
            singleSelect: true,
            fitColumns : true,
            method: "get",
            remoteSort: false,
            scrollbarSize: 15,
            singleSelect : true,
            data: data.scys_lst,
            columns: [[
                { field: 'id', title: 'ID', hidden: true },
                { field: 'ysdm', title: '定义输出要素', width: 28 },
                { field: 'ysz', title: '值', width: 67 }
            ]]
    });
    
    $("#spFhz").text( data.fhz );
    
}
