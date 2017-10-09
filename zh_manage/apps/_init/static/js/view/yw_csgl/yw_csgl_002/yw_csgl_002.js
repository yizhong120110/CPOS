/**
* 初始化页面元素
* 表格
* 条件查询框
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
        url: "/oa/yw_csgl/yw_csgl_002/yw_csgl_002_view/data_view",
        remoteSort: false,
        columns: [[
            // 业务简称、业务名称、交易数量
            { field: 'id', title: '业务id', hidden:true },
            { field: 'ywbm', title: '业务简称', width: 31 },
            { field: 'ywmc', title: '业务名称', width: 33, formatter: function(value,row,index){
                if (row.ywbm.toUpperCase() == 'BEAITX') {
                    return value
                } else {
                    return '<a href="javascript:;" onclick = "ywxx_ck(\''+ value +'\', \''+ row.id +'\');" >'+value+'</a>';
                }
            } },
            { field: 'jysl', title: '交易数量', width: 20, halign: 'center', align:'right' }
        ]],
        toolbar: [{
            iconCls: '',
            text: '',
            handler: function() {
            }
        }]
    });
    // 搜索框设置
    // 首先获取数据表格title
    var fields =  $('#dgYwgl').datagrid('getColumnFields');
    var muit="";
    // 遍历数据表格title，组织条件查询选项
    for(var i=0; i<fields.length-1; i++){
        var opts = $('#dgYwgl').datagrid('getColumnOption', fields[i]);
        // id是隐藏域，不作为查询条件
        if( fields[i] != 'id' ){
            muit += "<div data-options=\"name:'"+  fields[i] +"'\">"+ opts.title +"</div>";
        }
    };
    // 将查询选项追加到查询控件中
    $('#divSearch').html($('#divSearch').html()+muit);
    // 查询条件输入框赋值默认值
    $('#search_box').searchbox({
        menu:'#divSearch',
        prompt:'请输入查询内容',
        searcher:doSearch
    });
});

/**
* 所属框查询
* value: 输入查询内容
* name：查询条件key
*/
function doSearch(value,name){
    // 重新定义url
    var tj_str = 'search_name=' + name + '&search_value=' + value;
    // 业务数据表格重新获取数据
    $('#dgYwgl').datagrid( {url:'/oa/yw_csgl/yw_csgl_002/yw_csgl_002_view/data_view?' + tj_str });
}

/**
* 函数说明：查看业务详情：业务基本信息+参数信息
* value: 业务名称
* id：业务id
*/
function ywxx_ck(value, id) {
    // 设置操作行不被选中
    event = event || window.event
    event.stopPropagation();
    // 打开页面title默认为业务参数
    var title = '业务参数';
    // 业务名称存在则为：业务参数_业务名称
    if ( value != '' )
        title = '业务参数_' + value;
    // 直接调用开发系统业务基本信息中的后台程序
    // 平台
    var pt = $("#hidPt").val();
    // 此处多传入pt，用于区分请求是由运维系统的参数管理过去的
    var url = "/oa/kf_ywgl/kf_ywgl_002/kf_ywgl_002_view/index_view?ywid="+id + '&pt=' + pt;
    // 打开一个新标签
    newTab(title, url);
}
