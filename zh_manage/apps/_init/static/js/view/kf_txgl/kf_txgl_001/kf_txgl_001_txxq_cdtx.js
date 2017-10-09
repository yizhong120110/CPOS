$(document).ready(function() {
    
    // 渲染表格
    var txid = $('#hidTxid').val();
    var url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_data_view?txid=" + txid;
    datagrid = $('#dgCdtx').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        singleSelect : false,
        url: url,
        remoteSort: false,
        frozenColumns: [[
            { field: 'ck', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: 'ID', hidden: true },
            { field: 'bm', title: '编码', width: '7%'},
            { field: 'ywmc', title: '所属业务', width: '13%'},
            { field: 'dfjymc', title: '对方交易名称', width: '13%'},
            { field: 'dfjym', title: '对方交易码', width: '8%'},
            { field: 'cssj', title: '超时时间', width: '5%', align: 'right'},
            { field: 'dbjdmc', title: '打包', width: '11%'},
            { field: 'jbjdmc', title: '解包', width: '11%'},
            { field: 'dbssid', title: '挡板所属id', hidden: true },
            { field: 'zlcdyid', title: '子流程定义id', hidden: true },
            { field: 'dbmc', title: '应用挡板', width: '12%', formatter: function(value,rowData,rowIndex) {
                    if( value != '无' ){
                        return '<a href="javascript:void(0);" onclick="cdtxgl_dbxx(' + rowIndex + ');">'+ value +'</a><a href="javascript:void(0);" onclick="del_db(\'dgCdtx\',\'' + rowData.id +'\')" class="l-btn l-btn-small l-btn-plain" group="" id="" title = "删除挡板"><span class="l-btn-left l-btn-icon-left"><span class="l-btn-text"></span><span class="l-btn-icon icon-delete">&nbsp;</span></span></a>';
                    
                    }else{
                        return '<a href="javascript:void(0);" onclick="cdtxgl_dbxx(' + rowIndex + ');">'+ value +'</a>';
                    }
                }
            },
            { field: 'jkqyzt', title: '接口校验', width: '5%', formatter: function(value,rowData,rowIndex) {
                    //0禁用 1启用
                    if( value == '1' ){
                        return '<a href="javascript:void(0);" onclick="cdtxgl_jkjy(' + rowIndex + ');">启用</a>';
                    
                    }else{
                        return '<a href="javascript:void(0);" onclick="cdtxgl_jkjy(' + rowIndex + ');">禁用</a>';
                    }
                }
            },
            { field: 'csalsl', title: '测试案例', width: '5%', align: 'right', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="cdtxgl_csal('+rowIndex+');">&nbsp;'+ value +'&nbsp;</a>';
                }
            },
            { field: 'cz', title: '操作', width: '6%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="showHide(\'update\',\'dgCdtx\',\''+rowData.id+'\',\'divCdtxWindow\',\'编辑C端通讯\');">编辑</a> ' +
                '<a href="javascript:void(0);" onclick="removeCdtx(\'dgCdtx\',\''+rowIndex+'\');">删除</a>';
            } }
        ]],
        toolbar : [
            {
                iconCls : 'icon-add',
                text : '新增',
                handler : function() {
                    // 增加
                    showHide( 'add','dgTxcs','', 'divCdtxWindow', '新增C端通讯' )
                }
            },{
                iconCls : 'icon-up',
                text : '导出C端通讯代码',
                handler : function() {
                    //导出C端通讯代码
                    var to_path = 'window.location.href="/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_view?txid=' + txid + '"'
                    dm_down( 'dgCdtx', 'cdtx', '', to_path, txid );
                }
            }
        ]
    });
    
    // 最大值限制
    $("#txtBm").next().children().attr("maxlength","50");
    $("#txtDfjym").next().children().attr("maxlength","50");
    $("#txtDfjymc").next().children().attr("maxlength","25");
    $("#txtCssj").next().children().attr("maxlength","4");
    
    // 给查询按钮定义onclick事件
    $("#lbtnSearch").click(function(e){
        // 取消默认提交事件
        e.preventDefault();
        // 查询
        doSearch();
    });

    // 查询条件Tab顺
    $("#formSearch").tabSort(); 
    
    //初始化C端通讯按钮(保存)
    $("#lbtnCdtxSubmit").click(function(e){
        e.preventDefault();
        // 保存提交
        saveSub( 'dgCdtx', 'divCdtxWindow' );
    })
    
    //初始化C端通讯按钮（取消）
    $("#lbtnCdtxCancel").click(function(e){
        e.preventDefault();
        $("#divCdtxWindow").window('close');
    })
    
    // 所属业务与冲正配置联动
    $('#selSsywid').combobox({
        onSelect: function(record) {
            var ssywid = record.value;
            // 子流程id
            zlcdyid = $("#hidZlcdyid").val();
            $("#selCzpzid").combobox('select', '');
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_czpz_view",
                data: {'ssywid': ssywid,'zlcdyid': zlcdyid},
                success: function(data){
                    // 反馈信息初始化文件列表
                    data = $.parseJSON(data);
                    // 获取数据成功
                    if( data.state == true ){
                        data.czpz_lst.unshift({
                            'value': '',
                            'text': '请选择'
                        });
                        $('#selCzpzid').combobox('loadData', data.czpz_lst);
                        $('#txform').tabSort();
                    }else{
                        afterAjax(data, "", "");
                    }
                },
                error : function(){
                    errorAjax();
                }
            });
        }
    });

});

/**
* 新增or编辑C端通讯弹窗
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
    var txid = $("#txid").val();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_add2edit_sel_view",
        data: { 'cdtxid': updid,'txid': txid },
        success: function(data){
            // 打开窗口
            newWindow($( "#" + winid ),wintit,720,300);
            // 反馈信息
            data = $.parseJSON( data );
            if( data.state == true ){
                // 初始化页面元素
                pageInit( handle, data )
                // 重新初始化tabindex
                $('#cdtxform').tabSort();
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
*C端通讯初始化新增or编辑页面
*/
function pageInit( handle, data ){
    
    // 初始化打包配置、解包配置
    initDbJb();
    
    // 冲正配置
    $('#selCzpzid').combobox({
        editable:true,
        data:[{value: '', text: '请选择'}],
        valueField:'value',
        textField:'text'
    });
    
    // 根据类型不同做不同处理
    if(handle=='add'){
        // 新增可用
        $('#txtBm').textbox('enable');
        $('#selSsywid').combobox('enable');
        // 初始化所属业务
        $('#selSsywid').combobox({
            editable:true,
            data:[{value: '', text: '请选择'}].concat(data.yw_lst),
            valueField:'value',
            textField:'text'
        });
        // 默认选中第一个值
        if( $("#selSsywid").combobox("getData").length > 0 ){
            $("#selSsywid").combobox('select', $("#selSsywid").combobox("getData")[0].value);
        }
        // 清空cdtxid
        $("#hidCdtxid").val('');
    }
    else if(handle=='update'){
        // 编辑对象信息
        var d = data.cdtxjbxx_dic;
        // 编码
        $("#txtBm").textbox('setValue', d.bm);
        $('#txtBm').textbox('disable');
        // 初始化所属业务
        $('#selSsywid').combobox({
            editable:true,
            data:data.yw_lst,
            valueField:'value',
            textField:'text'
        });
        
        // 其他信息
        $("#txtDfjym").textbox('setValue', d.dfjym);
        $("#txtDfjymc").textbox('setValue', d.dfjymc);
        $("#txtCssj").numberbox('setValue', d.cssj);
        // 打包配置
        $("#selDbjdid").combobox("select",d.dbjdid);
        // 解包配置
        $("#selJbjdid").combobox("select",d.jbjdid);
        // 赋值cdtxid
        $("#hidCdtxid").val(d.id);
        // 赋值zlcdyid
        $("#hidZlcdyid").val(d.zlcdyid);
        // 赋值dbjdid
        $("#hidYdbjdid").val(d.dbjdid);
        // 赋值jbjdid
        $("#hidYjbjdid").val(d.jbjdid);
        
        // 默认选中选择所属业务
        if( $("#selSsywid").combobox("getData").length > 0 ){
            $("#selSsywid").combobox('select', d.ssywid);
        }
        //$('#selSsywid').combobox('disable');
        
        // 冲正配置
        if( $("#selCzpzid").combobox("getData").length > 0 ){
            $("#selCzpzid").combobox('select', d.czzlcdyid);
        }
    }
}

/**
*初始化打包解包选择框
*/
function initDbJb(){
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_add2edit_dbjb_view",
        success: function(data){
            // 反馈信息
            data = $.parseJSON( data );
            if( data.state == true ){
                // 打包配置
                data.dbjd_lst.unshift({
                    'data': '',
                    'value': '请选择'
                });
                data.dbjd_lst.push({
                    'data': '',
                    'value': '<a href="javascript:;" onclick="nodeEdit(5)">新增打包节点</a>'
                });
                $('#selDbjdid').combobox('loadData', data.dbjd_lst);
                
                // 解包配置
                data.jbjd_lst.unshift({
                    'data': '',
                    'value': '请选择'
                });
                data.jbjd_lst.push({
                    'data': '',
                    'value': '<a href="javascript:;" onclick="nodeEdit(6)">新增解包节点</a>'
                });
                $('#selJbjdid').combobox('loadData', data.jbjd_lst);
                
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
*新增or编辑提交
*/
function saveSub( dgid, winid ){
    // 添加遮罩
    ajaxLoading();
    // 通讯ID
    var txid = $( "#hidTxid" ).val();
    // 出错提示(默认新增)
    var msg = "新增失败，请稍后再试";
    var url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_add_view";
    if ( $("#hidCdtxid").val() != "" ){
        // 修改
        url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_edit_view",
        msg = "修改失败，请稍后再试";
    }
    // 提交表单
    $('#' + winid).find('form').form('submit', {
        url: url,
        queryParams: {'txid': txid},
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
*编辑页面编辑前校验
*/
function subCheck(){
    // 编辑C端通讯
    var cdtxid = $("#hidCdtxid").val();
    // 返回参数默认true
    var ret = true;
    // 新增时需要校验C端通讯编码
    if( cdtxid == ''){
        var bm = $("#txtBm").textbox("getValue");
        // 校验编码
        ret = checkNull( bm, 'C端通讯编码', 'txtBm' );
        // 校验编码中文
        if( ret ){
            ret = checkBm( bm, 'C端通讯编码', 'txtBm' )
        }
    }
    // 编辑和新增都需要校验的信息
    var dfjym = $("#txtDfjym").textbox("getValue");
    var dfjymc = $("#txtDfjymc").textbox("getValue");
    var cssj = $("#txtCssj").numberbox("getValue");
    var selDbjdid = $("#selDbjdid").combobox("getValue");
    var selJbjdid = $("#selJbjdid").combobox("getValue");
    
    //校验对方交易码
    if( ret ){
        ret = checkNull( dfjym, '对方交易码', 'txtDfjym' );
    }
    // 校验对方交易码中文( 因为是对方的所有不可控，既只限定不可为中文 )
    if( ret ){
        ret = checkValZw( dfjym, '对方交易码', 'txtDfjym' )
    }
    //校验对方交易名称
    if( ret ){
        ret = checkNull( dfjymc, '对方交易名称', 'txtDfjymc' );
    }
    //校验超时时间
    if( ret ){
        ret = checkNull( cssj, '超时时间', 'txtCssj' );
    }
    if( ret ){
        ret = checkInt( cssj, '超时时间', 'txtCssj' );
    }
    //打包配置
    if( ret ){
         // 校验非空
        if (selDbjdid=="") {
            $.messager.alert('错误', '打包配置不可为空，请选择','error', function(){
                $("#selDbjdid").focus();
            });
            ret = false;
            return ret;
        }else if (selDbjdid == null ){
             // 校验下拉框内容选择是否存在下拉列表中
             ret = checkNull3( selDbjdid, '打包配置', 'selDbjdid' );
        }else{
            ret = true;
        }
    }
    //解包配置
    if( ret ){
        // 校验非空
        if (selJbjdid=="") {
            $.messager.alert('错误', '解包配置不可为空，请输入','error', function(){
                $("#selJbjdid").focus();
            });
            ret = false;
            return ret;
        }else if (selJbjdid == null ){
             // 校验下拉框内容选择是否存在下拉列表中
             ret = checkNull3( selJbjdid, '解包配置', 'selJbjdid' );
        }else{
            ret = true;
        }
    }
    // 校验所属业务
    var ssywid = $("#selSsywid").combobox("getValue");
    if (ssywid == '-1') {
        ssywid = '';
    }
     // 所属业务
    if( ret ){
        // 校验是否为空
        ret = checkNull2( ssywid, '所属业务', 'selSsywid' );
    }
    if(ret){
        // 校验下拉框内容选择是否存在下拉列表中
        ret = checkNull3( ssywid, '所属业务', 'selSsywid' );
    }

    return ret
}

/**
*删除
*/
function removeCdtx( dgid, rowIndex ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    $.messager.confirm('确认', 'C端通讯删除后将无法恢复，您确认要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            var d = $('#'+dgid).datagrid('getData').rows[rowIndex];
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_del_view",
                data: { "cdtxid": d.id, 'zlcdyid': d.zlcdyid, 'bm': d.bm },
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
*打开挡板信息页面
*/
function cdtxgl_dbxx( rowIndex ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 选择行信息
    var d = $('#dgCdtx').datagrid('getData').rows[rowIndex];
    //定义url
    url = '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_view?cdtxid=' + d.id;
    $('#dbglFrame').attr('src', url );
    newWindow($("#divDbglWindow"),d.dfjymc+'_挡板管理',1030,520);
}

/**
*删除挡板
*/
function del_db( dgid, cdtxid ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    $.messager.confirm('确认', '是否取消使用此挡板', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_yydb_del_sel_view",
                data: { "cdtxid": cdtxid },
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
*打开测试案例信息页面
*/
function cdtxgl_csal( rowIndex ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 选择行信息
    var d = $('#dgCdtx').datagrid('getData').rows[rowIndex];
    //定义url
    url = '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_csal_view?cdtxid=' + d.id;
    $('#csalFrame').attr('src', url );
    newWindow( $("#csalWindow"), '通讯测试案例管理',1230,520 );
}

/**
*节点编辑或新增
*/
function nodeEdit( jdlx, selId) {
    // 编辑
    if( selId != '' && selId != undefined ){
        var jdid = $("#" + selId).combobox("getValue");
        if( jdid == '' ){
            $.messager.alert( '错误', '请先选择节点，再进行编辑', 'error' );
            $("#" + selId).next().children().focus();
            return false;
        }
        newWindow2($("#winNodeEdit"), '节点编辑', '85', 480);
        $("#winNodeEdit iframe")[0].src = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_edit_view?nodeid=" + jdid;
    }else{
        // 新增
        newWindow2($("#winNodeEdit"), '节点新增', '85', 480);
        $("#winNodeEdit iframe")[0].src = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_edit_view?jdlx=" + jdlx;
    }
}

/**
*打开接口校验页面
*/
function cdtxgl_jkjy( rowIndex ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 选择行信息
    var d = $('#dgCdtx').datagrid('getData').rows[rowIndex];
    //定义url
    url = '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_jkjy_qyjy_sel_view?cdtxid=' + d.id;
    $('#jkjyFrame').attr('src', url );
    newWindow($("#divJkjyWindow"),'接口校验配置',750,450);
}

/**
 *  查询事件
 */
function doSearch(){

    // 编码
    var bm = $("#searchBm").textbox("getValue");
    // 对方交易名称
    var dfjymc = $("#searchDfjymc").textbox("getValue");
    // 对方交易码
    var dfjym = $("#searchDfjym").textbox("getValue");
    // 打包
    var db = $("#txtDb").textbox("getValue");
    // 解包
    var jb = $("#txtJb").textbox("getValue");
    // 有无挡板
    var ywdb = $("#searchYwdb").combobox("getValue");
    // 接口校验
    var jkjy = $("#searchJkjy").combobox("getValue");

    // 根据条件查询对象
    $("#dgCdtx").datagrid("load",{
        bm: bm,dfjymc: dfjymc,dfjym: dfjym,db: db,jb: jb,ywdb: ywdb,jkjy: jkjy
    });
};
