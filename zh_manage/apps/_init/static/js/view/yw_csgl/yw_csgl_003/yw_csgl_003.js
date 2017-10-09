/**
* 初始化页面元素
* 表格
* 条件查询框
*/
$(document).ready(function() {
    // 渲染表格
    $('#dgJygl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_csgl/yw_csgl_003/yw_csgl_003_view/data_view",
        remoteSort: false,
        columns: [[
            // 所属业务、交易码、交易名称、交易状态
            { field: 'id', title: '交易id', hidden:true },
            { field: 'ywmc', title: '所属业务', width: 31 },
            { field: 'jym', title: '交易码', width: 31 },
            { field: 'jymc', title: '交易名称', width: 33, formatter: function(value,row,index){
                return '<a href="javascript:;" onclick = "jyxx_ck(\''+ value +'\', \''+ row.id +'\');" >'+value+'</a>';
            } },
            { field: 'zt', title: '交易状态', width: 20 }
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
    var fields =  $('#dgJygl').datagrid('getColumnFields');
    var muit="";
    // 遍历数据表格title，组织条件查询选项
    // 根据所属业务、交易码、交易名称、交易状态进行查询
    for(var i=0; i<fields.length; i++){
        var opts = $('#dgJygl').datagrid('getColumnOption', fields[i]);
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
    // 交易数据表格重新获取数据
    $('#dgJygl').datagrid( {url:'/oa/yw_csgl/yw_csgl_003/yw_csgl_003_view/data_view?' + tj_str });
    
}

/**
* 函数说明：查看交易详情：交易基本信息+参数信息
* value: 交易名称
* id：交易id
*/
function jyxx_ck(value, id) {
    // 设置操作行不被选中
    event = event || window.event
    event.stopPropagation();
    // 打开页面title默认为交易参数
    var title = '交易参数';
    // 交易名称存在则为：交易参数_交易名称
    if ( value != '' )
        title = '交易参数_' + value;
    // 直接调用开发系统交易基本信息中的后台程序
    // 平台
    var pt = $("#hidPt").val();
    // 此处多传入pt，用于区分请求是由运维系统的参数管理过去的
    var url = "/oa/kf_ywgl/kf_ywgl_003/kf_ywgl_003_view/index_view?jyid="+id + '&pt=' + pt;;
    // 打开一个新标签
    newTab(title, url);
}
