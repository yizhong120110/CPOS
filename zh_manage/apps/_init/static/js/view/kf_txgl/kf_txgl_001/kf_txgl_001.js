
$(document).ready(function() {
    var txtFwfx = $("#txtFwfx").combobox("getValue");
    if (txtFwfx =="" || txtFwfx == null){
        $("#txtFwfx").combobox('setValue','0');
    }
    //tab顺
    $("#jbxxForm").tabSort()
    // 渲染表格
    $('#dgTxgl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize : 50,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/data_view",
        remoteSort: false,
        frozenColumns: [[
            { field: 'ck', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: '通讯id', width: 5, hidden:true },
            { field: 'bm', title: '通讯编码', width: 31 },
            { field: 'mc', title: '通讯名称', width: 33 },
            { field: 'fwfx', title: '服务方向id', width: 5, hidden:true },
            { field: 'fwfxmc', title: '服务方向', width: 12, formatter: function(value,rowData,rowIndex) {
                //服务方向 1（客户端） 2（服务端）
                fwfxmc = '客户端'
                if ( rowData.fwfx == '2' )
                    fwfxmc = '服务端'
                return fwfxmc;
            } },
            { field: 'txlx', title: '通讯类型', width: 23 },
            { field: 'txwjmc', title: '通讯文档名称', width: 25 },
            { field: 'operation', title: '操作', width: 19, formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="selTxglXq(event, \''+ rowData.id +'\', \''+ rowData.fwfx +'\', \''+ rowData.mc +'\')">详细信息</a>&nbsp;&nbsp;'
                      +'<a href="javascript:void(0);" onclick="txglRemove(\'dgTxgl\','+rowIndex+')">删除</a>'
                      +'<a href="javascript:;" onclick="tx_dm_dc(event,\''+rowData.id+'\');" > 代码导出</a>';
            } }
        ]],
        toolbar : [ 
            {
                iconCls : 'icon-add',
                text : '新增客户端通讯',
                handler : function() {
                    // 增加
                    showHideTx('新增客户端通讯','1');
                }
            },'-',{
                iconCls : 'icon-add',
                text : '新增服务端通讯',
                handler : function() {
                    // 增加
                    showHideTx('新增服务端通讯','2');
                }
            },'-',{
                iconCls : 'icon-down',
                text : '导入',
                handler : function() {
                    dr_tab();
                }
            },'-',{
                iconCls : 'icon-up',
                text : '导出',
                handler : function() {
                    //导出
                    dc_tab();
                }
            },'-',{
                iconCls : 'icon-history-look',
                text : '历史',
                handler : function() {
                    //查看
                    open_bqxxck();
                }
            }
        ]
    });
    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });
    
    //初始化按钮(保存)
    $("#lbtnTxglSubmit").click(function(e){
        e.preventDefault();
        // 新增提交
        addSub();
    })
    //初始化按钮（取消）
    $("#lbtnTxglCacel").click(function(e){
        e.preventDefault();
        $("#divTxglWindow").window('close');
    })
    
    // 最大值限制
    $("#txtTxbm").next().children().attr("maxlength","50");
    $("#txtTxmc").next().children().attr("maxlength","25");
    $("#txtCssj").next().children().attr("maxlength","4");
    
    // 通讯导入
    $("#lbtnTxdrCancel").click(function (e){
        e.preventDefault();
        e.stopImmediatePropagation();
        $("#divTxdrWindow").window('close');
    });
    $("#lbtnTxdrSubmit").click(function (e){
        e.preventDefault();
        //通讯ID
        var txid = $('#selTxdr').combogrid('getValues');
        if(txid==''){
            $.messager.alert('错误','导入通讯不可为空,请选择','error', function(){
                $("#selTxdc").next().children().focus();
            });
            return false;
        }
        title = '通讯导入';
        var url = "/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/index_view?txid="+txid+'&drlx='+'tx';
        newTab(title, url);
        $("#divTxdrWindow").window('close');
    });
});

// 信息查询
function doSearch() {
	
    // 通讯编码
    var txbm = $("#txtSeaTxbm").textbox('getValue');
    // 通讯名称
    var txmc = $("#txtSeaTxmc").textbox('getValue');
    // 服务方向
    var fwfx = $("#txtFwfx").combobox('getValue');
    // 通讯类型
    var txlx = $("#txtTxlx").textbox('getValue');
    // 通讯文档名称
    var txwdmc = $("#txtTxwdmc").textbox('getValue');

    // 根据条件查询对象
    $("#dgTxgl").datagrid('load',{
        txbm:txbm,
        txmc:txmc,
        fwfx:fwfx,
        txlx:txlx,
        txwdmc:txwdmc
    });
}

/**
* 添加通讯弹出框初始化
*/
function showHideTx(title, fwfx){
    //title：页面标题
    //fwfx：服务方向 1（客户端） 2（服务端）
    
    //向后台请求页面初始化信息，初始化页面
    $.ajax({
        type: 'GET',
        dataType: 'text',
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/data_add_sel_view",
        data: {'fwfx': fwfx},
        success: function(data){
            // 打开窗口
            // 服务端窗口要低一些(进程并发数存在高度为280)
            var height = 250;
            if( fwfx == '2' )
                height = 250
            newWindow($("#divTxglWindow"),title, 660, height);
            // 反馈信息初始化页面
            data = $.parseJSON(data);
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                addPageInit( fwfx, data )
                // 重新初始化tabindex
                $('#txform').tabSort();
            }else{
                afterAjax(data, "", "");
            }
        },
        error : function(){
            errorAjax();
        }
    });

};

/**
* 通讯新增页面初始化
*/
function addPageInit( fwfx, data ){
    // 通讯类型
    $('#selTxlx').combobox({
        editable:true,
        data:data.txlx_lst,
        valueField:'value',
        textField:'text',
        onSelect: function(record) {
            var txlxbm = record.value;
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/data_add_bytxlx_txwj_view",
                data: {'txlx': txlxbm, 'fwfx': fwfx},
                success: function(data){
                    // 反馈信息初始化文件列表
                    data = $.parseJSON(data);
                    // 获取数据成功
                    if( data.state == true ){
                        // 通讯文件名称
                        $('#selTxwjmc').combobox({
                            editable:true,
                            data:data.txwjmc_lst,
                            valueField:'value',
                            textField:'text'
                        });
                        //默认选择第一个
                        if( data.txwjmc_lst.length > 0 ){
                            $("#selTxwjmc").combobox('select', $("#selTxwjmc").combobox("getData")[0].value);
                        }
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
    //默认选择第一个
    if( data.txlx_lst.length > 0 ){
        $("#selTxlx").combobox('select', $("#selTxlx").combobox("getData")[0].value);
    }
    // 服务方向
    // 服务端
    if (fwfx == '2') {
        // 交易码解出交易显示
        $("#trJcbfs").hide();
        $("#hidFwfx").val("2");
        $("#spFwfxMc").text("服务端");
    } else {
        // 交易码解出交易隐藏
        $("#trJcbfs").hide();
        $("#hidFwfx").val("1");
        $("#spFwfxMc").text("客户端");
    }
    // 超时时间
    $("#txtCssj").numberbox('setValue',data.cssj);
}

/**
* 新增提交
*/
function addSub(){
    // 添加遮罩
    ajaxLoading();
    // 提交表单
    $('#divTxglWindow').find('form').form('submit', {
        url: '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/data_add_view',
        onSubmit: function(){
            // 获取校验元素值
            var ret = checkXx();
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
            afterAjax(data, "dgTxgl", "divTxglWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
    
}

/**
* 新增提交前台校验
*/
function checkXx(){
    var fwfx = $("#hidFwfx").val();
    var txbm = $("#txtTxbm").textbox("getValue");
    var txmc = $("#txtTxmc").textbox("getValue");
    var txlx = $("#selTxlx").combobox("getValue");
    var cssj = $("#txtCssj").numberbox("getValue");
    var txwjmc = $("#selTxwjmc").combobox("getValue");
    var jcbfs = $("#txtJcbfs").numberbox("getValue");
    
    // 校验通讯编码
    var ret = checkNull( txbm, '通讯编码', 'txtTxbm' );
    // 校验通讯编码中文
    if( ret ){
        ret = checkBm( txbm, '通讯编码', 'txtTxbm' )
    }
    // 通讯名称
    if( ret ){
        ret = checkNull( txmc, '通讯名称', 'txtTxmc' );
    }
    if( ret ){
        ret = checkMc( txmc, '通讯名称', 'txtTxmc' );
    }
    //通讯类型
    if( ret ){
        ret = checkNull2( txlx, '通讯类型', 'selTxlx' );
    }
    //通讯类型是否在拉框数据中
    if(ret){
        ret = checkNull3( txlx, '通讯类型', 'selTxlx' );
    }

    //通讯文件名称
    if( ret ){
        ret = checkNull2( txwjmc, '通讯文件名称', 'selTxwjmc' );
    }
    //通讯文件名称是否在拉框数据中
    if(ret){
        ret = checkNull3( txwjmc, '通讯文件名称', 'selTxwjmc' );
    }

    // 超时时间
    if( ret ){
        ret = checkNull( cssj, '超时时间', 'txtCssj' );
    }
    if( ret ){
        ret = checkInt( cssj, '超时时间', 'txtCssj' );
    }

//    //客户端校验：进程并发数
//    if( ret && fwfx == '1' ){
//        ret = checkNull( jcbfs, '进程并发数', 'txtJcbfs' );
//        if( ret ){
//            ret = checkInt( jcbfs, '进程并发数', 'txtJcbfs' );
//        }
//        if( ret ){
//            if( parseInt(jcbfs) <1 || parseInt(jcbfs) > 999 ){
//                $.messager.alert('错误','进程并发数不在规定范围[1-999]内，请重新输入','error', function(){
//                    $("#txtJcbfs").next().children().focus();
//                });
//                ret = false;
//            }
//        }
//    }
    
    return ret;

}

/**
* 删除通讯
*/
function txglRemove( dbId, rowIndex ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    $.messager.confirm('确认', '删除通讯会将此通讯下所有配置信息删除且不可恢复，您确定要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            var d = $('#'+dbId).datagrid('getData').rows[rowIndex];
            //发送删除请求
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/data_del_view",
                data: {'txid': d.id,'txmc': d.mc, 'fwfx': d.fwfx, 'txbm': d.bm},
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, dbId, "");
                },
                error : function(){
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    });
}

/**
* 查看通讯详情
*/
function selTxglXq( event, txid, fwfx, txmc ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    var title = '通讯详情';
    if ( txmc != '' )
        title = txmc + '_通讯详情';
    var url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_view?txid=" + txid + "&fwfx=" +fwfx + "&nocache=" +Math.random();
    newTab(title, url);
}

/*
*通讯导入
*/
function dr_tab(){
    var checkedItems = $('#dgTxgl').datagrid('getChecked');
    var txid = new Array();
    $(checkedItems).each(function(index, item){
        txid.push(item["id"]);
    });
    var txids = txid.join(",")
    if(txids){
        title = '通讯导入';
        var url = "/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/index_view?txid="+txids+'&drlx='+'tx';
        newTab(title, url);
    }
    else{
        $('#selTxdr').combogrid({
            panelWidth:280,
            editable:true,
            idField:'id',
            textField:'mc',
            method: "get",
            multiple:true,
            pagination : false,
            onChange:onChange,
            rowStyler: function(index,row) {
                style_str = '';
                if (row.id == '-1') {
                    style_str = "color:blue;"
                } 
                return style_str
            },
            url:'/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/dr_data_view',
            columns:[[   
                {field:'id', title:'ID', width:60, hidden:true},
                {field: 'mc', title: '通讯名称', width: 250},
            ]]
        })
        newWindow($("#divTxdrWindow"),'通讯管理导入',400,200);
    }
}

/**
*选择导入通讯时触发
*/
function onChange(newValue,oldValue){
    //选择导入新通讯，在选择其他通讯
    if(oldValue[0]!='' &&oldValue[0]!=undefined){
        if(oldValue.length!=0 && oldValue.length==1 &&oldValue[0] == '-1'&&newValue!=''){
            $('#selTxdr').combogrid('hidePanel');   
            $.messager.alert('提示','导入新通讯时,不可再导入其他通讯,请重新选择','info');
            $('#selTxdr').combogrid('reset');  
        }
    }
    if(newValue.lenth!=0&&oldValue[0]!='' &&oldValue[0]!=undefined&&oldValue[0]!='-1'){
        //若选择了其他通讯，在选择导入新通讯
        if(newValue[newValue.length-1] == '-1'){
            $('#selTxdr').combogrid('hidePanel');   
            $.messager.alert('提示','导入已存在通讯时,不可再导入新通讯,请重新选择','info');
            $('#selTxdr').combogrid('reset');  
        }
    }
}

/**
*通讯导出
*/
function dc_tab(){
    //校验是否可执行导出
    if( $('#dgTxgl').datagrid('getData').rows.length == 0 ){
        $.messager.alert('提示','没有可导出通讯','info')
        return false
    }
    var checkedItems = $('#dgTxgl').datagrid('getChecked');
    var txid = new Array();
    $(checkedItems).each(function(index, item){
        txid.push(item["id"]);
    });
    var txids = txid.join(",")
    title = '通讯导出';
    var url = "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/index_view?dclx="+'tx'+"&txid="+txids;
    newTab(title, url);
}

/*
*历史版本信息查看
*/
function open_bqxxck(){
    var title = '通讯管理_导入历史'
    var url = "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/index_view?nrlx=tx&ss_idlb=" + "&nocache=" +Math.random();
    newTab(title, url);
}

/*
*通讯代码导出
*/
function tx_dm_dc(event, txid){
    event.stopPropagation();
    var to_path = 'window.location.href="/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/index_view"'
    dm_down( 'dgTxgl', 'tx', '', to_path, txid );
}
