$(document).ready(function() {
    // 绑定增加/修改弹出框中的取消按钮
    $('#window_cancel').click(function(){
        $('#bean_window').window('close');
    });
    $('#dgJdgl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize : 50,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_jdgl/kf_jdgl_001/kf_jdgl_001_view/data_view",
        remoteSort: false,
        frozenColumns: [[
            { field: 'select_box', checkbox: true }
        ]],
        columns: [[
            { field: 'jdbm', title: '节点编码', width: 8 },
            { field: 'jdmc', title: '节点名称', width: 12 },
            { field: 'jdlx', title: '节点类型', width: 6 },
            { field: 'bbh', title: '版本号', width: 4, formatter: function(value,rowData,rowIndex) {
                if (rowData.bbsftj=='1' || rowData.bbsftj==1) {
                    return '<span class="clean">'+value+'</span>';
                } else {
                    return '<span class="modified">'+value+'</span>';
                }
            } },
            { field: 'yycs', title: '引用次数', width: 4, halign: 'center', align:'right', formatter: function(value,rowData,rowIndex) {
                if (value == '0') {
                    return value;
                } else {
                    return '<a href="javascript:jdgl_yycs(\''+rowData.jdid+'\');">' + accounting.formatNumber(value) +'</a>';
                }
            } },
            { field: 'jdid', title: 'jdid', hidden:true },
            { field: 'jdlxdm', title: 'jdlxdm', hidden:true },
            { field: 'operation', title: '操作', width: 250, fixed: true, formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:nodeEdit(\''+rowData.jdid+'\');">编辑</a> '+
                '<a href="javascript:auto_test(\''+rowData.jdid+'\',\'jd\',\''+rowData.jdmc+'\',\'节点\');">测试</a> '+
                '<a href="javascript:;" onclick="javascript:bbtj(\''+'jd'+'\',\''+rowData.bbsftj+'\',\''+rowData.jdid+'\',\''+'dgJdgl'+'\');">版本提交</a> '+
                '<a href="javascript:bbxxck(\''+rowData.jdmc+'\',\''+rowData.jdid+'\',\''+rowData.jdlxdm+'\');">版本信息查看</a> '+
                '<a href="javascript:;" onclick="javascript:bbhy(\''+'jd'+'\',\''+rowData.bbsftj+'\',\''+rowData.jdid+'\',\''+'dgJdgl'+'\',\''+rowData.bbh+'\');">版本还原</a>';
            } }
        ]],
        toolbar: [{
            iconCls : 'icon-remove',
            text : '删除',
            handler : function() {
                if(!checkSelected("dgJdgl")) {
                    return;
                }
                $.messager.confirm("确认", '所选节点将被删除且不可恢复，您确定要删除吗？', function (r) {
                    if (r) {
                        // 调用删除方法
                        removechecked();
                    }
                });
            }
        }],
        onLoadSuccess: function(data){ // 加载完毕后获取所有的checkbox遍历
            if (data.rows.length > 0) {
                // 循环判断操作为新增的不能选择
                for (var i = 0; i < data.rows.length; i++) {
                    // 根据引用次数让某些行不可选
                    if (data.rows[i].yycs != 0) {
                        $("input[type='checkbox']")[i + 1].disabled = true;
                    }
                }
            }
        },
        onClickRow: function(rowIndex, rowData){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgJdgl').datagrid('unselectRow', index - 1);
                }
            });
            // 如果可选的都已选中，全选复选框置为勾选状态
            if ($('.datagrid-cell-check input:enabled').length == $('#dgJdgl').datagrid('getChecked').length && $('#dgJdgl').datagrid('getChecked').length != 0) {
                $('.datagrid-header-check input').get(0).checked = true;
            }
        },
        onCheckAll: function(rows){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgJdgl').datagrid('unselectRow', index - 1);
                }
            });
            // 全选复选框置为勾选状态
            $('.datagrid-header-check input').get(0).checked = true;
        }
    });
    
    var fields =  $('#dgJdgl').datagrid('getColumnFields');
    var muit="";
    for(var i=0; i<fields.length-4; i++){
        var opts = $('#dgJdgl').datagrid('getColumnOption', fields[i]);
        muit += "<div data-options=\"name:'"+  fields[i] +"'\">"+ opts.title +"</div>";
    };
    $('#mm').html($('#mm').html()+muit);
    $('#search_box').searchbox({
        menu:'#mm'
    });
    
    $("#window_ok_update").click(function(){
        $.messager.alert('提示', '编辑成功!', 'info');
        $('#bean_window').window('close');
    });
    $("#window_cancel").click(function(){
        $('#bean_window').window('close');
    });
    
});

function doSearch(value, name){
    $('#dgJdgl').datagrid('reload', {
        search_name: name,
        search_value: value
    });
}

function nodeEdit(jdid) {
    newWindow2($("#winNodeEdit"), '节点编辑', '85', 480);
    $("#winNodeEdit iframe")[0].src = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_edit_view?nodeid=" + jdid;
}

function jdgl_yycs(jdid) {
    newWindow($("#yycs_window"), '引用次数查看', 800, 420);
    $("#yycs_window iframe")[0].src = "/oa/kf_jdgl/kf_jdgl_001/kf_jdgl_001_view/yycs_index_view?jdid=" + jdid;
}

/**
*批量删除
*/
function removechecked(){
    var checkedItems = $('#dgJdgl').datagrid('getChecked');
    var jdids = new Array();
    $(checkedItems).each(function(index, item){
        jdids.push(item["jdid"]);
    });
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_jdgl/kf_jdgl_001/kf_jdgl_001_view/data_del_view",
        data: {"jdids":jdids.join(",")},
        success: function(data){
            afterAjax(data, "dgJdgl", "");
        },
        error: function(){
            errorAjax();
        }
    });
}

/*
版本信息查看
*/
function bbxxck(lc,jdid,jdlx) {
    newTab(lc + '_版本信息查看', '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxxck_index_view?lx=jd&id=' + jdid+"&jdlx="+jdlx);
}
/**
 * 弹出自动化测试窗口
 * @returns {boolean}
 */
function auto_test(csalid,lx,jdmc,lxmc){
    $("#zdhcs_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/index_view?csaldyssid="+csalid+"&lx="+lx+"&text="+jdmc+"&lxmc="+lxmc);
    // 打开自动化测试的结果
    newWindow($("#zdhcs_window"),'自动化测试',1300, 480);
}
