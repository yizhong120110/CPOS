$(document).ready(function() {
    $('#dgZlclbForm').tabSort();
    // 渲染表格
    $('#dgZlclb').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_007/kf_ywgl_007_view/data_view?ywid="+$("#hidYwid").val(),
        remoteSort: false,
        frozenColumns: [[
            { field: 'ck', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: '编号', hidden:true },
            { field: 'zlcbm', title: '子流程编码', width: 5 },
            { field: 'zlcmc', title: '子流程名称', width: 10, formatter: function(value,row,index){
                return '<a href="javascript:;" onclick = "zlcxxck_tab(event,\''+value+'\', \''+ row.id+'\');">'+value+'</a>';
            } },
            { field: 'zlcms', title: '子流程描述', width: 10 },
            { field: 'bbh', title: '版本号', width: 4, formatter: function(value,row,index) {
                if (row.bbsftj == '1') {
                    return '<span class="clean">'+value+'</span>';
                } else {
                    return '<span class="modified">'+value+'</span>';
                }
            } },
            { field: 'yycs', title: '引用次数', width: 4, align:'right', halign:'center',formatter: function(value,row,index){
                if (value == 0){
                    return value;
                }else{
                    return '<a href="javascript:;" onclick = "yycsck(event,'+'\'zlc'+'\',\''+row.id+'\');">'+accounting.formatNumber(value)+'</a>';
                }
            }},
            { field: 'operation', title: '操作', width: 9, formatter: function(value,rowData,index) {
                return '<a href="javascript:;" onclick = "bbtj(\''+'zlc'+'\',\''+rowData.bbsftj+'\',\''+rowData.id+'\',\''+'dgZlclb'+'\');">版本提交</a> '+
                '<a href="javascript:;" onclick = "bbxxck(event,\''+rowData.zlcmc+'\',\''+rowData.id+'\');">版本信息查看</a> '+
                '<a href="javascript:;" onclick = "bbhy(\''+'zlc'+'\',\''+rowData.bbsftj+'\',\''+rowData.id+'\',\''+'dgZlclb'+'\',\''+rowData.bbh+'\');">版本还原</a>';
            } }
        ]],
        toolbar : [ {
            iconCls : 'icon-add',
            text : '新增',
            handler : function() {
                // 增加
                add_zlc( );
            }
        }, {
            iconCls : 'icon-remove',
            text : '删除',
            handler : function() {
                if(!checkSelected("dgZlclb")) {
                    return;
                }
                $.messager.confirm("确认", '子流程删除后数据将不可恢复，您确定要删除吗？', function (r) {
                    if (r) {
                        // 调用删除方法
                        removechecked();
                    }
                });
            }
        }]
    });
    
    // 新增子流程中的取消按钮
    $('#lbtnZlcCancel').click(function(e){
        e.preventDefault();
    	$('#divZlcWindow').window('close');
    });
    
    // 最大值限制
    $("#txtZlcmc").next().children().attr("maxlength","50");
    $("#txtZlcbm").next().children().attr("maxlength","50");
    $("#txtZlcms").next().children().attr("maxlength","150");
    
    $("#lbtnZlcSubmit").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 出错提示
        var msg = "新增失败，请稍后再试";
        url = "/oa/kf_ywgl/kf_ywgl_007/kf_ywgl_007_view/data_add_view";
        //所属业务
        var ssyw = $('#hidYwid').val()
        // 提交表单
        $('#divZlcWindow').find('form').form('submit', {
            url: url,
            queryParams:{'ssyw':ssyw},
            onSubmit: function(){
                var zlcmc = $("#txtZlcmc").textbox("getValue");
                var zlcbm = $("#txtZlcbm").textbox("getValue");
                var zlcms = $("#txtZlcms").textbox("getValue");
                if (zlcmc=="") {
                    $.messager.alert('错误','子流程名称不可为空，请输入','error', function(){
                        $("#txtZlcmc").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if(!checkMc(zlcmc,'子流程名称','txtZlcmc')){
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (zlcbm=="") {
                    $.messager.alert('错误','子流程编码不可为空，请输入','error', function(){
                        $("#txtZlcbm").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if(!checkBm(zlcbm,'子流程编码','txtZlcbm')){
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                return true;
            },
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, "dgZlclb", "divZlcWindow");
            },
            error: function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });

    
    
});


/**
*新增子流程的窗口
*/

function add_zlc() {
    // 增加窗体
    newWindow($("#divZlcWindow"),'新增子流程',500,310);
    $('#addZlcForm').tabSort();
    $("#txtSsyw").textbox('disable');
    $('#txtSsyw').textbox('setValue',$('#hidYwmc').val() );
    $("#txtZlcmc").next().children().select();
};





/**
*批量删除
*/
function removechecked(){
    // 添加遮罩
    ajaxLoading();
    var checkedItems = $('#dgZlclb').datagrid('getChecked');
    var zlcids = new Array();
    $(checkedItems).each(function(index, item){
        zlcids.push(item["id"]);
    });
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_ywgl/kf_ywgl_007/kf_ywgl_007_view/data_del_view",
        data: {"zlcids":zlcids.join(",")},
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgZlclb", "");
        },
        error: function(){
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}
/*
版本信息查看
*/
function bbxxck(event,lc,zlcid) {
    event.stopPropagation();
    newTab(lc + '_版本信息查看', '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxxck_index_view?lx=zlc&id=' + zlcid);
}
/*
子流程详细信息查看
*/
function zlcxxck_tab( event,zlcmc,zlcid ){
    event.stopPropagation();
    var title = '子流程详情查看';
    if ( zlcmc != '' )
        title = zlcmc + '_子流程详情查看';
    var href = "/oa/kf_ywgl/kf_ywgl_zlcxq?zlcid="+zlcid;
    newTab(title, href);

}
/*
引用次数查看
*/
function yycsck( event,lx,zlcid ){
    event.stopPropagation();
    newWindow($("#yycs_window"), '引用次数查看', 800, 420);
    $("#yycs_window iframe")[0].src = "/oa/kf_jdgl/kf_jdgl_001/kf_jdgl_001_view/yycs_index_view?jdid=" + zlcid;
}
