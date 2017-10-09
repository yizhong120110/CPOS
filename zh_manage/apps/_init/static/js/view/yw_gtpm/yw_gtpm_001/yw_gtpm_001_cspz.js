/**
 * 页面初始化加载
*/;
$(document).ready(function() {
    // 预定义当前页面显示信息
    var datagrid;
    // 渲染表格，页面初始化信息加载
    datagrid = $('#dgCspz').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        pagination: true,
        fitColumns: true,
        method: "post",
        selectOnCheck: true, 
        pageSize: 50,
        checkOnSelect: true,
        remoteSort: false,
        url: "/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/data_view",
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [[
            { field: 'id', title: 'id', hidden:true },
            { field: 'ywmc', title: '所属业务', width: 100 },
            { field: 'csdm', title: '参数代码', width: 80 },
            { field: 'kgl', title: '开关量', width: 50 },
            { field: 'csz', title: '参数值', width: 100 },
            { field: 'csz2', title: '参数值2', width: 100 }, 
            { field: 'csms', title: '参数描述', width: 100 },
            { field: 'czr', title: '操作人', width: 100 },
            { field: 'czsj', title: '操作时间', width: 100, align: 'center' },
            { field: 'cz', title: '操作', width: 80,
                formatter: function(value, rowData, rowIndex) {
                    return '<a href="javascript:" onclick = "showHide(\''+rowData.id+'\');">编辑</a> '
                }
            }
        ]],
        toolbar: [{
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                // 调用新增方法
                showHide('add');
            }
        }, {
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 调用删除方法
                removechecked( "" );
            }
        }]
    });
    // 主页面 form tab排序
    $("#fmSearch").tabSort();
});
/*
 *  新增页面和编辑页面
 */
function showHide( id ) {
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 根据参数不同展示不同的页面
    if (id == 'add' ) {
        // 打开新增页面
        newWindow($("#divXzcs"),'新增参数',500, 380);
        $("#ifmXzcs").attr("src","/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/cspz_ggym_view?id="+id);
    } else if( id != '' ){
        // 打开编辑页面
        newWindow($("#divXzcs"),'编辑参数',500, 380);
        $("#ifmXzcs").attr("src","/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/cspz_ggym_view?id="+id);
    }
};

/*
 *  删除
 */
function removechecked( id ) {
    var rows = $('#dgCspz').datagrid('getSelections');
    var csid = new Array();
    $(rows).each(function(index, item){
        csid.push(item["id"]);
    });
    if (rows.length) {
        $.messager.confirm('提示', '删除参数后不可恢复，您确定要删除吗？', function(r) {
            if (r) {
                // 添加遮罩
                ajaxLoading();
                //发送删除请求
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url: "/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/del_pl_view",
                    data: {'csid': csid.join(",")},
                    success: function(data){
                        // 取消遮罩
                        ajaxLoadEnd();
                        afterAjax(data, "dgCspz", "");
                    },
                    error : function(){
                        // 取消遮罩
                        ajaxLoadEnd();
                        errorAjax();
                    }
                });
            }
        })
    } else {
        $.messager.alert('提示', '至少选择一项', 'info');
    }
}
/*
 *  查询事件
 */
function doSearch(event){
    // 取消默认提交事件
    event.preventDefault();
    // 业务ID
    var ywid = $("#selYwmc").textbox("getValue");
    // 参数代码
    var csdm = $("#selCsdm").textbox("getValue");
    // 根据条件查询对象
    $("#dgCspz").datagrid('load',{
        csdm: csdm,
        ywid: ywid
    });
}
