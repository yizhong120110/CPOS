$(document).ready(function() {
    // 绑定增加/修改弹出框中的取消按钮
    $('#window_cancel').click(function(){
        $('#bean_window').window('close');
    });
    // 渲染表格
    var zlcdyid = $('#hidZlcdyid').val();
    var dfjymc = $('#hidDfjymc').val();
    var url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_csal_data_view?zlcdyid=" + zlcdyid;
    datagrid = $('#dgCsal').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: url,
        remoteSort: false,
        frozenColumns: [[
            { field: 'ck', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: 'ID', hidden: true },
            { field: 'mc', title: '名称', width: '25%'},
            { field: 'dfjymc', title: '对方交易名称', width: '25%', formatter: function(value,rowData,rowIndex) {
                return dfjymc;
            }
            },
            { field: 'ms', title: '描述', width: '30%'},
            { field: 'cz', title: '操作', width: '14%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:showHide(\'update\',\'dgCsal\',\''+rowData.id+'\',\'divCsalWindow\',\'编辑通讯测试案例\');">编辑</a> ';
            } }
        ]],
        toolbar : [
            {
                iconCls : 'icon-add',
                text : '新增',
                handler : function() {
                    // 新增
                    showHide( 'add','dgYydb','', 'divCsalWindow', '新增通讯测试案例' )
                }
            }, {
                iconCls : 'icon-remove',
                text : '删除',
                handler : function() {
                    // 调用删除方法
                    removechecked( 'dgCsal' );
                }
            },{
                iconCls : 'icon-auto-test',
                text : '进行自动化测试',
                handler : function() {
                    // 自动化测试
                    auto_test();
                }
        }
        ]
        
    });
    
    // 最大值限制
    $("#txtMc").next().children().attr("maxlength","50");
    $("#txtMs").next().children().attr("maxlength","50");
    
    // 初始化按钮(保存)
    $("#lbtnCsalSubmit").click(function(e){
        e.preventDefault();
        // 保存提交
        saveSub( 'dgCsal', 'divCsalWindow' );
    });
    
    // 初始化按钮（取消）
    $("#lbtnCsalCancel").click(function(e){
        e.preventDefault();
        $("#divCsalWindow").window('close');
    });
});

/**
* 新增or编辑测试案例弹窗
* handle: 操作类型
* dgid：数据表格id
* updid：编辑信息id
* winid：open窗口的win
* wintit：open窗口的title
*/
function showHide( handle, dgid, updid, winid, wintit ){
    // 向后台请求信息
    var cdtxid = $("#hidCdtxid").val();
    var ssywid = $("#hidSsywid").val();
    var zlcdyid = $("#hidZlcdyid").val();
    
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_csal_add2edit_sel_view",
        data: { 'cdtxid': cdtxid, 'ssywid': ssywid, 'csalid': updid },
        success: function(data){
            // 打开窗口
            newWindow($( "#" + winid ),wintit,520,400);
            // 反馈信息
            data = $.parseJSON( data );
            // 初始化页面元素
            pageInit( handle, data )
            // 重新初始化tabindex
            $('#csalform').tabSort();
        },
        error: function(){
            errorAjax();
        }
    });
}

/**
* 页面初始化
*/
function pageInit( handle, data ){
    //初始化输入要素
    $('#dgSrys').datagrid({
            nowrap : false,
            fit : false,
            height: 150,
            rownumbers : true,
            singleSelect: true,
            fitColumns : true,
            method: "get",
            remoteSort: false,
            scrollbarSize: 15,
            singleSelect : true,
            data: data.srys_lst,
            columns: [[
                { field: 'id', title: 'ID', hidden: true },
                { field: 'ysdm', title: '输入要素', width: 28 },
                { field: 'yysz', title: '原值', hidden: true },
                { field: 'ysz', title: '值', width: 67,formatter: function(value,rowData,rowIndex) {
                    return '<input type="text" autocomplete="off" id="txtSrYsz_'+ rowData.ysdm +'" name="srYsz_'+ rowData.ysdm +'" value = "'+ value +'" class="textbox-text" style="width:150px" />';
                } }
            ]]
    });
    //初始化输出要素
    $('#dgScys').datagrid({
            nowrap : false,
            fit : false,
            height: 150,
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
                { field: 'ysdm', title: '输出要素', width: 95 }
            ]]
    });
    
    // 限定值的长度(250)
    var rows = $("#dgSrys").datagrid("getRows");
    for(var i=0;i<rows.length;i++){
        var ysdm = rows[i].ysdm
        $("#txtSrYsz_" + ysdm).attr("maxlength","250");
    }
    // 所属通讯
    var dfjymc = $("#hidDfjymc").val();
    $("#spnSstx").text(dfjymc);
    // 所属业务
    $("#spnSsyw").text(data.ywmc);
    
    // 根据类型不同做不同处理
    if(handle=='add'){
        // 名称
        $("#txtMc").textbox('enable');
        // 清空dbid
        $("#hidCsalid").val('');
    }else if(handle=='update'){
        // 编辑对象信息
        var d = data.cdal_dic;
        // 名称
        $("#txtMc").textbox('setValue', d.mc);
        $("#txtMc").textbox('disable');
        // 挡板描述
        $("#txtMs").textbox('setValue', d.ms);
        // 赋值dbid
        $("#hidCsalid").val(d.id);
    }
}

/**
* 测试案例保存提交
*/
function saveSub( dgid, winid ){
    // 添加遮罩
    ajaxLoading();
    // C端通讯ID
    var cdtxid = $( "#hidCdtxid" ).val();
    // 所属业务
    var ssywid = $( "#hidSsywid" ).val();
    // 子流程定义id
    var zlcdyid = $("#hidZlcdyid").val();
    var ysxx_sr_str = '';
    var ysxx_sc_str = '';
    
    // 获取要素信息集合
    // 输入要素
    var ysxx_sr_arr = new Array();
    var rows = $("#dgSrys").datagrid("getRows");
    for(var i=0;i<rows.length;i++){
        var id = rows[i].id;
        var ysdm = rows[i].ysdm;
        var yysz = rows[i].yysz;
        var ysz = $("#txtSrYsz_" + ysdm).val();
        if( yysz != ysz ){
            ysxx_sr_arr.push( id + '^' + ysdm + '^'+ysz );
        }
    }
    var ysxx_sr_str = ysxx_sr_arr.join("~")
    
    // 新增&编辑操作
    var msg = "新增失败，请稍后再试";
    var url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_csal_add_view";
    if ( $("#hidCsalid").val() != "" ){
        // 修改
        url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_csal_edit_view",
        msg = "修改失败，请稍后再试";
    }else{
        // 输出要素
        var ysxx_sc_arr = new Array();
        var rows = $("#dgScys").datagrid("getRows");
        for(var i=0;i<rows.length;i++){
            var ysdm = rows[i].ysdm;
            ysxx_sc_arr.push( '^' + ysdm + '^' );
        }
        var ysxx_sc_str = ysxx_sc_arr.join("~")
    }
    
    // 提交表单
    $('#' + winid).find('form').form('submit', {
        url: url,
        queryParams: {'cdtxid': cdtxid, 'ssywid': ssywid, 'zlcdyid': zlcdyid, 'ysxx_sr_str': ysxx_sr_str, 'ysxx_sc_str': ysxx_sc_str},
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
            if(typeof data == 'string'){
                data = $.parseJSON(data);
            }
            if( data.state == true ){
                parent.$('#dgCdtx').datagrid('reload');
            }
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/**
* 编辑页面提交前校验
*/
function subCheck(){
    // 返回参数默认true
    var ret = true;
    // 编辑和新增都需要校验的信息
    var mc = $("#txtMc").textbox("getValue");
    // 测试案例名称
    if( ret ){
        ret = checkNull( mc, '测试案例名称', 'txtMc' );
    }
    
    return ret
}

/**
* 批量删除
*/
function removechecked( dgid ){
    if(!checkSelected(dgid)) {
        return;
    }
    $.messager.confirm('确认', '测试案例删除后数据将无法恢复，您确定要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 当前选中的记录
            var checkedItems = $('#' + dgid).datagrid('getChecked');
            var ids = new Array();
            var ids_mc = new Array();
            $(checkedItems).each(function(index, item){
                ids.push( item['id'] );
                ids_mc.push( item['mc'] );
            });
            
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_csal_del_view",
                data: { "ids": ids.join(","), 'ids_mc': ids_mc.join(",") },
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, dgid, "");
                    if(typeof data == 'string'){
                        data = $.parseJSON(data);
                    }
                    if( data.state == true ){
                        parent.$('#dgCdtx').datagrid('reload');
                    }
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
* 确定选择为挡板
*/
function selectDb(){
    var xz = getRadioValue( 'selectRadio' );
    if( xz == false ){
        $.messager.alert('错误', '请先选择挡板信息，再提交', 'error');
        return false;
    }
    $.messager.confirm('提示', '是否确认选择此挡板？', function(r){
        if (r) {
            var cdtxid = $( "#hidCdtxid" ).val();
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_sel_view",
                data: { "dbid": xz, 'cdtxid': cdtxid },
                success: function(data){
                    afterAjax( data, "", "" );
                    if(typeof data == 'string'){
                        data = $.parseJSON(data);
                    }
                    if( data.state == true ){
                        $( "#hidDbssid" ).val(xz);
                        parent.$('#dgCdtx').datagrid('reload');
                    }
                },
                error: function(){
                    errorAjax();
                }
            });
        }
    })
}

/**
* 获取选中的值
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
* 选择某个值
*/
function checkRadio( name ){
    var dbssid = $( "#hidDbssid" ).val();
    var oRadio = document.getElementsByName(name);
    //循环
    for(var i=0;i<oRadio.length;i++) {
        //比较值
        if(oRadio[i].value==dbssid){
            oRadio[i].checked=true; //修改选中状态
            break; //停止循环
        }
    }
}

/**
* 查看已有测试案例跳过输出信息
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
            // 初始化页面元素
            pageInit2( data )
            // 重新初始化tabindex
            $('#tgform').tabSort();
        },
        error: function(){
            errorAjax();
        }
    });
}

/**
* 初始化测试案例跳过信息查看页面初始化
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

/**
 * 弹出自动化测试窗口 todo
 * @returns {boolean}
 */
function auto_test(){
    var row = $('#dgCsal').datagrid('getSelections');
    if(row.length < 1){
        $.messager.alert('提示', '请选择需要测试的测试案例!', 'info');
        return false;
    }
    var csalids='';
    for(var i = 0,len=row.length; i< len; i++){
        csalids+= row[i].id+",";
    }
    
    $("#zdhcsal_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_014/kf_ywgl_014_view/index_view?csalids="+csalids);
    // 打开自动化测试的结果
    newWindow($("#bean_window"),'自动化测试',600,360);
}

/**
 * 弹出自动化测试日志查看
 * @returns {boolean}
 */
function view_rz(csalid,pc,zxjg,jgsm,demoid,ssid,lb,event){
    $("#ifmJbxx").attr("src","/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/index_view?lx=zlc"+"&id="+ssid+"&csalid="+csalid+"&pc="+pc+"&zxjg="+zxjg+"&jgsm="+jgsm+"&lxdm=4");
    // 打开自动化测试的结果
    newWindow($("#divJbxx"),'日志查看',1200,480);
}
