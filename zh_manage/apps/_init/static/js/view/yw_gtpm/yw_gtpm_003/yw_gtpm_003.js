/**
* 阈值校验流水
*/
$(document).ready(function() {
    // 渲染表格
    var datagrid = $('#dgYzxyls').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        pagination: true,
        fitColumns: true,
        method: "post",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        pageSize:50,
        remoteSort: false,
        url: "/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/data_view",
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [[
            {
                field: 'id',
                title: '文件id',
                hidden: true 
            },
            {
                field: 'wjlx',
                title: '文件类型',
                width: 70
            }, {
                field: 'wjmc',
                title: '文件名称',
                width: 100
            }, {
                field: 'ywmc',
                title: '所属业务',
                width: 100
            }, {
                field: 'pch',
                title: '批次号',
                width: 100
            }, {
                field: 'djrq',
                title: '登记日期',
                width: 100,
                align: 'center'
            }, {
                field: 'djsj',
                title: '登记时间',
                width: 100,
                align: 'center'
            }, {
                field: 'updtime',
                title: '最后更新时间',
                width: 100,
                align: 'center'
            }, {
                field: 'zt',
                title: '状态',
                width: 100
            }, {
                field: 'cz',
                title: '操作',
                width: 150,
                formatter: function(value, rowData, rowIndex) {
                    Str_show = '<a href="javascript:void(0);" onclick="ckmx(\''+rowData.id+'\',\''+rowData.wjmc+'\',\''+rowData.ywmc+'\');">查看明细</a> ' +
                        '<a href="javascript:void(0);" onclick="cx(' + rowData.id + ');">撤销</a> '+
                        '<a href="javascript:void(0);" onclick="tg(' + rowData.id + ');">通过</a> ';
                    if (rowData.ztbm == "66" || rowData.ztbm == "77" || rowData.ztbm == "88" ) {
                        Str_show = Str_show + '<a href="javascript:void(0);" onclick="xgyz(\''+rowData.id+'\');">修改阈值</a>';
                    }
                    return Str_show
                }
            }]
        ],
        toolbar: [{
            iconCls:'icon-edit',
            text: '将文件置为待扣款',
            handler:function(){
                zwjwdkk();
            }
        }],
    });

    // 所属业务的下拉列表
    $("#selSsyw").combobox({
        data: ssyw,
        valueField: 'id',
        textField: 'ywmc'
    });

    // 监控类型的下拉列表
    $("#selJklx").combobox({
        data: jklx,
        valueField: 'value',
        textField: 'text'
    });

    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });
    
    /*
     *新增或编辑页面按钮事件
     */
    $("#window_edit_yz").click(function() {
        $.messager.alert('提示', '保存成功!', 'info');
    });

    $("#window_edit_dkk").click(function() {
        $('#bean_window').window('close');
    });
    $('#yzjylsForm').tabSort();
});

/**
* 条件查询
* event：时间对象
*/
function doSearch(){
    // 所属业务
    var ssyw = $("#selSsyw").textbox("getValue");
    // 开始日期
    var startJyrq = $("#dateStartJyrq").datebox("getValue");
    // 结束日期
    var endJyrq = $("#dateEndJyrq").datebox("getValue");
    // 监控类型
    var jklx = $("#selJklx").textbox("getValue");
    var ksrq = startJyrq;
    var jsrq = endJyrq;
    if (ksrq && !jsrq) {
        $.messager.alert('错误','结束日期不可为空，请选择','error', function(){
            $("#dateEndJyrq").next().children().select();
        });
        return false;
    }
    if (jsrq && !ksrq) {
        $.messager.alert('错误','开始日期不可为空，请选择','error', function(){
            $("#dateStartJyrq").next().children().select();
        });
        return false;
    }
    if( ksrq ){
        if (!checkDate10( ksrq,'开始日期','dateStartJyrq' )){
            return false;
        }
    }
    if( jsrq ){
        if (!checkDate10( jsrq,'结束日期','dateEndJyrq' )){
            return false;
        }
    }
    if (ksrq>jsrq) {
        $.messager.alert('错误', '开始日期不可大于结束日期，请重新选择', 'info')
        return false;
    }
    // 根据条件查询管理对象
    $("#dgYzxyls").datagrid('load',{
        ssyw: ssyw,
        startJyrq: startJyrq,
        endJyrq: endJyrq,
        jklx: jklx
    });
}

/**
 * 修改阈值
 */
function xgyz(wjid) {
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 添加遮罩
    ajaxLoading();
    $.ajax({
        url:'/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/xgyz_view',
        type : 'post',
        dataType : 'text',
        data : {
            'wjid' : wjid
        },
        success:function(data){
            // 取消遮罩
            ajaxLoadEnd();
            if (typeof data == 'string') {
                data = $.parseJSON(data);
            }
            if (data.state == true) {
                // 打开编辑页面
                newWindow($("#divXzcs"),'编辑参数页面',500, 380);
                $("#iframeXzcs").attr("src","/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/cspz_ggym_view?id="+data['id']);
            }else{
                afterAjax(data,"","");
            }
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
};

/**
 * 撤销
 */
function cx(wjid) {
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    $.messager.confirm('提示','撤消后不再进行核心扣款，直接更新为扣款失败，您确定要撤销吗？', function(r){
        if(r){
            // 添加遮罩
            ajaxLoading();
            $.ajax({
                url:'/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/cx_view',
                type : 'post',
                dataType : 'json',
                data : {
                    'wjid' : wjid
                },
                success:function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    if (typeof data == 'string') {
                        data = $.parseJSON(data);
                    }
                    if (data.state == true) {
                        //执行请求后的方法
                        afterAjax(data, 'dgYzxyls','');
                    }else{
                        afterAjax(data, '','');
                    }
                },
                error: function () {
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    });
}
/**
 * 通过
 */
function tg(wjid) {
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    $.messager.confirm('提示','通过后不再进行阈值校验，直接导入GTP流水中，等待GTP扣款，您确定要通过吗？', function(r){
        if(r){
            // 添加遮罩
            ajaxLoading();
            $.ajax({
                url:'/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/tg_view',
                type : 'post',
                dataType : 'json',
                data : {
                    'wjid' : wjid
                },
                success:function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    if (typeof data == 'string') {
                        data = $.parseJSON(data);
                    }
                    if (data.state == true) {
                        //执行请求后的方法
                        afterAjax(data, 'dgYzxyls','');
                    }else{
                        afterAjax(data, '','');
                    }
                },
                error: function () {
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    });
}
/**
 * 查看明细
 */
function ckmx(id,wjm,ywmc) {
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 添加遮罩
    ajaxLoading();
    $.ajax({
        url:'/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/index_check_mxck_view',
        type : 'post',
        dataType : 'json',
        data : {
            'id' : id
        },
        success:function(data){
            // 取消遮罩
            ajaxLoadEnd();
            if (typeof data == 'string') {
                data = $.parseJSON(data);
            }
            if (data.state == true) {
                //执行请求后的方法
                newTab("阈值监控-查看明细", "/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/index_mxck_view?id="+id + "&wjm=" + wjm + "&ywmc=" + ywmc );
            }else{
                afterAjax(data,"","");
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
 * 置文件为代扣款
 */
function zwjwdkk() {
    if(!checkSelected("dgYzxyls")) {
        return; 
    }
    var rows = $('#dgYzxyls').datagrid('getSelections');
    var idArray = new Array();//创建存放id的数组
    $.each(rows,function(n,row){
        idArray[n] = row.id;
    });
    $.messager.confirm('确认','执行该操作后，会重新进行阈值校验，您确定要执行吗？', function(r){
        if(r){
            // 添加遮罩
            ajaxLoading();
            $.ajax({
            url:'/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/zwjwdkk_view',
            type : 'post',
            dataType : 'text',
            data : {
                'ids' : idArray.join(",")
            },
            success:function(data){
                // 取消遮罩
                ajaxLoadEnd();
                //执行请求后的方法
                afterAjax(data, 'dgYzxyls','');
            },
            error: function () {
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
            });
        }
    });
}
