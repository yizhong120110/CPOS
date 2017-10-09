/**
* 初始化页面元素
* 表格
*/
$(document).ready(function() {
    // 渲染表格
    $('#dgYwgl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_dsiv/yw_dsiv_001/yw_dsiv_001_view/data_view",
        remoteSort: false,
        columns: [[
            // 业务简称、业务名称、数据表数量
            { field: 'id', title: '业务id', hidden:true },
            { field: 'ywbm', title: '业务简称', width: 31 },
            { field: 'ywmc', title: '业务名称', width: 33, formatter: function(value,row,index){
                return '<a href="javascript:;" onclick = "ywxx_ck(\''+ value +'\', \''+ row.id +'\');" >'+value+'</a>';
            } },
            { field: 'sjbsl', title: '数据库表数量', halign: 'center', align:'right', width: 20 }
        ]]
    });
});
/**
* 函数说明：查看业务下表信息
* value: 业务名称
* id：业务id
*/
function ywxx_ck(value, id) {
    // 所在平台
    var pt = $('#hidPt').val();
    // 超链接操作不选择行
    event = event || window.event
    event.stopPropagation();
    // 页面标题为：业务名称_数据库查看
    title = value + '_数据库查看';
    // 直接调用开发系统数据库模型管理中的后台程序
    var url = "/oa/kf_ywgl/kf_ywgl_011/kf_ywgl_011_view/index_view?ywid="+id + "&pt=" + pt;
    // 打开一个新标签
    newTab(title, url);
}
