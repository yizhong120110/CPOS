/**
 * 页面初始化加载
*/

var codeKzjyfsmkdm = null;
var codeLsdrmkdm = null;
$(document).ready(function() {
    
    // 主页面 form tab排序
    $("#forSearch").tabSort();
    // 渲染表格
    $('#dgYwGtpm002').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/data_view",
        remoteSort: false,
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [[
            // 业务简称、业务名称、数据表数量
            { field: 'id', title: '业务id', hidden:true },
            { field: 'ywmc', title: '业务名称', width: 33},
            { field: 'wjlx', title: '批扣文件类型', halign: 'center', align:'left', width: 20 },
            { field: 'czr', title: '操作人', halign: 'center', align:'left', width: 20 },
            { field: 'czsj', title: '操作时间', halign: 'center', align:'center', width: 20 },
            { field: 'cz', title: '操作', halign: 'center', align:'left', width: 20,
                formatter: function(value, rowData, rowIndex) {
                    var czStr = '';
                    if (rowData) {
                        czStr += '<a href="javascript:void(0);" onclick="showHide(\'update\',\'dgYwGtpm002\',\'' + rowIndex + '\',event);">编辑</a> ';
                    }
                    return czStr;
                }
            }
        ]],
        toolbar: [{
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                // 新增
                showHide('add');
            }
        }, '-', {
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 删除
                removechecked();
            }
        }]
    });
    
    // 文件类型限制长度最大20位,只允许数字，字母下划线
    $("#txtSearchWjlx").next().children().attr("maxlength","20");
    $("#txtGtpmWjlx").next().children().attr("maxlength","20");
    
    // 按钮【查询】的click事件监听
    $("#lbtnSearch").click(function(e){
        e.preventDefault();
        // 调用查询的方法
        doSearch();
    });

});
/**
* 所属框查询
* value: 输入查询内容
* name：查询条件key
*/
function doSearch(){
    // 所属业务
    var ssyw = $("#combSearchSsyw").combobox('getValue');
    // 文件类型
    var wjlx = $("#txtSearchWjlx").textbox('getValue');
    // 根据条件查询业务配置列表信息
    $("#dgYwGtpm002").datagrid('load',{
        ssyw: ssyw,
        wjlx: wjlx
    });
}
/**
 * 新增or编辑业务参数弹窗初始化
 */
function showHide(handle,id,index) {
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    // 根据参数不同打开不同的页面
    if (handle == 'add') {
        // 打开新增页面
        newWindow($("#divYwGtpm002"), '新增业务配置', 700, 480, 350, 20);
        $("#ifmXzcs").attr("src","/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/ywpz_view?id=add");
    } else if(handle == 'update'){
        // 打开编辑页面
        newWindow($("#divYwGtpm002"), '编辑业务配置', 700, 480, 350, 20);
        var d = $('#' + id).datagrid('getData').rows[index];
        $("#ifmXzcs").attr("src","/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/ywpz_view?id="+d.id);
    }

}

/**
*批量删除
*/
function removechecked(){
    if(!checkSelected("dgYwGtpm002")) {
        return;
    }
    $.messager.confirm('提示', '删除业务配置后不可恢复，并且会删除对应的参数配置，您确定要删除吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            // 当前选中的记录
            var checkedItems = $('#dgYwGtpm002').datagrid('getChecked');
            var ids = new Array();
            $(checkedItems).each(function(index, item){
                ids.push(item["id"]);
            });
            $.ajax({
                type: 'post',
                dataType: 'text',
                url: "/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/delete_ywpz_view",
                data: {"ids": ids.join(",")},
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, "dgYwGtpm002", "");
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
