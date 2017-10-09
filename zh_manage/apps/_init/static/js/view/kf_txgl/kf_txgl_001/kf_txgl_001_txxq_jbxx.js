$(document).ready(function() {
    
    // 渲染表格
    datagrid = $('#dgTxcs').datagrid({
        title: '通讯参数设置',
        nowrap : false,
        fit : true,
        height: '150px',
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        method: "get",
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        frozenColumns: [[
            { field: 'select_box', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: '参数ID', hidden: true },
            { field: 'csdm', title: '参数代码', width: '20%' },
            { field: 'value', title: '参数值', width: '20%' },
            { field: 'csms', title: '参数描述', width: '30%' },
            { field: 'zt', title: '状态', width: '13%', formatter: function(value,rowData,rowIndex) {
                return value=="1" ? "启用" : "禁用"; 
            } },
            { field: 'cz', title: '操作', width: '12%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:void(0);" onclick="showHide(\'update\',\'dgTxcs\',\''+rowData.id+'\',\'divTxcsWindow\',\'编辑通讯参数\');">编辑</a>';
            } }
        ]],
        toolbar : [
            {
                iconCls : 'icon-add',
                text : '新增',
                handler : function() {
                    // 增加
                    showHide( 'add','dgTxcs','', 'divTxcsWindow', '新增通讯参数' )
                }
            }, {
                iconCls : 'icon-remove',
                text : '删除',
                handler : function() {
                    // 调用删除方法
                    removechecked( 'dgTxcs', 'hidTxid' );
                }
            }
        ]
    });
    
    // 进程并发数
    // 服务方向 1（客户端） 2（服务端）
    var fwfx = $('#hidFwfx').val();
    if( fwfx == '1' ){
        $("#tdJcbfsK").hide();
        $("#tdJcbfsV").hide();
    }else{
        $("#tdJcbfsK").hide();
        $("#tdJcbfsV").hide();
    }
    // 通讯文件名称选择
    if( $("#selTxwjmc").combobox("getData").length > 0 ){
        $("#selTxwjmc").combobox('select', $("#hidTxwjmc").val());
    }
    
    // 最大值限制
    $("#txtTxmc").next().children().attr("maxlength","25");
    $("#txtCssj").next().children().attr("maxlength","4");
    $("#txtCsdm").next().children().attr("maxlength","32");
    $("#txtCsz").next().children().attr("maxlength","100");
    $("#txtCsms").next().children().attr("maxlength","150");
    
    //初始化通讯基本信息保存按钮事件
    //初始化按钮
    $("#lbtnJbxxSubmit").click(function(e){
        e.preventDefault();
        editSub();
    })
    //初始化参数按钮
    $("#lbtnTxcsSubmit").click(function(e){
        e.preventDefault();
        // 保存提交
        saveSub( 'hidTxid', 'dgTxcs', 'divTxcsWindow' );
    })
    
    //初始化参数按钮
    $("#lbtnTxcsCancel").click(function(e){
        e.preventDefault();
        $("#divTxcsWindow").window('close');
    })
    
    // 主页面 form tab排序
    $("#fmJbxx").tabSort();
    
    $("#txtCsdm").next().children().on('keydown', function(e){
        var that = this;
        var value = this.value;
        // 按键的keycode
        var keycode = e.which;
        // shift键是否按住
        var isshift = e.shiftKey;
        if(keycode == 229) {
            $(that).blur();
            setTimeout(function() {
                $(that).focus()
            }, 10)
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    });

    $("#txtCsdm").next().children().on('keypress', function(e){
        var that = this;
        var value = this.value;
        // 按键的keycode
        var keycode = e.which;
        // shift键是否按住
        var isshift = e.shiftKey;
        if ((keycode >= 65 && keycode <= 90)
            || keycode == 8
            || keycode == 46
            // || keycode == 36
            || (keycode >= 48 && keycode <= 57)
            || (keycode == 95)) {
        } else {
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    });
    
    // 通讯类型
    $('#selTxlx').combobox({
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
                        $('#fmJbxx').tabSort();
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
    // 主页面重新定义元素顺序
    $('#fmJbxx').tabSort();
});

/**
*通讯基本信息保存提交
*/
function editSub(){
    // 添加遮罩
    ajaxLoading();
    // 提交表单
    $('#divJbxx').find('form').form('submit', {
        url: '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_jbxx_edit_view',
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
            afterAjax(data, "", "");
            // 更新tab名称
            txmc = $("#txtTxmc").textbox("getValue");
            var parentDocument = window.parent.parent.document;
            top.$(parentDocument).find("#pnlMain ul.tabs .tabs-selected span.tabs-title").text(txmc + '_通讯详情');
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/**
*编辑提交前台校验
*/
function checkXx(){
    var fwfx = $("#hidFwfx").val();
    var txmc = $("#txtTxmc").textbox("getValue");
    var txlx = $("#selTxlx").combobox("getValue");
    var cssj = $("#txtCssj").numberbox("getValue");
    var txwjmc = $("#selTxwjmc").combobox("getValue");
    var jcbfs = $("#txtJcbfs").numberbox("getValue");
    
    // 通讯名称
    var ret = checkNull( txmc, '通讯名称', 'txtTxmc' );
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
    // 超时时间
    if( ret ){
        ret = checkNull( cssj, '超时时间', 'txtCssj' );
    }
    if( ret ){
        ret = checkInt( cssj, '超时时间', 'txtCssj' );
    }
    //通讯文件名称
    if( ret ){
        ret = checkNull2( txwjmc, '通讯文件名称', 'selTxwjmc' );
    }
    //通讯文件名称是否在拉框数据中
    if(ret){
        ret = checkNull3( txwjmc, '通讯文件名称', 'selTxwjmc' );
    }
//    // 客户端校验进程并发数
//    if( ret && fwfx == '1' ){
//        ret = checkNull( jcbfs, '进程并发数', 'txtJcbfs' );
//        if( ret ){
//            ret = checkInt( jcbfs, '进程并发数', 'txtJcbfs' );
//        }
//    }
    
    return ret;
}

/**
* 新增or编辑通讯参数弹窗
* handle: 操作类型
* dgid：数据表格id
* csid：编辑信息id
* winid：open窗口的win
* wintit：open窗口的title
*/
function showHide( handle, dgid, csid, winid, wintit ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 向后台请求信息
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_csgl_add2edit_sel_view",
        data: {'csid': csid},
        success: function(data){
            // 打开窗口
            newWindow($( "#" + winid ),wintit,450,280);
            // 反馈信息
            data = $.parseJSON(data);
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                pageInit( handle, data )
                // 重新初始化tabindex
                $('#txcsform').tabSort();
            }else{
                afterAjax(data, "", "");
            }
            $('#txtCsdm').textbox('textbox').attr('placeholder', '仅能输入大写字母数字下划线');
        },
        error: function(){
            errorAjax();
        }
    });
}

/**
*参数页面初始化
*/
function pageInit( handle, data ){
    if(handle=='add'){
        $("#nfsCszt").get(0).checked = true;
        // 新增时参数代码控件可编辑
        $("#txtCsdm").textbox('enable');
        // 清空参数ID
        $("#csid").val('');
    }else if(handle=='update'){
        // 编辑对象信息
        var d = data.csxx_dic;
        $("#nfsCszt").get(0).checked = (d.zt=="1");
        $("#csid").val(d.id);
        // 参数代码
        $("#txtCsdm").textbox('setValue', d.csdm);
        $("#txtCsdm").textbox('disable');
        // 参数值、描述
        $("#txtCsz").textbox('setValue', d.value);
        $("#txtCsms").textbox('setValue', d.csms);
    }
}

/**
*参数信息提交
*/
function saveSub( ssidid, dgid, winid ){
    // 添加遮罩
    ajaxLoading();
    // 通讯ID
    var ssid = $( "#" + ssidid ).val();
    // 参数状态
    var cszt = $( "#nfsCszt" ).get(0).checked ? "1" : "0";
    // 出错提示
    var msg = "新增失败，请稍后再试";
    if ($("#csid").val()=="") {
        // 新增
        url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_csgl_add_view";
    } else {
        // 修改
        url = "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_csgl_edit_view",
        msg = "修改失败，请稍后再试";
    }
    // 提交表单
    $('#' + winid).find('form').form('submit', {
        url: url,
        queryParams: {'ssid': ssid, 'cszt': cszt},
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
*参数页面提交前校验
*/
function subCheck(){
    // 编辑参数id
    var csid = $("#csid").val();
    var csbm = $("#txtCsdm").textbox("getValue");
    var csz = $("#txtCsz").textbox("getValue");
    var csms = $("#txtCsms").textbox("getValue");
    
    // 查看样式
    ret = true
    if (csid=="") {
        // check 参数代码
        ret = checkNull( csbm, '参数代码', 'txtCsdm' );
        if( ret ){
            ret = checkBm( csbm, '参数代码', 'txtCsdm' )
        }
    }
    if ( ret ) {
        // 参数值
        ret = checkNull( csz, '参数值', 'txtCsz' );
    }
    return ret;
}

/**
*批量删除
*/
function removechecked( dgid, ssidid ){
    if(!checkSelected(dgid)) {
        return;
    }
    $.messager.confirm('确认', '参数删除后将无法恢复，您确认要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 当前选中的记录
            var checkedItems = $('#' + dgid).datagrid('getChecked');
            var ids = new Array();
            $(checkedItems).each(function(index, item){
                ids.push( item['id'] );
            });
            
            // 发送删除请求
            var ssid = $( "#" + ssidid ).val();
            var txbm = $("#txtTxbm").textbox("getValue");
            var txmc = $("#txtTxmc").textbox("getValue");
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_csgl_del_view",
                data: { "ids": ids.join(","), 'ssid': ssid, 'txbm': txbm, 'txmc': txmc },
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

