// 平台
var pt;
// 操作栏隐藏数据值，默认为true，隐藏
var hidval = true;
$(document).ready(function() {
    var sfxytb = $("#hidSfxytb").val()
    if ( sfxytb == 'True' ){
        newWindow($("#divSjktbxxtskWindow"),'同步信息提示',500,260);
    }
    // 平台
    pt = $("#hidPt").val();
    // 平台为开发平台，操作栏可用
    if( pt == 'kf' ){
        hidval = false;
    }
    // 渲染表格
    $('#dgSjkmx').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        singleSelect:true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_view?ywid="+$("#hidYwid").val(),
        remoteSort: false,
        columns: [[
            { field: 'id', title: 'ID', hidden:true },
            { field: 'sjbmc', title: '数据表名称', width: 15 },
            { field: 'sjbmcms', title: '数据表名称描述', width: 18, formatter: function(value,row,index) {
                return '<a href="javascript:;" onclick = "sjb_operation(\''+'upd'+'\',\''+row.sjbmc+'\', \''+ row.id+'\', \''+value+'\');">'+value+'</a>';
            } },
            { field: 'bbh', title: '版本号', width: 6, formatter: function(value,row,index) {
                if (row.bbsftj=='1') {
                    return '<span class="clean">'+value+'</span>';
                } else {
                    return '<span class="modified">'+value+'</span>';
                }
            } },
            { field: 'czr', title: '操作人', width: 10 },
            { field: 'czsj', title: '操作时间', width: 15, align:'center' },
            { field: 'Sjbxx', title: '数据表详细信息', width: 9, formatter: function(value,row,index) {
                return '<a href="javascript:;" onclick = "sjkxxck_tab(event,\''+row.sjbmcms+'\',\''+ row.id+'\');">'+'详细信息'+'</a>';
            } },
            { field: 'Operation', title: '操作', width: 15, hidden: hidval, formatter: function(value,rowData,index) {
                return '<a href="javascript:;" onclick ="bbtj(\''+'sjk'+'\',\''+rowData.bbsftj+'\',\''+rowData.id+'\',\''+'dgSjkmx'+'\');">版本提交</a> '+
                '<a href="javascript:;" onclick="bbxxck(event,\''+rowData.sjbmc+'\',\''+rowData.id+'\');">版本信息查看</a>'
            } }
        ]],
        toolbar : [ {
            iconCls : 'icon-look-over',
            text : '同步信息查看',
            handler : function() {
                tbxxck_tool();
            }}
        ],
        onLoadSuccess: function(data) {
            // 点击刷新按钮时，刷新整个页面
            $('.datagrid-pager td:last a').click(function(){
                location.reload();
            });
        }
    });
    // 开发系统
    if( pt == 'kf' ){
        $('#dgSjkmx').datagrid({
            toolbar : [ {
                    iconCls : 'icon-add',
                    text : '新增数据表',
                    handler : function() {
                        sjb_operation( 'add','','','');
                    }
                },{
                    iconCls : 'icon-look-over',
                    text : '同步信息查看',
                    handler : function() {
                        tbxxck_tool();
                    }}
                ],
        })
    }
    // 查询区域初始化
    // 名称
    $("#txtSeaMc").next().children().attr("maxlength","27");
    $("#txtSeaMs").next().children().attr("maxlength","25");
    // 主页面 form tab排序
    $("#fmSearch").tabSort();
    
    
    //数据库同步信息提示框确定按钮
    $('#lbtnSjktbxxtskSubmit').click( function(e){
        e.preventDefault();
        $("#divSjktbxxtskWindow").window('close');
    });
    //新增数据表时的取消按钮
    $('#lbtnSjkAddCancel').click( function(e){
        e.preventDefault();
        $("#divSjbAddWindow").window('close');
    });
    //新增or编辑字段时的取消按钮
    $('#lbtnSjkZdCancel').click( function(e){
        e.preventDefault();
        $("#divSjbZdWindow").window('close');
    });
    //新增索引时的取消按钮
    $('#lbtnSjkSyCancel').click( function(e){
        e.preventDefault();
        $("#divSjbSyWindow").window('close');
    });
    //新增约束时的取消按钮
    $('#lbtnSjkYsCancel').click( function(e){
        e.preventDefault();
        $("#divSjbYsWindow").window('close');
    });
    //编辑数据表窗口关闭后重新加载数据表
    $('#divSjbAddWindow').window({
        onClose:function(){
                $('#dgSjkmx').datagrid('reload');
            }
        }
    );
    // 最大值限制
    $("#txtSjbmc").next().children().attr("maxlength","27");
    $("#txtSjbmcms").next().children().attr("maxlength","25");
    $("#txtZdmc").next().children().attr("maxlength","30");
    $("#txtZdms").next().children().attr("maxlength","400");
    $("#txtMrz").next().children().attr("maxlength","100");
    $("#txtSymc").next().children().attr("maxlength","30");
    $("#txtYsmc").next().children().attr("maxlength","30");
    //保存字段
    $("#lbtnSjkZdSubmit").click(function(e){
        e.preventDefault();
        save_zd();
    });
    //保存数据表
    $("#lbtnSjkAddSubmit").click(function(e){
        e.preventDefault();
        save_sjb();
    });
    //编辑数据表tabs切换事件
    $("#tabSjbXxgl").tabs({
        onSelect: function(title, index){
            if( index == 0){
                load_zdgl();
            }else if( index == 1){
                load_sygl();
            }else if( index ==2 ){
                load_ysgl();
            }
        }
    });
    //新增索引时的保存按钮
    $("#lbtnSjkSySubmit").click(function(e){
        e.preventDefault();
        save_sy();
    });
    //新增约束时的保存按钮
    $("#lbtnSjkYsSubmit").click(function(e){
        e.preventDefault();
        save_ys();
    });
    //同步详情查看tabs切换事件
    $("#tbsSjbTbxx").tabs({
        onSelect: function(title, index){
            if( index == 0){
                tbzd();
            }else if( index == 1){
                tbsy();
            }else if( index ==2 ){
                tbys();
            }
        }
    });
    //当是否主键为是时，其是否可空属性自动为否
    $('#nfsIskey').change(function(){
        var iskey = $("#nfsIskey").get(0).checked ? "1" : "0";
        if(iskey == '1'){
            $("#nfsSfkk").get(0).checked = ( false );
        }
    });
    $('#dgSjktblsToolbarSearch').on('click', function() {
        var ksrq = $('#txtKsrq').textbox('getValue');
        var jsrq = $('#txtJsrq').textbox('getValue');
        if (ksrq && !jsrq) {
            $.messager.alert('错误','结束日期不可为空，请选择','error', function(){
                $("#txtJsrq").next().children().select();
            });
            return false;
        }
        if (jsrq && !ksrq) {
            $.messager.alert('错误','开始日期不可为空，请选择','error', function(){
                $("#txtKsrq").next().children().select();
            });
            return false;
        }
        if( ksrq ){
            if (!checkDate10( ksrq,'开始日期','txtKsrq' )){
                return false;
            }
        }
        if( jsrq ){
            if (!checkDate10( jsrq,'结束日期','txtJsrq' )){
                return false;
            }
        }
        if (ksrq>jsrq) {
            $.messager.alert('错误', '开始日期不可大于结束日期，请重新选择', 'info')
            return false;
        }
        //重新定义url
        var tj_str = 'ksrq=' + ksrq + '&jsrq=' + jsrq+'&ywid='+$("#hidYwid").val();
        $('#dgSjktbls').datagrid( {url:'/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_sjbtbls_view?' + tj_str });
    });
    
    $('#selZdlx').next().find('input').click(function(){
        var value = $('#selZdlx').combobox('getValue');
        if (value == '-1') {
            $('#selZdlx').combobox('setValue', '')
        }
        $('#selZdlx').combobox('showPanel');
    }).blur(function(){
        var value = $('#selZdlx').combobox('getValue');
        if ($(this).val() == '') {
            $('#selZdlx').combobox('select', '-1')
        }
    });
    $('#selSylx').combobox({
        onSelect: function(param){
            if(param.value == "BITMAP"){
                // 禁用 是否唯一索引
                $("#nfsSfwysy").get(0).checked = false;
                // 添加禁用状态
                $('#state_link').addClass("cursor_not_allowed");
                $('#nfsSfwysy').prop("disabled", true);
            }else{
                // 移除禁用状态
                $('#state_link').removeClass("cursor_not_allowed");
                $('#nfsSfwysy').prop("disabled", false);
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
    // 数据表名称
    var seaMc = $("#txtSeaMc").textbox("getValue");
    // 数据表名称描述
    var seaMs = $("#txtSeaMs").textbox("getValue");
    // 根据条件查询管理对象
    $("#dgSjkmx").datagrid('load',{
        pt: pt,
        seaMc: seaMc,
        seaMs: seaMs
    });
}
/*
*数据表信息查看
*/
function sjkxxck_tab( event,sjbmcms,sjbid ){
    event.stopPropagation();
    var title = '表数据查看';
    if ( sjbmcms != '' )
        title = sjbmcms + '_表数据';
    var url = "/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/index_view?sjkmxdy_id="+sjbid + "&pt=" + pt;
    newTab(title, url);
}

// 是否可以关闭新增or编辑数据表窗口
var canClose = false;

/*
*新增or编辑数据表
*/
function sjb_operation( handler,sjbmc,sjbid,sjbmcms ){
    event = event || window.event
    event.stopPropagation();
    $('#hidSjbhandler').val( handler );
    if( handler == 'add' ){
        $('#tabSjbXxgl').hide();
        $('#divSjbAddZdWindow,#lbtnSjkAddSubmit,#lbtnSjkAddCancel').show();
        // 增加窗体
        newWindow($("#divSjbAddWindow"),'新增数据表',800,500);
        $("#divSjbAddWindow").window({
            onBeforeClose: function() {
                if (canClose) {
                    return true;
                }
                if ($('#txtSjbmc').textbox('getValue') != '' || $('#txtSjbmcms').textbox('getValue') != '' || $('#dgSjbAddZd').datagrid('getRows').length > 0) {
                    $.messager.confirm("确认", '是否需要保存？', function (r) {
                        canClose = true;
                        if (r) {
                            // 进行保存
                            save_sjb();
                        } else {
                            // 直接关闭
                            $("#divSjbAddWindow").window('close');
                        }
                        canClose = false;
                    });
                } else {
                    canClose = true;
                }
                return canClose;
            }
        });
        $("#txtSjbmc").next().children().select();
        // 字段，在新增状态下
        $('#dgSjbAddZd').datagrid({
            nowrap : false,
            fit : true,
            rownumbers : true,
            singleSelect: true,
            fitColumns : true,
            method: "get",
            remoteSort: false,
            columns: [[
                { field: 'id', title: 'ID', width: 15,hidden:true},
                { field: 'zdmc', title: '字段名称', width: 20 },
                { field: 'zdms', title: '字段描述', width: 26 },
                { field: 'zdlx', title: '字段类型', width: 12 },
                { field: 'zdcd', title: '字段长度', width: 10,align:'right', halign:'center', formatter: function(value,row,index){
                    if(value){
                        return accounting.formatNumber(value) ;
                    }else{
                        return value;
                    }
                }},
                { field: 'xscd', title: '小数长度', width: 10,align:'right', halign:'center', formatter: function(value,row,index){
                    if(value){
                        return accounting.formatNumber(value) ;
                    }else{
                        return value;
                    }
                }},
                { field: 'sfkk', title: '是否可空', width: 10 ,formatter: function(value,row,index) {
                    return value=="1" ? "是" : "否";
                }},
                { field: 'iskey', title: '是否主键', width: 10,formatter: function(value,row,index) {
                    return value=="1" ? "是" : "否";
                }},
                { field: 'mrz', title: '默认值', width: 15},
                { field: 'cz', title: '操作', width: 12, hidden: hidval, formatter: function(value,row,index) {
                    var edit = '<a href="javascript:zd_operation(\'upd\',\''+row.id+'\','+index+');">编辑</a> ';
                    var rm = '<a href="javascript:zd_operation(\'del\',\''+row.id+'\','+index+');">删除</a>'
                    var sjbhandler =  $('#hidSjbhandler').val( );
                    //新增数据表时，有编辑及删除操作，编辑数据表时字段不可删除
                    if( sjbhandler == 'add'){
                        return edit+rm;
                    }else if( sjbhandler == 'upd'){
                        return edit;
                    }
                } }
            ]]
        });
        
        // 开发系统
        if( pt == 'kf' ){
            $('#dgSjbAddZd').datagrid({
                toolbar : [{
                    iconCls : 'icon-add',
                    text : '新增字段',
                    handler : function() {
                        zd_operation( 'add','','' )
                    }
                }]
            })
        }
        
        //清除数据
        $('#divSjbAddWindow').form('clear');
        //清除数据表
        $('#dgSjbAddZd').datagrid('loadData', { total: 0, rows: [] });
        $("#txtSjbmc").textbox('enable');
        $("#txtSjbmcms").textbox('enable');
    }else if( handler == "upd"){
        $('#tabSjbXxgl').show();
        $('#divSjbAddZdWindow,#lbtnSjkAddSubmit,#lbtnSjkAddCancel').hide();
        newWindow($("#divSjbAddWindow"),'编辑数据表',800,500,100);
        //默认优先展示字段管理
        $("#tabSjbXxgl").tabs("select", 0);
        $("#hidSjbid").val( sjbid );
        $("#txtSjbmc").textbox( "setValue",sjbmc );
        $("#txtSjbmcms").textbox( "setValue",sjbmcms );
        $("#txtSjbmc").textbox('disable');
        $("#txtSjbmcms").textbox('disable');
        //加载字段管理tabs数据
        load_zdgl()
    }
    // tab排序
    $("#divSjbAddWindow").children('form').tabSort();
}
/*
*新增or编辑表字段
*/
function zd_operation( handler,zdid,index ){
    var sjbhandler =  $('#hidSjbhandler').val( );
    //若数据表为新增
    if( sjbhandler == 'add' ){
        //若字段为新增
        if( handler == 'add'){
            // 打开窗口时,是否可空默认为是
            $("#nfsSfkk").get(0).checked = true;
            // 打开窗口时,是否主键默认为否
            $("#nfsIskey").get(0).checked = false;
            newWindow($("#divSjbZdWindow"),'新增表字段',700,240);
            $("#selZdlx").combobox("select",'-1');
            $('#hidHandler').val( handler );
            $('#spZdmcAdd').show();
            $('#spZdmcEdit').hide();
            $("#txtZdmc").next().children().select();
            $("#txtZdmc").textbox('enable');
        }else if( handler== 'upd' ){
            //若字段为编辑
            var row = $('#dgSjbAddZd').datagrid('getData').rows[index];
            $("#nfsSfkk").get(0).checked = ( row.sfkk == '1' );
            $("#nfsIskey").get(0).checked = ( row.iskey == '1');
            newWindow($("#divSjbZdWindow"),'编辑表字段',700,240);
            $("#txtZdmc").textbox("setValue",row.zdmc);
            $("#txtZdms").textbox("setValue",row.zdms);
            $("#selZdlx").combobox("setValue",row.zdlx);
            $("#txtZdcd").textbox("setValue",row.zdcd);
            $("#txtXscd").textbox("setValue",row.xscd);
            $("#txtMrz").textbox("setValue",row.mrz);
            $('#hidIskey').val(row.iskey);
            $('#hidZdlx').val(row.zdlx);
            $('#hidHandler').val( handler );
            $('#hidIndex').val( index );
            $("#txtZdmc").textbox('enable');
        }else if( handler == 'del' ){
            //删除指定行
            $('#dgSjbAddZd').datagrid('deleteRow',index)
            //为防止表格序号错误，重新加载表格
            $('#dgSjbAddZd').datagrid( 'loadData', $('#dgSjbAddZd').datagrid('getData') );
        }
    }else if( sjbhandler == 'upd' ){
        //若字段为新增
        if( handler == 'add'){
            // 打开窗口时,是否可空默认为是
            $("#nfsSfkk").get(0).checked = true;
            // 打开窗口时,是否主键默认为否
            $("#nfsIskey").get(0).checked = false;
            newWindow($("#divSjbZdWindow"),'新增表字段',700,240);
            $("#selZdlx").combobox("select",'-1');
            $("#txtZdmc").next().children().select();
            $('#hidHandler').val( handler );
            $('#hidIndex').val( index );
            $("#txtZdmc").textbox('enable');
        }else if(handler == 'upd'){
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_bef_zd_edit_view",
                data: {"id":zdid},
                success: function(data){
                    $("#nfsSfkk").get(0).checked = ( data.sfkk == '1' );
                    $("#nfsIskey").get(0).checked = ( data.iskey == '1');
                    newWindow($("#divSjbZdWindow"),'编辑表字段',700,240);
                    $("#txtZdmc").textbox("setValue",data.zdmc);
                    $("#txtZdms").textbox("setValue",data.zdms);
                    $("#selZdlx").combobox("setValue",data.zdlx);
                    $("#txtZdcd").textbox("setValue",data.zdcd);
                    $("#txtXscd").textbox("setValue",data.xscd);
                    $("#txtMrz").textbox("setValue",data.mrz);
                    $('#hidHandler').val( handler );
                    $('#hidZdid').val( data.id );
                    $('#hidIndex').val( index );
                    $("#txtZdmc").textbox('disable');
                    $('#hidIskey').val(data.iskey);
                    $('#hidZdlx').val(data.zdlx);
                    $("#divSjbZdWindow").children('form').tabSort();
                },
                error : function(){
                    errorAjax();
                }
            });
        }
    }
    $("#divSjbZdWindow").children('form').tabSort();
}


/*
*字段保存
*/
function save_zd(){
    // 出错提示
    var msg = "新增失败，请稍后再试";
    //字段操作
    hidHandler = $('#hidHandler').val();
    //数据表操作
    hidSjbhandler = $('#hidSjbhandler').val();
    //若数据表为新增
    if( hidSjbhandler == 'add' ){
        var zdmc = $("#txtZdmc").textbox("getValue").toUpperCase();
        var zdms = $("#txtZdms").textbox("getValue");
        var zdlx = $("#selZdlx").combobox("getValue");
        var zdcd = $("#txtZdcd").textbox("getValue");
        var xscd = $("#txtXscd").textbox("getValue");
        var sfkk = $("#nfsSfkk").get(0).checked ? "1" : "0";
        var iskey = $("#nfsIskey").get(0).checked ? "1" : "0";
        var mrz = $("#txtMrz").textbox("getValue");
        // 若字段为新增
        if( hidHandler == 'add' ){
            if( zdxxjy() ){
                $('#dgSjbAddZd').datagrid('appendRow',{
                    zdmc:zdmc,
                    zdms:zdms,
                    zdlx:zdlx,
                    zdcd:zdcd,
                    xscd:xscd,
                    sfkk:sfkk,
                    iskey:iskey,
                    mrz:mrz
                });
                $("#divSjbZdWindow").window('close');
            }
        }else if( hidHandler = 'upd'){
            if( zdxxjy() ){
                $('#dgSjbAddZd').datagrid('updateRow',{
                    index:$('#hidIndex').val(),
                    row:{
                        zdmc:zdmc,
                        zdms:zdms,
                        zdlx:zdlx,
                        zdcd:zdcd,
                        xscd:xscd,
                        sfkk:sfkk,
                        iskey:iskey,
                        mrz:mrz
                    }
                });
                $("#divSjbZdWindow").window('close');
            }
        }
        //为防止表格序号错误，重新加载表格
        $('#dgSjbAddZd').datagrid( 'loadData', $('#dgSjbAddZd').datagrid('getData') );

    }else if( hidSjbhandler == 'upd'){
        //是否可空
        var sfkk = $("#nfsSfkk").get(0).checked ? "1" : "0";
        //是否主键
        var iskey = $("#nfsIskey").get(0).checked ? "1" : "0";
        //数据表ID
        var sjbid = $('#hidSjbid').val();
        //数据表名称
        var sjbmc = $('#txtSjbmc').textbox("getValue");
        // 若字段为新增
        if( hidHandler == 'add' ){
            // 添加遮罩
            ajaxLoading();
            $('#divSjbZdWindow').find('form').form('submit', {
                url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_zd_add_view",
                queryParams: {'sfkk': sfkk,'iskey':iskey,'sjbid':sjbid,'sjbmc':sjbmc},
                onSubmit:function (){
                    var ret = zdxxjy();
                    // 反馈校验结果
                    if( ret == false ){
                        // 取消遮罩
                        ajaxLoadEnd();
                    }
                    return ret;
                } ,
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, "dgSjkzdgl", "divSjbZdWindow");
                },
                error: function () {
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }else if ( hidHandler == 'upd' ){
            // 添加遮罩
            ajaxLoading();
            var zdid = $('#hidZdid').val();
            var zdmc = $("#txtZdmc").textbox("getValue");
            $('#divSjbZdWindow').find('form').form('submit', {
                url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_zd_edit_view",
                queryParams: {'sfkk': sfkk,'iskey':iskey,'sjbid':sjbid,'sjbmc':sjbmc,'zdid':zdid,'zdmc':zdmc},
                onSubmit:function (){
                    var ret = zdxxjy();
                    // 反馈校验结果
                    if( ret == false ){
                        // 取消遮罩
                        ajaxLoadEnd();
                    }
                    return ret;
                } ,
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, "dgSjkzdgl", "divSjbZdWindow");
                },
                error: function () {
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    }
}
/*
*新增or编辑字段信息校验
*/
function zdxxjy(){
    //数据表操作
    var hidSjbhandler = $('#hidSjbhandler').val(  );
    //字段操作
    var  hidHandler = $('#hidHandler').val(  );
    var zdmc = $("#txtZdmc").textbox("getValue").toUpperCase();
    var zdms = $("#txtZdms").textbox("getValue");
    var zdlx = $("#selZdlx").combobox("getValue");
    var zdcd = $("#txtZdcd").textbox("getValue");
    var xscd = $("#txtXscd").textbox("getValue");
    var sfkk = $("#nfsSfkk").get(0).checked ? "1" : "0";
    var iskey = $("#nfsIskey").get(0).checked ? "1" : "0";
    var mrz = $("#txtMrz").textbox("getValue");
    var yiskey = $("#hidIskey").val();
    var yzdlx = $("#hidYzdlx").val();
    if( hidSjbhandler == 'add'){
        var data = $('#dgSjbAddZd').datagrid('getData');
    }else if( hidSjbhandler == 'upd' ){
        var data = $('#dgSjkzdgl').datagrid('getData');
    }
    var index = $('#hidIndex').val();
    if (zdmc=="") {
        $.messager.alert('错误','字段名称不可为空，请输入','error', function(){
            $("#txtZdmc").next().children().select();
        });
        return false;
    }
    if(!checkBm(zdmc,'字段名称','txtZdmc')){
        return false;
    }
    for(var i =0;i<ORACLE_KEYWORDS_LST.length;i++){
        var keyword = ORACLE_KEYWORDS_LST[i];
        if( zdmc == keyword ){
            $.messager.alert('错误','字段名称不可为ORACLE关键字,请重新输入','error', function(){
                $("#txtZdmc").next().children().select();
            });
            return false;
        }
    }
    var zjzd_sum = 0;
    for( var i = 0;i<data.rows.length;i++){
        row = data.rows[i];
        if(row.iskey=='1'){
            zjzd_sum+=1;
        }
        //若本次新增或修改的字段名称与表格中已存在的字段重复,进行提示
        if( row.zdmc == zdmc ){
            //在新增时,index是没有值的,为空，此时与i可不比较，因为i是数值型的，所以需要先判断index有没有值，若有值，在判断与表格中的索引是否一致
            if( index ){
                if( index != i ){
                    $.messager.alert('错误','字段名称['+zdmc+']已经存在,请重新输入','error', function(){
                        $("#txtZdmc").next().children().select();
                    });
                    return false;
                }
            }else{
                    $.messager.alert('错误','字段名称['+zdmc+']已经存在,请重新输入','error', function(){
                    $("#txtZdmc").next().children().select();
                });
                return false;
            }
        }
    }
    if (zdlx=="-1" || zdlx==undefined) {
        $.messager.alert('错误','字段类型不可为空，请选择','error', function(){
            $("#selZdlx").next().children().select();
        });
        return false;
    }
    if( hidHandler == 'add' && iskey == '1'){
        zjzd_sum=zjzd_sum+1;
    }else if(hidHandler == 'upd'&&yiskey=='1'&&iskey=='0' ){
        zjzd_sum = zjzd_sum-1;
    }else if(hidHandler == 'upd'&&yiskey=='0'&&iskey=='1' ){
        zjzd_sum = zjzd_sum +1;
    }
    if(zjzd_sum>10){
        $.messager.alert('错误','系统限制：主键字段最多10个，现在已经'+zjzd_sum+'个，请重新设置','error', function(){
            $("#nfsIskey").next().children().select();
        });
        return false;   
    }
    if (zdms=="") {
        $.messager.alert('错误','字段描述不可为空，请输入','error', function(){
            $("#txtZdms").next().children().select();
        });
        return false;
    }
    if ( zdcd!='' && !/^[0-9]*$/.test(zdcd)) {
        $.messager.alert('错误','字段长度只允许为整数,请重新输入','error', function(){
            $("#txtZdcd").next().children().select();
        });
        return false;
    }
    if( (zdlx == 'CHAR'||zdlx =='VARCHAR2'||zdlx =='NCHAR'||zdlx =='NVARCHAR2'||zdlx =='RAW'||zdlx =='DECIMAL'||zdlx =='FLOAT')&&zdcd == '' ){
        $.messager.alert('错误','字段长度不可为空,请输入','error', function(){
            $("#txtZdcd").next().children().select();
        });
        return false;
    }
    if(xscd!=''&&(zdlx != 'DECIMAL'&&zdlx != 'NUMBER')){
        $.messager.alert('错误','所选类型不允许输入小数,请重新输入','error', function(){
            $("#txtXscd").next().children().select();
        });
        return false;
    }
    if ( xscd!='' && !/^[0-9]*$/.test(xscd)) {
        $.messager.alert('错误','小数长度只允许为整数,请重新输入','error', function(){
            $("#txtXscd").next().children().select();
        });
        return false;
    }
    if( iskey == '1' && ( zdlx=='BLOB'||zdlx=='CLOB'||zdlx=='LONG RAW'||zdlx=='BFILE'||zdlx=='NCLOB'||zdlx=='LONG')){
        $.messager.alert('错误','字段类型['+zdlx+']不可为主键,请重新选择','error', function(){
            $("#nfsIskey").next().children().select();
        });
        return false;
    }
    if( iskey=='1' && sfkk == '1'){
        $.messager.alert('错误','主键字段为不可空,请选择','error', function(){
            $("#nfsSfkk").next().children().select();
        });
        return false;
    }
    return true;
}

/*
*新增or编辑数据表
*/
function save_sjb(){
    // 添加遮罩
    ajaxLoading();
    //数据表操作
    hidSjbhandler = $('#hidSjbhandler').val(  );
    var ywid = $('#hidYwid').val();
    var sjbid = $('#hidSjbid').val();
    var data = JSON.stringify( $('#dgSjbAddZd').datagrid('getData').rows );
    // 提交表单
    $('#divSjbAddWindow').find('form').form('submit', {
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/sjb_add_view",
        queryParams: {'ywid': ywid,'sjbid':sjbid,'data':data},
        onSubmit: function(){
            var sjbmc = $("#txtSjbmc").textbox("getValue").toUpperCase();
            var sjbmcms = $("#txtSjbmcms").textbox("getValue");
            var data = $('#dgSjbAddZd').datagrid('getData');
            if (sjbmc=="") {
                $.messager.alert('错误','数据表名称不可为空，请输入','error', function(){
                    $("#txtSjbmc").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            if(!checkBm(sjbmc,'数据表名称','txtSjbmc')){
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            for(var i =0;i<ORACLE_KEYWORDS_LST.length;i++){
                var keyword = ORACLE_KEYWORDS_LST[i];
                if( sjbmc == keyword ){
                    $.messager.alert('错误','数据表名称不可为ORACLE关键字,请重新输入','error', function(){
                        $("#txtSjbmc").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
            }
            if (sjbmcms=="") {
                $.messager.alert('错误','数据表名称描述不可为空，请输入','error', function(){
                    $("#txtSjbmcms").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            if(!checkMc(sjbmcms,'数据表名称描述','txtSjbmcms')){
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            if( $('#dgSjbAddZd').datagrid('getData').rows.length == 0 ){
                    $.messager.alert('错误','数据表必须有字段信息,请输入','error', function(){
                    $("#txtSjbmcms").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            //检验是否有主键字段
            var sfzj = ''
            for( var i = 0;i<data.rows.length;i++){
                row = data.rows[i];
                if( row.iskey == '1' ){
                    sfzj += row.iskey
                }
            }
            if(!sfzj){
                $.messager.alert('错误','数据表必须有主键字段,请输入','error','');
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            return true;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            canClose = true;
            afterAjax(data, "dgSjkmx", "divSjbAddWindow");
            canClose = false;
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}
/*
*数据表编辑时,加载字段管理数据
*/
function load_zdgl(){
    $('#dgSjkzdgl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : false,
        fitColumns : true,
        singleSelect:true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_zdgl_view?sjbid="+$("#hidSjbid").val(),
        remoteSort: false,
        columns: [[
            { field: 'id', title: 'ID', width: 15,hidden:true},
            { field: 'zdmc', title: '字段名称', width: 25 },
            { field: 'zdms', title: '字段描述', width: 30 },
            { field: 'zdlx', title: '字段类型', width: 12 },
            { field: 'zdcd', title: '字段长度', width: 12,align:'right', halign:'center', formatter: function(value,row,index){
                if(value){
                    return accounting.formatNumber(value) ;
                }else{
                    return value;
                }
                } },
            { field: 'xscd', title: '小数长度', width: 12,align:'right', halign:'center', formatter: function(value,row,index){
                if(value){
                    return accounting.formatNumber(value) ;
                }else{
                    return value;
                }
                } },
            { field: 'sfkk', title: '是否可空', width: 12 ,formatter: function(value,row,index) {
                return value=="1" ? "是" : "否";
            }},
            { field: 'iskey', title: '是否主键', width: 12,formatter: function(value,row,index) {
                return value=="1" ? "是" : "否";
            }},
            { field: 'mrz', title: '默认值', width: 15},
            { field: 'cz', title: '操作', width: 10, hidden: hidval, formatter: function(value,row,index) {
                var edit = '<a href="javascript:zd_operation(\'upd\', \''+row.id+'\','+index+');">编辑</a> ';
                var rm = '<a href="javascript:zd_operation(\'del\',\''+row.id+'\','+index+');">删除</a>'
                var sjbhandler =  $('#hidSjbhandler').val( );
                //新增数据表时，有编辑及删除操作，编辑数据表时字段不可删除
                if( sjbhandler == 'add'){
                    return edit+rm;
                }else if( sjbhandler == 'upd'){
                    return edit;
                }
            } }
        ]]
    });
    // 开发系统
    if( pt == 'kf' ){
        $('#dgSjkzdgl').datagrid({
            toolbar : [{
                iconCls : 'icon-add',
                text : '新增字段',
                handler : function() {
                    zd_operation( 'add','','' )
                }
            }]
        })
    }
}
/*
*数据表编辑时,加载索引管理数据
*/
function load_sygl(){
    // 索引列表，在编辑状态下
    $('#dgSjksygl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : false,
        fitColumns : true,
        singleSelect:true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_sygl_view?sjbid="+$("#hidSjbid").val(),
        remoteSort: false,
        columns: [[
            { field: 'id', title: 'ID', width: 15,hidden:true },
            { field: 'symc', title: '索引名称', width: 25 },
            { field: 'syzd', title: '索引字段', width: 25 },
            { field: 'sylx', title: '索引类型', width: 10 ,formatter: function(value,row,index) {
                return SYLX_DIC[value];
            } } ,
            { field: 'sfwysy', title: '是否唯一索引', width: 10,formatter: function(value,row,index) {
                return value=="UNIQUE" ? "是" : "否";
            } } ,
            { field: 'cz', title: '操作', width: 5, hidden: hidval, formatter: function(value,row,index) {
                return '<a href="javascript:remove_sy(\''+row.id+'\');">删除</a> ';
            } }
        ]]
    });
    
    // 开发系统
    if( pt == 'kf' ){
        $('#dgSjksygl').datagrid({
            toolbar : [ {
                iconCls : 'icon-add',
                text : '新增索引',
                handler : function() {
                    add_sy();
                }
            }]
        })
    }
    
}
/*
*数据表编辑时,加载字段管理数据
*/
function load_ysgl(){
    $('#dgSjkysgl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : false,
        fitColumns : true,
        singleSelect:true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_ysgl_view?sjbid="+$("#hidSjbid").val(),
        remoteSort: false,
        columns: [[
            { field: 'id', title: 'ID', width: 15,hidden:true },
            { field: 'ysmc', title: '约束名称', width: 15 },
            { field: 'yszd', title: '约束字段', width: 24 },
            { field: 'cz', title: '操作', width: 4, hidden: hidval, formatter: function(value,row,index) {
                return '<a href="javascript:remove_ys(\''+row.id+'\');">删除</a> ';
            } }
        ]]
    });
    
    // 开发系统
    if( pt == 'kf' ){
        $('#dgSjkysgl').datagrid({
            toolbar : [ {
                iconCls : 'icon-add',
                text : '新增唯一约束',
                handler : function() {
                    add_ys();
                }
            }]
        })
    }
}
/*
*增加索引
*/
function add_sy(){
    // 打开窗口时,是否唯一索引为否
    $("#nfsSfwysy").get(0).checked = false;
    //打开新窗口
    newWindow($("#divSjbSyWindow"),'新增索引',400,240);
    //打开窗口时,索引类型为正常索引
    $("#selSylx").combobox('select', 'NORMAL');
    $("#txtSymc").next().children().select();
    //加载索引字段下拉框
    load_zd( 'sy' );
}
/*
*加载索引字段或约束字段的下拉框
*/
function load_zd( handler ){
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_load_zd_view",
        data: {"sjbid":$("#hidSjbid").val() },
        success: function(data){
            if( handler == 'sy'){
                $('#txtSyzd').combobox({
                    editable:false,
                    data:data.zdmc_lst,
                    valueField:'zdmc',
                    textField:'zdmc'
                });
                $('#addSyForm').tabSort();
            }else if(handler == 'ys'){
                $('#txtYszd').combobox({
                    editable:false,
                    data:data.zdmc_lst,
                    valueField:'zdmc',
                    textField:'zdmc'
                });
                $('#addYsForm').tabSort();
            }
        },
        error : function(){
            errorAjax();
        }
    });
}
/*
*索引保存,form提交
*/
function save_sy(){
    // 添加遮罩
    ajaxLoading();
    //是否唯一索引
    var sfwysy = $("#nfsSfwysy").get(0).checked ? "UNIQUE" : "NONUNIQUE";
    //数据表ID
    var sjbid = $('#hidSjbid').val();
    //数据表名称
    var sjbmc = $("#txtSjbmc").textbox("getValue");
    //索引字段
    var syzd = $("#txtSyzd").combobox('getText');
    //索引类型
    var sylx = $("#selSylx").combobox("getValue");
    $('#divSjbSyWindow').find('form').form('submit', {
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_sy_add_view",
        queryParams: {'sfwysy': sfwysy,'sjbid':sjbid,'sjbmc':sjbmc,'syzd':syzd},
        onSubmit:function (){
            var symc = $("#txtSymc").textbox("getValue").toUpperCase();
            var sylx = $("#selSylx").combobox("getValue");
            var syzd = $("#txtSyzd").combobox('getText');
            if (symc=="") {
                $.messager.alert('错误','索引名称不可为空，请输入','error', function(){
                    $("#txtSymc").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            if(!checkBm(symc,'索引名称','txtSymc')){
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            for(var i =0;i<ORACLE_KEYWORDS_LST.length;i++){
                var keyword = ORACLE_KEYWORDS_LST[i];
                if( symc == keyword ){
                    $.messager.alert('错误','索引名称不可为ORACLE关键字,请重新输入','error', function(){
                        $("#txtSymc").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
            }
            if (syzd=="") {
                $.messager.alert('错误','索引字段不可为空，请选择','error', function(){
                    $("#txtSyzd").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            syzdArray = syzd.split("|");
            if (syzd!=""&&syzdArray.length>10) {
                $.messager.alert('错误','系统限制：索引包含字段限制为10个，现在本索引包含字段已经'+syzdArray.length+'个，请重新设置','error', function(){
                    $("#txtSyzd").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }

            if (sylx=="") {
                $.messager.alert('错误','索引类型不可为空，请选择','error', function(){
                    $("#selSylx").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            return true;
        } ,
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgSjksygl", "divSjbSyWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}
/*
*删除索引
*/
function remove_sy( syid ){
    //数据表ID
    var sjbid = $('#hidSjbid').val();
    //数据表名称
    var sjbmc = $("#txtSjbmc").textbox("getValue");
    $.messager.confirm('确认', '索引删除后数据将不可恢复，您确定要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_sy_del_view",
                data: {"syid": syid,'sjbid':sjbid,'sjbmc':sjbmc},
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, "dgSjksygl", "divSjbSyWindow");
                },
                error: function() {
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    });
}
/*
*增加约束
*/
function add_ys(){
    //打开新窗口
    newWindow($("#divSjbYsWindow"),'新增约束',400,180);
    $("#txtYsmc").next().children().select();
    //加载索引字段下拉框
    load_zd( 'ys' );
    $('#addYsForm').tabSort();
}
/*
*约束保存,form提交
*/
function save_ys(){
    // 添加遮罩
    ajaxLoading();
    //数据表ID
    var sjbid = $('#hidSjbid').val();
    //数据表名称
    var sjbmc = $("#txtSjbmc").textbox("getValue");
    //约束字段
    var yszd = $("#txtYszd").combobox('getText');
    $('#divSjbYsWindow').find('form').form('submit', {
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_ys_add_view",
        queryParams: {'sjbid':sjbid,'sjbmc':sjbmc,'yszd':yszd},
        onSubmit:function (){
            var ysmc = $("#txtYsmc").textbox("getValue").toUpperCase();
            var yszd = $("#txtYszd").combobox('getText');
            if (ysmc=="") {
                $.messager.alert('错误','约束名称不可为空，请输入','error', function(){
                    $("#txtYsmc").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            if(!checkBm(ysmc,'约束名称','txtYsmc')){
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            for(var i =0;i<ORACLE_KEYWORDS_LST.length;i++){
                var keyword = ORACLE_KEYWORDS_LST[i];
                if( ysmc == keyword ){
                    $.messager.alert('错误','约束名称不可为ORACLE关键字,请重新输入','error', function(){
                        $("#txtYsmc").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
            }
            if (yszd=="") {
                $.messager.alert('错误','约束字段不可为空，请选择','error', function(){
                    $("#txtYszd").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            yszdArray = yszd.split("|");
            if (yszd!=""&&yszdArray.length>10) {
                $.messager.alert('错误','系统限制：约束包含字段限制为10个，现在本约束包含字段已经'+yszdArray.length+'个，请重新设置','error', function(){
                    $("#txtYszd").next().children().select();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            return true;
        } ,
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgSjkysgl", "divSjbYsWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}
/*
*删除约束
*/
function remove_ys( ysid ){
    //数据表ID
    var sjbid = $('#hidSjbid').val();
    //数据表名称
    var sjbmc = $("#txtSjbmc").textbox("getValue");
    $.messager.confirm('确认', '约束删除后数据将不可恢复，您确定要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_ys_del_view",
                data: {"ysid": ysid,'sjbid':sjbid,'sjbmc':sjbmc},
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, "dgSjkysgl", "divSjbYsWindow");
                },
                error: function() {
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    });
}
/*
*同步信息查看
*/
function tbxxck_tool(){
    newWindow($("#divSjbtbxxckWindow"),'同步信息查看',800,400);
    // 渲染表格
    $('#dgSjktbls').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        singleSelect:true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_sjbtbls_view?ywid="+$("#hidYwid").val(),
        remoteSort: false,
        columns: [[
            { field: 'id', title: 'ID', width: 15,hidden:true },
            { field: 'sjbid', title: '数据表ID', width: 25,hidden:true },
            { field: 'sjbmc', title: '数据表名称', width: 25 },
            { field: 'tblx', title: '同步类型', width: 15, formatter: function(value,row,index) {
                return value == '1'?'删除':'修改'
            } },
            { field: 'tbr', title: '同步人', width: 10},
            { field: 'tbrq', title: '同步日期', width: 15,align:'center' },
            { field: 'tbsj', title: '同步时间', width: 17,align:'center' },
            { field: 'Operation', title: '操作', width: 15, formatter: function(value,row,index) {
                return '<a href="javascript:sjktb_xxxxck(\''+row.sjbid+'\',\''+row.id+'\',\''+row.sjbmc+'\');">详细信息</a> ';
            } }
        ]],
        toolbar: "#dgSjktblsToolbar",
    });
}

/*
*同步详细信息查看
*/
function sjktb_xxxxck( sjbid,tblsid,sjbmc ){
    //获取数据表的同步信息
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_tbxx_sjb_view",
        data: {"tblsid":tblsid,'sjbid':sjbid },
        success: function(data){
            newWindow($("#divSjbtbxxxxckWindow"),'同步详情查看',1100,460);
            $('#txtTbsjbmc').textbox( 'setValue',sjbmc)
            $('#txtTbqsjbmcms').textbox( 'setValue',data.tbqsjbmcms);
            $('#txtTbhsjbmcms').textbox( 'setValue',data.tbhsjbmcms);
            $('#hidTblsid').val( tblsid );
            //优先展示同步字段
            $("#tbsSjbTbxx").tabs("select", 0);
            //加载同步字段
            tbzd();
        },
        error : function(){
            errorAjax();
        }
    });
}
/*
*同步字段展示
*/
function tbzd(){
    // 渲染表格
    $('#dgTbzd').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : false,
        fitColumns : false,
        singleSelect:true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_tbxx_zd_view?tblsid="+$('#hidTblsid').val(),
        remoteSort: false,
        columns:[[
            {field:'zdmc',title:'字段名称',rowspan:2,width:100},
            {field:'tblx',title:'同步类型',rowspan:2,width:55, formatter: function(value,row,index){
                return value == '1'?'新增':( value == '2'?'删除':'修改') ;
            }},
            {title:'字段描述',colspan:2},
            {title:'字段类型',colspan:2},
            {title:'字段长度',colspan:2},
            {title:'小数长度',colspan:2},
            {title:'是否可空',colspan:2},
            {title:'是否主键',colspan:2},
            {title:'默认值',colspan:2}
        ],[
            {field:'zdms_q',title:'同步前',width:110},
            {field:'zdms_h',title:'同步后',width:110},
            {field:'zdlx_q',title:'同步前',width:80},
            {field:'zdlx_h',title:'同步后',width:80},
            { field: 'zdcd_q', title: '同步前', width: 40,align:'right', halign:'center', formatter: function(value,row,index){
                if(value){
                    return accounting.formatNumber(value) ;
                }else{
                    return value;
                }
            } },
            { field: 'zdcd_h', title: '同步后', width: 40,align:'right', halign:'center', formatter: function(value,row,index){
                if(value){
                    return accounting.formatNumber(value) ;
                }else{
                    return value;
                }
            } },
            { field: 'xscd_q', title: '同步前', width: 40,align:'right', halign:'center', formatter: function(value,row,index){
                if(value){
                    return accounting.formatNumber(value) ;
                }else{
                    return value;
                }
                } },
            { field: 'xscd_h', title: '同步后', width: 40,align:'right', halign:'center', formatter: function(value,row,index){
                if(value){
                    return accounting.formatNumber(value) ;
                }else{
                    return value;
                }
                } },
            { field: 'sfkk_q', title: '同步前', width: 40 ,formatter: function(value,row,index) {
                if(value){
                    return value=="1" ? "是" : "否";
                }else{
                    return value;
                }
            }},
            { field: 'sfkk_h', title: '同步后', width: 40 ,formatter: function(value,row,index) {
                if(value){
                    return value=="1" ? "是" : "否";
                }else{
                    return value;
                }
            }},
            { field: 'iskey_q', title: '同步前', width: 40,formatter: function(value,row,index) {
                if(value){
                    return value=="1" ? "是" : "否";
                }else{
                    return value;
                }
            }},
            { field: 'iskey_h', title: '同步后', width: 40,formatter: function(value,row,index) {
                if(value){
                    return value=="1" ? "是" : "否";
                }else{
                    return value;
                }
            }},
            {field:'mrz_q',title:'同步前',width:80},
            {field:'mrz_h',title:'同步后',width:80},
        ]]
    });
}
/*
*同步索引
*/
function tbsy(){
    $('#dgTbsy').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        singleSelect:true,
        pagination : false,
        fitColumns : false,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_tbxx_sy_view?tblsid="+$('#hidTblsid').val(),
        remoteSort: false,
        columns:[[
            {field:'symc',title:'索引名称',rowspan:2,width:400},
            {field:'tblx',title:'同步类型',rowspan:2,width:75, formatter: function(value,row,index){
                return value == '1'?'新增':( value == '2'?'删除':'修改') ;
            }},
            {title:'索引字段',colspan:2},
            {title:'索引类型',colspan:2},
            {title:'是否唯一索引',colspan:2}
        ],[
            {field:'syzd_q',title:'同步前',width:90},
            {field:'syzd_h',title:'同步后',width:90},
            {field:'sylx_q',title:'同步前',width:90,formatter: function(value,row,index) {
                return SYLX_DIC[value];
            }},
            {field:'sylx_h',title:'同步后',width:90,formatter: function(value,row,index) {
                return SYLX_DIC[value];
            }},
            {field:'sfwysy_q',title:'同步前',width:90,formatter: function(value,row,index) {
                if( value ){
                    return value == "UNIQUE" ? "是" : "否";
                }else{
                    return value;
                }
            }},
            {field:'sfwysy_h',title:'同步后',width:90,formatter: function(value,row,index) {
                if( value ){
                    return value == "UNIQUE" ? "是" : "否";
                }else{
                    return value;
                }
            }}
        ]]
    });
}
/*
*同步约束
*/

function tbys(){
    $('#dgTbys').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : false,
        fitColumns : false,
        singleSelect:true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/data_tbxx_ys_view?tblsid="+$('#hidTblsid').val(),
        remoteSort: false,
        columns:[[
            {field:'ysmc',title:'约束名称',rowspan:2,width:400},
            {field:'tblx',title:'同步类型',rowspan:2,width:195, formatter: function(value,row,index){
                return value == '1'?'新增':( value == '2'?'删除':'修改') ;
            }},
            {title:'约束字段',colspan:2}
        ],[
            {field:'yszd_q',title:'同步前',width:210},
            {field:'yszd_h',title:'同步后',width:210}
        ]]
    });
}

/*
版本信息查看
*/
function bbxxck(event,lc,sjkid) {
    event.stopPropagation();
    newTab(lc + '_版本信息查看', '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxxck_index_view?lx=sjk&id=' + sjkid);
}
