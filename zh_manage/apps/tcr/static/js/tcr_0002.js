/**
 * 页面ready方法
 */
$(function() {
    // 终端状态
    var statelx = [{"bm":"0", "mc":"请选择"},{"bm":"1", "mc":"已激活"},{"bm":"2", "mc":"已注销"}]

    // 机构号最大值限制
    $("#txt_tcrjgh").next().children().attr("maxlength","30");
    // 机构名称最大值限制
    $("#txt_tcrjgmc").next().children().attr("maxlength","60");
    // 虚拟柜员号最大值限制
    $("#txt_tcrvghy").next().children().attr("maxlength","20");

    // 终端号最大值限制
    $("#txt_tcrid").next().children().attr("maxlength","20");
    // 终端名称最大值限制
    $("#txt_tcrname").next().children().attr("maxlength","25");
    // 终端IP最大值限制
    $("#txt_tcrip").next().children().attr("maxlength","15");

    // 终端一览
    $("#dgZdxx").datagrid({
        nowrap : true,
        fit: true,
        rownumbers : true,
        pagination : true,
        pageSize : 50,
        fitColumns : true,
        method: "POST",
        url: "/tcr/oa/tcr_0002/tcr_0002_view/data_view",
        singleSelect: true,
        selectOnCheck: true, 
        checkOnSelect: true,
        remoteSort: false,
        frozenColumns: [
            [{field: 'select_box', checkbox: true}]
        ],
        columns: [
            [
             {field: 'jgh', title: '机构号', width: 15, align: 'center' },
             {field: 'jgmc2', title: '机构名称', width: 20, halign:'center', align: 'left' },
             {field: 'vgyh', title: '虚拟柜员号', width: 15, align: 'center' },
             {field: 'terminal_id', title: '终端号', width: 15, align: 'center' },
             {field: 'jgmc', title: '终端名称', width: 20 },
             {field: 'cip', title: '终端IP',width: 12},
             {field: 'gzqssj',title: '工作开始时间',width: 12, align: 'center'},
             {field: 'gzjssj',title: '工作结束时间',width: 12, align: 'center'},
             {field: 'state',title: '终端状态',width: 10, align: 'center', 
                formatter: function(value, rowData, rowIndex) {
                    if(value == '1') {
                        return "已激活";
                    } else {
                        return "已注销";
                    }
            }},
            {field: 'usest', title: '使用状态', width: 10, align: 'center',
                formatter: function(value, rowData, rowIndex) {
                    if(value == '0') {
                        return "未使用";
                    } else if(value == '1') {
                        return "已签到";
                    } else {
                        return "已签退";
                    }
                }
            },
            {field: 'sign_person', title: '当前签到人', width: 12, align: 'center' },
            {field: 'load_time', title: '签到时间', width: 18, align: 'center',
                formatter: function(value, rowData, rowIndex) {
                    var loadTime = '';
                    if(value != '' && value != null) {
                        loadTime = value.substring(0, 4) + '/';
                        loadTime += value.substring(4, 6) + '/';
                        loadTime += value.substring(6, 8) + ' ';
                        loadTime += value.substring(8, 10) + ':';
                        loadTime += value.substring(10, 12) + ' ';
                        loadTime += value.substring(12, 14);
                    }
                    return loadTime;
                }
            },
            {field: 'cz',title: '操作',width: 20, align: 'center', 
                formatter: function(value, rowData, rowIndex) {
                    var czStr = '';
                    if(rowData) {
                        czStr += '<a href="javascript:;" onclick="javascript:edit_tcr(' + rowIndex + ');">编辑</a>&nbsp;<a href="javascript:;" onclick="javascript:force_exit(' + rowIndex + ');">强制签退</a>';
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
                tcr_add2upd(-1, 'add');
            }
        }, '-', {
            iconCls: 'icon-ok',
            text: '激活',
            handler: function() {
                // 激活
                qyjk('1');
            }
        }, '-', {
            iconCls: 'icon-cancel',
            text: '注销',
            handler: function() {
                // 注销
                qyjk('0');
            }
        }]
    });
    // 绑定添加管理对象的方法
    $('#lbtnJkdx_ok_add').on('click', function(e) {
        e.preventDefault();
        window_update_add_func();
    });
    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });
    $("#lbtnJkdx_cancel").on('click', function(e) {
        e.preventDefault();
        $("#tcr_add2upd_window").window('close');
    });
    // 终端状态的下拉列表
    $("#combSearch_state").combobox({
        data: statelx,
        valueField: 'bm',
        textField: 'mc',
    });
    $("#combSearch_state").combobox('setValue', '0');

    // tab顺 
    $('#dxForm').tabSort();
});

/**
* 新增或编辑TCR.
**/
function tcr_add2upd(rowIndex, type, event) {

    if (event){
        event.stopPropagation();
    }

    $("#hidJkdx_id").val('');

    if (type == 'add') {
        // 创建新增窗口
        newWindow($('#tcr_add2upd_window'), "新增终端", '400', '345');
        // 工作开始时间
        $("#txt_gzqssj").timespinner('setValue', '08:00');
        // 工作结束时间
        $("#txt_gzjssj").timespinner('setValue', '18:00');
    } else if (type = 'upd') {
        newWindow($('#tcr_add2upd_window'), "编辑终端", '400', '345');
        // 取得当前行状态
        var row = $("#dgZdxx").datagrid('getData').rows[rowIndex];
        // 终端号不可修改
        $('#txt_tcrid').textbox("disable");
        $('#txt_tcrid').textbox('setValue', row.terminal_id);
        $("#hidJkdx_id").val(row.terminal_id);
        // 机构号
        $('#txt_tcrjgh').textbox('setValue', row.jgh);
        // 机构名称
        $('#txt_tcrjgmc').textbox('setValue', row.jgmc2);
        // 虚拟柜员号
        $('#txt_tcrvgyh').textbox('setValue', row.vgyh);

        // 终端名称
        $('#txt_tcrname').textbox('setValue', row.jgmc);
        // 终端IP
        $('#txt_tcrip').textbox('setValue', row.cip);
        // 工作开始时间
        $("#txt_gzqssj").timespinner('setValue', row.gzqssj);
        // 工作结束时间
        $("#txt_gzjssj").timespinner('setValue', row.gzjssj);
    }
}

/**
 * 注销,激活
 */
function qyjk(able) {
    var comf = "1" == able?"激活":"注销";
    // 获取所有选中的监控对象
    var checkedItems = $('#dgZdxx').datagrid('getChecked');
    // 校验至少选择一项
    if (!checkSelected("dgZdxx")){
        return;
    }
    if("1" == able){
        msg = "您确定要激活吗？";
    } else {
        msg = "您确定要注销吗？";
    }
    $.messager.confirm("提示", msg, function(flag) {
        if (flag) {
            url = '/tcr/oa/tcr_0002/tcr_0002_view/able_view';
            // 启用监控对象
            ajax_jkdx(url, able);
        }
    })
}
/**
 * 激活或注销终端.
 **/
function ajax_jkdx(url, zt){

    var tcrjgh = "";
    var tcrjgmc = "";
    var tcrvgyh = "";

    var tcrid = "";
    var tcrip = "";
    var gzqssj = "";
    var gzjssj = "";
    var jgmc = "";

    // 添加遮罩
    ajaxLoading();
    // 激活或注销终端
    var rows = $('#dgZdxx').datagrid('getSelections');
    // 获取所有id
    $.each(rows,function(n,row){
        tcrid = row.terminal_id;
        tcrip = row.cip;
        gzqssj = row.gzqssj;
        gzjssj = row.gzjssj;
        jgmc = row.jgmc;
    });
    // ajax请求
    $.ajax({
        url:url,
        type : 'POST',
        dataType : 'json',
        data : {
            'tcrid': tcrid,
            'tcrip': tcrip,
            'zt': zt,
            'gzqssj': gzqssj,
            'gzjssj': gzjssj,
            'jgmc':jgmc
        },
        success:function(data){
            // 取消遮罩
            ajaxLoadEnd();
            //执行请求后的方法
            afterAjax(data, 'dgZdxx','');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

// 公共函数更新方法
function window_update_add_func(e){

    if(e) {
        e.preventDefault();
    }

    // 添加遮罩
    ajaxLoading();
    // 添加监控对象url
    var url = "/tcr/oa/tcr_0002/tcr_0002_view/add_view";
    if( $('#hidJkdx_id').val() != '' ){
        url = '/tcr/oa/tcr_0002/tcr_0002_view/edit_view'
    }
    // 添加监控对象
    $('#tcr_add2upd_window').find('form').form('submit', {
        url: url,
        dataType: 'json',
        onSubmit: function(){
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
            //执行请求后的方法
            afterAjax(data, 'dgZdxx','tcr_add2upd_window');
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
* 表格查询
**/
function doSearch() {

    // 机构名称
    var jgmc = $("#txtSearch_jgmc2").textbox('getValue').trim();
    // 终端名称
    var tcrmc = $("#txtSearch_jgmc").textbox('getValue').trim();
    // 终端IP
    var tcrip = $("#txtSearch_cip").textbox('getValue');
    // 终端状态
    var tcrst = $("#combSearch_state").combobox('getValue');
    if(tcrst == "0") {
        tcrst = "";
    }

    // 根据条件查询终端一览
    $("#dgZdxx").datagrid('load',{
        jgmc: jgmc,
        tcrmc: tcrmc,
        tcrip: tcrip,
        tcrst: tcrst
    });
}

/**
* 强制签退.
*/
function force_exit(rowIndex) {

    // 取得当前行状态
    var row = $("#dgZdxx").datagrid('getData').rows[rowIndex];
    // 状态为不是已签到时
    if(row.usest != "1") {
        $.messager.alert('提示','终端状态不是已签到，不能强制签退!','info');
        return;
    }

    $.messager.confirm("提示", "确定要强制签退？", function(flag) {
        if (flag) {
            // ajax请求
            $.ajax({
                url: "/tcr/oa/tcr_0002/tcr_0002_view/force_exit_view",
                type : 'POST',
                dataType : 'json',
                data : {
                    'tcrid': row.terminal_id
                },
                success:function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    //执行请求后的方法
                    afterAjax(data, 'dgZdxx','');
                },
                error : function(){
                    // 取消遮罩
                    ajaxLoadEnd();
                    // 失败后要执行的方法
                    errorAjax();
                }
            });
        }
    });
}

/**
* 编辑.
**/
function edit_tcr(rowIndex) {

    tcr_add2upd(rowIndex, "upd");
}

// 输入框校验
function validate(){

    // 机构号
    var tcrjgh = $("#txt_tcrjgh").textbox('getValue').trim();
    // 机构名称
    var tcrjgmc = $("#txt_tcrjgmc").textbox('getValue').trim();
    // 虚拟柜员号
    var tcrvgyh = $("#txt_tcrvgyh").textbox('getValue').trim();

    // 终端ID
    var tcrid = $("#txt_tcrid").textbox('getValue').trim();
    // 终端名称
    var tcrname = $("#txt_tcrname").textbox('getValue').trim();
    // 终端IP
    var tcrip = $("#txt_tcrip").textbox('getValue').trim();
    // 工作开始时间
    var gzqssj = $("#txt_gzqssj").timespinner('getValue');
    // 工作结束时间
    var gzjssj = $("#txt_gzjssj").timespinner('getValue');

    // 机构号
    if(tcrjgh == "" || tcrjgh == null) {
        $.messager.alert('错误','机构号不能为空','error', function(){
            $("#txt_tcrjgh").next().children().focus();
        });
        return false;
    }

    // 机构名称
    if(tcrjgmc == "" || tcrjgmc == null) {
        $.messager.alert('错误','机构名称不能为空','error', function(){
            $("#txt_tcrjgmc").next().children().focus();
        });
        return false;
    }

    // 虚拟柜员号
    if(tcrvgyh == "" || tcrvgyh == null) {
        $.messager.alert('错误','虚拟柜员号不能为空','error', function(){
            $("#txt_tcrvgyh").next().children().focus();
        });
        return false;
    }

    // 终端ID
    if(tcrid == "" || tcrid == null) {
        $.messager.alert('错误','终端ID不能为空','error', function(){
            $("#txt_tcrid").next().children().focus();
        });
        return false;
    }

    // 终端名称
    if( tcrname == "" || tcrname == null ) {
        $.messager.alert('错误','终端名称不能为空','error', function(){
            $("#txt_tcrname").next().children().focus();
        });
        return false;
    }
    
    // 终端IP
    if(tcrip == "" || tcrip == null) {
        $.messager.alert('错误','终端IP不能为空','error', function(){
            $("#txt_tcrip").next().children().focus();
        });
        return false;
    }
    if(isIP(tcrip) == false) {
        $.messager.alert('错误','终端IP格式不正确','error', function(){
            $("#txt_tcrip").next().children().focus();
        });
        return false;
    }

    return true;
}

/**
* IP地址校验.
**/
function isIP(ip) {

    var reSpaceCheck = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;

    if (reSpaceCheck.test(ip)) {  
        ip.match(reSpaceCheck);  
        if (RegExp.$1<=255&&RegExp.$1>=0  
          &&RegExp.$2<=255&&RegExp.$2>=0  
          &&RegExp.$3<=255&&RegExp.$3>=0  
          &&RegExp.$4<=255&&RegExp.$4>=0) {  
            return true;
        } else {  
            return false;
        }  
    } else {  
        return false;
    }  
} 